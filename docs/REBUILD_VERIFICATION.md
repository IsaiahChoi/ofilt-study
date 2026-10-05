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

## D2: P22–P28 (verified at the D2 checkpoint)

Every structural claim in P22–P28 holds in the rebuilt repo (`tests/test_docs_d2.py`, 7 tests, plus the tests cited). P28's quoted numbers meet the **rebuilt** Stage C. Three P28 numbers are reproduced exactly and are asserted. The others differ and are listed below for Isaiah; they are not asserted, and the adopted text is not edited.

| Entry | Claim | Evidence | Result |
|---|---|---|---|
| P22 | Huber c = 1.345, fixed scale 1.4826 × MAD; → OLS-DK as c → ∞ (1e-12) | spec `robustness.huber`; `inference.fit_huber`; `test_inference_b2` | ✓ |
| P22 | winsorised FX at 0.5% / 99.5%, values fixed in the spec (usdjpy [−1.6482588843e-02, 1.4399911615e-02], eurusd [−1.6324806371e-02, 1.5438152188e-02]) | spec `robustness.winsorize_fx` | ✓ |
| P22 | influence curve by date, k = 0…20, exact date-deletion (brute force 1e-12); named crisis windows removed | spec `robustness.influence_curve`; `inference.influence_curve`; `test_inference_b2`; no crisis window in `robustness` | ✓ |
| P23 | TOST at α = 0.05; SESOI `PENDING_COSTS`; viability decided in Pass 4; `Spec.sesoi()` raises `SpecPendingError` | spec `equivalence`; raises | ✓ |
| P24 | f = b/δ_cc with δ_cc = δ_gap + b (1e-12); one stacked fit (`fit_joint`); delta method and Fieller; status mentions 2022 | spec `fraction_unpriced`; `test_inference_b3` | ✓ |
| P25 | four Holm members with AM-01 main effects; highrv threshold 1.2950114214e-08 | `inference.SECONDARY_TERMS` (four); spec family strings; `rv_per_bar_dev_median` == `Spec.rv_per_bar_dev_median()`. The spec block also holds the threshold key, which is a parameter, not a member. | ✓ |
| P26 | ladder M0, M1, M2, M3, M4, M5, M7 (M6 dropped); M2 = controls + EUR/USD, M3 = M2 + usdjpy_ret; M5 α multipliers 1e-4…1; M3 in-fold == pooled_ols (1e-12); M4 18 coefficients | spec `forecast.models`; model features; `ridge.ALPHA_MULTS`; `test_models_c2` | ✓ |
| P26 | comparisons (primary CW M3/M2 one-sided; CW M4/M3, M5/M3, M7/M1; DM M7/M1 two-sided, positive favours M7); importance spec; test aggregation | `fctests.spec_comparisons`; spec; `test_fctests_c5` (aggregation == hand computation) | ✓ |
| P27 | expanding, pooled, refit every 21, scaling in fold; 500 **eligible** training dates; training rows exclude `excl_inference`; evaluation exclusions; one sample per call; firewall | spec `forecast`; `test_forecast_c1`; `test_fctests_c5` (pairing refuses anything else) | ✓ |
| P27 | M7: early_stopping=False, lr 0.03, min_samples_leaf 100, l2 1.0; grid {2, 3} × {50, 100, 200, 400}; 20 PRE_OPEN sources; tuned on the last 250 training dates | `gbm.FIXED`, `gbm.GRID`; `test_models_c4` | ✓ |
| P27 | registry line: run id, UTC, git commit, spec and data hashes, models, grids, per-fold chosen hyperparameters, output path | `registry.KEYS` (superset), `FOLD_KEYS`; `test_importance_registry_c6` | ✓ (see difference 6) |
| P28 | slow tier `OFILT_SLOW=1`, `reports/C7_mc.json` + `C7_h1_same_dgp.json`, bands re-asserted, staleness by code hash; bands [2%, 9%] and ≥ 80% | `tools/c7_mc.py`; `test_validation_c7` | ✓ (see difference 7) |
| P28 | CW power b = 0.4: 100% [98.1%, 100%]; b = 0.25: 89.5% [84.5%, 93.0%]; same-panel H1 two-sided 87.5% | rebuilt report: 200/200, 179/200, 175/200 | ✓ exact |
| P28 | look-ahead bit-identical (M1–M5; M7 with M1), block-level leak caught | `test_validation_c7` (+ mutation check, C7 entry) | ✓ |
| P28 | importance: planted feature first, noise near 0 | `test_importance_registry_c6` | ✓ qualitative (P28 quotes no number) |

**Differences (flagged; no decision depends on them):**

1. **P28, CW size:** quoted 2.67% (8/300, [1.36%, 5.17%]); rebuilt **3.00%** (9/300, [1.59%, 5.60%]). One rejection apart, inside both intervals and the band. Flag 12's reading (CW conservative) holds.
2. **P28, same-panel H1 one-sided:** 94.0% vs **93.5%** (188 vs 187 of 200).
3. **P28, agreement:** CW rejects in 170 of 175 H1-significant runs vs **175 of 175** in the rebuild (4 CW-only, 0 H1-only).
4. **P28, PT size:** 4.6% vs **4.3%** one-sided (4.5% two-sided); P28 does not state sidedness, length or marginals.
5. **P28, M7 on pure noise:** mean OOS R² −0.011 vs **−0.0064** (C4). The planted-signal check holds (+0.364).
6. **P27, registry path:** "every call appends … to `RUN_REGISTRY.jsonl`". In the rebuild, real-provenance calls append there; synthetic calls go to a registry in the temp directory (Flag 15d). The handoff records the committed registry as empty after a Pass 1 that ran many synthetic forecasts, which this reproduces. The rebuilt line also has extra fields (git_dirty, provenance, target, seed, importance).
7. **P28, slow tier operation:** "run detached". The rebuild runs it as resumable, chunk-invariant detached chunks, because background processes do not survive the end of a turn in this environment. It has 2 slow tests where the original had 3.
8. **P26, training-window base rate:** implemented through a new fold-log field `train_up`. Its definition is a rebuild choice (Flag 14d, e).

The data-generating process behind P28's numbers is not recorded, so exact equality was not expected.

## D3: P29–P35 (verified at the D3 checkpoint)

Every machine-checkable claim in P29–P35 holds (`tests/test_docs_d3.py`, 6 tests, plus the tests cited). The P30–P31 numbers come from the committed B7 pilot and B7b preview reports, which predate the C3 checkpoint, so the rebuild did not regenerate them; the verification checks that the adopted text quotes them correctly. P32 and most of P34–P35 are claim wording and plans, with nothing in the repo to test yet.

| Entry | Claim | Evidence | Result |
|---|---|---|---|
| P29 | tag gates: synthetic passes; dev_real needs `spec-dev-v1`; confirm_real needs both tags; missing or unknown refused; attrs and kwarg must agree; neither tag exists in Pass 1 | `blind.require_unblinded` on a toy frame; `git tag`; `test_blind` | ✓ |
| P29 | `io.load_confirm` gated by `prereg-v1`, logs attempts; `_guards_fallback.py` fails closed (Flag 5) | file present; `test_io`, `test_blind` | ✓ |
| P29 | sealed blind fit: conditions (a)–(e), AST check that the coefficients never leave local scope | `sim._sealed_blind_fit`; `test_sim_b5` (the real-data part is opt-in and skipped) | ✓ |
| P29 | opt-in `OFILT_RUN_SEALED=1`; `checkpoint.sh` unsets it | `checkpoint.sh` contains `env -u OFILT_RUN_SEALED` and never sets it | ✓ |
| P29 | `BLIND_FIT_LOG`: 6 dev_real lines, all on `panel_dev.csv`; lines 1–3 from `test_sim_b5`, 4–5 from `report_B7.py`, 6 from `report_B7b.py` | parsed: 6 lines, provenance, panel hash == spec dev hash, caller fields | ✓ |
| P29 | Stage C synthetic only | rebuilt C4–C7 attestations in `PASS1_STATUS.md` | ✓ |
| P30 | B7b preview at T = 1013, lag 6: H1 size 6.04% [5.41%, 6.73%]; H3 5.92%; pooled coverage 93.91%, SE/sd 0.960, bias ≈ 0; power 22.5 / 78.2 / 98.5%; MDE80 0.257; no flag | `reports/B7b_size_preview.json`: 302/5000, 296/5000, 225 / 782 / 985 of 1000, probit MDE 0.2568, flags [] | ✓ |
| P30 | CW power 89.5% at b = 0.25 (synthetic) | rebuilt C7: 179/200 | ✓ exact |
| P31 | SE/sd 0.954 at T = 983 (pooled over 2,000 sims); 0.960 at T = 1013 | `reports/B_sim_pilot.json` four 500-rep cells pooled: 0.9539, coverage 93.95%; B7b pooled 0.9604 | ✓ |
| P31 | if the true size is 6.04%, P(5000-rep rate > 6.5%) = 0.086; at 6.73%, 0.742 | recomputed independently: 0.086 and 0.742 under the normal approximation (the exact binomial gives 0.083 and 0.731) | ✓ |
| P33 | closed robustness list: Huber, winsorised FX, influence curve + 10 rows, in the stated order; the post-2024-11-05 row not yet in `inference.py` | spec `robustness`; `inference.py` has no such term | ✓ |
| P34 | sealed panel hash `9c18a6c1…` in the spec until the Pass 2 rebuild; CONTEMPORANEOUS empty; calendar 1,019 / 1013 | spec; `schema` (D1); `calendar` (D1) | ✓ |
| P35 | T3 needs `walk_forward` on DevCalibrator draws with target `y_sim` | `walk_forward` has `target=`; `sim.DevCalibrator` exists | ✓ (capability only) |
| P32; P34 items 1–8; P35 T1–T7 | claim tiers, Pass 2 pulls, Pass 4 tasks | plans and wording | text only, not checkable in Pass 1 |

**Differences:** none new. Two D3 sentences restate P28 numbers that the rebuild reproduces differently (see D2):
- P30: "H1 and CW agree in about 97% of H1-significant runs". This is P28's 170/175; the rebuild has 175/175 (D2 difference 3).
- P31: "CW is conservative (2.67% …)". The rebuild has 3.00%, still conservative (D2 difference 1).

## D3b: P36

Not yet verified (next item).

## D4–D6: README, PLAN, DATA_DICTIONARY, setup docs

Not yet started.
