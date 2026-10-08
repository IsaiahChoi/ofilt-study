"""D3 (rebuild): machine-checkable claims of P29-P35 (docs/DECISIONS_P14_onward.md, adopted,
never edited) against the rebuilt repo. P30-P31 numbers are checked against the committed B7
pilot and B7b preview reports (produced before the C3 checkpoint, not by the rebuild), and
P31's two exceedance probabilities are recomputed independently. Plans and claim wording
(P32, most of P34-P35) are text-only and are listed, not tested. No data are read."""
import hashlib
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
sys.path.insert(0, str(Path(__file__).resolve().parent))  # P3-8b: the tests folder, for tag_state
import tag_state as TS  # noqa: E402  (P3-8b)


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
        dev_open = "spec-dev-v1" in tags  # P3-8b: was self.assertNotIn("spec-dev-v1", tags) ("Pass 1: neither tag exists"); the state on both sides of the tag
        if dev_open:  # P3-8b: with the tag, it is annotated, an ancestor of HEAD and on the frozen spec
            TS.check_spec_tag(self)  # P3-8b
        self.assertNotIn("prereg-v1", tags)
        df = pd.DataFrame({"date": pd.to_datetime(["2030-01-07"]), "ticker": ["5706"], "x": [0.123456789]})
        for prov, ok in ((B.SYNTHETIC, True), (B.DEV_REAL, dev_open), (B.CONFIRM_REAL, False), ("other", False)):  # P3-8b: was (B.DEV_REAL, False)
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
        if dev_open:  # P3-8b: with the tag, confirm_real is refused for prereg-v1 alone
            c = df.copy()  # P3-8b
            c.attrs = {"provenance": B.CONFIRM_REAL}  # P3-8b
            with self.assertRaisesRegex(B.BlindingError, r"\['prereg-v1'\]"):  # P3-8b
                B.require_unblinded(c)  # P3-8b

    def test_sealed_fit_opt_in_and_record(self):
        self.assertTrue(callable(S._sealed_blind_fit))
        ck = (ROOT / "tools" / "checkpoint.sh").read_text()
        self.assertIn("env -u OFILT_RUN_SEALED", ck)
        self.assertNotIn("OFILT_RUN_SEALED=1", ck)
        raw = (ROOT / "BLIND_FIT_LOG").read_bytes()
        lines = [json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
        self.assertEqual(len(lines), 7)                                          # DQ5: Pass 1's six lines and P3-4's line 7
        self.assertEqual(hashlib.sha256(b"".join(raw.splitlines(keepends=True)[:6])).hexdigest(),
                         "dad93285d2911abc6c7145c160d729df1126b24b439302bd8577cf407d397301")   # DQ5: lines 1-6 byte-identical
        self.assertTrue(all(x["provenance"] == B.DEV_REAL for x in lines))
        dev = "736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42"   # AM-04, P51: lines 1-6 are Pass 1 history (row 12)
        self.assertTrue(all(x["panel_sha256"] == dev for x in lines[:6]))        # lines 1-6 on the Pass 1 panel_dev.csv (DQ5)
        callers = [x["caller"] for x in lines]
        self.assertTrue(all("test_sim_b5" in c for c in callers[:3]))            # lines 1-3: B5 tests
        self.assertTrue(all("report_B7.py" in c for c in callers[3:5]))          # lines 4-5: report_B7
        self.assertIn("report_B7b.py", callers[5])                               # line 6: report_B7b
        l7 = lines[6]                                                            # DQ5: line 7, the P3-4 sealed fit, by its fields
        self.assertEqual(set(l7), {"utc", "provenance", "panel_sha256", "spec_sha256", "n_rows_input", "caller"})
        self.assertEqual(l7["panel_sha256"], "36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68")   # AM-04's dev panel
        self.assertEqual(l7["spec_sha256"], "0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee408561f68f96fd94d3b0f9")   # the configuration's spec_sha256
        self.assertEqual(l7["n_rows_input"], 5124)
        self.assertIn("tools/p3_sealed_run.py", l7["caller"])


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
        self.assertEqual(rob["others"], ["beta_rolling_250", "beta_rolling_500", "raw_target", "copx_to_fcx", "ewj_yen_denominated", "xau_control", "nikkei_proxy_p42", "mechanism_session_fx_gotobi", "exclusion_d_plus_2", "exclude_audit_flag", "exclude_boj_day", "exclude_sq_major", "post_2024_11_05_indicator_CONFIRMATION_ONLY", "per_ticker_slopes_holm"])   # AM-05 (row 10)
        self.assertNotIn("post_2024_11_05", (ROOT / "ofilt" / "drift" / "inference.py").read_text())   # "not yet"

    def test_p34_p35_named_artifacts(self):
        s = Spec.load()
        self.assertTrue(s.value("data.sealed_panel_sha256").startswith("b575272a"))   # AM-04 (row 11)
        self.assertIn("target", inspect.signature(F.walk_forward).parameters)         # T3: target y_sim
        self.assertTrue(hasattr(S, "DevCalibrator"))


if __name__ == "__main__":
    unittest.main()
