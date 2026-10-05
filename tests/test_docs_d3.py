"""D3 (rebuild): machine-checkable claims of P29-P35 (docs/DECISIONS_P14_onward.md, adopted,
never edited) against the rebuilt repo. P30-P31 numbers are checked against the committed B7
pilot and B7b preview reports (produced before the C3 checkpoint, not by the rebuild), and
P31's two exceedance probabilities are recomputed independently. Plans and claim wording
(P32, most of P34-P35) are text-only and are listed, not tested. No data are read."""
import inspect
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import forecast as F  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402


def find(obj, pred):
    """All dicts nested in obj satisfying pred."""
    out = []
    if isinstance(obj, dict):
        if pred(obj):
            out.append(obj)
        for v in obj.values():
            out += find(v, pred)
    elif isinstance(obj, list):
        for v in obj:
            out += find(v, pred)
    return out


class TestP29Blinding(unittest.TestCase):
    def test_tag_gates(self):
        tags = subprocess.run(["git", "-C", str(ROOT), "tag"], capture_output=True, text=True).stdout.split()
        self.assertNotIn("spec-dev-v1", tags)                                   # Pass 1: neither tag exists
        self.assertNotIn("prereg-v1", tags)
        df = pd.DataFrame({"date": pd.to_datetime(["2030-01-07"]), "ticker": ["5706"], "x": [0.123456789]})
        for prov, ok in ((B.SYNTHETIC, True), (B.DEV_REAL, False), (B.CONFIRM_REAL, False), ("other", False)):
            d = df.copy()
            d.attrs = {"provenance": prov}
            if ok:
                self.assertEqual(B.require_unblinded(d), prov)
            else:
                with self.assertRaises(B.BlindingError):
                    B.require_unblinded(d)
        with self.assertRaises(B.BlindingError):                                # missing provenance
            B.require_unblinded(df)
        d = df.copy()
        d.attrs = {"provenance": B.SYNTHETIC}
        with self.assertRaises(B.BlindingError):                                # attrs and kwarg must agree
            B.require_unblinded(d, provenance=B.DEV_REAL)
        self.assertTrue((ROOT / "ofilt" / "drift" / "_guards_fallback.py").exists())

    def test_sealed_fit_opt_in_and_record(self):
        self.assertTrue(callable(S._sealed_blind_fit))
        ck = (ROOT / "tools" / "checkpoint.sh").read_text()
        self.assertIn("env -u OFILT_RUN_SEALED", ck)
        self.assertNotIn("OFILT_RUN_SEALED=1", ck)
        lines = [json.loads(x) for x in (ROOT / "BLIND_FIT_LOG").read_text().splitlines() if x.strip()]
        self.assertEqual(len(lines), 6)                                          # "dev_real lines: 6"
        self.assertTrue(all(x["provenance"] == B.DEV_REAL for x in lines))
        dev = Spec.load().value("data.dev_panel_sha256")
        self.assertTrue(all(x["panel_sha256"] == dev for x in lines))            # all on panel_dev.csv
        callers = [x["caller"] for x in lines]
        self.assertTrue(all("test_sim_b5" in c for c in callers[:3]))            # lines 1-3: B5 tests
        self.assertTrue(all("report_B7.py" in c for c in callers[3:5]))          # lines 4-5: report_B7
        self.assertIn("report_B7b.py", callers[5])                               # line 6: report_B7b


class TestP30P31Power(unittest.TestCase):
    def test_p30_b7b_preview(self):
        d = json.loads((ROOT / "reports" / "B7b_size_preview.json").read_text())
        self.assertEqual((d["T"], d["lag"], d["flags"]), (1013, 6, []))
        cells = {c["b_sim"]: c for c in d["cells"]}
        self.assertEqual((cells[0.0]["reps"], cells[0.0]["reject_H1"]["k"], cells[0.0]["reject_H3"]["k"]),
                         (5000, 302, 296))                                       # 6.04%, 5.92%
        self.assertEqual([round(100 * x, 2) for x in cells[0.0]["reject_H1"]["wilson95"]], [5.41, 6.73])
        self.assertEqual([(cells[b]["reps"], cells[b]["reject_H1"]["k"]) for b in (0.1, 0.25, 0.4)],
                         [(1000, 225), (1000, 782), (1000, 985)])                # 22.5 / 78.2 / 98.5%
        self.assertEqual(round(d["mde80"]["probit_interpolated"], 3), 0.257)
        pooled = d["pooled_calibration"]["H1"]
        self.assertEqual((round(100 * pooled["coverage"]["rate"], 2), round(pooled["se_over_sd"], 3)), (93.91, 0.960))
        self.assertLess(abs(pooled["bias"]), 2 * pooled["bias_mc_se"])           # "bias ~ 0"

    def test_p31_calibration_numbers(self):
        pilot = json.loads((ROOT / "reports" / "B_sim_pilot.json").read_text())
        at983 = find(pilot, lambda x: x.get("T") == 983)
        self.assertTrue(at983)
        self.assertEqual(sorted(r["b_sim"] for r in at983), [0.0, 0.1, 0.25, 0.4])
        self.assertTrue(all(r["reps"] == 500 for r in at983))                   # 2,000 sims, equal cells
        # pooled over the 2,000 sims (B7 entry, Flag 10): b_hat - b_sim does not depend on b_sim
        pooled = (sum(r["mean_se"] for r in at983) / 4) / (sum(r["sd_b"] ** 2 for r in at983) / 4) ** 0.5
        self.assertEqual(round(pooled, 3), 0.954)                                # SE/sd 0.954 at T = 983
        self.assertEqual(round(100 * sum(r["coverage"] for r in at983) / 4, 2), 93.95)
        for p, quoted in ((0.0604, 0.086), (0.0673, 0.742)):                    # P(5000-rep rate > 6.5%)
            z = (0.065 - p) / (p * (1 - p) / 5000) ** 0.5
            self.assertEqual(round(float(stats.norm.sf(z)), 3), quoted)        # normal approximation


class TestP33toP35(unittest.TestCase):
    def test_p33_closed_robustness_list(self):
        rob = Spec.load().value("robustness")
        self.assertEqual(list(rob), ["huber", "winsorize_fx", "influence_curve", "others"])
        self.assertEqual(rob["others"], ["beta_rolling_250", "raw_target", "copx_to_fcx",
                                         "ewj_yen_denominated_REQUIRES_PASS2", "exclusion_d_plus_2",
                                         "exclude_audit_flag", "exclude_boj_day", "exclude_sq_major",
                                         "post_2024_11_05_indicator_CONFIRMATION_ONLY", "per_ticker_slopes_holm"])
        self.assertNotIn("post_2024_11_05", (ROOT / "ofilt" / "drift" / "inference.py").read_text())   # "not yet"

    def test_p34_p35_named_artifacts(self):
        s = Spec.load()
        self.assertTrue(s.value("data.sealed_panel_sha256").startswith("9c18a6c1"))   # superseded in Pass 2
        self.assertIn("target", inspect.signature(F.walk_forward).parameters)         # T3: target y_sim
        self.assertTrue(hasattr(S, "DevCalibrator"))


if __name__ == "__main__":
    unittest.main()
