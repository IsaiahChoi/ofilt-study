"""C6: run registry (DECISIONS P27). Every forecast.walk_forward call appends ONE strict-JSON
line (json.dumps(allow_nan=False); unknown types raise) to the registry, or raises, so no
forecast run goes unrecorded and a run that cannot be recorded returns nothing.

Line keys (exactly KEYS): run_id (uuid4 hex), utc, git_commit, git_dirty, spec_sha256,
data_sha256 (sha256 of the input frame: column names + dtypes + pandas row hashes incl. the
index), provenance, target, seed (effective), models {name: class}, grids {name: {grid |
alpha_mults} or null}, folds [per-fold geometry, row counts and `chosen` hyperparameters],
importance (model names scored), output_path (as given, or null). Non-string dict keys are
stringified (int -> str(int), float -> repr), e.g. M5's val_mse keyed by alpha multiplier.

Paths: real provenance (dev_real, confirm_real) -> RUN_REGISTRY.jsonl at the repo root
(committed); synthetic -> SYNTHETIC_PATH in the system temp directory, so the suite's and the
slow tier's synthetic runs never enter the committed file. Tests patch both constants.
Hashing the input frame is a hash, not a relation between columns (allowed by P29).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import subprocess
import tempfile
import uuid
from pathlib import Path

import numpy as np
import pandas as pd

from . import blind
from .spec import REPO_ROOT

REAL_PATH = REPO_ROOT / "RUN_REGISTRY.jsonl"
SYNTHETIC_PATH = Path(tempfile.gettempdir()) / "ofilt_RUN_REGISTRY_synthetic.jsonl"
KEYS = frozenset({"run_id", "utc", "git_commit", "git_dirty", "spec_sha256", "data_sha256", "provenance",
                  "target", "seed", "models", "grids", "folds", "importance", "output_path"})
FOLD_KEYS = ("model", "fold", "train_end", "test_start", "test_end", "n_train_dates", "n_train", "n_test", "chosen")
GRID_ATTRS = ("grid", "alpha_mults")


def registry_path(provenance: str) -> Path:
    if provenance == blind.SYNTHETIC:
        return SYNTHETIC_PATH
    if provenance in (blind.DEV_REAL, blind.CONFIRM_REAL):
        return REAL_PATH
    raise blind.BlindingError(f"no registry for provenance {provenance!r}")


def _key(k) -> str:
    if isinstance(k, str):
        return k
    if isinstance(k, (bool, np.bool_)):
        raise TypeError("boolean dict key")
    if isinstance(k, (int, np.integer)):
        return str(int(k))
    if isinstance(k, (float, np.floating)):
        return repr(float(k))
    raise TypeError(f"dict key not JSON-safe: {type(k).__name__}")


def json_safe(x):
    """Plain JSON types only; raises TypeError otherwise (NaN is left for json.dumps to refuse)."""
    if x is None or isinstance(x, str):
        return x
    if isinstance(x, dict):
        return {_key(k): json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [json_safe(v) for v in x]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return float(x)
    if isinstance(x, (pd.Timestamp, np.datetime64, _dt.datetime, _dt.date)):
        return pd.Timestamp(x).isoformat()
    raise TypeError(f"not JSON-safe: {type(x).__name__}")


def frame_sha256(df: pd.DataFrame) -> str:
    h = hashlib.sha256()
    h.update(json.dumps([[str(c), str(df[c].dtype)] for c in df.columns]).encode())
    h.update(pd.util.hash_pandas_object(df, index=True).to_numpy().tobytes())
    return h.hexdigest()


def git_state(repo: Path = REPO_ROOT) -> tuple[str, bool]:
    """(HEAD commit, working tree dirty). Raises if the repo cannot be read."""
    run = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, text=True).stdout
    return run("rev-parse", "HEAD").strip(), bool(run("status", "--porcelain", "--untracked-files=no").strip())


def record_run(*, df: pd.DataFrame, models: dict, spec, provenance: str, target: str, seed: int,
               fold_log: pd.DataFrame, importance, output_path) -> str:
    path = registry_path(provenance)
    commit, dirty = git_state()
    insts = {name: factory() for name, factory in models.items()}
    rec = dict(
        run_id=uuid.uuid4().hex,
        utc=_dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        git_commit=commit, git_dirty=dirty, spec_sha256=spec.sha256, data_sha256=frame_sha256(df),
        provenance=provenance, target=target, seed=int(seed),
        models={n: f"{type(m).__module__}.{type(m).__qualname__}" for n, m in insts.items()},
        grids={n: ({a: json_safe(getattr(m, a)) for a in GRID_ATTRS if hasattr(m, a)} or None)
               for n, m in insts.items()},
        folds=[{k: json_safe(r[k]) for k in FOLD_KEYS} for r in fold_log.to_dict("records")],
        importance=[str(x) for x in importance],
        output_path=None if output_path is None else str(output_path))
    if set(rec) != KEYS:
        raise AssertionError("registry record keys drifted")
    line = json.dumps(rec, allow_nan=False, sort_keys=True, separators=(",", ":"))
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return rec["run_id"]


def read_registry(path: Path | None = None) -> list[dict]:
    p = Path(path) if path is not None else REAL_PATH
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
