"""Inference (Stage B). Part 1 (B1): design builder, pooled OLS, Driscoll-Kraay.
Part 2 (B2): Huber M-estimator, exact date-deletion influence and curve, TOST.
Part 3 (B3): stacked (b, delta_cc) with joint DK covariance; fraction unpriced f
with delta-method and Fieller CIs; b_mkt and the raw/abnormal decomposition; Holm.

Blinding: every entry point calls blind.require_unblinded BEFORE touching the
target. On real dev data in Pass 1 that raises, so nothing involving a target
and an FX column together is ever computed.

Design (spec `model`): ticker fixed effects, NO global intercept; common FX
block [usdjpy_ret, eurusd_ret]; ticker-specific slopes on [spy_oc, copx_oc];
optionally ONE secondary family member (spec secondary_family_holm, amended
AM-01): the moderator main effect AND its interaction with usdjpy_ret; the
tested coefficient is the interaction (SECONDARY_TESTED). fx_asymmetry replaces
usdjpy_ret by (e_pos, e_neg) and tests equal slopes. Sample: drop rows flagged by the exclusion columns, then
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
SECONDARY_TESTED = {"fx_x_longwindow": {"usdjpy_ret:long_window": 1.0},
                    "fx_x_jumpshare": {"usdjpy_ret:jumpshare": 1.0},
                    "fx_x_highrv": {"usdjpy_ret:highrv": 1.0},
                    "fx_asymmetry": {"e_pos": 1.0, "e_neg": -1.0}}   # contrast weights; H0: = 0
FORBIDDEN_TARGET_NAMES = frozenset(
    (schema.all_grouped_columns() - schema.TARGET_INPUTS) | schema.ALLOWED_FEATURES
    | blind.FX_NAMES | (DERIVED_NONFEATURES - CONSTRUCTED_TARGETS) | {"highrv"})


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
    mod = None
    if secondary == "fx_x_longwindow":
        mod, mname = feats["long_window"].to_numpy(), "long_window"
    elif secondary == "fx_x_jumpshare":
        mod, mname = feats["jumpshare"].to_numpy(), "jumpshare"
    elif secondary == "fx_x_highrv":
        thr = spec.rv_per_bar_dev_median() if rv_threshold is None else float(rv_threshold)
        rvb = feats["rv_per_bar"].to_numpy()
        if np.isnan(rvb).any():
            raise DesignError("rv_per_bar undefined (usdjpy_bars <= 0) on some rows")
        mod, mname = (rvb > thr).astype(float), "highrv"
    if mod is not None:  # AM-01: moderator main effect, then the tested interaction
        cols += [mod, e * mod]; names += [mname, f"{h1}:{mname}"]
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
    info: dict | None = None

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


# ================================================================ part 2
def _check(design: Design) -> None:
    blind.require_unblinded(provenance=design.provenance, arrays={"y": design.y})


def subset_design(design: Design, keep: np.ndarray) -> Design:
    """Rows where keep is True; date codes and T recomputed; rank re-checked."""
    keep = np.asarray(keep, dtype=bool)
    X = design.X[keep]
    if np.linalg.matrix_rank(X) < X.shape[1]:
        raise DesignError("rank-deficient design after subsetting")
    dates = design.dates[keep]
    _, codes = np.unique(dates, return_inverse=True)
    return Design(y=design.y[keep], X=X, names=design.names, dates=dates, tickers=design.tickers[keep],
                  index=design.index[keep], date_codes=codes.astype(np.int64), T=int(codes.max()) + 1,
                  target=design.target, secondary=design.secondary, provenance=design.provenance)


# ----------------------------------------------------------------- Huber
def huber_psi(u: np.ndarray, c: float) -> np.ndarray:
    return np.clip(u, -c, c)


def fit_huber(design: Design, spec: Spec | None = None, *, c: float | None = None, lag: int | None = None,
              tol: float = 1e-11, max_iter: int = 1000) -> Result:
    """Huber M-estimator by IRLS with FIXED scale s = 1.4826 * MAD(OLS residuals)
    (MAD about the median). Sandwich A^-1 S A^-1 with row scores g = x * s * psi(r/s),
    A = X' diag(psi'(r/s)) X, S = DK long-run matrix of per-date sums of g (same lag
    rule). As c -> inf this is exactly OLS with DK SEs. The scale is treated as
    known (standard for a fixed preliminary scale)."""
    _check(design)
    spec = spec or Spec.load()
    c = spec.huber_c if c is None else float(c)
    X, y = design.X, design.y
    ols = pooled_ols(design)
    r0 = ols.resid
    scale = 1.4826 * float(np.median(np.abs(r0 - np.median(r0))))
    if not scale > 0:
        raise ValueError("MAD scale of OLS residuals is zero")
    beta = ols.coef.copy()
    for it in range(1, max_iter + 1):
        u = (y - X @ beta) / scale
        w = np.where(np.abs(u) <= c, 1.0, c / np.maximum(np.abs(u), 1e-300))
        sw = np.sqrt(w)
        new = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
        step = np.max(np.abs(new - beta)) / max(1.0, np.max(np.abs(new)))
        beta = new
        if step < tol:
            break
    else:
        raise RuntimeError(f"Huber IRLS did not converge in {max_iter} iterations")
    u = (y - X @ beta) / scale
    g = X * (scale * huber_psi(u, c))[:, None]
    A = X.T @ (X * (np.abs(u) <= c)[:, None])
    Ainv = np.linalg.inv(A)
    L = Spec.dk_lag(int(design.T)) if lag is None else lag
    cov = Ainv @ bartlett_long_run(date_sums(g, design.date_codes, design.T), L) @ Ainv
    return Result(design.names, beta, cov, int(L), design.T, len(y), spec.alpha,
                  info=dict(estimator="huber", c=c, scale=scale, iterations=it,
                            share_downweighted=float(np.mean(np.abs(u) > c))))


# ------------------------------------------------------------- influence
def date_influence(design: Design, param: str | None = None) -> pd.DataFrame:
    """Exact OLS change in `param` from deleting ALL rows of each date:
    beta_(-t) - beta = -(X'X)^-1 X_t' (I - H_tt)^-1 e_t. Sorted by |change| desc."""
    _check(design)
    param = param or Spec.load().h1_parameter
    j = design.col(param)
    fit = pooled_ols(design)
    X, e, Binv = design.X, fit.resid, fit.bread
    rows = np.argsort(design.date_codes, kind="stable")
    bounds = np.r_[0, np.cumsum(np.bincount(design.date_codes, minlength=design.T))]
    delta = np.empty(design.T)
    for t in range(design.T):
        idx = rows[bounds[t]:bounds[t + 1]]
        Xt = X[idx]
        Htt = Xt @ Binv @ Xt.T
        delta[t] = -(Binv @ Xt.T @ np.linalg.solve(np.eye(len(idx)) - Htt, e[idx]))[j]
    udates = np.unique(design.dates)
    out = pd.DataFrame({"date": udates, "delta_b": delta, "abs_delta_b": np.abs(delta)})
    out = out.sort_values("abs_delta_b", ascending=False, kind="mergesort").reset_index(drop=True)
    out["rank"] = np.arange(1, len(out) + 1)
    return out


def influence_curve(design: Design, spec: Spec | None = None, param: str | None = None,
                    k_max: int | None = None) -> pd.DataFrame:
    """b (with DK SE) after cumulatively deleting the top-k influential dates,
    k = 0..k_max; ranking fixed from the FULL sample (spec robustness.influence_curve)."""
    _check(design)
    spec = spec or Spec.load()
    param = param or spec.h1_parameter
    k_max = spec.influence_k_max if k_max is None else int(k_max)
    ranking = date_influence(design, param)
    rows = []
    for k in range(0, k_max + 1):
        drop = ranking["date"].to_numpy(dtype="datetime64[ns]")[:k]   # explicit dtype: isin is dtype-sensitive
        sub = subset_design(design, ~np.isin(design.dates, drop)) if k else design
        r = fit_dk(sub, spec)
        p = r.param(param)
        rows.append(dict(k=k, date_removed=ranking["date"].iloc[k - 1] if k else pd.NaT,
                         b=p["estimate"], se=p["se"], z=p["z"], p=p["p"], n_dates=r.T, lag=r.lag))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ TOST
def tost(estimate: float, se: float, sesoi: float, alpha: float = 0.05) -> dict:
    """Two one-sided tests of H0: |theta| >= sesoi (normal reference).
    Equivalence iff both one-sided nulls are rejected at alpha, i.e. iff the
    (1 - 2*alpha) CI lies inside (-sesoi, sesoi)."""
    if not (sesoi > 0 and se > 0 and 0 < alpha < 0.5):
        raise ValueError("need sesoi > 0, se > 0, 0 < alpha < 0.5")
    p_lower = float(stats.norm.sf((estimate + sesoi) / se))    # H0: theta <= -sesoi
    p_upper = float(stats.norm.cdf((estimate - sesoi) / se))   # H0: theta >= +sesoi
    q = stats.norm.ppf(1 - alpha)
    return dict(p=max(p_lower, p_upper), p_lower=p_lower, p_upper=p_upper,
                equivalent=bool(max(p_lower, p_upper) < alpha),
                ci=(estimate - q * se, estimate + q * se), sesoi=sesoi, alpha=alpha)


def tost_result(result: Result, param: str, spec: Spec | None = None, sesoi: float | None = None) -> dict:
    """TOST on a fitted parameter. Without an explicit sesoi it uses spec.sesoi(),
    which raises SpecPendingError while the spec says PENDING_COSTS."""
    spec = spec or Spec.load()
    sesoi = spec.sesoi() if sesoi is None else sesoi
    p = result.param(param)
    return tost(p["estimate"], p["se"], float(sesoi), float(spec.value("equivalence.alpha")))


# ================================================================ part 3
@dataclass(frozen=True)
class JointResult:
    """Two targets on ONE common sample and ONE design; joint DK covariance."""
    names: tuple[str, ...]
    targets: tuple[str, str]
    coef: np.ndarray        # (2k,): [coef target 1, coef target 2]
    cov: np.ndarray         # (2k, 2k)
    lag: int
    T: int
    n: int
    alpha: float

    def pair(self, param: str) -> tuple[float, float, np.ndarray]:
        k, j = len(self.names), self.names.index(param)
        ix = [j, k + j]
        return float(self.coef[j]), float(self.coef[k + j]), self.cov[np.ix_(ix, ix)]

    def result(self, i: int) -> Result:
        k = len(self.names)
        sl = slice(i * k, (i + 1) * k)
        return Result(self.names, self.coef[sl], self.cov[sl, sl], self.lag, self.T, self.n, self.alpha)


def fit_joint(df: pd.DataFrame, spec: Spec | None = None, *, targets: tuple[str, str] = ("abn_oc", "cc_abn"),
              secondary: str | None = None, exclude: list[str] | None = None,
              provenance: str | None = None, lag: int | None = None) -> JointResult:
    """Stacked OLS of two targets on the same design and common sample (rows where
    both targets are non-missing). Row scores [x*e1, x*e2] are summed by date and
    passed through the same Bartlett long-run matrix: cov = Bj S Bj, Bj = diag(B, B)."""
    blind.require_unblinded(df, provenance=provenance)
    spec = spec or Spec.load()
    t1, t2 = targets
    for t in targets:
        if t in FORBIDDEN_TARGET_NAMES or t not in df.columns:
            raise DesignError(f"bad target {t!r}")
    sub = df.loc[df[t1].notna() & df[t2].notna()]
    d1 = build_design(sub, spec, target=t1, secondary=secondary, exclude=exclude, provenance=provenance)
    d2 = build_design(sub, spec, target=t2, secondary=secondary, exclude=exclude, provenance=provenance)
    if not (np.array_equal(d1.index, d2.index) and np.array_equal(d1.X, d2.X)):
        raise DesignError("joint designs differ")  # cannot happen with a common sample
    f1, f2 = pooled_ols(d1), pooled_ols(d2)
    L = Spec.dk_lag(int(d1.T)) if lag is None else lag
    H = date_sums(np.hstack([d1.X * f1.resid[:, None], d1.X * f2.resid[:, None]]), d1.date_codes, d1.T)
    Bj = linalg.block_diag(f1.bread, f1.bread)
    cov = Bj @ bartlett_long_run(H, L) @ Bj
    return JointResult(d1.names, (t1, t2), np.r_[f1.coef, f2.coef], cov, int(L), d1.T, len(d1.y), spec.alpha)


def fraction_from(b: float, d: float, V: np.ndarray, alpha: float) -> dict:
    """f = b/d with delta-method and Fieller CIs (normal reference).
    Fieller set {f: (b - f d)^2 <= q^2 (Vbb - 2 f Vbd + f^2 Vdd)}, i.e.
    A f^2 + B f + C <= 0 with A = d^2 - q^2 Vdd, B = -2(b d - q^2 Vbd), C = b^2 - q^2 Vbb.
    f_hat always belongs to it, so it is never empty: 'bounded' iff A > 0
    (|t_d| > q), else 'two_rays' (complement of an open interval) or 'real_line'."""
    V = np.asarray(V, dtype=float)
    q = float(stats.norm.ppf(1 - alpha / 2))
    f = b / d
    g = np.array([1.0 / d, -b / d ** 2])
    se = float(np.sqrt(g @ V @ g))
    A, Bc, C = d * d - q * q * V[1, 1], -2.0 * (b * d - q * q * V[0, 1]), b * b - q * q * V[0, 0]
    disc = Bc * Bc - 4.0 * A * C
    if A > 0:
        r = np.sqrt(max(disc, 0.0))
        fie = dict(kind="bounded", ci=((-Bc - r) / (2 * A), (-Bc + r) / (2 * A)))
    elif disc > 0 and A < 0:
        r = np.sqrt(disc)
        lo, hi = sorted(((-Bc - r) / (2 * A), (-Bc + r) / (2 * A)))
        fie = dict(kind="two_rays", ci=((-np.inf, lo), (hi, np.inf)))
    else:
        fie = dict(kind="real_line", ci=(-np.inf, np.inf))
    return dict(f=f, se_delta=se, ci_delta=(f - q * se, f + q * se), fieller=fie,
                t_denominator=float(d / np.sqrt(V[1, 1])), b=b, delta_cc=d, alpha=alpha)


def fraction_unpriced(joint: JointResult, param: str | None = None) -> dict:
    """f = b / delta_cc for the (abn_oc, cc_abn) joint fit (spec fraction_unpriced)."""
    param = param or Spec.load().h1_parameter
    b, d, V = joint.pair(param)
    return fraction_from(b, d, V, joint.alpha)


def fit_market(df: pd.DataFrame, spec: Spec | None = None, *, exclude: list[str] | None = None,
               provenance: str | None = None, lag: int | None = None) -> Result:
    """b_mkt: hedge_oc on the date-level version of the primary design (intercept +
    FX block + controls with common slopes), one row per unique date of the primary
    estimation sample; time-series NW with the same lag rule (= DK with one row per date)."""
    spec = spec or Spec.load()
    hedge = spec.hedge_oc_column
    pooled = build_design(df, spec, target=hedge, exclude=exclude, provenance=provenance)  # guard first
    cols = [hedge] + list(spec.fx_block) + list(spec.controls)
    rows = df.loc[pooled.index, ["date"] + cols]
    if (rows.groupby("date")[cols].nunique(dropna=False) > 1).any().any():
        raise DesignError("market variables differ across tickers within a date")
    m = rows.groupby("date", sort=True)[cols].first()
    T = len(m)
    X = np.column_stack([np.ones(T)] + [m[c].to_numpy(dtype=float) for c in cols[1:]])
    dm = Design(y=m[hedge].to_numpy(dtype=float), X=X, names=("const",) + tuple(cols[1:]),
                dates=m.index.to_numpy(dtype="datetime64[ns]"), tickers=np.array(["MKT"] * T),
                index=np.arange(T), date_codes=np.arange(T, dtype=np.int64), T=T, target=hedge,
                secondary=None, provenance=pooled.provenance)
    return fit_dk(dm, spec, lag)


def decomposition(df: pd.DataFrame, spec: Spec | None = None, *, exclude: list[str] | None = None,
                  provenance: str | None = None) -> dict:
    """b_raw vs mean_beta * b_mkt + b_abn (spec target.decomposition). Exact (gap = 0)
    when beta is constant and the sample is balanced; otherwise an approximation."""
    spec = spec or Spec.load()
    h1 = spec.h1_parameter
    da = build_design(df, spec, target="abn_oc", exclude=exclude, provenance=provenance)
    dr = build_design(df, spec, target="raw_oc", exclude=exclude, provenance=provenance)
    if not np.array_equal(da.index, dr.index):
        raise DesignError("raw and abnormal samples differ")
    ra, rr = fit_dk(da, spec).param(h1), fit_dk(dr, spec).param(h1)
    rm = fit_market(df, spec, exclude=exclude, provenance=provenance).param(h1)
    mean_beta = float(df.loc[da.index, "beta"].mean())
    approx = mean_beta * rm["estimate"] + ra["estimate"]
    return dict(b_raw=rr["estimate"], b_abn=ra["estimate"], b_mkt=rm["estimate"], mean_beta=mean_beta,
                approx=approx, gap=rr["estimate"] - approx,
                se_raw=rr["se"], se_abn=ra["se"], se_mkt=rm["se"])


def holm(pvalues) -> np.ndarray:
    """Holm step-down adjusted p-values, in the input order (monotone, capped at 1)."""
    p = np.asarray(pvalues, dtype=float)
    if p.ndim != 1 or not np.all((p >= 0) & (p <= 1)):
        raise ValueError("p-values must be a 1-d array in [0, 1]")
    m = len(p)
    order = np.argsort(p, kind="mergesort")
    adj = np.minimum(1.0, np.maximum.accumulate((m - np.arange(m)) * p[order]))
    out = np.empty(m)
    out[order] = adj
    return out


def secondary_family_tests(df: pd.DataFrame, spec: Spec | None = None, *, exclude: list[str] | None = None,
                           provenance: str | None = None) -> pd.DataFrame:
    """The four secondary members (AM-01 designs), each tested on its SECONDARY_TESTED
    contrast with DK SEs; Holm across the family."""
    spec = spec or Spec.load()
    rows = []
    for term in SECONDARY_TERMS:
        r = fit_dk(build_design(df, spec, secondary=term, exclude=exclude, provenance=provenance), spec)
        c = r.contrast(SECONDARY_TESTED[term])
        rows.append(dict(member=term, estimate=c["estimate"], se=c["se"], z=c["z"], p=c["p"]))
    out = pd.DataFrame(rows)
    out["p_holm"] = holm(out["p"].to_numpy())
    return out
