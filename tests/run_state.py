"""P6-1c (D2, conditions 3 and 4; P6Q7 as clarified; docs/PREREG_v1.md §7.6; docs/P6_RUN2_CRITERIA.md §6): REPO's
state around the two requests of the confirmation panel, for the four tests that asserted the state before any request
(the absence of ACCESS_LOG; the registry's two dev_real lines).

The first request (P6-1, GRANTED at 221507d0..., then FileNotFoundError before any byte of the sealed panel was read)
left one ACCESS_LOG line. P6-1c renamed that file, its bytes unchanged, to reports/P6_runs/attempt1/ACCESS_LOG (D2,
condition 3), so that the unchanged script's one-shot check permits the second request. The second request writes a new
ACCESS_LOG at REPO's root.
  - Before the second request: the first request's log is the only name starting ACCESS_LOG in REPO outside .git, at
    its path, with its pinned SHA-256: one GRANTED line for prereg-v1 at 221507d0..., which descends from the tag and is
    an ancestor of HEAD. The registry holds the dev run's two lines (the tests' earlier assertions).
  - After it: REPO's root also holds ACCESS_LOG, with exactly one line, GRANTED for prereg-v1, whose head is the commit
    at which both confirm_real registry lines were recorded; that commit descends from the first request's and is an
    ancestor of HEAD. The registry holds the dev run's two lines, then the confirmation run's two (main then m7, the run
    ids of reports/P6_runs/confirm/runtime.json).
Not a test module (no test_ prefix). Imports no module of ofilt and reads no data: only the two logs, the registry,
the two runtime.json files and git's view of REPO."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCESS_LOG = ROOT / "ACCESS_LOG"
FIRST_LOG_REL = "reports/P6_runs/attempt1/ACCESS_LOG"
FIRST_LOG = ROOT / FIRST_LOG_REL
FIRST_LOG_SHA256 = "c6eb0d5ecf89f2f6b705488c71b0c281154ba94008755731739a7c0ffadfbc03"
FIRST_HEAD = "221507d01547869376e73cde51c20b86892bed95"
REGISTRY = ROOT / "RUN_REGISTRY.jsonl"
CONFIRM_RUNTIME = ROOT / "reports" / "P6_runs" / "confirm" / "runtime.json"
CONFIRM_TAG = "prereg-v1"


def confirm_run_made() -> bool:
    """True once the second request of the confirmation panel has been made: ACCESS_LOG exists at REPO's root."""
    return ACCESS_LOG.exists()


def access_log_names() -> list:
    """Every name starting ACCESS_LOG under REPO outside .git, relative to REPO, sorted (names only)."""
    found = []
    for r, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not (Path(r) == ROOT and d == ".git")]
        found += [os.path.relpath(os.path.join(r, n), ROOT) for n in dirs + names if n.startswith("ACCESS_LOG")]
    return sorted(found)


def _registry() -> list:
    return [json.loads(x) for x in REGISTRY.read_text(encoding="utf-8").splitlines() if x.strip()]


def _git_rc(*args) -> int:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True).returncode


def _tag_commit() -> str:
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", f"refs/tags/{CONFIRM_TAG}^{{commit}}"],
                          capture_output=True, text=True, check=True).stdout.strip()


def _one_granted_line(tc, path):
    lines = path.read_text(encoding="utf-8").splitlines()
    tc.assertEqual(len(lines), 1)
    rec = json.loads(lines[0])
    tc.assertEqual((rec["result"], rec["tag"]), ("GRANTED", CONFIRM_TAG))
    return rec


def check_first_request(tc) -> None:
    """The first request's ACCESS_LOG, kept byte for byte at FIRST_LOG: one GRANTED line at FIRST_HEAD."""
    tc.assertTrue(FIRST_LOG.is_file())
    tc.assertEqual(hashlib.sha256(FIRST_LOG.read_bytes()).hexdigest(), FIRST_LOG_SHA256)
    rec = _one_granted_line(tc, FIRST_LOG)
    tc.assertEqual(rec["head"], FIRST_HEAD)
    tc.assertEqual(_git_rc("merge-base", "--is-ancestor", _tag_commit(), FIRST_HEAD), 0)
    tc.assertEqual(_git_rc("merge-base", "--is-ancestor", FIRST_HEAD, "HEAD"), 0)


def check_access_log_before(tc) -> None:
    """Before the second request: the first request's log is the only ACCESS_LOG in REPO."""
    tc.assertEqual(access_log_names(), [FIRST_LOG_REL])
    check_first_request(tc)


def check_access_log_after(tc) -> None:
    """After the second request: the first request's log unchanged, and ACCESS_LOG at REPO's root with one GRANTED line
    for prereg-v1 at the commit of both confirm_real registry lines."""
    tc.assertEqual(access_log_names(), sorted(["ACCESS_LOG", FIRST_LOG_REL]))
    check_first_request(tc)
    rec = _one_granted_line(tc, ACCESS_LOG)
    reg = _registry()
    tc.assertEqual(len(reg), 4)
    tc.assertEqual([r["provenance"] for r in reg[2:]], ["confirm_real", "confirm_real"])
    tc.assertEqual([r["git_commit"] for r in reg[2:]], [rec["head"], rec["head"]])
    tc.assertEqual(_git_rc("merge-base", "--is-ancestor", _tag_commit(), rec["head"]), 0)
    tc.assertEqual(_git_rc("merge-base", "--is-ancestor", FIRST_HEAD, rec["head"]), 0)
    tc.assertEqual(_git_rc("merge-base", "--is-ancestor", rec["head"], "HEAD"), 0)


def check_registry_after(tc, reg, dev_run) -> None:
    """The registry after the second request: the dev run's two lines, then the confirmation run's two."""
    tc.assertEqual(len(reg), 4)
    tc.assertEqual(sorted(r["run_id"] for r in reg[:2]), sorted(dev_run["run_ids"].values()))
    tc.assertEqual({r["provenance"] for r in reg[:2]}, {"dev_real"})
    confirm_ids = json.loads(CONFIRM_RUNTIME.read_text(encoding="utf-8"))["run_ids"]
    tc.assertEqual([r["run_id"] for r in reg[2:]], [confirm_ids["main"], confirm_ids["m7"]])
    tc.assertEqual({r["provenance"] for r in reg[2:]}, {"confirm_real"})
