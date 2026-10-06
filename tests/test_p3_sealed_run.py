"""P3-2b (supervisor message of 2026-10-06): tests of tools/p3_sealed_run.py and docs/P3_RUN_CONFIG.json.
Synthetic only; no data file is read. No test sets the OFILT_RUN_SEALED environment variable: the real-mode checks are
tested on the pure refusal function, and subprocess runs have the variable removed from their environment.

1. Static (AST): one DevCalibrator( call; no banned import; files written by one function; the calibrator's private
   attributes only in the row-count assertion.
2. Invariance (D3.2, D3.3 amended): (b_hat - b)/se and t* agree at b = 0, 0.25 and 0.8652 (1e-10); and
   calib.bootstrap_t_given_fit returns exactly calib.bootstrap_t's t* for the same frame and seed.
3. Configuration: the committed file is the rebuilt configuration and validates; a missing key, a changed hash or an
   --expect-config-sha256 mismatch is refused.
4. Real-mode refusals with no data read (io.load_dev mocked to fail).
5. Outputs of a tiny synthetic run: every key whitelisted; no list longer than 20.
6. The run-registry directory: one line per walk_forward call; the run's directory deleted.
7. Seeds: disjoint from each other and from the B7, B7b, C7 and P3-2a blocks.
8. Logs: the 6 -> 7 -> 7 checks.
9. Determinism: two tiny synthetic runs identical apart from `runtime`.
"""
import ast
import contextlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import p3_sealed_run as P  # noqa: E402
from ofilt.drift import calib as C  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

TOOL = ROOT / "tools" / "p3_sealed_run.py"
CFG = json.loads(P.CONFIG_PATH.read_text(encoding="utf-8"))


def tiny_run(out_dir: Path, tmp_dir: Path, nodata: Path, smoke: int = 2) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != P.SEALED_ENV}
    env.update(OFILT_DATA_DIR=str(nodata), TMPDIR=str(tmp_dir))
    return subprocess.run([sys.executable, str(TOOL), "--synthetic", "--smoke", str(smoke), "--out-dir", str(out_dir)],
                          cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=900)


class TestStatic(unittest.TestCase):
    def test_1_static(self):
        tree = ast.parse(TOOL.read_text(encoding="utf-8"))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
        dc = [n for n in calls if (isinstance(n.func, ast.Attribute) and n.func.attr == "DevCalibrator")
              or (isinstance(n.func, ast.Name) and n.func.id == "DevCalibrator")]
        self.assertEqual(len(dc), 1)
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add(n.module or "")
        banned = ("multiprocessing", "concurrent", "joblib", "subprocess", "pickle")
        self.assertFalse([m for m in mods for b in banned if m == b or m.startswith(b + ".")], sorted(mods))
        writers = {}
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and ((isinstance(n.func, ast.Attribute) and n.func.attr in
                                                 ("write_text", "write_bytes", "write", "open"))
                                                or (isinstance(n.func, ast.Name) and n.func.id == "open")):
                    writers.setdefault(fn.name, 0)
                    writers[fn.name] += 1
        self.assertEqual(set(writers), {"_write_file"}, writers)
        private = {"_bounds", "_resid", "_fc", "_pred", "_cal"}
        where = []
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            for n in ast.walk(fn):
                if isinstance(n, ast.Attribute) and n.attr in private:
                    where.append((fn.name, n.attr))
        self.assertEqual(where, [("assert_calibrator_shape", "_bounds")])


class TestInvariance(unittest.TestCase):
    def test_2_invariance_and_given_fit(self):
        spec = Spec.load()
        df = S.synthetic_panel(300, b=0.4, a2=-0.2, seed=91, tails="t5")
        with tempfile.TemporaryDirectory() as t, mock.patch.object(S, "BLIND_FIT_LOG_PATH", Path(t) / "LOG"):
            cal = S.DevCalibrator(df, spec)
        pos = cal.positions(np.random.default_rng(5), 300)
        z, ts, ts3 = [], [], []
        for b in (0.0, 0.25, 0.8652):
            y = cal.draw(b, 0.0, seed=7, positions=pos)
            f = C.fit_t(y, spec, "y_sim")
            z.append((f["b"] - b) / f["se"])
            w = C.bootstrap_t(y, spec, np.random.default_rng(11), "y_sim", 1)
            ts.append(w["t_star"][0])
            ts3.append(w["t_star_h3"][0])
            g = C.bootstrap_t_given_fit(y, spec, np.random.default_rng(11), "y_sim", 1, f)
            self.assertTrue(np.array_equal(g["t_star"], w["t_star"]))          # exactly bootstrap_t's t*
            self.assertTrue(np.array_equal(g["t_star_h3"], w["t_star_h3"]))
        for vals in (z, ts, ts3):
            self.assertLess(max(vals) - min(vals), 1e-10, vals)
        y = cal.draw(0.25, 0.0, seed=8)
        f = C.fit_t(y, spec, "y_sim")
        w3 = C.bootstrap_t(y, spec, np.random.default_rng(12), "y_sim", 3)
        g3 = C.bootstrap_t_given_fit(y, spec, np.random.default_rng(12), "y_sim", 3, f)
        self.assertTrue(np.array_equal(w3["t_star"], g3["t_star"]))


class TestConfig(unittest.TestCase):
    def test_3_configuration(self):
        self.assertEqual(P.CONFIG_PATH.read_text(encoding="utf-8"), P.config_text(P.build_config()))
        self.assertEqual(P.validate_config(CFG), [])
        bad = {k: v for k, v in CFG.items() if k != "seeds"}
        self.assertTrue(any("missing" in x for x in P.validate_config(bad)))
        changed = dict(CFG, dev_panel_sha256="0" * 64)
        self.assertTrue(P.validate_config(changed))
        changed = dict(CFG, spec_sha256="f" * 64)
        self.assertTrue(P.validate_config(changed))
        sha = P.sha256_file(P.CONFIG_PATH)
        r = P.mode_refusal(real=True, smoke=None, rehearsal=False, sealed_value="1", config_sha=sha,
                           expected_sha="0" * 64, dirty=False)
        self.assertIn("expect-config-sha256", r)
        self.assertIsNone(P.mode_refusal(real=True, smoke=None, rehearsal=False, sealed_value="1", config_sha=sha,
                                         expected_sha=sha, dirty=False))


class TestRealRefusals(unittest.TestCase):
    def test_4_real_mode_refusals_read_no_data(self):
        sha = P.sha256_file(P.CONFIG_PATH)
        with mock.patch.object(IO, "load_dev", side_effect=AssertionError("data read")) as ld:
            self.assertIn(P.SEALED_ENV, P.mode_refusal(real=True, smoke=None, rehearsal=False, sealed_value=None,
                                                       config_sha=sha, expected_sha=sha, dirty=False))
            self.assertIn("dirty", P.mode_refusal(real=True, smoke=None, rehearsal=False, sealed_value="1",
                                                   config_sha=sha, expected_sha=sha, dirty=True))
            self.assertIn("expect-config-sha256", P.mode_refusal(real=True, smoke=None, rehearsal=False,
                                                                 sealed_value="1", config_sha=sha,
                                                                 expected_sha=sha[::-1], dirty=False))
            for argv in (["--real", "--smoke", "5"], ["--real", "--rehearsal"]):
                buf = StringIO()
                with contextlib.redirect_stdout(buf):                       # keep the suite output clean
                    rc = P.main(argv)
                self.assertEqual(rc, P.EXIT_REFUSED)
                self.assertTrue(buf.getvalue().startswith("REFUSED"), buf.getvalue())
            ld.assert_not_called()
        with tempfile.TemporaryDirectory() as t:                       # a fresh process, the variable removed
            nodata, tmp = Path(t) / "nodata", Path(t) / "tmp"
            nodata.mkdir(); tmp.mkdir()
            env = {k: v for k, v in os.environ.items() if k != P.SEALED_ENV}
            env.update(OFILT_DATA_DIR=str(nodata), TMPDIR=str(tmp))
            r = subprocess.run([sys.executable, str(TOOL), "--real", "--expect-config-sha256", sha], cwd=str(ROOT),
                               env=env, capture_output=True, text=True, timeout=300)
            self.assertEqual(r.returncode, P.EXIT_REFUSED, r.stdout + r.stderr)
            self.assertIn(f"REFUSED: --real needs {P.SEALED_ENV}=1", r.stdout)
            self.assertEqual(list(tmp.iterdir()), [])                      # the run's directory removed


class TestTinyRuns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._t = tempfile.TemporaryDirectory()
        base = Path(cls._t.name)
        cls.out, cls.tmp, cls.res = [], [], []
        for i in (1, 2):
            tm, nd = base / f"tmp{i}", base / f"nodata{i}"
            o = tm / "out"                                         # --out-dir must lie under TMPDIR or /tmp
            tm.mkdir(); nd.mkdir()
            cls.res.append(tiny_run(o, tm, nd))
            cls.out.append(o); cls.tmp.append(tm)
        cls.js = [json.loads((o / f"{P.REAL_STEM}.json").read_text(encoding="utf-8")) for o in cls.out]

    @classmethod
    def tearDownClass(cls):
        cls._t.cleanup()

    def test_5_outputs_whitelisted_and_aggregates_only(self):
        for r, j in zip(self.res, self.js):
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(j["complete"])
            self.assertEqual(j["errors"], [])
            self.assertIsNone(j["aborted"])
            self.assertEqual(P.check_output(j, set(CFG["outputs"])), [])
            self.assertEqual(j["calibrator"], {"T_source": CFG["T_source"], "rows": CFG["rows"]})
            self.assertEqual(sorted(p.name for p in self.out[0].iterdir()), [f"{P.REAL_STEM}.json", f"{P.REAL_STEM}.md"])

    def test_6_registry_directory(self):
        for j, tm in zip(self.js, self.tmp):
            self.assertEqual(j["t3"]["walk_forward_calls"], 3 * 2)       # cells 9 to 11 at smoke 2
            self.assertEqual(j["t3"]["registry_lines"], j["t3"]["walk_forward_calls"])
            self.assertEqual([p.name for p in tm.iterdir()], ["out"])      # the run's own directory deleted

    def test_9_determinism(self):
        a, b = (dict(j) for j in self.js)
        self.assertNotEqual(a["runtime"], None)
        a.pop("runtime"); b.pop("runtime")
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        ma, mb = ((o / f"{P.REAL_STEM}.md").read_text(encoding="utf-8").split("## Runtime")[0] for o in self.out)
        self.assertEqual(ma, mb)


class TestSeedsAndLogs(unittest.TestCase):
    def test_7_seeds_disjoint(self):
        ours = P.seed_ranges(CFG)
        b7 = [(100_000 * (1 + ci) + 10_000 * bi, 100_000 * (1 + ci) + 10_000 * bi + 499)
              for ci in (0, 1) for bi in range(4)]
        b7b = [(1_000_000, 1_004_999)] + [(1_000_000 + 100_000 * c, 1_000_000 + 100_000 * c + 999) for c in (1, 2, 3)]
        c7 = [(3_000_000, 3_000_299), (3_100_000, 3_100_199), (3_200_000, 3_200_199)]
        p2a = [(base + off, base + off + 199) for base in (4_000_000, 4_100_000) for off in (0, 50_000, 60_000)]
        allr = ours + b7 + b7b + c7 + p2a
        for i, (lo1, hi1) in enumerate(allr):
            for lo2, hi2 in allr[i + 1:]:
                self.assertTrue(hi1 < lo2 or hi2 < lo1, ((lo1, hi1), (lo2, hi2)))
        self.assertEqual(len(ours), len(CFG["cells"]) + len(CFG["pooled_cells"]))

    def test_8_log_checks(self):
        dev = CFG["dev_panel_sha256"]
        line = lambda prov, panel, caller: json.dumps({"utc": "x", "provenance": prov, "panel_sha256": panel,
                                                       "spec_sha256": "s", "n_rows_input": 1, "caller": caller})
        with tempfile.TemporaryDirectory() as t:
            log = Path(t) / "BLIND_FIT_LOG"
            six = [line("dev_real", "736636031ca1", "test_sim_b5") for _ in range(6)]
            log.write_text("\n".join(six) + "\n", encoding="utf-8")
            self.assertEqual(P.check_log(log, 6), [])
            caller = f'File "/x/tools/{P.SCRIPT_NAME}", line 1, in _run | cal = S.DevCalibrator(base, spec)'
            log.write_text("\n".join(six + [line("dev_real", dev, caller)]) + "\n", encoding="utf-8")
            self.assertEqual(P.check_log(log, 7, panel_sha=dev, caller=P.SCRIPT_NAME), [])
            self.assertTrue(P.check_log(log, 6))                                        # wrong count
            log.write_text("\n".join(six + [line("dev_real", "0" * 64, caller)]) + "\n", encoding="utf-8")
            self.assertTrue(P.check_log(log, 7, panel_sha=dev, caller=P.SCRIPT_NAME))     # wrong hash
            log.write_text("\n".join(six + [line("dev_real", dev, "report_B7b.py")]) + "\n", encoding="utf-8")
            self.assertTrue(P.check_log(log, 7, panel_sha=dev, caller=P.SCRIPT_NAME))     # wrong caller
            log.write_text("\n".join(six + [line("synthetic", dev, caller)]) + "\n", encoding="utf-8")
            self.assertTrue(P.check_log(log, 7, panel_sha=dev, caller=P.SCRIPT_NAME))     # not dev_real


if __name__ == "__main__":
    unittest.main()
