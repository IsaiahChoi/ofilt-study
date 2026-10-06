"""P2-5 check 2.1: A7 on 1306 (P17, P18; D9). TARGET-ONLY.

Reads only date, ticker, y_oc, y_topix_oc, y_1306_oc, earn_flag and news_flag from the fresh P2-4 dev
panel, after verifying its SHA-256 against the build's MANIFEST.json. No predictor column is loaded.
y_topix_oc is loaded for the self-check only. io.load_dev is not used: it refuses the 60-column panel
until the switch commit, as intended.

Definitions are tools/report_A7.py's, imported where they are functions or constants (TICKERS,
WINDOWS, keep_mask, lowest_is_expanding). report_A7's beta and value functions hard-code the
TOPIX hedge, so their two-line bodies are restated here with the hedge passed explicitly
to targets.past_beta:
* beta: targets.past_beta(..., hedge=<hedge>, eligible=~targets.exclusion_mask) (beta on non-excluded
  rows, spec estimate_on), lag 1 day; expanding with min_periods 250; rolling = the last w eligible rows;
* evaluation rows: date >= 2017-01-01, earn_flag == 0, news_flag == 0, per ticker;
* value: var(y_oc - beta * hedge) x 1e8 (bp^2), pandas ddof = 1, rows with NaN beta skipped;
  `none` = var(y_oc) on the same rows;
* table (a): each window on its own rows; table (b), the DECISION TABLE: all windows on the common rows
  where every beta exists.

Self-check first: the same harness with hedge = y_topix_oc must reproduce both TOPIX tables of the
committed reports/A_hedge_efficiency.md (decision table and own-rows table) cell for cell, as printed.
On any mismatch: STOP before anything is computed with y_1306_oc.
D9: STOP and flag if expanding is not lowest on common rows for every ticker.

Writes reports/A_hedge_efficiency_1306.md. tools/report_A7.py and reports/A_hedge_efficiency.md are
not modified. usage: python tools/report_A7_1306.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import report_A7 as A7  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

PANEL_DIR = Path(os.environ["HOME"]) / "Desktop" / "FX_Project" / "build_out" / "p2_20261006T002928Z"
COLS = ["date", "ticker", "y_oc", "y_topix_oc", "y_1306_oc", "earn_flag", "news_flag"]
BETA_WINDOWS = [w for w in A7.WINDOWS if w != "none"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load():
    manifest_sha = sha256(PANEL_DIR / "MANIFEST.json")
    m = json.loads((PANEL_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    want = m["outputs"]["panel_dev.csv"]["sha256"]
    if sha256(PANEL_DIR / "panel_dev.csv") != want:
        sys.exit("STOP: panel_dev.csv does not hash to MANIFEST's entry")
    d = pd.read_csv(PANEL_DIR / "panel_dev.csv", usecols=COLS, dtype={"ticker": str}, parse_dates=["date"])
    assert set(d.columns) == set(COLS), "loaded columns differ from the check's list"
    d = d.sort_values(["date", "ticker"], kind="mergesort").reset_index(drop=True)   # io._read_panel's order
    d.attrs["provenance"] = "dev_real"
    return d, manifest_sha, want


def beta(d, w, hedge, eligible):
    """report_A7.impl_beta with the hedge passed explicitly."""
    if w == "expanding":
        return TG.past_beta(d, hedge=hedge, method="expanding", min_periods=250, eligible=eligible)
    return TG.past_beta(d, hedge=hedge, method="rolling", window=w, eligible=eligible)


def reported(d, b, t, hedge):
    """report_A7.reported with the hedge passed explicitly."""
    k = A7.keep_mask(d) & (d.ticker == t)
    r = (d.y_oc - b * d[hedge])[k]
    return float(r.var() * 1e8), int(r.notna().sum())


def table(d, hedge, bb, common=None):
    """Values and row counts for every window; `common` restricts all windows to the same rows."""
    dd = d if common is None else d.assign(y_oc=d.y_oc.where(common))
    vals, ns = {}, {}
    for w in A7.WINDOWS:
        b = pd.Series(0.0, index=d.index) if w == "none" else bb[w]
        res = [reported(dd, b, t, hedge) for t in A7.TICKERS]
        vals[w], ns[w] = [r[0] for r in res], [r[1] for r in res]
    return vals, ns


def fmt_tab(vals, ns=None, ref=None):
    """report_A7's table format (its fmt_tab is local to its main())."""
    lines = ["| window | " + " | ".join(A7.TICKERS) + " |", "|---|---|---|---|"]
    for w in A7.WINDOWS:
        cells = []
        for j in range(3):
            c = f"{vals[w][j]:,.1f}"
            if ref is not None:
                c += f" ({100 * (vals[w][j] / ref[w][j] - 1):+.3f}%)"
            if ns is not None:
                c += f" [n={ns[w][j]}]"
            cells.append(c)
        lines.append(f"| {w} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def committed_table(heading: str) -> list[str]:
    t = (ROOT / "reports" / "A_hedge_efficiency.md").read_text(encoding="utf-8")
    i = t.index(heading)
    j = t.find("\n## ", i + 1)
    return [line for line in t[i:j if j > 0 else None].splitlines() if line.startswith("|")]   # header, separator, rows


def harness(d, hedge, spec):
    elig = ~TG.exclusion_mask(d, spec)
    bb = {w: beta(d, w, hedge, elig) for w in BETA_WINDOWS}
    own_v, own_n = table(d, hedge, bb)
    common = A7.keep_mask(d) & pd.concat(bb.values(), axis=1).notna().all(axis=1)
    c_v, c_n = table(d, hedge, bb, common)
    return own_v, own_n, c_v, c_n


def main() -> int:
    d, manifest_sha, panel_sha = load()
    spec = Spec.load()
    out = []
    say = out.append
    # --- self-check: TOPIX on the fresh panel = the committed TOPIX tables, as printed
    all_v, _ = table(d, "y_topix_oc", {w: beta(d, w, "y_topix_oc", None) for w in BETA_WINDOWS})   # part (a): all rows
    own_v, own_n, c_v, c_n = harness(d, "y_topix_oc", spec)
    mine_dec = fmt_tab(c_v, c_n).splitlines()
    mine_own = fmt_tab(own_v, own_n, all_v).splitlines()
    ref_dec = committed_table("## (b) DECISION TABLE")
    ref_own = committed_table("## (b-own-rows)")
    dec_ok, own_ok = mine_dec == ref_dec, mine_own == ref_own
    print(f"self-check, TOPIX decision table (common rows) equals the committed report, cell for cell: {dec_ok}")
    print(f"self-check, TOPIX own-rows table equals the committed report, cell for cell: {own_ok}")
    if not (dec_ok and own_ok):
        for a, b in zip(mine_dec + mine_own, ref_dec + ref_own):
            if a != b:
                print(f"  mismatch: computed {a!r} vs committed {b!r}")
        print("STOP: the TOPIX self-check failed; nothing is computed with y_1306_oc")
        return 2
    # --- 1306
    nan_1306 = int(d["y_1306_oc"].isna().sum())
    v13, n13, cv13, cn13 = harness(d, "y_1306_oc", spec)
    low = A7.lowest_is_expanding(cv13)
    common_n = {t: cn13["expanding"][j] for j, t in enumerate(A7.TICKERS)}
    say("# A7 on 1306: hedge efficiency of past-only beta windows (dev, target-only)")
    say("")
    say(f"Generated by `tools/report_A7_1306.py` (P2-5, check 2.1; P17, P18; D9) from the P2-4 dev panel "
        f"`build_out/{PANEL_DIR.name}/panel_dev.csv`. The panel was SHA-256-verified against its `MANIFEST.json` "
        f"(`{panel_sha}`) before loading; the MANIFEST's own SHA-256 is `{manifest_sha}`.")
    say("")
    say("Reads only " + ", ".join(f"`{c}`" for c in COLS) + "; no predictor column is loaded. `y_topix_oc` is used only "
        "for the self-check.")
    say("")
    say("**Definitions** (tools/report_A7.py's, with the hedge passed explicitly):")
    say("- **Evaluation rows:** date >= 2017-01-01, earn_flag == 0, news_flag == 0, per ticker.")
    say("- **Beta:** `targets.past_beta(..., hedge=y_1306_oc, eligible = ~excl_inference)`, i.e. on non-excluded rows (spec "
        "`estimate_on: non_excluded_rows`), lag 1 day; expanding with min_periods 250; rolling = the last w eligible rows.")
    say("- **Value:** var(y_oc − beta · y_1306_oc) × 1e8 (bp²), pandas ddof = 1, rows with NaN beta skipped. "
        "`none` = var(y_oc) on the same rows.")
    say("- **Table (a):** each window on its own rows, with n per cell. **Table (b), the decision table:** all windows on "
        "the common rows where every beta exists, with the common n per ticker.")
    say("")
    say(f"`y_1306_oc` NaN count: {nan_1306} (expected 0).")
    say("")
    say("**Self-check (TOPIX).** The same harness with hedge = `y_topix_oc` on this panel reproduces both TOPIX tables of "
        f"the committed `reports/A_hedge_efficiency.md` cell for cell: decision table {dec_ok}; own-rows table {own_ok}.")
    say("")
    say("## (a) 1306: each window on its own rows")
    say("")
    say(fmt_tab(v13, n13))
    say("")
    say("## (b) DECISION TABLE, 1306: all windows on common rows")
    say("")
    say(fmt_tab(cv13, cn13))
    say("")
    say("Common rows per ticker: " + ", ".join(f"{t} {n}" for t, n in common_n.items()) + ".")
    say("")
    say(f"- Lowest variance among windows is `expanding` for ({', '.join(A7.TICKERS)}): {low}.")
    say("  **" + ("PASS (D9): expanding is the lowest-variance window on common rows for all three tickers." if all(low)
                  else "STOP (D9): expanding is NOT lowest on common rows for every ticker; flag for Isaiah.") + "**")
    say("")
    say("## Blinding")
    say("Target-only statistics (variances of hedged and unhedged open-to-close returns) on dev. No predictor column was "
        "loaded; nothing relates a predictor to a target.")
    text = "\n".join(out) + "\n"
    (ROOT / "reports" / "A_hedge_efficiency_1306.md").write_text(text, encoding="utf-8")
    print(text)
    return 0 if all(low) and nan_1306 == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
