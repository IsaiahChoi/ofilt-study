"""P3-0b pre-flight facts (supervisor message of 2026-10-06, item P3-0b). DEV ONLY. FACTS ONLY: no rule is applied.

Part A: the AM-03 estimation sample of the sealed fit, i.e. the rows that inference's design builder keeps for
the primary design (target abn_oc, default exclusions). The rule mirrors ofilt/drift/inference.py:92-98:
    excl_cols = spec.inference_exclusion_flags
    need      = spec.require_nonmissing + [abn_oc] + schema.feature_sources(fx_block + controls)
    keep      = ~df[excl_cols].astype(bool).any(axis=1) & df[need].notna().all(axis=1)
(and inference.py:130-131, which refuses non-finite values among the kept rows). T_source mirrors
ofilt/drift/sim.py:203-210: the number of unique dates among the kept rows. Predictor columns enter only through
non-missingness; no statistic of any predictor's values is computed, and nothing combines predictor values with
target values. Targets are built with targets.add_targets (target-only, as before the B7 calibrators).

Part B: the miners' price levels and price grids, from the target-side price columns `open` and `close` only, on
all dev rows. No cost, no SESOI and no mean |e| is computed.

The dev panel's SHA-256 is checked against the registry (the spec's dev-panel hash, AM-04, and
docs/PASS2_INPUTS.json pass2_outputs) BEFORE the file is read. Prints the report and writes only --out.

usage: python tools/p3_0b_preflight.py            # DATA/panel_dev.csv -> reports/P3_0b_preflight.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import schema  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

TARGET = "abn_oc"
GRID_CANDIDATES = (0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0)
GRID_TOL = 1e-6
SHARE_NEAR = 0.99
# Share-count changes (1:10 consolidations of 5711 and 5706; 1:2 of 5713), DATA_PROVENANCE.md line 67.
PROV_DOC, PROV_LINE = ROOT / "docs" / "DATA_PROVENANCE.md", 67
DICT_DOC, DICT_LINE = ROOT / "docs" / "replacements" / "DATA_DICTIONARY.md", 116
CONSOLIDATION = {"5706": "2017-09-27", "5711": "2016-09-28", "5713": "2017-09-27"}
QUANTILES = (("min", 0.0), ("p5", 0.05), ("median", 0.5), ("p95", 0.95), ("max", 1.0))


# ------------------------------------------------------------------ hash check
def registry_hashes(spec: Spec) -> dict:
    reg = json.loads((ROOT / "docs" / "PASS2_INPUTS.json").read_text(encoding="utf-8"))
    return {"spec data.dev_panel_sha256 (AM-04)": spec.data_hash("dev_panel"),
            "docs/PASS2_INPUTS.json pass2_outputs/panel_dev.csv/sha256": reg["pass2_outputs"]["panel_dev.csv"]["sha256"]}


def verify_panel(path: Path, spec: Spec) -> str:
    """SHA-256 of the file; SystemExit unless it equals every registry entry. Reads bytes only."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    bad = [k for k, v in registry_hashes(spec).items() if v != got]
    if bad:
        raise SystemExit(f"REFUSED: {path} SHA-256 {got} does not match the registry ({'; '.join(bad)})")
    return got


# ------------------------------------------------------------------ Part A
def need_columns(spec: Spec) -> list[str]:
    fx, ctl = list(spec.fx_block), list(spec.controls)
    return list(dict.fromkeys(list(spec.require_nonmissing) + [TARGET] + sorted(schema.feature_sources(fx + ctl))))


def sample_keep(df: pd.DataFrame, spec: Spec) -> pd.Series:
    """True on the rows the primary design keeps (inference.py:92-98). Non-missingness only."""
    excl_cols = list(spec.inference_exclusion_flags)
    return ~df[excl_cols].astype(bool).any(axis=1) & df[need_columns(spec)].notna().all(axis=1)


def sample_steps(df: pd.DataFrame, spec: Spec) -> list[tuple[str, pd.Series]]:
    """The same rule, applied sequentially: exclusion flags; beta and abn_oc; the other required columns."""
    excl_cols = list(spec.inference_exclusion_flags)
    need = need_columns(spec)
    s0 = pd.Series(True, index=df.index)
    s1 = s0 & ~df[excl_cols].astype(bool).any(axis=1)
    s2 = s1 & df[["beta", TARGET]].notna().all(axis=1)
    others = [c for c in need if c not in ("beta", TARGET)]
    s3 = s2 & df[others].notna().all(axis=1)
    return [("all dev rows", s0), (f"after the exclusion flags {excl_cols}", s1),
            ("after beta and abn_oc availability", s2), (f"after the other required columns {others}", s3)]


# ------------------------------------------------------------------ Part B
def on_grid(x: np.ndarray, g: float) -> np.ndarray:
    q = np.asarray(x, dtype=float) / g
    return np.abs(q - np.round(q)) < GRID_TOL


def grid_shares(x: np.ndarray) -> dict:
    return {g: float(on_grid(x, g).mean()) for g in GRID_CANDIDATES}


def detect_grid(x: np.ndarray) -> tuple[float | None, float | None]:
    """(largest g with share 1.0, largest g with share >= SHARE_NEAR); None if no candidate qualifies."""
    sh = grid_shares(x)
    full = [g for g in GRID_CANDIDATES if sh[g] == 1.0]
    near = [g for g in GRID_CANDIDATES if sh[g] >= SHARE_NEAR]
    return (max(full) if full else None), (max(near) if near else None)


def period_of(dates: pd.Series, ticker: str) -> pd.Series:
    cut = pd.Timestamp(CONSOLIDATION[ticker])
    return pd.Series(np.where(dates < cut, f"before {CONSOLIDATION[ticker]}", f"from {CONSOLIDATION[ticker]}"),
                     index=dates.index)


def grid_table(px: pd.DataFrame) -> list[dict]:
    """One row per (ticker, calendar year, period): shares over the pooled opens and closes, and the grids."""
    rows = []
    for t, sub in px.groupby("ticker", sort=True):
        per = period_of(sub["date"], t)
        for (yr, p), cell in sub.groupby([sub["date"].dt.year, per], sort=True):
            x = np.r_[cell["open"].to_numpy(float), cell["close"].to_numpy(float)]
            full, near = detect_grid(x)
            rows.append(dict(ticker=t, year=int(yr), period=p, n_prices=int(x.size), shares=grid_shares(x),
                             grid=full, grid_099=near))
    return rows


def fmt_share(s: float) -> str:
    return "1" if s == 1.0 else f"{math.floor(s * 1e4) / 1e4:.4f}"


def fmt_g(g: float | None) -> str:
    return "none" if g is None else f"{g:g}"


def fmt_px(v: float) -> str:
    return f"{v:.7g}"


# ------------------------------------------------------------------ report
def build_report(df: pd.DataFrame, spec: Spec, digest: str) -> str:
    L = []
    say = L.append
    tick = df["ticker"].astype(str)
    say("# P3-0b pre-flight facts (dev only; facts only, no rule applied)")
    say("")
    say(f"Generated by `tools/p3_0b_preflight.py`. Dev panel SHA-256 `{digest}`, equal to the spec's dev-panel hash "
        f"(AM-04) and to `docs/PASS2_INPUTS.json` (checked before the file was read). Spec SHA-256 `{spec.sha256}`. "
        f"Targets built by `targets.add_targets` (hedge `{spec.hedge_oc_column}`). Rows in the dev panel: {len(df)}.")
    say("")

    # ---------------- Part A
    keep = sample_keep(df, spec)
    steps = sample_steps(df, spec)
    if not steps[-1][1].equals(keep):
        raise AssertionError("sequential rule differs from the one-expression rule")
    need = need_columns(spec)
    finite = bool(np.isfinite(df.loc[keep, need].to_numpy(dtype=float)).all())
    if not finite:
        raise AssertionError("non-finite values among kept rows: the design builder would refuse this sample")
    k = df.loc[keep, ["date", "ticker"]]
    udates = np.sort(k["date"].unique())
    per_date = k.groupby("date").size()
    say("## Part A: the AM-03 estimation sample")
    say("")
    say("Rule (mirrors `ofilt/drift/inference.py:92-98`; T_source as `ofilt/drift/sim.py:203-210`): drop rows with any "
        f"of `spec.inference_exclusion_flags` = {list(spec.inference_exclusion_flags)} set; keep rows where "
        f"{need} are all non-missing (`spec.require_nonmissing` + `{TARGET}` + the primary design's feature "
        "sources). Kept rows are all finite in those columns (`inference.py:130-131`): True.")
    say("")
    say(f"- Kept rows: **{int(keep.sum())}**")
    say(f"- Kept unique dates (T_source): **{len(udates)}**")
    say("- Kept rows per ticker: " + ", ".join(f"{t} {int((keep & (tick == t)).sum())}" for t in IO.TICKERS))
    say(f"- First kept date: {pd.Timestamp(udates[0]).date()}; last kept date: {pd.Timestamp(udates[-1]).date()}")
    say("- Kept dates with 1, 2 and 3 tickers: " + ", ".join(f"{n}: {int((per_date == n).sum())}" for n in (1, 2, 3)))
    say("")
    say("Sequential drop table (rows remaining; dropped at the step in brackets):")
    say("")
    say("| Step | " + " | ".join(IO.TICKERS) + " | All |")
    say("|---|" + "---|" * (len(IO.TICKERS) + 1))
    prev = None
    for name, s in steps:
        cells = []
        for sel in [tick == t for t in IO.TICKERS] + [pd.Series(True, index=df.index)]:
            n = int((s & sel).sum())
            cells.append(str(n) if prev is None else f"{n} ({int((prev & sel).sum()) - n})")
        say(f"| {name} | " + " | ".join(cells) + " |")
        prev = s
    say("")
    say("Flag 4 windows (kept rows of one ticker; one row per date, so kept dates = kept rows):")
    say("")
    say("| Ticker | Window | Kept dates | Kept rows |")
    say("|---|---|---|---|")
    for t, note in (("5711", "1:10"), ("5706", "1:10"), ("5713", "1:2, for information")):
        sel = keep & (tick == t) & (df["date"] < pd.Timestamp(CONSOLIDATION[t]))
        say(f"| {t} | before {CONSOLIDATION[t]} ({note}) | {int(df.loc[sel, 'date'].nunique())} | {int(sel.sum())} |")
    say("")
    say("For comparison only: Pass 1's B7 T_source was 1,439 dates, on the TOPIX hedge.")
    say("")

    # ---------------- Part B
    px = df[["date", "ticker", "open", "close"]].copy()
    px["ticker"] = px["ticker"].astype(str)
    if px[["open", "close"]].isna().any().any():
        raise AssertionError("missing open/close prices in the dev panel")
    prov_line = PROV_DOC.read_text(encoding="utf-8").splitlines()[PROV_LINE - 1]
    dict_line = DICT_DOC.read_text(encoding="utf-8").splitlines()[DICT_LINE - 1]
    if not all(d in prov_line for d in CONSOLIDATION.values()):
        raise AssertionError("DATA_PROVENANCE line does not list the consolidation dates")
    say("## Part B: miner price levels and grids (`open`, `close`; all dev rows)")
    say("")
    say("**B1. Adjustment.** The panel's miner prices are adjusted for capital changes:")
    say("")
    say(f"> `docs/DATA_PROVENANCE.md:{PROV_LINE}`: {prov_line}")
    say(">")
    say(f"> `docs/replacements/DATA_DICTIONARY.md:{DICT_LINE}`: {dict_line}")
    say("")
    say("**B2. Levels** (numpy linear-interpolation quantiles):")
    say("")
    say("| Ticker | Period | Rows | Column | min | p5 | median | p95 | max |")
    say("|---|---|---|---|---|---|---|---|---|")
    for t in IO.TICKERS:
        sub = px[px["ticker"] == t]
        per = period_of(sub["date"], t)
        for p in sorted(per.unique(), key=lambda s: not s.startswith("before")):
            cell = sub[per == p]
            for col in ("open", "close"):
                v = cell[col].to_numpy(float)
                qs = " | ".join(fmt_px(float(np.quantile(v, q))) for _, q in QUANTILES)
                say(f"| {t} | {p} | {len(cell)} | {col} | {qs} |")
    say("")
    gt = grid_table(px)
    say("**B3. Grids.** Share of the pooled opens and closes that are integer multiples of g "
        f"(|x/g - round(x/g)| < {GRID_TOL:g}); shares truncated to 4 decimals, '1' means exactly 1. "
        f"Detected grid = the largest g with share 1; 'share >= {SHARE_NEAR}' = the largest g with share >= {SHARE_NEAR}, "
        "shown only where it differs.")
    say("")
    say("| Ticker | Year | Period | Prices | " + " | ".join(f"g={g:g}" for g in GRID_CANDIDATES)
        + f" | Detected | Share >= {SHARE_NEAR} |")
    say("|---|---|---|---|" + "---|" * len(GRID_CANDIDATES) + "---|---|")
    for r in gt:
        near = fmt_g(r["grid_099"]) if r["grid_099"] != r["grid"] else ""
        say(f"| {r['ticker']} | {r['year']} | {r['period']} | {r['n_prices']} | "
            + " | ".join(fmt_share(r["shares"][g]) for g in GRID_CANDIDATES) + f" | {fmt_g(r['grid'])} | {near} |")
    say("")
    say("**B4. One tick in basis points.** Median over the period's rows of 10,000 x g / price, with g the detected "
        "grid of the row's (ticker, year, period) cell in B3. The ratio does not depend on the capital-change "
        "adjustment, which scales g and the price alike.")
    say("")
    say("| Ticker | Period | open | close | Rows without a detected grid |")
    say("|---|---|---|---|---|")
    gmap = {(r["ticker"], r["year"], r["period"]): r["grid"] for r in gt}
    for t in IO.TICKERS:
        sub = px[px["ticker"] == t]
        per = period_of(sub["date"], t)
        g = np.array([gmap[(t, int(y), p)] if gmap[(t, int(y), p)] is not None else np.nan
                      for y, p in zip(sub["date"].dt.year, per)], dtype=float)
        for p in sorted(per.unique(), key=lambda s: not s.startswith("before")):
            m = (per == p).to_numpy()
            ok = m & np.isfinite(g)
            med = {c: float(np.median(1e4 * g[ok] / sub[c].to_numpy(float)[ok])) for c in ("open", "close")}
            say(f"| {t} | {p} | {med['open']:.2f} | {med['close']:.2f} | {int(m.sum() - ok.sum())} |")
    say("")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", type=Path, default=IO.DATA_DIR / IO.DEV_FILE)
    ap.add_argument("--out", type=Path, default=ROOT / "reports" / "P3_0b_preflight.md")
    a = ap.parse_args(argv)
    spec = Spec.load()
    digest = verify_panel(a.panel, spec)                  # before the file is read
    df = TG.add_targets(IO.load_dev(a.panel, spec), spec)
    md = build_report(df, spec, digest)
    a.out.write_text(md, encoding="utf-8")
    print(md, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
