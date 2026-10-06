"""P3-2a (supervisor message of 2026-10-06): tests of ofilt/drift/calib.py. Synthetic only; no data file is read
(test 5 reads B7b's committed aggregates in reports/B7b_size_preview.json).

1. tost_declares with c = 1.644854 agrees with inference.tost on a grid, including both sides of each boundary.
2. fit_t equals fit_dk's coefficient and sqrt(cov) entry for usdjpy_ret and eurusd_ret; the lag is Spec.dk_lag(T);
   rejects(t, 1.959964) equals the normal two-sided 5% decision read from Result.param(name)["p"] < spec.alpha.
3. resample_dates: same number of dates; each output date's rows equal one source date's rows; provenance
   synthetic; reproducible; the mean run length of consecutive source dates within 10% of 5.
4. order_stat and order_stat_interval on hand-built examples, including n = 5,000 at 0.95 (k_lo 4,719, k_hi 4,781).
5. wilson and mde80 reproduce B7b's size interval and MDE80 from its committed aggregates.
6. winsorise_fx clips exactly at the spec's bounds, leaves other columns unchanged and is idempotent.
7. window_positions stays in [0, K).
8. Static: calib.py's import statements exclude multiprocessing, concurrent.futures, joblib, subprocess and
   pickle, and it contains no 'open('."""
import ast
import json
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import calib as C  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

KEY_COLS = ["ticker", "usdjpy_ret", "eurusd_ret", "spy_oc", "copx_oc", "abn_oc"]


class TestP3Calib(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = Spec.load()

    def test_1_tost_declares_matches_inference_tost(self):
        c = 1.644854
        for se in (0.01, 0.05, 0.2):
            for sesoi in (0.07152, 0.8652, 2.719):
                bounds = (-sesoi + c * se, sesoi - c * se)                   # the two boundaries in b
                grid = [0.0, -sesoi, sesoi, 3 * sesoi, -3 * sesoi]
                for bd in bounds:
                    grid += [bd - 1e-5 * se, bd + 1e-5 * se, bd - 0.1 * se, bd + 0.1 * se]
                for b in grid:
                    want = I.tost(b, se, sesoi, 0.05)["equivalent"]
                    self.assertEqual(bool(C.tost_declares(b, se, sesoi, c)), want, (b, se, sesoi))

    def test_2_fit_t_equals_fit_dk(self):
        for k, (b, seed, tails) in enumerate([(0.0, 31, "gaussian"), (0.05, 32, "t5"), (0.4, 33, "gaussian")]):
            df = S.synthetic_panel(1013, b=b, seed=seed, tails=tails, p_excl=0.03)
            with self.subTest(frame=k):
                f = C.fit_t(df, self.spec, "abn_oc")
                d = I.build_design(df, self.spec)
                r = I.fit_dk(d, self.spec)
                for name, kb, ks in (("usdjpy_ret", "b", "se"), ("eurusd_ret", "b_h3", "se_h3")):
                    j = r.names.index(name)
                    self.assertEqual(f[kb], float(r.coef[j]))
                    self.assertAlmostEqual(f[ks], float(np.sqrt(r.cov[j, j])), places=15)
                self.assertEqual(f["lag"], Spec.dk_lag(int(d.T)))
                self.assertEqual(f["T"], d.T)
                self.assertTrue(np.array_equal(f["index"], d.index))
                # the existing decision: Result.param(name)["p"] < spec.alpha (two-sided normal, inference.py:208-212)
                self.assertEqual(bool(C.rejects(f["t"], 1.959964)), r.param("usdjpy_ret")["p"] < self.spec.alpha)
                self.assertEqual(bool(C.rejects(f["t_h3"], 1.959964)), r.param("eurusd_ret")["p"] < self.spec.alpha)

    def test_3_resample_dates(self):
        df = S.synthetic_panel(1013, seed=41, p_excl=0.0)
        src_dates = np.sort(df["date"].unique())
        code_of = {round(float(v), 15): i for i, v in                     # usdjpy_ret is unique per source date
                   enumerate(df.groupby("date", sort=True)["usdjpy_ret"].first().to_numpy())}
        self.assertEqual(len(code_of), len(src_dates))
        by_date = {d: g[KEY_COLS].reset_index(drop=True) for d, g in df.groupby("date", sort=True)}
        out = C.resample_dates(df, np.random.default_rng(7))
        self.assertEqual(out["date"].nunique(), len(src_dates))
        self.assertEqual(B.provenance_of(out), B.SYNTHETIC)
        self.assertEqual(B.require_unblinded(out), B.SYNTHETIC)
        for d, g in out.groupby("date", sort=True):
            src = src_dates[code_of[round(float(g["usdjpy_ret"].iloc[0]), 15)]]
            pd.testing.assert_frame_equal(g[KEY_COLS].reset_index(drop=True), by_date[src])
        again = C.resample_dates(df, np.random.default_rng(7))
        pd.testing.assert_frame_equal(out, again)
        runs, n = 0, 0
        for s in range(60):
            o = C.resample_dates(df, np.random.default_rng(1000 + s))
            codes = np.array([code_of[round(float(v), 15)]
                              for v in o.groupby("date", sort=True)["usdjpy_ret"].first().to_numpy()])
            cont = (codes[1:] == (codes[:-1] + 1) % len(src_dates))
            runs += 1 + int((~cont).sum())
            n += len(codes)
        self.assertLess(abs(n / runs - 5.0), 0.5)                        # within 10% of 5

    def test_4_order_statistics(self):
        x = np.array([5.0, 1.0, 4.0, 2.0, 3.0])
        self.assertEqual(C.order_stat(x, 0.5), 3.0)                       # ceil(2.5) = 3rd smallest
        self.assertEqual(C.order_stat(x, 0.95), 5.0)                      # ceil(4.75) = 5th
        self.assertEqual(C.order_stat(x, 0.2), 1.0)                       # ceil(1.0) = 1st
        self.assertEqual(C.order_stat_ranks(5000, 0.95), (4750, 4719, 4781))
        self.assertEqual(C.order_stat_ranks(5000, 0.90)[0], 4500)
        self.assertEqual(C.order_stat_ranks(200, 0.95)[0], 190)
        v = np.arange(1, 5001, dtype=float)[::-1]                           # 1..5000, unsorted
        self.assertEqual(C.order_stat(v, 0.95), 4750.0)
        self.assertEqual(C.order_stat_interval(v, 0.95), (4719.0, 4781.0))
        self.assertEqual(C.order_stat_ranks(10, 0.5), (5, 1, 9))          # 5 -/+ 3.0990 -> floor 1, ceil 9
        with self.assertRaises(ValueError):
            C.order_stat_ranks(0, 0.95)

    def test_5_wilson_and_mde80_reproduce_b7b(self):
        d = json.loads((ROOT / "reports" / "B7b_size_preview.json").read_text(encoding="utf-8"))
        h1 = d["cells"][0]["reject_H1"]
        lo, hi = C.wilson(h1["k"], h1["n"])
        self.assertEqual((lo, hi), tuple(h1["wilson95"]))
        self.assertEqual((round(h1["k"] / h1["n"], 4), round(lo, 4), round(hi, 4)), (0.0604, 0.0541, 0.0673))
        bs = [0.0] + [c["b_sim"] for c in d["cells"][1:]]
        rates = [d["cells"][0]["reject_H1"]["rate"]] + [c["reject_H1"]["rate"] for c in d["cells"][1:]]
        pc = d["pooled_calibration"]["H1"]
        m = C.mde80(bs, rates, sd=pc["sd"], mean_se=pc["mean_se"])
        self.assertEqual(m, d["mde80"])
        self.assertEqual(round(m["probit_interpolated"], 3), 0.257)

    def test_6_winsorise_fx(self):
        df = S.synthetic_panel(300, seed=51, tails="t5")
        bounds = self.spec.winsor_bounds()
        (lo_u, hi_u), (lo_e, hi_e) = bounds["usdjpy_ret"], bounds["eurusd_ret"]
        df.loc[df.index[:3], "usdjpy_ret"] = [lo_u * 3, hi_u * 3, 0.0]     # force values beyond both bounds
        df.loc[df.index[3:6], "eurusd_ret"] = [lo_e * 2, hi_e * 2, 0.001]
        out = C.winsorise_fx(df, self.spec)
        for c, (lo, hi) in bounds.items():
            self.assertTrue(np.array_equal(out[c].to_numpy(), np.clip(df[c].to_numpy(), lo, hi)))
            self.assertEqual(float(out[c].min()), lo) if (df[c] < lo).any() else None
            self.assertEqual(float(out[c].max()), hi) if (df[c] > hi).any() else None
        others = [c for c in df.columns if c not in bounds]
        pd.testing.assert_frame_equal(out[others], df[others])
        pd.testing.assert_frame_equal(C.winsorise_fx(out, self.spec), out)
        self.assertEqual(B.provenance_of(out), B.SYNTHETIC)

    def test_7_window_positions(self):
        for K, n_out, seed in ((398, 1013, 1), (160, 1013, 2), (5, 50, 3), (1, 10, 4)):
            p = C.window_positions(K, n_out, np.random.default_rng(seed))
            self.assertEqual(p.shape, (n_out,))
            self.assertTrue(int(p.min()) >= 0 and int(p.max()) < K)

    def test_8_static_imports_and_no_open(self):
        src = (ROOT / "ofilt" / "drift" / "calib.py").read_text(encoding="utf-8")
        mods = set()
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add(n.module or "")
                mods |= {f"{n.module}.{a.name}" if n.module else a.name for a in n.names}
        banned = ("multiprocessing", "concurrent.futures", "concurrent", "joblib", "subprocess", "pickle")
        self.assertFalse([m for m in mods for b in banned if m == b or m.startswith(b + ".")], sorted(mods))
        self.assertNotIn("open(", src)


if __name__ == "__main__":
    unittest.main()
