"""P4-4c1 (P4Q38): ofilt/drift/confirm_claims.py and ofilt/drift/confirm_allowlist.py against
docs/P4_CONFIRM_CLAIMS_SPEC.md (version 1). Exactly the 15 test methods of its §5.2. Seeds are the spec seed
+ 8,400,000 + k (§5.1), disjoint from every earlier block. Every frame is synthetic; frames labelled dev_real or
confirm_real appear only in test 14's refused pairs. The document D1 is built once, as §5.1 says, with the run registry
patched to a temporary folder for the whole module (setUpModule, tearDownModule). Hand-made documents are deep copies
of D1 with named values set, evaluated by rows_from with D1's R12 gap, so that no frame is needed. R12's gap is
recomputed here from the frame C, built as P4-4a's §3.3 says, never from the module's internals."""
import ast
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import confirm_allowlist as AL  # noqa: E402
from ofilt.drift import confirm_claims as CC  # noqa: E402
from ofilt.drift import confirm_economic as CE  # noqa: E402
from ofilt.drift import confirm_forecast as CF  # noqa: E402
from ofilt.drift import confirm_inference as CI  # noqa: E402
from ofilt.drift import forecast as FC  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import registry as RG  # noqa: E402
from ofilt.drift import schema as SCH  # noqa: E402
from ofilt.drift import sim_full as SF  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

SPEC = Spec.load()
CFG = json.loads((ROOT / "docs" / "P4_CONFIRM_CONFIG.json").read_text(encoding="utf-8"))
SA = SF.Scenario(b=1.0, a2=0.6, delta_cc=1.5)
SHORT = SF.dev_calendar()[-900:]
ENTRY_KEYS = ["id", "item", "status", "values", "reason", "n_rows", "n_dates", "lag"]
P4C = [f"R{i}" for i in range(10, 27)]
ALLOWLIST = ROOT / "ofilt" / "drift" / "confirm_allowlist.py"
CLAIMS = ROOT / "ofilt" / "drift" / "confirm_claims.py"
REGRESSORS = {"ewj_oc_jpy", "xau_ret", "n225_ret", "gotobi_day", "c_usdjpy_sess_ret", "c_eurusd_sess_ret"}
FILTERS = {"n225_stale_start_min", "n225_stale_end_min", "audit_flag", "excl_d2"}
COSTS = {"open", "close"}
FORECASTING = ("ofilt/drift/forecast.py", "ofilt/drift/fctests.py", "ofilt/drift/models/__init__.py",
               "ofilt/drift/models/linear.py", "ofilt/drift/models/ridge.py", "ofilt/drift/models/gbm.py",
               "ofilt/drift/confirm_forecast.py")
BANNED_CALLS = ("open", "read_csv", "to_csv", "read_bytes", "read_text", "write_text", "write_bytes", "to_parquet",
                "to_pickle", "to_excel")
BANNED_STRINGS = ("load_dev", "load_confirm", "load_events", "OFILT_DATA_DIR", "RUN_REGISTRY")
_PATCHES: list = []
_TMP = None
_CACHE: dict = {}


class ZeroM7(FC.ForecastModel):
    """The M7 stand-in of P4-4b2's tests: no feature, a zero forecast, no noise column."""
    name, features = "M7", ()

    def fit(self, X, y, ctx):
        pass

    def predict(self, X, ctx):
        return np.zeros(len(X))


def setUpModule():
    global _TMP
    _TMP = tempfile.TemporaryDirectory()
    folder = Path(_TMP.name)
    for attr, name in (("SYNTHETIC_PATH", "synthetic.jsonl"), ("REAL_PATH", "real.jsonl")):
        p = mock.patch.object(RG, attr, folder / name)
        p.start()
        _PATCHES.append(p)


def tearDownModule():
    for p in reversed(_PATCHES):
        p.stop()
    _TMP.cleanup()


def seed(k):
    return SPEC.seed + 8_400_000 + k


def scaled(df):
    """A copy with 5706's open, close and prev_close multiplied by 0.1, attrs kept (as P4-4b2's tests)."""
    out = df.copy()
    m = (out["ticker"].astype(str) == "5706").to_numpy()
    for c in ("open", "close", "prev_close"):
        out[c] = np.where(m, out[c].to_numpy(dtype=float) * 0.1, out[c].to_numpy(dtype=float))
    out.attrs = dict(df.attrs)
    return out


def frames():
    """D1's frames (dev, events, confirm), 5706's prices scaled."""
    if "frames" not in _CACHE:
        o = SF.simulate(seed(1), SA, dev_dates=SHORT)
        _CACHE["frames"] = (scaled(o.dev), o.events, scaled(o.confirm))
    return _CACHE["frames"]


def d1():
    """The full document D1 of §5.1: infer, then P4-4b1's and P4-4b2's rows filled."""
    if "D1" not in _CACHE:
        dev, events, conf = frames()
        doc = CI.infer(dev, events, conf)
        calls = CF.run_calls(dev, events, conf, spec=SPEC, factories={"M7": ZeroM7})
        doc = CF.fill(doc, CF.forecast_rows(calls))
        _CACHE["D1"] = CE.fill(doc, CE.economic_row(calls, dev, events, conf, spec=SPEC))
    return _CACHE["D1"]


def d1_rows():
    """claim_rows on D1 and its own frames, computed once."""
    if "rows" not in _CACHE:
        dev, events, conf = frames()
        _CACHE["rows"] = CC.claim_rows(d1(), dev, events, conf, spec=SPEC)
    return _CACHE["rows"]


def rows_of(doc):
    """rows_from on a hand-made document, with D1's R12 gap (G1)."""
    return CC.rows_from(doc, d1_rows()["R12"]["values"]["a2_gap"], spec=SPEC)


def hand(licensed=None):
    """A deep copy of D1; licensed True or False sets mode confirmation and provenance confirm_real or synthetic."""
    doc = copy.deepcopy(d1())
    if licensed is not None:
        doc["mode"], doc["provenance"] = "confirmation", (B.CONFIRM_REAL if licensed else B.SYNTHETIC)
    return doc


def make_not_estimable(doc, rid):
    doc["rows"][rid].update(status="not_estimable", values=None, reason="set by the test")


def summary(c):
    return {"estimate": float(c["estimate"]), "se": float(c["se"]), "z": float(c["z"]), "p": float(c["p"]),
            "ci": [float(c["ci"][0]), float(c["ci"][1])]}


def string_constants(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def relabel(df, provenance):
    r = df.copy()
    attrs = {k: v for k, v in df.attrs.items() if k != "provenance"}
    if provenance is not None:
        attrs["provenance"] = provenance
    r.attrs = attrs
    return r


class TestConfirmClaims(unittest.TestCase):
    def assertNotEstimableFrom(self, e, rid):
        self.assertEqual(e["status"], "not_estimable")
        self.assertTrue(e["reason"].startswith(f"input {rid}"), e["reason"])
        self.assertIsNone(e["values"])
        self.assertEqual([e["n_rows"], e["n_dates"], e["lag"]], [None, None, None])

    # 1
    def test_allowlist_constants(self):
        self.assertEqual(AL.INFERENCE_ONLY_REGRESSORS, frozenset(REGRESSORS))
        self.assertEqual(AL.INFERENCE_ONLY_FILTERS, frozenset(FILTERS))
        self.assertEqual(AL.COST_INPUTS_ONLY, frozenset(COSTS))
        self.assertEqual(AL.INFERENCE_ONLY, frozenset(REGRESSORS | FILTERS | COSTS))
        self.assertEqual(AL.FORECASTING_MODULES, FORECASTING)
        for name in ("INFERENCE_ONLY_REGRESSORS", "INFERENCE_ONLY_FILTERS", "COST_INPUTS_ONLY", "INFERENCE_ONLY"):
            s = getattr(AL, name)
            self.assertIsInstance(s, frozenset, name)
            self.assertTrue(s.isdisjoint(SCH.PRE_OPEN_FEATURES), name)
            self.assertTrue(s.isdisjoint(SCH.ALLOWED_FEATURES), name)
        self.assertLessEqual(AL.INFERENCE_ONLY_REGRESSORS, SCH.PRE_OPEN_ROBUSTNESS | SCH.CONTEMPORANEOUS)
        self.assertLessEqual(AL.COST_INPUTS_ONLY, SCH.PROVENANCE)
        self.assertLessEqual(AL.INFERENCE_ONLY_FILTERS, SCH.PROVENANCE | SCH.ROBUSTNESS_ONLY | TG.MASK_COLUMNS)
        for rel in AL.FORECASTING_MODULES:
            self.assertTrue((ROOT / rel).is_file(), rel)

    # 2
    def test_no_forecasting_code_uses_the_allowlist(self):
        for rel in AL.FORECASTING_MODULES:
            path = ROOT / rel
            self.assertEqual(string_constants(path) & AL.INFERENCE_ONLY, set(), rel)
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imported = [a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names]
            imported += [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module]
            self.assertFalse([m for m in imported if "confirm_allowlist" in m], rel)

    # 3
    def test_the_robustness_rows_use_the_regressors(self):
        inf = string_constants(ROOT / "ofilt" / "drift" / "confirm_inference.py")
        self.assertLessEqual(AL.INFERENCE_ONLY_REGRESSORS | AL.INFERENCE_ONLY_FILTERS, inf)
        econ = string_constants(ROOT / "ofilt" / "drift" / "confirm_economic.py")
        self.assertLessEqual({"open", "close"}, econ)

    # 4
    def test_rows_and_schema(self):
        self.assertEqual(list(CC.ROWS), [i for i in CFG["rows"] if CI.ITEM_OF[i] == "P4-4c"])
        self.assertEqual(list(CC.ROWS), P4C)
        rows = d1_rows()
        self.assertEqual(list(rows), list(CC.ROWS))
        for rid, e in rows.items():
            self.assertEqual(list(e), ENTRY_KEYS, rid)
            self.assertEqual((e["id"], e["item"]), (rid, "P4-4c"))
            self.assertIn(e["status"], CI.STATUSES)
            self.assertNotEqual(e["status"], "pending", rid)
        filled = CC.fill(d1(), rows)
        self.assertEqual([rid for rid, e in filled["rows"].items() if e["status"] == "pending"], [])
        self.assertEqual({k: v for k, v in filled["rows"].items() if k not in CC.ROWS},
                         {k: v for k, v in d1()["rows"].items() if k not in CC.ROWS})
        text = CI.to_json(filled)
        self.assertNotIn("NaN", text)
        self.assertNotIn("Infinity", text)
        self.assertEqual(json.loads(text), filled)
        with self.assertRaises(ValueError):
            CC.fill(filled, rows)                                     # R10 (and the rest) no longer pending
        with self.assertRaises(ValueError):
            CC.fill(d1(), {k: v for k, v in rows.items() if k != "R26"})

    # 5
    def test_tier_i(self):
        for reject in (True, False):
            for lic in (True, False):
                doc = hand(lic)
                doc["rows"]["R4"]["values"]["reject"] = reject
                self.assertIs(CC.licensed(doc), lic)
                e = rows_of(doc)["R10"]
                v = e["values"]
                self.assertEqual(e["status"], "estimated")
                self.assertEqual((v["h1_rejected"], v["licensed"], v["claimed"]), (reject, lic, reject and lic))
                self.assertEqual((v["wording"], v["requires"], v["decision"]),
                                 (CFG["claims"]["tier_i"]["wording"], CFG["claims"]["tier_i"]["requires"], "P4Q18"))
        doc = hand()
        doc["provenance"] = B.CONFIRM_REAL
        doc["mode"] = "dev"
        self.assertIs(CC.licensed(doc), False)
        self.assertIs(CC.licensed(d1()), False)                      # synthetic
        doc = hand(True)
        make_not_estimable(doc, "R4")
        self.assertNotEstimableFrom(rows_of(doc)["R10"], "R4")

    # 6
    def test_tier_ii_conditions(self):
        cases = {   # name: (b_primary, b_with, b_without, p_with, reject), (conditions), claimed
            "all hold": ((1.0, 0.8, 1.0, 0.01, True), (True, True, True), True),
            "condition 1 fails": ((1.0, -0.8, 1.0, 0.01, True), (False, True, False), False),
            "condition 2 fails": ((1.0, 0.8, 1.0, 0.2, True), (True, False, True), False),
            "condition 3 fails": ((1.0, 0.4, 1.0, 0.01, True), (True, True, False), False),
            "b_without 0": ((1.0, 0.8, 0.0, 0.01, True), (True, True, False), False),
            "b_without negative": ((1.0, 0.8, -1.0, 0.01, True), (True, True, False), False),
            "H1 not rejected": ((1.0, 0.8, 1.0, 0.01, False), (True, True, True), False),
        }
        eligible = d1()["rows"]["O21"]["values"]["eligible_dates"]
        for name, ((bp, bw, bwo, p, reject), conds, claimed) in cases.items():
            doc = hand(True)
            doc["rows"]["R4"]["values"]["reject"] = reject
            doc["rows"]["O1"]["values"]["fit"]["estimate"] = bp
            o21 = doc["rows"]["O21"]["values"]
            o21["with"]["estimate"], o21["with"]["p"], o21["without"]["estimate"] = bw, p, bwo
            e = rows_of(doc)["R11"]
            v = e["values"]
            self.assertEqual(e["status"], "estimated", name)
            self.assertEqual((v["condition_1"], v["condition_2"], v["condition_3"]), conds, name)
            self.assertIs(v["claimed"], claimed, name)
            self.assertEqual(v["ratio"], None if bwo == 0 else bw / bwo, name)
            self.assertEqual((v["b_primary"], v["b_with"], v["b_without"], v["p_with"], v["h1_rejected"]),
                             (bp, bw, bwo, p, reject), name)
            self.assertEqual((v["eligible_dates"], v["licensed"], v["decision"]), (eligible, True, "P4Q16"), name)
            self.assertEqual(v["wording"], CFG["claims"]["tier_ii"]["wording"], name)

    # 7
    def test_tier_ii_inputs_not_estimable(self):
        for rid in ("O21", "O1", "R4"):
            doc = hand(True)
            make_not_estimable(doc, rid)
            self.assertNotEstimableFrom(rows_of(doc)["R11"], rid)
        doc = hand(True)
        make_not_estimable(doc, "O21")
        make_not_estimable(doc, "R4")
        self.assertNotEstimableFrom(rows_of(doc)["R11"], "R4")      # R4, O1, O21, in that order

    # 8
    def test_tier_iii_and_a2_gap(self):
        e = d1_rows()["R12"]
        v = e["values"]
        t = CFG["claims"]["tier_iii"]
        self.assertEqual(e["status"], "fixed")
        self.assertIs(v["claimed"], False)
        self.assertEqual((v["report_without_tier_reading"], v["a2_reading"], v["decision"]),
                         (t["report_without_tier_reading"], t["a2_reading"], "P4Q17"))
        self.assertEqual(v["rows"], {"H3": "O2", "copx_to_fcx": "O18", "xau_control": "O20", "raw_target": "O17"})
        dev, events, conf = frames()
        J = pd.concat([dev, conf], ignore_index=True)
        J.attrs = {"provenance": B.SYNTHETIC}
        T = TG.add_masks(TG.add_targets(J, SPEC), events, SPEC)
        C = T.loc[(T["date"] >= conf["date"].min()).to_numpy()]
        C.attrs = dict(T.attrs)
        D0 = I.build_design(C, SPEC)
        Dr = I.build_design(C, SPEC, target="raw_oc")
        abn = I.subset_design(D0, np.isin(D0.index, Dr.index))
        raw = I.subset_design(Dr, np.isin(Dr.index, abn.index))
        ra, rr = I.fit_dk(abn, SPEC), I.fit_dk(raw, SPEC)
        h3 = SPEC.h3_parameter
        expected = {"a2_raw": summary(rr.param(h3)), "a2_abn": summary(ra.param(h3)),
                    "difference": float(rr.param(h3)["estimate"]) - float(ra.param(h3)["estimate"]),
                    "n_rows": int(rr.n), "n_dates": int(rr.T)}
        G = v["a2_gap"]
        self.assertEqual(G, expected)
        self.assertEqual(G["difference"], G["a2_raw"]["estimate"] - G["a2_abn"]["estimate"])
        self.assertEqual(G["n_rows"], d1()["rows"]["O17"]["n_rows"])

    # 9
    def test_equivalence_wording(self):
        o11 = d1()["rows"]["O11"]["values"]
        eq = CFG["claims"]["equivalence"]
        for primary in (True, False):
            for lic in (True, False):
                doc = hand(lic)
                doc["rows"]["O10"]["values"]["equivalent"] = primary
                e = rows_of(doc)["R14"]
                v = e["values"]
                self.assertEqual(e["status"], "estimated")
                self.assertIs(v["viable"], True)
                self.assertEqual((v["equivalent_primary"], v["licensed"], v["claimed"]), (primary, lic, primary and lic))
                self.assertEqual((v["equivalent_low"], v["equivalent_high"]),
                                 (o11["low"]["equivalent"], o11["high"]["equivalent"]))
                self.assertEqual((v["wording"], v["beside"], v["mde80"], v["decision"]),
                                 (eq["wording"], eq["beside"], CFG["constants"]["mde80"], "P4Q19"))
        for rid in ("O10", "O11"):
            doc = hand(True)
            make_not_estimable(doc, rid)
            self.assertNotEstimableFrom(rows_of(doc)["R14"], rid)

    # 10
    def test_null_reading(self):
        for reject in (True, False):
            doc = hand()
            doc["rows"]["R4"]["values"]["reject"] = reject
            e = rows_of(doc)["R21"]
            v = e["values"]
            self.assertEqual(e["status"], "estimated")
            self.assertEqual((v["h1_rejected"], v["null"]), (reject, not reject))
            self.assertEqual(v["mde80"], 0.2471)
            self.assertEqual(v["mde80"], CFG["constants"]["mde80"])
            self.assertEqual((v["rule"], v["equivalence_row"], v["decision"]),
                             (CFG["claims"]["null_h1"]["rule"], "R14", "P4Q19"))
        doc = hand()
        make_not_estimable(doc, "R4")
        self.assertNotEstimableFrom(rows_of(doc)["R21"], "R4")

    # 11
    def test_fixed_rule_rows(self):
        rows = d1_rows()
        D1 = d1()
        outside = [rid for rid in D1["rows"] if rid not in CC.ROWS]
        expected = {
            "R13": {"viability": SPEC.value("equivalence.viability"), "viable": True, "recomputed": False,
                    "source": "P3-5; AM-07"},
            "R15": {"h1_method": "dk_normal", "cw_reference": "calibrated", "c_cw_cal": CFG["constants"]["c_cw_cal"],
                    "recomputed": False, "source": "P3-5"},
            "R16": {"rule": "DK-normal, selected for H1, applies to every other pre-registered DK test",
                    "reference": SPEC.value("inference.reference"), "source": "D3.5"},
            "R17": {"selected_for_confirmation": False, "recomputed": False, "source": "P73; P79"},
            "R18": {"recomputed": False, "not_examined_on_dev": CFG["not_examined_on_dev"]["items"],
                    "decision": "P4Q26", "source": "P75"},
            "R19": {"rows_flagged": [], "recomputed": False, "source": "P3-5"},
            "R22": {"spec_seed": SPEC.seed, "walk_forward_seed": "the spec seed (P4Q27)",
                    "fold_seed": "seed + 1000 * fold", "m7_noise": "default_rng([fold seed, stream])",
                    "importance": "default_rng([fold seed, 2, repeat])"},
            "R24": {"recovery": CFG["dry_run"]["recovery"]["rule"], "seeds": CFG["dry_run"]["seeds"]["rule"],
                    "item": "P4-5", "decisions": ["P4Q28", "P4Q29"]},
            "R26": {"rules": ["report every pre-registered result, including nulls",
                              "accuracy always next to its base rate", "nested comparisons by Clark-West",
                              "importance permutation-based only"],
                    "pending_rows": [],
                    "not_estimable_rows": [rid for rid in outside if D1["rows"][rid]["status"] == "not_estimable"]},
        }
        for rid, values in expected.items():
            e = rows[rid]
            self.assertEqual(e["status"], "fixed", rid)
            self.assertEqual(e["values"], values, rid)
            self.assertEqual([e["reason"], e["n_rows"], e["n_dates"], e["lag"]], [None] * 4, rid)
        self.assertIs(rows["R13"]["values"]["viable"], True)
        self.assertEqual(rows["R22"]["values"]["spec_seed"], SPEC.seed)
        doc = hand()
        make_not_estimable(doc, "O5")
        doc["rows"]["O45"].update(status="pending", values=None, reason=None)
        r26 = rows_of(doc)["R26"]["values"]
        self.assertEqual((r26["pending_rows"], r26["not_estimable_rows"]), (["O45"], ["O5"]))

    # 12
    def test_interim_wording_agreement(self):
        for h1, cw, agree in ((True, True, True), (True, False, False), (False, False, True)):
            doc = hand()
            doc["rows"]["R4"]["values"]["reject"] = h1
            doc["rows"]["O36"]["values"]["reject_calibrated"] = cw
            e = rows_of(doc)["R20"]
            self.assertEqual(e["status"], "fixed")
            self.assertEqual((e["values"]["h1_rejected"], e["values"]["cw_reject_calibrated"], e["values"]["agree"]),
                             (h1, cw, agree))
        doc = hand()
        make_not_estimable(doc, "O36")
        v = rows_of(doc)["R20"]["values"]
        self.assertEqual((v["h1_rejected"], v["cw_reject_calibrated"], v["agree"]),
                         (d1()["rows"]["R4"]["values"]["reject"], None, None))
        self.assertEqual((v["wording"], v["binding_description"], v["source"]),
                         ("H1 and the CW forecast test may disagree; disagreement is not by itself evidence against H1",
                          "the T3 cross-tab", "PLAN 4.4; P79"))

    # 13
    def test_one_shot_and_holdout(self):
        e = d1_rows()["R23"]
        self.assertEqual((e["status"], e["values"], e["reason"]),
                         ("not_applicable", None, "the one-shot rule applies to the confirmation panel only"))
        e = rows_of(hand(True))["R23"]
        self.assertEqual(e["status"], "fixed")
        self.assertEqual(e["values"], {"rule": "the confirmation panel is opened once, by the pre-registered script; "
                                               "any later change is a dated, labelled deviation",
                                       "source": "P13(c)"})
        e = d1_rows()["R25"]
        self.assertEqual(e["status"], "not_applicable")
        self.assertIn(CFG["forward_holdout"]["rule"], e["reason"])
        self.assertEqual(e["reason"], CFG["forward_holdout"]["rule"] + " (P4Q30); outside Pass 4")
        self.assertIsNone(e["values"])

    # 14
    def test_frames_must_match_the_document(self):
        dev, events, conf = frames()
        with self.assertRaises(ValueError):
            CC.claim_rows(d1(), dev, events)                         # the dev mode with a confirmation document
        cases = [(dev, relabel(conf, B.DEV_REAL)), (dev, relabel(conf, B.CONFIRM_REAL)),
                 (relabel(dev, B.DEV_REAL), conf), (relabel(dev, None), conf), (relabel(dev, B.CONFIRM_REAL), None)]
        for d, c in cases:
            before = B.registered_labels()
            with self.assertRaises(ValueError):
                CC.claim_rows(d1(), d, events, c, spec=SPEC)
            self.assertEqual(B.registered_labels(), before)
        with self.assertRaises(ValueError):
            CC.claim_rows(hand(True), dev, events, conf, spec=SPEC)  # the document's provenance is not the frames'
        self.assertEqual(list(d1_rows()), list(CC.ROWS))             # D1's own frames

    # 15
    def test_module_sources(self):
        al_tree = ast.parse(ALLOWLIST.read_text(encoding="utf-8"))
        for node in ast.walk(al_tree):
            if isinstance(node, ast.Import):
                self.fail(ast.dump(node))
            if isinstance(node, ast.ImportFrom):
                self.assertEqual((node.level, node.module), (0, "__future__"))
        assigned = {t.id for n in al_tree.body if isinstance(n, ast.Assign) for t in n.targets
                    if isinstance(t, ast.Name)}
        self.assertEqual(assigned, {"INFERENCE_ONLY_REGRESSORS", "INFERENCE_ONLY_FILTERS", "COST_INPUTS_ONLY",
                                    "INFERENCE_ONLY", "FORECASTING_MODULES"})
        self.assertFalse([n for n in al_tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.AugAssign,
                                                                    ast.AnnAssign))])
        cl_tree = ast.parse(CLAIMS.read_text(encoding="utf-8"))
        absolute = {"__future__", "copy", "math", "typing", "numpy", "pandas"}
        relative = {None: {"blind", "inference", "targets"}, "spec": {"Spec"},
                    "confirm_inference": {"ITEM_OF", "ROW_IDS", "STATUSES", "load_config", "_plain"},
                    "confirm_forecast": {"_check_inputs"}}
        for node in ast.walk(cl_tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertIn(a.name, absolute)
            elif isinstance(node, ast.ImportFrom):
                names = {a.name for a in node.names}
                if node.level == 0:
                    self.assertIn(node.module, absolute)
                else:
                    self.assertEqual(node.level, 1)
                    self.assertIn(node.module, relative)
                    self.assertLessEqual(names, relative[node.module], node.module)
        for path, tree in ((ALLOWLIST, al_tree), (CLAIMS, cl_tree)):
            called = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    f = node.func
                    called.append(f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None)
            for bad in BANNED_CALLS:
                self.assertNotIn(bad, called, path.name)
            src = path.read_text(encoding="utf-8")
            for s in BANNED_STRINGS:
                self.assertNotIn(s, src, path.name)
        functions = {n.name for n in cl_tree.body if isinstance(n, ast.FunctionDef)}
        assigned = {t.id for n in cl_tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
        self.assertLessEqual({"claim_rows", "rows_from", "fill", "licensed"}, functions)
        self.assertIn("ROWS", assigned)


if __name__ == "__main__":
    unittest.main()
