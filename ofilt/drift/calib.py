"""Calibration helpers for Pass 3 (DQ3, DQ4; PASS3_STATUS Decision log). Outside the C7 key.

Implements, by calling existing code without changing it (inference.build_design, inference.fit_dk,
inference.fit_huber, sim.stationary_bootstrap_positions, blind):
  D3.1  the bootstrap test of H1: the Driscoll-Kraay t of the H1 parameter, t = b/se; a stationary bootstrap of whole
        dates of the estimation sample (mean block 5), the T dates drawn to length T in drawn order and refitted with
        the same design and DK lag; t* = (b* - b)/se* (recentred, not null-imposed). Reject if |t| > c_boot, the 0.95
        order statistic of |t*|; interval b +/- c_boot se; TOST uses the 0.90 order statistic.
  D3.2  the warp-speed draw is bootstrap_t with B = 1.
  D3.3  order statistics with their 95% intervals (c_cal, c_boot, c_CW,cal).
  D4.3  FX winsorisation at the spec's bounds; stationary-bootstrap positions inside an early window.
Every public function that receives a frame calls blind.require_unblinded first, as the entry points of inference
(inference.py:75), fctests (fctests.py:99) and forecast (forecast.py:209) do (P29). No file I/O and no global state;
no other module's attributes are changed.
"""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np
import pandas as pd
from scipy import stats

from . import blind
from . import inference as _inf
from . import sim as _sim
from .spec import Spec

Z975 = float(stats.norm.ppf(0.975))     # as tools/report_B7b.py:34
Z_INTERVAL = 1.959964                   # the order-statistic interval's multiplier (P3-2a)


# ------------------------------------------------------------------ Monte Carlo summaries
def wilson(k: int, n: int, z: float = Z975) -> tuple[float, float]:
    """Wilson score interval, the arithmetic of tools/report_B7b.py:37-42 (fctests.wilson is the same, clipped)."""
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(c - h), float(c + h)


def order_stat_ranks(n: int, level: float) -> tuple[int, int, int]:
    """(k, k_lo, k_hi), 1-based: k = ceil(level n); k_lo = max(1, floor(n level - z sqrt(n level (1 - level))));
    k_hi = min(n, ceil(n level + z sqrt(...))), z = 1.959964. level is read as its decimal string (exact n level)."""
    if not (isinstance(n, (int, np.integer)) and n >= 1 and 0 < level < 1):
        raise ValueError("need an integer n >= 1 and 0 < level < 1")
    nl = Fraction(str(level)) * int(n)
    half = Z_INTERVAL * math.sqrt(float(nl) * (1 - level))
    k = math.ceil(nl)
    return int(k), int(max(1, math.floor(float(nl) - half))), int(min(n, math.ceil(float(nl) + half)))


def order_stat(x, level: float) -> float:
    """The ceil(level n)-th smallest value of x."""
    v = np.sort(np.asarray(x, dtype=float).ravel())
    k, _, _ = order_stat_ranks(v.size, level)
    return float(v[k - 1])


def order_stat_interval(x, level: float) -> tuple[float, float]:
    """The 95% order-statistic interval of the level quantile: the k_lo-th and k_hi-th smallest values."""
    v = np.sort(np.asarray(x, dtype=float).ravel())
    _, lo, hi = order_stat_ranks(v.size, level)
    return float(v[lo - 1]), float(v[hi - 1])


def mde80(bs, rates, sd: float | None = None, mean_se: float | None = None) -> dict:
    """MDE at 80% power as tools/report_B7b.py:70-77 (probit-scale interpolation between bracketing grid points,
    b ascending) and its cross-checks as report_B7b.py:122-128: (z_.975 + z_.80) x sd(b_hat) and x mean DK SE."""
    points = list(zip([float(b) for b in bs], [float(r) for r in rates]))
    target = stats.norm.ppf(0.80)
    probit = None
    for (b0, p0), (b1, p1) in zip(points[:-1], points[1:]):
        if p0 <= 0.80 <= p1 and p1 > p0:
            q0, q1 = stats.norm.ppf(np.clip([p0, p1], 1e-6, 1 - 1e-6))
            probit = float(b0 + (target - q0) * (b1 - b0) / (q1 - q0))
            break
    k = Z975 + stats.norm.ppf(0.8)
    return dict(probit_interpolated=probit,
                normal_approx_sd=None if sd is None else float(k * sd),
                normal_approx_mean_se=None if mean_se is None else float(k * mean_se))


# ------------------------------------------------------------------ decisions
def rejects(t, c):
    """Two-sided rejection: |t| > c (elementwise)."""
    return np.abs(np.asarray(t, dtype=float)) > c


def tost_declares(b, se, sesoi, c):
    """Equivalence declared: (b - c se > -sesoi) and (b + c se < sesoi) (elementwise)."""
    b, se = np.asarray(b, dtype=float), np.asarray(se, dtype=float)
    return (b - c * se > -sesoi) & (b + c * se < sesoi)


# ------------------------------------------------------------------ fits and resampling
def fit_t(frame: pd.DataFrame, spec: Spec, target: str, lag: int | None = None) -> dict:
    """build_design then fit_dk (normal reference). b, se, t and lag for spec.h1_parameter, and b, se, t for
    spec.h3_parameter (H3); T and n of the design; the index of the estimation-sample rows."""
    blind.require_unblinded(frame)
    d = _inf.build_design(frame, spec, target=target)
    r = _inf.fit_dk(d, spec, lag)
    p1, p3 = r.param(spec.h1_parameter), r.param(spec.h3_parameter)
    return dict(b=p1["estimate"], se=p1["se"], t=p1["estimate"] / p1["se"], lag=r.lag,
                b_h3=p3["estimate"], se_h3=p3["se"], t_h3=p3["estimate"] / p3["se"],
                T=r.T, n=r.n, index=d.index)


def resample_dates(frame: pd.DataFrame, rng: np.random.Generator, mean_block: float = 5.0) -> pd.DataFrame:
    """Stationary bootstrap of whole dates: the frame's T unique dates (sorted) are drawn to length T with
    sim.stationary_bootstrap_positions(T, mean_block, rng, n_out=T); each drawn date's rows are copied in drawn order
    and the dates are relabelled to a consecutive synthetic business-day calendar from sim.SIM_CALENDAR_START, the
    mechanism of DevCalibrator.draw (sim.py:225-230). The provenance is the input's (synthetic stays synthetic)."""
    prov = blind.require_unblinded(frame)
    f = frame.sort_values(["date", "ticker"], kind="mergesort")
    codes = np.unique(f["date"].to_numpy(dtype="datetime64[ns]"), return_inverse=True)[1]
    bounds = np.r_[0, np.cumsum(np.bincount(codes))]
    T = len(bounds) - 1
    pos = _sim.stationary_bootstrap_positions(T, mean_block, rng, n_out=T)
    lens = np.diff(bounds)[pos]
    offs = np.r_[0, np.cumsum(lens)[:-1]]
    src = np.repeat(bounds[pos] - offs, lens) + np.arange(int(lens.sum()))
    out = f.iloc[src].reset_index(drop=True)
    cal = pd.bdate_range(_sim.SIM_CALENDAR_START, periods=T)
    out["date"] = np.repeat(cal.to_numpy(), lens)
    out.attrs = {"provenance": prov}
    return out


def bootstrap_t(frame: pd.DataFrame, spec: Spec, rng: np.random.Generator, target: str, B: int,
                mean_block: float = 5.0) -> dict:
    """B resamples of the estimation sample's dates (resample_dates), each refitted by fit_t with the original fit's
    DK lag: t* = (b* - b)/se* for H1 and for H3. B = 1 is the warp-speed draw (D3.2)."""
    blind.require_unblinded(frame)
    if not (isinstance(B, (int, np.integer)) and B >= 1):
        raise ValueError("B must be an integer >= 1")
    f0 = fit_t(frame, spec, target)
    sample = frame.loc[f0["index"]]
    sample.attrs = dict(frame.attrs)
    t1, t3 = np.empty(B), np.empty(B)
    for i in range(B):
        fi = fit_t(resample_dates(sample, rng, mean_block), spec, target, lag=f0["lag"])
        t1[i] = (fi["b"] - f0["b"]) / fi["se"]
        t3[i] = (fi["b_h3"] - f0["b_h3"]) / fi["se_h3"]
    return dict(fit={k: v for k, v in f0.items() if k != "index"}, t_star=t1, t_star_h3=t3)


def bootstrap_test(frame: pd.DataFrame, spec: Spec, rng: np.random.Generator, target: str, B: int = 9999,
                   mean_block: float = 5.0) -> dict:
    """The confirmation procedure of D3.1: reject H1 if |t| > c_boot = the 0.95 order statistic of |t*|; interval
    b +/- c_boot se; c_boot at 0.90 for TOST (tost_declares(b, se, sesoi, c_boot_90))."""
    blind.require_unblinded(frame)
    bt = bootstrap_t(frame, spec, rng, target, B, mean_block)
    f = bt["fit"]
    a = np.abs(bt["t_star"])
    c95, c90 = order_stat(a, 0.95), order_stat(a, 0.90)
    return dict(reject=bool(rejects(f["t"], c95)), c_boot_95=c95, c_boot_90=c90,
                interval=(f["b"] - c95 * f["se"], f["b"] + c95 * f["se"]), b=f["b"], se=f["se"], t=f["t"],
                lag=f["lag"], B=int(B))


# ------------------------------------------------------------------ D4.3 helpers
def winsorise_fx(frame: pd.DataFrame, spec: Spec) -> pd.DataFrame:
    """Copy of the frame with usdjpy_ret and eurusd_ret clipped at Spec.winsor_bounds(); other columns unchanged."""
    blind.require_unblinded(frame)
    out = frame.copy()
    for c, (lo, hi) in spec.winsor_bounds().items():
        out[c] = out[c].clip(lower=lo, upper=hi)
    out.attrs = dict(frame.attrs)
    return out


def window_positions(K: int, n_out: int, rng: np.random.Generator, mean_block: float = 5.0) -> np.ndarray:
    """Stationary-bootstrap positions in [0, K) (the first K source dates: D4.3's early window)."""
    return _sim.stationary_bootstrap_positions(int(K), mean_block, rng, n_out=int(n_out))


# ------------------------------------------------------------------ P3-2b addition (new function only)
def bootstrap_t_given_fit(frame: pd.DataFrame, spec: Spec, rng: np.random.Generator, target: str, B: int,
                          fit: dict, mean_block: float = 5.0) -> dict:
    """bootstrap_t with the original fit supplied (fit_t(frame, spec, target)'s output) instead of recomputed: the same
    resampling, refits and t* = (b* - b)/se*, for H1 and H3. tests/test_p3_sealed_run.py shows it returns exactly
    bootstrap_t's t* for the same frame and generator seed."""
    blind.require_unblinded(frame)
    if not (isinstance(B, (int, np.integer)) and B >= 1):
        raise ValueError("B must be an integer >= 1")
    sample = frame.loc[fit["index"]]
    sample.attrs = dict(frame.attrs)
    t1, t3 = np.empty(B), np.empty(B)
    for i in range(B):
        fi = fit_t(resample_dates(sample, rng, mean_block), spec, target, lag=fit["lag"])
        t1[i] = (fi["b"] - fit["b"]) / fi["se"]
        t3[i] = (fi["b_h3"] - fit["b_h3"]) / fi["se_h3"]
    return dict(t_star=t1, t_star_h3=t3)
