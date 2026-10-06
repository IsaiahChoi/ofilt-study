"""Pass 2 build: the 60-column panels, append-only (P51; builder prompt A′, item P2-2).

1. Verify every input before reading it: the raw files, the event files and the frozen build code
   against docs/PASS2_INPUTS.json, and the original dev panel against its hash (736636...).
2. Run the frozen build/pass1/build_panel.py exactly as in P2-0b (a working folder holding the
   hash-verified event files; raw = <raw>) into a temporary folder. Its dev and sealed outputs
   must hash to the Mac baseline (656d5117... / 138e5e21...; Isaiah, 2026-10-05).
3. Compute the 19 new columns from the raw inputs with build/pass2/columns.py.
4. For each panel, read the old panel back as strings (dtype=str, keep_default_na=False), append
   the new columns by date, assert that row count and order are unchanged, and write the
   60-column panel. Old-column source (Isaiah, 2026-10-05): dev = the original panel_dev.csv;
   sealed = the frozen build's output on this machine.
5. Write MANIFEST.json. It records `git rev-parse HEAD` and whether
   `git status --porcelain -- build/ docs/PASS2_INPUTS.json` is empty; the command line refuses to
   run when it is not (P2-2b, Isaiah 2026-10-05).

The usdjpy_us_ret assertion is the amended one (Isaiah, 2026-10-05): 0.0 wherever us_n_sessions == 0,
finite wherever us_n_sessions > 0; MANIFEST counts the nights with sessions that sum to exactly 0.0.

Prints only hashes, row counts, spans and booleans; never a panel value. Every assertion message
is a fixed text. The expectations (hashes, counts) default to the real study's; tests pass
synthetic ones through `build(..., expect=...)`.

usage: python build/pass2/build_panel_p2.py --raw <RAW> --events <folder with events_*.csv>
           --orig-dev <original panel_dev.csv> --out <new output folder>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import columns as C  # noqa: E402

REPO = C.REPO
FROZEN_BUILD = C.FROZEN_PATH
FROZEN_FILES = ("build_panel.py", "make_events.py", "events.py")
BOOK2 = "Book2.xlsx"
USDJPY = "usdjpy_dukascopy_2015-01-01_2026-03-05.csv"
EURUSD = "eurusd_dukascopy_2015-01-01_2026-03-05.csv"
FIXED = "newbloombergdata_fixed.xlsx"
XAU = "xauusd_dukascopy_2015-01-01_2026-03-05.csv.gz"
N225 = "jpn225_dukascopy_2015-01-01_2026-03-05.csv.gz"
RAW_INPUTS = (BOOK2, USDJPY, EURUSD, FIXED, XAU, N225)
DEV_FILE, SEALED_FILE = "panel_dev.csv", "panel_confirm_SEALED.csv"
N_OLD = 41
MAC_DEV = "656d5117a7d0027f7ba7d2cc8d16236fcc9258af384363c8be4577ce15933bd4"      # Isaiah, 2026-10-05
MAC_SEALED = "138e5e2104d5ebf6e9616edc55ca00f548e38be604365bd47932e1716f4d9d19"   # Isaiah, 2026-10-05
LIBRARIES = ("pandas", "numpy", "scipy", "scikit-learn", "openpyxl", "PyYAML")


class BuildAssertion(AssertionError):
    """A build-time assertion failed; the message is a fixed text."""


@dataclass(frozen=True)
class Expect:
    inputs: dict                    # raw file name -> sha256
    events: dict                    # event file name -> sha256
    code: dict                      # build/pass1 file name -> sha256
    orig_dev: str                   # original dev panel (dev's old-column source)
    frozen_dev: str                 # frozen build's dev output on this platform
    frozen_sealed: str              # frozen build's sealed output on this platform (sealed's old-column source)
    div_rows: int                   # 1306 distribution rows used
    gotobi_dev_per_ticker: int
    gotobi_sealed_per_ticker: int
    early_closes: tuple = C.NYSE_EARLY_CLOSES
    reference_pairs: dict = field(default_factory=dict)


def real_expect() -> Expect:
    reg = json.loads((REPO / "docs" / "PASS2_INPUTS.json").read_text(encoding="utf-8"))
    base = reg["baseline_outputs"]
    return Expect(
        inputs={n: reg["inputs"][n]["sha256"] for n in RAW_INPUTS},
        events={n: e["sha256"] for n, e in reg["event_files"].items()},
        code={n: reg["code"][n]["sha256"] for n in FROZEN_FILES},
        orig_dev=base[DEV_FILE]["sha256"], frozen_dev=MAC_DEV, frozen_sealed=MAC_SEALED,
        div_rows=11, gotobi_dev_per_ticker=529, gotobi_sealed_per_ticker=319,
        reference_pairs={"dev": {"original": base[DEV_FILE]["sha256"], "mac_frozen_build": MAC_DEV},
                         "sealed": {"original": base[SEALED_FILE]["sha256"], "mac_frozen_build": MAC_SEALED}})


class Checks:
    def __init__(self):
        self.passed: list[str] = []

    def __call__(self, name: str, ok) -> None:
        if not bool(ok):
            raise BuildAssertion(f"build assertion failed: {name}")
        self.passed.append(name)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_old_panel(path: Path) -> pd.DataFrame:
    """An old panel as the original strings (A′ P2-2 step 3)."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def projection_sha256(old: pd.DataFrame) -> str:
    """SHA-256 of the 41-column projection written with to_csv(index=False) from the string frame."""
    return hashlib.sha256(old.to_csv(index=False).encode("utf-8")).hexdigest()


def to_float(s: pd.Series) -> pd.Series:
    """String column -> float; the empty string (a NaN written by to_csv) -> NaN."""
    return pd.to_numeric(s.where(s != "", np.nan)).astype(float)


def same_dates(a, b) -> bool:
    a, b = pd.DatetimeIndex(a), pd.DatetimeIndex(b)
    return len(a) == len(b) and bool((a.as_unit("ns") == b.as_unit("ns")).all())


def append_new_columns(old: pd.DataFrame, per_date: pd.DataFrame) -> pd.DataFrame:
    """Append the 19 new columns to the string frame `old` by date, in NEW_COLUMNS order.
    `per_date` is indexed by 'YYYY-MM-DD' and holds the per-date columns plus
    `topix_tr_component`. The two per-row columns use the old panel's own values:
    ewj_oc_jpy = ewj_oc + usdjpy_us_ret; ao_topix_gap_tradj = ao_topix_gap + the TOPIX dividend
    component. The old columns stay the original strings; row count and order are unchanged."""
    keys = old["date"].to_numpy()
    if not pd.Index(keys).isin(per_date.index).all():
        raise BuildAssertion("build assertion failed: every panel date has new-column values")
    new = per_date.loc[keys].reset_index(drop=True)
    new["ewj_oc_jpy"] = to_float(old["ewj_oc"]).to_numpy() + new["usdjpy_us_ret"].to_numpy()
    new["ao_topix_gap_tradj"] = to_float(old["ao_topix_gap"]).to_numpy() + new["topix_tr_component"].to_numpy()
    for c in ("xau_bars", "n225_bars"):
        new[c] = new[c].astype("Int64")
    new["gotobi_day"] = new["gotobi_day"].astype("int64")
    return pd.concat([old.reset_index(drop=True), new[[c for c, _ in C.NEW_COLUMNS]]], axis=1)


def check_us_ret(label: str, dates, ur: np.ndarray, n_sess: np.ndarray, check: Checks) -> int:
    """The amended usdjpy_us_ret rule (Isaiah, 2026-10-05; replaces A′'s 'if and only if'):
    usdjpy_us_ret == 0.0 wherever us_n_sessions == 0, and finite wherever us_n_sessions > 0. A night
    with sessions may sum to exactly 0.0 (equal bids at the NY open and close). Returns the number of
    such nights (distinct dates), which MANIFEST reports."""
    none = n_sess == 0
    check(f"{label}: usdjpy_us_ret == 0.0 wherever us_n_sessions == 0", (ur[none] == 0.0).all())
    check(f"{label}: usdjpy_us_ret finite wherever us_n_sessions > 0", np.isfinite(ur[~none]).all())
    return len(set(np.asarray(dates)[(~none) & (ur == 0.0)]))


def git_state() -> dict:
    """HEAD and whether `git status --porcelain -- build/ docs/PASS2_INPUTS.json` is empty."""
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True)
    st = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--", "build/", "docs/PASS2_INPUTS.json"],
                        capture_output=True, text=True)
    return {"head": head.stdout.strip() if head.returncode == 0 else None,
            "build_and_inputs_registry_clean": st.returncode == 0 and st.stdout.strip() == ""}


def library_versions() -> dict:
    out = {"python": platform.python_version()}
    for name in LIBRARIES:
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            out[name] = "not installed"
    return out


def run_frozen(raw: Path, events_dir: Path, tmp: Path, expect: Expect, check: Checks) -> Path:
    """The frozen build exactly as in P2-0b: cwd = a working folder with hash-verified event files."""
    work, fout = tmp / "work", tmp / "out"
    work.mkdir()
    for n in expect.events:
        shutil.copyfile(events_dir / n, work / n)
        check(f"working copy of {n} hashes to the registry", sha256(work / n) == expect.events[n])
    r = subprocess.run([sys.executable, str(FROZEN_BUILD), str(raw), str(fout)], cwd=work,
                       capture_output=True, text=True)
    check("the frozen build exits 0", r.returncode == 0)
    return fout


def build(raw: Path, events_dir: Path, orig_dev: Path, out: Path, expect: Expect | None = None) -> dict:
    expect = expect or real_expect()
    raw, events_dir, orig_dev, out = Path(raw), Path(events_dir), Path(orig_dev), Path(out)
    if out.exists() and any(out.iterdir()):
        raise BuildAssertion("build assertion failed: the output folder is new or empty")
    check = Checks()
    git = git_state()

    # 1. inputs, verified before any read (A′ hard rule 1)
    in_sha = {n: sha256(raw / n) for n in expect.inputs}
    for n in expect.inputs:
        check(f"input {n} hashes to the registry", in_sha[n] == expect.inputs[n])
    ev_sha = {n: sha256(events_dir / n) for n in expect.events}
    for n in expect.events:
        check(f"event file {n} hashes to the registry", ev_sha[n] == expect.events[n])
    code_sha = {f"build/pass1/{n}": sha256(REPO / "build" / "pass1" / n) for n in FROZEN_FILES}
    for n in FROZEN_FILES:
        check(f"build/pass1/{n} hashes to the registry", code_sha[f"build/pass1/{n}"] == expect.code[n])
    code_sha.update({f"build/pass2/{p.name}": sha256(p) for p in sorted((REPO / "build" / "pass2").glob("*.py"))})
    orig_sha = sha256(orig_dev)
    check("the original dev panel hashes to its reference", orig_sha == expect.orig_dev)

    out.mkdir(parents=True, exist_ok=True)
    # 2. the frozen build, into a temporary folder
    with tempfile.TemporaryDirectory(dir=out, prefix="_frozen_") as tmp:
        fout = run_frozen(raw, events_dir, Path(tmp), expect, check)
        f_dev, f_sealed = sha256(fout / DEV_FILE), sha256(fout / SEALED_FILE)
        check("the frozen build's dev output hashes to the platform baseline", f_dev == expect.frozen_dev)
        check("the frozen build's sealed output hashes to the platform baseline", f_sealed == expect.frozen_sealed)
        frozen_dev_old = read_old_panel(fout / DEV_FILE)
        sealed_old = read_old_panel(fout / SEALED_FILE)
    dev_old = read_old_panel(orig_dev)
    old_cols = list(sealed_old.columns)
    check("the old panels have 41 columns", len(old_cols) == N_OLD)
    check("the original dev panel's columns equal the frozen build's", list(dev_old.columns) == old_cols
          and list(frozen_dev_old.columns) == old_cols)
    check("the original dev panel's dates and tickers equal the frozen build's, row for row",
          dev_old[["date", "ticker"]].equals(frozen_dev_old[["date", "ticker"]]))
    del frozen_dev_old

    # 3. inputs for the new columns
    px, top, us, div, cal, uscal = C.pass1.load_workbook(raw / BOOK2)
    wb = pd.read_excel(raw / FIXED, sheet_name=["1306", "1306 dividends", "TOPIX optional"], header=None)
    p1306 = C.parse_price_sheet(wb["1306"])
    dist, used = C.parse_dividends(wb["1306 dividends"])
    tr = C.parse_topix_tr(wb["TOPIX optional"])
    check("1306 dates equal the miners' calendar", same_dates(p1306.index, cal))
    check("1306 OHLC has no NaN", not p1306[["open", "close", "high", "low"]].isna().any().any())
    check(f"exactly {expect.div_rows} 1306 distribution rows are used", len(used) == expect.div_rows)
    check("every 1306 distribution row used is Regular Cash", (used["type"] == "Regular Cash").all())
    check("every 1306 ex-date is in the calendar", pd.DatetimeIndex(dist.index).isin(cal).all())
    check("TOPIX TR holds the 2020-10-01 row", C.OUTAGE in tr.index)
    tr = tr.drop(C.OUTAGE)
    check("TOPIX TR dates equal the miners' calendar after dropping 2020-10-01", same_dates(tr.index, cal))
    us_days = {C.day_key(d) for d in uscal}
    check("every NYSE early-close date is a date in Book2's US calendar",
          all(C.day_key(d) in us_days for d in expect.early_closes))
    jpy, eur = C.pass1.load_fx(raw / USDJPY), C.pass1.load_fx(raw / EURUSD)
    xau, n225 = C.pass1.load_fx(raw / XAU), C.pass1.load_fx(raw / N225)

    # new columns, per Tokyo date
    days = cal[1:]
    hedge = C.hedge_1306(p1306, dist, cal)
    comp = C.topix_tr_component(tr, top.close)
    xw = C.dark_window(*xau, cal, "xau")
    nw = C.dark_window(*n225, cal, "n225")
    inst = C.dark_window_instants(cal)
    usr = C.usdjpy_us_ret(*jpy, uscal, cal, expect.early_closes)
    sj, se = C.session_fx(*jpy, cal, "usdjpy"), C.session_fx(*eur, cal, "eurusd")
    gb = C.gotobi_flags(cal)
    xcols = ["xau_ret", "xau_rv", "xau_bv", "xau_bars", "xau_stale_start_min", "xau_stale_end_min",
             "window_start_utc", "window_end_utc"]
    ncols = ["n225_ret", "n225_bars", "n225_stale_start_min", "n225_stale_end_min", "window_start_utc", "window_end_utc"]
    xw, nw = xw.reindex(index=days, columns=xcols), nw.reindex(index=days, columns=ncols)
    per = pd.DataFrame(index=days)
    for c in ("y_1306_oc", "ao_1306_gap_raw", "ao_1306_gap_adj"):
        per[c] = hedge[c].reindex(days)
    per["topix_tr_component"] = comp.reindex(days)
    for c in xcols[:6]:
        per[c] = xw[c]
    for c in ncols[:4]:
        per[c] = nw[c]
    per["usdjpy_us_ret"] = usr["usdjpy_us_ret"].reindex(days)
    per["us_sessions_summed"] = usr["us_sessions_summed"].reindex(days)
    per["gotobi_day"] = gb.reindex(days)
    per["c_usdjpy_sess_ret"] = sj["c_usdjpy_sess_ret"].reindex(days)
    per["c_eurusd_sess_ret"] = se["c_eurusd_sess_ret"].reindex(days)
    inst = inst.reindex(days)

    # assertions on the per-date columns
    for w, name in ((xw, "XAU"), (nw, "Japan 225")):
        has = w["window_start_utc"].notna()
        check(f"{name} windows, where recorded, use the usdjpy window instants",
              (w.loc[has, "window_start_utc"] == inst.loc[has, "window_start_utc"]).all()
              and (w.loc[has, "window_end_utc"] == inst.loc[has, "window_end_utc"]).all())
    for c in ("xau_bars", "xau_stale_start_min", "xau_stale_end_min", "n225_bars", "n225_stale_start_min",
              "n225_stale_end_min"):
        check(f"{c} >= 0 wherever present", (per[c].dropna() >= 0).all())
    for s, name in ((sj, "usdjpy"), (se, "eurusd")):
        late = s.index >= C.pass1.TSE_CLOSE_CHANGE
        span = (s["session_close_utc"] - s.index.to_series()).to_numpy()
        want = np.where(late, np.timedelta64(390, "m"), np.timedelta64(360, "m"))   # 15:30 / 15:00 JST in UTC
        check(f"{name} session close is 15:30 JST exactly when t >= 2024-11-05", (span == want).all())
    per.index = [C.day_key(d) for d in days]
    inst.index = per.index

    # 4. panels
    results = {}
    for fname, old, source, src_sha in ((DEV_FILE, dev_old, "original panel_dev.csv", orig_sha),
                                        (SEALED_FILE, sealed_old, "frozen build/pass1 output on this machine", f_sealed)):
        label = "dev" if fname == DEV_FILE else "sealed"
        proj = projection_sha256(old)
        check(f"{label}: the old-column projection hashes to its source file", proj == src_sha)
        final = append_new_columns(old, per)
        check(f"{label}: row count unchanged", len(final) == len(old))
        check(f"{label}: row order unchanged", final[["date", "ticker"]].equals(old[["date", "ticker"]]))
        check(f"{label}: 60 columns, the 19 new ones appended in order",
              list(final.columns) == old_cols + [c for c, _ in C.NEW_COLUMNS])
        keys = old["date"].to_numpy()
        n_sess = to_float(old["us_n_sessions"]).to_numpy()   # written "1.0" by the frozen build (float column)
        check(f"{label}: us_n_sessions is a whole number on every row", np.isfinite(n_sess).all()
              and (n_sess == np.round(n_sess)).all())
        summed = per.loc[keys, "us_sessions_summed"].astype(int).to_numpy()
        check(f"{label}: NY sessions summed equal us_n_sessions on every row", (summed == n_sess).all())
        ur = final["usdjpy_us_ret"].to_numpy(dtype=float)
        zero_sum_nights = check_us_ret(label, keys, ur, n_sess, check)
        ewj = to_float(old["ewj_oc"]).to_numpy()
        check(f"{label}: ewj_oc_jpy is NaN if and only if ewj_oc is NaN",
              (np.isnan(final["ewj_oc_jpy"].to_numpy(dtype=float)) == np.isnan(ewj)).all())
        for c in ("y_1306_oc", "ao_1306_gap_raw", "ao_1306_gap_adj"):
            check(f"{label}: {c} finite on every row", np.isfinite(final[c].to_numpy(dtype=float)).all())
        ws = pd.to_datetime(old["window_start_utc"]).to_numpy(dtype="datetime64[ns]")
        we = pd.to_datetime(old["window_end_utc"]).to_numpy(dtype="datetime64[ns]")
        check(f"{label}: XAU and Japan 225 window instants equal the panel's window_start_utc and window_end_utc on every row",
              (ws == inst.loc[keys, "window_start_utc"].to_numpy(dtype="datetime64[ns]")).all()
              and (we == inst.loc[keys, "window_end_utc"].to_numpy(dtype="datetime64[ns]")).all())
        want_g = expect.gotobi_dev_per_ticker if label == "dev" else expect.gotobi_sealed_per_ticker
        g = final.groupby("ticker")["gotobi_day"].sum()
        check(f"{label}: gotobi_day sums to {want_g} per ticker", (g == want_g).all())

        final.to_csv(out / fname, index=False)
        back = read_old_panel(out / fname)
        check(f"{label}: written panel has 60 columns", back.shape[1] == N_OLD + len(C.NEW_COLUMNS))
        check(f"{label}: written old columns equal the original strings", back.iloc[:, :N_OLD].equals(old))
        proj_back = projection_sha256(back.iloc[:, :N_OLD])
        check(f"{label}: written old-column projection hashes to its source", proj_back == src_sha)
        results[fname] = {"sha256": sha256(out / fname), "rows": int(len(final)), "columns": int(final.shape[1]),
                          "span": [str(final["date"].min()), str(final["date"].max())],   # ISO strings
                          "old41_projection_sha256": proj_back,
                          "old41_source": {"what": source, "sha256": src_sha},
                          "usdjpy_us_ret_zero_sum_session_nights": zero_sum_nights}

    # 5. MANIFEST
    manifest = {
        "built": pd.Timestamp.now(tz="UTC").isoformat(),
        "builder": "build/pass2/build_panel_p2.py (Pass 2, P51; append-only)",
        "platform": {"platform": platform.platform(), "machine": platform.machine(), "sys_version": sys.version},
        "git": git,
        "libraries": library_versions(),
        "split_date": str(C.pass1.SPLIT_DATE.date()),
        "inputs": in_sha,
        "event_files": ev_sha,
        "original_dev_panel": {"path": str(orig_dev), "sha256": orig_sha},
        "code": code_sha,
        "frozen_build_outputs": {DEV_FILE: f_dev, SEALED_FILE: f_sealed},
        "old_columns": {"dev": results[DEV_FILE]["old41_source"], "sealed": results[SEALED_FILE]["old41_source"],
                        "reference_pairs": expect.reference_pairs},
        "new_columns": [{"name": c, "group": g} for c, g in C.NEW_COLUMNS],
        "outputs": results,
        "build_assertions": {"passed": len(check.passed), "names": check.passed},
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", required=True, type=Path)
    ap.add_argument("--events", required=True, type=Path)
    ap.add_argument("--orig-dev", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    if not git_state()["build_and_inputs_registry_clean"]:
        raise SystemExit("refusing to run: `git status --porcelain -- build/ docs/PASS2_INPUTS.json` is not empty")
    m = build(a.raw.expanduser(), a.events.expanduser(), a.orig_dev.expanduser(), a.out.expanduser())
    print(json.dumps({"outputs": {k: {x: v[x] for x in ("sha256", "rows", "columns", "span", "old41_projection_sha256")}
                                  for k, v in m["outputs"].items()},
                      "build_assertions_passed": m["build_assertions"]["passed"]}, indent=2))


if __name__ == "__main__":
    main()
