import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))  # P3-8b: the tests folder, for tag_state
import tag_state as TS  # noqa: E402  (P3-8b)

TICK = ["5706", "5711", "5713"]


def panel(n_dates=400, seed=0, b=0.3, a2=-0.1):
    """Synthetic panel with every column the primary design and secondary terms need."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2015-01-06", periods=n_dates)
    e, eur = rng.normal(0, 4e-3, n_dates), rng.normal(0, 4e-3, n_dates)
    spy, copx = rng.normal(0, 8e-3, n_dates), rng.normal(0, 1.5e-2, n_dates)
    wh = np.where(rng.random(n_dates) < 0.2, 65.9833, 17.9833)
    rv = rng.uniform(0.5, 2.0, n_dates) * 1.3e-8 * 1079
    bv = rv * rng.uniform(0.6, 1.1, n_dates)
    rows = []
    for j, t in enumerate(TICK):
        y = 0.001 * j + b * e + a2 * eur + 0.4 * spy + 0.2 * copx + rng.normal(0, 0.01, n_dates)
        rows.append(pd.DataFrame(dict(
            date=dates, ticker=t, usdjpy_ret=e, eurusd_ret=eur, spy_oc=spy, copx_oc=copx,
            window_hours=wh, usdjpy_rv=rv, usdjpy_bv=bv, usdjpy_bars=1079.0,
            earn_flag=(rng.random(n_dates) < 0.04).astype(int), news_flag=0, beta=1.0, abn_oc=y)))
    df = pd.concat(rows).sort_values(["date", "ticker"], kind="mergesort").reset_index(drop=True)
    return B.mark_synthetic(df)


class TestDesign(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()
        self.df = panel()

    def test_layout_and_values(self):
        d = I.build_design(self.df, self.spec)
        self.assertEqual(d.names, ("fe[5706]", "fe[5711]", "fe[5713]", "usdjpy_ret", "eurusd_ret",
                                   "spy_oc:5706", "spy_oc:5711", "spy_oc:5713",
                                   "copx_oc:5706", "copx_oc:5711", "copx_oc:5713"))
        self.assertTrue(np.allclose(d.X[:, :3].sum(axis=1), 1.0))      # FE partition, no intercept
        src = self.df.loc[d.index]
        self.assertTrue(np.array_equal(d.X[:, d.col("usdjpy_ret")], src.usdjpy_ret.to_numpy()))
        m = src.ticker.to_numpy() == "5711"
        self.assertTrue(np.array_equal(d.X[m, d.col("copx_oc:5711")], src.copx_oc.to_numpy()[m]))
        self.assertTrue((d.X[~m, d.col("copx_oc:5711")] == 0).all())
        self.assertEqual(d.T, len(np.unique(d.dates)))
        self.assertTrue((np.diff(d.date_codes[np.argsort(d.dates, kind="stable")]) >= 0).all())

    def test_sample_rules(self):
        df = self.df.copy()
        df.loc[5, "copx_oc"] = np.nan
        df.loc[7, "beta"] = np.nan
        df.loc[9, "news_flag"] = 1
        d = I.build_design(df, self.spec)
        dropped = set(df.index) - set(d.index)
        self.assertEqual(dropped, set(df.index[(df.earn_flag == 1) | (df.news_flag == 1)]) | {5, 7})
        d2 = I.build_design(df, self.spec, exclude=[])                 # robustness hook
        self.assertEqual(set(df.index) - set(d2.index), {5, 7})

    def test_secondary_terms(self):
        base = I.build_design(self.df, self.spec)
        e = base.X[:, base.col("usdjpy_ret")]
        src = self.df.loc[base.index]
        thr = self.spec.rv_per_bar_dev_median()
        mods = {"fx_x_longwindow": ("long_window", (src.window_hours.to_numpy() > 18).astype(float)),
                "fx_x_jumpshare": ("jumpshare", np.clip((src.usdjpy_rv - src.usdjpy_bv) / src.usdjpy_rv, 0, 1).to_numpy()),
                "fx_x_highrv": ("highrv", ((src.usdjpy_rv / src.usdjpy_bars).to_numpy() > thr).astype(float))}
        for term, (mname, m) in mods.items():   # AM-01: primary + main effect + interaction
            d = I.build_design(self.df, self.spec, secondary=term)
            self.assertEqual(d.names, base.names + (mname, f"usdjpy_ret:{mname}"), term)
            self.assertTrue(np.allclose(d.X[:, -2], m), term)
            self.assertTrue(np.allclose(d.X[:, -1], e * m), term)
            self.assertEqual(list(I.SECONDARY_TESTED[term]), [f"usdjpy_ret:{mname}"])
            self.assertTrue(0 < m.astype(bool).sum() < len(m), term)      # moderator varies
        self.assertEqual(I.SECONDARY_TESTED["fx_asymmetry"], {"e_pos": 1.0, "e_neg": -1.0})
        a = I.build_design(self.df, self.spec, secondary="fx_asymmetry")
        self.assertNotIn("usdjpy_ret", a.names)
        self.assertTrue(np.allclose(a.X[:, a.col("e_pos")] + a.X[:, a.col("e_neg")], e))

    def test_refusals(self):
        for t in ["oc_lag1", "usdjpy_ret", "ao_gap_adj", "beta", "excl_inference", "open", "earn_flag",
                  "jumpshare", "rv_per_bar"]:
            with self.subTest(t=t), self.assertRaises(I.DesignError):
                I.build_design(self.df.assign(**{t: 0.0}) if t not in self.df else self.df, self.spec, target=t)
        with self.assertRaises(I.DesignError):
            I.build_design(self.df, self.spec, secondary="fx_x_whatever")
        with self.assertRaises(I.DesignError):
            I.build_design(self.df.drop(columns=["beta"]), self.spec)
        with self.assertRaises(I.DesignError):
            I.build_design(self.df.assign(copx_oc=self.df.spy_oc), self.spec)   # rank-deficient
        real = self.df.copy()
        real.attrs = {"provenance": "dev_real"}
        with TS.blinded(), self.assertRaises(B.BlindingError):  # P3-8b: was with self.assertRaises(B.BlindingError):; the guard in a repository without the tags
            I.build_design(real, self.spec)
        with self.assertRaises(B.BlindingError):
            I.build_design(self.df, self.spec, provenance="dev_real")      # attrs/kwarg conflict

    def test_entry_points_recheck_provenance(self):
        d = I.build_design(self.df, self.spec)
        forged = I.Design(**{**d.__dict__, "provenance": "dev_real"})
        with TS.blinded(), self.assertRaises(B.BlindingError):  # P3-8b: was with self.assertRaises(B.BlindingError):; the guard in a repository without the tags
            I.pooled_ols(forged)


class TestOLSandDK(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()
        self.d = I.build_design(panel(n_dates=300, seed=3), self.spec)   # unbalanced: earn_flag exclusions

    def test_ols_matches_lstsq(self):
        f = I.pooled_ols(self.d)
        ref = np.linalg.lstsq(self.d.X, self.d.y, rcond=None)[0]
        self.assertLess(np.max(np.abs(f.coef - ref)), 1e-10)
        self.assertLess(np.max(np.abs(f.bread - np.linalg.inv(self.d.X.T @ self.d.X))), 1e-6 * np.abs(f.bread).max())
        self.assertLess(np.abs(self.d.X.T @ f.resid).max(), 1e-10)

    def test_dk_equals_pairwise_kernel_definition(self):
        f = I.pooled_ols(self.d)
        for L in (0, 1, 3, I.Spec.dk_lag(self.d.T), 12):
            cov, used = I.driscoll_kraay(f, lag=L)
            s = self.d.X * f.resid[:, None]
            dl = np.abs(self.d.date_codes[:, None] - self.d.date_codes[None, :])
            W = np.clip(1.0 - dl / (L + 1.0), 0.0, None)
            ref = f.bread @ (s.T @ W @ s) @ f.bread
            self.assertEqual(used, L)
            self.assertLess(np.max(np.abs(cov - ref)) / np.max(np.abs(ref)), 1e-12, L)

    def test_default_lag_rule_and_lag0_cluster(self):
        f = I.pooled_ols(self.d)
        _, used = I.driscoll_kraay(f)
        self.assertEqual(used, int(np.floor(4 * (self.d.T / 100) ** (2 / 9))))
        cov0, _ = I.driscoll_kraay(f, lag=0)
        H = np.array([(self.d.X * f.resid[:, None])[self.d.date_codes == t].sum(axis=0) for t in range(self.d.T)])
        self.assertLess(np.max(np.abs(cov0 - f.bread @ H.T @ H @ f.bread)), 1e-14)

    def test_result_outputs(self):
        r = I.fit_dk(self.d, self.spec)
        p = r.param("usdjpy_ret")
        j = r.names.index("usdjpy_ret")
        self.assertAlmostEqual(p["estimate"], r.coef[j])
        self.assertAlmostEqual(p["se"], r.se[j])
        self.assertAlmostEqual(p["p"], 2 * stats.norm.sf(abs(r.coef[j] / r.se[j])))
        q = stats.norm.ppf(1 - self.spec.alpha / 2)
        self.assertAlmostEqual(p["ci"][1] - p["ci"][0], 2 * q * r.se[j])
        c = r.contrast({"usdjpy_ret": 1.0, "eurusd_ret": -1.0})
        k = r.names.index("eurusd_ret")
        self.assertAlmostEqual(c["se"] ** 2, r.cov[j, j] + r.cov[k, k] - 2 * r.cov[j, k])
        self.assertLess(abs(p["estimate"] - 0.3), 0.15)     # planted b = 0.3 recovered (loose, synthetic)

    def test_lag_validation(self):
        with self.assertRaises(ValueError):
            I.bartlett_long_run(np.zeros((5, 2)), -1)


if __name__ == "__main__":
    unittest.main()
