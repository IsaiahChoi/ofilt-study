import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import numpy as np  # noqa: E402

import fill_spec_A6 as F  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift.schema import AT_OPEN, TARGET_INPUTS  # noqa: E402
from ofilt.drift.spec import DEFAULT_SPEC_PATH, Spec  # noqa: E402


class TestFillA6(unittest.TestCase):
    def test_spec_filled_and_reproducible(self):
        sp = Spec.load()
        self.assertEqual(sp.unfilled(), [])
        self.assertTrue(F.check(sp))
        for c, (lo, hi) in sp.winsor_bounds().items():
            self.assertTrue(lo < 0 < hi, c)
        self.assertGreater(sp.rv_per_bar_dev_median(), 0)

    def test_computation_never_reads_targets(self):
        self.assertFalse(set(F.PREDICTOR_COLS) & (TARGET_INPUTS | AT_OPEN))
        real = IO.load_dev
        def poisoned(*a, **k):
            d = real(*a, **k)
            for c in sorted(TARGET_INPUTS | AT_OPEN | {"open", "close", "prev_close"}):
                d[c] = np.nan
            return d
        with mock.patch.object(IO, "load_dev", poisoned):
            self.assertTrue(F.check())

    def test_window_hours_structure(self):
        wh = F.per_date_predictors().window_hours.round(4)
        self.assertTrue(((wh == 17.9833) | (wh >= 41.9833)).all())   # > 18 == multi-night window
        self.assertEqual(int((wh == 17.9833).sum()) + int((wh > 18).sum()), len(wh))

    def test_refill_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "spec.yaml"
            shutil.copy(DEFAULT_SPEC_PATH, p)
            with self.assertRaises(SystemExit):
                F.fill(p)                       # no TO_FILL lines remain
            self.assertEqual(p.read_bytes(), DEFAULT_SPEC_PATH.read_bytes())


if __name__ == "__main__":
    unittest.main()
