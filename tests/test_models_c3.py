import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ofilt.drift import forecast as F  # noqa: E402
from ofilt.drift import schema  # noqa: E402
from ofilt.drift import spec as SP  # noqa: E402
from ofilt.drift.models import M1, M3, M4, M5, M5_SPEC  # noqa: E402
from ofilt.drift.models.ridge import tuning_split  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402
from test_forecast_c1 import masked_panel  # noqa: E402
from test_models_c2 import ctx  # noqa: E402


class TestM4M5(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()
        self.df = masked_panel(800, seed=33)
        cut = np.sort(self.df.date.unique())[600]
        tr = (self.df.date < cut) & ~self.df.excl_inference
        self.train, self.test = self.df[tr].reset_index(drop=True), self.df[self.df.date >= cut].reset_index(drop=True)
        self.c = ctx(self.spec)
        self.y = self.train.abn_oc.to_numpy()

    def frame(self, d, feats=M4.features):
        return pd.concat([d[["date", "ticker"]], schema.select_features(d, list(feats))], axis=1)

    def test_m4_direct_ols_and_threshold(self):
        m = M4(); m.fit(self.frame(self.train), self.y, self.c)
        Xf = self.frame(self.train)
        thr = Xf.groupby("date").rv_per_bar.first().median()
        self.assertEqual(m.thr, thr)
        e, tk, T = Xf.usdjpy_ret.to_numpy(), Xf.ticker.to_numpy(), ("5706", "5711", "5713")
        hr = (Xf.rv_per_bar.to_numpy() > thr).astype(float)
        lw, js = Xf.long_window.to_numpy(), Xf.jumpshare.to_numpy()
        X = np.column_stack([(tk == t) * 1.0 for t in T]
                            + [e, Xf.eurusd_ret, lw, js, hr, e * lw, e * js, e * hr, np.minimum(e, 0)]
                            + [Xf[c].to_numpy() * (tk == t) for c in ("spy_oc", "copx_oc") for t in T])
        self.assertTrue(np.array_equal(Xf.e_neg.to_numpy(), np.minimum(e, 0)))
        ref = np.linalg.lstsq(X, self.y, rcond=None)[0]
        self.assertEqual(len(m.coef), 18)
        self.assertLess(np.max(np.abs(m.coef - ref)), 1e-12)
        Xt = self.frame(self.test)
        p1 = m.predict(Xt, self.c)
        Xt2 = Xt.copy(); Xt2["rv_per_bar"] = Xt2.rv_per_bar * 0 + 1.0              # test values cannot move the threshold
        m.predict(Xt2, self.c)
        self.assertEqual(m.thr, thr)
        self.assertTrue(np.isfinite(p1).all())

    def test_m5_anchors(self):
        Xtr, Xte = self.frame(self.train), self.frame(self.test)
        m4 = M4(); m4.fit(Xtr, self.y, self.c)
        r0 = M5(alpha_mults=(0.0,)); r0.fit(Xtr, self.y, self.c)
        self.assertLess(np.max(np.abs(r0.predict(Xte, self.c) - m4.predict(Xte, self.c))), 1e-10)   # alpha 0 == M4
        rinf = M5(alpha_mults=(1e12,)); rinf.fit(Xtr, self.y, self.c)
        m1 = M1(); m1.fit(Xtr[["date", "ticker"]], self.y, self.c)
        self.assertLess(np.max(np.abs(rinf.predict(Xte, self.c) - m1.predict(Xte, self.c))), 1e-9)  # alpha inf == M1

    def test_m5_tuning(self):
        Xtr = self.frame(self.train)
        val = tuning_split(Xtr)
        d = np.sort(Xtr.date.unique())
        self.assertEqual(set(Xtr.date[val]), set(d[-250:]))
        self.assertLess(Xtr.date[~val].max(), Xtr.date[val].min())
        m = M5(); m.fit(Xtr, self.y, self.c)
        self.assertIn(m.chosen["alpha_mult"], (1e-4, 1e-3, 1e-2, 1e-1, 1.0))
        self.assertEqual(set(m.chosen["val_mse"]), {1e-4, 1e-3, 1e-2, 1e-1, 1.0})
        self.assertEqual(m.chosen["alpha_mult"], min(m.chosen["val_mse"], key=m.chosen["val_mse"].get))
        self.assertAlmostEqual(m.chosen["alpha"], m.chosen["alpha_mult"] * len(self.y))
        # the chosen candidate's validation MSE is reproducible by an independent refit on the inner rows
        st = M5._fit_core(Xtr.loc[~val].reset_index(drop=True), self.y[~val], m.chosen["alpha_mult"])
        mse = np.mean((self.y[val] - M5._predict_core(st, Xtr.loc[val].reset_index(drop=True))) ** 2)
        self.assertAlmostEqual(mse, m.chosen["val_mse"][m.chosen["alpha_mult"]], places=14)
        with self.assertRaises(ValueError):
            tuning_split(Xtr[Xtr.date <= d[200]])

    def test_spec_strings(self):
        self.assertEqual(self.spec.raw("forecast.models.M4"), SP.M4_DEF)
        self.assertEqual(self.spec.raw("forecast.models.M5"), M5_SPEC)
        self.assertEqual(set(M4.features) - set(M3.features), {"long_window", "jumpshare", "rv_per_bar", "e_neg"})
        schema.assert_features_allowed(list(M4.features))

    def test_m3_m4_m5_in_engine(self):
        pred, folds = F.walk_forward(self.df, {"M3": M3, "M4": M4, "M5": M5}, self.spec)
        self.assertEqual(sorted(pred.model.unique()), ["M3", "M4", "M5"])
        f4 = folds[folds.model == "M4"].reset_index(drop=True)
        dates = np.sort(self.df.date.unique())
        for _, r in f4.iterrows():                                                # threshold is past-only
            past = self.df[(self.df.date < r.test_start) & ~self.df.excl_inference]
            pb = (past.usdjpy_rv / past.usdjpy_bars).groupby(past.date).first().median()
            self.assertAlmostEqual(r.chosen["rv_threshold"], pb, places=15)
        self.assertTrue(folds[folds.model == "M5"].chosen.map(lambda c: "alpha_mult" in c).all())
        self.assertTrue(np.isfinite(pred.yhat).all())
        self.assertGreater(len(dates), 700)


if __name__ == "__main__":
    unittest.main()
