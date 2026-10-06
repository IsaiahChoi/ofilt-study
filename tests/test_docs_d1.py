"""D1 (rebuild): docs/DECISIONS_P14_onward.md is the adopted text, restored byte for byte from
the Project copy and pinned by hash (never edited by the rebuild). This module checks every
machine-checkable claim of P14-P21 against the rebuilt repo; claims carried by other tests are
cited in docs/REBUILD_VERIFICATION.md. Structural only: the one real-data read is the dev
panel's header (column names)."""
import hashlib
import inspect
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd  # noqa: E402

from ofilt.drift import calendar as CAL  # noqa: E402
from ofilt.drift import io  # noqa: E402
from ofilt.drift import schema as SC  # noqa: E402
from ofilt.drift import targets as T  # noqa: E402
from ofilt.drift.spec import SIZE_RULE, Spec, dk_lag  # noqa: E402

DOC = ROOT / "docs" / "DECISIONS_P14_onward.md"
DOC_SHA256 = "3d13201636ad459ce0bb61fb5e29385c2a7531cf7daad848d1a970706ca02dd0"   # Project copy, 2026-10-05
PROJECT_COPY = Path("/mnt/project/DECISIONS_P14_onward.md")


def report_rows(section_start: str, section_end: str) -> dict:
    """{window: [(value, n) for 5706, 5711, 5713]} from a table of reports/A_hedge_efficiency.md."""
    text = (ROOT / "reports" / "A_hedge_efficiency.md").read_text()
    i = text.index(section_start)
    j = text.find(section_end, i + 1)
    block = text[i:j if j > 0 else None]
    out = {}
    for line in block.splitlines():
        m = re.match(r"\| (\w+) \|(.*)\|$", line)
        if m and m.group(1) in {"60", "120", "250", "500", "expanding"}:
            cells = re.findall(r"([\d,]+\.\d)(?: \([^)]*\))? \[n=(\d+)\]", m.group(2))
            out[m.group(1)] = [(float(v.replace(",", "")), int(n)) for v, n in cells]
    return out


class TestAdoptedText(unittest.TestCase):
    def test_restored_byte_for_byte(self):
        self.assertEqual(hashlib.sha256(DOC.read_bytes()).hexdigest(), DOC_SHA256)
        if PROJECT_COPY.exists():
            self.assertEqual(DOC.read_bytes(), PROJECT_COPY.read_bytes())
        text = DOC.read_text()
        for p in range(14, 37):                                                 # P14-P36 all present, in order
            self.assertIn(f"**P{p}:", text)
        self.assertEqual([int(x) for x in re.findall(r"^\*\*P(\d+):", text, re.M)], list(range(14, 37)))


class TestP14toP16(unittest.TestCase):
    def test_p14_p15_design_and_parameters(self):
        s = Spec.load()
        self.assertEqual(s.value("model.fixed_effects"), "ticker")
        self.assertEqual(s.value("model.fx_block_common"), ["usdjpy_ret", "eurusd_ret"])
        self.assertEqual(s.value("model.controls_ticker_specific"), ["spy_oc", "copx_oc"])
        self.assertEqual((s.value("model.h1_parameter"), s.value("model.h3_parameter")), ("usdjpy_ret", "eurusd_ret"))
        self.assertEqual((s.value("inference.test"), s.value("inference.alpha")), ("two_sided", 0.05))

    def test_p16_at_open_refused(self):
        self.assertEqual(SC.AT_OPEN, frozenset({"ao_gap_adj", "ao_gap_raw", "ao_topix_gap", "ao_1306_gap_raw",
                                                "ao_1306_gap_adj", "ao_topix_gap_tradj"}))   # P50 (row 26)
        self.assertIn("auction-conditional spec retired", SC.GROUP_REASON["AT_OPEN"] if hasattr(SC, "GROUP_REASON")
                      else inspect.getsource(SC))
        df = pd.DataFrame({c: [0.0] for c in SC.AT_OPEN})
        for c in SC.AT_OPEN:
            with self.assertRaises(SC.FeatureNotAllowedError):
                SC.select_features(df, [c])
        rec = (ROOT / "PASS1_STATUS.md").read_text()                            # B6 record == P16's numbers
        for frag in ("pre -0.003, auction 0.162 (k*delta 0.167)", "surprise == pre (1e-16)",
                     "rho=0.7: 0.154 / 0.269 (0.15 / 0.267)"):
            self.assertIn(frag, rec)


class TestP17toP19(unittest.TestCase):
    def test_p17_beta_and_a7(self):
        s = Spec.load()
        self.assertEqual(s.value("target.beta"), {"method": "expanding", "min_periods": 250, "lag_days": 1,
                                                  "estimate_on": "non_excluded_rows", "continue_across_samples": True})
        self.assertIn("beta_rolling_250", s.value("robustness.others"))
        self.assertTrue(callable(T.past_beta))
        common = report_rows("## (b) DECISION TABLE", "\n## ")
        self.assertEqual(common["expanding"][1], (11639.9, 1140))               # 5711, common rows
        self.assertEqual(common["500"][1], (11659.7, 1140))
        for j in range(3):                                                      # expanding lowest for all three
            self.assertEqual(min(common, key=lambda w: common[w][j][0]), "expanding")
        text = (ROOT / "reports" / "A_hedge_efficiency.md").read_text()
        self.assertIn("| 500 | 24,073.9 (-0.245%) [n=1150] | 11,659.7 (-0.336%) [n=1140]", text)   # own rows
        self.assertIn("| expanding | 24,063.0 (+0.046%) [n=1178] | 11,662.6 (+0.006%) [n=1168]", text)
        self.assertAlmostEqual(100 * (11662.6 - 11659.7) / 11662.6, 0.025, delta=0.0005)   # "by 0.025%"
        c7 = (ROOT / "tests" / "test_validation_c7.py").read_text()             # "C7 for predictions"
        self.assertIn("class TestForecastLookAhead", c7)

    def test_p18_hedge_and_secondary(self):
        s = Spec.load()
        self.assertEqual(s.value("target.hedge_oc_column"), "y_1306_oc")   # AM-03 (row 7)
        self.assertEqual(s.value("target.secondary"), "raw_oc")
        self.assertEqual(T.HEDGE_GAP_FOR, {"y_topix_oc": "ao_topix_gap", "y_1306_oc": "ao_1306_gap_adj"})   # AM-03 (row 7)
        self.assertIn("if hedge not in HEDGE_GAP_FOR", inspect.getsource(T.add_targets))

    def test_p19_controls_and_robustness(self):
        s = Spec.load()
        self.assertEqual(s.value("data.require_nonmissing") if "require_nonmissing" in s.value("data")
                         else s.value("sample.require_nonmissing"), ["usdjpy_ret", "eurusd_ret", "spy_oc", "copx_oc", "beta"])
        design = set(s.value("model.fx_block_common")) | set(s.value("model.controls_ticker_specific"))
        self.assertNotIn("ewj_oc", design)
        self.assertNotIn("fcx_oc", design)
        rob = s.value("robustness.others")
        for r in ("ewj_yen_denominated", "copx_to_fcx", "exclude_boj_day", "exclude_sq_major"):   # AM-05 (row 8)
            self.assertIn(r, rob)
        self.assertIn("fx_x_longwindow", s.value("secondary_family_holm"))
        for c in ("gap_adj_lag1", "oc_lag1", "window_hours", "boj_day", "sq_major", "exdiv_day"):
            self.assertNotIn(c, design)


class TestP20P21(unittest.TestCase):
    def test_p20_allowlist(self):
        groups = {"KEYS": 2, "PRE_OPEN_FEATURES": 20, "EXCLUSION_FLAGS": 2, "INFORMATIONAL": 1, "ROBUSTNESS_ONLY": 1,
                  "AT_OPEN": 6, "TARGET_INPUTS": 3, "PROVENANCE": 16, "CONTEMPORANEOUS": 2,
                  "PRE_OPEN_ROBUSTNESS": 7}                                  # P50 (row 9)
        sets = {g: getattr(SC, g) for g in groups}
        self.assertEqual({g: len(v) for g, v in sets.items()}, groups)
        union = set().union(*sets.values())
        self.assertEqual(len(union), sum(groups.values()))                      # pairwise disjoint
        cols = list(pd.read_csv(io.DATA_DIR / io.DEV_FILE, nrows=0).columns)    # header only
        self.assertEqual((len(cols), set(cols)), (60, union))   # P50 (row 9)
        self.assertEqual(set(SC.DERIVED_FEATURES),
                         {"long_window", "jumpshare", "rv_per_bar", "e_pos", "e_neg", "no_us_session"})
        self.assertEqual(SC.PERMITTED_DERIVED_SOURCES, frozenset({"usdjpy_bars"}))
        self.assertEqual(SC.SYNTHETIC_FEATURES, frozenset({"noise_N01"}))
        df = pd.DataFrame({c: [1.0] for c in ("open", "close", "prev_close", "audit_flag", "spy_oc")})
        for c in ("open", "close", "prev_close", "audit_flag"):
            self.assertNotIn(c, SC.ALLOWED_FEATURES)
            with self.assertRaises(SC.FeatureNotAllowedError):
                SC.select_features(df, [c])
        with self.assertRaisesRegex(SC.FeatureNotAllowedError, "unknown column"):     # fail closed
            SC.select_features(df.assign(new_col=1.0), ["new_col"])

    def test_p21_inference_size_rule_calendar(self):
        s = Spec.load()
        self.assertEqual((dk_lag(1708), dk_lag(1013)), (7, 6))
        self.assertEqual((s.value("inference.se"), s.value("inference.small_sample_correction"),
                          s.value("inference.reference")), ("driscoll_kraay", "none", "normal"))
        self.assertEqual(s.value("inference.size_rule"), SIZE_RULE)
        for frag in ("5000 dev-calibrated sims", "[3.5%, 6.5%]", "stationary block bootstrap (mean block 5)",
                     "decided before tag", "1013 per ofilt.drift.calendar"):
            self.assertIn(frag, SIZE_RULE)
        self.assertEqual((CAL.N_CONF_DAYS, CAL.T_CONF, len(CAL.confirmation_calendar())), (1019, 1013, 1019))


if __name__ == "__main__":
    unittest.main()
