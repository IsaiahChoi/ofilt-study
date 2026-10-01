"""A7: beta-window hedge efficiency. TARGET-ONLY: reads y_oc, y_topix_oc and the
two exclusion flags; no FX column is ever loaded into the working frame.

(a) Isaiah's exact reference code (beta on ALL rows) vs targets.past_beta.
(b) targets.past_beta with beta estimated on non-excluded rows only.
Evaluation rows (both parts): date >= 2017-01-01, earn_flag == 0, news_flag == 0;
value = var(y - beta*m) * 1e8 with pandas default ddof=1, NaN beta skipped
(exactly as the reference code does; matters for w = 500, see report).

usage: python tools/report_A7.py   -> writes reports/A_hedge_efficiency.md, exits 1 on any failure
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

COLS = ["date", "ticker", "y_oc", "y_topix_oc", "earn_flag", "news_flag"]
WINDOWS = [60, 120, 250, 500, "expanding", "none"]
TICKERS = ["5706", "5711", "5713"]
PROMPT_TABLE = {  # bp^2, from the Pass 1 prompt
    60: [24619, 11888, 18127], 120: [24406, 11753, 17952], 250: [24483, 11747, 17955],
    500: [24133, 11699, 17818], "expanding": [24052, 11662, 17750], "none": [29603, 15855, 22955]}
TOL_PROMPT, TOL_IMPL = 0.005, 1e-9


def load() -> pd.DataFrame:
    d = IO.load_dev()[COLS].copy()
    assert not [c for c in d.columns if c.startswith(("usdjpy", "eurusd"))]
    d.attrs["provenance"] = "dev_real"
    return d


def reference_beta(d: pd.DataFrame, w) -> pd.Series:
    """Isaiah's code, verbatim in substance: per ticker, date-indexed, ALL rows."""
    out = pd.Series(np.nan, index=d.index)
    for t in TICKERS:
        s = d[d.ticker == t].set_index("date")
        y, m = s.y_oc, s.y_topix_oc
        R = (lambda z: z.rolling(w)) if w != "expanding" else (lambda z: z.expanding(250))
        c = R(y * m).mean() - R(y).mean() * R(m).mean()
        v = R(m).var(ddof=0)
        out.loc[d.ticker == t] = (c / v).shift(1).to_numpy()
    return out


def impl_beta(d: pd.DataFrame, w, eligible=None) -> pd.Series:
    if w == "expanding":
        return TG.past_beta(d, method="expanding", min_periods=250, eligible=eligible)
    return TG.past_beta(d, method="rolling", window=w, eligible=eligible)


def keep_mask(d):
    return (d.date >= "2017-01-01") & (d.earn_flag == 0) & (d.news_flag == 0)


def reported(d, b, t):
    k = keep_mask(d) & (d.ticker == t)
    r = (d.y_oc - b * d.y_topix_oc)[k]
    return float(r.var() * 1e8), int(r.notna().sum())


def table(d, beta_fn):
    vals, ns = {}, {}
    for w in WINDOWS:
        b = pd.Series(0.0, index=d.index) if w == "none" else beta_fn(d, w)
        res = [reported(d, b, t) for t in TICKERS]
        vals[w], ns[w] = [r[0] for r in res], [r[1] for r in res]
    return vals, ns


def lowest_is_expanding(vals) -> list[bool]:
    cand = [60, 120, 250, 500, "expanding"]
    return [min(cand, key=lambda w: vals[w][j]) == "expanding" for j in range(3)]


def main() -> int:
    d = load()
    spec = Spec.load()
    ok = True
    # --- (a)
    ref_v, ref_n = table(d, reference_beta)
    imp_v, imp_n = table(d, impl_beta)
    beta_diff, nan_same = 0.0, True
    for w in WINDOWS[:-1]:
        rb, ib = reference_beta(d, w), impl_beta(d, w)
        nan_same &= bool((rb.isna() == ib.isna()).all())
        beta_diff = max(beta_diff, float((rb - ib).abs().max()))
    impl_rel = max(abs(imp_v[w][j] / ref_v[w][j] - 1) for w in WINDOWS for j in range(3))
    prompt_rel = {w: [ref_v[w][j] / PROMPT_TABLE[w][j] - 1 for j in range(3)] for w in WINDOWS}
    prompt_ok = all(abs(x) < TOL_PROMPT for v in prompt_rel.values() for x in v)
    impl_ok = nan_same and impl_rel < TOL_IMPL and ref_n == imp_n
    ok &= prompt_ok and impl_ok
    # --- (b)
    elig = ~TG.exclusion_mask(d, spec)
    b_v, b_n = table(d, lambda dd, w: impl_beta(dd, w, eligible=elig))
    low_a, low_b = lowest_is_expanding(imp_v), lowest_is_expanding(b_v)
    b_ok = all(low_b)
    # DIAGNOSTIC (not the A7 criterion): every window on the SAME rows (all betas available)
    bb = {w: impl_beta(d, w, eligible=elig) for w in WINDOWS[:-1]}
    common = keep_mask(d) & pd.concat(bb.values(), axis=1).notna().all(axis=1)
    c_v, c_n = {}, {}
    for w in WINDOWS:
        b = pd.Series(0.0, index=d.index) if w == "none" else bb[w]
        res = [reported(d.assign(y_oc=d.y_oc.where(common)), b, t) for t in TICKERS]
        c_v[w], c_n[w] = [r[0] for r in res], [r[1] for r in res]
    low_c = lowest_is_expanding(c_v)
    exact = beta_diff == 0.0 and impl_rel == 0.0

    def fmt_tab(vals, ns=None, ref=None):
        lines = ["| window | " + " | ".join(TICKERS) + " |", "|---|---|---|---|"]
        for w in WINDOWS:
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

    md = f"""# A7: hedge efficiency of past-only beta windows (dev, target-only)

Generated by `tools/report_A7.py` from `panel_dev.csv` (SHA-256 verified on load). Reads only
{", ".join(f"`{c}`" for c in COLS)}; no FX column is loaded into the working frame.

**Evaluation rows (both parts):** date >= 2017-01-01, earn_flag == 0, news_flag == 0, per ticker.
**Value:** var(y_oc - beta * y_topix_oc) x 1e8 (bp^2), pandas default ddof = 1, rows with NaN beta
skipped (as in the reference code). `none` = var(y_oc) on the same rows. Beta lag = 1 day.

**Note on w = 500.** Dev has 488 rows per ticker before 2017-01-01, so rolling-500 beta is first
available on the 501st row: the first 12 evaluation-period rows have no beta and are skipped. The
500 row therefore averages over slightly fewer (early-2017) days than the others; `n` is shown.

## (a) Beta on ALL rows: Isaiah's reference code vs `targets.past_beta`

Reference code: per ticker, date-indexed, `c = (y*m).R.mean() - y.R.mean()*m.R.mean()`,
`v = m.R.var(ddof=0)`, `b = (c/v).shift(1)`, with R = `rolling(w)` or `expanding(250)`.

Reproduced values vs the prompt's table (percent difference in parentheses):

{fmt_tab(ref_v, ref_n, PROMPT_TABLE)}

- Within 0.5% of the prompt's table in every cell: **{"PASS" if prompt_ok else "FAIL"}**
  (max |diff| {100 * max(abs(x) for v in prompt_rel.values() for x in v):.3f}%; the prompt's values are rounded to integers).
- `targets.past_beta` vs reference: NaN pattern identical: **{nan_same}**; max |beta difference|
  {beta_diff:.2e}; max relative difference of reported variances {impl_rel:.2e} (tolerance {TOL_IMPL:g});
  identical row counts: **{ref_n == imp_n}**. {"Bit-identical on every row" if exact else "Equal to floating-point accuracy"}: **{"PASS" if impl_ok else "FAIL"}**.
- Lowest variance among windows is `expanding` for (5706, 5711, 5713): {low_a}.

## (b) Beta on non-excluded rows only (spec `estimate_on: non_excluded_rows`)

`targets.past_beta(..., eligible = ~excl_inference)`; rolling windows are the last w eligible rows.
Percent differences in parentheses are relative to part (a).

{fmt_tab(b_v, b_n, imp_v)}

- Lowest variance among windows is `expanding` for (5706, 5711, 5713): {low_b}.
  **{"PASS: the spec's expanding beta remains the lowest-variance choice for all three tickers." if all(low_b) else "STOP: expanding is NOT lowest for every ticker; flagged for Isaiah, spec unchanged."}**

## (b') DIAGNOSTIC, not the A7 criterion: all windows on common rows

Same as (b), but every window is evaluated on the same rows: evaluation rows on which ALL five
betas exist (drops the early-2017 rows where the eligible-row 500 window has no beta yet). Shown
only to separate a sample-composition effect from a genuine ranking change; the A7 decision rule
above is unchanged.

{fmt_tab(c_v, c_n)}

- Lowest variance among windows is `expanding` for (5706, 5711, 5713) on common rows: {low_c}.

## Blinding
Target-only statistics (variances of hedged and unhedged open-to-close returns). Permitted under
rule 2; no coefficient, correlation or other quantity involving any FX column was computed.
"""
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "A_hedge_efficiency.md").write_text(md, encoding="utf-8")
    print(md)
    print("(a):", "PASS" if ok else "FAIL", "| (b):", "PASS" if b_ok else "STOP (flagged)",
          "| (b') expanding lowest on common rows:", low_c)
    return 0 if (ok and b_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
