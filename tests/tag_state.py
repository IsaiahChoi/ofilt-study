"""P3-8b (supervisor message of 2026-10-07): the repository's tag state, for the tests that hold before and after
spec-dev-v1. spec_tagged and check_spec_tag read REPO's own tags; blinded points the guard at a throwaway git
repository in which neither spec-dev-v1 nor prereg-v1 exists, so a test of an entry point's refusal still refuses
whatever REPO's tags are, and nothing runs past the guard. Not a test module (no test_ prefix); no data are read."""
import contextlib
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ofilt.drift import blind as B  # noqa: E402

SPEC_PATH = "spec/analysis_spec_dev_v1.yaml"
FROZEN_SPEC_SHA256 = "feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26"   # AM-10: the frozen spec


def _git(*args, text=True):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=text)


def spec_tagged() -> bool:
    """True iff spec-dev-v1 exists in REPO; check_spec_tag and the guard check the rest."""
    return "spec-dev-v1" in _git("tag", "-l").stdout.split()


def check_spec_tag(tc) -> None:
    """With spec-dev-v1 present: it is an annotated tag, its commit is an ancestor of HEAD, and the spec at the tag is
    the frozen spec."""
    tc.assertEqual(_git("cat-file", "-t", "refs/tags/spec-dev-v1").stdout.strip(), "tag")
    tc.assertEqual(_git("merge-base", "--is-ancestor", "refs/tags/spec-dev-v1^{commit}", "HEAD").returncode, 0)
    spec = _git("show", f"spec-dev-v1:{SPEC_PATH}", text=False).stdout
    tc.assertEqual(hashlib.sha256(spec).hexdigest(), FROZEN_SPEC_SHA256)


@contextlib.contextmanager
def blinded():
    """For the duration of the block, the guard (blind._GUARD_REPO, with no external guard) points at a new git
    repository with one empty commit and no tag."""
    with tempfile.TemporaryDirectory() as t:
        repo = Path(t) / "repo"
        repo.mkdir()
        g = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], check=True)
        subprocess.run(g + ["commit", "-q", "--allow-empty", "-m", "blinded"], check=True)
        with mock.patch.object(B, "_GUARD_REPO", repo), mock.patch.object(B, "_external_check_access", None):
            yield repo
