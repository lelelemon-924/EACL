"""Provenance capture, pre-registration gating, and clustered resampling.

Every number these harnesses emit has to survive a reviewer asking "where did
this come from" three weeks after the fact, so three things are enforced here
rather than left to discipline:

* **Provenance.** Each stage writes a sidecar ``*.provenance.json`` recording
  the resolved checkpoint fingerprints, the git commit, the full argv, and the
  library versions. A results file without its sidecar is not citable.

* **Pre-registration.** ``Prereg.load`` refuses to run an analysis whose plan
  file has changed since it was locked. This does not by itself prove the plan
  predates the results -- only the git history does that, which is why the
  runbook has you commit the lock file before any scoring job starts. What the
  gate does buy is that an *accidental* post-hoc edit to a margin or an
  inclusion rule fails loudly instead of silently changing a conclusion.

* **Clustering.** The unit of analysis is a (prompt, state) observation, but
  observations nest inside prompts, so the bootstrap resamples prompts and
  carries all of a prompt's observations together. Resampling observations
  independently understates the interval, and with six states per prompt the
  understatement is not small.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

# Weight files worth hashing when fingerprinting a checkpoint directory. The
# tokenizer and config are included because a tokenizer change silently moves
# every teacher-forced score, which is exactly the kind of drift that makes two
# runs disagree for no visible reason.
FINGERPRINT_GLOBS = (
    "*.safetensors",
    "*.bin",
    "config.json",
    "generation_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
)


# ---------------------------------------------------------------------------
# JSONL IO
# ---------------------------------------------------------------------------

def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records = []
    with open(path, "r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: {exc}") from exc
    return records


def write_jsonl(path: str | Path, records: Iterable[dict[str, Any]]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def iter_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


# ---------------------------------------------------------------------------
# Hashing and provenance
# ---------------------------------------------------------------------------

def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while block := handle.read(chunk):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint_checkpoint(path: str, mode: str = "full") -> dict[str, Any]:
    """Identify a checkpoint well enough to prove two runs used the same one.

    ``mode="full"`` hashes the weights, which for a 9B checkpoint means reading
    roughly 18 GB and costs tens of seconds. ``mode="fast"`` records only sizes,
    which catches an accidentally swapped path but not a silently rewritten
    weight file. A Hub id with no local directory is recorded as-is; pin the
    revision in that case, because ``main`` moves.
    """
    resolved = Path(path)
    if not resolved.exists():
        return {"path": path, "kind": "hub_id_or_missing_path", "mode": mode}

    if resolved.is_file():
        entry = {"path": str(resolved), "kind": "file", "size": resolved.stat().st_size}
        if mode == "full":
            entry["sha256"] = sha256_file(resolved)
        return entry

    files = []
    for pattern in FINGERPRINT_GLOBS:
        files.extend(sorted(resolved.glob(pattern)))
    entries = []
    for item in sorted(set(files)):
        record = {"name": item.name, "size": item.stat().st_size}
        if mode == "full":
            record["sha256"] = sha256_file(item)
        entries.append(record)

    summary = sha256_text(json.dumps(entries, sort_keys=True))
    return {
        "path": str(resolved),
        "kind": "directory",
        "mode": mode,
        "files": entries,
        "directory_digest": summary,
    }


def git_commit() -> dict[str, Any]:
    def run(*args: str) -> str | None:
        try:
            out = subprocess.run(
                args, cwd=REPO_ROOT, capture_output=True, text=True, timeout=15
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return out.stdout.strip() if out.returncode == 0 else None

    commit = run("git", "rev-parse", "HEAD")
    if commit is None:
        return {"available": False}
    dirty = run("git", "status", "--porcelain")
    return {
        "available": True,
        "commit": commit,
        "branch": run("git", "rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(dirty),
    }


def library_versions() -> dict[str, str]:
    versions = {"python": platform.python_version(), "numpy": np.__version__}
    for name in ("torch", "transformers", "vllm", "scipy"):
        try:
            module = __import__(name)
        except ImportError:
            continue
        versions[name] = getattr(module, "__version__", "unknown")
    return versions


@dataclass
class Provenance:
    """The sidecar written next to every artifact these scripts produce."""

    stage: str
    argv: list[str] = field(default_factory=lambda: list(sys.argv))
    started_at: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z")
    )
    git: dict[str, Any] = field(default_factory=git_commit)
    libraries: dict[str, str] = field(default_factory=library_versions)
    host: str = field(default_factory=platform.node)
    inputs: dict[str, Any] = field(default_factory=dict)
    checkpoints: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    counts: dict[str, Any] = field(default_factory=dict)
    prereg: dict[str, Any] | None = None

    def record_input(self, label: str, path: str | Path, hash_file: bool = True) -> None:
        path = Path(path)
        entry: dict[str, Any] = {"path": str(path)}
        if path.exists() and path.is_file():
            entry["size"] = path.stat().st_size
            if hash_file:
                entry["sha256"] = sha256_file(path)
        else:
            entry["missing"] = True
        self.inputs[label] = entry

    def write(self, artifact: str | Path) -> Path:
        sidecar = Path(str(artifact) + ".provenance.json")
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        payload["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        sidecar.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return sidecar


# ---------------------------------------------------------------------------
# Pre-registration
# ---------------------------------------------------------------------------

class PreregError(SystemExit):
    pass


@dataclass
class Prereg:
    path: Path
    plan: dict[str, Any]
    plan_sha256: str
    locked_at: str

    @property
    def statistics(self) -> dict[str, Any]:
        return self.plan.get("statistics", {})

    def require(self, *keys: str) -> Any:
        node: Any = self.plan
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                raise PreregError(
                    f"{self.path}: plan is missing required field {'.'.join(keys)!r}"
                )
            node = node[key]
        return node

    def as_record(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "plan_sha256": self.plan_sha256,
            "locked_at": self.locked_at,
            "experiment": self.plan.get("experiment"),
            "version": self.plan.get("version"),
        }

    @staticmethod
    def lock_path(plan_path: str | Path) -> Path:
        return Path(str(plan_path) + ".lock")

    @classmethod
    def lock(cls, plan_path: str | Path, force: bool = False) -> Path:
        plan_path = Path(plan_path)
        digest = sha256_file(plan_path)
        lock = cls.lock_path(plan_path)
        if lock.exists() and not force:
            existing = json.loads(lock.read_text(encoding="utf-8"))
            if existing.get("plan_sha256") != digest:
                raise PreregError(
                    f"{lock} already locks a different plan.\n"
                    f"  locked: {existing.get('plan_sha256')}\n"
                    f"  now:    {digest}\n"
                    "Re-locking after results exist invalidates the "
                    "pre-registration. If the plan genuinely had to change "
                    "before any result was produced, pass --force and say so "
                    "in the response."
                )
            return lock
        lock.write_text(
            json.dumps(
                {
                    "plan_sha256": digest,
                    "locked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "git": git_commit(),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return lock

    @classmethod
    def load(cls, plan_path: str | Path) -> "Prereg":
        plan_path = Path(plan_path)
        if not plan_path.exists():
            raise PreregError(f"{plan_path}: analysis plan not found")
        lock = cls.lock_path(plan_path)
        if not lock.exists():
            raise PreregError(
                f"{lock} not found. Lock the plan before producing results:\n"
                f"  python -m cure_controls.common lock {plan_path}"
            )
        locked = json.loads(lock.read_text(encoding="utf-8"))
        digest = sha256_file(plan_path)
        if locked.get("plan_sha256") != digest:
            raise PreregError(
                f"{plan_path} changed after it was locked.\n"
                f"  locked: {locked.get('plan_sha256')}\n"
                f"  now:    {digest}\n"
                "Restore the locked plan, or treat any analysis from the edited "
                "plan as exploratory and label it that way."
            )
        return cls(
            path=plan_path,
            plan=json.loads(plan_path.read_text(encoding="utf-8")),
            plan_sha256=digest,
            locked_at=locked.get("locked_at", "unknown"),
        )


# ---------------------------------------------------------------------------
# Clustered bootstrap
# ---------------------------------------------------------------------------

@dataclass
class Estimate:
    """A point estimate with a percentile interval from clustered resampling."""

    value: float
    low: float
    high: float
    n_observations: int
    n_clusters: int
    replicates: int
    alpha: float

    def excludes_zero(self) -> bool:
        return self.low > 0.0 or self.high < 0.0

    def as_record(self) -> dict[str, Any]:
        return {
            "value": round(self.value, 6),
            "ci_low": round(self.low, 6),
            "ci_high": round(self.high, 6),
            "n_observations": self.n_observations,
            "n_clusters": self.n_clusters,
            "replicates": self.replicates,
            "alpha": self.alpha,
        }

    def format(self, unit: str = "", digits: int = 3) -> str:
        return (
            f"{self.value:.{digits}f}{unit} "
            f"[{self.low:.{digits}f}, {self.high:.{digits}f}]"
        )


def cluster_bootstrap_mean(
    values: Sequence[float],
    cluster_ids: Sequence[Any],
    replicates: int = 10_000,
    alpha: float = 0.05,
    seed: int = 0,
) -> Estimate:
    """Mean of ``values`` with a prompt-clustered percentile interval.

    ``values`` are per-observation quantities -- a paired difference, a 0/1
    outcome, a margin -- and ``cluster_ids`` says which prompt each observation
    belongs to. Resampling draws prompts with replacement and takes every
    observation of a drawn prompt, so the interval reflects between-prompt
    variation rather than treating six states from one prompt as six
    independent samples.

    The pooled mean over a replicate is computed from per-cluster sums and
    counts, which is exact for the mean and keeps 10,000 replicates cheap.
    """
    values = np.asarray(values, dtype=np.float64)
    if values.size == 0:
        raise ValueError("cluster_bootstrap_mean: no observations")
    if len(cluster_ids) != values.size:
        raise ValueError("cluster_bootstrap_mean: values/cluster_ids length mismatch")

    _, inverse = np.unique(np.asarray(cluster_ids, dtype=object), return_inverse=True)
    n_clusters = int(inverse.max()) + 1
    sums = np.bincount(inverse, weights=values, minlength=n_clusters)
    counts = np.bincount(inverse, minlength=n_clusters).astype(np.float64)

    rng = np.random.default_rng(seed)
    draws = rng.integers(0, n_clusters, size=(replicates, n_clusters))
    replicate_means = sums[draws].sum(axis=1) / counts[draws].sum(axis=1)

    low, high = np.quantile(replicate_means, [alpha / 2, 1 - alpha / 2])
    return Estimate(
        value=float(values.mean()),
        low=float(low),
        high=float(high),
        n_observations=int(values.size),
        n_clusters=n_clusters,
        replicates=replicates,
        alpha=alpha,
    )


def wilson_interval(successes: int, total: int, z: float = 1.959963985) -> tuple[float, float]:
    """Wilson score interval, for describing a single rate with no pairing."""
    if total == 0:
        return (0.0, 0.0)
    phat = successes / total
    denom = 1 + z**2 / total
    centre = (phat + z**2 / (2 * total)) / denom
    half = z * np.sqrt(phat * (1 - phat) / total + z**2 / (4 * total**2)) / denom
    return (float(max(0.0, centre - half)), float(min(1.0, centre + half)))


def _cli() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m cure_controls.common",
        description="Lock an analysis plan before any results exist.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    lock = sub.add_parser("lock", help="write PLAN.json.lock")
    lock.add_argument("plan")
    lock.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing lock; only legitimate before results exist",
    )
    args = parser.parse_args()

    path = Prereg.lock(args.plan, force=args.force)
    record = json.loads(path.read_text(encoding="utf-8"))
    print(f"locked {args.plan}")
    print(f"  plan sha256 {record['plan_sha256']}")
    print(f"  at          {record['locked_at']}")
    print("Commit this lock file now, before starting any scoring job.")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
