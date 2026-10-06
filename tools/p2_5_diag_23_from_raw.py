"""P2-5, check 2.3 diagnostic (run after the 2.3 STOP; HEDGE-ONLY and GAP-ONLY, dev): recompute
ln(open_t / (close_{t-1} - D_t)) on the 7 dev 1306 ex-dates from the hash-verified raw 1306 sheet and its stored
distributions, and compare with the panel's ao_1306_gap_adj.

Saved on 2026-10-05 (supervisor message after the P2-5 report, item 1a) from the inline command whose output
is /tmp/p2_0/p2_5_23_raw.out; the code below is that command's, statement for statement. Run from the
repository root. The resolution is in reports/P2_5_resolutions.md.
"""
import hashlib, json, os
from pathlib import Path
import numpy as np, pandas as pd
FX = Path(os.environ["HOME"]) / "Desktop/FX_Project"
reg = json.load(open("docs/PASS2_INPUTS.json"))["inputs"]
fixed = FX / "raw" / "newbloombergdata_fixed.xlsx"
ok = hashlib.sha256(fixed.read_bytes()).hexdigest() == reg["newbloombergdata_fixed.xlsx"]["sha256"]
print("newbloombergdata_fixed.xlsx hashes to PASS2_INPUTS.json:", ok)
assert ok
P = FX / "build_out/p2_20261006T002928Z"
m = json.loads((P / "MANIFEST.json").read_text())
print("panel_dev.csv hashes to MANIFEST:", hashlib.sha256((P / "panel_dev.csv").read_bytes()).hexdigest() == m["outputs"]["panel_dev.csv"]["sha256"])
wb = pd.read_excel(fixed, sheet_name=["1306", "1306 dividends"], header=None)
px = wb["1306"].copy(); px.columns = ["date", "open", "close", "high", "low"]; px["date"] = pd.to_datetime(px["date"]); px = px.set_index("date").sort_index()
dv = wb["1306 dividends"].copy(); dv.columns = ["declared", "ex", "record", "pay", "amount", "freq", "type"]
D = dv.assign(ex=pd.to_datetime(dv["ex"])).groupby("ex")["amount"].sum()
pan = pd.read_csv(P / "panel_dev.csv", usecols=["date", "ticker", "ao_1306_gap_adj"], dtype={"ticker": str}).groupby("date").first()
print("| Ex-date | from raw: ln(open/(prev close - D)) in % | panel ao_1306_gap_adj in % | equal (to 1e-12) |")
allok = True
for x in ["2015-07-08", "2016-07-06", "2017-07-06", "2018-07-06", "2019-07-08", "2020-07-09", "2021-07-08"]:
    t = pd.Timestamp(x); k = px.index.get_loc(t)
    v = float(np.log(px.open.iloc[k] / (px.close.iloc[k - 1] - D[t])))
    p = float(pan.loc[x, "ao_1306_gap_adj"])
    eq = abs(v - p) <= 1e-12
    allok &= eq
    print(f"| {x} | {100 * v:+.4f} | {100 * p:+.4f} | {eq} |")
print("panel equals the independent recomputation on all 7 ex-dates:", allok)
