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
sys.path.insert(0, str(Path(__file__).resolve().parent))  # P3-8b: the tests folder, for tag_state
import tag_state as TS  # noqa: E402  (P3-8b)
import run_state as RS  # noqa: E402  (P6-1c, D2)

TAGS = ("spec-dev-v1", "prereg-v1")


class TestP36(unittest.TestCase):
    def test_tag_semantics_as_implemented(self):
        self.assertEqual(B.REQUIRED_TAGS, {B.SYNTHETIC: (), B.DEV_REAL: ("spec-dev-v1",),
                                           B.CONFIRM_REAL: ("spec-dev-v1", "prereg-v1")})
        self.assertEqual(io.CONFIRM_TAG, "prereg-v1")                          # load_confirm gate (P29)
        self.assertEqual(B._tag_ok("spec-dev-v1"), TS.spec_tagged())  # P3-8b: was "for t in TAGS: self.assertFalse(B._tag_ok(t))" ("neither exists in Pass 1")
        self.assertEqual(B._tag_ok("prereg-v1"), TS.prereg_tagged())  # P5-1 (P5Q4, test-change protocol): was self.assertFalse(B._tag_ok("prereg-v1")) ("prereg-v1 stays absent until Pass 5")
        if TS.prereg_tagged():  # P5-1: with the tag, it is annotated, follows spec-dev-v1 and holds the pinned documents
            TS.check_prereg_tag(self)  # P5-1
        naming = sorted(str(p.relative_to(ROOT)) for d in ("ofilt", "tools") for p in (ROOT / d).rglob("*.py")
                        if any(t in p.read_text() for t in TAGS))
        self.assertEqual(naming, ["ofilt/drift/blind.py", "ofilt/drift/io.py"])  # the only unblinding events

    def test_lock_amendments_and_nothing_real_before_the_tag(self):
        s = Spec.load()
        self.assertEqual(s.status, "FROZEN")                                     # AM-10 (P3-6): frozen at the switch
        self.assertIn("frozen at the Pass 3 switch (AM-10)", (ROOT / "spec" / "analysis_spec_dev_v1.yaml").read_text())
        self.assertIn("decided before tag", SIZE_RULE)                          # = before spec-dev-v1 (P36)
        heads = re.findall(r"^## (AM-\d\d) ", (ROOT / "spec" / "SPEC_AMENDMENTS.md").read_text(), re.M)
        self.assertEqual(heads, ["AM-01", "AM-02", "AM-03", "AM-04", "AM-05", "AM-07", "AM-09", "AM-10"])   # + the switch (P3-6)
        log = [json.loads(x) for x in (ROOT / "BLIND_FIT_LOG").read_text().splitlines() if x.strip()]
        self.assertEqual(len(log), 7)                                           # only the sealed fits (P29): Pass 1's six and P3-4's line 7 (DQ5)
        # P4Q6, P4Q40 (P4-6, test-change protocol): was `(ROOT / "RUN_REGISTRY.jsonl").read_text() == ""`.
        # After the dev run the registry holds exactly its two forecasting calls, both dev_real (reports/P4_runs/dev).
        reg = [json.loads(x) for x in (ROOT / "RUN_REGISTRY.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        dev_run = json.loads((ROOT / "reports" / "P4_runs" / "dev" / "runtime.json").read_text(encoding="utf-8"))
        # P6-1c (D2, condition 4; P6Q7; the pre-registration's §7.6; test-change protocol): the dev run's two assertions now
        # hold until the second request of the confirmation panel (the first added no registry line), which appends its two
        # confirm_real lines (tests/run_state.py). Was: the two, unconditionally.
        if RS.confirm_run_made():
            RS.check_registry_after(self, reg, dev_run)
        else:
            self.assertEqual(sorted(r["run_id"] for r in reg), sorted(dev_run["run_ids"].values()))
            self.assertEqual({r["provenance"] for r in reg}, {"dev_real"})


if __name__ == "__main__":
    unittest.main()
