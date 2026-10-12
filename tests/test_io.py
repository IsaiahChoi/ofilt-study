import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd  # noqa: E402

from ofilt.drift import _guards_fallback as G  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift.spec import REPO_ROOT, Spec  # noqa: E402


def make_temp_repo(tmp: Path) -> Path:
    """Throwaway git repo with two commits on main and one on a side branch."""
    repo = tmp / "repo"
    repo.mkdir()
    g = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], check=True)
    subprocess.run(g + ["commit", "-q", "--allow-empty", "-m", "c1"], check=True)
    subprocess.run(g + ["tag", "early"], check=True)
    subprocess.run(g + ["checkout", "-q", "-b", "side"], check=True)
    subprocess.run(g + ["commit", "-q", "--allow-empty", "-m", "side"], check=True)
    subprocess.run(g + ["tag", "sidetag"], check=True)
    subprocess.run(g + ["checkout", "-q", "main"], check=True)
    subprocess.run(g + ["commit", "-q", "--allow-empty", "-m", "c2"], check=True)
    subprocess.run(g + ["tag", "-a", "annotated", "-m", "a"], check=True)
    return repo


class TestLoadDev(unittest.TestCase):
    def test_load_dev(self):
        df = IO.load_dev()
        self.assertEqual(df.attrs["provenance"], "dev_real")
        self.assertEqual(df.attrs["sha256"], Spec.load().data_hash("dev_panel"))
        self.assertEqual(len(df), 5124)
        self.assertEqual(df["date"].nunique(), 1708)
        self.assertEqual(set(df["ticker"]), {"5706", "5711", "5713"})
        self.assertTrue(pd.api.types.is_string_dtype(df["ticker"]))
        self.assertTrue((df["date"] < pd.Timestamp("2022-01-01")).all())
        self.assertEqual(str(df["date"].min().date()), "2015-01-06")
        self.assertEqual(str(df["date"].max().date()), "2021-12-30")
        self.assertTrue(df[["date", "ticker"]].equals(
            df[["date", "ticker"]].sort_values(["date", "ticker"]).reset_index(drop=True)))

    def test_hash_mismatch_raises(self):
        with tempfile.TemporaryDirectory() as t:
            bad = Path(t) / "panel_dev.csv"
            shutil.copy(IO.DATA_DIR / IO.DEV_FILE, bad)
            with open(bad, "ab") as fh:
                fh.write(b"\n")
            with self.assertRaises(IO.DataHashError):
                IO.load_dev(bad)

    def test_events(self):
        ev = IO.load_events_firm()
        self.assertEqual(len(ev), 163)
        self.assertEqual(ev.groupby("category").size().to_dict(),
                         {"AUDIT_CANDIDATE": 15, "MECHANICAL": 5, "STANDALONE_NEWS": 8, "TANSHIN": 135})
        self.assertEqual(len(IO.load_events_boj()), 98)
        with tempfile.TemporaryDirectory() as t:
            bad = Path(t) / "events_firm.csv"
            bad.write_bytes((IO.DATA_DIR / IO.EVENTS_FIRM_FILE).read_bytes().replace(b"2015-02-06", b"2015-02-05", 1))
            with self.assertRaises(IO.DataHashError):
                IO.load_events_firm(bad)


class TestGuardFallback(unittest.TestCase):
    def test_semantics_in_temp_repo(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_temp_repo(Path(t))
            self.assertTrue(G.is_ancestor_tag("early", repo))       # strict ancestor
            self.assertTrue(G.is_ancestor_tag("annotated", repo))   # annotated tag at HEAD
            self.assertFalse(G.is_ancestor_tag("sidetag", repo))    # exists, not an ancestor
            self.assertFalse(G.is_ancestor_tag("missing", repo))
            for bad in ("", "HEAD~1 ", "../x", "-x", None, 3):
                self.assertFalse(G.is_ancestor_tag(bad, repo))
            G.check_access("early", repo)
            with self.assertRaises(G.AccessDenied):
                G.check_access("sidetag", repo)
            not_repo = Path(t) / "plain"
            not_repo.mkdir()
            self.assertFalse(G.is_ancestor_tag("early", not_repo))

    def test_main_repo_has_no_unblinding_tags_while_draft(self):
        if Spec.load().status != "DRAFT":
            self.skipTest("spec frozen; tags expected")
        for tag in ("spec-dev-v1", "prereg-v1"):
            self.assertFalse(G.is_ancestor_tag(tag, REPO_ROOT), tag)


class TestLoadConfirm(unittest.TestCase):
    def test_denied_and_logged(self):
        with tempfile.TemporaryDirectory() as t:
            log = Path(t) / "ACCESS_LOG"
            repo = make_temp_repo(Path(t))  # P5-1 (P5Q3, P5Q4, test-change protocol): the guard on a throwaway repository without prereg-v1; was REPO's own guard, which refuses only while REPO lacks the tag
            with mock.patch.object(IO, "ACCESS_LOG_PATH", log), \
                 mock.patch.object(IO, "DATA_DIR", Path(t) / "does_not_exist"), \
                 mock.patch.object(IO, "_GUARD_REPO", repo), mock.patch.object(IO, "_external_check_access", None):  # P5-1
                with self.assertRaises(IO.AccessDenied):   # guard fires before any path is touched
                    IO.load_confirm()
                with self.assertRaises(IO.AccessDenied):
                    IO.load_confirm()
            lines = [json.loads(x) for x in log.read_text().splitlines()]
            self.assertEqual(len(lines), 2)
            for rec in lines:
                self.assertEqual((rec["tag"], rec["result"]), ("prereg-v1", "DENIED"))
                self.assertIn("utc", rec)
                self.assertIn("head", rec)

    def test_guard_is_the_only_gate(self):
        """With the tag present (temp repo), load_confirm proceeds to the file and
        fails there (no sealed file exists anywhere in this sandbox)."""
        with tempfile.TemporaryDirectory() as t:
            repo = make_temp_repo(Path(t))
            subprocess.run(["git", "-C", str(repo), "tag", "prereg-v1"], check=True)
            log = Path(t) / "ACCESS_LOG"
            with mock.patch.object(IO, "_GUARD_REPO", repo), mock.patch.object(IO, "ACCESS_LOG_PATH", log), \
                 mock.patch.object(IO, "DATA_DIR", Path(t) / "empty"), \
                 mock.patch.object(IO, "_external_check_access", None):
                with self.assertRaises(FileNotFoundError):
                    IO.load_confirm()
            self.assertEqual(json.loads(log.read_text().splitlines()[0])["result"], "GRANTED")

    def test_no_repo_override_parameter(self):
        import inspect
        self.assertNotIn("repo", inspect.signature(IO.load_confirm).parameters)


if __name__ == "__main__":
    unittest.main()
