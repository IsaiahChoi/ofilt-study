"""P4-4b2 (P4Q37): ofilt/drift/confirm_economic.py against docs/P4_CONFIRM_ECON_SPEC.md (version 1). Exactly the 14
test methods of its §6.2. Seeds are the spec seed + 8,300,000 + k (§6.1), disjoint from every earlier block. Every
frame is synthetic, with 5706's open, close and prev_close multiplied by 0.1 so that its traded prices stay inside the
tick tables (§6.1); frames labelled dev_real or confirm_real appear only in test 13's refused pairs. Every run_calls
uses a zero-forecast M7 stand-in. The run registry is patched to a temporary folder for the whole module. Expected
values are recomputed from calls.main.ev, the test's own T and tools/p3_1_sesoi.py, never from the module."""
import ast
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import p3_1_sesoi as P31  # noqa: E402
from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import confirm_economic as CE  # noqa: E402
from ofilt.drift import confirm_forecast as CF  # noqa: E402
from ofilt.drift import confirm_inference as CI  # noqa: E402
from ofilt.drift import forecast as FC  # noqa: E402
from ofilt.drift import registry as RG  # noqa: E402
from ofilt.drift import sim_full as SF  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

SPEC = Spec.load()
MODULE = ROOT / "ofilt" / "drift" / "confirm_economic.py"
SA = SF.Scenario(b=1.0, a2=0.6, delta_cc=1.5)
CALENDARS = {"SHORT": SF.dev_calendar()[-900:], "TINY": SF.dev_calendar()[-300:], "DEFAULT": None}
RUN_SPECS = {"E1": (1, "SHORT", "confirmation"), "E3": (3, "DEFAULT", "dev"), "E4": (4, "TINY", "dev")}
ENTRY_KEYS = ["id", "item", "status", "values", "reason", "n_rows", "n_dates", "lag"]
COMPONENTS = ("mean_rt", "miner_commission", "miner_execution", "hedge_leg", "short", "c_m", "c_h", "x_h", "s")
_PATCHES: list = []
_TMP = None
_CACHE: dict = {}


class ZeroM7(FC.ForecastModel):
    """The M7 stand-in of §6.1: no feature, a zero forecast, no noise column."""
    name, features = "M7", ()

    def fit(self, X, y, ctx):
        pass

    def predict(self, X, ctx):
        return np.zeros(len(X))


def setUpModule():
    global _TMP
    _TMP = tempfile.TemporaryDirectory()
    folder = Path(_TMP.name)
    for attr, name in (("SYNTHETIC_PATH", "synthetic.jsonl"), ("REAL_PATH", "real.jsonl")):
        p = mock.patch.object(RG, attr, folder / name)
        p.start()
        _PATCHES.append(p)


def tearDownModule():
    for p in reversed(_PATCHES):
        p.stop()
    _TMP.cleanup()


def seed(k):
    return SPEC.seed + 8_300_000 + k


def scaled(df):
    """A copy with 5706's open, close and prev_close multiplied by 0.1, attrs kept (§6.1)."""
    out = df.copy()
    m = (out["ticker"].astype(str) == "5706").to_numpy()
    for c in ("open", "close", "prev_close"):
        out[c] = np.where(m, out[c].to_numpy(dtype=float) * 0.1, out[c].to_numpy(dtype=float))
    out.attrs = dict(df.attrs)
    return out


def frames(label):
    """(dev, events, confirm or None) of a run, scaled."""
    if ("frames", label) not in _CACHE:
        k, cal, mode = RUN_SPECS[label]
        dates = CALENDARS[cal]
        o = SF.simulate(seed(k), SA) if dates is None else SF.simulate(seed(k), SA, dev_dates=dates)
        _CACHE[("frames", label)] = (scaled(o.dev), o.events, scaled(o.confirm) if mode == "confirmation" else None)
    return _CACHE[("frames", label)]


def calls_of(label):
    if ("calls", label) not in _CACHE:
        dev, events, conf = frames(label)
        _CACHE[("calls", label)] = CF.run_calls(dev, events, conf, spec=SPEC, factories={"M7": ZeroM7})
    return _CACHE[("calls", label)]


def entry_of(label):
    if ("entry", label) not in _CACHE:
        dev, events, conf = frames(label)
        _CACHE[("entry", label)] = CE.economic_row(calls_of(label), dev, events, conf, spec=SPEC)
    return _CACHE[("entry", label)]


def frame_T(label):
    """The test's own T (§3.1 of the forecasting specification)."""
    dev, events, conf = frames(label)
    J = pd.concat([dev, conf], ignore_index=True) if conf is not None else dev.copy()
    J.attrs = {"provenance": B.SYNTHETIC}
    return TG.add_masks(TG.add_targets(J, SPEC), events, SPEC)


def model_rows(calls, model):
    ev = calls.main.ev
    return ev.loc[ev["model"] == model].sort_values(["date", "ticker"], kind="mergesort").reset_index(drop=True)


def test_px(label):
    """The test's px: its own T's date, ticker, open, close and beta at the M3 rows' keys, in their order."""
    if ("px", label) not in _CACHE:
        T = frame_T(label)
        R = model_rows(calls_of(label), "M3")
        tk = pd.MultiIndex.from_arrays([T["date"].to_numpy(), T["ticker"].astype(str).to_numpy()])
        pos = tk.get_indexer(pd.MultiIndex.from_arrays([R["date"].to_numpy(), R["ticker"].astype(str).to_numpy()]))
        assert (pos >= 0).all()
        _CACHE[("px", label)] = T.iloc[pos][["date", "ticker", "open", "close", "beta"]].reset_index(drop=True)
    return _CACHE[("px", label)]


def tool_rt(px, inputs):
    """Per-row round trips per case by costs' formula, with the tool's own helpers (tools/p3_1_sesoi.py)."""
    tk = px["ticker"].astype(str).to_numpy()
    beta = px["beta"].to_numpy(float)
    win = np.zeros(len(px), dtype=bool)
    for t, w in ((t, w) for t, w in inputs["flag4_windows"].items() if not t.startswith("_")):
        win |= (tk == t) & (px["date"] < pd.Timestamp(w["before"])).to_numpy()
    out = {}
    for case in P31.CASES:
        c_m, c_h = float(inputs["commission_miners_bp"][case]), float(inputs["commission_1306_bp"][case])
        imp_m, imp_h = float(inputs["impact_miners_bp"][case]), float(inputs["impact_1306_bp"][case])
        s = float(inputs["short_cost_per_day_bp"][case])
        ht_h = inputs["half_tick_1306_bp"][case]
        if case == "primary":
            prim = {side: P31.side_ticks_table(px, inputs, inputs["primary_table"], side) for side in P31.SIDES}
            x_side = {side: np.maximum(imp_m, P31.half_tick_bp(*prim[side])) for side in P31.SIDES}
            xm_t = {t: float(np.mean(np.r_[x_side["open"][(tk == t) & ~win], x_side["close"][(tk == t) & ~win]]))
                    for t in sorted(set(tk))}
            x_m, x_h = np.array([xm_t[t] for t in tk]), max(imp_h, float(ht_h))
        elif case == "low":
            x_m, x_h = np.full(len(px), imp_m), imp_h
        else:
            st = P31.side_ticks(px, inputs, None)
            x_m = imp_m + 0.5 * (P31.half_tick_bp(st["open"][0], st["open"][1])
                                 + P31.half_tick_bp(st["close"][0], st["close"][1]))
            x_h = imp_h + float(ht_h)
        out[case] = 2 * (c_m + x_m) + beta * 2 * (c_h + x_h) + s
    return out


def relabel(df, provenance):
    r = df.copy()
    attrs = {k: v for k, v in df.attrs.items() if k != "provenance"}
    if provenance is not None:
        attrs["provenance"] = provenance
    r.attrs = attrs
    return r


def ht(t, p):
    """Half a tick in bp, by hand."""
    return 1e4 * 0.5 * t / p


class TestConfirmEconomic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = P31.load_inputs()            # docs/P3_COST_INPUTS.json, through the tool (not data)

    # 1
    def test_cost_inputs_pin_and_refusal(self):
        data = CE.COST_INPUTS_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), CE.COST_INPUTS_SHA256)
        obj = json.loads(data.decode("utf-8"))
        self.assertEqual(CE.load_cost_inputs(), obj)
        bad = bytearray(data)
        bad[data.index(b"decided")] ^= 0x01
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "P3_COST_INPUTS.json"
            p.write_bytes(bytes(bad))
            with self.assertRaises(ValueError):
                CE.load_cost_inputs(p)
        self.assertIsNone(CE.check_cost_inputs(obj))
        with self.assertRaises(ValueError):
            CE.check_cost_inputs({k: v for k, v in obj.items() if k != "flag4_windows"})

    # 2
    def test_round_trips_match_the_tool(self):
        px = test_px("E1")
        mine = CE.round_trips(px, self.inputs)
        tool = P31.costs(px, self.inputs)
        for case in CE.CASES:
            for k in COMPONENTS:
                self.assertLessEqual(abs(mine[case][k] - tool[case][k]), 1e-12, (case, k))
        self.assertLessEqual(abs(mine["beta_bar"] - tool["beta_bar"]), 1e-12)
        for case, key in (("primary", "primary_xm"), ("high", "high_xm")):
            self.assertEqual(sorted(mine[case]["x_m_by_ticker"]), sorted(tool["detail"][key]))
            for t, v in tool["detail"][key].items():
                self.assertLessEqual(abs(mine[case]["x_m_by_ticker"][t] - v), 1e-12, (case, t))

    # 3
    def test_round_trips_hand_computation(self):
        px = pd.DataFrame({
            "date": pd.to_datetime(["2023-03-01"] * 3 + ["2023-03-02"] * 3),
            "ticker": ["5706", "5711", "5713"] * 2,
            "open": [95.0, 2800.0, 600.0, 120.0, 900.0, 3000.0],     # 5706 traded = stored x 10 (f = 1/10)
            "close": [250.0, 4000.0, 12000.0, 400.0, 20000.0, 8000.0],
            "beta": [0.9, 1.1, 1.2, 1.0, 0.8, 1.3]})
        beta = px["beta"].to_numpy()
        # primary, the fine table: x_m per ticker = mean over its rows and sides of max(2, half tick)
        xm = {"5706": np.mean([max(2, ht(0.1, 950)), max(2, ht(0.5, 1200)), max(2, ht(0.5, 2500)), max(2, ht(1, 4000))]),
              "5711": np.mean([max(2, ht(0.5, 2800)), max(2, ht(0.1, 900)), max(2, ht(1, 4000)), max(2, ht(5, 20000))]),
              "5713": np.mean([max(2, ht(0.1, 600)), max(2, ht(0.5, 3000)), max(2, ht(5, 12000)), max(2, ht(1, 8000))])}
        rt_p = np.array([2 * (4.3 + xm[t]) + b * 2 * (4.3 + max(1.5, 1.25)) + 0 for t, b in zip(px["ticker"], beta)])
        rt_l = np.array([2 * (0 + 0.5) + b * 2 * (0 + 0.5) + 0 for b in beta])
        # high, the dev tables (5706 and 5711 standard, 5713 fine): x_m per row = 8 + mean of its sides' half ticks
        xh = 8 + 0.5 * np.array([ht(1, 950) + ht(1, 2500), ht(1, 2800) + ht(5, 4000), ht(0.1, 600) + ht(5, 12000),
                                 ht(1, 1200) + ht(5, 4000), ht(1, 900) + ht(10, 20000), ht(0.5, 3000) + ht(1, 8000)])
        rt_h = 2 * (8 + xh) + beta * 2 * (8 + 4 + 4.2) + 1
        r = CE.round_trips(px, self.inputs)
        for case, rt in (("primary", rt_p), ("low", rt_l), ("high", rt_h)):
            self.assertEqual(r[case]["rt"].shape, (6,), case)
            self.assertLessEqual(float(np.max(np.abs(r[case]["rt"] - rt))), 1e-12, case)
        self.assertGreater(xm["5706"], 2.0)           # a half tick above the impact (2.083 bp at 1,200 yen)
        self.assertEqual(xm["5711"], 2.0)             # the impact floor binds

    # 4
    def test_pnl_bp(self):
        y = np.array([0.01, -0.02, 0.005, -0.004])
        yhat = np.array([0.3, -0.1, 0.0, 0.2])
        rt = np.array([20.0, 20.0, 20.0, 15.0])
        gross, net = CE.pnl_bp(y, yhat, rt)
        self.assertTrue(np.allclose(gross, [100.0, 200.0, 0.0, -40.0], rtol=0, atol=1e-12))
        self.assertTrue(np.allclose(net, [80.0, 180.0, 0.0, -55.0], rtol=0, atol=1e-12))
        self.assertEqual((gross[2], net[2]), (0.0, 0.0))

    # 5
    def test_entry_schema_and_fill(self):
        e = entry_of("E1")
        self.assertEqual(list(e), ENTRY_KEYS)
        self.assertEqual((e["id"], e["item"], e["status"]), ("O45", "P4-4b", "estimated"))
        dev, events, conf = frames("E1")
        d1 = CF.fill(CI.infer(dev, events, conf), CF.forecast_rows(calls_of("E1")))
        d2 = CE.fill(d1, e)
        self.assertEqual([r for r, x in d2["rows"].items() if x["item"] == "P4-4b" and x["status"] == "pending"], [])
        self.assertEqual(d2["rows"]["O45"], e)
        self.assertEqual({k: v for k, v in d2["rows"].items() if k != "O45"},
                         {k: v for k, v in d1["rows"].items() if k != "O45"})
        self.assertEqual({k: d2[k] for k in d2 if k != "rows"}, {k: d1[k] for k in d1 if k != "rows"})
        text = CI.to_json(d2)
        self.assertNotIn("NaN", text)
        self.assertNotIn("Infinity", text)
        self.assertEqual(json.loads(text), d2)
        with self.assertRaises(ValueError):
            CE.fill(d2, e)                                         # O45 no longer pending
        with self.assertRaises(ValueError):
            CE.fill(d1, dict(e, id="O44"))

    # 6
    def test_break_even_and_difference(self):
        calls, v = calls_of("E1"), entry_of("E1")["values"]
        ev = calls.main.ev
        be, share = {}, {}
        for m in ("M3", "M2"):
            r = ev.loc[ev["model"] == m]
            s = np.sign(r["yhat"].to_numpy(dtype=float))
            be[m] = 1e4 * float(np.mean(s * r["y"].to_numpy(dtype=float)))
            share[m] = float(np.mean(s != 0))
            self.assertLessEqual(abs(v["break_even_bp"][m] - be[m]), 1e-12, m)
        self.assertLessEqual(abs(v["break_even_bp"]["difference"] - (be["M3"] - be["M2"])), 1e-12)
        self.assertEqual(v["break_even_bp"]["difference"], v["break_even_bp"]["M3"] - v["break_even_bp"]["M2"])
        self.assertEqual(v["traded_share"], share)

    # 7
    def test_net_pnl(self):
        calls, v = calls_of("E1"), entry_of("E1")["values"]
        rt = tool_rt(test_px("E1"), self.inputs)
        for m in ("M3", "M2"):
            r = model_rows(calls, m)
            s = np.sign(r["yhat"].to_numpy(dtype=float))
            for case in CE.CASES:
                net = float(np.mean(1e4 * s * r["y"].to_numpy(dtype=float) - rt[case] * np.abs(s)))
                self.assertLessEqual(abs(v["net_bp"][m][case] - net), 1e-9, (m, case))

    # 8
    def test_rows_beta_and_prices(self):
        calls, e = calls_of("E1"), entry_of("E1")
        dev, events, conf = frames("E1")
        R3 = model_rows(calls, "M3")
        self.assertEqual((e["n_rows"], e["n_dates"]), (len(R3), R3["date"].nunique()))
        R, R2, px = CE.economic_px(calls, dev, events, conf, spec=SPEC)
        self.assertGreaterEqual(R["date"].min(), conf["date"].min())
        mine = test_px("E1")
        for c in ("date", "ticker", "open", "close", "beta"):
            self.assertTrue(np.array_equal(px[c].to_numpy(), mine[c].to_numpy()), c)
        self.assertEqual(e["values"]["beta_bar"], float(mine["beta"].mean()))

    # 9
    def test_dev_mode(self):
        e = entry_of("E3")
        dev, events, _ = frames("E3")
        self.assertEqual(e["status"], "estimated")
        self.assertEqual((e["values"]["mode"], e["values"]["from"]), ("dev", None))
        R, _, _ = CE.economic_px(calls_of("E3"), dev, events, None, spec=SPEC)
        self.assertLess(R["date"].max(), pd.Timestamp("2022-01-01"))

    # 10
    def test_main_call_failed(self):
        e, calls = entry_of("E4"), calls_of("E4")
        self.assertEqual(calls.main.status, "failed")
        self.assertEqual((e["status"], e["reason"]), ("not_estimable", calls.main.reason))
        self.assertTrue(e["reason"].startswith("walk_forward ("))
        self.assertEqual((e["values"], e["n_rows"], e["n_dates"], e["lag"]), (None, None, None, None))

    # 11
    def test_cost_case_failure(self):
        calls = calls_of("E1")
        dev, events, conf = frames("E1")
        R = model_rows(calls, "M3")
        d = R.loc[R["ticker"].astype(str) == "5706", "date"].iloc[0]
        conf2 = conf.copy()
        conf2.loc[((conf2["date"] == d) & (conf2["ticker"].astype(str) == "5706")).to_numpy(), "open"] = 1e7
        conf2.attrs = dict(conf.attrs)
        e = CE.economic_row(calls, dev, events, conf2, spec=SPEC)
        v = e["values"]
        self.assertEqual(e["status"], "estimated")
        self.assertEqual(sorted(v["cases_failed"]), ["high", "primary"])
        for case in ("primary", "high"):
            self.assertTrue(v["cases_failed"][case].startswith("ValueError"), case)
            self.assertIsNone(v["round_trip_bp"][case])
            self.assertIsNone(v["x_m_by_ticker"][case])
            self.assertEqual([v["net_bp"][m][case] for m in ("M3", "M2")], [None, None])
        self.assertIsInstance(v["round_trip_bp"]["low"], dict)
        self.assertIsInstance(v["net_bp"]["M3"]["low"], float)
        self.assertEqual(v["break_even_bp"], entry_of("E1")["values"]["break_even_bp"])

    # 12
    def test_mismatched_frames_refused(self):
        calls = calls_of("E1")
        dev, events, conf = frames("E1")
        R = model_rows(calls, "M3")
        d, t = R["date"].iloc[0], str(R["ticker"].iloc[0])
        conf3 = conf.copy()
        rows = ((conf3["date"] == d) & (conf3["ticker"].astype(str) == t)).to_numpy()
        conf3.loc[rows, "y_oc"] = conf3.loc[rows, "y_oc"] + 0.01
        conf3.attrs = dict(conf.attrs)
        with self.assertRaises(ValueError):
            CE.economic_row(calls, dev, events, conf3, spec=SPEC)

    # 13
    def test_provenance_pairs_refused(self):
        calls = calls_of("E1")
        dev, events, conf = frames("E1")
        cases = [(dev, relabel(conf, B.DEV_REAL)), (dev, relabel(conf, B.CONFIRM_REAL)),
                 (relabel(dev, B.DEV_REAL), conf), (relabel(dev, None), conf), (relabel(dev, B.CONFIRM_REAL), None)]
        for d, c in cases:
            before = B.registered_labels()
            with self.assertRaises(ValueError):
                CE.economic_row(calls, d, events, c, spec=SPEC)
            self.assertEqual(B.registered_labels(), before)

    # 14
    def test_module_source(self):
        src = MODULE.read_text(encoding="utf-8")
        tree = ast.parse(src)
        absolute = {"__future__", "dataclasses", "fractions", "hashlib", "json", "math", "typing", "numpy", "pandas"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertIn(a.name, absolute)
            elif isinstance(node, ast.ImportFrom):
                names = {a.name for a in node.names}
                if node.level == 0:
                    self.assertIn(node.module, absolute)
                elif node.module is None:
                    self.assertLessEqual(names, {"blind", "targets"})
                elif node.module == "spec":
                    self.assertLessEqual(names, {"Spec", "REPO_ROOT"})
                elif node.module == "confirm_inference":
                    self.assertLessEqual(names, {"ITEM_OF", "load_config", "_plain"})
                else:
                    self.assertEqual(node.module, "confirm_forecast")
                    self.assertLessEqual(names, {"Calls", "_check_inputs"})
        called = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                called.append(f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None)
        for bad in ("open", "read_csv", "to_csv", "read_text", "write_text", "write_bytes", "to_parquet", "to_pickle",
                    "to_excel"):
            self.assertNotIn(bad, called)
        self.assertEqual(called.count("read_bytes"), 1)
        for s in ("load_dev", "load_confirm", "load_events", "OFILT_DATA_DIR", "RUN_REGISTRY"):
            self.assertNotIn(s, src)
        functions = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
        assigned = {t.id for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
        self.assertLessEqual({"load_cost_inputs", "check_cost_inputs", "round_trips", "pnl_bp", "economic_px",
                              "economic_row", "fill"}, functions)
        self.assertLessEqual({"COST_INPUTS_PATH", "COST_INPUTS_SHA256", "CASES", "MODELS"}, assigned)


if __name__ == "__main__":
    unittest.main()
