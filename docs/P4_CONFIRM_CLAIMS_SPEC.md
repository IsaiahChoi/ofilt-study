# P4_CONFIRM_CLAIMS_SPEC: the claim and rule rows, and the inference-only allowlist (P4-4c1; P4Q38)

Version 1, written by the supervisor chat that began on 2026-10-11 with handoff H9, for P4-4c1. It specifies two modules, `ofilt/drift/confirm_allowlist.py` and `ofilt/drift/confirm_claims.py`, and their tests `tests/test_p4_confirm_claims.py`. P4-4c1 commits it as `docs/P4_CONFIRM_CLAIMS_SPEC.md`. A change after P4-4c1 is a new version of this file, recorded with its reason.

The claims module computes the 17 rows that `confirm_inference.ITEM_OF` gives to P4-4c: R10 to R26. Most are rules fixed before Pass 4, which the document records with their outcome and source; four are decisions read off rows already computed (R10, R11, R14, R21); one adds a quantity that P4-4a did not store (R12's a₂ gap). The run script that assembles the whole document, the two-run identity rule, the registry routing and the `io.load_confirm` refusal tests are P4-4c2's.

The texts it implements: the configuration's `claims`, `constants`, `not_examined_on_dev`, `forward_holdout` and `dry_run`; the spec's `inference` and `equivalence`; the audit's rows R10 to R26 (`reports/P4_reports/p4_1_audit.md`, §1) and gaps G8 to G11; PLAN §1.4 and §10 rule 6; `PASS4_STATUS.md`'s P4Q2, P4Q16 to P4Q19, P4Q31; the entry schema of `docs/P4_CONFIRM_INF_SPEC.md` §4.

## 1. Rules for the code

### 1.1 Placement and imports
- Two new modules and one new test file. No existing file changes; no C7-hashed file changes.
- `confirm_allowlist.py` imports nothing but `__future__`. It defines constants only (§2).
- `confirm_claims.py` imports only `__future__`, `copy`, `math`, `typing`, `numpy`, `pandas`, and from the package `blind`, `inference`, `targets`, `spec` (`Spec`), `confirm_inference` (`ITEM_OF`, `ROW_IDS`, `STATUSES`, `load_config`, `_plain`) and `confirm_forecast` (`_check_inputs`). It does not import `io`, `forecast`, `fctests`, `models`, `registry`, `sim`, `sim_full`, `calendar`, `schema`, `calib`, `confirm_economic` or anything under `tools/`.
- Neither module opens, reads or writes a file itself (the configuration through `confirm_inference.load_config`), or draws a random number.

### 1.2 Static tests they must satisfy
As `docs/P4_CONFIRM_INF_SPEC.md` §1.2 (`test_sim_b5`, `test_schema`, `test_docs_d3b`, `test_docs_d6`).

### 1.3 Read first (as text)
The configuration's sections named above, in full; the audit's rows R1 to R26 and gaps G8 to G11; PLAN §1.4 and §10; `PASS4_STATUS.md`'s Decision log entries P4Q2, P4Q12, P4Q16 to P4Q19 and P4Q31; `ofilt/drift/schema.py` (its groups); `ofilt/drift/confirm_inference.py` (the entries R4, O1, O2, O10, O11, O17, O18, O20, O21 and how they are built); `ofilt/drift/confirm_forecast.py` and `ofilt/drift/confirm_economic.py` (their `fill`).

## 2. `confirm_allowlist.py` (P4Q2)

Constants, each a `frozenset` of column names:
- `INFERENCE_ONLY_REGRESSORS = {"ewj_oc_jpy", "xau_ret", "n225_ret", "gotobi_day", "c_usdjpy_sess_ret", "c_eurusd_sess_ret"}`: the columns that P33's and AM-05's robustness rows add as regressors and that the forecasting allowlist does not hold;
- `INFERENCE_ONLY_FILTERS = {"n225_stale_start_min", "n225_stale_end_min", "audit_flag", "excl_d2"}`: columns used only to select rows of robustness rows;
- `COST_INPUTS_ONLY = {"open", "close"}`: columns used only by the economic evaluation's costs;
- `INFERENCE_ONLY = INFERENCE_ONLY_REGRESSORS | INFERENCE_ONLY_FILTERS | COST_INPUTS_ONLY`;
- `FORECASTING_MODULES`: the repository paths of the forecasting code, `("ofilt/drift/forecast.py", "ofilt/drift/fctests.py", "ofilt/drift/models/__init__.py", "ofilt/drift/models/linear.py", "ofilt/drift/models/ridge.py", "ofilt/drift/models/gbm.py", "ofilt/drift/confirm_forecast.py")`.

The derived terms of the robustness rows (`post`, `usdjpy_ret:post`, `usdjpy_ret:gotobi_day`, the ticker-specific FX block) are design columns, not panel columns, and are not listed.

## 3. `confirm_claims.py`: API

- `ROWS = ("R10", ..., "R26")`, in the configuration's order (17 IDs, each `ITEM_OF` "P4-4c").
- `claim_rows(doc, dev, events, confirm=None, *, spec=None) -> dict`: `{id: entry}` for exactly `ROWS`, in order. `doc` is a document whose P4-4a and P4-4b rows are filled (P4-4b's by `confirm_forecast.fill` and `confirm_economic.fill`); `dev`, `events`, `confirm` are the frames it was computed on. First, `confirm_forecast._check_inputs(dev, confirm)`; then `ValueError` unless `doc["mode"]` is `"confirmation"` exactly when `confirm` is given, and `doc["provenance"]` equals the provenance that `confirm_inference.infer` gives for these frames. The frames are used only for R12's a₂ gap (§4).
- `rows_from(doc, a2_gap) -> dict`: the pure part of `claim_rows`: every row of §4 read from `doc`, with R12's gap passed in (a dict as §4 defines G). `claim_rows` checks its inputs, computes G, and returns `rows_from(doc, G)`.
- `fill(doc, rows) -> dict`: a copy (by `_plain`) with each entry of `rows` replacing the pending entry of the same ID; `ValueError` unless `rows`' keys are exactly `ROWS`, each replaced entry is a pending P4-4c entry, and each new entry has its own ID and item "P4-4c".
- `licensed(doc) -> bool`: True exactly when `doc["mode"]` is `"confirmation"` and `doc["provenance"]` is `"confirm_real"`. A claim is made only when it is licensed; on dev and on synthetic documents its arithmetic is exercised and reported, never claimed (D14 P36 step 5).

## 4. The rows

Each entry has the schema of `docs/P4_CONFIRM_INF_SPEC.md` §4.2 with item "P4-4c". "Not estimable from X" means: status `not_estimable`, reason `f"input {X} not estimable: {X's reason}"`, values None, counts None (P4Q31: a claim whose inputs include a not-estimable result is not made). Every value plain; a non-finite float makes the row not estimable, reason `"non-finite estimate"`. `cfg` is the configuration; `L` is `licensed(doc)`. Counts are None in every row.

| ID | Status and values |
|---|---|
| R10 | Tier (i) (P4Q18). Not estimable from R4 if R4 is not estimated. Estimated: `{"wording": cfg.claims.tier_i.wording, "requires": cfg.claims.tier_i.requires, "h1_rejected": R4.values.reject, "licensed": L, "claimed": L and h1_rejected, "decision": "P4Q18"}`. |
| R11 | Tier (ii) (AM-05, P4Q16). Not estimable from R4, O1 or O21, in that order, if one is not estimated. Else `b_primary` = O1's fit estimate; `b_with`, `b_without` = O21's `with` and `without` estimates; `p_with` = O21's `with` p. Conditions: (1) `sign(b_with) == sign(b_primary)` and both non-zero; (2) `p_with < spec.alpha`; (3) `ratio = b_with / b_without` defined (`b_without` finite and non-zero) and `ratio >= 0.5` (it fails if the two differ in sign, as a negative ratio is below 0.5). Estimated: `{"wording": cfg.claims.tier_ii.wording, "h1_rejected", "b_primary", "b_with", "b_without", "p_with", "ratio" (None if undefined), "condition_1", "condition_2", "condition_3", "eligible_dates": O21's, "licensed": L, "claimed": L and h1_rejected and all three conditions, "decision": "P4Q16"}`. |
| R12 | Tier (iii) (P4Q17): fixed. `{"claimed": False, "report_without_tier_reading": cfg.claims.tier_iii.report_without_tier_reading, "a2_reading": cfg.claims.tier_iii.a2_reading, "rows": {"H3": "O2", "copx_to_fcx": "O18", "xau_control": "O20", "raw_target": "O17"}, "a2_gap": G, "decision": "P4Q17"}`, where G is: on the frame C that P4-4a builds (`docs/P4_CONFIRM_INF_SPEC.md` §3.3, §3.4), `D0 = build_design(C, spec)`, `Dr = build_design(C, spec, target="raw_oc")`, the rows of D0 whose index is in `Dr.index` (as O17 restricts them), and on those rows `a2_abn` and `a2_raw` = the `eurusd_ret` estimates of `fit_dk` on D0 and on Dr restricted to the same index labels; `G = {"a2_raw": summary, "a2_abn": summary, "difference": a2_raw - a2_abn, "n_rows", "n_dates"}`, each summary as §4.4 there. A `DesignError` or no common row makes G `{"status": "not_estimable", "reason": ...}`; R12 stays fixed. |
| R13 | D2.6 viability: fixed. `{"viability": spec.value("equivalence.viability"), "viable": that text starts with "viable", "recomputed": False, "source": "P3-5; AM-07"}`. |
| R14 | The equivalence wording (D2.7, P4Q19). Not estimable from O10 or O11 if one is not estimated. Estimated: `{"wording": cfg.claims.equivalence.wording, "viable": R13's, "equivalent_primary": O10.values.equivalent, "equivalent_low": O11.values.low.equivalent, "equivalent_high": O11.values.high.equivalent, "licensed": L, "claimed": L and viable and equivalent_primary, "beside": cfg.claims.equivalence.beside, "mde80": cfg.constants.mde80, "decision": "P4Q19"}`. |
| R15 | D3.4: fixed. `{"h1_method": "dk_normal", "cw_reference": "calibrated", "c_cw_cal": cfg.constants.c_cw_cal, "recomputed": False, "source": "P3-5"}`. |
| R16 | D3.5: fixed. `{"rule": "DK-normal, selected for H1, applies to every other pre-registered DK test", "reference": spec.value("inference.reference"), "source": "D3.5"}`. |
| R17 | D3.2 and D3.3 amended: fixed. `{"selected_for_confirmation": False, "recomputed": False, "source": "P73; P79"}`. |
| R18 | D4.3 T6: fixed. `{"recomputed": False, "not_examined_on_dev": cfg.not_examined_on_dev.items, "decision": "P4Q26", "source": "P75"}`. |
| R19 | D4.3b: fixed. `{"rows_flagged": [], "recomputed": False, "source": "P3-5"}`. |
| R20 | The interim wording on H1 and Clark–West: fixed. `{"wording": "H1 and the CW forecast test may disagree; disagreement is not by itself evidence against H1", "binding_description": "the T3 cross-tab", "h1_rejected": R4's reject or None, "cw_reject_calibrated": O36's or None, "agree": both given and equal, else None, "source": "PLAN 4.4; P79"}`. |
| R21 | The reading of a null H1 (P4Q19). Not estimable from R4. Estimated: `{"h1_rejected", "null": not h1_rejected, "rule": cfg.claims.null_h1.rule, "mde80": cfg.constants.mde80, "equivalence_row": "R14", "decision": "P4Q19"}`. |
| R22 | Seeds: fixed. `{"spec_seed": spec.seed, "walk_forward_seed": "the spec seed (P4Q27)", "fold_seed": "seed + 1000 * fold", "m7_noise": "default_rng([fold seed, stream])", "importance": "default_rng([fold seed, 2, repeat])"}`. |
| R23 | The one-shot rule (P13(c)): fixed if `doc["provenance"]` is `"confirm_real"`, with `{"rule": "the confirmation panel is opened once, by the pre-registered script; any later change is a dated, labelled deviation", "source": "P13(c)"}`; otherwise not applicable, reason `"the one-shot rule applies to the confirmation panel only"`. |
| R24 | The dry run (P13(b)): fixed. `{"recovery": cfg.dry_run.recovery.rule, "seeds": cfg.dry_run.seeds.rule, "item": "P4-5", "decisions": ["P4Q28", "P4Q29"]}`. |
| R25 | The forward holdout (P13(a)): not applicable, reason `cfg.forward_holdout.rule + " (P4Q30); outside Pass 4"`. |
| R26 | Reporting rules (PLAN §10 rule 6): fixed. `{"rules": ["report every pre-registered result, including nulls", "accuracy always next to its base rate", "nested comparisons by Clark-West", "importance permutation-based only"], "pending_rows": [the IDs of doc's rows outside ROWS whose status is pending], "not_estimable_rows": [the IDs of doc's rows outside ROWS that are not estimable]}`. |

## 5. Tests (`tests/test_p4_confirm_claims.py`: exactly these 15)

### 5.1 Seeds, documents and run time
- Seeds S_k = `Spec.load().seed` + 8,400,000 + k, k below 1,000 (disjoint from + 8,000,000 to + 8,300,000 and + 8,500,000).
- **The full document D1**: on `sim_full.simulate(S1, Scenario(b=1.0, a2=0.6, delta_cc=1.5), dev_dates=sim_full.dev_calendar()[-900:])` with 5706's `open`, `close` and `prev_close` multiplied by 0.1 (as P4-4b2's tests), `infer`, then `run_calls` with the zero-forecast M7 stand-in of P4-4b2's tests, `confirm_forecast.fill` with `forecast_rows`, `confirm_economic.fill` with `economic_row`; computed once, with the run registry patched to a temporary folder for the module.
- **Hand-made documents**: copies of D1 (`copy.deepcopy`) in which named values are set by the test (for example R4's `reject`, O21's estimates, `mode` and `provenance`), to reach each branch of R10, R11, R14 and R21 deterministically. Copies are evaluated with `rows_from(copy, G1)`, G1 being D1's R12 gap, so that no frame is needed and §3's frame checks do not apply.
- The file runs in under 120 s; the report gives its time.

### 5.2 The 15 tests
1. `test_allowlist_constants`: the four sets as §2; each is disjoint from `schema.PRE_OPEN_FEATURES` and from `schema.ALLOWED_FEATURES`; the regressors lie in `schema.PRE_OPEN_ROBUSTNESS | schema.CONTEMPORANEOUS`, the cost inputs in `schema.PROVENANCE`, the filters in `schema.PROVENANCE | schema.ROBUSTNESS_ONLY | targets.MASK_COLUMNS`.
2. `test_no_forecasting_code_uses_the_allowlist` (P4Q2): for each file of `FORECASTING_MODULES`, by `ast`, no string constant equals a name of `INFERENCE_ONLY`.
3. `test_the_robustness_rows_use_the_regressors`: by `ast`, every name of `INFERENCE_ONLY_REGRESSORS` and of `INFERENCE_ONLY_FILTERS` is a string constant of `ofilt/drift/confirm_inference.py`, and `open` and `close` are string constants of `ofilt/drift/confirm_economic.py`.
4. `test_rows_and_schema` (D1): `ROWS` is R10 to R26 in the configuration's order; `claim_rows` returns exactly `ROWS`, each with the 8 keys, item P4-4c, a status other than pending; `fill(D1, rows)` leaves no pending entry at all, serialises with `to_json` without `NaN` or `Infinity` and round-trips; `fill` raises `ValueError` on a document whose R10 is not pending and on rows missing an ID.
5. `test_tier_i` (copies of D1): with R4's `reject` True and False, and `licensed` True and False (`mode`, `provenance` set), R10's `claimed` is True only for reject True and licensed; with R4 not estimable, R10 is not estimable with a reason starting `input R4`.
6. `test_tier_ii_conditions` (copies of D1): hand-set O1 and O21 estimates and p give, for each of these cases, the expected three conditions and claim: all hold (b_primary 1.0, b_with 0.8, b_without 1.0, p 0.01); condition 1 fails (b_with −0.8); condition 2 fails (p 0.2); condition 3 fails (b_with 0.4); b_without 0 (ratio None, condition 3 False); b_without negative with b_with positive (condition 3 False); and H1 not rejected (no claim with all three conditions true).
7. `test_tier_ii_inputs_not_estimable`: with O21 not estimable, R11 is not estimable with a reason starting `input O21`; with R4 not estimable, `input R4`.
8. `test_tier_iii_and_a2_gap` (D1): R12 is fixed with `claimed` False and the configuration's texts; its `a2_gap` equals the test's own refit on the frame C (built as P4-4a's §3.3), with `difference` = `a2_raw − a2_abn` exactly; `n_rows` equals O17's.
9. `test_equivalence_wording` (copies of D1): `claimed` is True only for viable, equivalent at the primary SESOI and licensed; `equivalent_low` and `equivalent_high` are O11's; with O10 not estimable, R14 is not estimable.
10. `test_null_reading` (copies of D1): R21's `null` is the negation of R4's `reject`; `mde80` is the configuration's 0.2471.
11. `test_fixed_rule_rows` (D1): R13, R15, R16, R17, R18, R19, R22, R24 and R26 are fixed with the values of §4; R13's `viable` is True; R22's `spec_seed` is the spec's seed; R26's `pending_rows` is empty and its `not_estimable_rows` lists exactly D1's not-estimable rows outside `ROWS`.
12. `test_interim_wording_agreement` (copies of D1): R20's `agree` is True, False and None for R4 and O36 equal, different, and O36 not estimated.
13. `test_one_shot_and_holdout`: R23 is not applicable on D1 (synthetic) and fixed on a copy with provenance `confirm_real` and mode confirmation (through `rows_from`); R25 is not applicable with the configuration's rule in its reason.
14. `test_frames_must_match_the_document` (D1's frames): `claim_rows` raises `ValueError` for the dev mode with a confirmation document, for frames with another provenance (refused pairs, before any target is built: `blind.registered_labels()` unchanged), and runs on D1's own frames.
15. `test_module_sources`, by `ast`: `confirm_allowlist.py` imports only `__future__` and assigns only the names of §2; `confirm_claims.py` imports only as §1.1 allows; neither calls `open`, `read_csv`, `to_csv`, `read_bytes`, `read_text`, `write_text`, `write_bytes`, `to_parquet`, `to_pickle` or `to_excel`, nor holds the strings `load_dev`, `load_confirm`, `load_events`, `OFILT_DATA_DIR` or `RUN_REGISTRY`; `confirm_claims.py` defines `ROWS`, `claim_rows`, `rows_from`, `fill` and `licensed`.

## 6. Notes for the builder
- The item's message has a probe step (c.2): it builds D1 as §5.1 says and prints the entries R4, O1, O2, O10, O11, O17, O18, O20, O21 and O36 (their keys and values), the configuration's sections of §1.3, and the spec's `inference.reference` and `equivalence.viability`. It asserts nothing.
- R12's gap is the one quantity this module computes from frames; every other row reads the document.
- If a test can pass only by departing from this file, or this file is wrong on a point a test depends on, stop and say which.
