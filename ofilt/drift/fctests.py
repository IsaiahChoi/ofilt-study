"""C5: forecast comparisons (spec forecast.comparisons and forecast.test_aggregation;
DECISIONS P26). Synthetic data only in Pass 1.

Inputs are the tidy predictions of ONE forecast.walk_forward call (PRED_COLUMNS: date,
ticker, fold, train_end, model, y, yhat) and, for the Pesaran-Timmermann base rate, that
call's fold log. Every public entry point that takes a predictions frame calls
blind.require_unblinded FIRST, before any column is read. On real dev data in Pass 1 that
raises, so no forecast of a real target is ever scored.

Pairing (fail closed). Two models are compared only on identical rows: the same
(date, ticker) keys, each exactly once, with the same fold, train_end and target value y
(bit for bit). walk_forward guarantees this for models run in the SAME call (one sample
per call, P27). Models from different calls, a dropped or duplicated row, or a different
target raise PairingError; nothing is silently aligned or intersected.

Aggregation (spec): per-row loss differential f_it -> mean across the tickers present on
each date, fbar_t -> Newey-West test of E[fbar_t] = 0 on the ordered date series:
    Omega = gamma_0 + 2 sum_{l=1..L} (1 - l/(L+1)) gamma_l,
    gamma_l = (1/T) sum_t (fbar_t - m)(fbar_{t-l} - m),  m = mean_t fbar_t,
    se = sqrt(Omega / T),  z = m / se,  normal reference,
with L = the spec lag rule at T = unique evaluation dates. The kernel is
inference.bartlett_long_run (the Driscoll-Kraay kernel) applied to the demeaned series.

Tests:
  * Clark-West (nested; ONE-sided; positive = the unrestricted model is better):
        f = (y - yhat_r)^2 - [(y - yhat_u)^2 - (yhat_r - yhat_u)^2]
          = 2 (y - yhat_r)(yhat_u - yhat_r).
  * Diebold-Mariano (TWO-sided; squared-error loss): d = (y - yhat_bench)^2 - (y - yhat_model)^2,
    positive favours `model`. Between nested models (M7 vs M1) DM's null distribution is
    non-standard and the test tends to under-reject; CW is the nested-appropriate test for
    the same pair, and both are reported as specified (P26).
  * OOS R2 = 1 - SSE(model) / SSE(benchmark), pooled over all evaluation rows and per ticker.
  * Pesaran-Timmermann (1992) directional test, 'up' = value > 0 (zero counts as not up),
    ONE-sided (positive = signs agree more often than independence implies), per ticker and
    on the equal-weighted portfolio (mean y and mean yhat across the tickers present on each
    date). Undefined (stat NaN, defined=False) when the outcome or the forecast has a
    constant sign, e.g. M0. Reported next to the training-window base rate: the share of
    positive targets in each fold's training rows (walk_forward's fold log, `train_up`),
    averaged over the evaluation rows (portfolio: evaluation dates) it applies to.
  * Wilson score interval for Monte Carlo rejection rates (C7); identical arithmetic to
    tools/report_B7b.wilson, clipped to [0, 1].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from . import blind
from .forecast import PRED_COLUMNS
from .inference import bartlett_long_run
from .spec import Spec, SpecError, dk_lag

SIDED = {"clark_west": "one", "diebold_mariano": "two"}
Z95 = float(stats.norm.ppf(0.975))


class PairingError(ValueError):
    """Two models' predictions are not on identical rows of one walk_forward call."""


@dataclass(frozen=True)
class Paired:
    first: str
    second: str
    dates: np.ndarray          # datetime64[ns], sorted by (date, ticker)
    tickers: np.ndarray        # str
    y: np.ndarray
    yhat_first: np.ndarray
    yhat_second: np.ndarray
    provenance: str


# ------------------------------------------------------------------ pairing
def _check_frame(preds: pd.DataFrame) -> None:
    missing = [c for c in PRED_COLUMNS if c not in preds.columns]
    if missing:
        raise ValueError(f"predictions lack {missing}")


def _model_rows(preds: pd.DataFrame, model: str) -> pd.DataFrame:
    rows = preds.loc[preds["model"] == model]
    if rows.empty:
        raise PairingError(f"model {model!r} has no predictions in this frame")
    rows = rows.sort_values(["date", "ticker"], kind="mergesort")
    if rows.duplicated(["date", "ticker"]).any():
        raise PairingError(f"{model}: duplicate (date, ticker) rows (predictions from more than one call?)")
    for c in ("y", "yhat"):
        if not np.isfinite(rows[c].to_numpy(dtype=float)).all():
            raise ValueError(f"{model}: non-finite {c}")
    return rows


def pair(preds: pd.DataFrame, first: str, second: str, *, provenance: str | None = None) -> Paired:
    """Align two models' predictions; refuse anything but identical rows."""
    prov = blind.require_unblinded(preds, provenance=provenance)
    _check_frame(preds)
    if first == second:
        raise ValueError("a model cannot be compared with itself")
    a, b = _model_rows(preds, first), _model_rows(preds, second)
    if len(a) != len(b):
        raise PairingError(f"{first} has {len(a)} rows and {second} has {len(b)}: not one walk_forward sample")
    for c in ("date", "ticker", "fold", "train_end", "y"):
        if not np.array_equal(a[c].to_numpy(), b[c].to_numpy()):
            raise PairingError(f"{first} and {second} differ in column {c!r}: not one walk_forward sample")
    return Paired(first, second, a["date"].to_numpy(dtype="datetime64[ns]"), a["ticker"].astype(str).to_numpy(),
                  a["y"].to_numpy(dtype=float), a["yhat"].to_numpy(dtype=float), b["yhat"].to_numpy(dtype=float),
                  prov)


# -------------------------------------------------------------- aggregation
def date_means(dates: np.ndarray, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(sorted unique dates, mean of `values` over the rows of each date)."""
    dates = np.asarray(dates, dtype="datetime64[ns]")
    values = np.asarray(values, dtype=float)
    u, inv = np.unique(dates, return_inverse=True)
    return u, np.bincount(inv, weights=values, minlength=u.size) / np.bincount(inv, minlength=u.size)


def nw_mean(x: np.ndarray, lag: int | None = None) -> dict:
    """Newey-West (Bartlett) test of E[x_t] = 0 on an ORDERED series (pure arithmetic).
    lrv = Omega (long-run variance of x_t), se = sqrt(Omega / T). Default lag = spec rule."""
    x = np.asarray(x, dtype=float).ravel()
    T = int(x.size)
    if T < 2 or not np.isfinite(x).all():
        raise ValueError("need at least 2 finite observations")
    L = dk_lag(T) if lag is None else lag
    m = float(x.mean())
    lrv = float(bartlett_long_run((x - m)[:, None], L)[0, 0]) / T
    if not lrv > 0:
        raise ValueError("degenerate series: zero long-run variance (identical forecasts?)")
    se = math.sqrt(lrv / T)
    return dict(mean=m, se=se, stat=m / se, lrv=lrv, lag=int(L), T=T)


def _date_aggregate(p: Paired, values: np.ndarray) -> float:
    return float(date_means(p.dates, values)[1].mean())


def _differential_test(p: Paired, f: np.ndarray, sided: str, alpha: float) -> dict:
    out = nw_mean(date_means(p.dates, f)[1])
    z = out["stat"]
    pval = float(stats.norm.sf(z)) if sided == "one" else float(2.0 * stats.norm.sf(abs(z)))
    out.update(p=pval, sided=sided, alpha=float(alpha), reject=bool(pval < alpha), n_rows=int(f.size))
    return out


# -------------------------------------------------------------------- tests
def clark_west(preds: pd.DataFrame, unrestricted: str, restricted: str, spec: Spec | None = None, *,
               provenance: str | None = None) -> dict:
    """One-sided Clark-West; positive = the unrestricted (larger, nesting) model is better."""
    p = pair(preds, unrestricted, restricted, provenance=provenance)
    spec = spec or Spec.load()
    e_u, e_r = p.y - p.yhat_first, p.y - p.yhat_second
    adj = (p.yhat_second - p.yhat_first) ** 2
    f = e_r ** 2 - (e_u ** 2 - adj)
    out = dict(test="clark_west", unrestricted=unrestricted, restricted=restricted)
    out.update(_differential_test(p, f, SIDED["clark_west"], spec.alpha))
    # Components on the same aggregation: mean = mspe_restricted - mspe_unrestricted + adjustment.
    out.update(mspe_restricted=_date_aggregate(p, e_r ** 2), mspe_unrestricted=_date_aggregate(p, e_u ** 2),
               adjustment=_date_aggregate(p, adj))
    return out


def diebold_mariano(preds: pd.DataFrame, model: str, benchmark: str, spec: Spec | None = None, *,
                    provenance: str | None = None) -> dict:
    """Two-sided Diebold-Mariano, squared-error loss; positive = `model` has the lower loss."""
    p = pair(preds, model, benchmark, provenance=provenance)
    spec = spec or Spec.load()
    l_m, l_b = (p.y - p.yhat_first) ** 2, (p.y - p.yhat_second) ** 2
    out = dict(test="diebold_mariano", model=model, benchmark=benchmark, loss="squared_error")
    out.update(_differential_test(p, l_b - l_m, SIDED["diebold_mariano"], spec.alpha))
    out.update(mse_model=_date_aggregate(p, l_m), mse_benchmark=_date_aggregate(p, l_b))
    return out


def oos_r2(preds: pd.DataFrame, model: str, benchmark: str, *, provenance: str | None = None) -> dict:
    """1 - SSE(model)/SSE(benchmark), pooled over all evaluation rows and per ticker."""
    p = pair(preds, model, benchmark, provenance=provenance)
    s_m, s_b = (p.y - p.yhat_first) ** 2, (p.y - p.yhat_second) ** 2

    def r2(sel):
        den = float(s_b[sel].sum())
        return float(1.0 - s_m[sel].sum() / den) if den > 0 else float("nan")

    return dict(model=model, benchmark=benchmark, pooled=r2(np.ones(p.y.size, dtype=bool)),
                per_ticker={t: r2(p.tickers == t) for t in np.unique(p.tickers)},
                n_rows=int(p.y.size), T=int(np.unique(p.dates).size))


def oos_r2_table(preds: pd.DataFrame, benchmarks: tuple[str, ...] = ("M0", "M1"), *,
                 provenance: str | None = None) -> pd.DataFrame:
    """Spec report_all: OOS R2 of every model in the frame against each benchmark present."""
    prov = blind.require_unblinded(preds, provenance=provenance)
    _check_frame(preds)
    models = sorted(preds["model"].unique())
    rows = []
    for bench in benchmarks:
        if bench not in models:
            continue
        for m in models:
            if m != bench:
                r = oos_r2(preds, m, bench, provenance=prov)
                rows.append(dict(model=m, benchmark=bench, pooled=r["pooled"], n_rows=r["n_rows"], T=r["T"],
                                 **{f"r2_{t}": v for t, v in r["per_ticker"].items()}))
    return pd.DataFrame(rows)


def pt_stat(y: np.ndarray, yhat: np.ndarray) -> dict:
    """Pesaran-Timmermann (1992) statistic for two equally long series (pure arithmetic):
    P = hit rate, P* = Py Pf + (1-Py)(1-Pf),
    Var(P) = P*(1-P*)/n,
    Var(P*) = (2Py-1)^2 Pf(1-Pf)/n + (2Pf-1)^2 Py(1-Py)/n + 4 Py Pf (1-Py)(1-Pf)/n^2,
    PT = (P - P*) / sqrt(Var(P) - Var(P*)), one-sided p = 1 - Phi(PT); 'up' = value > 0."""
    y, f = np.asarray(y, dtype=float), np.asarray(yhat, dtype=float)
    if y.ndim != 1 or y.shape != f.shape or y.size < 2:
        raise ValueError("y and yhat must be 1-d, equally long, n >= 2")
    if not (np.isfinite(y).all() and np.isfinite(f).all()):
        raise ValueError("non-finite input")
    n = int(y.size)
    uy, uf = y > 0, f > 0
    hit, py, pf = float(np.mean(uy == uf)), float(uy.mean()), float(uf.mean())
    p_star = py * pf + (1 - py) * (1 - pf)
    v_hit = p_star * (1 - p_star) / n
    v_star = ((2 * py - 1) ** 2 * pf * (1 - pf) / n + (2 * pf - 1) ** 2 * py * (1 - py) / n
              + 4 * py * pf * (1 - py) * (1 - pf) / n ** 2)
    out = dict(hit_rate=hit, p_star=p_star, up_share_y=py, up_share_yhat=pf, n=n)
    if py * (1 - py) * pf * (1 - pf) > 0:          # exact: zero iff a sign is constant
        den = v_hit - v_star
        if not den > 0:
            raise ArithmeticError("PT variance difference not positive")
        z = (hit - p_star) / math.sqrt(den)
        out.update(stat=float(z), p=float(stats.norm.sf(z)), defined=True)
    else:
        out.update(stat=float("nan"), p=float("nan"), defined=False)
    return out


def _fold_base_rates(rows: pd.DataFrame, folds: pd.DataFrame, model: str) -> tuple[np.ndarray, dict]:
    """Per-row training up-share by (fold, ticker) and per-fold portfolio up-share, from the
    fold log of the SAME call (checked against the predictions' per-fold row counts)."""
    if not isinstance(folds, pd.DataFrame) or not {"model", "fold", "n_test", "train_up"} <= set(folds.columns):
        raise ValueError("folds must be the walk_forward fold log (with train_up)")
    fl = folds.loc[folds["model"] == model]
    if fl["fold"].duplicated().any():
        raise PairingError(f"{model}: duplicate folds in the fold log (more than one call?)")
    fl = fl.set_index("fold")
    counts = rows.groupby("fold").size()
    for f, n in counts.items():
        if f not in fl.index or int(fl.at[f, "n_test"]) != int(n):
            raise PairingError(f"{model}: fold log does not match the predictions in fold {f} (another call?)")
    share = np.empty(len(rows))
    for i, (f, t) in enumerate(zip(rows["fold"].to_numpy(), rows["ticker"].astype(str).to_numpy())):
        n_up, n = fl.at[f, "train_up"]["by_ticker"].get(t, (0, 0))
        if n <= 0:
            raise ValueError(f"no training rows for ticker {t} in fold {f}")
        share[i] = n_up / n
    port = {f: fl.at[f, "train_up"]["portfolio"][0] / fl.at[f, "train_up"]["portfolio"][1] for f in counts.index}
    return share, port


def pesaran_timmermann(preds: pd.DataFrame, model: str, folds: pd.DataFrame, *,
                       provenance: str | None = None) -> dict:
    """PT per ticker and on the equal-weighted portfolio, each next to its training-window
    base rate (share of positive targets in the training rows, averaged over the
    evaluation rows / dates it applies to)."""
    blind.require_unblinded(preds, provenance=provenance)
    _check_frame(preds)
    rows = _model_rows(preds, model)
    share, port = _fold_base_rates(rows, folds, model)
    y, f = rows["y"].to_numpy(dtype=float), rows["yhat"].to_numpy(dtype=float)
    tick = rows["ticker"].astype(str).to_numpy()
    dates = rows["date"].to_numpy(dtype="datetime64[ns]")
    per = {}
    for t in np.unique(tick):
        sel = tick == t
        per[t] = dict(pt_stat(y[sel], f[sel]), base_rate_train=float(share[sel].mean()))
    u, ym = date_means(dates, y)
    _, fm = date_means(dates, f)
    fold_of_date = pd.Series(rows["fold"].to_numpy(), index=dates).groupby(level=0).first().reindex(u)
    portfolio = dict(pt_stat(ym, fm), base_rate_train=float(np.mean([port[k] for k in fold_of_date.to_numpy()])))
    return dict(model=model, per_ticker=per, portfolio=portfolio, n_rows=int(len(rows)), T=int(u.size))


# --------------------------------------------------------- spec comparisons
def spec_comparisons(spec: Spec | None = None) -> list[dict]:
    """The spec's forecast comparisons in order: primary first, then the secondaries."""
    spec = spec or Spec.load()
    pf = spec.value("forecast.comparisons.primary_forecast")
    if pf["test"] != "clark_west" or pf["sided"] != SIDED["clark_west"]:
        raise SpecError("primary forecast comparison must be one-sided Clark-West")
    out = [dict(role="primary", test=pf["test"], first=pf["unrestricted"], second=pf["restricted"],
                sided=pf["sided"])]
    for test, a, b in spec.value("forecast.comparisons.secondary"):
        out.append(dict(role="secondary", test=test, first=a, second=b, sided=SIDED[test]))
    return out


def run_comparisons(preds: pd.DataFrame, spec: Spec | None = None, *, provenance: str | None = None) -> dict:
    """Every spec comparison whose two models are in this frame (one walk_forward call);
    the others are listed under 'skipped' (they belong to another call, e.g. M7 with M1)."""
    prov = blind.require_unblinded(preds, provenance=provenance)
    _check_frame(preds)
    spec = spec or Spec.load()
    present = set(preds["model"].unique())
    done, skipped = [], []
    for c in spec_comparisons(spec):
        if {c["first"], c["second"]} <= present:
            fn = clark_west if c["test"] == "clark_west" else diebold_mariano
            done.append(dict(fn(preds, c["first"], c["second"], spec, provenance=prov), role=c["role"]))
        else:
            skipped.append(c)
    return dict(results=done, skipped=skipped)


# ------------------------------------------------------------- MC intervals
def wilson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion k/n (same arithmetic as
    tools/report_B7b.wilson), clipped to [0, 1]."""
    for v in (k, n):
        if isinstance(v, bool) or not isinstance(v, (int, np.integer)):
            raise TypeError("k and n must be integers")
    if not (n >= 1 and 0 <= k <= n and 0 < alpha < 1):
        raise ValueError("need n >= 1, 0 <= k <= n and 0 < alpha < 1")
    z = Z95 if alpha == 0.05 else float(stats.norm.ppf(1 - alpha / 2))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(max(0.0, c - h)), float(min(1.0, c + h))


def rate_summary(k: int, n: int, alpha: float = 0.05) -> dict:
    """Monte Carlo rejection rate with its MC SE and Wilson interval (keys as in B7b)."""
    lo, hi = wilson(k, n, alpha)
    p = k / n
    return dict(rate=p, k=int(k), n=int(n), mc_se=float(np.sqrt(p * (1 - p) / n)), wilson95=(lo, hi))
