# Data Provenance

Status: October 2026. §4 added 2026-10-04 (Pass 2 inputs) and updated 2026-10-05 (§4.4, §4.5, new §4.6) and 2026-10-06 (corrections to §4.2–§4.5; new §5, the Pass 2 build). This supersedes the September 2026 version, which documented the HistData FX layer.
Every claim below comes from an automated check run on the files themselves, not from vendor documentation. Two exceptions are labelled where they occur: the issuer documentation behind P47 (§4.4) and the settings-check attestation (§4.4, D2).
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

Every claim below comes from a check run on the files themselves. Hashes are in `PASS2_INPUTS.json`. All raw files stay local, in `~/Desktop/FX_Project/raw/`, and never go in the Claude Project, because each contains 2022+ data. Decisions are in `DECISIONS_P37_onward.md`.

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
| Gaps over 6 h | Weekends; the Christmas and New Year closures; and the 11 Good Friday closures, 2015–2025 (omitted from the 2026-10-04 record; found 2026-10-05). Good Friday is a TSE trading day: on the nights around it the XAU window endpoints are hours stale (§5.4), and no night has an empty xau_ret (0 dev, 0 confirmation). |
| 1-minute moves over 2% | Four: 2015-07-20 (flash crash), 2020-03-15 (Sunday reopen after the Fed's emergency cut), 2021-08-08/09 (flash crash), and 2026-01-29 15:27 (a fast decline over several minutes with partial recovery, not a one-tick spike). All four kept. |

### 4.3 Japan 225 CFD 1-minute (`jpn225_dukascopy_2015-01-01_2026-03-05.csv.gz`)

The instrument is `INSTRUMENT_IDX_ASIA_E_N225JAP`.

| Check | Result |
|---|---|
| Span | 2015-01-02 00:00 → 2026-03-06 00:00 UTC |
| Rows | 3,314,917 |
| Integrity | 0 nulls, 0 duplicates, monotone, 0 OHLC violations; flat bars 4.4% |
| 1-minute moves over 2% | 30, at session re-opens after the daily data holes; not errors |

**Coverage limitation.** Dukascopy did not quote this CFD through the Tokyo pre-open in the early years. From 2015-H2 through 2018-04-12 the "08:59 JST" price is stale on every Tokyo day. In 2016–2017 there are no bars between about 21:00 and 01:00 UTC, so it is about 4 hours stale. It is fresh on every Tokyo day from 2018-04-13 to 2018-06-29, and on 97.6–100% of Tokyo days in every later half-year.

Share of Tokyo days whose 08:59 JST price is at most 5 minutes stale. The calendar is the miners' calendar, one row per date. 2015-H1 includes 2015-01-05, which has no panel row.

| Half-year | Days | Fresh | Share |
|---|---|---|---|
| 2015-H1 | 121 | 45 | 37.2% |
| 2015-H2 → 2017-H2 | 615 | 0 | 0% |
| 2018-H1 | 121 | 53 | 43.8% |
| 2018-H2 | 124 | 123 | 99.2% |
| 2019-H1 | 117 | 116 | 99.1% |
| 2019-H2 | 124 | 121 | 97.6% |
| 2020-H1 | 119 | 118 | 99.2% |
| 2020-H2 | 123 | 121 | 98.4% |
| 2021-H1 | 121 | 121 | 100% |
| 2021-H2 | 124 | 121 | 97.6% |
| 2022-H1 | 120 | 119 | 99.2% |
| 2022-H2 | 124 | 123 | 99.2% |
| 2023-H1 | 122 | 122 | 100% |
| 2023-H2 | 124 | 122 | 98.4% |
| 2024-H1 | 120 | 119 | 99.2% |
| 2024-H2 | 125 | 123 | 98.4% |
| 2025-H1 | 119 | 118 | 99.2% |
| 2025-H2 | 124 | 123 | 99.2% |
| 2026-H1 | 41 | 41 | 100% |

**Earlier figures.** The 2026-10-04 figures (37% / about 0% / 97–99%; changeover 2018-07-02) were computed on a Mon–Fri calendar. On the miners' calendar, the trailing 60-day share first reaches 95% on **2018-07-05**. A Mon–Fri calendar gives 2018-07-02, and a 60-calendar-day window gives 2018-06-11. The date is descriptive only, because P42 is applied night by night.

**Threshold.** Freshness is all-or-nothing in this data. The variants "stale < 5 min", "≤ 4 min" and "a bar one minute later" give identical shares (builder, 2026-10-05), so the 5-minute threshold is not a forking-path choice.

**Scope.** Under P42's two-endpoint rule, 929 of the 1,708 dev nights are eligible (40 in 2015-H1, the rest from 2018-04-13), and 999 of the 1,019 confirmation nights; the counts are identical at thresholds of 4, 5 and 10 minutes (reports/P2_5_dev_checks.md §2.4).

Usage rule: P42, adopted at the Pass 2 decision checkpoint (D7; DECISIONS P63).

### 4.4 Bloomberg 1306 and TOPIX total return (`newbloombergdata.xlsx` → `newbloombergdata_fixed.xlsx`)

**Sheet `1306`** (date, open, last, high, low; values only; no header):
- 2,728 rows on dates **identical** to the miners' calendar (2015-01-05 → 2026-03-05).
- No nulls or duplicates; OHLC consistent on every row; no split discontinuity (no |log open/prev close| > 0.5).
- Six rows have open = close = previous close (2016-12-14, 2017-02-23, 2017-05-29, 2017-06-26, 2018-05-21, 2023-10-06). All have a nonzero high–low range. On a 0.1-tick split-adjusted grid this is coincidence, not staleness, so they are kept.
- **Open-auction timing (P18; D8).**
  - The split-adjusted price grid is 0.1 in 2015–2020, with 0.05 steps in 2021 (14 of 245 moves).
  - 84 dev dates (4.92%) open exactly at the previous close.
  - The tick rule's R = 1.541 flagged, driven by 2021's mixed grid (2015–2020 alone: 1.43).
  - The zero-gap gate places the 84 dates in the quintiles of |TOPIX gap| as 72 / 12 / 0 / 0 / 0, with a maximum of 0.306%: tick coincidences on quiet mornings, not stale opens.
  - D8 (a): the check is treated as passed on documented exchange convention plus consistency evidence (PASS2_HANDOFF D8; DECISIONS P64). Evidence: `reports/P2_5_dev_checks.md` (§2.3) and `reports/P2_3b_d8_gate.md`.

**Sheet `1306 dividends`** (DVD_HIST_ALL; 11 annual ex-dates, 2015–2025):
- **The amounts were on the pre-split basis.** Raw amount / prior close gives implied yields of 13.6–21% on every dev ex-date (2015–2021). For the four 2022+ ex-dates, the boolean 'every raw implied yield lies in 13.6–21%' is False. The ÷10 factor does not rest on this range; it rests on the two sources below (P47).
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
  - In binary floating point, RAW ÷ 10 differs from the stored corrected amount in the last bit on 1 of the 11 rows. The build uses the stored corrected amounts and never recomputes RAW ÷ 10 (Isaiah, 2026-10-05).
- **The type was `Distribution`,** which `build_panel.CASH_TYPES` would silently drop. The corrected copy relabels it `Regular Cash`.
- `1306 dividends RAW` keeps Bloomberg's original values, and every other sheet is a cell-for-cell copy.

**1306 and TOPIX gaps on the dev ex-dates** (log, % to 2 decimals; corrected 2026-10-05, `reports/P2_5_resolutions.md`). The panel's `ao_1306_gap_adj` equals an independent recomputation, ln(open_t / (close_{t−1} − D_t)) from the raw sheet, to 1e-12:

| Ex-date | 1306 adjusted gap | TOPIX gap |
|---|---|---|
| 2015-07-08 | −0.30 | −0.41 |
| 2016-07-06 | −1.64 | −1.55 |
| 2017-07-06 | 0.00 | −0.04 |
| 2018-07-06 | +0.78 | +0.55 |
| 2019-07-08 | −0.17 | −0.26 |
| 2020-07-09 | −0.13 | −0.09 |
| 2021-07-08 | −0.22 | −0.15 |

The largest difference is 0.23 pp, so the ÷10 factor holds in every dev year. The table handed to P2-5 had four 1306 values off by 0.01 pp, because it was built from rounded simple percentages; the panel was right.

**Index staleness (P55; D10).** The reverse-slope 95% CIs lie above 1 in both samples, so staleness is established. The brackets are [0.757, 0.829] and [0.758, 0.829]: the TOPIX 09:00 print carries about 76–83% of the fresh market gap (`reports/P2_5_dev_checks.md` §2.2). Documentation only: it qualifies the fallback's staleness caveat (P18).

**Sheet `TOPIX optional`** (TOPIX total-return close):
- 2,729 rows: the miners' calendar plus **2020-10-01**, the TSE outage day, the same stale row Book2's TOPIX sheet has, which the build drops.
- The level (1,916.75 in January 2015, against about 1,431 for the price index) identifies it as a total-return index. The series is **TPXDDVD Index**, TOPIX's dividend-included (gross total-return) index (D3, Isaiah, 2026-10-05), checked by the supervisor against JPX's TOPIX factsheet. JPX also publishes a separate net total-return index; the gross series is the right one for the ex-date correction.
- Used only by the fallback path.

**Resolved (2026-10-05):**
- **Settings check (P39b), by attestation (D2, Isaiah, 2026-10-05).** Book2 and the 1306 sheet were both pulled with the JT suffix and the Appendix E settings. The 1A cell-for-cell re-pull was not run.
  - The adjustment settings are corroborated by the data for both files (§2; this section; P47).
  - The suffix itself cannot be identified from daily data.
  - A 1A re-pull remains optional. If one is ever run and fails, D2's remedy applies (PASS2_HANDOFF §6, item 2).
- **TOPIX total-return ticker (P40):** TPXDDVD Index (above). The workbook holds values only, so Isaiah supplied the ticker.
- **CACS split ratio and date** (P47).

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

**2026-10-05, second supervisor chat** (its attestation: the 2026-10-05 supervisor handoff, §10; retired from the Project). All of it was on the Project copies:
- the SHA-256 of every Project file;
- `open`, `prev_close` and `ao_gap_raw` from the dev panel, printing only counts of implementation matches (Flag 16);
- `date` and `ao_topix_gap` on the 7 dev 1306 ex-dates, printing the gap values (dev, gap-only; D8);
- synthetic `log` tests.

**2026-10-05, third supervisor chat** (its attestations: the P2-6 records register, §4, and the P2-6 supervisor handoff, §8; both retired from the Project). Also on the Project copies only:
- the SHA-256 of every Project file;
- the dev panel's `date` column, for calendar counts.

**2026-10-06, supervisor chat (the P2-6 review).** Also on the Project copies only: the SHA-256 of every Project file; the dev panel's `date` column, for the calendar count in §5.4.

No other column of any data file was read. In none of these chats was any target related to any predictor, and no sealed, raw or 2022+ value was seen.

The builder's real-data contact in Pass 2 is listed in PASS2_STATUS, Blinding attestation.

Nothing related any predictor to any target.

**Pass 3 supervisor chats (2026-10-06 to 2026-10-07).** Each chat's own attestation is in its handoff: H1, `PASS3_SUPERVISOR_HANDOFF_2_2026-10-06.md` §9; H2, `PASS3_SUPERVISOR_HANDOFF_3_2026-10-07.md` §9; H3, `PASS3_SUPERVISOR_HANDOFF_4_2026-10-07.md` §8. The last chat's is recorded here directly. The handoffs stay on the Mac, outside the repo and the Project.
- **2026-10-06, supervisor chat (the P2-6 review), supplement** from its handoff (H0, `PASS3_SUPERVISOR_HANDOFF_2026-10-06.md` §7): also a count of the lines in the Pass 1 `MANIFEST.json` that contain two hash prefixes, and calendar arithmetic on the P2-1 gap timestamps (2022+ dates only).
- **2026-10-06, Pass 3 supervisor chat 1 (the builder prompt; P3-0).** On the Project copies, or on reports the builder returned: the SHA-256 of all 36 Project files; documents; the key fields of the two synthetic C7 reports; `MANIFEST.json`'s platform and library-version fields; `PASS2_INPUTS.json`'s registry hash fields; and the P3-0 report (hashes, counts, BLIND_FIT_LOG metadata, code excerpts, the structure of the B7 and B7b reports with no values, and the synthetic B6 diff). Web searches for public cost references (IBKR, SBI, JPX tick tables).
- **2026-10-06 to 2026-10-07, Pass 3 supervisor chat 2 (P3-0b to P3-3a).** Whole-file hashes of the Project files and documents. Builder reports: target-side price quantiles, grids and counts (P3-0b); mean |ẽ| (predictor-only), β̄ (target-only), the round trips and the SESOI (P3-1); synthetic timings and aggregates (P3-1b, P3-2a); K = 409 and K16 = 165, target-only counts (P3-2b); code, the structural check's booleans and counts, and synthetic smoke runs (P3-2c to P3-2e); the first rehearsal's log and synthetic outputs; the spec, `spec.py`, test code, synthetic aggregates and the DQ5 patch (P3-3a). Isaiah's cost note: approximate 2026 price levels, share counts and trading values, with no daily prices or returns. Web searches: JPX tick-size notices, TOPIX100 constituent lists and the warp-speed reference. Synthetic simulations in the supervisor's sandbox, with no data.
- **2026-10-07, Pass 3 supervisor chat 3 (P3-3b to P3-5).** Whole-file hashes of the Project files and documents. Builder reports from P3-3b to P3-5, including the sealed run's aggregates (rejection and TOST rates with counts, critical values with intervals, MDE80, the T3 rates and cross-tabs, and the centred T6 blocks), which are aggregates over synthetic draws from the sealed calibrator. Isaiah's Terminal output of the launcher (checks, status line, hashes and times). In the supervisor's sandbox, with no data: the launcher rebuilt and run against a stub tool in a fake repository; a synthetic check of D4.3a's winsorised dependence; recomputations from printed integers. No web searches.
- **2026-10-07, Pass 3 supervisor chat 4 (P3-6a to P3-7b).** Whole-file hashes of the 36 Project files and of the chat uploads (the handoffs H1 to H3 and a P3-5 copy of `PASS3_STATUS.md`); the chat interface also attached the column names and row counts of the Project's `panel_dev.csv`, `events_firm.csv` and `events_boj.csv` (no values). Documents; builder reports from P3-5 to P3-7a2, and the new builder session's orientation report; recomputations from printed integers and hashes in the supervisor's sandbox, with no data. No web searches.

No data file was opened in the four Pass 3 chats, and in none of them did anything relate any predictor to any target. No raw, sealed or 2022+ value was seen in them, except the coarse 2026 levels in Isaiah's cost note (chat 2), which is prior exposure carried to the pre-registration (DECISIONS_P71_onward, carried item 4).

The builder's real-data contact in Pass 3 is listed in PASS3_STATUS, Blinding attestation, including the one sanctioned sealed fit (`BLIND_FIT_LOG` line 7).

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

---

## 5. The Pass 2 build (2026-10-05; MANIFEST `built` 2026-10-06T00:30:20.330090+00:00)

### 5.1 Where it ran
| Item | Value |
|---|---|
| Machine | Isaiah's Mac, macOS arm64 (Apple Silicon). The builder is Claude Code 2.1.289 |
| Environment | `~/venvs/ofilt_p2`: Python 3.12.4; numpy 2.4.4, pandas 3.0.2, scipy 1.17.1, scikit-learn 1.8.0, openpyxl 3.1.5, PyYAML 6.0.3, joblib 1.5.3, threadpoolctl 3.6.0, python-dateutil 2.9.0.post0; BLAS is Apple Accelerate. The versions are pinned to a Claude sandbox's on 2026-10-05. The suite needs numpy ≥ 2. Conda is not used |
| Local layout | Under `~/Desktop/FX_Project/`: `ofilt_pass1/` (REPO); `raw/` (RAW, with `raw/checks/`, organised by `organize_raw_inputs.py`, originals untouched); `data/` (DATA = `OFILT_DATA_DIR`); `files/pass2_kit_2026-10-05/` (KIT); `build_out/` (OUT, outside the repo, holding the sealed panels) |
| Build code | The frozen `build/pass1/` originals (hashes as in PASS2_INPUTS.json) run unchanged. `build/pass2/build_panel_p2.py` and `columns.py` append the 19 new columns (P51). Hashes: `build_panel_p2.py` `7ac2199480bf1659812d3de8fcbce15d77c6ef2fc44d3c75402ca29833772572`; `columns.py` `6037dc9b26da4c61b5e85e9649920a3b6bb9795ddfe44cce21eb9c48e06ba1d6` (MANIFEST.json) |

### 5.2 Flag 16: platform floating point
The Pass 1 panels (`736636…`, `9c18a6c1…`) were built on 2026-10-01 in a Claude sandbox (x86_64, AVX-512), using numpy's SIMD `log`. macOS arm64 computes `log` differently in the last bit, so no Mac environment reproduces either hash.

The Mac is deterministic. Both Mac environments produce identical panels, and the repo's frozen build reproduces the Mac hashes exactly (P2-0b): dev `656d5117…` and sealed `138e5e21…`, with full hashes in PASS2_INPUTS.json.

- **Dev comparison with `736636…`,** under a rule stated in advance:
  - the 23 non-log columns are string-identical;
  - the 18 log-derived columns agree within 1e-8 relative, with the largest relative difference 2.273e-13;
  - single-log columns differ by at most 1 ulp, and rv/bv by up to 1,876 ulps (cancellation in minute differences).
- **Mechanism** (supervisor; dev, gap-only, counts only):
  - the stored `ao_gap_raw` equals numpy's SIMD `log(open/prev_close)` on 5,124 of 5,124 rows;
  - it differs from the C-library `log` on 223 rows, by 1 ulp each;
  - the Mac differs on 222 rows.
- **Consequence.** Hashes prove identity only on the same numerical platform. A cross-platform rebuild is checked against a tolerance rule stated in advance, as above.
- **B6 report.** `reports/B6_coverage.json` is rewritten by every suite run and differs off the sandbox in the last digits. `tools/checkpoint.sh` restores it.
- **C7:** rerun once, on the Mac, inside the switch (D16; P2-3b). The structure and keys, every integer, boolean, string and null except `key.spec_sha256` (which equals the edited spec's SHA-256, by design), and every per-replication rejection flag and summary count are identical to the sandbox report. In `C7_mc.json`, 2,772 of the 2,846 floats other than `runtime_s` differ only in the last bits (largest relative difference 4.4e-11); in `C7_h1_same_dgp.json`, no float other than `runtime_s` differs. The wall-clock `runtime_s` is information only. The slow tier's two bit-identity tests pass on the Mac against the Mac report.

### 5.3 Where the old columns come from (the hybrid; Isaiah, 2026-10-05)
- **Dev.** The 41 old columns are the original `736636…` strings, read back as strings (P51). Acceptance (a): the dev 41-column projection hashes to `736636…`.
- **Sealed.** The 41 old columns are the Mac frozen build's. Acceptance (b): the sealed 41-column projection hashes to `138e5e21…`.
- **Disclosure.** The original sealed file (`9c18a6c1…`) is not available anywhere on the Mac, so byte identity of the sealed old columns with it cannot be demonstrated. On dev, where both builds exist, they differ only as in §5.2. The pre-registration discloses this.
- MANIFEST records both reference pairs.

### 5.4 Build checks and outputs (P2-4, `build_out/p2_20261006T002928Z/`; `reports/P2_4_acceptance.md`)
- **Verification:** every input, event-file and code hash checked against PASS2_INPUTS.json before reading. Acceptance (a)–(g): all True ("P2-4 ACCEPTED: True"). Build assertions: 72, all passed; their names are in MANIFEST.json (`build_assertions.names`): 14 hash checks (inputs, event files and their working copies, frozen code, the original dev panel), 17 per panel on each of dev and sealed (rows, order, columns, `us_n_sessions`, `usdjpy_us_ret`, `ewj_oc_jpy`, the 1306 columns, window instants, `gotobi_day`, and the written old columns), and 24 on the frozen build, the old panels, the 1306, TOPIX and NYSE calendars, and the XAU and Japan 225 windows.
- **`usdjpy_us_ret`:** 0.0 wherever `us_n_sessions` = 0, and finite wherever it is > 0. This amended rule replaces A′'s "if and only if". Nights with sessions but an exact 0.0 sum: 4 (dev) and 2 (sealed), each an equal bid at the NY open and close on distinct, fresh bars (`reports/P2_5_dev_checks.md` §2.4).
- **`xau_ret`:** empty on 0 dev dates (sealed: a count only, 0). On a night with no bar in the window, every `xau_*` / `n225_*` column is empty. XAU window endpoints more than 60 minutes stale: dev 14 (start) and 15 (end) dates, 2–3 a year; sealed 8 and 8 (counts; `reports/P2_5_dev_checks.md` §2.4). These counts follow from the long XAU closures (§4.2; the gap times are in `reports/P2_1_inputs.md`). Each Good Friday closure and each Christmas closure leaves one window start and one window end more than 60 minutes stale. That accounts for all 14 dev start dates, 14 of the 15 dev end dates, and all 8 and 8 confirmation dates; the New Year closures fall while the TSE is closed. The remaining dev end date comes from a shorter outage, below the 6-hour gap threshold (supervisor, 2026-10-06; calendar arithmetic on the gap times and the TSE calendar; counts only).
- **Japan 225 freshness:** equals §4.3 on the same dates, every half-year, dev and 2022+: True.
- **`gotobi_day`:** 529 (dev) and 319 (sealed) per ticker: True.
- **Outputs:**
  - dev `panel_dev.csv`: SHA-256 `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68`, 5,124 rows, 60 columns, 2015-01-06 → 2021-12-30;
  - sealed `panel_confirm_SEALED.csv`: SHA-256 `b575272aad752b3af84abe109fa66edde421f7c99184c9d1885bacdce64f06d1`, 3,057 rows, 60 columns, 2022-01-04 → 2026-03-05;
  - `MANIFEST.json`: SHA-256 `1345c0772777b87e9d5fcc01794340231c04068f383330762e68ff3ef468e8bd`;
  - git HEAD at the build: `34f61dbb49a14bdb1965e20fab71ded33057509b` (`checkpoint: P2-3a`).

### 5.5 The switch (P2-3b)
- Commit `b9bf6f3d2e7b11243af6d626713417b5c87423b8` (`checkpoint: P2-3b switch (AM-03, AM-04, AM-05; C7 rerun on the Mac)`).
- Spec SHA-256 after AM-03, AM-04 and AM-05: `0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee408561f68f96fd94d3b0f9`.
- The dev panel in DATA is the P2-4 dev panel, `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68`.
- The Pass 1 dev panel is archived as `data/archive/panel_dev_736636031ca1.csv` (`736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42`), so `BLIND_FIT_LOG` lines 1–6 stay verifiable.
