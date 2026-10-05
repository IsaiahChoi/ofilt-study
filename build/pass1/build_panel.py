"""Build the analysis panel for the prediction version of the study.

One row per (stock, Tokyo trading day t). Columns fall in three groups:
  * no prefix : known by 08:59 JST on day t (pre-open). Usable in the
                MOO-tradable specification.
  * `ao_`     : known only AT the 09:00 opening auction (they use day t's
                opening price). Usable only in the auction-conditional
                specification, which is tradable only from a post-open
                price, not at the auction.
  * `y_`      : outcomes of day t's session. Targets only, never features.

The panel stores raw ingredients only. Anything requiring an estimated
coefficient (beta to TOPIX for abnormal returns; the projection of
USD/JPY on EUR/USD for the dollar/yen split) is left to model code,
where it must be estimated on development data or on past data only.

Conventions (verified, Sept 2026):
* Dukascopy bars are true UTC and START-labeled: the bar labeled 12:30
  covers 12:30:00-12:30:59 and its close is the price at ~12:31:00.
* So "price at instant X" = close of the last bar labeled <= X - 1 min.
* Window start = TSE close of the previous session (15:00 JST until
  2024-11-04, 15:30 JST from 2024-11-05). Window end = 08:59:00 JST on
  day t (close of bar labeled 08:58), a 60-second buffer before the
  09:00 opening auction.
* Miner prices: capital changes adjusted, cash dividends NOT adjusted;
  dividend amounts are on the same share basis.

usage:  python build_panel.py <uploads_dir> <out_dir>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SPLIT_DATE = pd.Timestamp("2022-01-01")  # dev < SPLIT_DATE <= confirm; Plan 7.2 Design 1; signed off 2026-09-30 (DECISIONS P10)
TSE_CLOSE_CHANGE = pd.Timestamp("2024-11-05")
STOCKS = ["5713", "5711", "5706"]
US = ["SPY", "EWJ", "FCX", "COPX"]
CASH_TYPES = {"Final", "Interim", "Regular Cash", "Special Cash", "Memorial"}


# ---------------------------------------------------------------- loaders
def load_workbook(path: Path):
    X = pd.read_excel(path, sheet_name=None, header=None)
    px = {}
    for t in STOCKS:
        d = X[t].copy()
        d.columns = ["date", "open", "close", "high", "low"]  # order verified empirically
        d["date"] = pd.to_datetime(d["date"])
        px[t] = d.set_index("date").sort_index()
    cal = px[STOCKS[0]].index
    for t in STOCKS[1:]:
        assert px[t].index.equals(cal), f"{t} calendar differs"

    top = X["TOPIX"].copy()
    top.columns = ["date", "open", "close"]
    top["date"] = pd.to_datetime(top["date"])
    top = top.set_index("date").drop(pd.Timestamp("2020-10-01"))  # TSE outage: stale row
    assert top.index.equals(cal), "TOPIX calendar differs from miners after outage fix"

    us = {}
    for t in US:
        d = X[t].copy()
        d.columns = ["date", "open", "close"]
        d["date"] = pd.to_datetime(d["date"])
        d = d.set_index("date").sort_index()
        stale = (d.open == d.close) & (d.open == d.close.shift(1))
        d.loc[stale, ["open", "close"]] = np.nan  # EWJ: 3 stale rows 2015-16
        us[t] = d
    uscal = us["SPY"].index
    for t in US[1:]:
        assert us[t].index.equals(uscal), f"{t} US calendar differs"

    div = {}
    for t in STOCKS:
        d = X[f"{t} dividends"].copy()
        d.columns = ["declared", "ex", "record", "pay", "amount", "freq", "type"]
        d = d[d["type"].isin(CASH_TYPES)].copy()
        d["ex"] = pd.to_datetime(d["ex"], errors="coerce")
        d["amount"] = pd.to_numeric(d["amount"], errors="coerce")
        div[t] = d.dropna(subset=["ex", "amount"]).groupby("ex")["amount"].sum()
    return px, top, us, div, cal, uscal


def load_fx(path: Path) -> tuple[np.ndarray, np.ndarray]:
    d = pd.read_csv(path, usecols=["ts_utc", "close"], parse_dates=["ts_utc"])
    d = d.sort_values("ts_utc")
    ts = d["ts_utc"].dt.tz_convert("UTC").dt.tz_localize(None).values.astype("datetime64[ns]")
    return ts, d["close"].to_numpy()


# ------------------------------------------------------------- FX windows
def jst_to_utc(day: pd.Timestamp, hh: int, mm: int) -> np.datetime64:
    return np.datetime64(day + pd.Timedelta(hours=hh, minutes=mm) - pd.Timedelta(hours=9), "ns")


def price_at(ts, px, instant: np.datetime64):
    """Close of the last bar labeled <= instant - 1 min, i.e. the last
    price known at `instant`. Returns (price, staleness_minutes, idx)."""
    target_label = instant - np.timedelta64(1, "m")
    i = np.searchsorted(ts, target_label, side="right") - 1
    if i < 0:
        return np.nan, np.nan, -1
    stale = (target_label - ts[i]) / np.timedelta64(1, "m")
    return px[i], float(stale), i


def fx_windows(ts, px, cal: pd.DatetimeIndex, name: str) -> pd.DataFrame:
    out = []
    for k in range(1, len(cal)):
        prev, cur = cal[k - 1], cal[k]
        ch, cm = (15, 30) if prev >= TSE_CLOSE_CHANGE else (15, 0)
        t0 = jst_to_utc(prev, ch, cm)
        t1 = jst_to_utc(cur, 8, 59)
        p0, s0, i0 = price_at(ts, px, t0)
        p1, s1, i1 = price_at(ts, px, t1)
        if i0 < 0 or i1 <= i0:
            out.append(dict(date=cur)); continue
        r = np.diff(np.log(px[i0:i1 + 1]))
        out.append(dict(
            date=cur,
            **{f"{name}_ret": float(np.log(p1 / p0)),
               f"{name}_rv": float((r ** 2).sum()),
               f"{name}_bv": float((np.pi / 2) * (np.abs(r[1:]) * np.abs(r[:-1])).sum()),
               f"{name}_bars": int(i1 - i0),
               f"{name}_stale_start_min": s0,
               f"{name}_stale_end_min": s1},
            window_start_utc=pd.Timestamp(t0), window_end_utc=pd.Timestamp(t1),
            window_hours=float((t1 - t0) / np.timedelta64(1, "h")),
        ))
    return pd.DataFrame(out).set_index("date")


# ------------------------------------------------------------ US sessions
def us_features(us, uscal, cal) -> pd.DataFrame:
    """US sessions inside Tokyo night t: NY dates d with t_prev <= d <= t-1.
    (A NY session opens 22:30/23:30 JST and closes 05:00/06:00 JST the next
    calendar day, so this set lies entirely inside the dark window.)"""
    oc = {t: np.log(us[t].close / us[t].open) for t in US}
    rows = []
    for k in range(1, len(cal)):
        prev, cur = cal[k - 1], cal[k]
        sess = uscal[(uscal >= prev) & (uscal <= cur - pd.Timedelta(days=1))]
        row = dict(date=cur, us_n_sessions=len(sess))
        for t in US:
            v = oc[t].reindex(sess)
            row[f"{t.lower()}_oc"] = 0.0 if len(sess) == 0 else (np.nan if v.isna().any() else float(v.sum()))
        rows.append(row)
    return pd.DataFrame(rows).set_index("date")


# ------------------------------------------------------------- calendars
def sq_flags(cal: pd.DatetimeIndex) -> pd.DataFrame:
    """SQ = 2nd Friday of each month, moved to the previous trading day if a holiday."""
    f = pd.DataFrame(index=cal, data={"sq_day": 0, "sq_major": 0})
    for m in pd.period_range(cal[0], cal[-1], freq="M"):
        first = m.start_time
        fri = first + pd.Timedelta(days=(4 - first.weekday()) % 7 + 7)
        d = cal[cal <= fri]
        if len(d) and d[-1].to_period("M") == m:
            f.loc[d[-1], "sq_day"] = 1
            f.loc[d[-1], "sq_major"] = int(m.month in (3, 6, 9, 12))
    return f


def event_rows(dates, cal: pd.DatetimeIndex, span: int) -> set:
    """Map release dates to trading rows. D* = first trading day >= D;
    flag D*, ..., D*+span-1 (span=2 gives D and D+1)."""
    hit = set()
    for d in pd.to_datetime(dates):
        k = cal.searchsorted(d)
        hit.update(cal[k:k + span])
    return hit


# ------------------------------------------------------------------ main
def main(up: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    px, top, us, div, cal, uscal = load_workbook(up / "Book2.xlsx")

    print("FX windows...", flush=True)
    jpy = fx_windows(*load_fx(up / "usdjpy_dukascopy_2015-01-01_2026-03-05.csv"), cal, "usdjpy")
    eur = fx_windows(*load_fx(up / "eurusd_dukascopy_2015-01-01_2026-03-05.csv"), cal, "eurusd")
    eur = eur.drop(columns=["window_start_utc", "window_end_utc", "window_hours"])
    mkt = jpy.join(eur).join(us_features(us, uscal, cal)).join(sq_flags(cal))
    mkt["ao_topix_gap"] = np.log(top.open / top.close.shift(1))
    mkt["topix_oc_lag1"] = np.log(top.close / top.open).shift(1)
    mkt["y_topix_oc"] = np.log(top.close / top.open)
    boj = set(pd.to_datetime(pd.read_csv("events_boj.csv")["announcement_date"]))
    mkt["boj_day"] = mkt.index.isin(boj).astype(int)

    ev = pd.read_csv("events_firm.csv", dtype={"ticker": str})
    frames = []
    for t in STOCKS:
        p = px[t]
        d = pd.DataFrame(index=cal)
        d["ticker"] = t
        d["open"], d["close"] = p.open, p.close
        d["prev_close"] = p.close.shift(1)
        d["div_exdate"] = div[t].reindex(cal).fillna(0.0)
        d["exdiv_day"] = (d.div_exdate > 0).astype(int)
        d["ao_gap_raw"] = np.log(d.open / d.prev_close)
        d["ao_gap_adj"] = np.log(d.open / (d.prev_close - d.div_exdate))  # Plan P2
        d["oc_lag1"] = np.log(p.close / p.open).shift(1)
        d["range_lag1"] = np.log(p.high / p.low).shift(1)
        d["y_oc"] = np.log(p.close / p.open)          # TARGET (raw; abnormal built in model code)
        e = ev[ev.ticker == t]
        for col, cat, span in [("earn_flag", "TANSHIN", 2), ("news_flag", "STANDALONE_NEWS", 2),
                               ("mech_flag", "MECHANICAL", 1), ("audit_flag", "AUDIT_CANDIDATE", 2)]:
            d[col] = d.index.isin(event_rows(e[e.category == cat].date, cal, span)).astype(int)
        d["gap_adj_lag1"] = d.ao_gap_adj.shift(1)
        frames.append(d.join(mkt))
    P = pd.concat(frames).rename_axis("date").reset_index()
    P = P[P.date > cal[0]]  # first day has no previous session

    # ---------------------------------------------------------- checks
    assert (P.window_end_utc < P.date + pd.Timedelta(hours=0)).all()  # 08:59 JST = 23:59 UTC prev day
    assert ((P.window_end_utc + pd.Timedelta(hours=9)).dt.time == pd.Timestamp("08:59").time()).all()
    assert P[["usdjpy_ret", "eurusd_ret", "y_oc", "ao_gap_adj"]].notna().all().all(), "core NaNs"
    assert (P.usdjpy_stale_end_min <= 5).mean() > 0.99, "end staleness unexpectedly high"
    assert P.groupby("ticker").date.is_monotonic_increasing.all()

    cols = ["date", "ticker",
            # known before 09:00 JST on day t
            "usdjpy_ret", "usdjpy_rv", "usdjpy_bv", "eurusd_ret", "eurusd_rv",
            "spy_oc", "ewj_oc", "fcx_oc", "copx_oc", "us_n_sessions",
            "window_hours", "gap_adj_lag1", "oc_lag1", "range_lag1", "topix_oc_lag1",
            "earn_flag", "news_flag", "mech_flag", "audit_flag", "boj_day",
            "sq_day", "sq_major", "exdiv_day", "div_exdate",
            # known only at the 09:00 auction -- auction-conditional spec only
            "ao_gap_adj", "ao_gap_raw", "ao_topix_gap",
            # outcomes of day t's session -- TARGETS ONLY
            "y_oc", "y_topix_oc",
            # provenance / QA
            "open", "close", "prev_close", "window_start_utc", "window_end_utc",
            "usdjpy_bars", "usdjpy_stale_start_min", "usdjpy_stale_end_min",
            "eurusd_bars", "eurusd_stale_end_min"]
    P = P[cols]

    dev, conf = P[P.date < SPLIT_DATE], P[P.date >= SPLIT_DATE]
    dev.to_csv(out / "panel_dev.csv", index=False)
    conf.to_csv(out / "panel_confirm_SEALED.csv", index=False)

    def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    manifest = {
        "built": pd.Timestamp.now(tz="UTC").isoformat(),
        "split_date": str(SPLIT_DATE.date()),
        "inputs": {f: sha(up / f) for f in ["Book2.xlsx",
                   "usdjpy_dukascopy_2015-01-01_2026-03-05.csv",
                   "eurusd_dukascopy_2015-01-01_2026-03-05.csv"]},
        "event_files": {f: sha(f) for f in ["events_firm.csv", "events_boj.csv"]},
        "outputs": {
            "panel_dev.csv": {"sha256": sha(out / "panel_dev.csv"), "rows": len(dev),
                              "span": [str(dev.date.min().date()), str(dev.date.max().date())]},
            "panel_confirm_SEALED.csv": {"sha256": sha(out / "panel_confirm_SEALED.csv"),
                                         "rows": len(conf),
                                         "span": [str(conf.date.min().date()), str(conf.date.max().date())]},
        },
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest["outputs"], indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
