"""C4: M7 = HistGradientBoostingRegressor (spec forecast.models.M7; EXPLORATORY, P26/P27).

  features:   the 20 PRE_OPEN_FEATURES (all of them, sorted), plus a one-hot of the
              tickers seen in training, plus a seeded N(0,1) column `noise_N01` that
              the model generates itself (it is not a panel column, so it is not
              declared to the engine);
  fixed:      learning_rate 0.03, min_samples_leaf 100, l2_regularization 1.0,
              early_stopping=False SET EXPLICITLY (sklearn's default 'auto' turns early
              stopping on above 10,000 rows, with a random, non-temporal split);
  grid:       max_depth {2, 3} x max_iter {50, 100, 200, 400};
  tune:       each candidate is fit on the training rows before the last 250 unique
              training dates (ridge.tuning_split) and scored by MSE on those 250 dates;
              ties go to the simpler candidate (smaller depth, then fewer iterations);
              the winner is refit on the full training fold;
  seed:       random_state = the fold seed (inert here: no subsampling below 200,000
              rows and no early stopping).
Noise column: drawn from numpy's default_rng([fold seed, stream]) with stream 0 for
training rows and 1 for test rows, in row order. It depends only on the seed and the
row count, never on data values, so it cannot carry information across dates.
`predict` uses a `noise_N01` column if the caller supplies one (the permutation-
importance routine permutes it as the calibration column); otherwise it draws the
test noise itself. Tickers are fixed from the training rows; an unseen ticker raises.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from .. import schema
from ..forecast import FoldContext, ForecastModel
from .ridge import tuning_split

NOISE = "noise_N01"
GRID = tuple((d, n) for d in (2, 3) for n in (50, 100, 200, 400))
FIXED = {"learning_rate": 0.03, "min_samples_leaf": 100, "l2_regularization": 1.0, "early_stopping": False}
M7_SPEC = {"type": "HistGradientBoostingRegressor",
           "features": "PRE_OPEN allowlist + ticker one-hot + N(0,1) noise column",
           "grid": {"max_depth": [2, 3], "max_iter": [50, 100, 200, 400]},
           "fixed": {"learning_rate": 0.03, "min_samples_leaf": 100, "l2_regularization": 1.0,
                     "early_stopping": False},
           "tune": "last 250 dates of training fold", "status": "exploratory"}
TRAIN_STREAM, TEST_STREAM = 0, 1


def grid_key(depth: int, iters: int) -> str:
    """JSON-safe key for the per-candidate validation MSE (run registry, C6)."""
    return f"max_depth={int(depth)},max_iter={int(iters)}"


def draw_noise(seed: int, stream: int, n: int) -> np.ndarray:
    return np.random.default_rng([int(seed), int(stream)]).standard_normal(int(n))


class M7(ForecastModel):
    name = "M7"
    features = tuple(sorted(schema.PRE_OPEN_FEATURES))

    def __init__(self, grid=GRID):
        super().__init__()
        self.grid = tuple((int(d), int(n)) for d, n in grid)

    @staticmethod
    def estimator(depth: int, iters: int, seed: int) -> HistGradientBoostingRegressor:
        return HistGradientBoostingRegressor(max_depth=int(depth), max_iter=int(iters), random_state=int(seed),
                                             **FIXED)

    def _matrix(self, X: pd.DataFrame, noise: np.ndarray) -> np.ndarray:
        tk = X["ticker"].astype(str).to_numpy()
        unseen = sorted(set(np.unique(tk)) - set(self.tickers))
        if unseen:
            raise ValueError(f"tickers {unseen} not seen in training")
        onehot = [(tk == t).astype(float) for t in self.tickers]
        return np.column_stack([X[list(self.features)].to_numpy(dtype=float)] + onehot
                               + [np.asarray(noise, dtype=float)])

    def test_noise(self, n: int, ctx: FoldContext) -> np.ndarray:
        """The noise column `predict` uses for n test rows when none is supplied."""
        return draw_noise(ctx.seed, TEST_STREAM, n)

    def fit(self, X: pd.DataFrame, y: np.ndarray, ctx: FoldContext) -> None:
        y = np.asarray(y, dtype=float)
        self.tickers = tuple(np.unique(X["ticker"].astype(str).to_numpy()))
        Z = self._matrix(X, draw_noise(ctx.seed, TRAIN_STREAM, len(X)))
        if len(self.grid) == 1:
            best, scores = self.grid[0], {}
        else:
            val = tuning_split(X)
            scores = {}
            for d, n in self.grid:
                m = self.estimator(d, n, ctx.seed).fit(Z[~val], y[~val])
                scores[(d, n)] = float(np.mean((y[val] - m.predict(Z[val])) ** 2))
            best = min(self.grid, key=lambda g: (scores[g], g))
        self.model = self.estimator(best[0], best[1], ctx.seed).fit(Z, y)
        self.n_fit_rows = len(y)
        self.chosen = {"max_depth": best[0], "max_iter": best[1],
                       "val_mse": {grid_key(*g): s for g, s in scores.items()}}

    def predict(self, X: pd.DataFrame, ctx: FoldContext) -> np.ndarray:
        noise = X[NOISE].to_numpy(dtype=float) if NOISE in X.columns else self.test_noise(len(X), ctx)
        return self.model.predict(self._matrix(X, noise))
