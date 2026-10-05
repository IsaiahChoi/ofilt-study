"""D4 (rebuild): README and PLAN. The Project holds the CURRENT adopted versions (README of
2026-10-04; PLAN v2.2, which supersedes v2.1 = Pass 1's original D4b output). They are restored
byte for byte to docs/replacements/ and pinned; this module checks that each edit P14-P36
assigns to README or PLAN is present. Superseded Pass 1 text is not reconstructed.
P57 (2026-10-05): the pins follow the 2026-10-05 refresh (README of 2026-10-05; PLAN v2.3, which
supersedes v2.2); the PASS2_ADDENDUM §5 phase-P2-0 test changes, pre-approved."""
import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {"README.md": ("README__2_.md", "9596fe7d2de098c1"), "PLAN.md": ("PLAN.md", "8030770119338ad8")}  # P57: was dc7983326fc4964e / 220fc762a511b13a


def text(name):
    return (ROOT / "docs" / "replacements" / name).read_text(encoding="utf-8")


def section(t, start, end):
    i = t.index(start)
    return t[i:t.index(end, i + 1)]


class TestRestored(unittest.TestCase):
    def test_byte_for_byte(self):
        for name, (project_name, prefix) in DOCS.items():
            data = (ROOT / "docs" / "replacements" / name).read_bytes()
            self.assertTrue(hashlib.sha256(data).hexdigest().startswith(prefix), name)
            src = Path("/mnt/project") / project_name
            if src.exists():
                self.assertEqual(data, src.read_bytes(), name)
        self.assertTrue(text("PLAN.md").startswith("# Research Plan v2.3"))      # P57: was v2.2
        # P57: was "Supersedes:** v2.1 (Pass 1, item D4b, `docs/replacements/PLAN.md`)"
        self.assertIn("Supersedes:** v2.2 (2026-10-04), which superseded v2.1 (Pass 1, item D4b, "
                      "`docs/replacements/PLAN.md`)", text("PLAN.md"))


class TestReadme(unittest.TestCase):
    def test_p14_p16_p20_edits(self):
        r = text("README.md")
        self.assertIsNone(re.search(r"two[- ]spec|never mix", r, re.I))                       # P14, P16
        self.assertIn("**The auction-conditional specification is retired** (P16)", r)
        self.assertIn('Features come only from the explicit allowlist** in `ofilt/drift/schema.py` (P20). '
                      'This replaces the old rule "features come from unprefixed columns".', r)           # P20
        self.assertIn("`open`, `close`, `prev_close` (auction or target prices) and `audit_flag` "
                      "(outcome-selected) are **forbidden** as features", r)


class TestPlan(unittest.TestCase):
    def test_content_edits(self):
        p = text("PLAN.md")
        required = {
            "P14 two-sided H1": "Two-sided test at α = 0.05",
            "P16 H2 retired": "**H2: RETIRED (P16).**",
            "P15 H3 restated": "**H3 (secondary, restated, P15).** a₂ = 0",
            "P17 beta": "past-only **expanding** β, estimated on non-excluded rows, lagged one day",
            "P19 controls": "### 3.3 Controls (P19)",
            "P22 crisis windows": "These replace v2.0's named crisis windows",
            "P23 TOST": "**Equivalence (P23).** A TOST test",
            "P26 M6 dropped": "M6 (a Kalman filter on time-varying β) is dropped.",
            "P26 Lemma K advisor": "replaces Lemma K [ADVISOR QUESTION]",
            "P27 eligible dates": "500 **eligible** training dates",
            "P30 MDE in b": "**b ≈ 0.257**",
            "P33 robustness": "## 6. Robustness (pre-listed; P33)",
        }
        for entry, frag in required.items():
            self.assertIn(frag, p, entry)
        self.assertIn("EWJ:** it is USD-denominated", section(p, "### 3.3 Controls", "### 3.4"))

    def test_p36_milestone_order(self):
        s8 = section(text("PLAN.md"), "## 8. Passes and milestones (P36 order; P44 naming)", "**Pass 2 is done when:**")
        rows = [r.split("|")[2].strip() for r in s8.splitlines() if re.match(r"\| (\d|—) \|", r)]
        self.assertEqual(rows, ["Analysis machine", "Data and rebuild (`PASS2_HANDOFF.md`)",
                                "Calibration, dev still blinded", "**Tag `spec-dev-v1`**",
                                "Dev first look (exploratory) + P13(b) dry run", "Pre-registration (S4)",
                                "Confirmation"])                                                  # P36 steps 1-7
        self.assertIn("**tag `prereg-v1`**", s8)
        self.assertIn("171 tests, 5 skipped by default", s8)    # ORIGINAL repo; the rebuild differs (D4 difference 1)


if __name__ == "__main__":
    unittest.main()
