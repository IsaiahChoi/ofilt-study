"""The confirmation module, the economic evaluation (P4-4b2; P4Q37), as docs/P4_CONFIRM_ECON_SPEC.md (version 1) specifies.

`economic_row` computes row O45 from the main forecast call of confirm_forecast.run_calls (M3 and M2): the break-even
of each (the mean gross P&L per name-day, in bp, of the every-day, beta-hedged, open-to-close strategy that trades the
sign of the forecast), their difference, and the mean net P&L under the primary, low and high round trips of D2.3 to
D2.5, with each row's own beta and own prices (D2.8, P4Q24, P4Q25). The round trips re-implement the cost arithmetic of
the P3-1 SESOI tool operation for operation, each case on its own, so that one case's failure leaves the others.
`fill` writes the entry into the document in place of its pending O45. The module reads one file besides the spec
and the configuration, the cost inputs, whose SHA-256 it pins; it writes no file and draws no random number.
"""
from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from typing import Any

import numpy as np
import pandas as pd

from . import blind, targets
from .confirm_forecast import Calls, _check_inputs
from .confirm_inference import ITEM_OF, _plain, load_config
from .spec import REPO_ROOT, Spec

COST_INPUTS_PATH = REPO_ROOT / "docs" / "P3_COST_INPUTS.json"
COST_INPUTS_SHA256 = "a2bbca432e5398a732c9c1bfb7a12106c5474a10b027d4aa1757f5a27c2f8dc6"
CASES = ("primary", "low", "high")
MODELS = ("M3", "M2")
TICKERS = ("5706", "5711", "5713")
SIDES = ("open", "close")
CASE_KEYS = ("notional_jpy", "commission_miners_bp", "commission_1306_bp", "impact_miners_bp", "impact_1306_bp",
             "short_cost_per_day_bp", "half_tick_1306_bp")
REQUIRED_KEYS = ("decided",) + CASE_KEYS + ("price_factor", "tick_tables", "dev_table", "primary_table",
                                            "flag4_windows", "sources")
PX_COLUMNS = ("date", "ticker", "open", "close", "beta")
ROW_ID = "O45"


# ------------------------------------------------------------------ the cost inputs
def check_cost_inputs(obj) -> None:
    """ValueError if a key the P3-1 tool requires is missing, or a case of a case-valued key, or a ticker."""
    missing = [k for k in REQUIRED_KEYS if k not in obj]
    missing += [f"{k}.{c}" for k in CASE_KEYS if k in obj for c in CASES if c not in obj[k]]
    for k in ("price_factor", "dev_table"):
        missing += [f"{k}.{t}" for t in TICKERS if k in obj and t not in obj[k]]
    missing += [f"primary_table.{t}" for t in TICKERS if "primary_table" in obj and t not in obj["primary_table"]]
    if missing:
        raise ValueError(f"the cost inputs lack key(s) {missing}")


def load_cost_inputs(path=None) -> dict:
    """The cost inputs' decoded content; ValueError unless their SHA-256 is COST_INPUTS_SHA256 and no key is missing."""
    p = COST_INPUTS_PATH if path is None else type(COST_INPUTS_PATH)(path)
    data = p.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != COST_INPUTS_SHA256:
        raise ValueError(f"cost inputs {p} have SHA-256 {digest}, not {COST_INPUTS_SHA256}")
    obj = json.loads(data.decode("utf-8"))
    check_cost_inputs(obj)
    return obj


# ------------------------------------------------------------------ the tool's helpers, re-implemented
def _segment(segments: list, date: pd.Timestamp, field: str):
    """Value of the last segment whose start (inclusive; None = -inf) is on or before date."""
    val = None
    for s in segments:
        if s["start"] is None or pd.Timestamp(s["start"]) <= date:
            val = s[field]
    if val is None:
        raise ValueError(f"no segment covers {date.date()}")
    return val


def _factor(inputs: dict, ticker: str, date) -> Fraction:
    return Fraction(_segment(inputs["price_factor"][ticker], pd.Timestamp(date), "f"))


def _dev_table(inputs: dict, ticker: str, date) -> str:
    return _segment(inputs["dev_table"][ticker], pd.Timestamp(date), "table")


def _tick(rows: list, price: float) -> float:
    """Tick of a traded price under a table of [inclusive upper bound, tick] rows; ValueError above the last bound."""
    for bound, t in rows:
        if price <= bound:
            return float(t)
    raise ValueError(f"traded price {price} exceeds the table's last bound {rows[-1][0]}")


def _traded(stored: np.ndarray, f: Fraction) -> np.ndarray:
    """Traded price = stored / f."""
    return np.asarray(stored, dtype=float) * f.denominator / f.numerator


def _half_tick_bp(price: np.ndarray, t: np.ndarray) -> np.ndarray:
    return 1e4 * 0.5 * np.asarray(t, dtype=float) / np.asarray(price, dtype=float)


def _side_ticks(px: pd.DataFrame, inputs: dict, table: str | None) -> dict:
    """Per side: (traded price, tick, above-bound flag) for each row; table None = the row's dev table."""
    tables = inputs["tick_tables"]
    out = {}
    for side in SIDES:
        p = np.empty(len(px))
        tk = np.empty(len(px))
        above = np.zeros(len(px), dtype=bool)
        for i, (d, tkr, s) in enumerate(zip(px["date"], px["ticker"].astype(str), px[side].to_numpy(float))):
            p[i] = _traded(np.array([s]), _factor(inputs, tkr, d))[0]
            rows = tables[_dev_table(inputs, tkr, d) if table is None else table]["rows"]
            try:
                tk[i] = _tick(rows, p[i])
            except ValueError:
                tk[i], above[i] = np.nan, True
        out[side] = (p, tk, above)
    return out


def _side_ticks_table(px: pd.DataFrame, inputs: dict, table_by_ticker: dict, side: str) -> tuple:
    """(traded price, tick) of one side under a per-ticker table name (the primary table); ValueError above a bound."""
    tables = inputs["tick_tables"]
    p = np.empty(len(px))
    tk = np.empty(len(px))
    for i, (d, t, s) in enumerate(zip(px["date"], px["ticker"].astype(str), px[side].to_numpy(float))):
        p[i] = _traded(np.array([s]), _factor(inputs, t, d))[0]
        tk[i] = _tick(tables[table_by_ticker[t]]["rows"], p[i])
    return p, tk


# ------------------------------------------------------------------ §3: the round trips
def _one_case(case: str, px: pd.DataFrame, inputs: dict, tk: np.ndarray, beta: np.ndarray, bbar: float,
              win: np.ndarray) -> dict:
    c_m, c_h = float(inputs["commission_miners_bp"][case]), float(inputs["commission_1306_bp"][case])
    imp_m, imp_h = float(inputs["impact_miners_bp"][case]), float(inputs["impact_1306_bp"][case])
    s = float(inputs["short_cost_per_day_bp"][case])
    ht_h = inputs["half_tick_1306_bp"][case]
    if case == "primary":
        prim = {side: _side_ticks_table(px, inputs, inputs["primary_table"], side) for side in SIDES}
        x_side = {side: np.maximum(imp_m, _half_tick_bp(*prim[side])) for side in SIDES}
        by_ticker = {}
        for t in sorted(set(tk)):
            use = (tk == t) & ~win
            by_ticker[t] = float(np.mean(np.r_[x_side["open"][use], x_side["close"][use]]))
        x_m = np.array([by_ticker[t] for t in tk])
        x_h = max(imp_h, float(ht_h))
    elif case == "low":
        x_m = np.full(len(px), imp_m)
        x_h = imp_h
        by_ticker = {t: imp_m for t in sorted(set(tk))}
    else:
        st = _side_ticks(px, inputs, None)
        if any(st[side][2].any() for side in SIDES):
            raise ValueError("a traded price exceeds its dev table's last bound")
        x_m = imp_m + 0.5 * (_half_tick_bp(st["open"][0], st["open"][1]) + _half_tick_bp(st["close"][0], st["close"][1]))
        x_h = imp_h + float(ht_h)
        by_ticker = {t: float(x_m[tk == t].mean()) for t in sorted(set(tk))}
    rt = 2 * (c_m + x_m) + beta * 2 * (c_h + x_h) + s
    return dict(rt=rt, miner_commission=2 * c_m, miner_execution=float(np.mean(2 * x_m)),
                hedge_leg=bbar * 2 * (c_h + x_h), short=s, mean_rt=float(np.mean(rt)),
                c_m=c_m, c_h=c_h, x_h=x_h, s=s, x_m_by_ticker=by_ticker)


def round_trips(px: pd.DataFrame, inputs: dict) -> dict:
    """Round trips per case on px (date, ticker, open, close, beta), in bp, as the P3-1 tool's `costs` computes them;
    a case that raises ValueError is returned as {"error": ...} and the others are computed."""
    tk = px["ticker"].astype(str).to_numpy()
    beta = px["beta"].to_numpy(float)
    bbar = float(beta.mean())
    win = np.zeros(len(px), dtype=bool)
    for t, w in ((t, w) for t, w in inputs["flag4_windows"].items() if not t.startswith("_")):
        win |= (tk == t) & (px["date"] < pd.Timestamp(w["before"])).to_numpy()
    out: dict = {}
    for case in CASES:
        try:
            out[case] = _one_case(case, px, inputs, tk, beta, bbar, win)
        except ValueError as e:
            out[case] = {"error": f"{type(e).__name__}: {e}"}
    out["beta_bar"] = bbar
    return out


def pnl_bp(y, yhat, rt):
    """Per row: the position is the forecast's sign; gross = 1e4 * sign * y; net = gross - rt * |sign|."""
    s = np.sign(np.asarray(yhat, dtype=float))
    gross = 1e4 * s * np.asarray(y, dtype=float)
    net = gross - np.asarray(rt, dtype=float) * np.abs(s)
    return gross, net


# ------------------------------------------------------------------ §4: the row
class _NotEstimable(Exception):
    def __init__(self, reason: str, n_rows: int | None = None, n_dates: int | None = None):
        super().__init__(reason)
        self.reason, self.n_rows, self.n_dates = reason, n_rows, n_dates


def _frame_T(dev, events, confirm, spec: Spec) -> pd.DataFrame:
    """The frame T exactly as confirm_forecast's run_calls builds it."""
    if confirm is not None:
        J = pd.concat([dev, confirm], ignore_index=True)
        J.attrs = {"provenance": blind.provenance_of(confirm)}
    else:
        J = dev.copy()
    return targets.add_masks(targets.add_targets(J, spec), events, spec)


def _keys(frame: pd.DataFrame) -> pd.MultiIndex:
    return pd.MultiIndex.from_arrays([frame["date"].to_numpy(), frame["ticker"].astype(str).to_numpy()])


def _model_rows(ev: pd.DataFrame, model: str) -> pd.DataFrame:
    rows = ev.loc[ev["model"] == model]
    return rows.sort_values(["date", "ticker"], kind="mergesort").reset_index(drop=True)


def economic_px(calls: Calls, dev, events, confirm=None, *, spec=None):
    """§4.1: (R, R2, px), the main call's evaluated M3 and M2 rows and their prices and betas in T. A failed main call
    or no M3 row raises _NotEstimable (economic_row turns it into the entry); frames that do not match the calls raise
    ValueError."""
    _check_inputs(dev, confirm)
    spec = spec or Spec.load()
    T = _frame_T(dev, events, confirm, spec)
    if calls.mode != ("confirmation" if confirm is not None else "dev"):
        raise ValueError(f"the calls were made in the {calls.mode} mode")
    if calls.main.status != "ok":
        raise _NotEstimable(calls.main.reason)
    R, R2 = _model_rows(calls.main.ev, "M3"), _model_rows(calls.main.ev, "M2")
    if R.empty:
        raise _NotEstimable("no rows", 0, 0)
    if not (len(R) == len(R2) and _keys(R).equals(_keys(R2))):
        raise ValueError("M3's and M2's evaluated rows differ: not one call's sample")
    tkeys = _keys(T)
    if not tkeys.is_unique:
        raise ValueError("duplicate (date, ticker) keys in the frame")
    pos = tkeys.get_indexer(_keys(R))
    if (pos < 0).any():
        raise ValueError(f"{int((pos < 0).sum())} evaluated row(s) have no row in the frame")
    if not np.array_equal(R["y"].to_numpy(dtype=float), T["abn_oc"].to_numpy(dtype=float)[pos]):
        raise ValueError("the evaluated rows' y differs from the frame's abn_oc: the frames do not match the calls")
    px = T.iloc[pos][list(PX_COLUMNS)].reset_index(drop=True)
    return R, R2, px


def _all_finite(x: Any) -> bool:
    if isinstance(x, float):
        return math.isfinite(x)
    if isinstance(x, dict):
        return all(_all_finite(v) for v in x.values())
    if isinstance(x, list):
        return all(_all_finite(v) for v in x)
    return True


def _entry(status: str, values, reason, n_rows, n_dates) -> dict:
    return {"id": ROW_ID, "item": ITEM_OF[ROW_ID], "status": status, "values": values, "reason": reason,
            "n_rows": _plain(n_rows), "n_dates": _plain(n_dates), "lag": None}


def economic_row(calls: Calls, dev, events, confirm=None, *, spec=None, inputs=None) -> dict:
    """The O45 entry (§4) from run_calls on the same three frames."""
    try:
        R, R2, px = economic_px(calls, dev, events, confirm, spec=spec)
    except _NotEstimable as e:
        return _entry("not_estimable", None, e.reason, e.n_rows, e.n_dates)
    inputs = load_cost_inputs() if inputs is None else inputs
    cfg = load_config()
    E0 = None if confirm is None else pd.Timestamp(confirm["date"].min())
    rts = round_trips(px, inputs)
    rows = {"M3": R, "M2": R2}
    gross = {m: pnl_bp(r["y"], r["yhat"], np.zeros(len(r)))[0] for m, r in rows.items()}
    be = {m: float(np.mean(gross[m])) for m in MODELS}
    failed = {c: rts[c]["error"] for c in CASES if "error" in rts[c]}
    ok = [c for c in CASES if c not in failed]
    values = {
        "models": list(MODELS), "call": "main", "mode": calls.mode, "from": E0,
        "aggregation": cfg["economic_evaluation"]["aggregation"], "decisions": ["P4Q24", "P4Q25"],
        "break_even_bp": {"M3": be["M3"], "M2": be["M2"], "difference": be["M3"] - be["M2"]},
        "traded_share": {m: float(np.mean(np.sign(r["yhat"].to_numpy(dtype=float)) != 0)) for m, r in rows.items()},
        "round_trip_bp": {c: ({k: v for k, v in rts[c].items() if k not in ("rt", "x_m_by_ticker")} if c in ok
                              else None) for c in CASES},
        "x_m_by_ticker": {c: (rts[c]["x_m_by_ticker"] if c in ok else None) for c in CASES},
        "beta_bar": rts["beta_bar"],
        "net_bp": {m: {c: (float(np.mean(pnl_bp(r["y"], r["yhat"], rts[c]["rt"])[1])) if c in ok else None)
                       for c in CASES} for m, r in rows.items()},
        "cases_failed": failed,
        "sesoi_locked": cfg["constants"]["sesoi"],
    }
    values = _plain(values)
    n_rows, n_dates = len(R), int(R["date"].nunique())
    if not _all_finite(values):
        return _entry("not_estimable", None, "non-finite estimate", n_rows, n_dates)
    return _entry("estimated", values, None, n_rows, n_dates)


def fill(doc: dict, entry: dict) -> dict:
    """A copy of the document (made with _plain) with its pending O45 replaced by the entry."""
    old = doc["rows"][ROW_ID]
    if old.get("status") != "pending" or old.get("item") != "P4-4b":
        raise ValueError("the document's O45 is not a pending P4-4b entry")
    if entry.get("id") != ROW_ID or entry.get("item") != "P4-4b":
        raise ValueError("the entry is not O45 of P4-4b")
    out = _plain(doc)
    out["rows"][ROW_ID] = _plain(entry)
    return out
