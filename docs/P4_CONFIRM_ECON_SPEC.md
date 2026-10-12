# P4_CONFIRM_ECON_SPEC: the confirmation module, the economic evaluation (P4-4b2; P4Q37)

Version 1, written by the supervisor chat that began on 2026-10-11 with handoff H9, for P4-4b2. It specifies `ofilt/drift/confirm_economic.py` and its tests `tests/test_p4_confirm_economic.py`. P4-4b2 commits it as `docs/P4_CONFIRM_ECON_SPEC.md`. A change after P4-4b2 is a new version of this file, recorded with its reason.

The module computes row O45, the last of the 18 rows that `confirm_inference.ITEM_OF` gives to P4-4b. The texts it implements are D2.3 to D2.5 and D2.8 (`PASS3_STATUS.md`, Decision log, DQ2), PLAN §4.5, the configuration's `economic_evaluation` (P4Q24, P4Q25), `docs/P3_COST_INPUTS.json`, the cost arithmetic of `tools/p3_1_sesoi.py` (`costs` and the helpers it calls), and the entry schema of `docs/P4_CONFIRM_INF_SPEC.md` §4. The builder resolves and records where this file is unclear, and stops only as that rule says.

## 1. Rules for the code

### 1.1 Placement and imports
- One new module, `ofilt/drift/confirm_economic.py`, and one new test file. No existing file changes; no C7-hashed file changes.
- The module imports only `__future__`, `dataclasses`, `fractions`, `hashlib`, `json`, `math`, `typing`, `numpy`, `pandas`, and from the package `blind`, `targets`, `spec` (`Spec`, `REPO_ROOT`), `confirm_inference` (`ITEM_OF`, `load_config`, `_plain`) and `confirm_forecast` (`Calls`, `_check_inputs`). It does not import `io`, `forecast`, `fctests`, `models`, `registry`, `sim`, `sim_full`, `calendar`, `schema` or anything under `tools/` (`tools/p3_1_sesoi.py` imports `io`).
- It writes no file and draws no random number. Besides what `Spec.load` and `confirm_inference.load_config` read, it reads exactly one file, the cost inputs, with one `Path.read_bytes` call in `load_cost_inputs`.
- The cost arithmetic is a re-implementation of `tools/p3_1_sesoi.py`'s `costs`, operation for operation (§3), so that test 2 can compare the two on the same rows.

### 1.2 Static tests it must satisfy
As `docs/P4_CONFIRM_INF_SPEC.md` §1.2 (`test_sim_b5`, `test_schema`, `test_docs_d3b`, `test_docs_d6`). The literal column names it uses (`open`, `close`, `beta`, `date`, `ticker`, `abn_oc`) are named explicitly. `open` and `close` are cost inputs only (P4Q2's allowlist).

### 1.3 Read first (as text)
`tools/p3_1_sesoi.py` (`load_inputs`, `_segment`, `factor`, `dev_table`, `tick`, `traded`, `half_tick_bp`, `side_ticks`, `side_ticks_table`, `costs`) and `tests/test_p3_1_sesoi.py` (its cost tests); `docs/P3_COST_INPUTS.json` in full; `PASS3_STATUS.md` D2.3 to D2.5 and D2.8; `ofilt/drift/confirm_forecast.py` (`run_calls`, `Calls`, `CallResult`, `_check_inputs`); the configuration's `economic_evaluation`; the audit's row O45 and gaps G16 and G17.

## 2. API

- `COST_INPUTS_PATH = REPO_ROOT / "docs" / "P3_COST_INPUTS.json"`; `COST_INPUTS_SHA256 = "a2bbca432e5398a732c9c1bfb7a12106c5474a10b027d4aa1757f5a27c2f8dc6"`.
- `CASES = ("primary", "low", "high")`; `MODELS = ("M3", "M2")`.
- `load_cost_inputs(path=None) -> dict`: reads the bytes (default `COST_INPUTS_PATH`); `ValueError` unless their SHA-256 is `COST_INPUTS_SHA256`; then `check_cost_inputs` on the decoded dict; returns it.
- `check_cost_inputs(obj) -> None`: `ValueError` if a key the tool's `load_inputs` requires is missing (the same keys, the same cases of the case-valued keys, and the three tickers in `price_factor`, `dev_table` and `primary_table`).
- `round_trips(px, inputs) -> dict`: §3.
- `pnl_bp(y, yhat, rt) -> (gross, net)`: per row, `s = np.sign(yhat)`, `gross = 1e4 * s * y`, `net = gross - rt * np.abs(s)` (a zero forecast takes no position and pays no cost).
- `economic_px(calls, dev, events, confirm=None, *, spec=None) -> (R, R2, px)`: §4.1's rows and price frame (used by `economic_row`; raises as §4.1 says).
- `economic_row(calls, dev, events, confirm=None, *, spec=None, inputs=None) -> dict`: the O45 entry (§4). `calls` is `confirm_forecast.run_calls` on the same three frames; `inputs=None` means `load_cost_inputs()`. A test may pass another inputs dict (§6); the run script (P4-4c) never does.
- `fill(doc, entry) -> dict`: a deep copy of `doc` (made with `_plain`) with `doc["rows"]["O45"]` replaced by `entry`; `ValueError` unless the document's O45 is a pending P4-4b entry and `entry` has id O45 and item P4-4b.

## 3. `round_trips(px, inputs)`

`px` has columns `date`, `ticker`, `open`, `close`, `beta` (one row per evaluated name-day). The function follows `tools/p3_1_sesoi.costs` exactly: the Flag 4 windows from `flag4_windows`; per case the commissions `c_m`, `c_h`, impacts `imp_m`, `imp_h`, short cost `s` and the 1306 half tick; the primary `x_m` = max(`imp_m`, half tick) per side under `primary_table`, averaged per ticker over its rows outside the windows and over both sides, then assigned to each row by its ticker, with `x_h = max(imp_h, half tick 1306)`; the low `x_m = imp_m`, `x_h = imp_h`; the high `x_m = imp_m + 0.5 (half tick open + half tick close)` under each row's dev table (`ValueError` if any traded price exceeds its table's last bound), `x_h = imp_h + half tick 1306`; traded price = stored price ÷ f (`price_factor`); `rt = 2 (c_m + x_m) + beta · 2 (c_h + x_h) + s`.

It returns, per case, `{"rt": rt (an array, one per row), "miner_commission", "miner_execution", "hedge_leg", "short", "mean_rt", "c_m", "c_h", "x_h", "s"}` with the tool's definitions, plus `"x_m_by_ticker"` (primary: the per-ticker averages; high: the per-ticker means of the row values; low: `imp_m` for every ticker), and `"beta_bar"`. It computes each case independently, so that a `ValueError` in one case (a price above a table's bound, a date no segment covers) does not stop the others: the failed case is returned as `{"error": f"{type(e).__name__}: {e}"}`.

## 4. The row

### 4.1 Rows and inputs
- First, `confirm_forecast._check_inputs(dev, confirm)` (the provenance pair, then the guard). Then the frame `T` exactly as `confirm_forecast` §3.1 builds it, and `E0`.
- If the main call failed, the entry is `not_estimable` with its reason (counts None). Otherwise `R` = the rows of `calls.main.ev` with model M3, sorted by (date, ticker); `R2` the same for M2. If `R` is empty: `not_estimable`, reason `"no rows"`, counts 0 and 0.
- The keys (date, ticker) of `R` and `R2` must be equal (one call's sample), and each must match exactly one row of `T`; else `ValueError` (a bug, not a contingency). `R`'s `y` must equal `T`'s `abn_oc` at those keys exactly; else `ValueError`.
- `px` = `T`'s `date`, `ticker`, `open`, `close` and `beta` at those keys, in `R`'s order: each row's own β and its own prices (D2.8, P4Q25).

### 4.2 Values
`status` estimated; `values`:
- `"models": ["M3", "M2"]`, `"call": "main"`, `"mode": calls.mode`, `"from": E0` (None in the dev mode), `"aggregation": cfg["economic_evaluation"]["aggregation"]`, `"decisions": ["P4Q24", "P4Q25"]`;
- `"break_even_bp"`: `{"M3": mean gross of M3, "M2": mean gross of M2, "difference": M3 minus M2}`, pooled over the rows (per name-day);
- `"traded_share"`: per model, the share of rows with a non-zero forecast;
- `"round_trip_bp"`: per case, the components and `mean_rt` of §3 (without the `rt` array), or None if the case failed;
- `"x_m_by_ticker"`: per case, §3's per-ticker values, or None if failed; `"beta_bar"`: the mean β of the rows;
- `"net_bp"`: per model, per case, the mean of `net` from `pnl_bp(y, yhat, rt_case)`, or None if the case failed;
- `"cases_failed"`: `{case: error}` for the failed cases (empty if none);
- `"sesoi_locked"`: `cfg["constants"]["sesoi"]`, for reference (P4Q25: the locked SESOI is unchanged).

`n_rows` = len(R), `n_dates` = R's distinct dates, `lag` None. Every value plain (`_plain`); a non-finite float anywhere makes the entry `not_estimable`, reason `"non-finite estimate"`, values None, counts kept. The entry has the 8 keys of `docs/P4_CONFIRM_INF_SPEC.md` §4.2, item "P4-4b".

## 5. Not in scope
Threshold variants (exploratory, D2.8), per-ticker P&L (P4Q24 chose pooled) and any standard error of the break-even.

## 6. Tests (`tests/test_p4_confirm_economic.py`: exactly these 14)

### 6.1 Seeds, frames, registry and run time
- Seeds S_k = `Spec.load().seed` + 8,300,000 + k (disjoint from + 8,000,000, + 8,100,000, + 8,200,000 and + 8,500,000, all k below 1,000).
- **SA** = `sim_full.Scenario(b=1.0, a2=0.6, delta_cc=1.5)`. **SHORT** = `sim_full.dev_calendar()[-900:]`; **TINY** = `sim_full.dev_calendar()[-300:]`.
- **Prices.** The simulator starts 5706 at a stored price of 3,000, which `price_factor` (1/10 from 2017-09-27) makes a traded price near 30,000, at the tables' last bound. The tests therefore use frames in which 5706's `open`, `close` and `prev_close` are multiplied by 0.1 (copies, attrs kept): these columns enter no target, feature or forecast, only the costs.
- **The M7 call.** Every `run_calls` in the tests passes `factories={"M7": ZeroM7}`, where `ZeroM7` is a `forecast.ForecastModel` subclass defined in the test file with `name = "M7"`, `features = ()`, a no-op `fit` and a zero `predict`, and no `test_noise`: O45 does not use the M7 call, and this keeps its run time to seconds.
- **Runs** (cached at module level): E1 = (S1, SA, SHORT, scaled), confirmation mode; E3 = (S3, SA, the default dev calendar, scaled), dev mode; E4 = (S4, SA, TINY, scaled), dev mode (both calls fail).
- **Registry**: as `docs/P4_CONFIRM_FC_SPEC.md` §7.1 (both paths patched to a temporary folder for the module).
- "Recomputed in the test" means from `calls.main.ev`, the test's own `T` and `tools/p3_1_sesoi.py`, never from the module's internals. The file runs in under 120 s; the report gives its time.

### 6.2 The 14 tests
1. `test_cost_inputs_pin_and_refusal`: the file has `COST_INPUTS_SHA256`; `load_cost_inputs()` equals its decoded content; a copy with one byte changed raises `ValueError`; a copy with the right hash cannot be made, so the missing-key refusal is tested by calling the key check on the decoded dict with `flag4_windows` removed (the module exposes it as `check_cost_inputs(obj)`, which `load_cost_inputs` calls).
2. `test_round_trips_match_the_tool` (E1): on E1's `px`, for each case, `mean_rt`, `miner_commission`, `miner_execution`, `hedge_leg`, `short`, `c_m`, `c_h`, `x_h` and `s` equal `tools/p3_1_sesoi.costs(px, inputs)`'s within 1e-12, `beta_bar` too, and the primary per-ticker `x_m` equals its `detail["primary_xm"]`, the high its `detail["high_xm"]`.
3. `test_round_trips_hand_computation`: a hand-built `px` of six rows (two dates, three tickers, after 2017-09-27, prices chosen on each table's bands) gives, for each case, the per-row `rt` computed by hand in the test from the cost file's numbers.
4. `test_pnl_bp`: hand arrays with a zero forecast: gross `1e4 * sign * y`, and the zero-forecast row has gross 0 and net 0.
5. `test_entry_schema_and_fill` (E1): the entry's 8 keys in order, id O45, item P4-4b, status estimated; `fill(confirm_forecast.fill(infer(...), forecast_rows(calls)), entry)` leaves no entry of item P4-4b pending, changes nothing else, serialises with `to_json` without `NaN` or `Infinity`, and round-trips; `fill` raises `ValueError` if O45 is not pending or the entry's id is not O45.
6. `test_break_even_and_difference` (E1): the three break-evens equal `1e4 * mean(sign(yhat) * y)` over the M3 and M2 rows of `calls.main.ev`, recomputed in the test, within 1e-12, and the difference is their difference; `traded_share` as recomputed.
7. `test_net_pnl` (E1): each `net_bp[model][case]` equals the mean of `1e4 * sign(yhat) * y - rt * |sign(yhat)|`, with `rt` from the tool's arithmetic recomputed in the test (`costs`' formula on the same `px`), within 1e-9.
8. `test_rows_beta_and_prices` (E1): `n_rows` and `n_dates` equal the M3 rows of `calls.main.ev`; every row is dated on or after E0; `px`'s β, open and close (exposed as `economic_px(calls, dev, events, confirm)`, which `economic_row` uses) equal the test's `T` at the same keys; `beta_bar` equals their mean β.
9. `test_dev_mode` (E3): mode "dev", `from` None, every row dated before 2022-01-01, status estimated.
10. `test_main_call_failed` (E4): the entry is not estimable with the main call's reason (starting `walk_forward (`), counts None.
11. `test_cost_case_failure`: with E1's calls and a copy of E1's scaled frames in which the `open` of one 5706 row that is among the evaluated rows is set to 1e7 (the targets do not change, so E1's calls still match), the primary and high cases are in `cases_failed` with a reason starting `ValueError`, their `round_trip_bp`, `x_m_by_ticker` and `net_bp` entries None; the low case and the break-evens are computed; status estimated.
12. `test_mismatched_frames_refused` (E1): `economic_row(calls, …)` with frames whose `y_oc` differs on one evaluated row (so `abn_oc` differs) raises `ValueError`.
13. `test_provenance_pairs_refused`: the five refused pairs of P4-4a's test 5 raise `ValueError` from `economic_row` (with E1's calls), before any target is built (`blind.registered_labels()` unchanged).
14. `test_module_source`, by `ast`: imports only as §1.1 allows (nothing from `tools`); no call of `open`, `read_csv`, `to_csv`, `read_text`, `write_text`, `write_bytes`, `to_parquet`, `to_pickle` or `to_excel`; exactly one call of `read_bytes`; none of the strings `load_dev`, `load_confirm`, `load_events`, `OFILT_DATA_DIR` and `RUN_REGISTRY`; it defines `load_cost_inputs`, `check_cost_inputs`, `round_trips`, `pnl_bp`, `economic_px`, `economic_row`, `fill`, `COST_INPUTS_PATH`, `COST_INPUTS_SHA256`, `CASES` and `MODELS`.

## 7. Notes for the builder
- The item's message has a probe step (c.2): on E1's frames (scaled) with the `ZeroM7` factory, it runs `run_calls`, prints the main call's evaluated M3 rows' count, the traded price ranges per ticker and side, `tools/p3_1_sesoi.costs` on `px` per case, and the same on the unscaled frames. It asserts nothing.
- `tools/p3_1_sesoi.py` may be imported by the tests and the probe (add `tools` to `sys.path`, as `tests/test_p3_1_sesoi.py` does); never by the module.
- If a test can pass only by departing from this file, or this file is wrong on a point a test depends on, stop and say which.
