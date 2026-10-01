import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd  # noqa: E402

from ofilt.drift import calendar as C  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402

ALL_THREE = ["2022-02-09", "2022-08-09", "2024-08-08", "2025-02-13", "2025-08-08", "2025-11-11"]


class TestConfirmationCalendar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = IO.load_events_firm()                                   # hash-verified, dates only
        cls.dev_dates = pd.read_csv(IO.DATA_DIR / "panel_dev.csv", usecols=["date"], parse_dates=["date"]).date

    def test_trading_day_count_and_shape(self):
        cal = C.confirmation_calendar()
        self.assertEqual(len(cal), C.N_CONF_DAYS)                            # 1,019 (MANIFEST/PLAN)
        self.assertEqual((cal[0], cal[-1]), (C.CONF_START, C.CONF_END))
        self.assertTrue(cal.is_monotonic_increasing and cal.is_unique)
        self.assertFalse((cal.weekday >= 5).any())
        self.assertFalse(cal.isin(C.CONF_HOLIDAYS).any())
        self.assertFalse((C.CONF_HOLIDAYS.weekday >= 5).any())               # list has no weekend dates
        self.assertLess(self.dev_dates.max(), cal[0])

    def test_event_exclusions_per_ticker(self):
        conf = C.confirmation_calendar()
        dev = pd.DatetimeIndex(sorted(self.dev_dates.unique()))
        ex = C.excluded_dates(self.events, dev.append(conf))
        for t in C.TICKERS:
            self.assertEqual(len({d for d in ex[t] if d >= conf[0]}), 34, t)

    def test_t_conf(self):
        T, common = C.t_conf(self.events, self.dev_dates)
        self.assertEqual([d.date().isoformat() for d in common], ALL_THREE)
        self.assertEqual(T, C.T_CONF)
        self.assertEqual(T, 1013)

    def test_mapping_rule_matches_panel_flags_on_dev(self):
        # Same rule as build_panel.event_rows: on the DEV calendar it reproduces earn|news exactly.
        dev = IO.load_dev()[["date", "ticker", "earn_flag", "news_flag"]]
        ex = C.excluded_dates(self.events, pd.DatetimeIndex(sorted(dev.date.unique())))
        for t in C.TICKERS:
            s = dev[dev.ticker == t]
            flagged = set(s.date[(s.earn_flag == 1) | (s.news_flag == 1)])
            self.assertEqual({d for d in ex[t] if d <= s.date.max()}, flagged, t)

    def test_no_sealed_panel_access(self):
        src = (ROOT / "ofilt" / "drift" / "calendar.py").read_text(encoding="utf-8")
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        for forbidden in ("panel_confirm", "SEALED.csv", "load_confirm", "read_csv"):
            self.assertNotIn(forbidden, code)


if __name__ == "__main__":
    unittest.main()
