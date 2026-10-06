# P2-5 dev checks (reports only)

Panel: `build_out/p2_20261006T002928Z/panel_dev.csv`, SHA-256 `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68`, equal to its `MANIFEST.json` entry: True. SHA-256 of `MANIFEST.json`: `1345c0772777b87e9d5fcc01794340231c04068f383330762e68ff3ef468e8bd`. Sections 2.2 and 2.3 are written by `tools/p2_5_staleness.py`, section 2.4 by `tools/p2_5_coverage.py`. A7 on 1306 (2.1) is in `reports/A_hedge_efficiency_1306.md`.

**Environment (ofilt_p2):**
- python 3.12.4 (arm64; macOS-26.6.2-arm64-arm-64bit)
- pandas 3.0.2
- numpy 2.4.4
- scipy 1.17.1
- scikit-learn 1.8.0
- openpyxl 3.1.5
- PyYAML 6.0.3
- joblib 1.5.3
- threadpoolctl 3.6.0
- python-dateutil 2.9.0.post0
- numpy blas: accelerate (version unknown)
- numpy lapack: accelerate (version unknown)

## 2.2 Index-staleness test (P55; D10). Gap-only

Columns: `date`, `ticker`, `ao_topix_gap`, `ao_topix_gap_tradj`, `ao_1306_gap_raw`, `ao_1306_gap_adj`, `exdiv_day`. One row per date.
- Gap columns identical across the tickers of every date: `ao_topix_gap` True; `ao_topix_gap_tradj` True; `ao_1306_gap_raw` True; `ao_1306_gap_adj` True
- Dev dates: 1708; miner ex-day dates (exdiv_day == 1 for any ticker): 14
- 1306 ex-dates (ao_1306_gap_adj != ao_1306_gap_raw): 2015-07-08, 2016-07-06, 2017-07-06, 2018-07-06, 2019-07-08, 2020-07-09, 2021-07-08; exactly the 7 dev ex-dates: True
- NaN dates per gap column: `ao_topix_gap` 0; `ao_topix_gap_tradj` 0; `ao_1306_gap_raw` 0; `ao_1306_gap_adj` 0

Estimator: OLS with an intercept; g_E = `ao_1306_gap_adj`. b_IE = slope of g_I on g_E; b_EI = slope of g_E on g_I; R² centred; N = dates. Reverse-slope 95% CI = b_EI ± 1.96·SE, SE Newey–West (Bartlett) at lag floor(4·(N/100)^(2/9)), no small-sample correction. P55 reading: staleness established iff the CI lies entirely above 1.

| Sample | N (NaN dates dropped) | b_IE | b_EI | R² | b_IE·b_EI − R² | bracket [b_IE, b_IE/R²] | NW lag | SE(b_EI) | 95% CI of b_EI | P55 reading |
|---|---|---|---|---|---|---|---|---|---|---|
| (i) no miner ex-day and no 1306 ex-date; g_I = ao_topix_gap | 1687 (0) | 0.7571 | 1.2068 | 0.9137 | 1.1e-16 | [0.7571, 0.8286] | 7 | 0.0250 | [1.1578, 1.2559] | staleness established |
| (ii) all dev dates; g_I = ao_topix_gap_tradj | 1708 (0) | 0.7579 | 1.2061 | 0.9141 | 0.0e+00 | [0.7579, 0.8291] | 7 | 0.0248 | [1.1575, 1.2548] | staleness established |

## 2.3 1306 evidence for P18 (D8). Gap-only

**P2-1's dividend and split results (quoted from `reports/P2_1_inputs.md`; not recomputed):**
> - OHLC violations (low > min(open, close), high < max(open, close), or low ≤ 0): dev 0; 2022+ 0
> - Split artifacts (|ln(open/prev close)| > 0.5): dev 0; 2022+ 0. (|ln(close/prev close)| > 0.5): dev 0; 2022+ 0
> - Rows with open = close = previous close: 6 (dev 5, 2022+ 1)
> - Types: fixed ['Regular Cash']; RAW ['Distribution']. Frozen build CASH_TYPES contains 'Regular Cash': True; contains 'Distribution': False
> - Fixed amount = RAW amount ÷ 10: float equality False; decimal equality of the stored values True
> - Declared, ex, record, pay and frequency columns identical between fixed and RAW: True
> - Every ex-date is in the miners' calendar: dev True; 2022+ True
> - Every ex-date is in July: dev True; 2022+ True. Record date 10 July of the same year: dev True; 2022+ True

Share of dev dates with a gap of exactly 0 (one row per date):

| Period | Dates | ao_1306_gap_raw == 0 | ao_topix_gap == 0 |
|---|---|---|---|
| all dev | 1708 | 84 (4.92%) | 0 (0.00%) |
| 2015 | 243 | 14 (5.76%) | 0 (0.00%) |
| 2016 | 245 | 10 (4.08%) | 0 (0.00%) |
| 2017 | 247 | 16 (6.48%) | 0 (0.00%) |
| 2018 | 245 | 14 (5.71%) | 0 (0.00%) |
| 2019 | 241 | 11 (4.56%) | 0 (0.00%) |
| 2020 | 242 | 12 (4.96%) | 0 (0.00%) |
| 2021 | 245 | 7 (2.86%) | 0 (0.00%) |

The 7 dev 1306 ex-dates (gaps in %, 2 decimals), against the supervisor's table:

| Ex-date | ao_1306_gap_adj | ao_topix_gap | abs. difference (pp) | Supervisor (1306 adj / TOPIX) | Equal at 2 decimals |
|---|---|---|---|---|---|
| 2015-07-08 | -0.30 | -0.41 | 0.11 | -0.30 / -0.41 | True |
| 2016-07-06 | -1.64 | -1.55 | 0.09 | -1.63 / -1.55 | False |
| 2017-07-06 | +0.00 | -0.04 | 0.04 | +0.00 / -0.04 | True |
| 2018-07-06 | +0.78 | +0.55 | 0.23 | +0.79 / +0.55 | False |
| 2019-07-08 | -0.17 | -0.26 | 0.10 | -0.16 / -0.26 | False |
| 2020-07-09 | -0.13 | -0.09 | 0.04 | -0.13 / -0.09 | True |
| 2021-07-08 | -0.22 | -0.15 | 0.07 | -0.21 / -0.15 | False |

- Every ex-date equals the supervisor's table at 2 decimals: False
- Largest absolute difference: 0.23 pp from the unrounded gaps; 0.23 pp from the 2-decimal values; supervisor 0.24 pp; equal: False

**STOP: the 7 ex-date gaps differ from the supervisor's table at 2 decimals.**

Blinding: gap columns and the miner ex-day flag only (dev). No target and no predictor column was loaded.

## 2.4 Japan 225 eligibility (P42 as proposed; D7) and new-column coverage. Predictors and provenance only

Written by `tools/p2_5_coverage.py`. Both panels verified against `MANIFEST.json` (SHA-256 `1345c0772777b87e9d5fcc01794340231c04068f383330762e68ff3ef468e8bd`) before loading. Columns: `date`, `ticker`, `us_n_sessions`, `xau_ret`, `xau_rv`, `xau_bv`, `n225_ret`, `usdjpy_us_ret`, `ewj_oc_jpy`, `gotobi_day`, `c_usdjpy_sess_ret`, `c_eurusd_sess_ret`, `xau_bars`, `xau_stale_start_min`, `xau_stale_end_min`, `n225_bars`, `n225_stale_start_min`, `n225_stale_end_min`. No `y_` or `ao_` column is loaded. Sealed side: counts and booleans only.

- Date-level columns identical across the tickers of every date: dev True; sealed True

**Japan 225 by half-year** (one row per date; fresh = at most 5 minutes stale; eligible = both endpoints fresh):

| Half-year | Dates | No Japan 225 bar | Start fresh | End fresh | Eligible (both) | End fresh = P2-4 table |
|---|---|---|---|---|---|---|
| 2015-H1 | 120 | 1 | 43 | 44 | 40 | True |
| 2015-H2 | 123 | 1 | 34 | 0 | 0 | True |
| 2016-H1 | 122 | 1 | 121 | 0 | 0 | True |
| 2016-H2 | 123 | 1 | 122 | 0 | 0 | True |
| 2017-H1 | 123 | 1 | 121 | 0 | 0 | True |
| 2017-H2 | 124 | 1 | 123 | 0 | 0 | True |
| 2018-H1 | 121 | 1 | 120 | 53 | 53 | True |
| 2018-H2 | 124 | 0 | 123 | 123 | 122 | True |
| 2019-H1 | 117 | 0 | 116 | 116 | 115 | True |
| 2019-H2 | 124 | 0 | 123 | 121 | 121 | True |
| 2020-H1 | 119 | 0 | 118 | 118 | 117 | True |
| 2020-H2 | 123 | 0 | 122 | 121 | 120 | True |
| 2021-H1 | 121 | 0 | 121 | 121 | 121 | True |
| 2021-H2 | 124 | 0 | 123 | 121 | 120 | True |
| 2022-H1 | 120 | 0 | 118 | 119 | 117 | True |
| 2022-H2 | 124 | 0 | 123 | 123 | 122 | True |
| 2023-H1 | 122 | 0 | 122 | 122 | 122 | True |
| 2023-H2 | 124 | 0 | 122 | 122 | 120 | True |
| 2024-H1 | 120 | 0 | 119 | 119 | 118 | True |
| 2024-H2 | 125 | 0 | 123 | 123 | 121 | True |
| 2025-H1 | 119 | 0 | 118 | 118 | 117 | True |
| 2025-H2 | 124 | 0 | 122 | 123 | 121 | True |
| 2026-H1 | 41 | 0 | 41 | 41 | 41 | True |

- Dev totals: 1708 dates; no Japan 225 bar 7; start fresh 1530; end fresh 938; eligible 929. First eligible dev date 2015-01-06; last 2021-12-30.
- Sealed totals: 1019 dates; eligible 999.

**Threshold sensitivity** (eligible = both endpoints at most k minutes stale):

| Half-year | Dates | k = 4 | k = 5 | k = 10 |
|---|---|---|---|---|
| 2015-H1 | 120 | 40 | 40 | 40 |
| 2015-H2 | 123 | 0 | 0 | 0 |
| 2016-H1 | 122 | 0 | 0 | 0 |
| 2016-H2 | 123 | 0 | 0 | 0 |
| 2017-H1 | 123 | 0 | 0 | 0 |
| 2017-H2 | 124 | 0 | 0 | 0 |
| 2018-H1 | 121 | 53 | 53 | 53 |
| 2018-H2 | 124 | 122 | 122 | 122 |
| 2019-H1 | 117 | 115 | 115 | 115 |
| 2019-H2 | 124 | 121 | 121 | 121 |
| 2020-H1 | 119 | 117 | 117 | 117 |
| 2020-H2 | 123 | 120 | 120 | 120 |
| 2021-H1 | 121 | 121 | 121 | 121 |
| 2021-H2 | 124 | 120 | 120 | 120 |
| 2022-H1 | 120 | 117 | 117 | 117 |
| 2022-H2 | 124 | 122 | 122 | 122 |
| 2023-H1 | 122 | 122 | 122 | 122 |
| 2023-H2 | 124 | 120 | 120 | 120 |
| 2024-H1 | 120 | 118 | 118 | 118 |
| 2024-H2 | 125 | 121 | 121 | 121 |
| 2025-H1 | 119 | 117 | 117 | 117 |
| 2025-H2 | 124 | 121 | 121 | 121 |
| 2026-H1 | 41 | 41 | 41 | 41 |

**Japan 225 endpoint staleness in minutes, bins {0, 1–5, 6–60, > 60, empty}** (dev by half-year; sealed in total):

| Period | Endpoint | 0 | 1-5 | 6-60 | >60 | empty |
|---|---|---|---|---|---|---|
| 2015-H1 | start | 43 | 0 | 0 | 76 | 1 |
| 2015-H1 | end | 43 | 1 | 0 | 75 | 1 |
| 2015-H2 | start | 34 | 0 | 0 | 88 | 1 |
| 2015-H2 | end | 0 | 0 | 0 | 122 | 1 |
| 2016-H1 | start | 121 | 0 | 0 | 0 | 1 |
| 2016-H1 | end | 0 | 0 | 0 | 121 | 1 |
| 2016-H2 | start | 122 | 0 | 0 | 0 | 1 |
| 2016-H2 | end | 0 | 0 | 0 | 122 | 1 |
| 2017-H1 | start | 121 | 0 | 1 | 0 | 1 |
| 2017-H1 | end | 0 | 0 | 0 | 122 | 1 |
| 2017-H2 | start | 121 | 2 | 0 | 0 | 1 |
| 2017-H2 | end | 0 | 0 | 0 | 123 | 1 |
| 2018-H1 | start | 120 | 0 | 0 | 0 | 1 |
| 2018-H1 | end | 48 | 5 | 0 | 67 | 1 |
| 2018-H2 | start | 123 | 0 | 0 | 1 | 0 |
| 2018-H2 | end | 121 | 2 | 0 | 1 | 0 |
| 2019-H1 | start | 116 | 0 | 0 | 1 | 0 |
| 2019-H1 | end | 112 | 4 | 0 | 1 | 0 |
| 2019-H2 | start | 122 | 1 | 0 | 1 | 0 |
| 2019-H2 | end | 106 | 15 | 1 | 2 | 0 |
| 2020-H1 | start | 118 | 0 | 0 | 1 | 0 |
| 2020-H1 | end | 118 | 0 | 0 | 1 | 0 |
| 2020-H2 | start | 122 | 0 | 0 | 1 | 0 |
| 2020-H2 | end | 117 | 4 | 0 | 2 | 0 |
| 2021-H1 | start | 121 | 0 | 0 | 0 | 0 |
| 2021-H1 | end | 121 | 0 | 0 | 0 | 0 |
| 2021-H2 | start | 123 | 0 | 0 | 1 | 0 |
| 2021-H2 | end | 121 | 0 | 0 | 3 | 0 |
| sealed, total | start | 1008 | 0 | 2 | 9 | 0 |
| sealed, total | end | 1007 | 3 | 1 | 8 | 0 |

**XAU endpoint staleness in minutes, bins {0, 1–5, 6–60, > 60, empty}** (dev by year; sealed in total):

| Period | Endpoint | 0 | 1-5 | 6-60 | >60 | empty |
|---|---|---|---|---|---|---|
| 2015 | start | 241 | 0 | 0 | 2 | 0 |
| 2015 | end | 240 | 0 | 0 | 3 | 0 |
| 2016 | start | 243 | 0 | 0 | 2 | 0 |
| 2016 | end | 243 | 0 | 0 | 2 | 0 |
| 2017 | start | 245 | 0 | 0 | 2 | 0 |
| 2017 | end | 245 | 0 | 0 | 2 | 0 |
| 2018 | start | 243 | 0 | 0 | 2 | 0 |
| 2018 | end | 243 | 0 | 0 | 2 | 0 |
| 2019 | start | 239 | 0 | 0 | 2 | 0 |
| 2019 | end | 235 | 4 | 0 | 2 | 0 |
| 2020 | start | 240 | 0 | 0 | 2 | 0 |
| 2020 | end | 240 | 0 | 0 | 2 | 0 |
| 2021 | start | 243 | 0 | 0 | 2 | 0 |
| 2021 | end | 243 | 0 | 0 | 2 | 0 |
| sealed, total | start | 1011 | 0 | 0 | 8 | 0 |
| sealed, total | end | 1010 | 0 | 1 | 8 | 0 |

**Coverage: empty / NaN dates of each new column** (one row per date):

| Column | Dev (of 1708) | Sealed (of 1019) |
|---|---|---|
| `xau_ret` | 0 | 0 |
| `xau_rv` | 0 | 0 |
| `xau_bv` | 0 | 0 |
| `n225_ret` | 7 | 0 |
| `usdjpy_us_ret` | 0 | 0 |
| `ewj_oc_jpy` | 3 | 0 |
| `gotobi_day` | 0 | 0 |
| `c_usdjpy_sess_ret` | 0 | 0 |
| `c_eurusd_sess_ret` | 0 | 0 |
| `xau_bars` | 0 | 0 |
| `xau_stale_start_min` | 0 | 0 |
| `xau_stale_end_min` | 0 | 0 |
| `n225_bars` | 7 | 0 |
| `n225_stale_start_min` | 7 | 0 |
| `n225_stale_end_min` | 7 | 0 |

- `ewj_oc_jpy` empty on 3 dev dates (expected 3, P12) and 0 sealed dates (expected 0): True

**usdjpy_us_ret exact-zero session nights** (us_n_sessions > 0 and usdjpy_us_ret == 0.0):

- Raw USD/JPY master and Book2.xlsx hash to PASS2_INPUTS.json: True
- Count: dev 4, sealed 2; equal to MANIFEST (4 / 2): True

| Dev date | us_n_sessions | NY session | open: bar label (UTC), staleness | close: bar label (UTC), staleness | distinct bars |
|---|---|---|---|---|---|
| 2015-03-30 | 1 | 2015-03-27 | 2015-03-27 13:29, 0 min | 2015-03-27 19:59, 0 min | True |
| 2015-04-15 | 1 | 2015-04-14 | 2015-04-14 13:29, 0 min | 2015-04-14 19:59, 0 min | True |
| 2017-04-24 | 1 | 2017-04-21 | 2017-04-21 13:29, 0 min | 2017-04-21 19:59, 0 min | True |
| 2019-07-23 | 1 | 2019-07-22 | 2019-07-22 13:29, 0 min | 2019-07-22 19:59, 0 min | True |

- Dev: sessions recomputed = us_n_sessions on every such night: True; recomputed sum exactly 0.0 on every such night: True; every session's open and close resolve to distinct bars: True
- Sealed: nights 2; sessions 2; sessions recomputed = us_n_sessions on every such night: True; recomputed sum exactly 0.0 on every such night: True; every session's open and close resolve to distinct bars: True

No STOP condition in 2.4.

Blinding: predictor and provenance columns only, as counts (sealed side: counts and booleans only); the raw USD/JPY master read by script for bar labels and staleness. No target and no gap column was loaded.
