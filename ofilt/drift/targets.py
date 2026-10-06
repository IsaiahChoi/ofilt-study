"""Targets and sample masks (A5). No estimation involving FX happens here.

Timing of beta (spec target.beta): for each ticker, on its ELIGIBLE rows only
(not excluded by the inference flags, finite y and hedge), compute an
expanding (min_periods) or rolling (last `window` eligible rows) cov/var with
ddof=0. The estimate "as of" an eligible row includes that row. It is scattered
to all rows, forward-filled across ineligible rows, then shifted by `lag_days`
(>= 1). Hence beta_t uses exactly the eligible rows dated <= t-1, and excluded
rows never enter. To "continue across samples", call on the concatenated
dev+confirm panel; never restart the estimator on the confirmation sample.

Constructed targets (all share the same lagged beta, so the OLS identity
delta_cc = delta_gap + b holds exactly on a common design and sample):
  raw_oc  = y_oc
  abn_oc  = y_oc - beta * hedge_oc
  gap_abn = ao_gap_adj - beta * hedge_gap
  cc_abn  = gap_abn + abn_oc
  cc_raw  = ao_gap_adj + y_oc
On real data every constructed target is registered with the blinding
fingerprint registry (gap_abn too: its beta is target-derived).

KNOWN ISSUE (Flag 6, fix decided in Pass 2; spec unchanged): ao_gap_adj is
dividend-adjusted but the hedge gap (ao_topix_gap) is not. On mass ex-dividend
dates (~end-Mar/Sep) TOPIX gaps down mechanically, so gap_abn and cc_abn carry
an upward error of about beta x the index dividend drop on ~2 days/year.
abn_oc (primary) is unaffected. The 1306 hedge's own ex-date needs the same fix.

Masks (True = drop the row):
  excl_inference     = any(spec.sample.inference_exclude_rows_if)  (P07: D, D+1)
  excl_d2            = TANSHIN or STANDALONE_NEWS on D, D+1, D+2   (robustness)
  excl_forecast_eval = spec.sample.forecast_eval_exclusion offsets (TANSHIN D,D+1; news D+1)
D = first trading day on or after the release date, on the panel's calendar.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import blind
from .spec import Spec

BETA_COL = "beta"
CONSTRUCTED_TARGETS = frozenset({"raw_oc", "abn_oc", "gap_abn", "cc_abn", "cc_raw"})
MASK_COLUMNS = frozenset({"excl_inference", "excl_d2", "excl_forecast_eval"})
DERIVED_NONFEATURES = CONSTRUCTED_TARGETS | MASK_COLUMNS | {BETA_COL}
# Gap column of each permitted hedge. AM-03 (P18): the 1306 ETF's open->close, with its own
# dividend-adjusted gap (Flag 6 fixed on the hedge leg). The TOPIX pair stays for the fallback path.
HEDGE_GAP_FOR = {"y_topix_oc": "ao_topix_gap", "y_1306_oc": "ao_1306_gap_adj"}
D2_OFFSETS = (0, 1, 2)
EXCLUDED_EVENT_CATEGORIES = ("TANSHIN", "STANDALONE_NEWS")
_REAL = (blind.DEV_REAL, blind.CONFIRM_REAL)


def _check_keys(df: pd.DataFrame) -> None:
    if not df.index.is_unique:
        raise ValueError("index must be unique")
    if df.duplicated(["date", "ticker"]).any():
        raise ValueError("duplicate (date, ticker) keys")


# -------------------------------------------------------------------- beta
def past_beta(df: pd.DataFrame, *, y: str = "y_oc", hedge: str = "y_topix_oc",
              method: str = "expanding", window: int | None = None, min_periods: int | None = None,
              lag_days: int = 1, eligible: pd.Series | None = None) -> pd.Series:
    """Past-only hedge beta per ticker, aligned to df.index (NaN until min_periods)."""
    _check_keys(df)
    if method not in ("expanding", "rolling"):
        raise ValueError(f"unknown beta method {method!r}")
    if not isinstance(lag_days, (int, np.integer)) or lag_days < 1:
        raise ValueError("lag_days must be an integer >= 1 (lag 0 is look-ahead)")
    if method == "rolling":
        if not isinstance(window, (int, np.integer)) or window < 2:
            raise ValueError("rolling beta needs an integer window >= 2")
        min_periods = window if min_periods is None else min_periods
    elif min_periods is None or window is not None:
        raise ValueError("expanding beta needs min_periods and no window")
    yv, hv = df[y].astype(float), df[hedge].astype(float)
    elig = np.isfinite(yv) & np.isfinite(hv)
    if eligible is not None:
        elig &= eligible.reindex(df.index).fillna(False).astype(bool)
    out = pd.Series(np.nan, index=df.index, name=BETA_COL)
    for _, sub in df.groupby("ticker", sort=True):
        idx = sub.sort_values("date", kind="mergesort").index
        e = elig.loc[idx].to_numpy(bool)
        ys = pd.Series(yv.loc[idx].to_numpy()[e])
        hs = pd.Series(hv.loc[idx].to_numpy()[e])
        roll = (ys.expanding(min_periods=min_periods) if method == "expanding"
                else ys.rolling(window, min_periods=min_periods))
        hroll = (hs.expanding(min_periods=min_periods) if method == "expanding"
                 else hs.rolling(window, min_periods=min_periods))
        b_e = (roll.cov(hs, ddof=0) / hroll.var(ddof=0)).to_numpy()
        full = np.full(len(idx), np.nan)
        full[e] = b_e
        out.loc[idx] = pd.Series(full).ffill().shift(lag_days).to_numpy()
    return out


def exclusion_mask(df: pd.DataFrame, spec: Spec) -> pd.Series:
    flags = list(spec.inference_exclusion_flags)
    return df[flags].astype(bool).any(axis=1).rename("excl_inference")


# ----------------------------------------------------------------- targets
def add_targets(df: pd.DataFrame, spec: Spec | None = None, *, method: str | None = None,
                window: int | None = None, estimate_on: str | None = None) -> pd.DataFrame:
    """Copy of df with beta, the constructed targets and excl_inference (attrs kept)."""
    spec = spec or Spec.load()
    bs = spec.beta
    method = method or bs.method
    estimate_on = estimate_on or bs.estimate_on
    if estimate_on not in ("non_excluded_rows", "all_rows"):
        raise ValueError(f"unknown estimate_on {estimate_on!r}")
    hedge = spec.hedge_oc_column
    if hedge not in HEDGE_GAP_FOR:
        raise ValueError(f"no gap column registered for hedge {hedge!r}; extend HEDGE_GAP_FOR")
    excl = exclusion_mask(df, spec)
    elig = ~excl if estimate_on == "non_excluded_rows" else pd.Series(True, index=df.index)
    mp = bs.min_periods if method == "expanding" else None
    b = past_beta(df, y="y_oc", hedge=hedge, method=method, window=window, min_periods=mp,
                  lag_days=bs.lag_days, eligible=elig)
    out = df.copy()
    out["excl_inference"] = excl
    out[BETA_COL] = b
    out["raw_oc"] = out["y_oc"]
    out["abn_oc"] = out["y_oc"] - b * out[hedge]
    out["gap_abn"] = out["ao_gap_adj"] - b * out[HEDGE_GAP_FOR[hedge]]
    out["cc_abn"] = out["gap_abn"] + out["abn_oc"]
    out["cc_raw"] = out["ao_gap_adj"] + out["y_oc"]
    out.attrs = dict(df.attrs)
    out.attrs["targets"] = dict(method=method, window=window, estimate_on=estimate_on,
                                hedge=hedge, lag_days=bs.lag_days, min_periods=mp)
    prov = df.attrs.get("provenance")
    if prov in _REAL:
        for c in ("abn_oc", "gap_abn", "cc_abn", "cc_raw"):
            blind.register_real_values(out[c].to_numpy(dtype=float), label=f"{prov}:{c}",
                                       dates=out["date"], tickers=out["ticker"])
    return out


# ------------------------------------------------------------------- masks
def event_rows(events: pd.DataFrame, df: pd.DataFrame, categories, offsets) -> pd.Series:
    """True on (ticker, cal[k+o]) for each release, k = first panel date >= release date."""
    mask = pd.Series(False, index=df.index)
    last = df["date"].max()
    ev = events[events["category"].isin(list(categories)) & (events["date"] <= last)]
    for t, sub in df.groupby("ticker", sort=True):
        cal = pd.DatetimeIndex(np.sort(sub["date"].unique()))
        hit = set()
        for d in ev.loc[ev["ticker"] == t, "date"]:
            k = cal.searchsorted(d)
            hit.update(cal[k + o] for o in offsets if k + o < len(cal))
        mask.loc[sub.index[sub["date"].isin(hit).to_numpy()]] = True
    return mask


def add_masks(df: pd.DataFrame, events: pd.DataFrame, spec: Spec | None = None) -> pd.DataFrame:
    spec = spec or Spec.load()
    _check_keys(df)
    fe = spec.forecast_eval_exclusion
    out = df.copy()
    if "excl_inference" not in out:
        out["excl_inference"] = exclusion_mask(df, spec)
    out["excl_d2"] = event_rows(events, df, EXCLUDED_EVENT_CATEGORIES, D2_OFFSETS)
    out["excl_forecast_eval"] = (event_rows(events, df, ["TANSHIN"], fe.tanshin)
                                 | event_rows(events, df, ["STANDALONE_NEWS"], fe.standalone_news))
    out.attrs = dict(df.attrs)
    return out
