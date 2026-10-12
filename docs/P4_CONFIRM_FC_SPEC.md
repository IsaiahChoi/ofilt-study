# P4_CONFIRM_FC_SPEC: the confirmation module, forecasting rows (P4-4b1; P4Q36)

Version 1, written by the supervisor chat that began on 2026-10-11 with handoff H9, for P4-4b1. It specifies `ofilt/drift/confirm_forecast.py` and its tests `tests/test_p4_confirm_forecast.py`. P4-4b1 commits it as `docs/P4_CONFIRM_FC_SPEC.md`. A change after P4-4b1 is a new version of this file, recorded with its reason.

The module computes 17 of the 18 rows that `confirm_inference.ITEM_OF` gives to P4-4b: O29 to O44 and R9. O45 (the economic evaluation) is P4-4b2's; it stays `pending`. The texts it implements are the spec (`forecast`), the audit (`reports/P4_reports/p4_1_audit.md`, §1 rows O29 to O44 and R9), `docs/P4_CONFIRM_CONFIG.json` (`forecast`, `constants`, `contingencies`) and `docs/P4_CONFIRM_INF_SPEC.md` (the entry schema, §4). The builder resolves and records where this file is unclear (the item's message), and stops only as that rule says.

## 1. Rules for the code

### 1.1 Placement and imports
- One new module, `ofilt/drift/confirm_forecast.py`, and one new test file. No existing file changes; no C7-hashed file changes (`inference.py`, `sim.py`, `forecast.py`, `fctests.py`, `models/linear.py`, `tools/c7_mc.py`).
- The module imports only `__future__`, `dataclasses`, `math`, `typing`, `numpy`, `pandas`, and from the package `blind`, `fctests`, `forecast`, `models` (`REGISTRY`), `targets`, `spec` (`Spec`) and `confirm_inference` (`ITEM_OF`, `STATUSES`, `TICKERS`, `load_config`, `to_json`, `_plain`). It does not import `io`, `registry`, `sim`, `sim_full`, `calendar`, `schema`, `calib` or `inference`. It calls the engine as `forecast.walk_forward` and the importance table as `forecast.importance_table` (attribute access on the module, so that test 16 can patch them), and the factories as `models.REGISTRY[name]`.
- It opens, reads and writes no file itself. The configuration is read through `confirm_inference.load_config`. Each `forecast.walk_forward` call appends one line to the run registry, as the engine does by design (P27): synthetic runs to `registry.SYNTHETIC_PATH`, real runs to `RUN_REGISTRY.jsonl` (P4Q6).
- It draws no random number itself. Given the same inputs, its entries are identical (the registry's run ids are kept out of them, §4.3).

### 1.2 Static tests it must satisfy
As `docs/P4_CONFIRM_INF_SPEC.md` §1.2: `test_sim_b5` (never names the unguarded design core), `test_schema` (no column selection by prefix or pattern: columns named explicitly), `test_docs_d3b` (no tag name), `test_docs_d6` (no file written).

### 1.3 Read first (as text, in full)
`ofilt/drift/forecast.py`, `ofilt/drift/fctests.py`, `ofilt/drift/models/__init__.py`, `models/linear.py`, `models/ridge.py`, `models/gbm.py`, `ofilt/drift/registry.py`; `targets.add_masks`; `schema.select_features` and `schema.feature_sources`; `ofilt/drift/confirm_inference.py` (its §3.2 checks and `_plain`); the configuration's `forecast` and `constants`; the audit's rows O29 to O44 and R9; the spec's `forecast` block.

## 2. API

- `ROWS = ("O29", ..., "O44", "R9")` in the configuration's order: O29 to O35, R9, O36 to O44 (17 IDs). Every one has `ITEM_OF[id] == "P4-4b"`; O45 is not among them.
- `MAIN_CALL = ("M0", "M1", "M2", "M3", "M4", "M5")`; `M7_CALL = tuple(cfg["forecast"]["m7_call"]["models"])`, which is `("M7", "M1", "M0")`; `IMPORTANCE = tuple(cfg["forecast"]["importance"]["models"])`, which is `("M7",)`. The module defines `MAIN_CALL` and `M7_CALL` as literal tuples and test 1 checks `M7_CALL` and `IMPORTANCE` against the configuration.
- `MODEL_ROWS = {"O29": "M0", "O30": "M1", "O31": "M2", "O32": "M3", "O33": "M4", "O34": "M5", "O35": "M7"}`.
- `cw_reject_calibrated(stat, c) -> bool`: `stat > c`, strictly (AM-09). `c` is `cfg["constants"]["c_cw_cal"]`.
- `run_calls(dev, events, confirm=None, *, spec=None, factories=None) -> Calls` (§3).
- `forecast_rows(calls) -> dict`: `{id: entry}` for exactly `ROWS`, in that order (§5).
- `fill(doc, rows) -> dict`: a copy of `doc` (P4-4a's document) in which each entry of `rows` replaces the pending entry of the same ID (§6).
- `factories`: `None` in production. A test may pass a dict `{name: zero-argument factory}` whose keys are model names of the two calls; each replaces `models.REGISTRY[name]` for that name in both calls. The run script (P4-4c) never passes it.

## 3. The two calls

### 3.1 Provenance and frames
- First, exactly as `docs/P4_CONFIRM_INF_SPEC.md` §3.2: the provenance pair is checked (`ValueError` otherwise), then `blind.require_unblinded` runs on `dev` and on `confirm`. Nothing else runs before these checks.
- The frame: with `confirm`, `J = pd.concat([dev, confirm], ignore_index=True)` with `J.attrs = {"provenance": <confirm's provenance>}`; without it, `J = dev.copy()`. Then `T = targets.add_masks(targets.add_targets(J, spec), events, spec)`. The inputs are never modified.
- The first evaluation date `E0`: the first date of `confirm` in the confirmation mode (P4Q20); in the dev mode, no restriction (P4Q21).

### 3.2 The main call: M0 to M5
- `F_main = T.copy()` (attrs kept), with `usdjpy_bars` set to NaN on every row where it is finite and ≤ 0. Such a row makes `rv_per_bar` undefined, so M4 and M5 cannot use it: `models.linear.rv_threshold` raises once its date is in a training fold, and on a test row `highrv` would be coded 0 silently. Setting the source missing makes the engine drop the row for all six models, from training and from evaluation, as it drops any row with a missing feature source (one sample per call, P27), and it leaves the panel dates and so the fold geometry unchanged. The numbers of rows and dates so treated are reported in R9 (as P4Q14's counts).
- `forecast.walk_forward(F_main, {m: factory(m) for m in MAIN_CALL}, spec)`, with the default target (`abn_oc`) and the default seed (P4Q27), and no importance.

### 3.3 The M7 call: M7, M1, M0
- `forecast.walk_forward(T, {m: factory(m) for m in M7_CALL}, spec, importance=list(IMPORTANCE))` (P4Q22, P4Q23). `usdjpy_bars` is not changed here: no model of this call reads it.

### 3.4 Failures
A call that raises `ValueError` or `ArithmeticError` (for example `fold_starts` with fewer than 500 eligible training dates, or a rank-deficient training design) is a failed call: its reason is `f"walk_forward ({name}): {type(e).__name__}: {e}"` with `name` `"main"` or `"m7"`, and every row that needs it is not estimable with that reason (§5). Any other exception propagates.

### 3.5 The evaluation rows
For each successful call: `preds` and `folds` as `walk_forward` returns them; `ev` = the rows of `preds` dated on or after `E0` (all rows in the dev mode), with `ev.attrs = dict(preds.attrs)` and a fresh RangeIndex; and `folds_ev` = a copy of `folds` in which each row's `n_test` is the number of rows of `ev` with that row's model and fold (0 where none), so that `fctests.pesaran_timmermann` checks its base rates against the evaluated rows only. Every comparison, every `report_all` item and every model row uses `ev` (P4Q20, P4Q21).

### 3.6 `Calls`
A dataclass holding: `mode` (`"confirmation"` or `"dev"`), `E0` (a Timestamp, or None in the dev mode), `cfg`, `spec`, and for each of `"main"` and `"m7"`: `status` (`"ok"` or `"failed"`), `reason`, `preds`, `folds`, `ev`, `folds_ev`, `run_id` (from `folds.attrs`; None if failed); and `bars_le_0_rows`, `bars_le_0_dates` (the counts of §3.2, over all rows of `T`).

## 4. Entries

### 4.1 Schema
Each entry has exactly the keys of `docs/P4_CONFIRM_INF_SPEC.md` §4.2, in its order (`id`, `item`, `status`, `values`, `reason`, `n_rows`, `n_dates`, `lag`), `item` = `"P4-4b"`, and every value plain (§4.3 there), through `confirm_inference._plain`.

### 4.2 Contingencies (P4Q31)
- A row that needs a failed call is `not_estimable` with the call's reason; `values`, `n_rows`, `n_dates` and `lag` are None.
- A library call of `fctests` or `forecast.importance_table` that raises `ValueError` (including `fctests.PairingError`) or `ArithmeticError` makes its row `not_estimable`, with reason `f"{type(e).__name__}: {e}"`. Any other exception propagates.
- A non-finite float anywhere in a row's plain values makes the row `not_estimable`, reason `"non-finite estimate"`, values None, counts kept. The one exception: a Pesaran–Timmermann result with `defined` False carries `stat` and `p` as None (written so before the check), and does not make its row not estimable.

### 4.3 Runtime fields
No run id, time or path enters an entry. `Calls` keeps the run ids for P4-4c.

## 5. The rows

`m` is a call's name (`"main"` or `"m7"`). "The library result" is the dict a `fctests` function returns, made plain.

| ID | Status and values |
|---|---|
| O29 to O35 | One per model of `MODEL_ROWS`, from its call (M0 to M5: main; M7: m7). Estimated: `{"model", "call", "spec": spec.value(f"forecast.models.{model}"), "n_folds": the number of folds with at least one row of `ev` for the model, "first_eval_date", "last_eval_date"}`; `n_rows` and `n_dates` = the model's rows and distinct dates in `ev`; `lag` None. |
| R9 | Fixed: `{"scheme", "min_train_dates", "refit_every_dates", "pooled_across_tickers", "scaling"}` from the spec's `forecast` block; `"evaluation": {"mode", "from": E0 or None, "decision": "P4Q20" or "P4Q21"}`; and `"calls"`: for each of main and m7, `{"models": list, "status", "reason", "n_folds": len of that call's fold log for its first model (0 if failed), "first_test_date", "last_test_date" (from the fold log; None if failed), "eval_rows": the number of rows of `ev` for the call's first model, "eval_dates": its distinct dates}`; the main call adds `"bars_le_0_rows"` and `"bars_le_0_dates"`, the m7 call adds `"importance": list(IMPORTANCE)`. Counts None. R9 is fixed whether or not the calls failed. |
| O36 | The primary forecast comparison (AM-09): `r = fctests.clark_west(ev_main, "M3", "M2", spec)`. Estimated: the library result plus `"c_cw_cal": c`, `"reject_calibrated": cw_reject_calibrated(r["stat"], c)`, `"decision_reference": "calibrated"` and `"exploratory"`: False in the confirmation mode, True in the dev mode (P4Q21: the dev run shows both references, as exploratory). `n_rows` = `r["n_rows"]`, `n_dates` = `r["T"]`, `lag` = `r["lag"]`. |
| O37 | `fctests.clark_west(ev_main, "M4", "M3", spec)`: the library result (normal reference, one-sided); counts as O36. |
| O38 | `fctests.clark_west(ev_main, "M5", "M3", spec)`: as O37. |
| O39 | `fctests.clark_west(ev_m7, "M7", "M1", spec)`: as O37. |
| O40 | `fctests.diebold_mariano(ev_m7, "M7", "M1", spec)`: the library result (two-sided, squared-error loss); counts as O36. |
| O41 | `oos_r2_vs_M0`: `{"main": {model: fctests.oos_r2(ev_main, model, "M0")} for M1 to M5, "m7": {model: fctests.oos_r2(ev_m7, model, "M0")} for M7 and M1}` (each the library result). Counts None. A failed call's part is `None`, and `"failed"` (always present) maps each failed call's name to its reason; the row is estimated if at least one call succeeded, else not estimable with the main call's reason. |
| O42 | `oos_r2_vs_M1`: as O41 against `"M1"`: main for M0, M2 to M5; m7 for M7 and M0. |
| O43 | `pesaran_timmermann_with_training_base_rate`: `{"main": {model: fctests.pesaran_timmermann(ev_main, model, folds_ev_main)} for every model of MAIN_CALL, "m7": {...} for every model of M7_CALL}`, failed parts as O41. M0's results have `defined` False (its forecast has a constant sign). Counts None. |
| O44 | Permutation importance (P4Q23): `t = forecast.importance_table(K, "M7")`, where `K` is the m7 call's fold log restricted to the folds whose `test_start` is on or after `E0` (all folds in the dev mode). Values: `{"model": "M7", "table": t's rows as records (feature, rank, mean_dmse, sd_dmse, min_dmse, max_dmse, is_noise, exceeds_noise), "repeats", "n_folds", "folds_straddling_excluded": the number of folds with test_start < E0 ≤ test_end, 0 in the dev mode}`; `n_rows` = `t.attrs["n_rows"]`, `n_dates` None, `lag` None. A fold that straddles E0 is excluded because its permutation SSEs pool its dev and confirmation rows, which cannot be separated; its confirmation rows remain in O39 to O43. |

## 6. `fill`
`fill(doc, rows)` returns a deep copy of `doc` with `doc["rows"][id]` replaced by `rows[id]` for every `id` of `rows`. It raises `ValueError` if `rows`' keys are not exactly `ROWS`, if any replaced entry of `doc` is not `pending` or its item is not `"P4-4b"`, or if any entry of `rows` has a different `id` or item. No other entry changes; O45 stays pending.

## 7. Tests (`tests/test_p4_confirm_forecast.py`: exactly these 17)

### 7.1 Seeds, frames, registry and run time
- Seeds S_k = `Spec.load().seed` + 8,200,000 + k (disjoint from P4-3's + 8,000,000, P4-4a's + 8,100,000 and P4-4p's + 8,500,000 blocks, all k below 1,000).
- **SA** = `sim_full.Scenario(b=1.0, a2=0.6, delta_cc=1.5)`; **SN** = `sim_full.Scenario.not_estimable()`.
- **Calendars**: SHORT = `sim_full.dev_calendar()[-900:]` (so the first forecast falls in the dev part and a fold can straddle E0); TINY = `sim_full.dev_calendar()[-300:]` (too short for 500 eligible training dates).
- **Factories**: every test call passes `factories = {"M7": lambda: M7(grid=((2, 50),))}` (one candidate, so no tuning), to keep the run time down. Test 16 checks the production default by inspection, without running it.
- **Runs** (computed once, cached at module level): R1 = `run_calls` on `simulate(S1, SA, dev_dates=SHORT)` in the confirmation mode; R1b = the same again (for test 3); R2 = (S2, SN, SHORT), confirmation mode; R3 = (S3, SA) with the default dev calendar, dev mode; R4 = (S4, SA, TINY), dev mode.
- **Registry**: `setUpModule` patches `registry.SYNTHETIC_PATH` and `registry.REAL_PATH` (`unittest.mock.patch.object`) to two files in a `tempfile.TemporaryDirectory`, and `tearDownModule` undoes it; the cache records the synthetic file's line count before and after each run. No test touches `RUN_REGISTRY.jsonl` or the system temp registry.
- "Matches" means equal to the library call on the same inputs, after `_plain`, exactly. The file runs in under 300 s; the report gives its time.

### 7.2 The 17 tests
1. `test_rows_items_and_calls`: `ROWS` is the 17 IDs in the configuration's order, each `ITEM_OF` "P4-4b", O45 not among them; `M7_CALL` and `IMPORTANCE` equal the configuration's; `MAIN_CALL` is M0 to M5; `MODEL_ROWS` as §2; `cw_reject_calibrated(c, c)` is False and `cw_reject_calibrated(c + 1e-12, c)` is True.
2. `test_entry_schema_and_json` (R1): `forecast_rows` returns exactly `ROWS`, in order; each entry has the 8 keys in order, item "P4-4b", a status of `STATUSES` other than `pending`; `fill(infer(...), rows)` (P4-4a's `infer` on the same frames) serialises with `to_json`, contains neither `NaN` nor `Infinity`, and round-trips with `json.loads`.
3. `test_determinism_and_inputs_unchanged`: `forecast_rows(R1) == forecast_rows(R1b)`; R1's and R1b's `preds` are equal (`pandas.testing`, exact); the frames passed to `run_calls` for R1 are unchanged afterwards, attrs included.
4. `test_provenance_pairs_refused`: `ValueError` for the five refused pairs of P4-4a's test 5, each before any target is built (`blind.registered_labels()` unchanged) and with no registry line written.
5. `test_evaluation_restriction_and_protocol` (R1): `E0` is the confirmation frame's first date; each call's `ev` equals its `preds` restricted to dates ≥ E0, and has at least one row before the restriction is applied that is dated before E0 (SHORT puts the first forecast in the dev part); `folds_ev`'s `n_test` equals the per-(model, fold) counts of `ev`; R9's protocol values equal the spec's, its calls' fold counts and test dates equal the fold logs', and O29 to O35's counts equal `ev`'s.
6. `test_primary_clark_west` (R1): O36 matches `fctests.clark_west(ev_main, "M3", "M2", spec)` plus the four added keys; `reject_calibrated` equals `stat > 1.411608406163672` and, under SA, is True; `exploratory` is False.
7. `test_secondary_comparisons` (R1): O37, O38 and O39 match `clark_west` for (M4, M3), (M5, M3) and (M7, M1), and O40 matches `diebold_mariano` for (M7, M1), each on its call's `ev`.
8. `test_oos_r2_rows` (R1): O41 and O42 match `fctests.oos_r2` for every pair §5 lists (M7 against M0 among them, P4Q22); under SA, M3's pooled OOS R² against M1 is positive.
9. `test_pesaran_timmermann_rows` (R1): O43 matches `fctests.pesaran_timmermann(ev, model, folds_ev)` for every model of both calls, with `stat` and `p` None where `defined` is False; M0's entries have `defined` False.
10. `test_importance_row` (R1): O44 matches `forecast.importance_table` on the m7 fold log restricted to `test_start` ≥ E0, the noise column is in the table with `is_noise` True, and `folds_straddling_excluded` equals the number of the fold log's M7 folds with test_start < E0 ≤ test_end, recomputed in the test.
11. `test_bars_zero_rows_dropped` (R2): R9's main call has `bars_le_0_dates` 6 and `bars_le_0_rows` 18, recomputed in the test from the simulated confirmation frame; the main call's `preds` contain none of those dates; the m7 call's `preds` contain those of the dates that lie on or after its first test date and have at least one row that the engine's evaluation rule keeps (finite `abn_oc`, M7's feature sources present by `schema.feature_sources`, `excl_forecast_eval` False), recomputed in the test; O33, O34, O37 and O38 are estimated.
12. `test_dev_mode` (R3): mode "dev", `E0` None; every `ev` equals its `preds`; the last evaluated date is before 2022-01-01; O36 has `exploratory` True and both `p` and `reject_calibrated`; O44's `folds_straddling_excluded` is 0.
13. `test_call_failure_not_estimable` (R4): both calls failed, each reason starting `walk_forward (`; every row of `ROWS` except R9 is not estimable with a reason starting `walk_forward (`; R9 is fixed with both calls' status "failed".
14. `test_registry_routing`: each of R1, R1b, R2 and R3 added exactly 2 lines to the patched synthetic registry, R4 and test 4's refusals none; the patched real registry file does not exist; `RUN_REGISTRY.jsonl` in the repository has 0 bytes.
15. `test_fill_refuses_non_pending` (R1): `fill` replaces exactly the 17 entries and leaves every other entry, O45's included, equal to the input document's; `ValueError` if a target entry is not pending, if `rows` lacks an ID of `ROWS` or has an extra one, or if an entry's item is not "P4-4b".
16. `test_default_factories_are_the_registry`: by `ast` on the module's source and by inspection, with `factories=None` each model's factory is `models.REGISTRY[name]` (the test patches `forecast.walk_forward` with a recorder that raises after recording, so nothing runs, and checks the factories it received, the call's models and the `importance` argument).
17. `test_module_source`, by `ast`: imports only as §1.1 allows; no call of `open`, `read_csv`, `to_csv`, `read_bytes`, `read_text`, `write_text`, `write_bytes`, `to_parquet`, `to_pickle` or `to_excel`; none of the strings `load_dev`, `load_confirm`, `load_events`, `OFILT_DATA_DIR` and `RUN_REGISTRY`; it defines `run_calls`, `forecast_rows`, `fill`, `cw_reject_calibrated`, `ROWS`, `MAIN_CALL`, `M7_CALL`, `MODEL_ROWS` and `IMPORTANCE`.

## 8. Notes for the builder
- The item's message has a probe step (c.2) that runs the two calls once on (S1, SA, SHORT) with the test factories and prints what §5 uses: the fold geometry, E0, the counts, the keys of each library result, PT with `folds_ev`, the importance table, and the time of each call. It asserts nothing. Use it to settle details under "resolve and record".
- `walk_forward` drops a row for every model of a call when any model's feature source is missing; §3.2's NaN relies on that, and test 11 checks it.
- `fctests.pesaran_timmermann` raises `PairingError` if the fold log's `n_test` does not match the rows it is given: hence `folds_ev` (§3.5).
- If a test can pass only by departing from this file, or this file is wrong on a point a test depends on, stop and say which.
