"""Walk-forward forecasting engine (C1). Spec `forecast`: expanding scheme, first
forecast after `min_train_dates` (500) dates, refit every `refit_every_dates` (21),
pooled across tickers, scaling in-fold only, thresholds past-only.

Information firewall (enforced here, not trusted to models):
  * a model DECLARES its features; they must pass schema.assert_features_allowed
    and are built only through schema.select_features (the production path);
  * fit(X_train, y_train, ctx) sees training rows dated strictly before the fold's
    first test date; predict(X_test, ctx) never receives the target;
  * every model frame holds exactly {date, ticker} + declared features.
Samples:
  * training rows: excl_inference == False (past event days are known at training
    time; the spec defines no separate training exclusion -- Flag 11), target and
    features non-missing;
  * evaluation rows: excl_forecast_eval == False (TANSHIN D, D+1; news D+1), target
    and features non-missing. Unscheduled news day D therefore stays in evaluation.
Fold geometry (C1 correction): an ELIGIBLE training date has at least one eligible
training row. The first test date is the first panel date after the 500th eligible
date, so fold 0 trains on exactly 500 eligible dates (beta warm-up dates do not
count); folds then advance every 21 PANEL dates and train on all eligible rows dated
before the fold's first test date. All models in one call share the fold geometry,
the training rows and the evaluation rows: the sample requires the feature sources
of EVERY model in the call, so paired comparisons (CW, DM) use identical rows.
Output: one tidy row per (date, ticker, model).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import blind, schema
from .inference import FORBIDDEN_TARGET_NAMES
from .spec import Spec

PRED_COLUMNS = ("date", "ticker", "fold", "train_end", "model", "y", "yhat")
REQUIRED_MASKS = ("excl_inference", "excl_forecast_eval")


@dataclass(frozen=True)
class FoldContext:
    fold: int
    train_end: pd.Timestamp       # last date with a training row allowed (strictly < first test date)
    test_start: pd.Timestamp
    n_train_dates: int
    spec: Spec
    seed: int


@dataclass
class FoldScaler:
    """In-fold standardisation: moments from TRAINING rows only (ddof=0; sd 0 -> 1)."""
    mean: np.ndarray = field(default_factory=lambda: np.zeros(0))
    sd: np.ndarray = field(default_factory=lambda: np.ones(0))

    @classmethod
    def fit(cls, X: np.ndarray) -> "FoldScaler":
        X = np.asarray(X, dtype=float)
        sd = X.std(axis=0)
        return cls(X.mean(axis=0), np.where(sd > 0, sd, 1.0))

    def transform(self, X: np.ndarray) -> np.ndarray:
        return (np.asarray(X, dtype=float) - self.mean) / self.sd


class ForecastModel:
    """Interface. Subclasses set `name` and `features`, implement fit/predict, and may
    fill `self.chosen` (per-fold hyperparameters for the registry)."""
    name = "base"
    features: tuple[str, ...] = ()

    def __init__(self):
        self.chosen: dict = {}

    def fit(self, X: pd.DataFrame, y: np.ndarray, ctx: FoldContext) -> None:
        raise NotImplementedError

    def predict(self, X: pd.DataFrame, ctx: FoldContext) -> np.ndarray:
        raise NotImplementedError


def fold_starts(dates: pd.DatetimeIndex, eligible_dates, spec: Spec) -> list[int]:
    """Panel-date positions of the fold starts. The first test date is the first panel
    date after the min_train_dates-th ELIGIBLE training date (a date with at least one
    eligible training row), so fold 0 trains on exactly min_train_dates eligible dates;
    later folds advance every refit_every_dates PANEL dates (C1 correction)."""
    m, k = int(spec.value("forecast.min_train_dates")), int(spec.value("forecast.refit_every_dates"))
    dates = pd.DatetimeIndex(dates)
    elig = pd.DatetimeIndex(np.sort(pd.to_datetime(pd.Series(eligible_dates)).unique()))
    if len(elig) < m:
        raise ValueError(f"need {m} eligible training dates for a first forecast, have {len(elig)}")
    s0 = int(dates.searchsorted(elig[m - 1], side="right"))
    if s0 >= len(dates):
        raise ValueError("no panel dates left after the training warm-up")
    return list(range(s0, len(dates), k))


def walk_forward(df: pd.DataFrame, models: dict, spec: Spec | None = None, *, target: str = "abn_oc",
                 provenance: str | None = None, seed: int | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """models: {name: zero-argument factory returning a fresh ForecastModel}.
    Returns (predictions with PRED_COLUMNS, per-fold log)."""
    prov = blind.require_unblinded(df, provenance=provenance)
    spec = spec or Spec.load()
    if not isinstance(target, str) or target in FORBIDDEN_TARGET_NAMES or target not in df.columns:
        raise ValueError(f"bad forecast target {target!r}")
    missing = [c for c in REQUIRED_MASKS + ("date", "ticker") if c not in df.columns]
    if missing:
        raise ValueError(f"panel lacks {missing}")
    seed = spec.seed if seed is None else int(seed)
    dates = pd.DatetimeIndex(np.sort(df["date"].unique()))
    k = int(spec.value("forecast.refit_every_dates"))
    y_all = df[target].to_numpy(dtype=float)
    feats_by = {}
    for name, factory in models.items():
        feats_by[name] = list(factory().features)
        schema.assert_features_allowed(feats_by[name])
    # One sample for ALL models in the call (paired comparisons need identical rows):
    # finite target and every model's feature sources present.
    need = sorted(set().union(*(schema.feature_sources(f) for f in feats_by.values())))
    ok = np.isfinite(y_all) & df[need].notna().all(axis=1).to_numpy()
    train_ok = ok & ~df["excl_inference"].astype(bool).to_numpy()
    eval_ok = ok & ~df["excl_forecast_eval"].astype(bool).to_numpy()
    dvals = df["date"].to_numpy(dtype="datetime64[ns]")
    elig_dates = pd.DatetimeIndex(np.unique(dvals[train_ok]))
    starts = fold_starts(dates, elig_dates, spec)
    preds, folds = [], []
    for name, factory in models.items():
        feats = feats_by[name]
        base = schema.select_features(df, feats) if feats else pd.DataFrame(index=df.index)
        F = pd.concat([df[["date", "ticker"]], base], axis=1)
        for f, s in enumerate(starts):
            t0, t1 = dates[s], dates[min(s + k, len(dates)) - 1]
            tr = train_ok & (dvals < np.datetime64(t0))
            te = eval_ok & (dvals >= np.datetime64(t0)) & (dvals <= np.datetime64(t1))
            ctx = FoldContext(fold=f, train_end=dates[s - 1], test_start=t0,
                              n_train_dates=int(elig_dates.searchsorted(t0)), spec=spec, seed=seed + 1000 * f)
            m = factory()
            m.fit(F.loc[tr].reset_index(drop=True), y_all[tr], ctx)
            if te.any():
                yhat = np.asarray(m.predict(F.loc[te].reset_index(drop=True), ctx), dtype=float)
                if yhat.shape != (int(te.sum()),) or not np.isfinite(yhat).all():
                    raise ValueError(f"{name}: bad predictions in fold {f}")
                preds.append(pd.DataFrame({"date": df.loc[te, "date"].to_numpy(), "ticker": df.loc[te, "ticker"].to_numpy(),
                                           "fold": f, "train_end": dates[s - 1], "model": name,
                                           "y": y_all[te], "yhat": yhat}))
            folds.append(dict(model=name, fold=f, train_end=dates[s - 1], test_start=t0, test_end=t1,
                              n_train_dates=ctx.n_train_dates, n_train=int(tr.sum()), n_test=int(te.sum()),
                              chosen=dict(m.chosen)))
    out = pd.concat(preds, ignore_index=True)[list(PRED_COLUMNS)] if preds else pd.DataFrame(columns=PRED_COLUMNS)
    out.attrs = {"provenance": prov, "target": target}
    return out, pd.DataFrame(folds)
