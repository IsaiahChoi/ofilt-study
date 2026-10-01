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
construction) are registered as the set of their 9-significant-digit decimal
mantissas. A frame claimed `synthetic` raises if any numeric column outside
the PRE_OPEN allowlist has >= MIN_DISTINCT distinct informative values of which
>= MATCH_FRAC are registered. Mantissas ignore sign and powers of ten, so
copies, subsets, sign flips and bp/percent rescalings are all caught.

Why PRE_OPEN columns are exempt: `oc_lag1` and `topix_oc_lag1` ARE lagged
real targets and are legitimate predictors in dev-calibrated simulations. The
exemption is safe only because the design builder (B1) refuses to use any
allowlisted predictor name as the target column.

Why the threshold is 0.5, not lower: real log-price-ratio columns collide
EXACTLY with the target fingerprint because TSE prices sit on a tick grid and
the same rational ratio recurs across days (y_oc has only 4,162 distinct values
in 5,124 dev rows). Measured on dev (A4): ao_gap_adj 21.9%, ao_gap_raw 21.8%,
ao_topix_gap 0.2% of distinct values match. Copies, subsets and rescalings of a
target match ~100%. With MIN_DISTINCT = 100, a 21.9% base rate reaches 50% only
as a ~6.8-sigma binomial event, so legitimate frames carrying real gap columns
pass while any mislabelled frame containing >= 100 real target values fails.

Why low-precision values are ignored: a mantissa with <= 5 significant digits
(round prices, bar counts, grid values) carries no identifying information and
would otherwise create false positives. Log-return targets are never round.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import _guards_fallback as _fallback
from .schema import PRE_OPEN_FEATURES
from .spec import REPO_ROOT

try:  # same guard selection as io.py
    from ofilt.guards import check_access as _external_check_access  # type: ignore
except ImportError:
    _external_check_access = None

SYNTHETIC, DEV_REAL, CONFIRM_REAL = "synthetic", "dev_real", "confirm_real"
SPEC_TAG, PREREG_TAG = "spec-dev-v1", "prereg-v1"
REQUIRED_TAGS = {SYNTHETIC: (), DEV_REAL: (SPEC_TAG,), CONFIRM_REAL: (SPEC_TAG, PREREG_TAG)}
_GUARD_REPO = REPO_ROOT

FINGERPRINT_EXEMPT = frozenset(PRE_OPEN_FEATURES)
MIN_DISTINCT = 100
MATCH_FRAC = 0.5
_SCALE = 1e8            # key = rint(mantissa * 1e8), mantissa in [1, 10): 9 significant digits
_LOWINFO_MOD = 10_000   # keys divisible by 1e4 have <= 5 significant digits -> ignored

_REGISTRY: dict[str, np.ndarray] = {}
_ALL_KEYS = np.empty(0, dtype=np.int64)


class BlindingError(PermissionError):
    """An analysis entry point was called on data it may not see yet."""


# ------------------------------------------------------------ fingerprints
def mantissa_keys(values) -> np.ndarray:
    """Sorted distinct informative mantissa keys of the finite nonzero values."""
    a = np.abs(np.asarray(values, dtype=float).ravel())
    a = a[np.isfinite(a) & (a > 0)]
    if a.size == 0:
        return np.empty(0, dtype=np.int64)
    m = a / np.power(10.0, np.floor(np.log10(a)))
    m = np.where(m >= 10.0, m / 10.0, m)
    m = np.where(m < 1.0, m * 10.0, m)
    k = np.rint(m * _SCALE).astype(np.int64)
    k = np.where(k >= 10 * int(_SCALE), int(_SCALE), k)  # 9.9999999995 rounds up to 10.0
    k = np.unique(k)
    return k[k % _LOWINFO_MOD != 0]


def register_real_values(values, label: str) -> int:
    """Record real target values; returns the number of keys registered under `label`."""
    global _ALL_KEYS
    if not isinstance(label, str) or not label:
        raise ValueError("label must be a non-empty string")
    k = mantissa_keys(values)
    prev = _REGISTRY.get(label)
    _REGISTRY[label] = k if prev is None else np.union1d(prev, k)
    _ALL_KEYS = np.union1d(_ALL_KEYS, k)
    return int(_REGISTRY[label].size)


def registered_labels() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))


def match_fraction(values) -> tuple[float, int]:
    """(fraction of informative distinct keys found in the registry, n distinct keys)."""
    k = mantissa_keys(values)
    if k.size == 0 or _ALL_KEYS.size == 0:
        return 0.0, int(k.size)
    return float(np.isin(k, _ALL_KEYS, assume_unique=True).mean()), int(k.size)


def _numeric(s: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s)


def check_no_real_values(df: pd.DataFrame | None = None, arrays: dict | None = None) -> None:
    """Raise BlindingError if any checked column/array matches registered real targets."""
    items = []
    if df is not None:
        items += [(f"column {c!r}", df[c]) for c in df.columns
                  if c not in FINGERPRINT_EXEMPT and _numeric(df[c])]
    for name, arr in (arrays or {}).items():
        items.append((f"array {name!r}", np.asarray(arr, dtype=float)))
    for what, vals in items:
        frac, n = match_fraction(vals)
        if n >= MIN_DISTINCT and frac >= MATCH_FRAC:
            raise BlindingError(f"{what} is labelled synthetic but {frac:.1%} of its {n} distinct "
                                f"values match registered real target values")


# ------------------------------------------------------------- tag gate
def _tag_ok(tag: str) -> bool:
    if _external_check_access is not None:
        try:
            _external_check_access(tag)
            return True
        except Exception:  # any failure, incl. signature mismatch, is a denial
            return False
    return _fallback.is_ancestor_tag(tag, _GUARD_REPO)


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
