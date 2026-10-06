"""D5 (rebuild): DATA_DICTIONARY. The Project copy is the post-P20 version; it is restored byte for
byte to docs/replacements/ and pinned, and its schema groups, PRE_OPEN list and derived features
are checked against ofilt/drift/schema.py. Structural only; no data are read."""
import hashlib
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ofilt.drift import schema as SC  # noqa: E402

DOC = ROOT / "docs" / "replacements" / "DATA_DICTIONARY.md"
GROUPS = ("KEYS", "PRE_OPEN_FEATURES", "EXCLUSION_FLAGS", "INFORMATIONAL", "ROBUSTNESS_ONLY", "AT_OPEN",
          "TARGET_INPUTS", "PROVENANCE", "CONTEMPORANEOUS", "PRE_OPEN_ROBUSTNESS")   # P50 (row 13)


def text():
    return DOC.read_text(encoding="utf-8")


class TestDataDictionary(unittest.TestCase):
    def test_restored_byte_for_byte(self):
        data = DOC.read_bytes()
        self.assertTrue(hashlib.sha256(data).hexdigest().startswith("14f9e1ac8348e5a9"))   # P50: the 60-column DATA_DICTIONARY (row 13)
        src = Path("/mnt/project/DATA_DICTIONARY.md")
        if src.exists():
            self.assertEqual(data, src.read_bytes())

    def test_p20_wording(self):
        t = text()
        self.assertIsNone(re.search(r"unprefixed\s*(=|means|columns are)\s*pre-open", t, re.I))   # old wording gone
        self.assertIn("Being unprefixed does not make a column a feature: `open`, `close`, `prev_close` and "
                      "`audit_flag` are unprefixed and forbidden", t)                    # P20's replacement
        self.assertIn("explicit frozensets in `ofilt/drift/schema.py` (DECISIONS P20)", t)
        self.assertIn("Unknown columns are refused everywhere, and nothing selects columns by prefix", t)
        self.assertIn("`usdjpy_bars` is the only PROVENANCE column a derived feature may read", t)
        self.assertIn("**not features in any specification**. The auction-conditional specification is retired (P16)", t)

    def test_groups_table_matches_schema(self):
        t = text()
        rows = {}
        for line in t[t.index("## Schema groups"):t.index("### PRE_OPEN_FEATURES")].splitlines():
            m = re.match(r"\| ([A-Z_]+) \| (\d+) \| (.*?) \| (.*) \|$", line)
            if m:
                rows[m.group(1)] = (int(m.group(2)), set(re.findall(r"`([a-z_0-9]+)`", m.group(3))))
        self.assertEqual(list(rows), list(GROUPS))
        for g in GROUPS:
            n, named = rows[g]
            self.assertEqual(n, len(getattr(SC, g)), g)
            if named:                                                           # explicit member lists
                self.assertEqual(named, set(getattr(SC, g)), g)
        self.assertEqual(sum(n for n, _ in rows.values()), 60)   # P50 (row 13)
        pre = section_names(t, "### PRE_OPEN_FEATURES", "**Model-side features**")
        self.assertEqual(pre, set(SC.PRE_OPEN_FEATURES))
        derived = section_names(t, "**Model-side features**", "### Flags")
        self.assertTrue(set(SC.DERIVED_FEATURES) <= derived)
        every = set().union(*(getattr(SC, g) for g in GROUPS))
        self.assertTrue(every <= set(re.findall(r"`([a-z][a-z0-9_]*)`", t)))   # all 60 columns documented (P50, row 13)


def section_names(t, start, end):
    i = t.index(start)
    return set(re.findall(r"`([a-z][a-z0-9_]*)`", t[i:t.index(end, i + 1)]))


if __name__ == "__main__":
    unittest.main()
