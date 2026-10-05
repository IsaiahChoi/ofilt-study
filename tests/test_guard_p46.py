"""P46 (2026-10-05): the tag gate is conjunctive and fail-closed in io._check_access and
blind._tag_ok. The fallback check (the tag exists and is an ancestor of HEAD) always runs; if
the external guard (ofilt.guards.check_access) is importable it must ALSO return None or True
without raising. Any exception, and any other return value, is a denial. Every case runs in a
throwaway git repo with a stand-in external guard; no data is read."""
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from test_io import make_temp_repo  # noqa: E402

TAGS = (B.SPEC_TAG, B.PREREG_TAG)


class TestConjunctiveGate(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.repo = make_temp_repo(self.tmp)
        self.log = self.tmp / "ACCESS_LOG"

    def tag(self, *tags, at="HEAD"):
        for t in tags:
            subprocess.run(["git", "-C", str(self.repo), "tag", t, at], check=True)

    def gates(self, stack, external):
        """Point both gates at the temp repo, with `external` as the importable external guard."""
        for target, name, value in ((IO, "_GUARD_REPO", self.repo), (IO, "_external_check_access", external),
                                    (IO, "ACCESS_LOG_PATH", self.log), (IO, "DATA_DIR", self.tmp / "empty"),
                                    (B, "_GUARD_REPO", self.repo), (B, "_external_check_access", external)):
            stack.enter_context(mock.patch.object(target, name, value))

    def last_access(self):
        return json.loads(self.log.read_text().splitlines()[-1])["result"]

    def assert_denied(self, external):
        with ExitStack() as stack:
            self.gates(stack, external)
            for t in TAGS:
                with self.assertRaises(IO.AccessDenied):
                    IO._check_access(t)
                self.assertFalse(B._tag_ok(t), t)
            with self.assertRaises(B.BlindingError):
                B.require_unblinded(provenance=B.DEV_REAL)
            with self.assertRaises(B.BlindingError):
                B.require_unblinded(provenance=B.CONFIRM_REAL)
            with self.assertRaises(IO.AccessDenied):
                IO.load_confirm()
        self.assertEqual(self.last_access(), "DENIED")

    def test_external_returns_false_denied(self):
        """Tags are ancestors (the fallback grants) but the external guard returns False, or any
        value other than None/True: denied. The comparison is identity, so np.True_ is denied too."""
        self.tag(*TAGS)
        for value in (False, 0, 1, "", "granted", [], np.True_):
            calls = []
            with self.subTest(value=value):
                self.assert_denied(lambda tag, v=value: (calls.append(tag), v)[1])
                self.assertIn(B.PREREG_TAG, calls)  # the external guard was consulted

    def test_external_returns_none_tag_absent_denied(self):
        """The external guard returns None, but the tag is absent (then: present only on a side
        branch, not an ancestor of HEAD): the fallback still denies."""
        self.assert_denied(lambda tag: None)
        self.tag(*TAGS, at="side")
        self.assert_denied(lambda tag: None)

    def test_external_raises_denied(self):
        """Tags are ancestors, but the external guard raises (including a signature mismatch): denied."""
        self.tag(*TAGS)

        def unavailable(tag):
            raise RuntimeError("guard unavailable")

        def wrong_signature():
            return None

        for external in (unavailable, wrong_signature):
            with self.subTest(external=external.__name__):
                self.assert_denied(external)

    def test_both_satisfied_granted(self):
        """Tags are ancestors AND the external guard returns None or True: granted."""
        self.tag(*TAGS)
        for value in (None, True):
            calls = []
            with self.subTest(value=value), ExitStack() as stack:
                self.gates(stack, lambda tag, v=value: (calls.append(tag), v)[1])
                for t in TAGS:
                    self.assertIsNone(IO._check_access(t))
                    self.assertTrue(B._tag_ok(t), t)
                self.assertEqual(B.require_unblinded(provenance=B.DEV_REAL), B.DEV_REAL)
                self.assertEqual(B.require_unblinded(provenance=B.CONFIRM_REAL), B.CONFIRM_REAL)
                with self.assertRaises(FileNotFoundError):  # granted: proceeds to the (absent) sealed file
                    IO.load_confirm()
                self.assertEqual(self.last_access(), "GRANTED")
                self.assertEqual(set(calls), set(TAGS))


if __name__ == "__main__":
    unittest.main()
