"""P4-4c2 (P4Q39): ofilt/drift/confirm_run.py and tools/p4_confirm_run.py against docs/P4_CONFIRM_RUN_SPEC.md
(version 1). Exactly the 12 test methods of its §5.2. Seeds are the spec seed + 8,600,000 + k (§5.1), disjoint from
every earlier block. Every frame is synthetic; frames labelled dev_real or confirm_real appear only in test 11's refused
pairs. The script's dev branch is never run (only its refusals are tested), and the confirmation loader is called only
in test 8, with ACCESS_LOG and the data folder patched to temporary paths. setUpModule patches the run registry to a
temporary folder and io.ACCESS_LOG_PATH to a file in it; every output folder lies in a temporary directory. M7 is the
zero-forecast stand-in of P4-4b2's tests: through factories in build_document, patched into models.REGISTRY for the
script."""
import ast
import contextlib
import hashlib
import io as stdio
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import p4_confirm_run as SCRIPT  # noqa: E402
from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import confirm_claims as CC  # noqa: E402
from ofilt.drift import confirm_economic as CE  # noqa: E402
from ofilt.drift import confirm_forecast as CF  # noqa: E402
from ofilt.drift import confirm_inference as CI  # noqa: E402
from ofilt.drift import confirm_run as CR  # noqa: E402
from ofilt.drift import forecast as FC  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import models as MD  # noqa: E402
from ofilt.drift import registry as RG  # noqa: E402
from ofilt.drift import sim_full as SF  # noqa: E402
from ofilt.drift.spec import REPO_ROOT, Spec  # noqa: E402

SPEC = Spec.load()
SA = SF.Scenario(b=1.0, a2=0.6, delta_cc=1.5)
SHORT = SF.dev_calendar()[-900:]
MODULE = ROOT / "ofilt" / "drift" / "confirm_run.py"
SCRIPT_PATH = ROOT / "tools" / "p4_confirm_run.py"
MANIFEST_KEYS = ["output", "files", "document_schema_version", "document_schema_version_meaning", "specifications",
                 "config_sha256", "cost_inputs_sha256", "analysis_spec_sha256", "mode", "provenance", "dates",
                 "runtime_fields"]
BOUND = 30000.0   # the last bound of the tick tables in force for 5706 (§5.2, test 5)
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
    for obj, attr, name in ((RG, "SYNTHETIC_PATH", "synthetic.jsonl"), (RG, "REAL_PATH", "real.jsonl"),
                            (IO, "ACCESS_LOG_PATH", "ACCESS_LOG")):
        p = mock.patch.object(obj, attr, folder / name)
        p.start()
        _PATCHES.append(p)


def tearDownModule():
    for p in reversed(_PATCHES):
        p.stop()
    _TMP.cleanup()


def seed(k):
    return SPEC.seed + 8_600_000 + k


def reg_lines():
    p = RG.SYNTHETIC_PATH
    if not p.exists():
        return 0
    with open(p, encoding="utf-8") as fh:
        return sum(1 for _ in fh)


def scaled(df):
    """A copy with 5706's open, close and prev_close multiplied by 0.1, attrs kept (as P4-4c1's tests)."""
    out = df.copy()
    m = (out["ticker"].astype(str) == "5706").to_numpy()
    for c in ("open", "close", "prev_close"):
        out[c] = np.where(m, out[c].to_numpy(dtype=float) * 0.1, out[c].to_numpy(dtype=float))
    out.attrs = dict(df.attrs)
    return out


def frames(k):
    """S_k's frames (dev, events, confirm), on the last 900 dev dates, 5706's prices scaled."""
    if ("frames", k) not in _CACHE:
        o = SF.simulate(seed(k), SA, dev_dates=SHORT)
        _CACHE[("frames", k)] = (scaled(o.dev), o.events, scaled(o.confirm))
    return _CACHE[("frames", k)]


def built(label):
    """build_document on S1's frames; labels "a" and "b" are two builds on the same frames."""
    if ("built", label) not in _CACHE:
        dev, events, conf = frames(1)
        _CACHE[("built", label)] = CR.build_document(dev, events, conf, spec=SPEC, factories={"M7": ZeroM7})
    return _CACHE[("built", label)]


def relabel(df, provenance):
    r = df.copy()
    attrs = {k: v for k, v in df.attrs.items() if k != "provenance"}
    if provenance is not None:
        attrs["provenance"] = provenance
    r.attrs = attrs
    return r


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def no_access_log_in_repo():
    found = []
    for root, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not (Path(root) == ROOT and d == ".git")]
        found += [n for n in dirs + names if n.startswith("ACCESS_LOG")]
    return found == []


def segment(segments, date, field):
    """The value of the last segment whose start (None = the panel's start) is on or before date."""
    val = None
    for s in segments:
        if s["start"] is None or pd.Timestamp(s["start"]) <= date:
            val = s[field]
    return val


def recorder(log, name):
    def rec(*args, **kwargs):
        log.append(name)
    return rec


class TestConfirmRun(unittest.TestCase):
    # 1
    def test_build_document_complete(self):
        doc = built("a").doc
        self.assertEqual(list(doc["rows"]), list(CI.ROW_IDS))
        self.assertEqual(len(doc["rows"]), 71)
        for rid, e in doc["rows"].items():
            self.assertNotEqual(e["status"], "pending", rid)
            self.assertEqual((e["id"], e["item"]), (rid, CI.ITEM_OF[rid]))
        text = CI.to_json(doc)
        self.assertNotIn("NaN", text)
        self.assertNotIn("Infinity", text)
        self.assertEqual(json.loads(text), doc)
        self.assertIs(CC.licensed(doc), False)
        self.assertEqual((doc["mode"], doc["provenance"]), ("confirmation", B.SYNTHETIC))

    # 2
    def test_two_builds_identical(self):
        a, b = built("a"), built("b")
        self.assertEqual(CI.to_json(a.doc).encode("utf-8"), CI.to_json(b.doc).encode("utf-8"))
        ma, mb = CR.manifest(a.doc, spec=SPEC), CR.manifest(b.doc, spec=SPEC)
        self.assertEqual(json.dumps(ma, indent=2), json.dumps(mb, indent=2))
        for name in ("main", "m7"):
            self.assertIsNotNone(a.runtime["run_ids"][name])
            self.assertNotEqual(a.runtime["run_ids"][name], b.runtime["run_ids"][name], name)
        self.assertEqual(set(a.runtime), {"utc_start", "utc_end", "wall_seconds", "run_ids"})
        for key in ("utc_start", "utc_end"):
            self.assertTrue(a.runtime[key].endswith("Z"), a.runtime[key])

    # 3
    def test_write_outputs(self):
        a = built("a")
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "nested" / "out"
            hashes = CR.write_outputs(out, a, spec=SPEC)
            self.assertEqual(sorted(p.name for p in out.iterdir()), sorted(CR.OUTPUT_FILES))
            self.assertEqual((out / "document.json").read_bytes(), CI.to_json(a.doc).encode("utf-8"))
            self.assertEqual(hashes, {n: sha((out / n).read_bytes()) for n in CR.OUTPUT_FILES})
            self.assertEqual(json.loads((out / "manifest.json").read_text(encoding="utf-8")),
                             CR.manifest(a.doc, spec=SPEC))
            self.assertEqual(json.loads((out / "runtime.json").read_text(encoding="utf-8"))["run_ids"],
                             a.runtime["run_ids"])
            for n in CR.OUTPUT_FILES:
                self.assertNotIn(b"\r", (out / n).read_bytes(), n)
            with self.assertRaises(FileExistsError):
                CR.write_outputs(out, a, spec=SPEC)

    # 4
    def test_manifest_pins(self):
        self.assertEqual([p for p, _, _ in CR.SPEC_FILES], ["docs/P4_CONFIRM_INF_SPEC.md", "docs/P4_CONFIRM_FC_SPEC.md",
                                                             "docs/P4_CONFIRM_ECON_SPEC.md",
                                                             "docs/P4_CONFIRM_CLAIMS_SPEC.md"])
        for path, version, digest in CR.SPEC_FILES:
            data = (ROOT / path).read_bytes()
            self.assertEqual(sha(data), digest, path)
            first = data.decode("utf-8").split("\n## ", 1)[0]
            self.assertIn(f"Version {version},", first, path)
        m = CR.manifest(built("a").doc, spec=SPEC)
        self.assertEqual(list(m), MANIFEST_KEYS)
        self.assertEqual(m["config_sha256"], sha((ROOT / "docs" / "P4_CONFIRM_CONFIG.json").read_bytes()))
        self.assertEqual(m["cost_inputs_sha256"], sha((ROOT / "docs" / "P3_COST_INPUTS.json").read_bytes()))
        self.assertEqual(m["analysis_spec_sha256"], Spec.load().sha256)
        self.assertEqual(m["specifications"], [{"path": p, "version": v, "sha256": h} for p, v, h in CR.SPEC_FILES])
        self.assertEqual(m["files"], list(CR.OUTPUT_FILES))
        self.assertEqual(m["document_schema_version"], built("a").doc["spec_version"])

    # 5
    def test_script_synthetic_twice(self):
        argv = ["--source", "synthetic", "--seed", str(seed(2)), "--scenario", '{"b": 1.0, "a2": 0.6, "delta_cc": 1.5}',
                "--dev-dates", "900"]
        with tempfile.TemporaryDirectory() as t:
            a, b = Path(t) / "a", Path(t) / "b"
            before = reg_lines()
            out = stdio.StringIO()
            with mock.patch.dict(MD.REGISTRY, {"M7": ZeroM7}), contextlib.redirect_stdout(out):
                rc = [SCRIPT.main(argv + ["--out", str(a)]), SCRIPT.main(argv + ["--out", str(b)])]
            gained = reg_lines() - before
            self.assertEqual(rc, [0, 0])
            self.assertTrue(CR.documents_equal(a, b))
            self.assertNotEqual((a / "runtime.json").read_bytes(), (b / "runtime.json").read_bytes())
            self.assertEqual(gained, 4)
            self.assertFalse(RG.REAL_PATH.exists())
            self.assertEqual((ROOT / "RUN_REGISTRY.jsonl").stat().st_size, 0)
            printed = out.getvalue().splitlines()
            self.assertEqual(printed, [f"{d / n} {sha((d / n).read_bytes())}" for d in (a, b) for n in CR.OUTPUT_FILES])
            o45 = json.loads((a / "document.json").read_text(encoding="utf-8"))["rows"]["O45"]
        self.assertEqual(o45["status"], "estimated")
        # the evaluated rows' traded prices, recomputed: the same simulation (unscaled), its main call, its prices
        o = SF.simulate(seed(2), SA, dev_dates=SHORT)
        calls = CF.run_calls(o.dev, o.events, o.confirm, spec=SPEC, factories={"M7": ZeroM7})
        _, _, px = CE.economic_px(calls, o.dev, o.events, o.confirm, spec=SPEC)
        inputs = json.loads((ROOT / "docs" / "P3_COST_INPUTS.json").read_text(encoding="utf-8"))
        tables = inputs["tick_tables"]
        above_5706, primary_fails, high_fails = False, False, False
        for d, tk, op, cl in zip(px["date"], px["ticker"].astype(str), px["open"], px["close"]):
            f = float(factor_value(segment(inputs["price_factor"][tk], d, "f")))
            for traded in (op / f, cl / f):
                above_5706 |= tk == "5706" and traded > BOUND
                primary_fails |= traded > tables[inputs["primary_table"][tk]]["rows"][-1][0]
                high_fails |= traded > tables[segment(inputs["dev_table"][tk], d, "table")]["rows"][-1][0]
        expected = {c for c, failed in (("primary", primary_fails), ("high", high_fails)) if failed}
        self.assertEqual(expected, {"primary", "high"} if above_5706 else set())
        self.assertEqual(set(o45["values"]["cases_failed"]), expected)

    # 6
    def test_script_refuses_confirm(self):
        log = []
        access = IO.ACCESS_LOG_PATH
        size = access.stat().st_size if access.exists() else None
        with tempfile.TemporaryDirectory() as t:
            D = Path(t) / "out"
            out = stdio.StringIO()
            with mock.patch.object(IO, "load_confirm", recorder(log, "confirm")), \
                    mock.patch.object(IO, "load_dev", recorder(log, "dev")), \
                    mock.patch.object(SF, "simulate", recorder(log, "simulate")), contextlib.redirect_stdout(out):
                rc = SCRIPT.main(["--source", "confirm", "--out", str(D)])
            self.assertEqual(rc, 2)
            self.assertEqual(log, [])
            self.assertFalse(D.exists())
        self.assertEqual(access.stat().st_size if access.exists() else None, size)
        self.assertEqual(out.getvalue(), "REFUSED: the confirmation panel is not opened in Pass 4 (P4Q3; P13(c)); "
                                         "the confirmation run is Pass 6's\n")

    # 7
    def test_script_refuses_dev_without_sanction(self):
        for value in (None, "P4-5"):
            log = []
            with tempfile.TemporaryDirectory() as t:
                D = Path(t) / "out"
                out = stdio.StringIO()
                with mock.patch.dict(os.environ), mock.patch.object(IO, "load_dev", recorder(log, "dev")), \
                        mock.patch.object(IO, "load_events_firm", recorder(log, "events")), \
                        contextlib.redirect_stdout(out):
                    os.environ.pop(CR.DEV_RUN_SANCTION_VAR, None)
                    if value is not None:
                        os.environ[CR.DEV_RUN_SANCTION_VAR] = value
                    rc = SCRIPT.main(["--source", "dev", "--out", str(D)])
                self.assertEqual(rc, 2, value)
                self.assertEqual(log, [], value)
                self.assertFalse(D.exists(), value)
                self.assertEqual(out.getvalue(), "REFUSED: the dev run needs its sanction (P4-6): set "
                                                 "OFILT_P4_DEV_RUN=P4-6\n")
        self.assertNotIn(CR.DEV_RUN_SANCTION_VAR, os.environ)

    # 8
    def test_load_confirm_refused_and_logged(self):
        with tempfile.TemporaryDirectory() as t:
            log = Path(t) / "logs" / "ACCESS_LOG"
            log.parent.mkdir()
            empty = Path(t) / "empty"
            empty.mkdir()
            with mock.patch.object(IO, "ACCESS_LOG_PATH", log), mock.patch.object(IO, "DATA_DIR", empty):
                with self.assertRaises(IO.AccessDenied):
                    IO.load_confirm()
            lines = log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            rec = json.loads(lines[0])
            self.assertEqual((rec["result"], rec["tag"]), ("DENIED", "prereg-v1"))
            self.assertEqual(IO.CONFIRM_TAG, "prereg-v1")
            self.assertTrue(no_access_log_in_repo())
            self.assertEqual(list(empty.iterdir()), [])

    # 9
    def test_registry_routing(self):
        self.assertEqual(RG.registry_path(B.SYNTHETIC), RG.SYNTHETIC_PATH)
        for prov in (B.DEV_REAL, B.CONFIRM_REAL):
            self.assertEqual(RG.registry_path(prov), RG.REAL_PATH, prov)
        for prov in ("", "real", "dev", None, "unknown"):
            with self.assertRaises(B.BlindingError):
                RG.registry_path(prov)
        tree = ast.parse((ROOT / "ofilt" / "drift" / "registry.py").read_text(encoding="utf-8"))
        assigns = [n for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "REAL_PATH" for t in n.targets)]
        self.assertEqual(len(assigns), 1)
        v = assigns[0].value
        self.assertIsInstance(v, ast.BinOp)
        self.assertIsInstance(v.op, ast.Div)
        self.assertEqual((type(v.left), getattr(v.left, "id", None)), (ast.Name, "REPO_ROOT"))
        self.assertEqual((type(v.right), getattr(v.right, "value", None)), (ast.Constant, "RUN_REGISTRY.jsonl"))
        self.assertEqual(REPO_ROOT.resolve(), ROOT)
        self.assertTrue((ROOT / "RUN_REGISTRY.jsonl").is_file())

    # 10
    def test_dev_mode_document(self):
        o = SF.simulate(seed(3), SA)
        a = CR.build_document(scaled(o.dev), o.events, spec=SPEC, factories={"M7": ZeroM7})
        rows = a.doc["rows"]
        self.assertEqual(a.doc["mode"], "dev")
        self.assertEqual([rid for rid, e in rows.items() if e["status"] == "pending"], [])
        for rid in ("O8", "O27", "R23", "R25"):
            self.assertEqual(rows[rid]["status"], "not_applicable", rid)
        self.assertIs(rows["R10"]["values"]["claimed"], False)
        self.assertLess(a.doc["dates"]["last"], "2022-01-01")

    # 11
    def test_refused_pairs_before_anything(self):
        dev, events, conf = frames(1)
        cases = [(dev, relabel(conf, B.DEV_REAL)), (dev, relabel(conf, B.CONFIRM_REAL)),
                 (relabel(dev, B.DEV_REAL), conf), (relabel(dev, None), conf), (relabel(dev, B.CONFIRM_REAL), None)]
        for d, c in cases:
            labels, lines = B.registered_labels(), reg_lines()
            with self.assertRaises(ValueError):
                CR.build_document(d, events, c, spec=SPEC, factories={"M7": ZeroM7})
            self.assertEqual(B.registered_labels(), labels)
            self.assertEqual(reg_lines(), lines)

    # 12
    def test_sources(self):
        tree = ast.parse(MODULE.read_text(encoding="utf-8"))
        absolute = {"__future__", "dataclasses", "datetime", "json", "math", "pathlib", "time", "typing"}
        package = {"blind", "confirm_inference", "confirm_forecast", "confirm_economic", "confirm_claims"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertIn(a.name, absolute)
            elif isinstance(node, ast.ImportFrom):
                names = {a.name for a in node.names}
                if node.level == 0:
                    self.assertIn(node.module, absolute)
                elif node.module is None:
                    self.assertEqual(node.level, 1)
                    self.assertLessEqual(names, package)
                else:
                    self.assertEqual((node.level, node.module), (1, "spec"))
                    self.assertLessEqual(names, {"Spec"})
        where = {}                      # call name -> the top-level functions (None: module level) that call it
        for top in tree.body:
            owner = top.name if isinstance(top, (ast.FunctionDef, ast.ClassDef)) else None
            for node in ast.walk(top):
                if isinstance(node, ast.Call):
                    f = node.func
                    name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
                    where.setdefault(name, set()).add(owner)
                    if name == "open" and owner == "write_outputs":
                        modes = [a.value for a in node.args[1:2] + [k.value for k in node.keywords if k.arg == "mode"]
                                 if isinstance(a, ast.Constant)]
                        self.assertTrue(modes and "r" not in modes[0], "open for reading in write_outputs")
        for name in ("open", "write_text", "write_bytes"):
            self.assertLessEqual(where.get(name, set()), {"write_outputs", "documents_equal"}, name)
        for name in ("read_bytes", "read_text"):
            self.assertLessEqual(where.get(name, set()), {"documents_equal"}, name)
        script_src = SCRIPT_PATH.read_text(encoding="utf-8")
        for path, src in ((MODULE, MODULE.read_text(encoding="utf-8")), (SCRIPT_PATH, script_src)):
            self.assertNotIn("load_confirm", src, path.name)
        st = ast.parse(script_src)
        parents = {}
        for node in ast.walk(st):
            for child in ast.iter_child_nodes(node):
                parents[child] = node

        def enclosing_function(node):
            while node in parents:
                node = parents[node]
                if isinstance(node, ast.FunctionDef):
                    return node.name
            return None

        loader_calls = [(n.func.attr, enclosing_function(n)) for n in ast.walk(st) if isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Attribute) and n.func.attr in ("load_dev", "load_events_firm")]
        self.assertEqual(sorted(a for a, _ in loader_calls), ["load_dev", "load_events_firm"])
        self.assertEqual({f for _, f in loader_calls}, {"_dev_frames"})
        fn = next(n for n in st.body if isinstance(n, ast.FunctionDef) and n.name == "_dev_frames")
        body = fn.body[1:] if (isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant)) \
            else fn.body
        first = body[0]
        self.assertIsInstance(first, ast.If)
        test_src = ast.unparse(first.test)
        self.assertIn("DEV_RUN_SANCTION_VAR", test_src)
        self.assertIn("DEV_RUN_SANCTION_VALUE", test_src)
        self.assertIsInstance(first.body[-1], ast.Return)
        self.assertFalse([n for n in ast.walk(first) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                          and n.func.attr in ("load_dev", "load_events_firm")])
        dev_calls = [n for n in ast.walk(st) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                     and n.func.id == "_dev_frames"]
        self.assertTrue(dev_calls)
        for call in dev_calls:
            node, guarded = call, False
            while node in parents:
                child, node = node, parents[node]
                if isinstance(node, ast.If) and child in node.body:
                    t = node.test
                    if (isinstance(t, ast.Compare) and isinstance(t.left, ast.Attribute) and t.left.attr == "source"
                            and len(t.ops) == 1 and isinstance(t.ops[0], ast.Eq)
                            and isinstance(t.comparators[0], ast.Constant) and t.comparators[0].value == "dev"):
                        guarded = True
            self.assertTrue(guarded, ast.dump(call))


def factor_value(text):
    """A price factor as a float: "10", "1", "2" or "1/10" (docs/P3_COST_INPUTS.json, price_factor)."""
    num, _, den = str(text).partition("/")
    return float(num) / float(den or 1)


if __name__ == "__main__":
    unittest.main()
