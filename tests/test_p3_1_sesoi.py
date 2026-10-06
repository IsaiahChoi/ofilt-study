"""P3-1 (supervisor message of 2026-10-06): tests of tools/p3_1_sesoi.py. Synthetic only; no data are read.

1. The FWL residual: the tool's e~ equals the residual of the usdjpy_ret column on the other columns of
   inference.build_design(df, spec)'s design matrix (Design attributes used: X, names, index, col), on identical rows.
2. Tick tables and price factors: band edges, the factor and table on the day before and on each change date, and a
   refusal above a table's last bound.
3. The conformity check: hand-built series on and off the grid.
4. The cost arithmetic: round trips and SESOI equal a hand computation for primary, low and high.
5. Refusals: a panel whose hash does not match the registry; a cost file with a missing key."""
import json
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import p3_1_sesoi as T  # noqa: E402
from p3_0b_preflight import sample_keep  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402


def injected(n_dates, seed, p_excl, nan_cols, tails="gaussian"):
    """synthetic_panel with news_flag exclusions, a beta warm-up and scattered NaNs injected."""
    df = S.synthetic_panel(n_dates, seed=seed, p_excl=p_excl, tails=tails)
    rng = np.random.default_rng(seed + 1)
    n = len(df)
    df.loc[rng.random(n) < 0.03, "news_flag"] = 1
    df["beta"] = df["beta"].astype(float)
    df.loc[(df.groupby("ticker").cumcount() < 25) | (rng.random(n) < 0.02), "beta"] = np.nan
    dates = df["date"].unique()
    for c in nan_cols:
        if c in ("usdjpy_ret", "eurusd_ret"):                       # FX is per date
            df.loc[df["date"].isin(rng.choice(dates, size=5, replace=False)), c] = np.nan
        else:
            df.loc[rng.random(n) < 0.02, c] = np.nan
    return df


def ht(t, p):
    """Half a tick in bp, by hand."""
    return 1e4 * 0.5 * t / p


class TestP31Sesoi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = Spec.load()
        cls.inputs = T.load_inputs()                                    # docs/P3_COST_INPUTS.json (not data)

    def test_fwl_residual(self):
        frames = [injected(320, 21, 0.05, ["usdjpy_ret", "spy_oc", "abn_oc"]),
                  injected(260, 22, 0.10, ["eurusd_ret", "copx_oc"], tails="t5"),
                  injected(400, 23, 0.25, ["usdjpy_ret", "eurusd_ret", "spy_oc", "copx_oc"])]
        for k, df in enumerate(frames):
            with self.subTest(frame=k):
                keep = sample_keep(df, self.spec)
                e, names = T.partial_e(df, self.spec, keep)
                d = I.build_design(df, self.spec)                       # synthetic provenance
                self.assertTrue(np.array_equal(e.index.to_numpy(), d.index))          # identical rows
                self.assertTrue(np.array_equal(df.loc[e.index, ["date", "ticker"]].to_numpy(),
                                               df.loc[d.index, ["date", "ticker"]].to_numpy()))
                j = d.col("usdjpy_ret")
                others = [i for i in range(len(d.names)) if i != j]
                self.assertEqual(names, [d.names[i] for i in others])
                y, X = d.X[:, j], d.X[:, others]
                r = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
                self.assertLess(float(np.max(np.abs(e.to_numpy() - r))), 1e-10)

    def test_tick_tables_and_factors(self):
        tb = {k: v["rows"] for k, v in self.inputs["tick_tables"].items() if not k.startswith("_")}
        edges = {  # traded price -> tick, per table
            "standard": {1000: 1, 1000.5: 1, 3000: 1, 3001: 5, 5000: 5, 5010: 10, 10000: 10, 30000: 10},
            "topix100_phase2": {1000: 0.1, 1000.5: 0.5, 3000: 0.5, 3001: 0.5, 5000: 0.5, 5010: 1, 10000: 1},
            "fine": {1000: 0.1, 1000.5: 0.5, 3000: 0.5, 3001: 1, 5000: 1, 5010: 1, 10000: 1, 10001: 5, 30000: 5},
        }
        for name, cases in edges.items():
            for p, t in cases.items():
                self.assertEqual(T.tick(tb[name], p), t, (name, p))
        for name, above in (("standard", 30000.5), ("topix100_phase2", 10000.5), ("fine", 30001)):
            with self.assertRaises(ValueError):
                T.tick(tb[name], above)
        for tkr, day, before, after in (("5711", "2016-09-28", Fraction(10), Fraction(1)),
                                        ("5713", "2017-09-27", Fraction(2), Fraction(1)),
                                        ("5706", "2017-09-27", Fraction(1), Fraction(1, 10))):
            prev = (pd.Timestamp(day) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            self.assertEqual(T.factor(self.inputs, tkr, prev), before)
            self.assertEqual(T.factor(self.inputs, tkr, day), after)
        self.assertEqual(T.dev_table(self.inputs, "5713", "2015-09-23"), "topix100_phase2")
        self.assertEqual(T.dev_table(self.inputs, "5713", "2015-09-24"), "fine")
        self.assertEqual({T.dev_table(self.inputs, t, "2019-01-04") for t in ("5711", "5706")}, {"standard"})
        self.assertEqual(T.traded(np.array([3830.0]), Fraction(10))[0], 383.0)
        self.assertEqual(T.traded(np.array([304.5]), Fraction(1, 10))[0], 3045.0)

    def test_conformity(self):
        self.assertEqual(list(T.conforms(np.array([383.0, 3045.0, 993.1, 1250.5, 3047.0]),
                                         np.array([1.0, 5.0, 0.1, 0.5, 5.0]))), [True, True, True, True, False])
        px = pd.DataFrame({"date": pd.to_datetime(["2016-06-01", "2016-06-02", "2018-01-10", "2018-01-11"]),
                           "ticker": ["5711", "5711", "5706", "5706"],
                           "open": [3830.0, 3835.0, 305.5, 305.3],      # 383.5 off the 1-yen grid; 3053 off 5
                           "close": [3850.0, 3840.0, 120.3, 120.3]})
        st = T.side_ticks(px, self.inputs, None)
        on = {s: T.conforms(st[s][0], st[s][1]) for s in T.SIDES}
        self.assertEqual(list(on["open"]), [True, False, True, False])
        self.assertEqual(list(on["close"]), [True, True, True, True])
        big = px.assign(close=[3850.0, 3840.0, 3500.0, 120.3])           # 5706: traded 35,000 > 30,000
        self.assertTrue(T.side_ticks(big, self.inputs, None)["close"][2][2])

    def test_cost_arithmetic(self):
        px = pd.DataFrame({
            "date": pd.to_datetime(["2016-06-01", "2017-03-01", "2018-01-10", "2015-03-02", "2016-05-02"]),
            "ticker": ["5711", "5711", "5706", "5713", "5706"],
            "open": [3830.0, 3005.0, 305.5, 1000.4, 200.0],
            "close": [3850.0, 2999.0, 120.3, 2500.0, 210.0],
            "beta": [0.9, 1.1, 0.8, 1.2, 1.0]})
        beta = px["beta"].to_numpy()
        bbar = beta.mean()
        # Traded prices and ticks by hand. Rows 0 (5711) and 4 (5706) are in the Flag 4 windows.
        # primary (fine table), rows outside the windows: x_m = mean over sides of max(2, half tick)
        xm = {"5711": np.mean([max(2, ht(1, 3005)), max(2, ht(0.5, 2999))]),
              "5706": np.mean([max(2, ht(1, 3055)), max(2, ht(0.5, 1203))]),
              "5713": np.mean([max(2, ht(0.1, 500.2)), max(2, ht(0.5, 1250))])}
        rt_p = np.array([2 * (4.3 + xm[t]) + b * 2 * (4.3 + 1.5) for t, b in zip(px["ticker"], beta)])
        rt_l = np.array([2 * (0 + 0.5) + b * 2 * (0 + 0.5) + 0 for b in beta])
        # high (dev tables): x_m per row = 8 + mean over the row's sides of the half tick
        xh_rows = 8 + 0.5 * np.array([ht(1, 383) + ht(1, 385), ht(5, 3005) + ht(1, 2999), ht(5, 3055) + ht(1, 1203),
                                      ht(0.1, 500.2) + ht(0.5, 1250), ht(1, 200) + ht(1, 210)])
        rt_h = 2 * (8 + xh_rows) + beta * 2 * (8 + 8.2) + 1
        cc = T.costs(px, self.inputs)
        mean_abs_e = 37.5
        for case, rt in (("primary", rt_p), ("low", rt_l), ("high", rt_h)):
            r = cc[case]
            self.assertAlmostEqual(r["mean_rt"], rt.mean(), places=12)
            self.assertAlmostEqual(r["mean_rt"] / mean_abs_e, rt.mean() / mean_abs_e, places=12)
            parts = r["miner_commission"] + r["miner_execution"] + r["hedge_leg"] + r["short"]
            self.assertAlmostEqual(parts, r["mean_rt"], places=12)
            rt_at_bbar = 2 * (r["c_m"] + r["miner_execution"] / 2) + bbar * 2 * (r["c_h"] + r["x_h"]) + r["s"]
            self.assertLess(abs(rt_at_bbar - r["mean_rt"]), 1e-12)        # mean RT = RT at beta-bar
        self.assertEqual(cc["detail"]["primary_rows"], {"5706": 1, "5711": 1, "5713": 1})
        self.assertEqual(cc["detail"]["primary_xm"]["5711"], 2.0)          # the floor binds
        self.assertGreater(cc["detail"]["primary_xm"]["5706"], 2.0)        # 1/2 tick 2.078 bp > 2 on one side
        self.assertEqual(cc["detail"]["primary_share"], {"5706": 0.5, "5711": 0.0, "5713": 0.0})
        moved = px.assign(open=px["open"] * 1.5, close=px["close"] * 1.5)   # low: no tick term
        self.assertEqual(T.costs(moved, self.inputs)["low"]["miner_execution"], cc["low"]["miner_execution"])
        self.assertAlmostEqual(cc["high"]["miner_execution"], float(np.mean(2 * xh_rows)), places=12)  # additive

    def test_refusals(self):
        with tempfile.TemporaryDirectory() as t:
            fake, out = Path(t) / "panel_dev.csv", Path(t) / "out.md"
            fake.write_text("date,ticker\n2015-01-05,5706\n", encoding="utf-8")
            with mock.patch.object(IO, "load_dev", side_effect=AssertionError("panel read")) as ld:
                with self.assertRaises(SystemExit) as cm:
                    T.main(["--panel", str(fake), "--out", str(out)])
            self.assertTrue(str(cm.exception.code).startswith("REFUSED"))
            ld.assert_not_called()
            obj = json.loads(T.INPUTS_PATH.read_text(encoding="utf-8"))
            for key in ("impact_miners_bp", "tick_tables", "flag4_windows"):
                bad = Path(t) / f"inputs_without_{key}.json"
                bad.write_text(json.dumps({k: v for k, v in obj.items() if k != key}), encoding="utf-8")
                with mock.patch.object(T, "verify_panel", side_effect=AssertionError("panel hashed")) as vp, \
                        mock.patch.object(IO, "load_dev", side_effect=AssertionError("panel read")) as ld:
                    with self.assertRaises(SystemExit) as cm:
                        T.main(["--inputs", str(bad), "--panel", str(fake), "--out", str(out)])
                self.assertIn(key, str(cm.exception.code))
                self.assertTrue(str(cm.exception.code).startswith("REFUSED"))
                vp.assert_not_called()
                ld.assert_not_called()
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
