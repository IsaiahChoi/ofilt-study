"""P3-0b (supervisor message of 2026-10-06): tests of tools/p3_0b_preflight.py. Synthetic only; no data are read.

1. The Part A sample rule keeps exactly the (date, ticker) rows of inference.build_design on synthetic panels with
   injected exclusions and missing values (beta, predictors, the target).
2. The grid detector on hand-built price series with known grids, including a grid change mid-sample.
3. The tool refuses a panel whose SHA-256 does not match the registry, before reading it."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import p3_0b_preflight as P  # noqa: E402
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
    first = df.groupby("ticker").cumcount() < 25                    # beta warm-up: NaN on each ticker's first rows
    df.loc[first | (rng.random(n) < 0.02), "beta"] = np.nan
    dates = df["date"].unique()
    for c in nan_cols:
        if c in ("usdjpy_ret", "eurusd_ret"):                       # FX is per date: missing on every ticker row
            gone = rng.choice(dates, size=5, replace=False)
            df.loc[df["date"].isin(gone), c] = np.nan
        else:
            df.loc[rng.random(n) < 0.02, c] = np.nan
    return df


class TestP30bPreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = Spec.load()

    def test_sample_rule_equals_build_design(self):
        frames = {
            "excl+beta+usdjpy+spy+abn": injected(320, 11, 0.05, ["usdjpy_ret", "spy_oc", "abn_oc"]),
            "t5 excl+beta+eurusd+copx": injected(260, 12, 0.10, ["eurusd_ret", "copx_oc"], tails="t5"),
            "heavy excl+beta+all four": injected(400, 13, 0.25, ["usdjpy_ret", "eurusd_ret", "spy_oc", "copx_oc"]),
        }
        for name, df in frames.items():
            with self.subTest(frame=name):
                keep = P.sample_keep(df, self.spec)
                self.assertTrue(0 < int(keep.sum()) < len(df))                  # the injections bite
                d = I.build_design(df, self.spec)                               # synthetic provenance
                self.assertTrue(np.array_equal(df.index[keep.to_numpy()], d.index))
                rule_rows = df.loc[keep, ["date", "ticker"]].reset_index(drop=True)
                design_rows = df.loc[d.index, ["date", "ticker"]].reset_index(drop=True)
                pd.testing.assert_frame_equal(rule_rows, design_rows)
                self.assertTrue(P.sample_steps(df, self.spec)[-1][1].equals(keep))
                self.assertEqual(int(keep.sum()), len(d.y))
                self.assertEqual(df.loc[keep, "date"].nunique(), d.T)          # T_source = unique kept dates

    def test_grid_detector(self):
        self.assertEqual(P.detect_grid(np.array([101.0, 203.0, 305.0, 1007.0, 2009.0])), (1.0, 1.0))
        halves = np.arange(3400, 3600, 5) / 10.0                                 # 340.0, 340.5, ... (float noise)
        self.assertEqual(P.detect_grid(halves), (0.5, 0.5))
        self.assertEqual(P.detect_grid(np.arange(1, 50) * 20.0)[0], 20.0)
        near = np.r_[5.0 * (2 * np.arange(995) + 1), [1001.0, 1002.0, 1003.0, 1004.0, 1006.0]]
        self.assertEqual(P.detect_grid(near), (1.0, 5.0))                        # 99.5% on 5, all on 1
        self.assertEqual(P.detect_grid(np.array([0.123, 0.456, 0.789])), (None, None))
        self.assertEqual(P.grid_shares(np.array([2.0, 4.0, 5.0, 7.0]))[2.0], 0.5)
        # Grid change mid-sample: 5711 on a 10-yen grid before 2016-09-28, on a 1-yen grid from then.
        dates = pd.bdate_range("2016-06-01", "2016-12-30")
        before = dates < pd.Timestamp("2016-09-28")
        rng = np.random.default_rng(5)
        o = np.where(before, 10.0 * rng.integers(250, 400, len(dates)), 1.0 * rng.integers(2500, 4000, len(dates)))
        c = np.where(before, 10.0 * rng.integers(250, 400, len(dates)), 1.0 * rng.integers(2500, 4000, len(dates)))
        px = pd.DataFrame({"date": dates, "ticker": "5711", "open": o, "close": c})
        cells = {(r["year"], r["period"]): r["grid"] for r in P.grid_table(px)}
        self.assertEqual(cells, {(2016, "before 2016-09-28"): 10.0, (2016, "from 2016-09-28"): 1.0})
        self.assertEqual(P.detect_grid(np.r_[o, c])[0], 1.0)                    # pooled: the finer grid

    def test_refuses_unregistered_panel(self):
        with tempfile.TemporaryDirectory() as t:
            fake, out = Path(t) / "panel_dev.csv", Path(t) / "out.md"
            fake.write_text("date,ticker\n2015-01-05,5706\n", encoding="utf-8")
            with mock.patch.object(IO, "load_dev", side_effect=AssertionError("panel read")) as ld:
                with self.assertRaises(SystemExit) as cm:
                    P.main(["--panel", str(fake), "--out", str(out)])
            self.assertTrue(str(cm.exception.code).startswith("REFUSED"))
            ld.assert_not_called()
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
