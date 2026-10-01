import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift.schema import PRE_OPEN_FEATURES  # noqa: E402
from test_io import make_temp_repo  # noqa: E402


def synth(n=600, seed=0, prov=True):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({"date": pd.bdate_range("2015-01-06", periods=n // 3).repeat(3),
                       "ticker": ["5706", "5711", "5713"] * (n // 3),
                       "usdjpy_ret": rng.normal(0, 4e-3, n), "eurusd_ret": rng.normal(0, 4e-3, n),
                       "y": rng.normal(0, 0.015, n)})
    return B.mark_synthetic(df) if prov else df


class TestGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = IO.load_dev()  # registers real target fingerprints as a side effect

    def test_dev_real_raises_in_main_repo(self):
        with self.assertRaises(B.BlindingError):
            B.require_unblinded(self.dev)
        with self.assertRaises(B.BlindingError):
            B.require_unblinded(self.dev.drop(columns=["y_oc"]), provenance="dev_real")

    def test_load_dev_registers_targets(self):
        labels = B.registered_labels()
        self.assertIn("dev_real:y_oc", labels)
        self.assertIn("dev_real:y_topix_oc", labels)
        self.assertGreater(B._REGISTRY["dev_real:y_oc"].size, 4000)

    def test_synthetic_passes(self):
        self.assertEqual(B.require_unblinded(synth()), "synthetic")
        bare = synth(prov=False)  # e.g. attrs dropped by a pandas op
        self.assertEqual(B.require_unblinded(bare, provenance="synthetic"), "synthetic")
        self.assertEqual(B.require_unblinded(provenance="synthetic", arrays={"y": bare.y}), "synthetic")

    def test_fail_closed(self):
        for kw in [dict(df=synth(prov=False)), dict(df=None), dict(provenance="Synthetic"),
                   dict(provenance=""), dict(provenance=1), dict(df=synth(prov=False), provenance="real")]:
            with self.subTest(kw=kw), self.assertRaises(B.BlindingError):
                B.require_unblinded(**kw)
        with self.assertRaises(B.BlindingError):
            B.require_unblinded(synth().to_numpy(), provenance="synthetic")
        d = synth(prov=False)
        d.attrs["provenance"] = None
        with self.assertRaises(B.BlindingError):
            B.require_unblinded(d)

    def test_conflict_raises(self):
        d = synth()
        with self.assertRaises(B.BlindingError):
            B.require_unblinded(d, provenance="dev_real")
        r = self.dev.copy()
        with self.assertRaises(B.BlindingError):
            B.require_unblinded(r, provenance="synthetic")

    def test_mislabelled_real_panel_raises(self):
        r = self.dev.copy()
        r.attrs = {"provenance": "synthetic"}
        with self.assertRaisesRegex(B.BlindingError, "y_oc|y_topix_oc"):
            B.require_unblinded(r)
        r.attrs = {}
        with self.assertRaises(B.BlindingError):
            B.require_unblinded(r, provenance="synthetic")

    def test_transformed_copies_caught(self):
        y = self.dev["y_oc"].to_numpy()
        cases = {"subset_bp_negated": -1e4 * y[::17], "percent": 100 * y[:400],
                 "two_thirds_real": np.r_[y[:400], np.random.default_rng(1).normal(0, .01, 200)]}
        for name, v in cases.items():
            d = B.mark_synthetic(pd.DataFrame({"target": v}))
            with self.subTest(name), self.assertRaises(B.BlindingError):
                B.require_unblinded(d)
        with self.assertRaises(B.BlindingError):
            B.require_unblinded(provenance="synthetic", arrays={"y": y[:500]})

    def test_real_predictors_with_synthetic_target_pass(self):
        cols = sorted(PRE_OPEN_FEATURES) + ["usdjpy_bars", "date", "ticker"]
        d = self.dev[cols].copy()
        d["y_sim"] = np.random.default_rng(2).normal(0, 0.015, len(d))
        d.attrs = {"provenance": "synthetic"}
        self.assertEqual(B.require_unblinded(d), "synthetic")  # oc_lag1 exempt; bar counts low-info

    def test_tick_grid_collision_margin(self):
        # Real gap columns collide with y_oc keys (tick-grid ratios) but must stay well clear.
        for c in ("ao_gap_adj", "ao_gap_raw", "ao_topix_gap"):
            frac, n = B.match_fraction(self.dev[c])
            self.assertLess(frac, 0.30, c)          # measured 0.219 / 0.218 / 0.002 at A4
            self.assertLess(frac, B.MATCH_FRAC / 1.5, c)
        d = self.dev[["ao_gap_adj", "ao_gap_raw", "ao_topix_gap", "usdjpy_ret"]].copy()
        d["y_sim"] = np.random.default_rng(4).normal(0, 0.015, len(d))
        d.attrs = {"provenance": "synthetic"}
        self.assertEqual(B.require_unblinded(d), "synthetic")
        small = B.mark_synthetic(pd.DataFrame({"t": self.dev["y_oc"].to_numpy()[:60]}))
        self.assertEqual(B.require_unblinded(small), "synthetic")  # documented limit: < MIN_DISTINCT

    def test_false_positive_rate(self):
        z = np.random.default_rng(3).standard_t(5, 50_000) * 0.015
        frac, n = B.match_fraction(z)
        self.assertGreater(n, 49_000)
        self.assertLess(frac, 1e-3)

    def test_mantissa_keys(self):
        x = np.array([0.0123456789, -3.14159265e-5, 2.71828182846])
        k = B.mantissa_keys(x)
        self.assertTrue(np.array_equal(k, B.mantissa_keys(-1e4 * x)))
        self.assertTrue(np.array_equal(k, B.mantissa_keys(np.r_[x, 0.0, np.nan, np.inf])))
        self.assertEqual(B.mantissa_keys([1079.0, 3450.0, 18.0, 0.25]).size, 0)  # low-info ignored

    def test_tag_gate_in_temp_repo(self):
        d = synth(prov=False)
        d.attrs["provenance"] = "dev_real"
        with tempfile.TemporaryDirectory() as t:
            repo = make_temp_repo(Path(t))
            g = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
            with mock.patch.object(B, "_GUARD_REPO", repo), mock.patch.object(B, "_external_check_access", None):
                with self.assertRaises(B.BlindingError):
                    B.require_unblinded(d)
                subprocess.run(g + ["tag", "spec-dev-v1", "side"], check=True)  # not an ancestor
                with self.assertRaises(B.BlindingError):
                    B.require_unblinded(d)
                subprocess.run(g + ["tag", "-d", "spec-dev-v1"], check=True, capture_output=True)
                subprocess.run(g + ["tag", "spec-dev-v1", "HEAD"], check=True)
                self.assertEqual(B.require_unblinded(d), "dev_real")
                c = synth(prov=False)
                c.attrs["provenance"] = "confirm_real"
                with self.assertRaisesRegex(B.BlindingError, "prereg-v1"):
                    B.require_unblinded(c)  # spec tag alone is not enough for confirmation data
                subprocess.run(g + ["tag", "prereg-v1", "HEAD"], check=True)
                self.assertEqual(B.require_unblinded(c), "confirm_real")

    def test_main_repo_guard_points_at_this_repo(self):
        self.assertEqual(Path(B._GUARD_REPO).resolve(), Path(IO._GUARD_REPO).resolve())


if __name__ == "__main__":
    unittest.main()
