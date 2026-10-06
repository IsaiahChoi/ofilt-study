import itertools
import os
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ofilt.drift import schema as SC  # noqa: E402
from ofilt.drift.spec import Spec, REPO_ROOT  # noqa: E402

DEV = Path(os.environ.get("OFILT_DATA_DIR", "/mnt/project")) / "panel_dev.csv"


def _panel_columns():
    return list(pd.read_csv(DEV, nrows=0).columns)  # header only: schema, no statistics


class TestGroups(unittest.TestCase):
    def test_pairwise_disjoint(self):
        for (a, ga), (b, gb) in itertools.combinations(SC.GROUPS.items(), 2):
            self.assertFalse(ga & gb, f"{a} and {b} overlap: {sorted(ga & gb)}")

    def test_sizes(self):
        self.assertEqual(len(SC.PRE_OPEN_FEATURES), 20)
        self.assertEqual(len(SC.PROVENANCE), 16)        # P50 (row 4)
        self.assertEqual(len(SC.AT_OPEN), 6)
        self.assertEqual(len(SC.CONTEMPORANEOUS), 2)
        self.assertEqual(len(SC.PRE_OPEN_ROBUSTNESS), 7)

    def test_every_panel_column_in_exactly_one_group(self):
        cols = _panel_columns()
        self.assertEqual(len(cols), 60)   # P50 (row 5)
        for c in cols:
            hits = [n for n, g in SC.GROUPS.items() if c in g]
            self.assertEqual(len(hits), 1, f"{c} in {hits}")
        self.assertEqual(SC.all_grouped_columns(), frozenset(cols),
                         "schema lists a column the panel lacks, or vice versa")

    def test_unknown_columns_fail_closed(self):
        for c in ("ao_new", "y_new", "usdjpy_new", "oc_lag2", "beta", ""):
            with self.assertRaises(SC.UnknownColumnError):
                SC.classify(c)


class TestAllowlist(unittest.TestCase):
    def test_allowed(self):
        SC.assert_features_allowed(sorted(SC.PRE_OPEN_FEATURES))
        SC.assert_features_allowed(sorted(SC.DERIVED_FEATURES))
        SC.assert_features_allowed(["noise_N01"])

    def test_every_non_feature_group_member_refused(self):
        for name, g in SC.GROUPS.items():
            if name == "PRE_OPEN_FEATURES":
                continue
            for c in g:
                with self.subTest(col=c):
                    with self.assertRaises(SC.FeatureNotAllowedError):
                        SC.assert_features_allowed(["usdjpy_ret", c])

    def test_unknown_refused(self):
        with self.assertRaises(SC.FeatureNotAllowedError):
            SC.assert_features_allowed(["usdjpy_ret", "ao_gap_new"])

    def test_derived_sources(self):
        self.assertEqual(SC.feature_sources(["rv_per_bar"]), {"usdjpy_rv", "usdjpy_bars"})
        self.assertEqual(SC.feature_sources(["jumpshare", "spy_oc"]), {"usdjpy_rv", "usdjpy_bv", "spy_oc"})
        for name, src in SC.DERIVED_FEATURES.items():
            self.assertTrue(src <= SC.PRE_OPEN_FEATURES | SC.PERMITTED_DERIVED_SOURCES, name)
        self.assertEqual(SC.PERMITTED_DERIVED_SOURCES, {"usdjpy_bars"})


class TestSelectFeatures(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "usdjpy_ret": [0.01, -0.02, 0.0, np.nan],
            "usdjpy_rv": [4e-5, 1e-5, 0.0, 2e-5],
            "usdjpy_bv": [3e-5, 2e-5, 0.0, np.nan],
            "usdjpy_bars": [1079, 1079, 3959, 1079],
            "window_hours": [17.983333, 65.983333, 18.0, 17.483333],
            "us_n_sessions": [1, 1, 0, 1],
            "open": [1.0, 2, 3, 4], "y_oc": [0.1, 0.2, 0.3, 0.4],
        })

    def test_derived_values(self):
        f = SC.select_features(self.df, ["long_window", "jumpshare", "rv_per_bar", "e_pos", "e_neg",
                                         "no_us_session", "usdjpy_ret"])
        np.testing.assert_array_equal(f["long_window"], [0, 1, 0, 0])   # 18.0 is not > 18
        np.testing.assert_allclose(f["jumpshare"].to_numpy()[:3], [0.25, 0.0, 0.0])  # clipped at 0; rv=0 -> 0
        self.assertTrue(np.isnan(f["jumpshare"].iloc[3]))
        np.testing.assert_allclose(f["rv_per_bar"], self.df.usdjpy_rv / self.df.usdjpy_bars)
        np.testing.assert_array_equal(f["e_pos"].to_numpy()[:3], [0.01, 0.0, 0.0])
        np.testing.assert_array_equal(f["e_neg"].to_numpy()[:3], [0.0, -0.02, 0.0])
        np.testing.assert_array_equal(f["no_us_session"], [0, 0, 1, 0])
        self.assertEqual(list(f.columns)[-1], "usdjpy_ret")
        self.assertTrue(f.index.equals(self.df.index))

    def test_forbidden_in_production_path(self):
        for c in ("open", "y_oc", "usdjpy_bars", "audit_flag", "ao_gap_adj"):
            with self.assertRaises(SC.FeatureNotAllowedError):
                SC.select_features(self.df, ["usdjpy_ret", c])

    def test_synthetic_column_must_be_supplied(self):
        with self.assertRaises(KeyError):
            SC.select_features(self.df, ["noise_N01"])


class TestSpecConsistency(unittest.TestCase):
    def test_spec_columns_are_in_the_right_groups(self):
        sp = Spec.load()
        self.assertTrue(set(sp.inference_exclusion_flags) <= SC.EXCLUSION_FLAGS)
        self.assertTrue(set(sp.fx_block) <= SC.PRE_OPEN_FEATURES)
        self.assertTrue(set(sp.controls) <= SC.PRE_OPEN_FEATURES)
        self.assertTrue(set(sp.require_nonmissing) - {"beta"} <= SC.PRE_OPEN_FEATURES)
        self.assertIn(sp.hedge_oc_column, SC.TARGET_INPUTS)
        self.assertTrue(set(sp.raw("robustness.winsorize_fx.cols")) <= SC.PRE_OPEN_FEATURES)

    def test_secondary_family_strings_match_implementation(self):
        # AM-01 (2026-10-01): definitions now include the moderator main effects.
        from ofilt.drift import spec as SP
        sp = Spec.load()
        for k, v in SP.SECONDARY_DEFS.items():
            self.assertEqual(sp.raw(f"secondary_family_holm.{k}"), v)
        self.assertIn("long_window = 1[window_hours > 18]", SP.SECONDARY_DEFS["fx_x_longwindow"])
        self.assertEqual(SC.LONG_WINDOW_HOURS, 18.0)
        self.assertIn("clip((usdjpy_rv - usdjpy_bv)/usdjpy_rv, 0, 1)", SP.SECONDARY_DEFS["fx_x_jumpshare"])
        self.assertIn("usdjpy_rv/usdjpy_bars > rv_per_bar_dev_median", SP.SECONDARY_DEFS["fx_x_highrv"])
        self.assertEqual(sp.raw("forecast.models.M4"), SP.M4_DEF)

class TestNoPatternColumnSelection(unittest.TestCase):
    """Static check: no package module selects columns by prefix or pattern."""
    BAD = [r"filter\(\s*like\s*=", r"filter\(\s*regex\s*=", r"\.str\.startswith", r"\.str\.match",
           r"startswith\(\s*['\"](ao_|y_|usdjpy_|eurusd_)", r"endswith\(\s*['\"](_bars|_oc|_flag)"]

    def test_package_source(self):
        pkg = REPO_ROOT / "ofilt"
        for py in pkg.rglob("*.py"):
            src = py.read_text(encoding="utf-8")
            for pat in self.BAD:
                self.assertIsNone(re.search(pat, src), f"{py.relative_to(REPO_ROOT)} matches {pat}")


class TestP50FeaturePins(unittest.TestCase):
    PASS1 = {"usdjpy_ret", "usdjpy_rv", "usdjpy_bv", "eurusd_ret", "eurusd_rv", "spy_oc", "ewj_oc", "fcx_oc",
             "copx_oc", "us_n_sessions", "window_hours", "gap_adj_lag1", "oc_lag1", "range_lag1",
             "topix_oc_lag1", "boj_day", "sq_day", "sq_major", "exdiv_day", "div_exdate"}

    def test_pre_open_features_and_m7_unchanged(self):
        self.assertEqual(set(SC.PRE_OPEN_FEATURES), self.PASS1)       # P50: exactly the 20 Pass 1 columns
        from ofilt.drift.models.gbm import M7
        self.assertEqual(M7.features, tuple(sorted(self.PASS1)))       # M7's inputs unchanged (P43/P50)
        for c in SC.PRE_OPEN_ROBUSTNESS | SC.CONTEMPORANEOUS:
            with self.assertRaises(SC.FeatureNotAllowedError):
                SC.select_features(pd.DataFrame({c: [0.0]}), [c])


if __name__ == "__main__":
    unittest.main()
