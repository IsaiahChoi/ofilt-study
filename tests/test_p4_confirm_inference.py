"""P4-4a (P4Q35): ofilt/drift/confirm_inference.py against docs/P4_CONFIRM_INF_SPEC.md (version 2). Exactly the 23
test methods of its §8.3. Seeds are the spec seed + 8,100,000 + k (§8.1), disjoint from every earlier block. Every
frame is synthetic; frames labelled dev_real or confirm_real appear only in test 5's refused pairs, so no synthetic
value is ever registered as real. Expected masks and counts are recomputed here from C and D0, built as §3.3 and §6
say, independently of the module's internals (§8.2)."""
import ast
import copy
import dataclasses
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import calib as CB  # noqa: E402
from ofilt.drift import confirm_inference as CI  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift import sim_full as SF  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

SPEC = Spec.load()
H1 = SPEC.h1_parameter
MODULE = ROOT / "ofilt" / "drift" / "confirm_inference.py"
CFG = json.loads((ROOT / "docs" / "P4_CONFIRM_CONFIG.json").read_text(encoding="utf-8"))
SA = SF.Scenario(b=1.0, a2=0.6, delta_cc=1.5)
SB = SF.Scenario(b=1.0, delta_post=-1.0, a2=0.6, delta_cc=1.5)
SC = SF.Scenario(b=1.0, a2=0.6, delta_cc=1.5, c_usd_sess=0.5, c_eur_sess=-0.3, b_gotobi=0.4)
SD = SF.Scenario(b=1.0, b_spread=(-0.3, 0.1, 0.2), a2=0.6, delta_cc=1.5)
SZ = SF.Scenario()
SN = SF.Scenario.not_estimable()
TOP_KEYS = ["module", "spec_version", "config_sha256", "mode", "provenance", "dates", "rows"]
ENTRY_KEYS = ["id", "item", "status", "values", "reason", "n_rows", "n_dates", "lag"]
P4A = [f"O{i}" for i in range(1, 29)] + [f"R{i}" for i in range(1, 9)]
P4B = [f"O{i}" for i in range(29, 46)] + ["R9"]
P4C = [f"R{i}" for i in range(10, 27)]
TICKERS = ("5706", "5711", "5713")
_SIMS: dict = {}
_DOCS: dict = {}
_FRAMES: dict = {}


def seed(k):
    return SPEC.seed + 8_100_000 + k


def out(k, scenario):
    key = (k, scenario)
    if key not in _SIMS:
        _SIMS[key] = SF.simulate(seed(k), scenario)
    return _SIMS[key]


def doc(k, scenario, mode="confirmation"):
    key = (k, scenario, mode)
    if key not in _DOCS:
        o = out(k, scenario)
        _DOCS[key] = CI.infer(o.dev, o.events, o.confirm) if mode == "confirmation" else CI.infer(o.dev, o.events)
    return _DOCS[key]


def rows_of(frame, keep):
    r = frame.loc[keep]
    r.attrs = dict(frame.attrs)
    return r


def frames(k, scenario):
    """C, C250, C500, the two period frames and D0, built here as §3.3 and §6 say."""
    key = (k, scenario)
    if key not in _FRAMES:
        o = out(k, scenario)
        J = pd.concat([o.dev, o.confirm], ignore_index=True)
        J.attrs = {"provenance": B.SYNTHETIC}
        T = TG.add_masks(TG.add_targets(J, SPEC), o.events, SPEC)
        keep = (T["date"] >= o.confirm["date"].min()).to_numpy()
        C = rows_of(T, keep)
        f = {"C": C, "C250": rows_of(TG.add_targets(J, SPEC, method="rolling", window=250), keep),
             "C500": rows_of(TG.add_targets(J, SPEC, method="rolling", window=500), keep)}
        for part in ("confirmatory", "descriptive"):
            lo, hi = pd.Timestamp(CFG["f"][part]["from"]), pd.Timestamp(CFG["f"][part]["to"])
            f[part] = rows_of(C, ((C["date"] >= lo) & (C["date"] <= hi)).to_numpy())
        f["D0"] = I.build_design(C, SPEC)
        _FRAMES[key] = f
    return _FRAMES[key]


def summary(c):
    return {"estimate": float(c["estimate"]), "se": float(c["se"]), "z": float(c["z"]), "p": float(c["p"]),
            "ci": [float(c["ci"][0]), float(c["ci"][1])]}


def tost_plain(t):
    return {"p": float(t["p"]), "p_lower": float(t["p_lower"]), "p_upper": float(t["p_upper"]),
            "equivalent": bool(t["equivalent"]), "ci": [float(t["ci"][0]), float(t["ci"][1])],
            "sesoi": float(t["sesoi"]), "alpha": float(t["alpha"])}


def at(C, design, column):
    return C.loc[design.index, column].to_numpy(dtype=float)


def relabel(df, provenance):
    r = df.copy()
    attrs = {k: v for k, v in df.attrs.items() if k != "provenance"}
    if provenance is not None:
        attrs["provenance"] = provenance
    r.attrs = attrs
    return r


class TestConfirmInference(unittest.TestCase):
    def assertRecovers(self, s, x):
        self.assertLessEqual(abs(s["estimate"] - x), 5 * s["se"], (s, x))

    # 1
    def test_config_pin_and_refusal(self):
        data = CI.CONFIG_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), CI.CONFIG_SHA256)
        cfg = CI.load_config()
        self.assertEqual(cfg, json.loads(data.decode("utf-8")))
        bad = bytearray(data)
        bad[data.index(b"P4_CONFIRM_CONFIG")] ^= 0x01
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "P4_CONFIRM_CONFIG.json"
            p.write_bytes(bytes(bad))
            with self.assertRaises(ValueError):
                CI.load_config(p)
        self.assertEqual(list(cfg["rows"]), list(CI.ROW_IDS))

    # 2
    def test_row_ids_and_items(self):
        self.assertEqual(len(CI.ROW_IDS), 71)
        self.assertEqual(len(set(CI.ROW_IDS)), 71)
        self.assertEqual(set(CI.ITEM_OF), set(CI.ROW_IDS))
        for item, ids, n in (("P4-4a", P4A, 36), ("P4-4b", P4B, 18), ("P4-4c", P4C, 17)):
            mine = sorted(i for i in CI.ROW_IDS if CI.ITEM_OF[i] == item)
            self.assertEqual(len(mine), n)
            self.assertEqual(mine, sorted(ids))

    # 3
    def test_document_schema(self):
        d = doc(0, SA)
        self.assertEqual(list(d), TOP_KEYS)
        self.assertEqual(list(d["rows"]), list(CI.ROW_IDS))
        for rid, e in d["rows"].items():
            self.assertEqual(list(e), ENTRY_KEYS, rid)
            self.assertEqual((e["id"], e["item"]), (rid, CI.ITEM_OF[rid]))
            self.assertIn(e["status"], CI.STATUSES)
            if rid in P4A:
                self.assertNotEqual(e["status"], "pending", rid)
            else:
                self.assertEqual(e["status"], "pending", rid)
                self.assertEqual([e[k] for k in ENTRY_KEYS[3:]], [None] * 5, rid)

    # 4
    def test_json_round_trip_and_determinism(self):
        o = out(1, SA)
        text = CI.to_json(CI.infer(o.dev, o.events, o.confirm))
        d2 = CI.infer(o.dev, o.events, o.confirm)
        self.assertEqual(CI.to_json(d2), text)
        self.assertEqual(json.loads(CI.to_json(d2)), d2)
        self.assertNotIn("NaN", text)
        self.assertNotIn("Infinity", text)
        V = np.diag([0.01, 0.01])
        e1 = CI.encode_fraction(I.fraction_from(1.0, 0.05, V, 0.05))
        self.assertEqual(e1["fieller"]["kind"], "two_rays")
        ci = e1["fieller"]["ci"]
        lo, hi = ci[0][1], ci[1][0]
        self.assertEqual(ci, [[None, lo], [hi, None]])
        self.assertIsInstance(lo, float)
        self.assertIsInstance(hi, float)
        self.assertLess(lo, hi)
        e2 = CI.encode_fraction(I.fraction_from(0.01, 0.01, V, 0.05))
        self.assertEqual(e2["fieller"]["kind"], "real_line")
        self.assertEqual(e2["fieller"]["ci"], [None, None])
        json.dumps(e1, allow_nan=False)
        json.dumps(e2, allow_nan=False)

    # 5
    def test_provenance_pairs_refused(self):
        o = out(1, SA)
        cases = [(o.dev, relabel(o.confirm, B.DEV_REAL)), (o.dev, relabel(o.confirm, B.CONFIRM_REAL)),
                 (relabel(o.dev, B.DEV_REAL), o.confirm), (relabel(o.dev, None), o.confirm),
                 (relabel(o.dev, B.CONFIRM_REAL), None)]
        for dev, conf in cases:
            before = B.registered_labels()
            with self.assertRaises(ValueError):
                if conf is None:
                    CI.infer(dev, o.events)
                else:
                    CI.infer(dev, o.events, conf)
            self.assertEqual(B.registered_labels(), before)

    # 6
    def test_inputs_unchanged(self):
        o = out(1, SA)
        inputs = (o.dev, o.confirm, o.events)
        snap = [(f.copy(deep=True), copy.deepcopy(f.attrs)) for f in inputs]
        CI.infer(o.dev, o.events, o.confirm)
        for f, (g, attrs) in zip(inputs, snap):
            pd.testing.assert_frame_equal(f, g, check_exact=True)
            self.assertEqual(f.attrs, attrs)

    # 7
    def test_primary_and_sample_rows(self):
        rows = doc(1, SA)["rows"]
        F = frames(1, SA)
        r = I.fit_dk(I.build_design(F["C"], SPEC), SPEC)
        self.assertEqual(rows["O1"]["values"]["fit"], summary(r.param(H1)))
        self.assertRecovers(rows["O1"]["values"]["fit"], 1.0)
        self.assertRecovers(rows["O2"]["values"]["fit"], 0.6)
        r2 = rows["R2"]["values"]
        self.assertEqual((r2["dates"], r2["dates_all_excluded"], r2["matches_t_conf"]), (1013, 6, True))
        self.assertEqual(rows["R3"]["values"]["lag"], 6)
        self.assertIs(rows["R4"]["values"]["reject"], True)
        for rid in ("R1", "R3", "R5"):
            self.assertEqual(rows[rid]["status"], "fixed", rid)

    # 8
    def test_secondary_family_matches_library(self):
        rows = doc(1, SA)["rows"]
        fam = I.secondary_family_tests(frames(1, SA)["C"], SPEC)
        for i, rid in enumerate(("O3", "O4", "O5", "O6")):
            v = rows[rid]["values"]
            self.assertEqual(v["member"], fam["member"].iloc[i])
            for c in ("estimate", "se", "z", "p"):
                self.assertEqual(v["tested"][c], float(fam[c].iloc[i]), (rid, c))
        self.assertEqual(rows["R6"]["values"]["p"], [float(x) for x in fam["p"]])
        self.assertEqual(rows["R6"]["values"]["p_holm"], [float(x) for x in fam["p_holm"]])

    # 9
    def test_secondary_family_not_estimable_member(self):
        rows = doc(2, SN)["rows"]
        self.assertEqual(rows["O5"]["status"], "not_estimable")
        self.assertIn("rv_per_bar", rows["O5"]["reason"])
        for rid in ("O3", "O4", "O6"):
            self.assertEqual(rows[rid]["status"], "estimated", rid)
        v = rows["R6"]["values"]
        self.assertEqual(v["p"], [rows["O3"]["values"]["tested"]["p"], rows["O4"]["values"]["tested"]["p"], 1.0,
                                  rows["O6"]["values"]["tested"]["p"]])
        self.assertEqual(v["p_holm"], [float(x) for x in I.holm(v["p"])])
        self.assertEqual(v["not_estimable"], ["O5"])

    # 10
    def test_fraction_unpriced_periods(self):
        for k, sc in ((1, SA), (3, SB)):
            rows = doc(k, sc)["rows"]
            F = frames(k, sc)
            o7 = rows["O7"]["values"]
            for part in ("confirmatory", "descriptive"):
                P = o7[part]
                self.assertEqual((P["status"], P["f_defined"]), ("estimated", True), (k, part))
                J = I.fit_joint(F[part], SPEC)
                fr = I.fraction_unpriced(J)
                for c in ("f", "se_delta", "t_denominator", "b", "delta_cc"):
                    self.assertEqual(P[c], float(fr[c]), (k, part, c))
                self.assertEqual(P["ci_delta"], [float(x) for x in fr["ci_delta"]])
                self.assertEqual(P["fieller"]["kind"], fr["fieller"]["kind"])
                if fr["fieller"]["kind"] == "bounded":
                    self.assertEqual(P["fieller"]["ci"], [float(x) for x in fr["fieller"]["ci"]])
                self.assertEqual((P["n_rows"], P["n_dates"], P["lag"]), (J.n, J.T, J.lag))
                if sc is SA or part == "confirmatory":
                    self.assertLessEqual(abs(P["f"] - 1 / 1.5), 5 * P["se_delta"], (k, part))
            self.assertEqual(rows["O8"]["status"], "fixed")
            for part in ("confirmatory", "descriptive"):
                self.assertEqual(rows["O8"]["values"][part], [CFG["f"][part]["from"], CFG["f"][part]["to"]])

    # 11
    def test_fraction_not_estimable_2022(self):
        e = doc(2, SN)["rows"]["O7"]
        self.assertEqual(e["status"], "not_estimable")
        conf, desc = e["values"]["confirmatory"], e["values"]["descriptive"]
        self.assertEqual(conf["status"], "not_estimable")
        self.assertIsInstance(conf["reason"], str)
        self.assertTrue(conf["reason"])
        self.assertEqual(desc["status"], "estimated")

    # 12
    def test_decomposition_and_tost(self):
        for k, sc in ((4, SZ), (1, SA)):
            dec = I.decomposition(frames(k, sc)["C"], SPEC)
            self.assertEqual(doc(k, sc)["rows"]["O9"]["values"], {c: float(v) for c, v in dec.items()})
        self.assertIs(doc(4, SZ)["rows"]["O10"]["values"]["equivalent"], True)
        rows = doc(1, SA)["rows"]
        r0 = I.fit_dk(frames(1, SA)["D0"], SPEC)
        s = CFG["constants"]["sesoi"]
        self.assertEqual(rows["O10"]["values"], tost_plain(I.tost_result(r0, H1, SPEC, sesoi=s["primary"])))
        for name in ("low", "high"):
            self.assertEqual(rows["O11"]["values"][name], tost_plain(I.tost_result(r0, H1, SPEC, sesoi=s[name])))

    # 13
    def test_huber_winsorised_influence(self):
        rows = doc(1, SA)["rows"]
        F = frames(1, SA)
        D0, C = F["D0"], F["C"]
        self.assertEqual(rows["O12"]["values"], summary(I.fit_huber(D0, SPEC).param(H1)))
        W = CB.winsorise_fx(C, SPEC)
        self.assertEqual(rows["O13"]["values"], summary(I.fit_dk(I.build_design(W, SPEC), SPEC).param(H1)))
        ic = I.influence_curve(D0, SPEC)
        curve = rows["O14"]["values"]["curve"]
        self.assertEqual(len(curve), 21)
        self.assertEqual([c["k"] for c in curve], list(range(21)))
        for c, (_, lib) in zip(curve, ic.iterrows()):
            removed = None if pd.isna(lib["date_removed"]) else pd.Timestamp(lib["date_removed"]).strftime("%Y-%m-%d")
            self.assertEqual(c, {"k": int(lib["k"]), "date_removed": removed, "b": float(lib["b"]),
                                 "se": float(lib["se"]), "z": float(lib["z"]), "p": float(lib["p"]),
                                 "n_dates": int(lib["n_dates"]), "lag": int(lib["lag"])})
        self.assertEqual(curve[0]["b"], rows["O1"]["values"]["fit"]["estimate"])

    # 14
    def test_rolling_beta_and_raw_rows(self):
        rows = doc(1, SA)["rows"]
        F = frames(1, SA)
        D0, C = F["D0"], F["C"]
        for rid, Dr in (("O15", I.build_design(F["C250"], SPEC)), ("O16", I.build_design(F["C500"], SPEC)),
                        ("O17", I.build_design(C, SPEC, target="raw_oc"))):
            e, v = rows[rid], rows[rid]["values"]
            rw = I.fit_dk(I.subset_design(D0, np.isin(D0.index, Dr.index)), SPEC)
            self.assertEqual((rw.n, rw.T), (e["n_rows"], e["n_dates"]), rid)
            self.assertEqual(v["without"], summary(rw.param(H1)), rid)
            self.assertEqual(v["dropped_rows"], len(D0.y) - e["n_rows"], rid)
            self.assertRecovers(v["with"], 1.0)
            self.assertRecovers(v["without"], 1.0)

    # 15
    def test_fcx_ewj_xau_rows(self):
        rows = doc(1, SA)["rows"]
        F = frames(1, SA)
        D0, C = F["D0"], F["C"]
        for rid, col in (("O18", "fcx_oc"), ("O19", "ewj_oc_jpy"), ("O20", "xau_ret")):
            e, v = rows[rid], rows[rid]["values"]
            mask = np.isfinite(at(C, D0, col))
            self.assertEqual(e["n_rows"], int(mask.sum()), rid)
            rw = I.fit_dk(I.subset_design(D0, mask), SPEC)
            self.assertEqual((rw.n, rw.T), (e["n_rows"], e["n_dates"]), rid)
            self.assertEqual(v["without"], summary(rw.param(H1)), rid)
            self.assertRecovers(v["with"], 1.0)
            self.assertRecovers(v["without"], 1.0)

    # 16
    def test_nikkei_eligibility(self):
        rows = doc(1, SA)["rows"]
        F = frames(1, SA)
        D0, C = F["D0"], F["C"]
        mask = ((at(C, D0, "n225_stale_start_min") <= 5) & (at(C, D0, "n225_stale_end_min") <= 5)
                & np.isfinite(at(C, D0, "n225_ret")))
        e = rows["O21"]
        self.assertEqual(e["n_rows"], int(mask.sum()))
        missing = C.loc[~np.isfinite(C["n225_ret"].to_numpy(dtype=float)), "date"].to_numpy(dtype="datetime64[ns]")
        self.assertGreater(len(missing), 0)
        self.assertFalse(np.isin(D0.dates[mask], missing).any())
        self.assertRecovers(e["values"]["with"], 1.0)
        self.assertRecovers(e["values"]["without"], 1.0)

    # 17
    def test_mechanism_row(self):
        rows = doc(5, SC)["rows"]
        F = frames(5, SC)
        D0, C = F["D0"], F["C"]
        e = rows["O22"]
        coef = e["values"]["coefficients"]
        for name, x in (("c_usdjpy_sess_ret", 0.5), ("c_eurusd_sess_ret", -0.3), (f"{H1}:gotobi_day", 0.4),
                        ("gotobi_day", 0.0)):
            self.assertRecovers(coef[name], x)
        self.assertRecovers(e["values"]["with"], 1.0)
        sess = (np.isfinite(C["c_usdjpy_sess_ret"].to_numpy(dtype=float))
                & np.isfinite(C["c_eurusd_sess_ret"].to_numpy(dtype=float)))
        missing = C.loc[~sess, "date"].to_numpy(dtype="datetime64[ns]")
        on_missing = np.isin(D0.dates, missing)
        self.assertGreater(int(on_missing.sum()), 0)
        kept = (np.isfinite(at(C, D0, "c_usdjpy_sess_ret")) & np.isfinite(at(C, D0, "c_eurusd_sess_ret"))
                & np.isfinite(at(C, D0, "gotobi_day")))
        self.assertTrue(np.array_equal(kept, ~on_missing))
        self.assertEqual(e["n_rows"], len(D0.y) - int(on_missing.sum()))

    # 18
    def test_exclusion_rows(self):
        rows = doc(1, SA)["rows"]
        F = frames(1, SA)
        D0, C = F["D0"], F["C"]
        flags = list(SPEC.inference_exclusion_flags)
        for rid, extra in (("O23", "excl_d2"), ("O24", "audit_flag"), ("O25", "boj_day"), ("O26", "sq_major")):
            e, v = rows[rid], rows[rid]["values"]
            truthy = C.loc[D0.index, extra].astype(bool).to_numpy()
            self.assertEqual(e["n_rows"], len(D0.y) - int(truthy.sum()), rid)
            self.assertLess(e["n_rows"], rows["O1"]["n_rows"], rid)
            self.assertRecovers(v["fit"], 1.0)
            self.assertEqual(v["excluded_columns"][:len(flags)], flags, rid)

    # 19
    def test_post_break_row(self):
        v = doc(3, SB)["rows"]["O27"]["values"]
        self.assertRecovers(v["b_pre"], 1.0)
        self.assertRecovers(v["b_post"], 0.0)
        F = frames(3, SB)
        D0, C = F["D0"], F["C"]
        post = (D0.dates >= np.datetime64(pd.Timestamp(CFG["constants"]["post_break_date"]))).astype(float)
        Dd = dataclasses.replace(D0, X=np.column_stack([D0.X, post, at(C, D0, H1) * post]),
                                 names=D0.names + ("post", f"{H1}:post"))
        rd = I.fit_dk(Dd, SPEC)
        self.assertEqual(v["b_post"], summary(rd.contrast({H1: 1.0, f"{H1}:post": 1.0})))

    # 20
    def test_per_ticker_slopes_and_holm(self):
        rows = doc(6, SD)["rows"]
        slopes = rows["O28"]["values"]["slopes"]
        for t, x in zip(TICKERS, (0.7, 1.1, 1.2)):
            self.assertRecovers(slopes[t], x)
        p = [slopes[t]["p"] for t in TICKERS]
        self.assertEqual(rows["R7"]["values"]["p_holm"], [float(x) for x in I.holm(p)])

    # 21
    def test_not_estimable_preset_completes(self):
        rows = doc(2, SN)["rows"]
        self.assertEqual((rows["O20"]["status"], rows["O20"]["reason"]), ("not_estimable", "no rows"))
        self.assertEqual((rows["O22"]["status"], rows["O22"]["reason"]), ("not_estimable", "rank-deficient design"))
        for rid in P4A:
            if rid not in ("O5", "O7", "O20", "O22"):
                self.assertIn(rows[rid]["status"], ("estimated", "fixed"), rid)

    # 22
    def test_dev_mode(self):
        d = doc(1, SA, mode="dev")
        rows = d["rows"]
        self.assertEqual(d["mode"], "dev")
        self.assertLess(d["dates"]["last"], "2022-01-01")
        self.assertRecovers(rows["O1"]["values"]["fit"], 1.0)
        P = rows["O7"]["values"]["dev_stand_in"]
        self.assertLessEqual(abs(P["f"] - 1 / 1.5), 5 * P["se_delta"])
        self.assertEqual((rows["O8"]["status"], rows["O8"]["reason"]), ("not_applicable", CFG["f"]["dev"]["periods"]))
        on_dev = CFG["robustness"]["post_2024_11_05_indicator_CONFIRMATION_ONLY"]["on_dev"]
        self.assertEqual((rows["O27"]["status"], rows["O27"]["reason"]), ("not_applicable", on_dev))
        r2 = rows["R2"]["values"]
        self.assertEqual((r2["t_conf_expected"], r2["matches_t_conf"]), (None, None))

    # 23
    def test_module_source(self):
        src = MODULE.read_text(encoding="utf-8")
        tree = ast.parse(src)
        absolute = {"__future__", "dataclasses", "hashlib", "json", "math", "typing", "numpy", "pandas"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertIn(a.name, absolute)
            elif isinstance(node, ast.ImportFrom):
                names = {a.name for a in node.names}
                if node.level == 0:
                    self.assertIn(node.module, absolute)
                elif node.module is None:
                    self.assertLessEqual(names, {"blind", "calib", "inference", "targets"})
                else:
                    self.assertEqual(node.module, "spec")
                    self.assertLessEqual(names, {"Spec", "REPO_ROOT"})
        called = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                called.append(f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None)
        for bad in ("open", "read_csv", "to_csv", "write_text", "write_bytes", "to_parquet", "to_pickle", "to_excel"):
            self.assertNotIn(bad, called)
        self.assertEqual(called.count("read_bytes"), 1)
        for s in ("load_dev", "load_confirm", "load_events", "OFILT_DATA_DIR"):
            self.assertNotIn(s, src)
        functions = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
        assigned = {t.id for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
        self.assertLessEqual({"infer", "load_config", "encode_fraction", "to_json"}, functions)
        self.assertLessEqual({"CONFIG_SHA256", "CONFIG_PATH", "ROW_IDS", "ITEM_OF", "STATUSES", "TICKERS"}, assigned)
        self.assertEqual(CI.TICKERS, S.TICKERS)


if __name__ == "__main__":
    unittest.main()
