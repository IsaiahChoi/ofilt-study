"""Column groups of panel_dev.csv and the feature allowlist.

Every group is an explicit frozenset. Nothing in this package selects columns
by prefix or pattern: a new column that is not listed here is UNKNOWN and is
refused everywhere (fail closed). This supersedes README rule 2 ("features come
from unprefixed columns"), which is unsafe: `open`, `close`, `prev_close` are
unprefixed but are auction/target information, and `audit_flag` is unprefixed
but outcome-selected.

Model features may come only from PRE_OPEN_FEATURES, from DERIVED_FEATURES
(deterministic row-wise functions of permitted sources, no estimated
parameters), or from SYNTHETIC_FEATURES (generated in model code). Ticker
fixed effects / one-hot columns are built from the `ticker` key by the design
builder and are not passed through this check.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

KEYS = frozenset({"date", "ticker"})

# Known by 08:59 JST on day t.
PRE_OPEN_FEATURES = frozenset({
    "usdjpy_ret", "usdjpy_rv", "usdjpy_bv", "eurusd_ret", "eurusd_rv",
    "spy_oc", "ewj_oc", "fcx_oc", "copx_oc", "us_n_sessions", "window_hours",
    "gap_adj_lag1", "oc_lag1", "range_lag1", "topix_oc_lag1",
    "boj_day", "sq_day", "sq_major", "exdiv_day", "div_exdate",
})
EXCLUSION_FLAGS = frozenset({"earn_flag", "news_flag"})      # sample filters (P07), never features
INFORMATIONAL = frozenset({"mech_flag"})                      # recorded, not excluded, not a feature
ROBUSTNESS_ONLY = frozenset({"audit_flag"})                   # outcome-selected (P08): robustness filter only
AT_OPEN = frozenset({"ao_gap_adj", "ao_gap_raw", "ao_topix_gap"})  # uses the 09:00 print
TARGET_INPUTS = frozenset({"y_oc", "y_topix_oc"})             # outcomes of day t's session
PROVENANCE = frozenset({
    "open", "close", "prev_close",                            # auction / target information
    "window_start_utc", "window_end_utc",
    "usdjpy_bars", "usdjpy_stale_start_min", "usdjpy_stale_end_min",
    "eurusd_bars", "eurusd_stale_end_min",
})
CONTEMPORANEOUS = frozenset()  # Pass 2 placeholder (e.g. post-open FX); empty in Pass 1

GROUPS: dict[str, frozenset] = {
    "KEYS": KEYS,
    "PRE_OPEN_FEATURES": PRE_OPEN_FEATURES,
    "EXCLUSION_FLAGS": EXCLUSION_FLAGS,
    "INFORMATIONAL": INFORMATIONAL,
    "ROBUSTNESS_ONLY": ROBUSTNESS_ONLY,
    "AT_OPEN": AT_OPEN,
    "TARGET_INPUTS": TARGET_INPUTS,
    "PROVENANCE": PROVENANCE,
    "CONTEMPORANEOUS": CONTEMPORANEOUS,
}

_FORBIDDEN_REASON = {
    "KEYS": "key column (fixed effects are built by the design builder, not passed as features)",
    "EXCLUSION_FLAGS": "sample-exclusion flag (P07); filters rows, never a feature",
    "INFORMATIONAL": "informational flag; not a feature",
    "ROBUSTNESS_ONLY": "outcome-selected (P08); robustness row filter only",
    "AT_OPEN": "uses the 09:00 auction print; decomposition/hedge only (auction-conditional spec retired)",
    "TARGET_INPUTS": "target input; never a feature",
    "PROVENANCE": "provenance/QA or auction/target price; never a feature",
    "CONTEMPORANEOUS": "contemporaneous with the session; not pre-open",
}

# Long-window threshold of the secondary term fx_x_longwindow. Normal dev
# nights are 15:00 -> 08:59 = 17.983 h, so > 18 h flags multi-night windows only.
LONG_WINDOW_HOURS = 18.0

# Derived features: name -> source columns. All are deterministic row-wise
# functions with no estimated parameter. Thresholds that ARE estimated
# (rv_per_bar dev median, expanding past median) are applied by the design
# builder / forecast engine, never here.
DERIVED_FEATURES: dict[str, frozenset] = {
    "long_window": frozenset({"window_hours"}),               # 1[window_hours > 18]
    "jumpshare": frozenset({"usdjpy_rv", "usdjpy_bv"}),       # clip((rv-bv)/rv, 0, 1)
    "rv_per_bar": frozenset({"usdjpy_rv", "usdjpy_bars"}),    # rv / bars
    "e_pos": frozenset({"usdjpy_ret"}),                       # max(e, 0)
    "e_neg": frozenset({"usdjpy_ret"}),                       # min(e, 0)
    "no_us_session": frozenset({"us_n_sessions"}),            # 1[us_n_sessions == 0]
}
# The ONLY non-PRE_OPEN column a derived feature may read: usdjpy_bars is a
# count of 1-minute bars inside the dark window (known pre-open), classified as
# PROVENANCE, used solely as the denominator of rv_per_bar.
PERMITTED_DERIVED_SOURCES = frozenset({"usdjpy_bars"})

SYNTHETIC_FEATURES = frozenset({"noise_N01"})  # M7 / importance calibration column

ALLOWED_FEATURES = PRE_OPEN_FEATURES | frozenset(DERIVED_FEATURES) | SYNTHETIC_FEATURES


class UnknownColumnError(KeyError):
    """A column not listed in any group (fail closed)."""


class FeatureNotAllowedError(ValueError):
    """A forbidden column was requested as a model feature."""


def all_grouped_columns() -> frozenset:
    out: frozenset = frozenset()
    for g in GROUPS.values():
        out = out | g
    return out


def classify(col: str) -> str:
    hits = [name for name, g in GROUPS.items() if col in g]
    if len(hits) == 0:
        raise UnknownColumnError(f"column {col!r} is not in any schema group")
    if len(hits) > 1:  # impossible if groups are disjoint; checked by tests
        raise RuntimeError(f"column {col!r} is in several groups: {hits}")
    return hits[0]


def assert_features_allowed(cols: Iterable[str]) -> None:
    """Raise FeatureNotAllowedError unless every col is an allowed feature."""
    bad = []
    for c in cols:
        if c in ALLOWED_FEATURES:
            continue
        try:
            reason = _FORBIDDEN_REASON[classify(c)]
        except UnknownColumnError:
            reason = "unknown column (not in any schema group)"
        bad.append(f"{c}: {reason}")
    if bad:
        raise FeatureNotAllowedError("forbidden feature(s): " + "; ".join(bad))


def feature_sources(cols: Iterable[str]) -> frozenset:
    """Panel columns that must be read to build `cols` (after allowlist check)."""
    cols = list(cols)
    assert_features_allowed(cols)
    src: set = set()
    for c in cols:
        if c in PRE_OPEN_FEATURES:
            src.add(c)
        elif c in DERIVED_FEATURES:
            s = DERIVED_FEATURES[c]
            extra = s - PRE_OPEN_FEATURES - PERMITTED_DERIVED_SOURCES
            if extra:  # defensive: the map above must never allow this
                raise FeatureNotAllowedError(f"derived {c} reads non-permitted {sorted(extra)}")
            src |= s
    return frozenset(src)


def select_features(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    """THE production path for model features: allowlist check, then build.

    Returns a new float DataFrame with exactly `cols` (same index as df).
    Synthetic columns (noise_N01) must already be present in df, added by the
    caller from a seeded generator.
    """
    cols = list(cols)
    srcs = feature_sources(cols)
    missing = [c for c in srcs if c not in df.columns]
    missing += [c for c in cols if c in SYNTHETIC_FEATURES and c not in df.columns]
    if missing:
        raise KeyError(f"panel lacks source column(s) {sorted(set(missing))}")
    out = {}
    for c in cols:
        if c in PRE_OPEN_FEATURES or c in SYNTHETIC_FEATURES:
            out[c] = df[c].to_numpy(dtype=float, copy=True)
        elif c == "long_window":
            out[c] = (df["window_hours"].to_numpy(dtype=float) > LONG_WINDOW_HOURS).astype(float)
        elif c == "jumpshare":
            rv = df["usdjpy_rv"].to_numpy(dtype=float)
            bv = df["usdjpy_bv"].to_numpy(dtype=float)
            with np.errstate(divide="ignore", invalid="ignore"):
                js = np.where(rv > 0, (rv - bv) / rv, 0.0)
            out[c] = np.where(np.isnan(rv) | np.isnan(bv), np.nan, np.clip(js, 0.0, 1.0))
        elif c == "rv_per_bar":
            bars = df["usdjpy_bars"].to_numpy(dtype=float)
            with np.errstate(divide="ignore", invalid="ignore"):
                out[c] = np.where(bars > 0, df["usdjpy_rv"].to_numpy(dtype=float) / bars, np.nan)
        elif c == "e_pos":
            out[c] = np.maximum(df["usdjpy_ret"].to_numpy(dtype=float), 0.0)
        elif c == "e_neg":
            out[c] = np.minimum(df["usdjpy_ret"].to_numpy(dtype=float), 0.0)
        elif c == "no_us_session":
            out[c] = (df["us_n_sessions"].to_numpy(dtype=float) == 0).astype(float)
        else:  # pragma: no cover - guarded by assert_features_allowed
            raise FeatureNotAllowedError(c)
    return pd.DataFrame(out, index=df.index)
