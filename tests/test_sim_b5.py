"""B5: sealed blind fit (Flag 8 conditions a-e) and the dev-calibrated simulator.
TestRealDev is the ONLY place the sealed fit runs on real data: one call per suite run,
each recorded in BLIND_FIT_LOG and summarised in the blinding attestation."""
import ast
import contextlib
import io as _io
import json
import os
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
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))  # P3-8b: the tests folder, for tag_state
import tag_state as TS  # noqa: E402  (P3-8b)

CORE = "_design_core"
ALLOWED_CALLERS = [("inference.py", "build_design"), ("sim.py", "_sealed_blind_fit")]


def scan_core_references(source: str, filename: str) -> list[tuple]:
    """Every reference to the unguarded core: (kind, file, enclosing function)."""
    tree = ast.parse(source)
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and n.body and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
    call_funcs = {id(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    hits = []

    class V(ast.NodeVisitor):
        def __init__(self):
            self.stack = []

        def visit_FunctionDef(self, n):
            self.stack.append(n.name); self.generic_visit(n); self.stack.pop()
        visit_AsyncFunctionDef = visit_FunctionDef

        def _hit(self, kind, n):
            hits.append((kind, filename, self.stack[-1] if self.stack else None))

        def visit_Name(self, n):
            if n.id == CORE:
                self._hit("call" if id(n) in call_funcs else "name", n)

        def visit_Attribute(self, n):
            if n.attr == CORE:
                self._hit("call" if id(n) in call_funcs else "attr", n)
            self.generic_visit(n)

        def visit_alias(self, n):
            if CORE in (n.name, n.asname) or n.name.endswith("." + CORE):
                self._hit("import", n)

        def visit_Constant(self, n):
            if isinstance(n.value, str) and CORE in n.value and id(n) not in docs:
                self._hit("string", n)

    V().visit(tree)
    return hits


class TestStatic(unittest.TestCase):
    def test_design_core_called_from_exactly_two_places(self):
        hits = []
        for py in sorted((ROOT / "ofilt").rglob("*.py")):
            hits += scan_core_references(py.read_text(encoding="utf-8"), py.name)
        self.assertEqual(sorted((f, fn) for k, f, fn in hits if k == "call"), sorted(ALLOWED_CALLERS))
        self.assertEqual([h for h in hits if h[0] != "call"], [])        # no alias, import or string use

    def test_scanner_catches_bypasses(self):
        for src, kind in [("def f():\n    inference._design_core(df)\n", "call"),
                          ("from .inference import _design_core as g\n", "import"),
                          ("def f():\n    return getattr(inference, '_design_core')\n", "string"),
                          ("def f():\n    h = inference._design_core\n", "attr")]:
            self.assertEqual([h[0] for h in scan_core_references(src, "x.py")], [kind], src)

    def test_sealed_fit_ast_containment(self):
        tree = ast.parse((ROOT / "ofilt" / "drift" / "sim.py").read_text(encoding="utf-8"))
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_sealed_blind_fit")
        nodes = list(ast.walk(fn))
        self.assertFalse([n for n in nodes if isinstance(n, (ast.Global, ast.Nonlocal))])
        for n in nodes:  # the function never mutates any object: plain-name stores only
            if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                tg = n.targets if isinstance(n, ast.Assign) else [n.target]
                self.assertTrue(all(isinstance(t, ast.Name) for t in tg), ast.dump(n)[:80])
        self.assertFalse([n for n in nodes if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                          and n.func.id in ("print", "setattr", "exec", "eval")])
        coef_assign = [st for st in fn.body if isinstance(st, ast.Assign)
                       and any(isinstance(c, ast.Attribute) and c.attr == "lstsq" for c in ast.walk(st.value))]
        self.assertEqual([st.targets[0].id for st in coef_assign], ["coef"])
        for st in fn.body:  # every statement mentioning coef is one of exactly four allowed forms
            if "coef" in {n.id for n in ast.walk(st) if isinstance(n, ast.Name)}:
                ok = (st in coef_assign
                      or (isinstance(st, ast.Assign) and st.targets[0].id in ("residuals", "fitted_controls"))
                      or (isinstance(st, ast.Delete) and [t.id for t in st.targets] == ["coef"]))
                self.assertTrue(ok, ast.dump(st)[:120])
        rets = [n for n in nodes if isinstance(n, ast.Return)]
        self.assertEqual(len(rets), 1)
        self.assertIsInstance(rets[0].value, ast.Dict)
        self.assertEqual({k.value for k in rets[0].value.keys}, set(S.FIT_KEYS))
        self.assertNotIn("coef", {n.id for n in ast.walk(rets[0]) if isinstance(n, ast.Name)})


class SyntheticBase(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()
        self.tmp = tempfile.TemporaryDirectory()
        self.log = Path(self.tmp.name) / "BLIND_FIT_LOG"
        self.patch = mock.patch.object(S, "BLIND_FIT_LOG_PATH", self.log)
        self.patch.start()
        self.stand_in = S.synthetic_panel(800, b=0.4, a2=-0.2, seed=31, p_excl=0.03)  # "real" stand-in, b != b_sim

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()


class TestSealedFitMechanics(SyntheticBase):
    def test_keys_orthogonality_span_silence_and_log(self):
        out, err = _io.StringIO(), _io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            fit = S._sealed_blind_fit(self.stand_in, self.spec)
        self.assertEqual(out.getvalue() + err.getvalue(), "")
        self.assertEqual(set(fit), set(S.FIT_KEYS))
        d = I.build_design(self.stand_in, self.spec)
        self.assertTrue(np.array_equal(fit["row_index"], d.index))
        self.assertLess(np.abs(d.X.T @ fit["residuals"]).max(), 1e-10)          # resid orthogonal to X
        fx_part = d.y - fit["fitted_controls"] - fit["residuals"]                # = FX part only
        F = d.X[:, [d.col("usdjpy_ret"), d.col("eurusd_ret")]]
        r = fx_part - F @ np.linalg.lstsq(F, fx_part, rcond=None)[0]
        self.assertLess(np.abs(r).max(), 1e-12)                                  # fitted_controls has no FX
        recs = [json.loads(l) for l in self.log.read_text().splitlines()]
        self.assertEqual(len(recs), 1)
        self.assertEqual(set(recs[0]), {"utc", "provenance", "panel_sha256", "spec_sha256", "n_rows_input", "caller"})
        self.assertFalse([v for v in recs[0].values() if isinstance(v, float)])
        S._sealed_blind_fit(self.stand_in, self.spec)
        self.assertEqual(len(self.log.read_text().splitlines()), 2)              # one line per call

    def test_real_fit_is_opt_in(self):
        relabelled = self.stand_in.copy()          # synthetic data labelled dev_real: no real data involved
        relabelled.attrs = {"provenance": "dev_real", "sha256": "synthetic-standin"}
        env = {k: v for k, v in os.environ.items() if k != S.SEALED_ENV}
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaisesRegex(B.BlindingError, "deliberately invoked"):
                S._sealed_blind_fit(relabelled, self.spec)
            with self.assertRaises(B.BlindingError):
                S.DevCalibrator(relabelled, self.spec)
        self.assertFalse(self.log.exists())        # refused attempts compute nothing and log nothing
        with mock.patch.dict(os.environ, {S.SEALED_ENV: "1"}):
            self.assertEqual(set(S._sealed_blind_fit(relabelled, self.spec)), set(S.FIT_KEYS))
        self.assertEqual(len(self.log.read_text().splitlines()), 1)
        for v in ("0", "true", "yes", ""):
            with mock.patch.dict(os.environ, {S.SEALED_ENV: v}), self.assertRaises(B.BlindingError):
                S._sealed_blind_fit(relabelled, self.spec)
        sh = (ROOT / "tools" / "checkpoint.sh").read_text(encoding="utf-8")
        self.assertIn("env -u OFILT_RUN_SEALED python -m unittest discover", sh)
        self.assertNotIn("OFILT_RUN_SEALED=1", sh)

    def test_refusals_and_guard_intact(self):
        for prov in ("confirm_real", None, "weird"):
            d = self.stand_in.copy()
            d.attrs = {} if prov is None else {"provenance": prov}
            with self.assertRaises(B.BlindingError):
                S._sealed_blind_fit(d, self.spec)
        real = self.stand_in.copy()
        real.attrs = {"provenance": "dev_real"}
        with TS.blinded(), self.assertRaises(B.BlindingError):  # P3-8b: was with self.assertRaises(B.BlindingError):; the guard in a repository without the tags
            I.build_design(real, self.spec)                                      # public path still guarded


class TestDevCalibrated(SyntheticBase):
    def test_identity_map_returns_b_sim_exactly(self):
        cal = S.DevCalibrator(self.stand_in, self.spec)
        y = cal.draw(0.25, -0.1, positions=np.arange(cal.T))
        r = I.fit_dk(I.build_design(y, self.spec, target="y_sim"), self.spec)
        self.assertAlmostEqual(r.param("usdjpy_ret")["estimate"], 0.25, places=10)   # not the stand-in's 0.4
        self.assertAlmostEqual(r.param("eurusd_ret")["estimate"], -0.1, places=10)

    def test_no_leak_and_recovery_under_bootstrap(self):
        cal = S.DevCalibrator(self.stand_in, self.spec)
        for b_sim in (0.0, 0.25):
            est = [I.fit_dk(I.build_design(cal.draw(b_sim, seed=k), self.spec, target="y_sim"), self.spec)
                   .param("usdjpy_ret")["estimate"] for k in range(20)]
            self.assertLess(abs(np.mean(est) - b_sim), 3 * np.std(est) / np.sqrt(20) + 0.02, b_sim)
        self.assertEqual(len(self.log.read_text().splitlines()), 1)              # one sealed fit for all draws

    def test_output_contract(self):
        cal = S.DevCalibrator(self.stand_in, self.spec)
        y = cal.draw(0.1, seed=3)
        self.assertEqual(tuple(y.columns), S.SIM_COLUMNS)
        self.assertFalse(set(y.columns) & ({"abn_oc", "raw_oc", "cc_abn", "gap_abn", "y_oc", "y_topix_oc"}
                                           | set(S.FIT_KEYS) | {"index", "source", "src"}))
        self.assertEqual(B.require_unblinded(y), "synthetic")
        self.assertTrue((y.date < "2000-01-01").all())
        self.assertEqual(set(y.attrs["truth"]), {"b", "a2", "seed", "mean_block", "n_dates", "source"})
        self.assertEqual(y.date.nunique(), cal.T)
        self.assertTrue(y.equals(cal.draw(0.1, seed=3)))
        with self.assertRaises(ValueError):
            cal.draw(0.1, positions=np.arange(cal.T - 1))
        short = cal.draw(0.1, seed=3, n_dates=383)                               # B7: any output length
        self.assertEqual(short.date.nunique(), 383)
        self.assertEqual(short.attrs["truth"]["n_dates"], 383)
        self.assertEqual(B.require_unblinded(short), "synthetic")
        long_ = cal.draw(0.1, seed=3, n_dates=2 * cal.T)
        self.assertEqual(long_.date.nunique(), 2 * cal.T)
        ident = cal.draw(0.25, -0.1, positions=np.r_[np.arange(cal.T), np.arange(cal.T)], n_dates=2 * cal.T)
        r = I.fit_dk(I.build_design(ident, self.spec, target="y_sim"), self.spec)
        self.assertAlmostEqual(r.param("usdjpy_ret")["estimate"], 0.25, places=10)  # duplicated identity map

    def test_stationary_bootstrap(self):
        rng = np.random.default_rng(0)
        T, starts, n = 1708, 0, 0
        for _ in range(20):
            p = S.stationary_bootstrap_positions(T, 5.0, rng)
            self.assertTrue((p >= 0).all() and (p < T).all())
            starts += int((p[1:] != (p[:-1] + 1) % T).sum()); n += T - 1
        self.assertLess(abs(starts / n - 0.2), 0.015)                            # mean block length 5
        p = S.stationary_bootstrap_positions(10, 1e9, np.random.default_rng(1))
        self.assertTrue(np.array_equal(p, (p[0] + np.arange(10)) % 10))          # wrap-around
        with self.assertRaises(ValueError):
            S.stationary_bootstrap_positions(10, 0.5, rng)


@unittest.skipUnless(os.environ.get("OFILT_RUN_SEALED") == "1", "real-data sealed fit is opt-in (OFILT_RUN_SEALED=1)")
class TestRealDev(unittest.TestCase):
    """The real-data sealed fit; runs ONLY when deliberately invoked with OFILT_RUN_SEALED=1
    (one call per invocation, logged to the real BLIND_FIT_LOG). Checkpoints never set it."""

    @classmethod
    def setUpClass(cls):
        cls.spec = Spec.load()
        dev = TG.add_targets(IO.load_dev(), cls.spec)
        log = S.BLIND_FIT_LOG_PATH
        cls.n_before = len(log.read_text().splitlines()) if log.exists() else 0
        out, err = _io.StringIO(), _io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            cls.cal = S.DevCalibrator(dev, cls.spec)
        cls.printed = out.getvalue() + err.getvalue()
        cls.recs = [json.loads(l) for l in log.read_text().splitlines()]
        cls.sha = dev.attrs["sha256"]

    def test_logged_and_silent(self):
        self.assertEqual(self.printed, "")
        self.assertEqual(len(self.recs), self.n_before + 1)
        last = self.recs[-1]
        self.assertEqual((last["provenance"], last["panel_sha256"]), ("dev_real", self.sha))
        self.assertFalse([v for v in last.values() if isinstance(v, float)])

    def test_draw_passes_guard_and_contract(self):
        y = self.cal.draw(0.25, seed=1)
        self.assertEqual(B.require_unblinded(y), "synthetic")
        self.assertEqual(tuple(y.columns), S.SIM_COLUMNS)
        self.assertTrue((y.date < "2000-01-01").all())
        self.assertFalse(hasattr(self.cal, "coef") or any("coef" in k for k in vars(self.cal)))


if __name__ == "__main__":
    unittest.main()
