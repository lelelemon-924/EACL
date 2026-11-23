#!/usr/bin/env python3
"""Tail-Recovery-SFT: the missing cross-cell for reviewer ptEw.

    python -m cure_controls.train_tail_sft \
        --triples data/train_triples.jsonl \
        --base /ckpt/qwen3.5-9b-base \
        --anchors data/anchor_pairs.jsonl \
        --plan plans/E2_tail_sft.json \
        --out-dir runs/tail_recovery_sft_seed13 \
        --seed 13

The submitted factorial shows two things at *uniform* aggregation: same-state
DPO beats recovery SFT (26.1 vs 37.4 on S1), and, holding DPO, the top-2 rule
beats uniform (20.2 vs 26.1). It never crosses the two, so it cannot rule out
that CURE-DPO's edge over Recovery SFT is really the aggregation, not the
objective. ptEw asked for exactly that cell.

This trainer isolates the objective by changing *only* it. Everything else is
the CURE-DPO recipe:

    * same six states per prompt, same frozen recovery/harmful branches;
    * the same detached top-K selection over per-state losses (K from the plan);
    * the same clean-safety and benign anchors at the same weights;
    * the same optimizer, LR, effective batch, step budget, and seeds.

Two selection modes, both defensible, decided in the plan not here:

    loss_topk         select the K states with the largest *SFT* loss each step.
                      This is the honest "SFT with lower-tail selection" method.
    replay_indices    replay, step for step, the exact state indices the matched
                      CURE-DPO run selected. This removes even the "different
                      states were selected" degree of freedom, at the cost of
                      needing the CURE run's selection log.

Only the per-state loss differs from CURE-DPO: recovery-token NLL on r_t instead
of the DPO preference between r_t and u_t. The harmful branch is therefore unused
by the loss under ``loss_topk`` (it still defines the pair for bookkeeping); this
is the whole point -- SFT never sees the competing harmful future.

Heavy deps (torch, transformers) are imported inside ``run`` so ``--dry-run``
validates the plan, data, and step math on a laptop.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .common import Prereg, Provenance, fingerprint_checkpoint, load_jsonl


def _validate_triples(triples: list[dict[str, Any]], states_per_prompt: int) -> dict[str, Any]:
    by_prompt: dict[str, list[dict[str, Any]]] = {}
    for triple in triples:
        for field in ("prompt_id", "state_id", "state_text", "recovery_branch"):
            if field not in triple:
                raise SystemExit(f"triple missing {field!r}: {triple.get('state_id')}")
        by_prompt.setdefault(triple["prompt_id"], []).append(triple)

    bad = {pid: len(v) for pid, v in by_prompt.items() if len(v) != states_per_prompt}
    if bad:
        sample = dict(list(bad.items())[:5])
        raise SystemExit(
            f"{len(bad)} prompts do not have exactly {states_per_prompt} states, "
            f"e.g. {sample}. Tail selection assumes a fixed state count per prompt."
        )
    return by_prompt


def run(args: argparse.Namespace) -> int:
    prereg = Prereg.load(args.plan)
    objective = prereg.require("objective")
    if objective != "tail_recovery_sft":
        raise SystemExit(
            f"plan objective is {objective!r}, expected 'tail_recovery_sft'. "
            "Use the E2 plan, not the DPO plan."
        )
    selection_mode = prereg.require("selection", "mode")  # loss_topk | replay_indices
    top_k = int(prereg.require("selection", "top_k"))
    states_per_prompt = int(prereg.require("states_per_prompt"))
    hp = prereg.require("optimization")

    triples = load_jsonl(args.triples)
    by_prompt = _validate_triples(triples, states_per_prompt)

    replay = None
    if selection_mode == "replay_indices":
        if not args.selection_log:
            raise SystemExit(
                "selection mode 'replay_indices' needs --selection-log from the "
                "matched CURE-DPO run (its per-step chosen state_ids)."
            )
        replay = load_jsonl(args.selection_log)

    prov = Provenance(stage="train_tail_sft")
    prov.record_input("triples", args.triples)
    if args.anchors:
        prov.record_input("anchors", args.anchors)
    if args.selection_log:
        prov.record_input("selection_log", args.selection_log)
    prov.checkpoints["base"] = fingerprint_checkpoint(args.base, mode=args.fingerprint)
    prov.prereg = prereg.as_record()
    prov.config.update(
        {
            "selection_mode": selection_mode,
            "top_k": top_k,
            "states_per_prompt": states_per_prompt,
            "seed": args.seed,
            "optimization": hp,
        }
    )
    prov.counts.update({"prompts": len(by_prompt), "triples": len(triples)})

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        eff_batch = hp["effective_batch"]
        steps = hp["max_steps"]
        print("dry run OK")
        print(f"  prompts:            {len(by_prompt)}")
        print(f"  states/prompt:      {states_per_prompt}")
        print(f"  selection:          {selection_mode} (top_k={top_k})")
        print(f"  effective batch:    {eff_batch}")
        print(f"  planned steps:      {steps}")
        print(f"  LR / seed:          {hp['learning_rate']} / {args.seed}")
        print("  (no weights loaded; rerun without --dry-run on the cluster)")
        prov.write(out_dir / "dry_run")
        return 0

    import torch
    from torch.nn import functional as F
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        get_cosine_schedule_with_warmup,
        set_seed,
    )

    set_seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(args.base, revision=args.revision)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.base, torch_dtype=torch.bfloat16, device_map="auto", revision=args.revision
    )
    model.gradient_checkpointing_enable()
    model.train()
    device = next(model.parameters()).device

    def recovery_nll(state_text: str, recovery: str) -> "torch.Tensor":
        """Length-normalized NLL of the recovery branch given the reached state.

        Same teacher-forced boundary handling as the scorer: only recovery
        tokens carry loss, and the state prefix is masked by slicing rather than
        by a labels=-100 trick, so a tokenizer seam cannot leak state tokens in.
        """
        prefix_ids = tokenizer(state_text, add_special_tokens=False).input_ids
        full_ids = tokenizer(state_text + recovery, add_special_tokens=False).input_ids
        boundary = len(prefix_ids)
        if full_ids[:boundary] != prefix_ids:
            boundary = 0
            for a, b in zip(prefix_ids, full_ids):
                if a != b:
                    break
                boundary += 1
        ids = torch.tensor(full_ids, dtype=torch.long, device=device).unsqueeze(0)
        logits = model(ids).logits[0].float()
        targets = ids[0, boundary:]
        picked = F.log_softmax(logits[boundary - 1 : len(full_ids) - 1], dim=-1).gather(
            -1, targets.unsqueeze(-1)
        ).squeeze(-1)
        return -picked.mean()

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=hp["learning_rate"],
        betas=tuple(hp.get("betas", (0.9, 0.95))),
        weight_decay=hp.get("weight_decay", 0.0),
    )
    scheduler = get_cosine_schedule_with_warmup(
        optimizer, hp.get("warmup_steps", 0), hp["max_steps"]
    )

    anchors = load_jsonl(args.anchors) if args.anchors else []
    lambda_c = prereg.require("anchors", "lambda_clean")
    lambda_b = prereg.require("anchors", "lambda_benign")

    prompt_ids = list(by_prompt.keys())
    rng = torch.Generator().manual_seed(args.seed)
    step = 0
    log: list[dict[str, Any]] = []

    while step < hp["max_steps"]:
        order = torch.randperm(len(prompt_ids), generator=rng).tolist()
        for pointer in order:
            if step >= hp["max_steps"]:
                break
            pid = prompt_ids[pointer]
            states = by_prompt[pid]

            per_state_loss = torch.stack([
                recovery_nll(s["state_text"], s["recovery_branch"]) for s in states
            ])

            if selection_mode == "loss_topk":
                chosen = torch.topk(per_state_loss.detach(), k=top_k).indices.tolist()
            else:  # replay_indices
                chosen_ids = replay[step].get("chosen_state_ids") if step < len(replay) else None
                if chosen_ids is None:
                    raise SystemExit(f"selection log has no entry for step {step}")
                id_to_pos = {s["state_id"]: i for i, s in enumerate(states)}
                chosen = [id_to_pos[c] for c in chosen_ids if c in id_to_pos]
                if not chosen:
                    raise SystemExit(
                        f"step {step}: none of the replayed state ids match prompt {pid}; "
                        "the selection log and triples are misaligned."
                    )

            tail_loss = per_state_loss[chosen].mean()
            loss = tail_loss
            # Anchors are the same objective form as the paper's, applied to
            # root-conditioned pairs, and not subject to the top-k mask.
            if anchors and (lambda_c or lambda_b):
                anchor = anchors[step % len(anchors)]
                if lambda_c and "clean_state_text" in anchor:
                    loss = loss + lambda_c * recovery_nll(
                        anchor["clean_state_text"], anchor["clean_safe_branch"]
                    )
                if lambda_b and "benign_state_text" in anchor:
                    loss = loss + lambda_b * recovery_nll(
                        anchor["benign_state_text"], anchor["benign_target"]
                    )

            loss.backward()
            if hp.get("grad_clip"):
                torch.nn.utils.clip_grad_norm_(model.parameters(), hp["grad_clip"])
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad(set_to_none=True)

            if step % args.log_every == 0:
                log.append(
                    {
                        "step": step,
                        "prompt_id": pid,
                        "tail_loss": float(tail_loss.item()),
                        "chosen_positions": chosen,
                        "chosen_state_ids": [states[i]["state_id"] for i in chosen],
                    }
                )
            step += 1

    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)
    (out_dir / "training_log.jsonl").write_text(
        "".join(json.dumps(entry) + "\n" for entry in log), encoding="utf-8"
    )
    prov.counts["steps_run"] = step
    prov.write(out_dir / "checkpoint")
    print(f"saved Tail-Recovery-SFT ({selection_mode}) checkpoint -> {out_dir}")
    print("Evaluate with the SAME S1-S4 harness used for the main table, then")
    print("form the paired CURE - Tail-SFT contrast on S1 and S3.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--triples", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--anchors", default=None)
    parser.add_argument("--selection-log", default=None,
                        help="matched CURE-DPO per-step selection, for replay_indices")
    parser.add_argument("--revision", default=None)
    parser.add_argument("--fingerprint", choices=("full", "fast"), default="full")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--log-every", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true",
                        help="validate plan/data/step math without loading weights")
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
