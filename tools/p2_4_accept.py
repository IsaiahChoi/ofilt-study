"""P2-4 acceptance of a Pass 2 build (builder prompt A′, as amended by Isaiah on 2026-10-05).

Reads a build folder (panel_dev.csv, panel_confirm_SEALED.csv, MANIFEST.json) and prints each
acceptance item as True/False, with hashes for dev and counts only for the sealed side. Never prints
a panel value. Prints to stdout only; writes reports/P2_4_acceptance.md only with --write-report
(P2-4b, Isaiah 2026-10-05: the committed report is the run-time record and is not regenerated).

(a) dev 41-column projection hashes to 736636031ca1...   (b) sealed projection to 138e5e2104d5...
(c) sealed dates = calendar.confirmation_calendar() (1,019); dev dates unchanged (1,708)
(d) rows 5,124 / 3,057; 60 columns            (f) the frozen build's own assertions passed
(e) 1306 columns finite; the amended usdjpy_us_ret rule; gotobi 529 / 319 per ticker; Japan 225
    dates with n225_stale_end_min <= 5 per half-year = reports/P2_1_inputs.md on the same dates
    (the panel has no row for 2015-01-05, accounted for explicitly); dates with an empty xau_ret
(g) every new build-time assertion passed

usage: python tools/p2_4_accept.py <build folder> <raw dir> <original dev panel> <build exit code> [--write-report]
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build" / "pass2"))
import build_panel_p2 as B  # noqa: E402
import columns as C  # noqa: E402
from ofilt.drift.calendar import confirmation_calendar  # noqa: E402

DEV_OLD = "736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42"
SEALED_OLD = "138e5e2104d5ebf6e9616edc55ca00f548e38be604365bd47932e1716f4d9d19"     # hybrid (Isaiah, 2026-10-05)
FIRST_CAL_DAY = pd.Timestamp("2015-01-05")
out: list[str] = []


def say(s: str = "") -> None:
    out.append(s)


def item(name: str, ok) -> bool:
    say(f"- {name}: {bool(ok)}")
    return bool(ok)


def half(d: str) -> str:
    return f"{d[:4]}-H{1 if int(d[5:7]) <= 6 else 2}"


def main(folder: Path, raw: Path, orig_dev: Path, build_rc: int, write_report: bool = False) -> int:
    m = json.loads((folder / "MANIFEST.json").read_text(encoding="utf-8"))
    say(f"# P2-4 acceptance: `{folder.name}`")
    say()
    say("## Files and MANIFEST")
    ok = []
    for f in (B.DEV_FILE, B.SEALED_FILE):
        ok.append(item(f"{f} hashes to its MANIFEST entry", B.sha256(folder / f) == m["outputs"][f]["sha256"]))
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    mh = m["git"]["head"]
    say(f"- MANIFEST git head: {mh}; this checkout's HEAD: {head}")
    anc = subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", mh, "HEAD"]).returncode == 0
    ok.append(item("MANIFEST git head is an ancestor of HEAD", anc))
    same = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", mh, "HEAD", "--", "build/",
                           "docs/PASS2_INPUTS.json"]).returncode == 0
    ok.append(item("build/ and docs/PASS2_INPUTS.json unchanged from the MANIFEST head to HEAD", same))
    ok.append(item("MANIFEST records build/ and docs/PASS2_INPUTS.json clean", m["git"]["build_and_inputs_registry_clean"]))
    ok.append(item("the original dev panel hashes to 736636031ca1...", B.sha256(orig_dev) == DEV_OLD))

    dev = B.read_old_panel(folder / B.DEV_FILE)
    sea = B.read_old_panel(folder / B.SEALED_FILE)
    old_dev = B.read_old_panel(orig_dev)
    say()
    say("## (a), (b) old-column projections (in memory)")
    pa = B.projection_sha256(dev.iloc[:, :B.N_OLD])
    a = item(f"(a) dev 41-column projection hashes to 736636031ca1... (computed {pa})", pa == DEV_OLD)
    b = item("(b) sealed 41-column projection hashes to 138e5e2104d5...",
             B.projection_sha256(sea.iloc[:, :B.N_OLD]) == SEALED_OLD)

    say()
    say("## (c) calendars")
    conf = [C.day_key(d) for d in confirmation_calendar()]
    s_dates = sorted(set(sea["date"]))
    c1 = item(f"(c) sealed dates equal calendar.confirmation_calendar() ({len(s_dates)} vs {len(conf)})", s_dates == conf)
    d_dates = sorted(set(dev["date"]))
    c2 = item(f"(c) dev dates unchanged ({len(d_dates)} dates; 1,708)", d_dates == sorted(set(old_dev["date"]))
              and len(d_dates) == 1708)

    say()
    say("## (d) shape")
    d1 = item(f"(d) dev rows 5,124 and 60 columns ({dev.shape[0]}, {dev.shape[1]})", dev.shape == (5124, 60))
    d2 = item(f"(d) sealed rows 3,057 and 60 columns ({sea.shape[0]}, {sea.shape[1]})", sea.shape == (3057, 60))

    say()
    say("## (e) new columns (sealed side: counts and booleans only)")
    e = []
    for name, p in (("dev", dev), ("sealed", sea)):
        f = {c: B.to_float(p[c]).to_numpy() for c in ("y_1306_oc", "ao_1306_gap_raw", "ao_1306_gap_adj",
                                                       "usdjpy_us_ret", "us_n_sessions", "gotobi_day")}
        e.append(item(f"(e) {name}: y_1306_oc, ao_1306_gap_raw, ao_1306_gap_adj finite on every row",
                      all(np.isfinite(f[c]).all() for c in ("y_1306_oc", "ao_1306_gap_raw", "ao_1306_gap_adj"))))
        none = f["us_n_sessions"] == 0
        e.append(item(f"(e) {name}: usdjpy_us_ret == 0.0 wherever us_n_sessions == 0", (f["usdjpy_us_ret"][none] == 0.0).all()))
        e.append(item(f"(e) {name}: usdjpy_us_ret finite wherever us_n_sessions > 0", np.isfinite(f["usdjpy_us_ret"][~none]).all()))
        say(f"  - {name}: nights with sessions summing to exactly 0.0 (MANIFEST): "
            f"{m['outputs'][B.DEV_FILE if name == 'dev' else B.SEALED_FILE]['usdjpy_us_ret_zero_sum_session_nights']}")
        want = 529 if name == "dev" else 319
        g = pd.Series(f["gotobi_day"]).groupby(p["ticker"].to_numpy()).sum()
        e.append(item(f"(e) {name}: gotobi_day sums to {want} per ticker ({', '.join(f'{k} {int(v)}' for k, v in g.items())})",
                      (g == want).all()))
        n_empty = p.loc[p["xau_ret"] == "", "date"].nunique()
        say(f"  - {name}: dates with an empty xau_ret: {n_empty} of {p['date'].nunique()}")

    # Japan 225: fresh 08:59 price (n225_stale_end_min <= 5), one row per date, against reports/P2_1_inputs.md
    p21 = {}
    for line in (ROOT / "reports" / "P2_1_inputs.md").read_text(encoding="utf-8").splitlines():
        r = re.match(r"^\| (\d{4}-H[12]) \| (\d+) \| (\d+) \|", line)
        if r:
            p21[r.group(1)] = (int(r.group(2)), int(r.group(3)))
    reg = json.loads((ROOT / "docs" / "PASS2_INPUTS.json").read_text(encoding="utf-8"))["inputs"]
    n_hash = B.sha256(raw / B.N225) == reg[B.N225]["sha256"]
    say(f"  - the raw Japan 225 file hashes to the registry (read only for 2015-01-05): {n_hash}")
    ts, px = C.pass1.load_fx(raw / B.N225)
    _, stale0, _ = C.pass1.price_at(ts, px, C.pass1.jst_to_utc(FIRST_CAL_DAY, 8, 59))
    fresh0 = int(stale0 <= 5)
    say(f"  - 2015-01-05 (first calendar day; no panel row): 08:59 JST price at most 5 minutes stale: {bool(fresh0)}")
    say()
    say("  | Half-year | Panel dates | Panel fresh | P2-1 dates | P2-1 fresh | Expected (P2-1 minus 2015-01-05) | Equal |")
    say("  |---|---|---|---|---|---|---|")
    n_ok = []
    for name, p in (("dev", dev), ("sealed", sea)):
        one = p.drop_duplicates("date")
        st = B.to_float(one["n225_stale_end_min"]).to_numpy()
        fresh = pd.Series((st <= 5).astype(int), index=one["date"].map(half).to_numpy())
        for hy, grp in fresh.groupby(level=0, sort=True):
            pd_n, pd_f = len(grp), int(grp.sum())
            exp_n, exp_f = p21[hy]
            if hy == "2015-H1":
                exp_n, exp_f = exp_n - 1, exp_f - fresh0
            eq = (pd_n, pd_f) == (exp_n, exp_f)
            n_ok.append(eq)
            say(f"  | {hy} | {pd_n} | {pd_f} | {p21[hy][0]} | {p21[hy][1]} | {exp_n} / {exp_f} | {eq} |")
    say()
    e.append(item("(e) Japan 225 fresh-date counts equal P2-1's on the same dates, every half-year (dev and 2022+)", all(n_ok)))
    e.append(item("(e) every half-year of P2-1 appears in the panels", len(n_ok) == len(p21)))

    say()
    say("## (f), (g) build assertions")
    names = m["build_assertions"]["names"]
    f_ok = item("(f) the frozen build's own assertions passed (it ran inside the build and exited 0)",
                "the frozen build exits 0" in names)
    g_ok = item(f"(g) every new build-time assertion passed (build exit code {build_rc}; "
                f"{m['build_assertions']['passed']} assertions recorded)",
                build_rc == 0 and m["build_assertions"]["passed"] == len(names))
    say()
    allok = all(ok) and a and b and c1 and c2 and d1 and d2 and all(e) and f_ok and g_ok
    say(f"**P2-4 ACCEPTED: {allok}**")
    text = "\n".join(out) + "\n"
    if write_report:
        (ROOT / "reports" / "P2_4_acceptance.md").write_text(text, encoding="utf-8")
    print(text)
    return 0 if allok else 1


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--write-report"]
    if len(args) != 4:
        sys.exit("usage: python tools/p2_4_accept.py <build folder> <raw dir> <original dev panel> <build exit code> "
                 "[--write-report]")
    sys.exit(main(Path(args[0]), Path(args[1]), Path(args[2]), int(args[3]), "--write-report" in sys.argv[1:]))
