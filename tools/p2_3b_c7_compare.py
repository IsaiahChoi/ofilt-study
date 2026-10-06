"""P2-3b item 4c: compare the committed C7 reports (x86_64 run) with the Mac rerun (D16). SYNTHETIC only.

Acceptance criterion (fixed in the supervisor message of 2026-10-05, before the rerun was compared):
  (i)   the same JSON structure and keys (same dict keys, same list lengths, same leaf types);
  (ii)  every integer, boolean, string and null value identical, except key.spec_sha256, which must equal
        the SHA-256 of the edited spec/analysis_spec_dev_v1.yaml;
  (iii) every float equal, or with |a - b| <= 1e-9 * max(|a|, |b|); the fields named runtime_s (wall-clock
        seconds) are information only and excluded from (iii) (D16 amendment, Isaiah, 2026-10-05);
  (iv)  in particular, every per-replication rejection flag (booleans under reps named *reject*) and every
        summary count (every integer under cells in C7_mc.json; every integer outside key in
        C7_h1_same_dgp.json) identical.
The criterion is applied as written. Lines marked "information only" do not change any verdict.
usage: python tools/p2_3b_c7_compare.py OLD_MC NEW_MC OLD_H1 NEW_H1
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec" / "analysis_spec_dev_v1.yaml"
REL_TOL = 1e-9
SPEC_PATH = "key.spec_sha256"
INFO_ONLY = "runtime_s"   # D16 amendment: excluded from (iii), printed as information


def kind(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "str"
    if isinstance(v, list):
        return "list"
    if isinstance(v, dict):
        return "dict"
    raise TypeError(type(v).__name__)


def leaves(o, path=""):
    """Yield (path, value) for every leaf, in document order."""
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, o


def structure(o, path="", out=None):
    """Container shape: (path, kind, sorted keys or length) for every node, leaves included."""
    out = [] if out is None else out
    k = kind(o)
    if k == "dict":
        out.append((path, k, tuple(o.keys())))
        for key, v in o.items():
            structure(v, f"{path}.{key}" if path else key, out)
    elif k == "list":
        out.append((path, k, len(o)))
        for i, v in enumerate(o):
            structure(v, f"{path}[{i}]", out)
    else:
        out.append((path, k, None))
    return out


def rel(a: float, b: float) -> float:
    if a == b:
        return 0.0
    if not (math.isfinite(a) and math.isfinite(b)):
        return math.inf
    return abs(a - b) / max(abs(a), abs(b))


def is_iv(path: str, value, mc: bool) -> bool:
    last = path.rsplit(".", 1)[-1]
    if kind(value) == "bool" and path.startswith("reps.") and "reject" in last:
        return True
    if kind(value) == "int":
        return path.startswith("cells.") if mc else not path.startswith("key.")
    return False


def compare(old_path: Path, new_path: Path, mc: bool, spec_sha: str, say) -> bool:
    old = json.loads(old_path.read_text(encoding="utf-8"))
    new = json.loads(new_path.read_text(encoding="utf-8"))
    say(f"== {new_path.name}: old {old_path} ({old_path.stat().st_size} bytes) vs new {new_path} "
        f"({new_path.stat().st_size} bytes)")
    s_old, s_new = structure(old), structure(new)
    ok_i = s_old == s_new
    if not ok_i:
        diffs = [(a, b) for a, b in zip(s_old, s_new) if a != b][:20]
        say(f"   (i) structure differs; node counts {len(s_old)} vs {len(s_new)}; first differences: {diffs}")
    say(f"(i)   same JSON structure and keys ({len(s_old)} nodes): {'PASS' if ok_i else 'FAIL'}")
    if not ok_i:
        return False
    lo, ln = list(leaves(old)), list(leaves(new))
    assert [p for p, _ in lo] == [p for p, _ in ln]
    n_nonfloat, nonfloat_diffs, spec_ok = 0, [], None
    n_float, n_float_diff, max_rel, max_rel_path, over = 0, 0, 0.0, None, []
    n_iv, iv_diffs = 0, []
    info = []
    for (p, a), (_, b) in zip(lo, ln):
        k = kind(a)
        if k == "float" and p.rsplit(".", 1)[-1] == INFO_ONLY:
            info.append((p, a, b))
        elif k == "float":
            n_float += 1
            r = rel(a, b)
            if a != b:
                n_float_diff += 1
            if r > max_rel:
                max_rel, max_rel_path = r, p
            if r > REL_TOL:
                over.append((p, a, b, r))
        else:
            n_nonfloat += 1
            if p == SPEC_PATH:
                spec_ok = b == spec_sha
                nonfloat_diffs.append((p, a, b, f"must equal SHA-256 of {SPEC.relative_to(ROOT)}: {spec_ok}"))
            elif a != b:
                nonfloat_diffs.append((p, a, b, "DIFFERS"))
        if is_iv(p, a, mc):
            n_iv += 1
            if a != b:
                iv_diffs.append((p, a, b))
    ok_ii = spec_ok is True and all(d[3] != "DIFFERS" for d in nonfloat_diffs)
    say(f"   non-float leaves compared: {n_nonfloat}; differences (every one listed):")
    for p, a, b, note in nonfloat_diffs:
        say(f"     {p}: old {a!r} -> new {b!r}  [{note}]")
    if not nonfloat_diffs:
        say("     none")
    say(f"(ii)  integers, booleans, strings, nulls identical; {SPEC_PATH} equals the edited spec's SHA-256: "
        f"{'PASS' if ok_ii else 'FAIL'}")
    say(f"   float leaves compared: {n_float}; differing at all: {n_float_diff}; largest relative difference: "
        f"{max_rel!r} (at {max_rel_path})")
    say(f"   floats beyond {REL_TOL!r} relative (every one listed): {len(over)}")
    for p, a, b, r in over:
        say(f"     {p}: old {a!r} -> new {b!r}  (relative {r!r})")
    for p, a, b in info:
        say(f"   information only, excluded from (iii) (D16 amendment): {p}: old {a!r} -> new {b!r}")
    ok_iii = not over
    say(f"(iii) every float equal or within {REL_TOL!r} relative: {'PASS' if ok_iii else 'FAIL'}")
    rest = [o for o in over if o[0] != "runtime_s"]
    rest_max = max((rel(a, b) for (p, a), (_, b) in zip(lo, ln) if kind(a) == "float" and p != "runtime_s"),
                   default=0.0)
    say(f"   information only: floats other than runtime_s (wall-clock seconds) beyond tolerance: {len(rest)}; "
        f"largest relative difference among them: {rest_max!r}")
    ok_iv = not iv_diffs
    say(f"   rejection flags and summary counts compared: {n_iv}; differences: {len(iv_diffs)}")
    for p, a, b in iv_diffs:
        say(f"     {p}: old {a!r} -> new {b!r}")
    say(f"(iv)  every per-replication rejection flag and summary count identical: {'PASS' if ok_iv else 'FAIL'}")
    return ok_i and ok_ii and ok_iii and ok_iv


def main(argv) -> int:
    if len(argv) != 5:
        print(__doc__)
        return 2
    h = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    lines = []
    say = lines.append
    say(f"SHA-256 of {SPEC.relative_to(ROOT)}: {h}")
    ok_mc = compare(Path(argv[1]), Path(argv[2]), True, h, say)
    ok_h1 = compare(Path(argv[3]), Path(argv[4]), False, h, say)
    say(f"OVERALL (criterion as written): C7_mc.json {'PASS' if ok_mc else 'FAIL'}; "
        f"C7_h1_same_dgp.json {'PASS' if ok_h1 else 'FAIL'}")
    print("\n".join(lines))
    return 0 if ok_mc and ok_h1 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
