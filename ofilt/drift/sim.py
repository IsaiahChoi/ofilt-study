"""Simulators. Part 1 (B4): synthetic_panel, a fully synthetic DGP.

Every frame produced here is labelled provenance='synthetic' and carries the
true parameters in attrs['truth']. It contains every column the B1-B3 designs
need, so it is a drop-in input for build_design / fit_dk / fit_joint / ...

DGP, per Tokyo date t and ticker i:
  (e, eur, spy, copx)_t ~ joint innovations with covariance PRED_COV
                          (corr(e, eur) = rho_fx, default -0.44)
  eps_it = phi * eps_i,t-1 + sqrt(1 - phi^2) u_it   (stationary, unit variance),
           u_t ~ equicorrelated across tickers (resid_corr, default 0.43)
  abn_oc = fe_i + b e + a2 eur + g_i spy + k_i copx + sigma_i eps_it
tails='t5': multivariate t(5) innovations (one chi-square draw per date, shared
across the block) rescaled by sqrt(3/5) to unit variance, applied to both the
predictor block and the residual innovations (independent chi-square draws).
Optional, consistent with targets.py identities:
  y_topix_oc = b_mkt e + 0.5 spy + 0.008 u_m;  raw_oc = abn_oc + beta * y_topix_oc
  gap_abn = (delta_cc - b) e + 0.01 u_g;       cc_abn = gap_abn + abn_oc
Magnitudes are round numbers; sigma defaults are the A7 per-ticker abnormal
open->close SDs (a target-only statistic), and the long-window share is the A6
dev share. Nothing here is fitted to data (that is B5's dev_calibrated).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import blind
from .spec import Spec

TICKERS = ("5706", "5711", "5713")
DEFAULT_SIGMA = (0.0155, 0.0108, 0.0133)   # ~ sqrt of A7 expanding-beta variances (bp^2 -> return)
PRED_NAMES = ("usdjpy_ret", "eurusd_ret", "spy_oc", "copx_oc")
PRED_SD = np.array([0.005, 0.004, 0.009, 0.016])
FE = (0.0002, -0.0001, 0.0001)
SPY_SLOPE, COPX_SLOPE = (0.5, 0.4, 0.45), (0.35, 0.2, 0.3)
LONG_SHARE, SHORT_H, LONG_H, BARS = 0.227, 17.9833, 65.9833, 1079.0


def pred_corr(rho_fx: float) -> np.ndarray:
    C = np.array([[1.0, rho_fx, 0.25, 0.10],
                  [rho_fx, 1.0, 0.05, 0.25],
                  [0.25, 0.05, 1.0, 0.60],
                  [0.10, 0.25, 0.60, 1.0]])
    np.linalg.cholesky(C)  # raises if not positive definite
    return C


def _innovations(rng: np.random.Generator, n: int, corr: np.ndarray, tails: str) -> np.ndarray:
    z = rng.standard_normal((n, corr.shape[0])) @ np.linalg.cholesky(corr).T
    if tails == "t5":
        z = z / np.sqrt(rng.chisquare(5, size=n) / 5.0)[:, None] * np.sqrt(3.0 / 5.0)
    return z


def synthetic_panel(n_dates: int = 1708, *, b: float = 0.0, a2: float = 0.0, seed: int | None = None,
                    tails: str = "gaussian", rho_fx: float = -0.44, resid_corr: float = 0.43,
                    phi: float = 0.1, sigma=DEFAULT_SIGMA, p_excl: float = 0.0, beta: float = 1.0,
                    b_mkt: float = 0.2, delta_cc: float | None = None,
                    start: str = "2015-01-06") -> pd.DataFrame:
    if tails not in ("gaussian", "t5"):
        raise ValueError(f"tails must be 'gaussian' or 't5', got {tails!r}")
    if not (isinstance(n_dates, (int, np.integer)) and n_dates >= 10):
        raise ValueError("n_dates must be an integer >= 10")
    if not (-1 < rho_fx < 1 and -0.5 < resid_corr < 1 and -1 < phi < 1 and 0 <= p_excl < 1):
        raise ValueError("rho_fx, resid_corr, phi or p_excl out of range")
    seed = Spec.load().seed if seed is None else int(seed)
    rng = np.random.default_rng(seed)
    n, k = int(n_dates), len(TICKERS)
    sigma = np.asarray(sigma, dtype=float)
    dates = pd.bdate_range(start, periods=n)

    P = _innovations(rng, n, pred_corr(rho_fx), tails) * PRED_SD      # (n, 4)
    Rc = np.full((k, k), resid_corr) + (1 - resid_corr) * np.eye(k)
    U = _innovations(rng, n, Rc, tails)                                # (n, 3)
    eps = np.empty_like(U)
    eps[0] = U[0]
    for t in range(1, n):
        eps[t] = phi * eps[t - 1] + np.sqrt(1 - phi * phi) * U[t]
    longw = rng.random(n) < LONG_SHARE
    bars = np.full(n, BARS)
    rv = bars * 1.2950114214e-08 * np.exp(rng.normal(0.0, 0.5, n))
    bv = rv * rng.uniform(0.7, 1.05, n)
    u_m, u_g = rng.standard_normal(n), rng.standard_normal((n, k))
    excl = rng.random((n, k)) < p_excl

    e, eur, spy, copx = (P[:, j] for j in range(4))
    m = b_mkt * e + 0.5 * spy + 0.008 * u_m
    frames = []
    for i, t in enumerate(TICKERS):
        abn = FE[i] + b * e + a2 * eur + SPY_SLOPE[i] * spy + COPX_SLOPE[i] * copx + sigma[i] * eps[:, i]
        d = dict(date=dates, ticker=t, usdjpy_ret=e, eurusd_ret=eur, spy_oc=spy, copx_oc=copx,
                 window_hours=np.where(longw, LONG_H, SHORT_H), usdjpy_rv=rv, usdjpy_bv=bv, usdjpy_bars=bars,
                 earn_flag=excl[:, i].astype(int), news_flag=0, beta=float(beta), abn_oc=abn,
                 y_topix_oc=m, raw_oc=abn + beta * m)
        if delta_cc is not None:
            d["gap_abn"] = (delta_cc - b) * e + 0.01 * u_g[:, i]
            d["cc_abn"] = d["gap_abn"] + abn
        frames.append(pd.DataFrame(d))
    df = pd.concat(frames).sort_values(["date", "ticker"], kind="mergesort").reset_index(drop=True)
    df.attrs = {"provenance": blind.SYNTHETIC,
                "truth": dict(b=b, a2=a2, fe=FE, spy_slope=SPY_SLOPE, copx_slope=COPX_SLOPE,
                              sigma=tuple(sigma), phi=phi, resid_corr=resid_corr, rho_fx=rho_fx,
                              tails=tails, beta=beta, b_mkt=b_mkt, delta_cc=delta_cc, seed=seed,
                              n_dates=n, p_excl=p_excl)}
    return df


def true_residuals(df: pd.DataFrame) -> np.ndarray:
    """sigma_i * eps_it recovered from attrs['truth'] (synthetic frames only), in df row order."""
    if df.attrs.get("provenance") != blind.SYNTHETIC or "truth" not in df.attrs:
        raise ValueError("true_residuals needs a synthetic_panel frame")
    tr = df.attrs["truth"]
    j = df["ticker"].map({t: i for i, t in enumerate(TICKERS)}).to_numpy()
    fe, gs, ks = (np.asarray(tr[x])[j] for x in ("fe", "spy_slope", "copx_slope"))
    return (df.abn_oc - fe - tr["b"] * df.usdjpy_ret - tr["a2"] * df.eurusd_ret
            - gs * df.spy_oc - ks * df.copx_oc).to_numpy()
