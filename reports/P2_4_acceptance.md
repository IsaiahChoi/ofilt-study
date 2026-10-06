# P2-4 acceptance: `p2_20261006T002928Z`

## Files and MANIFEST
- panel_dev.csv hashes to its MANIFEST entry: True
- panel_confirm_SEALED.csv hashes to its MANIFEST entry: True
- MANIFEST git head is this checkout's HEAD: True
- MANIFEST records build/ and docs/PASS2_INPUTS.json clean: True
- the original dev panel hashes to 736636031ca1...: True

## (a), (b) old-column projections (in memory)
- (a) dev 41-column projection hashes to 736636031ca1... (computed 736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42): True
- (b) sealed 41-column projection hashes to 138e5e2104d5...: True

## (c) calendars
- (c) sealed dates equal calendar.confirmation_calendar() (1019 vs 1019): True
- (c) dev dates unchanged (1708 dates; 1,708): True

## (d) shape
- (d) dev rows 5,124 and 60 columns (5124, 60): True
- (d) sealed rows 3,057 and 60 columns (3057, 60): True

## (e) new columns (sealed side: counts and booleans only)
- (e) dev: y_1306_oc, ao_1306_gap_raw, ao_1306_gap_adj finite on every row: True
- (e) dev: usdjpy_us_ret == 0.0 wherever us_n_sessions == 0: True
- (e) dev: usdjpy_us_ret finite wherever us_n_sessions > 0: True
  - dev: nights with sessions summing to exactly 0.0 (MANIFEST): 4
- (e) dev: gotobi_day sums to 529 per ticker (5706 529, 5711 529, 5713 529): True
  - dev: dates with an empty xau_ret: 0 of 1708
- (e) sealed: y_1306_oc, ao_1306_gap_raw, ao_1306_gap_adj finite on every row: True
- (e) sealed: usdjpy_us_ret == 0.0 wherever us_n_sessions == 0: True
- (e) sealed: usdjpy_us_ret finite wherever us_n_sessions > 0: True
  - sealed: nights with sessions summing to exactly 0.0 (MANIFEST): 2
- (e) sealed: gotobi_day sums to 319 per ticker (5706 319, 5711 319, 5713 319): True
  - sealed: dates with an empty xau_ret: 0 of 1019
  - the raw Japan 225 file hashes to the registry (read only for 2015-01-05): True
  - 2015-01-05 (first calendar day; no panel row): 08:59 JST price at most 5 minutes stale: True

  | Half-year | Panel dates | Panel fresh | P2-1 dates | P2-1 fresh | Expected (P2-1 minus 2015-01-05) | Equal |
  |---|---|---|---|---|---|---|
  | 2015-H1 | 120 | 44 | 121 | 45 | 120 / 44 | True |
  | 2015-H2 | 123 | 0 | 123 | 0 | 123 / 0 | True |
  | 2016-H1 | 122 | 0 | 122 | 0 | 122 / 0 | True |
  | 2016-H2 | 123 | 0 | 123 | 0 | 123 / 0 | True |
  | 2017-H1 | 123 | 0 | 123 | 0 | 123 / 0 | True |
  | 2017-H2 | 124 | 0 | 124 | 0 | 124 / 0 | True |
  | 2018-H1 | 121 | 53 | 121 | 53 | 121 / 53 | True |
  | 2018-H2 | 124 | 123 | 124 | 123 | 124 / 123 | True |
  | 2019-H1 | 117 | 116 | 117 | 116 | 117 / 116 | True |
  | 2019-H2 | 124 | 121 | 124 | 121 | 124 / 121 | True |
  | 2020-H1 | 119 | 118 | 119 | 118 | 119 / 118 | True |
  | 2020-H2 | 123 | 121 | 123 | 121 | 123 / 121 | True |
  | 2021-H1 | 121 | 121 | 121 | 121 | 121 / 121 | True |
  | 2021-H2 | 124 | 121 | 124 | 121 | 124 / 121 | True |
  | 2022-H1 | 120 | 119 | 120 | 119 | 120 / 119 | True |
  | 2022-H2 | 124 | 123 | 124 | 123 | 124 / 123 | True |
  | 2023-H1 | 122 | 122 | 122 | 122 | 122 / 122 | True |
  | 2023-H2 | 124 | 122 | 124 | 122 | 124 / 122 | True |
  | 2024-H1 | 120 | 119 | 120 | 119 | 120 / 119 | True |
  | 2024-H2 | 125 | 123 | 125 | 123 | 125 / 123 | True |
  | 2025-H1 | 119 | 118 | 119 | 118 | 119 / 118 | True |
  | 2025-H2 | 124 | 123 | 124 | 123 | 124 / 123 | True |
  | 2026-H1 | 41 | 41 | 41 | 41 | 41 / 41 | True |

- (e) Japan 225 fresh-date counts equal P2-1's on the same dates, every half-year (dev and 2022+): True
- (e) every half-year of P2-1 appears in the panels: True

## (f), (g) build assertions
- (f) the frozen build's own assertions passed (it ran inside the build and exited 0): True
- (g) every new build-time assertion passed (build exit code 0; 72 assertions recorded): True

**P2-4 ACCEPTED: True**
