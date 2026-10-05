# Data Provenance

Status: October 2026. §4 added 2026-10-04 (Pass 2 inputs) and updated 2026-10-05 (§4.4, §4.5, new §4.6). This supersedes the September 2026 version, which documented the HistData FX layer.
Every claim below comes from an automated check run on the files themselves, not from vendor documentation.
Input hashes are in `MANIFEST.json`.

---

## 1. FX: Dukascopy 1-minute bars (sole FX source)

| File | Rows | Span (UTC) |
|---|---|---|
| `usdjpy_dukascopy_2015-01-01_2026-03-05.csv` | 4,162,935 | 2015-01-01 22:00 → 2026-03-06 00:00 |
| `eurusd_dukascopy_2015-01-01_2026-03-05.csv` | 4,164,182 | 2015-01-01 22:00 → 2026-03-06 00:00 |

The columns are `ts_utc, open, high, low, close`. They were pulled with `pull_dukascopy.py` (bid side) or a close variant of it. **Offer side: RESOLVED, BID (2026-10-04).** A fresh bid-side pull of 2019-06-04 matched the USD/JPY master on 1,199 of 1,199 overlapping bars, close for close (DECISIONS P37).

**Integrity.**
- Zero nulls, zero duplicate timestamps, monotone timestamps, and zero OHLC violations.
- About 373,000 bars per year out of roughly 374,400 possible minutes.
- Every weekday with fewer than 1,000 bars is a Christmas or New Year holiday.
- About 0.6–0.7% of bars are flat carry-forwards, concentrated at the 21:00–23:00 UTC rollover. There is no systematic forward-filling.
- There are only two one-minute USD/JPY moves larger than 2%, both on Brexit night (2016-06-23/24). Both are genuine.
- There is no equivalent of the 2023 HistData vendor hole.

**Timestamps are true UTC.** The test that matters looks at the weeks between the US and EU clock changes, where HistData was off by an hour. Pooled across 2015–2025, the 08:30 New York release appears at 12:30 UTC, not 13:30 UTC:

| Pair | Spring gap: 12:30 / 13:30 UTC | Autumn gap: 12:30 / 13:30 UTC |
|---|---|---|
| EUR/USD | 3.22 / 1.48 bp | 4.63 / 1.09 bp |
| USD/JPY | 3.48 / 2.17 bp | 4.59 / 1.39 bp |

Year-by-year checks show the same shift on the US transition date in most years. The noisy years are dominated by other scheduled releases, such as the ECB decision at 12:45 UTC in March 2022.

**Bars are start-labeled.** The 08:30 New York release spike falls in the bar labeled 12:30 UTC (about 5.1 bp), not the bar labeled 12:31 (about 2.0 bp), in EUR/USD during US daylight time. So a bar labeled X covers X to X+1 minute, and its close is the price at about X+1 minute. The USD/JPY Tokyo-fix activity sits in the bar labeled 00:54 UTC (09:54–09:55 JST), which is consistent with this.

**Consequence.** The price at instant X is the close of the last bar labeled at or before X − 1 minute. The dark window therefore ends at the close of the bar labeled 08:58 JST, which is the price at 08:59:00, a 60-second buffer before the auction.

**Cross-validation against HistData.** About 7,400 dark-window returns were recomputed over identical windows. Correlation is 0.995–0.9998 and the slope is 1.00. On ordinary Tokyo nights in 2023–2026, the mean absolute difference is 0.11 bp, and no night differs by more than 5 bp. The disagreements are concentrated in HistData's defect windows:

| Window | Share of nights differing by more than 5 bp |
|---|---|
| 2023 vendor hole | 32% |
| Spring 2023 DST gap | 40% |
| Autumn 2024 DST gap | 40% |
| Autumn 2025 DST gap | 80% |

Dukascopy passed the release-timing test independently in exactly these weeks, so the errors are on the HistData side. The autumn 2025 result indicates that HistData changed its convention during 2025, and that `histdata_tz.py` mis-corrects that window.

**HistData is retired**, along with `histdata_tz.py`, `build_windows.py`, `slim_encode.py`, and `fx_dark_window_features.csv`. The September findings about HistData (EU-date DST switching, the 2023 hole, the xlsx dimension-record trap) remain true of HistData. They are no longer relevant to this project's data.

## 2. Equities, index, US controls, dividends: `Book2.xlsx` (Bloomberg)

**Sheets.**
- 5713, 5711, 5706 (columns: date, open, last, high, low)
- TOPIX, SPY, EWJ, FCX, COPX (columns: date, open, last)
- One `<ticker> dividends` sheet per miner, which is `DVD_HIST_ALL` output

The sheets have no header rows. The column order was inferred from the data: high ≥ max(open, last) and low ≤ min(open, last) hold on 100% of rows.

**Coverage.**
- Miners and TOPIX: 2015-01-05 → 2026-03-05. The miners have 2,728 identical trading dates.
- US series: 2015-01-02 → 2026-03-05, 2,809 identical dates.
- There are no nulls.

**Adjustment convention.** This was established from the data, which closes the old DPDF open item.
- **Capital changes are adjusted.** There are no price jumps at any of the four share-count changes in the dividend sheets: 5711 1:10 (2016-09-28), 5713 1:2 (2017-09-27), 5706 1:10 (2017-09-27), and 5706 10:1 (ex-date 2026-09-29).
- **Cash dividends are not adjusted.** Across 48 ex-dates, the mean gap is −1.23% against a mean dividend yield of 1.43%. The difference is 0.19% with a standard error of 0.22%.
- **Dividend amounts are on the same share basis as prices.** Implied yields run from 0.4% to 4%.
- **Warning:** because of the 2026-09-29 split, 5706 prices here are on the post-split basis. The Math 86 `JPEquities.xlsx` predates the split. Never mix the two files.

**Dividend types.** Cash dividends appear as Final, Interim, Regular Cash, Special Cash, and Memorial. These are summed by ex-date. Stock Split, Omitted, Cancelled, and Poison Pill rows are excluded.

**Known bad rows, handled in `build_panel.py`.**
- **TOPIX 2020-10-01:** this was the TSE's full-day system outage. Bloomberg carries a stale row with open = close = prior close. It is dropped, and the miners correctly have no row that day.
- **EWJ 2015-07-20, 2016-08-30, 2016-10-07:** open = close = prior close. These are set to missing.

**Extreme moves checked.** Every extreme move matches a real event. FCX's −22.5% open→close move on 2016-01-11 was checked and is genuine.

## 3. Event calendars

**Source.** A Claude Deep Research report (September 2026) built from company IR archives, TDnet PDFs, aggregators (irbank, buffett-code), and boj.or.jp.

**Files.** The calendars are written to `events_firm.csv` and `events_boj.csv` by `make_events.py`.

- **Earnings (決算短信):** 135 releases, 45 per company, FY2014 Q3 → FY2025 Q3. All three companies close their fiscal year on March 31.
- **Standalone news:** 8 items (forecast revisions, special losses, delay notices).
- **Mechanical:** 5 items (corrections and a consolidation restatement). These are recorded, not excluded.
- **Audit candidates:** 15. These are outcome-identified large moves, used for robustness only.
- **BoJ:** 98 policy announcements, 2014-12-19 → 2026-03-19. The report's headline total of 94 was an arithmetic error; the per-year counts and the 98 rows are correct.

**Validation against prices.**
- 68% of earnings releases show a market-adjusted move above 2σ on day D's open→close or on day D+1's gap, against a base rate of 7–9%. HIGH- and LOW-confidence rows confirm at similar rates (71% vs 67%).
- On BoJ announcement days, TOPIX open→close exceeds 2σ on 12% of days versus 6% otherwise (one-sided p ≈ 0.05).
- Every event date maps to a TSE trading day.

**Manual checks** were done by Isaiah in October 2026. The 15 audit candidates and 5711's 2022-08-09 release were checked with no changes. The `check_status` column records which rows were checked.

---

## 4. Pass 2 inputs (added 2026-10-04)

Every claim below comes from a check run on the files themselves. Hashes are in `PASS2_INPUTS.json`. All raw files stay local, in `~/Desktop/FX Project/raw/`, and never go in the Claude Project, because each contains 2022+ data. Decisions are in `DECISIONS_P37_onward.md`.

### 4.1 Dukascopy pull procedure (patched `pull_dukascopy.py`)

- **Offer side is bid** for the masters, confirmed against the USD/JPY master (P37).
- **The library reads naive datetimes as local time.** A request for 2019-06-04 00:00 on a US-Eastern machine returned data from 04:00 UTC. Request bounds are now built in UTC and converted to local clock time before the call. A re-pull then gave 2019-06-04 00:00 → 2019-06-05 00:00 UTC (1,439 bars).
- **Output timestamps are UTC.** The labels match the verified masters bar for bar.
- **The existing masters are unaffected.** Their yearly fetches are contiguous, and their UTC labelling was verified independently (§1, release-timing test).
- **Every request is capped at end_date + 1 day + 1 minute.** No data after 2026-03-05 is downloaded (forward-holdout rule, P13).

### 4.2 XAU/USD 1-minute (`xauusd_dukascopy_2015-01-01_2026-03-05.csv.gz`)

| Check | Result |
|---|---|
| Span | 2015-01-01 23:00 → 2026-03-06 00:00 UTC |
| Rows | 3,957,473 (about 353–356k per full year; gold has a daily trading break) |
| Integrity | 0 nulls, 0 duplicates, monotone, 0 OHLC violations, 0 non-positive prices; flat bars 0.26% |
| Gaps over 6 h | Weekends, plus the Christmas and New Year closures only |
| 1-minute moves over 2% | Four: 2015-07-20 (flash crash), 2020-03-15 (Sunday reopen after the Fed's emergency cut), 2021-08-08/09 (flash crash), and 2026-01-29 15:27 (a fast decline over several minutes with partial recovery, not a one-tick spike). All four kept. |

### 4.3 Japan 225 CFD 1-minute (`jpn225_dukascopy_2015-01-01_2026-03-05.csv.gz`)

The instrument is `INSTRUMENT_IDX_ASIA_E_N225JAP`.

| Check | Result |
|---|---|
| Span | 2015-01-02 00:00 → 2026-03-06 00:00 UTC |
| Rows | 3,314,917 |
| Integrity | 0 nulls, 0 duplicates, monotone, 0 OHLC violations; flat bars 4.4% |
| 1-minute moves over 2% | 30, at session re-opens after the daily data holes; not errors |

**Coverage limitation.** Dukascopy did not quote this CFD through the Tokyo pre-open in early years. From 2015-H2 to 2018-H1 there are no bars between about 21:00 and 01:00 UTC, so the "08:59 JST" price is about 4 hours stale.

Share of Tokyo days whose 08:59 JST price is at most 5 minutes stale:

| Period | 2015-H1 | 2015-H2 → 2018-H1 | 2018-H2 onward |
|---|---|---|---|
| Share | 37% | about 0% | 97–99% |

The trailing 60-day share first reaches 95% on **2018-07-02**. Usage rule: see P42 (PROPOSED).

### 4.4 Bloomberg 1306 and TOPIX total return (`newbloombergdata.xlsx` → `newbloombergdata_fixed.xlsx`)

**Sheet `1306`** (date, open, last, high, low; values only; no header):
- 2,728 rows on dates **identical** to the miners' calendar (2015-01-05 → 2026-03-05).
- No nulls or duplicates; OHLC consistent on every row; no split discontinuity (no |log open/prev close| > 0.5).
- Six rows have open = close = previous close (2016-12-14, 2017-02-23, 2017-05-29, 2017-06-26, 2018-05-21, 2023-10-06). All have a nonzero high–low range. On a 0.1-tick split-adjusted grid this is coincidence, not staleness, so they are kept.

**Sheet `1306 dividends`** (DVD_HIST_ALL; 11 annual ex-dates, 2015–2025):
- **The amounts were on the pre-split basis.** Raw amount / prior close gives implied yields of 13.6–21% on every ex-date.
  - Divided by 10, they match the ex-day opening drops: 2017-07-06 1.55% vs 1.55%; 2019-07-08 2.00% vs 2.16%; 2020-07-09 2.01% vs 2.14%; 2021-07-08 1.80% vs 2.01%.
  - One factor fits all 11, so the split postdates 2025-07-09.
  - **The corrected copy divides the amounts by 10.** The factor is **CONFIRMED** (P47, 2026-10-05) by two independent sources:
    - *The issuer.* Nomura Asset Management's notice for NEXT FUNDS TOPIX ETF, and its timely disclosure of 2026-02-17, announce a 1-unit → 10-unit split with record date 2026-03-31 and effective date 2026-04-01. That is after the panel's last date, which is why the prices show no discontinuity and only the dividend amounts kept the old basis.
    - *The amounts.* Raw amount ÷ 10 equals Nomura's published split-adjusted distribution per unit for July 2021 (3.66 yen). It also matches for July 2022–2025, checked as booleans only.
    - `1306 JT Equity CACS <GO>` is an optional extra confirmation of Bloomberg's own record.
  - Dev ex-dates, raw → corrected amount in yen per unit (all with record date 10 July):

    | Ex-date | Raw | Corrected |
    |---|---|---|
    | 2015-07-08 | 23.0 | 2.30 |
    | 2016-07-06 | 27.3 | 2.73 |
    | 2017-07-06 | 26.0 | 2.60 |
    | 2018-07-06 | 30.5 | 3.05 |
    | 2019-07-08 | 33.3 | 3.33 |
    | 2020-07-09 | 32.9 | 3.29 |
    | 2021-07-08 | 36.6 | 3.66 |
- **The type was `Distribution`,** which `build_panel.CASH_TYPES` would silently drop. The corrected copy relabels it `Regular Cash`.
- `1306 dividends RAW` keeps Bloomberg's original values, and every other sheet is a cell-for-cell copy.

**Sheet `TOPIX optional`** (TOPIX total-return close):
- 2,729 rows: the miners' calendar plus **2020-10-01**, the TSE outage day, the same stale row Book2's TOPIX sheet has, which the build drops.
- The level (1,916.75 in January 2015, against about 1,431 for the price index) identifies it as a total-return index. The ticker is PENDING (P40).
- Used only by the fallback path.

**Pending (P39/P40), as of 2026-10-05:**
- The settings-check result: which suffix (JT/JP) matched `Book2.xlsx` exactly, and whether 1306 used it. **Blocking for Pass 2.**
- The TOPIX total-return ticker, needed for records only. It can't be recovered from the workbook: every sheet holds pasted values, with no formula, header or ticker text (checked 2026-10-05).
- Resolved: the CACS split ratio and date (P47).

### 4.5 Blinding note for this section

All computations here were predictor-only or hedge-only. They cover dates, counts, integrity booleans, gaps, staleness, and dividend-to-price ratios (shown for dev ex-dates only; 2022+ as a pass/fail).

A few 2026 XAU closes around 2026-01-29 were printed while checking an outlier. One 1306 stale-row date (2023-10-06) is in the confirmation period. Nothing related any predictor to any miner target, and no target column was read.

**2026-10-05, supervisor chat.**
- **Hashes.** The five uploaded files (`newbloombergdata.xlsx`, the 2019-06-04 USD/JPY check file, the XAU and Japan 225 files, and `pull_dukascopy.py`) were hashed, and all match `PASS2_INPUTS.json`. The Dukascopy files were hashed only, never parsed.
- **Workbook.** Only the following was read:
  - the cell types (not values) of every sheet;
  - the `1306 dividends` sheet: ex-dates, record dates and amounts. The dev amounts are shown in §4.4; the 2022+ amounts were compared with Nomura's published figures as booleans only.
  - The `1306` price sheet and the `TOPIX optional` sheet were loaded only so their cell types could be counted. None of their values was printed, summarised or used.
- **Calendars.** The gotobi counts in §4.6 use calendar data only: the dev panel's `date` column and `calendar.confirmation_calendar()`.
- **Test suite.** The repo's suite was run on the Project's dev panel. These are Pass 1's own structural and target-only tests, with `OFILT_RUN_SEALED` unset; `BLIND_FIT_LOG` was unchanged at 6 lines.
- **Probe.** One probe changed a comment in the spec of a scratch copy and ran the C7 staleness and spec tests; it read no data.

Nothing related any predictor to any target.

### 4.6 Calendar facts used by the Pass 2 build (2026-10-05)

**TSE sessions.**
- The half-day sessions on the first and last trading days of the year were abolished from 30 December 2009 (Daiwa Institute of Research). Every 2015–2026 session therefore closes at 15:00 JST, or at 15:30 JST from 2024-11-05.
- The 2020-10-01 system outage remains the only missing session.

**NYSE early closes at 13:00 ET, 2015-01 → 2026-03-05.** These come from the NYSE Group / ICE holiday and early-closing calendar releases of 2013–2023. There are 23 dates, and none in 2026-01-01 → 2026-03-05. Full-day closures are simply absent from Book2's US calendar. The build uses this list for `usdjpy_us_ret` (P49).

| Year | Dates |
|---|---|
| 2015 | 2015-11-27, 2015-12-24 |
| 2016 | 2016-11-25 |
| 2017 | 2017-07-03, 2017-11-24 |
| 2018 | 2018-07-03, 2018-11-23, 2018-12-24 |
| 2019 | 2019-07-03, 2019-11-29, 2019-12-24 |
| 2020 | 2020-11-27, 2020-12-24 |
| 2021 | 2021-11-26 |
| 2022 | 2022-11-25 |
| 2023 | 2023-07-03, 2023-11-24 |
| 2024 | 2024-07-03, 2024-11-29, 2024-12-24 |
| 2025 | 2025-07-03, 2025-11-28, 2025-12-24 |

**Gotobi calendar (P48).** This is computed on the miners' TSE calendar.
- Dev: 529 of the 1,708 panel dates are flagged (31.0%; 74, 76, 78, 77, 75, 75 and 74 for 2015 through 2021).
- Confirmation: 319 of the 1,019 calendar dates (31.3%).
- Four nominal dates roll back into the previous month:

  | Nominal date | Rolls to |
  |---|---|
  | 2019-05-05 | 2019-04-26 |
  | 2020-01-05 | 2019-12-30 |
  | 2021-05-05 | 2021-04-30 |
  | 2025-01-05 | 2024-12-30 |

**1306 split in the forward holdout.** The record date is 2026-03-31 and the effective date 2026-04-01 (P47). When the holdout is pulled after `prereg-v1`, check for a price discontinuity around these dates, as P13(a) requires for 5706.
