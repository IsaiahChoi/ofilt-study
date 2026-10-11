"""P4-3 (P4Q32, P4Q33): ofilt/drift/sim_full.py, the full-schema simulator, against docs/P4_SIM_SPEC.md (version 2).
Exactly the 20 test methods of its §9.3. Seeds are the spec seed + 8,000,000 + k (§9.1), disjoint from every earlier
block. Every frame here is synthetic, except in test_dev_panel_kinds_and_guard (P4Q33), which reads the dev panel and
the firm events for their column names, order and dtype kinds only, and lets the loader register the real targets so
that the guard checks the simulator's frames against them. The calendar rules are recomputed here independently."""
import ast
import bisect
import calendar as pycal
import datetime as dt
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import calendar as CAL  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import schema as SC  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift import sim_full as SF  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

SPEC = Spec.load()
MODULE = ROOT / "ofilt" / "drift" / "sim_full.py"
SC1 = SF.Scenario(b=1.0, delta_post=-1.0, b_spread=(-0.3, 0.1, 0.2), a2=0.6, a2_gap=0.2, delta_cc=1.5,
                  c_usd_sess=0.5, c_eur_sess=-0.3, b_gotobi=0.4, sess_missing=(0, 0))
SC2 = SF.Scenario(b=1.0, delta_post=-1.0, a2=0.6, delta_cc=1.5)
BRK = pd.Timestamp("2024-11-05")
BRK_D = BRK.date()
P0 = (3000.0, 2500.0, 4500.0)
DIV = (40.0, 30.0, 50.0)
TOL = 1e-12
SIX = ("2022-06-14", "2022-06-15", "2023-12-14", "2023-12-15", "2025-07-14", "2025-07-15")
SPOT = {   # §3.3: date -> (prev, window minutes, bar count, us_n_sessions, window_start_utc, window_end_utc)
    "2015-01-06": ("2015-01-05", 1079, 1079, 1, "2015-01-05 06:00:00", "2015-01-05 23:59:00"),
    "2015-01-20": ("2015-01-19", 1079, 1079, 0, "2015-01-19 06:00:00", "2015-01-19 23:59:00"),
    "2022-01-04": ("2021-12-30", 6839, 3959, 3, "2021-12-30 06:00:00", "2022-01-03 23:59:00"),
    "2023-07-05": ("2023-07-04", 1079, 1079, 0, "2023-07-04 06:00:00", "2023-07-04 23:59:00"),
    "2024-11-05": ("2024-11-01", 5399, 2519, 2, "2024-11-01 06:00:00", "2024-11-04 23:59:00"),
    "2024-11-06": ("2024-11-05", 1049, 1049, 1, "2024-11-05 06:30:00", "2024-11-05 23:59:00"),
}
_SIMS: dict = {}
_TARGETS: dict = {}


def seed(k):
    return SPEC.seed + 8_000_000 + k


def out(k, scenario=None):
    key = (k, scenario)
    if key not in _SIMS:
        _SIMS[key] = SF.simulate(seed(k), scenario)
    return _SIMS[key]


def joined(o):
    j = pd.concat([o.dev, o.confirm], ignore_index=True)
    j.attrs = {"provenance": B.SYNTHETIC}
    return j


def targets_of(k, scenario=None):
    key = (k, scenario)
    if key not in _TARGETS:
        _TARGETS[key] = TG.add_targets(joined(out(k, scenario)), SPEC)
    return _TARGETS[key]


def dates(frame):
    return pd.DatetimeIndex(frame["date"].unique())


def cal_dates(o):
    """The joined calendar C as datetime.date."""
    return [d.date() for d in dates(o.dev)] + [d.date() for d in dates(o.confirm)]


def weekday_before(d):
    d -= dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def nth_weekday(y, m, wd, n):
    d = dt.date(y, m, 1)
    return d + dt.timedelta(days=(wd - d.weekday()) % 7 + 7 * (n - 1))


def last_weekday(y, m, wd):
    d = dt.date(y, m, pycal.monthrange(y, m)[1])
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)


def us_holidays():
    h = set()
    for y in range(2015, 2027):
        h |= {dt.date(y, 1, 1), nth_weekday(y, 1, 0, 3), nth_weekday(y, 2, 0, 3), last_weekday(y, 5, 0),
              dt.date(y, 7, 4), nth_weekday(y, 9, 0, 1), nth_weekday(y, 11, 3, 4), dt.date(y, 12, 25)}
        if y >= 2022:
            h.add(dt.date(y, 6, 19))
    return h


def windows(C):
    """§3.3, per date of C: (prev, minutes, bar count, us_n_sessions, start text, end text)."""
    hol = us_holidays()
    res, p = [], weekday_before(C[0])
    for t in C:
        close = dt.time(15, 30) if p >= BRK_D else dt.time(15, 0)
        start = dt.datetime.combine(p, close) - dt.timedelta(hours=9)
        end = dt.datetime.combine(t, dt.time(8, 59)) - dt.timedelta(hours=9)
        minutes = int((end - start).total_seconds() // 60)
        between = [p + dt.timedelta(days=i) for i in range(1, (t - p).days)]
        weekend = sum(1 for d in between if d.weekday() >= 5)
        us = sum(1 for i in range((t - p).days) if (p + dt.timedelta(days=i)).weekday() < 5
                 and (p + dt.timedelta(days=i)) not in hol)
        res.append((p, minutes, minutes - 1440 * weekend, us, start.strftime("%Y-%m-%d %H:%M:%S"),
                    end.strftime("%Y-%m-%d %H:%M:%S")))
        p = t
    return res


def by_month(C):
    m = {}
    for d in C:
        m.setdefault((d.year, d.month), []).append(d)
    return m


def roll_back(nominal, C):
    if not C[0] <= nominal <= C[-1]:
        return None
    i = bisect.bisect_right(C, nominal) - 1
    return C[i] if i >= 0 else None


def col(frame, c):
    return frame[c].to_numpy(dtype=float)


def per_date(frame, c):
    return frame[c].to_numpy()[::3]


class SimFullTests(unittest.TestCase):
    def assertRecovers(self, r, name, truth):
        p = r.param(name)
        self.assertLessEqual(abs(p["estimate"] - truth), 5 * p["se"], (name, p["estimate"], p["se"], truth))

    # 1
    def test_columns_order_and_keys(self):
        o = out(0)
        for f, part in ((o.dev, "dev"), (o.confirm, "confirmation")):
            self.assertEqual(tuple(f.columns), SF.COLUMNS)
            self.assertEqual(frozenset(f.columns), SC.all_grouped_columns())
            self.assertTrue(f.index.equals(pd.RangeIndex(len(f))))
            self.assertFalse(f.duplicated(["date", "ticker"]).any())
            self.assertEqual(list(f["ticker"]), list(SF.TICKERS) * (len(f) // 3))
            d = f["date"].to_numpy()
            self.assertTrue((d[::3] == d[1::3]).all() and (d[::3] == d[2::3]).all())
            self.assertTrue((np.diff(d[::3]) > np.timedelta64(0)).all())
            self.assertEqual(set(f.attrs), {"provenance", "part", "truth"})
            self.assertEqual((f.attrs["provenance"], f.attrs["part"]), (B.SYNTHETIC, part))
            self.assertEqual(f.attrs["truth"], o.truth)
        self.assertTrue((dates(o.dev) < pd.Timestamp("2022-01-01")).all())
        cd = dates(o.confirm)
        self.assertEqual((cd.min(), cd.max()), (pd.Timestamp("2022-01-04"), pd.Timestamp("2026-03-05")))

    # 2
    def test_dev_panel_kinds_and_guard(self):
        o = out(0)
        real, real_ev = IO.load_dev(), IO.load_events_firm()        # P4Q33: names, order and kinds only
        for f in (o.dev, o.confirm):
            self.assertEqual(list(f.columns), list(real.columns))
        self.assertEqual(list(o.events.columns), list(real_ev.columns))
        for c in real.columns:
            rk = real[c].dtype.kind
            for f in (o.dev, o.confirm):
                expected = "f" if rk == "i" and f[c].isna().any() else rk
                self.assertEqual(f[c].dtype.kind, expected, c)
        for c in real_ev.columns:
            self.assertEqual(o.events[c].dtype.kind, real_ev[c].dtype.kind, c)
        self.assertEqual(B.require_unblinded(o.dev), B.SYNTHETIC)
        self.assertEqual(B.require_unblinded(o.confirm), B.SYNTHETIC)

    # 3
    def test_dtype_rule(self):
        o, ne = out(0), out(4, SF.Scenario.not_estimable())
        for c in SF.INT_COLUMNS:
            self.assertEqual(o.dev[c].dtype, np.dtype("int64"), c)
        self.assertEqual(ne.confirm["xau_bars"].dtype, np.dtype("float64"))
        for c in SF.INT_COLUMNS:
            if c != "xau_bars":
                self.assertEqual(ne.confirm[c].dtype, np.dtype("int64"), c)
        for f in (o.dev, o.confirm):
            self.assertEqual(f["n225_bars"].dtype, np.dtype("float64"))
            v = f["n225_bars"].dropna().to_numpy()
            self.assertTrue((v == np.round(v)).all())
            for c in ("ticker", "window_start_utc", "window_end_utc"):
                self.assertTrue(pd.api.types.is_string_dtype(f[c]), c)
                self.assertTrue(all(type(x) is str for x in f[c]), c)
            self.assertTrue(pd.api.types.is_datetime64_any_dtype(f["date"]))
            for c in SF.COLUMNS:
                if c not in SF.INT_COLUMNS and c not in ("date", "ticker", "window_start_utc", "window_end_utc"):
                    self.assertEqual(f[c].dtype, np.dtype("float64"), c)

    # 4
    def test_dates(self):
        o = out(0)
        self.assertEqual(list(dates(o.confirm)), list(CAL.confirmation_calendar()))
        dc = SF.dev_calendar()
        self.assertEqual(len(dc), 1714)
        self.assertEqual((dc[0], dc[-1]), (pd.Timestamp("2015-01-06"), pd.Timestamp("2021-12-30")))
        self.assertEqual(list(dates(o.dev)), list(dc))
        sub = dc[-600:]
        o5 = SF.simulate(seed(5), dev_dates=sub)
        self.assertEqual(list(dates(o5.dev)), list(sub))
        self.assertEqual(o5.dev["window_start_utc"].iloc[0], f"{weekday_before(sub[0].date())} 06:00:00")
        with self.assertRaises(ValueError):
            SF.simulate(seed(5), dev_dates=dc[-599:].append(pd.DatetimeIndex(["2022-01-04"])))
        with self.assertRaises(ValueError):
            SF.simulate(seed(5), dev_dates=dc[-299:])

    # 5
    def test_window_columns(self):
        o = out(0)
        C = cal_dates(o)
        w = windows(C)
        j = joined(o)
        rep = np.repeat
        self.assertTrue(np.array_equal(col(j, "window_hours"), rep([x[1] / 60 for x in w], 3)))
        self.assertEqual(list(j["window_start_utc"]), [x[4] for x in w for _ in range(3)])
        self.assertEqual(list(j["window_end_utc"]), [x[5] for x in w for _ in range(3)])
        bar = rep([float(x[2]) for x in w], 3)
        zeroed = col(j, "usdjpy_bars") == 0.0
        self.assertFalse(zeroed.any())
        self.assertTrue(np.array_equal(col(j, "usdjpy_bars")[~zeroed], bar[~zeroed]))
        self.assertTrue(np.array_equal(col(j, "eurusd_bars"), bar))
        for c, off in (("xau_bars", 60.0), ("n225_bars", 120.0)):
            x = col(j, c)
            present = ~np.isnan(x)
            self.assertTrue(np.array_equal(x[present], bar[present] - off), c)
        row = {d: i for i, d in enumerate(C)}
        for d, (p, minutes, b, _, s, e) in SPOT.items():
            i = row[dt.date.fromisoformat(d)]
            self.assertEqual((str(w[i][0]), w[i][1], w[i][2], w[i][4], w[i][5]), (p, minutes, b, s, e), d)
            r = j.iloc[3 * i]
            self.assertEqual((r["window_hours"], r["usdjpy_bars"], r["window_start_utc"], r["window_end_utc"]),
                             (minutes / 60, float(b), s, e), d)

    # 6
    def test_us_sessions_and_us_returns(self):
        o = out(0)
        C = cal_dates(o)
        w = windows(C)
        j = joined(o)
        us = col(j, "us_n_sessions")
        self.assertTrue(np.array_equal(us, np.repeat([float(x[3]) for x in w], 3)))
        row = {d: i for i, d in enumerate(C)}
        for d, spot in SPOT.items():
            self.assertEqual(us[3 * row[dt.date.fromisoformat(d)]], float(spot[3]), d)
        none = us == 0
        self.assertTrue(none.any())
        for c in ("spy_oc", "ewj_oc", "fcx_oc", "copx_oc", "usdjpy_us_ret", "ewj_oc_jpy"):
            x = col(j, c)[none]
            self.assertTrue(((x == 0.0) | np.isnan(x)).all(), c)
        ewj, usd, jpy = col(j, "ewj_oc"), col(j, "usdjpy_us_ret"), col(j, "ewj_oc_jpy")
        self.assertTrue(np.array_equal(np.isnan(jpy), np.isnan(ewj)))
        present = ~np.isnan(ewj)
        self.assertTrue(np.array_equal(jpy[present], ewj[present] + usd[present]))

    # 7
    def test_calendar_flags(self):
        o = out(0)
        C = cal_dates(o)
        months = by_month(C)
        ym_all = sorted({(d.year, d.month) for d in C})
        ym_all = sorted(set(ym_all) | {(y, m) for y in range(C[0].year, C[-1].year + 1) for m in range(1, 13)
                                       if (C[0].year, C[0].month) <= (y, m) <= (C[-1].year, C[-1].month)})
        sq, sqm, got = set(), set(), set()
        for y, m in ym_all:
            r = roll_back(nth_weekday(y, m, 4, 2), C)
            if r is not None:
                sq.add(r)
                if m in (3, 6, 9, 12):
                    sqm.add(r)
            last = pycal.monthrange(y, m)[1]
            for day in [dd for dd in (5, 10, 15, 20, 25, 30) if dd <= last] + [last]:
                r = roll_back(dt.date(y, m, day), C)
                if r is not None:
                    got.add(r)
        boj = {ds[14] for (y, m), ds in months.items() if m in (1, 3, 4, 6, 7, 9, 10, 12) and len(ds) >= 15}
        self.assertEqual(len(boj), 89)
        exdiv = {months[(y, m)][-2] for y in range(2015, 2026) for m in (3, 9)}
        self.assertEqual(len(exdiv), 22)
        ex1306 = {months[(y, 7)][7] for y in range(2015, 2026)}
        self.assertEqual(len(ex1306), 11)
        j = joined(o)
        cd = [d for d in C for _ in range(3)]
        for c, s, kind in (("sq_day", sq, float), ("sq_major", sqm, float), ("gotobi_day", got, int),
                           ("boj_day", boj, float), ("exdiv_day", exdiv, int)):
            expected = np.array([kind(1) if d in s else kind(0) for d in cd])
            self.assertTrue(np.array_equal(j[c].to_numpy(), expected), c)
        div = np.array([DIV[i] if d in exdiv else 0.0 for d in C for i in range(3)])
        self.assertTrue(np.array_equal(col(j, "div_exdate"), div))
        d1306 = col(j, "ao_1306_gap_raw") - col(j, "ao_1306_gap_adj")
        on = np.array([d in ex1306 for d in cd])
        self.assertTrue((np.abs(d1306[on] + 0.02) <= TOL).all() and (np.abs(d1306[~on]) <= TOL).all())
        dtop = col(j, "ao_topix_gap_tradj") - col(j, "ao_topix_gap")
        on = np.array([d in exdiv for d in cd])
        self.assertTrue((np.abs(dtop[on] - 0.008) <= TOL).all() and (np.abs(dtop[~on]) <= TOL).all())

    # 8
    def test_events_table(self):
        o = out(0)
        ev = o.events
        self.assertEqual(tuple(ev.columns), SF.EVENT_COLUMNS)
        self.assertEqual([ev[c].dtype.kind for c in ev.columns], ["O", "M", "O", "O", "O", "O"])
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(ev["date"]))
        self.assertEqual(set(ev["category"]), {"TANSHIN", "STANDALONE_NEWS", "MECHANICAL", "AUDIT_CANDIDATE"})
        part = np.where(ev["date"] < pd.Timestamp("2022-01-01"), "dev", "conf")
        counts = ev.assign(part=part).groupby(["category", "part"]).size().to_dict()
        self.assertEqual(counts, {("TANSHIN", "dev"): 84, ("TANSHIN", "conf"): 60, ("STANDALONE_NEWS", "dev"): 42,
                                  ("STANDALONE_NEWS", "conf"): 25, ("MECHANICAL", "dev"): 21, ("MECHANICAL", "conf"): 12,
                                  ("AUDIT_CANDIDATE", "dev"): 21, ("AUDIT_CANDIDATE", "conf"): 12})
        self.assertEqual(len(ev), 277)
        self.assertTrue(ev.equals(ev.sort_values(["date", "ticker", "category"], kind="mergesort")
                                  .reset_index(drop=True)))
        self.assertTrue(ev.index.equals(pd.RangeIndex(len(ev))))
        self.assertFalse(ev.duplicated(["ticker", "date", "category"]).any())
        self.assertTrue(set(d.date() for d in ev["date"]) <= set(cal_dates(o)))
        self.assertEqual(set(ev["ticker"]), set(SF.TICKERS))
        for c in ("note", "check_status", "check_note"):
            self.assertEqual(set(ev[c]), {"synthetic"}, c)

    # 9
    def test_flags_follow_events(self):
        o = out(0)
        C = cal_dates(o)
        pos = {d: i for i, d in enumerate(C)}
        exp = {c: np.zeros((len(C), 3), dtype=np.int64) for c in ("earn_flag", "news_flag", "audit_flag", "mech_flag")}
        rule = {"TANSHIN": ("earn_flag", (0, 1)), "STANDALONE_NEWS": ("news_flag", (0, 1)),
                "AUDIT_CANDIDATE": ("audit_flag", (0, 1)), "MECHANICAL": ("mech_flag", (0,))}
        for t, d, cat in zip(o.events["ticker"], o.events["date"], o.events["category"]):
            name, offs = rule[cat]
            i = pos[d.date()]
            for off in offs:
                if i + off < len(C):
                    exp[name][i + off, SF.TICKERS.index(t)] = 1
        j = joined(o)
        for c, e in exp.items():
            self.assertTrue(np.array_equal(j[c].to_numpy(), e.reshape(-1)), c)

    # 10
    def test_t_conf_and_masks(self):
        o = out(0)
        T, common = CAL.t_conf(o.events, dates(o.dev))
        self.assertEqual(T, 1013)
        self.assertEqual([str(pd.Timestamp(d).date()) for d in common], list(SIX))
        self.assertEqual((o.truth["t_conf"], o.truth["excluded_all_three"]), (1013, list(SIX)))
        m = TG.add_masks(joined(o), o.events, SPEC)
        self.assertFalse((m["excl_inference"] & ~m["excl_d2"]).any())
        self.assertFalse((m["excl_forecast_eval"] & ~m["excl_inference"]).any())

    # 11
    def test_price_and_lag_identities(self):
        o = out(0)
        j = joined(o)
        n = len(j) // 3
        g = np.random.default_rng(o.truth["seed"]).spawn(5)[3]       # the row-level generator (module docstring)
        u_g, X = g.standard_normal((n, 3)), g.standard_exponential((n, 3))
        self.assertTrue(np.array_equal(0.008 * u_g.reshape(-1), o.components["gap_resid"].to_numpy()))
        for i, t in enumerate(SF.TICKERS):
            f = j.loc[j["ticker"] == t]
            pc, op, cl = col(f, "prev_close"), col(f, "open"), col(f, "close")
            adj, raw, y = col(f, "ao_gap_adj"), col(f, "ao_gap_raw"), col(f, "y_oc")
            div = col(f, "div_exdate")
            for r in range(len(f)):
                self.assertLessEqual(abs(op[r] - (pc[r] - div[r]) * math.exp(adj[r])), TOL)
                self.assertLessEqual(abs(raw[r] - math.log(op[r] / pc[r])), TOL)
                self.assertLessEqual(abs(cl[r] - op[r] * math.exp(y[r])), TOL)
            self.assertTrue(np.array_equal(pc[1:], cl[:-1]))
            self.assertEqual(pc[0], P0[i])
            self.assertTrue(np.array_equal(col(f, "gap_adj_lag1")[1:], adj[:-1]))
            self.assertTrue(np.array_equal(col(f, "oc_lag1")[1:], y[:-1]))
            self.assertTrue(np.array_equal(col(f, "topix_oc_lag1")[1:], col(f, "y_topix_oc")[:-1]))
            self.assertTrue(np.array_equal(col(f, "range_lag1")[1:], np.abs(y[:-1]) + 0.008 * X[:-1, i]))
            self.assertTrue((col(f, "range_lag1") >= np.abs(col(f, "oc_lag1"))).all())
            for x in (pc, op, cl):
                self.assertTrue((x > 0).all() and (x >= 0.2 * P0[i]).all() and (x <= 5 * P0[i]).all())

    # 12
    def test_truth_dict(self):
        o = out(1, SC1)
        tr = o.truth
        self.assertEqual(set(tr), {"source", "seed", "scenario", "constants", "break_date", "b_pre", "b_post",
                                   "b_ticker", "b_conf_mix", "f_2022", "f_2023_2026", "exact_target", "n_dev_dates",
                                   "n_conf_dates", "t_conf", "excluded_all_three"})
        cd = dates(o.confirm)
        n_pre, n_post = int((cd < BRK).sum()), int((cd >= BRK).sum())
        n_a = int(((cd >= pd.Timestamp("2023-01-01")) & (cd < BRK)).sum())
        self.assertEqual((n_pre, n_post, n_a), (695, 324, 451))
        b, d, dcc = SC1.b, SC1.delta_post, SC1.delta_cc
        self.assertEqual((tr["source"], tr["seed"], tr["scenario"], tr["break_date"]),
                         ("sim_full", seed(1), SC1.to_dict(), "2024-11-05"))
        self.assertEqual(tr["constants"], {"fe": list(S.FE), "spy_slope": list(S.SPY_SLOPE),
                                           "copx_slope": list(S.COPX_SLOPE), "sigma": list(S.DEFAULT_SIGMA),
                                           "pred_sd": [float(x) for x in S.PRED_SD], "price_start": list(P0),
                                           "dividend": list(DIV), "pull": 0.01})
        self.assertEqual((tr["b_pre"], tr["b_post"]), (b, b + d))
        self.assertEqual(tr["b_ticker"], {t: b + SC1.b_spread[i] for i, t in enumerate(SF.TICKERS)})
        self.assertAlmostEqual(tr["b_conf_mix"], (n_pre * b + n_post * (b + d)) / (n_pre + n_post), places=15)
        self.assertAlmostEqual(tr["f_2022"], b / dcc, places=15)
        self.assertAlmostEqual(tr["f_2023_2026"], ((n_a * b + n_post * (b + d)) / (n_a + n_post)) / dcc, places=15)
        self.assertEqual((tr["n_dev_dates"], tr["n_conf_dates"]), (1714, 1019))
        self.assertEqual((tr["t_conf"], tr["excluded_all_three"]), (1013, list(SIX)))
        self.assertTrue(tr["exact_target"])
        self.assertTrue(out(0).truth["exact_target"])
        self.assertFalse(out(6, SF.Scenario(b_mkt=0.2)).truth["exact_target"])

    # 13
    def test_components_identities(self):
        o = out(1, SC1)
        j, comp = joined(o), o.components
        tk = np.tile(np.arange(3), len(j) // 3)
        post = (j["date"] >= BRK).to_numpy()
        b_it = SC1.b + np.array(SC1.b_spread)[tk] + SC1.delta_post * post
        self.assertTrue(np.array_equal(comp["b_it"].to_numpy(), b_it))
        self.assertEqual(list(comp["part"]), ["dev"] * len(o.dev) + ["confirmation"] * len(o.confirm))
        fe, gam, kap = (np.array(v)[tk] for v in (S.FE, S.SPY_SLOPE, S.COPX_SLOPE))
        beta = np.array(SC1.beta_hedge)[tk]
        e, eur, spy, copx = (col(j, c) for c in ("usdjpy_ret", "eurusd_ret", "spy_oc", "copx_oc"))
        v_wo = (fe + b_it * e + SC1.a2 * eur + gam * spy + kap * copx + SC1.c_usd_sess * col(j, "c_usdjpy_sess_ret")
                + SC1.c_eur_sess * col(j, "c_eurusd_sess_ret") + SC1.b_gotobi * e * col(j, "gotobi_day"))
        resid = col(j, "y_oc") - beta * col(j, "y_1306_oc") - v_wo
        self.assertTrue((np.abs(resid - comp["resid"].to_numpy()) <= TOL).all())
        g_wo = ((SC1.delta_cc - b_it) * e + SC1.a2_gap * eur + 0.2 * spy
                - 0.01 * np.log(col(j, "prev_close") / np.array(P0)[tk]))
        gres = col(j, "ao_gap_adj") - beta * col(j, "ao_1306_gap_adj") - g_wo
        self.assertTrue((np.abs(gres - comp["gap_resid"].to_numpy()) <= TOL).all())

    # 14
    def test_residual_properties(self):
        o = out(1, SC1)
        j, comp = joined(o), o.components
        R = comp["resid"].to_numpy().reshape(-1, 3)
        for i, sigma in enumerate(S.DEFAULT_SIGMA):
            x = R[:, i]
            self.assertLess(abs(x.std() / sigma - 1), 0.10, i)
            self.assertLess(abs(np.corrcoef(x[1:], x[:-1])[0, 1] - SC1.phi), 0.08, i)
        Cm = np.corrcoef(R.T)
        self.assertTrue((np.abs(Cm[np.triu_indices(3, 1)] - SC1.resid_corr) < 0.08).all())
        r = comp["resid"].to_numpy()
        xs = [col(j, c) for c in ("usdjpy_ret", "eurusd_ret", "spy_oc", "copx_oc", "c_usdjpy_sess_ret")]
        xs.append(col(j, "usdjpy_ret") * col(j, "gotobi_day"))
        for x in xs:
            self.assertLess(abs(np.corrcoef(r, x)[0, 1]), 0.08)
        g = comp["gap_resid"].to_numpy()
        self.assertLess(abs(g.std() / 0.008 - 1), 0.10)
        self.assertLess(abs(np.corrcoef(g, col(j, "usdjpy_ret"))[0, 1]), 0.08)

    # 15
    def test_b_a2_and_break_recovered(self):
        o = out(2, SC2)
        D = I.build_design(targets_of(2, SC2), SPEC)
        dd = D.dates
        dev = dd < np.datetime64("2022-01-01")
        pre = (dd >= np.datetime64("2022-01-04")) & (dd < np.datetime64("2024-11-05"))
        post = dd >= np.datetime64("2024-11-05")
        self.assertRecovers(I.fit_dk(I.subset_design(D, dev), SPEC), "usdjpy_ret", o.truth["b_pre"])
        r = I.fit_dk(I.subset_design(D, pre), SPEC)
        self.assertRecovers(r, "usdjpy_ret", o.truth["b_pre"])
        self.assertRecovers(r, "eurusd_ret", SC2.a2)
        self.assertRecovers(I.fit_dk(I.subset_design(D, post), SPEC), "usdjpy_ret", o.truth["b_post"])
        D3 = I.build_design(targets_of(3), SPEC)
        conf3 = D3.dates >= np.datetime64("2022-01-04")
        self.assertRecovers(I.fit_dk(I.subset_design(D3, conf3), SPEC), "usdjpy_ret", out(3).truth["b_pre"])

    # 16
    def test_cc_and_raw_slopes(self):
        T = targets_of(2, SC2)
        Dc = I.build_design(T, SPEC, target="cc_abn")
        y2022 = (Dc.dates >= np.datetime64("2022-01-01")) & (Dc.dates <= np.datetime64("2022-12-31"))
        self.assertRecovers(I.fit_dk(I.subset_design(Dc, y2022), SPEC), "usdjpy_ret", SC2.delta_cc)
        Dr = I.build_design(T, SPEC, target="raw_oc")
        pre = (Dr.dates >= np.datetime64("2022-01-04")) & (Dr.dates < np.datetime64("2024-11-05"))
        self.assertRecovers(I.fit_dk(I.subset_design(Dr, pre), SPEC), "usdjpy_ret", SC2.b)

    # 17
    def test_default_missingness(self):
        o, sc = out(0), SF.Scenario()
        knobs = {"ewj_missing": ("ewj_oc", "ewj_oc_jpy"), "fcx_missing": ("fcx_oc",),
                 "sess_missing": ("c_usdjpy_sess_ret", "c_eurusd_sess_ret"),
                 "xau_missing": ("xau_ret", "xau_rv", "xau_bv", "xau_bars", "xau_stale_start_min", "xau_stale_end_min"),
                 "n225_missing": ("n225_ret", "n225_bars", "n225_stale_start_min", "n225_stale_end_min")}
        for p, f in enumerate((o.dev, o.confirm)):
            na = f.isna()
            touched = set()
            for name, cols in knobs.items():
                count = getattr(sc, name)[p]
                ref = None
                for c in cols:
                    by_date = na[c].groupby(f["date"])
                    self.assertTrue((by_date.all() == by_date.any()).all(), c)     # date-level
                    miss = set(by_date.all().index[by_date.all().to_numpy()])
                    self.assertEqual(len(miss), count, (p, c))
                    ref = miss if ref is None else ref
                    self.assertEqual(miss, ref, (p, c))
                if count:
                    touched |= set(cols)
            self.assertEqual(set(na.columns[na.any()]), touched, p)
            self.assertTrue((col(f, "usdjpy_bars") > 0).all())
            nk = f.iloc[::3]
            present = nk[["n225_ret", "n225_bars", "n225_stale_start_min", "n225_stale_end_min"]].notna().all(axis=1)
            stale = (nk["n225_stale_start_min"] > 5) | (nk["n225_stale_end_min"] > 5)
            self.assertLess(abs(stale[present].mean() - sc.n225_stale_share[p]), 0.05, p)
        zero = SF.Scenario(ewj_missing=(0, 0), fcx_missing=(0, 0), sess_missing=(0, 0), xau_missing=(0, 0),
                           n225_missing=(0, 0))
        o7 = out(7, zero)
        for f in (o7.dev, o7.confirm):
            self.assertFalse(f.isna().any().any())

    # 18
    def test_not_estimable_preset(self):
        ne = SF.Scenario.not_estimable()
        o = out(4, ne)
        xau = ("xau_ret", "xau_rv", "xau_bv", "xau_bars", "xau_stale_start_min", "xau_stale_end_min")
        self.assertTrue(o.confirm[list(xau)].isna().all().all())
        self.assertFalse(o.dev[list(xau)].isna().any().any())
        self.assertTrue((o.confirm["gotobi_day"] == 0).all())
        self.assertTrue((o.dev["gotobi_day"] == 1).any())
        for f, count in ((o.dev, 0), (o.confirm, 6)):
            zero = (f["usdjpy_bars"] == 0.0).to_numpy()
            for c in ("usdjpy_rv", "usdjpy_bv"):
                self.assertTrue(np.array_equal((f[c] == 0.0).to_numpy(), zero), c)
            zdates = set(f.loc[zero, "date"])
            self.assertEqual(len(zdates), count)
            self.assertEqual(int(zero.sum()), 3 * count)
            rows = f["date"].isin(zdates)
            self.assertEqual(int((f.loc[rows, "earn_flag"] + f.loc[rows, "news_flag"]).sum()), 0)
        in2022 = (o.confirm["date"] <= pd.Timestamp("2022-12-31")).to_numpy()
        for c in ("ao_1306_gap_adj", "ao_1306_gap_raw"):
            self.assertTrue(np.array_equal(o.confirm[c].isna().to_numpy(), in2022), c)
            self.assertFalse(o.dev[c].isna().any(), c)
        T = targets_of(4, ne)
        Tc = T.loc[T["date"] >= pd.Timestamp("2022-01-01")]
        Tc.attrs = dict(T.attrs)
        with self.assertRaises(I.DesignError):
            I.build_design(Tc, SPEC, secondary="fx_x_highrv")
        I.build_design(Tc, SPEC)
        self.assertTrue(T.loc[(T["date"] >= pd.Timestamp("2022-01-01"))
                              & (T["date"] <= pd.Timestamp("2022-12-31")), "cc_abn"].isna().all())

    # 19
    def test_seed_determinism(self):
        a, b = SF.simulate(seed(0)), SF.simulate(seed(0))
        for x, y in ((a.dev, b.dev), (a.confirm, b.confirm), (a.events, b.events), (a.components, b.components)):
            pd.testing.assert_frame_equal(x, y, check_exact=True)
        self.assertEqual(a.truth, b.truth)
        c = SF.simulate(seed(8))
        self.assertFalse(np.array_equal(col(a.dev, "y_oc"), col(c.dev, "y_oc")))

    # 20
    def test_module_source(self):
        src = MODULE.read_text(encoding="utf-8")
        tree = ast.parse(src)
        allowed = {"__future__", "dataclasses", "math", "typing", "numpy", "pandas"}
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                self.assertTrue({a.name for a in n.names} <= allowed, ast.dump(n))
            elif isinstance(n, ast.ImportFrom):
                if n.level == 0:
                    self.assertIn(n.module, allowed)
                else:
                    self.assertEqual((n.level, n.module), (1, None))
                    self.assertTrue({a.name for a in n.names} <= {"blind", "calendar", "schema", "sim"})
        banned = {"open", "read_csv", "read_table", "read_parquet", "read_json", "read_excel", "read_pickle", "to_csv",
                  "to_parquet", "to_json", "to_excel", "to_pickle", "read_text", "read_bytes", "write_text",
                  "write_bytes"}
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                name = n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", None)
                self.assertNotIn(name, banned, ast.dump(n.func))
        for s in ("load_dev", "load_confirm", "load_events", "OFILT_DATA_DIR"):
            self.assertNotIn(s, src)
            self.assertFalse([n for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
                              and s in n.value])
        top = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        top |= {t.id for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
        self.assertTrue({"simulate", "dev_calendar", "Scenario", "SimOutput", "COLUMNS", "INT_COLUMNS",
                         "BREAK_DATE"} <= top)


if __name__ == "__main__":
    unittest.main()
