# PASS3_STATUS.md

Pass 3 (calibration, dev still blinded), run per the Pass 3 builder prompt (2026-10-06) and the supervisor messages that follow it. Paths: REPO `~/Desktop/FX_Project/ofilt_pass1`, DATA `~/Desktop/FX_Project/data`, KIT3 `~/Desktop/FX_Project/files/pass3`, VENV `~/venvs/ofilt_p2`. Out of scope for all of Pass 3: RAW `~/Desktop/FX_Project/raw` and OUT `~/Desktop/FX_Project/build_out`.

## Progress

| Item | Status | Notes |
|---|---|---|
| P3-0 Setup, integrity, code survey | done; accepted by Isaiah 2026-10-06 | `checkpoint: P3-0`. Date gate 2026-10-06. arm64, macOS 26.6.2; VENV Python 3.12.4, numpy 2.4.4, pandas 3.0.2, scipy 1.17.1, scikit-learn 1.8.0, PyYAML 6.0.3, openpyxl 3.1.5; BLAS accelerate, LAPACK accelerate. HEAD `c9cea24` on `main`, tree clean, tags `pass1-final` only (lightweight). Five hashes agree three ways (computed, registry, prompt); DATA holds exactly the four expected files. BLIND_FIT_LOG 6 dev_real lines, SHA-256 `dad93285d2911abc6c7145c160d729df1126b24b439302bd8577cf407d397301`; RUN_REGISTRY.jsonl 0 bytes. Suite and slow tier pass (Test results). B7/B7b reports: structure only, no per-replication values. Code survey Q1–Q14 in the P3-0 report (`/tmp/p3_0.txt`). Saved prompt SHA-256 `018c489ff53db0aa069881874e0c4faea0e165a2e23ba02b875963b034dfee36`. Planned STOP for the supervisor's review |
| P3-0b Records and pre-flight facts | done; accepted by Isaiah 2026-10-06 | `checkpoint: P3-0b`. Decisions recorded (P3-0 accepted; the rerun-once rule; step f). P3-0 report copied byte for byte to `reports/P3_0_report.txt`. `tools/p3_0b_preflight.py` (dev only, facts only; no rule applied) ran once on the real dev panel and wrote `reports/P3_0b_preflight.md`: Part A, the AM-03 estimation sample (the counts DQ1.3 needs; T_source); Part B, the miners' price levels, grids and one tick in bp. Synthetic tests in `tests/test_p3_0b_preflight.py` (3, OK). Report `/tmp/p3_0b.txt`. Planned STOP for the supervisor's review |
| P3-1 Cost model and SESOI | done; accepted by Isaiah 2026-10-06 | `checkpoint: P3-1`. P3-0b acceptance, the cost inputs and DQ2 (D2.1–D2.9) recorded. `docs/P3_COST_INPUTS.json`; `tools/p3_1_sesoi.py` (dev only: mean \|ẽ\|, β̄, the round trips and the primary, low and high SESOI) ran once on the real dev panel, all three gates True, and wrote `reports/P3_1_sesoi.md`; synthetic tests in `tests/test_p3_1_sesoi.py` (5, OK). Report `/tmp/p3_1.txt`. Planned STOP: supervisor review and Isaiah's approval of the computation (D2.9) |
| P3-1b Records; synthetic timing probe | done; accepted by Isaiah 2026-10-06 | `checkpoint: P3-1b`. Report `/tmp/p3_1b.txt`; planned STOP for DQ3, DQ4 and DQ7. P3-1 acceptance and the SESOI approval (D2.9) recorded. Synthetic timing and feasibility probe `/tmp/p3_1b_probe.py` (not committed; existing code only; `OFILT_DATA_DIR` an empty folder, `TMPDIR` the probe's own folder); its facts inform DQ3 and DQ4 and decide nothing |
| P3-2a DQ3, DQ4, DQ7; calibration module; warp-speed check | done; accepted by Isaiah 2026-10-06 | `checkpoint: P3-2a`. P3-1b acceptance, DQ3, DQ4, DQ7, the DQ1 clarifications, the G2 STOP's resolution and the D3.2/D3.3 amendment recorded. New module `ofilt/drift/calib.py` (outside the C7 key) with 8 synthetic tests in `tests/test_p3_calib.py`, all OK. Synthetic warp-speed check `tools/p3_2a_warp_check.py`: run 1 (`reports/P3_2a_warp_check_run1.md`) passed G1 and failed G2, which was then superseded as mis-specified (STOP); run 2 (`reports/P3_2a_warp_check.md`, fresh seeds) passed G1 and G2′. Synthetic only; no data file read. Reports `/tmp/p3_2a.txt` and `/tmp/p3_2a_cont.txt`. Planned STOP |
| P3-2b Warp-path check; sealed-run tool, configuration, smoke run | done; accepted by Isaiah 2026-10-06 | `checkpoint: P3-2b`. Report `/tmp/p3_2b.txt`; planned STOP. P3-2a acceptance and the sealed-run tool's design recorded. Warp-path gate (step b) passed (9 of 9). K = 409. Configuration valid; 9 tests OK (after one test-setup fix); smoke gates passed; projected full run 1.54 h with an empty registry. `tools/p3_2b_preflight.py` (K_early, target-only), `docs/P3_RUN_CONFIG.json`, `tools/p3_sealed_run.py` with tests `tests/test_p3_sealed_run.py`, and a synthetic smoke run (`reports/P3_2b_smoke.md`). No `--real` or `--rehearsal` run |
| P3-2c Records; tool listing; test output hygiene | done; accepted by Isaiah 2026-10-06 | `checkpoint: P3-2c`. Report `/tmp/p3_2c.txt`; planned STOP for the supervisor's full review of the tool before the rehearsal. P3-2b acceptance and the DQ1.3 clean-tree clarification recorded. Read-only listing of `tools/p3_sealed_run.py` (unchanged) for the supervisor's full review; test 4's refusal output captured in `tests/test_p3_sealed_run.py` (test-only change) |
| P3-2d Review changes R1, R2; structural check; rehearsal script | done | `checkpoint: P3-2d`. Report `/tmp/p3_2d.txt`; planned STOP for the supervisor's review before Isaiah starts the full rehearsal. Structural gate passed; smoke rehearsal PASSED (projected full run 1.92 h with the registry populated). P3-2c acceptance, the review's decisions (R1, R2, R3), the rehearsal procedure and the records rule recorded. R1 and R2 in `tools/p3_sealed_run.py` (configuration unchanged); the structural check `tools/p3_2d_structural.py` (R3); `tools/p3_3_rehearse.sh` with a `--smoke 20` run. No `--real` run; the full rehearsal not started |
| Pass 3 | in progress | |

## Next action

P3-3: after the supervisor's review of P3-2d, Isaiah runs `tools/p3_3_rehearse.sh` (full) in his own Terminal; then the DQ5 test-change rehearsal and the DQ6 amendment drafts.

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

> - P3-1 accepted (Isaiah, 2026-10-06, on the supervisor's recommendation).
>   - Checkpoint `8aba8df8ed33225071d4451741c2f7ab140ef18c`.
>   - The acceptance covers the recorded deviations P3-1 d (the cost file's structure; every value as decided) and P3-1 g.3 (one text edit run with the system interpreter, outside the venv and without `env -u OFILT_RUN_SEALED`; it read no data), and the removal, before the real run, of one report line that was outside the Outputs list (the tests were rerun).
>   - Every P3-1 gate passed: the sample (4,192 rows, 1,439 dates), the regressor set, and the conformity of all 5,124 dev opens and closes with the dev tick tables.
> - SESOI approved as computed (Isaiah, 2026-10-06, on the supervisor's recommendation; D2.9). The supervisor recomputed every component from the report.
>   - mean |ẽ| = 28.4288 bp; β̄ = 1.0333.
>   - Mean round trip per name-day: primary 24.5961 bp, low 2.0333 bp, high 77.2878 bp.
>   - SESOI: primary 0.8652, low 0.07152, high 2.719. These four-significant-digit values are the ones used in the run configuration and in the switch's amendment.

> - P3-1b accepted (Isaiah, 2026-10-06, on the supervisor's recommendation).
>   - Checkpoint `87aff1406356701396a3e99b7b2923257ba81d62`, including the recorded deviation P3-1b c (panel B with `p_excl` = 0; explicit synthetic provenance on `pair` and `clark_west`).
>   - Probe facts (synthetic, empty fingerprint registry): `build_design` + `fit_dk` at 1,013 dates, median 0.025 s; `fit_huber`, 0.007 s; `stationary_bootstrap_positions`, 0.0002 s; `walk_forward` with {M2, M3} on 2,452 dates, 0.92 s; Clark–West on the last 1,013 dates, 0.033 s. The first forecast falls at date 501 and every one of the last 1,013 dates is forecast. `registry.py` fixes the synthetic registry path at import (`registry.py:34`), and a TMPDIR set before the process starts contains every line.
> - DQ3 (Isaiah, 2026-10-06, on the supervisor's recommendation): the inference methods, their evaluation and the joint T1/T4 rule.
>   - D3.1 The bootstrap test (AM-02's branch). The statistic is the Driscoll–Kraay t of `usdjpy_ret`, t = b̂/se. The resampling is a stationary bootstrap of whole dates of the estimation sample (mean block 5): the sample's T dates are drawn to length T, taken in drawn order and refitted with the same design and DK lag, giving t* = (b̂* − b̂)/se* (recentred, not null-imposed). The two-sided 5% test rejects if |t| > c_boot, the 95% quantile of |t*|; the interval is b̂ ± c_boot·se; TOST uses the 90% quantile of |t*|. At the confirmation it uses 9,999 resamples, seeded from the spec's seed (the seed goes into the amendment).
>   - D3.2 Its evaluation in the sealed run is the warp-speed method (Giacomini, Politis and White, 2013, Econometric Theory 29(3), 567–589, DOI 10.1017/S0266466612000655): one resample per simulated replication, with each cell's critical values taken as quantiles of the pooled |t*| over that cell's replications. P3-2a checks it on synthetic data against a full inner bootstrap.
>   - D3.3 The simulation-calibrated critical value (P31). c_cal(α) is the ⌈(1 − α)·n⌉-th smallest |t| over T1's n = 5,000 replications at b = 0 (α = 0.05 for H1; α = 0.10 for TOST), reported with its 95% order-statistic interval. Power under it is size-adjusted power. For Clark–West, c_CW,cal is the ⌈0.95·n⌉-th smallest CW statistic over T3's replications at b = 0 (one-sided).
>   - D3.4 The joint T1/T4 rule (Flags 10 and 12), applied at P3-5 to point estimates, as AM-02 is.
>     - H1: if the DK-normal rejection rate at b = 0 (T1) lies in [3.5%, 6.5%], primary inference is DK with the normal reference. Otherwise it is the D3.1 bootstrap (AM-02), provided the bootstrap's own rate at b = 0 lies in that band; if it does not, primary inference is DK with c_cal(0.05).
>     - Clark–West: if its rate at b = 0 (T3, normal reference) lies in [3.5%, 6.5%], the normal reference stays; otherwise c_CW,cal replaces it.
>     - The selected methods' numbers are the binding ones (power, MDE80, D2.6 and the T3 cross-tab). Every method's numbers are reported (DQ1.6).
>   - D3.5 When the method selected for H1 is DK-normal or the bootstrap, it applies to every other pre-registered DK test (H3, the secondary family, H4 and the robustness rows). Under c_cal, which is specific to H1 and TOST, the other tests keep the normal reference.
> - DQ4 (Isaiah, 2026-10-06, on the supervisor's recommendation): the designs of T2, T3, T5's viability and T6.
>   - D4.1 The cells, in task order (cell id: task, b, replications). Every draw has n_dates = 1,013 unless stated, a₂ = 0 and mean block 5.
>     - 0: T1, b = 0, 5,000.
>     - 1: T5's boundary (D2.6 (ii)), b = +0.8652, 5,000.
>     - 2 to 4: T2, b = 0.10, 0.25 and 0.40, 1,000 each.
>     - 5 to 8: T6, full draws at b = 0 and 0.25, and early-window draws at b = 0 and 0.25, 1,000 each.
>     - 9 to 11: T3, n_dates = 2,452, b = 0, 0.10 and 0.25, with 2,000, 500 and 500.
>     - The counts may be revised before the sanction, on runtime grounds only.
>   - D4.2 T3. On each 2,452-date draw (T_source + T_conf): `walk_forward` with {M2, M3}, target `y_sim`, both masks False, and the replication's outer seed; Clark–West (M3 vs M2) on the rows of the last 1,013 dates; H1 on the same last 1,013 dates. The cross-tab (both, H1 only, CW only, neither) is reported per cell for every H1 method × CW method.
>   - D4.3 T6. Early-window draws resample only the source dates before 2017-09-27 (the coarse-grid period of 5711 and 5706); their count is a target-only pre-flight fact, taken at P3-2b. The estimators are OLS-DK, Huber-DK (c = 1.345, MAD scale) and OLS-DK on FX winsorised at the spec's bounds, all with the normal reference. Reported: the rejection rate, mean bias, sd(b̂), mean SE/sd, coverage, and Huber's mean share downweighted. If an estimator's rate at b = 0 on early-window draws lies outside [3.5%, 6.5%], the pre-registration flags that robustness row as unreliable on coarse-grid periods.
>   - D4.4 TOST viability (D2.6): (i) from cell 0, at the primary, low and high SESOI; (ii) from cell 1.
>   - D4.5 Seeds. The outer seed is the spec's seed + 5,000,000 + 100,000·cell + replication; the warp-speed resample of the same replication uses that seed + 50,000. These are disjoint from the B7, B7b and C7 blocks.
>   - D4.6 DK and Newey–West lags come from `Spec.dk_lag` on each fit's unique dates; the run asserts 6 for every fit.
>   - D4.7 Outputs, per cell and method, are only: rejection counts, rates and Wilson intervals; means and standard deviations across replications; coverage; the named quantiles (c_boot, c_cal, c_CW,cal) with their order-statistic intervals; MDE80 per method (probit interpolation with B7b's cross-checks); the cross-tab counts; H3's rate at b = 0; and each task's runtime.
> - DQ7 (Isaiah, 2026-10-06, on the supervisor's recommendation): code scope.
>   - New code only: `ofilt/drift/calib.py` and its tests (P3-2a); `tools/p3_sealed_run.py`, its tests and `docs/P3_RUN_CONFIG.json` (P3-2b). The confirmation-time entry point for the selected method lives in `calib.py`.
>   - Unchanged until the switch: the C7-hashed files, `spec.py`, `blind.py`, `io.py`, `registry.py`, `targets.py` and the guard; `build/pass1/` and `build/pass2/`; `PRE_OPEN_FEATURES` (the 20 Pass 1 columns).
>   - The switch (P3-6) may change only the spec (AM-07 onward), `spec.py`'s validation of the new inference fields, and the pins listed under DQ5. Any other change needs its own listed approval.
> - Clarifications of DQ1 (Isaiah, 2026-10-06, on the supervisor's recommendation).
>   - DQ1.2. Because `registry.py` fixes the synthetic run-registry path at import, the sealed-run script creates its own temporary directory and sets `tempfile.tempdir` to it before importing any `ofilt` module. It asserts that `registry.SYNTHETIC_PATH` lies inside that directory, asserts at the end that the directory holds exactly one line per `walk_forward` call, and then deletes it. No line is printed or kept. If a run is killed, Isaiah deletes the directory before anything else.
>   - DQ1.3. "Imports none of multiprocessing, concurrent.futures, joblib or subprocess" is tested on the import statements of the script and of `calib.py`. The indirect imports by sklearn (through `models`) and by `registry.py` (for git) are permitted.
>   - DQ1.5. The rehearsal loads the dev panel with `io.load_dev` and `targets.add_targets` to populate the fingerprint registry. This is target-only contact: nothing is printed, and no `DevCalibrator` is constructed on real data.

> - P3-2a step e, the G2 STOP (Isaiah, 2026-10-06, on the supervisor's recommendation).
>   - Run 1 (R = 200, B = 99, seeds from the spec seed + 4,000,000): G1 passed; G2 failed (n10 = 0, n01 = 9).
>   - The gate was mis-specified by the supervisor. McNemar's test assumes independent discordant pairs, but every warp-speed decision shares one critical value estimated from 200 draws, so the discordances run one way whenever that estimate lands high. q_warp(0.95) = 2.2356 lay about 1.9 standard errors above q_full(0.95) = 1.9751; a 95% quantile estimated from 200 draws has a standard error of about 0.14. With q_full, the pooled-quantile test rejected 14 of 200 replications, against the per-replication bootstrap's 15. The failure measures the Monte Carlo noise of q_warp at R = 200, not a defect of the method or of the code.
>   - Run 1's report is kept as `reports/P3_2a_warp_check_run1.md`.
>   - Before run 2, G2 is replaced by G2′: McNemar between the per-replication full bootstrap decisions and the decisions at q_full(0.95), whose critical value is estimated from 19,800 draws. G2′ passes if |n10′ − n01′| ≤ 1.959964·√(n10′ + n01′), or if n10′ + n01′ = 0.
>   - Run 2 uses fresh seeds (spec seed + 4,100,000 + r) and is judged on G1 and G2′.
> - D3.2 and D3.3 amended (Isaiah, 2026-10-06, on the supervisor's recommendation): pooled critical values.
>   - In the sealed run's draws, y_sim = fitted controls + b·e + a₂·eur + residuals, and the fitted controls lie in the design's column space. So (b̂ − b)/se and the recentred t* = (b̂* − b̂)/se* do not depend on b: their distributions are the same in every cell of full 1,013-date draws.
>   - c_boot at 0.95 and 0.90 is therefore the order statistic of |t*| pooled over cells 0 to 4 (13,000 warp-speed draws). c_cal(α) is the order statistic of |(b̂ − b)/se| pooled over the same cells. Each is reported with its 95% order-statistic interval.
>   - Both apply to cells 0 to 4 and to T3's H1 column, because the last 1,013 dates of a stationary-bootstrap draw are distributed as a 1,013-date draw. The noise these critical values add to a rejection rate falls to about ±0.2 percentage points, from about ±0.3 with 5,000 draws and about ±1 with 500.
>   - Each cell's own quantiles are reported for information, as a check of the invariance. P3-2b adds a synthetic test that, with identical positions and seeds, (b̂ − b)/se is the same at every b to 1e-10.
>   - Clark–West's c_CW,cal stays as D3.3 defines it (T3's cell at b = 0), because its statistic is not invariant to b.

> - P3-2a accepted (Isaiah, 2026-10-06, on the supervisor's recommendation).
>   - Checkpoint `8bced4b38ff1365d15344267a6f57d38f270ee08`, including the recorded deviations (c.1, e, c, the STOP and its resolution, and the records correction for P3-1's test file).
>   - Run 2 passed G1 and G2′ (n10′ = 2, n01′ = 1). Across both runs, the per-replication bootstrap rejected 24 of 400 replications and the q_full test 22 of 400.
>   - Open point, resolved at P3-2b step b: q_warp(0.95) exceeded q_full(0.95) in both runs, by 0.26 and 0.22. If the warp-speed and inner draws come from identical code, two such deviations together have a probability of roughly 0.1% to 1% (supervisor's simulation). The code path is therefore checked before the pooled critical values are relied on.
> - Design of the sealed-run tool (Isaiah, 2026-10-06, on the supervisor's recommendation). It implements DQ1, DQ3 and DQ4 in `tools/p3_sealed_run.py` and `docs/P3_RUN_CONFIG.json`.
>   - Modes.
>     - `--synthetic`, the default, runs on a synthetic stand-in with a temporary BLIND_FIT_LOG, as `tools/report_B7.py --synthetic` does.
>     - `--real` runs only if `OFILT_RUN_SEALED=1` is set for that command, the tree is clean, and `--expect-config-sha256` equals the configuration file's SHA-256. This binds Isaiah's sanction (DQ1.7) to the configuration.
>     - `--rehearsal`, synthetic only and for P3-3, also loads the dev panel with `io.load_dev` and `targets.add_targets` to populate the fingerprint registry (DQ1.5).
>     - `--smoke N`, synthetic only, caps every cell at N replications.
>   - The stand-in is `sim.synthetic_panel` with 1,439 dates and no exclusions, with `abn_oc` removed on seeded rows so that 29 dates keep one ticker, 67 keep two and 1,343 keep three (4,192 rows). The calibrator's source dates and rows then equal the real sample's, and the real run's assertions run unchanged.
>   - Assertions in every mode: the calibrator's source dates equal T_source (1,439) and its rows equal 4,192 (the rows read from the calibrator's private row bounds, for this assertion only); every DK and Newey–West lag is 6; the run-registry directory holds one line per `walk_forward` call (DQ1.2).
>   - Assertions in real mode also: the dev panel's and the spec's SHA-256 equal the registry's; BLIND_FIT_LOG has 6 dev_real lines before the calibrator, 7 immediately after it (line 7 dev_real, on AM-04's panel hash, with this script as caller), and 7 at the end (DQ1.3). Any failed assertion aborts the run.
>   - Flushing (DQ1.4).
>     - After each cell, its method-independent and DK-normal aggregates are written.
>     - After cell 4, the pooled critical values (D3.2 and D3.3, amended) and every aggregate of cells 0 to 4 that uses them are written.
>     - T6 and T3 follow, in that order. T3 uses the pooled critical values and draws no warp-speed resample.
>     - An exception in a task is recorded by its class and line number only, and the run continues with the next task.
>   - Outputs. Real mode writes `reports/P3_4_sealed_run.json` and `reports/P3_4_sealed_run.md`, rewritten after each flush. Synthetic mode writes the same two files under `--out-dir` (under `/tmp`). Runtime fields sit in their own `runtime` section; everything else is byte-identical between runs with the same configuration (sorted keys; floats as `repr`).
>   - The tool applies no decision rule. D2.6, D3.4 and D4.3's flag rule are applied at P3-5, from its outputs.

> - P3-2b accepted (Isaiah, 2026-10-06, on the supervisor's recommendation).
>   - Checkpoint `befb7da4a4d7fdd5fbcfca8a303110ee213e741e`. The configuration `docs/P3_RUN_CONFIG.json` has SHA-256 `645ef80ee91c91e81ac4a880ff34b0fc19906bbb3c36f5300575d727dc1d7eaa`; it is not yet sanctioned (DQ1.7).
>   - The acceptance covers P3-2b's recorded deviations: the tests' setup bug and its one rerun; the design choices listed for review; test 4's use of the pure function `mode_refusal`; and the reuse-the-first-fit variant `calib.bootstrap_t_given_fit`, appended to `calib.py` with every existing function unchanged.
>   - The warp-path gate passed. The warp-speed and inner draws come from the same `calib.bootstrap_t` path, and all 9 seeded identity checks were True. The two high values of q_warp in P3-2a were therefore chance, and the open point of the P3-2a acceptance is closed.
>   - K_early = 409 (K16 = 165). The two smoke runs were identical apart from runtime and project 1.54 hours for the full configuration at empty-registry rates.
> - DQ1.3 clarification (Isaiah, 2026-10-06, on the supervisor's recommendation): the clean-tree check. The script may not import subprocess, so its own check (`registry.git_state`) covers tracked files only. The P3-4 launch command therefore begins with a shell check that `git status --porcelain` prints nothing, untracked files included, and does not start the run otherwise.

> - P3-2c accepted (Isaiah, 2026-10-06, on the supervisor's recommendation).
>   - Checkpoint `b94d8a48fdce45e424cb772ff77d7941d60dde0b`, including the recorded deviation P3-2c d (the two imports the test change needs).
>   - The remote was verified by Isaiah on 2026-10-06: `refs/heads/main` was `befb7da4a4d7fdd5fbcfca8a303110ee213e741e` and `refs/tags/pass1-final` was `81905c1b576d24bdac2c96e2ab76429e0a1d24d1`. This closes the push confirmation open since P3-0.
> - The supervisor's review of the full sealed-run tool (Isaiah, 2026-10-06, on the supervisor's recommendation). Three changes come before any rehearsal; the configuration stays byte-identical.
>   - R1. Every real-mode check on line 7 is rehearsed, and the panel hash is checked before the sealed fit.
>     - In synthetic and rehearsal modes, the temporary log must hold exactly one line after the calibrator, with provenance `synthetic` and a caller that names this script.
>     - In rehearsal and real modes, before the calibrator, the frame's provenance must be `dev_real`, and the panel hash that `sim._sealed_blind_fit` will log for it, computed by the same expression, must equal the configured dev-panel hash.
>     - In rehearsal mode, the repository's BLIND_FIT_LOG must also pass the 6-line check, read only.
>     - Any failure aborts the run. Before this change, these checks ran only in real mode, after line 7 had been written, so a format mismatch would have spent the sealed fit.
>   - R2. No exception message or traceback is printed in any mode. An unexpected exception outside a task is recorded like a task's, by its class and line only; the run stops, and the outputs written so far are flushed with that record.
>   - R3. A structural check of the real-data construction path, run once (`tools/p3_2d_structural.py`).
>     - The dev panel is loaded with `io.load_dev` and `targets.add_targets`, which registers the real targets.
>     - A frame is built from it that keeps only date, ticker, the exclusion flags and the predictor columns that `DevCalibrator` reads. The target and target-derived columns it needs are replaced by synthetic values on exactly the rows where the real ones are present, and every other column is dropped.
>     - The frame is labelled synthetic, so the fingerprint guard checks it against the registered real targets. One `DevCalibrator` is constructed on it, with a temporary log. The check prints only booleans and counts.
>     - No real target value enters any computation. This is the category of the existing guard test that relabels the dev frame synthetic after removing its targets (`test_blind.test_fx_columns_never_compared`).
>   - The real-data construction path itself has not run since Pass 1, on a panel that has since changed (AM-03, AM-04). R3 exercises its code on the real frame's structure without a sealed fit.
> - The rehearsal procedure (Isaiah, 2026-10-06, on the supervisor's recommendation; DQ1.5).
>   - `tools/p3_3_rehearse.sh` runs the tool's `--rehearsal` mode twice, in sequence, with the checks of step f, and compares the two outputs.
>   - Isaiah runs the full rehearsal in his own Terminal, after the supervisor has reviewed P3-2d: `caffeinate -i`, mains power, lid open, and no other heavy job running.
>   - Its runtimes give the expected duration of the real run, stated before the sanction.
> - The records rule (Isaiah, 2026-10-06, on the supervisor's recommendation): until the switch, no line added to PASS3_STATUS.md begins with a prefix from which the configuration's rules are copied, and every records step ends with `--check-config` printing valid: True.

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

**P3-2a:**
- Calibration tests alone (`python -m unittest tests.test_p3_calib -v`): 8 tests, OK, on the first run.
- Warp-speed check, run 1 (`reports/P3_2a_warp_check_run1.md`; R = 200, B = 99, seeds from the spec seed + 4,000,000): G1 True; G2 False, superseded (mis-specified; Decision log).
- Run 2 (`reports/P3_2a_warp_check.md`; seeds from the spec seed + 4,100,000): G1 True, G2′ True. The superseded G2, printed for information, was also True.
- Chunked and unchunked runs gave identical reports apart from the Runtime section (R = 4) at both seed bases.
- The full suite ran inside the P3-2a checkpoint; its result is in the continuation report (`/tmp/p3_2a_cont.txt`).

**P3-2b:**
- Warp-path gate (step b):
  - The code read confirms that the warp-speed and inner draws differ only in the generator and in B: True.
  - t*[0] with B = 1 equals t*[0] with B = 99 (`==`) in 9 of 9 comparisons (3 frames × 3 seeds): True.
- Early-window pre-flight (`reports/P3_2b_preflight.md`): K = 409, K16 = 165. Gate (398 ≤ K ≤ 1,439; 160 ≤ K16 ≤ K): True.
- `docs/P3_RUN_CONFIG.json` is the configuration rebuilt from the registry, and it validates.
- `tests/test_p3_sealed_run.py`: run 1 had 6 tests OK and an error in `setUpClass` of the tiny-run tests (a test setup bug; see Deviations); the one rerun had 9 tests, OK.
- Smoke run (`--smoke 20`, twice): both complete, with no exception and no abort (True), and the JSON outputs are identical apart from `runtime` (True). The projected full run is in `reports/P3_2b_smoke.md` (empty fingerprint registry).
- The full suite ran inside the P3-2b checkpoint; its result is in the P3-2b report (`/tmp/p3_2b.txt`).

**P3-2c:**
- `tests/test_p3_sealed_run.py` alone, after the step d change: 9 tests, OK; no `REFUSED` line in the output.
- The full suite ran inside the P3-2c checkpoint; its result is in the P3-2c report (`/tmp/p3_2c.txt`).

**P3-2d:**
- `tests/test_p3_sealed_run.py` (13 tests, including 4 new) and `tests/test_p3_2d_structural.py` (1 new) together: 14 tests, OK, on the first run. The tiny runs, which exercise R1's new synthetic-log check, completed.
- Structural check (R3; `reports/P3_2d_structural.md`): every printed boolean True.
  - The construction succeeded; T 1,439; rows 4,192.
  - The draw passes the guard, has exactly `SIM_COLUMNS` and has lag 6.
  - The temporary log has 1 synthetic line, and the repository's BLIND_FIT_LOG is unchanged.
- Smoke rehearsal (`tools/p3_3_rehearse.sh --smoke 20`, from a scratch clone; see Deviations): REHEARSAL PASSED.
  - Both runs printed `COMPLETE … errors: 0`, and the JSON outputs are identical apart from `runtime`. Every hash and size was unchanged.
  - Seconds per replication with the fingerprint registry populated (mean of the two runs): T1 0.2124, T5 boundary 0.2142, T2 0.2125, T6 0.2202, T3 1.0877.
  - At these rates the full configuration projects to 6,914 s (1.92 h), against 1.54 h with an empty registry (P3-2b).
- The full suite ran inside the P3-2d checkpoint; its result is in the P3-2d report (`/tmp/p3_2d.txt`).

## Test changes

Protocol: PASS2_ADDENDUM §5, rules 2–4, read for Pass 3. No existing test was changed or deleted.

| Test | Old | New | Entry | Phase |
|---|---|---|---|---|
| new `tests/test_p3_0b_preflight.py` | — | 3 tests, synthetic only: the Part A sample rule keeps exactly `inference.build_design`'s rows on three injected `synthetic_panel` frames; the grid detector on hand-built series (including a grid change mid-sample); the tool refuses a panel whose hash does not match the registry, before reading it | P3-0b (supervisor message, 2026-10-06) | P3-0b |
| new `tests/test_p3_1_sesoi.py` (row recorded at P3-2a; see Deviations) | — | 5 tests, synthetic only: the FWL residual equals the residual of `usdjpy_ret` on `build_design`'s other columns; tick tables, band edges and price factors; the conformity check; the cost arithmetic (primary, low, high); refusals (unregistered panel, cost file with a missing key) | P3-1 (supervisor message, 2026-10-06) | P3-1 |
| new `tests/test_p3_calib.py` | — | 8 tests, synthetic only (test 5 reads B7b's committed aggregates): `tost_declares` vs `inference.tost`; `fit_t` vs `fit_dk`; `resample_dates`; order statistics and their intervals; `wilson` and `mde80` reproduce B7b; `winsorise_fx`; `window_positions`; static imports and no `open(` in `calib.py` | P3-2a (supervisor message, 2026-10-06) | P3-2a |
| new `tests/test_p3_sealed_run.py` | — | 9 tests, synthetic only (no data file read; no test sets `OFILT_RUN_SEALED`):<br>1. static checks (one `DevCalibrator(`; no banned import; one writing function; private attributes only in the row-count assertion);<br>2. the invariance of (b̂ − b)/se and t* across b, and `calib.bootstrap_t_given_fit` equal to `calib.bootstrap_t`;<br>3. the configuration (rebuilt equals committed; refusals);<br>4. real-mode refusals with no data read;<br>5. outputs whitelisted, no list over 20;<br>6. the run-registry directory;<br>7. seeds disjoint;<br>8. the 6 → 7 → 7 log checks;<br>9. determinism<br>P3-2c change: test 4's two in-process refusals have their stdout captured (`contextlib.redirect_stdout`), and the captured text must start with `REFUSED` (was: printed to the suite's stdout, uncaptured) | P3-2b (supervisor message, 2026-10-06); P3-2c (supervisor message, 2026-10-06) | P3-2b; P3-2c |
| `tests/test_p3_sealed_run.py`: 4 tests added (existing tests unchanged) | 9 tests | 13 tests:<br>10. R1: the generalised log check (a synthetic line passes; a wrong count, provenance or caller fails) and the logged-panel check (provenance `dev_real` and the logged hash);<br>11. R2: the generic handlers in `main` and `_run` reference no exception message (AST);<br>12. R2: `_abort_text` gives `<class> at line <n>` without the message;<br>13. `tools/p3_3_rehearse.sh`, static: no real-mode flag and no `OFILT_RUN_SEALED=1`; first line `set -euo pipefail`; the sealed-variable refusal before any Python line | P3-2d (supervisor message, 2026-10-06) | P3-2d |
| new `tests/test_p3_2d_structural.py` | — | 1 test, synthetic only: the structural frame builder keeps exactly the stated columns, keeps the missing pattern of `abn_oc` and `beta`, replaces their present values, drops every `y_*`, `ao_*`, `open`, `close` and `prev_close` column, and labels the frame synthetic | P3-2d (supervisor message, 2026-10-06) | P3-2d |

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
- **P3-1b (supervisor message of 2026-10-06)**, by category:
  - Records only, in PASS3_STATUS.md.
  - The probe `/tmp/p3_1b_probe.py` (not committed) is synthetic only. It ran once, with `OFILT_DATA_DIR` pointed at an empty folder and `TMPDIR` at its own folder.
    - It read no data file, constructed no `DevCalibrator`, called no `_sealed_blind_fit`, and ran no script's mode.
    - It printed wall-clock times, counts, positions and booleans only.
    - The in-process fingerprint registry was empty at every check.
    - BLIND_FIT_LOG's SHA-256, RUN_REGISTRY.jsonl's size and the usual synthetic run registry's size were unchanged across the run. Both folders were deleted afterwards.
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED` was unset throughout (every Python command ran in the venv under `env -u OFILT_RUN_SEALED`). BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-2a (supervisor messages of 2026-10-06: the item, and its continuation after the G2 STOP)**, by category:
  - Records only, in PASS3_STATUS.md.
  - Synthetic code and tests: `ofilt/drift/calib.py`, `tests/test_p3_calib.py` and `tools/p3_2a_warp_check.py`. Test 5 reads B7b's committed aggregates in `reports/B7b_size_preview.json`.
  - Both warp-speed checks (run 1, run 2 and the two small-R chunking checks) were synthetic only, with `OFILT_DATA_DIR` pointed at an empty folder and `TMPDIR` at an empty folder of their own.
    - No data file was read, and no `DevCalibrator` or `_sealed_blind_fit` was used.
    - BLIND_FIT_LOG's SHA-256, RUN_REGISTRY.jsonl's size and the usual synthetic run registry's size were unchanged across each check.
    - Both folders stayed empty and were deleted afterwards.
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED` was unset throughout (every Python command ran in the venv under `env -u OFILT_RUN_SEALED`). BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-2b (supervisor message of 2026-10-06)**, by category:
  - Records only, in PASS3_STATUS.md.
  - The step d pre-flight (`tools/p3_2b_preflight.py`) gave target-only counts.
    - It hashed the dev panel against the registry before reading it, then used `io.load_dev`, `targets.add_targets` and the P3-0b Part A rule (predictors only through non-missingness).
    - It reported kept rows, T_source, K, K16 and the kept rows per ticker. No predictor value entered any computation.
  - Synthetic only:
    - the warp-path check;
    - the sealed-run tool's synthetic runs (the two smoke runs, the test runs, and one diagnostic run with one refusal check);
    - `tests/test_p3_sealed_run.py`.
  - The synthetic runs used `OFILT_DATA_DIR` pointed at an empty folder and `TMPDIR` at a folder of their own.
    - No data file was read, and no `DevCalibrator` was built on real data. The stand-in calibrator's log was temporary.
    - BLIND_FIT_LOG's SHA-256, RUN_REGISTRY.jsonl's size and the usual synthetic run registry's size were unchanged across each check.
    - Every folder was deleted afterwards.
  - No `--real` or `--rehearsal` run. `docs/P3_RUN_CONFIG.json` was built from the registry, the reports and the spec (no data file).
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED` was unset throughout (every Python command ran in the venv under `env -u OFILT_RUN_SEALED`). BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-2c (supervisor message of 2026-10-06)**, by category:
  - Records only, and a code listing (the tool, the tests and `sim.py`, printed with `cat -n`).
  - `tests/test_p3_sealed_run.py` ran alone (synthetic; the same tests as P3-2b, with test 4's output captured).
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests. No data file was read otherwise.
  - No `--real` or `--rehearsal` run. No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED` was unset throughout (every Python command ran in the venv under `env -u OFILT_RUN_SEALED`). BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-2d (supervisor message of 2026-10-06)**, by category:
  - Records only, in PASS3_STATUS.md. Code facts read from `sim.py`, `io.py` and `targets.py`.
  - The structural check (`tools/p3_2d_structural.py`, run once): real predictors with synthetic targets.
    - The dev panel was hashed against the registry before it was read, then loaded with `io.load_dev` and built with `targets.add_targets`, which registered the real targets.
    - Its frame kept date, ticker, the exclusion flags, the predictors `DevCalibrator` reads, and the availability (non-missingness) of `abn_oc` and `beta`. Their values were replaced by synthetic ones; every `y_*`, `ao_*`, `open`, `close` and `prev_close` column was dropped.
    - The real targets were registered and never computed with; the fingerprint guard checked the synthetic-labelled draw against them.
    - One `DevCalibrator` was built on the synthetic-labelled frame with a temporary log. Booleans and counts were printed.
  - The smoke rehearsal (`tools/p3_3_rehearse.sh --smoke 20`, from a scratch clone with the same files; two runs of `--rehearsal`): the dev panel was loaded (hash-checked; `io.load_dev`, `targets.add_targets`) only to populate the fingerprint registry (target-only; DQ1.5).
    - The draws are synthetic stand-in draws, and the sealed fit in each run was the stand-in's, logged to a temporary file.
    - Only aggregates were written, under `/tmp/p3_3_smoke_*`, and deleted afterwards. The clone was deleted afterwards.
  - Synthetic tests: `tests/test_p3_sealed_run.py` (including tiny synthetic runs) and `tests/test_p3_2d_structural.py`.
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - No `--real` run, and the full rehearsal was not started. No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED` was unset throughout (every Python command ran in the venv under `env -u OFILT_RUN_SEALED`; the rehearsal script was started under `env -u OFILT_RUN_SEALED`). BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.

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
- P3-1b c: two probe details the item did not fix.
  - Panel B used `p_excl = 0`, with `b = 0`. `tools/c7_mc.py` builds its panels with `p_excl = 0.02`. With 0, `earn_flag` is 0 everywhere, as in a DevCalibrator draw and consistent with the all-False masks the item specifies.
  - `fctests.pair` and `fctests.clark_west` on the row subset were given `provenance="synthetic"` explicitly. The probe also printed whether the subset kept `attrs['provenance']`: it did, in every run.
- P3-2a c.1, the Wilson citation: the supervisor's message cited `tools/report_B7.py`, which has no Wilson function. `calib.wilson` mirrors `tools/report_B7b.py:37-42`, as test 5 (B7b's interval) requires; `fctests.wilson` is the same arithmetic, clipped to [0, 1].
- P3-2a e, chunk equivalence: chunked and unchunked reports are compared with the Runtime section excluded (wall-clock times and the chunk count), as D16 excluded `runtime_s`. They were identical (R = 4) at both seed bases.
- P3-2a c, `calib.py`'s first write: it ended in an unfinished placeholder line (invalid syntax). It was rewritten in full before any import, test or run.
- P3-2a e, the STOP: run 1's gate G2 failed (n10 = 0, n01 = 9).
  - G2 was replaced by G2′ before run 2 (Decision log). Run 1's report is kept byte for byte as `reports/P3_2a_warp_check_run1.md`.
  - `tools/p3_2a_warp_check.py` changed only as the continuation's step e lists: `--seed-base`, G2′, the information counts at the ends of q_warp(0.95)'s interval, and the superseded G2 printed and labelled. `--out` already existed with the required default and is unchanged. The docstring's design and gate lines were updated to match.
  - Run 2 used fresh seeds (spec seed + 4,100,000 + r) and passed G1 and G2′.
- P3-2a g.1, a records correction: P3-1 added `tests/test_p3_1_sesoi.py` (5 tests) without a Test changes row, because P3-1's record step did not ask for one. The continuation's step g refers to rows "as at P3-0b and P3-1", so the missing P3-1 row was added at P3-2a, labelled as such.
- P3-2b g, the tests' first run: 6 of the tests passed, and `setUpClass` of the tiny-run tests errored.
  - The cause was a bug in the test's setup, not in the tool. The test set each subprocess's `TMPDIR` to its own folder and passed an `--out-dir` outside it, which the tool refuses by design.
  - Diagnosis before the one rerun: the tool was run directly once (synthetic, `--smoke 2`, contained in `/tmp/p3_2b_dbg_*`) and completed with no error. One refusal check confirmed that an `--out-dir` outside the temporary locations is refused and nothing is written.
  - The test alone was fixed: `--out-dir` now lies inside the run's `TMPDIR`. The one rerun passed (9 of 9). Both runs, the diagnosis and the diff are in the P3-2b report.
- P3-2b f, the tree check in real mode (for the supervisor). DQ1.3 forbids the script to import `subprocess`, so it checks the tree with `registry.git_state()`, which runs `git status --porcelain --untracked-files=no` (registry.py:87-90). A modified tracked file refuses the run; an untracked file does not. A stricter check needs a decision before P3-4.
- P3-2b f, other design choices the item did not fix (for review):
  - `--out-dir` in synthetic modes may lie under `/tmp` or under the system temporary directory (needed for the tests' temporary folders on macOS). Never inside the repository.
  - The configuration has two keys beyond step e's list: `stand_in`, which describes the stand-in (with its counts read from `reports/P3_0b_preflight.md`), and `early_window_before` (K's cut date, read from `reports/P3_2b_preflight.md`).
  - The `rules` are stored as the Decision-log lines with their `> ` markers.
  - MDE80 per method uses cells 0, 2, 3 and 4 (b = 0, 0.10, 0.25 and 0.40, as B7b). Its cross-checks use sd(b̂) and the mean se pooled over cells 0 to 4.
  - H3's bootstrap decision uses c_boot_h3, the 0.95 order statistic of |t*_h3| pooled over cells 0 to 4 (D3.5).
  - A task's exception is recorded with the line number of its innermost frame in this script.
  - Real mode takes no `--out-dir`.
- P3-2b g, test 4: the real-mode conditions are tested on the pure function `mode_refusal`, with the sealed value passed as an argument. No test sets the `OFILT_RUN_SEALED` environment variable; the subprocess test removes it from the child's environment.
- P3-2b, the optional reuse-the-first-fit variant: the tool uses `calib.bootstrap_t_given_fit`, a new function appended to `calib.py`, to avoid refitting each draw a second time. Test 2 shows it returns exactly `calib.bootstrap_t`'s t*. Every existing function of `calib.py` is unchanged: the P3-2a file is a byte prefix of the new one.
- P3-2c d: besides the test 4 change, the diff adds the two imports it needs (`import contextlib` and `from io import StringIO`). Nothing else in the file changed.
- P3-2d f, where the smoke rehearsal ran: `tools/p3_3_rehearse.sh` refuses a dirty tree (its step 2), and REPO held this item's uncommitted files.
  - It ran from a scratch clone, `/tmp/p3_2d_clone`: a local clone of HEAD `b94d8a4` with no remote, plus this item's files in one local commit (`39a39cc…`, never pushed).
  - All 134 files were byte-identical to REPO's working tree, and the clone's tree was clean.
  - The clone and the outputs were deleted afterwards. REPO's HEAD, BLIND_FIT_LOG and RUN_REGISTRY.jsonl were unchanged, as was the usual temporary run registry.
- P3-2d d, R2's scope: the generic handlers print only `<class> at line <n>`, and the `AbortRun` handlers print only a line number. The `Refused` handler still prints its reason. That reason is a refusal message the tool composes itself (a mode combination, the sealed variable, the configuration SHA-256, the tree, or `validate_config`'s key names), with no data value; test 4, which this item leaves unchanged, asserts it.
- P3-2d e, the structural check's draw used `n_dates` = T_conf (1,013), the sealed run's length, for the lag-6 gate (at the source length of 1,439 dates the DK lag would be 7). The check reads the calibrator's private row bounds for its row count; that tool is not the sealed-run tool.
- P3-2d f, the rehearsal script's last summary line is "the larger total" of the two runs, as specified. In smoke mode that is the smoke total (105 s), not a full-count projection. The P3-2d report gives the per-task rates and the full-count projection (1.92 h), computed by script from the two runs' runtime sections.
- P3-2d f, the script has no shebang line: its first line is `set -euo pipefail`, as specified, and it is run with `bash`.
