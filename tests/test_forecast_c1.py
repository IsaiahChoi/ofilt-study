import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import forecast as F  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402


def masked_panel(n_dates=700, seed=0):
    df = S.synthetic_panel(n_dates, b=0.2, seed=seed, p_excl=0.05)
    rng = np.random.default_rng(seed + 1)
    df["news_flag"] = (rng.random(len(df)) < 0.03).astype(int)
    df["excl_inference"] = (df.earn_flag == 1) | (df.news_flag == 1)
    df["excl_forecast_eval"] = df.earn_flag == 1                # news day D stays in evaluation
    return B.mark_synthetic(df)


def spy_factory(log, features=("usdjpy_ret", "spy_oc", "long_window")):
    class Spy(F.ForecastModel):
        name = "spy"

        def __init__(self):
            super().__init__()
            self.features = features

        def fit(self, X, y, ctx):
            log.append(("fit", ctx.fold, X["date"].max(), tuple(X.columns), len(y), ctx))
            self.mu = float(np.mean(y))
            self.chosen = {"mu": self.mu}

        def predict(self, X, ctx):
            log.append(("predict", ctx.fold, X["date"].min(), tuple(X.columns), len(X), ctx))
            return np.full(len(X), self.mu)
    return Spy


class TestWalkForward(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()
        self.df = masked_panel()
        self.dates = pd.DatetimeIndex(np.sort(self.df.date.unique()))

    def test_fold_geometry_and_firewall(self):
        log = []
        pred, folds = F.walk_forward(self.df, {"spy": spy_factory(log)}, self.spec)
        starts = list(range(500, 700, 21))
        self.assertEqual(list(folds.fold), list(range(len(starts))))
        fits = [e for e in log if e[0] == "fit"]
        prds = {e[1]: e for e in log if e[0] == "predict"}
        for (_, f, train_max, cols, n_tr, ctx), s in zip(fits, starts):
            t0 = self.dates[s]
            self.assertLess(train_max, t0)                                       # strictly earlier
            self.assertEqual(ctx.train_end, self.dates[s - 1])
            self.assertEqual(ctx.n_train_dates, s)
            self.assertEqual(set(cols), {"date", "ticker", "usdjpy_ret", "spy_oc", "long_window"})
            self.assertGreaterEqual(prds[f][2], t0)
            self.assertNotIn("abn_oc", prds[f][3])                              # no target at predict
            elig = (self.df.date < t0) & ~self.df.excl_inference
            self.assertEqual(n_tr, int(elig.sum()))                              # training mask applied
        g = pred.groupby("fold").date
        for f, s in enumerate(starts):
            self.assertEqual(g.min()[f], self.dates[s])
            self.assertEqual(g.max()[f], self.dates[min(s + 21, 700) - 1])
        self.assertEqual(tuple(pred.columns), F.PRED_COLUMNS)

    def test_eval_mask_and_completeness(self):
        pred, _ = F.walk_forward(self.df, {"spy": spy_factory([])}, self.spec)
        test = self.df[self.df.date >= self.dates[500]]
        keep = test[~test.excl_forecast_eval]
        self.assertEqual(len(pred), len(keep))
        self.assertFalse(pred.merge(test[test.excl_forecast_eval], on=["date", "ticker"]).shape[0])
        kept_news = test[test.excl_inference & ~test.excl_forecast_eval]
        self.assertGreater(len(kept_news), 0)
        self.assertEqual(pred.merge(kept_news, on=["date", "ticker"]).shape[0], len(kept_news))
        self.assertFalse(pred.duplicated(["date", "ticker", "model"]).any())
        self.assertTrue(np.array_equal(pred.y.to_numpy(), keep.abn_oc.to_numpy()))

    def test_allowlist_guards_and_determinism(self):
        for bad in (("ao_gap_adj",), ("y_oc",), ("abn_oc",), ("open",)):
            with self.subTest(bad=bad), self.assertRaises(Exception):
                F.walk_forward(self.df.assign(**{c: 0.0 for c in bad}), {"m": spy_factory([], bad)}, self.spec)
        real = self.df.copy()
        real.attrs = {"provenance": "dev_real"}
        with self.assertRaises(B.BlindingError):
            F.walk_forward(real, {"m": spy_factory([])}, self.spec)
        with self.assertRaises(ValueError):
            F.walk_forward(self.df, {"m": spy_factory([])}, self.spec, target="usdjpy_ret")
        with self.assertRaises(ValueError):
            F.walk_forward(self.df.drop(columns=["excl_forecast_eval"]), {"m": spy_factory([])}, self.spec)
        with self.assertRaises(ValueError):
            F.walk_forward(masked_panel(500), {"m": spy_factory([])}, self.spec)   # needs > 500 dates
        a, fa = F.walk_forward(self.df, {"m": spy_factory([])}, self.spec)
        b, fb = F.walk_forward(self.df, {"m": spy_factory([])}, self.spec)
        pd.testing.assert_frame_equal(a, b)
        self.assertEqual(list(fa.chosen), list(fb.chosen))

    def test_fold_scaler_uses_training_moments_only(self):
        rng = np.random.default_rng(0)
        Xtr, Xte = rng.normal(3, 2, (500, 3)), rng.normal(-5, 9, (100, 3))
        sc = F.FoldScaler.fit(Xtr)
        self.assertTrue(np.allclose(sc.transform(Xtr).mean(axis=0), 0) and np.allclose(sc.transform(Xtr).std(axis=0), 1))
        self.assertTrue(np.allclose(sc.transform(Xte), (Xte - Xtr.mean(axis=0)) / Xtr.std(axis=0)))
        const = F.FoldScaler.fit(np.ones((10, 2)))
        self.assertTrue(np.array_equal(const.sd, np.ones(2)))

    def test_fold_starts(self):
        self.assertEqual(F.fold_starts(543, self.spec), [500, 521, 542])
        with self.assertRaises(ValueError):
            F.fold_starts(500, self.spec)


if __name__ == "__main__":
    unittest.main()
