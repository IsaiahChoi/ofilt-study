# PASS3_STATUS.md

Pass 3 (calibration, dev still blinded), run per the Pass 3 builder prompt (2026-10-06) and the supervisor messages that follow it. Paths: REPO `~/Desktop/FX_Project/ofilt_pass1`, DATA `~/Desktop/FX_Project/data`, KIT3 `~/Desktop/FX_Project/files/pass3`, VENV `~/venvs/ofilt_p2`. Out of scope for all of Pass 3: RAW `~/Desktop/FX_Project/raw` and OUT `~/Desktop/FX_Project/build_out`.

## Progress

| Item | Status | Notes |
|---|---|---|
| P3-0 Setup, integrity, code survey | done; accepted by Isaiah 2026-10-06 | `checkpoint: P3-0`. Date gate 2026-10-06. arm64, macOS 26.6.2; VENV Python 3.12.4, numpy 2.4.4, pandas 3.0.2, scipy 1.17.1, scikit-learn 1.8.0, PyYAML 6.0.3, openpyxl 3.1.5; BLAS accelerate, LAPACK accelerate. HEAD `c9cea24` on `main`, tree clean, tags `pass1-final` only (lightweight). Five hashes agree three ways (computed, registry, prompt); DATA holds exactly the four expected files. BLIND_FIT_LOG 6 dev_real lines, SHA-256 `dad93285d2911abc6c7145c160d729df1126b24b439302bd8577cf407d397301`; RUN_REGISTRY.jsonl 0 bytes. Suite and slow tier pass (Test results). B7/B7b reports: structure only, no per-replication values. Code survey Q1–Q14 in the P3-0 report (`/tmp/p3_0.txt`). Saved prompt SHA-256 `018c489ff53db0aa069881874e0c4faea0e165a2e23ba02b875963b034dfee36`. Planned STOP for the supervisor's review |
| P3-0b Records and pre-flight facts | done; accepted by Isaiah 2026-10-06 | `checkpoint: P3-0b`. Decisions recorded (P3-0 accepted; the rerun-once rule; step f). P3-0 report copied byte for byte to `reports/P3_0_report.txt`. `tools/p3_0b_preflight.py` (dev only, facts only; no rule applied) ran once on the real dev panel and wrote `reports/P3_0b_preflight.md`: Part A, the AM-03 estimation sample (the counts DQ1.3 needs; T_source); Part B, the miners' price levels, grids and one tick in bp. Synthetic tests in `tests/test_p3_0b_preflight.py` (3, OK). Report `/tmp/p3_0b.txt`. Planned STOP for the supervisor's review |
| P3-1 Cost model and SESOI | done | `checkpoint: P3-1`. P3-0b acceptance, the cost inputs and DQ2 (D2.1–D2.9) recorded. `docs/P3_COST_INPUTS.json`; `tools/p3_1_sesoi.py` (dev only: mean \|ẽ\|, β̄, the round trips and the primary, low and high SESOI) ran once on the real dev panel, all three gates True, and wrote `reports/P3_1_sesoi.md`; synthetic tests in `tests/test_p3_1_sesoi.py` (5, OK). Report `/tmp/p3_1.txt`. Planned STOP: supervisor review and Isaiah's approval of the computation (D2.9) |
| Pass 3 | in progress | |

## Next action

P3-1 awaits the supervisor's review and Isaiah's approval of the computation (D2.9). P3-2 also waits for DQ3, DQ4 and DQ7.

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

> - P3-0 accepted (Isaiah, 2026-10-06, on the supervisor's recommendation).
>   - Checkpoint `2ac5a85b51d8604ccad84cf877baf45ff2d45f76`.
>   - This includes the step c deviation. On the first run, the hash-check script's table parser dropped the rows beginning `| DATA`, so it printed "AGREE: False", although every computed-versus-registry comparison was True. The parser was fixed, and the rerun agreed three ways.
>   - The deviation is accepted as recorded, as P69 did for the P2-5 parser bug.
> - Standing rule (Isaiah, 2026-10-06, on the supervisor's recommendation): rerun once after a script bug.
>   - If one of the builder's own check scripts fails because of a bug in that script, rather than because of the condition it checks, the builder may fix the script and rerun it once.
>   - Both runs and the fix are recorded in the report and in Deviations.
>   - A failure on the rerun is a STOP.
> - P3-0 step f (Isaiah, 2026-10-06, on the supervisor's recommendation): the Pass 1 sealed-run reports.
>   - The committed B7 and B7b reports hold per-cell aggregates only, with no per-replication values.
>   - The pre-registration states this; nothing needs remedying.

> - P3-0b accepted (Isaiah, 2026-10-06, on the supervisor's recommendation).
>   - Checkpoint `022260254ff9b76739120fd51eed8d0e22656397`.
>   - The acceptance covers the recorded deviations P3-0 e (an unused shell variable holding a hand-typed hash), P3-0b d (the finiteness boolean, mirroring `inference.py:130-131`) and P3-0b b.1 (the checkpoint name moved to the Notes cell).
>   - Part A: 4,192 kept rows on 1,439 dates (equal to Pass 1's B7 T_source), from 2016-01-26 to 2021-12-30. The four predictors remove no row, so the target-only pre-flight count equals the sealed fit's sample. The sealed run asserts these two numbers.
>   - Part B: every detected grid agrees with the TSE tick tables applied to traded prices, where stored price = traded price × f: f = 10 for 5711 before 2016-09-28; f = 2 for 5713 before 2017-09-27; f = 1 for 5706 before 2017-09-27 and f = 1/10 from that date (because of 5706's 10:1 split, ex-date 2026-09-29); f = 1 otherwise. 5711 and 5706 follow the standard table and 5713 the TOPIX100 table.
> - Cost inputs (Isaiah, 2026-10-06). Primary / low / high, fixed on economic grounds before any SESOI ingredient was computed:
>   1. Notional per name: JPY 10,000,000 / 1,000,000 / 100,000,000 (assumption).
>   2. Commission per side, miners, consumption tax included: 4.3 / 0 / 8 bp. Primary: IBKR Japan Tiered, blended across Tier I (0.05%) and Tier II (0.04%) at the strategy's own monthly volume, plus the TSE exchange and clearing fees (about 0.27 bp). Low: SBI "Zero Revolution" or Rakuten's zero course. High: IBKR Fixed (0.08%).
>   3. Commission per side, 1306: the same as item 2.
>   4. Auction impact per side, miners: 2 / 0.5 / 8 bp (assumption, checked against JPX closing-auction shares and square-root-law evidence on TSE data).
>   5. Auction impact per side, 1306: 1.5 / 0.5 / 4 bp (assumption).
>   6. Intraday short cost per day: 0 / 0 / 1 bp (day-trade margin at SBI, Rakuten and Matsui: 0% interest and 0% lending fee; the high covers standard margin at 1.10% a year and special short fees).
>   - Source: Isaiah's cost note of 2026-10-06. It stays outside the repository and the Claude Project because it quotes post-dev prices.
>   - Note (supervisor): the primary pairs IBKR commissions with a zero-cost day-trade short. A single-account primary would differ by at most 1 bp a day (item 6's range).
> - DQ2 (Isaiah, 2026-10-06, on the supervisor's recommendation): the cost model and the SESOI, defined before any of their ingredients is computed.
>   - D2.1 The overnight FX regressor. ẽ is the OLS residual of `usdjpy_ret` on the primary design's other regressors (ticker fixed effects, `eurusd_ret`, and ticker-specific `spy_oc` and `copx_oc`), fitted once on the AM-03 estimation sample (the P3-0b Part A rule). The SESOI denominator is mean |ẽ| over those rows (row weighting). This is a predictor-only regression; target columns select rows only through availability.
>   - D2.2 The hedge ratio. β̄ is the mean of the expanding past-only β over the same rows (target-only). Because the cost is linear in β, the mean per-row cost equals the cost at β̄.
>   - D2.3 The round trip per name-day: RT = 2·(c_m + x_m) + β·2·(c_h + x_h) + s, with c the commission per side, x the execution cost per side and s the short cost (m: miner; h: 1306). SESOI = mean RT / mean |ẽ| over the D2.1 rows (a ratio of means). It is the ratio of two marginal statistics; nothing in it depends on the joint distribution of predictors and targets.
>   - D2.4 The tick term for the miners. TSE tables apply to traded prices (stored price ÷ f).
>     - Primary: x_m = max(stated impact, ½ tick), averaged per ticker over its kept rows outside the Flag 4 windows (5711 before 2016-09-28; 5706 before 2017-09-27) and over the open and close sides, under the fine table (up to JPY 1,000: 0.1; to 3,000: 0.5; to 10,000: 1; to 30,000: 5). That table covered TOPIX100 constituents from 2015-09-24 and TOPIX500 constituents from September 2023 at the latest, including the three miners (Isaiah's cost note), so it governs most of the confirmation period. The consolidations raised traded prices tenfold for good, so the coarse grids cannot recur in the confirmation; Flag 4 enters through the high case.
>     - Low: no tick term; x_m = stated impact.
>     - High: x_m = stated impact + ½ tick on every kept row, including the Flag 4 windows, under the tables in force during dev (the standard table for 5711 and 5706; the TOPIX100 table for 5713).
>   - D2.5 The 1306 tick, with no RAW read. Half a tick of 1306 is an assumption: primary 1.25 bp (½ × JPY 0.5 on about JPY 2,000; the TOPIX100 table applies to ETFs from 2021-11-29, as P2-5c's 0.05 steps on stored prices in 2021 show); high 4.2 bp (½ × JPY 1 on about JPY 1,200, the dev table at dev lows). Primary x_h = max(impact, ½ tick); low x_h = impact; high x_h = impact + ½ tick.
>   - D2.6 Viability (the spec's `equivalence.viability`, written in the switch). TOST is viable at T_conf if, under the primary inference method that the T1 and T4 rules select, (i) the probability of declaring equivalence at b = 0 is at least 0.80 at the primary SESOI, and (ii) the rate of declaring equivalence at b = +SESOI (primary) is at most 6.5%. The run also reports (i) at the low and high SESOI, under every DQ1.6 method. If TOST is not viable, it is reported as descriptive only, the equivalence wording is not used, and a null H1 is read against MDE80.
>   - D2.7 Claim wording. The equivalence wording ("no drift exploitable net of costs") is used only if TOST declares equivalence at the primary SESOI, and the report states next to it whether it also does at the low SESOI. It is an economic statement; MDE80 remains the statement about informational pricing.
>   - D2.8 Economic evaluation (P35 T5). The costs are the primary, low and high round trips of D2.3 to D2.5, with each confirmation row's own β. The break-even is the mean gross P&L per name-day, in bp, of the every-day, β-hedged, market-on-open to market-on-close strategy that trades the sign of the forecast, for M3 and for M2; their difference isolates `usdjpy_ret`. Threshold-trading variants are exploratory.
>   - D2.9 Fixity. The SESOI is set by these definitions and inputs. Isaiah's approval at the P3-1 review checks the computation only. Any change to an input or a definition after the P3-1 report is a labelled deviation.

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

**P3-0b e:** the new tests alone (`python -m unittest tests.test_p3_0b_preflight -v`): 3 tests, OK, on the first run. The full suite ran inside the P3-0b checkpoint; its result is in the P3-0b report (`/tmp/p3_0b.txt`).

**P3-1:**
- New tests alone (`python -m unittest tests.test_p3_1_sesoi -v`): 5 tests, OK, on the first run. They were run again, OK, after an output line was removed from the tool's report (see the P3-1 report), before the real run.
- `tools/p3_1_sesoi.py` gates on the real dev panel (`reports/P3_1_sesoi.md`):
  - step 1: the Part A counts equal `reports/P3_0b_preflight.md`: True;
  - step 2: the partialling set is {ticker fixed effects, `eurusd_ret`, ticker-specific `spy_oc` and `copx_oc`}: True;
  - step 3: every (ticker, year, period) cell's opens and closes conform to the dev tick tables at traded prices (share 1), and none is above a bound: True.
- The full suite ran inside the P3-1 checkpoint; its result is in the P3-1 report (`/tmp/p3_1.txt`).

## Test changes

Protocol: PASS2_ADDENDUM §5, rules 2–4, read for Pass 3. No existing test was changed or deleted.

| Test | Old | New | Entry | Phase |
|---|---|---|---|---|
| new `tests/test_p3_0b_preflight.py` | — | 3 tests, synthetic only: the Part A sample rule keeps exactly `inference.build_design`'s rows on three injected `synthetic_panel` frames; the grid detector on hand-built series (including a grid change mid-sample); the tool refuses a panel whose hash does not match the registry, before reading it | P3-0b (supervisor message, 2026-10-06) | P3-0b |

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
- (P3-0b, for the supervisor) DQ2, price units: the panel's miner prices are adjusted for capital changes and are on the basis after 5706's 10:1 split (ex-date 2026-09-29; DATA_PROVENANCE.md:67, :70; DATA_DICTIONARY.md:116). Read with B3's grids, panel prices therefore differ from the prices traded at the time by a factor: 5711 ×10 before 2016-09-28 (grid 10, a 1-yen tick); 5713 ×2 before 2017-09-27 (2016 grid 0.2, a 0.1-yen tick); 5706 ÷10 from 2017-09-27 (grid 0.1 or 0.5, a 1- or 5-yen tick). A TSE tick-size schedule applies to traded prices, so it cannot be applied to the panel prices as they stand. B4's ratio g / price does not depend on the factor.
- (P3-0b, for the supervisor) DQ2, B4 as specified uses the finest grid detected in each (ticker, year, period) cell. Where a year spans TSE tick bands, rows in the coarser band have a larger tick than g, and B4 understates it. Example: 5706 in 2018 has 86.32% of its prices on 0.5, but its detected grid is 0.1. The g ≥ 0.99 column catches only cells that are almost entirely on one grid.
- (P3-0b review, supervisor, 2026-10-06; a routing record, not a decision) The P3-0 and P3-0b flags: the `walk_forward` run-registry write → DQ4, with a DQ1.2 clarification; the static-test imports → a DQ1.3 clarification at P3-2 (the script's own import statements); the target pre-flight → resolved by P3-0b Part A (the four predictors remove no row: 4,192 rows, 1,439 dates); the T3 confirmation structure → DQ4; the SESOI denominator → resolved by D2.1; T6 winsorisation → DQ3 and DQ7 (a new module outside the C7 key); the T5 data source → resolved by D2.4 and D2.5 (the dev panel's open and close, as target-side price statistics); the DQ1.5 rehearsal contact → to be confirmed with P3-3; the pins → DQ5; the step f disclosure → resolved by the P3-0 step f decision (pre-registration carry list); price units and B4's understatement → resolved by D2.4 (the TSE tables applied row by row to traded prices).

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
- **P3-0b (supervisor message of 2026-10-06)**, by category:
  - Records: document edits to PASS3_STATUS.md; the P3-0 report copied into `reports/` and hashed.
  - `tools/p3_0b_preflight.py`, run once on the real dev panel. It hashed `panel_dev.csv` against both registry entries before reading it, then loaded it with `io.load_dev` (which registers the real targets in the in-process fingerprint registry) and built targets with `targets.add_targets` (target-only).
    - Part A used the exclusion flags, the non-missingness of `beta`, `abn_oc` and the four predictors, and one boolean for finiteness (see Deviations). It also used dates and tickers.
    - Part B used the target-side price columns `open` and `close` only.
    - It printed and wrote counts, dates, price quantiles, grid shares and tick ratios only. No statistic of any predictor's values was computed, and nothing combined predictor values with target values. No `build_design`, `_design_core`, inference function or `walk_forward` was called on real data. No cost, SESOI or mean |e| was computed.
  - `tests/test_p3_0b_preflight.py` is synthetic only. The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - RAW and OUT: untouched. No data file was opened by any viewer. `OFILT_RUN_SEALED` was unset throughout (every Python command ran under `env -u OFILT_RUN_SEALED`).
- **P3-1 (supervisor message of 2026-10-06)**, by category:
  - Records: document edits to PASS3_STATUS.md; `docs/P3_COST_INPUTS.json` written from the Decision log.
  - `tools/p3_1_sesoi.py`, run once on the real dev panel. It hashed `panel_dev.csv` against both registry entries before reading it, then loaded it with `io.load_dev` and built targets with `targets.add_targets` (target-only).
    - Predictor values (`usdjpy_ret`, `eurusd_ret`, `spy_oc`, `copx_oc`) entered only the D2.1 predictor-only regression, whose only output is mean |ẽ|.
    - `beta` was used only for β̄ (and each row's hedge leg, whose mean is the β̄ term).
    - `open` and `close` were used only for the ticks and the conformity gate.
    - Target columns were otherwise used only through availability (the P3-0b Part A rule).
    - No output depends jointly on predictors and targets.
    - No `build_design`, `_design_core`, inference function, `walk_forward` or `DevCalibrator` was called on real data. No probability of equivalence, size or power was computed.
  - `tests/test_p3_1_sesoi.py` is synthetic only. The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED` was unset throughout. BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.

## Deviations

- P3-0 c: the first run of the hash-check script (`/tmp/p3_0_hashes.py`) printed "listed in prompt: None" for the four DATA rows, and an overall False. Its table parser kept only rows starting with ``| ` ``, so it dropped the rows starting with `| DATA`. Every computed-vs-registry comparison in that run was True. The parser was fixed to keep every table body row, and the rerun agreed three ways on all five files. Both runs are in the P3-0 report.
- P3-0 e: the post-run check command assigned a shell variable holding the BLIND_FIT_LOG baseline hash, typed by hand. The variable was never used; the comparison read the baseline from step d's printed output.
- P3-0b d: beyond non-missingness, Part A checks one boolean: the kept rows are finite in the required columns (`beta`, `abn_oc` and the four predictors). This mirrors `inference.py:130-131`, where the design builder refuses non-finite values, so the counts match the sealed fit's sample exactly. It reads finiteness, a missingness-type property, and computes no statistic of any value. It printed True.
- P3-0b b.1: the P3-0 status cell reads "done; accepted by Isaiah 2026-10-06" as instructed. The checkpoint name `checkpoint: P3-0`, which the standing prompt puts in that row, moved to the start of its Notes cell.
- P3-1 d: in `docs/P3_COST_INPUTS.json`, every value the message specified is present as given. The structure has three additions:
  - each tick table's rows (`[inclusive upper bound, tick]`) sit under `rows` in an object, with the in-force period under `in_force` where step d gives one;
  - `price_factor` and `dev_table` are lists of dated segments (`start` inclusive, `null` for the start of the panel);
  - `_about` keys explain the shapes.
- P3-1 g.3: one PASS3_STATUS.md text edit (the P3-1 Progress row) ran as `python3 - <<'PY' …` with the system interpreter: not in the activated venv, and without the `env -u OFILT_RUN_SEALED` prefix the standing prompt requires of every Python command. The script only replaced two strings in this file and read no data. `OFILT_RUN_SEALED` was unset in the shell (`printenv` printed nothing at step a). Every other Python command in P3-1 followed the rule.
