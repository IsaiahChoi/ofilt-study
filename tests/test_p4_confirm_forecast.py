"""P4-4b1 (P4Q36): ofilt/drift/confirm_forecast.py against docs/P4_CONFIRM_FC_SPEC.md (version 1). Exactly the 17
test methods of its §7.2. Seeds are the spec seed + 8,200,000 + k (§7.1), disjoint from every earlier block. Every
frame is synthetic; frames labelled dev_real or confirm_real appear only in test 4's refused pairs. The run registry is
patched to two files in a temporary folder for the whole module (setUpModule, tearDownModule), so no test writes to
the repository's registry or to the system temp registry. M7 runs with one candidate (§7.1) to keep the time down;
test 16 checks the production factories by inspection, without running them."""
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
from ofilt.drift import confirm_forecast as CF  # noqa: E402
from ofilt.drift import confirm_inference as CI  # noqa: E402
from ofilt.drift import fctests as FT  # noqa: E402
from ofilt.drift import forecast as FC  # noqa: E402
from ofilt.drift import models as MD  # noqa: E402
from ofilt.drift import registry as RG  # noqa: E402
from ofilt.drift import schema as SCH  # noqa: E402
from ofilt.drift import sim_full as SF  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))  # P6-1c: the tests folder, for run_state
import run_state as RS  # noqa: E402  (P6-1c, D2)
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.models.gbm import M7  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

SPEC = Spec.load()
MODULE = ROOT / "ofilt" / "drift" / "confirm_forecast.py"
CFG = json.loads((ROOT / "docs" / "P4_CONFIRM_CONFIG.json").read_text(encoding="utf-8"))
SA = SF.Scenario(b=1.0, a2=0.6, delta_cc=1.5)
SN = SF.Scenario.not_estimable()
CALENDARS = {"SHORT": SF.dev_calendar()[-900:], "TINY": SF.dev_calendar()[-300:], "DEFAULT": None}
FACTORIES = {"M7": lambda: M7(grid=((2, 50),))}
RUN_SPECS = {"R1": (1, SA, "SHORT", "confirmation"), "R1b": (1, SA, "SHORT", "confirmation"),
             "R2": (2, SN, "SHORT", "confirmation"), "R3": (3, SA, "DEFAULT", "dev"), "R4": (4, SA, "TINY", "dev")}
ENTRY_KEYS = ["id", "item", "status", "values", "reason", "n_rows", "n_dates", "lag"]
plain = CI._plain
_PATCHES: list = []
_TMP = None
_SIMS: dict = {}
_RUNS: dict = {}
_SNAP: dict = {}
LINES: dict = {}
_CACHE: dict = {}


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


def reg_lines():
    p = RG.SYNTHETIC_PATH
    if not p.exists():
        return 0
    with open(p, encoding="utf-8") as fh:
        return sum(1 for _ in fh)


def sim(k, scenario, cal):
    key = (k, scenario, cal)
    if key not in _SIMS:
        dates = CALENDARS[cal]
        _SIMS[key] = SF.simulate(seed(k), scenario) if dates is None else SF.simulate(seed(k), scenario, dev_dates=dates)
    return _SIMS[key]


def seed(k):
    return SPEC.seed + 8_200_000 + k


def inputs(label):
    k, sc, cal, mode = RUN_SPECS[label]
    o = sim(k, sc, cal)
    return o, (o.confirm if mode == "confirmation" else None)


def run(label):
    """run_calls for a run of §7.1, computed once; records the synthetic registry's lines added by the run."""
    if label not in _RUNS:
        o, conf = inputs(label)
        if label == "R1":
            _SNAP["R1"] = [(f.copy(deep=True), copy.deepcopy(f.attrs)) for f in (o.dev, o.events, o.confirm)]
        before = reg_lines()
        _RUNS[label] = CF.run_calls(o.dev, o.events, conf, spec=SPEC, factories=FACTORIES)
        LINES[label] = reg_lines() - before
    return _RUNS[label]


def rows_of(label):
    if ("rows", label) not in _CACHE:
        _CACHE[("rows", label)] = CF.forecast_rows(run(label))
    return _CACHE[("rows", label)]


def doc_of(label):
    if ("doc", label) not in _CACHE:
        o, conf = inputs(label)
        _CACHE[("doc", label)] = CI.infer(o.dev, o.events, conf)
    return _CACHE[("doc", label)]


def relabel(df, provenance):
    r = df.copy()
    attrs = {k: v for k, v in df.attrs.items() if k != "provenance"}
    if provenance is not None:
        attrs["provenance"] = provenance
    r.attrs = attrs
    return r


def refusals():
    """The five refused pairs of P4-4a's test 5, run once: (exceptions, labels unchanged, registry lines added)."""
    if "refusals" not in _CACHE:
        o = sim(1, SA, "SHORT")
        cases = [(o.dev, relabel(o.confirm, B.DEV_REAL)), (o.dev, relabel(o.confirm, B.CONFIRM_REAL)),
                 (relabel(o.dev, B.DEV_REAL), o.confirm), (relabel(o.dev, None), o.confirm),
                 (relabel(o.dev, B.CONFIRM_REAL), None)]
        out = []
        for dev, conf in cases:
            labels, lines = B.registered_labels(), reg_lines()
            try:
                CF.run_calls(dev, o.events, conf, spec=SPEC, factories=FACTORIES)
                exc = None
            except ValueError as e:
                exc = e
            out.append((exc, B.registered_labels() == labels, reg_lines() - lines))
        _CACHE["refusals"] = out
    return _CACHE["refusals"]


def frame_T(label):
    """The frame T of §3.1, built here."""
    o, conf = inputs(label)
    J = pd.concat([o.dev, conf], ignore_index=True) if conf is not None else o.dev.copy()
    J.attrs = {"provenance": B.SYNTHETIC}
    return TG.add_masks(TG.add_targets(J, SPEC), o.events, SPEC)


class TestConfirmForecast(unittest.TestCase):
    # 1
    def test_rows_items_and_calls(self):
        ids = [i for i in CFG["rows"] if CI.ITEM_OF[i] == "P4-4b" and i != "O45"]
        self.assertEqual(list(CF.ROWS), ids)
        self.assertEqual(len(CF.ROWS), 17)
        self.assertNotIn("O45", CF.ROWS)
        self.assertTrue(all(CI.ITEM_OF[i] == "P4-4b" for i in CF.ROWS))
        self.assertEqual(CF.M7_CALL, tuple(CFG["forecast"]["m7_call"]["models"]))
        self.assertEqual(CF.IMPORTANCE, tuple(CFG["forecast"]["importance"]["models"]))
        self.assertEqual(CF.MAIN_CALL, ("M0", "M1", "M2", "M3", "M4", "M5"))
        self.assertEqual(CF.MODEL_ROWS, {"O29": "M0", "O30": "M1", "O31": "M2", "O32": "M3", "O33": "M4",
                                         "O34": "M5", "O35": "M7"})
        c = CFG["constants"]["c_cw_cal"]
        self.assertIs(CF.cw_reject_calibrated(c, c), False)
        self.assertIs(CF.cw_reject_calibrated(c + 1e-12, c), True)

    # 2
    def test_entry_schema_and_json(self):
        rows = rows_of("R1")
        self.assertEqual(list(rows), list(CF.ROWS))
        for rid, e in rows.items():
            self.assertEqual(list(e), ENTRY_KEYS, rid)
            self.assertEqual((e["id"], e["item"]), (rid, "P4-4b"))
            self.assertIn(e["status"], CI.STATUSES)
            self.assertNotEqual(e["status"], "pending", rid)
        filled = CF.fill(doc_of("R1"), rows)
        text = CI.to_json(filled)
        self.assertNotIn("NaN", text)
        self.assertNotIn("Infinity", text)
        self.assertEqual(json.loads(text), filled)

    # 3
    def test_determinism_and_inputs_unchanged(self):
        self.assertEqual(rows_of("R1"), rows_of("R1b"))
        for name in ("main", "m7"):
            pd.testing.assert_frame_equal(getattr(run("R1"), name).preds, getattr(run("R1b"), name).preds,
                                          check_exact=True)
        o = sim(1, SA, "SHORT")
        run("R1")
        for f, (g, attrs) in zip((o.dev, o.events, o.confirm), _SNAP["R1"]):
            pd.testing.assert_frame_equal(f, g, check_exact=True)
            self.assertEqual(f.attrs, attrs)

    # 4
    def test_provenance_pairs_refused(self):
        for exc, labels_same, lines in refusals():
            self.assertIsInstance(exc, ValueError)
            self.assertTrue(labels_same)
            self.assertEqual(lines, 0)

    # 5
    def test_evaluation_restriction_and_protocol(self):
        calls, rows = run("R1"), rows_of("R1")
        o = sim(1, SA, "SHORT")
        E0 = o.confirm["date"].min()
        self.assertEqual(calls.E0, E0)
        r9 = rows["R9"]["values"]
        for k in ("scheme", "min_train_dates", "refit_every_dates", "pooled_across_tickers", "scaling"):
            self.assertEqual(r9[k], SPEC.value(f"forecast.{k}"), k)
        for name in ("main", "m7"):
            c = getattr(calls, name)
            expected = c.preds.loc[c.preds["date"] >= E0].reset_index(drop=True)
            pd.testing.assert_frame_equal(c.ev, expected, check_exact=True)
            self.assertTrue((c.preds["date"] < E0).any(), name)
            counts = c.ev.groupby(["model", "fold"]).size()
            self.assertEqual(list(c.folds_ev["n_test"]),
                             [int(counts.get((m, f), 0)) for m, f in zip(c.folds["model"], c.folds["fold"])])
            fl = c.folds.loc[c.folds["model"] == c.models[0]]
            part = r9["calls"][name]
            self.assertEqual(part["n_folds"], len(fl))
            self.assertEqual(part["first_test_date"], fl["test_start"].min().strftime("%Y-%m-%d"))
            self.assertEqual(part["last_test_date"], fl["test_end"].max().strftime("%Y-%m-%d"))
        for rid, model in CF.MODEL_ROWS.items():
            c = calls.m7 if model == "M7" else calls.main
            mr = c.ev.loc[c.ev["model"] == model]
            self.assertEqual((rows[rid]["n_rows"], rows[rid]["n_dates"]), (len(mr), mr["date"].nunique()), rid)

    # 6
    def test_primary_clark_west(self):
        calls, v = run("R1"), rows_of("R1")["O36"]["values"]
        lib = plain(FT.clark_west(calls.main.ev, "M3", "M2", SPEC))
        self.assertEqual({k: v[k] for k in lib}, lib)
        self.assertEqual(set(v) - set(lib), {"c_cw_cal", "reject_calibrated", "decision_reference", "exploratory"})
        self.assertEqual(v["reject_calibrated"], lib["stat"] > 1.411608406163672)
        self.assertIs(v["reject_calibrated"], True)
        self.assertIs(v["exploratory"], False)

    # 7
    def test_secondary_comparisons(self):
        calls, rows = run("R1"), rows_of("R1")
        for rid, (name, u, r) in (("O37", ("main", "M4", "M3")), ("O38", ("main", "M5", "M3")),
                                  ("O39", ("m7", "M7", "M1"))):
            self.assertEqual(rows[rid]["values"], plain(FT.clark_west(getattr(calls, name).ev, u, r, SPEC)), rid)
        self.assertEqual(rows["O40"]["values"], plain(FT.diebold_mariano(calls.m7.ev, "M7", "M1", SPEC)))

    # 8
    def test_oos_r2_rows(self):
        calls, rows = run("R1"), rows_of("R1")
        for rid, bench, pairs in (("O41", "M0", {"main": ("M1", "M2", "M3", "M4", "M5"), "m7": ("M7", "M1")}),
                                  ("O42", "M1", {"main": ("M0", "M2", "M3", "M4", "M5"), "m7": ("M7", "M0")})):
            v = rows[rid]["values"]
            self.assertEqual(v["failed"], {})
            for name, ms in pairs.items():
                self.assertEqual(sorted(v[name]), sorted(ms), (rid, name))
                for m in ms:
                    self.assertEqual(v[name][m], plain(FT.oos_r2(getattr(calls, name).ev, m, bench)), (rid, m))
        self.assertGreater(rows["O42"]["values"]["main"]["M3"]["pooled"], 0.0)

    # 9
    def test_pesaran_timmermann_rows(self):
        calls, v = run("R1"), rows_of("R1")["O43"]["values"]
        for name, ms in (("main", CF.MAIN_CALL), ("m7", CF.M7_CALL)):
            c = getattr(calls, name)
            self.assertEqual(sorted(v[name]), sorted(ms))
            for m in ms:
                lib = plain(FT.pesaran_timmermann(c.ev, m, c.folds_ev))
                for part in list(lib["per_ticker"].values()) + [lib["portfolio"]]:
                    if part["defined"] is False:
                        part["stat"], part["p"] = None, None
                self.assertEqual(v[name][m], lib, (name, m))
            m0 = v[name]["M0"]
            self.assertTrue(all(p["defined"] is False for p in list(m0["per_ticker"].values()) + [m0["portfolio"]]))

    # 10
    def test_importance_row(self):
        calls, e = run("R1"), rows_of("R1")["O44"]
        E0 = calls.E0
        K = calls.m7.folds.loc[calls.m7.folds["test_start"] >= E0]
        t = FC.importance_table(K, "M7")
        v = e["values"]
        self.assertEqual(v["table"], plain(t[list(CF.TABLE_COLUMNS)].to_dict("records")))
        self.assertEqual((v["repeats"], v["n_folds"], e["n_rows"]), (t.attrs["repeats"], t.attrs["n_folds"],
                                                                    t.attrs["n_rows"]))
        noise = [r for r in v["table"] if r["feature"] == FC.NOISE_COLUMN]
        self.assertEqual(len(noise), 1)
        self.assertIs(noise[0]["is_noise"], True)
        fl = calls.m7.folds.loc[calls.m7.folds["model"] == "M7"]
        self.assertEqual(v["folds_straddling_excluded"], int(((fl["test_start"] < E0) & (E0 <= fl["test_end"])).sum()))

    # 11
    def test_bars_zero_rows_dropped(self):
        calls, rows = run("R2"), rows_of("R2")
        conf = sim(2, SN, "SHORT").confirm
        bars = conf["usdjpy_bars"].to_numpy(dtype=float)
        le0 = np.isfinite(bars) & (bars <= 0)
        zero_dates = set(conf.loc[le0, "date"])
        main_part = rows["R9"]["values"]["calls"]["main"]
        self.assertEqual((main_part["bars_le_0_dates"], main_part["bars_le_0_rows"]), (len(zero_dates), int(le0.sum())))
        self.assertEqual((len(zero_dates), int(le0.sum())), (6, 18))
        self.assertFalse(set(calls.main.preds["date"]) & zero_dates)
        T = frame_T("R2")
        need = sorted(SCH.feature_sources(M7.features))
        kept = (np.isfinite(T["abn_oc"].to_numpy(dtype=float)) & T[need].notna().all(axis=1).to_numpy()
                & ~T["excl_forecast_eval"].astype(bool).to_numpy())
        first_test = calls.m7.folds["test_start"].min()
        expected = {d for d in zero_dates if d >= first_test and kept[(T["date"] == d).to_numpy()].any()}
        self.assertTrue(expected)
        self.assertEqual(set(calls.m7.preds["date"]) & zero_dates, expected)
        for rid in ("O33", "O34", "O37", "O38"):
            self.assertEqual(rows[rid]["status"], "estimated", rid)

    # 12
    def test_dev_mode(self):
        calls, rows = run("R3"), rows_of("R3")
        self.assertEqual(calls.mode, "dev")
        self.assertIsNone(calls.E0)
        for name in ("main", "m7"):
            c = getattr(calls, name)
            pd.testing.assert_frame_equal(c.ev, c.preds, check_exact=True)
            self.assertLess(c.ev["date"].max(), pd.Timestamp("2022-01-01"))
        v = rows["O36"]["values"]
        self.assertIs(v["exploratory"], True)
        self.assertIn("p", v)
        self.assertIn("reject_calibrated", v)
        self.assertEqual(rows["O44"]["values"]["folds_straddling_excluded"], 0)

    # 13
    def test_call_failure_not_estimable(self):
        calls, rows = run("R4"), rows_of("R4")
        for name in ("main", "m7"):
            c = getattr(calls, name)
            self.assertEqual(c.status, "failed")
            self.assertTrue(c.reason.startswith("walk_forward ("), c.reason)
        for rid in CF.ROWS:
            if rid == "R9":
                continue
            self.assertEqual(rows[rid]["status"], "not_estimable", rid)
            self.assertTrue(rows[rid]["reason"].startswith("walk_forward ("), rid)
        self.assertEqual(rows["R9"]["status"], "fixed")
        self.assertEqual([rows["R9"]["values"]["calls"][n]["status"] for n in ("main", "m7")], ["failed", "failed"])

    # 14
    def test_registry_routing(self):
        for label in ("R1", "R1b", "R2", "R3", "R4"):
            run(label)
        self.assertEqual({k: LINES[k] for k in ("R1", "R1b", "R2", "R3", "R4")},
                         {"R1": 2, "R1b": 2, "R2": 2, "R3": 2, "R4": 0})
        self.assertEqual([lines for _, _, lines in refusals()], [0] * 5)
        self.assertFalse(RG.REAL_PATH.exists())
        # P4Q6, P4Q40 (P4-6, test-change protocol): was `(ROOT / "RUN_REGISTRY.jsonl").stat().st_size == 0`.
        # After the dev run the registry holds exactly its two forecasting calls, both dev_real (reports/P4_runs/dev).
        reg = [json.loads(x) for x in (ROOT / "RUN_REGISTRY.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        dev_run = json.loads((ROOT / "reports" / "P4_runs" / "dev" / "runtime.json").read_text(encoding="utf-8"))
        # P6-1c (D2, condition 4; P6Q7; the pre-registration's §7.6; test-change protocol): the dev run's two assertions now
        # hold until the second request of the confirmation panel (the first added no registry line), which appends its two
        # confirm_real lines (tests/run_state.py). Was: the two, unconditionally.
        if RS.confirm_run_made():
            RS.check_registry_after(self, reg, dev_run)
        else:
            self.assertEqual(sorted(r["run_id"] for r in reg), sorted(dev_run["run_ids"].values()))
            self.assertEqual({r["provenance"] for r in reg}, {"dev_real"})

    # 15
    def test_fill_refuses_non_pending(self):
        doc, rows = doc_of("R1"), rows_of("R1")
        filled = CF.fill(doc, rows)
        self.assertEqual(list(filled["rows"]), list(doc["rows"]))
        for rid, e in filled["rows"].items():
            self.assertEqual(e, rows[rid] if rid in CF.ROWS else doc["rows"][rid], rid)
        self.assertEqual(filled["rows"]["O45"]["status"], "pending")
        self.assertEqual({k: filled[k] for k in filled if k != "rows"}, {k: doc[k] for k in doc if k != "rows"})
        bad_doc = copy.deepcopy(doc)
        bad_doc["rows"]["O29"]["status"] = "estimated"
        lacking = {k: v for k, v in rows.items() if k != "O44"}
        extra = dict(rows, O45=doc["rows"]["O45"])
        wrong_item = copy.deepcopy(rows)
        wrong_item["O30"]["item"] = "P4-4a"
        for d, r in ((bad_doc, rows), (doc, lacking), (doc, extra), (doc, wrong_item)):
            with self.assertRaises(ValueError):
                CF.fill(d, r)

    # 16
    def test_default_factories_are_the_registry(self):
        tree = ast.parse(MODULE.read_text(encoding="utf-8"))
        subs = [n for n in ast.walk(tree) if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Attribute)
                and n.value.attr == "REGISTRY" and isinstance(n.value.value, ast.Name) and n.value.value.id == "models"]
        self.assertTrue(subs)
        seen = []

        def recorder(df, model_factories, spec=None, **kw):
            seen.append((dict(model_factories), dict(kw)))
            raise ValueError("recorder: nothing runs")

        o = sim(1, SA, "SHORT")
        with mock.patch.object(FC, "walk_forward", recorder):
            calls = CF.run_calls(o.dev, o.events, o.confirm, spec=SPEC)
        self.assertEqual(len(seen), 2)
        for (facs, kw), names, imp in ((seen[0], CF.MAIN_CALL, None), (seen[1], CF.M7_CALL, list(CF.IMPORTANCE))):
            self.assertEqual(tuple(facs), names)
            for n in names:
                self.assertIs(facs[n], MD.REGISTRY[n], n)
            self.assertEqual(kw.get("importance"), imp)
        self.assertEqual([calls.main.status, calls.m7.status], ["failed", "failed"])

    # 17
    def test_module_source(self):
        src = MODULE.read_text(encoding="utf-8")
        tree = ast.parse(src)
        absolute = {"__future__", "dataclasses", "math", "typing", "numpy", "pandas"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertIn(a.name, absolute)
            elif isinstance(node, ast.ImportFrom):
                names = {a.name for a in node.names}
                if node.level == 0:
                    self.assertIn(node.module, absolute)
                elif node.module is None:
                    self.assertLessEqual(names, {"blind", "fctests", "forecast", "models", "targets"})
                elif node.module == "spec":
                    self.assertLessEqual(names, {"Spec"})
                else:
                    self.assertEqual(node.module, "confirm_inference")
                    self.assertLessEqual(names, {"ITEM_OF", "STATUSES", "TICKERS", "load_config", "to_json", "_plain"})
        called = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                called.append(f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None)
        for bad in ("open", "read_csv", "to_csv", "read_bytes", "read_text", "write_text", "write_bytes", "to_parquet",
                    "to_pickle", "to_excel"):
            self.assertNotIn(bad, called)
        for s in ("load_dev", "load_confirm", "load_events", "OFILT_DATA_DIR", "RUN_REGISTRY"):
            self.assertNotIn(s, src)
        functions = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
        assigned = {t.id for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
        self.assertLessEqual({"run_calls", "forecast_rows", "fill", "cw_reject_calibrated"}, functions)
        self.assertLessEqual({"ROWS", "MAIN_CALL", "M7_CALL", "MODEL_ROWS", "IMPORTANCE"}, assigned)


if __name__ == "__main__":
    unittest.main()
