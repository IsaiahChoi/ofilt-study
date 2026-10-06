# PASS3_STATUS.md

Pass 3 (calibration, dev still blinded), run per the Pass 3 builder prompt (2026-10-06) and the supervisor messages that follow it. Paths: REPO `~/Desktop/FX_Project/ofilt_pass1`, DATA `~/Desktop/FX_Project/data`, KIT3 `~/Desktop/FX_Project/files/pass3`, VENV `~/venvs/ofilt_p2`. Out of scope for all of Pass 3: RAW `~/Desktop/FX_Project/raw` and OUT `~/Desktop/FX_Project/build_out`.

## Progress

| Item | Status | Notes |
|---|---|---|
| P3-0 Setup, integrity, code survey | done; `checkpoint: P3-0` | Date gate 2026-10-06. arm64, macOS 26.6.2; VENV Python 3.12.4, numpy 2.4.4, pandas 3.0.2, scipy 1.17.1, scikit-learn 1.8.0, PyYAML 6.0.3, openpyxl 3.1.5; BLAS accelerate, LAPACK accelerate. HEAD `c9cea24` on `main`, tree clean, tags `pass1-final` only (lightweight). Five hashes agree three ways (computed, registry, prompt); DATA holds exactly the four expected files. BLIND_FIT_LOG 6 dev_real lines, SHA-256 `dad93285d2911abc6c7145c160d729df1126b24b439302bd8577cf407d397301`; RUN_REGISTRY.jsonl 0 bytes. Suite and slow tier pass (Test results). B7/B7b reports: structure only, no per-replication values. Code survey Q1–Q14 in the P3-0 report (`/tmp/p3_0.txt`). Saved prompt SHA-256 `018c489ff53db0aa069881874e0c4faea0e165a2e23ba02b875963b034dfee36`. Planned STOP for the supervisor's review |
| Pass 3 | in progress | |

## Next action

P3-1 (cost model and SESOI) waits for Isaiah's cost inputs and the open design questions DQ2–DQ8. Nothing of P3-1 has started.

## Decision log

> - DQ1.1 (Isaiah, 2026-10-06, on the supervisor's recommendation): Architecture.
>   - Pass 3's one real-data sealed fit, dev_real line 7, is a single `DevCalibrator` constructed in a single foreground process.
>   - Isaiah launches it himself in his own Terminal.app window, not in Claude Code:
>     - the Mac on mains power, with the lid open;
>     - under `caffeinate -i`;
>     - with `OFILT_RUN_SEALED=1` given as a prefix to that one command only, never exported;
>     - with an explicit `--real` flag.
>   - The calibrator's state is never written anywhere, so the run is never chunked or resumed.
>   - Every simulation that needs real residuals runs in that process.
> - DQ1.2 (Isaiah, 2026-10-06, on the supervisor's recommendation): Outputs.
>   - The real run writes and prints only aggregates stated in advance: counts, rates, Wilson intervals, means and standard deviations across replications, and named quantiles.
>   - It writes and prints none of the following:
>     - any per-replication value (estimate, standard error, t-statistic, p-value, rejection flag);
>     - any residual or fitted control;
>     - any calibrator attribute;
>     - any cache, pickle or figure.
>   - Reason: a replication's simulated estimate satisfies b̂*_r − b_sim = Σᵢ c_{r,i} ûᵢ, with c_r computable from the real predictors and the seed. Enough per-replication estimates therefore determine the residual vector, and, with the real y, b̂.
>   - Synthetic mode may keep per-replication values for its tests.
>   - At P3-0, the structure of the committed B7 and B7b reports is checked: key paths, types and lengths, no values. Any per-replication simulated estimates found there are a disclosure item for the pre-registration.
> - DQ1.3 (Isaiah, 2026-10-06, on the supervisor's recommendation): Verifiability.
>   - **Committed before the sanction.** The script and a run configuration are committed at a checkpoint. The configuration states:
>     - every cell, and the replication counts;
>     - a seed formula disjoint from the B7 and B7b seed blocks;
>     - the DK lags;
>     - the output fields;
>     - every decision rule, verbatim.
>   - **Refusal.** The real run refuses to start on a dirty tree.
>   - **Report.** It records HEAD and the SHA-256 of the configuration, the dev panel and the spec, with the expected values read from the registry.
>   - **Log assertions.** BLIND_FIT_LOG must have:
>     - 6 dev_real lines before the run;
>     - 7 immediately after the calibrator is constructed, before any simulation, with line 7 carrying AM-04's dev-panel hash and the script as caller;
>     - 7 at the end.
>     Any deviation aborts the run (STOP).
>   - **Static tests.** The script constructs exactly one DevCalibrator. It imports none of multiprocessing, concurrent.futures, joblib or subprocess. It serialises no calibrator attribute.
>   - **Target check before the run.** A code read confirms, and the script asserts, that the sealed fit's target is AM-03's: the 1306 hedge, the expanding past-only β, non-excluded rows. A target-only pre-flight gives the expected estimation-sample row and date counts, and the real run asserts that the calibrator's source dates equal them.
> - DQ1.4 (Isaiah, 2026-10-06, on the supervisor's recommendation): Crash containment and salvage.
>   - The tasks run in a fixed order, T1 first and T3 last.
>   - Each task's aggregates are written and flushed as soon as it completes.
>   - An exception in a task is recorded by its class and line number only, with the message suppressed. The run then continues with the next task.
>   - If any task fails, a second sanctioned fit (line 8) reruns the identical committed configuration with identical seeds. Every task completed in line 7 must reproduce exactly (same platform; Flag 16).
>   - New seeds are never used.
> - DQ1.5 (Isaiah, 2026-10-06, on the supervisor's recommendation): Rehearsal. Before the sanction, the script runs end to end in synthetic mode:
>   - with the populated real-target fingerprint registry, so that the guard's cost is realistic (B7b's dry run was not);
>   - on a stand-in with the real estimation sample's shape;
>   - with the log redirected to a temporary file, and the real BLIND_FIT_LOG's SHA-256 asserted unchanged;
>   - twice, with byte-identical outputs apart from runtime fields.
>   Each task's runtime is recorded, and the expected duration of the real run is stated before the sanction.
> - DQ1.6 (Isaiah, 2026-10-06, on the supervisor's recommendation): Scope.
>   - The one run covers T1, T2, T3, the TOST-viability part of T5, and T6.
>   - Some binding numbers depend on the primary inference method: T2's power and MDE80, T3's H1 column and T5's viability. Each is computed under every method that the T1 and T4 rules can select:
>     - Driscoll–Kraay with the normal reference;
>     - the stationary block bootstrap (mean block 5);
>     - the simulation-calibrated critical value.
>     Their exact definitions are set by DQ3.
>   - Information-only extras from the same fits: H3 size, and the DK SE/sd, coverage and bias.
> - DQ1.7 (Isaiah, 2026-10-06, on the supervisor's recommendation): The sanction is separate.
>   - DQ1.1–DQ1.6 do not sanction dev_real line 7.
>   - Isaiah sanctions it at P3-4, in a later message, against the SHA-256 of the final committed configuration. The sanction carries that message's date.
>   - Until then, `OFILT_RUN_SEALED` stays unset in every builder command, and the builder never runs any script's real mode.

- Pass 3 builder prompt adopted (Isaiah, 2026-10-06).

## Test results

**P3-0 e** (`env -u OFILT_RUN_SEALED`, VENV, `OFILT_DATA_DIR` = DATA):
- Suite: `Ran 247 tests in 325.651s`; `OK (skipped=5)`. Pass 2 took 245–273 s.
- Skipped (5):
  - `test_project_claims (test_docs_d6.TestProjectSetup.test_project_claims) ... skipped 'Claude Project not mounted'`
  - `test_draw_passes_guard_and_contract (test_sim_b5.TestRealDev.test_draw_passes_guard_and_contract) ... skipped 'real-data sealed fit is opt-in (OFILT_RUN_SEALED=1)'`
  - `test_logged_and_silent (test_sim_b5.TestRealDev.test_logged_and_silent) ... skipped 'real-data sealed fit is opt-in (OFILT_RUN_SEALED=1)'`
  - `test_first_reps_bit_identical (test_validation_c7.TestSlowReproduce.test_first_reps_bit_identical) ... skipped 'slow tier (OFILT_SLOW=1)'`
  - `test_last_reps_bit_identical (test_validation_c7.TestSlowReproduce.test_last_reps_bit_identical) ... skipped 'slow tier (OFILT_SLOW=1)'`
- B6: the suite rewrote `reports/B6_coverage.json` only; restored with `git checkout -- reports/B6_coverage.json`; `git status --porcelain` then empty.
- Slow tier (`OFILT_SLOW=1 … python -m unittest tests.test_validation_c7 -v`): `Ran 6 tests in 32.037s`; `OK`. The prompt expects about 21 s.
- After both runs: BLIND_FIT_LOG SHA-256 unchanged, RUN_REGISTRY.jsonl 0 bytes, `git status --porcelain` empty.

## Test changes

None.

## Flags

- (P3-0, for the supervisor) T3 and DQ1.2: every `walk_forward` call appends one line to a run registry. For synthetic provenance, which DevCalibrator draws carry, the line goes to `<system temp>/ofilt_RUN_REGISTRY_synthetic.jsonl` (registry.py:34, 41-46). It holds the input frame's `data_sha256` (the frame contains `y_sim`), the seed and per-fold row counts, and each call runs `git rev-parse HEAD` and `git status` (registry.py:87-90). In the real run, that is a per-replication write outside DQ1.2's list of outputs.
- (P3-0, for the supervisor) DQ1.3 static test: importing the analysis modules loads `joblib`, `multiprocessing` and `concurrent.futures` (`ofilt.drift.models` imports `gbm`, which imports sklearn). `registry.py` and `_guards_fallback.py` import `subprocess`. "Imports none of …" can therefore only be tested on the script's own import statements, not on `sys.modules`.
- (P3-0, for the supervisor) DQ1.3 target pre-flight: the sealed fit's estimation sample also requires `usdjpy_ret`, `eurusd_ret`, `spy_oc` and `copx_oc` to be non-missing (`spec.require_nonmissing` and the feature sources, inference.py:93-98), not only the exclusions, β and `abn_oc`. A strictly target-only count reproduces the sample only if those predictors are never missing where the target and β exist. A count that combines the predictor-missingness mask with the target mask needs a ruling. The calibrator exposes its source-date count as `T`; its row count is reachable only through private attributes.
- (P3-0, for the supervisor) T3 confirmation structure: `walk_forward` always starts forecasting after the 500th eligible training date (`forecast.min_train_dates`) and has no argument for a later evaluation start; `tools/c7_mc.py` trains its first fold on 500 dates. A dev-length history with evaluation on T_conf dates needs a stated arrangement (`fctests.pair` accepts any row subset applied to both models).
- (P3-0, for the supervisor) SESOI denominator: no code defines the "partialled overnight USD/JPY" of PLAN §4.5. Its regressors, unit (row or date) and sample need a definition before P3-1.
- (P3-0, for the supervisor) T6: no routine applies the spec's FX winsorisation bounds (only `Spec.winsor_bounds()`). Huber exists (`inference.fit_huber`, which takes a Design built from a draw). Where a winsorised fit lives needs a decision; `inference.py` is C7-hashed.
- (P3-0, for the supervisor) T5 data: there is no tick-size, spread or cost code for the miners. The only price-grid tools (`tools/p2_5_tick_1306.py`, `tools/p2_3b_d8_zero_gate.py`) cover the 1306 hedge and read RAW or OUT, both outside Pass 3's scope. Miner price levels in DATA are the PROVENANCE columns `open`, `close` and `prev_close` (target-input prices), so the source of T5's tick sizes and grids needs a decision.
- (P3-0, for the supervisor) DQ1.5 rehearsal: a populated fingerprint registry needs `io.load_dev` and `targets.add_targets` in the rehearsal process. That means real target contact: β and the constructed targets are computed on the dev panel and registered, never printed. It needs confirming as sanctioned for P3-3.
- (P3-0, for the supervisor) Pins that line 7 and the AM-07 switch will break, to be listed as P3-6 test-change rows: `test_docs_d3.py:66` (6 lines) and `:69` (every panel hash is the Pass 1 dev hash); `test_docs_d3b.py:41` (6 lines) and `:39` (AM-01..AM-05 only); `test_docs_d2.py:41-43` (`PENDING_COSTS`; "Pass 4" in viability), if the SESOI or viability text changes; and the C7 key, on any spec edit. The byte- or hash-pinned documents (`DECISIONS_P14_onward.md`, `PLAN.md`, `DECISIONS_P58_onward.md`) state the six sealed fits.
- (P3-0, for the supervisor) DQ1.2 disclosure (step f): the committed B7 and B7b reports hold no per-replication values, only per-cell aggregates. These include per-cell means of the simulated estimates (B7 `mean_b`, B7b `bias`), each one linear functional of the residual vector given the seeds.

## Blinding attestation

- **P3-0 (Pass 3 builder prompt, 2026-10-06)**, by category:
  - DATA: `panel_dev.csv`, `events_firm.csv`, `events_boj.csv` and `archive/panel_dev_736636031ca1.csv` hashed with `shasum -a 256`; DATA and DATA/archive listed (names and sizes only). No data file was opened by any viewer.
  - `panel_dev.csv` was read only by the suite's structural and target-only tests (the step e run and the run inside the P3-0 checkpoint). The slow tier is synthetic.
  - RAW and OUT: untouched (not read, listed, hashed, searched or written).
  - BLIND_FIT_LOG: metadata read by script (line, utc, provenance, hash prefixes, n_rows_input, caller) and hashed.
  - B7 and B7b reports: structure only (key paths, types, list lengths; markdown counts), no values. From the C7 reports only `key.spec_sha256` was read; from `docs/PASS2_INPUTS.json` only hashes.
  - Code survey: code, tests, spec and docs only. The spec holds the predictor-only A6 values (winsorisation bounds, rv_per_bar median).
  - KIT3: the saved prompt was hashed and its step c table parsed for the listed hashes.
  - `OFILT_RUN_SEALED` was unset throughout: `printenv` printed nothing, and every Python command ran under `env -u OFILT_RUN_SEALED`. No script's real mode was run.
  - No computation related a predictor to a target. BLIND_FIT_LOG still has 6 dev_real lines (SHA-256 unchanged), and RUN_REGISTRY.jsonl is 0 bytes.

## Deviations

- P3-0 c: the first run of the hash-check script (`/tmp/p3_0_hashes.py`) printed "listed in prompt: None" for the four DATA rows, and an overall False. Its table parser kept only rows starting with ``| ` ``, so it dropped the rows starting with `| DATA`. Every computed-vs-registry comparison in that run was True. The parser was fixed to keep every table body row, and the rerun agreed three ways on all five files. Both runs are in the P3-0 report.
- P3-0 e: the post-run check command assigned a shell variable holding the BLIND_FIT_LOG baseline hash, typed by hand. The variable was never used; the comparison read the baseline from step d's printed output.
