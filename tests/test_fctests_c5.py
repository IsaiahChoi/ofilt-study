"""C5 tests (synthetic only): forecast comparisons in ofilt/drift/fctests.py."""
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import fctests as FT  # noqa: E402
from ofilt.drift import forecast as F  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift.models import M0, M1, M2, M3  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

TICKERS = ("5706", "5711", "5713")
PT_SIZE_SEED = 20261001 + 5000


def hand_frame(seed=3):
    """Small unbalanced predictions frame (12 dates x 3 tickers minus 3 rows, the SAME rows
    for every model), synthetic dates and values; models M1, M2, M3, M7."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2030-01-07", periods=12)
    drop = {(3, "5711"), (7, "5706"), (8, "5713")}
    keys = [(i, d, t) for i, d in enumerate(dates) for t in TICKERS if (i, t) not in drop]
    y = rng.standard_normal(len(keys)) * 0.01
    out = []
    for m in ("M1", "M2", "M3", "M7"):
        yhat = y * rng.uniform(0.0, 0.6) + rng.standard_normal(len(keys)) * 0.008
        out.append(pd.DataFrame({
            "date": [d for _, d, _ in keys], "ticker": [t for _, _, t in keys],
            "fold": [0 if i < 6 else 1 for i, _, _ in keys],
            "train_end": [pd.Timestamp("2030-01-04") if i < 6 else dates[5] for i, _, _ in keys],
            "model": m, "y": y, "yhat": yhat}))
    return B.mark_synthetic(pd.concat(out, ignore_index=True)[list(F.PRED_COLUMNS)])


def by_hand(df, first, second, kind):
    """Plain-Python reference: per-row differential, date means in date order, NW with the
    spec lag rule written out, normal p-value via math.erfc."""
    a = {(r.date, r.ticker): r for r in df[df.model == first].itertuples()}
    b = {(r.date, r.ticker): r for r in df[df.model == second].itertuples()}
    per_date = {}
    for k in sorted(a):
        y, u, r = a[k].y, a[k].yhat, b[k].yhat
        if kind == "cw":
            f = (y - r) ** 2 - ((y - u) ** 2 - (r - u) ** 2)
        else:                                            # DM: loss(second) - loss(first)
            f = (y - r) ** 2 - (y - u) ** 2
        per_date.setdefault(k[0], []).append(f)
    fbar = [sum(v) / len(v) for _, v in sorted(per_date.items())]
    T = len(fbar)
    L = math.floor(4 * (T / 100) ** (2 / 9))
    m = sum(fbar) / T
    gamma = [sum((fbar[t] - m) * (fbar[t - l] - m) for t in range(l, T)) / T for l in range(L + 1)]
    omega = gamma[0] + 2 * sum((1 - l / (L + 1)) * gamma[l] for l in range(1, L + 1))
    se = math.sqrt(omega / T)
    z = m / se
    p = 0.5 * math.erfc(z / math.sqrt(2)) if kind == "cw" else math.erfc(abs(z) / math.sqrt(2))
    return dict(mean=m, se=se, stat=z, p=p, lag=L, T=T, lrv=omega)


def strong_panel(n_dates=800, b=1.0, seed=11):
    """masked_panel (test_forecast_c1) with a strong planted FX loading."""
    df = S.synthetic_panel(n_dates, b=b, seed=seed, p_excl=0.05)
    rng = np.random.default_rng(seed + 1)
    df["news_flag"] = (rng.random(len(df)) < 0.03).astype(int)
    df["excl_inference"] = (df.earn_flag == 1) | (df.news_flag == 1)
    df["excl_forecast_eval"] = df.earn_flag == 1
    return B.mark_synthetic(df)


def pt_size(reps=1000, n=1013, mu_y=0.1, mu_f=0.25, seed=PT_SIZE_SEED):
    """Rejections (one-sided, two-sided; 5%) of PT on independent series with unequal
    up-shares (about 0.54 and 0.60), so the P* correction matters."""
    z1, z2 = stats.norm.ppf(0.95), stats.norm.ppf(0.975)
    k1 = k2 = 0
    for r in range(reps):
        rng = np.random.default_rng([seed, r])
        s = FT.pt_stat(rng.standard_normal(n) + mu_y, rng.standard_normal(n) + mu_f)["stat"]
        k1 += s > z1
        k2 += abs(s) > z2
    return int(k1), int(k2)


class TestAggregation(unittest.TestCase):
    def test_nw_equals_pairwise_bartlett_definition(self):
        x = np.random.default_rng(5).standard_normal(57) * 0.3 + 0.1
        T, m = x.size, x.mean()
        for L in (0, 1, 3, Spec.dk_lag(57), 12, 80):
            pair_sum = sum((1 - abs(s - t) / (L + 1)) * (x[s] - m) * (x[t] - m)
                           for s in range(T) for t in range(T) if abs(s - t) <= L)
            r = FT.nw_mean(x, lag=L)
            self.assertAlmostEqual(r["lrv"] / (pair_sum / T), 1.0, delta=1e-12)
            self.assertAlmostEqual(r["se"], math.sqrt(pair_sum / T / T), delta=1e-15)
        self.assertEqual(FT.nw_mean(x)["lag"], Spec.dk_lag(57))
        self.assertEqual((Spec.dk_lag(1013), Spec.dk_lag(1708)), (6, 7))
        with self.assertRaises(ValueError):
            FT.nw_mean(np.zeros(20))                     # degenerate: zero long-run variance
        with self.assertRaises(ValueError):
            FT.nw_mean(x, lag=-1)

    def test_cw_dm_equal_hand_computation(self):
        df = hand_frame()
        cw = FT.clark_west(df, "M3", "M2")
        ref = by_hand(df, "M3", "M2", "cw")
        self.assertEqual((cw["lag"], cw["T"], cw["n_rows"], cw["sided"]), (ref["lag"], 12, 33, "one"))
        for k in ("mean", "se", "stat", "lrv"):
            self.assertAlmostEqual(cw[k] / ref[k], 1.0, delta=1e-12, msg=k)
        self.assertAlmostEqual(cw["p"], ref["p"], delta=1e-14)
        self.assertAlmostEqual(cw["mean"], cw["mspe_restricted"] - cw["mspe_unrestricted"] + cw["adjustment"],
                               delta=1e-17)
        dm = FT.diebold_mariano(df, "M7", "M1")
        ref = by_hand(df, "M7", "M1", "dm")
        self.assertEqual((dm["lag"], dm["T"], dm["sided"], dm["loss"]), (ref["lag"], 12, "two", "squared_error"))
        for k in ("mean", "se", "stat", "lrv"):
            self.assertAlmostEqual(dm[k] / ref[k], 1.0, delta=1e-12, msg=k)
        self.assertAlmostEqual(dm["p"], ref["p"], delta=1e-14)
        rev = FT.diebold_mariano(df, "M1", "M7")             # antisymmetric, exactly
        self.assertEqual(rev["stat"], -dm["stat"])
        self.assertEqual(rev["p"], dm["p"])
        # CW differential == 2 (y - yhat_r)(yhat_u - yhat_r)
        p = FT.pair(df, "M3", "M2")
        f = (p.y - p.yhat_second) ** 2 - ((p.y - p.yhat_first) ** 2 - (p.yhat_second - p.yhat_first) ** 2)
        np.testing.assert_allclose(f, 2 * (p.y - p.yhat_second) * (p.yhat_first - p.yhat_second), rtol=0, atol=1e-18)
        same = df[df.model == "M2"].assign(model="M2b")
        with self.assertRaises(ValueError):                   # identical forecasts: degenerate
            FT.clark_west(pd.concat([df, same], ignore_index=True), "M2b", "M2")


class TestPairing(unittest.TestCase):
    def setUp(self):
        self.df = hand_frame()

    def test_mismatched_rows_refused(self):
        df = self.df
        i2 = df.index[df.model == "M2"]
        cases = {
            "dropped row": df.drop(index=i2[4]),
            "y differs": df.assign(y=np.where(df.index == i2[4], df.y + 1e-12, df.y)),
            "fold differs": df.assign(fold=np.where(df.index == i2[4], 5, df.fold)),
            "train_end differs": df.assign(train_end=df.train_end.where(df.index != i2[4], pd.Timestamp("2029-12-31"))),
            "duplicated row": pd.concat([df, df.loc[[i2[4]]]], ignore_index=True),
            "two calls concatenated": pd.concat([df, df[df.model == "M2"]], ignore_index=True),
            "whole output twice": pd.concat([df, df], ignore_index=True),   # lengths and keys still match
            "shifted date": df.assign(date=df.date.where(df.index != i2[4], pd.Timestamp("2030-03-01"))),
        }
        for name, bad in cases.items():
            with self.subTest(name), self.assertRaises(FT.PairingError):
                FT.clark_west(bad, "M3", "M2")
        with self.assertRaises(FT.PairingError):
            FT.pair(df, "M3", "M5")                           # model absent
        with self.assertRaises(ValueError):
            FT.pair(df, "M3", "M3")
        with self.assertRaises(ValueError):
            FT.pair(df.drop(columns=["fold"]), "M3", "M2")
        with self.assertRaises(ValueError):
            FT.pair(df.assign(yhat=np.where(df.index == i2[0], np.nan, df.yhat)), "M3", "M2")
        p = FT.pair(df, "M3", "M2")                           # the clean frame pairs
        self.assertEqual(p.y.size, 33)

    def test_guard_runs_first(self):
        real = self.df.drop(columns=["y"]).copy()             # malformed AND labelled real
        real.attrs = {"provenance": B.DEV_REAL}
        bare = self.df.copy()
        bare.attrs = {}
        calls = [lambda d: FT.pair(d, "M3", "M2"), lambda d: FT.clark_west(d, "M3", "M2"),
                 lambda d: FT.diebold_mariano(d, "M7", "M1"), lambda d: FT.oos_r2(d, "M3", "M1"),
                 lambda d: FT.oos_r2_table(d), lambda d: FT.pesaran_timmermann(d, "M3", None),
                 lambda d: FT.run_comparisons(d)]
        for fn in calls:
            for d in (real, bare):
                with self.assertRaises(B.BlindingError):
                    fn(d)
        with self.assertRaises(B.BlindingError):              # attrs/kwarg conflict
            FT.pair(self.df, "M3", "M2", provenance=B.DEV_REAL)
        self.assertEqual(FT.pair(bare, "M3", "M2", provenance=B.SYNTHETIC).provenance, B.SYNTHETIC)


class TestPesaranTimmermann(unittest.TestCase):
    def test_formula_and_identities(self):
        y = np.array([0.3, -0.2, 0.1, 0.4, -0.5, 0.2, -0.1, 0.6, -0.3, 0.0])
        f = np.array([0.1, -0.1, -0.2, 0.3, -0.4, 0.1, 0.2, 0.2, 0.1, -0.1])
        r = FT.pt_stat(y, f)                       # y up: 5 of 10 (0.0 is not up); f up: 6 of 10
        n, hit, py, pf = 10, 0.7, 0.5, 0.6
        ps = py * pf + (1 - py) * (1 - pf)
        den = ps * (1 - ps) / n - ((2 * py - 1) ** 2 * pf * (1 - pf) / n + (2 * pf - 1) ** 2 * py * (1 - py) / n
                                   + 4 * py * pf * (1 - py) * (1 - pf) / n ** 2)
        self.assertEqual((r["hit_rate"], r["up_share_y"], r["up_share_yhat"], r["n"]), (hit, py, pf, n))
        self.assertAlmostEqual(r["p_star"], ps, delta=1e-15)
        self.assertAlmostEqual(r["stat"], (hit - ps) / math.sqrt(den), delta=1e-12)
        self.assertAlmostEqual(r["p"], 0.5 * math.erfc(r["stat"] / math.sqrt(2)), delta=1e-14)
        rng = np.random.default_rng(9)
        for _ in range(5):
            a, b = rng.standard_normal(400) + 0.2, rng.standard_normal(400) * 0.3 + rng.standard_normal(400) - 0.1
            q = FT.pt_stat(a, b)
            uy, uf, m = a > 0, b > 0, 400
            closed = 4 * uy.mean() * (1 - uy.mean()) * uf.mean() * (1 - uf.mean()) * (m - 1) / m ** 2
            ps = q["p_star"]
            vstar = ((2 * q["up_share_y"] - 1) ** 2 * q["up_share_yhat"] * (1 - q["up_share_yhat"]) / m
                     + (2 * q["up_share_yhat"] - 1) ** 2 * q["up_share_y"] * (1 - q["up_share_y"]) / m
                     + 4 * q["up_share_y"] * q["up_share_yhat"] * (1 - q["up_share_y"]) * (1 - q["up_share_yhat"]) / m ** 2)
            self.assertAlmostEqual((ps * (1 - ps) / m - vstar) / closed, 1.0, delta=1e-10)
            phi = np.corrcoef(uy.astype(float), uf.astype(float))[0, 1]
            self.assertAlmostEqual(q["stat"], phi * m / math.sqrt(m - 1), delta=1e-10)   # PT = sqrt(n^2/(n-1)) r
        self.assertFalse(FT.pt_stat(y, np.zeros(10))["defined"])                         # M0: constant sign
        self.assertTrue(math.isnan(FT.pt_stat(np.ones(10), f)["stat"]))
        strong = FT.pt_stat(a, a + 0.1 * rng.standard_normal(400))
        self.assertGreater(strong["stat"], 10)
        for bad in ((y, f[:5]), (y[:1], f[:1]), (np.r_[y[:9], np.nan], f)):
            with self.assertRaises(ValueError):
                FT.pt_stat(*bad)

    def test_size_on_independent_series(self):
        k1, k2 = pt_size()
        self.assertTrue(0.03 <= k1 / 1000 <= 0.07, k1)         # P28 quoted 4.6% (band [3%, 7%])
        self.assertTrue(0.03 <= k2 / 1000 <= 0.07, k2)


class TestWalkForwardIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = Spec.load()
        cls.df = strong_panel()
        cls.models = {"M0": M0, "M1": M1, "M2": M2, "M3": M3}
        cls.preds, cls.folds = F.walk_forward(cls.df, cls.models, cls.spec)

    def test_comparisons_oos_r2_and_spec_driver(self):
        comps = FT.spec_comparisons(self.spec)
        self.assertEqual([(c["role"], c["test"], c["first"], c["second"], c["sided"]) for c in comps], [
            ("primary", "clark_west", "M3", "M2", "one"), ("secondary", "clark_west", "M4", "M3", "one"),
            ("secondary", "clark_west", "M5", "M3", "one"), ("secondary", "clark_west", "M7", "M1", "one"),
            ("secondary", "diebold_mariano", "M7", "M1", "two")])
        out = FT.run_comparisons(self.preds, self.spec)
        self.assertEqual(len(out["results"]), 1)
        self.assertEqual(len(out["skipped"]), 4)              # M4, M5, M7 belong to other calls
        cw = out["results"][0]
        self.assertEqual((cw["role"], cw["unrestricted"], cw["restricted"]), ("primary", "M3", "M2"))
        ev = self.preds[self.preds.model == "M3"]
        self.assertEqual((cw["n_rows"], cw["T"]), (len(ev), ev.date.nunique()))
        self.assertEqual(cw["lag"], Spec.dk_lag(ev.date.nunique()))
        self.assertTrue(cw["reject"])
        self.assertLess(cw["p"], 1e-6)                        # b = 1.0 planted
        tab = FT.oos_r2_table(self.preds).set_index(["model", "benchmark"])
        self.assertEqual(len(tab), 6)
        for (m, bench), row in tab.iterrows():
            a = self.preds[self.preds.model == m].sort_values(["date", "ticker"])
            b = self.preds[self.preds.model == bench].sort_values(["date", "ticker"])
            sse = ((a.y.to_numpy() - a.yhat.to_numpy()) ** 2).sum()
            self.assertAlmostEqual(row.pooled, 1 - sse / ((b.y.to_numpy() - b.yhat.to_numpy()) ** 2).sum(), delta=1e-12)
            for t in TICKERS:
                sa, sb = a[a.ticker == t], b[b.ticker == t]
                self.assertAlmostEqual(row[f"r2_{t}"], 1 - ((sa.y - sa.yhat) ** 2).sum() / ((sb.y - sb.yhat) ** 2).sum(),
                                       delta=1e-12)
        self.assertAlmostEqual(tab.loc[("M1", "M0"), "pooled"],
                               1 - ((ev.y - self.preds[self.preds.model == "M1"].yhat.to_numpy()) ** 2).sum()
                               / (ev.y ** 2).sum(), delta=1e-12)
        self.assertGreater(tab.loc[("M3", "M1"), "pooled"], tab.loc[("M2", "M1"), "pooled"])

    def test_second_call_refused(self):
        df2 = self.df.copy()
        late = np.sort(df2.date.unique())[700]
        df2.loc[(df2.date >= late) & (df2.ticker == "5711"), "copx_oc"] = np.nan   # a different sample
        df2 = B.mark_synthetic(df2)
        p2, f2 = F.walk_forward(df2, {"M3b": M3, "M3": M3}, self.spec)
        mixed = pd.concat([self.preds, p2[p2.model == "M3b"]], ignore_index=True)
        with self.assertRaises(FT.PairingError):
            FT.clark_west(mixed, "M3b", "M2")
        with self.assertRaises(FT.PairingError):              # fold log from another call
            FT.pesaran_timmermann(self.preds, "M3", f2)

    def test_pt_base_rate_from_fold_log(self):
        df, need = self.df, ["usdjpy_ret", "eurusd_ret", "spy_oc", "copx_oc"]
        ok = df.abn_oc.notna() & df[need].notna().all(axis=1) & ~df.excl_inference
        for _, fr in self.folds[self.folds.model == "M2"].iterrows():
            tr = df[ok & (df.date < fr.test_start)]
            exp = {t: [int((g.abn_oc > 0).sum()), len(g)] for t, g in tr.groupby("ticker")}
            pm = tr.groupby("date").abn_oc.mean()
            self.assertEqual(fr.train_up, {"by_ticker": exp, "portfolio": [int((pm > 0).sum()), len(pm)]})
            self.assertEqual(sum(v[1] for v in exp.values()), fr.n_train)
        fl = self.folds
        for m in self.models:                                  # identical across models in one call
            self.assertEqual(list(fl[fl.model == m].train_up), list(fl[fl.model == "M0"].train_up))
        json.dumps(list(fl.train_up))                          # JSON-safe for the run registry
        r = FT.pesaran_timmermann(self.preds, "M3", self.folds)
        rows = self.preds[self.preds.model == "M3"].sort_values(["date", "ticker"])
        ups = fl[fl.model == "M3"].set_index("fold").train_up
        for t in TICKERS:
            g = rows[rows.ticker == t]
            ref = FT.pt_stat(g.y.to_numpy(), g.yhat.to_numpy())
            self.assertEqual({k: r["per_ticker"][t][k] for k in ref}, ref)
            br = np.mean([ups[f]["by_ticker"][t][0] / ups[f]["by_ticker"][t][1] for f in g.fold])
            self.assertAlmostEqual(r["per_ticker"][t]["base_rate_train"], br, delta=1e-15)
        dm = rows.groupby("date")[["y", "yhat"]].mean()
        ref = FT.pt_stat(dm.y.to_numpy(), dm.yhat.to_numpy())
        for k in ("hit_rate", "p_star", "n", "defined"):
            self.assertEqual(r["portfolio"][k], ref[k])
        self.assertAlmostEqual(r["portfolio"]["stat"], ref["stat"], delta=1e-12)
        fold_of = rows.groupby("date").fold.first()
        self.assertAlmostEqual(r["portfolio"]["base_rate_train"],
                               np.mean([ups[f]["portfolio"][0] / ups[f]["portfolio"][1] for f in fold_of]), delta=1e-15)
        self.assertGreater(r["portfolio"]["stat"], 3)          # strong planted signal
        self.assertFalse(FT.pesaran_timmermann(self.preds, "M0", self.folds)["portfolio"]["defined"])
        bad = self.folds.copy()
        bad.loc[bad.index[bad.model == "M3"][0], "n_test"] += 1
        with self.assertRaises(FT.PairingError):
            FT.pesaran_timmermann(self.preds, "M3", bad)


class TestWilson(unittest.TestCase):
    def test_wilson(self):
        import report_B7b
        for n in (1, 7, 200, 300, 1000, 5000):
            for k in sorted({0, 1, n // 3, n // 2, n - 1, n}):
                lo, hi = report_B7b.wilson(k, n)
                self.assertEqual(FT.wilson(k, n), (max(0.0, lo), min(1.0, hi)))
        quoted = {(8, 300): (1.36, 5.17, 2), (200, 200): (98.1, 100.0, 1), (179, 200): (84.5, 93.0, 1)}   # P28
        for (k, n), (lo, hi, dp) in quoted.items():
            w = FT.wilson(k, n)
            self.assertEqual((round(100 * w[0], dp), round(100 * w[1], dp)), (lo, hi))
        b7b = json.loads((ROOT / "reports" / "B7b_size_preview.json").read_text())["cells"][0]["reject_H1"]
        self.assertEqual(FT.rate_summary(b7b["k"], b7b["n"])["wilson95"], tuple(b7b["wilson95"]))
        self.assertAlmostEqual(FT.wilson(0, 10)[0], 0.0, delta=1e-15)    # exact endpoints up to 1 ulp
        self.assertAlmostEqual(FT.wilson(10, 10)[1], 1.0, delta=1e-15)   # (B7b arithmetic gives 1 - 2^-53)
        lo90, hi90 = FT.wilson(30, 100, alpha=0.10)
        lo95, hi95 = FT.wilson(30, 100)
        self.assertTrue(lo95 < lo90 < 0.3 < hi90 < hi95)
        for bad in ((11, 10), (-1, 10), (1, 0), (1.0, 10), (True, 10)):
            with self.assertRaises((ValueError, TypeError)):
                FT.wilson(*bad)


if __name__ == "__main__":
    unittest.main()
