"""P2-2 (Pass 2): unit tests of build/pass2/columns.py on synthetic minute bars and calendars with
known answers (builder prompt A′, item P2-2). Log-derived values are compared within an explicit
tolerance; instants, bar counts, staleness and flags are exact by construction (Flag 16: never
bit-identical floats across platforms). Also shows that the re-implemented routines give the same
output as the frozen build/pass1 code (Isaiah, 2026-10-05). No real data is read."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build" / "pass2"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import columns as C  # noqa: E402
import p2_synth as S  # noqa: E402

RTOL = 1e-12
T = pd.Timestamp


def bars(start, end, drop=()):
    """Continuous 1-minute bars (UTC labels) with a known close per label; `drop` removes labels."""
    labels = pd.date_range(start, end, freq="min", inclusive="left")
    labels = labels[~labels.isin(pd.DatetimeIndex([T(x) for x in drop]))]
    k = ((labels - T("2000-01-01")) // pd.Timedelta(minutes=1)).to_numpy().astype(float)
    close = 100.0 + 1e-3 * (k % 997) + 0.01 * np.sin(k / 7.0)
    return labels.to_numpy().astype("datetime64[ns]"), close, dict(zip(labels, close))


def ln(a, b):
    return float(np.log(a / b))


class TestFrozenReuse(unittest.TestCase):
    def test_frozen_module_is_build_pass1(self):
        self.assertEqual(Path(C.pass1.__file__).resolve(), (ROOT / "build" / "pass1" / "build_panel.py").resolve())
        for name in ("load_workbook", "load_fx", "fx_windows", "price_at", "jst_to_utc", "us_features"):
            self.assertTrue(callable(getattr(C.pass1, name)), name)
            self.assertNotIn(name, vars(C), name)          # reused by import, not re-implemented
        self.assertFalse((ROOT / "build" / "pass1" / "__pycache__").exists())   # build/pass1/ untouched

    def test_dark_window_is_frozen_fx_windows(self):
        ts, px, _ = bars("2024-10-31", "2024-11-07")
        cal = pd.DatetimeIndex(["2024-11-01", "2024-11-05", "2024-11-06"])
        self.assertTrue(C.dark_window(ts, px, cal, "xau").equals(C.pass1.fx_windows(ts, px, cal, "xau")))

    def test_new_columns_p50(self):
        names = [c for c, _ in C.NEW_COLUMNS]
        self.assertEqual(len(names), 19)
        self.assertEqual(len(set(names)), 19)
        groups = {}
        for c, g in C.NEW_COLUMNS:
            groups.setdefault(g, []).append(c)
        self.assertEqual(groups["PRE_OPEN_ROBUSTNESS"], ["xau_ret", "xau_rv", "xau_bv", "n225_ret", "usdjpy_us_ret",
                                                         "ewj_oc_jpy", "gotobi_day"])
        self.assertEqual(groups["PROVENANCE"], ["xau_bars", "xau_stale_start_min", "xau_stale_end_min", "n225_bars",
                                                "n225_stale_start_min", "n225_stale_end_min"])
        self.assertEqual(groups["TARGET_INPUTS"], ["y_1306_oc"])
        self.assertEqual(groups["AT_OPEN"], ["ao_1306_gap_raw", "ao_1306_gap_adj", "ao_topix_gap_tradj"])
        self.assertEqual(groups["CONTEMPORANEOUS"], ["c_usdjpy_sess_ret", "c_eurusd_sess_ret"])
        self.assertEqual(len(C.NYSE_EARLY_CLOSES), 23)


class TestPriceAndWindows(unittest.TestCase):
    def test_price_at_instant_rule(self):
        ts, px, p = bars("2024-11-05 10:00", "2024-11-05 10:10", drop=["2024-11-05 10:02", "2024-11-05 10:03"])
        price, stale, _ = C.pass1.price_at(ts, px, np.datetime64("2024-11-05T10:05", "ns"))
        self.assertEqual(price, p[T("2024-11-05 10:04")])      # last bar labelled <= X - 1 min
        self.assertEqual(stale, 0.0)
        price, stale, _ = C.pass1.price_at(ts, px, np.datetime64("2024-11-05T10:04", "ns"))
        self.assertEqual(price, p[T("2024-11-05 10:01")])      # 10:02 and 10:03 missing
        self.assertEqual(stale, 2.0)

    def test_dark_window_bounds_and_2024_11_05_close_change(self):
        ts, px, p = bars("2024-10-31", "2024-11-07")
        cal = pd.DatetimeIndex(["2024-11-01", "2024-11-05", "2024-11-06"])
        w = C.dark_window(ts, px, cal, "xau")
        # night 2024-11-05: prev 2024-11-01 closes 15:00 JST = 06:00 UTC; ends 08:59 JST = 2024-11-04 23:59 UTC
        self.assertEqual(w.loc["2024-11-05", "window_start_utc"], T("2024-11-01 06:00"))
        self.assertEqual(w.loc["2024-11-05", "window_end_utc"], T("2024-11-04 23:59"))
        # night 2024-11-06: prev 2024-11-05 closes 15:30 JST = 06:30 UTC
        self.assertEqual(w.loc["2024-11-06", "window_start_utc"], T("2024-11-05 06:30"))
        self.assertEqual(w.loc["2024-11-06", "window_end_utc"], T("2024-11-05 23:59"))
        np.testing.assert_allclose(w.loc["2024-11-06", "xau_ret"],
                                   ln(p[T("2024-11-05 23:58")], p[T("2024-11-05 06:29")]), rtol=RTOL)
        self.assertEqual(w.loc["2024-11-06", "xau_bars"], (23 * 60 + 58) - (6 * 60 + 29))
        lab = pd.date_range("2024-11-05 06:29", "2024-11-05 23:58", freq="min")
        r = np.diff(np.log([p[x] for x in lab]))
        np.testing.assert_allclose(w.loc["2024-11-06", "xau_rv"], float((r ** 2).sum()), rtol=1e-9)
        np.testing.assert_allclose(w.loc["2024-11-06", "xau_bv"],
                                   float(np.pi / 2 * (np.abs(r[1:]) * np.abs(r[:-1])).sum()), rtol=1e-9)
        inst = C.dark_window_instants(cal)
        pd.testing.assert_frame_equal(inst, w[["window_start_utc", "window_end_utc"]], check_dtype=False)

    def test_endpoint_staleness(self):
        ts, px, _ = bars("2024-10-31", "2024-11-07",
                         drop=["2024-11-05 06:27", "2024-11-05 06:28", "2024-11-05 06:29",
                               "2024-11-05 23:56", "2024-11-05 23:57", "2024-11-05 23:58"])
        cal = pd.DatetimeIndex(["2024-11-05", "2024-11-06"])
        w = C.dark_window(ts, px, cal, "n225")
        self.assertEqual(w.loc["2024-11-06", "n225_stale_start_min"], 3.0)
        self.assertEqual(w.loc["2024-11-06", "n225_stale_end_min"], 3.0)

    def test_night_without_bars(self):
        ts, px, _ = bars("2024-11-04", "2024-11-05 06:00")       # nothing after the window opens
        cal = pd.DatetimeIndex(["2024-11-05", "2024-11-06"])
        w = C.dark_window(ts, px, cal, "xau")
        self.assertEqual(list(w.index), [T("2024-11-06")])
        self.assertEqual(list(w.columns), [])                    # fx_windows records only the date that night
        self.assertTrue(np.isnan(w.reindex(columns=["xau_ret"]).loc["2024-11-06", "xau_ret"]))
        inst = C.dark_window_instants(cal)
        self.assertEqual(inst.loc["2024-11-06", "window_start_utc"], T("2024-11-05 06:30"))

    def test_dark_window_instants_match_frozen(self):
        ts, px, _ = bars("2020-09-24", "2020-10-09")
        cal = S.TOKYO[:7]
        w = C.pass1.fx_windows(ts, px, cal, "usdjpy")
        pd.testing.assert_frame_equal(C.dark_window_instants(cal), w[["window_start_utc", "window_end_utc"]],
                                      check_dtype=False)


class TestSessionFx(unittest.TestCase):
    def test_session_window_by_day_t(self):
        ts, px, p = bars("2024-10-31", "2024-11-07")
        cal = pd.DatetimeIndex(["2024-11-01", "2024-11-05", "2024-11-06"])
        s = C.session_fx(ts, px, cal, "usdjpy")
        # 09:00:00 JST = close of the bar labelled 08:59 JST (23:59 UTC the day before)
        self.assertEqual(s.loc["2024-11-01", "session_open_utc"], T("2024-11-01 00:00"))
        self.assertEqual(s.loc["2024-11-01", "session_close_utc"], T("2024-11-01 06:00"))   # 15:00 JST
        self.assertEqual(s.loc["2024-11-05", "session_close_utc"], T("2024-11-05 06:30"))   # 15:30 JST, by day t
        np.testing.assert_allclose(s.loc["2024-11-01", "c_usdjpy_sess_ret"],
                                   ln(p[T("2024-11-01 05:59")], p[T("2024-10-31 23:59")]), rtol=RTOL)
        np.testing.assert_allclose(s.loc["2024-11-05", "c_usdjpy_sess_ret"],
                                   ln(p[T("2024-11-05 06:29")], p[T("2024-11-04 23:59")]), rtol=RTOL)
        self.assertEqual(C.session_close_jst(T("2024-11-04")), (15, 0))
        self.assertEqual(C.session_close_jst(T("2024-11-05")), (15, 30))


class TestUsSession(unittest.TestCase):
    def test_ny_dst_and_early_close_instants(self):
        cases = {"2024-03-08": ("14:30", "21:00"),     # EST
                 "2024-03-11": ("13:30", "20:00"),     # EDT (DST began 2024-03-10)
                 "2024-11-01": ("13:30", "20:00"),     # EDT
                 "2024-11-04": ("14:30", "21:00")}     # EST (DST ended 2024-11-03)
        for day, (o, c) in cases.items():
            t0, t1 = C.us_session_instants(T(day), ())
            self.assertEqual(T(t0), T(f"{day} {o}"), day)
            self.assertEqual(T(t1), T(f"{day} {c}"), day)
        _, t1 = C.us_session_instants(T("2024-11-29"), C.NYSE_EARLY_CLOSES)   # early close, EST
        self.assertEqual(T(t1), T("2024-11-29 18:00"))
        _, t1 = C.us_session_instants(T("2024-07-03"), C.NYSE_EARLY_CLOSES)   # early close, EDT
        self.assertEqual(T(t1), T("2024-07-03 17:00"))

    def test_usdjpy_us_ret(self):
        ts, px, p = bars("2024-03-05", "2024-03-14")
        cal = pd.DatetimeIndex(["2024-03-06", "2024-03-07", "2024-03-11", "2024-03-12", "2024-03-13"])
        uscal = pd.DatetimeIndex(["2024-03-06", "2024-03-07", "2024-03-08", "2024-03-11"])
        r = C.usdjpy_us_ret(ts, px, uscal, cal, early_closes=("2024-03-08",))

        def leg(o_lab, c_lab):
            return ln(p[T(c_lab)], p[T(o_lab)])
        np.testing.assert_allclose(r.loc["2024-03-07", "usdjpy_us_ret"],          # one session, EST
                                   leg("2024-03-06 14:29", "2024-03-06 20:59"), rtol=RTOL)
        np.testing.assert_allclose(r.loc["2024-03-11", "usdjpy_us_ret"],          # two sessions; 03-08 closes 13:00 ET
                                   leg("2024-03-07 14:29", "2024-03-07 20:59") + leg("2024-03-08 14:29", "2024-03-08 17:59"),
                                   rtol=RTOL)
        np.testing.assert_allclose(r.loc["2024-03-12", "usdjpy_us_ret"],          # one session, EDT
                                   leg("2024-03-11 13:29", "2024-03-11 19:59"), rtol=RTOL)
        self.assertEqual(r.loc["2024-03-13", "usdjpy_us_ret"], 0.0)               # no US session: exactly 0.0
        self.assertEqual(list(r["us_sessions_summed"]), [1, 2, 1, 0])
        us = {t: pd.DataFrame({"open": 1.0, "close": 1.01}, index=uscal) for t in ("SPY", "EWJ", "FCX", "COPX")}
        frozen = C.pass1.us_features(us, uscal, cal)
        self.assertEqual(list(frozen["us_n_sessions"]), list(r["us_sessions_summed"]))

    def test_us_session_dates_match_frozen(self):
        us = {t: pd.DataFrame({"open": 1.0, "close": 1.01}, index=S.US) for t in ("SPY", "EWJ", "FCX", "COPX")}
        frozen = C.pass1.us_features(us, S.US, S.TOKYO)["us_n_sessions"]
        mine = pd.Series({d: len(s) for d, s in C.us_session_dates(S.US, S.TOKYO).items()})
        self.assertEqual(list(frozen), list(mine))
        self.assertEqual(list(frozen.index), list(mine.index))
        self.assertEqual(mine[T("2024-11-01")], 0)


class TestGotobi(unittest.TestCase):
    def check(self, cal, flagged, rolls):
        g = C.gotobi_flags(cal)
        self.assertEqual([C.day_key(d) for d in g.index[g == 1]], flagged)
        self.assertTrue(set(g.unique()) <= {0, 1})
        crossing = [(C.day_key(n), C.day_key(t)) for n, t in C.gotobi_map(cal) if (n.year, n.month) != (t.year, t.month)]
        self.assertEqual(crossing, rolls)

    def test_month_crossing_rolls(self):
        self.check(S.bdays("2019-04-22", "2019-05-10", ["2019-04-29", "2019-04-30", "2019-05-01", "2019-05-02",
                                                       "2019-05-03", "2019-05-06"]),
                   ["2019-04-25", "2019-04-26", "2019-05-10"], [("2019-05-05", "2019-04-26")])
        self.check(S.bdays("2019-12-23", "2020-01-10", ["2019-12-31", "2020-01-01", "2020-01-02", "2020-01-03"]),
                   ["2019-12-25", "2019-12-30", "2020-01-10"], [("2020-01-05", "2019-12-30")])
        self.check(S.bdays("2021-04-26", "2021-05-14", ["2021-04-29", "2021-05-03", "2021-05-04", "2021-05-05"]),
                   ["2021-04-30", "2021-05-10"], [("2021-05-05", "2021-04-30")])
        self.check(S.bdays("2024-12-23", "2025-01-10", ["2024-12-31", "2025-01-01", "2025-01-02", "2025-01-03"]),
                   ["2024-12-25", "2024-12-30", "2025-01-10"], [("2025-01-05", "2024-12-30")])

    def test_february(self):
        self.check(S.bdays("2024-02-01", "2024-03-08", ["2024-02-12", "2024-02-23"]),       # leap year: the 29th
                   ["2024-02-05", "2024-02-09", "2024-02-15", "2024-02-20", "2024-02-22", "2024-02-29",
                    "2024-03-05"], [])
        self.check(S.bdays("2023-02-01", "2023-03-03", ["2023-02-23"]),                     # the 28th; no 30th
                   ["2023-02-03", "2023-02-10", "2023-02-15", "2023-02-20", "2023-02-24", "2023-02-28"], [])

    def test_30th_and_31st_on_a_weekend(self):
        cal = S.bdays("2024-03-18", "2024-04-05", ["2024-03-20"])     # 2024-03-30 Sat, 03-31 Sun
        self.check(cal, ["2024-03-19", "2024-03-25", "2024-03-29", "2024-04-05"], [])
        g = C.gotobi_flags(cal)
        self.assertEqual(g[T("2024-03-29")], 1)                          # one flag, the union
        self.assertEqual(sorted(C.day_key(n) for n, t in C.gotobi_map(cal) if C.day_key(t) == "2024-03-29"),
                         ["2024-03-30", "2024-03-31"])


class Test1306AndTopix(unittest.TestCase):
    def test_dividend_adjusted_gap_identity(self):
        cal = pd.DatetimeIndex(["2024-07-01", "2024-07-02", "2024-07-03", "2024-07-04"])
        px = pd.DataFrame({"open": [100.0, 101.0, 99.0, 98.5], "close": [100.5, 100.0, 98.0, 99.0],
                           "high": 102.0, "low": 97.0}, index=cal)
        D = 2.5
        h = C.hedge_1306(px, pd.Series({T("2024-07-03"): D}), cal)
        np.testing.assert_allclose(h["y_1306_oc"], np.log(px.close / px.open), rtol=RTOL)
        np.testing.assert_allclose(np.exp(h.loc["2024-07-03", "ao_1306_gap_adj"]) * (100.0 - D), 99.0, rtol=RTOL)
        np.testing.assert_allclose(h.loc["2024-07-03", "ao_1306_gap_adj"] - h.loc["2024-07-03", "ao_1306_gap_raw"],
                                   -np.log(1 - D / 100.0), rtol=1e-9)
        for d in ("2024-07-02", "2024-07-04"):          # no distribution: adj is raw, exactly (prev - 0.0 == prev)
            self.assertEqual(h.loc[d, "ao_1306_gap_adj"], h.loc[d, "ao_1306_gap_raw"])
        self.assertTrue(np.isnan(h.loc["2024-07-01", "ao_1306_gap_raw"]))

    def test_tradj_component_on_an_ex_date(self):
        cal = pd.DatetimeIndex(["2024-07-01", "2024-07-02", "2024-07-03"])
        pr = pd.Series([2000.0, 2010.0, 1990.0], index=cal)
        q = 0.0123                                       # dividend points as a share of the index on 07-03
        tr = pd.Series([3000.0, 3000.0 * 2010 / 2000, 3000.0 * 1990 / 2000 * (1 + q)], index=cal)
        comp = C.topix_tr_component(tr, pr)
        self.assertTrue(np.isnan(comp.iloc[0]))
        np.testing.assert_allclose(comp.iloc[1], 0.0, atol=1e-12)
        np.testing.assert_allclose(comp.iloc[2], np.log(1 + q), rtol=1e-9)

    def test_parsers_match_frozen_load_workbook(self):
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "Book2.xlsx"
            S.write_sheets(path, S.book2_sheets())
            px, top, us, div, cal, uscal = C.pass1.load_workbook(path)
            X = pd.read_excel(path, sheet_name=None, header=None)
            for tk in ("5713", "5711", "5706"):
                self.assertTrue(C.parse_price_sheet(X[tk]).equals(px[tk]), tk)
                series, used = C.parse_dividends(X[f"{tk} dividends"])
                self.assertTrue(series.equals(div[tk]), tk)
                self.assertEqual(len(used), 1)

    def test_dividends_use_stored_amounts_and_cash_types(self):
        sheet = S.fixed_sheets()["1306 dividends"]
        series, used = C.parse_dividends(sheet)
        self.assertEqual(len(used), 2)                   # the 'Distribution' row is not a cash type
        self.assertEqual(set(used["type"]), {"Regular Cash"})
        self.assertEqual(list(series.values), [2.3, 3.1])    # the stored values, not RAW / 10


if __name__ == "__main__":
    unittest.main()
