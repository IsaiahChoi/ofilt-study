import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402
from test_inference_b1 import panel  # noqa: E402
import tag_state as TS  # noqa: E402  (P3-8b)


def panel3(n_dates=400, seed=0, exclusions=True, const_beta=True, b=0.3, delta=0.6):
    """B1 panel + consistent targets: gap, cc = gap + abn, raw = abn + beta*m (m common per date)."""
    df = panel(n_dates=n_dates, seed=seed, b=b)
    rng = np.random.default_rng(seed + 100)
    dates = df.date.unique()
    m = dict(zip(dates, rng.normal(0, 0.008, len(dates)) + 0.2 * df.groupby("date").usdjpy_ret.first().to_numpy()))
    df["y_topix_oc"] = df.date.map(m).to_numpy()
    df["y_1306_oc"] = df["y_topix_oc"]   # AM-03 (row 18)
    if not exclusions:
        df["earn_flag"] = 0
    df["beta"] = 1.0 if const_beta else rng.uniform(0.6, 1.4, len(df))
    df["gap_abn"] = (delta - b) * df.usdjpy_ret + rng.normal(0, 0.01, len(df))
    df["cc_abn"] = df.gap_abn + df.abn_oc
    df["raw_oc"] = df.abn_oc + df.beta * df.y_topix_oc
    return B.mark_synthetic(df)


class TestJoint(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()
        self.df = panel3()

    def test_blocks_equal_separate_fits_and_cross_cov_definition(self):
        df = self.df.copy()
        df.loc[[3, 10, 40], "cc_abn"] = np.nan                         # common sample must drop these
        J = I.fit_joint(df, self.spec)
        sub = df.drop(index=[3, 10, 40])
        for i, t in enumerate(("abn_oc", "cc_abn")):
            r = I.fit_dk(I.build_design(sub, self.spec, target=t), self.spec)
            self.assertLess(np.max(np.abs(J.result(i).coef - r.coef)), 1e-14)
            self.assertLess(np.max(np.abs(J.result(i).cov - r.cov)) / np.abs(r.cov).max(), 1e-12)
        d = I.build_design(sub, self.spec)
        e1 = I.pooled_ols(d).resid
        e2 = I.pooled_ols(I.build_design(sub, self.spec, target="cc_abn")).resid
        dl = np.abs(d.date_codes[:, None] - d.date_codes[None, :])
        W = np.clip(1 - dl / (J.lag + 1.0), 0, None)
        Bm = np.linalg.inv(d.X.T @ d.X)
        cross = Bm @ (d.X * e1[:, None]).T @ W @ (d.X * e2[:, None]) @ Bm
        k = len(J.names)
        self.assertLess(np.max(np.abs(J.cov[:k, k:] - cross)) / np.abs(cross).max(), 1e-10)
        self.assertEqual(J.n, len(d.y))

    def test_delta_cc_identity(self):
        J = I.fit_joint(self.df, self.spec)
        g = I.fit_dk(I.build_design(self.df, self.spec, target="gap_abn"), self.spec)
        k = len(J.names)
        self.assertLess(np.max(np.abs(J.coef[k:] - (g.coef + J.coef[:k]))), 1e-12)


class TestFraction(unittest.TestCase):
    def test_delta_method_and_fieller_geometry(self):
        b, d, V, a = 0.3, 0.6, np.array([[0.01, 0.004], [0.004, 0.02]]), 0.05
        r = I.fraction_from(b, d, V, a)
        q = stats.norm.ppf(0.975)
        eps = 1e-7
        grad = np.array([((b + eps) / d - (b - eps) / d) / (2 * eps),
                         (b / (d + eps) - b / (d - eps)) / (2 * eps)])
        self.assertAlmostEqual(r["se_delta"], np.sqrt(grad @ V @ grad), places=7)
        self.assertEqual(r["fieller"]["kind"], "bounded")                    # t_d = 4.24 > q
        lo, hi = r["fieller"]["ci"]
        quad = lambda f: (b - f * d) ** 2 - q * q * (V[0, 0] - 2 * f * V[0, 1] + f * f * V[1, 1])
        self.assertLess(abs(quad(lo)), 1e-12)
        self.assertLess(abs(quad(hi)), 1e-12)
        self.assertTrue(lo < r["f"] < hi and quad(r["f"]) <= 0)
        weak = I.fraction_from(0.3, 0.1, V, a)                              # t_d = 0.71 < q
        self.assertIn(weak["fieller"]["kind"], ("two_rays", "real_line"))
        if weak["fieller"]["kind"] == "two_rays":
            (_, x1), (x2, _) = weak["fieller"]["ci"]
            self.assertTrue(x1 < x2 and (weak["f"] <= x1 or weak["f"] >= x2))
        self.assertEqual(I.fraction_from(0.0, 0.01, np.eye(2), a)["fieller"]["kind"], "real_line")
        strong = I.fraction_from(0.3, 0.6, V / 400, a)                     # t_d = 85
        self.assertLess(max(abs(x - y) for x, y in zip(strong["ci_delta"], strong["fieller"]["ci"])),
                        0.02 * strong["se_delta"] * 2 * q)

    def test_fraction_unpriced_from_joint(self):
        spec = Spec.load()
        J = I.fit_joint(panel3(n_dates=600, seed=2), spec)
        r = I.fraction_unpriced(J)
        b, d, _ = J.pair("usdjpy_ret")
        self.assertAlmostEqual(r["f"], b / d)
        self.assertLess(abs(r["f"] - 0.5), 0.25)                            # planted b/delta = 0.3/0.6


class TestMarketDecompositionHolm(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()

    def test_market_regression_is_date_level_nw(self):
        df = panel3()
        r = I.fit_market(df, self.spec)
        d = I.build_design(df, self.spec, target="y_topix_oc")
        m = df.loc[d.index].groupby("date").first()
        X = np.column_stack([np.ones(len(m)), m.usdjpy_ret, m.eurusd_ret, m.spy_oc, m.copx_oc])
        beta = np.linalg.lstsq(X, m.y_topix_oc.to_numpy(), rcond=None)[0]
        self.assertLess(np.max(np.abs(r.coef - beta)), 1e-12)
        e = m.y_topix_oc.to_numpy() - X @ beta
        t = np.arange(len(m))
        W = np.clip(1 - np.abs(t[:, None] - t[None, :]) / (r.lag + 1.0), 0, None)
        Bm = np.linalg.inv(X.T @ X)
        ref = Bm @ (X * e[:, None]).T @ W @ (X * e[:, None]) @ Bm
        self.assertLess(np.max(np.abs(r.cov - ref)) / np.abs(ref).max(), 1e-10)
        self.assertEqual(r.lag, Spec.dk_lag(len(m)))

    def test_decomposition_exact_when_balanced_constant_beta(self):
        dec = I.decomposition(panel3(exclusions=False, const_beta=True), self.spec)
        self.assertLess(abs(dec["gap"]), 1e-12)
        self.assertEqual(dec["mean_beta"], 1.0)
        dec2 = I.decomposition(panel3(exclusions=True, const_beta=False, seed=7), self.spec)
        self.assertGreater(abs(dec2["gap"]), 0.0)                          # approximation otherwise
        self.assertLess(abs(dec2["gap"]), 0.1 * abs(dec2["b_raw"]) + 0.05)

    def test_holm(self):
        p = [0.01, 0.04, 0.03, 0.005]
        self.assertTrue(np.allclose(I.holm(p), [0.03, 0.06, 0.06, 0.02]))
        self.assertTrue(np.allclose(I.holm([0.6, 0.9]), [1.0, 1.0]))
        rng = np.random.default_rng(0)
        for _ in range(50):
            q = rng.random(7)
            a = I.holm(q)
            self.assertTrue((a >= q - 1e-15).all() and (a <= 1).all())
            o = np.argsort(q)
            self.assertTrue((np.diff(a[o]) >= -1e-15).all())                # monotone in p order
        with self.assertRaises(ValueError):
            I.holm([0.2, 1.2])

    def test_secondary_family(self):
        out = I.secondary_family_tests(panel3(), self.spec)
        self.assertEqual(list(out.member), list(I.SECONDARY_TERMS))
        self.assertTrue(np.allclose(out.p_holm, I.holm(out.p.to_numpy())))
        self.assertTrue((out.p_holm >= out.p - 1e-15).all())


class TestB3Blinding(unittest.TestCase):
    def test_entry_points_refuse_real(self):
        spec = Spec.load()
        df = panel3()
        df.attrs = {"provenance": "dev_real"}
        for fn in (lambda: I.fit_joint(df, spec), lambda: I.fit_market(df, spec),
                   lambda: I.decomposition(df, spec), lambda: I.secondary_family_tests(df, spec)):
            with TS.blinded(), self.assertRaises(B.BlindingError):  # P3-8b: was with self.assertRaises(B.BlindingError):; the guard in a repository without the tags
                fn()


if __name__ == "__main__":
    unittest.main()
