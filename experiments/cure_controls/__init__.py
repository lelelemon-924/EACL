"""Rebuttal control experiments for CURE-DPO (EACL / ARR August 2026).

Three harnesses, each targeting a specific reviewer concern:

* ``build_style_pairs`` + ``score_style_factorial`` (E1) -- does the same-state
  preference track safety or continuation register? (ptEw)
* ``benign_longform`` (E3) -- does same-state training abandon a benign task
  mid-generation? (ptEw, FaVn)
* ``train_tail_sft`` (E2) -- the missing Recovery-SFT-with-lower-tail cell.
  (ptEw)

``common`` holds provenance capture, pre-registration locking, and the
prompt-clustered bootstrap shared by all three. ``backends`` holds
teacher-forced scoring and long-form generation.

Design rule for the whole package: these scripts produce and analyze REAL model
outputs. None of them fabricates, targets, or interpolates a result. Numbers
enter the rebuttal only after running against real checkpoints and passing the
locked analysis plan.
"""

__all__ = [
    "common",
    "backends",
    "build_style_pairs",
    "score_style_factorial",
    "benign_longform",
    "train_tail_sft",
]
