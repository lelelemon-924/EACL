"""Model access: teacher-forced continuation scoring, and long-form generation.

Two traps are handled explicitly here because both produce plausible-looking
numbers when they go wrong.

**The tokenizer boundary.** Scoring a continuation ``y`` from a reached state
``s`` means summing ``log pi(y_j | s, y_<j)``, which requires knowing where
``s`` ends in the token sequence. Tokenizing ``s`` and ``s + y`` separately does
not guarantee that the second is a prefix-extension of the first: BPE merges
across the seam whenever the last character of ``s`` and the first of ``y`` form
a frequent pair, so ``"First,"`` + ``" you"`` can retokenize the boundary and
shift every index by one. Scoring from a wrong offset silently includes a state
token in the branch score, which inflates or deflates margins by a token's worth
of log-probability. ``score_continuations`` asserts prefix agreement, falls back
to the longest common token prefix when it fails, and reports the count of
fallbacks so the analysis can state it.

**Thinking mode.** Qwen3.5 emits a reasoning block by default, and that block
would appear *before* the assistant prefix that defines the reached state, which
changes the state being conditioned on. The paper's evaluation runs with
``enable_thinking=False`` throughout, so it is the default here and every call
records which setting was used.

``torch`` and ``transformers`` are imported lazily so the analysis scripts run on
a laptop with neither installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

DEFAULT_DTYPE = "bfloat16"


@dataclass
class ScoredContinuation:
    """One teacher-forced score. ``avg_logprob`` is Eq. 3 in the paper."""

    sum_logprob: float
    n_tokens: int
    avg_logprob: float
    boundary_exact: bool
    prefix_tokens: int


def _resolve_dtype(name: str):
    import torch

    return {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }[name]


class HFModel:
    """A frozen checkpoint used for scoring and, optionally, generation."""

    def __init__(
        self,
        path: str,
        dtype: str = DEFAULT_DTYPE,
        device_map: str = "auto",
        enable_thinking: bool = False,
        revision: str | None = None,
    ) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.path = path
        self.enable_thinking = enable_thinking
        self.tokenizer = AutoTokenizer.from_pretrained(path, revision=revision)
        self.model = AutoModelForCausalLM.from_pretrained(
            path,
            torch_dtype=_resolve_dtype(dtype),
            device_map=device_map,
            revision=revision,
        )
        self.model.eval()
        self._torch = torch
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    # -- prompt assembly ---------------------------------------------------

    def render_state(
        self, conversation: Sequence[dict[str, str]], assistant_prefix: str = ""
    ) -> str:
        """Render ``s_t = x + h_<=t`` as the exact string the model conditions on.

        ``add_generation_prompt=True`` opens the assistant turn; the reached
        state's assistant-side history is then appended verbatim, so the string
        ends mid-turn exactly as it does under a prefill attack.
        """
        kwargs: dict[str, Any] = {"tokenize": False, "add_generation_prompt": True}
        try:
            rendered = self.tokenizer.apply_chat_template(
                list(conversation), enable_thinking=self.enable_thinking, **kwargs
            )
        except TypeError:
            # Templates that predate the thinking flag reject the kwarg.
            rendered = self.tokenizer.apply_chat_template(list(conversation), **kwargs)
        return rendered + assistant_prefix

    # -- scoring -----------------------------------------------------------

    def score_continuations(
        self,
        items: Sequence[tuple[str, str]],
        batch_size: int = 8,
    ) -> list[ScoredContinuation]:
        """Score each ``(state_text, continuation)`` pair.

        Only continuation tokens contribute. Padding is right-hand and masked
        out by construction, since every score is gathered from an explicit
        token span rather than from a reduction over the whole row.
        """
        torch = self._torch
        results: list[ScoredContinuation] = []

        for start in range(0, len(items), batch_size):
            batch = items[start : start + batch_size]
            spans = []
            for state_text, continuation in batch:
                prefix_ids = self.tokenizer(
                    state_text, add_special_tokens=False
                ).input_ids
                full_ids = self.tokenizer(
                    state_text + continuation, add_special_tokens=False
                ).input_ids

                exact = full_ids[: len(prefix_ids)] == prefix_ids
                if exact:
                    boundary = len(prefix_ids)
                else:
                    boundary = 0
                    for a, b in zip(prefix_ids, full_ids):
                        if a != b:
                            break
                        boundary += 1
                if len(full_ids) <= boundary:
                    raise ValueError(
                        "continuation contributes no tokens; check for an empty "
                        f"branch in the record ending {state_text[-60:]!r}"
                    )
                spans.append((full_ids, boundary, exact, len(prefix_ids)))

            width = max(len(ids) for ids, _, _, _ in spans)
            pad_id = self.tokenizer.pad_token_id
            input_ids = torch.full((len(spans), width), pad_id, dtype=torch.long)
            attention = torch.zeros((len(spans), width), dtype=torch.long)
            for row, (ids, _, _, _) in enumerate(spans):
                input_ids[row, : len(ids)] = torch.tensor(ids, dtype=torch.long)
                attention[row, : len(ids)] = 1

            device = next(self.model.parameters()).device
            with torch.no_grad():
                logits = self.model(
                    input_ids=input_ids.to(device),
                    attention_mask=attention.to(device),
                ).logits.float()
                logprobs = torch.log_softmax(logits, dim=-1)

            for row, (ids, boundary, exact, prefix_len) in enumerate(spans):
                # Position j predicts token j+1, so the score of token t reads
                # from logits at t-1.
                targets = torch.tensor(ids[boundary:], dtype=torch.long, device=device)
                picked = logprobs[row, boundary - 1 : len(ids) - 1, :].gather(
                    -1, targets.unsqueeze(-1)
                ).squeeze(-1)
                total = float(picked.sum().item())
                count = int(targets.numel())
                results.append(
                    ScoredContinuation(
                        sum_logprob=total,
                        n_tokens=count,
                        avg_logprob=total / count,
                        boundary_exact=bool(exact),
                        prefix_tokens=prefix_len,
                    )
                )

        return results

    # -- generation --------------------------------------------------------

    def generate(
        self,
        prompts: Sequence[str],
        max_new_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        seed: int,
        batch_size: int = 4,
    ) -> list[dict[str, Any]]:
        torch = self._torch
        from transformers import set_seed

        set_seed(seed)
        self.tokenizer.padding_side = "left"
        outputs: list[dict[str, Any]] = []
        device = next(self.model.parameters()).device

        for start in range(0, len(prompts), batch_size):
            batch = list(prompts[start : start + batch_size])
            encoded = self.tokenizer(
                batch, return_tensors="pt", padding=True, add_special_tokens=False
            ).to(device)
            with torch.no_grad():
                generated = self.model.generate(
                    **encoded,
                    max_new_tokens=max_new_tokens,
                    do_sample=temperature > 0,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
            prompt_width = encoded["input_ids"].shape[1]
            for row in range(len(batch)):
                new_ids = generated[row, prompt_width:].tolist()
                if self.tokenizer.eos_token_id in new_ids:
                    stop = new_ids.index(self.tokenizer.eos_token_id)
                    hit_eos = True
                    new_ids = new_ids[:stop]
                else:
                    hit_eos = False
                outputs.append(
                    {
                        "text": self.tokenizer.decode(new_ids, skip_special_tokens=True),
                        "n_tokens": len(new_ids),
                        "hit_eos": hit_eos,
                        "truncated_at_limit": not hit_eos,
                    }
                )
        return outputs


class VLLMGenerator:
    """Generation only. Roughly an order of magnitude faster than HF for 1k+
    token completions, which is what makes the benign long-form suite fit in an
    afternoon. Scoring stays on ``HFModel`` because an explicit teacher-forced
    span is easier to verify than prompt-logprob bookkeeping."""

    def __init__(
        self,
        path: str,
        dtype: str = DEFAULT_DTYPE,
        tensor_parallel_size: int = 1,
        max_model_len: int | None = None,
        enable_thinking: bool = False,
        revision: str | None = None,
    ) -> None:
        from transformers import AutoTokenizer
        from vllm import LLM

        self.path = path
        self.enable_thinking = enable_thinking
        self.tokenizer = AutoTokenizer.from_pretrained(path, revision=revision)
        self.llm = LLM(
            model=path,
            dtype=dtype,
            tensor_parallel_size=tensor_parallel_size,
            max_model_len=max_model_len,
            revision=revision,
        )

    def render_state(
        self, conversation: Sequence[dict[str, str]], assistant_prefix: str = ""
    ) -> str:
        kwargs: dict[str, Any] = {"tokenize": False, "add_generation_prompt": True}
        try:
            rendered = self.tokenizer.apply_chat_template(
                list(conversation), enable_thinking=self.enable_thinking, **kwargs
            )
        except TypeError:
            rendered = self.tokenizer.apply_chat_template(list(conversation), **kwargs)
        return rendered + assistant_prefix

    def generate(
        self,
        prompts: Sequence[str],
        max_new_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        seed: int,
        batch_size: int | None = None,
    ) -> list[dict[str, Any]]:
        from vllm import SamplingParams

        params = SamplingParams(
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k if top_k > 0 else -1,
            seed=seed,
        )
        completions = self.llm.generate(list(prompts), params)
        outputs = []
        for completion in completions:
            best = completion.outputs[0]
            outputs.append(
                {
                    "text": best.text,
                    "n_tokens": len(best.token_ids),
                    "hit_eos": best.finish_reason == "stop",
                    "truncated_at_limit": best.finish_reason == "length",
                }
            )
        return outputs


def load_generator(
    path: str,
    engine: str,
    dtype: str = DEFAULT_DTYPE,
    tensor_parallel_size: int = 1,
    max_model_len: int | None = None,
    enable_thinking: bool = False,
    revision: str | None = None,
):
    if engine == "vllm":
        return VLLMGenerator(
            path,
            dtype=dtype,
            tensor_parallel_size=tensor_parallel_size,
            max_model_len=max_model_len,
            enable_thinking=enable_thinking,
            revision=revision,
        )
    if engine == "hf":
        return HFModel(
            path, dtype=dtype, enable_thinking=enable_thinking, revision=revision
        )
    raise ValueError(f"unknown engine {engine!r}; expected 'vllm' or 'hf'")
