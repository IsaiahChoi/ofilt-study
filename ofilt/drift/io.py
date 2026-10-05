"""Data loaders. The only module that opens panel or event files.

* load_dev():      verifies SHA-256 against the spec, checks scope (all dates
                   < 2022-01-01), schema (exactly the schema groups), keys;
                   tags attrs['provenance'] = 'dev_real'.
* load_confirm():  calls the access guard with tag 'prereg-v1' BEFORE touching
                   any path, appends one JSON line to ACCESS_LOG per attempt
                   (DENIED or GRANTED), and only then verifies and reads the
                   sealed panel. In Pass 1 it must raise.
* load_events_*(): verify the event-file hashes.

The guard repository is the repo containing this code (_GUARD_REPO). There is
deliberately no `repo=` argument: pointing the guard elsewhere would bypass it.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import traceback
from pathlib import Path

import pandas as pd

from . import _guards_fallback as _fallback
from .schema import all_grouped_columns
from .spec import REPO_ROOT, Spec

try:  # the real project guard, if this tree is merged into the ofilt repo
    from ofilt.guards import check_access as _external_check_access  # type: ignore
except ImportError:  # sandbox: no ofilt.guards
    _external_check_access = None

AccessDenied = _fallback.AccessDenied
DATA_DIR = Path(os.environ.get("OFILT_DATA_DIR", "/mnt/project"))
DEV_FILE = "panel_dev.csv"
CONFIRM_FILE = "panel_confirm_SEALED.csv"
EVENTS_FIRM_FILE = "events_firm.csv"
EVENTS_BOJ_FILE = "events_boj.csv"
ACCESS_LOG_PATH = REPO_ROOT / "ACCESS_LOG"
_GUARD_REPO = REPO_ROOT
CONFIRM_TAG = "prereg-v1"
DEV_END_EXCLUSIVE = pd.Timestamp("2022-01-01")
TICKERS = ("5706", "5711", "5713")


class DataHashError(RuntimeError):
    """File bytes do not match the SHA-256 recorded in the spec."""


class DataScopeError(RuntimeError):
    """File content is outside the permitted scope (e.g. a 2022+ date in dev)."""


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify(path: Path, expected: str, what: str) -> str:
    got = sha256_file(path)
    if got != expected:
        raise DataHashError(f"{what}: SHA-256 mismatch for {path}\n  expected {expected}\n  got      {got}")
    return got


def _read_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"ticker": str}, parse_dates=["date"])
    extra = set(df.columns) - all_grouped_columns()
    missing = all_grouped_columns() - set(df.columns)
    if extra or missing:
        raise DataScopeError(f"panel schema mismatch: extra={sorted(extra)} missing={sorted(missing)}")
    if set(df["ticker"].unique()) != set(TICKERS):
        raise DataScopeError(f"unexpected tickers {sorted(df['ticker'].unique())}")
    if df.duplicated(["date", "ticker"]).any():
        raise DataScopeError("duplicate (date, ticker) keys")
    # Canonical order: date-major, then ticker. Fresh RangeIndex.
    return df.sort_values(["date", "ticker"], kind="mergesort").reset_index(drop=True)


def load_dev(path: str | Path | None = None, spec: Spec | None = None) -> pd.DataFrame:
    spec = spec or Spec.load()
    p = Path(path) if path is not None else DATA_DIR / DEV_FILE
    digest = _verify(p, spec.data_hash("dev_panel"), "dev panel")
    df = _read_panel(p)
    if not (df["date"] < DEV_END_EXCLUSIVE).all():
        raise DataScopeError("dev panel contains dates >= 2022-01-01")
    df.attrs.update(provenance="dev_real", sha256=digest, source=str(p))
    _register_real_targets(df)
    return df


def _register_real_targets(df: pd.DataFrame) -> None:
    """Hook for the A4 blinding fingerprint registry (no-op until blind.py exists)."""
    try:
        from . import blind  # noqa: WPS433 (deferred to avoid import cycle)
    except ImportError:
        return
    reg = getattr(blind, "register_real_values", None)
    if reg is not None:
        for c in ("y_oc", "y_topix_oc"):
            reg(df[c].to_numpy(dtype=float), label=f"{df.attrs.get('provenance')}:{c}",
                dates=df["date"], tickers=df["ticker"])


def load_events_firm(path: str | Path | None = None, spec: Spec | None = None) -> pd.DataFrame:
    spec = spec or Spec.load()
    p = Path(path) if path is not None else DATA_DIR / EVENTS_FIRM_FILE
    _verify(p, spec.data_hash("events_firm"), "events_firm")
    ev = pd.read_csv(p, dtype={"ticker": str}, parse_dates=["date"])
    cats = set(ev["category"].unique())
    if cats != {"TANSHIN", "STANDALONE_NEWS", "MECHANICAL", "AUDIT_CANDIDATE"}:
        raise DataScopeError(f"unexpected event categories {sorted(cats)}")
    return ev


def load_events_boj(path: str | Path | None = None, spec: Spec | None = None) -> pd.DataFrame:
    spec = spec or Spec.load()
    p = Path(path) if path is not None else DATA_DIR / EVENTS_BOJ_FILE
    _verify(p, spec.data_hash("events_boj"), "events_boj")
    return pd.read_csv(p, parse_dates=["announcement_date"])


# ------------------------------------------------------------ confirmation
def _check_access(tag: str) -> None:
    """Conjunctive, fail-closed tag gate (P46): the fallback check always runs; if the external
    guard is importable it must ALSO return None or True without raising."""
    _fallback.check_access(tag, _GUARD_REPO)
    if _external_check_access is not None:
        try:
            result = _external_check_access(tag)
        except Exception as e:  # any exception (incl. signature mismatch) is a denial
            raise AccessDenied(f"external guard denied {tag!r}: {type(e).__name__}: {e}") from e
        if result is not None and result is not True:  # any other return value is a denial
            raise AccessDenied(f"external guard returned {result!r} for {tag!r}; only None or True grants")


def _log_access(result: str, reason: str) -> None:
    rec = {
        "utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "tag": CONFIRM_TAG,
        "result": result,
        "head": _fallback.head_commit(_GUARD_REPO) or "none",
        "guard": "ofilt.guards" if _external_check_access is not None else "fallback",
        "caller": "".join(traceback.format_stack(limit=4)[:-2]).strip().replace("\n", " | ")[:400],
        "reason": reason[:300],
    }
    with open(ACCESS_LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def load_confirm(path: str | Path | None = None, spec: Spec | None = None) -> pd.DataFrame:
    try:
        _check_access(CONFIRM_TAG)
    except Exception as e:  # fail closed on ANY guard failure
        _log_access("DENIED", f"{type(e).__name__}: {e}")
        raise AccessDenied(f"load_confirm refused: {e}") from e
    _log_access("GRANTED", "tag is an ancestor of HEAD")
    spec = spec or Spec.load()
    p = Path(path) if path is not None else DATA_DIR / CONFIRM_FILE
    digest = _verify(p, spec.data_hash("sealed_panel"), "sealed confirmation panel")
    df = _read_panel(p)
    df.attrs.update(provenance="confirm_real", sha256=digest, source=str(p))
    _register_real_targets(df)
    return df
