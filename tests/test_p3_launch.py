"""P3-3f (supervisor message of 2026-10-07): tests of tools/p3_4_launch.sh, the P3-4 launcher. Tests 1 to 6 read the
script's text; tests 7 and 8 run it in a subprocess that refuses before any git or Python command. No test sets the
sealed-run variable to 1, and no data file is read."""
import hashlib
import json
import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCH = ROOT / "tools" / "p3_4_launch.sh"
SH = LAUNCH.read_text(encoding="utf-8")
LINES = SH.splitlines()
CODE = [(i, l) for i, l in enumerate(LINES) if not l.lstrip().startswith("#")]   # (index, line), comments dropped
SEALED_LINE = "OFILT_RUN_SEALED=1"


def first(pred):
    return next(i for i, l in CODE if pred(l))


class TestLaunchScript(unittest.TestCase):
    def test_1_shape_and_usage(self):
        self.assertEqual(LINES[0], "set -euo pipefail")
        usage = next(l for l in LINES if l.startswith("USAGE="))
        for arg in ("--commit", "--expect-config-sha256", "--data-dir", "--dry-run"):
            self.assertIn(arg, usage)

    def test_2_the_one_command(self):
        hits = [l for l in LINES if SEALED_LINE in l]
        self.assertEqual(len(hits), 1, hits)
        cmd = hits[0]
        self.assertTrue(cmd.lstrip().startswith("OFILT_RUN_SEALED=1 OFILT_DATA_DIR="), cmd)
        self.assertIn("caffeinate -i", cmd)
        self.assertIn("tools/p3_sealed_run.py --real --expect-config-sha256", cmd)
        self.assertFalse([l for l in LINES if re.search(r"\b(export|declare\s+-x|typeset\s+-x)\b.*OFILT_RUN_SEALED", l)])
        self.assertEqual([l for l in LINES if "--real" in l], [cmd])

    def test_3_order(self):
        env_refusal = first(lambda l: "${OFILT_RUN_SEALED+x}" in l and "refuse" in l)
        first_py = first(lambda l: '"$PY" tools/' in l or re.search(r"\bpython3?\s+\S", l) is not None
                         or "/activate" in l)
        self.assertLess(env_refusal, first_py)
        cmd = first(lambda l: SEALED_LINE in l)
        dry_exit = first(lambda l: '[ -n "$DRY" ]' in l and "exit 0" in l)
        self.assertLess(dry_exit, cmd)
        refusals = [i for i, l in CODE if re.search(r"\brefuse\b", l) and not l.startswith("refuse()")]
        self.assertTrue(refusals)
        self.assertLess(max(refusals), cmd)

    def test_4_check_config_line(self):
        lines = [l for _, l in CODE if "--check-config" in l]
        self.assertEqual(len(lines), 1, lines)
        self.assertIn("env -u OFILT_RUN_SEALED", lines[0])

    def test_5_constants(self):
        const = dict(re.findall(r"^([A-Z_]+)=([0-9a-f]{64})  # ", SH, re.M))
        log = (ROOT / "reports" / "P3_3_rehearsal2.log").read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r"^tools/p3_sealed_run\.py sha256 ([0-9a-f]{64})$", log, re.M)), {const["TOOL_SHA"]})
        self.assertEqual(set(re.findall(r"^ofilt/drift/calib\.py sha256 ([0-9a-f]{64})$", log, re.M)), {const["CALIB_SHA"]})
        self.assertEqual(set(re.findall(r"^docs/P3_RUN_CONFIG\.json sha256 ([0-9a-f]{64});", log, re.M)),
                         {const["CONFIG_SHA"]})
        cfg = json.loads((ROOT / "docs" / "P3_RUN_CONFIG.json").read_text(encoding="utf-8"))
        self.assertEqual(const["SPEC_SHA"], cfg["spec_sha256"])
        raw = (ROOT / "BLIND_FIT_LOG").read_bytes()
        self.assertEqual(const["BASELINE"], hashlib.sha256(b"".join(raw.splitlines(keepends=True)[:6])).hexdigest())
        p30 = re.search(r"^BLIND_FIT_LOG sha256 \(baseline[^\n]*?([0-9a-f]{64})$",
                        (ROOT / "reports" / "P3_0_report.txt").read_text(encoding="utf-8"), re.M).group(1)
        self.assertEqual(const["BASELINE"], p30)
        dev = re.search(r'^DEV_FILE = "([^"]+)"$', (ROOT / "ofilt" / "drift" / "io.py").read_text(encoding="utf-8"), re.M)
        self.assertIn(f"DEV_FILE={dev.group(1)}  # ", SH)

    def test_6_no_tags_and_outputs_only_tested(self):
        for tag in ("spec-dev-v1", "prereg-v1"):
            self.assertNotIn(tag, SH)
        touching = [l for _, l in CODE if "P3_4_sealed_run" in l]
        self.assertTrue(touching)
        for l in touching:
            self.assertTrue(re.search(r"\[ !? ?-[ef] reports/P3_4_sealed_run\.(json|md) \]", l), l)
            rest = re.sub(r"\[ !? ?-[ef] reports/P3_4_sealed_run\.(json|md) \]|shasum -a 256 reports/P3_4_sealed_run\.(json|md)"
                          r"|\"reports/P3_4_sealed_run\.(json|md) [^\"$]*", "", l)
            self.assertNotIn("P3_4_sealed_run", rest, l)


class TestLaunchRefusals(unittest.TestCase):
    def run_launch(self, args, sealed=None):
        env = {k: v for k, v in os.environ.items() if k != "OFILT_RUN_SEALED"}
        if sealed is not None:
            env["OFILT_RUN_SEALED"] = sealed                        # never "1"
        self.assertNotEqual(sealed, "1")
        return subprocess.run(["bash", str(LAUNCH), *args], cwd=str(ROOT), env=env, capture_output=True, text=True,
                              timeout=60)

    def test_7_no_arguments(self):
        r = self.run_launch([])
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertTrue(r.stdout.startswith("LAUNCH REFUSED"), r.stdout)
        self.assertNotIn("LAUNCHING", r.stdout)

    def test_8_sealed_variable_present(self):
        r = self.run_launch(["--commit", "0" * 40, "--expect-config-sha256", "0" * 64, "--data-dir", "/tmp/p3_3f_nodata"],
                            sealed="0")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertTrue(r.stdout.startswith("LAUNCH REFUSED"), r.stdout)
        self.assertIn("OFILT_RUN_SEALED", r.stdout.splitlines()[0])
        self.assertNotIn("LAUNCHING", r.stdout)


if __name__ == "__main__":
    unittest.main()
