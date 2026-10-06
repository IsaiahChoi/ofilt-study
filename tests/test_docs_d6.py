"""D6 (rebuild): PROJECT_SETUP ('after Pass 1'), restored byte for byte to docs/replacements/ and
pinned; its claims about the repo and the Claude Project are checked. Project checks run only
where /mnt/project exists. Structural only: the dev panel's date column is the one data read.
P57 (2026-10-05): the pins follow the PROJECT_SETUP refresh of 2026-10-05 (PLAN v2.3); the
PASS2_ADDENDUM §5 phase-P2-0 test changes, pre-approved."""
import hashlib
import inspect
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd  # noqa: E402

from ofilt.drift import registry as R  # noqa: E402

DOC = ROOT / "docs" / "replacements" / "PROJECT_SETUP.md"
PROJECT = Path("/mnt/project")


class TestProjectSetup(unittest.TestCase):
    def test_restored_byte_for_byte(self):
        data = DOC.read_bytes()
        self.assertTrue(hashlib.sha256(data).hexdigest().startswith("8b342d1ec69d6069"))  # P70: was c137831848fb3956; P57: was d2afcf2a1fe90074
        if (PROJECT / "PROJECT_SETUP.md").exists():
            self.assertEqual(data, (PROJECT / "PROJECT_SETUP.md").read_bytes())
        # P57: was "# What goes in the Claude Project, and why (October 2026, after Pass 1)"
        # P70: was "...; refreshed 2026-10-05)"
        self.assertTrue(DOC.read_text(encoding="utf-8").startswith(
            "# What goes in the Claude Project, and why (October 2026, after Pass 1; refreshed 2026-10-06)"))

    def test_repo_claims(self):
        for p in ("ofilt/drift", "spec", "tests", "tools", "docs", "reports", "BLIND_FIT_LOG",
                  "RUN_REGISTRY.jsonl", "PASS1_STATUS.md", "docs/DECISIONS_P14_onward.md"):
            self.assertTrue((ROOT / p).exists(), p)                              # the repo it describes
        for name in ("README.md", "PLAN.md", "DATA_DICTIONARY.md", "PROJECT_SETUP.md"):
            self.assertTrue((ROOT / "docs" / "replacements" / name).exists(), name)
        self.assertIn('open(path, "a"', inspect.getsource(R.record_run))         # registry append-only
        self.assertEqual(sorted(p.name for p in ROOT.rglob("*") if "confirm" in p.name.lower() and
                                p.suffix == ".csv"), [])                          # no sealed panel in the repo

    @unittest.skipUnless(PROJECT.exists(), "Claude Project not mounted")
    def test_project_claims(self):
        names = {p.name for p in PROJECT.iterdir()}
        never = ("panel_confirm", "book2", "dukascopy_", "histdata")
        self.assertEqual([n for n in names if any(k in n.lower() for k in never) and n != "pull_dukascopy.py"], [])
        removed = ("fx_dark_window_features.csv", "build_windows.py", "histdata_tz.py", "slim_encode.py",
                   "MASTER_README__1_.md")
        self.assertEqual([n for n in removed if n in names], [])
        for n in ("PROJECT_SETUP.md", "DATA_PROVENANCE.md", "DATA_DICTIONARY.md", "MANIFEST.json",
                  "DECISIONS_ADDENDUM.md", "DECISIONS_P14_onward.md", "panel_dev.csv", "build_panel.py",
                  "make_events.py", "events.py", "events_firm.csv", "events_boj.csv", "pull_dukascopy.py", "PLAN.md"):
            self.assertIn(n, names)                                               # 'In the project' list
        last = pd.read_csv(PROJECT / "panel_dev.csv", usecols=["date"]).date.max()
        self.assertLessEqual(last, "2021-12-31")                                  # no 2022+ rows in the Project
        # Differences recorded in REBUILD_VERIFICATION D6 (not asserted as agreement):
        self.assertIn("`PLAN.md` (v2.4)", DOC.read_text(encoding="utf-8"))                     # P70: was (v2.3); P57: was (v2.1)
        self.assertTrue((PROJECT / "PLAN.md").read_text(encoding="utf-8").startswith("# Research Plan v2.4"))  # P70: was v2.3; P57: was v2.2


if __name__ == "__main__":
    unittest.main()
