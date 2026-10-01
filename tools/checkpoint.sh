#!/usr/bin/env bash
# usage: bash tools/checkpoint.sh "<item id>"
# Runs the test suite, commits, mirrors the tree to outputs, re-tars.
# Refuses to checkpoint on test failure unless FORCE=1 (then the failure
# must be recorded in PASS1_STATUS.md).
set -uo pipefail
cd /home/claude/ofilt_pass1
python -m unittest discover -s tests > /tmp/ckpt_tests.txt 2>&1; rc=$?
tail -n 4 /tmp/ckpt_tests.txt
if [ $rc -ne 0 ] && [ "${FORCE:-0}" != "1" ]; then echo "TESTS FAILED; not checkpointing"; exit 1; fi
git add -A && git commit -q -m "checkpoint: $1" && echo "commit $(git rev-parse --short HEAD)"
rm -rf /mnt/user-data/outputs/ofilt_pass1 && mkdir -p /mnt/user-data/outputs
cp -r /home/claude/ofilt_pass1 /mnt/user-data/outputs/ofilt_pass1
find /mnt/user-data/outputs/ofilt_pass1 -name __pycache__ -prune -exec rm -rf {} +
tar --exclude=__pycache__ -czf /mnt/user-data/outputs/ofilt_pass1.tar.gz -C /home/claude ofilt_pass1
cp PASS1_STATUS.md /mnt/user-data/outputs/PASS1_STATUS.md
ls -la /mnt/user-data/outputs/ofilt_pass1.tar.gz
