set -euo pipefail
# tools/p3_3_rehearse.sh: the P3-3 rehearsal (DQ1.5; PASS3_STATUS Decision log, "The rehearsal procedure").
# usage:  bash tools/p3_3_rehearse.sh --expect-config-sha256 <hash>             the full rehearsal: two runs
#         bash tools/p3_3_rehearse.sh --smoke N --expect-config-sha256 <hash>   the short one (cells capped at N)
# <hash> is docs/P3_RUN_CONFIG.json's SHA-256 (64 lowercase hex); the script refuses unless the file matches it.
# Capture the output with:  bash tools/p3_3_rehearse.sh --expect-config-sha256 <hash> 2>&1 | tee <log file>
# The script never passes the tool's real-mode flag, never sets the sealed-run environment variable, and writes nothing
# inside the repository. Any refusal prints "REHEARSAL REFUSED: <reason>" and exits 2; the end prints "REHEARSAL PASSED"
# (exit 0) or "REHEARSAL FAILED: <reason>" (exit 1).

refuse() { echo "REHEARSAL REFUSED: $1"; exit 2; }
fail() { echo "REHEARSAL FAILED: $1"; exit 1; }

# 1. The sealed-run environment variable must not be set at all (checked before any Python command).
if [ -n "${OFILT_RUN_SEALED+x}" ]; then refuse "OFILT_RUN_SEALED is set"; fi

MODE=full
SMOKE=""
EXPECT=""
USAGE="usage: bash tools/p3_3_rehearse.sh [--smoke N] --expect-config-sha256 <64 lowercase hex>"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --smoke) { [ "$#" -ge 2 ] && [[ "$2" =~ ^[0-9]+$ ]]; } || refuse "$USAGE"; MODE=smoke; SMOKE="$2"; shift 2 ;;
    --expect-config-sha256) [ "$#" -ge 2 ] || refuse "$USAGE"; EXPECT="$2"; shift 2 ;;
    *) refuse "$USAGE" ;;
  esac
done
[[ "$EXPECT" =~ ^[0-9a-f]{64}$ ]] || refuse "--expect-config-sha256 <64 lowercase hex> is required (missing or malformed)"

# 2. The repository root; the tree must be clean, untracked files included.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
[ -z "$(git status --porcelain)" ] || refuse "git status --porcelain is not empty"
CFG_SHA="$(shasum -a 256 docs/P3_RUN_CONFIG.json | cut -d' ' -f1)"
[ "$CFG_SHA" = "$EXPECT" ] || refuse "docs/P3_RUN_CONFIG.json's SHA-256 differs from --expect-config-sha256"
echo "configuration sha256: $CFG_SHA (equals --expect-config-sha256)"

# 3. Header.
echo "rehearsal mode: $MODE${SMOKE:+ (smoke $SMOKE)}"
echo "utc: $(date -u +%FT%TZ)"
HEAD0="$(git rev-parse HEAD)"
echo "HEAD: $HEAD0"
echo "macOS: $(sw_vers -productVersion)"
echo "machine: $(uname -m)"

# 4. The venv.
set +u
source "$HOME/venvs/ofilt_p2/bin/activate"
set -u
[ "$(command -v python)" = "$VIRTUAL_ENV/bin/python" ] || refuse "python is not \$VIRTUAL_ENV/bin/python"
echo "python: $(command -v python)"

# 5. Power.
PS_OUT="$(pmset -g ps)"
echo "power: $(printf '%s\n' "$PS_OUT" | head -1)"
if [ "$MODE" = full ]; then printf '%s\n' "$PS_OUT" | grep -q "AC Power" || refuse "not on AC Power"; fi

# 6. Baselines, read by script (the same script runs again after the runs).
baseline() {
  env -u OFILT_RUN_SEALED python - "$EXPECT" <<'PYEOF'
import hashlib, os, re, sys, tempfile
from pathlib import Path
R = Path.cwd()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
p30 = re.search(r"^BLIND_FIT_LOG sha256 \(baseline[^\n]*?([0-9a-f]{64})$", (R / "reports/P3_0_report.txt").read_text(), re.M).group(1)
exp = sys.argv[1]
log, cfg = sha(R / "BLIND_FIT_LOG"), sha(R / "docs/P3_RUN_CONFIG.json")
reg = (R / "RUN_REGISTRY.jsonl").stat().st_size
syn = Path(tempfile.gettempdir()) / "ofilt_RUN_REGISTRY_synthetic.jsonl"
print(f"BLIND_FIT_LOG sha256 {log}; equals the P3-0 baseline: {log == p30}")
print(f"docs/P3_RUN_CONFIG.json sha256 {cfg}; equals --expect-config-sha256: {cfg == exp}")
print(f"RUN_REGISTRY.jsonl bytes {reg}; is 0: {reg == 0}")
print(f"tools/p3_sealed_run.py sha256 {sha(R / 'tools/p3_sealed_run.py')}")
print(f"ofilt/drift/calib.py sha256 {sha(R / 'ofilt/drift/calib.py')}")
print(f"usual TMPDIR ofilt_RUN_REGISTRY_synthetic.jsonl bytes {syn.stat().st_size if syn.exists() else 'absent'}")
raise SystemExit(0 if (log == p30 and cfg == exp and reg == 0) else 1)
PYEOF
}
BASE0="$(baseline)" || { printf '%s\n' "$BASE0"; refuse "a baseline check failed"; }
printf '%s\n' "$BASE0"

# 7. The configuration validates.
CHK="$(env -u OFILT_RUN_SEALED python tools/p3_sealed_run.py --check-config)" || { printf '%s\n' "$CHK"; refuse "--check-config failed"; }
printf '%s\n' "$CHK"
printf '%s\n' "$CHK" | grep -q "valid: True" || refuse "the configuration is not valid"

# 8. The output folders must not exist yet.
if [ "$MODE" = full ]; then OUT1=/tmp/p3_3_rehearsal_1; OUT2=/tmp/p3_3_rehearsal_2; else OUT1=/tmp/p3_3_smoke_1; OUT2=/tmp/p3_3_smoke_2; fi
for d in "$OUT1" "$OUT2"; do [ ! -e "$d" ] || refuse "$d exists"; done

# The two runs, in sequence.
run_one() {
  local out="$1" rc
  echo "run start ($out): $(date -u +%FT%TZ)"
  set +e
  if [ -n "$SMOKE" ]; then
    RUN_OUT="$(env -u OFILT_RUN_SEALED OFILT_DATA_DIR="$HOME/Desktop/FX_Project/data" python tools/p3_sealed_run.py --rehearsal --smoke "$SMOKE" --out-dir "$out" 2>&1)"
  else
    RUN_OUT="$(env -u OFILT_RUN_SEALED OFILT_DATA_DIR="$HOME/Desktop/FX_Project/data" python tools/p3_sealed_run.py --rehearsal --out-dir "$out" 2>&1)"
  fi
  rc=$?
  set -e
  printf '%s\n' "$RUN_OUT"
  echo "run end ($out): $(date -u +%FT%TZ); exit $rc"
  [ "$rc" -eq 0 ] || fail "the run into $out exited $rc"
  printf '%s\n' "$RUN_OUT" | grep -q -E "^COMPLETE: .*errors: 0$" || fail "the run into $out did not print COMPLETE ... errors: 0"
}
run_one "$OUT1"
run_one "$OUT2"

# After the runs: the outputs, the baselines, the tree, the timings.
CMP="$(env -u OFILT_RUN_SEALED python - "$OUT1" "$OUT2" <<'PYEOF'
import json, sys
from pathlib import Path
a, b = (json.loads((Path(d) / "P3_4_sealed_run.json").read_text()) for d in sys.argv[1:3])
ra, rb = a.pop("runtime"), b.pop("runtime")
same = json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
print(f"the two JSON outputs are identical apart from runtime: {same}")
for name in [t["task"] for t in ra["tasks"]]:
    s = [next(t for t in r["tasks"] if t["task"] == name) for r in (ra, rb)]
    print(f"task {name}: run 1 {s[0]['seconds']:.1f} s, run 2 {s[1]['seconds']:.1f} s ({s[0]['replications']} replications each)")
print(f"calibrator: run 1 {ra['calibrator_seconds']:.2f} s, run 2 {rb['calibrator_seconds']:.2f} s")
print(f"totals: run 1 {ra['total_seconds']:.1f} s, run 2 {rb['total_seconds']:.1f} s")
m = max(ra["total_seconds"], rb["total_seconds"])
print(f"projected duration of the real run (the larger total): {m:.0f} s ({m / 3600:.2f} h)")
raise SystemExit(0 if same else 1)
PYEOF
)" || { printf '%s\n' "$CMP"; fail "the two outputs differ apart from runtime"; }
printf '%s\n' "$CMP"
BASE1="$(baseline)" || { printf '%s\n' "$BASE1"; fail "a baseline check failed after the runs"; }
printf '%s\n' "$BASE1"
[ "$BASE0" = "$BASE1" ] || fail "a hash or size changed during the rehearsal"
echo "hashes and sizes unchanged: True"
[ -z "$(git status --porcelain)" ] || fail "git status --porcelain is not empty after the runs"
[ "$(git rev-parse HEAD)" = "$HEAD0" ] || fail "HEAD changed"
echo "tree clean and HEAD unchanged: True"
echo "utc: $(date -u +%FT%TZ)"
echo "REHEARSAL PASSED"
