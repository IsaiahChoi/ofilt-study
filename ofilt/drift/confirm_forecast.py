"""The confirmation module, forecasting rows (P4-4b1; P4Q36), as docs/P4_CONFIRM_FC_SPEC.md (version 1) specifies.

`run_calls` makes the two forecast.walk_forward calls of section 3 (M0 to M5; M7 with M1 and M0, with M7's
permutation importance) on the joined dev and confirmation frame, or on the dev frame alone, and keeps each call's
predictions restricted to the evaluation dates. `forecast_rows` turns the calls into the entries of O29 to O44 and R9
(O45 is P4-4b2's), and `fill` writes those entries into P4-4a's document in place of its pending ones. Each
walk_forward call appends one line to the run registry, as the engine does by design (P27). The module opens no file
and draws no random number itself; the configuration is read through confirm_inference.load_config.
"""
from __future__ import annotations

import dataclasses
import math
from typing import Any, Callable

import numpy as np
import pandas as pd

from . import blind, fctests, forecast, models, targets
from .confirm_inference import ITEM_OF, _plain, load_config
from .spec import Spec

ROWS = ("O29", "O30", "O31", "O32", "O33", "O34", "O35", "R9",
        "O36", "O37", "O38", "O39", "O40", "O41", "O42", "O43", "O44")
MAIN_CALL = ("M0", "M1", "M2", "M3", "M4", "M5")
M7_CALL = ("M7", "M1", "M0")
IMPORTANCE = ("M7",)
MODEL_ROWS = {"O29": "M0", "O30": "M1", "O31": "M2", "O32": "M3", "O33": "M4", "O34": "M5", "O35": "M7"}
CW_ROWS = {"O36": ("main", "M3", "M2"), "O37": ("main", "M4", "M3"), "O38": ("main", "M5", "M3"),
           "O39": ("m7", "M7", "M1")}
PROTOCOL = ("scheme", "min_train_dates", "refit_every_dates", "pooled_across_tickers", "scaling")
TABLE_COLUMNS = ("feature", "rank", "mean_dmse", "sd_dmse", "min_dmse", "max_dmse", "is_noise", "exceeds_noise")


def cw_reject_calibrated(stat, c) -> bool:
    """The primary comparison's decision (AM-09): reject if and only if the statistic is strictly above c."""
    return bool(stat > c)


# ------------------------------------------------------------------ the two calls (section 3)
@dataclasses.dataclass
class CallResult:
    name: str
    models: tuple
    status: str
    reason: str | None = None
    preds: Any = None
    folds: Any = None
    ev: Any = None
    folds_ev: Any = None
    run_id: str | None = None


@dataclasses.dataclass
class Calls:
    mode: str
    E0: Any
    cfg: dict
    spec: Spec
    main: CallResult
    m7: CallResult
    bars_le_0_rows: int
    bars_le_0_dates: int


def _check_inputs(dev, confirm) -> None:
    """The provenance pair, then the blinding guard on dev and confirm (docs/P4_CONFIRM_INF_SPEC.md, section 3.2)."""
    p_dev = blind.provenance_of(dev)
    if confirm is None:
        if p_dev not in (blind.SYNTHETIC, blind.DEV_REAL):
            raise ValueError(f"dev mode needs a synthetic or dev_real frame, got provenance {p_dev!r}")
    else:
        p_conf = blind.provenance_of(confirm)
        if (p_dev, p_conf) not in ((blind.SYNTHETIC, blind.SYNTHETIC), (blind.DEV_REAL, blind.CONFIRM_REAL)):
            raise ValueError(f"refused provenance pair ({p_dev!r}, {p_conf!r})")
    blind.require_unblinded(dev)
    if confirm is not None:
        blind.require_unblinded(confirm)


def _call(name: str, names: tuple, run: Callable, E0) -> CallResult:
    """One walk_forward call (section 3.4's failures) and its evaluation rows (section 3.5)."""
    try:
        preds, folds = run()
    except (ValueError, ArithmeticError) as e:
        return CallResult(name, names, "failed", f"walk_forward ({name}): {type(e).__name__}: {e}")
    ev = (preds if E0 is None else preds.loc[preds["date"] >= E0]).reset_index(drop=True)
    ev.attrs = dict(preds.attrs)
    counts = ev.groupby(["model", "fold"]).size()
    folds_ev = folds.copy()
    folds_ev["n_test"] = [int(counts.get((m, f), 0)) for m, f in zip(folds["model"], folds["fold"])]
    folds_ev.attrs = dict(folds.attrs)
    return CallResult(name, names, "ok", None, preds, folds, ev, folds_ev, folds.attrs.get("run_id"))


def run_calls(dev, events, confirm=None, *, spec=None, factories=None) -> Calls:
    """The two calls of section 3 on the joined frame (confirmation mode) or the dev frame (dev mode)."""
    _check_inputs(dev, confirm)
    spec = spec or Spec.load()
    cfg = load_config()
    unknown = sorted(set(factories or {}) - set(MAIN_CALL) - set(M7_CALL))
    if unknown:
        raise ValueError(f"factories for models outside the two calls: {unknown}")

    def factory(name):
        return factories[name] if factories is not None and name in factories else models.REGISTRY[name]

    if confirm is not None:
        mode, E0 = "confirmation", pd.Timestamp(confirm["date"].min())
        J = pd.concat([dev, confirm], ignore_index=True)
        J.attrs = {"provenance": blind.provenance_of(confirm)}
    else:
        mode, E0 = "dev", None
        J = dev.copy()
    T = targets.add_masks(targets.add_targets(J, spec), events, spec)
    bars = T["usdjpy_bars"].to_numpy(dtype=float)
    le0 = np.isfinite(bars) & (bars <= 0)
    F_main = T.copy()
    if le0.any():           # rv_per_bar undefined: the engine then drops these rows for every model of the call
        F_main["usdjpy_bars"] = np.where(le0, np.nan, bars)
    main = _call("main", MAIN_CALL, lambda: forecast.walk_forward(F_main, {m: factory(m) for m in MAIN_CALL}, spec), E0)
    m7 = _call("m7", M7_CALL, lambda: forecast.walk_forward(T, {m: factory(m) for m in M7_CALL}, spec,
                                                            importance=list(IMPORTANCE)), E0)
    return Calls(mode, E0, cfg, spec, main, m7, int(le0.sum()), int(T.loc[le0, "date"].nunique()))


# ------------------------------------------------------------------ entries and contingencies (section 4)
class _NotEstimable(Exception):
    def __init__(self, reason: str, n_rows: int | None = None, n_dates: int | None = None):
        super().__init__(reason)
        self.reason, self.n_rows, self.n_dates = reason, n_rows, n_dates


@dataclasses.dataclass
class _Out:
    status: str
    values: Any = None
    reason: str | None = None
    n_rows: int | None = None
    n_dates: int | None = None
    lag: int | None = None


def _all_finite(x: Any) -> bool:
    if isinstance(x, float):
        return math.isfinite(x)
    if isinstance(x, dict):
        return all(_all_finite(v) for v in x.values())
    if isinstance(x, list):
        return all(_all_finite(v) for v in x)
    return True


def _row(rid: str, compute: Callable[[], _Out]) -> dict:
    """The one helper of section 4.2: computes a row's entry and applies the contingencies."""
    try:
        out = compute()
    except _NotEstimable as e:
        out = _Out("not_estimable", None, e.reason, e.n_rows, e.n_dates)
    values = _plain(out.values)
    if not _all_finite(values):
        out = _Out("not_estimable", None, "non-finite estimate", out.n_rows, out.n_dates, out.lag)
        values = None
    return {"id": rid, "item": ITEM_OF[rid], "status": out.status, "values": values, "reason": out.reason,
            "n_rows": _plain(out.n_rows), "n_dates": _plain(out.n_dates), "lag": _plain(out.lag)}


def _lib(fn: Callable, *args):
    """A library call of fctests or forecast.importance_table; ValueError (PairingError too) and ArithmeticError
    make the row not estimable."""
    try:
        return fn(*args)
    except (ValueError, ArithmeticError) as e:
        raise _NotEstimable(f"{type(e).__name__}: {e}") from e


def _need(calls: Calls, name: str) -> CallResult:
    c = getattr(calls, name)
    if c.status != "ok":
        raise _NotEstimable(c.reason)
    return c


def _pt(r: dict) -> dict:
    """A Pesaran-Timmermann result, plain, with stat and p None wherever defined is False."""
    r = _plain(r)
    for part in list(r["per_ticker"].values()) + [r["portfolio"]]:
        if part["defined"] is False:
            part["stat"], part["p"] = None, None
    return r


# ------------------------------------------------------------------ the rows (section 5)
def _model_row(calls: Calls, rid: str) -> _Out:
    model = MODEL_ROWS[rid]
    name = "m7" if model in M7_CALL and model not in MAIN_CALL else "main"
    c = _need(calls, name)
    rows = c.ev.loc[c.ev["model"] == model]
    if rows.empty:
        raise _NotEstimable("no rows", 0, 0)
    fl = c.folds_ev.loc[c.folds_ev["model"] == model]
    return _Out("estimated", {"model": model, "call": name, "spec": calls.spec.value(f"forecast.models.{model}"),
                              "n_folds": int((fl["n_test"] > 0).sum()), "first_eval_date": rows["date"].min(),
                              "last_eval_date": rows["date"].max()},
                n_rows=len(rows), n_dates=int(rows["date"].nunique()))


def _call_part(c: CallResult) -> dict:
    part = {"models": list(c.models), "status": c.status, "reason": c.reason}
    if c.status == "ok":
        first = c.models[0]
        fl = c.folds.loc[c.folds["model"] == first]
        er = c.ev.loc[c.ev["model"] == first]
        part.update(n_folds=len(fl), first_test_date=fl["test_start"].min(), last_test_date=fl["test_end"].max(),
                    eval_rows=len(er), eval_dates=int(er["date"].nunique()))
    else:
        part.update(n_folds=0, first_test_date=None, last_test_date=None, eval_rows=None, eval_dates=None)
    return part


def _r9(calls: Calls) -> _Out:
    values = {k: calls.spec.value(f"forecast.{k}") for k in PROTOCOL}
    part = "confirmation" if calls.mode == "confirmation" else "dev"
    values["evaluation"] = {"mode": calls.mode, "from": calls.E0,
                            "decision": calls.cfg["forecast"][part]["decision"]}
    main, m7 = _call_part(calls.main), _call_part(calls.m7)
    main.update(bars_le_0_rows=calls.bars_le_0_rows, bars_le_0_dates=calls.bars_le_0_dates)
    m7["importance"] = list(IMPORTANCE)
    values["calls"] = {"main": main, "m7": m7}
    return _Out("fixed", values)


def _clark_west(calls: Calls, rid: str) -> _Out:
    name, u, r_ = CW_ROWS[rid]
    r = _lib(fctests.clark_west, _need(calls, name).ev, u, r_, calls.spec)
    values = _plain(r)
    if rid == "O36":
        c = calls.cfg["constants"]["c_cw_cal"]
        values.update(c_cw_cal=c, reject_calibrated=cw_reject_calibrated(r["stat"], c),
                      decision_reference="calibrated", exploratory=calls.mode != "confirmation")
    return _Out("estimated", values, n_rows=r["n_rows"], n_dates=r["T"], lag=r["lag"])


def _diebold_mariano(calls: Calls) -> _Out:
    r = _lib(fctests.diebold_mariano, _need(calls, "m7").ev, "M7", "M1", calls.spec)
    return _Out("estimated", _plain(r), n_rows=r["n_rows"], n_dates=r["T"], lag=r["lag"])


def _per_call(calls: Calls, compute: Callable[[CallResult, str], dict]) -> _Out:
    """O41 to O43: one part per call; a failed call's part is None and its reason is listed under "failed"."""
    values: dict = {}
    failed: dict = {}
    for name in ("main", "m7"):
        c = getattr(calls, name)
        if c.status == "ok":
            values[name] = compute(c, name)
        else:
            values[name] = None
            failed[name] = c.reason
    values["failed"] = failed
    if len(failed) == 2:
        raise _NotEstimable(calls.main.reason)
    return _Out("estimated", values)


def _oos_r2(calls: Calls, bench: str) -> _Out:
    return _per_call(calls, lambda c, name: {m: _plain(_lib(fctests.oos_r2, c.ev, m, bench))
                                             for m in c.models if m != bench})


def _pesaran_timmermann(calls: Calls) -> _Out:
    return _per_call(calls, lambda c, name: {m: _pt(_lib(fctests.pesaran_timmermann, c.ev, m, c.folds_ev))
                                             for m in c.models})


def _importance(calls: Calls) -> _Out:
    c = _need(calls, "m7")
    model = IMPORTANCE[0]
    E0 = calls.E0
    K = c.folds if E0 is None else c.folds.loc[c.folds["test_start"] >= E0]
    t = _lib(forecast.importance_table, K, model)
    fl = c.folds.loc[c.folds["model"] == model]
    straddling = 0 if E0 is None else int(((fl["test_start"] < E0) & (E0 <= fl["test_end"])).sum())
    return _Out("estimated", {"model": model, "table": t[list(TABLE_COLUMNS)].to_dict("records"),
                              "repeats": t.attrs["repeats"], "n_folds": t.attrs["n_folds"],
                              "folds_straddling_excluded": straddling},
                n_rows=t.attrs["n_rows"])


def forecast_rows(calls: Calls) -> dict:
    """{id: entry} for exactly ROWS, in that order (section 5)."""
    compute = {"R9": lambda: _r9(calls), "O40": lambda: _diebold_mariano(calls),
               "O41": lambda: _oos_r2(calls, "M0"), "O42": lambda: _oos_r2(calls, "M1"),
               "O43": lambda: _pesaran_timmermann(calls), "O44": lambda: _importance(calls)}
    for rid in MODEL_ROWS:
        compute[rid] = lambda rid=rid: _model_row(calls, rid)
    for rid in CW_ROWS:
        compute[rid] = lambda rid=rid: _clark_west(calls, rid)
    return {rid: _row(rid, compute[rid]) for rid in ROWS}


# ------------------------------------------------------------------ fill (section 6)
def fill(doc: dict, rows: dict) -> dict:
    """A copy of P4-4a's document with each entry of `rows` in place of the pending entry of the same ID."""
    if set(rows) != set(ROWS) or len(rows) != len(ROWS):
        raise ValueError("rows must hold exactly the IDs of ROWS")
    out = _plain(doc)                      # rebuilds every dict and list: a deep copy of the plain document
    for rid in ROWS:
        old, new = out["rows"][rid], rows[rid]
        if old.get("status") != "pending" or old.get("item") != "P4-4b":
            raise ValueError(f"{rid}: the document's entry is not a pending P4-4b entry")
        if new.get("id") != rid or new.get("item") != "P4-4b":
            raise ValueError(f"{rid}: the new entry's id or item does not match")
        out["rows"][rid] = _plain(new)
    return out
