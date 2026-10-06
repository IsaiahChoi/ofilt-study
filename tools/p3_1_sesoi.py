"""P3-1: the SESOI's ingredients under DQ2 (D2.1-D2.5) and the primary, low and high SESOI. DEV ONLY.

Definitions (PASS3_STATUS Decision log, DQ2; inputs in docs/P3_COST_INPUTS.json):
  D2.1  e~ = OLS residual of usdjpy_ret on the primary design's other regressors (ticker fixed effects, eurusd_ret,
        ticker-specific spy_oc and copx_oc), fitted once on the AM-03 estimation sample (the P3-0b Part A rule).
        Denominator: mean |e~| over those rows. A predictor-only regression; targets select rows only by availability.
  D2.2  beta-bar = mean of the expanding past-only beta over the same rows (target-only).
  D2.3  RT = 2 (c_m + x_m) + beta 2 (c_h + x_h) + s per name-day; SESOI = mean RT / mean |e~| (a ratio of means).
  D2.4  Miner tick term on TRADED prices (stored / f): primary x_m = max(impact, 1/2 tick) under the fine table,
        averaged per ticker over its kept rows outside the Flag 4 windows and over the open and close sides; low
        x_m = impact; high x_m = impact + 1/2 tick per side under the dev tables, every kept row.
  D2.5  1306: primary x_h = max(impact, 1/2 tick); low x_h = impact; high x_h = impact + 1/2 tick.

Data use. Predictor values (usdjpy_ret, eurusd_ret, spy_oc, copx_oc) enter only the D2.1 regression, whose only
output is mean |e~|. Target-side values enter only as: beta (beta-bar and each row's hedge leg, which averages to
beta-bar), open and close (the ticks and the conformity gate); every other target column only through availability
(the Part A rule). No computed quantity depends jointly on predictor and target values. No inference function,
design builder, forecasting engine or simulator is called. Gates (each a STOP with the failing counts): the Part A
counts equal reports/P3_0b_preflight.md; the partialling set; price conformity with the dev tick tables.

usage: python tools/p3_1_sesoi.py     # DATA/panel_dev.csv + docs/P3_COST_INPUTS.json -> reports/P3_1_sesoi.md
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from p3_0b_preflight import sample_keep, verify_panel  # noqa: E402  (the P3-0b Part A rule and hash check)
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

INPUTS_PATH = ROOT / "docs" / "P3_COST_INPUTS.json"
PREFLIGHT_REPORT = ROOT / "reports" / "P3_0b_preflight.md"
CASE_KEYS = ("notional_jpy", "commission_miners_bp", "commission_1306_bp", "impact_miners_bp", "impact_1306_bp",
             "short_cost_per_day_bp", "half_tick_1306_bp")
REQUIRED_KEYS = ("decided",) + CASE_KEYS + ("price_factor", "tick_tables", "dev_table", "primary_table",
                                            "flag4_windows", "sources")
CASES = ("primary", "low", "high")
CONFORM_TOL = 1e-6
SIDES = ("open", "close")


# ------------------------------------------------------------------ inputs
def load_inputs(path: Path = INPUTS_PATH) -> dict:
    """The cost file; SystemExit if any required key (or a case of a case-valued key) is missing."""
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED_KEYS if k not in obj]
    missing += [f"{k}.{c}" for k in CASE_KEYS if k in obj for c in CASES if c not in obj[k]]
    for k in ("price_factor", "dev_table"):
        missing += [f"{k}.{t}" for t in IO.TICKERS if k in obj and t not in obj[k]]
    missing += [f"primary_table.{t}" for t in IO.TICKERS if "primary_table" in obj and t not in obj["primary_table"]]
    if missing:
        raise SystemExit(f"REFUSED: {path} lacks key(s) {missing}")
    return obj


def _segment(segments: list, date: pd.Timestamp, field: str):
    """Value of the last segment whose start (inclusive; None = -inf) is on or before date."""
    val = None
    for s in segments:
        if s["start"] is None or pd.Timestamp(s["start"]) <= date:
            val = s[field]
    if val is None:
        raise ValueError(f"no segment covers {date.date()}")
    return val


def factor(inputs: dict, ticker: str, date) -> Fraction:
    return Fraction(_segment(inputs["price_factor"][ticker], pd.Timestamp(date), "f"))


def dev_table(inputs: dict, ticker: str, date) -> str:
    return _segment(inputs["dev_table"][ticker], pd.Timestamp(date), "table")


def tick(rows: list, price: float) -> float:
    """Tick of a traded price under a table of [inclusive upper bound, tick] rows; ValueError above the last bound."""
    for bound, t in rows:
        if price <= bound:
            return float(t)
    raise ValueError(f"traded price {price} exceeds the table's last bound {rows[-1][0]}")


def traded(stored: np.ndarray, f: Fraction) -> np.ndarray:
    """Traded price = stored / f."""
    return np.asarray(stored, dtype=float) * f.denominator / f.numerator


def conforms(price: np.ndarray, t: np.ndarray) -> np.ndarray:
    q = np.asarray(price, dtype=float) / np.asarray(t, dtype=float)
    return np.abs(q - np.round(q)) < CONFORM_TOL


def half_tick_bp(price: np.ndarray, t: np.ndarray) -> np.ndarray:
    return 1e4 * 0.5 * np.asarray(t, dtype=float) / np.asarray(price, dtype=float)


def side_ticks(px: pd.DataFrame, inputs: dict, table: str | None) -> dict:
    """Per side: (traded price, tick, above-bound flag) for each row; table None = the row's dev table."""
    tables = inputs["tick_tables"]
    out = {}
    for side in SIDES:
        p = np.empty(len(px)); tk = np.empty(len(px)); above = np.zeros(len(px), dtype=bool)
        for i, (d, tkr, s) in enumerate(zip(px["date"], px["ticker"].astype(str), px[side].to_numpy(float))):
            p[i] = traded(np.array([s]), factor(inputs, tkr, d))[0]
            rows = tables[dev_table(inputs, tkr, d) if table is None else table]["rows"]
            try:
                tk[i] = tick(rows, p[i])
            except ValueError:
                tk[i], above[i] = np.nan, True
        out[side] = (p, tk, above)
    return out


# ------------------------------------------------------------------ D2.1 and step 2
def design_names(spec: Spec, tickers) -> list[str]:
    """The primary design's column names as inference._design_core builds them (inference.py:90, 106-113)."""
    utick = sorted(str(t) for t in tickers)
    names = [f"fe[{t}]" for t in utick] + list(spec.fx_block)
    names += [f"{c}:{t}" for c in spec.controls for t in utick]
    return names


def partial_e(df: pd.DataFrame, spec: Spec, keep: pd.Series) -> tuple[pd.Series, list[str]]:
    """D2.1: residual of the H1 column on the design's other columns, OLS (lstsq) on the kept rows.
    Reads only the predictor columns (and ticker); returns e~ indexed like df.loc[keep] and the regressor names."""
    d = df.loc[keep]
    tk = d["ticker"].astype(str).to_numpy()
    utick = sorted(np.unique(tk))
    h1 = spec.h1_parameter
    names = [n for n in design_names(spec, utick) if n != h1]
    cols = []
    for n in names:
        if n.startswith("fe["):
            cols.append((tk == n[3:-1]).astype(float))
        elif ":" in n:
            c, t = n.split(":")
            cols.append(d[c].to_numpy(float) * (tk == t))
        else:
            cols.append(d[n].to_numpy(float))
    X = np.column_stack(cols)
    y = d[h1].to_numpy(float)
    coef = np.linalg.lstsq(X, y, rcond=None)[0]
    return pd.Series(y - X @ coef, index=d.index, name="e_tilde"), names


# ------------------------------------------------------------------ D2.3-D2.5
def costs(px: pd.DataFrame, inputs: dict) -> dict:
    """Round trips per case on the kept rows px (date, ticker, open, close, beta), each in bp, and the D2.4 detail."""
    tk = px["ticker"].astype(str).to_numpy()
    beta = px["beta"].to_numpy(float)
    bbar = float(beta.mean())
    win = np.zeros(len(px), dtype=bool)
    for t, w in ((t, w) for t, w in inputs["flag4_windows"].items() if not t.startswith("_")):
        win |= (tk == t) & (px["date"] < pd.Timestamp(w["before"])).to_numpy()
    out, detail = {}, {}
    for case in CASES:
        c_m, c_h = float(inputs["commission_miners_bp"][case]), float(inputs["commission_1306_bp"][case])
        imp_m, imp_h = float(inputs["impact_miners_bp"][case]), float(inputs["impact_1306_bp"][case])
        s = float(inputs["short_cost_per_day_bp"][case])
        ht_h = inputs["half_tick_1306_bp"][case]
        if case == "primary":
            prim ={side: side_ticks_table(px, inputs, inputs["primary_table"], side) for side in SIDES}
            x_side = {side: np.maximum(imp_m, half_tick_bp(*prim[side])) for side in SIDES}
            xm_t, rows_t, share_t = {}, {}, {}
            for t in sorted(set(tk)):
                use = (tk == t) & ~win
                xm_t[t] = float(np.mean(np.r_[x_side["open"][use], x_side["close"][use]]))
                rows_t[t] = int(use.sum())
                share_t[t] = float(np.mean(np.r_[half_tick_bp(*prim["open"])[use] > imp_m,
                                                 half_tick_bp(*prim["close"])[use] > imp_m]))
            x_m = np.array([xm_t[t] for t in tk])
            x_h = max(imp_h, float(ht_h))
            detail.update(primary_rows=rows_t, primary_xm=xm_t, primary_share=share_t)
        elif case == "low":
            x_m = np.full(len(px), imp_m)
            x_h = imp_h
        else:
            st = side_ticks(px, inputs, None)
            if any(st[side][2].any() for side in SIDES):
                raise ValueError("a traded price exceeds its dev table's last bound")
            x_m = imp_m + 0.5 * (half_tick_bp(st["open"][0], st["open"][1]) + half_tick_bp(st["close"][0], st["close"][1]))
            x_h = imp_h + float(ht_h)
            detail["high_xm"] = {t: float(x_m[tk == t].mean()) for t in sorted(set(tk))}
        rt = 2 * (c_m + x_m) + beta * 2 * (c_h + x_h) + s
        out[case] = dict(miner_commission=2 * c_m, miner_execution=float(np.mean(2 * x_m)),
                         hedge_leg=bbar * 2 * (c_h + x_h), short=s, mean_rt=float(np.mean(rt)),
                         c_m=c_m, c_h=c_h, x_h=x_h, s=s)
    out["beta_bar"] = bbar
    out["detail"] = detail
    return out


def side_ticks_table(px: pd.DataFrame, inputs: dict, table_by_ticker: dict, side: str) -> tuple:
    """(traded price, tick) of one side under a per-ticker table name (the primary table); ValueError above a bound."""
    tables = inputs["tick_tables"]
    p = np.empty(len(px)); tk = np.empty(len(px))
    for i, (d, t, s) in enumerate(zip(px["date"], px["ticker"].astype(str), px[side].to_numpy(float))):
        p[i] = traded(np.array([s]), factor(inputs, t, d))[0]
        tk[i] = tick(tables[table_by_ticker[t]]["rows"], p[i])
    return p, tk


def sig4(x: float) -> str:
    return f"{x:.4g}"


def period_label(inputs: dict, ticker: str, date) -> str:
    segs = inputs["price_factor"][ticker]
    starts = [s["start"] for s in segs if s["start"] is not None]
    d = pd.Timestamp(date)
    for st in starts:
        if d < pd.Timestamp(st):
            return f"before {st}"
    return f"from {starts[-1]}" if starts else "all"


# ------------------------------------------------------------------ report
def run(df: pd.DataFrame, spec: Spec, inputs: dict, digest: str, inputs_text: str) -> str:
    L = []
    say = L.append
    say("# P3-1: the SESOI (DQ2; dev only)")
    say("")
    # (a) hash, step 1, step 2
    say("## (a) Hash check, sample and regressors")
    say("")
    say(f"- Dev panel SHA-256 `{digest}`: equal to the spec's dev-panel hash (AM-04) and to `docs/PASS2_INPUTS.json`, "
        "checked before the file was read.")
    keep = sample_keep(df, spec)
    n_rows, n_dates = int(keep.sum()), int(df.loc[keep, "date"].nunique())
    pre = PREFLIGHT_REPORT.read_text(encoding="utf-8")
    exp_rows = int(re.search(r"^- Kept rows: \*\*(\d+)\*\*$", pre, re.M).group(1))
    exp_dates = int(re.search(r"^- Kept unique dates \(T_source\): \*\*(\d+)\*\*$", pre, re.M).group(1))
    ok1 = (n_rows, n_dates) == (exp_rows, exp_dates)
    say(f"- Step 1 (the P3-0b Part A rule, imported from `tools/p3_0b_preflight.py`): kept rows {n_rows}, "
        f"T_source {n_dates}; `reports/P3_0b_preflight.md` says {exp_rows} and {exp_dates}. Gate: {ok1}.")
    if not ok1:
        raise SystemExit(f"STOP (gate 1): kept rows {n_rows} vs {exp_rows}; T_source {n_dates} vs {exp_dates}")
    tick_ids = sorted(df.loc[keep, "ticker"].astype(str).unique())
    names = design_names(spec, tick_ids)
    partial = [n for n in names if n != spec.h1_parameter]
    expected = {f"fe[{t}]" for t in IO.TICKERS} | {"eurusd_ret"} | {f"{c}:{t}" for c in ("spy_oc", "copx_oc")
                                                                   for t in IO.TICKERS}
    ok2 = set(partial) == expected and len(partial) == len(expected)
    say(f"- Step 2: the primary design's regressors, from `spec.fx_block`, `spec.controls` and `spec.h1_parameter` "
        f"as `ofilt/drift/inference.py:90` reads them, named as at `inference.py:106-113`: {names}. "
        f"The partialling set (the design minus `{spec.h1_parameter}`): {partial}. "
        f"Equals {{ticker fixed effects, eurusd_ret, ticker-specific spy_oc and copx_oc}}: {ok2}.")
    if not ok2:
        raise SystemExit(f"STOP (gate 2): partialling set {partial}")
    say("")

    # (b) conformity
    px_all = df[["date", "ticker", "open", "close"]].copy()
    px_all["ticker"] = px_all["ticker"].astype(str)
    st = side_ticks(px_all, inputs, None)
    say("## (b) Conformity of all dev opens and closes with the dev tick tables (traded price = stored / f)")
    say("")
    say(f"A price conforms if it is an integer multiple of its dev-table tick at its traded price "
        f"(|p/t - round(p/t)| < {CONFORM_TOL:g}); 'Above bound' counts traded prices above the table's last bound.")
    say("")
    say("| Ticker | Year | Period | Prices | Conforming share | Above bound |")
    say("|---|---|---|---|---|---|")
    per = np.array([period_label(inputs, t, d) for t, d in zip(px_all["ticker"], px_all["date"])])
    yrs = px_all["date"].dt.year.to_numpy()
    tks = px_all["ticker"].to_numpy()
    conf = {side: np.where(st[side][2], False, conforms(st[side][0], np.where(st[side][2], 1.0, st[side][1])))
            for side in SIDES}
    fails = []
    for t in IO.TICKERS:
        for y in sorted(set(yrs[tks == t])):
            for p in sorted(set(per[(tks == t) & (yrs == y)]), key=lambda s: not s.startswith("before")):
                m = (tks == t) & (yrs == y) & (per == p)
                c = np.r_[conf["open"][m], conf["close"][m]]
                ab = int(st["open"][2][m].sum() + st["close"][2][m].sum())
                share = float(c.mean())
                txt = "1" if share == 1.0 else f"{math.floor(share * 1e6) / 1e6:.6f}"
                say(f"| {t} | {y} | {p} | {c.size} | {txt} | {ab} |")
                if share != 1.0 or ab:
                    fails.append(f"{t} {y} {p}: {int(c.size - c.sum())} of {c.size} non-conforming, {ab} above bound")
    ok3 = not fails
    say("")
    say(f"Gate (every share exactly 1, no price above a bound): {ok3}.")
    say("")
    if not ok3:
        print("\n".join(L))
        raise SystemExit("STOP (gate 3, conformity): " + "; ".join(fails))

    # (c) e~ and beta-bar
    e, _ = partial_e(df, spec, keep)
    mean_abs_e = float(np.mean(np.abs(e.to_numpy()))) * 1e4
    kept = df.loc[keep, ["date", "ticker", "open", "close", "beta"]].copy()
    kept["ticker"] = kept["ticker"].astype(str)
    cc = costs(kept, inputs)
    say("## (c) The denominator and the hedge ratio")
    say("")
    say(f"- mean |e~| over the {n_rows} step 1 rows: **{mean_abs_e:.4f} bp** (D2.1; `numpy.linalg.lstsq`, "
        f"{len(partial)} regressors, no global intercept)")
    say(f"- beta-bar over the same rows: **{cc['beta_bar']:.4f}** (D2.2)")
    say("- Rows per ticker: " + ", ".join(f"{t} {int((kept['ticker'] == t).sum())}" for t in IO.TICKERS))
    say("")

    # (d) per ticker
    dt = cc["detail"]
    say("## (d) The miner execution cost per ticker (bp per side)")
    say("")
    say("| Ticker | Rows for the primary x_m (outside Flag 4 windows) | Primary x_m | Share of sides with 1/2 tick > "
        "stated impact (primary table) | High: mean x_m over all kept rows |")
    say("|---|---|---|---|---|")
    for t in IO.TICKERS:
        say(f"| {t} | {dt['primary_rows'][t]} | {dt['primary_xm'][t]:.4f} | {dt['primary_share'][t]:.4f} | "
            f"{dt['high_xm'][t]:.4f} |")
    say("")

    # (e) cases
    say("## (e) Round trips and the SESOI")
    say("")
    say("RT = 2 (c_m + x_m) + beta 2 (c_h + x_h) + s per name-day; components are means over the step 1 rows (bp). "
        "SESOI = mean RT / mean |e~|.")
    say("")
    say("| Case | Miner commission 2 c_m | Miner execution mean 2 x_m | Hedge leg beta-bar 2 (c_h + x_h) | Short s "
        "| Mean RT | SESOI |")
    say("|---|---|---|---|---|---|---|")
    for case in CASES:
        r = cc[case]
        say(f"| {case} | {r['miner_commission']:.4f} | {r['miner_execution']:.4f} | {r['hedge_leg']:.4f} | "
            f"{r['short']:.4f} | {r['mean_rt']:.4f} | **{sig4(r['mean_rt'] / mean_abs_e)}** |")
    say("")

    # (f) inputs
    say("## (f) `docs/P3_COST_INPUTS.json`")
    say("")
    say("```json")
    say(inputs_text.rstrip("\n"))
    say("```")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", type=Path, default=IO.DATA_DIR / IO.DEV_FILE)
    ap.add_argument("--inputs", type=Path, default=INPUTS_PATH)
    ap.add_argument("--out", type=Path, default=ROOT / "reports" / "P3_1_sesoi.md")
    a = ap.parse_args(argv)
    inputs = load_inputs(a.inputs)                         # refuses a cost file with a missing key
    spec = Spec.load()
    digest = verify_panel(a.panel, spec)                   # before the panel is read
    df = TG.add_targets(IO.load_dev(a.panel, spec), spec)
    md = run(df, spec, inputs, digest, Path(a.inputs).read_text(encoding="utf-8"))
    a.out.write_text(md, encoding="utf-8")
    print(md, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
