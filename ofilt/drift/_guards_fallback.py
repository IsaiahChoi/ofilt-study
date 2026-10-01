"""Fallback access guard, used only when `ofilt.guards.check_access` is absent.

Contract (same as the real guard): `check_access(tag)` returns None iff git
tag `tag` exists and its commit is an ancestor of (or equal to) HEAD of the
repository containing this code; otherwise it raises AccessDenied. Every
failure mode (no git, not a repo, no such tag, not an ancestor, timeout, bad
tag name) is a denial: the guard fails closed.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
_TAG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")


class AccessDenied(PermissionError):
    """The required git tag is not an ancestor of HEAD."""


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=30)


def repo_root(start: str | Path | None = None) -> Path | None:
    try:
        r = _git(Path(start) if start is not None else PACKAGE_DIR, "rev-parse", "--show-toplevel")
    except Exception:
        return None
    return Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None


def head_commit(repo: str | Path | None = None) -> str | None:
    root = repo_root(repo)
    if root is None:
        return None
    try:
        r = _git(root, "rev-parse", "--verify", "--quiet", "HEAD")
    except Exception:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def is_ancestor_tag(tag: str, repo: str | Path | None = None) -> bool:
    """True iff refs/tags/<tag> resolves to a commit that is an ancestor of HEAD."""
    if not isinstance(tag, str) or _TAG_RE.match(tag) is None:
        return False
    root = repo_root(repo)
    if root is None:
        return False
    try:
        r = _git(root, "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}")
        if r.returncode != 0 or not r.stdout.strip():
            return False
        r2 = _git(root, "merge-base", "--is-ancestor", r.stdout.strip(), "HEAD")
        return r2.returncode == 0
    except Exception:
        return False


def check_access(tag: str, repo: str | Path | None = None) -> None:
    if not is_ancestor_tag(tag, repo):
        raise AccessDenied(f"access denied: git tag {tag!r} is not an ancestor of HEAD "
                           f"(repo={repo_root(repo)})")
