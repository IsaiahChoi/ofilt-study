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
| P3-2d Review changes R1, R2; structural check; rehearsal script | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-2d`. Report `/tmp/p3_2d.txt`; planned STOP for the supervisor's review before Isaiah starts the full rehearsal. Structural gate passed; smoke rehearsal PASSED (projected full run 1.92 h with the registry populated). P3-2c acceptance, the review's decisions (R1, R2, R3), the rehearsal procedure and the records rule recorded. R1 and R2 in `tools/p3_sealed_run.py` (configuration unchanged); the structural check `tools/p3_2d_structural.py` (R3); `tools/p3_3_rehearse.sh` with a `--smoke 20` run. No `--real` run; the full rehearsal not started |
| P3-3a Rehearsal on record; DQ5 line-7 patch; DQ6 facts | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-3a`. Report `/tmp/p3_3a.txt`; planned STOP for the supervisor's review of the patch, the plausibility table (P9 False: the early-window flag) and the DQ6 facts. P3-2d acceptance, the P3-2e facts, the rehearsal (PASSED; about 2 h) and DQ5 recorded. The rehearsal's log, run 1's outputs and the P3-2e report copied into `reports/`; plausibility table of the synthetic outputs; the line-7 test changes rehearsed in scratch clones and written to `docs/P3_DQ5_line7.patch` (applied only after the real run); read-only listing for DQ6 |
| P3-3b T6 leak fixed; rehearsal script bound to the configuration; reports trail | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-3b`. Report `/tmp/p3_3b.txt`; planned STOP: the supervisor reviews the report, then gives Isaiah the full-rehearsal command with the new hash. P3-3a acceptance, D4.3 amended (D4.3a centred outputs; D4.3b flag rule), the rehearsal script's binding and the extended records rule recorded. T6 writes only the centred outputs (`centred_block` in `tools/p3_sealed_run.py`); configuration regenerated, SHA-256 `ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e` (key diff exactly `methods.t6`, `centred_reject` added to `outputs`, `rules.D4.3_flag`); `tools/p3_3_rehearse.sh` requires `--expect-config-sha256`; `tests/test_p3_sealed_run.py` 16 tests OK (3 new, test 13 extended); smoke rehearsal PASSED in a scratch clone, and both refusals as stated; the 9 Pass 3 reports copied to `reports/P3_reports/`. No `--real` run; the full rehearsal not started |
| P3-3c P3-3b accepted; D4.3a qualified; rehearsal 2 on record; plausibility table | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-3c`. Report `/tmp/p3_3c.txt`; planned STOP: the supervisor reviews the report, then gives P3-3d, the DQ6 amendment drafts. P3-3b acceptance, D4.3a qualified (winsorised OLS-DK in cells 7 and 8) and rehearsal 2 (PASSED; 1.88 h) recorded. Rehearsal 2's log, its run 1's outputs and the P3-3b report copied into `reports/`; run 2 checked equal to run 1 apart from runtime; plausibility table P1 to P11 of the synthetic outputs, all True (P11, the regression against rehearsal 1, included); read-only fact on `z2` and alpha. No `--real` run; the sealed-run tool run only as `--check-config`; the rehearsal script not run |
| P3-3d P3-3c accepted; read-only facts for DQ6 and the launcher | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-3d`. Report `/tmp/p3_3d.txt`; planned STOP: the supervisor reviews the report, then drafts P3-3e. P3-3c acceptance recorded, with its two post-checkpoint notes under Deviations. The P3-3c report copied to `reports/P3_reports/`. Read-only facts for DQ6 (`calib.py`'s functions; the readers of the spec fields DQ6 would change; the confirmation path; every pin a spec edit could touch; the amendment record format) and for the launcher (the real-mode refusals and log checks; `OFILT_RUN_SEALED=1`; PLAN's pins), in the P3-3d report. No code, test, spec or configuration changed |
| P3-3e P3-3d accepted; DQ6 drafts and dry switches | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-3e`. Report `/tmp/p3_3e.txt`; planned STOP: the supervisor reviews the report and the drafts; Isaiah decides on DQ6; then P3-3f. P3-3d acceptance and the DQ6 drafts' routing recorded. The P3-3d report copied to `reports/P3_reports/`. Read-only facts (the SESOIs; Clark-West in the sealed run; AM-04's record format; the stand-in values). `docs/P3_DQ6_drafts.md`: the supervisor's amendment texts (AM-07 to AM-10), the current lines and records, the `spec.py` validation diffs, the confirmation-code plan, the dry switches and a draft test-change table. Dry switches D1 to D3 in scratch clones (deleted). No code, test, spec or configuration changed in REPO |
| P3-3f P3-3e accepted; DQ6 decided; salvage (b); the launcher | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-3f`. Report `/tmp/p3_3f.txt`; planned STOP: the supervisor reviews the launcher, then gives P3-4. The clone rehearsal ran twice: the first run stopped at the dry run for the power source, and the second, on AC power, passed every gate. P3-3e acceptance, DQ6, salvage option (b) and the launcher's design recorded. The P3-3e report copied to `reports/P3_reports/`. `tools/p3_4_launch.sh` (constants filled by script from their sources) with 8 tests in `tests/test_p3_launch.py`; rehearsed in a scratch clone with `--dry-run` and refusal cases (a) to (k), with a data folder that does not exist. No `--real` run; `OFILT_RUN_SEALED=1` never set |
| P3-4 P3-3f accepted; Isaiah's sanction of the one real sealed fit | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-4`, the sanction commit. Report `/tmp/p3_4.txt`; planned STOP: the supervisor confirms the report, then Isaiah runs the command printed in it. P3-3f acceptance and Isaiah's sanction of the one real sealed fit (DQ1.7) recorded. The P3-3f report copied to `reports/P3_reports/`. After the checkpoint: one launcher dry run at the sanction commit, with a data folder that does not exist, and the command for Isaiah, both in the P3-4 report. No `--real` run; `OFILT_RUN_SEALED=1` never set |
| P3-4b The real sealed fit on record; the post-run checkpoint | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-4b`. Report `/tmp/p3_4b.txt`; planned STOP: the supervisor reviews the report, then gives P3-5. P3-4 acceptance and the real sealed fit recorded (Isaiah's Terminal, 2026-10-07T18:51:20Z to 20:45:12Z; COMPLETE, 0 errors; launcher exit 0). BLIND_FIT_LOG's line 7 and the two outputs committed as the run left them; the launcher's log and the P3-4 report copied into `reports/`; `docs/P3_DQ5_line7.patch` applied unchanged. The outputs read for six structural keys only |
| P3-5 The pre-stated rules applied to the sealed run's outputs | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-5`. Report `/tmp/p3_5.txt` (continued after a STOP under the rerun-once rule); planned STOP: the supervisor reviews the application of the rules, Isaiah approves the selection, then P3-6. P3-4b acceptance recorded. D3.4, D2.6 and D4.3b applied by script to `reports/P3_4_sealed_run.json`: M = dk_normal; CW = calibrated; viable: True; D4.3b flags: none. The binding numbers, the switch's branch and its placeholder values in `reports/P3_5_selection.md` and `.json` (the second run's files; Deviations). Plausibility checks as information. The P3-4b report copied to `reports/P3_reports/` |
| P3-6a P3-5 accepted; the selection approved; the switch rehearsed and written as a patch | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-6a`. Report `/tmp/p3_6a.txt`; planned STOP: the supervisor reviews the switch patch, then gives P3-6b. P3-5 acceptance, Isaiah's approval of the selection, the switch's C7 rerun (D16) and the patch's routing recorded. The P3-5 report copied to `reports/P3_reports/`. The switch (AM-07 ("viable"), AM-09, AM-10; `<date>` 2026-10-07) built in a scratch clone: the spec lines, `spec/SPEC_AMENDMENTS.md`, `spec.py`'s AM-09 validation and the test changes (tiny-run tests 5, 6, 9 and 15 retired; test 17 added). In the clone: the C7 rerun PASS under D16; the suite OK (skipped=6) on 285 tests; the slow tier OK. Written as `docs/P3_6_switch.patch` and checked in a second clone; both clones deleted. No spec, code or test changed in REPO |
| P3-6b The switch: AM-07, AM-09 and AM-10; the C7 rerun | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-6b`. Report `/tmp/p3_6b.txt`; planned STOP: the supervisor reviews the switch commit, then gives P3-7. P3-6a acceptance and the switch recorded. The P3-6a report copied to `reports/P3_reports/`. `docs/P3_6_switch.patch` applied unchanged in REPO (`git apply --check` and `git apply` exit 0; the eight files equal the rehearsal's first clone by SHA-256): the spec FROZEN, SHA-256 `feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26`, with AM-07 ("viable"), AM-09 and AM-10 in `spec/SPEC_AMENDMENTS.md`; `spec.py`'s AM-09 validation; the test changes (tiny-run tests 5, 6, 9 and 15 retired; test 17 added). The C7 rerun in REPO (4 chunks) passed D16 (C7_mc.json PASS; C7_h1_same_dgp.json PASS), 0 floats differing; the slow tier OK. `--check-config`: valid: False, exit 2, the one `spec_sha256` problem (DQ6). No `--real` run; `OFILT_RUN_SEALED=1` never set |
| P3-7a P3-6b accepted; read-only facts for the final records and the tag | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-7a`. Report `/tmp/p3_7a.txt`; planned STOP: the supervisor reviews the facts, then gives P3-7b. P3-6b acceptance, the new builder session and the final records' routing recorded. The boot and P3-6b reports copied to `reports/P3_reports/`. Read-only facts for P3-7b and P3-8 (step c, in the report): of the 16 named documents, 14 are tracked, each equal to its Project copy (14 of 14); not tracked: `DECISIONS_ADDENDUM.md`, `MANIFEST.json`; every pin on them; PLAN.md §8 and its Pass 3 lines; DATA_PROVENANCE §4.5; PROJECT_SETUP and `test_project_claims`; Flag 4; the handoffs by hash (H2, H3 found; H0, H1 not found); the reports trail; the checkpoint chain; the tag gate; the hygiene checks. No code, test, spec or configuration changed |
| P3-7a2 Read-only facts, continued: the tests that pin the documents, read the tags or call the guard | done; accepted by Isaiah 2026-10-07 | Read-only; no checkpoint. Report /tmp/p3_7a2.txt, copied at P3-7b. Its step b ran twice under the rerun-once rule (b.4's own matching rules). |
| P3-7b P3-7a and P3-7a2 accepted; the final Pass 3 records, rehearsed in a scratch clone | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-7b`. Report `/tmp/p3_7b.txt`; planned STOP: the supervisor reviews the report, then gives P3-8. P3-7a and P3-7a2 acceptance and the final records recorded. The P3-7a and P3-7a2 reports copied to `reports/P3_reports/`. Read-only facts for P3-8 (step c, in the report). From the supervisor's kit, checked by SHA-256: `docs/DECISIONS_P71_onward.md` new; PLAN v2.5, README, PROJECT_SETUP and DATA_PROVENANCE replaced whole; their pins moved in three tests (12 rows, P81). Rehearsed first in a scratch clone: the apply's checks True; the suite OK (skipped=6) (Ran 285 tests). REPO equals the clone on the eight paths. No tag created or deleted; `tools/p3_sealed_run.py` run only with `--check-config` |
| P3-8a P3-7b accepted; read-only facts for the tag-aware tests | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-8a`. Report `/tmp/p3_8a.txt`; planned STOP: the supervisor reads the facts of step b, then gives P3-8b. P3-7b acceptance, the tag-aware tests' routing and the note on the fifth supervisor chat recorded. The P3-7b report copied to `reports/P3_reports/`. Read-only facts for P3-8b (step b, in the report): the tag and guard tests, the tests that pass dev_real frames to an entry point and their classes, the code they reach, the skips, the data paths, `tools/checkpoint.sh`, git, and the SHA-256 of every tracked file under `tests/`, `ofilt/` and `tools/` (84). The suite in a scratch clone, verbose: `Ran 285 tests`, `OK (skipped=6)`, by module (39 modules); the six skips named. No tag created or deleted; `tools/p3_sealed_run.py` run only with `--check-config` |
| P3-8b P3-8a accepted; the tag-aware tests, rehearsed in a scratch clone with a scratch tag; the commit to be tagged | done; accepted by Isaiah 2026-10-07 | `checkpoint: P3-8b`. Report `/tmp/p3_8b.txt`; planned STOP: the supervisor reviews the report, then Isaiah tags. P3-8a acceptance, the code read, the tag-aware tests and the tag's routing recorded. The P3-8a report copied to `reports/P3_reports/`. `tests/tag_state.py` (new) and the edits E1 to E22 in nine tests, applied by one script, first in a scratch clone and then in REPO (equal by SHA-256). In the clone: the suite without a tag, `Ran 285 tests`, `OK (skipped=6)`; a scratch annotated `spec-dev-v1` on HEAD; the guard check (dev_real granted, confirm_real refused for `prereg-v1` alone, `load_confirm` denied and logged); the suite with the scratch tag, `Ran 285 tests`, `OK (skipped=6)`, every test's result the same; the clone, with its tag, deleted. No tag in REPO; `tools/p3_sealed_run.py` run only with `--check-config` |
| P3-8c spec-dev-v1 verified; P3-8b accepted; Pass 3 closed | done | `checkpoint: P3-8c`. Report `/tmp/p3_8c.txt`, copied at Pass 4's first checkpoint; planned STOP: the supervisor reviews the report, then the Pass 3 Project upload. P3-8b acceptance, `spec-dev-v1` and Pass 3's completion recorded. The P3-8b report copied to `reports/P3_reports/`. The tag (read-only): annotated (tag object `cee3b49e81d16f1f32e546cac9524b209ac1e493`), on the P3-8b commit, tagger date 2026-10-07, its message as given, the spec at the tag the frozen spec. The guard check in REPO with the tag: dev_real granted, confirm_real refused for `prereg-v1` alone, `load_confirm` denied. The suite with the tag present, in a scratch clone: `Ran 285 tests`, `OK (skipped=6)`, every test's result as in P3-8b's tagged run. No tag created, moved or deleted in REPO; `tools/p3_sealed_run.py` run only with `--check-config` |
| Pass 3 | done (2026-10-07) | The calibration is locked by the annotated spec-dev-v1 on f5271c03481b7514a1ec4b7e739fb85fbce8a774 (P3-8b), verified at P3-8c. Next: the Pass 3 Project upload, then Pass 4 under its own builder prompt. |

## Next action

The supervisor reviews P3-8c. Then the Pass 3 Project upload (PROJECT_SETUP, "After Pass 3"), re-hashed by the supervisor; then Pass 4, under its own builder prompt, whose first checkpoint copies the P3-8c report.

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

> - P3-2d accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `1c48d381bb794e65d6532ba915ea782761ba58b2`, including P3-2d's recorded deviations: the smoke rehearsal in a scratch clone; R2's scope; the structural check's draw length and private row bounds; the rehearsal script's summary line; and its missing shebang.
>   - The structural check (R3) passed every boolean: `DevCalibrator` built on the real frame's structure, with synthetic targets, gave T = 1,439 and rows = 4,192.
> - P3-2e (read-only; 2026-10-06), the last part of the real path not exercised before.
>   - `_design_core` stores its `provenance` argument in the returned `Design` and nothing else (`inference.py:85`, `:136-138`). It calls no function of `blind`, `io`, `registry` or the guard, and its behaviour does not depend on provenance. `inference.py` and `sim.py` are unchanged since `pass1-final`.
>   - `_sealed_blind_fit` refuses a wrong provenance, or a missing `OFILT_RUN_SEALED=1`, before it writes its log line, and it writes the line before the fit (`sim.py:157-163`).
>   - Every way `_design_core` can fail after that line (a forbidden target, missing columns, an empty sample, non-finite values, a rank-deficient design) is ruled out on the real path. The structural check built the same columns, rows and design matrix, and P3-0b found every required value finite.
> - The rehearsal (Isaiah's Terminal, 2026-10-07T00:12:19Z to 04:05:04Z, HEAD `1c48d38`): REHEARSAL PASSED (DQ1.5).
>   - Two full `--rehearsal` runs completed with no error. Their outputs are identical apart from runtime.
>   - BLIND_FIT_LOG, the configuration, RUN_REGISTRY.jsonl, the tool, `calib.py` and the usual temporary run registry were all unchanged, and the tree stayed clean.
>   - Runtimes were 6,955.0 s and 7,004.9 s. **The expected duration of the real run is about 2 hours** (1.95 h), stated before the sanction as DQ1.5 requires.
> - DQ5 (Isaiah, 2026-10-07, on the supervisor's recommendation): the test changes that the real line 7 requires.
>   - A post-run checkpoint, the first commit after the real run, commits BLIND_FIT_LOG's line 7, `reports/P3_4_sealed_run.json` and `reports/P3_4_sealed_run.md`. It also applies, unchanged, the line-7 test changes in `docs/P3_DQ5_line7.patch`, which the supervisor reviews before the sanction.
>   - Lines 1 to 6 stay pinned as Pass 1's history: the six-line prefix stays byte-identical, with SHA-256 `dad93285d2911abc6c7145c160d729df1126b24b439302bd8577cf407d397301`. Line 7 is pinned by its fields: provenance `dev_real`; panel hash `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68`; spec hash `0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee408561f68f96fd94d3b0f9` (the configuration's `spec_sha256`); 5,124 input rows; and a caller naming `tools/p3_sealed_run.py`. Line 7's time and caller text cannot be known in advance, so no whole-file hash of the seven-line log is pinned.
>   - The spec amendments (AM-07 onward) and their test changes come later, in the switch (DQ6).

> - P3-3a accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `cdded9b444ea889ef64859acf7883b89ffecf29b`, including P3-3a's recorded deviations: the copy script's zsh bug and its one rerun; the readings of P4 and P5; the P9 context; the patch script; and the flag.
>   - The DQ5 patch `docs/P3_DQ5_line7.patch` (SHA-256 `8b4eaa35b45605566f3a1447b61647f0ee55252f82852091c8189e9f00e2977c`) is approved. With a dummy line 7 and stand-in outputs the full suite passes; in the six-line state it fails only in the two patched tests.
>   - The plausibility table: P1 to P8 and P10 True; P9 False, which the next decision resolves.
> - D4.3 amended (Isaiah, 2026-10-07, on the supervisor's recommendation): T6's outputs, after the P9 finding.
>   - The finding. The calibrator's residuals are orthogonal to the design over the full estimation sample only.
>     - A draw that resamples only a window of source dates (cells 7 and 8) carries that window's own coefficient deviation: its b̂ is centred near b + (b̂_W − b̂), where b̂_W is the OLS coefficient on the window's dates and b̂ the full-sample one.
>     - An estimator other than the calibrator's OLS (Huber-DK, winsorised OLS-DK) is likewise centred near b plus the difference between its own full-sample estimate and OLS's, in every T6 cell.
>     - The rehearsal's stand-in showed this: a mean bias of −0.094 and a rejection rate of 33.7% at b = 0 in cell 7, and a Huber mean bias of +0.0115 in cell 5. The supervisor reproduced the mechanism in a toy calibrator.
>     - On the real panel, T6's mean biases, rejection rates and coverages would therefore reveal real-data differences between FX coefficients. That is a relation between FX and real targets, which the blinding rules forbid before `spec-dev-v1`.
>   - D4.3a The outputs. For every T6 cell (5 to 8) and every estimator, the sealed run computes and writes only:
>     - the centred rejection rate: the share of draws with |b̂ − b̄| > 1.959964·se, where b̄ is the cell's own mean of b̂, held in memory only, with its Wilson interval;
>     - sd(b̂), mean se and se/sd;
>     - for Huber-DK, the mean share downweighted.
>     - No mean bias, uncentred rejection rate or coverage is computed or written for T6. Centring removes any constant shift exactly, so these outputs do not depend on the deviations above. Cells 0 to 4 and 9 to 11 (the calibrator's own OLS on full draws) are unchanged.
>   - D4.3b The flag rule. If an estimator's centred rejection rate at b = 0 on early-window draws (cell 7) lies outside [3.5%, 6.5%], the pre-registration flags that robustness row as unreliable on coarse-grid periods. This replaces D4.3's flag sentence, and the configuration copies this line.
>   - The deviations themselves cannot be measured before `spec-dev-v1` without breaking the blinding; Pass 4 may examine them on dev. The pre-registration discloses the finding and this amendment.
> - The rehearsal script bound to the configuration (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - `tools/p3_3_rehearse.sh` takes a required `--expect-config-sha256` and refuses unless the configuration file's SHA-256 equals it. This replaces the comparison with the hash recorded in `reports/P3_2b_smoke.md`.
>   - Because the tool and the configuration change, the full rehearsal (DQ1.5) is run again, twice, on the new commit and before the sanction.
> - The records rule now also reserves the prefix `>   - D4.3b The flag rule.`.

> - P3-3b accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `56897128f2e93068b60747640a87ce4cd4148241`, including P3-3b's recorded deviations: the records-rule count and its correction; the flag's placement; `t6_block` replaced in place by `centred_block`; the winsorised estimator and test 16's scope (resolved by the next decision); and the Test changes preamble.
>   - The configuration `docs/P3_RUN_CONFIG.json`, SHA-256 `ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e`, is the one rehearsed below. This acceptance does not sanction it.
> - D4.3a qualified (Isaiah, 2026-10-07, on the supervisor's recommendation): winsorised OLS-DK in the early-window cells.
>   - The statement in D4.3a that the centred outputs do not depend on the deviations holds exactly for OLS-DK and Huber-DK, which are regression-equivariant (test 16), and approximately for winsorised OLS-DK in cells 7 and 8.
>   - Mechanism. Winsorised OLS-DK regresses on the clipped FX columns. The part of the window's FX-coefficient deviation that lies along the clipped excess (the dates beyond the spec's bounds, for `usdjpy_ret` and `eurusd_ret`) shifts each draw's b̂ by an amount that varies across draws, and changes its se. The dependence is first order in the deviation, with a coefficient set by the window's residuals on the clipped dates, of unknown sign. This replaces the reading "at second order" in P3-3b's deviation.
>   - Size (the supervisor's synthetic toy; no data): at a deviation of 0.2, sd(b̂) moves by about 0.5–1.2% (RMS; at most 2.5%), mean se by about 0.4–1.1% (RMS; at most 2.3%), se/sd by at most 0.6%, and the centred count by at most 6 of 1,000; about half that at 0.1. The Monte Carlo noise of sd(b̂) at 1,000 draws is about 2–4%.
>   - Accepted with disclosure, without changing T6. The outputs cannot identify the deviation, because their value at a zero deviation depends on the unknown real residuals (in the toy, the winsorised-to-OLS sd ratio ranged from about 0.5 to 1.3 across datasets). No rule is materially affected: D4.3b reads one count, which can move by a few.
>   - Cells 5 and 6 carry no such channel: the calibrator's residuals are orthogonal to the full design.
>   - The pre-registration discloses this together with D4.3 amended.
> - Rehearsal 2 on record (2026-10-07).
>   - The full rehearsal (DQ1.5; `tools/p3_3_rehearse.sh --expect-config-sha256` with the configuration above) ran in Isaiah's Terminal on `56897128f2e93068b60747640a87ce4cd4148241`, from 2026-10-07T05:41:48Z to 09:27:07Z, and printed `REHEARSAL PASSED`.
>   - Both runs printed `COMPLETE` with 0 errors and were identical apart from runtime; totals 6,757.6 s and 6,757.9 s. Every baseline hash and size was unchanged, and the tree was clean with HEAD unchanged.
>   - The expected duration of the real run is about 2 hours (1.88 h here; 1.93 h and 1.95 h at rehearsal 1).
>   - The plausibility checks P1 to P11 were stated before this run (the supervisor's handoff of 2026-10-07, Appendix C) and computed at P3-3c; the table is in Test results.

> - P3-3c accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `f5e6d281d1b95102fc19a6aab554d1af331d7828`, including P3-3c's recorded deviations (the expected values read from the saved message; the table's layout; the extra alpha print) and its two post-checkpoint notes, which P3-3d records under Deviations.
>   - The plausibility table on rehearsal 2's run 1: P1 to P11 all True. P11 found no difference from rehearsal 1 outside `runtime`, `config_sha256`, `head` and cells 5 to 8 (13 top-level keys, with cells 0 to 4, compared exactly).
>   - `z2` is `stats.norm.ppf(1 - alpha / 2)` with alpha 0.05, from the spec's `inference.alpha` through the configuration's `methods.alpha` (`tools/p3_sealed_run.py:397-398`): the quantile D4.3a states.

> - P3-3d accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `1fd79933b16ae98344a9b58abd1f21a4e5dd8198`, including P3-3d's recorded deviations: the typed informational hash; the first listing run in a zsh loop; the typed hash in the C7 search; and the listings beyond the items.
>   - The facts for DQ6: `inference.reference` is read only by `spec.validate`, and the normal reference is fixed in code (`inference.Result.contrast`, `inference.tost`, `fctests._differential_test`). No confirmation entry point exists yet. `calib.bootstrap_test` implements D3.1 for H1 only; `calib.rejects` and `calib.tost_declares` apply a supplied critical value; nothing yet applies a supplied Clark–West critical value.
>   - The facts for the launcher: in real mode the tool refuses unless BLIND_FIT_LOG has 6 lines before the fit (after it loads the panel, before any write); its tree check counts tracked files only; it does not refuse existing outputs, which it overwrites; and no test scans `tools/` as a whole for `OFILT_RUN_SEALED=1`.
> - The DQ6 drafts (a routing record, not a decision): P3-3e writes the supervisor's proposed amendment texts to `docs/P3_DQ6_drafts.md` and dry-runs them in scratch clones. Isaiah decides on them after the supervisor's review, before the sanction.

> - P3-3e accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `025d9c432b9592a5a062f24c07ccabd3bbf074c8`, including P3-3e's recorded deviations.
>   - The sealed run's Clark–West statistic is `fctests.clark_west(...)["stat"]` for M3 against M2 on the last 1,013 dates of each draw, at the spec's lag (6): the statistic a confirmation computes, so c_CW,cal applies to it (P3-3e, step c.2).
>   - With the DQ5 patch, a dummy line 7 and stand-in outputs, the suite passes (280, OK): the patch still holds at HEAD.
> - DQ6 decided (Isaiah, 2026-10-07, on the supervisor's recommendation): the switch's amendments, as drafted in `docs/P3_DQ6_drafts.md` (SHA-256 `9ad9b0941952dbaee6b45e53940d5f1ed8b206abdacc2198d60733e04d3697c3`).
>   - Its sections 2 to 4 are adopted: the texts and templates of AM-07 (both variants), AM-08 (both variants), AM-09 and AM-10; the `spec.py` validation changes; and the confirmation-code plan. P3-5 selects the branch by D3.4 and D2.6. P3-6 fills the placeholders from the run's outputs and applies the branch in one commit, with the C7 rerun.
>   - AM-10 needs no validation change: `validate` keeps accepting DRAFT or FROZEN, and the tests pin FROZEN.
>   - Its section 6, the test-change table, is adopted as P3-6's plan. P3-6 first rehearses the whole switch in a scratch clone, C7 rerun included, and confirms or corrects every row before the switch commit. The three rows for `tests/test_p3_sealed_run.py` rest on the builder's reading and are confirmed there. Tests retired at the switch (the tiny-run tests 5, 6, 9 and 15) are listed in Test changes with their reason.
>   - From the switch on, the configuration differs from a rebuild by its `spec_sha256`, by design. The records rule's `--check-config` step then ends; each later records step checks instead that the SHA-256 of `docs/P3_RUN_CONFIG.json` is still `ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e`.
> - Salvage (Isaiah, 2026-10-07, on the supervisor's recommendation): option (b).
>   - No salvage path is added before the run, because any change to `tools/p3_sealed_run.py` would require a third full rehearsal. DQ1.4 stands.
>   - If a task fails in the real run, a new reviewed item adds the salvage path: line 8, the identical configuration and seeds, every completed task reproducing exactly. It runs only after that review and a new sanction by Isaiah.
>   - A second `--real` run as the tool stands is refused at its 6-line check, before the fit and before any write (P3-3d, step c.6).
> - The launcher (Isaiah, 2026-10-07, on the supervisor's recommendation): `tools/p3_4_launch.sh`, as P3-3f step e specifies. It wraps the one sealed-run command with pre-checks and post-checks, and changes nothing the sealed run executes. It is committed, statically tested, and rehearsed in a scratch clone with `--dry-run` and a data folder that does not exist.

> - P3-3f accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `9629b6f766a63a0f2d7f030e57a0554e9bf42a83`, including P3-3f's recorded deviations: the power-source STOP and the one rerun; the refused `bash -c` listing; the launcher's choices beyond the item's text; and how the files were made.
>   - The launcher `tools/p3_4_launch.sh`, SHA-256 `d80296d490ea7cad5cdeb49cdfa7bb71f01edad1a4da6cf30f2f9ab0b51686ba`, was reviewed line by line by the supervisor and executed, byte-identical, in the supervisor's sandbox against a stub tool in a fake repository. Its real path behaved as specified for a completed run, an abort, a crash without a status line, and a refusal: it captured the tool's exit code through `PIPESTATUS`, ran every post-check, and printed none of the tool's other output. Check 9, the battery refusal and the dry run also behaved as specified.
> - The sanction (Isaiah, 2026-10-07, on the supervisor's recommendation; DQ1.7): the one real sealed fit, dev_real line 7 of BLIND_FIT_LOG.
>   - It is run once, by `tools/p3_4_launch.sh`, in Isaiah's own Terminal, on AC power, at the commit that records this sanction, with `--expect-config-sha256 ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e` and the data folder `$HOME/Desktop/FX_Project/data`.
>   - It runs the rehearsed code (rehearsal 2, PASSED): `tools/p3_sealed_run.py` `bd21c4503490aee0561c618f6ee02fd50e6be0dea4e5152f10d7579e4e609837`, `ofilt/drift/calib.py` `31f7b8ac3d81ff5123f8dc3f0bc2cf1871652f132d15653915c94b5a79224ad6`, the configuration `ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e` and the spec `0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee408561f68f96fd94d3b0f9`. The expected duration is about 2 hours.
>   - Nothing in the repository changes between this commit and the run, and nothing touches it during the run. The post-run checkpoint commits line 7 and the two outputs, and applies `docs/P3_DQ5_line7.patch` unchanged.
>   - If the run fails, salvage follows the P3-3f decision (option (b)): a new reviewed item and a new sanction.

> - P3-4 accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `b634cc04a73502821cd27850282659d683015b32`, the sanction commit. The final dry run at that commit passed every check.
> - The real sealed fit on record (2026-10-07).
>   - Isaiah ran `tools/p3_4_launch.sh` in his own Terminal at the sanction commit, on AC power, from 2026-10-07T18:51:20Z to 20:45:12Z (1 h 54 min). Every pre-check was True.
>   - The tool printed `COMPLETE` with 0 errors and exited 0, and the launcher exited 0. BLIND_FIT_LOG gained exactly one line, dev_real line 7, and its first six lines are unchanged.
>   - The outputs: `reports/P3_4_sealed_run.json` (SHA-256 `65e68c8cf9a76afda05869e8772b345e49f30fa24bcad6790de28d6bcab58942`) and `reports/P3_4_sealed_run.md` (SHA-256 `8acbece13ff366ba39a097cf927e9c168471eff190f7dc4eb8b3307fc00c29a9`).
>   - Line 7, the two outputs and the launcher's log (`reports/P3_4_launch.log`) are committed at P3-4b, with `docs/P3_DQ5_line7.patch` applied unchanged (DQ5).
>   - The outputs' aggregates are read first at P3-5, which applies the pre-stated rules (D2.6, D3.4, D4.3b).

> - P3-4b accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `57ceb44c4ebf79ac086c9aec3c8bc5c2601f7822`: line 7, the two outputs (their hashes equal those the launcher printed), the launcher's log, and the DQ5 patch applied unchanged.
> - The rules applied (a routing record, not a decision): P3-5 applied D3.4, D2.6 and D4.3b to `reports/P3_4_sealed_run.json` by script, as written before the run. The bands were tested on the point estimates in exact integer arithmetic. The results, the binding numbers and the switch's branch and placeholder values are in `reports/P3_5_selection.md` and `.json`. Isaiah approves them after the supervisor's review, at P3-6.

> - P3-5 accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `5b33bd0fb9b9b993105af0116d734918e606e120`, including P3-5's recorded deviations: the second run of the rules script, the comparison's STOP and its corrected rerun, and the state checks' typed values and count.
>   - The supervisor recomputed every rule test and MDE80 from the printed integers, with the same results.
> - The selection approved (Isaiah, 2026-10-07, on the supervisor's recommendation): the outcomes of the pre-stated rules, as `reports/P3_5_selection.json` (SHA-256 `110a045e5ff6c2f0657fecd93c2c9d400c679599ffbde09354ea9f8f5bd207d3`) records them.
>   - H1 (D3.4): DK with the normal reference. Its rate at b = 0 was 291 of 5,000 (5.82%), inside [3.5%, 6.5%]. AM-08 is unused.
>   - Clark–West (D3.4): the normal reference's rate at b = 0 was 66 of 2,000 (3.30%), outside the band, so the primary comparison uses c_CW,cal = 1.411608406163672 (AM-09).
>   - TOST (D2.6): viable under DK-normal. Equivalence was declared at b = 0 in 5,000 of 5,000 draws at the primary SESOI, and in 296 of 5,000 (5.92%) at b = +SESOI (AM-07, variant "viable").
>   - D4.3b: no robustness row is flagged (cell 7: 55, 57 and 52 of 1,000).
>   - The binding numbers under DK-normal: rejection 21.2%, 80.9% and 99.5% at b = 0.10, 0.25 and 0.40; MDE80 0.2471 (probit interpolated).
>   - The switch applies AM-07 ("viable"), AM-09 and AM-10, with `<date>` 2026-10-07, the date of this approval.
> - The switch's C7 rerun (Isaiah, 2026-10-07, on the supervisor's recommendation): D16's criterion, as amended at P68 (`runtime_s` excluded), applies to the one C7 rerun of the Pass 3 switch, with `key.spec_sha256` equal to the switched spec's SHA-256. It runs as at P2-3b: `tools/c7_mc.py --budget 90` in foreground chunks until complete, compared by `tools/p2_3b_c7_compare.py`, then the slow tier.
> - The switch patch (a routing record, not a decision): P3-6a builds the switch in a scratch clone (the spec lines, `spec/SPEC_AMENDMENTS.md`, `spec.py`'s AM-09 validation and the test changes), rehearses it whole with the C7 rerun, and writes it to `docs/P3_6_switch.patch`. P3-6b applies it unchanged, after the supervisor's review, in the switch commit.

> - P3-6a accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `6338409a30f57758523de8ec47a004774c45c0cd`, including P3-6a's recorded deviations and the notes in its report: the two zsh loops, the scratch clone's local commits, the `import json` choices, the sixth skip, the file-list check and its one rerun, and the records script's corrections before its run and its two formatting fixes after it.
>   - The switch patch `docs/P3_6_switch.patch` (SHA-256 `cd9d317db33ee04c8c627d1386565e3c5ad19f9ddeb511286c576a946515281a`) is approved as rehearsed, to be applied unchanged. The supervisor checked the three spec lines and the three amendment records against the current lines, `spec.py`'s AM-09 change, and every test change against "never weaken a test" and PASS2_ADDENDUM §5, and recomputed the counts.
>   - The sixth skip is by design: once the status is FROZEN, `tests/test_io.py`'s check that no unblinding tag exists while the spec is DRAFT skips (AM-10; `docs/P3_DQ6_drafts.md` section 6, "Not failures"). Access stays gated by the tag (P46). From the switch on, the expected suite result is OK with 6 skips; the 5 expected in P3-6a's step d.6 was an error in the supervisor's message.
> - The switch on record (2026-10-07): `docs/P3_6_switch.patch`, applied unchanged in REPO in the switch commit (P3-6b).
>   - The spec `spec/analysis_spec_dev_v1.yaml` is FROZEN, SHA-256 `feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26`. AM-07 (variant "viable"), AM-09 and AM-10 are recorded in `spec/SPEC_AMENDMENTS.md`; AM-08 is unused. `spec.py` validates the amended primary comparison (AM-09).
>   - The one C7 rerun of the Pass 3 switch passed D16's criterion (i) to (iv) for both reports, `runtime_s` excluded, with `key.spec_sha256` equal to the switched spec's SHA-256. The slow tier passed.
>   - The configuration `docs/P3_RUN_CONFIG.json` (SHA-256 `ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e`) is unchanged and differs from a rebuild only by its `spec_sha256` (DQ6). The sealed-run tool therefore refuses every run, real or synthetic (tests 4 and 17 of `tests/test_p3_sealed_run.py`).

> - P3-6b accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `cfc1deff58658eed87d691cb9cb38c60ac55cb97`, the switch commit, including P3-6b's recorded deviations and the notes in its report.
>   - The supervisor recomputed the commit's counts (12 files; 2,425 insertions and 80 deletions) and checked the C7 rerun: bit-identical to the reports it replaced apart from `key.spec_sha256` and `runtime_s` (0 of 2,846 and 0 of 20 floats differ; 2,148 and 13 flags and counts identical; two changed lines in each report).
>   - The committed copy of the P3-6a report has the SHA-256 that the new builder session computed for the file on the Mac before P3-6b (`f7f7ceec3aa248e5c3c6d5c7903a08eecc23a943d4f362b46a41287a3f4a9d9b`).
> - The new builder session (a routing record, not a decision): from P3-6b on, the builder runs in a new Claude Code session. A read-only supervisor message oriented it at the boundary after P3-6a; it found the standing prompt by its SHA-256 (`018c489ff53db0aa069881874e0c4faea0e165a2e23ba02b875963b034dfee36`) as `files/pass3/PASS3_BUILDER_PROMPT_2026-10-06.md` and wrote `/tmp/p3_boot.txt`, copied at P3-7a. Nothing in REPO changed.
> - The final records (a routing record, not a decision): P3-7a prints the facts that the final records and the tag need. P3-7b writes the final records, rehearsed in a scratch clone because PLAN and other documents are pinned. P3-8 is the tag.

> - P3-7a accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd`, including P3-7a's recorded deviations (RAW and OUT pruned from the name search; the readings of c.2 and c.11) and the notes in its report.
>   - Its facts: the 14 tracked documents equal their Project copies; the pins on them; the handoffs located by hash (H2 and H3 under `files/`; Isaiah later found H0 at the top of `~/Desktop/FX_Project` and H1 in `~/Downloads`, each with its recorded SHA-256); the tag gate; the hygiene checks.
> - P3-7a2 accepted (Isaiah, 2026-10-07, on the supervisor's recommendation): read-only, with no checkpoint; its report is copied at P3-7b. Its step b ran twice under the rerun-once rule, because its b.4 rules had three bugs. Its facts: the tests that pin the documents, and those that read the repository's tags or call its guard, which P3-8 makes hold before and after `spec-dev-v1`.
> - The final Pass 3 records (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - `docs/DECISIONS_P71_onward.md` (P71 to P81), new, from the supervisor's kit `p3_7b_kit.tar` (SHA-256 `4a7da1bebee9b5b357fcba85573df7dbf00ab11983ef24c586811bb478329a98`), pinned in `tests/test_docs_p2.py`.
>   - PLAN v2.5, README, PROJECT_SETUP and DATA_PROVENANCE (§4.5, the Pass 3 supervisor chats), replaced whole from the same kit; their pins move in `tests/test_docs_p2.py`, `tests/test_docs_d4.py` and `tests/test_docs_d6.py` (Test changes, P81).
>   - `PASS1_STATUS.md` and the earlier decision files stay as recorded; the P61 citation and the PASS1_STATUS Flag 4 correction are rows of the new file's status index.
>   - The Pass 3 Project upload follows the tag, as PROJECT_SETUP's "After Pass 3" list states; `PASS3_SUPERVISOR_HANDOFF_2026-10-06.md` is retired from the Project.

> - P3-7b accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `42a88bc987321871687097742226dceeb3631059`, including its recorded deviations (the configuration check run only as `--check-config`, on Isaiah's answer in the session; the six reserved prefixes read from the P3-7a message; the edits before the kit and apply scripts' only runs; c.6's `--local` exit codes; the kit-check lines inserted into the Test results by `/tmp/p3_7b_fix.py`) and the notes in its report.
>   - Its facts for P3-8 (step c): besides `test_docs_d3.TestP29Blinding.test_tag_gates`, `test_docs_d3b.TestP36.test_tag_semantics_as_implemented` and `test_blind.TestGuard.test_dev_real_raises_in_main_repo`, step c.5 lists further tests that pass a frame or a design labelled dev_real to an entry point and expect a refusal. Unless a test isolates the guard from REPO's tags, the guard grants dev_real once `spec-dev-v1` is an ancestor of HEAD. Their code, and the code they reach, is read before any tag is created, in REPO or in a scratch clone.
> - The tag-aware tests (a routing record, not a decision): P3-8a prints the read-only facts the code read needs. P3-8b makes the tests that read the repository's tags or call its guard hold before and after `spec-dev-v1`, checks the guard in a scratch clone with a scratch tag, and is the final records commit, which Isaiah tags.
> - The fifth Pass 3 supervisor chat (from the P3-7b review on) is not in DATA_PROVENANCE §4.5, which the P3-7b kit wrote before that chat began. Its real-data contact is recorded in its handoff and is added to DATA_PROVENANCE §4.5 at Pass 4's first records refresh.

> - P3-8a accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `25dad69ca184de575905b7aee80620fcb29172ca`, including its recorded deviations (the clone's verbose log parsed a second time under the rerun-once rule; the readings of b.7) and the notes in its report.
>   - The code read (the supervisor, on P3-8a's step b): once `spec-dev-v1` is an ancestor of HEAD, the only change in the code is that `require_unblinded` grants dev_real; `load_confirm` stays denied, because it requires `prereg-v1`, and the sealed fit does not read the tags. Ten test functions depend on REPO's tags: three assert REPO's state, and seven pass synthetic frames or designs labelled dev_real to an entry point and expect a refusal. No test passes real dev data past the guard; granted, `test_forecast_c1`'s call would append a dev_real line to the tracked `RUN_REGISTRY.jsonl`.
> - The tag-aware tests (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - `test_docs_d3.TestP29Blinding.test_tag_gates`, `test_docs_d3b.TestP36.test_tag_semantics_as_implemented` and `test_blind.TestGuard.test_dev_real_raises_in_main_repo` assert REPO's state on both sides of the tag: without `spec-dev-v1`, as before; with it, that it is annotated, an ancestor of HEAD and on the frozen spec (`feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26`), that dev_real is granted, and that confirm_real is refused for `prereg-v1` alone. `prereg-v1` stays absent on both sides.
>   - The seven refusal tests (in `test_fctests_c5`, `test_forecast_c1`, `test_inference_b1` (two), `test_inference_b2`, `test_inference_b3` and `test_sim_b5`) make their dev_real calls with the guard pointed at a throwaway repository without the tags (`tests/tag_state.py`, `blinded`), so they refuse whatever REPO's tags are, and nothing runs past the guard.
>   - Rehearsed in a scratch clone without a tag and with a scratch annotated `spec-dev-v1`, deleted with the clone; the suite is 285 tests, 6 skipped, with the same result for every test on both sides.
> - The tag (a routing record, not a decision): after the supervisor's review of P3-8b, Isaiah creates the annotated `spec-dev-v1` on this commit, which locks the calibration, and pushes it by name. P3-8c verifies it read-only; P3-8d copies the P3-8b and P3-8c reports and closes the Pass 3 row.

> - P3-8b accepted (Isaiah, 2026-10-07, on the supervisor's recommendation).
>   - Checkpoint `f5271c03481b7514a1ec4b7e739fb85fbce8a774`, including its recorded deviations (the first paste cut off, and only the full message saved and run; the apply's status check in REPO, which also expects step b's report copy) and the notes in its report (one edit to `/tmp/p3_8b_records.py` before its only run; the records of step e describe the clone's deletion, which ran at step f.3).
> - `spec-dev-v1` (Isaiah, 2026-10-07, on the supervisor's recommendation): annotated, on `f5271c03481b7514a1ec4b7e739fb85fbce8a774`, created and pushed by Isaiah. Verified at P3-8c: its commit is an ancestor of HEAD and the spec at the tag is the frozen spec; dev_real is granted, confirm_real is refused for `prereg-v1` alone, and `load_confirm` is denied; the suite with the tag present is 285 tests, 6 skipped, with every test's result as in P3-8b's clone with the scratch tag. The calibration is locked from here (PLAN §8).
> - Pass 3 complete (a routing record, not a decision). Next: the Pass 3 Project upload (PROJECT_SETUP, "After Pass 3"), then Pass 4, the dev first look and the P13(b) dry run, under its own builder prompt; Pass 4's first checkpoint copies the P3-8c report. Carried to Pass 4: `test_docs_d3` and `test_docs_d3b` assert that `BLIND_FIT_LOG` has 7 lines and that `RUN_REGISTRY.jsonl` is empty, which is Pass 3's end state, so Pass 4's first real run changes them by decision; and the fifth supervisor chat's entry in DATA_PROVENANCE §4.5.

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

**P3-3a:**
- The full rehearsal (Isaiah's Terminal, 2026-10-07T00:12:19Z to 04:05:04Z; `reports/P3_3_rehearsal.log`): REHEARSAL PASSED.
  - Totals were 6,955.0 s and 7,004.9 s, and the two outputs are identical apart from runtime.
  - Run 1's outputs are in `reports/P3_3_rehearsal_run1.json` and `.md`. The P3-2e report is in `reports/P3_2e_report.txt`.
- Plausibility table of the rehearsal's synthetic outputs (information; checks P1–P10 in the P3-3a report): P1–P8 and P10 True; **P9 False**. On the early-window cells, OLS-DK and winsorised OLS-DK reject 33.7% and Huber-DK 20.2% at b = 0, with a mean bias of −0.094 (OLS) at both b = 0 and b = 0.25 (Flags).
- The DQ5 patch, rehearsed in scratch clones:
  - clone A, unpatched, with a dummy line 7: 2 failures, `test_docs_d3` and `test_docs_d3b`;
  - clone B, patched, without line 7: 2 failures, only in the patched tests;
  - clone B, patched, with line 7 and the stand-in outputs: 277 tests, OK (skipped=5).
- The full suite ran inside the P3-3a checkpoint; its result is in the P3-3a report (`/tmp/p3_3a.txt`).

**P3-3b:**
- `tests/test_p3_sealed_run.py` alone, after steps d and e: 16 tests (3 new; test 13 extended), OK, on the first run. The tiny runs completed.
- The configuration: deleted, rebuilt with `--write-config`, then `--check-config`: `valid: True`. New SHA-256 `ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e` (was `645ef80ee91c91e81ac4a880ff34b0fc19906bbb3c36f5300575d727dc1d7eaa`).
- The configuration's key diff (by script; the old one from `git show HEAD:docs/P3_RUN_CONFIG.json`): the top-level keys that differ are exactly `methods`, `outputs` and `rules`; inside them, exactly `methods.t6`, `centred_reject` added to `outputs` (nothing removed) and `rules.D4.3_flag`: True.
- Smoke rehearsal (`tools/p3_3_rehearse.sh --smoke 20 --expect-config-sha256` with the new hash, read from the configuration file by the command; from a scratch clone, as at P3-2d): REHEARSAL PASSED.
  - Both runs printed `COMPLETE … errors: 0`, and the JSON outputs are identical apart from `runtime`. Every hash and size was unchanged, and the clone's tree stayed clean with HEAD unchanged. Totals 102.9 s and 102.7 s.
  - Step g.3, by script on run 1's JSON: in cells 5 to 8, every estimator block has exactly the D4.3a keys, `centred_reject` has `k`, `n`, `rate` and `wilson95`, and no `mean_bias`, `reject`, `coverage` or `tost` key appears; `config_sha256` equals the new hash; `complete` is True, `errors` empty and `aborted` null. All True.
  - Refusals: with no `--expect-config-sha256`, and with a wrong one (64 zeros), the script printed `REHEARSAL REFUSED` and exited 2, before any run started.
- The full suite ran inside the P3-3b checkpoint; its result is in the P3-3b report (`/tmp/p3_3b.txt`).

**P3-3c:**
- Copies (step b.1; bash, one `cp -p` per file), each byte-identical to its source (SHA-256 equal: True): `reports/P3_3_rehearsal2.log` (rehearsal 2's log), `reports/P3_3_rehearsal2_run1.json` and `.md` (its run 1's outputs) and `reports/P3_reports/p3_3b.txt`. `/tmp/p3_3b.txt` equals the copy the supervisor reviewed: True.
- Run 2 against run 1 (step b.2, by script, independently of the rehearsal script): the JSON outputs are equal apart from `runtime`: True; the Markdown files are equal up to their `## Runtime` heading: True.
- Plausibility table of rehearsal 2's synthetic outputs (`reports/P3_3_rehearsal2_run1.json`; checks stated before the run; information, except P11; values in the P3-3c report):
  - P1 cell 0 rejection in [3.0%, 8.0%] (each method) and calibrated in [4.3%, 5.7%]: True
  - P2 cell 0 coverage count + rejection count == n (each method): True
  - P3 cells 0-4 |mean bias| <= 3 sd/sqrt(n) and se/sd in [0.85, 1.15]: True
  - P4 cells 0-4 sd(b_hat) and mean se agree within 10% (max/min - 1): True
  - P5 rejection rises over cells 0, 2, 3, 4; MDE80 defined; probit vs normal approximations within 15%: True
  - P6 cell 1 TOST at the primary SESOI declares at most 7% (each method): True
  - P7 cell 0 TOST rates ordered low <= primary <= high (each method): True
  - P8 T3: cross-tabs sum to n; calibrated CW at cell 9 in [4.0%, 6.0%]; cell 9 DK-normal H1 within 2 pp of cell 0; CW at cells 10, 11 >= cell 9 (each CW method); registry lines == walk_forward calls == 3000: True
  - P9′ T6 cells 5-8, each estimator: keys exactly D4.3a; centred rejection in [3.0%, 8.0%]; se/sd in [0.85, 1.15]; Huber share downweighted in (0, 0.5): True
  - P10 complete True, errors empty, aborted null: True
  - P11 regression: outside runtime, config_sha256, head and cells 5-8, rehearsal 2 equals rehearsal 1 exactly: True
  - `SUMMARY: P1 True; P2 True; P3 True; P4 True; P5 True; P6 True; P7 True; P8 True; P9′ True; P10 True; P11 True`
  - For information, cell 7's centred rejection counts (the cell D4.3b reads): ols_dk 57/1000; huber_dk 49/1000; winsorised_ols_dk 57/1000.
- Step d (read-only): `z2` is assigned once, at `tools/p3_sealed_run.py:398`, as `stats.norm.ppf(1 - alpha / 2)`. Its alpha comes from line 397, the configuration's `methods.alpha`, which `build_config` writes at line 174 from the spec's `inference.alpha` (0.05, `spec/analysis_spec_dev_v1.yaml:32`). The other `norm.ppf` lines (176, 178 and 192) are description text inside `build_config`. T6's `centred_block` receives `z2` (lines 595 to 598).
- The full suite ran inside the P3-3c checkpoint; its result is in the P3-3c report (`/tmp/p3_3c.txt`).

**P3-3d:**
- The report copy (step b; bash, `cp -p`): `reports/P3_reports/p3_3c.txt` is byte-identical to `/tmp/p3_3c.txt` (SHA-256 equal: True).
- Read-only facts for DQ6 and the launcher: in the P3-3d report (`/tmp/p3_3d.txt`), step c.
- The full suite ran inside the P3-3d checkpoint; its result is in the P3-3d report (`/tmp/p3_3d.txt`).

**P3-3e:**
- The report copy (step b; bash, `cp -p`): `reports/P3_reports/p3_3d.txt` is byte-identical to `/tmp/p3_3d.txt` (SHA-256 equal: True).
- Read-only facts: in the P3-3e report, step c.
- The base (scratch clone at HEAD, with the DQ5 patch, a dummy line 7 and stand-in outputs): Ran 280 tests in 319.803s; `OK (skipped=5)`.
- The dry switches (scratch clones of the base; no test changed). `Spec.load()` validated in all three, the spec kept its 70 lines, and the VERBATIM spec was unchanged:
  - D1 (DK-normal, Clark-West normal, viable): Ran 276 tests in 334.439s; `FAILED (failures=8, errors=2, skipped=6)`. Failing: `test_3_configuration` (error), `TestTinyRuns.setUpClass` (error), `test_p23_tost_pending_costs`, `test_lock_amendments_and_nothing_real_before_the_tag`, `test_refusals_and_pending_sesoi`, `test_4_real_mode_refusals_read_no_data`, `test_default_spec_loads`, `test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines`, `test_sesoi_pending`, `test_bands_consistency_and_staleness`.
  - D2 (bootstrap, Clark-West calibrated, viable): Ran 276 tests in 322.163s; `FAILED (failures=9, errors=2, skipped=6)`. Failing: `test_3_configuration` (error), `TestTinyRuns.setUpClass` (error), `test_p21_inference_size_rule_calendar`, `test_p23_tost_pending_costs`, `test_lock_amendments_and_nothing_real_before_the_tag`, `test_refusals_and_pending_sesoi`, `test_4_real_mode_refusals_read_no_data`, `test_default_spec_loads`, `test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines`, `test_sesoi_pending`, `test_bands_consistency_and_staleness`.
  - D3 (calibrated, Clark-West calibrated, not viable): Ran 276 tests in 335.382s; `FAILED (failures=9, errors=2, skipped=6)`. Failing: `test_3_configuration` (error), `TestTinyRuns.setUpClass` (error), `test_p21_inference_size_rule_calendar`, `test_p23_tost_pending_costs`, `test_lock_amendments_and_nothing_real_before_the_tag`, `test_refusals_and_pending_sesoi`, `test_4_real_mode_refusals_read_no_data`, `test_default_spec_loads`, `test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines`, `test_sesoi_pending`, `test_bands_consistency_and_staleness`.
- `docs/P3_DQ6_drafts.md`: SHA-256 `9ad9b0941952dbaee6b45e53940d5f1ed8b206abdacc2198d60733e04d3697c3`. Its checks by script (the supervisor's texts verbatim; the records' old and new lines; the three diffs pass `git apply --check`): True.
- The full suite ran inside the P3-3e checkpoint; its result is in the P3-3e report (`/tmp/p3_3e.txt`).

**P3-3f:**
- The report copy (step b; bash, `cp -p`): `reports/P3_reports/p3_3e.txt` is byte-identical to `/tmp/p3_3e.txt` (SHA-256 equal: True).
- Step c's facts (the rehearsal script's interpreter, power, hash and refusal lines; `io.py`'s data folder and dev panel name): in the P3-3f report.
- `tests/test_p3_launch.py`: 8 tests, OK, alone in REPO on the first run, and in the scratch clone in both of its runs.
- The clone rehearsal (`/tmp/p3_3f_clone`; `--data-dir /tmp/p3_3f_nodata`, which never existed). The first run stopped at the dry run, which refused only for the power source (Deviations). The second run, after Isaiah plugged in:
  - the dry run: exit 0; every check line True (check 9 not run under `--dry-run`); last line `LAUNCH DRY RUN: all checks passed`.
  - (a): exit 2; `LAUNCH REFUSED: --commit is required exactly once (usage: bash tools/p3_4_launch.sh --commit <40 lowercase hex> --expect-config-sha256 <64 lowercase hex> --data-dir <path> [--dry-run])`
  - (b): exit 2; `LAUNCH REFUSED: --expect-config-sha256 must be 64 lowercase hex`
  - (c): exit 2; `LAUNCH REFUSED: OFILT_RUN_SEALED is set in the environment (to any value); unset it`
  - (d): exit 2; `LAUNCH REFUSED: OFILT_RUN_SEALED is set in the environment (to any value); unset it`
  - (e): exit 2; `LAUNCH REFUSED: HEAD 065ad799ca7c7f022c437aa5c25fe0a1bda210d4 differs from --commit 0000000000000000000000000000000000000000`
  - (f): exit 2; `LAUNCH REFUSED: git status --porcelain --untracked-files=all is not empty`
  - (g): exit 2; `LAUNCH REFUSED: --expect-config-sha256 differs from the rehearsed configuration SHA-256`
  - (h): exit 2; `LAUNCH REFUSED: BLIND_FIT_LOG differs from the P3-0 baseline or does not have exactly 6 lines (7)`
  - (i): exit 2; `LAUNCH REFUSED: RUN_REGISTRY.jsonl is not 0 bytes`
  - (j): exit 2; `LAUNCH REFUSED: reports/P3_4_sealed_run.json exists`
  - (k): exit 2; `LAUNCH REFUSED: ACCESS_LOG exists`
- The clone checks (second run): 'LAUNCHING' appears in no case's output (12 launcher runs): True; the clone is at its step-1 commit 065ad799ca7c7f022c437aa5c25fe0a1bda210d4, clean; BLIND_FIT_LOG dad93285d2911abc6c7145c160d729df1126b24b439302bd8577cf407d397301 equals the baseline; RUN_REGISTRY.jsonl 0 bytes: True; no p3_sealed_run_* directory under /tmp or the system temporary directory ([]): True; /tmp/p3_3f_nodata still does not exist: True.
- The full suite ran inside the P3-3f checkpoint; its result is in the P3-3f report (`/tmp/p3_3f.txt`).

**P3-4:**
- The report copy (step b; bash, `cp -p`): `reports/P3_reports/p3_3f.txt` is byte-identical to `/tmp/p3_3f.txt` (SHA-256 equal: True).
- The final dry run at the sanction commit: in the P3-4 report, step e.
- The full suite ran inside the P3-4 checkpoint; its result is in the P3-4 report (`/tmp/p3_4.txt`).

**P3-4b:**
- The post-run state (step a, by script; all True):
  - HEAD at the sanction commit; the tree changed only by the run (` M BLIND_FIT_LOG` and the two new outputs); the outputs' SHA-256 values as listed (`reports/P3_4_sealed_run.json` `65e68c8cf9a76afda05869e8772b345e49f30fa24bcad6790de28d6bcab58942`, `.md` `8acbece13ff366ba39a097cf927e9c168471eff190f7dc4eb8b3307fc00c29a9`).
  - The tool, the configuration, `calib.py`, the spec, the launcher and the patch unchanged; RUN_REGISTRY.jsonl 0 bytes; tags `pass1-final` only; no `ACCESS_LOG`.
  - BLIND_FIT_LOG has exactly 7 lines, and the SHA-256 of its first six lines equals the P3-0 baseline. Line 7 is one JSON object with keys ['utc', 'provenance', 'panel_sha256', 'spec_sha256', 'n_rows_input', 'caller']: `provenance` `dev_real`; `panel_sha256` `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68` (the configuration's `dev_panel_sha256`); `spec_sha256` `0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee408561f68f96fd94d3b0f9` (the configuration's `spec_sha256`); `n_rows_input` 5124; its `caller` names `tools/p3_sealed_run.py`.
  - The launcher's log: `the tool's exit code: 0`; one `COMPLETE: ... errors: 0` line; `BLIND_FIT_LOG has 7 lines: True`; both outputs `exists: True` with the listed SHA-256; `LAUNCH FINISHED`; `launcher exit: 0`; first and last stamps `Wed Oct  7 18:51:20 UTC 2026` and `Wed Oct  7 20:45:12 UTC 2026`.
  - `reports/P3_4_sealed_run.json`, six top-level keys only (matched as lines; the file was not parsed as a whole): `mode` "real"; `head` the sanction commit; `config_sha256` the configuration's; `complete` true; `errors` empty; `aborted` null.
- The copies (step b; one `cp -p` each): `reports/P3_4_launch.log` (SHA-256 `da76746b137a2dbc966b78ee99a7b2404e8f365e32608140b8c14de1e58eee67`) and `reports/P3_reports/p3_4.txt`, each byte-identical to its source.
- The DQ5 patch (step c): `git apply --check` and `git apply` exit 0; it changed exactly `tests/test_docs_d3.py` (16 lines) and `tests/test_docs_d3b.py` (2 lines). `python -m unittest tests.test_docs_d3 tests.test_docs_d3b`: 8 tests, OK.
- The full suite ran inside the P3-4b checkpoint; its result is in the P3-4b report (`/tmp/p3_4b.txt`).

**P3-5:**
- The report copy (step b; bash, `cp -p`): `reports/P3_reports/p3_4b.txt` is byte-identical to `/tmp/p3_4b.txt` (SHA-256 equal: True).
- The rules (step c; `/tmp/p3_5_rules.py`; exact integer tests on the point estimates):
  - D3.4, H1: cell 0 `dk_normal` 291/5000: `35·5000 = 175000 <= 1000·291 = 291000 <= 65·5000 = 325000: True`
  - M = `dk_normal`.
  - D3.4, Clark–West: cell 9 `normal` 66/2000: `35·2000 = 70000 <= 1000·66 = 66000 <= 65·2000 = 130000: False`. CW = `calibrated`.
  - D2.6 under `dk_normal`: (i) cell 0 TOST at the primary SESOI 5000/5000: `5·5000 = 25000 >= 4·5000 = 20000: True`; (ii) cell 1 TOST at the primary SESOI 296/5000: `1000·296 = 296000 <= 65·5000 = 325000: True`. Viable: True.
  - D4.3b, `huber_dk`: cell 7 centred 57/1000: `35·1000 = 35000 <= 1000·57 = 57000 <= 65·1000 = 65000: True`; flagged: False.
  - D4.3b, `ols_dk`: cell 7 centred 55/1000: `35·1000 = 35000 <= 1000·55 = 55000 <= 65·1000 = 65000: True`; flagged: False.
  - D4.3b, `winsorised_ols_dk`: cell 7 centred 52/1000: `35·1000 = 35000 <= 1000·52 = 52000 <= 65·1000 = 65000: True`; flagged: False.
  - The binding numbers under `dk_normal`: rejection rates cell 0 (b 0.0) 291/5000 = 0.0582; cell 2 (b 0.1) 212/1000 = 0.212; cell 3 (b 0.25) 809/1000 = 0.809; cell 4 (b 0.4) 995/1000 = 0.995. MDE80: probit interpolated 0.24707872570018363; normal approximations 0.2425411037781687 (sd) and 0.23995965196729913 (mean se).
  - The switch's branch: AM-07 ("viable"), AM-09, AM-10; AM-08 unused.
  - The selection files are the second run's: `reports/P3_5_selection.json` SHA-256 `110a045e5ff6c2f0657fecd93c2c9d400c679599ffbde09354ea9f8f5bd207d3`, `reports/P3_5_selection.md` SHA-256 `33365cde94848b318986ca729deda60c7a3f7ff9ff877f940726430b4badee0d`.
- The two runs compared (continuation step b; `/tmp/p3_5_compare_runs2.py`): True. Exactly seven JSON strings differ, all under keys named `test`, and run 1 with `*` -> `·` in those strings equals run 2. The Markdown differs at exactly lines 9, 11, 13, 14, 16, 17 and 18, each only by `*` and `·`.
- The plausibility checks (step d; P3-3c's script with the input path changed and P11 removed). Information only: they were written for the synthetic stand-in and decide nothing:
  - P1 cell 0 rejection in [3.0%, 8.0%] (each method) and calibrated in [4.3%, 5.7%]: True
  - P2 cell 0 coverage count + rejection count == n (each method): True
  - P3 cells 0-4 |mean bias| <= 3 sd/sqrt(n) and se/sd in [0.85, 1.15]: True
  - P4 cells 0-4 sd(b_hat) and mean se agree within 10% (max/min - 1): True
  - P5 rejection rises over cells 0, 2, 3, 4; MDE80 defined; probit vs normal approximations within 15%: True
  - P6 cell 1 TOST at the primary SESOI declares at most 7% (each method): True
  - P7 cell 0 TOST rates ordered low <= primary <= high (each method): True
  - P8 T3: cross-tabs sum to n; calibrated CW at cell 9 in [4.0%, 6.0%]; cell 9 DK-normal H1 within 2 pp of cell 0; CW at cells 10, 11 >= cell 9 (each CW method); registry lines == walk_forward calls == 3000: True
  - P9′ T6 cells 5-8, each estimator: keys exactly D4.3a; centred rejection in [3.0%, 8.0%]; se/sd in [0.85, 1.15]; Huber share downweighted in (0, 0.5): True
  - P10 complete True, errors empty, aborted null: True
  - `SUMMARY: P1 True; P2 True; P3 True; P4 True; P5 True; P6 True; P7 True; P8 True; P9′ True; P10 True`
- The full suite ran inside the P3-5 checkpoint; its result is in the P3-5 report (`/tmp/p3_5.txt`).

**P3-6a:**
- The report copy (step b; bash, `cp -p`): `reports/P3_reports/p3_5.txt` is byte-identical to `/tmp/p3_5.txt` (SHA-256 equal: True).
- Step d, in a scratch clone of HEAD (`/tmp/p3_6a_clone`, remote removed), every command under `env -u OFILT_RUN_SEALED` in the venv:
  - d.2, the switch (`/tmp/p3_6a_switch.py`: AM-07 ("viable"), AM-09, AM-10; `<date>` 2026-10-07; texts and templates from `docs/P3_DQ6_drafts.md` sections 2 and 3, values from `reports/P3_5_selection.json`). The checks (`/tmp/p3_6a_switch_check.py`), all True:
    - ofilt.drift.spec imported from the clone (/private/tmp/p3_6a_clone/ofilt/drift/spec.py): True
    - Spec.load() validates (status 'FROZEN'; spec sha256 feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26): True
    - the spec still has 70 lines (70): True
    - spec/analysis_spec_dev_v1.VERBATIM.yaml unchanged (9007339534c0f31aae65487d5b879bcc5070c2e7dc78da4587c6ecfd9d3d91ec): True
    - parsed equivalence.sesoi 0.8652 equals the configuration's primary SESOI 0.8652: True
    - parsed critical_value 1.411608406163672 equals t3.c_cw_cal.value 1.411608406163672 exactly: True
    - no placeholder remains in spec/analysis_spec_dev_v1.yaml (clone 0; REPO before the switch 0): True
    - no placeholder remains in spec/SPEC_AMENDMENTS.md (clone 0; REPO before the switch 0): True
    - no placeholder remains in ofilt/drift/spec.py (clone 0; REPO before the switch 0): True
  - d.3, the first suite (after the switch, before any test change): `Ran 284 tests in 353.473s`, `FAILED (failures=8, errors=2, skipped=6)`. The failures and errors, by name:
    - ERROR: `test_p3_sealed_run.TestConfig.test_3_configuration`
    - ERROR: `test_p3_sealed_run.TestTinyRuns`
    - FAIL: `test_docs_d2.TestP22toP25.test_p23_tost_pending_costs`
    - FAIL: `test_docs_d3b.TestP36.test_lock_amendments_and_nothing_real_before_the_tag`
    - FAIL: `test_inference_b2.TestTOST.test_refusals_and_pending_sesoi`
    - FAIL: `test_p3_sealed_run.TestRealRefusals.test_4_real_mode_refusals_read_no_data`
    - FAIL: `test_spec.TestSpecLoad.test_default_spec_loads`
    - FAIL: `test_spec.TestSpecLoad.test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines`
    - FAIL: `test_spec.TestToFillRefusal.test_sesoi_pending`
    - FAIL: `test_validation_c7.TestC7Report.test_bands_consistency_and_staleness`
  - d.4, the test changes: `docs/P3_DQ6_drafts.md` section 6's rows for this branch, in `tests/test_docs_d2.py`, `tests/test_docs_d3b.py`, `tests/test_inference_b2.py`, `tests/test_spec.py` and `tests/test_p3_sealed_run.py`; each changed assertion asserts the amended state. The tiny-run tests 5, 6, 9 and 15 retired, and test 17 asserts that a synthetic run is refused. Each change is in the report as a diff with its row.
  - d.5, the C7 rerun: `tools/c7_mc.py --budget 90` in 4 foreground chunks (`PARTIAL {"size": 195, "power_040": 0, "power_025": 0}`; `PARTIAL {"size": 300, "power_040": 92, "power_025": 0}`; `PARTIAL {"size": 300, "power_040": 200, "power_025": 91}`; `COMPLETE`). The comparison (`tools/p2_3b_c7_compare.py`): `C7_mc.json PASS; C7_h1_same_dgp.json PASS`. The only non-float difference in each report is `key.spec_sha256`, `0320d6aa…` -> `feb6005d…` (the switched spec's SHA-256, `feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26`: reports/C7_mc.json True, reports/C7_h1_same_dgp.json True). `runtime_s` differs, as information only (D16 as amended).
  - d.6, the full suite again: `Ran 285 tests in 300.355s`, `OK (skipped=6)`. 288 at HEAD - 4 (tiny-run tests 5, 6, 9 and 15 retired) + 1 (test 17 added) = 285. The six skips:
    - `tests.test_docs_d6.TestProjectSetup.test_project_claims`: "Claude Project not mounted"
    - `tests.test_sim_b5.TestRealDev.test_draw_passes_guard_and_contract`: "real-data sealed fit is opt-in (OFILT_RUN_SEALED=1)"
    - `tests.test_sim_b5.TestRealDev.test_logged_and_silent`: "real-data sealed fit is opt-in (OFILT_RUN_SEALED=1)"
    - `tests.test_validation_c7.TestSlowReproduce.test_first_reps_bit_identical`: "slow tier (OFILT_SLOW=1)"
    - `tests.test_validation_c7.TestSlowReproduce.test_last_reps_bit_identical`: "slow tier (OFILT_SLOW=1)"
    - `tests.test_io.TestGuardFallback.test_main_repo_has_no_unblinding_tags_while_draft`: "spec frozen; tags expected"
  - d.7, the slow tier (`tests.test_validation_c7`, `OFILT_SLOW=1`): 6 tests, OK.
  - d.8, the configuration: SHA-256 unchanged: True. `--check-config` (once): `config docs/P3_RUN_CONFIG.json SHA-256 ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e; valid: False`, exit 2; `validate_config` returns `["key 'spec_sha256' differs from the registry"]`, the spec hash difference DQ6 expects.
  - d.9, the patch: `docs/P3_6_switch.patch`, SHA-256 `cd9d317db33ee04c8c627d1386565e3c5ad19f9ddeb511286c576a946515281a`, 288 lines. Its files (added/removed lines): `ofilt/drift/spec.py` 5/1; `spec/SPEC_AMENDMENTS.md` 27/0; `spec/analysis_spec_dev_v1.yaml` 3/3; `tests/test_docs_d2.py` 5/5; `tests/test_docs_d3b.py` 3/3; `tests/test_inference_b2.py` 4/2; `tests/test_p3_sealed_run.py` 19/54; `tests/test_spec.py` 9/5. Exactly the switch's files: True (the check's first form printed False; Deviations). In a second clone of HEAD: `git apply --check` exit 0; `git apply` exit 0; the eight files equal the first clone's by SHA-256, and across all 166 tracked files only `reports/C7_h1_same_dgp.json` and `reports/C7_mc.json` differ (`/tmp/p3_6a_clone2_check.py`: True).
  - d.10, cleanup: both clones and `/tmp/p3_6a_c7_old/` deleted; REPO's HEAD, the ten files of step a.2, BLIND_FIT_LOG, RUN_REGISTRY.jsonl and the two C7 reports unchanged; `git status` shows only this item's two new files (`/tmp/p3_6a_cleanup_check.py`: True).
  - The gate (step 2's checks; the test changes; step 5 PASS; steps 6 and 7 OK; the patch applies and reproduces the clone): passed.
- The full suite in REPO ran inside the P3-6a checkpoint; its result is in the P3-6a report (`/tmp/p3_6a.txt`).

**P3-6b:**
- The report copy (step b; bash, `cp -p /tmp/p3_6a.txt reports/P3_reports/p3_6a.txt`), checked by `/tmp/p3_6b_b.py`:
  - copy   reports/P3_reports/p3_6a.txt sha256 f7f7ceec3aa248e5c3c6d5c7903a08eecc23a943d4f362b46a41287a3f4a9d9b
  - source /tmp/p3_6a.txt sha256 f7f7ceec3aa248e5c3c6d5c7903a08eecc23a943d4f362b46a41287a3f4a9d9b
  - copy equals source: True
  - first two lines ['2026-10-07T21:50:34Z', '5b33bd0fb9b9b993105af0116d734918e606e120'] equal ['2026-10-07T21:50:34Z', '5b33bd0fb9b9b993105af0116d734918e606e120']: True
  - last two non-empty lines ['2026-10-07T22:32:28Z', '6338409a30f57758523de8ec47a004774c45c0cd'] equal ['2026-10-07T22:32:28Z', '6338409a30f57758523de8ec47a004774c45c0cd']: True
  - the line 'docs/P3_6_switch.patch sha256 cd9d317db33ee04c8c627d1386565e3c5ad19f9ddeb511286c576a946515281a; 288 lines' occurs exactly once (1): True
  - B CHECK: True
- d.1, the old C7 reports, copied to `/tmp/p3_6b_c7_old/` (`cp -p`, one per file), checked by `/tmp/p3_6b_d1.py`:
  - /tmp/p3_6b_c7_old/C7_mc.json sha256 2c9277cf7c9f8f68a5fe6996d75d954341c3ed41c878b0783f7242e8cb09036f; equals step a.2's value: True
  - /tmp/p3_6b_c7_old/C7_h1_same_dgp.json sha256 9c44e88fc963f744d6be554ba96366fb2f950cf6982fccbde66db95ed53e5fd6; equals step a.2's value: True
  - D1 CHECK: True
- d.2, the patch in REPO: `git apply --check docs/P3_6_switch.patch` exit 0; `git apply docs/P3_6_switch.patch` exit 0.
- d.3, the checks (`/tmp/p3_6b_d3.py`):
  - the patch's files (8) equal the message's eight (8), as sets: True
  - status lines (9) equal exactly ' M' for the eight files and '?? reports/P3_reports/p3_6a.txt', as a set: True
  - lines matching the regular expression in reports/P3_reports/p3_6a.txt: 8 (must be 8): True
  - one line per file: their files equal the patch's eight, as a set: True
  - ofilt/drift/spec.py sha256 1aa32e1798c76fce05448340d6d47d8c84e264525df27aae692112803a251fa9 equals the first clone's value: True
  - spec/SPEC_AMENDMENTS.md sha256 c603206bd68ba225904fae8c30d25651c3c5c56afb8e8242f54cc52a85a52617 equals the first clone's value: True
  - spec/analysis_spec_dev_v1.yaml sha256 feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26 equals the first clone's value: True
  - tests/test_docs_d2.py sha256 8e15fb87f418352e41dd47a0f43acf12b95b2dc3440a63fda5408ac2de378c18 equals the first clone's value: True
  - tests/test_docs_d3b.py sha256 9c46ae79ca5ccfc81fed4bb05e1c24b034c516452439c78971a6903661908e0d equals the first clone's value: True
  - tests/test_inference_b2.py sha256 30e72bb5d79c3ab66a7d9b4bd87eb96e90facabf670fec4d59b5eedce695effd equals the first clone's value: True
  - tests/test_p3_sealed_run.py sha256 2ea015b359a1d0af9af5dfd284dd18601a5436b3e57189df556c5632944cffa6 equals the first clone's value: True
  - tests/test_spec.py sha256 3e48600364168f8574fa693d3efee68528af52ea6af0b6d6a2c7cd86cde5dd1f equals the first clone's value: True
  - spec/analysis_spec_dev_v1.yaml sha256 feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26 equals the message's feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26: True
  - ofilt.drift.spec imported from REPO (/Users/isaiahchoi/Desktop/FX_Project/ofilt_pass1/ofilt/drift/spec.py): True
  - Spec.load() validates (status 'FROZEN'; spec sha256 feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26): True
  - status is FROZEN: True
  - the spec has 70 lines (70): True
  - git diff --quiet HEAD -- spec/analysis_spec_dev_v1.VERBATIM.yaml exits 0 (0): True
  - git apply --reverse --check exits 0 (the tree holds exactly the patch's post-image): True
  - D3 CHECK: True
- d.4, the C7 rerun in REPO (`tools/c7_mc.py --budget 90`, foreground chunks, one command per chunk; no partial file before the first chunk: True):
  - chunk 1: 2026-10-07T23:24:15Z to 2026-10-07T23:25:47Z, `PARTIAL {"size": 190, "power_040": 0, "power_025": 0}`, exit 0
  - chunk 2: 2026-10-07T23:25:53Z to 2026-10-07T23:27:25Z, `PARTIAL {"size": 300, "power_040": 80, "power_025": 0}`, exit 0
  - chunk 3: 2026-10-07T23:27:31Z to 2026-10-07T23:29:03Z, `PARTIAL {"size": 300, "power_040": 200, "power_025": 69}`, exit 0
  - chunk 4: 2026-10-07T23:29:09Z to 2026-10-07T23:30:17Z, `COMPLETE`, exit 0
  - the partial file afterwards: absent; status (as a set) equals step d.3's 9 lines (read from this report) plus ' M' for the two C7 reports: True
- d.5, the comparison (`tools/p2_3b_c7_compare.py`, old copies against the new reports): `OVERALL (criterion as written): C7_mc.json PASS; C7_h1_same_dgp.json PASS`.
  - `C7_mc.json`: float leaves compared 2846, differing at all 0; rejection flags and summary counts compared 2148, differences 0; the only non-float difference: `key.spec_sha256: old '0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee408561f68f96fd94d3b0f9' -> new 'feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26'  [must equal SHA-256 of spec/analysis_spec_dev_v1.yaml: True]`. `runtime_s` (information only): 316.75257444381714 -> 336.3097012042999.
  - `C7_h1_same_dgp.json`: float leaves compared 20, differing at all 0; rejection flags and summary counts compared 13, differences 0; the only non-float difference: `key.spec_sha256: old '0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee408561f68f96fd94d3b0f9' -> new 'feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26'  [must equal SHA-256 of spec/analysis_spec_dev_v1.yaml: True]`. `runtime_s` (information only): 316.75257444381714 -> 336.3097012042999.
  - `reports/C7_mc.json`: `key.spec_sha256` feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26, equal to the switched spec's SHA-256: True
  - `reports/C7_h1_same_dgp.json`: `key.spec_sha256` feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26, equal to the switched spec's SHA-256: True
  - The gate (`/tmp/p3_6b_d5.py`): True. The new reports' SHA-256: `reports/C7_mc.json` `72d4a6bc4ffa5084169cfa18534a7480c252afab1224b6dce5eb113d6a5d4b9a`; `reports/C7_h1_same_dgp.json` `5644e6168cd7c100a2fd01c6eaef3ecda9bb0542b30df34ff2a807e0a5ed7821`.
- d.6, the slow tier (`tests.test_validation_c7`, `OFILT_SLOW=1`): `Ran 6 tests in 33.014s`, `OK`.
- d.7, the configuration after the switch (`/tmp/p3_6b_cfg.py`): docs/P3_RUN_CONFIG.json sha256 ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e is still ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e: True. `--check-config` (once): `config docs/P3_RUN_CONFIG.json SHA-256 ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e; valid: False`, exit 2; `validate_config` of the committed configuration returns `["key 'spec_sha256' differs from the registry"]`.
- The full suite ran inside the P3-6b checkpoint; its result is in the P3-6b report (`/tmp/p3_6b.txt`).

**P3-7a:**
- The report copies (step b; bash, one `cp -p` per file: `/tmp/p3_boot.txt` and `/tmp/p3_6b.txt` to `reports/P3_reports/`), checked by `/tmp/p3_7a_b.py` (all True):
  - copy   reports/P3_reports/p3_boot.txt sha256 acd98c562e0c0504b3dca9e1fddad97fb2f143c0b1d1fcf3bc9cc027da9e13fe
  - source /tmp/p3_boot.txt sha256 acd98c562e0c0504b3dca9e1fddad97fb2f143c0b1d1fcf3bc9cc027da9e13fe
  - p3_boot.txt: copy equals source: True
  - p3_boot.txt: first two lines ['2026-10-07T23:15:00Z', '6338409a30f57758523de8ec47a004774c45c0cd'] equal ['2026-10-07T23:15:00Z', '6338409a30f57758523de8ec47a004774c45c0cd']: True
  - p3_boot.txt: last two non-empty lines ['2026-10-07T23:16:10Z', '6338409a30f57758523de8ec47a004774c45c0cd'] equal ['2026-10-07T23:16:10Z', '6338409a30f57758523de8ec47a004774c45c0cd']: True
  - copy   reports/P3_reports/p3_6b.txt sha256 9ce9d338ea83b8b3eb1498f6d6ae0b6fb5fc9f29661c20d649501df05440ed8e
  - source /tmp/p3_6b.txt sha256 9ce9d338ea83b8b3eb1498f6d6ae0b6fb5fc9f29661c20d649501df05440ed8e
  - p3_6b.txt: copy equals source: True
  - p3_6b.txt: first two lines ['2026-10-07T23:22:31Z', '6338409a30f57758523de8ec47a004774c45c0cd'] equal ['2026-10-07T23:22:31Z', '6338409a30f57758523de8ec47a004774c45c0cd']: True
  - p3_6b.txt: last two non-empty lines ['2026-10-07T23:44:59Z', 'cfc1deff58658eed87d691cb9cb38c60ac55cb97'] equal ['2026-10-07T23:44:59Z', 'cfc1deff58658eed87d691cb9cb38c60ac55cb97']: True
  - p3_6b.txt: the line 'b97a268b05e078d9e05e659a9ff1d5e4ce6131e139d283a064513c063b7b9e20  /tmp/p3_6b_msg.txt' occurs exactly once (1): True
- The read-only facts of step c are in the P3-7a report (`/tmp/p3_7a.txt`).
- The full suite ran inside the P3-7a checkpoint; its result is in the P3-7a report (`/tmp/p3_7a.txt`).

**P3-7b:**
- The report copies (step b; bash, one `cp -p` per file: `/tmp/p3_7a.txt` and `/tmp/p3_7a2.txt` to `reports/P3_reports/`), checked by `/tmp/p3_7b_b.py`:
  - copy   reports/P3_reports/p3_7a.txt sha256 3321556df44c1caa52f48b89633acec69d88d5bf669bf75c9aecf804fb815727
  - source /tmp/p3_7a.txt sha256 3321556df44c1caa52f48b89633acec69d88d5bf669bf75c9aecf804fb815727
  - p3_7a.txt: copy equals source: True
  - p3_7a.txt: first two lines ['2026-10-08T00:10:34Z', 'cfc1deff58658eed87d691cb9cb38c60ac55cb97'] equal ['2026-10-08T00:10:34Z', 'cfc1deff58658eed87d691cb9cb38c60ac55cb97']: True
  - p3_7a.txt: last two non-empty lines ['2026-10-08T00:20:55Z', '80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd'] equal ['2026-10-08T00:20:55Z', '80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd']: True
  - p3_7a.txt: the line '0fd1225e6b4ad730449df3f0e3150d61b7bb257cc25a05e55fa32106f6352481  /tmp/p3_7a_msg.txt' occurs exactly once (1): True
  - copy   reports/P3_reports/p3_7a2.txt sha256 378db0461a105b2bb5b17ff10b94706b7f0b8021fedd5382349b1fef9335e3d1
  - source /tmp/p3_7a2.txt sha256 378db0461a105b2bb5b17ff10b94706b7f0b8021fedd5382349b1fef9335e3d1
  - p3_7a2.txt: copy equals source: True
  - p3_7a2.txt: first two lines ['2026-10-08T00:28:54Z', '80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd'] equal ['2026-10-08T00:28:54Z', '80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd']: True
  - p3_7a2.txt: last two non-empty lines ['2026-10-08T00:34:40Z', '80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd'] equal ['2026-10-08T00:34:40Z', '80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd']: True
  - p3_7a2.txt: the line '6b7ea274f98369ad8a18cdb4ea2dae7b8e3715b6e13609deb99be95fa9879d67  /tmp/p3_7a2_msg.txt' occurs exactly once (1): True
- The kit check (`/tmp/p3_7b_kit.py`, read-only):
  - kit table rows read: 5 (must be 5): True
  - the folder holds exactly the five kit files and SHA256SUMS_P3-7b.txt, as a set: True
  - every entry is a regular file: True
  - SHA256SUMS_P3-7b.txt sha256 6373c10e2e2b8834911fa8c6b2599d61911fcbf01c071d2ab0b2f5c52a42f09f equals 6373c10e2e2b8834911fa8c6b2599d61911fcbf01c071d2ab0b2f5c52a42f09f: True
  - SHA256SUMS_P3-7b.txt lists exactly the five kit files with their 'after' values: True
  - PLAN.md sha256 cba8471919635f9c823078e5956398ddf84505a8e5e6eb3e70324b611acd7772 equals its 'after' value (target docs/replacements/PLAN.md): True
  - README.md sha256 12d56d1270f41d385977bcb9d3622a5a3410eceab4483711298e469be8130cd0 equals its 'after' value (target docs/replacements/README.md): True
  - PROJECT_SETUP.md sha256 267c3aa8f22724cc5378d99bb0104122f7eb1f2fc198f4d701bbc7a407ef013f equals its 'after' value (target docs/replacements/PROJECT_SETUP.md): True
  - DATA_PROVENANCE.md sha256 48f39045bea417fbe0d4370f545986854e0c7f9ae51734cdb50c0b9b548795dd equals its 'after' value (target docs/DATA_PROVENANCE.md): True
  - DECISIONS_P71_onward.md sha256 c3eadc756e8d9754bb6ef289e7b7ba5d30a53ecec9182d53bd69fc5eb9fa1b83 equals its 'after' value (target docs/DECISIONS_P71_onward.md): True
- The scratch clone (`git clone --no-hardlinks`, remote removed): clone HEAD 80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd; REPO HEAD 80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd; equal: True; clone status empty: True (0 lines).
- The apply in the clone (`/tmp/p3_7b_apply.py /tmp/p3_7b_clone`):
  - docs/replacements/PLAN.md: before 641fb05f4ec6958a4e55672af00453b73da8f1388fd539c22d9d67c0f272e6c5; equals the table: True
  - docs/replacements/README.md: before 4896b40905f4426c618085ea589a2dab9596f1f0187010aa879c653a08f6b48f; equals the table: True
  - docs/replacements/PROJECT_SETUP.md: before 8b342d1ec69d6069476d4e8ec3478456298ca4d9c34a6b1f1f100143edc9d091; equals the table: True
  - docs/DATA_PROVENANCE.md: before 0efa0121cbd4f2d074b18eab3f776c3e7f58381c3db9623aaf662ba6d5f36aed; equals the table: True
  - docs/DECISIONS_P71_onward.md: does not exist: True
  - docs/replacements/PLAN.md sha256 cba8471919635f9c823078e5956398ddf84505a8e5e6eb3e70324b611acd7772 equals its 'after' value: True
  - docs/replacements/README.md sha256 12d56d1270f41d385977bcb9d3622a5a3410eceab4483711298e469be8130cd0 equals its 'after' value: True
  - docs/replacements/PROJECT_SETUP.md sha256 267c3aa8f22724cc5378d99bb0104122f7eb1f2fc198f4d701bbc7a407ef013f equals its 'after' value: True
  - docs/DATA_PROVENANCE.md sha256 48f39045bea417fbe0d4370f545986854e0c7f9ae51734cdb50c0b9b548795dd equals its 'after' value: True
  - docs/DECISIONS_P71_onward.md sha256 c3eadc756e8d9754bb6ef289e7b7ba5d30a53ecec9182d53bd69fc5eb9fa1b83 equals its 'after' value: True
  - tests/test_docs_p2.py: numstat +5 -4; expected +5 -4: True
  - tests/test_docs_d4.py: numstat +4 -3; expected +4 -3: True
  - tests/test_docs_d6.py: numstat +5 -4; expected +5 -4: True
  - APPLY CHECK: True
- The suite in the clone (`/tmp/p3_7b_suite.py`, no commit): `Ran 285 tests in 307.241s`, `OK (skipped=6)`.
- The apply in REPO (the same script): APPLY CHECK: True. REPO against the clone (`/tmp/p3_7b_e2.py`):
  - changed paths read: 8 (must be 8): True
  - docs/replacements/PLAN.md: REPO cba8471919635f9c823078e5956398ddf84505a8e5e6eb3e70324b611acd7772; clone cba8471919635f9c823078e5956398ddf84505a8e5e6eb3e70324b611acd7772; equal: True
  - docs/replacements/README.md: REPO 12d56d1270f41d385977bcb9d3622a5a3410eceab4483711298e469be8130cd0; clone 12d56d1270f41d385977bcb9d3622a5a3410eceab4483711298e469be8130cd0; equal: True
  - docs/replacements/PROJECT_SETUP.md: REPO 267c3aa8f22724cc5378d99bb0104122f7eb1f2fc198f4d701bbc7a407ef013f; clone 267c3aa8f22724cc5378d99bb0104122f7eb1f2fc198f4d701bbc7a407ef013f; equal: True
  - docs/DATA_PROVENANCE.md: REPO 48f39045bea417fbe0d4370f545986854e0c7f9ae51734cdb50c0b9b548795dd; clone 48f39045bea417fbe0d4370f545986854e0c7f9ae51734cdb50c0b9b548795dd; equal: True
  - docs/DECISIONS_P71_onward.md: REPO c3eadc756e8d9754bb6ef289e7b7ba5d30a53ecec9182d53bd69fc5eb9fa1b83; clone c3eadc756e8d9754bb6ef289e7b7ba5d30a53ecec9182d53bd69fc5eb9fa1b83; equal: True
  - tests/test_docs_p2.py: REPO c75f4be3f7d2131bbd33725ec6eec57e80c96a1fa602e8e739930c717b6865a3; clone c75f4be3f7d2131bbd33725ec6eec57e80c96a1fa602e8e739930c717b6865a3; equal: True
  - tests/test_docs_d4.py: REPO b3673edf363f22e72fe4421da66db562ba0d743eb040984082a1de734a729d87; clone b3673edf363f22e72fe4421da66db562ba0d743eb040984082a1de734a729d87; equal: True
  - tests/test_docs_d6.py: REPO d6267dfc43e070eaca0219f93b419f80ca0d8f9d5b3ef69a65315719091307c3; clone d6267dfc43e070eaca0219f93b419f80ca0d8f9d5b3ef69a65315719091307c3; equal: True
  - status (10 lines) is exactly seven ' M' lines (7) and three '??' lines (3), as a set: True
  - E2 CHECK: True
- The full suite ran inside the P3-7b checkpoint; its result is in the P3-7b report (`/tmp/p3_7b.txt`).

**P3-8a:**
- The report copy (step d; bash, `cp -p /tmp/p3_7b.txt reports/P3_reports/p3_7b.txt`), checked by `/tmp/p3_8a_d.py`:
  - copy   reports/P3_reports/p3_7b.txt sha256 43b39cd1b99d633cbbb01023d49160a0532e9bc39f9d01010c32694d5fb1166e
  - source /tmp/p3_7b.txt sha256 43b39cd1b99d633cbbb01023d49160a0532e9bc39f9d01010c32694d5fb1166e
  - p3_7b.txt: copy equals source: True
  - p3_7b.txt: first two lines ['2026-10-08T01:01:40Z', '80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd'] equal ['2026-10-08T01:01:40Z', '80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd']: True
  - p3_7b.txt: last two non-empty lines ['2026-10-08T01:29:27Z', '42a88bc987321871687097742226dceeb3631059'] equal ['2026-10-08T01:29:27Z', '42a88bc987321871687097742226dceeb3631059']: True
  - p3_7b.txt: the line '7c8c4363b179660a656f1fb7c0a2d98a5c0c66ead9bd36eaef9a460772b0b1bb  /tmp/p3_7b_msg.txt' occurs exactly once (1): True
- The suite in a scratch clone, verbose (`/tmp/p3_8a_suite.py`; no tag, no commit; the log parsed again by `/tmp/p3_8a_suite_parse.py`, Deviations): `Ran 285 tests in 299.898s`, `OK (skipped=6)`; result kinds {'ok': 279, 'skipped': 6}. The six skipped tests:
  - `test_docs_d6.TestProjectSetup.test_project_claims`: skipped 'Claude Project not mounted'
  - `test_io.TestGuardFallback.test_main_repo_has_no_unblinding_tags_while_draft`: skipped 'spec frozen; tags expected'
  - `test_sim_b5.TestRealDev.test_draw_passes_guard_and_contract`: skipped 'real-data sealed fit is opt-in (OFILT_RUN_SEALED=1)'
  - `test_sim_b5.TestRealDev.test_logged_and_silent`: skipped 'real-data sealed fit is opt-in (OFILT_RUN_SEALED=1)'
  - `test_validation_c7.TestSlowReproduce.test_first_reps_bit_identical`: skipped 'slow tier (OFILT_SLOW=1)'
  - `test_validation_c7.TestSlowReproduce.test_last_reps_bit_identical`: skipped 'slow tier (OFILT_SLOW=1)'
- The read-only facts of step b are in the P3-8a report (`/tmp/p3_8a.txt`).
- The full suite ran inside the P3-8a checkpoint; its result is in the P3-8a report (`/tmp/p3_8a.txt`).

**P3-8b:**
- The report copy (step b; bash, `cp -p /tmp/p3_8a.txt reports/P3_reports/p3_8a.txt`), checked by `/tmp/p3_8b_b.py`:
  - copy   reports/P3_reports/p3_8a.txt sha256 0c25520592f759d9b006b3422e9997e9488036b10bb44d82e101362b3e248661
  - source /tmp/p3_8a.txt sha256 0c25520592f759d9b006b3422e9997e9488036b10bb44d82e101362b3e248661
  - p3_8a.txt: copy equals source: True
  - p3_8a.txt: first two lines ['2026-10-08T01:47:29Z', '42a88bc987321871687097742226dceeb3631059'] equal ['2026-10-08T01:47:29Z', '42a88bc987321871687097742226dceeb3631059']: True
  - p3_8a.txt: last two non-empty lines ['2026-10-08T02:07:15Z', '25dad69ca184de575905b7aee80620fcb29172ca'] equal ['2026-10-08T02:07:15Z', '25dad69ca184de575905b7aee80620fcb29172ca']: True
  - p3_8a.txt: the line '3cfc9a66f0bd764b52b49616eda745209078c4f6e171205f46a3cce044cb9bfc  /tmp/p3_8a_msg.txt' occurs exactly once (1): True
- The apply (`/tmp/p3_8b_apply.py`): in the clone, APPLY CHECK True (the nine tests at their step a.2 values; `tests/tag_state.py` written with the message's SHA-256; every anchor found once; the numstat exactly the table's; every file parses and compiles; the status exact):
  - tests/test_docs_d3.py: numstat +11 -2; expected +11 -2: True
  - tests/test_docs_d3b.py: numstat +4 -2; expected +4 -2: True
  - tests/test_blind.py: numstat +5 -0; expected +5 -0: True
  - tests/test_fctests_c5.py: numstat +3 -1; expected +3 -1: True
  - tests/test_forecast_c1.py: numstat +3 -1; expected +3 -1: True
  - tests/test_inference_b1.py: numstat +4 -2; expected +4 -2: True
  - tests/test_inference_b2.py: numstat +2 -1; expected +2 -1: True
  - tests/test_inference_b3.py: numstat +2 -1; expected +2 -1: True
  - tests/test_sim_b5.py: numstat +3 -1; expected +3 -1: True
- The suite in the clone, no tag (`/tmp/p3_8b_suite.py notag`): `Ran 285 tests in 305.429s`, `OK (skipped=6)`; result kinds {'ok': 279, 'skipped': 6}; the skips and the set of test ids equal to P3-8a's verbose log; the clone's BLIND_FIT_LOG, RUN_REGISTRY.jsonl and tags unchanged (SUITE CHECK True).
- The scratch tag (`/tmp/p3_8b_tagcheck.py`): TAG CHECK True:
  - git -C clone cat-file -t spec-dev-v1 prints 'tag' (must be 'tag'): True
  - the tag's commit 25dad69ca184de575905b7aee80620fcb29172ca is the clone's HEAD 25dad69ca184de575905b7aee80620fcb29172ca and equals 25dad69ca184de575905b7aee80620fcb29172ca: True
  - the clone's git tag -l ['pass1-final', 'spec-dev-v1'] is pass1-final and spec-dev-v1: True
  - REPO's git tag -l ['pass1-final'] is still only pass1-final: True
- The guard check in the clone (`/tmp/p3_8b_guard.py`): GUARD CHECK True:
  - ofilt.drift.blind imported from the clone (/private/tmp/p3_8b_clone/ofilt/drift/blind.py): True
  - ofilt.drift.io imported from the clone (/private/tmp/p3_8b_clone/ofilt/drift/io.py): True
  - blind._GUARD_REPO /private/tmp/p3_8b_clone resolves to the clone: True
  - io._GUARD_REPO /private/tmp/p3_8b_clone resolves to the clone: True
  - blind._tag_ok('spec-dev-v1') is True: True
  - blind._tag_ok('prereg-v1') is False: True
  - blind.require_unblinded(provenance='dev_real') returns 'dev_real' (must be 'dev_real'): True
  - it raises BlindingError; the message contains ['prereg-v1'] and not spec-dev-v1: True
  - /tmp/p3_8b_access.jsonl does not exist first: True
  - the data folder /tmp/p3_8b_nodata_does_not_exist does not exist: True
  - io.load_confirm() raises AccessDenied: True
  - /tmp/p3_8b_access.jsonl holds exactly one line (1): True
  - its tag is prereg-v1 and its result DENIED: True
  - no ACCESS_LOG in the clone afterwards: True
  - the data folder /tmp/p3_8b_nodata_does_not_exist still does not exist: True
- The suite in the clone, with the scratch tag (`/tmp/p3_8b_suite.py tag`): `Ran 285 tests in 305.364s`, `OK (skipped=6)`; result kinds {'ok': 279, 'skipped': 6}; every test has the same result as in c.3 (/tmp/p3_8b_suite_notag.log); tests that differ: []: True (SUITE CHECK True).
- The apply in REPO (the same script): APPLY CHECK True. REPO against the clone (`/tmp/p3_8b_d2.py`): D2 CHECK True; the ten paths equal by SHA-256.
- The full suite ran inside the P3-8b checkpoint; its result is in the P3-8b report (`/tmp/p3_8b.txt`).

**P3-8c:**
- The tag, read-only (`/tmp/p3_8c_tag.py`): TAG CHECK True; the tag object `cee3b49e81d16f1f32e546cac9524b209ac1e493`, tagger date 2026-10-07:
  - git cat-file -t spec-dev-v1 prints 'tag' (must be 'tag'): True
  - the tag's commit f5271c03481b7514a1ec4b7e739fb85fbce8a774 is f5271c03481b7514a1ec4b7e739fb85fbce8a774, which is HEAD f5271c03481b7514a1ec4b7e739fb85fbce8a774: True
  - git merge-base --is-ancestor f5271c03481b HEAD exits 0 (must be 0): True
  - the tag's message, trailing whitespace removed, is exactly 'spec-dev-v1: Pass 3 calibration complete (P3-8)' (got 'spec-dev-v1: Pass 3 calibration complete (P3-8)'): True
  - the tagger date 2026-10-07 is 2026-10-07: True
  - sha256 of git show spec-dev-v1:spec/analysis_spec_dev_v1.yaml feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26 equals feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26: True
- The guard check in REPO, with the tag present (`/tmp/p3_8c_guard.py`; its first run executed an empty file, Deviations): GUARD CHECK True:
  - ofilt.drift.blind imported from REPO (/Users/isaiahchoi/Desktop/FX_Project/ofilt_pass1/ofilt/drift/blind.py): True
  - ofilt.drift.io imported from REPO (/Users/isaiahchoi/Desktop/FX_Project/ofilt_pass1/ofilt/drift/io.py): True
  - blind._GUARD_REPO /Users/isaiahchoi/Desktop/FX_Project/ofilt_pass1 resolves to REPO: True
  - io._GUARD_REPO /Users/isaiahchoi/Desktop/FX_Project/ofilt_pass1 resolves to REPO: True
  - blind._tag_ok('spec-dev-v1') is True: True
  - blind._tag_ok('prereg-v1') is False: True
  - blind.require_unblinded(provenance='dev_real') returns 'dev_real' (must be 'dev_real'): True
  - it raises BlindingError; the message contains ['prereg-v1'] and not spec-dev-v1: True
  - /tmp/p3_8c_access.jsonl does not exist first: True
  - the data folder /tmp/p3_8c_nodata_does_not_exist does not exist: True
  - io.load_confirm() raises AccessDenied: True
  - /tmp/p3_8c_access.jsonl holds exactly one line (1): True
  - its tag is prereg-v1 and its result DENIED: True
  - no ACCESS_LOG in REPO afterwards: True
  - the data folder /tmp/p3_8c_nodata_does_not_exist still does not exist: True
- The suite in a scratch clone with the tag present (`/tmp/p3_8c_suite.py`, verbose): `Ran 285 tests in 349.601s`, `OK (skipped=6)`; result kinds {'ok': 279, 'skipped': 6}; every one of the 285 tests has the same result as in /tmp/p3_8b_suite_tag.log (285 tests, parsed by the same rule); tests that differ: []: True (SUITE CHECK True). The clone, with its copies of REPO's tags, was deleted at c.3.
- The report copy (step d; bash, `cp -p /tmp/p3_8b.txt reports/P3_reports/p3_8b.txt`), checked by `/tmp/p3_8c_d.py` (D CHECK True):
  - copy   reports/P3_reports/p3_8b.txt sha256 89be0dd0f3901f746dbdb39c0c79062be3be4e3674ffad79001d1d75c75a4c85
  - source /tmp/p3_8b.txt sha256 89be0dd0f3901f746dbdb39c0c79062be3be4e3674ffad79001d1d75c75a4c85
  - p3_8b.txt: copy equals source: True
  - p3_8b.txt: first two lines ['2026-10-08T02:55:52Z', '25dad69ca184de575905b7aee80620fcb29172ca'] equal ['2026-10-08T02:55:52Z', '25dad69ca184de575905b7aee80620fcb29172ca']: True
  - p3_8b.txt: last two non-empty lines ['2026-10-08T03:19:03Z', 'f5271c03481b7514a1ec4b7e739fb85fbce8a774'] equal ['2026-10-08T03:19:03Z', 'f5271c03481b7514a1ec4b7e739fb85fbce8a774']: True
  - p3_8b.txt: the line '87bb98c99294752d3204e00d208144a3965f60a0e8d1da33f93b6cf8126b442b  /tmp/p3_8b_msg.txt' occurs exactly once (1): True
- The full suite ran inside the P3-8c checkpoint; its result is in the P3-8c report (`/tmp/p3_8c.txt`).

## Test changes

Protocol: PASS2_ADDENDUM §5, rules 2–4, read for Pass 3. No test that existed before Pass 3 was changed or deleted before the post-run checkpoint (P3-4b). Since then, such tests changed only through DQ5's patch (P3-4b) and the switch's patch (P3-6b), in the two tables below; changes to Pass 3's own tests are in their rows.

| Test | Old | New | Entry | Phase |
|---|---|---|---|---|
| new `tests/test_p3_0b_preflight.py` | — | 3 tests, synthetic only: the Part A sample rule keeps exactly `inference.build_design`'s rows on three injected `synthetic_panel` frames; the grid detector on hand-built series (including a grid change mid-sample); the tool refuses a panel whose hash does not match the registry, before reading it | P3-0b (supervisor message, 2026-10-06) | P3-0b |
| new `tests/test_p3_1_sesoi.py` (row recorded at P3-2a; see Deviations) | — | 5 tests, synthetic only: the FWL residual equals the residual of `usdjpy_ret` on `build_design`'s other columns; tick tables, band edges and price factors; the conformity check; the cost arithmetic (primary, low, high); refusals (unregistered panel, cost file with a missing key) | P3-1 (supervisor message, 2026-10-06) | P3-1 |
| new `tests/test_p3_calib.py` | — | 8 tests, synthetic only (test 5 reads B7b's committed aggregates): `tost_declares` vs `inference.tost`; `fit_t` vs `fit_dk`; `resample_dates`; order statistics and their intervals; `wilson` and `mde80` reproduce B7b; `winsorise_fx`; `window_positions`; static imports and no `open(` in `calib.py` | P3-2a (supervisor message, 2026-10-06) | P3-2a |
| new `tests/test_p3_sealed_run.py` | — | 9 tests, synthetic only (no data file read; no test sets `OFILT_RUN_SEALED`):<br>1. static checks (one `DevCalibrator(`; no banned import; one writing function; private attributes only in the row-count assertion);<br>2. the invariance of (b̂ − b)/se and t* across b, and `calib.bootstrap_t_given_fit` equal to `calib.bootstrap_t`;<br>3. the configuration (rebuilt equals committed; refusals);<br>4. real-mode refusals with no data read;<br>5. outputs whitelisted, no list over 20;<br>6. the run-registry directory;<br>7. seeds disjoint;<br>8. the 6 → 7 → 7 log checks;<br>9. determinism<br>P3-2c change: test 4's two in-process refusals have their stdout captured (`contextlib.redirect_stdout`), and the captured text must start with `REFUSED` (was: printed to the suite's stdout, uncaptured) | P3-2b (supervisor message, 2026-10-06); P3-2c (supervisor message, 2026-10-06) | P3-2b; P3-2c |
| `tests/test_p3_sealed_run.py`: 4 tests added (existing tests unchanged) | 9 tests | 13 tests:<br>10. R1: the generalised log check (a synthetic line passes; a wrong count, provenance or caller fails) and the logged-panel check (provenance `dev_real` and the logged hash);<br>11. R2: the generic handlers in `main` and `_run` reference no exception message (AST);<br>12. R2: `_abort_text` gives `<class> at line <n>` without the message;<br>13. `tools/p3_3_rehearse.sh`, static: no real-mode flag and no `OFILT_RUN_SEALED=1`; first line `set -euo pipefail`; the sealed-variable refusal before any Python line | P3-2d (supervisor message, 2026-10-06) | P3-2d |
| new `tests/test_p3_2d_structural.py` | — | 1 test, synthetic only: the structural frame builder keeps exactly the stated columns, keeps the missing pattern of `abn_oc` and `beta`, replaces their present values, drops every `y_*`, `ao_*`, `open`, `close` and `prev_close` column, and labels the frame synthetic | P3-2d (supervisor message, 2026-10-06) | P3-2d |
| `tests/test_p3_sealed_run.py`: test 13 (`test_13_rehearsal_script_static`) changed; everything it checked before is still required | no real-mode flag and no `OFILT_RUN_SEALED=1`; first line `set -euo pipefail`; the sealed-variable refusal before any Python line | also: the `--expect-config-sha256` refusal (missing or malformed) and the configuration-hash refusal (`[ "$CFG_SHA" = "$EXPECT" ]`), both before any Python line; `CFG_SHA` computed from `docs/P3_RUN_CONFIG.json`; the baselines compare with the flag (`cfg == exp`); no reference to `P3_2b_smoke` | P3-3b (supervisor message, 2026-10-07), step e | P3-3b |
| `tests/test_p3_sealed_run.py`: 3 tests added | 13 tests | 16 tests:<br>14. (i) `centred_block`: identical output after adding a constant to every b̂ (+3.0 on a dyadic example of 8; +0.37 on 200 random draws, with the count exact and sd to 12 places); its rate equals a hand computation (4 of 8);<br>15. (ii) in the tiny runs, every T6 estimator block (cells 5 to 8) has exactly `centred_reject`, `sd`, `mean_se` and `se_over_sd`, plus `mean_share_downweighted` for Huber-DK, and no `estimates`, `reject` or `coverage`;<br>16. (iii) the leak test: on a synthetic `DevCalibrator` (temporary log), adding 0.3·`usdjpy_ret` to its residuals (in the test only) shifts every OLS-DK b̂ by 0.3 (to 1e-10) and every Huber-DK b̂ by 0.3 (to 1e-8), leaves their se and Huber's share unchanged to the same tolerances, and leaves the centred counts exactly unchanged, in a full-window and an early-window cell (6 draws each, identical seeds and positions) | P3-3b (supervisor message, 2026-10-07), step d | P3-3b |
| new `tests/test_p3_launch.py` | — | 8 tests on `tools/p3_4_launch.sh` (1 to 6 on its text; 7 and 8 run it in a subprocess that refuses before any git or Python command):<br>1. the first line is `set -euo pipefail`, and the usage names the four arguments;<br>2. `OFILT_RUN_SEALED=1` is on exactly one line, which begins `OFILT_RUN_SEALED=1 OFILT_DATA_DIR=` and contains `caffeinate -i` and `tools/p3_sealed_run.py --real --expect-config-sha256`; no line exports the variable; no other line contains `--real`;<br>3. the sealed-variable refusal precedes the first Python line; the `--dry-run` exit and every refusal precede the command line;<br>4. the `--check-config` line contains `env -u OFILT_RUN_SEALED`;<br>5. the constants equal their sources: the tool, `calib.py` and configuration hashes as `reports/P3_3_rehearsal2.log` prints them; the spec hash as the configuration's `spec_sha256`; the baseline as BLIND_FIT_LOG's first six lines and the P3-0 baseline; and `DEV_FILE` as `io.py` names the dev panel;<br>6. no tag name; the commands that touch `reports/P3_4_sealed_run.*` only test existence or compute a SHA-256;<br>7. no arguments: exit 2, `LAUNCH REFUSED`;<br>8. `OFILT_RUN_SEALED=0` with well-formed arguments: exit 2, a refusal naming `OFILT_RUN_SEALED` | P3-3f (supervisor message, 2026-10-07) | P3-3f |

**Applied unchanged at P3-4b, the post-run checkpoint (DQ5).** `docs/P3_DQ5_line7.patch` was applied unchanged in the first commit after the real run (P3-4b), together with BLIND_FIT_LOG's line 7 and `reports/P3_4_sealed_run.json` and `.md`. It was rehearsed in scratch clones at P3-3a: with a dummy line 7 and stand-in outputs the suite passes (277, OK); without them it fails only in these two tests.

| Test (line) | Old | New | Entry | Phase |
|---|---|---|---|---|
| `test_docs_d3.TestP29Blinding.test_sealed_fit_opt_in_and_record` (65-73) | BLIND_FIT_LOG has 6 lines, all `dev_real`, all on the Pass 1 dev panel `7366…`, with callers B5 ×3, `report_B7.py` ×2 and `report_B7b.py` | 7 lines, all `dev_real`. The six-line prefix's SHA-256 is pinned (`dad93285…`, raw bytes). Lines 1–6 are on `7366…`, with the same callers. Line 7 is pinned by its fields: key set; panel hash `36f7dd69…` (AM-04); spec hash `0320d6aa…` (the configuration's); 5,124 input rows; and a caller naming `tools/p3_sealed_run.py`. No whole-file hash. Adds `import hashlib` | DQ5 (Isaiah, 2026-10-07) | post-run checkpoint |
| `test_docs_d3b.TestP36.test_lock_amendments_and_nothing_real_before_the_tag` (41) | `len(log) == 6` | `len(log) == 7` (Pass 1's six and P3-4's line 7); `RUN_REGISTRY.jsonl` still empty | DQ5 (Isaiah, 2026-10-07) | post-run checkpoint |

**Applied unchanged at P3-6b, the switch commit (DQ6).**

Retired at the switch (DQ6): tests 5, 6, 9 and 15 of `tests/test_p3_sealed_run.py`, which ran two tiny synthetic runs of the sealed-run tool and checked their outputs (whitelisted aggregates, the run-registry directory, determinism, and T6's centred-only blocks). From the switch on, the configuration differs from a rebuild by its `spec_sha256`, so the tool refuses every run before it starts, and the tiny runs cannot run. Their properties were verified on the tool before the sealed run (P3-2b to P3-3c, and both rehearsals, which ran the same code), and the sealed run's own outputs were checked at P3-4b (six structural keys) and P3-5 (P9′, T6's D4.3a keys; P10). Test 17 asserts the refusal.

| Test | Old | New | Entry | Phase |
|---|---|---|---|---|
| `test_docs_d2.TestP22toP25.test_p23_tost_pending_costs` | the SESOI is `PENDING_COSTS`; the viability contains "Pass 4"; `Spec.sesoi()` raises `SpecPendingError` | the SESOI equals the configuration's `sesoi.primary` (0.8652); the viability begins "viable (D2.6, P3-5)"; `Spec.sesoi()` returns the SESOI (AM-07) | DQ6 (P3-3f); the patch approved with P3-6a | the switch commit (P3-6b) |
| `test_docs_d3b.TestP36.test_lock_amendments_and_nothing_real_before_the_tag` | status DRAFT; the YAML says "FROZEN only when Isaiah tags spec-dev-v1"; amendment headings AM-01 to AM-05 | status FROZEN; the YAML holds AM-10's comment "frozen at the Pass 3 switch (AM-10)"; headings AM-01 to AM-05, then AM-07, AM-09 and AM-10. The 7-line BLIND_FIT_LOG and empty-registry checks are unchanged | DQ6 (P3-3f); the patch approved with P3-6a | the switch commit (P3-6b) |
| `test_inference_b2.TestTOST.test_refusals_and_pending_sesoi` | `tost_result` without a SESOI raises `SpecPendingError` | `tost_result` without a SESOI uses the spec's: its `sesoi` equals the configuration's `sesoi.primary` and its `alpha` is 0.05 (AM-07); the file gains `import json`. The `PENDING_COSTS` refusal stays tested on a mutated spec (`test_spec.TestToFillRefusal.test_sesoi_pending`) | DQ6 (P3-3f); the patch approved with P3-6a | the switch commit (P3-6b) |
| `test_spec.TestSpecLoad.test_default_spec_loads` | status DRAFT | status FROZEN (AM-10) | DQ6 (P3-3f); the patch approved with P3-6a | the switch commit (P3-6b) |
| `test_spec.TestSpecLoad.test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines` | amended lines 4, 7, 14, 33, 42 to 46 and 62; record ids AM-01 to AM-05 | amended lines also 2, 49 and 66; ids also AM-07, AM-09 and AM-10. The record checks are unchanged and pass | DQ6 (P3-3f); the patch approved with P3-6a | the switch commit (P3-6b) |
| `test_spec.TestToFillRefusal.test_sesoi_pending` | `Spec.sesoi()` raises `SpecPendingError` | `Spec.sesoi()` equals the configuration's `sesoi.primary`, and a spec mutated back to `PENDING_COSTS` still raises `SpecPendingError` (AM-07) | DQ6 (P3-3f); the patch approved with P3-6a | the switch commit (P3-6b) |
| `test_p3_sealed_run.TestConfig.test_3_configuration` (test 3) | the configuration equals a rebuild; `validate_config` returns no problem | the configuration is the sealed run's (its SHA-256 equals the run's `config_sha256`), its `spec_sha256` equals BLIND_FIT_LOG line 7's, and `validate_config` returns exactly the `spec_sha256` difference (DQ6). The refusal checks that follow are unchanged | DQ6 (P3-3f); the patch approved with P3-6a | the switch commit (P3-6b) |
| `test_p3_sealed_run.TestRealRefusals.test_4_real_mode_refusals_read_no_data` (test 4) | a `--real` subprocess is refused for the sealed variable | a `--real` subprocess is refused for the configuration, before the mode check, and reads no data; the in-process refusal checks are unchanged | DQ6 (P3-3f); the patch approved with P3-6a | the switch commit (P3-6b) |
| `test_p3_sealed_run.TestTinyRuns` (tests 5, 6, 9 and 15; test 17) | two tiny synthetic runs; test 5, the outputs whitelisted; test 6, the run-registry directory; test 9, determinism; test 15, T6's blocks centred only | tests 5, 6, 9 and 15 retired (above); new test 17: a synthetic run is refused for the configuration (exit 2, the exact refusal line), writes nothing to `--out-dir` and removes its own directory | DQ6 (P3-3f); the patch approved with P3-6a | the switch commit (P3-6b) |

**Applied at P3-7b, the final records (P81).** Line numbers are those before the change.

| Test (line) | Old | New | Entry | Phase |
|---|---|---|---|---|
| `tests/test_docs_p2.py` (11, `PINNED`) | `docs/DATA_PROVENANCE.md` `0efa0121cbd4f2d074b18eab3f776c3e7f58381c3db9623aaf662ba6d5f36aed` | `48f39045bea417fbe0d4370f545986854e0c7f9ae51734cdb50c0b9b548795dd` | P81 | P3-7b |
| `tests/test_docs_p2.py` (16) | `docs/replacements/PLAN.md` `641fb05f4ec6958a4e55672af00453b73da8f1388fd539c22d9d67c0f272e6c5` | `cba8471919635f9c823078e5956398ddf84505a8e5e6eb3e70324b611acd7772` | P81 | P3-7b |
| `tests/test_docs_p2.py` (17) | `docs/replacements/PROJECT_SETUP.md` `8b342d1ec69d6069476d4e8ec3478456298ca4d9c34a6b1f1f100143edc9d091` | `267c3aa8f22724cc5378d99bb0104122f7eb1f2fc198f4d701bbc7a407ef013f` | P81 | P3-7b |
| `tests/test_docs_p2.py` (18) | `docs/replacements/README.md` `4896b40905f4426c618085ea589a2dab9596f1f0187010aa879c653a08f6b48f` | `12d56d1270f41d385977bcb9d3622a5a3410eceab4483711298e469be8130cd0` | P81 | P3-7b |
| `tests/test_docs_p2.py` (`NEW_PINNED`) | (none) | `docs/DECISIONS_P71_onward.md` `c3eadc756e8d9754bb6ef289e7b7ba5d30a53ecec9182d53bd69fc5eb9fa1b83` | P81 | P3-7b |
| `tests/test_docs_d4.py` (13, `DOCS`) | `4896b40905f4426c` / `641fb05f4ec6958a` | `12d56d1270f41d38` / `cba8471919635f9c` | P81 | P3-7b |
| `tests/test_docs_d4.py` (33) | `# Research Plan v2.4` | `# Research Plan v2.5` | P81 | P3-7b |
| `tests/test_docs_d4.py` (36) | `Supersedes:** v2.3 (2026-10-05), which superseded v2.2 (2026-10-04), v2.1 (Pass 1, item D4b,` | `Supersedes:** v2.4 (2026-10-06), which superseded v2.3 (2026-10-05), v2.2 (2026-10-04), v2.1 (Pass 1, item D4b,`, with a citing comment line added before it | P81 | P3-7b |
| `tests/test_docs_d6.py` (25) | `8b342d1ec69d6069` | `267c3aa8f22724cc` | P81 | P3-7b |
| `tests/test_docs_d6.py` (31) | `refreshed 2026-10-06` | `refreshed 2026-10-07`, with a citing comment line added | P81 | P3-7b |
| `tests/test_docs_d6.py` (58) | `` `PLAN.md` (v2.4) `` | `` `PLAN.md` (v2.5) `` | P81 | P3-7b |
| `tests/test_docs_d6.py` (59) | `# Research Plan v2.4` | `# Research Plan v2.5` | P81 | P3-7b |

**Applied at P3-8b, the tag-aware tests.** Line numbers are those before the change.

| Test (line) | Old | New | Entry | Phase |
|---|---|---|---|---|
| `tests/test_docs_d3.py` (42) | `self.assertNotIn("spec-dev-v1", tags)                                   # Pass 1: neither tag exists` | `dev_open`, whether REPO has `spec-dev-v1`; with it, `TS.check_spec_tag` (annotated, an ancestor of HEAD, the frozen spec). | P3-8b | P3-8b |
| `tests/test_docs_d3.py` (45) | `for prov, ok in ((B.SYNTHETIC, True), (B.DEV_REAL, False), (B.CONFIRM_REAL, False), ("other", False)):` | `(B.DEV_REAL, dev_open)`: dev_real granted with the tag, refused without it. | P3-8b | P3-8b |
| `tests/test_docs_d3.py` (after 59) | (none) | with the tag, confirm_real refused, the message naming `['prereg-v1']` alone. | P3-8b | P3-8b |
| `tests/test_docs_d3.py` (after 22) | (none) | the tests folder on `sys.path`; `import tag_state as TS`. | P3-8b | P3-8b |
| `tests/test_docs_d3b.py` (27) | `for t in TAGS:` | `_tag_ok("spec-dev-v1")` equals whether REPO has the tag; `_tag_ok("prereg-v1")` False. | P3-8b | P3-8b |
| `tests/test_docs_d3b.py` (28) | `self.assertFalse(B._tag_ok(t))                                      # neither exists in Pass 1` | deleted (the loop's body; replaced by E5's two lines). | P3-8b | P3-8b |
| `tests/test_docs_d3b.py` (after 17) | (none) | the tests folder on `sys.path`; `import tag_state as TS`. | P3-8b | P3-8b |
| `tests/test_blind.py` (after 33) | (none) | with the tag, both calls granted (`dev_real`); without it, the refusals as before. | P3-8b | P3-8b |
| `tests/test_blind.py` (after 16) | (none) | `import tag_state as TS`. | P3-8b | P3-8b |
| `tests/test_fctests_c5.py` (180) | `with self.assertRaises(B.BlindingError):` | `with TS.blinded(), self.assertRaises(B.BlindingError):`. | P3-8b | P3-8b |
| `tests/test_fctests_c5.py` (after 20) | (none) | the tests folder on `sys.path`; `import tag_state as TS`. | P3-8b | P3-8b |
| `tests/test_forecast_c1.py` (99) | `with self.assertRaises(B.BlindingError):` | `with TS.blinded(), self.assertRaises(B.BlindingError):`. | P3-8b | P3-8b |
| `tests/test_forecast_c1.py` (after 12) | (none) | the tests folder on `sys.path`; `import tag_state as TS`. | P3-8b | P3-8b |
| `tests/test_inference_b1.py` (100) | `with self.assertRaises(B.BlindingError):` | `with TS.blinded(), self.assertRaises(B.BlindingError):`. | P3-8b | P3-8b |
| `tests/test_inference_b1.py` (108) | `with self.assertRaises(B.BlindingError):` | `with TS.blinded(), self.assertRaises(B.BlindingError):`. | P3-8b | P3-8b |
| `tests/test_inference_b1.py` (after 12) | (none) | the tests folder on `sys.path`; `import tag_state as TS`. | P3-8b | P3-8b |
| `tests/test_inference_b2.py` (124) | `with self.assertRaises(B.BlindingError):` | `with TS.blinded(), self.assertRaises(B.BlindingError):`. | P3-8b | P3-8b |
| `tests/test_inference_b2.py` (after 15) | (none) | `import tag_state as TS`. | P3-8b | P3-8b |
| `tests/test_inference_b3.py` (155) | `with self.assertRaises(B.BlindingError):` | `with TS.blinded(), self.assertRaises(B.BlindingError):`. | P3-8b | P3-8b |
| `tests/test_inference_b3.py` (after 13) | (none) | `import tag_state as TS`. | P3-8b | P3-8b |
| `tests/test_sim_b5.py` (177) | `with self.assertRaises(B.BlindingError):` | `with TS.blinded(), self.assertRaises(B.BlindingError):`. | P3-8b | P3-8b |
| `tests/test_sim_b5.py` (after 25) | (none) | the tests folder on `sys.path`; `import tag_state as TS`. | P3-8b | P3-8b |
| `tests/tag_state.py` (new) | (none) | the helper module (spec_tagged, check_spec_tag, blinded), SHA-256 2b0cb379e2e5ec677098feb5e82a802b43ba4a0c12e6e3ad264e7f66b8348684 | P3-8b | P3-8b |

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
- (P3-3a, for the supervisor; before the sanction) The T6 early-window cells (D4.3; cells 7 and 8) are biased, and in the real run their outputs may depend on the real FX–target relation.
  - In the rehearsal's synthetic outputs, the early-window cells show a mean bias of b̂ − b of −0.094 (OLS-DK and winsorised) and −0.074 (Huber), the same at b = 0 and b = 0.25, with se/sd near 1. Hence cell 7's rejection rates at b = 0 are 33.7%, 33.7% and 20.2%. The full-window cells 5 and 6 show no such bias.
  - Reading (builder's algebra, not computed on any real data): `DevCalibrator`'s residuals are orthogonal to the design over the full estimation sample, not within a subset of its dates. With y_sim = fitted controls + b·e + residuals, OLS on draws resampled only from the first K source dates estimates b + c, where c is the coefficient on e of the full-sample residuals regressed on the design within those dates, which equals b̂(early dates) − b̂(full sample).
  - On real data, cells 7 and 8's mean bias and rejection rates would therefore reflect the real b̂(before 2017-09-27) − b̂(full dev). That is a relation between predictors and real targets, which the P29 argument for full-window draws does not cover.
  - The D4.3 flag rule would also flag every estimator as unreliable for this reason, not because of the coarse grids.
  - Cells 0 to 6 and 9 to 11 resample all source dates and are not affected.
  - Nothing was changed. The configuration and the tool stay as accepted.
  - Resolved by D4.3 amended (P3-3b).

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
- **P3-3a (supervisor message of 2026-10-07)**, by category:
  - The full rehearsal, run by Isaiah in his own Terminal (2026-10-07T00:12:19Z to 04:05:04Z), with synthetic stand-in draws.
    - The dev panel was loaded (hash-checked; `io.load_dev`, `targets.add_targets`) only to populate the fingerprint registry (target-only; DQ1.5).
    - The sealed fit in each run was the stand-in's, logged to a temporary file. Only aggregates were written, under `/tmp`.
  - The copies into `reports/`: byte-for-byte copies of the rehearsal's log, run 1's outputs (synthetic aggregates) and the read-only P3-2e report.
  - The plausibility table: computed by script from `reports/P3_3_rehearsal_run1.json` (synthetic aggregates).
  - The clone suites (`/tmp/p3_3a_cloneA`, `/tmp/p3_3a_cloneB`, deleted):
    - each clone held a dummy line 7 appended to its own copy of BLIND_FIT_LOG, and the stand-in outputs;
    - no real fit was run, and the suite read `panel_dev.csv` only through its structural and target-only tests.
  - Read-only listings: the spec, `spec.py`, tests and docs.
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - No viewer was used. RAW and OUT: untouched. The sealed-run tool was not run in any mode by the builder. `OFILT_RUN_SEALED` was unset throughout (every Python command ran in the venv under `env -u OFILT_RUN_SEALED`). REPO's BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-3b (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md. Read-only code listings (step c): the tool, the rehearsal script and the tests.
  - Code and configuration changes: T6's outputs in `tools/p3_sealed_run.py` (D4.3a), `--expect-config-sha256` in `tools/p3_3_rehearse.sh`, and `docs/P3_RUN_CONFIG.json` rebuilt by `--write-config` from the registry, the reports and the spec (no data file).
  - Synthetic tests: `tests/test_p3_sealed_run.py`, including tiny synthetic runs and a synthetic `DevCalibrator` with a temporary log (test 16).
  - The smoke rehearsal (`--smoke 20`, from a scratch clone with the same files; two runs of `--rehearsal`): the dev panel was loaded (hash-checked; `io.load_dev`, `targets.add_targets`) only to populate the fingerprint registry (target-only; DQ1.5).
    - The draws are synthetic stand-in draws, and the sealed fit in each run was the stand-in's, logged to a temporary file.
    - Only aggregates were written, under `/tmp/p3_3_smoke_*`. The step g.3 check printed keys, the configuration hash and booleans only. The outputs and the clone were deleted afterwards.
    - The two refusal runs stopped before any Python command.
  - The report copies: byte-for-byte copies of the builder's own Pass 3 reports into `reports/P3_reports/`.
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - No `--real` run, and the full rehearsal was not started. No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED` was unset throughout (every Python command ran in the venv under `env -u OFILT_RUN_SEALED`; the rehearsal script was started under `env -u OFILT_RUN_SEALED`). REPO's BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-3c (supervisor message of 2026-10-07)**, by category:
  - Rehearsal 2, run by Isaiah in his own Terminal (2026-10-07T05:41:48Z to 09:27:07Z; from its log): two `--rehearsal` runs.
    - The dev panel was loaded (hash-checked; `io.load_dev`, `targets.add_targets`) only to populate the fingerprint registry (target-only; DQ1.5).
    - The draws were synthetic stand-in draws, and the sealed fit in each run was the stand-in's, logged to a temporary file.
    - Only aggregates were written, under `/tmp/p3_3_rehearsal_1` and `/tmp/p3_3_rehearsal_2`. BLIND_FIT_LOG, RUN_REGISTRY.jsonl and the tree were unchanged, and HEAD did not move.
  - This item:
    - Records: document edits to PASS3_STATUS.md.
    - Byte-for-byte copies: rehearsal 2's log, its run 1's outputs (synthetic aggregates) and the P3-3b report.
    - Scripts read only the rehearsal's files (synthetic aggregates and its log): the step a.3 check (hashes, names and booleans), the run 2 against run 1 check, and the plausibility script, which read only the two rehearsal JSONs.
    - The read-only listing: `tools/p3_sealed_run.py`, the spec's alpha line and the configuration's `methods.alpha`.
    - The sealed-run tool ran only as `--check-config`, and the rehearsal script was not run.
    - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
    - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED` was unset throughout (every Python command ran in the venv under `env -u OFILT_RUN_SEALED`). BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-3d (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md.
  - The report copy: a byte-for-byte copy of the P3-3c report into `reports/P3_reports/`.
  - Read-only listings of code, tests and documents: `ofilt/`, `tools/`, `tests/`, `docs/` (with `docs/replacements/`), `spec/`, the key lines of the two C7 reports and the committed P3-3a report. The searches skipped data-type files, of which the repository holds none. No data file was opened.
  - The sealed-run tool ran only as `--check-config`.
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED` was unset throughout (every Python command ran in the venv under `env -u OFILT_RUN_SEALED`). BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-3e (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md. The report copy: a byte-for-byte copy of the P3-3d report into `reports/P3_reports/`.
  - Read-only listings of code and documents, and values read from the synthetic rehearsal JSON (`reports/P3_3_rehearsal2_run1.json`).
  - The drafts document `docs/P3_DQ6_drafts.md`: the supervisor's texts, and lines, records and diffs built by script from the spec, `spec.py` and the configuration.
  - The scratch clones (`/tmp/p3_3e_clone` and one per dry switch; remote removed; never pushed; deleted): a dummy BLIND_FIT_LOG line 7; stand-in synthetic outputs and values; spec and validation edits in the clones only.
  - The suites in the clones and in REPO (inside the checkpoint) read `panel_dev.csv` only through their structural and target-only tests.
  - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED` was unset throughout (every Python command ran in the venv under `env -u OFILT_RUN_SEALED`). REPO's BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-3f (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md. The report copy: a byte-for-byte copy of the P3-3e report into `reports/P3_reports/`. Read-only listings of `tools/p3_3_rehearse.sh` and `ofilt/drift/io.py`.
  - The launcher `tools/p3_4_launch.sh` (its constants filled by script from the rehearsal log, the configuration, the P3-0 report and `io.py`) and its static tests `tests/test_p3_launch.py`. Tests 7 and 8 refuse before any git or Python command; test 8 sets `OFILT_RUN_SEALED` to 0 in its child only.
  - The scratch clone (`/tmp/p3_3f_clone`; remote removed; never pushed; deleted):
    - `--check-config` ran in it, inside the launcher's dry runs;
    - the dry runs and the refusal cases (a) to (k) all used `--data-dir /tmp/p3_3f_nodata`, which was checked to be absent before every call and never created;
    - cases (c) and (d) set `OFILT_RUN_SEALED` to 0 and to the empty string;
    - no `--real` run, and `LAUNCHING` was printed by no case;
    - the clone's BLIND_FIT_LOG and RUN_REGISTRY.jsonl were restored to their committed state after cases (h) and (i), and REPO's were never touched.
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED=1` was never set; every Python command ran in the venv under `env -u OFILT_RUN_SEALED`. BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-4 (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md. The report copy: a byte-for-byte copy of the P3-3f report into `reports/P3_reports/`.
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - One launcher dry run in REPO, at the sanction commit, with `--data-dir /tmp/p3_4_nodata`, a folder that does not exist and was never created: no `--real` run.
  - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED=1` was never set; every Python command ran in the venv under `env -u OFILT_RUN_SEALED`. BLIND_FIT_LOG still has 6 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-4b (supervisor message of 2026-10-07)**, by category:
  - The real run, in Isaiah's Terminal (from the launcher's log and line 7):
    - the dev panel was loaded (hash-checked) for the one sanctioned sealed fit, BLIND_FIT_LOG's line 7;
    - the draws came from the sealed calibrator;
    - only aggregates were written, to `reports/P3_4_sealed_run.*`;
    - no coefficient was written or printed.
  - This item:
    - Records: document edits to PASS3_STATUS.md. The copies: the launcher's log and the P3-4 report, byte for byte. The patch: `docs/P3_DQ5_line7.patch`, applied unchanged.
    - The outputs were read for six structural keys only (`mode`, `head`, `config_sha256`, `complete`, `errors`, `aborted`), matched as lines, with the file not parsed as a whole; otherwise only their SHA-256 values were computed.
    - BLIND_FIT_LOG's line 7 was read and printed (its fields are hashes, a row count, a time and the caller).
    - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
    - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED=1` was never set in this item; every Python command ran in the venv under `env -u OFILT_RUN_SEALED`. BLIND_FIT_LOG has 7 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-5 (supervisor messages of 2026-10-07: the item, and its continuation after the STOP)**, by category:
  - The sealed run's aggregates were read for the first time. They come from synthetic draws of the sealed calibrator, and are rates, critical values, standard deviations and the centred T6 blocks; no coefficient of the real data exists in them.
  - Records: document edits to PASS3_STATUS.md. The report copy. The two selection files, built by script from `reports/P3_4_sealed_run.json` and `docs/P3_RUN_CONFIG.json` alone.
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED=1` was never set; every Python command ran in the venv under `env -u OFILT_RUN_SEALED`. BLIND_FIT_LOG has 7 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-6a (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md. The report copy. Read-only listings of documents, code and tests (step c and the test files' imports).
  - The scratch clones: the spec lines, `spec/SPEC_AMENDMENTS.md`, `spec.py`'s AM-09 validation and the test changes were edited in the clones only. The C7 rerun is synthetic only. Both clones and the copied C7 reports were deleted at step d.10.
  - The patch document: `docs/P3_6_switch.patch`, the first clone's diff, checked in a second clone and, in REPO, with `git apply --check` only. Nothing was applied in REPO.
  - The suites in the clones and in REPO (inside the checkpoint) read `panel_dev.csv` only through their structural and target-only tests.
  - No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED=1` was never set; every Python command ran in the venv under `env -u OFILT_RUN_SEALED`. `tools/p3_sealed_run.py` ran only with `--check-config`. BLIND_FIT_LOG has 7 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-6b (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md. The report copy (`reports/P3_reports/p3_6a.txt`, byte for byte). Read-only listings of PASS3_STATUS.md (step c), the P3-6a report, and code (`tools/p3_sealed_run.py`'s `main`; the imports of `tools/p2_3b_c7_compare.py` and `tests/test_p3_sealed_run.py`; `ofilt/drift/spec.py`'s `load` and `status`).
  - The switch in REPO: the spec, `spec.py`'s validation and the tests changed only through `git apply docs/P3_6_switch.patch`, applied unchanged.
  - The C7 rerun (`tools/c7_mc.py`, foreground chunks) and its comparison (`tools/p2_3b_c7_compare.py`): synthetic only; no data file read.
  - The slow tier, and the full suite inside the checkpoint, read `panel_dev.csv` only through their structural and target-only tests.
  - `tools/p3_sealed_run.py` ran only with `--check-config` (steps a.3 and d.7, and the records rule). No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED=1` was never set; every Python command ran in the venv under `env -u OFILT_RUN_SEALED`. BLIND_FIT_LOG has 7 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-7a (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md. The two report copies (`reports/P3_reports/p3_boot.txt` and `reports/P3_reports/p3_6b.txt`, byte for byte).
  - Read-only listings of tracked files (step c), and the hash-only search of step c.8 (the SHA-256 of `.md` files under `~/Desktop/FX_Project/files`; only the matches and the count printed).
  - The existence checks of step c.12: two paths tested for existence, and a name-only search to depth 2 under `~/Desktop/FX_Project`, with RAW and OUT pruned. Nothing was opened.
  - The full suite (inside the checkpoint) read `panel_dev.csv` only through its structural and target-only tests.
  - `tools/p3_sealed_run.py` ran only with `--check-config`. No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED=1` was never set; every Python command ran in the venv under `env -u OFILT_RUN_SEALED`. No git tag was created, moved or deleted. BLIND_FIT_LOG has 7 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-7b (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md. The two report copies (`reports/P3_reports/p3_7a.txt` and `reports/P3_reports/p3_7a2.txt`, byte for byte).
  - The final records: the kit's five documents written whole, each checked by SHA-256 before and after, in a scratch clone first and then in REPO; the pin edits in three tests.
  - No data file was opened by any script of this item; the documents and tests of step c were read as text. The suites in the clone and in REPO (inside the checkpoint) read `panel_dev.csv` only through their structural and target-only tests.
  - No tag was created, moved or deleted, in REPO or in the clone. `tools/p3_sealed_run.py` ran only with `--check-config` (Isaiah's answer in the session; Deviations); no sealed run. No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED=1` was never set; every Python command ran in the venv under `env -u OFILT_RUN_SEALED`. BLIND_FIT_LOG has 7 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-8a (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md. The report copy (`reports/P3_reports/p3_7b.txt`, byte for byte).
  - No script of this item opened a data file. The code of step b (tracked files under `tests/`, `ofilt/` and `tools/`) was read as text, and hashed.
  - The two suites (in a scratch clone, verbose, and inside the checkpoint) read the dev panel only through the tests' structural and target-only reads; only the Ran and result lines, the skips and the per-module counts of the clone's log were printed.
  - No tag was created, moved or deleted, in REPO or in the clone. `tools/p3_sealed_run.py` ran only with `--check-config`. No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED=1` was never set; every Python command ran in the venv under `env -u OFILT_RUN_SEALED`. BLIND_FIT_LOG has 7 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-8b (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md. The report copy (`reports/P3_reports/p3_8a.txt`, byte for byte). The test edits and `tests/tag_state.py`, written by one script from the message, in the clone and then in REPO.
  - No script of this item opened a data file. The three suites (two in the clone, one inside the checkpoint) read the dev panel only through the tests' structural and target-only reads; only the parsed lines of the clone's verbose logs were printed.
  - The scratch annotated `spec-dev-v1` existed only in `/tmp/p3_8b_clone` and was deleted with it; no tag was created, moved or deleted in REPO. The guard check called the guard with provenances only, and `load_confirm` with a data folder that does not exist; its one access record went to `/tmp/p3_8b_access.jsonl`.
  - `tools/p3_sealed_run.py` ran only with `--check-config`. No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED=1` was never set; every Python command ran in the venv under `env -u OFILT_RUN_SEALED`. BLIND_FIT_LOG has 7 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.
- **P3-8c (supervisor message of 2026-10-07)**, by category:
  - Records: document edits to PASS3_STATUS.md. The report copy (`reports/P3_reports/p3_8b.txt`, byte for byte).
  - No script of this item opened a data file or computed on the dev panel. With `spec-dev-v1` present, the guard check called the guard with provenances only, and `load_confirm` with a data folder that does not exist; its one access record went to `/tmp/p3_8c_access.jsonl`.
  - The two suites (in a scratch clone with the tag, and inside the checkpoint) read the dev panel only through the tests, which P3-8b made tag-aware; only the parsed lines of the clone's verbose log were printed.
  - No tag was created, moved or deleted in REPO; the scratch clone carried copies of REPO's tags and was deleted with them. `tools/p3_sealed_run.py` ran only with `--check-config`. No viewer was used. RAW and OUT: untouched. `OFILT_RUN_SEALED=1` was never set; every Python command ran in the venv under `env -u OFILT_RUN_SEALED`. BLIND_FIT_LOG has 7 dev_real lines, and RUN_REGISTRY.jsonl is 0 bytes.

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
- P3-3a d, the first copy attempt: my copy script looped over "source destination" pairs with `set -- $pair`. The shell running it is zsh, which does not word-split an unquoted `$pair`, so every `cp` failed and nothing was copied (the tree was checked). Its "equal: True" lines compared two empty hashes and are spurious, and d.2 then failed on the missing copy. Fix: one explicit `cp -p` and hash comparison per file. The one rerun (rerun-once rule) copied all four files byte for byte, and d.2 found run 2 equal to run 1 apart from runtime. Both runs are in the P3-3a report.
- P3-3a e, two readings the item left open:
  - P4's "agree within 10%" is computed as max/min − 1 ≤ 0.10 over cells 0 to 4. The own-quantile intervals are reported as a count (10 of 10 contain the pooled value).
  - P5's MDE80 agreement compares the probit value with both of B7b's normal approximations (sd(b̂) and mean se).
- P3-3a e, the P9 context: beyond the table, the report prints cells 5 to 8's mean bias, sd and se/sd per estimator from the same JSON (synthetic aggregates), to support the P3-3a flag.
- P3-3a f, the patch: made by a script (`/tmp/p3_3a_make_patch.py`, in the report) that reads the six-line prefix hash, the line-7 hashes and the row count from the registry files. The dummy line 7's caller text imitates `_log_blind_fit`'s format, with an invented line number. Both clones were taken from HEAD, so they lack this item's uncommitted files. Clone A's suite ran on HEAD plus the dummy line and the stand-ins.
- P3-3a g, a flag beyond the listed edits: the early-window finding (P9) went into Flags, because it needs a decision before the sanction.
- P3-3b b.4, the records-rule count: the report's line "lines in the file beginning '>   - D4.3b The flag rule.': 2" counted lines containing the string (`grep -c -F`), and the records-rule bullet of the step b block quotes the prefix mid-line. Lines beginning with the prefix, which `_rule_lines`' `one()` matches: 1, the step b line. The report keeps the original line, followed by the correction.
- P3-3b b.2, the flag: "Resolved by D4.3 amended (P3-3b)." was appended as the last sub-bullet of the P3-3a early-window flag, which has sub-bullets, not to its first line.
- P3-3b d, `t6_block`: its only callers were the three T6 estimator lines, so it was replaced in place by `centred_block` (whose signature drops `b`), not left as unused code. `est_summary` and `rate` are unchanged.
- P3-3b d, the winsorised estimator and test 16's scope (for the supervisor; builder's algebra, not computed).
  - OLS-DK and Huber-DK (c and scale fixed) are regression-equivariant. If the residuals gain any vector in the span of the draw's design, b̂ moves by that vector's coefficient, the same in every draw. The window's OLS coefficient deviation of D4.3's finding (cells 7 and 8) is such a vector, so centring removes it from these two estimators' outputs exactly. Test 16 shows this for a shift along `usdjpy_ret`.
  - Winsorised OLS-DK regresses on the winsorised FX columns, while that deviation runs along the unwinsorised `usdjpy_ret`. Its b̂ moves by the deviation times γ, the coefficient of `usdjpy_ret` on the winsorised design within the draw. γ is near 1 but varies across draws with the rows the draw winsorises.
  - Centring removes the mean of that shift, not its spread. Winsorised OLS-DK's centred outputs in cells 7 and 8 therefore depend on the deviation at second order, through its product with the spread of γ across draws. D4.3a's "these outputs do not depend on the deviations above" holds exactly for OLS-DK and Huber-DK and approximately for winsorised OLS-DK.
  - Test 16 covers OLS-DK and Huber-DK, as step d(iii) specifies. Nothing beyond step d was changed.
- P3-3b h, the Test changes preamble: "No existing test was changed or deleted" was written at P3-0b and refers to the tests that existed before Pass 3; it still holds for them. Changes to Pass 3's own tests are in their rows (P3-2c: test 4; P3-3b: test 13). The line was left as it stands.
- P3-3c a and c, the expected values: the state check and the plausibility table read their expected hashes, times and lines by script from the P3-3c message as saved from this session's transcript (`/tmp/p3_3c_msg.txt`), not typed. Rehearsal 1's expected SHA-256 was passed to the plausibility script as an argument, so that the script itself reads only the two rehearsal JSONs.
- P3-3c c, the table's layout: P9′ prints its per-cell and per-estimator values on lines after its row, and P11 prints its input's hash check on a line before its row. P1 to P8 and P10 are P3-3a's code unchanged apart from the input path (the diff is in the report).
- P3-3c d, beyond the listed lines: the report also prints `docs/P3_RUN_CONFIG.json`'s `methods.alpha` and the two quantiles it gives (`z2` 1.959963984540054, `z1` 1.644853626951472), by a one-line script, and the spec's alpha line.
- P3-3c g.2 (after the checkpoint), the deletion: the first attempt ran the three removals inside a bash -c script together with the checks. Claude Code's built-in safety check refused that command before anything in it ran. g.1 was then run on its own (True), and the removal was issued as one plain command with the three literal paths, which completed. Nothing else was deleted.
- P3-3c g.2, the HEAD check after the deletion compared git rev-parse HEAD with the checkpoint hash copied into the command from step f.2's output, not read by script. The pre-deletion state line, read from git, printed the same value.
- P3-3d b, an informational line beyond the step: after the required copy check (by script, True), the report also compared the source's SHA-256 with the P3-3c report's hash as printed at the end of P3-3c. That hash was typed into the command, and the line's label wrongly said it was read from that output. A correction line follows it in the report.
- P3-3d c, a shell loop in zsh: before the report's run, the seven listing parts were run once to scratch files (`/tmp/p3_3d_c1.out` to `/tmp/p3_3d_c7.out`) by a `for` loop in zsh, against the reminder to run loops in bash. The loop had no word-splitting step, and every part exited 0. The listings in the report come from a second run, in bash, after two changes to the script: c.1 prints the signatures verbatim from the source, and c.3 adds `_log_access`.
- P3-3d c.4, a typed hash: the extra search of the two C7 reports typed the spec's SHA-256 into the command, copied from the message, instead of reading it by script as the c.4 search itself did.
- P3-3d c, beyond the listed items (for the supervisor's use):
  - c.3 also prints `io._log_access`: `load_confirm` appends to `ACCESS_LOG` at the repository root on every attempt.
  - c.4 adds the C7 reports' key lines and the test that compares them (test_validation_c7.py:44, through tools/c7_mc.py:74).
  - c.6 adds `combo_refusal`, `registry.git_state` and the tests that scan whole directories of code.
  - c.7 notes test_docs_d4's text pins of PLAN.
  - Method: c.2's readers were found by regular expressions over `ofilt/` and `tools/` (printed with the listing), with the enclosing names from the AST. c.4 reports compiled `__pycache__` files that contain a term by name only.
- P3-3e e, two shell loops in zsh, against the reminder to run loops in bash: the `for` that appended three scripts to the report (`cat` of literal paths), and the `for` that listed the four clones before their deletion. Both iterated over literal lists with no word-splitting step, and their output is complete in the report.
- P3-3e d.3, AM-10: the drafts read AM-10 as needing no validation change, because `validate` already accepts FROZEN (spec.py:133). A FROZEN-only pin is described for the supervisor, not proposed, and not applied in the dry switches.
- P3-3e d.3, the form of the `spec.py` changes:
  - AM-08 replaces "normal" with the constant in `validate`'s `pinned` table, which compares by equality, rather than adding a separate check. It is the smaller change.
  - The constants sit apart (AM-08's after `CANONICAL_LAG_RULE`, AM-09's after `FORBIDDEN_MODELS`), so that the diffs apply together in either order.
- P3-3e d.2 and e, placeholder formats the texts leave open: `<R_dk>`, `<R_boot>` and `<R_cw>` are written to four decimals, as AM-07's note fixes for its rates.
- P3-3e e, what the dry switches append to `spec/SPEC_AMENDMENTS.md`: the heading, the filled text, `**Lines (exact):**` and the record, but not the placeholder notes, which are guidance. The records are written with non-ASCII characters unescaped, as the existing records are.
- P3-3e d.2, the document's layout:
  - a title line above the six sections;
  - headings, texts, templates and records in fenced code blocks, since bare placeholders would read as HTML;
  - an amendment's shared text before its variants.
  - `/tmp/p3_3e_dq6.py` was changed once after its first listing in the report, for that placement. Its final form is also printed.
- P3-3e e, the dry switches:
  - Each ran in its own clone of the base clone, committed locally.
  - The dummy line 7's `utc` is the time of writing. Its caller text imitates `sim`'s format, with invented line numbers.
  - 276 tests ran in each, not 280, because `TestTinyRuns.setUpClass` errored. The sixth skip was identified by a verbose run of two modules in the D1 clone.
- P3-3e d.6, the three `tests/test_p3_sealed_run.py` rows: their proposals rest on the builder's reading of the tool after the switch's C7 rerun (the configuration would be refused for its `spec_sha256`). That state was not run.
- P3-3f e.2, the power-source STOP and the rerun:
  - The first run of the clone rehearsal passed its 8 tests, then stopped at the dry run. The dry run refused only for the power source: check 7, after checks 1 to 6 passed, printed "not on AC Power (Now drawing from 'Battery Power')".
  - As step e.2 directs, the builder stopped. No refusal case had run.
  - Isaiah plugged in (`pmset -g ps`: AC Power) and asked for the clone rehearsal to be run once more from its start, with the driver unchanged. The second run passed: the 8 tests, the dry run, cases (a) to (k) and every step 4 check.
  - Both runs are in the report.
- P3-3f c, a refused command: the first attempt at step c's listing was a `bash -c` script of `awk` and `grep` lines. Claude Code's built-in safety check refused it as a possible removal. It contained no removal, and nothing in it ran. The same lines were printed with plain commands.
- P3-3f e, the launcher's choices beyond the item's text:
  - `--data-dir` must be an absolute path.
  - The interpreter, which the item does not number, is chosen after check 7 and before check 8.
  - Check 8 requires the tool's exact line `config docs/P3_RUN_CONFIG.json SHA-256 <rehearsed>; valid: True`.
  - The summary prints the command as the script's own line, read from the file at the marker `# >>> THE ONE COMMAND <<<`, together with the values of DATA_DIR, PY and EXPECT. The sealed variable and `--real` therefore appear on one line of the script only (test 2).
  - The command pipes the tool's output through `grep -E '^(COMPLETE|ABORTED|REFUSED)'`, which keeps only the tool's own status lines, and takes the tool's exit code from `PIPESTATUS`. `caffeinate` passes its child's exit code through; this was checked once with a harmless child (`sh -c 'exit 3'`).
  - The power check matches "AC Power" with a bash pattern rather than a pipe into `grep -q`, which can fail under `pipefail`.
  - Line counts use `awk`, because `grep -c` exits 1 on an empty file under `set -e`.
  - A `DEV_FILE` constant (`io.py`'s name) serves check 9. Test 5 also checks it, beyond the item's list.
- P3-3f e, how the files were made:
  - The launcher was written from a template by `/tmp/p3_3f_make_launcher.py`, which filled its six constants from their sources. Both are in the report.
  - The clone driver (`/tmp/p3_3f_cases.py`) was corrected twice before its first run, so neither change was a rerun. A regular expression had a stray alternative that could not yield the hash. The dry run's "check 9 ... not checked (--dry-run)" line is now exempt from the all-True condition, as step e specifies that check 9 is skipped under `--dry-run`.
- P3-5 c, a second run of the rules script, not requested by the item: the first run's test strings used *, which Markdown reads as emphasis in the .md tables. The first run's files were kept as /tmp/p3_5_run1_selection.json and .md and removed from reports/. The script was changed in its three test strings only (* to ·) and run a second time. Every result is the same in both runs, and the committed selection files are the second run's.
- P3-5 c, the comparison of the two runs: the first attempt, an inline python -c, failed with a quoting SyntaxError. Its one rerun, /tmp/p3_5_compare_runs.py, printed False because of two bugs in the check: json.dumps writes the character · as an escape, and the .md lines' bold markers were replaced too. Under the rerun-once rule this was a STOP. After the supervisor's review, the continuation ran a corrected comparison, /tmp/p3_5_compare_runs2.py; its result is in Test results.
- P3-5 c, the state at the STOP: the outputs' and BLIND_FIT_LOG's hashes printed at the STOP were compared with step a.2's values copied into the command from its output, not read by script.
- P3-5, continuation a.2, the state check: its first run printed False only for its own count check, which expected nine listed hash values where the message lists eight. Every file check was True. The count was corrected and the script run once more (rerun-once rule): True. Both runs are in the report.
- P3-5 c.7, the placeholder table: the rules script may read only the run's JSON and the configuration, so the placeholders each amendment uses are written into it as a table. A separate script checked that table against `docs/P3_DQ6_drafts.md` section 2 before the rules ran (True).
- P3-6a d.4, before the test changes: one read-only listing (the import lines and module constants of the five test files, by `grep -n`) ran as a zsh `for` loop, against the standing rule to run loops in bash or write one command per file. It read tracked test files only and changed nothing.
- P3-6a d, the scratch clone's local commits: the switch, the test changes and the C7 rerun were each committed in `/tmp/p3_6a_clone` (remote removed), so that each suite ran on a clean tree and the patch is one `git diff --binary` from REPO's HEAD to the clone's HEAD, with the two C7 reports excluded. The commits were deleted with the clone.
- P3-6a d.4, choices beyond the rows' text: the tests read the configuration's SESOI with `json`, so `tests/test_inference_b2.py` gains `import json` at its top, and `tests/test_spec.py` imports it inside `test_sesoi_pending`. The tiny runs' class keeps its name, `TestTinyRuns`, and holds test 17 alone.
- P3-6a d.3 and d.6, six skips where step d.6 expected five: after the switch, `tests/test_io.py:89-93` (`test_main_repo_has_no_unblinding_tags_while_draft`) skips once the status is FROZEN ("spec frozen; tags expected"), as `docs/P3_DQ6_drafts.md` section 6 notes under "Not failures". A verbose run of four modules in the clone showed the six skips. The result was OK, so the builder read the gate's "steps 6 and 7 OK" as met. After the switch commit, REPO's suite would skip six tests.
- P3-6a d.9, the file-list check: its first form compared the list as `sort` printed it with a string in byte order. Under the user's locale, macOS `sort` placed `spec/SPEC_AMENDMENTS.md` after `spec/analysis_spec_dev_v1.yaml`, so the check printed False, although the patch's numstat listed exactly the eight expected files. The check was rewritten as a set comparison and run once more (rerun-once rule): True. The rerun's command line also held a redundant first `git apply --numstat`, piped into the venv's activation, which reads no input; it had no effect. Both runs are in the report.
- P3-6a, notes in its report outside Deviations (recorded at P3-6b): /tmp/p3_6a_records.py had two parsing lines corrected before its only run; after it ran, two formatting slips it had written into the P3-6a Test results ("= 285.." and a Python list repr) were fixed by exact replacement; and after the checkpoint, step g printed four scripts into the report with a zsh for loop (echo, shasum and cat of literal paths only). None of them changed a result.
- P3-6b d.4, the status check after the C7 rerun: it ran as an inline Python heredoc (`python -`), not as a saved script; the report prints it as it ran. It read the expected lines from the report's d.3 section. The bash command before it also defined a shell variable listing the expected lines, typed; that variable was never used.
- P3-6b e, a formatting slip in the records script's output: the P3-6b Test results listed the line "copy equals source: True" twice, because the filter for the SHA-256 lines (lines beginning "copy " or "source ") also matched that check line. One copy was removed by exact replacement (`/tmp/p3_6b_fix.py`); the records script was not rerun. No result changed.
- P3-6b, notes in its report outside Deviations (recorded at P3-7a): /tmp/p3_6b_records.py had five exact replacements made to it by an inline edit before its only run; three check scripts wrote their output to temporary files under /tmp/p3_6b, appended them to the report and deleted them; and --check-config ran four times, each required by a step, with /tmp/p3_6b_cfg.py labelling every run "(run once)". None of them changed a result.
- The new session's orientation (recorded at P3-7a; /tmp/p3_boot.txt, read-only, before P3-6b): one read-only command failed in zsh on "echo ====" after its first part had printed, and its remaining grep was run on its own; and its first note gave a file count (166) typed from an earlier run, corrected in an addendum (167: 40, 70 and 57 by search root). The standing prompt matched by SHA-256 in both runs. Nothing was written outside /tmp/p3_boot.txt.
- P3-7a c.12, the name search: the item asks for files under `~/Desktop/FX_Project` to depth 2. RAW (`~/Desktop/FX_Project/raw`) and OUT (`~/Desktop/FX_Project/build_out`) are pruned from the search, because the standing prompt forbids listing or searching anything under them. A file of that name at depth 2 inside either would not be found.
- P3-7a c, choices the item left open: in c.2, a line holding a document's full SHA-256 is listed once, as a full hit, and lines holding only its first 16 characters are listed as "first 16 only"; in c.11, the filter for `git tag` calls prints every line in `tests/` with a quoted "tag" argument, with its enclosing function. That includes `tests/test_docs_d3.py:41`, which lists REPO's tags, and `tests/test_io.py:109`, an assertion.
- P3-7a, notes in its report (recorded at P3-7b): /tmp/p3_7a_records.py had one line changed before its only run, and the checkpoint ran after midnight UTC while the local date, which the date gate reads, was 2026-10-07. Neither changed a result.
- P3-7a2 (recorded at P3-7b; read-only, no checkpoint): its step b ran twice under the rerun-once rule, because the first run's b.4 had three bugs in its own matching rules. b.1 to b.3 were byte-identical in both runs, and a read-only grep supplemented b.4 for the one importlib binding. Nothing in REPO changed.
- P3-7b a.3, f.8 and g.2, the configuration check: the message says "No run of `tools/p3_sealed_run.py` in any mode", while its records rule requires `--check-config` to print valid: False and exit 2. Before a.3 the builder asked Isaiah in the session; his answer: run `--check-config`, as at P3-6b and P3-7a (it reads no data). The tool ran in that mode only.
- P3-7b f.8, the records rule's prefixes: the message calls them the six prefixes of `validate_config`'s rebuild. The rebuild (`_rule_lines` in `tools/p3_sealed_run.py`) reads five of them from PASS3_STATUS.md, and AM-02 from the spec. The check uses the six reserved prefixes as the P3-7a message lists them (those five and `>   - D4.3 T6.`), read from `/tmp/p3_7a_msg.txt` after its SHA-256 is checked.
- P3-7b d.1 and d.3, edits before the scripts' only runs: `/tmp/p3_7b_kit.py` had its kit-path line simplified, and `/tmp/p3_7b_apply.py` was changed to check every "before" value before writing any file, and to take the four documents from the kit table rather than by name. Each then ran once (the apply script once per root).
- P3-7b c.6: the item asks whether `git config user.name` and `user.email` are set in REPO; the exit codes of `git config --local` for both are printed as well.
- P3-7b f, an omission in the records script's output: the P3-7b Test results listed the kit check without its lines, because `/tmp/p3_7b_records.py` reused the name `k`, which held the report's d.1 section, as a loop variable before using it. The lines were inserted from the report's d.1 output by exact replacement (`/tmp/p3_7b_fix.py`); the records script was not rerun. No result changed.
- P3-8a c.2, the parse: the first parse of the clone's verbose log (`/tmp/p3_8a_suite.py`) listed 10 skipped tests where the result line says skipped=6. It took a test's result from its own line or the next one, so four tests whose result was not on their own line took the next test's "skipped". Under the rerun-once rule the parse was fixed (the next line is read only if it is not another test's line) and run once more on the saved log (`/tmp/p3_8a_suite_parse.py`): 279 ok and 6 skipped, the six expected. The suite itself ran once, correctly; both parses are in the report.
- P3-8a b, choices the item left open: in b.7, "every function that contains" a line is read as the outermost function containing it (for a method, the method), and b.7.2 prints the module's top-level functions and methods, not nested functions separately (one edit before the script's only run); b.1 also prints each file's SHA-256 and line count.
- P3-8b a.1, the message: its first paste was cut off in step f.2. The builder ran the date gate and asked how to proceed; the question was declined and the full message pasted. The date gate then ran again first, and the full message was saved. Nothing else ran on the first paste. Before a.2, a read-only `python -c` checked that the saved message's `tests/tag_state.py` block has the given SHA-256 (True).
- P3-8b c.2 and d.1, a reading the item left open: the apply's status check expects exactly the nine ` M` and `?? tests/tag_state.py`; in REPO it also expects step b's report copy (`?? reports/P3_reports/p3_8a.txt`), which step d.2 lists.
- P3-8c b.2, the guard check: a first attempt to make `/tmp/p3_8c_guard.py` by `sed` from P3-8b's script failed on a `sed` syntax error (a replacement held the delimiter), and its output redirect left a 0-byte file. The Write of the script was then refused, because the file existed unread, and the same command block ran the 0-byte file, which exited 0 and checked nothing; no access record was written and the tree stayed clean. Under the rerun-once rule the script was written whole and run once: GUARD CHECK True. Both runs are in the report.
- P3-8c e.7, the check's wording (Isaiah's reading, on the supervisor's recommendation, in the continuation message): "the decision block's checkpoint appears exactly once in the added Decision-log lines" reads as: exactly one added Decision-log line contains `Checkpoint` followed by the hash `f5271c03481b7514a1ec4b7e739fb85fbce8a774`, the form P3-7b used. The hash also appears, by design, on the tag's line ("annotated, on" the hash). P3-8c stopped at e.7 on the literal wording; nothing was reverted, and the continuation ran e.7 again with this reading, then step f.
