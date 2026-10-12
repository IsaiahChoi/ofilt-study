"""P3-8b (supervisor message of 2026-10-07): the repository's tag state, for the tests that hold before and after
spec-dev-v1. spec_tagged and check_spec_tag read REPO's own tags; blinded points the guard at a throwaway git
repository in which neither spec-dev-v1 nor prereg-v1 exists, so a test of an entry point's refusal still refuses
whatever REPO's tags are, and nothing runs past the guard. Not a test module (no test_ prefix); no data are read.

P5-1 (P5Q4; docs/P5_CONFIRM_SCRIPT_SPEC.md section 4): the same for prereg-v1. prereg_tagged and check_prereg_tag
read the tags of REPO, or of the repository given as root (the throwaway repositories of tests/test_p5_tag_state.py);
io_blinded points io's guard, as well as blind's, at a throwaway repository without the tags, so a refusal test of
io.load_confirm refuses whatever REPO's tags are. PREREG_SHA256 is the pre-registration's pin, set at P5-2 when the
document is installed (a documentation pin); until then check_prereg_tag fails, so a tag made before the pin fails
the suite."""
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
from ofilt.drift import io as IO  # noqa: E402  (P5-1: io_blinded)

SPEC_PATH = "spec/analysis_spec_dev_v1.yaml"
FROZEN_SPEC_SHA256 = "feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26"   # AM-10: the frozen spec
SPEC_TAG, PREREG_TAG = "spec-dev-v1", "prereg-v1"                                           # P5-1
CONFIG_PATH = "docs/P4_CONFIRM_CONFIG.json"                                                 # P5-1
CONFIG_SHA256 = "5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd"          # P5-1: P4Q9 to P4Q31, version 1
PREREG_PATH = "docs/PREREG_v1.md"                                                           # P5-1 (P5Q6)
PREREG_SHA256 = "79447ba199ce2360fb1fc8c51ae5d0eea3c20ba2645d6167c17ba1e1792f35e6"  # P5-2 (P5Q18, documentation pin): was None (P5-1)


def _git_at(root, *args, text=True):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=text)


def _git(*args, text=True):
    return _git_at(ROOT, *args, text=text)


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


def prereg_tagged(root=ROOT) -> bool:
    """P5-1: True iff prereg-v1 exists in the repository at root (REPO by default); check_prereg_tag checks the rest."""
    return PREREG_TAG in _git_at(root, "tag", "-l").stdout.split()


def check_prereg_tag(tc, root=ROOT, prereg_sha256=None) -> None:
    """P5-1: with prereg-v1 present at root: it is an annotated tag; its commit is an ancestor of HEAD, and spec-dev-v1's
    commit is an ancestor of it; and at the tag, the frozen spec, the configuration and the pre-registration document
    have their pinned SHA-256 (prereg_sha256, default PREREG_SHA256, which must be set)."""
    want = PREREG_SHA256 if prereg_sha256 is None else prereg_sha256
    tc.assertIsNotNone(want, "the pre-registration's pin, PREREG_SHA256, is set at P5-2")
    tc.assertEqual(_git_at(root, "cat-file", "-t", f"refs/tags/{PREREG_TAG}").stdout.strip(), "tag")
    tc.assertEqual(_git_at(root, "merge-base", "--is-ancestor", f"refs/tags/{PREREG_TAG}^{{commit}}", "HEAD").returncode, 0)
    tc.assertEqual(_git_at(root, "merge-base", "--is-ancestor", f"refs/tags/{SPEC_TAG}^{{commit}}",
                           f"refs/tags/{PREREG_TAG}^{{commit}}").returncode, 0)
    for path, digest in ((SPEC_PATH, FROZEN_SPEC_SHA256), (CONFIG_PATH, CONFIG_SHA256), (PREREG_PATH, want)):
        blob = _git_at(root, "show", f"refs/tags/{PREREG_TAG}:{path}", text=False)
        tc.assertEqual(blob.returncode, 0, path)
        tc.assertEqual(hashlib.sha256(blob.stdout).hexdigest(), digest, path)


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


@contextlib.contextmanager
def io_blinded():
    """P5-1: as blinded(), and io's guard (io._GUARD_REPO, with no external guard) points at the same repository, so
    io.load_confirm refuses whatever REPO's tags are. It does not patch io.ACCESS_LOG_PATH or io.DATA_DIR; the
    caller does (P5Q3)."""
    with blinded() as repo, mock.patch.object(IO, "_GUARD_REPO", repo), \
            mock.patch.object(IO, "_external_check_access", None):
        yield repo
