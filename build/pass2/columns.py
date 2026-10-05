"""Pass 2 new columns (P50), as pure functions: no file I/O. build_panel_p2.py loads the inputs.

Definitions: PASS2_ADDENDUM Appendix A′ (the P2-2 table), P48 (gotobi), P49 (US session).
Price at instant X everywhere means the close of the last bar labeled <= X - 1 min (the frozen
price_at).

The frozen Pass 1 helpers in build/pass1/build_panel.py are reused by import and never edited
(P51; Isaiah, 2026-10-05): load_workbook, load_fx, fx_windows, price_at, jst_to_utc, us_features
and the constants TSE_CLOSE_CHANGE, CASH_TYPES and SPLIT_DATE. xau_* and n225_* come from the
frozen fx_windows itself. Four frozen routines are not callable as is for Pass 2's inputs; only
those are re-implemented here, and tests/test_p2_columns.py shows identical output to the frozen
code on synthetic inputs:
* parse_price_sheet and parse_dividends: load_workbook's per-sheet parsing (load_workbook itself
  reads only Book2's fixed sheet names);
* dark_window_instants: fx_windows' window bounds, needed on nights where fx_windows records none;
* us_session_dates: us_features' session set, which us_features does not return.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
FROZEN_PATH = REPO / "build" / "pass1" / "build_panel.py"


def _load_frozen():
    spec = importlib.util.spec_from_file_location("build_panel_pass1", FROZEN_PATH)
    mod = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True          # leave build/pass1/ untouched (no __pycache__)
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = old
    return mod


pass1 = _load_frozen()

OUTAGE = pd.Timestamp("2020-10-01")           # TSE outage: stale row, dropped as the frozen build does
NY_TZ = "America/New_York"
NYSE_EARLY_CLOSES = (                         # P49: 13:00 ET closes, 2015-01 -> 2026-03-05 (23)
    "2015-11-27", "2015-12-24", "2016-11-25", "2017-07-03", "2017-11-24", "2018-07-03", "2018-11-23",
    "2018-12-24", "2019-07-03", "2019-11-29", "2019-12-24", "2020-11-27", "2020-12-24", "2021-11-26",
    "2022-11-25", "2023-07-03", "2023-11-24", "2024-07-03", "2024-11-29", "2024-12-24", "2025-07-03",
    "2025-11-28", "2025-12-24")
GOTOBI_DAYS = (5, 10, 15, 20, 25, 30)         # P48, plus the month's last calendar day

NEW_COLUMNS = (                               # P50 names and groups, in Appendix A′ order
    ("y_1306_oc", "TARGET_INPUTS"),
    ("ao_1306_gap_raw", "AT_OPEN"),
    ("ao_1306_gap_adj", "AT_OPEN"),
    ("ao_topix_gap_tradj", "AT_OPEN"),
    ("xau_ret", "PRE_OPEN_ROBUSTNESS"),
    ("xau_rv", "PRE_OPEN_ROBUSTNESS"),
    ("xau_bv", "PRE_OPEN_ROBUSTNESS"),
    ("n225_ret", "PRE_OPEN_ROBUSTNESS"),
    ("usdjpy_us_ret", "PRE_OPEN_ROBUSTNESS"),
    ("ewj_oc_jpy", "PRE_OPEN_ROBUSTNESS"),
    ("gotobi_day", "PRE_OPEN_ROBUSTNESS"),
    ("c_usdjpy_sess_ret", "CONTEMPORANEOUS"),
    ("c_eurusd_sess_ret", "CONTEMPORANEOUS"),
    ("xau_bars", "PROVENANCE"),
    ("xau_stale_start_min", "PROVENANCE"),
    ("xau_stale_end_min", "PROVENANCE"),
    ("n225_bars", "PROVENANCE"),
    ("n225_stale_start_min", "PROVENANCE"),
    ("n225_stale_end_min", "PROVENANCE"),
)


def day_key(d) -> str:
    return pd.Timestamp(d).strftime("%Y-%m-%d")


# ---------------------------------------------------------------- 1306
def parse_price_sheet(sheet: pd.DataFrame) -> pd.DataFrame:
    """load_workbook's per-stock price parsing (no header; date, open, close, high, low), for the
    `1306` sheet of the fixed workbook (DATA_PROVENANCE §4.4: date, open, last, high, low)."""
    d = sheet.copy()
    d.columns = ["date", "open", "close", "high", "low"]
    d["date"] = pd.to_datetime(d["date"])
    return d.set_index("date").sort_index()


def parse_dividends(sheet: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """load_workbook's per-stock dividend parsing: cash types only (the frozen CASH_TYPES), stored
    amounts summed by ex-date. Also returns the rows used. The amounts are used as stored; for 1306
    they are the corrected ones, and RAW / 10 is never recomputed (P2-1)."""
    d = sheet.copy()
    d.columns = ["declared", "ex", "record", "pay", "amount", "freq", "type"]
    d = d[d["type"].isin(pass1.CASH_TYPES)].copy()
    d["ex"] = pd.to_datetime(d["ex"], errors="coerce")
    d["amount"] = pd.to_numeric(d["amount"], errors="coerce")
    used = d.dropna(subset=["ex", "amount"])
    return used.groupby("ex")["amount"].sum(), used


def hedge_1306(px: pd.DataFrame, dist: pd.Series, cal: pd.DatetimeIndex) -> pd.DataFrame:
    """y_1306_oc = ln(close/open); ao_1306_gap_raw = ln(open_t/close_{t-1});
    ao_1306_gap_adj = ln(open_t/(close_{t-1} - D_t)), D_t the distribution with ex-date t, else 0
    (the frozen miners' ao_gap_adj rule). `px` is indexed by the calendar `cal`."""
    p = px.reindex(cal)
    prev = p.close.shift(1)
    D = dist.reindex(cal).fillna(0.0)
    return pd.DataFrame({"y_1306_oc": np.log(p.close / p.open),
                         "ao_1306_gap_raw": np.log(p.open / prev),
                         "ao_1306_gap_adj": np.log(p.open / (prev - D))}, index=cal)


# ---------------------------------------------------------- TOPIX TR
def parse_topix_tr(sheet: pd.DataFrame) -> pd.Series:
    """`TOPIX optional` sheet (no header; date, total-return close)."""
    d = sheet.copy()
    d.columns = ["date", "close"]
    d["date"] = pd.to_datetime(d["date"])
    return d.set_index("date")["close"].sort_index()


def topix_tr_component(tr: pd.Series, pr: pd.Series) -> pd.Series:
    """The TOPIX dividend component on day t: ln(TR_t/TR_{t-1}) - ln(PR_t/PR_{t-1}), both on the
    miners' calendar with 2020-10-01 dropped. ao_topix_gap_tradj = ao_topix_gap + this (P40)."""
    return np.log(tr / tr.shift(1)) - np.log(pr / pr.shift(1))


# ------------------------------------------------------- dark window
def dark_window(ts: np.ndarray, px: np.ndarray, cal: pd.DatetimeIndex, name: str) -> pd.DataFrame:
    """The frozen fx_windows, unchanged: the usdjpy_ window, bars and staleness rule applied to
    another minute series (XAU, Japan 225)."""
    return pass1.fx_windows(ts, px, cal, name)


def dark_window_instants(cal: pd.DatetimeIndex) -> pd.DataFrame:
    """fx_windows' bounds for every night, including nights where fx_windows records none:
    start = TSE close of t_prev (15:00 JST; 15:30 if t_prev >= 2024-11-05), end = 08:59 JST on t."""
    rows = []
    for k in range(1, len(cal)):
        prev, cur = cal[k - 1], cal[k]
        ch, cm = (15, 30) if prev >= pass1.TSE_CLOSE_CHANGE else (15, 0)
        rows.append(dict(date=cur, window_start_utc=pd.Timestamp(pass1.jst_to_utc(prev, ch, cm)),
                         window_end_utc=pd.Timestamp(pass1.jst_to_utc(cur, 8, 59))))
    return pd.DataFrame(rows).set_index("date")


# ------------------------------------------------------- session FX
def session_close_jst(day: pd.Timestamp) -> tuple[int, int]:
    """TSE close of day t itself: 15:00 JST through 2024-11-04, 15:30 JST from 2024-11-05."""
    return (15, 30) if day >= pass1.TSE_CLOSE_CHANGE else (15, 0)


def session_fx(ts: np.ndarray, px: np.ndarray, cal: pd.DatetimeIndex, name: str) -> pd.DataFrame:
    """c_<name>_sess_ret = ln(P(t, close) / P(t, 09:00:00 JST)), with the instants used."""
    rows = []
    for day in cal:
        t0 = pass1.jst_to_utc(day, 9, 0)
        t1 = pass1.jst_to_utc(day, *session_close_jst(day))
        p0, p1 = pass1.price_at(ts, px, t0)[0], pass1.price_at(ts, px, t1)[0]
        rows.append({"date": day, f"c_{name}_sess_ret": float(np.log(p1 / p0)),
                     "session_open_utc": pd.Timestamp(t0), "session_close_utc": pd.Timestamp(t1)})
    return pd.DataFrame(rows).set_index("date")


# ------------------------------------------------------- US session
def ny_instant(day: pd.Timestamp, hh: int, mm: int) -> np.datetime64:
    """hh:mm America/New_York on `day`, as naive UTC (DST from the tz database)."""
    t = pd.Timestamp(day.year, day.month, day.day, hh, mm).tz_localize(NY_TZ).tz_convert("UTC")
    return np.datetime64(t.tz_localize(None), "ns")


def us_session_instants(day: pd.Timestamp, early_closes) -> tuple[np.datetime64, np.datetime64]:
    """P49: open 09:30 ET; close 16:00 ET, or 13:00 ET on an NYSE early-close day."""
    early = {day_key(d) for d in early_closes}
    close = (13, 0) if day_key(day) in early else (16, 0)
    return ny_instant(day, 9, 30), ny_instant(day, *close)


def us_session_dates(uscal: pd.DatetimeIndex, cal: pd.DatetimeIndex) -> dict:
    """us_features' session set (P11) for each night t = cal[k]: NY dates d with t_prev <= d <= t - 1."""
    return {cal[k]: uscal[(uscal >= cal[k - 1]) & (uscal <= cal[k] - pd.Timedelta(days=1))]
            for k in range(1, len(cal))}


def usdjpy_us_ret(ts: np.ndarray, px: np.ndarray, uscal: pd.DatetimeIndex, cal: pd.DatetimeIndex,
                  early_closes) -> pd.DataFrame:
    """P49: sum over the night's NY sessions of ln(P(close_d) / P(open_d)) on the USD/JPY master;
    exactly 0.0 when the night has no session. Also returns the number of sessions summed."""
    rows = []
    for cur, sess in us_session_dates(uscal, cal).items():
        total = 0.0
        for d in sess:
            t0, t1 = us_session_instants(d, early_closes)
            total += float(np.log(pass1.price_at(ts, px, t1)[0] / pass1.price_at(ts, px, t0)[0]))
        rows.append(dict(date=cur, usdjpy_us_ret=total if len(sess) else 0.0, us_sessions_summed=len(sess)))
    return pd.DataFrame(rows).set_index("date")


# ------------------------------------------------------------ gotobi
def gotobi_map(cal: pd.DatetimeIndex) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """P48: every nominal date (the 5th, 10th, 15th, 20th, 25th and 30th where it exists, and the
    month's last calendar day) with the trading day it lands on: itself, or the preceding trading
    day of `cal`, even in the previous month. Nominal dates outside [cal[0], cal[-1]] are skipped:
    the calendar beyond it is unknown (forward holdout, P13)."""
    out = []
    for m in pd.period_range(cal[0], cal[-1], freq="M"):
        last = m.days_in_month
        for day in sorted({x for x in GOTOBI_DAYS if x <= last} | {last}):
            nom = pd.Timestamp(m.year, m.month, day)
            if nom < cal[0] or nom > cal[-1]:
                continue
            out.append((nom, cal[cal.searchsorted(nom, side="right") - 1]))
    return out


def gotobi_flags(cal: pd.DatetimeIndex) -> pd.Series:
    """gotobi_day_t = 1 if at least one nominal date lands on trading day t (one flag, the union)."""
    hit = {day_key(t) for _, t in gotobi_map(cal)}
    return pd.Series([int(day_key(d) in hit) for d in cal], index=cal, name="gotobi_day")
