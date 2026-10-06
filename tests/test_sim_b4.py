import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402


def wide(df, values):
    return pd.DataFrame({"date": df.date, "ticker": df.ticker, "v": values}).pivot(index="date", columns="ticker", values="v")


class TestSyntheticPanel(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()

    def test_drop_in_for_all_entry_points(self):
        df = S.synthetic_panel(600, b=0.2, seed=1, delta_cc=0.5, p_excl=0.03)
        df["y_1306_oc"] = df["y_topix_oc"]   # AM-03; sim.py is frozen (row 19)
        self.assertEqual(B.require_unblinded(df), "synthetic")
        self.assertEqual(len(df), 1800)
        I.fit_dk(I.build_design(df, self.spec), self.spec)
        I.fit_huber(I.build_design(df, self.spec), self.spec)
        fam = I.secondary_family_tests(df, self.spec)
        self.assertEqual(len(fam), 4)
        I.fraction_unpriced(I.fit_joint(df, self.spec))
        I.decomposition(df, self.spec)
        hr = I.build_design(df, self.spec, secondary="fx_x_highrv")
        share = hr.X[:, hr.col("highrv")].mean()
        self.assertTrue(0.35 < share < 0.65, share)                 # threshold splits near the median
        self.assertTrue(0.18 < (df.window_hours > 18).mean() < 0.28)

    def test_recovers_parameters(self):
        df = S.synthetic_panel(1708, b=0.25, a2=-0.15, seed=2)
        r = I.fit_dk(I.build_design(df, self.spec), self.spec)
        for name, truth in (("usdjpy_ret", 0.25), ("eurusd_ret", -0.15)):
            p = r.param(name)
            self.assertLess(abs(p["estimate"] - truth), 4 * p["se"], name)

    def test_moments(self):
        df = S.synthetic_panel(20000, seed=3)
        dd = df.drop_duplicates("date")
        self.assertLess(abs(np.corrcoef(dd.usdjpy_ret, dd.eurusd_ret)[0, 1] + 0.44), 0.02)
        W = wide(df, S.true_residuals(df))
        C = np.corrcoef(W.to_numpy().T)
        self.assertLess(np.max(np.abs(C[np.triu_indices(3, 1)] - 0.43)), 0.03)
        for j, t in enumerate(S.TICKERS):
            x = W[t].to_numpy()
            self.assertLess(abs(np.corrcoef(x[1:], x[:-1])[0, 1] - 0.1), 0.03, t)
            self.assertLess(abs(x.std() / S.DEFAULT_SIGMA[j] - 1), 0.03, t)

    def test_t5_tails(self):
        g = wide(S.synthetic_panel(20000, seed=4), S.true_residuals(S.synthetic_panel(20000, seed=4)))
        t5df = S.synthetic_panel(20000, seed=4, tails="t5")
        t = wide(t5df, S.true_residuals(t5df))
        for j, c in enumerate(S.TICKERS):
            self.assertLess(abs(t[c].std() / S.DEFAULT_SIGMA[j] - 1), 0.08, c)   # unit-variance scaling
            self.assertGreater(stats.kurtosis(t[c]), 1.5, c)
            self.assertLess(abs(stats.kurtosis(g[c])), 0.3, c)
        dd = t5df.drop_duplicates("date")
        self.assertGreater(stats.kurtosis(dd.usdjpy_ret), 1.5)

    def test_determinism_and_truth(self):
        a, b = S.synthetic_panel(200, seed=9), S.synthetic_panel(200, seed=9)
        pd.testing.assert_frame_equal(a, b)
        self.assertFalse(a.abn_oc.equals(S.synthetic_panel(200, seed=10).abn_oc))
        self.assertEqual(S.synthetic_panel(50).attrs["truth"]["seed"], self.spec.seed)
        self.assertEqual(a.attrs["provenance"], "synthetic")

    def test_delta_cc_and_identities(self):
        df = S.synthetic_panel(1708, b=0.2, seed=5, delta_cc=0.6)
        self.assertTrue(np.array_equal(df.cc_abn, df.gap_abn + df.abn_oc))
        self.assertTrue(np.array_equal(df.raw_oc, df.abn_oc + df.beta * df.y_topix_oc))
        J = I.fit_joint(df, self.spec)
        b, d, V = J.pair("usdjpy_ret")
        self.assertLess(abs(d - 0.6), 4 * np.sqrt(V[1, 1]))
        self.assertNotIn("gap_abn", S.synthetic_panel(30, seed=1).columns)

    def test_validation(self):
        for kw in [dict(tails="cauchy"), dict(n_dates=5), dict(rho_fx=1.0), dict(phi=1.0), dict(p_excl=1.0)]:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                S.synthetic_panel(**({"n_dates": 50} | kw))
        d = S.synthetic_panel(50)
        d.attrs = {}
        with self.assertRaises(ValueError):
            S.true_residuals(d)                                      # attrs dropped -> refused


if __name__ == "__main__":
    unittest.main()
