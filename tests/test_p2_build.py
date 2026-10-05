"""P2-2 (Pass 2): tests of build/pass2/build_panel_p2.py on synthetic inputs generated in temporary
folders (tests/p2_synth.py). Covers:
* the string round-trip: old columns stay byte-identical (A′, P2-2 unit tests);
* the end-to-end append-only build: the frozen build run as in P2-0b, the old-column sources
  (Isaiah, 2026-10-05: dev = the original panel, sealed = the frozen output), every build-time
  assertion, the new columns' values against independent computations, and MANIFEST.json;
* the refusals: a wrong input, original-dev or frozen-output hash, or a non-empty output folder.
No real data is read: the expectations passed to build() are the synthetic files' own hashes and
counts. Log-derived values are compared within an explicit tolerance (Flag 16)."""
import dataclasses
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build" / "pass2"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import build_panel_p2 as B  # noqa: E402
import columns as C  # noqa: E402
import p2_synth as S  # noqa: E402

RTOL = 1e-12
NEW = [c for c, _ in C.NEW_COLUMNS]
PER_FLOAT = ("y_1306_oc", "ao_1306_gap_raw", "ao_1306_gap_adj", "topix_tr_component", "xau_ret", "xau_rv", "xau_bv",
             "xau_stale_start_min", "xau_stale_end_min", "n225_ret", "n225_stale_start_min", "n225_stale_end_min",
             "usdjpy_us_ret", "c_usdjpy_sess_ret", "c_eurusd_sess_ret")


def per_frame(dates) -> pd.DataFrame:
    n = len(dates)
    per = pd.DataFrame({c: np.linspace(1e-3, 2e-3, n) + i * 1e-4 for i, c in enumerate(PER_FLOAT)}, index=dates)
    per["xau_bars"] = [1079.0, np.nan, 2519.0][:n]
    per["n225_bars"] = [7.0, 8.0, np.nan][:n]
    per["gotobi_day"] = [0, 1, 0][:n]
    per["us_sessions_summed"] = [1, 0, 2][:n]
    return per


class TestStringRoundTrip(unittest.TestCase):
    def test_old_columns_byte_identical(self):
        num = pd.DataFrame({
            "date": ["2021-01-04", "2021-01-04", "2021-01-05", "2021-01-06"],
            "ticker": ["5713", "5711", "5713", "5713"],
            "ewj_oc": [1e-05, np.nan, -0.0, 0.1 + 0.2],
            "ao_topix_gap": [123456789.123456789, 2.5e-300, -0.004217, 0.0],
            "us_n_sessions": [1.0, 1.0, 0.0, 2.0],
            "window_start_utc": pd.to_datetime(["2020-12-30 06:00", "2020-12-30 06:00", "2021-01-04 06:00",
                                                "2021-01-05 06:00"]),
            "flag": [0, 1, 0, 1]})
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "old.csv"
            num.to_csv(src, index=False)
            old = B.read_old_panel(src)
            self.assertEqual(B.projection_sha256(old), B.sha256(src))
            final = B.append_new_columns(old, per_frame(["2021-01-04", "2021-01-05", "2021-01-06"]))
            self.assertEqual(list(final.columns), list(old.columns) + NEW)
            self.assertTrue(final[list(old.columns)].equals(old))
            out = Path(t) / "final.csv"
            final.to_csv(out, index=False)
            back = B.read_old_panel(out)
            self.assertTrue(back.iloc[:, :old.shape[1]].equals(old))
            self.assertEqual(B.projection_sha256(back.iloc[:, :old.shape[1]]), B.sha256(src))
            self.assertEqual(list(back["ewj_oc"]), ["1e-05", "", "-0.0", "0.30000000000000004"])
            self.assertEqual(list(back["xau_bars"]), ["1079", "1079", "", "2519"])       # Int64: no ".0"
            self.assertEqual(back.loc[1, "ewj_oc_jpy"], "")                              # NaN where ewj_oc is NaN
            us = per_frame(["2021-01-04", "2021-01-05", "2021-01-06"])["usdjpy_us_ret"]
            np.testing.assert_allclose(B.to_float(back["ewj_oc_jpy"]).iloc[[0, 2, 3]],
                                       np.array([1e-05, -0.0, 0.1 + 0.2]) + us.iloc[[0, 1, 2]].to_numpy(), rtol=RTOL)

    def test_missing_date_refused(self):
        old = pd.DataFrame({"date": ["2021-01-04", "2021-01-07"], "ticker": ["5713", "5713"],
                            "ewj_oc": ["0.1", "0.2"], "ao_topix_gap": ["0.0", "0.0"]})
        with self.assertRaisesRegex(B.BuildAssertion, "every panel date"):
            B.append_new_columns(old, per_frame(["2021-01-04", "2021-01-05"]))


def synthetic_expect(inp, orig, frozen_dev, frozen_sealed) -> B.Expect:
    real = B.real_expect()
    g = C.gotobi_flags(S.TOKYO)
    days = S.TOKYO[1:]
    return B.Expect(
        inputs={n: B.sha256(inp["raw"] / n) for n in B.RAW_INPUTS},
        events={n: B.sha256(inp["events"] / n) for n in real.events},
        code=real.code, orig_dev=B.sha256(orig), frozen_dev=frozen_dev, frozen_sealed=frozen_sealed, div_rows=2,
        gotobi_dev_per_ticker=int(g.reindex(days)[days < "2022-01-01"].sum()),
        gotobi_sealed_per_ticker=int(g.reindex(days)[days >= "2022-01-01"].sum()),
        early_closes=S.EARLY, reference_pairs={"synthetic": True})


class TestEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        t = Path(cls._tmp.name)
        cls.t = t
        cls.inp = S.make_inputs(t)
        fout = S.run_frozen(cls.inp["raw"], cls.inp["events"], t / "frozen")
        cls.frozen_dev, cls.frozen_sealed = B.sha256(fout / B.DEV_FILE), B.sha256(fout / B.SEALED_FILE)
        # the "original" dev panel differs from this platform's frozen output in one log-derived cell (Flag 16)
        d = B.read_old_panel(fout / B.DEV_FILE)
        d.loc[0, "y_oc"] = repr(float(np.nextafter(float(d.loc[0, "y_oc"]), np.inf)))
        cls.orig = t / "orig_panel_dev.csv"
        d.to_csv(cls.orig, index=False)
        cls.expect = synthetic_expect(cls.inp, cls.orig, cls.frozen_dev, cls.frozen_sealed)
        cls.out = t / "out"
        cls.manifest = B.build(cls.inp["raw"], cls.inp["events"], cls.orig, cls.out, expect=cls.expect)
        cls.dev = B.read_old_panel(cls.out / B.DEV_FILE)
        cls.sealed = B.read_old_panel(cls.out / B.SEALED_FILE)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def row(self, date, ticker="5713"):
        p = self.dev if date < "2022-01-01" else self.sealed
        return p[(p.date == date) & (p.ticker == ticker)].iloc[0]

    def test_outputs_and_manifest(self):
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), ["MANIFEST.json", B.SEALED_FILE, B.DEV_FILE])
        m = self.manifest
        for k in ("platform", "machine", "sys_version"):
            self.assertTrue(m["platform"][k], k)
        self.assertEqual(set(m["libraries"]), {"python", *B.LIBRARIES})
        self.assertEqual(set(m["inputs"]), set(B.RAW_INPUTS))
        self.assertEqual(set(m["event_files"]), {"events_firm.csv", "events_boj.csv"})
        self.assertEqual(m["original_dev_panel"]["sha256"], B.sha256(self.orig))
        self.assertEqual(set(m["code"]), {"build/pass1/build_panel.py", "build/pass1/make_events.py",
                                          "build/pass1/events.py", "build/pass2/build_panel_p2.py",
                                          "build/pass2/columns.py"})
        self.assertEqual(m["frozen_build_outputs"], {B.DEV_FILE: self.frozen_dev, B.SEALED_FILE: self.frozen_sealed})
        self.assertEqual([c["name"] for c in m["new_columns"]], NEW)
        for f, panel in ((B.DEV_FILE, self.dev), (B.SEALED_FILE, self.sealed)):
            o = m["outputs"][f]
            self.assertEqual(o["sha256"], B.sha256(self.out / f))
            self.assertEqual((o["rows"], o["columns"]), panel.shape)
            self.assertEqual(o["columns"], 60)
            self.assertEqual(o["span"], [panel.date.min(), panel.date.max()])
        self.assertEqual(m["build_assertions"]["passed"], len(m["build_assertions"]["names"]))
        self.assertGreater(m["build_assertions"]["passed"], 60)

    def test_old_columns_from_their_sources(self):
        dev_proj = B.projection_sha256(self.dev.iloc[:, :B.N_OLD])
        self.assertEqual(dev_proj, B.sha256(self.orig))                  # dev: the original panel's strings
        self.assertNotEqual(dev_proj, self.frozen_dev)                   # not this platform's frozen output
        self.assertEqual(B.projection_sha256(self.sealed.iloc[:, :B.N_OLD]), self.frozen_sealed)
        self.assertEqual(self.manifest["old_columns"]["dev"]["sha256"], B.sha256(self.orig))
        self.assertEqual(self.manifest["old_columns"]["sealed"]["sha256"], self.frozen_sealed)
        self.assertEqual(list(self.dev.columns[B.N_OLD:]), NEW)
        self.assertEqual(list(self.sealed.columns[B.N_OLD:]), NEW)

    def test_new_column_values(self):
        bars, b2, fx = self.inp["bars"], self.inp["book2"], self.inp["fixed"]
        jpy, xau = bars[S.USDJPY], bars[S.XAU]
        f = B.to_float

        def lr(df, c_lab, o_lab):
            return float(np.log(S.bar_close(df, c_lab) / S.bar_close(df, o_lab)))
        # usdjpy_us_ret, night 2024-11-05: NY 2024-11-01 (EDT; synthetic early close 13:00) + 2024-11-04 (EST)
        r = self.row("2024-11-05")
        np.testing.assert_allclose(float(r.usdjpy_us_ret),
                                   lr(jpy, "2024-11-01 16:59", "2024-11-01 13:29") + lr(jpy, "2024-11-04 20:59",
                                                                                         "2024-11-04 14:29"), rtol=RTOL)
        np.testing.assert_allclose(float(r.ewj_oc_jpy), float(r.ewj_oc) + float(r.usdjpy_us_ret), rtol=RTOL)
        # no US session on night 2024-11-01: exactly 0.0
        r = self.row("2024-11-01")
        self.assertEqual((r.us_n_sessions, float(r.usdjpy_us_ret), float(r.ewj_oc_jpy)), ("0.0", 0.0, 0.0))
        # EWJ stale on 2022-01-05: ewj_oc NaN on night 2022-01-06, and so ewj_oc_jpy
        r = self.row("2022-01-06")
        self.assertEqual((r.ewj_oc, r.ewj_oc_jpy), ("", ""))
        # session FX by day t: 15:00 JST on 2024-11-01, 15:30 JST on 2024-11-05
        np.testing.assert_allclose(float(self.row("2024-11-01").c_usdjpy_sess_ret),
                                   lr(jpy, "2024-11-01 05:59", "2024-10-31 23:59"), rtol=RTOL)
        np.testing.assert_allclose(float(self.row("2024-11-05").c_usdjpy_sess_ret),
                                   lr(jpy, "2024-11-05 06:29", "2024-11-04 23:59"), rtol=RTOL)
        # XAU over the usdjpy window, night 2024-11-06 (start 15:30 JST on 2024-11-05)
        r = self.row("2024-11-06")
        np.testing.assert_allclose(float(r.xau_ret), lr(xau, "2024-11-05 23:58", "2024-11-05 06:29"), rtol=RTOL)
        self.assertEqual((r.xau_bars, r.xau_stale_start_min, r.xau_stale_end_min), ("1049", "0.0", "0.0"))
        self.assertEqual((r.window_start_utc, r.window_end_utc), ("2024-11-05 06:30:00", "2024-11-05 23:59:00"))
        # 1306 on its ex-date 2020-10-05 (prev trading day 2020-10-02), stored amount 2.3
        s = fx["1306"].set_index("date")
        r = self.row("2020-10-05")
        np.testing.assert_allclose(float(r.y_1306_oc), np.log(s.close[pd.Timestamp("2020-10-05")] /
                                                              s.open[pd.Timestamp("2020-10-05")]), rtol=RTOL)
        np.testing.assert_allclose(float(r.ao_1306_gap_adj), np.log(s.open[pd.Timestamp("2020-10-05")] /
                                                                    (s.close[pd.Timestamp("2020-10-02")] - 2.3)), rtol=RTOL)
        self.assertNotEqual(r.ao_1306_gap_adj, r.ao_1306_gap_raw)
        # TOPIX TR component on 2020-10-02 (2020-10-01 dropped: previous day 2020-09-30)
        tr = fx["TOPIX optional"].set_index("date")["close"]
        pr = b2["TOPIX"].set_index("date")["close"]
        a, b = pd.Timestamp("2020-10-02"), pd.Timestamp("2020-09-30")
        r = self.row("2020-10-02")
        np.testing.assert_allclose(float(r.ao_topix_gap_tradj),
                                   float(r.ao_topix_gap) + np.log(tr[a] / tr[b]) - np.log(pr[a] / pr[b]), rtol=1e-9)
        # gotobi_day (P48) on every row
        g = C.gotobi_flags(S.TOKYO)
        for p in (self.dev, self.sealed):
            want = [g[pd.Timestamp(d)] for d in p.date]
            self.assertEqual([int(x) for x in p.gotobi_day], want)
        # the window instants of the new series are the panel's
        self.assertTrue((f(self.dev.xau_stale_end_min) >= 0).all())

    def test_refusals(self):
        raw, ev = self.inp["raw"], self.inp["events"]
        cases = (
            (dataclasses.replace(self.expect, orig_dev="0" * 64), "original dev panel"),
            (dataclasses.replace(self.expect, inputs={**self.expect.inputs, S.XAU: "0" * 64}), "input xauusd"),
            (dataclasses.replace(self.expect, frozen_dev="0" * 64), "frozen build's dev output"),
            (dataclasses.replace(self.expect, frozen_sealed="0" * 64), "frozen build's sealed output"),
        )
        for i, (ex, msg) in enumerate(cases):
            out = self.t / f"refused_{i}"
            with self.subTest(msg=msg), self.assertRaisesRegex(B.BuildAssertion, msg):
                B.build(raw, ev, self.orig, out, expect=ex)
            panels = sorted(p.name for p in out.iterdir()) if out.exists() else []
            self.assertEqual(panels, [], msg)                    # nothing written, temporary folder removed
        busy = self.t / "busy"
        busy.mkdir()
        (busy / "x").write_text("x")
        with self.assertRaisesRegex(B.BuildAssertion, "output folder"):
            B.build(raw, ev, self.orig, busy, expect=self.expect)


if __name__ == "__main__":
    unittest.main()
