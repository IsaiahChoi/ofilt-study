import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ofilt.drift import forecast as F  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import schema  # noqa: E402
from ofilt.drift.models import REGISTRY, M0, M1, M2, M3, MODEL_SPEC_STRINGS  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402
from test_forecast_c1 import masked_panel  # noqa: E402


def ctx(spec):
    return F.FoldContext(fold=0, train_end=pd.Timestamp("2016-01-01"), test_start=pd.Timestamp("2016-01-04"),
                         n_train_dates=500, spec=spec, seed=0)


class TestModels(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()
        self.df = masked_panel(800, seed=21)
        dates = np.sort(self.df.date.unique())
        cut = dates[600]
        tr = (self.df.date < cut) & ~self.df.excl_inference
        self.train, self.test = self.df[tr].reset_index(drop=True), self.df[self.df.date >= cut].reset_index(drop=True)
        self.c = ctx(self.spec)

    def frame(self, d, model):
        return pd.concat([d[["date", "ticker"]], schema.select_features(d, list(model.features))], axis=1)

    def test_m0_m1(self):
        m0 = M0(); m0.fit(self.frame(self.train, m0), self.train.abn_oc.to_numpy(), self.c)
        self.assertTrue((m0.predict(self.frame(self.test, m0), self.c) == 0).all())
        m1 = M1(); m1.fit(self.frame(self.train, m1), self.train.abn_oc.to_numpy(), self.c)
        want = self.train.groupby("ticker").abn_oc.mean()
        got = m1.predict(self.frame(self.test, m1), self.c)
        self.assertTrue(np.allclose(got, self.test.ticker.map(want).to_numpy(), rtol=0, atol=1e-15))
        bad = self.frame(self.test, m1).assign(ticker="9999")
        with self.assertRaises(ValueError):
            m1.predict(bad, self.c)

    def test_m3_equals_inference_pooled_ols(self):
        m3 = M3(); m3.fit(self.frame(self.train, m3), self.train.abn_oc.to_numpy(), self.c)
        d = I.build_design(self.train, self.spec)                              # same rows: no exclusions left
        self.assertEqual(len(d.y), len(self.train))
        ref = I.pooled_ols(d).coef
        self.assertLess(np.max(np.abs(m3.coef - ref)), 1e-12)
        self.assertEqual(d.names[:5], ("fe[5706]", "fe[5711]", "fe[5713]", "usdjpy_ret", "eurusd_ret"))
        Xt = self.frame(self.test, m3)
        manual = I.build_design(self.test.assign(earn_flag=0, news_flag=0), self.spec).X @ ref
        self.assertLess(np.max(np.abs(m3.predict(Xt, self.c) - manual)), 1e-12)

    def test_m2_direct_ols(self):
        m2 = M2(); m2.fit(self.frame(self.train, m2), self.train.abn_oc.to_numpy(), self.c)
        tk = self.train.ticker.to_numpy()
        T = ("5706", "5711", "5713")
        X = np.column_stack([(tk == t) * 1.0 for t in T] + [self.train.eurusd_ret]
                            + [self.train[c] * (tk == t) for c in ("spy_oc", "copx_oc") for t in T])
        ref = np.linalg.lstsq(X, self.train.abn_oc.to_numpy(), rcond=None)[0]
        self.assertLess(np.max(np.abs(m2.coef - ref)), 1e-12)
        self.assertEqual(len(m2.coef), 3 + 1 + 6)

    def test_declared_features_match_spec_strings(self):
        for k, s in MODEL_SPEC_STRINGS.items():
            self.assertEqual(self.spec.raw(f"forecast.models.{k}"), s, k)
        self.assertEqual(set(M2.features), {"spy_oc", "copx_oc", "eurusd_ret"})
        self.assertEqual(set(M3.features), set(M2.features) | {"usdjpy_ret"})
        self.assertEqual((M0.features, M1.features), ((), ()))
        for m in REGISTRY.values():
            schema.assert_features_allowed(list(m.features))

    def test_rank_deficiency_raises(self):
        bad = self.train.assign(copx_oc=self.train.spy_oc)
        m3 = M3()
        with self.assertRaises(ValueError):
            m3.fit(self.frame(bad, m3), bad.abn_oc.to_numpy(), self.c)

    def test_all_four_in_engine(self):
        pred, folds = F.walk_forward(self.df, {k: REGISTRY[k] for k in ("M0", "M1", "M2", "M3")}, self.spec)
        self.assertEqual(sorted(pred.model.unique()), ["M0", "M1", "M2", "M3"])
        keys = {k: g[["date", "ticker"]].reset_index(drop=True) for k, g in pred.groupby("model")}
        for k in ("M1", "M2", "M3"):
            pd.testing.assert_frame_equal(keys["M0"], keys[k])                  # identical evaluation rows
        self.assertTrue((pred[pred.model == "M0"].yhat == 0).all())
        m1 = pred[pred.model == "M1"]
        self.assertTrue((m1.groupby(["fold", "ticker"]).yhat.nunique() == 1).all())
        self.assertTrue(np.isfinite(pred.yhat).all())
        self.assertEqual(folds.groupby("model").fold.count().nunique(), 1)


if __name__ == "__main__":
    unittest.main()
