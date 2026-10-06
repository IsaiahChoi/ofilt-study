"""P2-5 check 2.4: Japan 225 eligibility (P42 as proposed; D7) and new-column coverage. PREDICTORS AND
PROVENANCE ONLY: no y_ and no ao_ column is loaded from either panel.

Both P2-4 panels are hash-verified against the build's MANIFEST.json before loading. Sealed values are used
only to form counts and booleans; no sealed date or value is printed. One row per date: the date-level
columns must be identical across tickers (else STOP).
* Japan 225 by half-year: dates; dates with no bar (every n225_* empty); start fresh (n225_stale_start_min <= 5);
  end fresh (n225_stale_end_min <= 5); both fresh (P42-eligible). End-fresh counts must equal the P2-4
  acceptance table (reports/P2_4_acceptance.md), else STOP and flag. Dev totals; first and last eligible dev date.
* Threshold sensitivity: eligible counts at <= 4, <= 5, <= 10 minutes by half-year; each endpoint's staleness
  in bins {0, 1-5, 6-60, > 60, empty}: dev by half-year, sealed in total. XAU endpoints in the same bins:
  dev by year, sealed in total.
* Coverage: empty dates of each of the 15 new predictor and provenance columns, dev and sealed.
* usdjpy_us_ret exact-zero session nights: the raw USD/JPY master is hash-verified against PASS2_INPUTS.json,
  then each such night's NY sessions are recomputed with build/pass2's own functions. Dev: dates, bar labels
  and staleness, no price. Sealed: counts and booleans only.

Writes section 2.4 of reports/P2_5_dev_checks.md (replacing it; sections 2.2-2.3 come from
tools/p2_5_staleness.py). usage: python tools/p2_5_coverage.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build" / "pass2"))
import columns as C  # noqa: E402

FX = Path(os.environ["HOME"]) / "Desktop" / "FX_Project"
PANEL_DIR = FX / "build_out" / "p2_20261006T002928Z"
RAW = FX / "raw"
COLS = ["date", "ticker", "us_n_sessions", "xau_ret", "xau_rv", "xau_bv", "n225_ret", "usdjpy_us_ret", "ewj_oc_jpy",
        "gotobi_day", "c_usdjpy_sess_ret", "c_eurusd_sess_ret", "xau_bars", "xau_stale_start_min", "xau_stale_end_min",
        "n225_bars", "n225_stale_start_min", "n225_stale_end_min"]
NEW15 = COLS[3:]
N225 = ["n225_ret", "n225_bars", "n225_stale_start_min", "n225_stale_end_min"]
BINS = ("0", "1-5", "6-60", ">60", "empty")
USDJPY = "usdjpy_dukascopy_2015-01-01_2026-03-05.csv"
SECTION = "## 2.4"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(name: str, manifest: dict) -> pd.DataFrame:
    if sha256(PANEL_DIR / name) != manifest["outputs"][name]["sha256"]:
        sys.exit(f"STOP: {name} does not hash to MANIFEST's entry")
    p = pd.read_csv(PANEL_DIR / name, usecols=COLS, dtype=str, keep_default_na=False)
    assert set(p.columns) == set(COLS), "loaded columns differ from the check's list"
    return p


def per_date(p: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    same = bool((p.groupby("date")[COLS[2:]].nunique() == 1).all().all())
    d = p.groupby("date", sort=True)[COLS[2:]].first()
    num = pd.DataFrame({c: pd.to_numeric(d[c].where(d[c] != "", np.nan)).astype(float) for c in COLS[2:]}, index=d.index)
    return num, same


def half(idx) -> pd.Series:
    return pd.Series([f"{x[:4]}-H{1 if int(x[5:7]) <= 6 else 2}" for x in idx], index=idx)


def bins(s: pd.Series) -> dict:
    return {"0": int((s == 0).sum()), "1-5": int(((s > 0) & (s <= 5)).sum()), "6-60": int(((s > 5) & (s <= 60)).sum()),
            ">60": int((s > 60).sum()), "empty": int(s.isna().sum())}


def main() -> int:
    manifest_sha = sha256(PANEL_DIR / "MANIFEST.json")
    m = json.loads((PANEL_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    dev, same_d = per_date(load("panel_dev.csv", m))
    sea, same_s = per_date(load("panel_confirm_SEALED.csv", m))
    out, flags, stop = [], [], []
    say = out.append
    say(f"{SECTION} Japan 225 eligibility (P42 as proposed; D7) and new-column coverage. Predictors and provenance only")
    say("")
    say(f"Written by `tools/p2_5_coverage.py`. Both panels verified against `MANIFEST.json` (SHA-256 `{manifest_sha}`) "
        "before loading. Columns: " + ", ".join(f"`{c}`" for c in COLS) + ". No `y_` or `ao_` column is loaded. "
        "Sealed side: counts and booleans only.")
    say("")
    say(f"- Date-level columns identical across the tickers of every date: dev {same_d}; sealed {same_s}")
    if not (same_d and same_s):
        stop.append("a date-level column differs across tickers")
    # Japan 225 eligibility
    p24 = {}
    for line in (ROOT / "reports" / "P2_4_acceptance.md").read_text(encoding="utf-8").splitlines():
        r = re.match(r"^\s*\| (\d{4}-H[12]) \| (\d+) \| (\d+) \|", line)
        if r:
            p24[r.group(1)] = (int(r.group(2)), int(r.group(3)))
    say("")
    say("**Japan 225 by half-year** (one row per date; fresh = at most 5 minutes stale; eligible = both endpoints fresh):")
    say("")
    say("| Half-year | Dates | No Japan 225 bar | Start fresh | End fresh | Eligible (both) | End fresh = P2-4 table |")
    say("|---|---|---|---|---|---|---|")
    end_ok = []
    for frame in (dev, sea):
        h = half(frame.index)
        nobar = frame[N225].isna().all(axis=1)
        sf, ef = frame["n225_stale_start_min"] <= 5, frame["n225_stale_end_min"] <= 5
        for hy in sorted(h.unique()):
            k = h == hy
            eq = (int(k.sum()), int(ef[k].sum())) == p24.get(hy)
            end_ok.append(eq)
            say(f"| {hy} | {int(k.sum())} | {int(nobar[k].sum())} | {int(sf[k].sum())} | {int(ef[k].sum())} | "
                f"{int((sf & ef)[k].sum())} | {eq} |")
    if not all(end_ok) or len(end_ok) != len(p24):
        stop.append("the Japan 225 end-fresh counts differ from the P2-4 acceptance table")
    elig_dev = (dev["n225_stale_start_min"] <= 5) & (dev["n225_stale_end_min"] <= 5)
    e_dates = dev.index[elig_dev]
    say("")
    say(f"- Dev totals: {len(dev)} dates; no Japan 225 bar {int(dev[N225].isna().all(axis=1).sum())}; start fresh "
        f"{int((dev['n225_stale_start_min'] <= 5).sum())}; end fresh {int((dev['n225_stale_end_min'] <= 5).sum())}; "
        f"eligible {int(elig_dev.sum())}. First eligible dev date {e_dates[0]}; last {e_dates[-1]}.")
    say(f"- Sealed totals: {len(sea)} dates; eligible "
        f"{int(((sea['n225_stale_start_min'] <= 5) & (sea['n225_stale_end_min'] <= 5)).sum())}.")
    # threshold sensitivity
    say("")
    say("**Threshold sensitivity** (eligible = both endpoints at most k minutes stale):")
    say("")
    say("| Half-year | Dates | k = 4 | k = 5 | k = 10 |")
    say("|---|---|---|---|---|")
    for frame in (dev, sea):
        h = half(frame.index)
        for hy in sorted(h.unique()):
            k = h == hy
            cells = [int(((frame["n225_stale_start_min"] <= t) & (frame["n225_stale_end_min"] <= t))[k].sum()) for t in (4, 5, 10)]
            say(f"| {hy} | {int(k.sum())} | " + " | ".join(map(str, cells)) + " |")
    for name, cols, unit in (("Japan 225", ("n225_stale_start_min", "n225_stale_end_min"), "half"),
                             ("XAU", ("xau_stale_start_min", "xau_stale_end_min"), "year")):
        say("")
        say(f"**{name} endpoint staleness in minutes, bins {{0, 1–5, 6–60, > 60, empty}}** "
            f"(dev by {'half-year' if unit == 'half' else 'year'}; sealed in total):")
        say("")
        say("| Period | Endpoint | " + " | ".join(BINS) + " |")
        say("|---|---|" + "---|" * len(BINS))
        grp = half(dev.index) if unit == "half" else pd.Series([x[:4] for x in dev.index], index=dev.index)
        for g in sorted(grp.unique()):
            for c in cols:
                b = bins(dev.loc[grp == g, c])
                say(f"| {g} | {c.split('_')[2]} | " + " | ".join(str(b[x]) for x in BINS) + " |")
        for c in cols:
            b = bins(sea[c])
            say(f"| sealed, total | {c.split('_')[2]} | " + " | ".join(str(b[x]) for x in BINS) + " |")
    # coverage
    say("")
    say("**Coverage: empty / NaN dates of each new column** (one row per date):")
    say("")
    say("| Column | Dev (of {}) | Sealed (of {}) |".format(len(dev), len(sea)))
    say("|---|---|---|")
    for c in NEW15:
        say(f"| `{c}` | {int(dev[c].isna().sum())} | {int(sea[c].isna().sum())} |")
    ewj = (int(dev["ewj_oc_jpy"].isna().sum()), int(sea["ewj_oc_jpy"].isna().sum()))
    say("")
    say(f"- `ewj_oc_jpy` empty on {ewj[0]} dev dates (expected 3, P12) and {ewj[1]} sealed dates (expected 0): {ewj == (3, 0)}")
    if ewj != (3, 0):
        flags.append("ewj_oc_jpy coverage differs from the expected 3 / 0")
    # exact-zero session nights
    reg = json.loads((ROOT / "docs" / "PASS2_INPUTS.json").read_text(encoding="utf-8"))["inputs"]
    say("")
    say("**usdjpy_us_ret exact-zero session nights** (us_n_sessions > 0 and usdjpy_us_ret == 0.0):")
    say("")
    hashes_ok = all(sha256(RAW / n) == reg[n]["sha256"] for n in (USDJPY, "Book2.xlsx"))
    say(f"- Raw USD/JPY master and Book2.xlsx hash to PASS2_INPUTS.json: {hashes_ok}")
    if not hashes_ok:
        stop.append("a raw input hash differs")
        rep = ROOT / "reports" / "P2_5_dev_checks.md"
        print("\n".join(out) + "\n\n**STOP: " + "; ".join(stop) + ".**")
        return 2
    ts, px = C.pass1.load_fx(RAW / USDJPY)          # only after the hash check (A′ hard rule 1)
    cal = pd.DatetimeIndex(pd.to_datetime(pd.read_excel(RAW / "Book2.xlsx", sheet_name="5713", header=None, usecols=[0])[0])).sort_values()
    uscal = pd.DatetimeIndex(pd.to_datetime(pd.read_excel(RAW / "Book2.xlsx", sheet_name="SPY", header=None, usecols=[0])[0])).sort_values()
    sessions = {C.day_key(k): v for k, v in C.us_session_dates(uscal, cal).items()}

    def nights(frame):
        z = frame[(frame["us_n_sessions"] > 0) & (frame["usdjpy_us_ret"] == 0.0)]
        res = []
        for day, row in z.iterrows():
            legs, total = [], 0.0
            for dd in sessions[day]:
                t0, t1 = C.us_session_instants(dd, C.NYSE_EARLY_CLOSES)
                p0, s0, i0 = C.pass1.price_at(ts, px, t0)
                p1, s1, i1 = C.pass1.price_at(ts, px, t1)
                total += float(np.log(p1 / p0))
                legs.append(dict(ny=C.day_key(dd), open_bar=pd.Timestamp(ts[i0]), open_stale=s0,
                                 close_bar=pd.Timestamp(ts[i1]), close_stale=s1, distinct=bool(i0 != i1)))
            res.append(dict(date=day, n=int(row["us_n_sessions"]), legs=legs, recomputed_zero=total == 0.0,
                            count_ok=len(legs) == int(row["us_n_sessions"])))
        return res
    zd, zs = nights(dev), nights(sea)
    mz = (m["outputs"]["panel_dev.csv"]["usdjpy_us_ret_zero_sum_session_nights"],
          m["outputs"]["panel_confirm_SEALED.csv"]["usdjpy_us_ret_zero_sum_session_nights"])
    say(f"- Count: dev {len(zd)}, sealed {len(zs)}; equal to MANIFEST ({mz[0]} / {mz[1]}): {(len(zd), len(zs)) == mz}")
    say("")
    say("| Dev date | us_n_sessions | NY session | open: bar label (UTC), staleness | close: bar label (UTC), staleness | distinct bars |")
    say("|---|---|---|---|---|---|")
    for r in zd:
        for leg in r["legs"]:
            say(f"| {r['date']} | {r['n']} | {leg['ny']} | {leg['open_bar']:%Y-%m-%d %H:%M}, {leg['open_stale']:.0f} min | "
                f"{leg['close_bar']:%Y-%m-%d %H:%M}, {leg['close_stale']:.0f} min | {leg['distinct']} |")
    dev_ok = all(leg["distinct"] for r in zd for leg in r["legs"])
    sea_ok = all(leg["distinct"] for r in zs for leg in r["legs"])
    say("")
    say(f"- Dev: sessions recomputed = us_n_sessions on every such night: {all(r['count_ok'] for r in zd)}; recomputed sum "
        f"exactly 0.0 on every such night: {all(r['recomputed_zero'] for r in zd)}; every session's open and close resolve "
        f"to distinct bars: {dev_ok}")
    say(f"- Sealed: nights {len(zs)}; sessions {sum(len(r['legs']) for r in zs)}; sessions recomputed = us_n_sessions on "
        f"every such night: {all(r['count_ok'] for r in zs)}; recomputed sum exactly 0.0 on every such night: "
        f"{all(r['recomputed_zero'] for r in zs)}; every session's open and close resolve to distinct bars: {sea_ok}")
    if not (dev_ok and sea_ok):
        flags.append("a zero-sum night has a session whose open and close resolve to the same bar (a data gap, not equal bids)")
    say("")
    say("**STOP: " + "; ".join(stop) + ".**" if stop else "No STOP condition in 2.4.")
    if flags:
        say("")
        say("**Flags:** " + "; ".join(flags) + ".")
    say("")
    say("Blinding: predictor and provenance columns only, as counts (sealed side: counts and booleans only); the raw "
        "USD/JPY master read by script for bar labels and staleness. No target and no gap column was loaded.")
    section = "\n".join(out) + "\n"
    rep = ROOT / "reports" / "P2_5_dev_checks.md"
    t = rep.read_text(encoding="utf-8")
    t = t[: t.index(SECTION)] if SECTION in t else t + "\n"
    rep.write_text(t + section, encoding="utf-8")
    print(section)
    return 2 if stop else 0


if __name__ == "__main__":
    sys.exit(main())
