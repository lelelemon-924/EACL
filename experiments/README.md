# Rebuttal control experiments — Plan A runbook

Three experiments answering the concrete objections in the reviews, ordered by
cost. E1 and E3 are inference-only and fit comfortably in the window; E2 is one
training run and is the stretch goal.

| ID | Question it settles | Reviewer | Model work | Wall-clock* |
|----|--------------------|----------|-----------|-------------|
| E1 | Does the same-state preference track **safety** or continuation **register**? | ptEw | scoring only (+ one restyle gen) | ~0.5 day |
| E3 | Does same-state training **abandon benign long-form tasks** mid-generation? | ptEw, FaVn | generation + your refusal judge | ~1 day |
| E2 | The missing **Recovery-SFT-with-lower-tail** cell | ptEw | one SFT run + your S1–S4 eval | ~2–3 days |

\* On 1×A100-80G for a 9B model. Scale by your hardware.

Everything writes a `*.provenance.json` sidecar (checkpoint fingerprints, git
commit, argv, library versions) and every analysis is gated on a **locked**
plan. A results file without its sidecar, or produced from an edited plan, is
not citable — that is the point.

---

## What you must supply (input contract)

These scripts do the scoring, generation, statistics, provenance, and gating.
They deliberately do **not** re-implement your judges, your S1–S4 attack suites,
or invent data. You point them at:

### Checkpoints (local paths or pinned Hub revisions)
- `Base` (the frozen, untrained base — same one that generated the pair pool)
- `Recovery SFT`, `Uniform Same-State DPO`, `CURE-DPO` (seed you report)
- `W-DOOR` (for E3 only, optional)

### Data files (JSONL, one object per line)

`data/heldout_states.jsonl` — reached states from **held-out** prompts, disjoint
from training/mining. One object per state:
```json
{"state_id": "s0001", "prompt_id": "hb_0042", "source": "harmbench",
 "depth_tokens": 96,
 "conversation": [{"role": "user", "content": "..."}],
 "assistant_prefix": "First, you will need to ",
 "recovery_branch": "I can't help with that. ...",
 "harmful_branch": "gather the following materials ..."}
```
`recovery_branch` / `harmful_branch` are the **frozen** branches already in your
pair pool. `conversation` + `assistant_prefix` must render to the exact reached
state the pool was built from.

`data/benign_longform_prompts.jsonl` — benign prompts that pass through
risk-adjacent territory (defensive security, medical, legal, long-form writing):
```json
{"prompt_id": "b0001", "category": "defensive_security_technical",
 "conversation": [{"role": "user", "content": "Explain how TLS certificate pinning works ..."}]}
```

`data/train_triples.jsonl` (E2 only) — the exact same six states per prompt used
to train CURE-DPO:
```json
{"prompt_id": "p001", "state_id": "p001_s3", "state_text": "<rendered reached state>",
 "recovery_branch": "...", "harmful_branch": "..."}
```

`data/anchor_pairs.jsonl` (E2 only) — clean-safety and benign anchors at the
paper's weights:
```json
{"clean_state_text": "...", "clean_safe_branch": "...",
 "benign_state_text": "...", "benign_target": "..."}
```

### Judges you already have (not re-implemented here)
- **Safety/refusal classifier** (WildGuard response-refusal field — the paper's).
- **Intent-preservation / NLI** check for restyled text (E1).
- **S1–S4 attack + judge harness** (E2 evaluation), used unchanged.

---

## Zero: environment + lock the plans (do this first, and commit)

```bash
cd experiments
python -m pip install torch transformers vllm numpy scipy   # cluster
# analysis-only machine needs just numpy (+scipy)

# Lock every plan BEFORE producing any result, then commit the locks.
python -m cure_controls.common lock plans/E1_style_control.json
python -m cure_controls.common lock plans/E2_tail_sft.json
python -m cure_controls.common lock plans/E3_benign_longform.json
git add plans/*.json plans/*.lock && git commit -m "Lock rebuttal analysis plans"
```

The lock stores a hash of the plan. If you later edit a margin or an inclusion
rule, every `analyze`/`finalize` refuses to run until you restore it — so a
number cannot be chosen after seeing results. Fill the two placeholders in
`plans/E2_tail_sft.json` first (`optimization.max_steps` = the matched CURE-DPO
step budget; confirm `learning_rate`), *then* lock.

Sanity-check the machinery on synthetic data (no GPU, no real data):
```bash
python tests/test_common.py
```

---

## E1 — Safety vs register (inference-only)

```bash
# 1. Synthesise the two counterfactual cells (safe-in-harmful-register and
#    harmful-in-recovery-register). Local model only; never a hosted API.
python -m cure_controls.build_style_pairs generate \
    --states data/heldout_states.jsonl \
    --restyle-model /ckpt/qwen3.5-9b-base \
    --out work/style_candidates.jsonl

# 2. Run YOUR safety classifier + NLI over the restyled cells, plus a blinded
#    human audit, producing:
#      work/style_verdicts.jsonl   {state_id, cell, is_safe, intent_preserved}
#      work/style_audit.csv        state_id,cell,safety_ok,intent_ok,coherence_ok
# 3. Keep only complete, screened 2x2 quartets:
python -m cure_controls.build_style_pairs finalize \
    --candidates work/style_candidates.jsonl \
    --verdicts work/style_verdicts.jsonl \
    --audit-labels work/style_audit.csv \
    --plan plans/E1_style_control.json \
    --out work/style_pairs.jsonl

# 4. Score the quartet on each checkpoint, then decompose.
for CK in Base "Recovery SFT" "Uniform Same-State DPO" CURE-DPO; do
  python -m cure_controls.score_style_factorial score \
      --pairs work/style_pairs.jsonl --states data/heldout_states.jsonl \
      --checkpoint /ckpt/${CK// /-} --name "$CK" \
      --out "work/style_scores.${CK// /-}.jsonl"
  python -m cure_controls.score_style_factorial analyze \
      --scores "work/style_scores.${CK// /-}.jsonl" \
      --plan plans/E1_style_control.json \
      --out "work/style_effects.${CK// /-}.json"
done
```

**Read**: `safety_effect_holding_register` should be large with a CI excluding 0;
`register_effect_holding_safety` should be small. If register is comparable, the
plan tells you to narrow the claim rather than hide it.

---

## E3 — Benign long-form mid-generation (inference-only)

```bash
for CK in Base "Recovery SFT" "Uniform Same-State DPO" W-DOOR CURE-DPO; do
  python -m cure_controls.benign_longform generate \
      --prompts data/benign_longform_prompts.jsonl \
      --checkpoint /ckpt/${CK// /-} --name "$CK" --engine vllm \
      --out "work/benign.${CK// /-}.jsonl"
done

# Judge refusal ONSET spans with your WildGuard-refusal harness over each
#   work/benign.<CK>.judge_queue.jsonl, emitting
#   work/benign.<CK>.refusal.jsonl  {prompt_id, began_benign, refusal_onset_token, onset_boundary}

# Analyze Base first (it becomes the paired baseline), then each model vs Base.
python -m cure_controls.benign_longform analyze \
    --generations work/benign.Base.jsonl --refusal-labels work/benign.Base.refusal.jsonl \
    --plan plans/E3_benign_longform.json --out work/benign.Base.analysis.json
for CK in "Recovery SFT" "Uniform Same-State DPO" W-DOOR CURE-DPO; do
  python -m cure_controls.benign_longform analyze \
      --generations "work/benign.${CK// /-}.jsonl" \
      --refusal-labels "work/benign.${CK// /-}.refusal.jsonl" \
      --baseline work/benign.Base.analysis.json \
      --plan plans/E3_benign_longform.json \
      --out "work/benign.${CK// /-}.analysis.json"
done
```

**Read**: the pre-registered non-inferiority test (margins in the plan) prints
PASS/FAIL for unnecessary-refusal and completion vs Base.

---

## E2 — Tail-Recovery-SFT (one training run; stretch goal)

```bash
# Validate plan/data/step math with no GPU first:
python -m cure_controls.train_tail_sft \
    --triples data/train_triples.jsonl --base /ckpt/qwen3.5-9b-base \
    --anchors data/anchor_pairs.jsonl --plan plans/E2_tail_sft.json \
    --out-dir runs/tail_recovery_sft_seed13 --seed 13 --dry-run

# Then the real run (drop --dry-run). Single seed is acceptable for the rebuttal;
# the plan says to label it as such and add seeds for camera-ready.
python -m cure_controls.train_tail_sft \
    --triples data/train_triples.jsonl --base /ckpt/qwen3.5-9b-base \
    --anchors data/anchor_pairs.jsonl --plan plans/E2_tail_sft.json \
    --out-dir runs/tail_recovery_sft_seed13 --seed 13
```

Evaluate `runs/tail_recovery_sft_seed13` with the **same** S1–S4 harness and judge
as the main table. The claim rests on the **paired CURE-DPO − Tail-SFT** gap on
S1/S3: a gap that survives says the pairwise objective adds something beyond
lower-tail selection; a gap that closes says it was mostly the aggregation, and
the plan commits you to reporting that either way.

---

## What is deliberately NOT automated

- **Judging.** Safety, intent-preservation, refusal-onset, and the S1–S4 verdicts
  come from your existing judges. Automating them here would just hide their
  assumptions.
- **Sampling more when the result is weak.** Achieved `n` and acceptance yield are
  reported; the plans forbid topping up after margins are visible.
- **Any number without a run.** Nothing interpolates, targets, or fabricates a
  result. If a run doesn't finish before the deadline, report what finished and
  say the rest is in progress — a smaller honest table beats a full invented one,
  and it is the version that survives the camera-ready check.
```
