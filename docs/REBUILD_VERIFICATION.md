# Rebuild verification of the adopted decision text (Stage D, rebuild)

`docs/DECISIONS_P14_onward.md` is the adopted text (P14–P36, ADOPTED by Isaiah 2026-10-01), restored **byte for byte** from the Claude Project copy (sha256 `3d13201636ad459ce0bb61fb5e29385c2a7531cf7daad848d1a970706ca02dd0`, pinned in `tests/test_docs_d1.py`). The rebuild does not edit it. Each Stage D item checks one part of it against the rebuilt repo. Where the repo agrees, the claim is marked ✓ with its evidence. Where it differs, the difference is listed here and in `PASS1_STATUS.md` (Deviations) for Isaiah, and the adopted text stays as it is.

Coverage, from the file's own header: D1 = P14–P21, D2 = P22–P28, D3 = P29–P35, D3b = P36. In-text references assign the README and PLAN changes to D4 (P16, P36) and the DATA_DICTIONARY wording to D5 (P20). D6, by elimination, is the setup docs.

## D1: P14–P21 (verified at the D1 checkpoint)

All machine-checkable claims in P14–P21 hold in the rebuilt repo. **No differences.** These entries describe Stages A–B, which survived in the C3 checkpoint unchanged, so agreement is expected. Each claim is checked by `tests/test_docs_d1.py` unless another test is named.

| Entry | Claim | Evidence | Result |
|---|---|---|---|
| P14 | ticker FE, no global intercept; FX block common [usdjpy_ret, eurusd_ret]; controls ticker-specific [spy_oc, copx_oc]; `h1_parameter = usdjpy_ret`; two-sided, α = 0.05 | spec `model`, `inference` | ✓ |
| P15 | `h3_parameter = eurusd_ret` | spec | ✓ |
| P16 | `ao_` columns never features; `schema.AT_OPEN` refuses them and documents the reason | `select_features` raises `FeatureNotAllowedError` for each; schema reason text | ✓ |
| P16 | B6 noisy auction: ρ = 1, pre-open −0.003, auction-conditional 0.162 (kδ = 0.167), surprise == pre-open (1e-16); ρ = 0.7, 0.154 / 0.269 (0.15 / 0.267) | `test_b6_identities` (n = 2,000,000; passes); B6 record in `PASS1_STATUS.md` quotes the same numbers | ✓ |
| P17 | β: expanding, min_periods 250, lag 1, non-excluded rows, continued across samples; `beta_rolling_250` robustness row; `targets.past_beta` | spec `target.beta`, `robustness.others` | ✓ |
| P17 | A7, own rows: 5711 rolling-500 11,659.7 [n = 1,140] vs expanding 11,662.6 [n = 1,168], 0.025% | `reports/A_hedge_efficiency.md` (parsed) | ✓ |
| P17 | A7, common rows: expanding lowest for all three (5711: 11,639.9 vs 11,659.7) | same report: 24,030.2 / 11,639.9 / 17,983.9 vs next-best 24,073.9 / 11,659.7 / 17,988.3 | ✓ |
| P17 | look-ahead tests: A8 for β and targets, C7 for predictions | `test_lookahead` (A8); `test_validation_c7.TestForecastLookAhead` (rebuilt C7) | ✓ |
| P18 | `hedge_oc_column = y_topix_oc` (placeholder); `HEDGE_GAP_FOR` raises for any other hedge; `target.secondary = raw_oc` | spec; `targets.HEDGE_GAP_FOR == {y_topix_oc: ao_topix_gap}`; `add_targets` check | ✓ |
| P18 | decomposition identity exact on a balanced panel with constant β (7e-16) | `test_inference_b3` (passes) | ✓ |
| P19 | `require_nonmissing = [usdjpy_ret, eurusd_ret, spy_oc, copx_oc, beta]`; EWJ and FCX out of the design; robustness rows `ewj_yen_denominated_REQUIRES_PASS2`, `copx_to_fcx`, `exclude_boj_day`, `exclude_sq_major`; `fx_x_longwindow` in the secondary family; no lags or calendar dummies in the design | spec `sample`, `model`, `robustness`, `secondary_family_holm` | ✓ |
| P19 | Isaiah's autocorrelation figures (≤ \|0.075\| at lags 1–5) | not recomputable in Pass 1 (blinding), as the entry itself states | not checked, by design |
| P20 | 41 panel columns, each in exactly one group: 2 / 20 / 2 / 1 / 1 / 3 / 2 / 10 / 0 | `schema` groups pairwise disjoint; union == the dev panel header (header read only) | ✓ |
| P20 | six derived features; only non-PRE_OPEN derived source `usdjpy_bars`; synthetic `noise_N01`; `open`, `close`, `prev_close`, `audit_flag` forbidden; unknown columns refused | `schema` constants; `select_features` refuses each (unknown: `FeatureNotAllowedError`, "unknown column") | ✓ |
| P21 | DK, Bartlett, lag ⌊4(T/100)^{2/9}⌋ = 7 at T = 1708 and 6 at T = 1013; no small-sample correction; normal reference | `dk_lag`; spec `inference` | ✓ |
| P21 | AM-02 size rule (5000 sims at T_conf, [3.5%, 6.5%], else stationary block bootstrap with mean block 5, decided before the tag) | `spec.SIZE_RULE` == spec `inference.size_rule` | ✓ |
| P21 | T_conf = 1013 = 1,019 confirmation trading days − 6 all-excluded dates; each ticker loses 34 rows | `calendar.N_CONF_DAYS`, `T_CONF`, `len(confirmation_calendar())`; `test_calendar` (34 rows per ticker, T = 1013; passes) | ✓ |

## D2: P22–P28

Not yet verified (next item). This is where the rebuilt Stage C numbers meet the quoted ones; those differences are already recorded in `PASS1_STATUS.md` Deviations (C4–C7).

## D3, D3b: P29–P36

Not yet verified.

## D4–D6: README, PLAN, DATA_DICTIONARY, setup docs

Not yet started.
