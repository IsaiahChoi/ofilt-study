# P2-5 resolutions

Written on 2026-10-05 (supervisor message after the P2-5 report, item 1b). It records how the 2.3 STOP was
resolved. It rewrites no committed report: `tools/p2_5_staleness.py` and `reports/P2_5_dev_checks.md` stay as
the run-time record and are not rerun.

## The 2.3 STOP (check 2.3, 1306 evidence for P18; D8)

As recorded at run time in `reports/P2_5_dev_checks.md`:

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

## Cause and resolution (Isaiah, 2026-10-05, on the supervisor's recommendation)

The supervisor's reference table was wrong, not the panel.
- Its 1306 column for 2017 and 2019–2021 was built from 2-decimal simple percentages (÷10 yield minus the ex-day
  open drop, from DATA_PROVENANCE §4.4). Its 2016 and 2018 values match no single definition.
- The panel's `ao_1306_gap_adj` equals the independent recomputation from the raw sheet to 1e-12 (diagnostic 2 below).

**Corrected table** (log gaps, %; 1306 / TOPIX):

| Ex-date | 1306 adjusted | TOPIX |
|---|---|---|
| 2015-07-08 | −0.30 | −0.41 |
| 2016-07-06 | −1.64 | −1.55 |
| 2017-07-06 | 0.00 | −0.04 |
| 2018-07-06 | +0.78 | +0.55 |
| 2019-07-08 | −0.17 | −0.26 |
| 2020-07-09 | −0.13 | −0.09 |
| 2021-07-08 | −0.22 | −0.15 |

The largest difference is 0.23 pp. D8's conclusion (÷10 holds every year) is unchanged.

**The SUPERVISOR reference values in `tools/p2_5_staleness.py` are superseded by this file.** That script and
`reports/P2_5_dev_checks.md` stay as the run-time record and are not rerun.

## Diagnostic 1: log gaps vs simple returns (`tools/p2_5_diag_23_simple_vs_log.py`; gap-only, dev)

Output, verbatim (`/tmp/p2_0/p2_5_23_diag.out`; a rerun of the saved script reproduced it byte for byte):

```
panel_dev.csv hashes to MANIFEST: True
Diagnostic (gap-only, dev): log gaps (as stored) and simple returns exp(g)-1, in % to 2 decimals
| Ex-date | 1306 log | 1306 simple | TOPIX log | TOPIX simple | supervisor (1306 / TOPIX) | 1306 simple = sup | TOPIX log = sup |
| 2015-07-08 | -0.30 | -0.30 | -0.41 | -0.41 | -0.30 / -0.41 | True | True |
| 2016-07-06 | -1.64 | -1.62 | -1.55 | -1.54 | -1.63 / -1.55 | False | True |
| 2017-07-06 | +0.00 | +0.00 | -0.04 | -0.04 | +0.00 / -0.04 | True | True |
| 2018-07-06 | +0.78 | +0.79 | +0.55 | +0.55 | +0.79 / +0.55 | True | True |
| 2019-07-08 | -0.17 | -0.17 | -0.26 | -0.26 | -0.16 / -0.26 | False | True |
| 2020-07-09 | -0.13 | -0.13 | -0.09 | -0.09 | -0.13 / -0.09 | True | True |
| 2021-07-08 | -0.22 | -0.22 | -0.15 | -0.15 | -0.21 / -0.15 | False | True |
1306 simple returns reproduce the supervisor's 1306 column on all 7 dates: False
TOPIX log gaps reproduce the supervisor's TOPIX column on all 7 dates: True
largest |1306 simple - TOPIX log| at 2 decimals: 0.24 pp
```

## Diagnostic 2: independent recomputation from the raw 1306 sheet (`tools/p2_5_diag_23_from_raw.py`; hedge-only and gap-only, dev)

Output, verbatim (`/tmp/p2_0/p2_5_23_raw.out`; a rerun of the saved script reproduced it byte for byte):

```
newbloombergdata_fixed.xlsx hashes to PASS2_INPUTS.json: True
panel_dev.csv hashes to MANIFEST: True
| Ex-date | from raw: ln(open/(prev close - D)) in % | panel ao_1306_gap_adj in % | equal (to 1e-12) |
| 2015-07-08 | -0.3004 | -0.3004 | True |
| 2016-07-06 | -1.6359 | -1.6359 | True |
| 2017-07-06 | +0.0000 | +0.0000 | True |
| 2018-07-06 | +0.7843 | +0.7843 | True |
| 2019-07-08 | -0.1655 | -0.1655 | True |
| 2020-07-09 | -0.1309 | -0.1309 | True |
| 2021-07-08 | -0.2201 | -0.2201 | True |
panel equals the independent recomputation on all 7 ex-dates: True
```

## Blinding

Gap columns and 1306 hedge prices and distributions only (dev). No target and no predictor column was read.
