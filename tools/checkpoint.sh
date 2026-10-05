#!/usr/bin/env bash
# usage: bash tools/checkpoint.sh "<item id>" ["<extra commit-message paragraph>" ...]
# Pass 2 checkpoint (P2-0e, P51): runs the test suite, then commits as "checkpoint: <item id>".
# Portable: the repo root comes from git, OFILT_DATA_DIR from the environment, python from the
# active venv. No mirroring, no tarball. Refuses to checkpoint on any test failure.
# The real-data sealed fit is opt-in via the OFILT_RUN_SEALED variable; checkpoints unset it.
set -uo pipefail

item="${1:-}"
if [ -z "$item" ]; then echo "usage: bash tools/checkpoint.sh \"<item id>\""; exit 2; fi
shift
root="$(git rev-parse --show-toplevel)" || { echo "not inside a git repository; not checkpointing"; exit 2; }
cd "$root" || exit 2

if [ -z "${OFILT_DATA_DIR:-}" ]; then echo "OFILT_DATA_DIR is unset; not checkpointing"; exit 2; fi
if [ -z "${VIRTUAL_ENV:-}" ]; then echo "VIRTUAL_ENV is unset (activate the venv); not checkpointing"; exit 2; fi
py="$(command -v python || true)"
if [ "$py" != "$VIRTUAL_ENV/bin/python" ]; then
    echo "python is '$py', not '$VIRTUAL_ENV/bin/python'; not checkpointing"; exit 2
fi
echo "interpreter: $py"
echo "version: $(python -c 'import sys; print(sys.version)')"
echo "repo: $root"
echo "OFILT_DATA_DIR: $OFILT_DATA_DIR"

B6="reports/B6_coverage.json"   # rewritten by test_b6_identities on every run; float noise off the sandbox (Flag 16)
status_before="$(git status --porcelain)"
diff_before="$(git diff --binary | shasum -a 256 | cut -d' ' -f1)"
echo "before suite: git diff --binary sha256 $diff_before"
echo "before suite: git status --porcelain"
[ -n "$status_before" ] && echo "$status_before"

log="$(mktemp "${TMPDIR:-/tmp}/ckpt_tests.XXXXXX")"
env -u OFILT_RUN_SEALED python -m unittest discover -s tests > "$log" 2>&1; rc=$?
tail -n 4 "$log"
if [ $rc -ne 0 ]; then echo "TESTS FAILED; not checkpointing (log: $log)"; exit 1; fi

status_after="$(git status --porcelain)"
diff_after="$(git diff --binary | shasum -a 256 | cut -d' ' -f1)"
if [ "$status_after" != "$status_before" ] || [ "$diff_after" != "$diff_before" ]; then
    if printf '%s\n' "$status_before" | grep -q -F " $B6"; then
        echo "the suite changed the tree and $B6 was already modified before it; not checkpointing"; exit 1
    fi
    if ! git diff --quiet -- "$B6"; then
        echo "the suite rewrote $B6; its diff:"
        git diff -- "$B6"
        git checkout -- "$B6" && echo "restored $B6"
        status_after="$(git status --porcelain)"
        diff_after="$(git diff --binary | shasum -a 256 | cut -d' ' -f1)"
    fi
    if [ "$status_after" != "$status_before" ] || [ "$diff_after" != "$diff_before" ]; then
        echo "the suite changed the working tree beyond $B6; not checkpointing"
        git status --porcelain
        exit 1
    fi
fi

git status --short
msg=(-m "checkpoint: $item")
for para in "$@"; do msg+=(-m "$para"); done
git add -A && git commit -q "${msg[@]}" && echo "commit $(git rev-parse HEAD)"
