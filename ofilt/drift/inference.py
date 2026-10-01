"""Inference (Stage B). Part 1 (B1): design builder, pooled OLS, Driscoll-Kraay.

Blinding: every entry point calls blind.require_unblinded BEFORE touching the
target. On real dev data in Pass 1 that raises, so nothing involving a target
and an FX column together is ever computed.

Design (spec `model`): ticker fixed effects, NO global intercept; common FX
block [usdjpy_ret, eurusd_ret]; ticker-specific slopes on [spy_oc, copx_oc];
optionally ONE secondary term (spec secondary_family_holm: "primary design +
one term", so no moderator main effects; fx_asymmetry replaces usdjpy_ret by
(e_pos, e_neg)). Sample: drop rows flagged by the exclusion columns, then
require non-missing spec.require_nonmissing + target + secondary sources.
Features are built only through schema.select_features (the allowlist path).

Driscoll-Kraay: per-date score sums h_t = sum_i x_it * e_it; long-run matrix
S = sum_{|l|<=L} (1 - |l|/(L+1)) Gamma_l over the ORDERED UNIQUE DATES of the
estimation sample; cov = (X'X)^-1 S (X'X)^-1. L = floor(4*(T/100)**(2/9)) with
T = unique dates in the estimation sample. No small-sample correction; normal
reference; two-sided tests.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import linalg, stats

from . import blind, schema
from .spec import Spec
from .targets import CONSTRUCTED_TARGETS, DERIVED_NONFEATURES

SECONDARY_TERMS = ("fx_x_longwindow", "fx_x_jumpshare", "fx_x_highrv", "fx_asymmetry")
_SECONDARY_FEATURES = {"fx_x_longwindow": ["long_window"], "fx_x_jumpshare": ["jumpshare"],
                       "fx_x_highrv": ["rv_per_bar"], "fx_asymmetry": ["e_pos", "e_neg"]}
FORBIDDEN_TARGET_NAMES = frozenset(
    (schema.all_grouped_columns() - schema.TARGET_INPUTS) | schema.ALLOWED_FEATURES
    | blind.FX_NAMES | (DERIVED_NONFEATURES - CONSTRUCTED_TARGETS))


class DesignError(ValueError):
    """The requested design cannot be built as specified (fails closed)."""


@dataclass(frozen=True)
class Design:
    y: np.ndarray
    X: np.ndarray
    names: tuple[str, ...]
    dates: np.ndarray        # datetime64[ns], one per row
    tickers: np.ndarray      # str, one per row
    index: np.ndarray        # original df index labels of the rows used
    date_codes: np.ndarray   # 0..T-1, ordered by date
    T: int
    target: str
    secondary: str | None
    provenance: str

    def col(self, name: str) -> int:
        return self.names.index(name)


def build_design(df: pd.DataFrame, spec: Spec | None = None, *, target: str = "abn_oc",
                 secondary: str | None = None, exclude: list[str] | None = None,
                 rv_threshold: float | None = None, provenance: str | None = None) -> Design:
    prov = blind.require_unblinded(df, provenance=provenance)  # first: before touching the target
    spec = spec or Spec.load()
    if not isinstance(target, str) or target in FORBIDDEN_TARGET_NAMES:
        raise DesignError(f"{target!r} may not be used as a target (feature/FX/schema name)")
    if secondary not in (None, *SECONDARY_TERMS):
        raise DesignError(f"unknown secondary term {secondary!r}")
    fx, ctl, h1 = list(spec.fx_block), list(spec.controls), spec.h1_parameter
    extra = _SECONDARY_FEATURES.get(secondary, [])
    excl_cols = list(spec.inference_exclusion_flags) if exclude is None else list(exclude)
    need = list(dict.fromkeys(list(spec.require_nonmissing) + [target]
                              + sorted(schema.feature_sources(fx + ctl + extra))))
    missing = [c for c in excl_cols + need + ["date", "ticker"] if c not in df.columns]
    if missing:
        raise DesignError(f"panel lacks column(s) {missing}")
    keep = ~df[excl_cols].astype(bool).any(axis=1) & df[need].notna().all(axis=1)
    d = df.loc[keep]
    if d.empty:
        raise DesignError("no rows left after exclusions and non-missing requirements")
    feats = schema.select_features(d, fx + ctl + extra)
    tick = d["ticker"].astype(str).to_numpy()
    utick = np.unique(tick)
    cols, names = [], []
    for t in utick:
        cols.append((tick == t).astype(float)); names.append(f"fe[{t}]")
    fx_terms = (["e_pos", "e_neg"] + [c for c in fx if c != h1]) if secondary == "fx_asymmetry" else fx
    for c in fx_terms:
        cols.append(feats[c].to_numpy()); names.append(c)
    for c in ctl:
        for t in utick:
            cols.append(feats[c].to_numpy() * (tick == t)); names.append(f"{c}:{t}")
    e = feats[h1].to_numpy() if h1 in feats else None
    if secondary == "fx_x_longwindow":
        cols.append(e * feats["long_window"].to_numpy()); names.append(f"{h1}:long_window")
    elif secondary == "fx_x_jumpshare":
        cols.append(e * feats["jumpshare"].to_numpy()); names.append(f"{h1}:jumpshare")
    elif secondary == "fx_x_highrv":
        thr = spec.rv_per_bar_dev_median() if rv_threshold is None else float(rv_threshold)
        rvb = feats["rv_per_bar"].to_numpy()
        if np.isnan(rvb).any():
            raise DesignError("rv_per_bar undefined (usdjpy_bars <= 0) on some rows")
        cols.append(e * (rvb > thr)); names.append(f"{h1}:highrv")
    X = np.column_stack(cols)
    y = d[target].to_numpy(dtype=float)
    if not (np.isfinite(X).all() and np.isfinite(y).all()):
        raise DesignError("non-finite values in the design after sample selection")
    if np.linalg.matrix_rank(X) < X.shape[1]:
        raise DesignError(f"rank-deficient design ({np.linalg.matrix_rank(X)} < {X.shape[1]}): {names}")
    dates = d["date"].to_numpy(dtype="datetime64[ns]")
    _, codes = np.unique(dates, return_inverse=True)
    return Design(y=y, X=X, names=tuple(names), dates=dates, tickers=tick, index=d.index.to_numpy(),
                  date_codes=codes.astype(np.int64), T=int(codes.max()) + 1, target=target,
                  secondary=secondary, provenance=prov)


# ------------------------------------------------------------------ OLS
@dataclass(frozen=True)
class OLSFit:
    design: Design
    coef: np.ndarray
    resid: np.ndarray
    bread: np.ndarray        # (X'X)^-1


def pooled_ols(design: Design) -> OLSFit:
    blind.require_unblinded(provenance=design.provenance, arrays={"y": design.y})
    Q, R = np.linalg.qr(design.X, mode="reduced")
    coef = linalg.solve_triangular(R, Q.T @ design.y)
    Rinv = linalg.solve_triangular(R, np.eye(R.shape[0]))
    return OLSFit(design, coef, design.y - design.X @ coef, Rinv @ Rinv.T)


# -------------------------------------------------- Driscoll-Kraay core
def date_sums(scores: np.ndarray, date_codes: np.ndarray, T: int) -> np.ndarray:
    """(T, k) matrix of per-date sums of row scores."""
    scores = np.asarray(scores, dtype=float).reshape(len(date_codes), -1)
    H = np.zeros((T, scores.shape[1]))
    np.add.at(H, date_codes, scores)
    return H


def bartlett_long_run(H: np.ndarray, lag: int) -> np.ndarray:
    """S = Gamma_0 + sum_{l=1..L} (1 - l/(L+1)) (Gamma_l + Gamma_l'), Gamma_l = sum_t h_t h_{t-l}'."""
    if not isinstance(lag, (int, np.integer)) or lag < 0:
        raise ValueError("lag must be a non-negative integer")
    S = H.T @ H
    for l in range(1, min(int(lag), H.shape[0] - 1) + 1):
        G = H[l:].T @ H[:-l]
        S += (1.0 - l / (lag + 1.0)) * (G + G.T)
    return S


def driscoll_kraay(fit: OLSFit, lag: int | None = None) -> tuple[np.ndarray, int]:
    """DK covariance of the OLS coefficients and the lag used."""
    d = fit.design
    blind.require_unblinded(provenance=d.provenance, arrays={"y": d.y})
    L = Spec.dk_lag(int(d.T)) if lag is None else lag
    H = date_sums(d.X * fit.resid[:, None], d.date_codes, d.T)
    return fit.bread @ bartlett_long_run(H, L) @ fit.bread, int(L)


# --------------------------------------------------------------- results
@dataclass(frozen=True)
class Result:
    names: tuple[str, ...]
    coef: np.ndarray
    cov: np.ndarray
    lag: int
    T: int
    n: int
    alpha: float

    @property
    def se(self) -> np.ndarray:
        return np.sqrt(np.diag(self.cov))

    def contrast(self, weights: dict[str, float]) -> dict:
        """Two-sided normal test of sum_j w_j * coef_j = 0."""
        w = np.zeros(len(self.names))
        for k, v in weights.items():
            w[self.names.index(k)] = v
        est, se = float(w @ self.coef), float(np.sqrt(w @ self.cov @ w))
        z = est / se
        q = stats.norm.ppf(1 - self.alpha / 2)
        return dict(estimate=est, se=se, z=z, p=float(2 * stats.norm.sf(abs(z))),
                    ci=(est - q * se, est + q * se))

    def param(self, name: str) -> dict:
        return self.contrast({name: 1.0})


def fit_dk(design: Design, spec: Spec | None = None, lag: int | None = None) -> Result:
    """Pooled OLS with Driscoll-Kraay SEs (the primary estimator)."""
    spec = spec or Spec.load()
    fit = pooled_ols(design)
    cov, L = driscoll_kraay(fit, lag)
    return Result(design.names, fit.coef, cov, L, design.T, len(design.y), spec.alpha)
