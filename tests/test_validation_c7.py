"""C7 tests (synthetic only): P28 validation of the forecasting machinery.
Default suite: re-assert the slow-tier bands from reports/C7_mc.json (and fail if the code it
hashed has changed), chunk invariance + resume of tools/c7_mc.py on a tiny config, and the
forecast look-ahead perturbation (M1-M5 in one call; M7 with M1).
Slow tier (OFILT_SLOW=1): reproduce stored replications bit for bit."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import c7_mc as C  # noqa: E402
from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import fctests as FT  # noqa: E402
from ofilt.drift import forecast as F  # noqa: E402
from ofilt.drift.models import M1, M2, M3, M4, M5, M7  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402
from test_fctests_c5 import strong_panel  # noqa: E402
from test_models_c4 import full_panel  # noqa: E402

SLOW = os.environ.get("OFILT_SLOW") == "1"
TINY = dict(C.FULL, n_dates=560, h1_dates=50, cells=[["size", 0.0, 3], ["power_040", 0.40, 2], ["power_025", 0.25, 2]],
            out=["reports/mc.json", "reports/h1.json"], partial="reports/partial.json")


def load_report():
    return json.loads((ROOT / C.FULL["out"][0]).read_text()), json.loads((ROOT / C.FULL["out"][1]).read_text())


class TestC7Report(unittest.TestCase):
    def test_bands_consistency_and_staleness(self):
        mc, h1 = load_report()
        self.assertEqual(mc["key"]["code"], C.code_hashes(),
                         "C7 report is STALE: code changed since the slow tier ran; rerun tools/c7_mc.py")
        spec = Spec.load()
        self.assertEqual(mc["key"], C.config_key(C.FULL, spec))
        state = dict(key=mc["key"], reps=mc["reps"], runtime_s=mc["runtime_s"])
        mc2, h12 = C.summarise(state)
        self.assertEqual(json.loads(json.dumps(mc2)), mc)                    # summary == its own reps
        self.assertEqual(json.loads(json.dumps(h12)), h1)
        for name, b, n in C.FULL["cells"]:
            reps = mc["reps"][name]
            self.assertEqual(len(reps), n)
            self.assertEqual([r["seed"] for r in reps],
                             [spec.seed + C.FULL["seed_offset"] + 100_000 * c + r
                              for c, (nm, _, _) in enumerate(C.FULL["cells"]) if nm == name for r in range(n)])
            self.assertEqual(tuple(mc["cells"][name]["cw"]["wilson95"]),
                             FT.wilson(mc["cells"][name]["cw"]["k"], n))
        lo, hi = C.FULL["bands"]["size"]
        self.assertTrue(lo <= mc["cells"]["size"]["cw"]["rate"] <= hi)       # P28 band [2%, 9%]
        self.assertGreaterEqual(mc["cells"]["power_040"]["cw"]["rate"], C.FULL["bands"]["power_040_min"])
        self.assertTrue(all(abs(t - 1013) <= 5 for c in mc["cells"].values() for t in c["T_eval_range"]))


class TestRunner(unittest.TestCase):
    def test_chunk_invariance_resume_and_stale_partial(self):
        spec = Spec.load()
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            self.assertTrue(C.run(TINY, budget=1e9, root=Path(a), spec=spec))
            calls = 0
            while not C.run(TINY, budget=0.4, root=Path(b), spec=spec):
                calls += 1
                self.assertLess(calls, 50)
            self.assertGreater(calls, 0)                                       # really chunked
            ra = json.loads((Path(a) / TINY["out"][0]).read_text())
            rb = json.loads((Path(b) / TINY["out"][0]).read_text())
            self.assertEqual(ra["reps"], rb["reps"])                           # chunking changes nothing
            self.assertEqual(ra["cells"], rb["cells"])
            self.assertFalse((Path(b) / TINY["partial"]).exists())
            self.assertFalse(C.run(TINY, budget=0.0, root=Path(a), spec=spec))  # fresh partial
            other = copy.deepcopy(TINY)
            other["p_excl"] = 0.03
            other["partial"] = TINY["partial"]
            with self.assertRaises(RuntimeError):                              # partial from another config
                C.run(other, budget=0.0, root=Path(a), spec=spec)


def perturb_after(df, tau, seed):
    """Replace every float column (targets and all feature sources) after tau by noise;
    positive columns stay positive. Keys, masks and integer flags are unchanged."""
    out = df.copy()
    rng = np.random.default_rng(seed)
    late = (out.date > tau).to_numpy()
    for c in out.columns:
        if out[c].dtype.kind == "f":
            x = out[c].to_numpy(dtype=float)
            z = rng.standard_normal(late.sum())
            sd = np.nanstd(x) or 1.0
            pos = np.nanmin(x) > 0
            x = x.copy()
            x[late] = np.abs(z) * (abs(np.nanmean(x)) + sd) + 1e-12 if pos else z * sd
            out[c] = x
    return B.mark_synthetic(out)


class TestForecastLookAhead(unittest.TestCase):
    def check(self, df, models):
        spec = Spec.load()
        p0, f0 = F.walk_forward(df, models, spec)
        fold1 = np.sort(p0[p0.fold == 1].date.unique())
        tau = fold1[10]                                                       # strictly inside a test block
        p1, _ = F.walk_forward(perturb_after(df, tau, 3), models, spec)
        for m in models:
            a = p0[(p0.model == m) & (p0.date <= tau)].reset_index(drop=True)
            b = p1[(p1.model == m) & (p1.date <= tau)].reset_index(drop=True)
            self.assertTrue(a[["date", "ticker", "fold"]].equals(b[["date", "ticker", "fold"]]), m)
            self.assertTrue(np.array_equal(a.yhat.to_numpy(), b.yhat.to_numpy()), m)   # bit-identical
            late0 = p0[(p0.model == m) & (p0.date > tau)].yhat.to_numpy()
            late1 = p1[(p1.model == m) & (p1.date > tau)].yhat.to_numpy()
            if m != "M0":
                self.assertFalse(np.array_equal(late0, late1), m)              # the perturbation bites

    def test_linear_ladder_one_call(self):
        self.check(strong_panel(700, b=1.0), {"M1": M1, "M2": M2, "M3": M3, "M4": M4, "M5": M5})

    def test_m7_with_m1(self):
        self.check(full_panel(600, seed=5, signal=0.02), {"M1": M1, "M7": M7})


@unittest.skipUnless(SLOW, "slow tier (OFILT_SLOW=1)")
class TestSlowReproduce(unittest.TestCase):
    def reproduce(self, idx):
        mc, _ = load_report()
        spec = Spec.load()
        for name, b, n in C.FULL["cells"]:
            for r in idx(n):
                stored = mc["reps"][name][r]
                self.assertEqual(json.loads(json.dumps(C.one_rep(stored["seed"], b, C.FULL, spec))), stored)

    def test_first_reps_bit_identical(self):
        self.reproduce(lambda n: range(3))

    def test_last_reps_bit_identical(self):
        self.reproduce(lambda n: [n - 1])


if __name__ == "__main__":
    unittest.main()
