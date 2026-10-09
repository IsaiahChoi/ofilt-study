# P4-1 audit: every pre-registered output and decision rule (P4Q4; read-only, HEAD 795385fa709f4cf6c8e7f441d879cc1c1b89e46b)

The builder's reading of the texts and the code at HEAD. It answers no open question and recommends nothing. Where a text leaves a detail open, the detail is a gap (section 2), with the options the texts permit.

**Abbreviations** (paths at HEAD; "L" = line): spec = `spec/analysis_spec_dev_v1.yaml`; AM = `spec/SPEC_AMENDMENTS.md`; PLAN = `docs/replacements/PLAN.md`; D14, D37, D58, D71 = `docs/DECISIONS_P14_onward.md`, `docs/DECISIONS_P37_onward.md`, `docs/DECISIONS_P58_onward.md`, `docs/DECISIONS_P71_onward.md`; P3S = `PASS3_STATUS.md`; DQ6d = `docs/P3_DQ6_drafts.md`; DD = `docs/replacements/DATA_DICTIONARY.md`; PR4 = the standing prompt, `files/pass4/PASS4_BUILDER_PROMPT_2026-10-08.md`.

**Status**, one per row:
- `implemented`: existing public functions, called with their existing arguments, compute every number the row reports, or apply the rule.
- `building blocks only`: part of the row needs new code (a design column, a re-arranged design, a test or decision helper, or fits assembled on matched rows), which P4Q2 places in new files.
- `none`: no code computes or applies it at HEAD. A rule applied once in Pass 3, whose outcome is now fixed in the spec or the records, has code entry `none` and status `none`; its On dev cell says so.

**(C7)** marks a file in `tools/c7_mc.py`'s `CODE_FILES` (L42-43): `ofilt/drift/inference.py`, `sim.py`, `forecast.py`, `fctests.py`, `models/linear.py`, and `tools/c7_mc.py`.

**Dev facts used below** (from the records; nothing was computed for this audit): the AM-03 estimation sample on dev has 4,192 rows on 1,439 dates, 2016-01-26 to 2021-12-30 (D71 L70). The DK lag is 7 at 1,439 dates (P3S L1205) and 6 at 1,013 (D14 L109). Every dev computation that relates a predictor to a target belongs to the one sanctioned dev run (PR4 P4Q1, P4Q6).

## 1. Table of outputs and rules

| ID | Output or rule | Defining text | Code entry point | Status | On dev | Open details |
|---|---|---|---|---|---|---|
| O1 | H1: b̂ on `usdjpy_ret` in the pooled design (ticker FE, no global intercept; common FX block usdjpy_ret, eurusd_ret; ticker-specific spy_oc, copx_oc), with its DK SE, z, two-sided p and 95% CI | spec L18-32; PLAN §1.2 (L69-94), §1.3 (L98), §3.4 (L213-217); D14 P14 (L21-32), P21 (L108-114) | `ofilt/drift/inference.py:build_design:71` (C7); `ofilt/drift/inference.py:fit_dk:218` (C7); `ofilt/drift/inference.py:param:214` (C7) | implemented | Computable: the dev b̂ on the AM-03 sample (4,192 rows, 1,439 dates), DK lag 7. It is the dev first look's FX–target result (D14 P36 step 5 and Note 1, L375, L380), computed only in the dev run. | - |
| R1 | H1 target: abn_oc = y_oc − β(i,t−1)·y_1306_oc (AM-03). β per ticker: the past-only expanding OLS slope of y_oc on y_1306_oc, min_periods 250, lag 1 day, on non-excluded rows, continued across samples. The P18 fallback did not fire | spec L12-17; AM-03 (AM L51-62); PLAN §1.2 (L73-78), §3.1 (L183-191); D14 P17 (L52-64), P18 (L66-74) | `ofilt/drift/targets.py:add_targets:104`; `ofilt/drift/targets.py:past_beta:62` | implemented | Computable: the first dev β is on 2016-01-26 (D71 L70). At the confirmation, β continues from dev, so it is computed on dev and confirmation rows together (targets.py L9-10). `io.load_confirm` returns the sealed panel alone (io.py L156-169), and no code joins the two. | - |
| R2 | H1 estimation sample: rows with earn_flag or news_flag (days D and D+1, P07) dropped; usdjpy_ret, eurusd_ret, spy_oc, copx_oc, beta and the target non-missing and finite. At the confirmation, T_conf = 1,013 dates (6 dates have all three tickers excluded) | spec L8-11, L33; PLAN §2.1 (L150), §3.2 (L193-201); D14 P19 (L83), P21 (L111) | `ofilt/drift/inference.py:build_design:71` (C7) | implemented | Computable: 4,192 rows on 1,439 dates (D71 L70). | - |
| R3 | DK lag rule: Bartlett kernel, L = floor(4(T/100)^(2/9)) with T = unique dates of the estimation sample; no small-sample correction (6 at T_conf) | spec L26-29; PLAN §3.4 (L215-217); D14 P21 (L109) | `ofilt/drift/spec.py:dk_lag:86`; `ofilt/drift/inference.py:driscoll_kraay:178` (C7) | implemented | Computable: 7 at 1,439 dates (P3S L1205). | - |
| R4 | H1 decision: b ≠ 0, two-sided at α = 0.05 against the normal reference (DK-normal) | spec L30-32; PLAN §1.3 (L98); D14 P14 (L27); P3S D3.4 (L160-163); D71 P79 (L161) | `ofilt/drift/inference.py:contrast:203` (C7) | implemented | Computable; exploratory on dev (D14 P36 step 5, L375). | - |
| R5 | The size-rule outcome (AM-02, applied by D3.4): DK-normal rejected 291 of 5,000 at b = 0 (5.82%), inside [3.5%, 6.5%]. DK-normal is kept, the bootstrap branch is not taken, and AM-08 is unused | spec L33; AM-02 (AM L33-49); PLAN §3.4 (L219-226); P3S D3.4 (L161); D71 P79 (L161) | none | none | Not recomputed: applied at P3-5 (D71 L160-161). It fixes R4. | - |
| O2 | H3: â₂ on `eurusd_ret` in the same fit, with its DK SE, two-sided at 5%. It is conditional on EUR/USD as the dollar proxy and COPX in the design | spec L23; PLAN §1.3 (L106); D14 P15 (L34-41); P3S D3.5 (L164) | `ofilt/drift/inference.py:fit_dk:218` (C7); `ofilt/drift/inference.py:param:214` (C7) | implemented | Computable (the same fit as O1). | G9 |
| O3 | Secondary family term `fx_x_longwindow`: long_window + usdjpy_ret × long_window, long_window = 1[window_hours > 18]; the interaction is tested | spec L43-44; AM-01 (AM L8-31); PLAN §1.3 (L110-117); D14 P25 (L150-161) | `ofilt/drift/inference.py:secondary_family_tests:492` (C7) | implemented | Computable. | - |
| O4 | Secondary family term `fx_x_jumpshare`: jumpshare + usdjpy_ret × jumpshare, jumpshare = clip((usdjpy_rv − usdjpy_bv)/usdjpy_rv, 0, 1); the interaction is tested | spec L45; AM-01 (AM L8-31); D14 P25 (L156) | `ofilt/drift/inference.py:secondary_family_tests:492` (C7) | implemented | Computable. | - |
| O5 | Secondary family term `fx_x_highrv`: highrv + usdjpy_ret × highrv, highrv = 1[usdjpy_rv/usdjpy_bars > 1.2950114214e-08] (the dev median); the interaction is tested | spec L46, L48; AM-01 (AM L8-31); D14 P25 (L157) | `ofilt/drift/inference.py:secondary_family_tests:492` (C7) | implemented | Computable. The build fails closed if usdjpy_bars ≤ 0 on a kept row (inference.py L121-124). | - |
| O6 | Secondary family term `fx_asymmetry`: max(e, 0) and min(e, 0) replace usdjpy_ret; equal slopes tested (the contrast e_pos − e_neg) | spec L47; D14 P25 (L158); inference.py L40-43 | `ofilt/drift/inference.py:secondary_family_tests:492` (C7) | implemented | Computable. | - |
| R6 | Holm adjustment across the four secondary-family tests (two-sided DK-normal p-values) | spec L43; PLAN §1.3 (L110); D14 P25 (L151); P3S D3.5 (L164) | `ofilt/drift/inference.py:holm:479` (C7); `ofilt/drift/inference.py:secondary_family_tests:492` (C7) | implemented | Computable. | - |
| O7 | Fraction unpriced f = b/δ_cc from one stacked fit of (abn_oc, cc_abn) on the same design, with a joint DK covariance; delta-method and Fieller intervals, and the Fieller set's kind (bounded, two rays or the whole real line) | spec L34-36; PLAN §1.3 (L119); D14 P24 (L140-148) | `ofilt/drift/inference.py:fit_joint:380` (C7); `ofilt/drift/inference.py:fraction_unpriced:431` (C7); `ofilt/drift/inference.py:fraction_from:405` (C7) | implemented | Computable on the dev sample as a whole. Neither of f's pre-registered periods (O8) lies in dev. | G1, G2 |
| O8 | f's periods: confirmatory for 2022 only; descriptive for 2023–2026 (prior exposure of gap quantities, PLAN §2.3) | spec L37; PLAN §1.3 (L119), §2.3 (L173-177); D14 P24 (L144), P32 (L298) | none | building blocks only | Empty by construction: dev ends 2021-12-30. | G1, G2 |
| O9 | Raw/abnormal decomposition: b_raw ≈ mean(β)·b_mkt + b_abn, with its approximation gap. b_mkt is the hedge open→close on the date-level design (intercept, FX block, controls with common slopes), time-series NW with the same lag rule | spec L16-17; PLAN §1.2 (L94); D14 P18 (L71) | `ofilt/drift/inference.py:decomposition:460` (C7); `ofilt/drift/inference.py:fit_market:438` (C7) | implemented | Computable. `fit_market` fails closed if a market column differs across tickers within a date (inference.py L448-449). | - |
| O10 | TOST at the primary SESOI 0.8652, α = 0.05: equivalence iff both one-sided p < α (the 90% CI inside ±SESOI), normal reference; viable under DK-normal (D2.6) | spec L49; AM-07 (AM L96-103); PLAN §1.3 (L121); D14 P23 (L131-138); P3S D2.6 (L139); D71 P79 (L163) | `ofilt/drift/inference.py:tost_result:347` (C7); `ofilt/drift/inference.py:tost:333` (C7) | implemented | Computable from the dev b̂ and its DK SE. | G11 |
| O11 | TOST at the low (0.07152) and high (2.719) SESOI, reported beside the primary | spec L49; AM-07 (AM L98); P3S D2.7 (L140); D71 carried item 6 (L210) | `ofilt/drift/inference.py:tost:333` (C7) | implemented | Computable. In the spec the two values appear only inside the viability string (spec L49); `Spec.sesoi` returns the primary value alone (spec.py L356-360). | G11 |
| O12 | Huber M-estimator: c = 1.345, fixed scale 1.4826 × MAD of the OLS residuals, IRLS, DK sandwich with the same kernel and lag | spec L39; PLAN §3.5 (L231); D14 P22 (L122) | `ofilt/drift/inference.py:fit_huber:249` (C7) | implemented | Computable. | - |
| O13 | FX winsorised at the dev 0.5%/99.5% quantiles (usdjpy [−1.6482588843e-02, 1.4399911615e-02]; eurusd [−1.6324806371e-02, 1.5438152188e-02]), then OLS-DK | spec L40; PLAN §3.5 (L232); D14 P22 (L123) | `ofilt/drift/calib.py:winsorise_fx:165`; `ofilt/drift/inference.py:build_design:71` (C7); `ofilt/drift/inference.py:fit_dk:218` (C7) | implemented | Computable. | - |
| O14 | Influence curve: b with its DK SE after deleting the k = 1…20 most influential dates of one fixed full-sample ranking (exact date-deletion change in b); n_dates and the DK lag recomputed for each k | spec L41; PLAN §3.5 (L233); D14 P22 (L124) | `ofilt/drift/inference.py:influence_curve:312` (C7); `ofilt/drift/inference.py:date_influence:289` (C7) | implemented | Computable (k = 0 is the primary). | - |
| O15 | `beta_rolling_250`: the target's β is a past-only rolling β in place of the expanding β | spec L42; PLAN §6 item 5 (L332); D14 P17 (L59), P33 (L315) | `ofilt/drift/targets.py:add_targets:104` (method "rolling", window 250); `ofilt/drift/inference.py:build_design:71` (C7); `ofilt/drift/inference.py:fit_dk:218` (C7) | implemented | Computable on the dev rows that have a rolling-250 β. | G3, G4 |
| O16 | `beta_rolling_500`: the past-only rolling β over the last 500 eligible rows (non-excluded, lag 1 day, continued across samples); rows with a finite rolling-500 β (every confirmation row) | AM-05 (AM L84); PLAN §6 item 5 (L332); D58 P65 (L212) | `ofilt/drift/targets.py:add_targets:104` (method "rolling", window 500); `ofilt/drift/inference.py:build_design:71` (C7); `ofilt/drift/inference.py:fit_dk:218` (C7) | implemented | Computable: on dev the rolling-500 β starts on 2017-02-16, and 3,570 of the 5,124 rows have one (D58 L212, L219). | - |
| O17 | `raw_target`: the raw open→close return (raw_oc = y_oc) as the target; also the secondary target, with the decomposition (O9) | spec L16, L42; PLAN §3.1 (L191), §6 item 6 (L333); D14 P18 (L71), P33 (L316) | `ofilt/drift/inference.py:build_design:71` (C7) (target "raw_oc"); `ofilt/drift/inference.py:fit_dk:218` (C7) | implemented | Computable. | G4 |
| O18 | `copx_to_fcx`: fcx_oc in place of copx_oc | spec L42; PLAN §6 item 4 (L331); D14 P19 (L79), P33 (L317) | none | building blocks only | Computable. `build_design` takes the spec's controls only (inference.py L90), so the swap re-arranges the columns of its output (PR4 P4Q2). Whether fcx_oc is missing on a primary row is a structural count (DD L38). | G4, G5 |
| O19 | `ewj_yen_denominated`: adds ewj_oc_jpy with ticker-specific slopes; rows: the primary rows with a finite ewj_oc_jpy; not a tier-(ii) check | AM-05 (AM L85); PLAN §6 item 10 (L337); D37 P49 (L214); D58 P63 (L174) | none | building blocks only | Computable: 3 dev nights are dropped (AM L85). ewj_oc_jpy is in PRE_OPEN_ROBUSTNESS, which `select_features` refuses (schema.py L52-54, L78). | - |
| O20 | `xau_control`: adds xau_ret with ticker-specific slopes; rows: all primary rows; no staleness filter | AM-05 (AM L86); PLAN §6 item 11 (L338); D37 P41 (L75) | none | building blocks only | Computable. xau_ret is in PRE_OPEN_ROBUSTNESS (refused by `select_features`). | G6 |
| O21 | `nikkei_proxy_p42`: adds n225_ret with ticker-specific slopes on the nights with n225_stale_start_min ≤ 5 and n225_stale_end_min ≤ 5 (a night with no Japan 225 bar is ineligible); b with and without n225_ret on those nights | AM-05 (AM L87); PLAN §6 item 12 (L339); D37 P42 (L84-86), P56 (L361); D58 P63 (L172-174) | none | building blocks only | Computable: 929 of the 1,708 dev nights are eligible. 40 of them fall in 2015-H1, before the first β (2016-01-26), and the rest from 2018-04-13 (D58 L172; DD L61). The staleness columns are PROVENANCE, read as a filter only (schema.py L44-47). | G8 |
| O22 | `mechanism_session_fx_gotobi` (not tradable): adds c_usdjpy_sess_ret and c_eurusd_sess_ret (common), gotobi_day (common) and usdjpy_ret × gotobi_day (common); rows: all primary rows. It reports b, the two session-FX coefficients and the interaction, with DK SEs; descriptive, outside every claim tier and the Holm family | AM-05 (AM L88); PLAN §6 item 13 (L340), L342; D37 P48 (L170-190) | none | building blocks only | Computable. The session-FX columns are CONTEMPORANEOUS and gotobi_day is PRE_OPEN_ROBUSTNESS, all refused by `select_features`. | G6 |
| O23 | `exclusion_d_plus_2`: TANSHIN and STANDALONE_NEWS days D, D+1 and D+2 excluded; β stays estimated under the primary exclusion (Flag 3) | spec L42; PLAN §6 item 1 (L328); D14 P33 (L319) | `ofilt/drift/targets.py:add_masks:156`; `ofilt/drift/inference.py:build_design:71` (C7) | implemented | Computable. excl_d2 needs events_firm.csv (targets.py L30, L163). `add_targets` estimates β under the primary flags (targets.py L116-120). | G4 |
| O24 | `exclude_audit_flag`: rows with audit_flag (outcome-identified audit candidates, D and D+1) also excluded | spec L42; PLAN §3.2 (L201), §6 item 2 (L329); D14 P33 (L320) | `ofilt/drift/inference.py:build_design:71` (C7) | implemented | Computable through `build_design`'s exclude list, which casts each flag with astype(bool) (inference.py L98). | G4 |
| O25 | `exclude_boj_day`: BoJ announcement days also excluded | spec L42; PLAN §6 item 8 (L335); D14 P19 (L80), P33 (L321) | `ofilt/drift/inference.py:build_design:71` (C7) | implemented | Computable. | G4 |
| O26 | `exclude_sq_major`: major SQ days (March, June, September, December) also excluded | spec L42; PLAN §6 item 8 (L335); D14 P19 (L80), P33 (L321); DD L43 | `ofilt/drift/inference.py:build_design:71` (C7) | implemented | Computable. | G4 |
| O27 | `post_2024_11_05_indicator_CONFIRMATION_ONLY`: the P14 design plus post and usdjpy_ret × post, with post = 1[date ≥ 2024-11-05]. b_pre is the usdjpy_ret coefficient; b_post = b_pre + the interaction coefficient, with its DK SE from the covariance of the two. Outside the Holm family | spec L42; PLAN §6 item 9 (L336); D14 P33 (L322, L325) | `ofilt/drift/inference.py:contrast:203` (C7) (b_post) | building blocks only | Not computable: post is identically 0 on dev (D14 L325), so the design is rank-deficient (inference.py L132-133). Not applicable by design on dev (PR4 L90); tested on synthetic data with a known break at 2024-11-05 (PR4 L89). | G4 |
| O28 | `per_ticker_slopes_holm` (H4, descriptive): b per stock | spec L42; PLAN §1.3 (L108), §6 item 7 (L334); D14 P33 (L323); P3S D3.5 (L164) | none | building blocks only | Computable. No per-ticker design exists: `build_design`'s FX block is common (inference.py L108-110). | G4, G7 |
| R7 | Holm adjustment across the three per-ticker tests | PLAN §1.3 (L108); D14 P33 (L323) | `ofilt/drift/inference.py:holm:479` (C7) | implemented | Computable once O28's p-values exist. | G7 |
| R8 | AM-05's reporting form: each AM-05 row reports b with and without its change on the same rows, next to the full-sample primary b, with the DK lag rule at T = that row's estimation dates (P56: on the same restricted rows) | AM L82; D37 P56 (L357-361) | `ofilt/drift/inference.py:subset_design:231` (C7); `ofilt/drift/inference.py:fit_dk:218` (C7) | building blocks only | Computable for O16 and O19 to O22. | G4 |
| O29 | M0: the zero forecast | spec L58; PLAN §4.1 (L245); D14 P26 (L168) | `ofilt/drift/models/linear.py:M0:37` (C7); `ofilt/drift/forecast.py:walk_forward:203` (C7) | implemented | Computable. Forecasts start after the 500th eligible training date (the β warm-up dates do not count; D14 P27 L197) and run to 2021-12-30. A dev_real call appends one line to RUN_REGISTRY.jsonl (registry.py L41-46; PR4 P4Q6). | G12, G13 |
| O30 | M1: the prevailing (training-fold) mean per ticker | spec L59; PLAN §4.1 (L246); D14 P26 (L169) | `ofilt/drift/models/linear.py:M1:47` (C7) | implemented | Computable. | G12, G13 |
| O31 | M2: ticker FE + ticker-specific spy_oc, copx_oc + eurusd_ret (the nested null for H1) | spec L60; PLAN §4.1 (L247); D14 P26 (L170, L177) | `ofilt/drift/models/linear.py:M2:77` (C7) | implemented | Computable. | G12, G13 |
| O32 | M3: M2 + usdjpy_ret (the primary design) | spec L61; PLAN §4.1 (L248); D14 P26 (L171) | `ofilt/drift/models/linear.py:M3:82` (C7) | implemented | Computable. | G12, G13 |
| O33 | M4: M3 + the AM-01 moderators and interactions + min(e, 0); the highrv threshold is the training fold's median (the expanding past median) | spec L62; AM-01 (AM L15); PLAN §4.1 (L249); D14 P26 (L172) | `ofilt/drift/models/linear.py:M4:108` (C7) | implemented | Computable. | G12, G13 |
| O34 | M5: ridge on the M4 design; FE unpenalised by in-fold within-ticker demeaning; α = n_train × {1e-4, 1e-3, 1e-2, 1e-1, 1}, tuned on the last 250 training dates | spec L63; PLAN §4.1 (L250); D14 P26 (L173) | `ofilt/drift/models/ridge.py:M5:34` | implemented | Computable. | G12, G13 |
| O35 | M7 (exploratory): HistGradientBoostingRegressor on the 20 PRE_OPEN features + a ticker one-hot + an N(0,1) noise column; run in its own walk_forward call with M1 | spec L64; PLAN §4.1 (L251); D14 P26 (L174), P27 (L200, L206-211) | `ofilt/drift/models/gbm.py:M7:55` | implemented | Computable. Its call's sample needs all 20 PRE_OPEN sources, and ewj_oc is NaN on 3 dev dates (D14 L200). | G12, G13 |
| R9 | Walk-forward protocol: expanding window; first forecast after 500 eligible training dates; refit every 21 dates; pooled; in-fold scaling; training rows exclude excl_inference; evaluation rows exclude earnings D, D+1 and news D+1; one sample per call; every call logged in the run registry | spec L9-10, L50-56; PLAN §3.2 (L197-199), §4.2 (L255-260); D14 P27 (L195-215) | `ofilt/drift/forecast.py:walk_forward:203` (C7); `ofilt/drift/forecast.py:fold_starts:101` (C7); `ofilt/drift/targets.py:add_masks:156`; `ofilt/drift/registry.py:record_run:93` | implemented | Computable. excl_forecast_eval needs events_firm.csv (targets.py L164-165). | G12, G13 |
| O36 | The primary forecast comparison: Clark–West, M3 against M2, one-sided; it rejects if the CW statistic exceeds c_CW,cal = 1.411608406163672 (strict) | spec L66; AM-09 (AM L105-112); PLAN §3.4 (L226), §4.3 (L266); D14 P26 (L183); D71 P79 (L162); DQ6d L314 | `ofilt/drift/fctests.py:clark_west:152` (C7) | building blocks only | Computable from the dev forecasts. c_CW,cal was calibrated on the last 1,013 dates of 2,452-date draws, with masks all False and lag 6 (P3S L173, L177). No code applies the critical value yet (DQ6d L314). | G12, G13 |
| O37 | Secondary comparison: Clark–West M4 against M3, one-sided, normal reference | spec L67; AM-09 (AM L107); D14 P26 (L184) | `ofilt/drift/fctests.py:run_comparisons:302` (C7); `ofilt/drift/fctests.py:clark_west:152` (C7) | implemented | Computable. | G12, G13 |
| O38 | Secondary comparison: Clark–West M5 against M3, one-sided, normal reference | spec L67; AM-09 (AM L107); D14 P26 (L184) | `ofilt/drift/fctests.py:run_comparisons:302` (C7); `ofilt/drift/fctests.py:clark_west:152` (C7) | implemented | Computable. | G12, G13 |
| O39 | Secondary comparison: Clark–West M7 against M1, one-sided, normal reference (M7's call) | spec L67; AM-09 (AM L107); D14 P26 (L184) | `ofilt/drift/fctests.py:run_comparisons:302` (C7); `ofilt/drift/fctests.py:clark_west:152` (C7) | implemented | Computable. | G12, G13 |
| O40 | Secondary comparison: Diebold–Mariano M7 against M1, two-sided, squared-error loss; positive favours M7 | spec L67; D14 P26 (L184, L190) | `ofilt/drift/fctests.py:diebold_mariano:168` (C7) | implemented | Computable. | G12, G13 |
| O41 | `report_all` item `oos_r2_vs_M0`: the OOS R² of every model against M0, pooled and per ticker | spec L68; PLAN §4.3 (L269); D14 P26 (L185) | `ofilt/drift/fctests.py:oos_r2_table:194` (C7); `ofilt/drift/fctests.py:oos_r2:180` (C7) | implemented | Computable for M1 to M5. M0 is not in M7's call, and `oos_r2_table` skips a benchmark absent from the frame (fctests.py L201-203). | G12, G13, G14 |
| O42 | `report_all` item `oos_r2_vs_M1`: the OOS R² of every model against M1, pooled and per ticker | spec L68; PLAN §4.3 (L269); D14 P26 (L185) | `ofilt/drift/fctests.py:oos_r2_table:194` (C7) | implemented | Computable. | G12, G13 |
| O43 | `report_all` item `pesaran_timmermann_with_training_base_rate`: PT per ticker and on the equal-weighted portfolio, next to the training-window base rate | spec L68; PLAN §4.3 (L268), §10 rule 6 (L452); D14 P26 (L185) | `ofilt/drift/fctests.py:pesaran_timmermann:265` (C7) | implemented | Computable. Undefined (stat NaN) for M0, whose forecast has a constant sign (fctests.py L36-37). | G12, G13 |
| O44 | Permutation importance: by whole dates within each fold's test block, 20 repeats, calibrated against a noise column | spec L69; PLAN §4.3 (L270), §10 rule 6 (L454); D14 P26 (L186) | `ofilt/drift/forecast.py:walk_forward:203` (C7) (importance argument); `ofilt/drift/forecast.py:importance_table:179` (C7); `ofilt/drift/forecast.py:_fold_importance:158` (C7) | implemented | Computable. Only M7 has a noise column (gbm.py L77-79), so exceeds_noise is None for the other models (forecast.py L196). | G12, G13, G15 |
| O45 | Economic evaluation (PLAN §4.5; D2.8): the every-day, β-hedged, market-on-open to market-on-close strategy that trades the sign of the forecast, for M3 and for M2 (their difference isolates usdjpy_ret). The break-even is the mean gross P&L per name-day in bp; costs are the primary, low and high round trips of D2.3 to D2.5 with each row's own β. Threshold variants are exploratory | PLAN §4.5 (L285-297); D14 P35 T5 (L358); P3S D2.3 to D2.5 (L133-138), D2.8 (L141) | `tools/p3_1_sesoi.py:costs:160` (a dev-only tool) | building blocks only | Computable from the dev forecasts of M3 and M2. It relates forecasts to targets, so only within the dev run (PR4 P4Q1). | G12, G13, G16, G17 |
| R10 | Claim tier (i), "overnight USD/JPY predicts the drift": H1 alone. Without (ii) and (iii), the wording stays at this tier | PLAN §1.4 (L129-133); D14 P32 (L301, L304) | none | building blocks only | Licenses nothing on dev (exploratory, D14 P36 step 5). Its input is R4's decision. | G10 |
| R11 | Claim tier (ii), "the exposure channel": only if H1 is rejected and, on the eligible confirmation nights, b with n225_ret (1) has the sign of the primary b̂, (2) rejects b = 0 at 5% two-sided under the primary inference method, and (3) is at least half of b without n225_ret on the same nights | AM-05 (AM L87); PLAN §1.4 (L134), §6 item 12 (L339); D37 P56 (L362); D58 P63 (L173); D14 P32 (L302) | none | building blocks only | Its nights are confirmation nights by definition. On dev only its arithmetic can be exercised, on the dev eligible nights. | G8 |
| R12 | Claim tier (iii), "the cascade": (ii) plus H3 (a₂ ≠ 0 in the predicted direction) plus the metals evidence (the COPX control and its robustness rows, plus XAU) | PLAN §1.4 (L135), §7 M2 (L365); D14 P32 (L303), P15 (L36) | none | none | No operational criterion exists to apply. | G9 |
| R13 | D2.6 Viability (reserved prefix): TOST is viable if P(equivalence at b = 0) ≥ 0.80 at the primary SESOI and the rate at b = +SESOI ≤ 6.5%; otherwise TOST is descriptive only, the equivalence wording is not used, and a null H1 is read against MDE80. Outcome: viable (5,000 of 5,000; 296 of 5,000 = 5.92%) | P3S D2.6 (L139); AM-07 (AM L96-103); spec L49; D71 P79 (L163) | none | none | Not recomputed: applied at P3-5; the outcome "viable" is in spec L49. | - |
| R14 | D2.7 Claim wording (reserved prefix): the equivalence wording ("no drift exploitable net of costs") only if TOST declares equivalence at the primary SESOI; next to it, whether it also does at the low SESOI (and at the high, D71 item 6); an economic statement, with MDE80 the statement about informational pricing | P3S D2.7 (L140); D71 carried item 6 (L210) | none | building blocks only | Its inputs are O10 and O11. | G11 |
| R15 | D3.4 The joint T1/T4 rule (reserved prefix; Flags 10 and 12): applied at P3-5 to point estimates. H1 keeps DK-normal (5.82%); Clark–West's normal rate was 3.30%, outside the band, so c_CW,cal applies; the selected methods' numbers are binding | P3S D3.4 (L160-163); D71 P73 (L84), P79 (L161-162) | none | none | Not recomputed: applied at P3-5. The outcomes are in spec L30 and L66. | - |
| R16 | D3.5: DK-normal, once selected for H1, applies to every other pre-registered DK test (H3, the secondary family, H4 and the robustness rows) | P3S D3.5 (L164); D71 P73 (L84) | `ofilt/drift/inference.py:contrast:203` (C7) | implemented | Computable. The normal reference is fixed in code (DQ6d L307). | - |
| R17 | D3.2 and D3.3 amended (reserved prefix): c_boot and c_cal are pooled over cells 0 to 4 (13,000 draws); c_CW,cal stays T3's cell at b = 0 | P3S (L194-199); D71 P73 (L86) | none | none | Not recomputed: used in the sealed run (P78). c_boot and c_cal are not selected for the confirmation (D71 P79 L161). | - |
| R18 | D4.3 T6 (reserved prefix): early-window draws before 2017-09-27; OLS-DK, Huber-DK and winsorised OLS-DK under the normal reference; outputs amended to centred quantities (D4.3a, qualified for the winsorised estimator) | P3S D4.3 (L174), D4.3 amended (L271-283), D4.3a qualified (L292-298); D71 P75 (L108-117) | none | none | Not recomputed: run once in the sealed run. The finding and the amendment are disclosed (P3S L283, L298). | G18 |
| R19 | D4.3b The flag rule (reserved prefix): a robustness row is flagged as unreliable on coarse-grid periods if its centred rate at b = 0 in cell 7 lies outside [3.5%, 6.5%]. Outcome: no row flagged (cell 7: 55, 57 and 52 of 1,000) | P3S D4.3b (L282); D71 P75 (L111), P79 (L164) | none | none | Not recomputed: applied at P3-5. | G18 |
| R20 | The interim wording on H1 and Clark–West ("H1 and the CW forecast test may disagree; disagreement is not by itself evidence against H1"); the T3 cross-tab is the binding description of their agreement | PLAN §4.4 (L281-283); D14 P26 (L189), P35 T3 (L356); D71 P79 (L165), carried item 11 (L215) | none | none | Nothing to compute: the cross-tab is fixed (D71 L165). | - |
| R21 | A null H1 is read against MDE80 (0.2471, binding) and, when viable, the equivalence test; never as "no effect" | PLAN §1.4 (L125-127), §5 (L312, L320); D14 P30 (L281); P3S D2.6 (L139), D2.7 (L140) | none | none | Nothing to compute: MDE80 is fixed (D71 L165). | G11 |
| R22 | Seeds for anything stochastic: spec seed 20261001. walk_forward's fold seed is seed + 1000·fold; M7's noise column comes from that seed (random_state = fold seed, inert); the importance permutations are drawn from it | spec L70; D14 P27 (L210-211); P3S D4.5 (L176) | `ofilt/drift/forecast.py:walk_forward:203` (C7); `ofilt/drift/models/gbm.py:draw_noise:51`; `ofilt/drift/forecast.py:_fold_importance:158` (C7) | implemented | Computable. walk_forward's seed defaults to the spec seed (forecast.py L220, L251); M7's noise uses default_rng([fold seed, stream]) (gbm.py L51-52); importance uses default_rng([fold seed, 2, r]) (forecast.py L170). | G19, G21 |
| R23 | The one-shot rule (P13(c)): the confirmation panel is opened once, by the pre-registered script; any later change to code or specification is a dated, labelled deviation | PR4 (L31); D14 P36 step 4 (L374) | `ofilt/drift/io.py:load_confirm:156` | building blocks only | Not applicable on dev. In Pass 4, `load_confirm` is called only by refusal tests (PR4 L82). | - |
| R24 | The P13(b) dry run: the script recovers a known b on simulated data and runs end to end on dev; P4Q5's setup (the confirmation calendar, the AM-03 target, b = 0 and at least one b ≠ 0, a known break at 2024-11-05) and criteria | PR4 (L29, L88-90); D14 P36 Note 1 (L380) | none | none | The synthetic half needs no dev data; the dev half is the one dev run (PR4 P4Q6). | G20, G21 |
| R25 | The forward holdout (P13(a)): data after 2026-03-05, pulled only after prereg-v1 and evaluated once; a sanity check, not a second test | PLAN §2.1 (L151); D58 P64 (L187); PR4 (L16) | none | none | Outside Pass 4: never pulled or built (PR4 L16). | G22 |
| R26 | Reporting rules: report every pre-registered result, including nulls; accuracy always next to its base rate; nested comparisons by Clark–West; importance permutation-based only | PLAN §10 rule 6 (L451-454) | none | none | Procedural; applies to every row above. | - |

## 2. Gaps

### G1. The two periods of f
- Rows: O7, O8
- Question: How are the confirmatory f (2022) and the descriptive f (2023–2026) estimated?
- Texts:
  - `spec/analysis_spec_dev_v1.yaml:37`: “status: "confirmatory for 2022 only; descriptive for 2023-2026"”
  - `docs/replacements/PLAN.md:119`: “**Confirmatory for 2022 only**, descriptive for 2023–2026”
  - `docs/DECISIONS_P14_onward.md:141`: “on the **same** design and sample”
- Options:
  - (a) one joint fit on the 2022 confirmation rows (its own T and DK lag) for the confirmatory f, and one on the rows from 2023-01-01 to 2026-03-05 for the descriptive f;
  - (b) as (a), with the descriptive f fitted per calendar year (2023, 2024, 2025, and 2026 to 2026-03-05);
  - (c) (a) or (b), plus an f on the whole confirmation sample, labelled descriptive.

### G2. f in the dev run
- Rows: O7, O8
- Question: What does the dev run compute for f, given that neither of its periods lies in dev?
- Texts:
  - `files/pass4/PASS4_BUILDER_PROMPT_2026-10-08.md:29`: “Confirm that it recovers b and produces every pre-registered output.”
  - `files/pass4/PASS4_BUILDER_PROMPT_2026-10-08.md:90`: “The criteria: every output present and finite, or marked not applicable by design”
  - `docs/DECISIONS_P14_onward.md:144`: “**Status: confirmatory for 2022 only; descriptive for 2023–2026**”
- Options:
  - (a) f on the whole dev estimation sample, labelled a dev stand-in;
  - (b) f on one dev calendar year, as a stand-in for the one-year confirmatory fit, with the other dev years as the descriptive stand-in;
  - (c) f marked not applicable by design on dev, and exercised on synthetic data only.

### G3. The window of the rolling-250 β
- Rows: O15
- Question: Is the rolling-250 β taken over the last 250 eligible rows, as the rolling-500 β is, or over the last 250 trading days?
- Texts:
  - `docs/DECISIONS_P14_onward.md:59`: “The rolling 250-day β is a robustness row (`beta_rolling_250`).”
  - `docs/replacements/PLAN.md:332`: “Rolling-250 β in place of the expanding β”
  - `spec/SPEC_AMENDMENTS.md:84`: “the past-only rolling β over the last 500 eligible rows”
  - `ofilt/drift/targets.py:5`: “rolling (last `window` eligible rows)”
- Options:
  - (a) the last 250 eligible rows (non-excluded, lag 1 day, continued across samples), as AM-05 defines the rolling-500 β and `targets.past_beta` computes;
  - (b) the eligible rows among the last 250 trading days.

### G4. The reporting form of the P33 rows outside AM-05
- Rows: O15, O17, O18, O23, O24, O25, O26, O27, O28, R8
- Question: Does AM-05's reporting form also apply to the robustness rows that are not AM-05 rows, and if not, what does each of them report?
- Texts:
  - `spec/SPEC_AMENDMENTS.md:82`: “Each row reports b with and without its change on the same rows, next to the full-sample primary b”
  - `docs/DECISIONS_P14_onward.md:310`: “From spec `robustness`, each reported next to the primary:”
  - `docs/DECISIONS_P37_onward.md:361`: “reports b with and without the added control **on the same restricted rows**, next to the full-sample primary.”
- Options:
  - (a) AM-05's form wherever "without its change on the same rows" is defined (beta_rolling_250, copx_to_fcx, raw_target), and, for the exclusion rows, post_2024 and the per-ticker row, the row's own estimates next to the full-sample primary b;
  - (b) every row outside AM-05 reports only its own estimates, with DK SEs, next to the full-sample primary b.

### G5. The rows of copx_to_fcx
- Rows: O18
- Question: On which rows is copx_to_fcx estimated?
- Texts:
  - `docs/DECISIONS_P14_onward.md:79`: “**FCX** enters only as the robustness swap `copx_to_fcx`.”
  - `docs/replacements/PLAN.md:331`: “FCX in place of COPX.”
  - `docs/replacements/DATA_DICTIONARY.md:38`: “NaN on 3 nights where EWJ was stale.”
  - `spec/SPEC_AMENDMENTS.md:85`: “Rows: primary rows with a finite ewj_oc_jpy (dev: 3 nights dropped; confirmation: none).”
- Options:
  - (a) the primary rows with a finite fcx_oc;
  - (b) the rows the primary sample rule selects with fcx_oc required in place of copx_oc (a row with a missing copx_oc and a finite fcx_oc enters).

### G6. An added column missing on rows that AM-05 calls "all primary rows"
- Rows: O20, O22
- Question: If xau_ret, a session-FX column or gotobi_day is missing on a primary row, which rows do these two rows use?
- Texts:
  - `spec/SPEC_AMENDMENTS.md:86`: “adds xau_ret (P41). Rows: all primary rows.”
  - `spec/SPEC_AMENDMENTS.md:88`: “gotobi_day (common) and usdjpy_ret × gotobi_day (common). Rows: all primary rows.”
  - `spec/SPEC_AMENDMENTS.md:85`: “Rows: primary rows with a finite ewj_oc_jpy (dev: 3 nights dropped; confirmation: none).”
- Options:
  - (a) "all primary rows" taken as a fact to verify by a structural count (P4Q1), with a STOP for a decision if it fails;
  - (b) the primary rows where the added columns are finite, with the dropped count reported, as the ewj row does.

### G7. The per-ticker design
- Rows: O28, R7
- Question: In the per-ticker row, which terms become ticker-specific, and is it one pooled fit or three fits?
- Texts:
  - `docs/replacements/PLAN.md:108`: “**H4 (descriptive).** Per-ticker slopes, Holm-corrected across the three stocks.”
  - `docs/DECISIONS_P14_onward.md:323`: “| `per_ticker_slopes_holm` | per-stock b with Holm across the three (H4) |”
- Options:
  - (a) one pooled DK fit with usdjpy_ret × ticker (three slopes) in place of the common usdjpy_ret, eurusd_ret staying common;
  - (b) as (a), with eurusd_ret also ticker-specific;
  - (c) three separate per-ticker fits, each with its own DK SE over its ticker's dates.
  - In each option, Holm is applied across the three two-sided p-values.

### G8. Condition (3) of the tier-(ii) criterion
- Rows: O21, R11
- Question: Is "at least half of b without n225_ret" a signed or an absolute comparison?
- Texts:
  - `spec/SPEC_AMENDMENTS.md:87`: “(3) is at least half of b without n225_ret on the same nights.”
  - `docs/DECISIONS_P58_onward.md:173`: “(3) is at least half of b without n225_ret on the same nights.”
  - `docs/DECISIONS_P37_onward.md:362`: “The operational criterion for claim tier (ii) is written into AM-05 before `spec-dev-v1`.”
- Options:
  - (a) signed: b_with / b_without ≥ 0.5, which fails if the two differ in sign;
  - (b) magnitudes: |b_with| ≥ 0.5 · |b_without|.

### G9. The tier-(iii) criterion
- Rows: O2, R12
- Question: What is the operational criterion for claim tier (iii): the predicted direction of a₂, and what the metals evidence must show?
- Texts:
  - `docs/replacements/PLAN.md:135`: “| (iii) | "the cascade" | (ii) plus H3 plus the metals controls |”
  - `docs/DECISIONS_P14_onward.md:303`: “additionally needs H3 (a₂ ≠ 0 in the predicted direction, P15) and the metals evidence”
  - `docs/DECISIONS_P14_onward.md:36`: “The cascade model predicts a₂ ≠ 0.”
  - `docs/replacements/PLAN.md:365`: “**M2.** The sign prediction is derived for the *conditional* coefficient a₂”
- Options:
  - (a) a criterion stated in the confirmation configuration before the dev run: H3's test and direction, and a stated requirement on copx_to_fcx and xau_control;
  - (b) a criterion stated in the pre-registration, before `prereg-v1`, after the advisor's M2;
  - (c) no tier-(iii) claim: H3 and the metals rows reported without a tier-(iii) reading.

### G10. The wording of tier (i)
- Rows: R10
- Question: Which sentence is tier (i)'s claim? (The two texts differ.)
- Texts:
  - `docs/replacements/PLAN.md:133`: “| (i) | "overnight USD/JPY predicts the drift" | H1 alone |”
  - `docs/DECISIONS_P14_onward.md:304`: “the wording is limited to "overnight USD/JPY predicts session drift"”
- Options:
  - (a) PLAN §1.4's sentence;
  - (b) P32's sentence.

### G11. The wording that equivalence, or a well-powered null, licenses
- Rows: O10, O11, R14, R21
- Question: Which claim does an equivalence declaration, or a well-powered null H1, license? (The texts differ.)
- Texts:
  - `docs/DECISIONS_P14_onward.md:132`: “If H1 does not reject, "the auction fully prices overnight FX" is claimed only through”
  - `PASS3_STATUS.md:140`: “The equivalence wording ("no drift exploitable net of costs") is used only if TOST declares equivalence at the primary SESOI”
  - `PASS3_STATUS.md:140`: “MDE80 remains the statement about informational pricing.”
  - `docs/replacements/PLAN.md:127`: “A well-powered null is a finding: "the auction prices overnight FX for FX-exposed miners"”
- Options:
  - (a) D2.7's economic wording for equivalence, with MDE80 as the informational statement; the sentences of P23 and PLAN §1.4 are not used;
  - (b) P23's sentence when TOST declares equivalence, with D2.7's wording beside it;
  - (c) PLAN §1.4's sentence for a null H1, and D2.7's wording for equivalence.

### G12. The forecast evaluation rows at the confirmation
- Rows: O29, O30, O31, O32, O33, O34, O35, R9, O36, O37, O38, O39, O40, O41, O42, O43, O44, O45
- Question: At the confirmation, which forecast rows enter the comparisons, the report_all items, the importance and the economic evaluation?
- Texts:
  - `docs/DECISIONS_P14_onward.md:356`: “CW's walk-forward trains on a dev-length history and evaluates on T_conf dates”
  - `PASS3_STATUS.md:173`: “Clark–West (M3 vs M2) on the rows of the last 1,013 dates; H1 on the same last 1,013 dates.”
  - `docs/replacements/PLAN.md:257`: “Expanding window. The first forecast comes after 500 **eligible** training dates”
  - `PASS3_STATUS.md:938`: “`walk_forward` always starts forecasting after the 500th eligible training date”
- Options:
  - (a) each walk_forward call runs on the dev and confirmation rows, and its outputs are restricted to the confirmation dates' evaluation rows;
  - (b) every forecast row each call produces, dev dates included.

### G13. The forecast evaluation rows in the dev run
- Rows: O29, O30, O31, O32, O33, O34, O35, R9, O36, O37, O38, O39, O40, O41, O42, O43, O44, O45
- Question: In the dev run, which forecast rows enter them?
- Texts:
  - `docs/DECISIONS_P14_onward.md:356`: “CW's walk-forward trains on a dev-length history and evaluates on T_conf dates”
  - `files/pass4/PASS4_BUILDER_PROMPT_2026-10-08.md:29`: “Confirm that it recovers b and produces every pre-registered output.”
- Options:
  - (a) every dev forecast row, from the first forecast after the 500th eligible training date to 2021-12-30;
  - (b) a confirmation-structured split of dev: a training history, then an evaluation span at the end of dev.

### G14. M7's OOS R² against M0
- Rows: O41
- Question: How is M7's OOS R² against M0 obtained, given that M7 runs in a call without M0?
- Texts:
  - `docs/DECISIONS_P14_onward.md:185`: “| Reported for all models | OOS R² vs M0 and vs M1, pooled and per ticker;”
  - `docs/DECISIONS_P14_onward.md:200`: “It is therefore run in its own call with its comparator M1”
- Options:
  - (a) M0 added to M7's call (M0 reads no feature, so the call's sample is unchanged);
  - (b) M7's OOS R² reported against M1 only.

### G15. Which models' importance
- Rows: O44
- Question: Which models' permutation importance is computed and reported?
- Texts:
  - `spec/analysis_spec_dev_v1.yaml:69`: “importance: {method: permutation, unit: date, repeats: 20, calibration: noise_column}”
  - `docs/DECISIONS_P14_onward.md:186`: “| Importance | permutation by whole dates within each fold's test block, 20 repeats, calibrated against a noise column |”
  - `docs/replacements/PLAN.md:270`: “| Permutation importance | Date-unit, calibrated against the noise column |”
- Options:
  - (a) M7 only, calibrated against its own noise column;
  - (b) M7 and the linear models M2 to M5, with the noise calibration available for M7 only. (A noise column for M0 to M4 would need a change in `ofilt/drift/models/linear.py`, which is C7-hashed and stays byte-identical under P4Q2.)

### G16. What the economic evaluation reports
- Rows: O45
- Question: Besides the break-even, what does the economic evaluation report?
- Texts:
  - `PASS3_STATUS.md:141`: “The break-even is the mean gross P&L per name-day, in bp”
  - `docs/replacements/PLAN.md:289`: “each with a primary value and a sensitivity range”
  - `docs/DECISIONS_P14_onward.md:358`: “It also fixes the economic evaluation's cost assumption and break-even.”
- Options:
  - (a) the break-even of M3 and of M2 and their difference, next to the primary, low and high mean round trips;
  - (b) (a), plus the mean net P&L per name-day under each of the three cost cases;
  - (c) (b), per ticker as well as pooled.

### G17. The tick terms at the confirmation
- Rows: O45
- Question: At the confirmation, are the tick terms x_m and x_h fixed at their dev values, or recomputed on the confirmation rows?
- Texts:
  - `PASS3_STATUS.md:135`: “Primary: x_m = max(stated impact, ½ tick), averaged per ticker over its kept rows outside the Flag 4 windows”
  - `PASS3_STATUS.md:141`: “with each confirmation row's own β”
- Options:
  - (a) fixed at the dev values of `reports/P3_1_sesoi.md`, with only β row-specific;
  - (b) recomputed by D2.4's and D2.5's rules on the confirmation rows' own open and close prices.

### G18. The D4.3 window deviations on dev
- Rows: R18, R19
- Question: Does Pass 4 examine the D4.3 deviations on dev?
- Texts:
  - `PASS3_STATUS.md:283`: “Pass 4 may examine them on dev.”
  - `files/pass4/PASS4_BUILDER_PROMPT_2026-10-08.md:95`: “No exploratory extras are planned.”
- Options:
  - (a) not examined;
  - (b) examined under their own decision, by a named committed script with recorded outputs, and listed for disclosure (P4Q7).

### G19. The seed of each walk_forward call
- Rows: R22
- Question: Which seed does each walk_forward call of the confirmation script use?
- Texts:
  - `spec/analysis_spec_dev_v1.yaml:70`: “seeds: {global: 20261001}”
  - `docs/DECISIONS_P14_onward.md:211`: “`random_state` = fold seed (inert in this configuration).”
- Options:
  - (a) the spec seed for every call (the engine's default);
  - (b) a distinct seed per call, derived from the spec seed by a stated offset.

### G20. The dry run's recovery criterion
- Rows: R24
- Question: Does "recovers b" carry a numeric criterion beyond P4Q5's?
- Texts:
  - `files/pass4/PASS4_BUILDER_PROMPT_2026-10-08.md:29`: “Confirm that it recovers b and produces every pre-registered output.”
  - `files/pass4/PASS4_BUILDER_PROMPT_2026-10-08.md:88`: “Recovery criteria are stated in advance, in the item that runs the synthetic dry run.”
  - `files/pass4/PASS4_BUILDER_PROMPT_2026-10-08.md:90`: “The criteria: every output present and finite, or marked not applicable by design”
- Options:
  - (a) P4Q5's criteria only;
  - (b) P4Q5's criteria plus a numeric tolerance for b̂ (and b_post) against the known values, stated in the dry-run item.

### G21. The dry run's seeds
- Rows: R22, R24
- Question: Which seeds do the synthetic dry run's draws use?
- Texts:
  - `spec/analysis_spec_dev_v1.yaml:70`: “seeds: {global: 20261001}”
  - `PASS3_STATUS.md:176`: “The outer seed is the spec's seed + 5,000,000 + 100,000·cell + replication”
- Options:
  - (a) the spec seed plus a new offset block, disjoint from the B7, B7b, C7 and sealed-run blocks (D4.5's pattern);
  - (b) the spec seed itself.

### G22. What the forward holdout evaluates
- Rows: R25
- Question: What is evaluated on the forward holdout, and by which script?
- Texts:
  - `docs/replacements/PLAN.md:151`: “Pulled only after `prereg-v1`; evaluated once; a sanity check, not a second test”
  - `docs/DECISIONS_P58_onward.md:187`: “Option (c), the intraday PX_OPEN check, is recorded as a forward-holdout check after the confirmation run.”
- Options:
  - (a) fixed in the pre-registration (Pass 5);
  - (b) the confirmation script run once on the holdout, its outputs descriptive, with D8's option (c) beside it.

## 3. Facts for the configuration

**Input columns, by row** (keys `date` and `ticker` throughout):
- Every inference row (O1 to O28, R1 to R8): y_oc, y_1306_oc, earn_flag, news_flag, usdjpy_ret, eurusd_ret, spy_oc, copx_oc. `beta` and the constructed targets come from `targets.add_targets`.
- O3: window_hours. O4: usdjpy_rv, usdjpy_bv. O5: usdjpy_rv, usdjpy_bars. O6: usdjpy_ret only.
- O7, O8: ao_gap_adj and ao_1306_gap_adj, through gap_abn and cc_abn (targets.py L126-127).
- O9, O17: y_oc (raw_oc) and y_1306_oc (b_mkt).
- O18: fcx_oc. O19: ewj_oc_jpy. O20: xau_ret. O21: n225_ret, n225_stale_start_min, n225_stale_end_min. O22: c_usdjpy_sess_ret, c_eurusd_sess_ret, gotobi_day.
- O23: events_firm.csv (TANSHIN and STANDALONE_NEWS releases), through `targets.add_masks` (excl_d2). O24: audit_flag. O25: boj_day. O26: sq_major. O27: date (for post). O28: the primary columns.
- O29 to O34 and R9: M2 and M3 read usdjpy_ret, eurusd_ret, spy_oc, copx_oc; M4 and M5 also read window_hours, usdjpy_rv, usdjpy_bv, usdjpy_bars. The masks are excl_inference (from earn_flag, news_flag) and excl_forecast_eval (from events_firm.csv).
- O35: the 20 PRE_OPEN_FEATURES: usdjpy_ret, usdjpy_rv, usdjpy_bv, eurusd_ret, eurusd_rv, spy_oc, ewj_oc, fcx_oc, copx_oc, us_n_sessions, window_hours, gap_adj_lag1, oc_lag1, range_lag1, topix_oc_lag1, boj_day, sq_day, sq_major, exdiv_day, div_exdate.
- O45: the M3 and M2 forecasts, abn_oc, beta, open and close (D2.4's tick terms on traded prices), and `docs/P3_COST_INPUTS.json`.

**Columns the forecasting allowlist refuses that a row needs** (P4Q2):
- As regressors (the inference-only allowlist): ewj_oc_jpy (O19), xau_ret (O20), n225_ret (O21) and gotobi_day (O22), which are PRE_OPEN_ROBUSTNESS; and c_usdjpy_sess_ret and c_eurusd_sess_ret (O22), which are CONTEMPORANEOUS.
- Derived terms that no schema group holds, built from permitted columns: post and usdjpy_ret × post (O27, from date); usdjpy_ret × gotobi_day (O22); usdjpy_ret × ticker (O28, under G7's options).
- As sample filters only, never regressors: n225_stale_start_min and n225_stale_end_min (PROVENANCE; O21); audit_flag (ROBUSTNESS_ONLY; O24); excl_d2 (a mask column, `targets.MASK_COLUMNS`; O23).
- As cost inputs only: open and close (PROVENANCE; O45).
- Not refused: fcx_oc, boj_day and sq_major are PRE_OPEN_FEATURES.

**Places where a C7-hashed function would have to change:**
- No row needs one, provided new code appends or re-arranges columns of `build_design`'s output (P4Q2) and fits the result with `fit_dk`. `Design` is a plain dataclass (inference.py L53-68), and `pooled_ols`, `driscoll_kraay` and `fit_dk` accept any Design that carries a provenance (inference.py L150-223). `Result.contrast` gives b_post and any other linear combination (L203-212). `subset_design` restricts rows and recomputes T (L231-241). `fctests.pair` compares any row subset of one call (P3S L938), so a restricted evaluation window needs no change in forecast.py.
- A noise column for M0 to M4 (outside G15's options) would need `ofilt/drift/models/linear.py` (C7) to change.
- AM-09's critical value is applied by a helper to `fctests.clark_west`'s "stat" (DQ6d L314); fctests.py itself is unchanged.

**Modules and functions the confirmation module is expected to call** (names only):
- `spec`: Spec.load, Spec.sesoi, Spec.winsor_bounds, Spec.seed, Spec.dk_lag, Spec.h1_parameter, Spec.h3_parameter.
- `io`: load_dev, load_events_firm; load_confirm (Pass 6 only; in Pass 4 only refusal tests call it, PR4 L82).
- `targets`: add_targets (default, and method "rolling" with windows 250 and 500), add_masks.
- `blind`: require_unblinded (inside every entry point).
- `inference`: build_design, fit_dk, Result.param, Result.contrast, subset_design, fit_huber, influence_curve, tost_result, tost, fit_joint, fraction_unpriced, decomposition, fit_market, holm, secondary_family_tests.
- `calib`: winsorise_fx.
- `forecast`: walk_forward, importance_table.
- `models`: M0, M1, M2, M3, M4, M5, M7 (`models.REGISTRY`).
- `fctests`: run_comparisons, clark_west, diebold_mariano, oos_r2_table, pesaran_timmermann.
- `registry`: record_run (through walk_forward).
- `calendar`: T_CONF, confirmation_calendar (the confirmation calendar of P4Q5's synthetic setup).
- `sim`: stationary_bootstrap_positions, as an existing resampler. The full-schema simulator is new (P4-3).

**Other facts:**
- `io.load_confirm` returns the sealed panel alone (io.py L156-169). β continues across samples (spec L15; targets.py L9-10), so the confirmation frame holds dev and confirmation rows, and no code assembles it yet.
- A dev_real or confirm_real walk_forward call appends to `RUN_REGISTRY.jsonl` (registry.py L33, L41-46).
- In the spec, the low and high SESOI values appear only inside the viability string (spec L49); they are also in `reports/P3_1_sesoi.md`. `Spec.sesoi` returns 0.8652 only.
- c_CW,cal = 1.411608406163672 is in spec L66 and pinned in `spec.PRIMARY_FORECAST` (spec.py L49-52).
- `build_design` drops a row if any listed exclusion column is truthy after astype(bool) (inference.py L98), so a NaN flag excludes its row.
- `fit_joint` uses the rows where both abn_oc and cc_abn are non-missing (inference.py L392). Its b equals O1's b only if cc_abn is finite wherever abn_oc is (a structural count).
- The highrv design fails closed if usdjpy_bars ≤ 0 on a kept row (inference.py L121-124).
- On dev, post is identically 0 (D14 L325), and the post row's design is rank-deficient (inference.py L132-133).
- The normal reference is fixed in code, in `Result.contrast`, `tost` and `fctests._differential_test` (DQ6d L307).

## 4. Coverage

Computed by `/tmp/p4_1_b4_audit.py` (verdict AUDIT CHECK), with each gap's quotes and the table's code entry points checked against HEAD by `/tmp/p4_1_b4_cites.py` (verdict CITES CHECK). Both are printed in `/tmp/p4_1.txt`.
