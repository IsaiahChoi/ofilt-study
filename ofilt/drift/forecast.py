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
Importance (C6; spec forecast.importance, P26): for the models named in `importance`,
each fold's FITTED model also scores permuted copies of its own test frame inside the
engine (fitted models never leave it). One feature at a time is permuted by whole dates
within the fold's evaluation rows: dates are permuted among dates with the SAME set of
evaluated tickers, so every row's donor is an evaluated row of the same ticker and a date's
cross-section moves together. `repeats` from the spec; one date permutation per (fold,
repeat), shared by all features. A model with a `test_noise(n, ctx)` hook (M7) is also
calibrated against its noise column: the engine supplies that model's own test noise as
`noise_N01` (the predictions must be bit-identical to the unpermuted ones) and permutes it
like a feature. This is the one case in which a model frame holds a non-declared column.
The fold log stores per fold the baseline SSE and the permuted SSE per feature and repeat;
`importance_table` pools them. Every call appends one strict-JSON line to the run registry
(registry.record_run, P27) or raises; the fold log's attrs carry the run id.
Output: one tidy row per (date, ticker, model). The fold log has one row per (model,
fold), including `train_up` (C5): the target's up-counts on the fold's training rows,
per ticker and for the equal-weighted portfolio, which fctests reports as the
training-window base rate next to Pesaran-Timmermann.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import blind, registry, schema
from .inference import FORBIDDEN_TARGET_NAMES
from .spec import Spec

PRED_COLUMNS = ("date", "ticker", "fold", "train_end", "model", "y", "yhat")
NOISE_COLUMN = "noise_N01"          # schema.SYNTHETIC_FEATURES; M7's calibration column
IMPORTANCE_STREAM = 2               # rng stream for date permutations (M7 noise uses 0 and 1)
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


def _train_up(tr: np.ndarray, y: np.ndarray, tick: np.ndarray, dvals: np.ndarray) -> dict:
    """Up-counts of the target on one fold's TRAINING rows (C5, Pesaran-Timmermann base
    rate): {'by_ticker': {ticker: [n_up, n]}, 'portfolio': [n_up, n]} where the portfolio
    series is the mean target across the tickers present on each training date and 'up'
    means > 0. Plain ints, str keys: JSON-safe for the run registry."""
    by = {str(t): [int((y[tr & (tick == t)] > 0).sum()), int((tr & (tick == t)).sum())]
          for t in np.unique(tick[tr])}
    _, inv = np.unique(dvals[tr], return_inverse=True)
    pm = np.bincount(inv, weights=y[tr]) / np.bincount(inv)
    return {"by_ticker": by, "portfolio": [int((pm > 0).sum()), int(pm.size)]}


def donor_index(dates: np.ndarray, tickers: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Whole-date permutation of evaluation rows: dates are permuted within groups of dates
    that have the same set of tickers; row (d, i) takes its donor from row (pi(d), i)."""
    dates = np.asarray(dates, dtype="datetime64[ns]")
    tickers = np.asarray(tickers).astype(str)
    rows: dict = {}
    for k, (d, t) in enumerate(zip(dates, tickers)):
        if t in rows.setdefault(d, {}):
            raise ValueError("duplicate (date, ticker) in evaluation rows")
        rows[d][t] = k
    groups: dict = {}
    for d in sorted(rows):
        groups.setdefault(tuple(sorted(rows[d])), []).append(d)
    donor = np.arange(len(dates))
    for g in sorted(groups):
        ds = groups[g]
        for d, dd in zip(ds, [ds[j] for j in rng.permutation(len(ds))]):
            for t in g:
                donor[rows[d][t]] = rows[dd][t]
    return donor


def _predict_checked(m, X, ctx, name, n) -> np.ndarray:
    yhat = np.asarray(m.predict(X, ctx), dtype=float)
    if yhat.shape != (n,) or not np.isfinite(yhat).all():
        raise ValueError(f"{name}: bad predictions in fold {ctx.fold}")
    return yhat


def _fold_importance(m, X: pd.DataFrame, y: np.ndarray, yhat: np.ndarray, ctx: FoldContext,
                     feats: list, repeats: int, name: str) -> dict:
    cols = list(feats)
    noise_fn = getattr(m, "test_noise", None)
    if callable(noise_fn):
        X = X.assign(**{NOISE_COLUMN: np.asarray(noise_fn(len(X), ctx), dtype=float)})
        if not np.array_equal(_predict_checked(m, X, ctx, name, len(X)), yhat):
            raise ValueError(f"{name}: supplied noise column does not reproduce the predictions")
        cols.append(NOISE_COLUMN)
    dates, tick = X["date"].to_numpy(dtype="datetime64[ns]"), X["ticker"].to_numpy()
    sse = {c: [] for c in cols}
    for r in range(repeats):
        donor = donor_index(dates, tick, np.random.default_rng([ctx.seed, IMPORTANCE_STREAM, r]))
        for c in cols:
            Xp = X.copy()
            Xp[c] = X[c].to_numpy()[donor]
            sse[c].append(float(((y - _predict_checked(m, Xp, ctx, name, len(X))) ** 2).sum()))
    return {"sse_base": float(((y - yhat) ** 2).sum()), "sse_perm": sse, "repeats": int(repeats),
            "noise_column": NOISE_COLUMN if callable(noise_fn) else None}


def importance_table(folds: pd.DataFrame, model: str) -> pd.DataFrame:
    """Pooled permutation importance: per repeat r, dMSE_r = sum_f (SSE_perm,f,r - SSE_base,f)
    / sum_f n_test,f over the folds that recorded importance; mean, sd (ddof 1), min, max over
    repeats; rank by mean (1 = most important). exceeds_noise = mean > max_r dMSE_r of the
    noise column (None when the model has no noise column)."""
    fl = folds.loc[(folds["model"] == model) & folds["importance"].notna()]
    if fl.empty:
        raise ValueError(f"no importance recorded for {model!r}")
    n = int(fl["n_test"].sum())
    imp = list(fl["importance"])
    cols = list(imp[0]["sse_perm"])
    R = imp[0]["repeats"]
    d = {c: np.array([sum(i["sse_perm"][c][r] - i["sse_base"] for i in imp) for r in range(R)]) / n for c in cols}
    noise = imp[0]["noise_column"]
    out = pd.DataFrame({"feature": cols, "mean_dmse": [d[c].mean() for c in cols],
                        "sd_dmse": [d[c].std(ddof=1) for c in cols], "min_dmse": [d[c].min() for c in cols],
                        "max_dmse": [d[c].max() for c in cols], "is_noise": [c == noise for c in cols]})
    out["exceeds_noise"] = [None if noise is None else bool(v > d[noise].max()) for v in out["mean_dmse"]]
    out = out.sort_values("mean_dmse", ascending=False, kind="mergesort").reset_index(drop=True)
    out.insert(1, "rank", np.arange(1, len(out) + 1))
    out.attrs = {"model": model, "repeats": int(R), "n_rows": n, "n_folds": int(len(fl))}
    return out


def walk_forward(df: pd.DataFrame, models: dict, spec: Spec | None = None, *, target: str = "abn_oc",
                 provenance: str | None = None, seed: int | None = None, importance=None,
                 output_path: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """models: {name: zero-argument factory returning a fresh ForecastModel}.
    importance: names of models (in `models`) to score by permutation importance.
    Returns (predictions with PRED_COLUMNS, per-fold log); appends one registry line."""
    prov = blind.require_unblinded(df, provenance=provenance)
    spec = spec or Spec.load()
    imp_set = set() if importance is None else set(importance)
    if not imp_set <= set(models):
        raise ValueError(f"importance names unknown models: {sorted(imp_set - set(models))}")
    repeats = int(spec.value("forecast.importance.repeats"))
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
    tick = df["ticker"].astype(str).to_numpy()
    # C5: training-window base rates for Pesaran-Timmermann (target only; identical for
    # every model in the call, because the training rows are).
    train_up = [_train_up(train_ok & (dvals < np.datetime64(dates[s])), y_all, tick, dvals) for s in starts]
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
            imp = None
            if te.any():
                Xte = F.loc[te].reset_index(drop=True)
                yhat = _predict_checked(m, Xte, ctx, name, int(te.sum()))
                if name in imp_set:
                    imp = _fold_importance(m, Xte, y_all[te], yhat, ctx, feats, repeats, name)
                preds.append(pd.DataFrame({"date": df.loc[te, "date"].to_numpy(), "ticker": df.loc[te, "ticker"].to_numpy(),
                                           "fold": f, "train_end": dates[s - 1], "model": name,
                                           "y": y_all[te], "yhat": yhat}))
            folds.append(dict(model=name, fold=f, train_end=dates[s - 1], test_start=t0, test_end=t1,
                              n_train_dates=ctx.n_train_dates, n_train=int(tr.sum()), n_test=int(te.sum()),
                              chosen=dict(m.chosen), train_up=train_up[f], importance=imp))
    out = pd.concat(preds, ignore_index=True)[list(PRED_COLUMNS)] if preds else pd.DataFrame(columns=PRED_COLUMNS)
    out.attrs = {"provenance": prov, "target": target}
    fold_log = pd.DataFrame(folds)
    run_id = registry.record_run(df=df, models=models, spec=spec, provenance=prov, target=target, seed=seed,
                                 fold_log=fold_log, importance=sorted(imp_set), output_path=output_path)
    fold_log.attrs = {"run_id": run_id, "provenance": prov}
    return out, fold_log
