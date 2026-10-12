"""P5-1 (P5Q5): tools/p6_confirm_run.py against docs/P5_CONFIRM_SCRIPT_SPEC.md (version 1). Exactly the 7 test methods
of its section 3.2. Seeds are the spec seed + 8,700,000 + k, disjoint from every earlier block. The script is never run
on real data: every test replaces its loaders by recorders or by stand-ins that return simulator frames, except test 5,
where io.load_confirm itself runs against a throwaway guard repository without the tags (TS.io_blinded) and refuses.
setUpModule patches the run registry to a temporary folder and io.ACCESS_LOG_PATH to a file in it that does not exist;
every output folder lies in a temporary directory. M7 is the zero-forecast stand-in of P4-4b2's tests, patched into
models.REGISTRY for both scripts."""
import ast
import contextlib
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import p4_confirm_run as P4  # noqa: E402
import p6_confirm_run as P6  # noqa: E402
import tag_state as TS  # noqa: E402
from ofilt.drift import confirm_run as CR  # noqa: E402
from ofilt.drift import forecast as FC  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import models as MD  # noqa: E402
from ofilt.drift import registry as RG  # noqa: E402
from ofilt.drift import sim_full as SF  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

SPEC = Spec.load()
SCRIPT_PATH = ROOT / "tools" / "p6_confirm_run.py"
SCENARIO = '{"b": 1.0, "a2": 0.6, "delta_cc": 1.5}'
DEV_DATES = 900
_PATCHES: list = []
_TMP = None


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
    return SPEC.seed + 8_700_000 + k


def recorder(log, name, value=None):
    def rec(*args, **kwargs):
        log.append(name)
        return value
    return rec


@contextlib.contextmanager
def sanction(value=P6.CONFIRM_RUN_SANCTION_VALUE):
    """os.environ with the run's sanction variable set to value (None: absent), restored afterwards."""
    with mock.patch.dict(os.environ):
        os.environ.pop(P6.CONFIRM_RUN_SANCTION_VAR, None)
        if value is not None:
            os.environ[P6.CONFIRM_RUN_SANCTION_VAR] = value
        yield


@contextlib.contextmanager
def loaders(log, dev=None, events=None, confirm=None):
    """io's three loaders replaced by recorders that return the given frames."""
    with mock.patch.object(IO, "load_dev", recorder(log, "dev", dev)), \
            mock.patch.object(IO, "load_events_firm", recorder(log, "events", events)), \
            mock.patch.object(IO, "load_confirm", recorder(log, "confirm", confirm)):
        yield


class TestP6ConfirmRun(unittest.TestCase):
    # 1
    def test_constants_and_texts(self):
        self.assertEqual((P6.CONFIRM_RUN_SANCTION_VAR, P6.CONFIRM_RUN_SANCTION_VALUE), ("OFILT_P6_CONFIRM_RUN", "P6-1"))
        self.assertNotEqual(P6.CONFIRM_RUN_SANCTION_VAR, CR.DEV_RUN_SANCTION_VAR)
        self.assertEqual(P6.EXIT_REFUSED, 2)
        self.assertNotIn(P6.CONFIRM_RUN_SANCTION_VAR, os.environ)       # the sanction is never set in the suite
        src = SCRIPT_PATH.read_text(encoding="utf-8")
        for s in (TS.SPEC_TAG, TS.PREREG_TAG, "sim_full", "OFILT_RUN_SEALED", "DATA_DIR"):
            self.assertNotIn(s, src, s)
        self.assertEqual(P6.SANCTION_REFUSAL,
                         "REFUSED: the confirmation run needs its sanction (Pass 6): set OFILT_P6_CONFIRM_RUN=P6-1")

    # 2
    def test_refuses_without_sanction(self):
        for value in (None, "", "P6", "P4-6", "p6-1"):
            log = []
            with tempfile.TemporaryDirectory() as t:
                D = Path(t) / "out"
                out = stdio.StringIO()
                with sanction(value), loaders(log), contextlib.redirect_stdout(out):
                    rc = P6.main(["--out", str(D)])
                self.assertEqual(rc, 2, value)
                self.assertEqual(log, [], value)
                self.assertFalse(D.exists(), value)
                self.assertEqual(out.getvalue(), P6.SANCTION_REFUSAL + "\n", value)
        self.assertFalse(IO.ACCESS_LOG_PATH.exists())

    # 3
    def test_refuses_when_access_log_exists(self):
        for content in (b"", b'{"result": "DENIED"}\n', b'{"result": "GRANTED"}\n'):
            log = []
            with tempfile.TemporaryDirectory() as t:
                access = Path(t) / "ACCESS_LOG"
                access.write_bytes(content)
                D = Path(t) / "out"
                out = stdio.StringIO()
                with sanction(), loaders(log), mock.patch.object(IO, "ACCESS_LOG_PATH", access), \
                        contextlib.redirect_stdout(out):
                    rc = P6.main(["--out", str(D)])
                self.assertEqual(rc, 2)
                self.assertEqual(log, [])
                self.assertFalse(D.exists())
                self.assertEqual(access.read_bytes(), content)
                self.assertEqual(out.getvalue(), P6.ONE_SHOT_REFUSAL.format(path=access) + "\n")

    # 4
    def test_refuses_existing_out(self):
        log = []
        with tempfile.TemporaryDirectory() as t:
            D = Path(t) / "out"
            D.mkdir()
            out = stdio.StringIO()
            with sanction(), loaders(log), contextlib.redirect_stdout(out):
                rc = P6.main(["--out", str(D)])
            self.assertEqual(rc, 2)
            self.assertEqual(log, [])
            self.assertEqual(list(D.iterdir()), [])
            self.assertEqual(out.getvalue(), f"REFUSED: --out {D} exists\n")

    # 5
    def test_guard_refuses_without_the_tag(self):
        log = []
        with tempfile.TemporaryDirectory() as t:
            access = Path(t) / "logs" / "ACCESS_LOG"
            access.parent.mkdir()
            empty = Path(t) / "empty"
            empty.mkdir()
            D = Path(t) / "out"
            with sanction(), mock.patch.object(IO, "load_dev", recorder(log, "dev")), \
                    mock.patch.object(IO, "load_events_firm", recorder(log, "events")), \
                    mock.patch.object(IO, "ACCESS_LOG_PATH", access), mock.patch.object(IO, "DATA_DIR", empty), \
                    TS.io_blinded(), contextlib.redirect_stdout(stdio.StringIO()):
                with self.assertRaises(IO.AccessDenied):
                    P6.main(["--out", str(D)])
            self.assertEqual(log, ["dev", "events"])
            lines = access.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual((json.loads(lines[0])["result"], json.loads(lines[0])["tag"]), ("DENIED", TS.PREREG_TAG))
            self.assertFalse(D.exists())
            self.assertEqual(list(empty.iterdir()), [])

    # 6
    def test_same_documents_as_the_p4_script(self):
        k = seed(1)
        o = SF.simulate(k, SF.Scenario(**json.loads(SCENARIO)), dev_dates=SF.dev_calendar()[-DEV_DATES:])
        with tempfile.TemporaryDirectory() as t:
            a, b = Path(t) / "p4", Path(t) / "p6"
            log = []
            out = stdio.StringIO()
            with mock.patch.dict(MD.REGISTRY, {"M7": ZeroM7}), contextlib.redirect_stdout(out):
                rc4 = P4.main(["--source", "synthetic", "--seed", str(k), "--scenario", SCENARIO,
                               "--dev-dates", str(DEV_DATES), "--out", str(a)])
                with sanction(), loaders(log, o.dev, o.events, o.confirm):
                    rc6 = P6.main(["--out", str(b)])
            self.assertEqual((rc4, rc6), (0, 0))
            self.assertEqual(log, ["dev", "events", "confirm"])
            self.assertTrue(CR.documents_equal(a, b))
            self.assertEqual(sorted(p.name for p in b.iterdir()), sorted(CR.OUTPUT_FILES))
            printed = out.getvalue().splitlines()[len(CR.OUTPUT_FILES):]
            self.assertEqual(printed, [f"{b / n} {CR._sha256((b / n).read_bytes())}" for n in CR.OUTPUT_FILES])
        self.assertFalse(RG.REAL_PATH.exists())
        self.assertFalse(IO.ACCESS_LOG_PATH.exists())

    # 7
    def test_sources(self):
        src = SCRIPT_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertIn(a.name, {"argparse", "os", "sys"})
            elif isinstance(node, ast.ImportFrom):
                if node.module == "pathlib":
                    self.assertEqual({a.name for a in node.names}, {"Path"})
                else:
                    self.assertEqual((node.level, node.module), (0, "ofilt.drift"))
                    self.assertEqual({a.name for a in node.names}, {"confirm_run", "io"})
        parents = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node

        def enclosing_function(node):
            while node in parents:
                node = parents[node]
                if isinstance(node, ast.FunctionDef):
                    return node.name
            return None

        loader_names = ("load_dev", "load_events_firm", "load_confirm")
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr in loader_names]
        self.assertEqual([c.func.attr for c in sorted(calls, key=lambda c: c.lineno)], list(loader_names))
        self.assertEqual({enclosing_function(c) for c in calls}, {"_confirm_frames"})
        self.assertTrue(all(isinstance(c.func.value, ast.Name) and c.func.value.id == "io" and not c.args
                            and not c.keywords for c in calls))
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_confirm_frames")
        body = fn.body[1:] if (isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant)) \
            else fn.body
        for stmt, needles in ((body[0], ("CONFIRM_RUN_SANCTION_VAR", "CONFIRM_RUN_SANCTION_VALUE")),
                              (body[1], ("ACCESS_LOG_PATH", "exists"))):
            self.assertIsInstance(stmt, ast.If)
            for s in needles:
                self.assertIn(s, ast.unparse(stmt.test))
            self.assertIsInstance(stmt.body[-1], ast.Return)
            self.assertFalse(stmt.orelse)
            self.assertFalse([n for n in ast.walk(stmt) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                              and n.func.attr in loader_names])
        uses = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id == "_confirm_frames"]
        self.assertEqual([enclosing_function(n) for n in uses], ["main"])
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        order = [ast.unparse(s) for s in main.body]
        out_check = next(i for i, s in enumerate(order) if s.startswith("if a.out.exists()"))
        frames_at = next(i for i, s in enumerate(order) if "_confirm_frames()" in s)
        self.assertLess(out_check, frames_at)
        for name in ("open", "write_text", "write_bytes", "read_text", "read_bytes", "remove", "unlink", "rmtree"):
            self.assertFalse([n for n in ast.walk(tree) if isinstance(n, ast.Call) and
                              ((isinstance(n.func, ast.Name) and n.func.id == name) or
                               (isinstance(n.func, ast.Attribute) and n.func.attr == name))], name)


if __name__ == "__main__":
    unittest.main()
