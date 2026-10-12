"""P5-1 (P5Q4): tests/tag_state.py's prereg-v1 helpers against throwaway repositories, so that the side of the tag on
which prereg-v1 exists is exercised before REPO has it (docs/P5_CONFIRM_SCRIPT_SPEC.md, section 4.2; exactly its 5
test methods). The throwaway repositories hold copies of REPO's frozen spec and configuration and a stand-in
pre-registration document; no data are read, and REPO's own tags are read only by test 5."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tag_state as TS  # noqa: E402
from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402

STAND_IN = b"# a stand-in pre-registration (tests/test_p5_tag_state.py)\n"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Repo:
    """A throwaway repository: commit 1 holds the frozen spec and the configuration; commit 2 adds the stand-in
    pre-registration; commit 3 is a later records commit on main; a side branch holds one commit off commit 2."""

    def __init__(self, root: Path):
        self.root = root
        root.mkdir()
        self.run("init", "-q", "-b", "main")
        for rel in (TS.SPEC_PATH, TS.CONFIG_PATH):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes((ROOT / rel).read_bytes())
        self.commit("c1: spec and configuration")
        self.c1 = self.rev("HEAD")
        (root / TS.PREREG_PATH).write_bytes(STAND_IN)
        self.commit("c2: pre-registration")
        self.c2 = self.rev("HEAD")
        self.run("checkout", "-q", "-b", "side")
        (root / "side.txt").write_text("side\n")
        self.commit("side")
        self.side = self.rev("HEAD")
        self.run("checkout", "-q", "main")
        (root / "records.md").write_text("records\n")
        self.commit("c3: records")

    def run(self, *args):
        return subprocess.run(["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                              check=True, capture_output=True, text=True)

    def commit(self, msg):
        self.run("add", "-A")
        self.run("commit", "-q", "-m", msg)

    def rev(self, ref):
        return self.run("rev-parse", ref).stdout.strip()

    def tag(self, name, at, annotated=True):
        self.run("tag", *(["-a", name, "-m", name] if annotated else [name]), at)


class TestP5TagState(unittest.TestCase):
    # 1
    def test_constants(self):
        self.assertEqual((TS.SPEC_TAG, TS.PREREG_TAG), ("spec-dev-v1", "prereg-v1"))
        self.assertEqual((TS.SPEC_TAG, TS.PREREG_TAG), (B.SPEC_TAG, B.PREREG_TAG))
        self.assertEqual(TS.PREREG_TAG, IO.CONFIRM_TAG)
        self.assertEqual(sha((ROOT / TS.SPEC_PATH).read_bytes()), TS.FROZEN_SPEC_SHA256)
        self.assertEqual(sha((ROOT / TS.CONFIG_PATH).read_bytes()), TS.CONFIG_SHA256)
        self.assertEqual(json.loads((ROOT / TS.CONFIG_PATH).read_text(encoding="utf-8"))["version"], 1)
        self.assertEqual(TS.PREREG_PATH, "docs/PREREG_v1.md")
        self.assertEqual(TS.PREREG_SHA256, sha((ROOT / TS.PREREG_PATH).read_bytes()))  # P5-2 (P5Q18, documentation pin): was self.assertIsNone(TS.PREREG_SHA256) (P5-1)

    # 2
    def test_prereg_absent_and_present(self):
        with tempfile.TemporaryDirectory() as t:
            r = Repo(Path(t) / "r")
            r.tag(TS.SPEC_TAG, r.c1)
            self.assertFalse(TS.prereg_tagged(r.root))
            r.tag(TS.PREREG_TAG, r.c2)
            self.assertTrue(TS.prereg_tagged(r.root))
            TS.check_prereg_tag(self, root=r.root, prereg_sha256=sha(STAND_IN))

    # 3
    def test_check_prereg_tag_refuses(self):
        def failing(setup, pin=sha(STAND_IN), label=""):
            with tempfile.TemporaryDirectory() as t:
                r = Repo(Path(t) / "r")
                setup(r)
                with self.assertRaises(AssertionError, msg=label):
                    TS.check_prereg_tag(self, root=r.root, prereg_sha256=pin)

        def lightweight(r):
            r.tag(TS.SPEC_TAG, r.c1)
            r.tag(TS.PREREG_TAG, r.c2, annotated=False)

        def not_an_ancestor(r):
            r.tag(TS.SPEC_TAG, r.c1)
            r.tag(TS.PREREG_TAG, r.side)

        def before_the_spec_tag(r):
            r.tag(TS.SPEC_TAG, r.c2)
            r.tag(TS.PREREG_TAG, r.c1)

        def no_spec_tag(r):
            r.tag(TS.PREREG_TAG, r.c2)

        def changed_configuration(r):
            r.tag(TS.SPEC_TAG, r.c1)
            (r.root / TS.CONFIG_PATH).write_bytes(b"{}\n")
            r.commit("c4: another configuration")
            r.tag(TS.PREREG_TAG, "HEAD")

        def absent(r):
            r.tag(TS.SPEC_TAG, r.c1)

        def good(r):
            r.tag(TS.SPEC_TAG, r.c1)
            r.tag(TS.PREREG_TAG, r.c2)

        for setup in (lightweight, not_an_ancestor, before_the_spec_tag, no_spec_tag, changed_configuration, absent):
            failing(setup, label=setup.__name__)
        failing(good, pin="0" * 64, label="wrong pin")
        failing(good, pin=None, label="no pin: PREREG_SHA256 is None at P5-1")
        with tempfile.TemporaryDirectory() as t:              # the stand-in without the pre-registration file
            r = Repo(Path(t) / "r")
            r.tag(TS.SPEC_TAG, r.c1)
            r.tag(TS.PREREG_TAG, r.c1)
            with self.assertRaises(AssertionError):
                TS.check_prereg_tag(self, root=r.root, prereg_sha256=sha(STAND_IN))

    # 4
    def test_io_blinded_refuses_whatever_the_guard_repository_holds(self):
        with tempfile.TemporaryDirectory() as t:
            r = Repo(Path(t) / "r")
            r.tag(TS.SPEC_TAG, r.c1)
            r.tag(TS.PREREG_TAG, r.c2)
            access = Path(t) / "ACCESS_LOG"
            empty = Path(t) / "empty"
            empty.mkdir()
            with mock.patch.object(IO, "_GUARD_REPO", r.root), mock.patch.object(B, "_GUARD_REPO", r.root), \
                    mock.patch.object(IO, "_external_check_access", None), \
                    mock.patch.object(B, "_external_check_access", None), \
                    mock.patch.object(IO, "ACCESS_LOG_PATH", access), mock.patch.object(IO, "DATA_DIR", empty):
                self.assertTrue(B._tag_ok(TS.PREREG_TAG))           # the stand-in "REPO" is tagged
                with TS.io_blinded() as repo:
                    self.assertNotEqual(Path(IO._GUARD_REPO), r.root)
                    self.assertEqual(Path(IO._GUARD_REPO), Path(B._GUARD_REPO))
                    self.assertEqual(Path(IO._GUARD_REPO), repo)
                    self.assertFalse(B._tag_ok(TS.PREREG_TAG))
                    with self.assertRaises(IO.AccessDenied):
                        IO.load_confirm()
                self.assertEqual(Path(IO._GUARD_REPO), r.root)       # restored
            self.assertEqual([json.loads(x)["result"] for x in access.read_text().splitlines()], ["DENIED"])
            self.assertEqual(list(empty.iterdir()), [])

    # 5
    def test_repo_state_both_sides(self):
        tagged = TS.prereg_tagged()
        self.assertEqual(tagged, B._tag_ok(TS.PREREG_TAG))
        if tagged:
            self.assertTrue(TS.spec_tagged())
            TS.check_prereg_tag(self)
        self.assertEqual((ROOT / TS.PREREG_PATH).exists(), TS.PREREG_SHA256 is not None)


if __name__ == "__main__":
    unittest.main()
