"""TSE trading calendar for the CONFIRMATION period 2022-01-04 .. 2026-03-05.

CALENDAR DATA ONLY. The dates come from a hard-coded TSE holiday list; nothing is
read from the sealed confirmation panel. Event release DATES for 2022+ (from the
hash-verified events_firm.csv) are calendar data with no outcomes, and reading
them is sanctioned (Isaiah, 2026-10-01).

  confirmation_calendar() = weekdays in [CONF_START, CONF_END] minus CONF_HOLIDAYS
                            -> 1,019 trading days (the count in MANIFEST/PLAN)
  T_CONF = confirmation trading days minus dates on which ALL three tickers are
           excluded (TANSHIN + STANDALONE_NEWS on D, D+1; same rule as
           build_panel.event_rows) -> 1019 - 6 = 1013. This is the length used
           by the Pass 4 size rule (spec amendment AM-02).

The event mapping runs on the CONTINUOUS dev + confirmation calendar, so a release
late in dev carries its D+1 into confirmation exactly as build_panel did.

Pass 2 cross-check: when the sealed panel is rebuilt, compare this calendar with
the rebuilt panel's `date` column (dates only, no other column), and assert
equality before the tag.
"""
from __future__ import annotations

import pandas as pd

CONF_START, CONF_END = pd.Timestamp("2022-01-04"), pd.Timestamp("2026-03-05")
_HOLIDAYS_TEXT = """\
2022-01-03 01-10 02-11 02-23 03-21 04-29 05-03 05-04 05-05 07-18 08-11 09-19 09-23 10-10 11-03 11-23
2023-01-02 01-03 01-09 02-23 03-21 05-03 05-04 05-05 07-17 08-11 09-18 10-09 11-03 11-23
2024-01-01 01-02 01-03 01-08 02-12 02-23 03-20 04-29 05-03 05-06 07-15 08-12 09-16 09-23 10-14 11-04 12-31
2025-01-01 01-02 01-03 01-13 02-11 02-24 03-20 04-29 05-05 05-06 07-21 08-11 09-15 09-23 10-13 11-03 11-24 12-31
2026-01-01 01-02 01-12 02-11 02-23"""
N_CONF_DAYS = 1019
T_CONF = 1013
EXCLUDED_CATEGORIES = ("TANSHIN", "STANDALONE_NEWS")
TICKERS = ("5706", "5711", "5713")


def _parse_holidays() -> pd.DatetimeIndex:
    out = []
    for line in _HOLIDAYS_TEXT.splitlines():
        first, *rest = line.split()
        year = first[:4]
        out += [pd.Timestamp(first)] + [pd.Timestamp(f"{year}-{md}") for md in rest]
    return pd.DatetimeIndex(out)


CONF_HOLIDAYS = _parse_holidays()


def confirmation_calendar() -> pd.DatetimeIndex:
    wd = pd.bdate_range(CONF_START, CONF_END)
    return wd[~wd.isin(CONF_HOLIDAYS)]


def excluded_dates(events: pd.DataFrame, calendar: pd.DatetimeIndex,
                   categories=EXCLUDED_CATEGORIES, offsets=(0, 1)) -> dict[str, set]:
    """Per ticker: calendar dates D*+o, D* = first calendar date >= release date."""
    cal = pd.DatetimeIndex(calendar).sort_values()
    ev = events[events["category"].isin(list(categories))]
    out = {}
    for t in TICKERS:
        hit = set()
        for d in pd.to_datetime(ev.loc[ev["ticker"].astype(str) == t, "date"]):
            k = cal.searchsorted(d)
            hit.update(cal[k + o] for o in offsets if k + o < len(cal))
        out[t] = hit
    return out


def t_conf(events: pd.DataFrame, dev_dates) -> tuple[int, list[pd.Timestamp]]:
    """(T_conf, dates excluded for all three tickers), on the continuous dev+conf calendar."""
    conf = confirmation_calendar()
    dev = pd.DatetimeIndex(sorted(pd.to_datetime(pd.Series(dev_dates)).unique()))
    if not dev.max() < conf.min():
        raise ValueError("dev calendar must end before the confirmation calendar starts")
    ex = excluded_dates(events, dev.append(conf))
    common = sorted(set.intersection(*(ex[t] for t in TICKERS)) & set(conf))
    return len(conf) - len(common), common
