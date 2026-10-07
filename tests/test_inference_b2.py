import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift.spec import Spec, SpecPendingError  # noqa: E402
from test_inference_b1 import panel  # noqa: E402


class TestHuber(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()
        self.d = I.build_design(panel(n_dates=350, seed=11), self.spec)

    def test_infinite_c_is_ols_dk(self):
        h = I.fit_huber(self.d, self.spec, c=1e12)
        o = I.fit_dk(self.d, self.spec)
        self.assertLess(np.max(np.abs(h.coef - o.coef)), 1e-12)
        self.assertLess(np.max(np.abs(h.cov - o.cov)) / np.max(np.abs(o.cov)), 1e-10)
        self.assertEqual(h.info["share_downweighted"], 0.0)

    def test_fixed_point_scale_and_sandwich(self):
        h = I.fit_huber(self.d, self.spec)
        r_ols = I.pooled_ols(self.d).resid
        s = 1.4826 * np.median(np.abs(r_ols - np.median(r_ols)))
        self.assertAlmostEqual(h.info["scale"], s, places=15)
        self.assertEqual(h.info["c"], 1.345)
        u = (self.d.y - self.d.X @ h.coef) / s
        psi = np.clip(u, -1.345, 1.345)
        self.assertLess(np.max(np.abs(self.d.X.T @ psi)), 1e-8)            # estimating equation
        g = self.d.X * (s * psi)[:, None]
        A = self.d.X.T @ (self.d.X * (np.abs(u) <= 1.345)[:, None])
        dl = np.abs(self.d.date_codes[:, None] - self.d.date_codes[None, :])
        W = np.clip(1 - dl / (h.lag + 1.0), 0, None)
        ref = np.linalg.inv(A) @ g.T @ W @ g @ np.linalg.inv(A)
        self.assertLess(np.max(np.abs(h.cov - ref)) / np.max(np.abs(ref)), 1e-10)
        self.assertGreater(h.info["share_downweighted"], 0.0)

    def test_robust_to_outliers(self):
        df = panel(n_dates=500, seed=12, b=0.3)
        rng = np.random.default_rng(1)
        bad = rng.choice(len(df), 30, replace=False)
        df.loc[bad, "abn_oc"] += 0.5 * np.sign(df.loc[bad, "usdjpy_ret"].to_numpy()) * 1   # leverage-aligned outliers
        d = I.build_design(df, self.spec)
        j = d.col("usdjpy_ret")
        err_ols = abs(I.fit_dk(d, self.spec).coef[j] - 0.3)
        err_hub = abs(I.fit_huber(d, self.spec).coef[j] - 0.3)
        self.assertLess(err_hub, err_ols / 5)


class TestInfluence(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()
        self.d = I.build_design(panel(n_dates=250, seed=21), self.spec)

    def refit_without(self, dates):
        dates = np.asarray(pd.to_datetime(list(dates)), dtype="datetime64[ns]")
        keep = ~np.isin(self.d.dates, dates)
        self.assertEqual(int((~keep).sum()) > 0, True)                  # guard against silent no-op
        sub = I.subset_design(self.d, keep)
        return I.pooled_ols(sub).coef[self.d.col("usdjpy_ret")]

    def test_closed_form_equals_refits(self):
        inf = I.date_influence(self.d)
        b0 = I.pooled_ols(self.d).coef[self.d.col("usdjpy_ret")]
        self.assertEqual(len(inf), self.d.T)
        self.assertTrue((np.diff(inf.abs_delta_b.to_numpy()) <= 0).all())
        for _, r in inf.sample(30, random_state=0).iterrows():
            self.assertAlmostEqual(self.refit_without([r.date]) - b0, r.delta_b, places=12)

    def test_curve(self):
        cur = I.influence_curve(self.d, self.spec)
        inf = I.date_influence(self.d)
        self.assertEqual(list(cur.k), list(range(21)))                    # k_max = 20 from the spec
        self.assertAlmostEqual(cur.b.iloc[0], I.fit_dk(self.d, self.spec).param("usdjpy_ret")["estimate"])
        for k in (1, 5, 20):
            top = inf.date.to_numpy()[:k]
            self.assertAlmostEqual(cur.b.iloc[k], self.refit_without(top), places=12)
            self.assertEqual(cur.n_dates.iloc[k], self.d.T - k)
            self.assertEqual(cur.lag.iloc[k], Spec.dk_lag(int(self.d.T - k)))
        self.assertEqual(list(cur.date_removed.iloc[1:]), list(inf.date.iloc[:20]))


class TestTOST(unittest.TestCase):
    def test_values_and_ci_characterisation(self):
        r = I.tost(0.0, 1.0, 3.0)
        self.assertTrue(r["equivalent"])
        self.assertAlmostEqual(r["p"], stats.norm.sf(3.0))
        self.assertFalse(I.tost(0.0, 1.0, 1.0)["equivalent"])
        q = stats.norm.ppf(0.95)
        for est in np.linspace(-2, 2, 41):
            for d in (0.5, 1.0, 2.0, 3.0):
                r = I.tost(est, 0.5, d)
                inside = (est - q * 0.5 > -d) and (est + q * 0.5 < d)
                self.assertEqual(r["equivalent"], inside, (est, d))

    def test_refusals_and_pending_sesoi(self):
        for args in [(0, 1, 0), (0, 1, -1), (0, 0, 1)]:
            with self.assertRaises(ValueError):
                I.tost(*args)
        spec = Spec.load()
        res = I.fit_dk(I.build_design(panel(n_dates=200, seed=4), spec), spec)
        r = I.tost_result(res, "usdjpy_ret", spec)                               # AM-07 (P3-6): the spec's SESOI and alpha
        cfg = json.loads((Path(__file__).resolve().parents[1] / "docs" / "P3_RUN_CONFIG.json").read_text(encoding="utf-8"))
        self.assertEqual((r["sesoi"], r["alpha"]), (cfg["sesoi"]["primary"], 0.05))
        self.assertIn("equivalent", I.tost_result(res, "usdjpy_ret", spec, sesoi=0.5))


class TestB2Blinding(unittest.TestCase):
    def test_forged_provenance_refused(self):
        spec = Spec.load()
        d = I.build_design(panel(n_dates=200, seed=5), spec)
        forged = I.Design(**{**d.__dict__, "provenance": "dev_real"})
        for fn in (lambda: I.fit_huber(forged, spec), lambda: I.date_influence(forged),
                   lambda: I.influence_curve(forged, spec)):
            with self.assertRaises(B.BlindingError):
                fn()


if __name__ == "__main__":
    unittest.main()
