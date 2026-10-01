"""B6: Stage B identity and calibration batch (synthetic only).

Covered elsewhere, not duplicated: OLS == lstsq (test_inference_b1), Huber -> OLS-DK as
c -> inf (test_inference_b2), delta_cc = delta_gap + b (test_inference_b3).
References below are plain numpy implementations, independent of the package helpers."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402

from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

Q95 = 1.959963984540054


def ols(X, y):
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    return beta, y - X @ beta


def nw_cov(X, e, lag):
    """Bartlett NW sandwich with one row per period (pairwise-kernel form)."""
    t = np.arange(len(e))
    W = np.clip(1 - np.abs(t[:, None] - t[None, :]) / (lag + 1.0), 0, None)
    B = np.linalg.inv(X.T @ X)
    s = X * e[:, None]
    return B @ s.T @ W @ s @ B


class TestPortfolioAndFWL(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()
        self.df = S.synthetic_panel(600, b=0.3, a2=-0.2, seed=61)          # balanced: p_excl = 0
        self.d = I.build_design(self.df, self.spec)
        self.r = I.fit_dk(self.d, self.spec)
        self.fx = [self.d.col(c) for c in self.spec.fx_block]

    def test_dk_equals_nw_on_equal_weighted_portfolio(self):
        self.assertEqual(self.d.T * 3, len(self.d.y))                       # balanced
        g = self.df.groupby("date", sort=True)
        ybar = g.abn_oc.mean().to_numpy()
        m = g[["usdjpy_ret", "eurusd_ret", "spy_oc", "copx_oc"]].first().to_numpy()
        Xp = np.column_stack([np.ones(len(m)), m])
        bp, ep = ols(Xp, ybar)
        Vp = nw_cov(Xp, ep, self.r.lag)
        self.assertLess(np.max(np.abs(self.r.coef[self.fx] - bp[1:3])), 1e-12)
        Vdk = self.r.cov[np.ix_(self.fx, self.fx)]
        self.assertLess(np.max(np.abs(Vdk - Vp[1:3, 1:3])) / np.abs(Vp[1:3, 1:3]).max(), 1e-8)

    def test_fwl(self):
        X, y = self.d.X, self.d.y
        nuis = [j for j in range(X.shape[1]) if j not in self.fx]
        _, ry = ols(X[:, nuis], y)
        RX = np.column_stack([ols(X[:, nuis], X[:, j])[1] for j in self.fx])
        bf, _ = ols(RX, ry)
        self.assertLess(np.max(np.abs(bf - self.r.coef[self.fx])), 1e-10)


class TestDeltaVsFieller(unittest.TestCase):
    def test_gap_is_order_q_over_t(self):
        # First-order theory: Fieller and delta endpoints differ by ~ q/t_d delta half-widths.
        # Bound 2.5/t_d (measured worst case on this grid: 2.39/t_d at t_d = 10, -> 1.96/t_d).
        prev = None
        for t in (10, 20, 50, 100):
            worst = 0.0
            for rho in (-0.9, -0.5, 0.0, 0.5, 0.9):
                for f0 in (0.1, 0.5, 1.0, 2.0):
                    sd = 1.0 / t
                    sb = 1.5 * sd
                    V = np.array([[sb * sb, rho * sb * sd], [rho * sb * sd, sd * sd]])
                    r = I.fraction_from(f0, 1.0, V, 0.05)
                    self.assertEqual(r["fieller"]["kind"], "bounded")
                    hw = Q95 * r["se_delta"]
                    worst = max(worst, max(abs(a - b) for a, b in zip(r["ci_delta"], r["fieller"]["ci"])) / hw)
            self.assertLess(worst, 2.5 / t, t)
            if prev is not None:
                self.assertLess(worst, prev)
            prev = worst


class TestNoisyAuction(unittest.TestCase):
    """Why the auction-conditional spec was retired (P15). Structural DGP:
    gap g = rho*delta*e + f + eta;  oc = (1 - rho)*delta*e - eta + u."""
    N, DELTA, VE, VF, VETA, SDU = 2_000_000, 0.5, 1.0, 4.0, 2.0, 3.0

    def run_case(self, rho, seed):
        rng = np.random.default_rng(seed)
        e = rng.normal(0, np.sqrt(self.VE), self.N)
        f = rng.normal(0, np.sqrt(self.VF), self.N)
        eta = rng.normal(0, np.sqrt(self.VETA), self.N)
        u = rng.normal(0, self.SDU, self.N)
        g = rho * self.DELTA * e + f + eta
        oc = (1 - rho) * self.DELTA * e - eta + u
        one = np.ones(self.N)
        b_pre = ols(np.column_stack([one, e]), oc)[0][1]
        b_auc = ols(np.column_stack([one, e, g]), oc)[0][1]
        s = ols(np.column_stack([one, e]), g)[1]                 # gap surprise: residualised on the design
        b_sur = ols(np.column_stack([one, e, s]), oc)[0][1]
        return b_pre, b_auc, b_sur

    def test_rho_1_and_0_7(self):
        k = self.VETA / (self.VF + self.VETA)
        self.assertAlmostEqual(k, 1 / 3)
        for rho, seed in ((1.0, 71), (0.7, 72)):
            b_pre, b_auc, b_sur = self.run_case(rho, seed)
            with self.subTest(rho=rho):
                self.assertLess(abs(b_pre - (1 - rho) * self.DELTA), 0.01)          # 0 / 0.15
                self.assertLess(abs(b_auc - self.DELTA * (1 - rho + k * rho)), 0.01)  # 0.1667 / 0.2667
                self.assertLess(abs(b_sur - b_pre), 1e-10)                          # FWL: exact


class TestOOSPenaltyLemma(unittest.TestCase):
    """Lemma: R2_oos (vs the training-mean forecast) ~ R2 - k/n_train for OLS with intercept."""

    def test_lemma(self):
        R2, n_tr, n_te, reps = 0.0025, 1700, 1000, 300
        beta = np.sqrt(R2 / (1 - R2))                                  # Var x = 1, Var eps = 1
        for k in (1, 10):
            rng = np.random.default_rng(80 + k)
            vals = []
            for _ in range(reps):
                X = rng.standard_normal((n_tr + n_te, k))
                y = beta * X[:, 0] + rng.standard_normal(n_tr + n_te)
                Xa = np.column_stack([np.ones(n_tr + n_te), X])
                coef = np.linalg.lstsq(Xa[:n_tr], y[:n_tr], rcond=None)[0]
                yt = y[n_tr:]
                vals.append(1 - np.sum((yt - Xa[n_tr:] @ coef) ** 2) / np.sum((yt - y[:n_tr].mean()) ** 2))
            with self.subTest(k=k):
                self.assertLess(abs(np.mean(vals) - (R2 - k / n_tr)), 0.0015, (k, np.mean(vals)))


class TestCoverage(unittest.TestCase):
    """1000-rep coverage of the 95% DK CI for b; T = 1708 (dev length); band [93.5%, 96.5%]."""
    T, REPS, B_TRUE = 1708, 1000, 0.25

    def test_coverage(self):
        spec = Spec.load()
        hits, est, ses = 0, [], []
        for r in range(self.REPS):
            df = S.synthetic_panel(self.T, b=self.B_TRUE, seed=50_000 + r)
            p = I.fit_dk(I.build_design(df, spec), spec).param("usdjpy_ret")
            hits += p["ci"][0] <= self.B_TRUE <= p["ci"][1]
            est.append(p["estimate"]); ses.append(p["se"])
        cov = hits / self.REPS
        out = dict(T=self.T, reps=self.REPS, b_true=self.B_TRUE, seeds="50000..50999", coverage=cov,
                   mc_se=float(np.sqrt(cov * (1 - cov) / self.REPS)), mean_b=float(np.mean(est)),
                   sd_b=float(np.std(est, ddof=1)), mean_se=float(np.mean(ses)),
                   se_over_sd=float(np.mean(ses) / np.std(est, ddof=1)), lag=Spec.dk_lag(self.T))
        (ROOT / "reports").mkdir(exist_ok=True)
        (ROOT / "reports" / "B6_coverage.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
        self.assertTrue(0.935 <= cov <= 0.965, out)


if __name__ == "__main__":
    unittest.main()
