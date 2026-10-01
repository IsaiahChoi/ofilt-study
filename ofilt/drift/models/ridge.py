"""C3: M5 = ridge on the M4 design (spec forecast.models.M5).

  fe:         unpenalized via in-fold within-ticker demeaning (ticker means of y and of
              every slope column, from the rows being fit);
  scaling:    FoldScaler on the demeaned slope columns (in-fold);
  alpha_grid: n_rows * [1e-4, 1e-3, 1e-2, 1e-1, 1], n_rows = rows in the fit;
  tune:       candidates are fit on training rows before the last 250 unique training
              dates (each with its own threshold, means and scaling) and scored by MSE on
              those last 250 dates; the winner is refit on the full training fold.
Anchors (tested): alpha = 0 reproduces M4 (OLS with FE); alpha -> inf reproduces M1.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..forecast import FoldContext, FoldScaler, ForecastModel
from .linear import M4, linear_design, m4_augment, rv_threshold

ALPHA_MULTS = (1e-4, 1e-3, 1e-2, 1e-1, 1.0)
TUNE_DATES = 250
M5_SPEC = {"type": "ridge", "design": "M4", "fe": "unpenalized via in-fold within-ticker demeaning",
           "alpha_grid": "n_train * [1e-4,1e-3,1e-2,1e-1,1]", "tune": "last 250 dates of training fold"}


def tuning_split(X: pd.DataFrame, n_val_dates: int = TUNE_DATES) -> np.ndarray:
    """Boolean mask of validation rows: the last n_val_dates unique dates of X."""
    d = np.sort(X["date"].unique())
    if len(d) <= n_val_dates:
        raise ValueError(f"need more than {n_val_dates} training dates to tune, have {len(d)}")
    return (X["date"] >= d[-n_val_dates]).to_numpy()


class M5(ForecastModel):
    name, features = "M5", M4.features

    def __init__(self, alpha_mults=ALPHA_MULTS):
        super().__init__()
        self.alpha_mults = tuple(float(a) for a in alpha_mults)

    @staticmethod
    def _fit_core(X: pd.DataFrame, y: np.ndarray, mult: float) -> dict:
        thr = rv_threshold(X)
        tickers = tuple(np.unique(X["ticker"].astype(str).to_numpy()))
        nt = len(tickers)
        S = linear_design(m4_augment(X, thr), tickers, M4.common)[:, nt:]          # slope columns only
        tk = X["ticker"].astype(str).to_numpy()
        S_mean = {t: S[tk == t].mean(axis=0) for t in tickers}
        y = np.asarray(y, dtype=float)
        y_mean = {t: float(y[tk == t].mean()) for t in tickers}
        Sd = S - np.vstack([S_mean[t] for t in tk])
        yd = y - np.array([y_mean[t] for t in tk])
        sc = FoldScaler.fit(Sd)
        Z = sc.transform(Sd)
        alpha = mult * len(y)
        beta = np.linalg.solve(Z.T @ Z + alpha * np.eye(Z.shape[1]), Z.T @ yd)
        return dict(thr=thr, tickers=tickers, S_mean=S_mean, y_mean=y_mean, sc=sc, beta=beta, alpha=alpha)

    @staticmethod
    def _predict_core(st: dict, X: pd.DataFrame) -> np.ndarray:
        nt = len(st["tickers"])
        S = linear_design(m4_augment(X, st["thr"]), st["tickers"], M4.common)[:, nt:]
        tk = X["ticker"].astype(str).to_numpy()
        Z = st["sc"].transform(S - np.vstack([st["S_mean"][t] for t in tk]))
        return np.array([st["y_mean"][t] for t in tk]) + Z @ st["beta"]

    def fit(self, X: pd.DataFrame, y: np.ndarray, ctx: FoldContext) -> None:
        y = np.asarray(y, dtype=float)
        if len(self.alpha_mults) == 1:
            best, scores = self.alpha_mults[0], {}
        else:
            val = tuning_split(X)
            Xi, Xv = X.loc[~val].reset_index(drop=True), X.loc[val].reset_index(drop=True)
            scores = {}
            for m in self.alpha_mults:
                st = self._fit_core(Xi, y[~val], m)
                scores[m] = float(np.mean((y[val] - self._predict_core(st, Xv)) ** 2))
            best = min(self.alpha_mults, key=lambda m: (scores[m], m))
        self.state = self._fit_core(X, y, best)
        self.chosen = {"alpha_mult": best, "alpha": self.state["alpha"], "val_mse": scores,
                       "rv_threshold": self.state["thr"]}

    def predict(self, X: pd.DataFrame, ctx: FoldContext) -> np.ndarray:
        return self._predict_core(self.state, X)
