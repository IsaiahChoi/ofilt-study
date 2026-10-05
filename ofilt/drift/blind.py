"""Blinding guard. Every estimation entry point calls `require_unblinded` first.

Provenance values (df.attrs['provenance'] or the explicit `provenance=` kwarg):

  synthetic     passes, subject to the real-value fingerprint check below.
  dev_real      passes only if git tag `spec-dev-v1` is an ancestor of HEAD.
  confirm_real  passes only if BOTH `spec-dev-v1` and `prereg-v1` are ancestors.

Anything else -- missing, empty, non-string, unknown -- raises (fail closed).
If both df.attrs['provenance'] and `provenance=` are present they must agree;
the explicit kwarg exists only because some pandas operations drop `.attrs`.

Fingerprint check (defence against mislabelling, not against an adversary).
Real target values (y_oc, y_topix_oc at load; constructed targets at
construction) are registered as 9-significant-digit decimal mantissas (sign-
and power-of-ten-invariant, so copies, subsets, sign flips and bp/percent
rescalings all match), both as a VALUE set and, when keys are supplied, as a
ROW set of (date, ticker, mantissa) codes. A frame claimed `synthetic` raises if
  * row-aligned (frames with date+ticker): any numeric column has >= MIN_DISTINCT
    informative rows of which >= MATCH_FRAC match a registered row code; or
  * value-only (all frames, and `arrays=`): any numeric column outside
    VALUE_EXEMPT = PRE_OPEN | AT_OPEN has >= MIN_DISTINCT distinct informative
    values of which >= MATCH_FRAC are registered values.

Why two checks (A4, revised during A5). TSE prices sit on a tick grid, so real
log-price-ratio columns collide EXACTLY with tick-grid targets (y_oc, cc_raw):
value-set overlap of real ao_gap_adj reached 0.89 on (5706, 2015) because
capital-change-adjusted pre-2017 prices are coarse. Value-only checks cannot
separate such columns, so gap columns (AT_OPEN) and allowlisted predictors
(PRE_OPEN; oc_lag1/topix_oc_lag1 ARE lagged targets, value overlap 0.9998) are
exempt from the value check. The row-aligned check needs no exemptions: worst
same-row overlap of any non-target dev column on any ticker-year subset is
0.187 (gap columns, 5706 2015: |gap_t| = |oc_t| reversals and open == close
days), ~8 sigma below 0.5 at n = 100; registered targets self-match at 1.0.
The value check still catches real targets pasted under synthetic dates.
`arrays=` is for TARGET vectors only (design matrices would trip on oc_lag1).
Rename hole: B1 must refuse target columns named in PRE_OPEN | AT_OPEN.
FX columns (FX_NAMES) are never fingerprint-compared, so the guard itself never
relates FX values to target values.

Why low-precision values are ignored: a mantissa with <= 5 significant digits
(round prices, bar counts, grid values) carries no identifying information.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import _guards_fallback as _fallback
from .schema import AT_OPEN, KEYS, PRE_OPEN_FEATURES
from .spec import REPO_ROOT

try:  # same guard selection as io.py
    from ofilt.guards import check_access as _external_check_access  # type: ignore
except ImportError:
    _external_check_access = None

SYNTHETIC, DEV_REAL, CONFIRM_REAL = "synthetic", "dev_real", "confirm_real"
SPEC_TAG, PREREG_TAG = "spec-dev-v1", "prereg-v1"
REQUIRED_TAGS = {SYNTHETIC: (), DEV_REAL: (SPEC_TAG,), CONFIRM_REAL: (SPEC_TAG, PREREG_TAG)}
_GUARD_REPO = REPO_ROOT

VALUE_EXEMPT = frozenset(PRE_OPEN_FEATURES | AT_OPEN)
# Blinding hygiene: the guard never compares FX values with target values (rule 2,
# "if unsure, don't"). Explicit names; a test checks every usdjpy_/eurusd_ panel column is here.
FX_NAMES = frozenset({
    "usdjpy_ret", "usdjpy_rv", "usdjpy_bv", "eurusd_ret", "eurusd_rv",
    "usdjpy_bars", "eurusd_bars", "usdjpy_stale_start_min", "usdjpy_stale_end_min",
    "eurusd_stale_end_min", "e_pos", "e_neg", "jumpshare", "rv_per_bar"})
MIN_DISTINCT = 100
MATCH_FRAC = 0.5
_SCALE = 1e8            # key = rint(mantissa * 1e8), mantissa in [1, 10): 9 significant digits
_LOWINFO_MOD = 10_000   # keys divisible by 1e4 have <= 5 significant digits -> ignored

_REGISTRY: dict[str, np.ndarray] = {}
_ALL_KEYS = np.empty(0, dtype=np.int64)
_ROW_KEYS = np.empty(0, dtype=np.int64)


class BlindingError(PermissionError):
    """An analysis entry point was called on data it may not see yet."""


# ------------------------------------------------------------ fingerprints
def _keys_all(values) -> np.ndarray:
    """Per-element mantissa key; 0 where non-finite, zero, or low-information."""
    a = np.abs(np.asarray(values, dtype=float).ravel())
    out = np.zeros(a.size, dtype=np.int64)
    ok = np.isfinite(a) & (a > 0)
    if ok.any():
        aa = a[ok]
        m = aa / np.power(10.0, np.floor(np.log10(aa)))
        m = np.where(m >= 10.0, m / 10.0, m)
        m = np.where(m < 1.0, m * 10.0, m)
        k = np.rint(m * _SCALE).astype(np.int64)
        out[ok] = np.where(k >= 10 * int(_SCALE), int(_SCALE), k)  # 9.9999999995 -> 10.0
    out[out % _LOWINFO_MOD == 0] = 0
    return out


def mantissa_keys(values) -> np.ndarray:
    """Sorted distinct informative mantissa keys of the finite nonzero values."""
    k = _keys_all(values)
    return np.unique(k[k > 0])


def _row_codes(values, dates, tickers) -> np.ndarray | None:
    """(date, ticker, mantissa) codes of informative rows; None if keys unusable."""
    try:
        day = pd.to_datetime(pd.Series(dates)).to_numpy().astype("datetime64[D]").astype(np.int64)
    except (ValueError, TypeError):
        return None
    tk = pd.to_numeric(pd.Series(tickers), errors="coerce").to_numpy(dtype=float)
    k = _keys_all(values)
    if not (len(day) == len(tk) == len(k)):
        raise ValueError("values, dates and tickers must have equal length")
    ok = (k > 0) & np.isfinite(tk) & (tk >= 0) & (tk < 10_000) & (day >= 0) & (day < 100_000)
    return (day[ok] * 10_000 + tk[ok].astype(np.int64)) * 10**9 + k[ok]


def register_real_values(values, label: str, *, dates=None, tickers=None) -> int:
    """Record real target values (and row codes if keys given); returns #value keys under label."""
    global _ALL_KEYS, _ROW_KEYS
    if not isinstance(label, str) or not label:
        raise ValueError("label must be a non-empty string")
    k = mantissa_keys(values)
    prev = _REGISTRY.get(label)
    _REGISTRY[label] = k if prev is None else np.union1d(prev, k)
    _ALL_KEYS = np.union1d(_ALL_KEYS, k)
    if dates is not None and tickers is not None:
        rc = _row_codes(values, dates, tickers)
        if rc is None:
            raise ValueError(f"unusable dates for {label}")
        _ROW_KEYS = np.union1d(_ROW_KEYS, rc)
    return int(_REGISTRY[label].size)


def registered_labels() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))


def match_fraction(values) -> tuple[float, int]:
    """Value-only: (fraction of distinct informative keys registered, n distinct keys)."""
    k = mantissa_keys(values)
    if k.size == 0 or _ALL_KEYS.size == 0:
        return 0.0, int(k.size)
    return float(np.isin(k, _ALL_KEYS, assume_unique=True).mean()), int(k.size)


def row_match_fraction(values, dates, tickers) -> tuple[float, int]:
    """Row-aligned: (fraction of informative rows whose code is registered, n rows)."""
    rc = _row_codes(values, dates, tickers)
    if rc is None or rc.size == 0 or _ROW_KEYS.size == 0:
        return 0.0, 0 if rc is None else int(rc.size)
    return float(np.isin(rc, _ROW_KEYS).mean()), int(rc.size)


def _numeric(s: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s)


def check_no_real_values(df: pd.DataFrame | None = None, arrays: dict | None = None) -> None:
    """Raise BlindingError if any checked column/array matches registered real targets."""
    def trip(what, frac, n, kind):
        if n >= MIN_DISTINCT and frac >= MATCH_FRAC:
            raise BlindingError(f"{what} is labelled synthetic but {frac:.1%} of its {n} {kind} "
                                f"match registered real target values")
    if df is not None:
        num = [c for c in df.columns if c not in KEYS and c not in FX_NAMES and _numeric(df[c])]
        if KEYS <= set(df.columns):
            for c in num:
                trip(f"column {c!r}", *row_match_fraction(df[c], df["date"], df["ticker"]), "rows")
        for c in num:
            if c not in VALUE_EXEMPT:
                trip(f"column {c!r}", *match_fraction(df[c]), "distinct values")
    for name, arr in (arrays or {}).items():
        trip(f"array {name!r}", *match_fraction(np.asarray(arr, dtype=float)), "distinct values")


# ------------------------------------------------------------- tag gate
def _tag_ok(tag: str) -> bool:
    """Conjunctive, fail-closed tag gate (P46): the fallback check always runs; if the external
    guard is importable it must ALSO return None or True without raising."""
    if not _fallback.is_ancestor_tag(tag, _GUARD_REPO):
        return False
    if _external_check_access is not None:
        try:
            result = _external_check_access(tag)
        except Exception:  # any failure, incl. signature mismatch, is a denial
            return False
        return result is None or result is True  # any other return value is a denial
    return True


# ------------------------------------------------------------ main guard
def provenance_of(df: pd.DataFrame | None) -> str | None:
    if df is None:
        return None
    return getattr(df, "attrs", {}).get("provenance")


def mark_synthetic(df: pd.DataFrame) -> pd.DataFrame:
    df.attrs["provenance"] = SYNTHETIC
    return df


def require_unblinded(df: pd.DataFrame | None = None, *, provenance: str | None = None,
                      arrays: dict | None = None) -> str:
    """Return the effective provenance, or raise BlindingError (fail closed)."""
    if df is not None and not isinstance(df, pd.DataFrame):
        raise BlindingError(f"require_unblinded expects a DataFrame, got {type(df).__name__}")
    attr = provenance_of(df)
    if attr is not None and provenance is not None and attr != provenance:
        raise BlindingError(f"provenance conflict: df.attrs says {attr!r}, caller says {provenance!r}")
    prov = provenance if provenance is not None else attr
    if not isinstance(prov, str) or prov not in REQUIRED_TAGS:
        raise BlindingError(f"missing or unknown provenance {prov!r}; refusing (fail closed)")
    missing = [t for t in REQUIRED_TAGS[prov] if not _tag_ok(t)]
    if missing:
        raise BlindingError(f"{prov} data is blinded: required tag(s) {missing} not ancestors of HEAD")
    if prov == SYNTHETIC:
        check_no_real_values(df, arrays)
    return prov
