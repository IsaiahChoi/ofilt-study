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
