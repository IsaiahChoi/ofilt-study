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
        # P3-6 (switch): the configuration is the sealed run's, bound to the pre-switch spec; a rebuild differs only there
        run = json.loads((ROOT / "reports" / f"{P.REAL_STEM}.json").read_text(encoding="utf-8"))
        self.assertEqual(run["config_sha256"], P.sha256_file(P.CONFIG_PATH))
        line7 = json.loads((ROOT / "BLIND_FIT_LOG").read_text(encoding="utf-8").splitlines()[6])
        self.assertEqual(CFG["spec_sha256"], line7["spec_sha256"])
        self.assertEqual(P.validate_config(CFG), ["key 'spec_sha256' differs from the registry"])
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
            self.assertIn("REFUSED: configuration: [\"key 'spec_sha256' differs from the registry\"]", r.stdout)   # P3-6 (switch)
            self.assertEqual(list(tmp.iterdir()), [])                      # the run's directory removed


class TestTinyRuns(unittest.TestCase):
    """P3-6 (switch): the configuration now differs from a rebuild by its spec_sha256, so every synthetic run is refused
    before it starts. The tiny runs' tests 5, 6, 9 and 15 retired at the switch (PASS3_STATUS, Test changes); test 17
    asserts the refusal."""

    def test_17_synthetic_run_refused_after_the_switch(self):
        with tempfile.TemporaryDirectory() as t:
            tm, nd = Path(t) / "tmp1", Path(t) / "nodata1"
            o = tm / "out"                                         # --out-dir must lie under TMPDIR or /tmp
            tm.mkdir(); nd.mkdir()
            r = tiny_run(o, tm, nd)
            self.assertEqual(r.returncode, P.EXIT_REFUSED, r.stdout + r.stderr)
            self.assertEqual(r.stdout.strip(), "REFUSED: configuration: [\"key 'spec_sha256' differs from the registry\"]")
            self.assertFalse(o.exists())                           # nothing written to --out-dir
            self.assertEqual(list(tm.iterdir()), [])               # the run's own directory removed


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


class TestP32d(unittest.TestCase):
    """P3-2d: R1 (the generalised log check; the logged-panel check), R2 (no exception message printed) and the
    rehearsal script (static)."""

    def test_10_r1_log_check_and_logged_panel(self):
        dev = CFG["dev_panel_sha256"]
        caller = f'File "/x/tools/{P.SCRIPT_NAME}", line 1, in main | cal = S.DevCalibrator(base, spec)'
        rec = lambda prov, c: json.dumps({"utc": "x", "provenance": prov, "panel_sha256": "none", "spec_sha256": "s",
                                          "n_rows_input": 1, "caller": c})
        with tempfile.TemporaryDirectory() as t:
            log = Path(t) / "BLIND_FIT_LOG"
            log.write_text(rec("synthetic", caller) + "\n", encoding="utf-8")
            self.assertEqual(P.check_log(log, 1, caller=P.SCRIPT_NAME, provenance="synthetic"), [])
            self.assertTrue(P.check_log(log, 1, caller=P.SCRIPT_NAME))                       # default: dev_real
            log.write_text((rec("synthetic", caller) + "\n") * 2, encoding="utf-8")
            self.assertTrue(P.check_log(log, 1, caller=P.SCRIPT_NAME, provenance="synthetic"))   # wrong count
            log.write_text(rec("dev_real", caller) + "\n", encoding="utf-8")
            self.assertTrue(P.check_log(log, 1, caller=P.SCRIPT_NAME, provenance="synthetic"))   # wrong provenance
            log.write_text(rec("synthetic", "report_B7b.py") + "\n", encoding="utf-8")
            self.assertTrue(P.check_log(log, 1, caller=P.SCRIPT_NAME, provenance="synthetic"))   # wrong caller
        import pandas as pd
        from ofilt.drift import blind as Bl
        f = pd.DataFrame({"x": [1.0]})
        f.attrs = {"provenance": "dev_real", "sha256": dev}
        P.assert_logged_panel(f, CFG, Bl)                                                   # passes
        for attrs in ({"provenance": "dev_real", "sha256": "0" * 64}, {"provenance": "dev_real"},
                      {"provenance": "synthetic", "sha256": dev}):
            g = f.copy()
            g.attrs = attrs
            with self.assertRaises(P.AbortRun):
                P.assert_logged_panel(g, CFG, Bl)

    def test_11_r2_generic_handlers_print_no_message(self):
        tree = ast.parse(TOOL.read_text(encoding="utf-8"))
        fns = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in ("main", "_run")}
        self.assertEqual(set(fns), {"main", "_run"})
        for name, fn in fns.items():
            generic = [h for h in ast.walk(fn) if isinstance(h, ast.ExceptHandler)
                       and isinstance(h.type, ast.Name) and h.type.id == "Exception"]
            self.assertTrue(generic, name)
            for h in generic:
                for n in ast.walk(ast.Module(body=h.body, type_ignores=[])):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("str", "repr"):
                        self.assertFalse(any(isinstance(x, ast.Name) and x.id == h.name for x in n.args), name)
                    if isinstance(n, ast.FormattedValue):
                        self.assertFalse(isinstance(n.value, ast.Name) and n.value.id == h.name, name)
                    if isinstance(n, ast.Attribute):
                        self.assertFalse(isinstance(n.value, ast.Name) and n.value.id == "traceback"
                                         and n.attr.startswith("print"), name)
                        self.assertFalse(isinstance(n.value, ast.Name) and n.value.id == h.name
                                         and n.attr == "args", name)

    def test_12_r2_abort_text(self):
        try:
            raise ValueError("a message that must not be printed")
        except ValueError as e:
            txt = P._abort_text(e)
            self.assertEqual(txt, f"ValueError at line {e.__traceback__.tb_lineno}")
        try:
            P.check_log(Path("/nonexistent/p3_2d/BLIND_FIT_LOG"), 1)                          # raised inside the tool
        except FileNotFoundError as e:
            txt = P._abort_text(e)
            self.assertRegex(txt, r"^FileNotFoundError at line \d+$")
            self.assertNotIn("nonexistent", txt)

    def test_13_rehearsal_script_static(self):
        sh = (ROOT / "tools" / "p3_3_rehearse.sh").read_text(encoding="utf-8")
        lines = sh.splitlines()
        self.assertEqual(lines[0], "set -euo pipefail")
        self.assertNotIn("--real", sh)
        self.assertNotIn("OFILT_RUN_SEALED=1", sh)
        check = next(i for i, l in enumerate(lines) if "${OFILT_RUN_SEALED+x}" in l and "refuse" in l)
        first_py = next(i for i, l in enumerate(lines) if "python" in l and not l.lstrip().startswith("#"))
        self.assertLess(check, first_py)
        # P3-3b: --expect-config-sha256 is required and checked against the configuration, before any Python line
        expect = next(i for i, l in enumerate(lines) if '[[ "$EXPECT" =~ ^[0-9a-f]{64}$ ]]' in l and "refuse" in l)
        cfg = next(i for i, l in enumerate(lines) if '[ "$CFG_SHA" = "$EXPECT" ]' in l and "refuse" in l)
        self.assertIn('CFG_SHA="$(shasum -a 256 docs/P3_RUN_CONFIG.json', sh)
        self.assertLess(expect, first_py)
        self.assertLess(cfg, first_py)
        self.assertIn("cfg == exp", sh)
        self.assertNotIn("P3_2b_smoke", sh)


class TestP33b(unittest.TestCase):
    """P3-3b (D4.3a): T6's centred outputs and the leak test."""

    def test_14_centred_block(self):
        from scipy import stats
        z = float(stats.norm.ppf(0.975))                                      # the tool's z2 at alpha 0.05
        bh = np.array([0.5, -0.5, 0.25, -0.25, 1.0, -1.0, 0.125, -0.125])     # dyadic, n = 8: mean and shifts exact
        se = np.full(8, 0.25)
        out = P.centred_block(bh, se, z, C)
        self.assertEqual(out, P.centred_block(bh + 3.0, se, z, C))           # a constant shift changes nothing
        self.assertEqual(set(out), {"centred_reject", "sd", "mean_se", "se_over_sd"})
        k = sum(abs(b - bh.mean()) > z * s for b, s in zip(bh, se))          # by hand: 0.5, -0.5, 1.0, -1.0 exceed 0.49
        self.assertEqual(k, 4)
        self.assertEqual(out["centred_reject"], {"k": 4, "n": 8, "rate": 0.5, "wilson95": list(C.wilson(4, 8))})
        sd = float(np.sqrt(np.sum(bh ** 2) / 7))
        self.assertAlmostEqual(out["sd"], sd, places=15)
        self.assertEqual(out["mean_se"], 0.25)
        self.assertAlmostEqual(out["se_over_sd"], 0.25 / sd, places=15)
        rng = np.random.default_rng(3)
        b2, s2 = rng.normal(size=200), rng.uniform(0.5, 1.5, 200)
        x, y = P.centred_block(b2, s2, z, C), P.centred_block(b2 + 0.37, s2, z, C)
        self.assertEqual(x["centred_reject"], y["centred_reject"])
        self.assertAlmostEqual(x["sd"], y["sd"], places=12)

    def test_16_leak_invariance(self):
        """Adding delta * usdjpy_ret to the calibrator's residuals (in the test only) shifts every OLS-DK and Huber-DK
        b_hat by delta and leaves their se, Huber's share and the centred counts unchanged, in a full-window and an
        early-window cell: a window's coefficient deviation cannot reach T6's centred outputs."""
        from scipy import stats
        from ofilt.drift import inference as I
        spec = Spec.load()
        z = float(stats.norm.ppf(0.975))
        df = S.synthetic_panel(300, b=0.4, a2=-0.2, seed=93, tails="t5")
        with tempfile.TemporaryDirectory() as t, mock.patch.object(S, "BLIND_FIT_LOG_PATH", Path(t) / "LOG"):
            cal = S.DevCalibrator(df, spec)
        cells = {"full": [cal.positions(np.random.default_rng(100 + r), cal.T) for r in range(6)],
                 "early": [C.window_positions(80, cal.T, np.random.default_rng(200 + r)) for r in range(6)]}

        def fits():
            out = {}
            for name, poss in cells.items():
                v = {k: [] for k in ("ob", "ose", "hb", "hse", "hsh")}
                for r, pos in enumerate(poss):
                    y = cal.draw(0.0, 0.0, seed=7 + r, positions=pos)
                    f = C.fit_t(y, spec, "y_sim")
                    h = I.fit_huber(I.build_design(y, spec, target="y_sim"), spec)
                    ph = h.param("usdjpy_ret")
                    for k, val in (("ob", f["b"]), ("ose", f["se"]), ("hb", ph["estimate"]), ("hse", ph["se"]),
                                   ("hsh", h.info["share_downweighted"])):
                        v[k].append(val)
                out[name] = {k: np.array(x) for k, x in v.items()}
            return out

        base = fits()
        delta = 0.3
        cal._resid = cal._resid + delta * cal._pred["usdjpy_ret"].to_numpy(dtype=float)   # the test only
        moved = fits()
        for name in cells:
            b0, b1 = base[name], moved[name]
            self.assertLess(float(np.max(np.abs(b1["ob"] - b0["ob"] - delta))), 1e-10, name)
            self.assertLess(float(np.max(np.abs(b1["ose"] - b0["ose"]))), 1e-10, name)
            self.assertLess(float(np.max(np.abs(b1["hb"] - b0["hb"] - delta))), 1e-8, name)
            self.assertLess(float(np.max(np.abs(b1["hse"] - b0["hse"]))), 1e-8, name)
            self.assertLess(float(np.max(np.abs(b1["hsh"] - b0["hsh"]))), 1e-8, name)
            for kb, ks in (("ob", "ose"), ("hb", "hse")):
                self.assertEqual(P.centred_block(b0[kb], b0[ks], z, C)["centred_reject"]["k"],
                                 P.centred_block(b1[kb], b1[ks], z, C)["centred_reject"]["k"], (name, kb))


if __name__ == "__main__":
    unittest.main()
