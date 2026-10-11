"""The full-schema simulator (T3; P4Q32): the synthetic loader of P4Q3.

Specification: docs/P4_SIM_SPEC.md (version 2); the section numbers below are its own. `simulate` generates a dev-like
and a confirmation-like panel, each with exactly the 60 schema columns in the dev panel's order and with its dtype
kinds, and an events table shaped as the firm events file, all from seeded generators. It reads and writes no file.

The truth is structural (§6): the hedge (1306) and the abnormal part are generated separately, and
y_oc = beta_i * y_1306_oc + the abnormal part. With the default b_mkt = gap_mkt = 0 the hedge is independent of the
design, so the AM-03 target that targets.add_targets builds recovers b, b_post and a2, and cc_abn recovers delta_cc,
up to estimation noise. Missingness knobs (§7) act after generation, on the reported columns only.

Generators (§1.4): numpy.random.default_rng(seed).spawn(5) gives, in order, the core block, the date-level draws, the
residuals, the row-level draws and the knobs. The row-level generator draws u_g (dates x tickers, standard normal),
then X (dates x tickers, standard exponential), then the pre-sample lags; the tests rely on this order.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, fields

import numpy as np
import pandas as pd

from . import blind, calendar, schema, sim

TICKERS = sim.TICKERS
BREAK_DATE = pd.Timestamp("2024-11-05")
DEV_START = pd.Timestamp("2015-01-06")
DEV_END = pd.Timestamp("2021-12-30")
DEV_PREV = pd.Timestamp("2015-01-05")

COLUMNS = (   # Table D: the dev panel's columns, in its order
    "date", "ticker", "usdjpy_ret", "usdjpy_rv", "usdjpy_bv", "eurusd_ret", "eurusd_rv", "spy_oc", "ewj_oc",
    "fcx_oc", "copx_oc", "us_n_sessions", "window_hours", "gap_adj_lag1", "oc_lag1", "range_lag1", "topix_oc_lag1",
    "earn_flag", "news_flag", "mech_flag", "audit_flag", "boj_day", "sq_day", "sq_major", "exdiv_day", "div_exdate",
    "ao_gap_adj", "ao_gap_raw", "ao_topix_gap", "y_oc", "y_topix_oc", "open", "close", "prev_close",
    "window_start_utc", "window_end_utc", "usdjpy_bars", "usdjpy_stale_start_min", "usdjpy_stale_end_min",
    "eurusd_bars", "eurusd_stale_end_min", "y_1306_oc", "ao_1306_gap_raw", "ao_1306_gap_adj", "ao_topix_gap_tradj",
    "xau_ret", "xau_rv", "xau_bv", "n225_ret", "usdjpy_us_ret", "ewj_oc_jpy", "gotobi_day", "c_usdjpy_sess_ret",
    "c_eurusd_sess_ret", "xau_bars", "xau_stale_start_min", "xau_stale_end_min", "n225_bars",
    "n225_stale_start_min", "n225_stale_end_min",
)
INT_COLUMNS = ("earn_flag", "news_flag", "mech_flag", "audit_flag", "exdiv_day", "gotobi_day", "xau_bars")
STRING_COLUMNS = ("ticker", "window_start_utc", "window_end_utc")
EVENT_COLUMNS = ("ticker", "date", "category", "note", "check_status", "check_note")
if len(COLUMNS) != 60 or frozenset(COLUMNS) != schema.all_grouped_columns():
    raise RuntimeError("COLUMNS must be exactly the schema's 60 columns")

PRICE_START = (3000.0, 2500.0, 4500.0)   # P0, per ticker
DIVIDEND = (40.0, 30.0, 50.0)            # yen per share on the ex-dividend dates, per ticker
PULL = 0.01                              # the gap's pull of the log price towards P0 (§6.3)

# The columns each missingness knob acts on (§7.1), named explicitly.
_KNOB_COLUMNS = {
    "ewj_missing": ("ewj_oc", "ewj_oc_jpy"),
    "fcx_missing": ("fcx_oc",),
    "sess_missing": ("c_usdjpy_sess_ret", "c_eurusd_sess_ret"),
    "xau_missing": ("xau_ret", "xau_rv", "xau_bv", "xau_bars", "xau_stale_start_min", "xau_stale_end_min"),
    "n225_missing": ("n225_ret", "n225_bars", "n225_stale_start_min", "n225_stale_end_min"),
}
_ZERO_COLUMNS = ("usdjpy_bars", "usdjpy_rv", "usdjpy_bv")
_HEDGE_GAP_COLUMNS = ("ao_1306_gap_adj", "ao_1306_gap_raw")
_COUNT_FIELDS = tuple(_KNOB_COLUMNS) + ("usdjpy_bars_zero",)
_EVENT_SCHEDULE = (   # §4.1: (category, months, k = k0 + step * j)
    ("TANSHIN", (2, 5, 8, 11), 6, 3),
    ("STANDALONE_NEWS", (3, 10), 4, 5),
    ("MECHANICAL", (4,), 5, 4),
    ("AUDIT_CANDIDATE", (7,), 7, 4),
)
_ALL_TICKER_TANSHIN = ((2022, 6), (2023, 12), (2025, 7))   # the 10th trading day of each


# ------------------------------------------------------------------ day arithmetic (days since 1970-01-01)
def _day(y: int, m: int, d: int) -> int:
    return int(np.datetime64(f"{y:04d}-{m:02d}-{d:02d}", "D").astype(np.int64))


def _days(index: pd.DatetimeIndex) -> np.ndarray:
    return index.values.astype("datetime64[D]").astype(np.int64)


def _weekday(d):
    """Monday = 0 (1970-01-01 was a Thursday)."""
    return (d + 3) % 7


def _month_bounds(y: int, m: int) -> tuple[int, int]:
    first = np.datetime64(f"{y:04d}-{m:02d}", "M")
    return (int(first.astype("datetime64[D]").astype(np.int64)),
            int((first + 1).astype("datetime64[D]").astype(np.int64)) - 1)


def _nth_weekday(y: int, m: int, wd: int, n: int) -> int:
    first, _ = _month_bounds(y, m)
    return first + (wd - _weekday(first)) % 7 + 7 * (n - 1)


def _last_weekday(y: int, m: int, wd: int) -> int:
    _, last = _month_bounds(y, m)
    return last - (_weekday(last) - wd) % 7


def _year_month(d: int) -> tuple[int, int]:
    k = int(np.datetime64(int(d), "D").astype("datetime64[M]").astype(np.int64))
    return 1970 + k // 12, k % 12 + 1


# ------------------------------------------------------------------ calendars (§3)
def _dev_holidays(y: int) -> set:
    """F_y, M_y and S_y of §3.1."""
    fixed = {_day(y, m, d) for m, d in ((1, 1), (1, 2), (1, 3), (2, 11), (3, 21), (4, 29), (5, 3), (5, 4), (5, 5),
                                         (9, 23), (11, 3), (11, 23), (12, 31))}
    if y >= 2016:
        fixed.add(_day(y, 8, 11))
    if y <= 2018:
        fixed.add(_day(y, 12, 23))
    if y >= 2020:
        fixed.add(_day(y, 2, 23))
    mondays = {_nth_weekday(y, 1, 0, 2), _nth_weekday(y, 7, 0, 3), _nth_weekday(y, 9, 0, 3), _nth_weekday(y, 10, 0, 2)}
    subs: set = set()
    for x in sorted(fixed - {_day(y, 1, 1), _day(y, 1, 2), _day(y, 1, 3), _day(y, 12, 31)}):
        if _weekday(x) == 6:
            d = x + 1
            while d in fixed or d in mondays or d in subs:
                d += 1
            subs.add(d)
    return fixed | mondays | subs


def dev_calendar() -> pd.DatetimeIndex:
    """§3.1: the weekdays from DEV_START to DEV_END outside the rule-based holidays (1,714 dates)."""
    hol = set().union(*(_dev_holidays(y) for y in range(2015, 2022)))
    wd = pd.bdate_range(DEV_START, DEV_END)
    return wd[~np.isin(_days(wd), sorted(hol))]


def _us_holidays(y: int) -> set:
    """§3.3: the US non-trading weekdays of year y (2015 to 2026), no observed shift, no Good Friday."""
    h = {_day(y, 1, 1), _nth_weekday(y, 1, 0, 3), _nth_weekday(y, 2, 0, 3), _last_weekday(y, 5, 0), _day(y, 7, 4),
         _nth_weekday(y, 9, 0, 1), _nth_weekday(y, 11, 3, 4), _day(y, 12, 25)}
    if y >= 2022:
        h.add(_day(y, 6, 19))
    return h


def _rolled_back(nominal: int, days: np.ndarray) -> int | None:
    """§5: the nominal date if it is in C, else the latest date of C before it; None if there is none."""
    i = int(np.searchsorted(days, nominal, side="right")) - 1
    return int(days[i]) if i >= 0 else None


# ------------------------------------------------------------------ the scenario (§7)
@dataclass(frozen=True)
class Scenario:
    b: float = 0.0
    delta_post: float = 0.0
    b_spread: tuple = (0.0, 0.0, 0.0)
    a2: float = 0.0
    a2_gap: float = 0.0
    delta_cc: float = 0.8
    b_mkt: float = 0.0
    gap_mkt: float = 0.0
    beta_hedge: tuple = (1.2, 1.0, 1.1)
    c_usd_sess: float = 0.0
    c_eur_sess: float = 0.0
    b_gotobi: float = 0.0
    tails: str = "gaussian"
    rho_fx: float = -0.44
    resid_corr: float = 0.43
    phi: float = 0.1
    ewj_missing: tuple = (3, 3)
    fcx_missing: tuple = (4, 4)
    sess_missing: tuple = (5, 5)
    xau_missing: tuple = (0, 6)
    n225_missing: tuple = (3, 3)
    n225_stale_share: tuple = (0.45, 0.05)
    usdjpy_bars_zero: tuple = (0, 0)
    xau_absent_conf: bool = False
    gotobi_zero_conf: bool = False
    hedge_gap_absent_2022: bool = False

    def __post_init__(self):
        for name in ("b_spread", "beta_hedge", "n225_stale_share") + _COUNT_FIELDS:
            v = getattr(self, name)
            if not isinstance(v, (tuple, list)):
                raise ValueError(f"{name} must be a tuple")
            object.__setattr__(self, name, tuple(v))
        if self.tails not in ("gaussian", "t5"):
            raise ValueError(f"tails must be 'gaussian' or 't5', got {self.tails!r}")
        if not (-1 < self.rho_fx < 1 and -0.5 < self.resid_corr < 1 and -1 < self.phi < 1):
            raise ValueError("rho_fx, resid_corr or phi out of range")
        if len(self.b_spread) != len(TICKERS) or len(self.beta_hedge) != len(TICKERS):
            raise ValueError("b_spread and beta_hedge need one value per ticker")
        if abs(sum(self.b_spread)) > 1e-12:
            raise ValueError("b_spread must sum to 0")
        for name in _COUNT_FIELDS:
            v = getattr(self, name)
            if len(v) != 2 or any(isinstance(c, bool) or not isinstance(c, int) or c < 0 for c in v):
                raise ValueError(f"{name} must be two non-negative integer counts")
        if len(self.n225_stale_share) != 2 or not all(0.0 <= s <= 1.0 for s in self.n225_stale_share):
            raise ValueError("n225_stale_share must be two shares in [0, 1]")

    def to_dict(self) -> dict:
        return {f.name: list(getattr(self, f.name)) if isinstance(getattr(self, f.name), tuple)
                else getattr(self, f.name) for f in fields(self)}

    @classmethod
    def not_estimable(cls) -> "Scenario":
        return cls(xau_absent_conf=True, gotobi_zero_conf=True, usdjpy_bars_zero=(0, 6), hedge_gap_absent_2022=True)


@dataclass(eq=False)
class SimOutput:
    dev: pd.DataFrame
    confirm: pd.DataFrame
    events: pd.DataFrame
    components: pd.DataFrame
    truth: dict


# ------------------------------------------------------------------ the simulator
def _check_dev_dates(dev_dates) -> pd.DatetimeIndex:
    if dev_dates is None:
        return dev_calendar()
    if not isinstance(dev_dates, pd.DatetimeIndex) or dev_dates.tz is not None:
        raise ValueError("dev_dates must be a naive DatetimeIndex")
    if len(dev_dates) < 300:
        raise ValueError("dev_dates needs at least 300 dates")
    if not (dev_dates.is_monotonic_increasing and dev_dates.is_unique):
        raise ValueError("dev_dates must be strictly increasing")
    if not (dev_dates < pd.Timestamp("2022-01-01")).all():
        raise ValueError("dev_dates must all be before 2022-01-01")
    return dev_dates


def simulate(seed: int, scenario: Scenario | None = None, *, dev_dates=None) -> SimOutput:
    """§2: the dev-like and confirmation-like frames, the events table, the components and the truth."""
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be an int >= 0")
    sc = Scenario() if scenario is None else scenario
    if not isinstance(sc, Scenario):
        raise ValueError("scenario must be a Scenario")
    dev_idx = _check_dev_dates(dev_dates)
    conf_idx = calendar.confirmation_calendar()
    n_dev, n_conf = len(dev_idx), len(conf_idx)
    n, k = n_dev + n_conf, len(TICKERS)
    for name in _COUNT_FIELDS:
        cd, cc = getattr(sc, name)
        if cd > n_dev or cc > n_conf:
            raise ValueError(f"{name} asks for more dates than its part has")

    # ---- §3.3: the joined calendar C, prev(t), the windows, the bar counts and the US sessions
    days = np.r_[_days(dev_idx), _days(conf_idx)]
    first_prev = int(days[0]) - 1
    while _weekday(first_prev) >= 5:
        first_prev -= 1
    prev = np.r_[first_prev, days[:-1]]
    brk = _day(BREAK_DATE.year, BREAK_DATE.month, BREAK_DATE.day)
    close_min = np.where(prev < brk, 15 * 60, 15 * 60 + 30)
    start_min = prev * 1440 + close_min - 9 * 60          # minutes since the epoch, UTC
    end_min = days * 1440 + 8 * 60 + 59 - 9 * 60
    window_minutes = end_min - start_min
    weekend = np.array([sum(1 for d in range(int(p) + 1, int(t)) if _weekday(d) >= 5) for p, t in zip(prev, days)])
    bars = (window_minutes - 1440 * weekend).astype(float)
    us_hol = set().union(*(_us_holidays(y) for y in range(2015, 2027)))
    us_n = np.array([sum(1 for d in range(int(p), int(t)) if _weekday(d) < 5 and d not in us_hol)
                     for p, t in zip(prev, days)], dtype=float)
    start_txt = [str(pd.Timestamp(np.datetime64(int(m), "m"))) for m in start_min]
    end_txt = [str(pd.Timestamp(np.datetime64(int(m), "m"))) for m in end_min]
    s_fx = np.sqrt(bars / 1079.0)
    s_us = np.sqrt(us_n)
    post = days >= brk
    s_sess = np.where(post, math.sqrt(6.5 / 6.0), 1.0)
    conf_part = np.arange(n) >= n_dev

    # ---- §4 and §5: the trading days of each month, the events, the flags and the calendar columns
    by_month: dict = {}
    for d in days:
        by_month.setdefault(_year_month(int(d)), []).append(int(d))
    pos = {int(d): i for i, d in enumerate(days)}
    years = sorted({ym[0] for ym in by_month})

    def kth(y, m, kk):
        ds = by_month.get((y, m), [])
        return ds[kk - 1] if len(ds) >= kk else None

    ev_rows = set()
    for y in years:
        for cat, months, k0, step in _EVENT_SCHEDULE:
            for j, t in enumerate(TICKERS):
                for m in months:
                    d = kth(y, m, k0 + step * j)
                    if d is not None:
                        ev_rows.add((t, d, cat))
    for y, m in _ALL_TICKER_TANSHIN:
        d = kth(y, m, 10)
        if d is not None:
            for t in TICKERS:
                ev_rows.add((t, d, "TANSHIN"))
    flags = {name: np.zeros((n, k), dtype=np.int64) for name in ("earn_flag", "news_flag", "mech_flag", "audit_flag")}
    offsets = {"TANSHIN": ("earn_flag", (0, 1)), "STANDALONE_NEWS": ("news_flag", (0, 1)),
               "AUDIT_CANDIDATE": ("audit_flag", (0, 1)), "MECHANICAL": ("mech_flag", (0,))}
    for t, d, cat in ev_rows:
        name, offs = offsets[cat]
        i = pos[d]
        for o in offs:
            if i + o < n:
                flags[name][i + o, TICKERS.index(t)] = 1

    first, last = int(days[0]), int(days[-1])
    sq = np.zeros(n)
    sq_major = np.zeros(n)
    gotobi = np.zeros(n, dtype=np.int64)
    months_all = sorted({_year_month(d) for d in range(first, last + 1)})
    for y, m in months_all:
        nominal = _nth_weekday(y, m, 4, 2)                 # the second Friday
        if first <= nominal <= last:
            d = _rolled_back(nominal, days)
            if d is not None:
                sq[pos[d]] = 1.0
                if m in (3, 6, 9, 12):
                    sq_major[pos[d]] = 1.0
        lo, hi = _month_bounds(y, m)
        nominals = [lo + dd - 1 for dd in (5, 10, 15, 20, 25, 30) if lo + dd - 1 <= hi] + [hi]
        for nominal in nominals:
            if first <= nominal <= last:
                d = _rolled_back(nominal, days)
                if d is not None:
                    gotobi[pos[d]] = 1
    boj = np.zeros(n)
    for (y, m), ds in by_month.items():
        if m in (1, 3, 4, 6, 7, 9, 10, 12) and len(ds) >= 15:
            boj[pos[ds[14]]] = 1.0
    exdiv = np.zeros(n, dtype=np.int64)
    ex1306 = np.zeros(n, dtype=bool)
    for y in range(2015, 2026):
        for m in (3, 9):
            ds = by_month.get((y, m), [])
            if len(ds) >= 2:
                exdiv[pos[ds[-2]]] = 1
        d = kth(y, 7, 8)
        if d is not None:
            ex1306[pos[d]] = True
    mass = exdiv.astype(float)
    div = exdiv[:, None] * np.array(DIVIDEND)[None, :]

    # ---- §6: the generators, in a fixed order
    g_core, g_date, g_resid, g_row, g_knob = np.random.default_rng(seed).spawn(5)
    z = g_core.standard_normal((n, 4)) @ np.linalg.cholesky(sim.pred_corr(sc.rho_fx)).T
    if sc.tails == "t5":
        z = z / np.sqrt(g_core.chisquare(5, size=n) / 5.0)[:, None] * math.sqrt(3.0 / 5.0)
    w = g_date.standard_normal((n, 14))                     # w1 .. w14 in columns 0 .. 13
    u_bv, u_xbv = g_date.uniform(0.7, 1.05, size=n), g_date.uniform(0.7, 1.05, size=n)
    fx_stale = []
    for _ in range(5):
        zero = g_date.random(n) < 0.9
        fx_stale.append(np.where(zero, 0.0, g_date.integers(1, 4, size=n).astype(float)))
    share = np.where(conf_part, sc.n225_stale_share[1], sc.n225_stale_share[0])
    stale = g_date.random(n) < share
    start_side = g_date.random(n) < 0.5
    hi_end = g_date.integers(6, 121, size=n).astype(float)
    lo_end = g_date.integers(0, 6, size=n).astype(float)
    calm_zero = g_date.random((n, 2)) < 0.8
    calm_val = g_date.integers(1, 6, size=(n, 2)).astype(float)
    calm = np.where(calm_zero, 0.0, calm_val)
    n225_start = np.where(stale, np.where(start_side, hi_end, lo_end), calm[:, 0])
    n225_end = np.where(stale, np.where(start_side, lo_end, hi_end), calm[:, 1])
    topix_lag0 = g_date.normal(0.0, 0.008)

    rc = np.full((k, k), sc.resid_corr) + (1.0 - sc.resid_corr) * np.eye(k)
    U = g_resid.standard_normal((n, k)) @ np.linalg.cholesky(rc).T
    if sc.tails == "t5":
        U = U / np.sqrt(g_resid.chisquare(5, size=n) / 5.0)[:, None] * math.sqrt(3.0 / 5.0)
    eps = np.empty_like(U)
    eps[0] = U[0]
    for t in range(1, n):
        eps[t] = sc.phi * eps[t - 1] + math.sqrt(1.0 - sc.phi ** 2) * U[t]

    u_g = g_row.standard_normal((n, k))
    X = g_row.standard_exponential((n, k))
    gap_lag0 = g_row.normal(0.0, 0.012, size=k)
    oc_lag0 = g_row.normal(0.0, 0.016, size=k)
    range_lag0 = np.abs(oc_lag0) + 0.008 * g_row.standard_exponential(k)

    # §6.1: the date-level predictors
    sd = sim.PRED_SD
    has_us = us_n > 0
    e = sd[0] * s_fx * z[:, 0]
    eur = sd[1] * s_fx * z[:, 1]
    spy = np.where(has_us, sd[2] * s_us * z[:, 2], 0.0)
    copx = np.where(has_us, sd[3] * s_us * z[:, 3], 0.0)
    ewj = np.where(has_us, 0.8 * spy + 0.006 * s_us * w[:, 0], 0.0)
    fcx = np.where(has_us, 1.3 * copx + 0.012 * s_us * w[:, 1], 0.0)
    usd_us = np.where(has_us, 0.4 * e + 0.0015 * s_us * w[:, 2], 0.0)
    ewj_jpy = ewj + usd_us
    xau_ret = 0.8 * eur + 0.006 * s_fx * w[:, 3]
    n225_ret = 0.5 * e + 0.6 * spy + 0.005 * s_fx * w[:, 4]
    c_usd = 0.003 * s_sess * w[:, 5]
    c_eur = 0.0025 * s_sess * (-0.4 * w[:, 5] + math.sqrt(0.84) * w[:, 6])
    usd_rv = bars * 1.2950114214e-08 * np.exp(0.5 * w[:, 7])
    usd_bv = usd_rv * u_bv
    eur_rv = bars * 1.0e-08 * np.exp(0.5 * w[:, 8])
    xau_bars = bars - 60.0
    xau_rv = xau_bars * 4.0e-08 * np.exp(0.5 * w[:, 9])
    xau_bv = xau_rv * u_xbv
    n225_bars = bars - 120.0
    # §6.2: the hedge and TOPIX
    h = sc.b_mkt * e + 0.008 * w[:, 10]
    topix_oc = h + 0.0005 * w[:, 11]
    hg = sc.gap_mkt * e + 0.4 * spy + 0.006 * w[:, 12]
    gap_raw_1306 = np.where(ex1306, hg - 0.02, hg)
    topix_gap = hg - 0.008 * mass + 0.0005 * w[:, 13]
    topix_gap_tradj = topix_gap + 0.008 * mass

    # §6.3: the miners
    beta = np.array(sc.beta_hedge, dtype=float)
    fe, gam, kap, sig = (np.array(v, dtype=float) for v in (sim.FE, sim.SPY_SLOPE, sim.COPX_SLOPE, sim.DEFAULT_SIGMA))
    p0 = np.array(PRICE_START)
    b_it = sc.b + np.array(sc.b_spread, dtype=float)[None, :] + sc.delta_post * post[:, None]
    resid = sig[None, :] * eps
    G = gotobi.astype(float)
    v = (fe[None, :] + b_it * e[:, None] + sc.a2 * eur[:, None] + gam[None, :] * spy[:, None]
         + kap[None, :] * copx[:, None] + sc.c_usd_sess * c_usd[:, None] + sc.c_eur_sess * c_eur[:, None]
         + sc.b_gotobi * (e * G)[:, None] + resid)
    y_oc = beta[None, :] * h[:, None] + v
    gap_resid = 0.008 * u_g
    gap_adj = np.empty((n, k))
    gap_raw = np.empty((n, k))
    px_open = np.empty((n, k))
    px_close = np.empty((n, k))
    px_prev = np.empty((n, k))
    for i in range(k):
        prev_close = float(p0[i])
        for t in range(n):
            g = ((sc.delta_cc - b_it[t, i]) * e[t] + sc.a2_gap * eur[t] + 0.2 * spy[t]
                 - PULL * math.log(prev_close / p0[i]) + gap_resid[t, i])
            adj = beta[i] * hg[t] + g
            op = (prev_close - div[t, i]) * math.exp(adj)
            cl = op * math.exp(y_oc[t, i])
            px_prev[t, i], gap_adj[t, i], px_open[t, i], px_close[t, i] = prev_close, adj, op, cl
            gap_raw[t, i] = math.log(op / prev_close)
            prev_close = cl
    rng_t = np.abs(y_oc) + 0.008 * X
    gap_lag = np.r_[gap_lag0[None, :], gap_adj[:-1]]
    oc_lag = np.r_[oc_lag0[None, :], y_oc[:-1]]
    range_lag = np.r_[range_lag0[None, :], rng_t[:-1]]
    topix_lag = np.r_[topix_lag0, topix_oc[:-1]]

    # ---- the reported columns, (n, k) each, before the knobs
    def tile(x):
        return np.repeat(np.asarray(x, dtype=float)[:, None], k, axis=1)

    rep = {
        "usdjpy_ret": tile(e), "usdjpy_rv": tile(usd_rv), "usdjpy_bv": tile(usd_bv), "eurusd_ret": tile(eur),
        "eurusd_rv": tile(eur_rv), "spy_oc": tile(spy), "ewj_oc": tile(ewj), "fcx_oc": tile(fcx), "copx_oc": tile(copx),
        "us_n_sessions": tile(us_n), "window_hours": tile(window_minutes / 60), "gap_adj_lag1": gap_lag,
        "oc_lag1": oc_lag, "range_lag1": range_lag, "topix_oc_lag1": tile(topix_lag),
        "earn_flag": flags["earn_flag"].astype(float), "news_flag": flags["news_flag"].astype(float),
        "mech_flag": flags["mech_flag"].astype(float), "audit_flag": flags["audit_flag"].astype(float),
        "boj_day": tile(boj), "sq_day": tile(sq), "sq_major": tile(sq_major), "exdiv_day": tile(exdiv),
        "div_exdate": div.astype(float), "ao_gap_adj": gap_adj, "ao_gap_raw": gap_raw, "ao_topix_gap": tile(topix_gap),
        "y_oc": y_oc, "y_topix_oc": tile(topix_oc), "open": px_open, "close": px_close, "prev_close": px_prev,
        "usdjpy_bars": tile(bars), "usdjpy_stale_start_min": tile(fx_stale[0]),
        "usdjpy_stale_end_min": tile(fx_stale[1]), "eurusd_bars": tile(bars), "eurusd_stale_end_min": tile(fx_stale[2]),
        "y_1306_oc": tile(h), "ao_1306_gap_raw": tile(gap_raw_1306), "ao_1306_gap_adj": tile(hg),
        "ao_topix_gap_tradj": tile(topix_gap_tradj), "xau_ret": tile(xau_ret), "xau_rv": tile(xau_rv),
        "xau_bv": tile(xau_bv), "n225_ret": tile(n225_ret), "usdjpy_us_ret": tile(usd_us), "ewj_oc_jpy": tile(ewj_jpy),
        "gotobi_day": tile(gotobi), "c_usdjpy_sess_ret": tile(c_usd), "c_eurusd_sess_ret": tile(c_eur),
        "xau_bars": tile(xau_bars), "xau_stale_start_min": tile(fx_stale[3]), "xau_stale_end_min": tile(fx_stale[4]),
        "n225_bars": tile(n225_bars), "n225_stale_start_min": tile(n225_start), "n225_stale_end_min": tile(n225_end),
    }

    # ---- §7.2: the knobs, on the reported columns only, in a fixed order
    parts = (np.arange(n_dev), np.arange(n_dev, n))
    no_flag = (flags["earn_flag"].sum(axis=1) + flags["news_flag"].sum(axis=1)) == 0
    for p, rows in enumerate(parts):
        for name, cols in _KNOB_COLUMNS.items():
            pick = g_knob.choice(rows, size=getattr(sc, name)[p], replace=False)
            for c in cols:
                rep[c][pick] = np.nan
        eligible = rows[no_flag[rows]]
        cnt = sc.usdjpy_bars_zero[p]
        if cnt > len(eligible):
            raise ValueError("usdjpy_bars_zero asks for more dates than its part has without earn_flag or news_flag")
        pick = g_knob.choice(eligible, size=cnt, replace=False)
        for c in _ZERO_COLUMNS:
            rep[c][pick] = 0.0
    if sc.xau_absent_conf:
        for c in _KNOB_COLUMNS["xau_missing"]:
            rep[c][parts[1]] = np.nan
    if sc.gotobi_zero_conf:
        rep["gotobi_day"][parts[1]] = 0.0
    if sc.hedge_gap_absent_2022:
        in_2022 = conf_part & (days >= _day(2022, 1, 1)) & (days <= _day(2022, 12, 31))
        for c in _HEDGE_GAP_COLUMNS:
            rep[c][in_2022] = np.nan

    # ---- §4.2 and §8: the events, the truth, the frames and the components
    c_index = dev_idx.append(conf_idx)
    ev_list = sorted(ev_rows, key=lambda r: (r[1], r[0], r[2]))
    events = pd.DataFrame({
        "ticker": [r[0] for r in ev_list],
        "date": c_index[[pos[r[1]] for r in ev_list]],
        "category": [r[2] for r in ev_list],
        "note": ["synthetic"] * len(ev_list),
        "check_status": ["synthetic"] * len(ev_list),
        "check_note": ["synthetic"] * len(ev_list),
    })
    events = events.sort_values(["date", "ticker", "category"], kind="mergesort").reset_index(drop=True)

    t_conf, excluded = calendar.t_conf(events, dev_idx)
    conf_days = days[n_dev:]
    n_pre, n_post = int((conf_days < brk).sum()), int((conf_days >= brk).sum())
    n_a = int(((conf_days >= _day(2023, 1, 1)) & (conf_days < brk)).sum())
    b_post_true = sc.b + sc.delta_post
    dcc = sc.delta_cc
    truth = {
        "source": "sim_full",
        "seed": seed,
        "scenario": sc.to_dict(),
        "constants": {"fe": list(sim.FE), "spy_slope": list(sim.SPY_SLOPE), "copx_slope": list(sim.COPX_SLOPE),
                      "sigma": list(sim.DEFAULT_SIGMA), "pred_sd": [float(x) for x in sim.PRED_SD],
                      "price_start": list(PRICE_START), "dividend": list(DIVIDEND), "pull": PULL},
        "break_date": "2024-11-05",
        "b_pre": sc.b,
        "b_post": b_post_true,
        "b_ticker": {t: sc.b + sc.b_spread[i] for i, t in enumerate(TICKERS)},
        "b_conf_mix": (n_pre * sc.b + n_post * b_post_true) / (n_pre + n_post),
        "f_2022": None if dcc == 0 else sc.b / dcc,
        "f_2023_2026": None if dcc == 0 else ((n_a * sc.b + n_post * b_post_true) / (n_a + n_post)) / dcc,
        "exact_target": bool(sc.b_mkt == 0 and sc.gap_mkt == 0),
        "n_dev_dates": n_dev,
        "n_conf_dates": n_conf,
        "t_conf": int(t_conf),
        "excluded_all_three": [str(pd.Timestamp(d).date()) for d in excluded],
    }

    frames = []
    for p, (rows, idx, label) in enumerate(zip(parts, (dev_idx, conf_idx), ("dev", "confirmation"))):
        data = {"date": np.repeat(idx.values, k), "ticker": list(TICKERS) * len(idx)}
        for c in COLUMNS:
            if c in ("date", "ticker"):
                continue
            if c == "window_start_utc":
                data[c] = [s for s in (start_txt[r] for r in rows) for _ in range(k)]
            elif c == "window_end_utc":
                data[c] = [s for s in (end_txt[r] for r in rows) for _ in range(k)]
            else:
                col = rep[c][rows].reshape(-1)
                data[c] = col.astype(np.int64) if c in INT_COLUMNS and not np.isnan(col).any() else col
        df = pd.DataFrame(data)[list(COLUMNS)]
        df.attrs = {"provenance": blind.SYNTHETIC, "part": label, "truth": truth}
        blind.require_unblinded(df)   # §1.4: fail closed on a frame holding registered real values
        frames.append(df)
    dev_df, conf_df = frames

    comp = pd.DataFrame({
        "date": pd.concat([dev_df["date"], conf_df["date"]], ignore_index=True),
        "ticker": list(TICKERS) * n,
        "part": ["dev"] * (n_dev * k) + ["confirmation"] * (n_conf * k),
        "b_it": b_it.reshape(-1),
        "resid": resid.reshape(-1),
        "gap_resid": gap_resid.reshape(-1),
    })
    return SimOutput(dev=dev_df, confirm=conf_df, events=events, components=comp, truth=truth)
