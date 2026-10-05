"""P51 (2026-10-05): the original Pass 1 build code is frozen under build/pass1/, byte for byte
(P2-0b). Each file's SHA-256 must equal its `code` entry in docs/PASS2_INPUTS.json, and the folder
holds exactly these three files. They never change; docs/PASS2_INPUTS.json is itself pinned by
test_docs_p2."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ("build_panel.py", "make_events.py", "events.py")


class TestBuildPass1Frozen(unittest.TestCase):
    def test_hashes_equal_pass2_inputs(self):
        code = json.loads((ROOT / "docs" / "PASS2_INPUTS.json").read_text(encoding="utf-8"))["code"]
        for name in FROZEN:
            with self.subTest(file=name):
                digest = hashlib.sha256((ROOT / "build" / "pass1" / name).read_bytes()).hexdigest()
                self.assertEqual(digest, code[name]["sha256"])

    def test_only_the_frozen_files(self):
        present = sorted(p.name for p in (ROOT / "build" / "pass1").iterdir()
                         if p.name != "__pycache__" and not p.name.startswith("."))
        self.assertEqual(present, sorted(FROZEN))


if __name__ == "__main__":
    unittest.main()
