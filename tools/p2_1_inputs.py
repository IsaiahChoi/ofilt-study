"""P2-1 (Pass 2): validate the new inputs. Reproduces DATA_PROVENANCE §4 on the raw files and compares
the results with PASS2_ADDENDUM Appendix B′ at the precision B′ states. Reports only: writes
reports/P2_1_inputs.md and prints the same text.

Blinding (builder prompt A′, hard rules 1-3):
* every input is hash-verified against docs/PASS2_INPUTS.json before it is read;
* nothing relates a predictor to a target;
* dev (dates < 2022-01-01): predictor-only, hedge-only (1306) and calendar-only statistics;
* 2022+: dates, counts and booleans only. No 2022+ price, return, amount, yield or share is printed.

usage: python tools/p2_1_inputs.py <raw_dir>
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
from dateutil.easter import easter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ofilt.drift.calendar import confirmation_calendar  # noqa: E402

SPLIT = pd.Timestamp("2022-01-01")
BOOK2, FIXED, ORIG = "Book2.xlsx", "newbloombergdata_fixed.xlsx", "newbloombergdata.xlsx"
XAU = "xauusd_dukascopy_2015-01-01_2026-03-05.csv.gz"
N225 = "jpn225_dukascopy_2015-01-01_2026-03-05.csv.gz"
DIV_COLS = ["declared", "ex", "record", "pay", "amount", "freq", "type"]
OUTAGE = pd.Timestamp("2020-10-01")
MOVE = 0.02                       # "1-minute moves over 2%": |ln(close_i / close_{i-1})| over consecutive bars
FRESH_MIN = 5                     # P42: at most 5 minutes stale
EARLY_CLOSES = pd.DatetimeIndex([  # P49 / B′: NYSE 13:00 ET closes, 2015-01 -> 2026-03-05
    "2015-11-27", "2015-12-24", "2016-11-25", "2017-07-03", "2017-11-24", "2018-07-03", "2018-11-23",
    "2018-12-24", "2019-07-03", "2019-11-29", "2019-12-24", "2020-11-27", "2020-12-24", "2021-11-26",
    "2022-11-25", "2023-07-03", "2023-11-24", "2024-07-03", "2024-11-29", "2024-12-24", "2025-07-03",
    "2025-11-28", "2025-12-24"])

# Appendix B′ (and DATA_PROVENANCE §4 where B′ is silent), at the precision they state.
B = {
    "1306_rows": 2728, "1306_stale_dev": ["2016-12-14", "2017-02-23", "2017-05-29", "2017-06-26", "2018-05-21"],
    "1306_stale_conf": ["2023-10-06"],
    "div_rows": 11, "div_dev": 7, "div_conf": 4,
    "div_dev_raw": {"2015-07-08": 23.0, "2016-07-06": 27.3, "2017-07-06": 26.0, "2018-07-06": 30.5,
                    "2019-07-08": 33.3, "2020-07-09": 32.9, "2021-07-08": 36.6},
    "div_dev_amount": [2.30, 2.73, 2.60, 3.05, 3.33, 3.29, 3.66],
    "div_dev_yield_pct": [1.36, 2.10, 1.55, 1.75, 2.00, 2.01, 1.80],
    "div_dev_drop_pct": {"2017-07-06": 1.55, "2019-07-08": 2.16, "2020-07-09": 2.14, "2021-07-08": 2.01},
    "div_raw_yield_band_pct": (13.6, 21.0),
    "tr_rows": 2729, "tr_first_close": 1916.75,
    "xau_rows": 3957473, "xau_span": ("2015-01-01 23:00", "2026-03-06 00:00"), "xau_outliers": 4,
    "xau_outlier_days": ["2015-07-20", "2020-03-15", "2021-08-08/09", "2026-01-29 15:27"],
    "n225_rows": 3314917, "n225_span": ("2015-01-02 00:00", "2026-03-06 00:00"), "n225_moves": 30,
    "n225_fresh_2015H1": 37, "n225_changeover": "2018-07-02",
    "gotobi_dev": 529, "gotobi_dev_by_year": [74, 76, 78, 77, 75, 75, 74], "gotobi_conf": 319,
    "gotobi_rolls": [("2019-05-05", "2019-04-26"), ("2020-01-05", "2019-12-30"), ("2021-05-05", "2021-04-30"),
                     ("2025-01-05", "2024-12-30")],
    "early_closes": 23,
}

out: list[str] = []
cmp_rows: list[tuple[str, str, str, bool]] = []


def say(s: str = "") -> None:
    out.append(s)


def compare(quantity: str, bprime, found, ok: bool) -> None:
    cmp_rows.append((quantity, str(bprime), str(found), bool(ok)))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def d(ts) -> str:
    return pd.Timestamp(ts).strftime("%Y-%m-%d")


def dm(ts) -> str:
    return pd.Timestamp(ts).strftime("%Y-%m-%d %H:%M")


def first_col_dates(path: Path, sheet: str) -> pd.DatetimeIndex:
    col = pd.read_excel(path, sheet_name=sheet, header=None, usecols=[0])[0]
    return pd.DatetimeIndex(pd.to_datetime(col)).as_unit("ns").sort_values()


def frozen_cash_types() -> set:
    sys.dont_write_bytecode = True   # leave build/pass1/ untouched
    spec = importlib.util.spec_from_file_location("frozen_build_panel", ROOT / "build" / "pass1" / "build_panel.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return set(mod.CASH_TYPES)


# ------------------------------------------------------------------ inputs
def verify(raw: Path) -> None:
    reg = json.loads((ROOT / "docs" / "PASS2_INPUTS.json").read_text(encoding="utf-8"))["inputs"]
    say("## 0. Input hashes (verified before any read)")
    say()
    for name in (BOOK2, FIXED, ORIG, XAU, N225):
        ok = sha256(raw / name) == reg[name]["sha256"]
        say(f"- `{name}`: SHA-256 equals docs/PASS2_INPUTS.json: {ok}")
        if not ok:
            print("\n".join(out))
            sys.exit(f"STOP: hash mismatch for {name}")
    say()


# --------------------------------------------------------------- calendars
def calendars(raw: Path):
    cal = first_col_dates(raw / BOOK2, "5713")
    same = all(first_col_dates(raw / BOOK2, t).equals(cal) for t in ("5711", "5706"))
    uscal = first_col_dates(raw / BOOK2, "SPY")
    say("## 1. Calendars (Book2)")
    say()
    say(f"- Miners' calendar: {len(cal):,} dates, {d(cal[0])} → {d(cal[-1])}; 5711 and 5706 identical to 5713: {same}")
    say(f"- 2020-10-01 (TSE outage) absent from the miners' calendar: {OUTAGE not in cal}")
    say(f"- US calendar (SPY sheet): {len(uscal):,} dates, {d(uscal[0])} → {d(uscal[-1])}")
    say()
    return cal, uscal


# --------------------------------------------------------------------- 1306
def check_1306(X: dict, cal: pd.DatetimeIndex):
    p = X["1306"].copy()
    p.columns = ["date", "open", "close", "high", "low"]
    p["date"] = pd.to_datetime(p["date"]).dt.as_unit("ns")
    nulls = int(p.isna().sum().sum())
    dups = int(p["date"].duplicated().sum())
    p = p.set_index("date").sort_index()
    dev, conf = p.index < SPLIT, p.index >= SPLIT
    prev = p.close.shift(1)
    viol = (p.low > p[["open", "close"]].min(axis=1)) | (p.high < p[["open", "close"]].max(axis=1)) | (p.low <= 0)
    gap_art = np.abs(np.log(p.open / prev)) > 0.5
    cc_art = np.abs(np.log(p.close / prev)) > 0.5
    stale = (p.open == p.close) & (p.open == prev)
    rng = p.high > p.low
    same_cal = p.index.equals(cal)
    say("## 2. 1306 prices (sheet `1306` of the fixed workbook)")
    say()
    say(f"- Rows: {len(p):,}; nulls: {nulls}; duplicate dates: {dups}")
    say(f"- Dates identical to the miners' calendar: {same_cal} (span {d(p.index[0])} → {d(p.index[-1])})")
    say(f"- OHLC violations (low > min(open, close), high < max(open, close), or low ≤ 0): dev {int(viol[dev].sum())}; "
        f"2022+ {int(viol[conf].sum())}")
    say(f"- Split artifacts (|ln(open/prev close)| > 0.5): dev {int(gap_art[dev].sum())}; 2022+ {int(gap_art[conf].sum())}. "
        f"(|ln(close/prev close)| > 0.5): dev {int(cc_art[dev].sum())}; 2022+ {int(cc_art[conf].sum())}")
    sd, sc = list(p.index[stale & dev]), list(p.index[stale & conf])
    say(f"- Rows with open = close = previous close: {int(stale.sum())} (dev {len(sd)}, 2022+ {len(sc)})")
    say(f"  - dev dates: {', '.join(d(x) for x in sd)}; all with high > low: {bool(rng[stale & dev].all())}")
    say(f"  - 2022+: count {len(sc)}; equal to DATA_PROVENANCE's 2022+ date: {[d(x) for x in sc] == B['1306_stale_conf']}; "
        f"all with high > low: {bool(rng[stale & conf].all())}")
    say()
    compare("1306 rows", B["1306_rows"], len(p), len(p) == B["1306_rows"])
    compare("1306 calendar identical to the miners'", True, same_cal, same_cal)
    compare("1306 open = close = previous close rows", "6 (5 dev dates as listed + 1 in 2022+)",
            f"{int(stale.sum())} (dev dates match: {[d(x) for x in sd] == B['1306_stale_dev']}; "
            f"2022+ matches: {[d(x) for x in sc] == B['1306_stale_conf']})",
            int(stale.sum()) == 6 and [d(x) for x in sd] == B["1306_stale_dev"] and [d(x) for x in sc] == B["1306_stale_conf"])
    return p


def check_dividends(X: dict, p: pd.DataFrame, cal: pd.DatetimeIndex):
    fx = X["1306 dividends"].copy()
    rw = X["1306 dividends RAW"].copy()
    fx.columns, rw.columns = DIV_COLS, DIV_COLS
    for f in (fx, rw):
        for c in ("declared", "ex", "record", "pay"):
            f[c] = pd.to_datetime(f[c]).dt.as_unit("ns")
    fx, rw = fx.sort_values("ex").reset_index(drop=True), rw.sort_values("ex").reset_index(drop=True)
    same_other = all(fx[c].equals(rw[c]) for c in ("declared", "ex", "record", "pay", "freq"))
    float_eq = bool((fx.amount == rw.amount / 10).all())
    dec_eq = all(Decimal(repr(float(a))) == Decimal(repr(float(r))) / 10 for a, r in zip(fx.amount, rw.amount))
    cash = frozen_cash_types()
    dev, conf = fx.ex < SPLIT, fx.ex >= SPLIT
    pos = p.index.get_indexer(fx.ex)
    in_cal = fx.ex.isin(cal).to_numpy()
    prev_close = pd.Series([p.close.iloc[k - 1] if k > 0 else np.nan for k in pos], index=fx.index)
    ex_open = pd.Series([p.open.iloc[k] if k >= 0 else np.nan for k in pos], index=fx.index)
    y_corr = 100 * fx.amount / prev_close
    y_raw = 100 * rw.amount / prev_close
    drop = 100 * (1 - ex_open / prev_close)
    july = (fx.ex.dt.month == 7)
    rec10 = (fx.record.dt.month == 7) & (fx.record.dt.day == 10) & (fx.record.dt.year == fx.ex.dt.year)
    lo, hi = B["div_raw_yield_band_pct"]
    band = (y_raw.round(1) >= lo) & (y_raw.round(1) <= hi)
    say("## 3. 1306 dividends (sheets `1306 dividends` and `1306 dividends RAW`)")
    say()
    say(f"- Rows: fixed {len(fx)}, RAW {len(rw)}; dev {int(dev.sum())}, 2022+ {int(conf.sum())}")
    say(f"- Types: fixed {sorted(set(fx.type))}; RAW {sorted(set(rw.type))}. Frozen build CASH_TYPES contains "
        f"'Regular Cash': {'Regular Cash' in cash}; contains 'Distribution': {'Distribution' in cash}")
    say(f"- Fixed amount = RAW amount ÷ 10: float equality {float_eq}; decimal equality of the stored values {dec_eq}")
    say(f"- Declared, ex, record, pay and frequency columns identical between fixed and RAW: {same_other}")
    say(f"- Every ex-date is in the miners' calendar: dev {bool(in_cal[dev.to_numpy()].all())}; 2022+ {bool(in_cal[conf.to_numpy()].all())}")
    say(f"- Every ex-date is in July: dev {bool(july[dev].all())}; 2022+ {bool(july[conf].all())}. "
        f"Record date 10 July of the same year: dev {bool(rec10[dev].all())}; 2022+ {bool(rec10[conf].all())}")
    say(f"- RAW amount / prior close within {lo}–{hi}% (1 dp) on every ex-date: dev {bool(band[dev].all())}; 2022+ {bool(band[conf].all())}")
    say()
    say("Dev ex-dates (prior close = 1306 close on the previous trading day; drop = 1 − open/prior close):")
    say()
    say("| Ex-date | RAW amount | Corrected | RAW / prior close | Corrected / prior close | Ex-day opening drop |")
    say("|---|---|---|---|---|---|")
    for i in fx.index[dev]:
        say(f"| {d(fx.ex[i])} | {rw.amount[i]:.1f} | {fx.amount[i]:.2f} | {y_raw[i]:.1f}% | {y_corr[i]:.2f}% | {drop[i]:.2f}% |")
    say()
    say("2022+: booleans and counts only (above).")
    say()
    exd = [d(x) for x in fx.ex[dev]]
    raw_ok = exd == list(B["div_dev_raw"]) and all(round(float(rw.amount[i]), 1) == B["div_dev_raw"][d(fx.ex[i])] for i in fx.index[dev])
    amt = [round(float(a), 2) for a in fx.amount[dev]]
    yl = [round(float(y), 2) for y in y_corr[dev]]
    drops = {d(fx.ex[i]): round(float(drop[i]), 2) for i in fx.index[dev] if d(fx.ex[i]) in B["div_dev_drop_pct"]}
    compare("1306 dividend rows (dev / 2022+)", f"{B['div_rows']} ({B['div_dev']} / {B['div_conf']})",
            f"{len(fx)} ({int(dev.sum())} / {int(conf.sum())})",
            len(fx) == B["div_rows"] and int(dev.sum()) == B["div_dev"] and int(conf.sum()) == B["div_conf"])
    n_float = int((fx.amount != rw.amount / 10).sum())
    compare("1306 dividends all Regular Cash; amounts = RAW ÷ 10 exactly (decimal values as stored)", "True; True",
            f"{set(fx.type) == {'Regular Cash'}}; decimal {dec_eq} (binary float RAW/10 differs in the last bit on "
            f"{n_float} of {len(fx)} rows)", set(fx.type) == {"Regular Cash"} and dec_eq)
    compare("1306 dev ex-dates and RAW amounts (DATA_PROVENANCE §4.4)", "as listed", raw_ok, raw_ok)
    compare("1306 dev corrected amounts (yen, 2 dp)", " / ".join(f"{x:.2f}" for x in B["div_dev_amount"]),
            " / ".join(f"{x:.2f}" for x in amt), amt == B["div_dev_amount"])
    compare("1306 dev implied yields (%, 2 dp)", " / ".join(f"{x:.2f}" for x in B["div_dev_yield_pct"]),
            " / ".join(f"{x:.2f}" for x in yl), yl == B["div_dev_yield_pct"])
    compare("1306 ex-day opening drops (%, 2 dp; DATA_PROVENANCE §4.4)",
            ", ".join(f"{k} {v:.2f}" for k, v in B["div_dev_drop_pct"].items()),
            ", ".join(f"{k} {v:.2f}" for k, v in drops.items()), drops == B["div_dev_drop_pct"])


def check_topix_tr(X: dict, O: dict, cal: pd.DatetimeIndex):
    tr = X["TOPIX optional"].copy()
    tr.columns = ["date", "close"]
    tr["date"] = pd.to_datetime(tr["date"]).dt.as_unit("ns")
    nulls = int(tr.isna().sum().sum())
    dups = int(tr.date.duplicated().sum())
    tr = tr.set_index("date").sort_index()
    plus = set(tr.index) == set(cal) | {OUTAGE}
    after = tr.drop(OUTAGE).index.equals(cal) if OUTAGE in tr.index else False
    first_ok = float(tr.close.iloc[0]) == B["tr_first_close"]
    say("## 4. TOPIX total return (sheet `TOPIX optional`; ticker TPXDDVD Index per D3 / P40)")
    say()
    say(f"- Rows: {len(tr):,}; nulls: {nulls}; duplicate dates: {dups}")
    say(f"- Dates = miners' calendar ∪ {{2020-10-01}}: {plus}; 2020-10-01 present: {OUTAGE in tr.index}; "
        f"after dropping it, identical to the miners' calendar: {after}")
    say(f"- First date {d(tr.index[0])}; first close equals {B['tr_first_close']} (DATA_PROVENANCE §4.4): {first_ok}")
    say()
    say("Fixed workbook against the original pull (`newbloombergdata.xlsx`), cell for cell:")
    say()
    say(f"- Original sheets: {list(O)}; fixed sheets: {list(X)}")
    for fs, os_ in (("1306", "1306"), ("TOPIX optional", "TOPIX optional"), ("1306 dividends RAW", "1306 dividends")):
        eq = os_ in O and X[fs].equals(O[os_])
        say(f"- fixed `{fs}` equals original `{os_}`: {eq}")
    say(f"- The fixed workbook's `README` sheet ({X['README'].shape[0]} × {X['README'].shape[1]}, text) was not read.")
    say()
    compare("TOPIX TR calendar = miners' calendar + 2020-10-01 (rows)", f"True ({B['tr_rows']:,})",
            f"{plus} ({len(tr):,})", plus and len(tr) == B["tr_rows"])


# ------------------------------------------------------------ minute files
def load_minutes(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    m = pd.read_csv(path)
    ts = pd.to_datetime(m["ts_utc"], utc=True, format="ISO8601")
    return m, ts


def integrity(name: str, m: pd.DataFrame, ts: pd.Series) -> dict:
    o, h, lo, c = (m[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    res = dict(rows=len(m), nulls=int(m.isna().sum().sum()), dups=int(ts.duplicated().sum()),
               mono=bool(ts.is_monotonic_increasing),
               viol=int(((lo > np.minimum(o, c)) | (h < np.maximum(o, c))).sum()),
               nonpos=int((np.minimum.reduce([o, h, lo, c]) <= 0).sum()),
               flat=int(((o == h) & (h == lo) & (lo == c)).sum()),
               first=dm(ts.iloc[0]), last=dm(ts.iloc[-1]))
    say(f"- Rows: {res['rows']:,}; span {res['first']} → {res['last']} UTC")
    say(f"- Nulls {res['nulls']}; duplicate timestamps {res['dups']}; monotone {res['mono']}; OHLC violations {res['viol']}; "
        f"non-positive prices {res['nonpos']}; flat bars {res['flat']:,} of {res['rows']:,} ({100 * res['flat'] / res['rows']:.2f}%)")
    years = ts.dt.year.value_counts().sort_index()
    say("- Rows per calendar year: " + "; ".join(f"{y} {n:,}" for y, n in years.items()))
    return res


def moves(ts: pd.Series, c: np.ndarray):
    r = np.abs(np.diff(np.log(c)))
    idx = np.flatnonzero(r > MOVE) + 1
    gap_min = ((ts.iloc[idx].to_numpy() - ts.iloc[idx - 1].to_numpy()) / np.timedelta64(1, "m")).astype(float)
    return idx, gap_min


def check_xau(raw: Path):
    m, ts = load_minutes(raw / XAU)
    say("## 5. XAU/USD 1-minute (Dukascopy, bid)")
    say()
    res = integrity("xau", m, ts)
    dt = ts.diff()
    big = np.flatnonzero((dt > pd.Timedelta(hours=6)).to_numpy())
    good_fri = {easter(y) - pd.Timedelta(days=2).to_pytimedelta() for y in range(2015, 2027)}
    kinds = {"weekend": [], "Christmas / New Year": [], "Good Friday": [], "other": []}
    for i in big:
        s, e = ts.iloc[i - 1], ts.iloc[i]
        if s.weekday() == 4 and e.weekday() in (6, 0) and e - s <= pd.Timedelta(days=3):
            kinds["weekend"].append((s, e))
        elif (s.month == 12 and s.day >= 24) or (e.month == 1 and e.day <= 3) or (e.month == 12 and e.day >= 24):
            kinds["Christmas / New Year"].append((s, e))
        elif any(s.date() <= g < e.date() for g in good_fri):
            kinds["Good Friday"].append((s, e))
        else:
            kinds["other"].append((s, e))
    say(f"- Gaps over 6 h: {len(big)} (weekend {len(kinds['weekend'])}; Christmas / New Year "
        f"{len(kinds['Christmas / New Year'])}; Good Friday {len(kinds['Good Friday'])}; other {len(kinds['other'])})")
    for k in ("Christmas / New Year", "Good Friday", "other"):
        if kinds[k]:
            say(f"  - {k}: " + "; ".join(f"{dm(s)} → {dm(e)}" for s, e in kinds[k]))
    idx, gap_min = moves(ts, m["close"].to_numpy(dtype=float))
    say(f"- 1-minute moves over 2% (|ln(close / previous close)| > {MOVE}): {len(idx)}, at "
        + "; ".join(f"{dm(ts.iloc[i])} UTC (previous bar {g:.0f} min earlier)" for i, g in zip(idx, gap_min)))
    say("  (timestamps only; no magnitudes)")
    say()
    compare("XAU rows", f"{B['xau_rows']:,}", f"{res['rows']:,}", res["rows"] == B["xau_rows"])
    compare("XAU span (UTC)", " → ".join(B["xau_span"]), f"{res['first']} → {res['last']}",
            (res["first"], res["last"]) == B["xau_span"])
    literal = len(kinds["other"]) + len(kinds["Good Friday"]) == 0
    gf_years = sorted(s.year for s, _ in kinds["Good Friday"])
    compare("XAU gaps over 6 h: weekends and Christmas / New Year only (DATA_PROVENANCE §4.2, literal)", True, literal, literal)
    compare("XAU gaps over 6 h not explained by weekends, Christmas / New Year or Good Friday", 0, len(kinds["other"]),
            len(kinds["other"]) == 0)
    compare("XAU Good Friday closures (one per year, 2015–2025)", "not stated", f"{len(gf_years)} ({gf_years[0]}–{gf_years[-1]})"
            if gf_years else "0", gf_years == list(range(2015, 2026)))
    compare("XAU outlier minutes (> 2%)", f"{B['xau_outliers']} ({', '.join(B['xau_outlier_days'])})",
            f"{len(idx)} ({', '.join(dm(ts.iloc[i]) for i in idx)})", len(idx) == B["xau_outliers"])


def check_n225(raw: Path, cal: pd.DatetimeIndex):
    m, ts = load_minutes(raw / N225)
    say("## 6. Japan 225 CFD 1-minute (Dukascopy, bid; INSTRUMENT_IDX_ASIA_E_N225JAP)")
    say()
    res = integrity("n225", m, ts)
    idx, gap_min = moves(ts, m["close"].to_numpy(dtype=float))
    say(f"- 1-minute moves over 2%: {len(idx)}; preceded by a data hole of ≥ 60 min: {int((gap_min >= 60).sum())}; "
        f"≥ 30 min: {int((gap_min >= 30).sum())}")
    # freshness of the 08:59 JST price (build_panel.price_at rule): last bar labeled <= 08:58 JST = t-1 23:58 UTC
    tsn = ts.dt.tz_convert("UTC").dt.tz_localize(None).to_numpy().astype("datetime64[ns]")
    lab = cal.to_numpy().astype("datetime64[ns]") - np.timedelta64(2, "m")
    k = np.searchsorted(tsn, lab, side="right") - 1
    stale = np.where(k >= 0, (lab - tsn[np.maximum(k, 0)]) / np.timedelta64(1, "m"), np.inf)
    fresh = pd.Series(stale <= FRESH_MIN, index=cal)
    half = pd.Series([f"{x.year}-H{1 if x.month <= 6 else 2}" for x in cal], index=cal)
    say(f"- Share of Tokyo days (miners' calendar) whose 08:59 JST price is at most {FRESH_MIN} minutes stale, by half-year "
        "(dev: share; 2022+: counts and a boolean only):")
    say()
    say("| Half-year | Days | Fresh | Share |")
    say("|---|---|---|---|")
    shares = {}
    for hy, g in fresh.groupby(half, sort=True):
        if g.index[0] < SPLIT:
            shares[hy] = g.mean()
            say(f"| {hy} | {len(g)} | {int(g.sum())} | {100 * g.mean():.1f}% |")
        else:
            ok = 0.965 <= g.mean() < 0.995
            shares[hy] = ok
            say(f"| {hy} | {len(g)} | {int(g.sum())} | rounds to 97–99%: {ok} |")
    say()
    roll = fresh.astype(float).rolling(60, min_periods=60).mean()
    hit = roll.index[roll >= 0.95]
    change = d(hit[0]) if len(hit) else "never"
    say(f"- Trailing 60-day share first reaches 95% on: {change}")
    say()
    dev_h = [h for h in shares if int(h[:4]) < 2022]
    mid = [h for h in dev_h if "2015-H2" <= h <= "2018-H1"]
    late_dev = [h for h in dev_h if h >= "2018-H2"]
    late_conf = [h for h in shares if int(h[:4]) >= 2022]
    p15 = round(100 * shares["2015-H1"])
    mid_ok = all(round(100 * shares[h]) <= 1 for h in mid)
    late_ok = all(97 <= round(100 * shares[h]) <= 99 for h in late_dev) and all(shares[h] for h in late_conf)
    compare("Japan 225 rows", f"{B['n225_rows']:,}", f"{res['rows']:,}", res["rows"] == B["n225_rows"])
    compare("Japan 225 span (UTC)", " → ".join(B["n225_span"]), f"{res['first']} → {res['last']}",
            (res["first"], res["last"]) == B["n225_span"])
    compare("Japan 225 fresh 08:59 share, 2015-H1 (%)", B["n225_fresh_2015H1"], p15, p15 == B["n225_fresh_2015H1"])
    compare("Japan 225 fresh share, 2015-H2 → 2018-H1", "about 0% (each half-year ≤ 1%)",
            ", ".join(f"{h} {100 * shares[h]:.1f}%" for h in mid), mid_ok)
    compare("Japan 225 fresh share, 2018-H2 onward", "97–99% (dev shares; 2022+ boolean)",
            ", ".join(f"{h} {100 * shares[h]:.1f}%" for h in late_dev) + f"; 2022+ all True: {all(shares[h] for h in late_conf)}",
            late_ok)
    compare("Japan 225 changeover (trailing 60-day share ≥ 95%)", B["n225_changeover"], change, change == B["n225_changeover"])
    compare("Japan 225 1-minute moves over 2% (DATA_PROVENANCE §4.3)", B["n225_moves"], len(idx), len(idx) == B["n225_moves"])
    # Diagnostic (dev only): the same rule on a Mon-Fri weekday calendar instead of the miners' TSE calendar.
    wk = pd.bdate_range(cal[0], SPLIT - pd.Timedelta(days=1)).as_unit("ns")
    labw = wk.to_numpy().astype("datetime64[ns]") - np.timedelta64(2, "m")
    kw = np.searchsorted(tsn, labw, side="right") - 1
    fw = pd.Series((labw - tsn[kw]) / np.timedelta64(1, "m") <= FRESH_MIN, index=wk)
    hw = fw.groupby([f"{x.year}-H{1 if x.month <= 6 else 2}" for x in wk]).mean()
    rw60 = fw.astype(float).rolling(60, min_periods=60).mean()
    cw = d(rw60.index[rw60 >= 0.95][0])
    s18 = fresh["2018-01-01":"2018-06-30"]
    first18 = s18.index[s18.to_numpy()][0]
    say("- Diagnostic, dev only: the same rule on a Mon–Fri weekday calendar (not the miners' calendar): "
        + ", ".join(f"{h} {100 * v:.1f}%" for h, v in hw.items()) + f"; trailing 60-day share first ≥ 95% on {cw}")
    say(f"- In 2018-H1 (miners' calendar) the first fresh day is {d(first18)}; every later 2018-H1 day is fresh: "
        f"{bool(s18[first18:].all())}; no earlier 2018-H1 day is fresh: {not bool(s18[:first18].iloc[:-1].any())}")
    say()
    w15, wmid = round(100 * hw["2015-H1"]), [h for h in hw.index if "2015-H2" <= h <= "2018-H1"]
    wlate = [h for h in hw.index if h >= "2018-H2"]
    compare("Japan 225 diagnostic, weekday calendar (dev): 2015-H1 (%)", B["n225_fresh_2015H1"], w15, w15 == B["n225_fresh_2015H1"])
    compare("Japan 225 diagnostic, weekday calendar (dev): changeover", B["n225_changeover"], cw, cw == B["n225_changeover"])
    compare("Japan 225 diagnostic, weekday calendar (dev): 2015-H2 → 2018-H1", "about 0% (each ≤ 1%)",
            ", ".join(f"{h} {100 * hw[h]:.1f}%" for h in wmid), all(round(100 * hw[h]) <= 1 for h in wmid))
    compare("Japan 225 diagnostic, weekday calendar (dev): 2018-H2 → 2021-H2", "97–99%",
            ", ".join(f"{h} {100 * hw[h]:.1f}%" for h in wlate), all(97 <= round(100 * hw[h]) <= 99 for h in wlate))


# ---------------------------------------------------- calendar facts (4.6)
def check_calendar_facts(cal: pd.DatetimeIndex, uscal: pd.DatetimeIndex):
    say("## 7. Calendar facts (DATA_PROVENANCE §4.6)")
    say()
    us_days = {d(x) for x in uscal}
    in_us = np.array([d(x) in us_days for x in EARLY_CLOSES])
    none26 = not ((EARLY_CLOSES >= "2026-01-01") & (EARLY_CLOSES <= "2026-03-05")).any()
    say(f"- NYSE early closes (P49): {len(EARLY_CLOSES)} dates; every one is in Book2's US calendar: {bool(in_us.all())}; "
        f"none in 2026-01-01 → 2026-03-05: {none26}")
    conf_cal = confirmation_calendar()
    conf_eq = [d(x) for x in conf_cal] == [d(x) for x in cal[cal >= SPLIT]]
    dev_dates = cal[(cal > cal[0]) & (cal < SPLIT)]
    flagged, rolls = set(), []
    for mth in pd.period_range(cal[0], cal[-1], freq="M"):
        last = mth.days_in_month
        for day in sorted({x for x in (5, 10, 15, 20, 25, 30) if x <= last} | {last}):
            nom = pd.Timestamp(mth.year, mth.month, day)
            if nom < cal[0] or nom > cal[-1]:      # outside the known calendar (forward holdout: P13)
                continue
            hit = cal[cal.searchsorted(nom, side="right") - 1]   # preceding trading day if not one
            flagged.add(d(hit))
            if (hit.year, hit.month) != (nom.year, nom.month):
                rolls.append((d(nom), d(hit)))
    g_dev = pd.Series([d(x) in flagged for x in dev_dates], index=dev_dates)
    g_conf = sum(d(x) in flagged for x in conf_cal)
    by_year = g_dev.groupby(g_dev.index.year).sum()
    say(f"- `calendar.confirmation_calendar()`: {len(conf_cal):,} dates; equal to the miners' calendar from 2022-01-01: {conf_eq}")
    say(f"- Gotobi (P48): dev {int(g_dev.sum())} of {len(dev_dates):,} panel dates "
        f"({'; '.join(f'{y} {n}' for y, n in by_year.items())}); confirmation {g_conf} of {len(conf_cal):,}")
    say(f"- Month-crossing rolls: {len(rolls)}: " + "; ".join(f"{a} → {b}" for a, b in rolls))
    say("- Nominal dates after the calendar's last date (2026-03-05) are not rolled back: the calendar beyond it is unknown.")
    say()
    compare("NYSE early closes in Book2's US calendar", f"{B['early_closes']}, all in the calendar",
            f"{len(EARLY_CLOSES)}, all in: {bool(in_us.all())}", len(EARLY_CLOSES) == B["early_closes"] and bool(in_us.all()))
    compare("Gotobi dev (of 1,708)", B["gotobi_dev"], f"{int(g_dev.sum())} (of {len(dev_dates):,})",
            int(g_dev.sum()) == B["gotobi_dev"] and len(dev_dates) == 1708)
    compare("Gotobi dev by year 2015–2021", " / ".join(map(str, B["gotobi_dev_by_year"])),
            " / ".join(str(int(n)) for n in by_year), [int(n) for n in by_year] == B["gotobi_dev_by_year"])
    compare("Gotobi confirmation (of 1,019)", B["gotobi_conf"], f"{g_conf} (of {len(conf_cal):,})",
            g_conf == B["gotobi_conf"] and len(conf_cal) == 1019)
    compare("Gotobi month-crossing rolls", "; ".join(f"{a} → {b}" for a, b in B["gotobi_rolls"]),
            "; ".join(f"{a} → {b}" for a, b in rolls), rolls == B["gotobi_rolls"])


def main(raw: Path) -> None:
    say("# P2-1: validation of the Pass 2 inputs")
    say()
    say("Generated by `tools/p2_1_inputs.py` (Pass 2, item P2-1). It reproduces DATA_PROVENANCE §4 and compares "
        "the results with PASS2_ADDENDUM Appendix B′ at the precision B′ states. Dev (< 2022-01-01) statistics are "
        "predictor-only, hedge-only or calendar-only. For 2022+ the report holds dates, counts and booleans only. "
        "Nothing relates a predictor to a target.")
    say()
    say("**Pending items, recorded (PASS2_STATUS Decision log):**")
    say("- Settings check (D2 / P39(b)): Book2.xlsx and the 1306 sheet of newbloombergdata_fixed.xlsx were both pulled "
        "with the JT suffix and the PASS2_HANDOFF Appendix E settings, per Isaiah's statement. The 1A cell-for-cell "
        "re-pull was not run. P2-1 proceeds on this statement.")
    say("- TOPIX total-return ticker (D3 / P40): TPXDDVD Index. Records only.")
    say()
    verify(raw)
    cal, uscal = calendars(raw)
    X = pd.read_excel(raw / FIXED, sheet_name=None, header=None)
    O = pd.read_excel(raw / ORIG, sheet_name=None, header=None)
    p = check_1306(X, cal)
    check_dividends(X, p, cal)
    check_topix_tr(X, O, cal)
    check_xau(raw)
    check_n225(raw, cal)
    check_calendar_facts(cal, uscal)
    say("## 8. Comparison with Appendix B′ (and DATA_PROVENANCE §4 where B′ is silent)")
    say()
    say("| Quantity | B′ / DATA_PROVENANCE | P2-1 | Match |")
    say("|---|---|---|---|")
    for q, b, f, ok in cmp_rows:
        say(f"| {q} | {b} | {f} | {ok} |")
    say()
    n_ok = sum(ok for *_, ok in cmp_rows)
    say(f"**{n_ok} of {len(cmp_rows)} comparisons match.**")
    text = "\n".join(out) + "\n"
    (ROOT / "reports" / "P2_1_inputs.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python tools/p2_1_inputs.py <raw_dir>")
    main(Path(sys.argv[1]).expanduser())
