"""Self-contained checks on the statistics and gating logic.

These validate the *code*, not any experiment: they run on synthetic arrays and
a throwaway plan file. Run with:  python -m pytest experiments/tests -q
or standalone:                     python experiments/tests/test_common.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cure_controls.common import (  # noqa: E402
    Prereg,
    PreregError,
    cluster_bootstrap_mean,
    wilson_interval,
)


def test_bootstrap_recovers_mean():
    rng = np.random.default_rng(0)
    values = rng.normal(0.5, 1.0, size=2000)
    clusters = np.arange(2000)  # one obs per cluster => ordinary bootstrap
    est = cluster_bootstrap_mean(values, clusters, replicates=2000, seed=1)
    assert abs(est.value - values.mean()) < 1e-9
    assert est.low < values.mean() < est.high
    assert est.n_clusters == 2000


def test_clustering_widens_interval():
    """Six correlated observations per prompt must not be treated as six
    independent ones. The clustered interval should be materially wider than the
    naive one when within-cluster correlation is high."""
    rng = np.random.default_rng(2)
    n_prompts = 150
    states = 6
    values, clustered_ids, naive_ids = [], [], []
    counter = 0
    for p in range(n_prompts):
        prompt_effect = rng.normal(0, 1.0)  # strong between-prompt variance
        for _ in range(states):
            values.append(prompt_effect + rng.normal(0, 0.1))
            clustered_ids.append(f"p{p}")
            naive_ids.append(f"obs{counter}")
            counter += 1

    clustered = cluster_bootstrap_mean(values, clustered_ids, replicates=3000, seed=3)
    naive = cluster_bootstrap_mean(values, naive_ids, replicates=3000, seed=3)
    clustered_width = clustered.high - clustered.low
    naive_width = naive.high - naive.low
    # With variance concentrated between prompts, ignoring clustering understates
    # uncertainty by roughly the sqrt(states-per-prompt) design effect (~2.45 for
    # 6 states). Require the clustered interval at least 2x wider.
    assert clustered_width > 2 * naive_width, (clustered_width, naive_width)


def test_paired_difference_sign():
    """A uniformly positive per-observation difference yields an interval that
    excludes zero on the positive side (used by the non-inferiority test)."""
    diffs = [0.05] * 400
    ids = [f"p{i//4}" for i in range(400)]
    est = cluster_bootstrap_mean(diffs, ids, replicates=1000, seed=4)
    assert est.low > 0
    assert est.excludes_zero()


def test_wilson_interval_bounds():
    lo, hi = wilson_interval(90, 100)
    assert 0.0 <= lo < 0.9 < hi <= 1.0
    assert wilson_interval(0, 0) == (0.0, 0.0)


def test_prereg_lock_and_tamper():
    with tempfile.TemporaryDirectory() as tmp:
        plan_path = Path(tmp) / "plan.json"
        plan_path.write_text(json.dumps({"experiment": "x", "acceptance": {}}), encoding="utf-8")

        Prereg.lock(plan_path)
        loaded = Prereg.load(plan_path)
        assert loaded.plan["experiment"] == "x"

        # Editing the plan after locking must fail the load.
        plan_path.write_text(json.dumps({"experiment": "x", "acceptance": {"cheat": 1}}), encoding="utf-8")
        try:
            Prereg.load(plan_path)
        except PreregError:
            pass
        else:  # pragma: no cover
            raise AssertionError("tampered plan was not rejected")


def test_prereg_requires_lock_first():
    with tempfile.TemporaryDirectory() as tmp:
        plan_path = Path(tmp) / "plan.json"
        plan_path.write_text(json.dumps({"experiment": "y"}), encoding="utf-8")
        try:
            Prereg.load(plan_path)
        except PreregError:
            pass
        else:  # pragma: no cover
            raise AssertionError("load without a lock should fail")


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as exc:
                failed += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(failed)
