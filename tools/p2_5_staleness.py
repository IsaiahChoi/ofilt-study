"""P2-5 checks 2.2 and 2.3 (GAP-ONLY): the index-staleness test (P55; D10) and the 1306 evidence for P18 (D8).

Reads only date, ticker, ao_topix_gap, ao_topix_gap_tradj, ao_1306_gap_raw, ao_1306_gap_adj and exdiv_day
from the P2-4 dev panel, after verifying its SHA-256 against the build's MANIFEST.json. No target and no
predictor column is loaded. io.load_dev is not used (it refuses the 60-column panel until the switch).

2.2 (operational details fixed by Isaiah on 2026-10-05 before this script ran):
* one row per date; the four gap columns must be identical across the tickers of each date (else STOP);
  a date is a miner ex-day if exdiv_day == 1 for any ticker;
* 1306 ex-dates = dates where ao_1306_gap_adj != ao_1306_gap_raw; they must be exactly the 7 dev ex-dates
  (else STOP);
* g_E = ao_1306_gap_adj. Sample (i): dev dates with no miner ex-day and no 1306 ex-date, g_I = ao_topix_gap.
  Sample (ii): all dev dates, g_I = ao_topix_gap_tradj. NaN dates dropped, with a count;
* OLS with an intercept: b_IE = slope of g_I on g_E, b_EI = slope of g_E on g_I, R^2 centred, N = dates;
  b_IE * b_EI = R^2 checked to 1e-12. Reverse-slope 95% CI = b_EI +/- 1.96 SE, SE Newey-West (Bartlett,
  inference.bartlett_long_run) at lag floor(4 (N/100)^(2/9)) (Spec.dk_lag(N)); no small-sample correction;
* P55 reading: "staleness established" iff the CI lies entirely above 1, else "not established (not a
  finding of freshness)".
2.3: P2-1's dividend and split results restated (quoted from reports/P2_1_inputs.md); the share of dev dates
  with ao_1306_gap_raw == 0 and with ao_topix_gap == 0, overall and by year; the 7 dev ex-dates, which must
  reproduce the supervisor's table at 2 decimals (else STOP and flag).

Writes reports/P2_5_dev_checks.md (header, 2.2, 2.3; section 2.4 is written by tools/p2_5_coverage.py).
usage: python tools/p2_5_staleness.py
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from importlib import metadata
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ofilt.drift.inference import bartlett_long_run  # noqa: E402  (pure function; no data guard involved)
from ofilt.drift.spec import Spec  # noqa: E402

PANEL_DIR = Path(os.environ["HOME"]) / "Desktop" / "FX_Project" / "build_out" / "p2_20261006T002928Z"
COLS = ["date", "ticker", "ao_topix_gap", "ao_topix_gap_tradj", "ao_1306_gap_raw", "ao_1306_gap_adj", "exdiv_day"]
GAPS = ["ao_topix_gap", "ao_topix_gap_tradj", "ao_1306_gap_raw", "ao_1306_gap_adj"]
EX_1306 = ["2015-07-08", "2016-07-06", "2017-07-06", "2018-07-06", "2019-07-08", "2020-07-09", "2021-07-08"]
SUPERVISOR = {  # % to 2 decimals: (1306 adjusted, TOPIX), supervisor message of 2026-10-05
    "2015-07-08": (-0.30, -0.41), "2016-07-06": (-1.63, -1.55), "2017-07-06": (0.00, -0.04),
    "2018-07-06": (0.79, 0.55), "2019-07-08": (-0.16, -0.26), "2020-07-09": (-0.13, -0.09),
    "2021-07-08": (-0.21, -0.15)}
SUPERVISOR_MAX_DIFF_PP = 0.24
LIBS = ("pandas", "numpy", "scipy", "scikit-learn", "openpyxl", "PyYAML", "joblib", "threadpoolctl", "python-dateutil")
SECTION_24 = "## 2.4"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def env_lines() -> list[str]:
    out = [f"- python {platform.python_version()} ({platform.machine()}; {platform.platform()})"]
    out += [f"- {n} {metadata.version(n)}" for n in LIBS]
    cfg = np.show_config(mode="dicts")["Build Dependencies"]
    out += [f"- numpy {k}: {cfg[k].get('name')} (version {cfg[k].get('version')})" for k in ("blas", "lapack")]
    return out


def ols_slope(y: np.ndarray, x: np.ndarray):
    X = np.column_stack([np.ones(len(x)), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coef, y - X @ coef, X


def p55(gE: np.ndarray, gI: np.ndarray) -> dict:
    n = len(gE)
    (_, b_ie), e_ie, _ = ols_slope(gI, gE)
    (_, b_ei), e_ei, X = ols_slope(gE, gI)
    r2 = 1.0 - (e_ie @ e_ie) / ((gI - gI.mean()) @ (gI - gI.mean()))
    lag = Spec.dk_lag(int(n))
    bread = np.linalg.inv(X.T @ X)
    V = bread @ bartlett_long_run(X * e_ei[:, None], lag) @ bread
    se = float(np.sqrt(V[1, 1]))
    lo, hi = b_ei - 1.96 * se, b_ei + 1.96 * se
    return dict(N=n, b_IE=float(b_ie), b_EI=float(b_ei), R2=float(r2), identity_gap=abs(b_ie * b_ei - r2),
                lag=lag, se=se, ci=(float(lo), float(hi)), bracket=(float(b_ie), float(b_ie / r2)),
                reading="staleness established" if lo > 1 else "not established (not a finding of freshness)")


def main() -> int:
    manifest_sha = sha256(PANEL_DIR / "MANIFEST.json")
    m = json.loads((PANEL_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    want = m["outputs"]["panel_dev.csv"]["sha256"]
    got = sha256(PANEL_DIR / "panel_dev.csv")
    if got != want:
        sys.exit("STOP: panel_dev.csv does not hash to MANIFEST's entry")
    raw = pd.read_csv(PANEL_DIR / "panel_dev.csv", usecols=COLS, dtype=str, keep_default_na=False)
    assert set(raw.columns) == set(COLS), "loaded columns differ from the check's list"
    stop = []
    # one row per date
    same = {c: bool((raw.groupby("date")[c].nunique() == 1).all()) for c in GAPS}
    if not all(same.values()):
        stop.append("a gap column differs across the tickers of a date")
    by = raw.groupby("date", sort=True)
    d = by[GAPS].first()
    for c in GAPS:
        d[c] = pd.to_numeric(d[c].where(d[c] != "", np.nan)).astype(float)
    d["miner_ex"] = by["exdiv_day"].agg(lambda s: bool((s == "1").any()))
    nan_counts = {c: int(d[c].isna().sum()) for c in GAPS}
    ex_1306 = sorted(d.index[(d["ao_1306_gap_adj"] != d["ao_1306_gap_raw"]) & d["ao_1306_gap_adj"].notna()])
    if ex_1306 != EX_1306:
        stop.append("the 1306 ex-dates are not exactly the 7 dev ex-dates")
    out = []
    say = out.append
    say("# P2-5 dev checks (reports only)")
    say("")
    say(f"Panel: `build_out/{PANEL_DIR.name}/panel_dev.csv`, SHA-256 `{got}`, equal to its `MANIFEST.json` entry: "
        f"{got == want}. SHA-256 of `MANIFEST.json`: `{manifest_sha}`. Sections 2.2 and 2.3 are written by "
        "`tools/p2_5_staleness.py`, section 2.4 by `tools/p2_5_coverage.py`. A7 on 1306 (2.1) is in "
        "`reports/A_hedge_efficiency_1306.md`.")
    say("")
    say("**Environment (ofilt_p2):**")
    out.extend(env_lines())
    say("")
    say("## 2.2 Index-staleness test (P55; D10). Gap-only")
    say("")
    say("Columns: " + ", ".join(f"`{c}`" for c in COLS) + ". One row per date.")
    say(f"- Gap columns identical across the tickers of every date: " + "; ".join(f"`{c}` {v}" for c, v in same.items()))
    say(f"- Dev dates: {len(d)}; miner ex-day dates (exdiv_day == 1 for any ticker): {int(d['miner_ex'].sum())}")
    say(f"- 1306 ex-dates (ao_1306_gap_adj != ao_1306_gap_raw): {', '.join(ex_1306)}; exactly the 7 dev ex-dates: "
        f"{ex_1306 == EX_1306}")
    say("- NaN dates per gap column: " + "; ".join(f"`{c}` {n}" for c, n in nan_counts.items()))
    if stop:
        say("")
        say("**STOP: " + "; ".join(stop) + ".**")
        text = "\n".join(out) + "\n"
        (ROOT / "reports" / "P2_5_dev_checks.md").write_text(text, encoding="utf-8")
        print(text)
        return 2
    is_ex = d.index.isin(ex_1306)
    samples = {
        "(i) no miner ex-day and no 1306 ex-date; g_I = ao_topix_gap": (d[~d["miner_ex"] & ~is_ex], "ao_topix_gap"),
        "(ii) all dev dates; g_I = ao_topix_gap_tradj": (d, "ao_topix_gap_tradj"),
    }
    say("")
    say("Estimator: OLS with an intercept; g_E = `ao_1306_gap_adj`. b_IE = slope of g_I on g_E; b_EI = slope of g_E on g_I; "
        "R² centred; N = dates. Reverse-slope 95% CI = b_EI ± 1.96·SE, SE Newey–West (Bartlett) at lag "
        "floor(4·(N/100)^(2/9)), no small-sample correction. P55 reading: staleness established iff the CI lies "
        "entirely above 1.")
    say("")
    say("| Sample | N (NaN dates dropped) | b_IE | b_EI | R² | b_IE·b_EI − R² | bracket [b_IE, b_IE/R²] | NW lag | SE(b_EI) | 95% CI of b_EI | P55 reading |")
    say("|---|---|---|---|---|---|---|---|---|---|---|")
    res = {}
    for name, (s, gi) in samples.items():
        keep = s[["ao_1306_gap_adj", gi]].notna().all(axis=1)
        r = p55(s.loc[keep, "ao_1306_gap_adj"].to_numpy(), s.loc[keep, gi].to_numpy())
        res[name] = r
        if r["identity_gap"] > 1e-12:
            stop.append(f"b_IE * b_EI != R^2 to 1e-12 in sample {name[:4]}")
        say(f"| {name} | {r['N']} ({int((~keep).sum())}) | {r['b_IE']:.4f} | {r['b_EI']:.4f} | {r['R2']:.4f} | "
            f"{r['identity_gap']:.1e} | [{r['bracket'][0]:.4f}, {r['bracket'][1]:.4f}] | {r['lag']} | {r['se']:.4f} | "
            f"[{r['ci'][0]:.4f}, {r['ci'][1]:.4f}] | {r['reading']} |")
    say("")

    # 2.3
    say("## 2.3 1306 evidence for P18 (D8). Gap-only")
    say("")
    say("**P2-1's dividend and split results (quoted from `reports/P2_1_inputs.md`; not recomputed):**")
    p21 = (ROOT / "reports" / "P2_1_inputs.md").read_text(encoding="utf-8").splitlines()
    for line in p21:
        if line.startswith(("- OHLC violations", "- Split artifacts", "- Rows with open = close = previous close",
                            "- Fixed amount = RAW amount", "- Every ex-date is in", "- Types: fixed",
                            "- Declared, ex, record, pay")):
            say("> " + line)
    say("")
    z13, ztp = d["ao_1306_gap_raw"] == 0.0, d["ao_topix_gap"] == 0.0
    yr = pd.Series(d.index.str[:4], index=d.index)
    say("Share of dev dates with a gap of exactly 0 (one row per date):")
    say("")
    say("| Period | Dates | ao_1306_gap_raw == 0 | ao_topix_gap == 0 |")
    say("|---|---|---|---|")
    for period, mask in [("all dev", pd.Series(True, index=d.index))] + [(y, yr == y) for y in sorted(yr.unique())]:
        n = int(mask.sum())
        say(f"| {period} | {n} | {int(z13[mask].sum())} ({100 * z13[mask].mean():.2f}%) | "
            f"{int(ztp[mask].sum())} ({100 * ztp[mask].mean():.2f}%) |")
    say("")
    say("The 7 dev 1306 ex-dates (gaps in %, 2 decimals), against the supervisor's table:")
    say("")
    say("| Ex-date | ao_1306_gap_adj | ao_topix_gap | abs. difference (pp) | Supervisor (1306 adj / TOPIX) | Equal at 2 decimals |")
    say("|---|---|---|---|---|---|")
    table_ok, diffs, rdiffs = True, [], []
    for x in EX_1306:
        a, t = 100 * d.loc[x, "ao_1306_gap_adj"], 100 * d.loc[x, "ao_topix_gap"]
        ra, rt = round(a, 2), round(t, 2)
        eq = (ra, rt) == SUPERVISOR[x]
        table_ok &= eq
        diffs.append(abs(a - t))
        rdiffs.append(abs(ra - rt))
        say(f"| {x} | {a:+.2f} | {t:+.2f} | {abs(a - t):.2f} | {SUPERVISOR[x][0]:+.2f} / {SUPERVISOR[x][1]:+.2f} | {eq} |")
    say("")
    mx, rmx = max(diffs), max(rdiffs)
    say(f"- Every ex-date equals the supervisor's table at 2 decimals: {table_ok}")
    say(f"- Largest absolute difference: {mx:.2f} pp from the unrounded gaps; {rmx:.2f} pp from the 2-decimal values; "
        f"supervisor {SUPERVISOR_MAX_DIFF_PP:.2f} pp; equal: {round(mx, 2) == SUPERVISOR_MAX_DIFF_PP and round(rmx, 2) == SUPERVISOR_MAX_DIFF_PP}")
    if not table_ok:
        stop.append("the 7 ex-date gaps differ from the supervisor's table at 2 decimals")
    say("")
    if stop:
        say("**STOP: " + "; ".join(stop) + ".**")
    else:
        say("No STOP condition in 2.2 or 2.3.")
    say("")
    say("Blinding: gap columns and the miner ex-day flag only (dev). No target and no predictor column was loaded.")
    say("")
    say(f"{SECTION_24} Japan 225 eligibility and new-column coverage (written by `tools/p2_5_coverage.py`)")
    say("")
    say("(not yet written)")
    text = "\n".join(out) + "\n"
    (ROOT / "reports" / "P2_5_dev_checks.md").write_text(text, encoding="utf-8")
    print(text)
    return 2 if stop else 0


if __name__ == "__main__":
    sys.exit(main())
