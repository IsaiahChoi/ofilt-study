import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.schema import ALLOWED_FEATURES  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402


def synth_panel(n_dates=300, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2015-01-06", periods=n_dates)
    rows = []
    for t, bt in zip(["5706", "5711", "5713"], [1.3, 0.9, 1.1]):
        h = rng.normal(0, 0.01, n_dates)
        rows.append(pd.DataFrame({
            "date": dates, "ticker": t, "y_topix_oc": h, "y_oc": bt * h + rng.normal(0, 0.01, n_dates),
            "ao_gap_adj": rng.normal(0, 0.01, n_dates), "ao_topix_gap": rng.normal(0, 0.005, n_dates),
            "earn_flag": (rng.random(n_dates) < 0.05).astype(int),
            "news_flag": (rng.random(n_dates) < 0.02).astype(int)}))
    df = pd.concat(rows).sort_values(["date", "ticker"], kind="mergesort").reset_index(drop=True)
    return B.mark_synthetic(df)


def brute_beta(df, i, *, window=None, min_periods, exclude=True):
    """Direct definition: eligible rows of the same ticker dated strictly before row i."""
    r = df.loc[i]
    s = df[(df.ticker == r.ticker) & (df.date < r.date)]
    if exclude:
        s = s[(s.earn_flag == 0) & (s.news_flag == 0)]
    if window is not None:
        s = s.iloc[-window:]
    if len(s) < min_periods:
        return np.nan
    y, h = s.y_oc.to_numpy(), s.y_topix_oc.to_numpy()
    return np.mean((y - y.mean()) * (h - h.mean())) / np.var(h)


class TestBeta(unittest.TestCase):
    def setUp(self):
        self.spec = Spec.load()
        self.df = synth_panel()

    def test_expanding_matches_definition(self):
        out = TG.add_targets(self.df, self.spec)
        ii = np.random.default_rng(1).choice(len(self.df), 120, replace=False)
        for i in ii:
            want = brute_beta(self.df, i, min_periods=self.spec.beta.min_periods)
            got = out.loc[i, "beta"]
            if np.isnan(want):
                self.assertTrue(np.isnan(got))
            else:
                self.assertAlmostEqual(got, want, places=12)
        self.assertTrue(out.beta.notna().any() and out.beta.isna().any())

    def test_rolling_and_all_rows_match_definition(self):
        b = TG.past_beta(self.df, method="rolling", window=60, lag_days=1)
        ball = TG.past_beta(self.df, method="expanding", min_periods=100)
        for i in np.random.default_rng(2).choice(len(self.df), 80, replace=False):
            w = brute_beta(self.df, i, window=60, min_periods=60, exclude=False)
            a = brute_beta(self.df, i, min_periods=100, exclude=False)
            for got, want in ((b[i], w), (ball[i], a)):
                self.assertTrue(np.isnan(got) if np.isnan(want) else abs(got - want) < 1e-12)

    def test_excluded_rows_never_enter(self):
        out = TG.add_targets(self.df, self.spec)
        d2 = self.df.copy()
        ex = (d2.earn_flag == 1) | (d2.news_flag == 1)
        d2.loc[ex, "y_oc"] = 9.0
        d2.loc[ex, "y_topix_oc"] = -7.0
        out2 = TG.add_targets(d2, self.spec)
        pd.testing.assert_series_equal(out.beta, out2.beta)
        pd.testing.assert_series_equal(out.abn_oc[~ex], out2.abn_oc[~ex])

    def test_identities_and_attrs(self):
        out = TG.add_targets(self.df, self.spec)
        self.assertTrue(np.array_equal(out.cc_abn, out.gap_abn + out.abn_oc, equal_nan=True))  # bit-exact
        self.assertTrue((out.cc_abn.isna() == out.beta.isna()).all())
        self.assertTrue(np.allclose(out.cc_raw, out.ao_gap_adj + out.y_oc, rtol=0, atol=0))
        ok = out.beta.notna()
        self.assertTrue(np.allclose(out.abn_oc[ok], out.y_oc[ok] - out.beta[ok] * out.y_topix_oc[ok]))
        self.assertTrue(np.allclose(out.gap_abn[ok], out.ao_gap_adj[ok] - out.beta[ok] * out.ao_topix_gap[ok]))
        self.assertTrue(out.raw_oc.equals(out.y_oc))
        self.assertEqual(out.attrs["provenance"], "synthetic")
        self.assertEqual(out.attrs["targets"]["method"], "expanding")
        self.assertFalse(TG.DERIVED_NONFEATURES & ALLOWED_FEATURES)

    def test_synthetic_not_registered(self):
        before = B.registered_labels()
        TG.add_targets(self.df, self.spec)
        self.assertEqual(before, B.registered_labels())

    def test_refusals(self):
        for kw in [dict(min_periods=5, lag_days=0), dict(min_periods=5, lag_days=-1),
                   dict(method="ewm", min_periods=5), dict(method="rolling"),
                   dict(method="rolling", window=1), dict(method="expanding", window=10, min_periods=5),
                   dict(method="expanding")]:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                TG.past_beta(self.df, **kw)
        dup = pd.concat([self.df, self.df.iloc[:1]], ignore_index=True)
        with self.assertRaises(ValueError):
            TG.past_beta(dup, min_periods=5)


class TestRealDev(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = Spec.load()
        cls.dev = IO.load_dev()
        cls.ev = IO.load_events_firm()
        cls.out = TG.add_masks(TG.add_targets(cls.dev, cls.spec), cls.ev, cls.spec)

    def test_rebuilt_flags_equal_panel_flags(self):
        earn = TG.event_rows(self.ev, self.dev, ["TANSHIN"], (0, 1))
        news = TG.event_rows(self.ev, self.dev, ["STANDALONE_NEWS"], (0, 1))
        self.assertTrue((earn == self.dev.earn_flag.astype(bool)).all())
        self.assertTrue((news == self.dev.news_flag.astype(bool)).all())

    def test_mask_nesting(self):
        o = self.out
        inf, d2, fe = o.excl_inference, o.excl_d2, o.excl_forecast_eval
        self.assertTrue((d2 | ~inf).all())                       # D+2 superset of D,D+1
        self.assertGreater(d2.sum(), inf.sum())
        self.assertTrue((inf | ~fe).all())                        # eval mask subset
        self.assertTrue((fe | ~o.earn_flag.astype(bool)).all())   # all TANSHIN D,D+1 in eval mask
        news_d = TG.event_rows(self.ev, self.dev, ["STANDALONE_NEWS"], (0,))
        kept_news_d = news_d & ~o.earn_flag.astype(bool) & ~TG.event_rows(self.ev, self.dev, ["STANDALONE_NEWS"], (1,))
        self.assertTrue((~fe[kept_news_d]).all())                 # unscheduled news day D stays in eval
        self.assertGreater(kept_news_d.sum(), 0)

    def test_real_targets_registered_and_collision_margin(self):
        for c in ("abn_oc", "gap_abn", "cc_abn", "cc_raw"):
            self.assertIn(f"dev_real:{c}", B.registered_labels())
        d = self.dev  # registry now includes tick-grid cc_raw; row-aligned margin must hold per ticker-year
        for _, g in d.groupby([d.ticker, d.date.dt.year]):
            for c in ("ao_gap_adj", "ao_gap_raw", "ao_topix_gap"):
                self.assertLess(B.row_match_fraction(g[c], g.date, g.ticker)[0], 0.25, c)
        for c in ("abn_oc", "gap_abn", "cc_abn", "cc_raw"):
            self.assertEqual(B.row_match_fraction(self.out[c], self.out.date, self.out.ticker)[0], 1.0, c)
        r = self.out.drop(columns=["y_oc", "y_topix_oc"])
        r.attrs = {"provenance": "synthetic"}
        with self.assertRaises(B.BlindingError):
            B.require_unblinded(r)                                 # constructed targets alone still caught

    def test_beta_coverage(self):
        b = self.out.beta
        # first 250 eligible rows per ticker have no beta; after that beta exists on every row
        for t, s in self.out.groupby("ticker"):
            s = s.sort_values("date")
            first = s.beta.first_valid_index()
            n_elig_before = (~s.loc[:first].excl_inference.iloc[:-1]).sum()
            self.assertEqual(n_elig_before, self.spec.beta.min_periods, t)
            self.assertTrue(s.loc[first:].beta.notna().all(), t)
        self.assertTrue(np.isfinite(b.dropna()).all())


if __name__ == "__main__":
    unittest.main()
