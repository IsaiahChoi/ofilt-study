"""P57 (2026-10-05): the kit documents synced into docs/ in P2-0h are pinned byte for byte to
their entries in SHA256SUMS_2026-10-05.txt of pass2_kit_2026-10-05 (its eight docs/ lines). PLAN,
README and PROJECT_SETUP replace the Pass 1 copies in docs/replacements/; the other five are new in
docs/. A later approved edit to any of them (e.g. PASS2_INPUTS.json at P2-6) updates its pin here."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINNED = {  # repo path -> SHA-256 of kit docs/<same file name>
    "docs/DATA_PROVENANCE.md": "0efa0121cbd4f2d074b18eab3f776c3e7f58381c3db9623aaf662ba6d5f36aed",  # P70 (row 22): was c9a6293bf7e965a0c0232e2c2317e3456b1014e87b406d321ce3040d2d081ae5
    "docs/DECISIONS_P37_onward.md": "b22bdc15ba5cae086738d7639ca8b95069bbb668b8d386de1a5c3a9a7e0175f1",
    "docs/PASS2_ADDENDUM.md": "36a7dadc23a5c0fea41019ecafc5317a4ed5bae779428af3e5925b5d9d3e316c",
    "docs/PASS2_HANDOFF.md": "0f89948ecc827040bc27ca4fdae9178bd8b70327c9b884439bffe279872e3f8f",
    "docs/PASS2_INPUTS.json": "d697a93a337aa5dd5bbc04f8f67faa852aad3ddda3ad71b529575bdbc3761f56",  # P70 (row 22): was 5a5b353267260afdd95e4745b37cd76ece3f79a3d228cca8e9089153c27604a0
    "docs/replacements/PLAN.md": "641fb05f4ec6958a4e55672af00453b73da8f1388fd539c22d9d67c0f272e6c5",  # P70 (row 22): was 8030770119338ad852cbd6b9b0d132ac6b815e7c16438a21dfd4485798473fcb
    "docs/replacements/PROJECT_SETUP.md": "8b342d1ec69d6069476d4e8ec3478456298ca4d9c34a6b1f1f100143edc9d091",  # P70 (row 22): was c137831848fb39566eec6441979af9172b188c01e5e5499174896b8ea9881078
    "docs/replacements/README.md": "4896b40905f4426c618085ea589a2dab9596f1f0187010aa879c653a08f6b48f",  # P70 (row 22): was 9596fe7d2de098c17b5be2b54ba249cafde9359b872e7e81ff29e9d95db4b9f6
}
NEW_PINNED = {  # P70 (row 22): docs added at P2-6
    "docs/DECISIONS_P58_onward.md": "e7874506706198850c9c680bf052859d6fcf453f511f6bc3ba5403dbef119131",
}


class TestKitDocsPinned(unittest.TestCase):
    def test_byte_for_byte(self):
        for rel, digest in PINNED.items():
            with self.subTest(doc=rel):
                self.assertEqual(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest(), digest)

    def test_the_eight_kit_docs(self):
        self.assertEqual(sorted(Path(rel).name for rel in PINNED),
                         ["DATA_PROVENANCE.md", "DECISIONS_P37_onward.md", "PASS2_ADDENDUM.md", "PASS2_HANDOFF.md",
                          "PASS2_INPUTS.json", "PLAN.md", "PROJECT_SETUP.md", "README.md"])

    def test_p70_new_docs_pinned(self):   # P70 (row 22): the new decision file, pinned at P2-6
        for rel, digest in NEW_PINNED.items():
            with self.subTest(doc=rel):
                self.assertEqual(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
