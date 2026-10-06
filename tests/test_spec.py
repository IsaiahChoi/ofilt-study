import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml  # noqa: E402

from ofilt.drift import spec as S  # noqa: E402

VERBATIM = S.REPO_ROOT / "spec" / "analysis_spec_dev_v1.VERBATIM.yaml"
STAGE_A_FIELDS = {"robustness.winsorize_fx.values", "secondary_family_holm.rv_per_bar_dev_median"}


def _raw():
    return yaml.safe_load(S.DEFAULT_SPEC_PATH.read_text(encoding="utf-8"))


def _load_mutated(mutate):
    d = copy.deepcopy(_raw())
    mutate(d)
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as fh:
        yaml.safe_dump(d, fh, allow_unicode=True, sort_keys=False)
    return S.Spec.load(fh.name)


class TestSpecLoad(unittest.TestCase):
    def test_default_spec_loads(self):
        sp = S.Spec.load()
        self.assertEqual(sp.spec_id, "drift-dev-v1")
        self.assertEqual(sp.status, "DRAFT")
        self.assertEqual(len(sp.sha256), 64)
        self.assertEqual(sp.data_hash("dev_panel"),
                         "36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68")   # AM-04 (row 1)

    def test_unfilled_only_stage_a_fields(self):
        self.assertTrue(set(S.Spec.load().unfilled()) <= STAGE_A_FIELDS)

    def test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines(self):
        import json, re
        live = S.DEFAULT_SPEC_PATH.read_text(encoding="utf-8").splitlines()
        orig = VERBATIM.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(live), len(orig))
        md = (S.REPO_ROOT / "spec" / "SPEC_AMENDMENTS.md").read_text(encoding="utf-8")
        recs = [json.loads(l) for blk in re.findall(r"```jsonl\n(.*?)```", md, re.S)
                for l in blk.splitlines() if l.strip()]
        amended = {}
        for r in recs:  # every record must describe the files exactly (no stale or duplicate records)
            self.assertNotIn(r["line"], amended, r)
            self.assertEqual(orig[r["line"] - 1], r["old"], r["id"])
            self.assertEqual(live[r["line"] - 1], r["new"], r["id"])
            self.assertNotIn("TO_FILL", r["old"])
            amended[r["line"]] = r["id"]
        for n, (a, b) in enumerate(zip(orig, live), start=1):
            if a != b and n not in amended:
                self.assertIn("TO_FILL", a, f"unrecorded change at line {n}:\n{a}\n{b}")
                self.assertNotIn("TO_FILL", b)
        self.assertEqual(sorted(amended), [4, 7, 14, 33, 42, 43, 44, 45, 46, 62])    # + AM-04: 4, 7; AM-03: 14; AM-05: 42 (row 3)
        self.assertEqual({r["id"] for r in recs}, {"AM-01", "AM-02", "AM-03", "AM-04", "AM-05"})

    def test_am01_pins_reject_pre_amendment_text(self):
        import copy, yaml
        d = yaml.safe_load(S.DEFAULT_SPEC_PATH.read_text(encoding="utf-8"))
        S.validate(d)
        for path, bad in [(("secondary_family_holm", "fx_x_longwindow"), "usdjpy_ret * 1[window_hours > 18]"),
                          (("secondary_family_holm", "fx_x_highrv"),
                           "usdjpy_ret * 1[usdjpy_rv/usdjpy_bars > rv_per_bar_dev_median]"),
                          (("inference", "size_rule"),
                           "Pass 4: rejection at b=0 over 2000 dev-calibrated sims must be in [3.5%, 6.5%]; else primary "
                           "inference = stationary block bootstrap (mean block 5), decided before tag"),
                          (("forecast", "models", "M4"),
                           "M3 + e*1[long] + e*jumpshare + e*1[rv_per_bar > expanding past median] + min(e,0)")]:
            e = copy.deepcopy(d)
            node = e
            for k in path[:-1]:
                node = node[k]
            node[path[-1]] = bad
            with self.subTest(path=path), self.assertRaises(S.SpecError):
                S.validate(e)

    def test_am02_size_rule_matches_calendar(self):
        from ofilt.drift import calendar as C
        self.assertIn(f"T = T_conf", S.SIZE_RULE)
        self.assertIn(f"; {C.T_CONF} per ofilt.drift.calendar", S.SIZE_RULE)
        self.assertIn("over 5000 dev-calibrated sims", S.SIZE_RULE)
        self.assertEqual(S.Spec.load().raw("inference.size_rule"), S.SIZE_RULE)

    def test_typed_accessors(self):
        sp = S.Spec.load()
        self.assertEqual(sp.inference_exclusion_flags, ("earn_flag", "news_flag"))
        fe = sp.forecast_eval_exclusion
        self.assertEqual(fe.tanshin, (0, 1))
        self.assertEqual(fe.standalone_news, (1,))
        b = sp.beta
        self.assertEqual((b.method, b.min_periods, b.lag_days, b.estimate_on, b.continue_across_samples),
                         ("expanding", 250, 1, "non_excluded_rows", True))
        self.assertEqual(sp.fx_block, ("usdjpy_ret", "eurusd_ret"))
        self.assertEqual(sp.controls, ("spy_oc", "copx_oc"))
        self.assertEqual((sp.h1_parameter, sp.h3_parameter), ("usdjpy_ret", "eurusd_ret"))
        self.assertEqual(sp.hedge_oc_column, "y_1306_oc")   # AM-03 (row 2)
        self.assertEqual(sp.alpha, 0.05)
        self.assertEqual(sp.seed, 20261001)
        self.assertEqual(sp.huber_c, 1.345)
        self.assertEqual(sp.influence_k_max, 20)


class TestToFillRefusal(unittest.TestCase):
    def _unfilled(self):
        def m(d):
            d["robustness"]["winsorize_fx"]["values"] = "TO_FILL"
            d["secondary_family_holm"]["rv_per_bar_dev_median"] = "TO_FILL"
        return _load_mutated(m)

    def test_refuses_to_fill(self):
        sp = self._unfilled()
        self.assertEqual(set(sp.unfilled()), STAGE_A_FIELDS)
        with self.assertRaises(S.SpecIncompleteError):
            sp.winsor_bounds()
        with self.assertRaises(S.SpecIncompleteError):
            sp.rv_per_bar_dev_median()
        with self.assertRaises(S.SpecIncompleteError):
            sp.assert_analysis_ready()
        with self.assertRaises(S.SpecIncompleteError):
            sp.value("robustness")  # TO_FILL nested anywhere inside is refused
        self.assertEqual(sp.raw("robustness.winsorize_fx.values"), "TO_FILL")  # raw is allowed

    def test_filled_values_accepted(self):
        def m(d):
            d["robustness"]["winsorize_fx"]["values"] = {"usdjpy_ret": [-0.01, 0.01], "eurusd_ret": [-0.008, 0.009]}
            d["secondary_family_holm"]["rv_per_bar_dev_median"] = 1.5e-08
        sp = _load_mutated(m)
        sp.assert_analysis_ready()
        self.assertEqual(sp.winsor_bounds()["eurusd_ret"], (-0.008, 0.009))
        self.assertEqual(sp.rv_per_bar_dev_median(), 1.5e-08)

    def test_sesoi_pending(self):
        with self.assertRaises(S.SpecPendingError):
            S.Spec.load().sesoi()


class TestLagRule(unittest.TestCase):
    def test_known_values(self):
        self.assertEqual(S.dk_lag(100), 4)
        self.assertEqual(S.dk_lag(1708), 7)   # dev days
        self.assertEqual(S.dk_lag(983), 6)
        self.assertEqual(S.dk_lag(1), 1)
        last = 0
        for T in range(1, 6000):
            v = S.dk_lag(T)
            self.assertGreaterEqual(v, last)
            last = v

    def test_rejects_bad_T(self):
        for bad in (0, -3, 2.5, True):
            with self.assertRaises(ValueError):
                S.dk_lag(bad)


class TestValidationRejects(unittest.TestCase):
    CASES = {
        "m6_present": lambda d: d["forecast"]["models"].__setitem__("M6", "kalman"),
        "lag_rule_edit": lambda d: d["inference"].__setitem__("lag_rule", "floor(T**0.25)"),
        "se_edit": lambda d: d["inference"].__setitem__("se", "newey_west"),
        "bad_sha": lambda d: d["data"].__setitem__("dev_panel_sha256", "abc"),
        "extra_key": lambda d: d.__setitem__("lockbox", True),
        "missing_key": lambda d: d.pop("seeds"),
        "early_stopping_on": lambda d: d["forecast"]["models"]["M7"]["fixed"].__setitem__("early_stopping", True),
        "beta_lag_zero": lambda d: d["target"]["beta"].__setitem__("lag_days", 0),
        "bad_comparison": lambda d: d["forecast"]["comparisons"]["secondary"].append(["clark_west", "M9", "M3"]),
        "bad_day_token": lambda d: d["sample"]["forecast_eval_exclusion"].__setitem__("tanshin", ["D-1"]),
        "primary_cw_edit": lambda d: d["forecast"]["comparisons"]["primary_forecast"].__setitem__("sided", "two"),
        "fx_overlap": lambda d: d["model"]["controls_ticker_specific"].append("eurusd_ret"),
        "bad_winsor_values": lambda d: d["robustness"]["winsorize_fx"].__setitem__("values", {"usdjpy_ret": [0.1, -0.1]}),
    }

    def test_each_case_rejected(self):
        for name, mut in self.CASES.items():
            with self.subTest(case=name):
                with self.assertRaises(S.SpecError):
                    _load_mutated(mut)


if __name__ == "__main__":
    unittest.main()
