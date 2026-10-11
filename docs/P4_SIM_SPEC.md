# P4_SIM_SPEC: the full-schema simulator (T3; P4Q32)

Version 2. Version 1 was written by the supervisor chat that began on 2026-10-09, for P4-3; this version was written by the supervisor chat that began on 2026-10-11, before any code of P4-3 existed, and §10 lists its changes. It specifies `ofilt/drift/sim_full.py` and its tests `tests/test_p4_sim_full.py`. P4-3 commits it as `docs/P4_SIM_SPEC.md`. A change after P4-3 is a new version of this file, recorded with its reason.

The simulator is the synthetic loader of P4Q3: it hands the confirmation module (P4-4) frames that look like the real ones, with a known truth. It generates the panel directly, with every value drawn from a seeded generator, and reads and writes no file.

## 1. Rules for the code

### 1.1 Placement
- One new module, `ofilt/drift/sim_full.py`, and one new test file, `tests/test_p4_sim_full.py`. No existing file changes. `ofilt/drift/sim.py` (C7-hashed) is imported for its constants and stays byte-identical.
- The module imports only `__future__`, `dataclasses`, `math`, `typing`, `numpy`, `pandas`, and from the package `blind`, `calendar`, `schema` and `sim`. It does not import `io` or `spec`.
- It opens, reads and writes no file: it calls no loader of `io`, and not `Spec.load`, which reads the spec file. Only the tests read the spec, for its seed.

### 1.2 Repository-wide static tests it must satisfy
- `tests/test_sim_b5.py`: the module never names the unguarded design core, in code, strings or docstrings. The tests do not name it either.
- `tests/test_schema.py`: no column selection by prefix or pattern. Columns are named explicitly.
- `tests/test_docs_d3b.py`: neither tag name appears in the module.
- `tests/test_docs_d6.py`: no file is written, so no `.csv` file appears anywhere.

### 1.3 Read first (as text)
- `ofilt/drift/sim.py`, `schema.py`, `targets.py`, `calendar.py`, `io.py`, `blind.py`, `spec.py`.
- `ofilt/drift/inference.py`: `build_design`, `DesignError`, `Result.param`, `fit_dk` and `subset_design`.
- `build/pass1/build_panel.py`, lines 98 to 140 (the window timestamps), and `build/pass2/build_panel_p2.py`, lines 146 and 147 (the bar columns written as nullable integers).
- `tests/test_sim_b4.py`, `tests/test_io.py`, `tests/test_sim_b5.py`, `tests/test_schema.py`, `tests/test_docs_d3b.py` and `tests/test_docs_d6.py`, for the repository's test conventions and static scans.

### 1.4 Determinism and the guard
- Every output is a deterministic function of `(seed, scenario, dev_dates)`. All randomness comes from `numpy.random.default_rng(seed)` or generators spawned from it, in an order the module fixes.
- Before returning, `simulate` calls `blind.require_unblinded` on the dev-like and the confirmation-like frame, so a frame holding registered real values is refused (fail closed).

## 2. API

- `TICKERS = sim.TICKERS` (`"5706"`, `"5711"`, `"5713"`, in this order; every per-ticker tuple below follows it).
- `BREAK_DATE = pd.Timestamp("2024-11-05")`.
- `DEV_START = pd.Timestamp("2015-01-06")`, `DEV_END = pd.Timestamp("2021-12-30")`.
- `DEV_PREV = pd.Timestamp("2015-01-05")`: the trading day before `DEV_START`.
- `COLUMNS`: the 60 names of Table D, in its order.
- `INT_COLUMNS`: the 7 names whose kind in Table D is `i`.
- `EVENT_COLUMNS = ("ticker", "date", "category", "note", "check_status", "check_note")`.
- `dev_calendar() -> pd.DatetimeIndex`: §3.1.
- `Scenario`: a frozen dataclass (§7), with `Scenario.not_estimable()` and `Scenario.to_dict()`.
- `SimOutput`: a dataclass (`eq=False`), fields `dev`, `confirm`, `events`, `components` and `truth` (§8).
- `simulate(seed: int, scenario: Scenario | None = None, *, dev_dates=None) -> SimOutput`.
  - `seed` must be an `int` (not a `bool`) and at least 0; there is no default seed. `scenario=None` means `Scenario()`.
  - `dev_dates`, if given, must be a strictly increasing `DatetimeIndex` of at least 300 dates, all before 2022-01-01. It replaces `dev_calendar()`, and the trading day before its first date is the weekday before it.
  - Anything else raises `ValueError`.

## 3. Calendars and windows

### 3.1 The dev history
For each year y from 2015 to 2021:
- **Fixed holidays F_y:** Jan 1, Jan 2, Jan 3, Feb 11, Mar 21, Apr 29, May 3, May 4, May 5, Sep 23, Nov 3, Nov 23 and Dec 31; plus Aug 11 if y ≥ 2016, Dec 23 if y ≤ 2018, and Feb 23 if y ≥ 2020.
- **Monday holidays M_y:** the 2nd Monday of January, the 3rd Monday of July, the 3rd Monday of September and the 2nd Monday of October.
- **Substitutes S_y:** take each date x of F_y other than Jan 1, Jan 2, Jan 3 and Dec 31, in date order. If x falls on a Sunday, add the first day after x that is in none of F_y, M_y and S_y as built so far.

`dev_calendar()` is the weekdays from `DEV_START` to `DEV_END` that are in no F_y, M_y or S_y: **1,714 dates**. It is a rule-based stand-in (the real dev panel has 1,708 dates), not a copy of any data.

### 3.2 The confirmation dates
`calendar.confirmation_calendar()`, unchanged: 1,019 dates from 2022-01-04 to 2026-03-05.

### 3.3 The joined calendar and the windows
- The joined calendar C is the dev dates followed by the confirmation dates.
- **prev(t)** is the date before t in C. For the first dev date it is `DEV_PREV`, or the weekday before the first date of `dev_dates`.
- **The window of date t** runs from prev(t) at its TSE close to t at 08:59 JST. The close is 15:00 JST if prev(t) < `BREAK_DATE`, and 15:30 JST otherwise. JST is UTC + 9 h.
- **`window_minutes`** is the window's length in whole minutes.
- **`window_hours`** = `window_minutes` / 60.
- **`window_start_utc` and `window_end_utc`** are the text that `str()` gives for the naive UTC `pd.Timestamp` of each end, for example `2015-01-05 06:00:00`. This is the format `build/pass1/build_panel.py` writes (`pd.Timestamp` of a naive UTC `numpy.datetime64`).
- **The bar count** = `window_minutes` − 1440 × (number of Saturdays and Sundays strictly between prev(t) and t).
  - `usdjpy_bars` = `eurusd_bars` = the bar count.
  - `xau_bars` = the bar count − 60.
  - `n225_bars` = the bar count − 120.
- **The FX scale** s_fx(t) = sqrt(bar count / 1079).
- **US sessions.** A US trading day is a weekday that is not one of these, for each year from 2015 to 2026: Jan 1, the 3rd Monday of January, the 3rd Monday of February, the last Monday of May, Jun 19 (from 2022), Jul 4, the 1st Monday of September, the 4th Thursday of November and Dec 25. No observed-holiday shift is applied, and Good Friday is not modelled.
  - **`us_n_sessions`** of date t is the number of US trading days d with prev(t) ≤ d ≤ t − 1 day.
  - **The US scale** s_us(t) = sqrt(`us_n_sessions`), which is 0 when there is no session.
- **The session scale** s_sess(t) = 1 if t < `BREAK_DATE`, and sqrt(6.5/6) otherwise.

**Spot values (default calendar):**

| Date | prev | `window_hours` | Bar count | `us_n_sessions` | `window_start_utc` | `window_end_utc` |
|---|---|---|---|---|---|---|
| 2015-01-06 | 2015-01-05 | 1079/60 | 1079 | 1 | 2015-01-05 06:00:00 | 2015-01-05 23:59:00 |
| 2015-01-20 | 2015-01-19 | 1079/60 | 1079 | 0 | 2015-01-19 06:00:00 | 2015-01-19 23:59:00 |
| 2022-01-04 | 2021-12-30 | 6839/60 | 3959 | 3 | 2021-12-30 06:00:00 | 2022-01-03 23:59:00 |
| 2023-07-05 | 2023-07-04 | 1079/60 | 1079 | 0 | 2023-07-04 06:00:00 | 2023-07-04 23:59:00 |
| 2024-11-05 | 2024-11-01 | 5399/60 | 2519 | 2 | 2024-11-01 06:00:00 | 2024-11-04 23:59:00 |
| 2024-11-06 | 2024-11-05 | 1049/60 | 1049 | 1 | 2024-11-05 06:30:00 | 2024-11-05 23:59:00 |

## 4. Events and flags

### 4.1 The schedule
"The k-th trading day of month (y, m)" means the k-th date of C in that month. An event is scheduled only if that date exists in C. For each year of C and each ticker index j (0, 1, 2 for 5706, 5711, 5713):

| Category | Months | k |
|---|---|---|
| TANSHIN | 2, 5, 8, 11 | 6 + 3j |
| STANDALONE_NEWS | 3, 10 | 4 + 5j |
| MECHANICAL | 4 | 5 + 4j |
| AUDIT_CANDIDATE | 7 | 7 + 4j |

In addition there is a TANSHIN for all three tickers on the 10th trading day of 2022-06, 2023-12 and 2025-07.

### 4.2 The events table
- One row per (ticker, release date, category), with the release date equal to the scheduled date.
- Columns `EVENT_COLUMNS`, in that order. `ticker` holds the strings of `TICKERS`, `date` is a datetime column, and `note`, `check_status` and `check_note` all hold the string `synthetic`.
- Rows are sorted by (date, ticker, category), with a fresh RangeIndex.
- **Counts on the default calendar:** TANSHIN 144 (84 in dev, 60 in confirmation), STANDALONE_NEWS 67 (42, 25), MECHANICAL 33 (21, 12), AUDIT_CANDIDATE 33 (21, 12). Total 277.

### 4.3 The flags
Each flag is per ticker and is set on the joined calendar. D is the first date of C on or after the release date (here, the release date itself), and D+1 is the next date of C, if one exists.
- `earn_flag` = 1 on D and D+1 of each TANSHIN of that ticker, else 0.
- `news_flag` is the same rule for STANDALONE_NEWS.
- `audit_flag` is the same rule for AUDIT_CANDIDATE.
- `mech_flag` = 1 on D of each MECHANICAL, else 0.

### 4.4 T_conf
`calendar.t_conf(events, dev dates)` must return 1013 and exactly the six dates **2022-06-14, 2022-06-15, 2023-12-14, 2023-12-15, 2025-07-14 and 2025-07-15**. These come from the three all-ticker releases; no other confirmation date is excluded for all three tickers.

## 5. Calendar columns

"Roll back" means: if a nominal date is not in C, use the latest date of C before it; if there is none, skip it. Only nominal dates from C's first date to C's last date are used.

- **`sq_day`** = 1.0 on the second Friday of each month, rolled back; else 0.0.
- **`sq_major`** = 1.0 on those dates in March, June, September and December; else 0.0.
- **`gotobi_day`** = 1 on the 5th, 10th, 15th, 20th, 25th and 30th and the last calendar day of each month, each rolled back; else 0. A month with no 30th has no nominal 30th. It is an integer.
- **`boj_day`** = 1.0 on the 15th trading day of January, March, April, June, July, September, October and December; else 0.0. The rule applies to every month of C: that is 8 dates in each year from 2015 to 2025 and 1 in 2026 (January), 89 in all.
- **The ex-dividend dates** are the second-to-last trading day of March and of September, in each year from 2015 to 2025: 22 dates.
  - On them, `exdiv_day` = 1 and `div_exdate` = the ticker's dividend (40.0, 30.0, 50.0 yen).
  - Elsewhere, `exdiv_day` = 0 and `div_exdate` = 0.0.
  - The same dates are the TOPIX mass ex-dividend dates.
- **The 1306 ex-date** is the 8th trading day of July, in each year from 2015 to 2025: 11 dates.

All these columns are date-level, identical for the three tickers, except `div_exdate`, whose amount is per ticker.

## 6. The data-generating process

Notation:
- All noise terms below (w, u, X and the U behind ε_it) are mutually independent draws, independent across dates and tickers, apart from the dependence the formulas state.
- "w_k" is a date-level standard normal, common to the three tickers.
- "u_it" is a row-level standard normal.
- The AR(1) recursion runs over C, continuous across the dev and confirmation parts.
- `PRED_SD` (0.005, 0.004, 0.009, 0.016), `pred_corr`, `FE`, `SPY_SLOPE`, `COPX_SLOPE` and `DEFAULT_SIGMA` come from `sim`. For ticker i the last four give fe_i, γ_i, κ_i and σ_i.

### 6.1 Date-level predictors
- **The core block.** z_t is drawn with correlation `pred_corr(rho_fx)`. With `tails = "t5"`, z_t is mixed as `sim`'s innovations are: one chi-square(5) per date, rescaled by sqrt(3/5).
  - `usdjpy_ret` e = 0.005 · s_fx · z1;
  - `eurusd_ret` eur = 0.004 · s_fx · z2;
  - `spy_oc` spy = 0.009 · s_us · z3;
  - `copx_oc` copx = 0.016 · s_us · z4.
- **Other US and overnight columns:**
  - `ewj_oc` = 0.8 · spy + 0.006 · s_us · w1;
  - `fcx_oc` = 1.3 · copx + 0.012 · s_us · w2;
  - `usdjpy_us_ret` = 0.4 · e + 0.0015 · s_us · w3 if `us_n_sessions` > 0, else exactly 0.0;
  - `ewj_oc_jpy` = `ewj_oc` + `usdjpy_us_ret`.
  - When `us_n_sessions` = 0, `spy_oc`, `ewj_oc`, `fcx_oc`, `copx_oc`, `usdjpy_us_ret` and `ewj_oc_jpy` are exactly 0.0.
- **Gold and the Nikkei proxy:**
  - `xau_ret` = 0.8 · eur + 0.006 · s_fx · w4;
  - `n225_ret` = 0.5 · e + 0.6 · spy + 0.005 · s_fx · w5.
- **Session FX:**
  - `c_usdjpy_sess_ret` = 0.003 · s_sess · w6;
  - `c_eurusd_sess_ret` = 0.0025 · s_sess · (−0.4 · w6 + sqrt(0.84) · w7).
- **Variances** (U(a, b) is a uniform draw):
  - `usdjpy_rv` = bar count · 1.2950114214e-08 · exp(0.5 · w8);
  - `usdjpy_bv` = `usdjpy_rv` · U(0.7, 1.05);
  - `eurusd_rv` = bar count · 1.0e-08 · exp(0.5 · w9);
  - `xau_rv` = `xau_bars` · 4.0e-08 · exp(0.5 · w10);
  - `xau_bv` = `xau_rv` · U(0.7, 1.05).
- **FX staleness.** `usdjpy_stale_start_min`, `usdjpy_stale_end_min`, `eurusd_stale_end_min`, `xau_stale_start_min` and `xau_stale_end_min` are each 0.0 with probability 0.9, else an integer from 1 to 3 (as a float).
- **Nikkei staleness.** A night is stale with probability `n225_stale_share` of its part. On a stale night, one endpoint, start or end with equal chance, is an integer from 6 to 120 and the other an integer from 0 to 5. On other nights each endpoint is 0 with probability 0.8, else an integer from 1 to 5. All are floats.

### 6.2 The hedge (1306) and TOPIX
These are date-level, common to the three tickers.
- `y_1306_oc` h = b_mkt · e + 0.008 · w11;
- `y_topix_oc` = h + 0.0005 · w12;
- the hedge gap hg = gap_mkt · e + 0.4 · spy + 0.006 · w13; `ao_1306_gap_adj` = hg;
- `ao_1306_gap_raw` = hg − 0.02 on the 1306 ex-dates, else hg;
- `ao_topix_gap` = hg − 0.008 · 1[mass ex-date] + 0.0005 · w14;
- `ao_topix_gap_tradj` = `ao_topix_gap` + 0.008 · 1[mass ex-date].

**The default is exact.** With b_mkt = 0 and gap_mkt = 0, `y_1306_oc` is independent of every regressor of the design and of the abnormal part, and the hedge gap loads on no FX regressor (only on `spy_oc`, which the ticker-specific controls absorb). The expanding β that `targets.add_targets` estimates is then consistent for β_i, so the AM-03 target's FX slopes are b, b_post and a₂, and `cc_abn`'s FX slope is δ_cc, up to estimation noise.

With b_mkt ≠ 0, the regression of `y_oc` on h absorbs part of the abnormal FX exposure, and the target's slope differs systematically from b. The truth then gives only the structural slopes (`exact_target` False).

### 6.3 The miners
For each ticker i and date t:
- b_it = b + b_spread_i + delta_post · 1[t ≥ `BREAK_DATE`].
- **The abnormal part** v_it = fe_i + b_it · e + a2 · eur + γ_i · spy + κ_i · copx + c_usd_sess · c_usd + c_eur_sess · c_eur + b_gotobi · e · G_t + σ_i · ε_it. Here c_usd, c_eur and G_t are the generated session columns and the generated gotobi indicator, before §7's knobs change them.
- **The residual:**
  - ε_i,0 = U_i,0;
  - ε_it = φ · ε_i,t−1 + sqrt(1 − φ²) · U_it;
  - U_t is drawn across the three tickers with equal correlation `resid_corr`, and mixed by its own chi-square per date when `tails = "t5"`.
- `y_oc` = β_i · h + v_it, with β_i = `beta_hedge`[i].
- **The gap part** g_it = (δ_cc − b_it) · e + a2_gap · eur + 0.2 · spy − 0.01 · ln(`prev_close`_it / P0_i) + 0.008 · u_g,it. P0 = (3000.0, 2500.0, 4500.0).
- `ao_gap_adj` = β_i · hg + g_it.
- **Prices**, in date order per ticker:
  - `prev_close` of the first dev date = P0_i, and of every later date = the previous row's `close`;
  - `open` = (`prev_close` − `div_exdate`) · exp(`ao_gap_adj`);
  - `ao_gap_raw` = ln(`open` / `prev_close`);
  - `close` = `open` · exp(`y_oc`).
  - Prices are continuous, not rounded to a tick, so that no value can collide with a real target in the guard.
- **The range:** range_it = |`y_oc`_it| + 0.008 · X_it, with X_it a standard exponential.
- **Lags** (each the previous row's value of the same ticker): `gap_adj_lag1` = `ao_gap_adj`, `oc_lag1` = `y_oc`, `range_lag1` = range, `topix_oc_lag1` = `y_topix_oc`.
  - The first dev date uses a pre-sample draw: `gap_adj_lag1` ~ N(0, 0.012²), `oc_lag1` ~ N(0, 0.016²), `range_lag1` = |`oc_lag1`| + 0.008 · X, and `topix_oc_lag1` ~ N(0, 0.008²) (date-level).

## 7. The scenario

### 7.1 Fields
A frozen dataclass. Each pair is (dev part, confirmation part).

| Field | Default | Meaning |
|---|---|---|
| `b` | 0.0 | the H1 slope before the break |
| `delta_post` | 0.0 | Δ: the change of b from `BREAK_DATE` on |
| `b_spread` | (0.0, 0.0, 0.0) | per-ticker deviations of b; their sum must be 0 (within 1e-12) |
| `a2` | 0.0 | the `eurusd_ret` slope (H3) |
| `a2_gap` | 0.0 | the gap's `eurusd_ret` slope |
| `delta_cc` | 0.8 | δ_cc, the close-to-close FX slope |
| `b_mkt` | 0.0 | the hedge's FX slope (§6.2) |
| `gap_mkt` | 0.0 | the hedge gap's FX slope (§6.2) |
| `beta_hedge` | (1.2, 1.0, 1.1) | β_i |
| `c_usd_sess` | 0.0 | the slope on `c_usdjpy_sess_ret` |
| `c_eur_sess` | 0.0 | the slope on `c_eurusd_sess_ret` |
| `b_gotobi` | 0.0 | the slope on `usdjpy_ret` × gotobi |
| `tails` | "gaussian" | "gaussian" or "t5" |
| `rho_fx` | −0.44 | corr(z1, z2) |
| `resid_corr` | 0.43 | the residuals' cross-ticker correlation |
| `phi` | 0.1 | the residuals' AR(1) coefficient |
| `ewj_missing` | (3, 3) | dates with `ewj_oc` and `ewj_oc_jpy` missing |
| `fcx_missing` | (4, 4) | dates with `fcx_oc` missing |
| `sess_missing` | (5, 5) | dates with both session FX columns missing |
| `xau_missing` | (0, 6) | dates with all six `xau_` columns missing |
| `n225_missing` | (3, 3) | dates with `n225_ret`, `n225_bars`, `n225_stale_start_min` and `n225_stale_end_min` all missing: nights with no Japan 225 window record, which the build leaves empty in exactly these four columns (AM-05 makes such a night ineligible for the Nikkei-proxy row) |
| `n225_stale_share` | (0.45, 0.05) | the share of stale Nikkei nights |
| `usdjpy_bars_zero` | (0, 0) | dates on which `usdjpy_bars`, `usdjpy_rv` and `usdjpy_bv` are 0.0 |
| `xau_absent_conf` | False | all six `xau_` columns missing on every confirmation date |
| `gotobi_zero_conf` | False | `gotobi_day` = 0 on every confirmation date |
| `hedge_gap_absent_2022` | False | `ao_1306_gap_adj` and `ao_1306_gap_raw` missing on every 2022 date |

**Validation (`ValueError`):**
- `tails` not in ("gaussian", "t5");
- `rho_fx`, `resid_corr` or `phi` outside the ranges `sim.synthetic_panel` accepts;
- a negative count, or a count larger than its part's dates;
- a share outside [0, 1];
- `b_spread` not summing to 0.

`Scenario.to_dict()` returns the fields as plain JSON types, with tuples as lists. `Scenario.not_estimable()` returns `Scenario()` with `xau_absent_conf=True`, `gotobi_zero_conf=True`, `usdjpy_bars_zero=(0, 6)` and `hedge_gap_absent_2022=True`.

### 7.2 How the knobs act
- They act after generation, on the reported columns only. The DGP uses the generated values.
- Each count picks that many distinct dates of its part, uniformly, with the generator. The missing values apply to all three tickers on those dates.
- The dates for `usdjpy_bars_zero` are drawn from the dates of the part on which no ticker has `earn_flag` or `news_flag` set.

## 8. Outputs

### 8.1 The frames
`dev` holds the dev dates and `confirm` the confirmation dates. Each frame:
- has exactly the columns of Table D, in its order;
- is sorted by date, then ticker (the order of `TICKERS`), with three rows per date and a fresh RangeIndex;
- holds no other column (no `beta`, no constructed target, no mask);
- carries `attrs = {"provenance": blind.SYNTHETIC, "part": "dev" or "confirmation", "truth": the truth dict}`.

**Kinds.**
- A column whose kind in Table D is `i` is int64. If it holds a missing value in a frame, it is float64 in that frame, as `pandas.read_csv` would give.
- Columns of kind `f` are float64.
- `n225_bars` is of kind `f`, as `io.load_dev` returns it: the build writes it as a nullable integer and leaves it empty on a night with no Japan 225 window record. It is float64 in both frames, with whole-number values where present.
- `date` is a datetime column.
- `ticker`, `window_start_utc` and `window_end_utc` hold Python strings. They are built with pandas' default inference, so that their dtype matches what `read_csv` gives in the running pandas.

**No other missing value** appears in either frame beyond those §7 places.

### 8.2 `components`
One row per row of `pd.concat([dev, confirm], ignore_index=True)`, in that order. Columns:
- `date`, `ticker`;
- `part` ("dev" or "confirmation");
- `b_it`;
- `resid` (σ_i · ε_it);
- `gap_resid` (0.008 · u_g,it).

It exists for the tests. The confirmation module never reads it.

### 8.3 `truth`
A dict with exactly these keys:
- `source` = "sim_full";
- `seed`;
- `scenario` = `Scenario.to_dict()`;
- `constants` = {`fe`, `spy_slope`, `copx_slope`, `sigma`, `pred_sd`, `price_start`, `dividend`, `pull` = 0.01};
- `break_date` = "2024-11-05";
- `b_pre` = b;
- `b_post` = b + delta_post;
- `b_ticker` = {ticker: b + b_spread_i};
- `b_conf_mix` = (n_pre · b + n_post · (b + delta_post)) / (n_pre + n_post), with n_pre and n_post the confirmation dates before and from `BREAK_DATE` (695 and 324);
- `f_2022` = b / delta_cc;
- `f_2023_2026` = ((n_a · b + n_b · (b + delta_post)) / (n_a + n_b)) / delta_cc, with n_a and n_b the confirmation dates from 2023-01-01 to 2024-11-04 and from `BREAK_DATE` on (451 and 324);
- `exact_target` = (b_mkt == 0 and gap_mkt == 0);
- `n_dev_dates`, `n_conf_dates`;
- `t_conf` (from `calendar.t_conf` on the output);
- `excluded_all_three` (its dates as ISO strings).

`f_2022` and `f_2023_2026` are None when delta_cc = 0. `b_conf_mix` and `f_2023_2026` are date-share approximations: OLS weights rows by squared FX moves, not by dates.

## 9. Tests (`tests/test_p4_sim_full.py`: exactly these 20)

### 9.1 Seeds and scenarios
- Seeds are S_k = `Spec.load().seed` + 8,000,000 + k, with k as listed.
- **Sc1** = `Scenario(b=1.0, delta_post=-1.0, b_spread=(-0.3, 0.1, 0.2), a2=0.6, a2_gap=0.2, delta_cc=1.5, c_usd_sess=0.5, c_eur_sess=-0.3, b_gotobi=0.4, sess_missing=(0, 0))`.
- **Sc2** = `Scenario(b=1.0, delta_post=-1.0, a2=0.6, delta_cc=1.5)`.
- Simulations may be cached at module level. The file must run in under 120 s.

### 9.2 Where the recovery tests start
- joined = `pd.concat([dev, confirm], ignore_index=True)`, with `joined.attrs = {"provenance": blind.SYNTHETIC}`.
- T = `targets.add_targets(joined)`; D = `inference.build_design(T)`.
- Each subset is `inference.fit_dk(inference.subset_design(D, keep))`, with keep on `D.dates`.
- An estimate passes if |estimate − truth| ≤ 5 · se, both read from `Result.param`.

### 9.3 The 20 tests
The file holds exactly these 20 test methods, with these names; helpers and classes are the builder's choice. Tests use S0 and `Scenario()` unless they say otherwise.

1. `test_columns_order_and_keys`. Both frames:
   - columns equal `COLUMNS`, and their set equals `schema.all_grouped_columns()`;
   - the sort, the three tickers per date and the RangeIndex hold, and keys are unique;
   - dev dates are before 2022-01-01, and confirmation dates are from 2022-01-04 to 2026-03-05;
   - `attrs` are as in §8.1, and `attrs["truth"]` equals `out.truth`.
2. `test_dev_panel_kinds_and_guard` (P4Q33).
   - `io.load_dev()` and `io.load_events_firm()`: names and order equal those of the frames and of `out.events`.
   - Each column's `dtype.kind` equals the real one, except that an integer real column holding a missing value in a frame must be float there.
   - Then `blind.require_unblinded` passes on both frames.
   - Apart from the guard's own check, the test prints and compares no value.
3. `test_dtype_rule`.
   - The default dev frame has `INT_COLUMNS` as int64.
   - The confirmation frame of S4 with `Scenario.not_estimable()` has `xau_bars` as float64 and the other `INT_COLUMNS` as int64.
   - `n225_bars` is float64 in both default frames, with whole-number values where present.
   - The string and datetime columns are as in §8.1.
4. `test_dates`.
   - The confirmation dates equal `calendar.confirmation_calendar()`.
   - The dev dates equal `dev_calendar()`: 1,714 dates, from 2015-01-06 to 2021-12-30.
   - With S5 and `dev_dates = dev_calendar()[-600:]`, the dev frame has exactly those dates, and its first `window_start_utc` is the weekday before them at 06:00:00.
   - `dev_dates` with a 2022 date, or with 299 dates, raises `ValueError`.
5. `test_window_columns`.
   - `window_hours`, the two window texts and the four bar columns follow §3.3 on every row: `xau_bars` and `n225_bars` where they are present, and `usdjpy_bars` on dates not zeroed.
   - The spot table of §3.3 holds.
6. `test_us_sessions_and_us_returns`.
   - `us_n_sessions` follows §3.3, and the spot values hold.
   - On nights with no session, the six columns of §6.1 are exactly 0.0, or missing where a knob put NaN.
   - `ewj_oc_jpy` equals `ewj_oc` + `usdjpy_us_ret` exactly, and is missing exactly where `ewj_oc` is missing.
7. `test_calendar_flags`.
   - `sq_day`, `sq_major`, `gotobi_day`, `boj_day`, `exdiv_day` and `div_exdate` follow §5.
   - `ao_1306_gap_raw` − `ao_1306_gap_adj` is −0.02 on the 1306 ex-dates and 0 elsewhere (tolerance 1e-12).
   - `ao_topix_gap_tradj` − `ao_topix_gap` is 0.008 on the mass ex-dates and 0 elsewhere (tolerance 1e-12).
8. `test_events_table`: columns, kinds, the four categories, the counts of §4.2, the sort, every date in C, and the tickers.
9. `test_flags_follow_events`: the four flags follow §4.3 on both frames, on the joined calendar.
10. `test_t_conf_and_masks`.
    - §4.4 holds, and `truth` reports it.
    - `targets.add_masks(joined, events)` gives `excl_inference` ⇒ `excl_d2` and `excl_forecast_eval` ⇒ `excl_inference` on every row.
11. `test_price_and_lag_identities`. Per ticker, on the joined rows:
    - the price identities of §6.3, within 1e-12;
    - `prev_close` equals the previous `close` exactly, across the dev and confirmation boundary too;
    - the first `prev_close` is P0;
    - the four lags equal the previous values exactly (from the second row on);
    - `range_lag1` ≥ |`oc_lag1`| on every row;
    - prices are positive and within [0.2 · P0, 5 · P0].
12. `test_truth_dict`.
    - The key set and the formulas of §8.3, including n_pre, n_post, n_a and n_b recomputed from the dates.
    - `exact_target` is True by default and False with S6 and `Scenario(b_mkt=0.2)`.
13. `test_components_identities` (S1, Sc1):
    - `b_it` follows §6.3 exactly;
    - `resid` = `y_oc` − β_i · `y_1306_oc` − (v_it without its residual) on every row;
    - `gap_resid` = `ao_gap_adj` − β_i · `ao_1306_gap_adj` − (g_it without its noise) on every row;
    - both within 1e-12, using the frames' columns.
14. `test_residual_properties` (S1, Sc1):
    - per ticker, the sd of `resid` is within 10% of σ_i, and its lag-1 autocorrelation is within 0.08 of φ;
    - the three cross-ticker correlations are within 0.08 of 0.43;
    - |corr(`resid`, x)| < 0.08 for x in `usdjpy_ret`, `eurusd_ret`, `spy_oc`, `copx_oc`, `c_usdjpy_sess_ret` and `usdjpy_ret` × `gotobi_day`;
    - the sd of `gap_resid` is within 10% of 0.008, and |corr(`gap_resid`, `usdjpy_ret`)| < 0.08.
15. `test_b_a2_and_break_recovered` (§9.2):
    - With S2 and Sc2: b on the dev dates; b and a₂ on the confirmation dates before `BREAK_DATE`; b + delta_post on the dates from it.
    - With S3 and `Scenario()`: b = 0 on all confirmation dates.
16. `test_cc_and_raw_slopes` (S2, Sc2):
    - the `usdjpy_ret` slope of `build_design(T, target="cc_abn")` on the 2022 dates recovers δ_cc;
    - that of `build_design(T, target="raw_oc")` on the confirmation dates before `BREAK_DATE` recovers b.
17. `test_default_missingness`.
    - Each knob's count of missing dates is exact per part, date-level, on exactly its columns.
    - The stale Nikkei shares, among each part's nights where the four Nikkei columns are present, are within 0.05 of the setting.
    - No other value is missing, and `usdjpy_bars` > 0 everywhere.
    - With S7 and all counts at 0, nothing is missing.
18. `test_not_estimable_preset` (S4, `Scenario.not_estimable()`):
    - the four patterns of §7.1 hold exactly, the six zeroed dates having no `earn_flag` or `news_flag` on any ticker;
    - on T restricted to the confirmation dates (attrs kept), `build_design` with `secondary="fx_x_highrv"` raises `inference.DesignError`, while the primary `build_design` succeeds;
    - `cc_abn` is missing on every 2022 row of T.
19. `test_seed_determinism`: two calls with S0 give equal frames, events, components and truth (`pandas.testing`, exact); S8 gives a different `y_oc`.
20. `test_module_source`, by `ast` on the module's source:
    - imports only as §1.1 allows;
    - no call of `open`, `read_csv`, `read_table`, `read_parquet`, `read_json`, `read_excel`, `read_pickle`, `to_csv`, `to_parquet`, `to_json`, `to_excel`, `to_pickle`, `read_text`, `read_bytes`, `write_text` or `write_bytes`;
    - none of the strings `load_dev`, `load_confirm`, `load_events` and `OFILT_DATA_DIR`;
    - it defines `simulate`, `dev_calendar`, `Scenario`, `SimOutput`, `COLUMNS`, `INT_COLUMNS` and `BREAK_DATE`.

### 9.4 Seed blocks already in use (relative to the spec seed unless absolute)
- B7: + 100,000 to + 230,500;
- B7b: + 1,000,000 on;
- C7: + 3,000,000 on;
- the P3-2a warp check: + 4,000,000 on;
- the sealed run: + 5,000,000 to about + 6,200,000;
- the existing tests' small absolute seeds; 50,000 to 50,999 (B6); + 5,000 (a Pesaran–Timmermann size test).

The block + 8,000,000 + k, k < 1,000, is disjoint from all of them. P4-5's dry-run block is set in P4-5 (P4Q29).

## 10. Changes from version 1

Version 1 (SHA-256 `6b500f4b30aece4be6d375ada094fc5cfde0f43260f32aba7a086f3db38a8e81`) was never committed. P4-3's step c.1, in its third run, found that the dev panel `io.load_dev` returns has `n225_bars` of kind `f`, where version 1's Table D gave `i`; P4-3 stopped there, before any code was written. The build writes that column as a nullable integer and leaves it empty on a night with no Japan 225 window record, so the kind means the dev panel has such nights. This version changes:
- Table D, row 58: kind `f`. §2's `INT_COLUMNS` therefore has 7 names; §8.1 says how `n225_bars` is held; tests 3 and 5 check it.
- §7.1: the knob `n225_missing`, default (3, 3), so that both frames hold nights with no Japan 225 window record, as the build writes them, and the rule of AM-05 that makes such a night ineligible for the Nikkei-proxy row can be exercised on synthetic data. Test 17 measures the stale Nikkei shares on the other nights.
- Two readings the builder recorded in the third run, now written in: test 7 states the tolerance 1e-12 for both differences, and §5 states `boj_day`'s count for 2026 (one date, in January). §5 also says that a month with no 30th has no nominal 30th for `gotobi_day`.
- §1.3 adds the two lines of `build/pass2/build_panel_p2.py` that write the bar columns.

Nothing else changes. Every count, date and spot value of §3 to §5 and §8.3 was reproduced independently, by a standalone script that ran no repository code, before this version was issued.

## Table D: the panel's columns (order and kind)

Kinds: `M` datetime, `O` string or object, `f` float, `i` integer. The order is the dev panel's, and each kind is the one `io.load_dev` returns (P4-3's step c.1 checks both).

| # | Column | Kind |
|---|---|---|
| 1 | `date` | M |
| 2 | `ticker` | O |
| 3 | `usdjpy_ret` | f |
| 4 | `usdjpy_rv` | f |
| 5 | `usdjpy_bv` | f |
| 6 | `eurusd_ret` | f |
| 7 | `eurusd_rv` | f |
| 8 | `spy_oc` | f |
| 9 | `ewj_oc` | f |
| 10 | `fcx_oc` | f |
| 11 | `copx_oc` | f |
| 12 | `us_n_sessions` | f |
| 13 | `window_hours` | f |
| 14 | `gap_adj_lag1` | f |
| 15 | `oc_lag1` | f |
| 16 | `range_lag1` | f |
| 17 | `topix_oc_lag1` | f |
| 18 | `earn_flag` | i |
| 19 | `news_flag` | i |
| 20 | `mech_flag` | i |
| 21 | `audit_flag` | i |
| 22 | `boj_day` | f |
| 23 | `sq_day` | f |
| 24 | `sq_major` | f |
| 25 | `exdiv_day` | i |
| 26 | `div_exdate` | f |
| 27 | `ao_gap_adj` | f |
| 28 | `ao_gap_raw` | f |
| 29 | `ao_topix_gap` | f |
| 30 | `y_oc` | f |
| 31 | `y_topix_oc` | f |
| 32 | `open` | f |
| 33 | `close` | f |
| 34 | `prev_close` | f |
| 35 | `window_start_utc` | O |
| 36 | `window_end_utc` | O |
| 37 | `usdjpy_bars` | f |
| 38 | `usdjpy_stale_start_min` | f |
| 39 | `usdjpy_stale_end_min` | f |
| 40 | `eurusd_bars` | f |
| 41 | `eurusd_stale_end_min` | f |
| 42 | `y_1306_oc` | f |
| 43 | `ao_1306_gap_raw` | f |
| 44 | `ao_1306_gap_adj` | f |
| 45 | `ao_topix_gap_tradj` | f |
| 46 | `xau_ret` | f |
| 47 | `xau_rv` | f |
| 48 | `xau_bv` | f |
| 49 | `n225_ret` | f |
| 50 | `usdjpy_us_ret` | f |
| 51 | `ewj_oc_jpy` | f |
| 52 | `gotobi_day` | i |
| 53 | `c_usdjpy_sess_ret` | f |
| 54 | `c_eurusd_sess_ret` | f |
| 55 | `xau_bars` | i |
| 56 | `xau_stale_start_min` | f |
| 57 | `xau_stale_end_min` | f |
| 58 | `n225_bars` | f |
| 59 | `n225_stale_start_min` | f |
| 60 | `n225_stale_end_min` | f |

## Table E: the events table's columns (order and kind)

| # | Column | Kind |
|---|---|---|
| 1 | `ticker` | O |
| 2 | `date` | M |
| 3 | `category` | O |
| 4 | `note` | O |
| 5 | `check_status` | O |
| 6 | `check_note` | O |
