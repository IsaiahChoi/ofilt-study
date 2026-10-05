"""C6 tests (synthetic only): permutation importance inside walk_forward, run registry."""
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import forecast as F  # noqa: E402
from ofilt.drift import registry as R  # noqa: E402
from ofilt.drift import schema  # noqa: E402
from ofilt.drift.models import M1, M2, M3, M5, M7  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402
from test_fctests_c5 import strong_panel  # noqa: E402
from test_models_c4 import full_panel  # noqa: E402


class TestDonorIndex(unittest.TestCase):
    def test_whole_date_permutation_within_ticker_sets(self):
        dates = pd.bdate_range("2030-01-07", periods=10)
        rows = [(d, t) for i, d in enumerate(dates) for t in ("5706", "5711", "5713")
                if not (t == "5711" and i in (2, 5, 8))]
        d = np.array([r[0] for r in rows], dtype="datetime64[ns]")
        t = np.array([r[1] for r in rows])
        don = F.donor_index(d, t, np.random.default_rng(1))
        self.assertEqual(sorted(don), list(range(len(rows))))                 # bijection on eval rows
        self.assertTrue((t[don] == t).all())                                  # same ticker
        sets = {x: frozenset(t[d == x]) for x in np.unique(d)}
        for x in np.unique(d):
            src = np.unique(d[don[d == x]])
            self.assertEqual(len(src), 1)                                     # the whole date moves
            self.assertEqual(sets[src[0]], sets[x])                           # same ticker set
        self.assertTrue((F.donor_index(d, t, np.random.default_rng(1)) == don).all())
        self.assertFalse((F.donor_index(d, t, np.random.default_rng(2)) == don).all())
        with self.assertRaises(ValueError):
            F.donor_index(np.r_[d, d[:1]], np.r_[t, t[:1]], np.random.default_rng(0))


class _Reg(unittest.TestCase):
    """Every walk_forward call here writes to a temporary registry."""
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls._patch = [mock.patch.object(R, "SYNTHETIC_PATH", Path(cls._tmp.name) / "synth.jsonl"),
                      mock.patch.object(R, "REAL_PATH", Path(cls._tmp.name) / "real.jsonl")]
        for p in cls._patch:
            p.start()
        cls.spec = Spec.load()

    @classmethod
    def tearDownClass(cls):
        for p in cls._patch:
            p.stop()
        cls._tmp.cleanup()


class TestImportanceLinear(_Reg):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.df = strong_panel(700, b=3.0)
        cls.preds, cls.folds = F.walk_forward(cls.df, {"M2": M2, "M3": M3}, cls.spec, importance=["M3"])

    def test_recorded_scores_and_independent_recompute(self):
        fl = self.folds
        self.assertTrue(fl[fl.model == "M2"].importance.isna().all())        # only the requested model
        f3 = fl[fl.model == "M3"].reset_index(drop=True)
        R_ = int(self.spec.value("forecast.importance.repeats"))
        for _, fr in f3.iterrows():
            imp = fr.importance
            self.assertEqual((set(imp["sse_perm"]), imp["repeats"], imp["noise_column"]), (set(M3.features), R_, None))
            self.assertTrue(all(len(v) == R_ for v in imp["sse_perm"].values()))
            g = self.preds[(self.preds.model == "M3") & (self.preds.fold == fr.fold)]
            self.assertAlmostEqual(imp["sse_base"], float(((g.y - g.yhat) ** 2).sum()), delta=1e-15)
        # independent recompute: fold 1, repeat 0, usdjpy_ret
        df, need = self.df, ["usdjpy_ret", "eurusd_ret", "spy_oc", "copx_oc"]
        ok = df.abn_oc.notna() & df[need].notna().all(axis=1)
        fr = f3.iloc[1]
        tr = ok & ~df.excl_inference & (df.date < fr.test_start)
        te = ok & ~df.excl_forecast_eval & (df.date >= fr.test_start) & (df.date <= fr.test_end)
        frame = lambda m: pd.concat([df.loc[m, ["date", "ticker"]], schema.select_features(df.loc[m], list(M3.features))],
                                    axis=1).reset_index(drop=True)
        ctx = F.FoldContext(fold=1, train_end=fr.train_end, test_start=fr.test_start, n_train_dates=fr.n_train_dates,
                            spec=self.spec, seed=self.spec.seed + 1000)
        m = M3(); m.fit(frame(tr), df.abn_oc[tr].to_numpy(), ctx)
        X = frame(te)
        don = F.donor_index(X.date.to_numpy(), X.ticker.to_numpy(), np.random.default_rng([ctx.seed, F.IMPORTANCE_STREAM, 0]))
        X["usdjpy_ret"] = X.usdjpy_ret.to_numpy()[don]
        sse = float(((df.abn_oc[te].to_numpy() - m.predict(X, ctx)) ** 2).sum())
        self.assertAlmostEqual(sse / fr.importance["sse_perm"]["usdjpy_ret"][0], 1.0, delta=1e-12)

    def test_table_ranking_determinism_and_no_side_effects(self):
        tab = F.importance_table(self.folds, "M3")
        self.assertEqual(tab.feature.iloc[0], "usdjpy_ret")                   # planted b = 3 ranks first
        self.assertEqual(list(tab["rank"]), [1, 2, 3, 4])
        self.assertTrue(tab.exceeds_noise.isna().all())                       # no noise column in M3
        self.assertEqual(tab.attrs["repeats"], 20)
        self.assertEqual(tab.attrs["n_rows"], int(self.folds[self.folds.model == "M3"].n_test.sum()))
        p0, f0 = F.walk_forward(self.df, {"M2": M2, "M3": M3}, self.spec)
        pd.testing.assert_frame_equal(p0, self.preds)                         # importance changes no prediction
        self.assertTrue(f0.importance.isna().all())
        p1, f1 = F.walk_forward(self.df, {"M2": M2, "M3": M3}, self.spec, importance=["M3"])
        pd.testing.assert_frame_equal(F.importance_table(f1, "M3"), tab)
        with self.assertRaises(ValueError):
            F.walk_forward(self.df, {"M3": M3}, self.spec, importance=["M7"])
        with self.assertRaises(ValueError):
            F.importance_table(self.folds, "M2")


class TestImportanceM7(_Reg):
    def test_noise_calibration(self):
        df = full_panel(600, seed=5, signal=0.02)                            # planted 1[gap>0]*1[oc>0]
        _, folds = F.walk_forward(df, {"M1": M1, "M7": M7}, self.spec, importance=["M7"])
        tab = F.importance_table(folds, "M7")
        self.assertEqual(set(tab.feature), set(M7.features) | {F.NOISE_COLUMN})
        self.assertEqual(set(tab.feature.iloc[:2]), {"gap_adj_lag1", "oc_lag1"})
        self.assertTrue(tab.exceeds_noise.iloc[:2].all())
        noise = tab[tab.is_noise].iloc[0]
        self.assertFalse(noise.exceeds_noise)
        self.assertLess(abs(noise.mean_dmse), 0.05 * tab.mean_dmse.iloc[0])  # noise column near 0


class TestRegistry(_Reg):
    def test_one_strict_line_per_call(self):
        df = strong_panel(560, b=1.0)
        p, f = F.walk_forward(df, {"M1": M1, "M5": M5}, self.spec, output_path="reports/x.json")
        p2, f2 = F.walk_forward(df.assign(abn_oc=df.abn_oc * 1.01), {"M1": M1}, self.spec)
        lines = R.read_registry(R.SYNTHETIC_PATH)
        self.assertEqual(len(lines), 2)
        self.assertFalse(R.REAL_PATH.exists())
        a = lines[0]
        self.assertEqual(set(a), R.KEYS)
        json.dumps(a, allow_nan=False)
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.assertEqual((a["git_commit"], a["spec_sha256"], a["provenance"], a["target"], a["seed"]),
                         (head, self.spec.sha256, B.SYNTHETIC, "abn_oc", self.spec.seed))
        self.assertEqual(a["data_sha256"], R.frame_sha256(df))
        self.assertNotEqual(lines[1]["data_sha256"], a["data_sha256"])
        self.assertEqual(a["models"], {"M1": "ofilt.drift.models.linear.M1", "M5": "ofilt.drift.models.ridge.M5"})
        self.assertEqual(a["grids"], {"M1": None, "M5": {"alpha_mults": [1e-4, 1e-3, 1e-2, 1e-1, 1.0]}})
        self.assertEqual((a["output_path"], a["importance"], lines[1]["output_path"]), ("reports/x.json", [], None))
        self.assertEqual(len(a["folds"]), len(f))
        self.assertEqual(set(a["folds"][0]), set(R.FOLD_KEYS))
        m5 = [x for x in a["folds"] if x["model"] == "M5"]
        self.assertEqual(set(m5[0]["chosen"]["val_mse"]), {"0.0001", "0.001", "0.01", "0.1", "1.0"})
        self.assertEqual(f.attrs["run_id"], a["run_id"])
        self.assertEqual(f2.attrs["run_id"], lines[1]["run_id"])
        self.assertEqual(m5[0]["test_start"], pd.Timestamp(f.test_start.iloc[0]).isoformat())

    def test_refusals_and_paths(self):
        class NaNChosen(F.ForecastModel):
            name, features = "nan", ("spy_oc",)

            def fit(self, X, y, ctx):
                self.chosen = {"x": float("nan")}

            def predict(self, X, ctx):
                return np.zeros(len(X))

        df = strong_panel(560, b=1.0)
        before = len(R.read_registry(R.SYNTHETIC_PATH))
        with self.assertRaises(ValueError):                                   # strict JSON: NaN refused
            F.walk_forward(df, {"nan": NaNChosen}, self.spec)
        self.assertEqual(len(R.read_registry(R.SYNTHETIC_PATH)), before)
        with mock.patch.object(R, "SYNTHETIC_PATH", Path(self._tmp.name)):    # unwritable (a directory)
            with self.assertRaises(OSError):
                F.walk_forward(df, {"M1": M1}, self.spec)
        self.assertEqual(R.registry_path(B.SYNTHETIC), R.SYNTHETIC_PATH)
        self.assertEqual(R.registry_path(B.DEV_REAL), R.REAL_PATH)
        self.assertEqual(R.registry_path(B.CONFIRM_REAL), R.REAL_PATH)
        with self.assertRaises(B.BlindingError):
            R.registry_path("other")
        for bad in ({True: 1}, {"a": object()}, {(1, 2): 3}):
            with self.assertRaises(TypeError):
                R.json_safe(bad)
        self.assertEqual(R.json_safe({1.5: np.int64(2), 3: (np.float64(0.5), pd.Timestamp("2030-01-02"))}),
                         {"1.5": 2, "3": [0.5, "2030-01-02T00:00:00"]})

    def test_committed_registry_empty_while_draft(self):
        real = ROOT / "RUN_REGISTRY.jsonl"
        self.assertTrue(real.exists())
        if self.spec.status == "DRAFT":                                       # no real forecast before the tags
            self.assertEqual(real.read_text(), "")


if __name__ == "__main__":
    unittest.main()
