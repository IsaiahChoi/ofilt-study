"""D3b (rebuild): machine-checkable claims of P36 (pass sequencing and tag semantics;
docs/DECISIONS_P14_onward.md, adopted, never edited) against the rebuilt repo. Steps 1-7 are a
plan; what is checkable is the tag semantics 'as implemented', that the two tags are the only
unblinding events in code, the lock (spec DRAFT until spec-dev-v1), the AM-xx amendment form,
and that nothing but the sealed fits has touched real FX and targets. No data are read."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import io  # noqa: E402
from ofilt.drift.spec import SIZE_RULE, Spec  # noqa: E402

TAGS = ("spec-dev-v1", "prereg-v1")


class TestP36(unittest.TestCase):
    def test_tag_semantics_as_implemented(self):
        self.assertEqual(B.REQUIRED_TAGS, {B.SYNTHETIC: (), B.DEV_REAL: ("spec-dev-v1",),
                                           B.CONFIRM_REAL: ("spec-dev-v1", "prereg-v1")})
        self.assertEqual(io.CONFIRM_TAG, "prereg-v1")                          # load_confirm gate (P29)
        for t in TAGS:
            self.assertFalse(B._tag_ok(t))                                      # neither exists in Pass 1
        naming = sorted(str(p.relative_to(ROOT)) for d in ("ofilt", "tools") for p in (ROOT / d).rglob("*.py")
                        if any(t in p.read_text() for t in TAGS))
        self.assertEqual(naming, ["ofilt/drift/blind.py", "ofilt/drift/io.py"])  # the only unblinding events

    def test_lock_amendments_and_nothing_real_before_the_tag(self):
        s = Spec.load()
        self.assertEqual(s.status, "DRAFT")
        self.assertIn("FROZEN only when Isaiah tags spec-dev-v1", (ROOT / "spec" / "analysis_spec_dev_v1.yaml").read_text())
        self.assertIn("decided before tag", SIZE_RULE)                          # = before spec-dev-v1 (P36)
        heads = re.findall(r"^## (AM-\d\d) ", (ROOT / "spec" / "SPEC_AMENDMENTS.md").read_text(), re.M)
        self.assertEqual(heads, ["AM-01", "AM-02", "AM-03", "AM-04", "AM-05"])   # AM-03, AM-04, AM-05 (row 27)
        log = [json.loads(x) for x in (ROOT / "BLIND_FIT_LOG").read_text().splitlines() if x.strip()]
        self.assertEqual(len(log), 7)                                           # only the sealed fits (P29): Pass 1's six and P3-4's line 7 (DQ5)
        self.assertEqual((ROOT / "RUN_REGISTRY.jsonl").read_text(), "")         # no real forecast run


if __name__ == "__main__":
    unittest.main()
