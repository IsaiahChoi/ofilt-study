"""C2: M0 (zero), M1 (prevailing mean per ticker), M2, M3 (pooled OLS with ticker FE).

M2/M3 use the inference design's column layout: fe[t] dummies (NO global intercept),
then the common FX terms in spec order, then ticker-specific control slopes
(spy_oc:t, copx_oc:t). M3's design is therefore the primary inference design, so its
in-fold coefficients equal inference.pooled_ols on the same rows (tested), and CW of
M3 vs M2 is the real-time counterpart of H1. No in-fold scaling is needed: with the
ticker FE spanning the intercept, OLS predictions are invariant to affine rescaling
of the regressors. Tickers are fixed from the TRAINING rows; an unseen test ticker
raises (fail closed); a rank-deficient training design raises.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..forecast import FoldContext, ForecastModel

CONTROLS = ("spy_oc", "copx_oc")
MODEL_SPEC_STRINGS = {"M0": "zero", "M1": "prevailing_mean_per_ticker",
                      "M2": "FE + ticker-specific spy_oc, copx_oc + eurusd_ret", "M3": "M2 + usdjpy_ret"}


def linear_design(X: pd.DataFrame, tickers: tuple[str, ...], common, ticker_specific=CONTROLS) -> np.ndarray:
    tk = X["ticker"].astype(str).to_numpy()
    unseen = sorted(set(np.unique(tk)) - set(tickers))
    if unseen:
        raise ValueError(f"tickers {unseen} not seen in training")
    cols = [(tk == t).astype(float) for t in tickers]
    cols += [X[c].to_numpy(dtype=float) for c in common]
    for c in ticker_specific:
        for t in tickers:
            cols.append(X[c].to_numpy(dtype=float) * (tk == t))
    return np.column_stack(cols)


class M0(ForecastModel):
    name, features = "M0", ()

    def fit(self, X: pd.DataFrame, y: np.ndarray, ctx: FoldContext) -> None:
        pass

    def predict(self, X: pd.DataFrame, ctx: FoldContext) -> np.ndarray:
        return np.zeros(len(X))


class M1(ForecastModel):
    """Prevailing (training-sample) mean of the target, per ticker."""
    name, features = "M1", ()

    def fit(self, X: pd.DataFrame, y: np.ndarray, ctx: FoldContext) -> None:
        s = pd.Series(np.asarray(y, dtype=float)).groupby(X["ticker"].astype(str).to_numpy()).mean()
        self.means = s.to_dict()

    def predict(self, X: pd.DataFrame, ctx: FoldContext) -> np.ndarray:
        tk = X["ticker"].astype(str)
        unseen = sorted(set(tk) - set(self.means))
        if unseen:
            raise ValueError(f"tickers {unseen} not seen in training")
        return tk.map(self.means).to_numpy(dtype=float)


class _PooledOLS(ForecastModel):
    common: tuple[str, ...] = ()

    def fit(self, X: pd.DataFrame, y: np.ndarray, ctx: FoldContext) -> None:
        self.tickers = tuple(np.unique(X["ticker"].astype(str).to_numpy()))
        D = linear_design(X, self.tickers, self.common)
        if np.linalg.matrix_rank(D) < D.shape[1]:
            raise ValueError(f"{self.name}: rank-deficient training design in fold {ctx.fold}")
        self.coef = np.linalg.lstsq(D, np.asarray(y, dtype=float), rcond=None)[0]

    def predict(self, X: pd.DataFrame, ctx: FoldContext) -> np.ndarray:
        return linear_design(X, self.tickers, self.common) @ self.coef


class M2(_PooledOLS):
    name, common = "M2", ("eurusd_ret",)
    features = ("eurusd_ret",) + CONTROLS


class M3(_PooledOLS):
    name, common = "M3", ("usdjpy_ret", "eurusd_ret")
    features = ("usdjpy_ret", "eurusd_ret") + CONTROLS


# ------------------------------------------------------------------ M4 (C3)
M4_EXTRA = ("long_window", "jumpshare", "highrv", "e:long_window", "e:jumpshare", "e:highrv", "e_neg")
M4_FEATURES = ("usdjpy_ret", "eurusd_ret") + CONTROLS + ("long_window", "jumpshare", "rv_per_bar", "e_neg")


def rv_threshold(X: pd.DataFrame) -> float:
    """Median of rv_per_bar over the frame's unique dates (one value per date): the
    'expanding past median' when X is a training fold."""
    per_date = X.groupby("date")["rv_per_bar"].first()
    if not np.isfinite(per_date).all() or per_date.empty:
        raise ValueError("rv_per_bar must be finite on every training date")
    return float(per_date.median())


def m4_augment(X: pd.DataFrame, thr: float) -> pd.DataFrame:
    e = X["usdjpy_ret"].to_numpy(dtype=float)
    hr = (X["rv_per_bar"].to_numpy(dtype=float) > thr).astype(float)
    return X.assign(highrv=hr, **{"e:long_window": e * X["long_window"].to_numpy(dtype=float),
                                  "e:jumpshare": e * X["jumpshare"].to_numpy(dtype=float), "e:highrv": e * hr})


class M4(_PooledOLS):
    """M3 + 1[long] + jumpshare + highrv + e*1[long] + e*jumpshare + e*highrv + min(e,0)
    (spec AM-01); highrv threshold = training-fold date median of rv_per_bar, frozen in fit."""
    name = "M4"
    common = ("usdjpy_ret", "eurusd_ret") + M4_EXTRA
    features = M4_FEATURES

    def fit(self, X: pd.DataFrame, y: np.ndarray, ctx: FoldContext) -> None:
        self.thr = rv_threshold(X)
        self.chosen = {"rv_threshold": self.thr}
        super().fit(m4_augment(X, self.thr), y, ctx)

    def predict(self, X: pd.DataFrame, ctx: FoldContext) -> np.ndarray:
        return super().predict(m4_augment(X, self.thr), ctx)
