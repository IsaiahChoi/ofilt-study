"""P2-5 D8 tick-grid check: 1306 HEDGE PRICES ONLY, dev (supervisor message of 2026-10-05 after the P2-5 report,
item 4). Do the 84 dev dates with ao_1306_gap_raw == 0 (4.92%) reflect tick discreteness, or excess opens at
the previous close?

a. newbloombergdata_fixed.xlsx is verified against docs/PASS2_INPUTS.json before it is read. From its `1306`
   sheet only the dates, opens and closes are used, filtered to dev dates (< 2022-01-01) before any statistic.
b. The price grid by year: the smallest positive |open_t - close_{t-1}|, and the share of |open_t - close_{t-1}|
   values that are integer multiples of it to within 1e-9. If that share is below 100% in any year, the modal
   smallest increment is used instead (said so in the output).
c. Counts of (open_t - close_{t-1}) at -2, -1, 0, +1, +2 grid steps, by year and in total; R = count(0) /
   mean(count(+1), count(-1)), overall and by year. Reading rule (fixed by Isaiah on 2026-10-05 before this
   script ran): "no excess opens at the previous close" if R <= 1.5 overall; otherwise flag for D8.
d. The dev count at 0 steps must equal 84 (check 2.3).
Prints grid sizes, shares, counts and R only; no price level. usage: python tools/p2_5_tick_1306.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIXED = Path(os.environ["HOME"]) / "Desktop" / "FX_Project" / "raw" / "newbloombergdata_fixed.xlsx"
SPLIT = pd.Timestamp("2022-01-01")
TOL = 1e-9
R_MAX = 1.5
ZERO_GAP_DATES_2_3 = 84
STEPS = (-2, -1, 0, 1, 2)


def main() -> int:
    reg = json.loads((ROOT / "docs" / "PASS2_INPUTS.json").read_text(encoding="utf-8"))["inputs"]
    ok = hashlib.sha256(FIXED.read_bytes()).hexdigest() == reg["newbloombergdata_fixed.xlsx"]["sha256"]
    print(f"newbloombergdata_fixed.xlsx hashes to PASS2_INPUTS.json: {ok}")
    if not ok:
        print("STOP: input hash mismatch")
        return 2
    s = pd.read_excel(FIXED, sheet_name="1306", header=None, usecols=[0, 1, 2])
    s.columns = ["date", "open", "close"]                 # sheet layout: date, open, last, high, low
    s["date"] = pd.to_datetime(s["date"])
    s = s[s["date"] < SPLIT].sort_values("date").reset_index(drop=True)   # dev only, before any statistic
    diff = (s["open"] - s["close"].shift(1)).iloc[1:]
    year = s["date"].dt.year.iloc[1:]
    a = diff.abs()
    print(f"dev dates in the sheet: {len(s)} ({s['date'].iloc[0]:%Y-%m-%d} → {s['date'].iloc[-1]:%Y-%m-%d}); "
          f"open_t − close_(t−1) defined on {len(diff)} dates")
    print()
    print("b. price grid by year (smallest positive |open_t − close_(t−1)|; share of |differences| that are integer "
          f"multiples of it within {TOL:g})")
    print("| Year | smallest positive step | share on its grid |")
    print("|---|---|---|")
    grid, full = {}, True
    for y in sorted(year.unique()):
        ay = a[year == y]
        g = float(ay[ay > 0].min())
        share = float((np.abs(ay - np.round(ay / g) * g) <= TOL).mean())
        grid[y] = g
        full &= share == 1.0
        print(f"| {y} | {g:.10g} | {100 * share:.2f}% |")
    if not full:
        mins = pd.Series(grid).round(9)
        modal = float(mins.mode().iloc[0])
        print(f"The share is below 100% in some year: the modal smallest increment {modal:.10g} is used for every year.")
        grid = {y: modal for y in grid}
    else:
        print("Every year is fully on its own grid; each year's smallest step is used for that year.")
    print()
    k = pd.Series([round(float(d) / grid[y]) for d, y in zip(diff, year)], index=diff.index)
    on_grid = pd.Series([abs(float(d) - round(float(d) / grid[y]) * grid[y]) <= TOL for d, y in zip(diff, year)],
                        index=diff.index)
    print("c. counts of open_t − close_(t−1) in grid steps, and R = count(0) / mean(count(+1), count(−1))")
    print("| Period | dates | −2 | −1 | 0 | +1 | +2 | R |")
    print("|---|---|---|---|---|---|---|---|")
    rows = [(str(y), year == y) for y in sorted(year.unique())] + [("all dev", pd.Series(True, index=diff.index))]
    r_all = None
    for name, mask in rows:
        c = {st: int(((k == st) & mask).sum()) for st in STEPS}
        r = c[0] / ((c[1] + c[-1]) / 2) if (c[1] + c[-1]) > 0 else float("inf")
        if name == "all dev":
            r_all, c_all = r, c
        print(f"| {name} | {int(mask.sum())} | " + " | ".join(str(c[st]) for st in STEPS) + f" | {r:.3f} |")
    print(f"(every difference is on the grid used: {bool(on_grid.all())})")
    print()
    reading = "no excess opens at the previous close" if r_all <= R_MAX else "excess opens at the previous close: FLAG for D8"
    print(f"Reading (R ≤ {R_MAX} overall): R = {r_all:.3f} → {reading}")
    print(f"d. dev count at 0 steps = {c_all[0]}; equals {ZERO_GAP_DATES_2_3} (check 2.3): {c_all[0] == ZERO_GAP_DATES_2_3}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
