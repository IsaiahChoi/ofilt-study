"""D2 (rebuild): machine-checkable claims of P22-P28 (docs/DECISIONS_P14_onward.md, adopted,
never edited) against the rebuilt repo. P28 numbers that the rebuilt C7 reproduces exactly
are asserted here; the ones that differ are listed in docs/REBUILD_VERIFICATION.md (D2) and
PASS1_STATUS.md Deviations, not asserted. Structural only; no data are read."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import c7_mc as C  # noqa: E402
from ofilt.drift import fctests as FT  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import registry as R  # noqa: E402
from ofilt.drift.models import gbm, ridge  # noqa: E402
from ofilt.drift.models import M0, M1, M2, M3, M4, M5, M7  # noqa: E402
from ofilt.drift.spec import Spec, SpecPendingError  # noqa: E402

SPEC_TEXT = (ROOT / "spec" / "analysis_spec_dev_v1.yaml").read_text()


class TestP22toP25(unittest.TestCase):
    def test_p22_tails_and_influence(self):
        s = Spec.load()
        self.assertEqual(s.value("robustness.huber"), {"c": 1.345, "scale": "1.4826*MAD of OLS residuals"})
        self.assertEqual(s.value("robustness.winsorize_fx.q"), [0.005, 0.995])
        self.assertEqual(s.value("robustness.winsorize_fx.values"),
                         {"usdjpy_ret": [-1.6482588843e-02, 1.4399911615e-02],
                          "eurusd_ret": [-1.6324806371e-02, 1.5438152188e-02]})
        self.assertEqual((s.value("robustness.influence_curve.unit"), s.value("robustness.influence_curve.k_max")),
                         ("date", 20))
        self.assertTrue(callable(I.fit_huber) and callable(I.influence_curve))
        for crisis in ("2020-03", "2024-08-01", "2025-04-02", "crisis"):            # named windows removed
            self.assertNotIn(crisis, str(s.value("robustness")))

    def test_p23_tost_pending_costs(self):                                       # AM-07 (P3-6): no longer pending
        s = Spec.load()
        primary = json.loads((ROOT / "docs" / "P3_RUN_CONFIG.json").read_text(encoding="utf-8"))["sesoi"]["primary"]
        self.assertEqual({k: s.value(f"equivalence.{k}") for k in ("test", "alpha", "sesoi")},
                         {"test": "TOST", "alpha": 0.05, "sesoi": primary})
        self.assertTrue(s.value("equivalence.viability").startswith("viable (D2.6, P3-5)"))
        self.assertEqual(s.sesoi(), primary)

    def test_p24_fraction_unpriced(self):
        s = Spec.load()
        self.assertIn("delta_cc = delta_gap + b", s.value("fraction_unpriced.f"))
        self.assertEqual(s.value("fraction_unpriced.ci"), ["delta_method", "fieller"])
        status = str(s.value("fraction_unpriced.status"))
        self.assertIn("2022", status)
        self.assertTrue(callable(I.fit_joint))

    def test_p25_secondary_family(self):
        s = Spec.load()
        fam = s.value("secondary_family_holm")
        four = ["fx_x_longwindow", "fx_x_jumpshare", "fx_x_highrv", "fx_asymmetry"]
        self.assertEqual(list(I.SECONDARY_TERMS), four)                             # Holm runs over these four
        self.assertEqual([k for k in fam if k != "rv_per_bar_dev_median"], four)    # + highrv's threshold key
        self.assertEqual((fam["rv_per_bar_dev_median"], s.rv_per_bar_dev_median()), (1.2950114214e-08,) * 2)
        self.assertIn("long_window + usdjpy_ret * long_window", fam["fx_x_longwindow"])   # AM-01 main effects
        self.assertIn("jumpshare + usdjpy_ret * jumpshare", fam["fx_x_jumpshare"])
        self.assertIn("highrv + usdjpy_ret * highrv", fam["fx_x_highrv"])
        self.assertIn("1.2950114214e-08", SPEC_TEXT)                                 # dev median rv per bar


class TestP26P27(unittest.TestCase):
    def test_p26_ladder_and_comparisons(self):
        s = Spec.load()
        models = s.value("forecast.models")
        names = list(models) if isinstance(models, dict) else [m if isinstance(m, str) else next(iter(m)) for m in models]
        self.assertEqual(names, ["M0", "M1", "M2", "M3", "M4", "M5", "M7"])          # M6 dropped
        self.assertEqual(set(M2.features), {"spy_oc", "copx_oc", "eurusd_ret"})
        self.assertEqual(set(M3.features), {"spy_oc", "copx_oc", "eurusd_ret", "usdjpy_ret"})
        self.assertEqual(M0.features, ())
        self.assertEqual(ridge.ALPHA_MULTS, (1e-4, 1e-3, 1e-2, 1e-1, 1.0))
        self.assertTrue(set(M3.features) < set(M4.features) and set(M5.features) == set(M4.features))
        comps = FT.spec_comparisons(s)
        self.assertEqual([(c["test"], c["first"], c["second"], c["sided"]) for c in comps],
                         [("clark_west", "M3", "M2", "one"), ("clark_west", "M4", "M3", "one"),
                          ("clark_west", "M5", "M3", "one"), ("clark_west", "M7", "M1", "one"),
                          ("diebold_mariano", "M7", "M1", "two")])
        self.assertEqual(s.value("forecast.importance"),
                         {"method": "permutation", "unit": "date", "repeats": 20, "calibration": "noise_column"})
        self.assertEqual(s.value("forecast.test_aggregation"),
                         "mean across tickers within date, then time-series NW with lag_rule")
        self.assertTrue(M1 and M7)

    def test_p27_protocol_m7_registry(self):
        s = Spec.load()
        self.assertEqual({k: s.value(f"forecast.{k}") for k in ("scheme", "min_train_dates", "refit_every_dates",
                                                                  "pooled_across_tickers", "scaling")},
                         {"scheme": "expanding", "min_train_dates": 500, "refit_every_dates": 21,
                          "pooled_across_tickers": True, "scaling": "in_fold_only"})
        self.assertEqual(gbm.FIXED, {"learning_rate": 0.03, "min_samples_leaf": 100, "l2_regularization": 1.0,
                                     "early_stopping": False})
        self.assertEqual(gbm.GRID, tuple((d, n) for d in (2, 3) for n in (50, 100, 200, 400)))
        self.assertEqual(len(M7.features), 20)                                       # all PRE_OPEN sources
        for k in ("run_id", "utc", "git_commit", "spec_sha256", "data_sha256", "models", "grids", "folds",
                  "output_path"):
            self.assertIn(k, R.KEYS)                                                 # P27's fields (superset)
        self.assertIn("chosen", R.FOLD_KEYS)


class TestP28(unittest.TestCase):
    def test_slow_tier_artifacts_and_exact_matches(self):
        self.assertEqual(C.FULL["bands"], {"size": [0.02, 0.09], "power_040_min": 0.80})
        self.assertEqual([c[2] for c in C.FULL["cells"]], [300, 200, 200])
        mc = json.loads((ROOT / "reports" / "C7_mc.json").read_text())
        h1 = json.loads((ROOT / "reports" / "C7_h1_same_dgp.json").read_text())
        cells = mc["cells"]
        self.assertEqual((cells["power_040"]["cw"]["k"], cells["power_025"]["cw"]["k"]), (200, 179))   # P28 100%, 89.5%
        self.assertEqual(h1["h1_two_sided"]["k"], 175)                               # P28 87.5% two-sided
        self.assertEqual([round(100 * x, 1) for x in cells["power_040"]["cw"]["wilson95"]], [98.1, 100.0])
        self.assertEqual([round(100 * x, 1) for x in cells["power_025"]["cw"]["wilson95"]], [84.5, 93.0])
        lo, hi = C.FULL["bands"]["size"]
        self.assertTrue(lo <= cells["size"]["cw"]["rate"] <= hi)


if __name__ == "__main__":
    unittest.main()
