# Analysis panel — data dictionary

Built by `build/pass2/build_panel_p2.py` (Pass 2; append-only, P51). The frozen `build/pass1/build_panel.py` produces the 41 Pass 1 columns from `Book2.xlsx`, the two Dukascopy FX files and `events_firm.csv` / `events_boj.csv`. The 19 Pass 2 columns are appended from `newbloombergdata_fixed.xlsx` (1306, its distributions, TOPIX total return) and the XAU and Japan 225 Dukascopy files. Input, code and output SHA-256 hashes are in `MANIFEST.json`.

One row per (ticker, Tokyo trading day). Tickers 5713, 5711, 5706. Returns are log returns.

| File | Span | Rows | Use |
|---|---|---|---|
| `panel_dev.csv` | 2015-01-06 → 2021-12-30 | 5,124 | Development: synthetic-only model building until `spec-dev-v1`, then the first look (PLAN §8) |
| `panel_confirm_SEALED.csv` | 2022-01-04 → 2026-03-05 | 3,057 | **Do not open** until `prereg-v1` is tagged. 1,019 trading days; T_conf = 1013 dates with a non-excluded row. Its Pass 1 hash `9c18a6c1…` is superseded by AM-04 |

Both panels have 60 columns: the 41 Pass 1 columns, then the 19 Pass 2 columns. The 41 old columns are the original strings, never recomputed: dev's are the original Pass 1 panel's (`736636…`), sealed's the frozen build's output on the Mac (`138e5e21…`; Flag 16, Isaiah 2026-10-05).

## Schema groups — which columns may be features

Every column is in exactly one group, defined as explicit frozensets in `ofilt/drift/schema.py` (DECISIONS P20). Unknown columns are refused everywhere, and nothing selects columns by prefix. **Only PRE_OPEN_FEATURES may be model features.** Being unprefixed does not make a column a feature: `open`, `close`, `prev_close` and `audit_flag` are unprefixed and forbidden. PRE_OPEN_ROBUSTNESS columns are known before the open but enter only the pre-listed robustness designs (P50).

| Group | n | Columns | Role |
|---|---|---|---|
| KEYS | 2 | `date`, `ticker` | Identifiers |
| PRE_OPEN_FEATURES | 20 | listed below | Known by 08:59 JST on day t; the only allowed features (unchanged in Pass 2, P50) |
| EXCLUSION_FLAGS | 2 | `earn_flag`, `news_flag` | Sample filters (D, D+1), never features |
| INFORMATIONAL | 1 | `mech_flag` | Recorded, not used |
| ROBUSTNESS_ONLY | 1 | `audit_flag` | Outcome-identified; a robustness exclusion only (P08) |
| AT_OPEN | 6 | `ao_gap_adj`, `ao_gap_raw`, `ao_topix_gap`, `ao_1306_gap_raw`, `ao_1306_gap_adj`, `ao_topix_gap_tradj` | Known only at the 09:00 auction; decomposition, f and the hedge gap only |
| TARGET_INPUTS | 3 | `y_oc`, `y_topix_oc`, `y_1306_oc` | Outcomes; never features |
| PROVENANCE | 16 | `open`, `close`, `prev_close`, `window_start_utc`, `window_end_utc`, `usdjpy_bars`, `usdjpy_stale_start_min`, `usdjpy_stale_end_min`, `eurusd_bars`, `eurusd_stale_end_min`, `xau_bars`, `xau_stale_start_min`, `xau_stale_end_min`, `n225_bars`, `n225_stale_start_min`, `n225_stale_end_min` | QA, prices, bar counts and staleness; never features (P42 reads the n225 staleness as a sample filter) |
| CONTEMPORANEOUS | 2 | `c_usdjpy_sess_ret`, `c_eurusd_sess_ret` | Session FX, 09:00 JST → the close of day t; never features |
| PRE_OPEN_ROBUSTNESS | 7 | `xau_ret`, `xau_rv`, `xau_bv`, `n225_ret`, `usdjpy_us_ret`, `ewj_oc_jpy`, `gotobi_day` | Known by 08:59 JST; robustness designs only (P50), refused by `select_features` |

### PRE_OPEN_FEATURES (known by 08:59 JST on day t)

| Column | Definition |
|---|---|
| `usdjpy_ret` | log USD/JPY from the previous TSE close (15:00 JST to 2024-11-04, 15:30 JST from 2024-11-05) to 08:59:00 JST. Positive = yen weakens. **H1 regressor.** |
| `usdjpy_rv`, `usdjpy_bv` | Realized variance and bipower variation of 1-minute returns over the same window. Dukascopy's flat rollover bars bias BV down. |
| `eurusd_ret`, `eurusd_rv` | Same window for EUR/USD. Positive = dollar weakens. `eurusd_ret` is in the primary design, which makes b approximately the yen-specific pass-through (P85); its coefficient is H3 (P14, P15; read with P84). |
| `spy_oc`, `ewj_oc`, `fcx_oc`, `copx_oc` | Sum of US open→close log returns over the NY sessions inside the window (NY dates from t_prev to t−1). 0 if there was no US session; NaN on 3 nights where EWJ was stale. Primary controls: `spy_oc`, `copx_oc`. `ewj_oc` and `fcx_oc` are robustness only (P19). |
| `us_n_sessions` | Number of US sessions in the window (0 on US holidays; up to 7 in Golden Week). Written as a float (e.g. `1.0`). |
| `window_hours` | Window length (18 h on normal nights; 258 h max). |
| `gap_adj_lag1`, `oc_lag1`, `range_lag1`, `topix_oc_lag1` | The previous session's gap, open→close, log(high/low), and TOPIX open→close. Not in the primary design (P19). |
| `boj_day` | BoJ policy announcement day (announced intraday). Exclusion is a robustness row. |
| `sq_day`, `sq_major` | SQ day (2nd Friday, moved to the prior trading day if a holiday); major = Mar/Jun/Sep/Dec. Major-SQ exclusion is a robustness row. |
| `exdiv_day`, `div_exdate` | Ex-dividend day and the yen amount (cash items with the same ex-date summed). |

**Model-side features** (built by `schema.select_features`; deterministic, row-wise, no estimated parameters):
- `long_window` = 1[window_hours > 18]
- `jumpshare` = clip((rv − bv)/rv, 0, 1)
- `rv_per_bar` = usdjpy_rv / usdjpy_bars. `usdjpy_bars` is the only PROVENANCE column a derived feature may read.
- `e_pos` = max(usdjpy_ret, 0) and `e_neg` = min(usdjpy_ret, 0)
- `no_us_session` = 1[us_n_sessions = 0]
- `noise_N01`: a seeded N(0,1) column generated by a model itself (M7) for importance calibration. It is not a panel column.

Thresholds such as `highrv` (rv_per_bar above its development median, 1.2950114214e-08) are applied in the design, not stored.

### PRE_OPEN_ROBUSTNESS (known by 08:59 JST; robustness designs only, P50)

| Column | Definition |
|---|---|
| `xau_ret`, `xau_rv`, `xau_bv` | XAU/USD (Dukascopy, bid) log return, realized variance and bipower variation over the `usdjpy_ret` window, by the same frozen rule (P41). No staleness filter (AM-05). |
| `n225_ret` | Japan 225 CFD (Dukascopy, bid) log return over the same window (P42). Used only in the nikkei_proxy_p42 row, on nights where both window endpoints are at most 5 minutes stale (P42; AM-05): 929 of the 1,708 dev dates (40 in 2015-H1, the rest from 2018-04-13) and 999 of the 1,019 confirmation dates. |
| `usdjpy_us_ret` | Sum over the night's NY sessions (the dates counted by `us_n_sessions`) of ln(USD/JPY at the NY close / at the NY open). Open 09:30 ET; close 16:00 ET, or 13:00 ET on the 23 NYSE early closes; DST from the tz database (P49). Exactly 0.0 when `us_n_sessions` = 0, and possibly also on a night with sessions (amended assertion, 2026-10-05). |
| `ewj_oc_jpy` | `ewj_oc` + `usdjpy_us_ret`: EWJ in yen (P49). NaN exactly where `ewj_oc` is NaN. |
| `gotobi_day` | 1 if a nominal date (the 5th, 10th, 15th, 20th, 25th, 30th, and the month's last calendar day) lands on day t, rolling a non-trading nominal date back to the preceding trading day (P48). Dev 529 of 1,708 dates; confirmation 319 of 1,019. |

On a night with no XAU (or Japan 225) bar in the window, every `xau_*` (or `n225_*`) column of that night is empty, including the bar count and staleness. The P42 rule therefore treats such a night as ineligible.

### Flags (never features)

| Column | Definition |
|---|---|
| `earn_flag` | 1 on trading days D and D+1 of each 決算短信 release (D = first trading day ≥ release date). |
| `news_flag` | Same D/D+1 rule for standalone forecast revisions, special losses and delay notices. Forecast evaluation keeps day D (P27). |
| `mech_flag` | Day of mechanical disclosures (corrections, consolidation restatement). Not an exclusion. |
| `audit_flag` | D/D+1 of outcome-identified audit candidates. **Robustness only**: using it in the primary spec selects on the outcome. |

### At-open (`ao_`, known only once the 09:00 auction prints)

These columns are **not features in any specification**. The auction-conditional specification is retired (P16). They build the gap and close-to-close targets for the decomposition and the fraction unpriced f (P24), and the hedge gap.

| Column | Definition |
|---|---|
| `ao_gap_adj` | log(open_t / (close_{t−1} − dividend_t)), the ex-dividend-adjusted gap. |
| `ao_gap_raw` | Unadjusted gap. |
| `ao_topix_gap` | TOPIX gap. Not dividend-adjusted (Flag 6); `ao_topix_gap_tradj` is the adjusted version. |
| `ao_1306_gap_raw` | 1306 gap, log(open_t / close_{t−1}). |
| `ao_1306_gap_adj` | log(open_t / (close_{t−1} − D_t)), with D_t the 1306 distribution with ex-date t, else 0. D_t is the stored corrected amount (P39, P47; never recomputed). The hedge gap under AM-03. |
| `ao_topix_gap_tradj` | `ao_topix_gap` + [ln(TR_t/TR_{t−1}) − ln(PR_t/PR_{t−1})]. TR is the TOPIX total return (TPXDDVD Index), PR Book2's TOPIX close, both without 2020-10-01. Fallback path only (P40). |

### Targets (`y_`; never features)

| Column | Definition |
|---|---|
| `y_oc` | Stock open→close on day t. |
| `y_topix_oc` | TOPIX open→close on day t; the Pass 1 placeholder hedge, and the fallback secondary's hedge (P18). |
| `y_1306_oc` | 1306 (NEXT FUNDS TOPIX ETF) open→close on day t; the hedge under AM-03 (P18). |

The primary target is built in model code (`ofilt/drift/targets.py`), not stored: `abn_oc` = y_oc − β_{i,t−1}·hedge_oc. β_{i,t−1} is the past-only **expanding** OLS slope on non-excluded rows (at least 250 observations, lagged one day, continued across the dev/confirmation boundary; P17). The secondary target is `raw_oc` = y_oc. `gap_abn` and `cc_abn` serve the decomposition and f.

### Contemporaneous (never features)

| Column | Definition |
|---|---|
| `c_usdjpy_sess_ret`, `c_eurusd_sess_ret` | ln(P(t, close) / P(t, 09:00:00 JST)): the session move from the 09:00 JST price (close of the bar labeled 08:59) to the TSE close of day t itself (15:00 JST through 2024-11-04, 15:30 JST from 2024-11-05). For the mechanism specification only (PLAN §6). |

### Provenance added in Pass 2 (never features)

| Column | Definition |
|---|---|
| `xau_bars`, `n225_bars` | 1-minute bars between the window's endpoint bars, as `usdjpy_bars`. Written as integers; the Pass 1 `usdjpy_bars` and `eurusd_bars` are written as floats (e.g. `1079.0`). |
| `xau_stale_start_min`, `xau_stale_end_min`, `n225_stale_start_min`, `n225_stale_end_min` | Minutes between each endpoint's target bar label and the last bar at or before it, as `usdjpy_stale_*`. The P42 rule reads the n225 values as a sample filter. |

## Conventions baked in (verified, not assumed)

- Dukascopy bars are true UTC and start-labeled. The price at instant X is the close of the last bar labeled ≤ X − 1 min.
- Miner prices are adjusted for capital changes but not for cash dividends. This includes 5706's 10:1 split, ex-date 2026-09-29. Never mix these prices with the Math 86 `JPEquities.xlsx`.
- The stale TOPIX row for 2020-10-01 (the TSE outage) is dropped, in TOPIX and in the TOPIX total return.
- The XAU and Japan 225 windows are exactly the `usdjpy_ret` window (asserted at build time).
- The US session is 09:30–16:00 America/New_York, or to 13:00 on NYSE early closes (P49).
- The 41 Pass 1 columns are read back as strings and never recomputed; the 19 new columns are appended by date (P51).

## Verification status (October 2026)

- `events_firm.csv` has a `check_status` column. The 15 audit candidates and 5711's 2022-08-09 release were checked by hand: no corrections, no reclassification. The remaining rows come from the Deep Research report, validated statistically against price reactions.
- FCX 2016-01-11 (−22.5% open→close): checked, genuine; no data change.
- The event layer is unchanged by the Pass 2 rebuild.
- The Pass 2 inputs are validated in `reports/P2_1_inputs.md`.

## Not panel columns

- The index-staleness test of the TOPIX 09:00 print is a dev report (P55), not a column.
- The post-2024-11-05 indicator is built in model code (confirmation only; P33).
- MoF intervention dates: optional, not included.
