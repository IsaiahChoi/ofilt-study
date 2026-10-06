"""P3-2d (supervisor message of 2026-10-06): test of tools/p3_2d_structural.py's frame builder. Synthetic only.

On sim.synthetic_panel frames with y_*, ao_*, open, close and prev_close columns and missing values injected, the
builder keeps exactly the stated columns, keeps the missing pattern of abn_oc and beta exactly, replaces their present
values by synthetic ones (abn_oc new values; beta 1.0), drops every y_* and ao_* column, and labels the frame synthetic.
"""
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import p3_2d_structural as T  # noqa: E402
from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402


class TestStructuralFrame(unittest.TestCase):
    def test_frame_builder(self):
        spec = Spec.load()
        want = ["date", "ticker", "earn_flag", "news_flag", "usdjpy_ret", "eurusd_ret", "spy_oc", "copx_oc", "beta",
                "abn_oc", "window_hours", "usdjpy_rv", "usdjpy_bv", "usdjpy_bars"]
        self.assertEqual(T.kept_columns(spec), want)
        for seed in (61, 62, 63):
            with self.subTest(seed=seed):
                df = S.synthetic_panel(200, seed=seed, p_excl=0.05)
                rng = np.random.default_rng(seed)
                df["beta"] = df["beta"].astype(float)
                df.loc[rng.random(len(df)) < 0.1, "beta"] = np.nan
                df.loc[rng.random(len(df)) < 0.1, "abn_oc"] = np.nan
                for c in ("y_oc", "y_1306_oc", "ao_gap_adj", "ao_1306_gap_adj", "open", "close", "prev_close"):
                    df[c] = rng.normal(size=len(df))
                out = T.build_structural_frame(df, spec, np.random.default_rng(1))
                self.assertEqual(list(out.columns), want)
                self.assertFalse([c for c in out.columns if c.startswith(("y_", "ao_"))])
                for c in ("open", "close", "prev_close", "y_topix_oc", "raw_oc"):
                    self.assertNotIn(c, out.columns)
                for c in ("abn_oc", "beta"):
                    self.assertTrue(np.array_equal(out[c].isna().to_numpy(), df[c].isna().to_numpy()), c)
                present = df["abn_oc"].notna().to_numpy()
                self.assertFalse(np.isin(out["abn_oc"].to_numpy()[present], df["abn_oc"].to_numpy()[present]).any())
                self.assertTrue((out["beta"].dropna() == 1.0).all())
                for c in want:
                    if c not in ("abn_oc", "beta"):
                        self.assertTrue(out[c].equals(df[c]), c)
                self.assertEqual(out.attrs, {"provenance": B.SYNTHETIC})


if __name__ == "__main__":
    unittest.main()
