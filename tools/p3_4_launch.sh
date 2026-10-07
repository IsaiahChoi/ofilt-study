set -euo pipefail
# tools/p3_4_launch.sh: the P3-4 launcher (P3-3f; PASS3_STATUS Decision log, "The launcher").
# usage:  bash tools/p3_4_launch.sh --commit <40 lowercase hex> --expect-config-sha256 <64 lowercase hex> --data-dir <path> [--dry-run]
#   --commit                 the sanctioned commit: HEAD must equal it
#   --expect-config-sha256   docs/P3_RUN_CONFIG.json's SHA-256: it must equal the rehearsed value below
#   --data-dir               the folder that holds the dev panel (an absolute path); OFILT_DATA_DIR of the one command
#   --dry-run                run every check, print the summary, and stop before the command
# Run it with bash. It wraps the one sealed-run command (marked below) with checks before and after it, and changes
# nothing the sealed run executes. Any refusal prints "LAUNCH REFUSED: <reason>" and exits 2, before the command. A dry
# run ends with "LAUNCH DRY RUN: all checks passed" and exit 0. Otherwise it prints "LAUNCHING", runs the command,
# prints the tool's own status line and the post-run checks, then "LAUNCH FINISHED". It exits with the tool's exit code,
# or with 4 after "POST-RUN CHECK FAILED". It never prints, reads or parses the contents of the run's outputs.

refuse() { echo "LAUNCH REFUSED: $1"; exit 2; }

# The rehearsed values, each read by script from its source when this file was written (P3-3f).
TOOL_SHA=bd21c4503490aee0561c618f6ee02fd50e6be0dea4e5152f10d7579e4e609837  # tools/p3_sealed_run.py, as reports/P3_3_rehearsal2.log prints it
CALIB_SHA=31f7b8ac3d81ff5123f8dc3f0bc2cf1871652f132d15653915c94b5a79224ad6  # ofilt/drift/calib.py, as reports/P3_3_rehearsal2.log prints it
CONFIG_SHA=ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e  # docs/P3_RUN_CONFIG.json, as reports/P3_3_rehearsal2.log prints it
SPEC_SHA=0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee408561f68f96fd94d3b0f9  # spec/analysis_spec_dev_v1.yaml: docs/P3_RUN_CONFIG.json's spec_sha256
BASELINE=dad93285d2911abc6c7145c160d729df1126b24b439302bd8577cf407d397301  # BLIND_FIT_LOG's six lines: the P3-0 baseline in reports/P3_0_report.txt
DEV_FILE=panel_dev.csv  # the dev panel's file name, as ofilt/drift/io.py names it (DEV_FILE)

# 1. The arguments: each required one exactly once and well formed; no unknown argument.
USAGE="usage: bash tools/p3_4_launch.sh --commit <40 lowercase hex> --expect-config-sha256 <64 lowercase hex> --data-dir <path> [--dry-run]"
COMMIT=""; EXPECT=""; DATA_DIR=""; DRY=""
N_COMMIT=0; N_EXPECT=0; N_DATA=0; N_DRY=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --commit)
      [ "$#" -ge 2 ] || refuse "--commit needs a value ($USAGE)"
      COMMIT="$2"; N_COMMIT=$((N_COMMIT + 1)); shift 2 ;;
    --expect-config-sha256)
      [ "$#" -ge 2 ] || refuse "--expect-config-sha256 needs a value ($USAGE)"
      EXPECT="$2"; N_EXPECT=$((N_EXPECT + 1)); shift 2 ;;
    --data-dir)
      [ "$#" -ge 2 ] || refuse "--data-dir needs a value ($USAGE)"
      DATA_DIR="$2"; N_DATA=$((N_DATA + 1)); shift 2 ;;
    --dry-run)
      DRY=1; N_DRY=$((N_DRY + 1)); shift ;;
    *) refuse "unknown argument '$1' ($USAGE)" ;;
  esac
done
[ "$N_COMMIT" -eq 1 ] || refuse "--commit is required exactly once ($USAGE)"
[ "$N_EXPECT" -eq 1 ] || refuse "--expect-config-sha256 is required exactly once ($USAGE)"
[ "$N_DATA" -eq 1 ] || refuse "--data-dir is required exactly once ($USAGE)"
[ "$N_DRY" -le 1 ] || refuse "--dry-run may be given at most once ($USAGE)"
[[ "$COMMIT" =~ ^[0-9a-f]{40}$ ]] || refuse "--commit must be 40 lowercase hex"
[[ "$EXPECT" =~ ^[0-9a-f]{64}$ ]] || refuse "--expect-config-sha256 must be 64 lowercase hex"
[[ "$DATA_DIR" == /* ]] || refuse "--data-dir must be an absolute path"

# 2. The sealed-run variable must be absent from the environment, with any value (before any Python line).
if [ -n "${OFILT_RUN_SEALED+x}" ]; then refuse "OFILT_RUN_SEALED is set in the environment (to any value); unset it"; fi

# 3. HEAD of the repository that contains this script must equal --commit.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
HEAD_NOW="$(git rev-parse HEAD)"
[ "$HEAD_NOW" = "$COMMIT" ] || refuse "HEAD $HEAD_NOW differs from --commit $COMMIT"

# 4. The tree must be clean, untracked files included.
[ -z "$(git status --porcelain --untracked-files=all)" ] || refuse "git status --porcelain --untracked-files=all is not empty"

# 5. The configuration, the tool, calib.py and the spec must be the rehearsed files.
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
[ "$EXPECT" = "$CONFIG_SHA" ] || refuse "--expect-config-sha256 differs from the rehearsed configuration SHA-256"
CFG_NOW="$(sha docs/P3_RUN_CONFIG.json)"
[ "$CFG_NOW" = "$CONFIG_SHA" ] || refuse "docs/P3_RUN_CONFIG.json's SHA-256 differs from the rehearsed value"
TOOL_NOW="$(sha tools/p3_sealed_run.py)"
[ "$TOOL_NOW" = "$TOOL_SHA" ] || refuse "tools/p3_sealed_run.py's SHA-256 differs from the rehearsed value"
CALIB_NOW="$(sha ofilt/drift/calib.py)"
[ "$CALIB_NOW" = "$CALIB_SHA" ] || refuse "ofilt/drift/calib.py's SHA-256 differs from the rehearsed value"
SPEC_NOW="$(sha spec/analysis_spec_dev_v1.yaml)"
[ "$SPEC_NOW" = "$SPEC_SHA" ] || refuse "spec/analysis_spec_dev_v1.yaml's SHA-256 differs from the configuration's spec_sha256"

# 6. The blinding log, the run registry, the access log and the outputs: the state before the run.
LOG_NOW="$(sha BLIND_FIT_LOG)"
LOG_N="$(awk 'END {print NR}' BLIND_FIT_LOG)"
[ "$LOG_NOW" = "$BASELINE" ] && [ "$LOG_N" = 6 ] || refuse "BLIND_FIT_LOG differs from the P3-0 baseline or does not have exactly 6 lines ($LOG_N)"
[ -f RUN_REGISTRY.jsonl ] && [ ! -s RUN_REGISTRY.jsonl ] || refuse "RUN_REGISTRY.jsonl is not 0 bytes"
[ ! -e ACCESS_LOG ] || refuse "ACCESS_LOG exists"
[ ! -e reports/P3_4_sealed_run.json ] || refuse "reports/P3_4_sealed_run.json exists"
[ ! -e reports/P3_4_sealed_run.md ] || refuse "reports/P3_4_sealed_run.md exists"

# 7. The machine must be on AC power (pmset -g ps, as the rehearsal script checks it).
PS_OUT="$(pmset -g ps)"
POWER="${PS_OUT%%$'\n'*}"
[[ "$PS_OUT" == *"AC Power"* ]] || refuse "not on AC Power ($POWER)"

# The interpreter, chosen as the rehearsal script chooses it.
set +u
source "$HOME/venvs/ofilt_p2/bin/activate"
set -u
PY="$(command -v python)"
[ "$PY" = "$VIRTUAL_ENV/bin/python" ] || refuse "python is not \$VIRTUAL_ENV/bin/python"

# 8. The configuration validates, with the rehearsed SHA-256.
CHK="$(env -u OFILT_RUN_SEALED "$PY" tools/p3_sealed_run.py --check-config)" || refuse "the configuration check failed: $CHK"
[ "$CHK" = "config docs/P3_RUN_CONFIG.json SHA-256 $CONFIG_SHA; valid: True" ] || refuse "the configuration check did not print valid: True with the rehearsed SHA-256 ($CHK)"

# 9. Without --dry-run: the data folder holds the dev panel's file (an existence check; the file is not opened).
if [ -z "$DRY" ]; then
  [ -f "$DATA_DIR/$DEV_FILE" ] || refuse "$DATA_DIR holds no $DEV_FILE"
fi

# The summary: one line per check, then the exact command (this script's own line, printed from the file).
CMD_LINE="$(awk '/^# >>> THE ONE COMMAND <<<$/ {getline; sub(/^[[:space:]]+/, ""); print; exit}' "${BASH_SOURCE[0]}")"
[ -n "$CMD_LINE" ] || refuse "the command line was not found in this script"
echo "check 1, the arguments (--commit $COMMIT; --expect-config-sha256 $EXPECT; --data-dir $DATA_DIR; --dry-run ${DRY:-0}): True"
echo "check 2, OFILT_RUN_SEALED absent from the environment: True"
echo "check 3, HEAD $HEAD_NOW equals --commit: True"
echo "check 4, git status --porcelain --untracked-files=all empty: True"
echo "check 5, --expect-config-sha256 $EXPECT equals the rehearsed configuration SHA-256: True"
echo "check 5, docs/P3_RUN_CONFIG.json $CFG_NOW: True"
echo "check 5, tools/p3_sealed_run.py $TOOL_NOW: True"
echo "check 5, ofilt/drift/calib.py $CALIB_NOW: True"
echo "check 5, spec/analysis_spec_dev_v1.yaml $SPEC_NOW: True"
echo "check 6, BLIND_FIT_LOG $LOG_NOW, $LOG_N lines, equals the P3-0 baseline: True"
echo "check 6, RUN_REGISTRY.jsonl 0 bytes; no ACCESS_LOG; neither output file exists: True"
echo "check 7, power ($POWER): True"
echo "the interpreter, $PY = \$VIRTUAL_ENV/bin/python: True"
echo "check 8, $CHK: True"
if [ -z "$DRY" ]; then echo "check 9, $DATA_DIR/$DEV_FILE exists: True"; else echo "check 9, the data folder: not checked (--dry-run)"; fi
echo "the command: $CMD_LINE"
echo "  run from $ROOT, with DATA_DIR=$DATA_DIR, PY=$PY, EXPECT=$EXPECT"

if [ -n "$DRY" ]; then echo "LAUNCH DRY RUN: all checks passed"; exit 0; fi

echo "LAUNCHING"
set +e
# >>> THE ONE COMMAND <<<
OFILT_RUN_SEALED=1 OFILT_DATA_DIR="$DATA_DIR" caffeinate -i "$PY" tools/p3_sealed_run.py --real --expect-config-sha256 "$EXPECT" 2>&1 | grep -E '^(COMPLETE|ABORTED|REFUSED)'
RCS=("${PIPESTATUS[@]}")
set -e
TOOL_RC="${RCS[0]}"

# After the run: the exit code, the blinding log, the outputs' existence and SHA-256, the tree.
OK=1
echo "the tool's exit code: $TOOL_RC"
N_AFTER="$(awk 'END {print NR}' BLIND_FIT_LOG)"
if [ "$N_AFTER" = 7 ]; then echo "BLIND_FIT_LOG has 7 lines: True"; else echo "BLIND_FIT_LOG has 7 lines: False ($N_AFTER)"; OK=0; fi
HEAD6="$(head -n 6 BLIND_FIT_LOG | shasum -a 256 | cut -d' ' -f1)"
if [ "$HEAD6" = "$BASELINE" ]; then echo "BLIND_FIT_LOG's first six lines equal the P3-0 baseline: True"; else echo "BLIND_FIT_LOG's first six lines equal the P3-0 baseline: False ($HEAD6)"; OK=0; fi
if [ -f reports/P3_4_sealed_run.json ]; then echo "reports/P3_4_sealed_run.json exists: True; sha256 $(shasum -a 256 reports/P3_4_sealed_run.json | cut -d' ' -f1)"; else echo "reports/P3_4_sealed_run.json exists: False"; OK=0; fi
if [ -f reports/P3_4_sealed_run.md ]; then echo "reports/P3_4_sealed_run.md exists: True; sha256 $(shasum -a 256 reports/P3_4_sealed_run.md | cut -d' ' -f1)"; else echo "reports/P3_4_sealed_run.md exists: False"; OK=0; fi
echo "git status --porcelain:"
git status --porcelain
echo "LAUNCH FINISHED"
if [ "$OK" != 1 ]; then echo "POST-RUN CHECK FAILED"; exit 4; fi
exit "$TOOL_RC"
