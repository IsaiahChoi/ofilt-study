"""A8 (reduced scope, per Isaiah): look-ahead perturbation of beta and every
constructed target. Real-data parts read target/flag/gap columns only (no FX)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import report_A7 as A7  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402
from test_targets import synth_panel  # noqa: E402

OUT_COLS = ["beta", "raw_oc", "abn_oc", "gap_abn", "cc_abn", "cc_raw", "excl_inference"]
REAL_COLS = ["date", "ticker", "y_oc", "y_topix_oc", "ao_gap_adj", "ao_topix_gap", "earn_flag", "news_flag"]
CONFIGS = [dict(), dict(method="rolling", window=60), dict(estimate_on="all_rows")]


def bits(s: pd.Series) -> np.ndarray:
    a = s.to_numpy(dtype=float)
    return a.view(np.int64)  # bit-level comparison (distinguishes -0.0, NaN payloads)


def perturb(df, tau, rng, scramble_all):
    p = df.copy()
    after = p.date > tau
    n = int(after.sum())
    p.loc[after, "y_oc"] = rng.normal(0, 0.03, n)
    p.loc[after, "y_topix_oc"] = rng.normal(0, 0.02, n)
    if scramble_all:
        p.loc[after, "ao_gap_adj"] = rng.normal(0, 0.03, n)
        p.loc[after, "ao_topix_gap"] = rng.normal(0, 0.02, n)
        p.loc[after, "earn_flag"] = (rng.random(n) < 0.3).astype(int)
        p.loc[after, "news_flag"] = (rng.random(n) < 0.3).astype(int)
    return p


class LookAhead:
    """Mixin: self.df (panel), self.taus."""

    def check(self, spec):
        rng = np.random.default_rng(20261001)
        for tau in self.taus:
            for cfg in CONFIGS:
                base = TG.add_targets(self.df, spec, **cfg)
                trunc = TG.add_targets(self.df[self.df.date <= tau], spec, **cfg)
                for scramble_all in (False, True):
                    pert = TG.add_targets(perturb(self.df, tau, rng, scramble_all), spec, **cfg)
                    le, gt = self.df.date <= tau, self.df.date > tau
                    with self.subTest(tau=str(tau.date()), cfg=cfg, scramble_all=scramble_all):
                        for c in OUT_COLS:
                            self.assertTrue(np.array_equal(bits(base.loc[le, c]), bits(pert.loc[le, c])), c)
                            self.assertTrue(np.array_equal(bits(base.loc[le, c]), bits(trunc[c])), c)
                        if not gt.any():
                            continue  # tau = last date: nothing after it to perturb
                        self.assertFalse(np.array_equal(bits(base.loc[gt, "abn_oc"]), bits(pert.loc[gt, "abn_oc"])))
                        if base.loc[gt, "beta"].notna().any():
                            self.assertFalse(np.array_equal(bits(base.loc[gt, "beta"]), bits(pert.loc[gt, "beta"])))

    def check_masks(self, events, spec):
        base = TG.add_masks(self.df, events, spec)
        for tau in self.taus:
            fake = pd.DataFrame({"ticker": ["5706", "5711", "5713"], "category": "TANSHIN",
                                 "date": tau + pd.Timedelta(days=1), "note": "", "check_status": "",
                                 "check_note": ""})
            m = TG.add_masks(self.df, pd.concat([events, fake], ignore_index=True), spec)
            le = self.df.date <= tau
            for c in ("excl_d2", "excl_forecast_eval"):
                self.assertTrue(base.loc[le, c].equals(m.loc[le, c]), c)


class TestLookAheadSynthetic(LookAhead, unittest.TestCase):
    def setUp(self):
        self.df = synth_panel(n_dates=700, seed=5)
        d = sorted(self.df.date.unique())
        self.taus = [pd.Timestamp(d[k]) for k in (100, 300, 451, 699)]  # before/at/after beta start, last

    def test_targets(self):
        self.check(Spec.load())


class TestLookAheadRealDev(LookAhead, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = IO.load_dev()[REAL_COLS].copy()   # target/flag/gap columns only: no FX column
        d.attrs = {"provenance": "dev_real"}
        cls.dev = d
        cls.events = IO.load_events_firm()

    def setUp(self):
        self.df = self.dev
        self.taus = [pd.Timestamp(t) for t in ("2016-06-30", "2018-12-28", "2021-06-30")]

    def test_targets(self):
        self.assertFalse([c for c in self.df.columns if c.startswith(("usdjpy", "eurusd"))])
        self.check(Spec.load())

    def test_masks(self):
        self.check_masks(self.events, Spec.load())


class TestA7Reference(unittest.TestCase):
    """Pins A7(a): Isaiah's reference moment code == targets.past_beta, bit for bit."""

    def test_reference_equals_past_beta(self):
        d = A7.load()
        for w in (60, 500, "expanding"):
            rb, ib = A7.reference_beta(d, w), A7.impl_beta(d, w)
            self.assertTrue(np.array_equal(rb.to_numpy(), ib.to_numpy(), equal_nan=True), w)
        v, _ = A7.table(d, A7.impl_beta)
        for w in A7.WINDOWS:
            for j in range(3):
                self.assertLess(abs(v[w][j] / A7.PROMPT_TABLE[w][j] - 1), A7.TOL_PROMPT)

    def test_a7_decision_rule_passes(self):
        # Amended A7(b) rule (Isaiah, 2026-10-01): windows compared on common rows; report exits 0.
        import contextlib, io as _io
        with contextlib.redirect_stdout(_io.StringIO()):
            self.assertEqual(A7.main(), 0)
        md = (ROOT / "reports" / "A_hedge_efficiency.md").read_text(encoding="utf-8")
        self.assertIn("DECISION TABLE", md)
        self.assertIn("superseded", md)


if __name__ == "__main__":
    unittest.main()
