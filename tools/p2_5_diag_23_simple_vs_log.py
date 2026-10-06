"""P2-5, check 2.3 diagnostic (run after the 2.3 STOP; GAP-ONLY, dev): do log gaps or simple returns
exp(g) - 1 reproduce the supervisor's reference table on the 7 dev 1306 ex-dates?

Saved on 2026-10-05 (supervisor message after the P2-5 report, item 1a) from the inline command whose output
is /tmp/p2_0/p2_5_23_diag.out; the code below is that command's, statement for statement. Run from the
repository root. Reads only date, ticker, ao_1306_gap_adj and ao_topix_gap from the P2-4 dev panel after
checking its hash against MANIFEST.json. The resolution is in reports/P2_5_resolutions.md.
"""
import hashlib, json, os, sys
from pathlib import Path
import numpy as np, pandas as pd
P = Path(os.environ["HOME"]) / "Desktop/FX_Project/build_out/p2_20261006T002928Z"
m = json.loads((P / "MANIFEST.json").read_text())
h = hashlib.sha256((P / "panel_dev.csv").read_bytes()).hexdigest()
print("panel_dev.csv hashes to MANIFEST:", h == m["outputs"]["panel_dev.csv"]["sha256"])
cols = ["date", "ticker", "ao_1306_gap_adj", "ao_topix_gap"]
d = pd.read_csv(P / "panel_dev.csv", usecols=cols, dtype={"ticker": str})
assert set(d.columns) == set(cols)
d = d.groupby("date").first()
sup = {"2015-07-08": (-0.30, -0.41), "2016-07-06": (-1.63, -1.55), "2017-07-06": (0.00, -0.04), "2018-07-06": (0.79, 0.55),
       "2019-07-08": (-0.16, -0.26), "2020-07-09": (-0.13, -0.09), "2021-07-08": (-0.21, -0.15)}
print("Diagnostic (gap-only, dev): log gaps (as stored) and simple returns exp(g)-1, in % to 2 decimals")
print("| Ex-date | 1306 log | 1306 simple | TOPIX log | TOPIX simple | supervisor (1306 / TOPIX) | 1306 simple = sup | TOPIX log = sup |")
all13, alltp = True, True
for x, (s13, stp) in sup.items():
    a, t = d.loc[x, "ao_1306_gap_adj"], d.loc[x, "ao_topix_gap"]
    a_l, a_s, t_l, t_s = 100 * a, 100 * np.expm1(a), 100 * t, 100 * np.expm1(t)
    e13, etp = round(a_s, 2) == s13, round(t_l, 2) == stp
    all13 &= e13; alltp &= etp
    print(f"| {x} | {a_l:+.2f} | {a_s:+.2f} | {t_l:+.2f} | {t_s:+.2f} | {s13:+.2f} / {stp:+.2f} | {e13} | {etp} |")
print("1306 simple returns reproduce the supervisor's 1306 column on all 7 dates:", all13)
print("TOPIX log gaps reproduce the supervisor's TOPIX column on all 7 dates:", alltp)
simple_max = max(abs(round(100 * np.expm1(d.loc[x, 'ao_1306_gap_adj']), 2) - round(100 * d.loc[x, 'ao_topix_gap'], 2)) for x in sup)
print(f"largest |1306 simple - TOPIX log| at 2 decimals: {simple_max:.2f} pp")
