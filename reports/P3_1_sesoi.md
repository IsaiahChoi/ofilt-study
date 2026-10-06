# P3-1: the SESOI (DQ2; dev only)

## (a) Hash check, sample and regressors

- Dev panel SHA-256 `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68`: equal to the spec's dev-panel hash (AM-04) and to `docs/PASS2_INPUTS.json`, checked before the file was read.
- Step 1 (the P3-0b Part A rule, imported from `tools/p3_0b_preflight.py`): kept rows 4192, T_source 1439; `reports/P3_0b_preflight.md` says 4192 and 1439. Gate: True.
- Step 2: the primary design's regressors, from `spec.fx_block`, `spec.controls` and `spec.h1_parameter` as `ofilt/drift/inference.py:90` reads them, named as at `inference.py:106-113`: ['fe[5706]', 'fe[5711]', 'fe[5713]', 'usdjpy_ret', 'eurusd_ret', 'spy_oc:5706', 'spy_oc:5711', 'spy_oc:5713', 'copx_oc:5706', 'copx_oc:5711', 'copx_oc:5713']. The partialling set (the design minus `usdjpy_ret`): ['fe[5706]', 'fe[5711]', 'fe[5713]', 'eurusd_ret', 'spy_oc:5706', 'spy_oc:5711', 'spy_oc:5713', 'copx_oc:5706', 'copx_oc:5711', 'copx_oc:5713']. Equals {ticker fixed effects, eurusd_ret, ticker-specific spy_oc and copx_oc}: True.

## (b) Conformity of all dev opens and closes with the dev tick tables (traded price = stored / f)

A price conforms if it is an integer multiple of its dev-table tick at its traded price (|p/t - round(p/t)| < 1e-06); 'Above bound' counts traded prices above the table's last bound.

| Ticker | Year | Period | Prices | Conforming share | Above bound |
|---|---|---|---|---|---|
| 5706 | 2015 | before 2017-09-27 | 486 | 1 | 0 |
| 5706 | 2016 | before 2017-09-27 | 490 | 1 | 0 |
| 5706 | 2017 | before 2017-09-27 | 364 | 1 | 0 |
| 5706 | 2017 | from 2017-09-27 | 130 | 1 | 0 |
| 5706 | 2018 | from 2017-09-27 | 490 | 1 | 0 |
| 5706 | 2019 | from 2017-09-27 | 482 | 1 | 0 |
| 5706 | 2020 | from 2017-09-27 | 484 | 1 | 0 |
| 5706 | 2021 | from 2017-09-27 | 490 | 1 | 0 |
| 5711 | 2015 | before 2016-09-28 | 486 | 1 | 0 |
| 5711 | 2016 | before 2016-09-28 | 362 | 1 | 0 |
| 5711 | 2016 | from 2016-09-28 | 128 | 1 | 0 |
| 5711 | 2017 | from 2016-09-28 | 494 | 1 | 0 |
| 5711 | 2018 | from 2016-09-28 | 490 | 1 | 0 |
| 5711 | 2019 | from 2016-09-28 | 482 | 1 | 0 |
| 5711 | 2020 | from 2016-09-28 | 484 | 1 | 0 |
| 5711 | 2021 | from 2016-09-28 | 490 | 1 | 0 |
| 5713 | 2015 | before 2017-09-27 | 486 | 1 | 0 |
| 5713 | 2016 | before 2017-09-27 | 490 | 1 | 0 |
| 5713 | 2017 | before 2017-09-27 | 364 | 1 | 0 |
| 5713 | 2017 | from 2017-09-27 | 130 | 1 | 0 |
| 5713 | 2018 | from 2017-09-27 | 490 | 1 | 0 |
| 5713 | 2019 | from 2017-09-27 | 482 | 1 | 0 |
| 5713 | 2020 | from 2017-09-27 | 484 | 1 | 0 |
| 5713 | 2021 | from 2017-09-27 | 490 | 1 | 0 |

Gate (every share exactly 1, no price above a bound): True.

## (c) The denominator and the hedge ratio

- mean |e~| over the 4192 step 1 rows: **28.4288 bp** (D2.1; `numpy.linalg.lstsq`, 10 regressors, no global intercept)
- beta-bar over the same rows: **1.0333** (D2.2)
- Rows per ticker: 5706 1400, 5711 1390, 5713 1402

## (d) The miner execution cost per ticker (bp per side)

| Ticker | Rows for the primary x_m (outside Flag 4 windows) | Primary x_m | Share of sides with 1/2 tick > stated impact (primary table) | High: mean x_m over all kept rows |
|---|---|---|---|---|
| 5706 | 1002 | 2.0000 | 0.0000 | 16.9017 |
| 5711 | 1230 | 2.0000 | 0.0000 | 13.9102 |
| 5713 | 1402 | 2.0148 | 0.0770 | 9.4111 |

## (e) Round trips and the SESOI

RT = 2 (c_m + x_m) + beta 2 (c_h + x_h) + s per name-day; components are means over the step 1 rows (bp). SESOI = mean RT / mean |e~|.

| Case | Miner commission 2 c_m | Miner execution mean 2 x_m | Hedge leg beta-bar 2 (c_h + x_h) | Short s | Mean RT | SESOI |
|---|---|---|---|---|---|---|
| primary | 8.6000 | 4.0099 | 11.9862 | 0.0000 | 24.5961 | **0.8652** |
| low | 0.0000 | 1.0000 | 1.0333 | 0.0000 | 2.0333 | **0.07152** |
| high | 16.0000 | 26.8091 | 33.4787 | 1.0000 | 77.2878 | **2.719** |

## (f) `docs/P3_COST_INPUTS.json`

```json
{
  "decided": "Isaiah, 2026-10-06; PASS3_STATUS Decision log (P3-1)",
  "notional_jpy": {
    "primary": 10000000,
    "low": 1000000,
    "high": 100000000
  },
  "commission_miners_bp": {
    "primary": 4.3,
    "low": 0,
    "high": 8
  },
  "commission_1306_bp": {
    "primary": 4.3,
    "low": 0,
    "high": 8
  },
  "impact_miners_bp": {
    "primary": 2,
    "low": 0.5,
    "high": 8
  },
  "impact_1306_bp": {
    "primary": 1.5,
    "low": 0.5,
    "high": 4
  },
  "short_cost_per_day_bp": {
    "primary": 0,
    "low": 0,
    "high": 1
  },
  "half_tick_1306_bp": {
    "primary": 1.25,
    "low": null,
    "high": 4.2
  },
  "price_factor": {
    "_about": "stored price = traded price x f; f parsed with fractions.Fraction. Segments: each applies from 'start' (inclusive; null = from the start of the panel) until the next segment's start.",
    "5711": [
      {
        "start": null,
        "f": "10"
      },
      {
        "start": "2016-09-28",
        "f": "1"
      }
    ],
    "5713": [
      {
        "start": null,
        "f": "2"
      },
      {
        "start": "2017-09-27",
        "f": "1"
      }
    ],
    "5706": [
      {
        "start": null,
        "f": "1"
      },
      {
        "start": "2017-09-27",
        "f": "1/10"
      }
    ]
  },
  "tick_tables": {
    "_about": "traded yen; each row is [inclusive upper bound, tick]; a traded price above the last bound is refused",
    "standard": {
      "rows": [
        [
          3000,
          1
        ],
        [
          5000,
          5
        ],
        [
          30000,
          10
        ]
      ]
    },
    "topix100_phase2": {
      "in_force": "2014-07-22 to 2015-09-23",
      "rows": [
        [
          1000,
          0.1
        ],
        [
          5000,
          0.5
        ],
        [
          10000,
          1
        ]
      ]
    },
    "fine": {
      "in_force": "TOPIX100 from 2015-09-24; TOPIX500 from September 2023 at the latest",
      "rows": [
        [
          1000,
          0.1
        ],
        [
          3000,
          0.5
        ],
        [
          10000,
          1
        ],
        [
          30000,
          5
        ]
      ]
    }
  },
  "dev_table": {
    "_about": "the table in force during dev; segments as in price_factor",
    "5711": [
      {
        "start": null,
        "table": "standard"
      }
    ],
    "5706": [
      {
        "start": null,
        "table": "standard"
      }
    ],
    "5713": [
      {
        "start": null,
        "table": "topix100_phase2"
      },
      {
        "start": "2015-09-24",
        "table": "fine"
      }
    ]
  },
  "primary_table": {
    "5706": "fine",
    "5711": "fine",
    "5713": "fine"
  },
  "flag4_windows": {
    "_about": "kept rows dated before the date are inside the window",
    "5711": {
      "before": "2016-09-28"
    },
    "5706": {
      "before": "2017-09-27"
    }
  },
  "sources": [
    "JPX, tick sizes for TOPIX100 constituents, Phase III (effective 2015-09-24)",
    "JPX leaflet, sub-yen tick sizes for TOPIX100 stocks (from 2014-07-22)",
    "JPX market news of 2021-11-25 (the TOPIX100 table for ETFs from 2021-11-29)",
    "JPX market news of 2023-09-05 and later (narrow tick sizes applied to TOPIX500 constituents)",
    "docs/DATA_PROVENANCE.md lines 67 and 70 and docs/replacements/DATA_DICTIONARY.md line 116 (capital-change adjustment; 5706 on the post-split basis)",
    "Isaiah's cost note of 2026-10-06 (kept outside the repository and the Claude Project): IBKR Japan Tiered (Tier I 0.05%, Tier II 0.04%) plus TSE exchange and clearing fees (about 0.27 bp); SBI 'Zero Revolution' or Rakuten's zero course; IBKR Fixed (0.08%); JPX closing-auction shares and square-root-law evidence on TSE data; day-trade margin at SBI, Rakuten and Matsui (0% interest, 0% lending fee); standard margin at 1.10% a year and special short fees"
  ]
}
```
