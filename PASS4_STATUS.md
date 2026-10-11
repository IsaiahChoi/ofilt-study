# PASS4_STATUS: the dev first look and the P13(b) dry run

Standing prompt: `files/pass4/PASS4_BUILDER_PROMPT_2026-10-08.md` (SHA-256 `96327904ec55a1de5ad4f51b1cc27fc9b447b9b124a05243400523835e47984d`), adopted by the P4-boot paste. `PASS3_STATUS.md` is closed (P4Q8).

## Progress

| Item | Status | Notes |
|---|---|---|
| Pass 4 | in progress | The dev first look and the P13(b) dry run (PLAN §8, row 4). |
| P4-0a P3-9 accepted; the /tmp records kept; the snapshot staged for the supervisor chat | done; accepted by Isaiah 2026-10-08 | Run under the Pass 3 prompt; no commit. Report `reports/P4_reports/p4_0a.txt`. |
| P4-boot a new builder session; the standing prompt found by its hash | done; accepted by Isaiah 2026-10-08 | Read-only; no commit. Report `reports/P4_reports/p4_boot.txt`. |
| P4-0b Pass 4 opened; P3-8c, P3-9, P4-0a and P4-boot accepted; reports copied | done; accepted by Isaiah 2026-10-08 | `checkpoint: P4-0b`. Report `reports/P4_reports/p4_0b.txt`. |
| P4-1 the read-only audit of every pre-registered output and rule (P4Q4) | done; accepted by Isaiah 2026-10-09 | Read-only; no commit. Report `reports/P4_reports/p4_1.txt`; the audit `reports/P4_reports/p4_1_audit.md`. |
| P4-2 P4-0b and P4-1 accepted; P4Q9 to P4Q31; the confirmation configuration; the M2 note | done; accepted by Isaiah 2026-10-11 | `checkpoint: P4-2`, made by its second run; the first stopped at b.1 (Decision log). Report `reports/P4_reports/p4_2.txt`. |
| P4-3 P4-2 accepted; P4Q32 and P4Q33; the full-schema simulator and its tests (T3) | done; accepted by Isaiah 2026-10-11 | `checkpoint: P4-3`, made by its fourth run; the first three stopped at a.1, b.1 and c.1 (Deviations). Report `reports/P4_reports/p4_3.txt`. |
| P4-4p P4-3 accepted; P4Q34 (P4-4 split); a read-only synthetic probe of the inference calls | done; accepted by Isaiah 2026-10-11 | Read-only; no commit. Report `reports/P4_reports/p4_4p.txt`. |
| P4-4a P4-4p accepted; P4Q35; the confirmation module's inference rows and their tests | done | `checkpoint: P4-4a`. Report `/tmp/p4_4a.txt`, copied at the next checkpoint; planned STOP: the supervisor reviews the report, then P4-4b. |

## Next action

The supervisor reviews P4-4a. Then P4-4b, forecasting and the economic evaluation (O29 to O45, R9), synthetic only, and its tests.

## Decision log

> - P3-8c accepted, its continuation included (Isaiah, 2026-10-08, on the supervisor's recommendation; recorded by the P3-9 paste).
>   - Checkpoint `96963b31d620ab98ff529458fcd095f412c443bd`.
>   - The e.7 reading of the continuation message: the check counts the one added Decision-log line that contains `Checkpoint` followed by the hash in backticks; the hash also appears, by design, on the tag's line. `PASS3_STATUS.md`, Deviations, records it.
>   - Report `reports/P3_reports/p3_8c.txt`: P3-8c and its continuation in one file.
> - P3-9 accepted (Isaiah, 2026-10-08, on the supervisor's recommendation; recorded by the P4-0a paste): the eleven files of PROJECT_SETUP's "After Pass 3" list staged from the committed tree; no commit. Report `reports/P3_reports/p3_9.txt`.
> - The Pass 3 Project upload verified (the supervisor, 2026-10-08; a routing record, not a decision): the Project holds exactly the 40 files of Appendix A of `PASS3_SUPERVISOR_HANDOFF_6_2026-10-08.md`, each byte-identical by SHA-256, after two extra files were deleted: the retired `PASS3_SUPERVISOR_HANDOFF_2026-10-06.md`, not yet deleted at the upload, and `SHA256SUMS_P3_upload.txt`, uploaded by mistake.
> - P4-0a accepted (Isaiah, 2026-10-08, on the supervisor's recommendation; recorded by the P4-0b paste): run under the Pass 3 prompt; no commit. The five `/tmp` records kept outside `/tmp`; a snapshot of the committed tree at `96963b31d620ab98ff529458fcd095f412c443bd` (178 files, none excluded), its manifest, the Pass 3 prompt and the P3-9 report staged for the supervisor chat, which verified the snapshot member by member. Report `reports/P4_reports/p4_0a.txt`.
> - The Pass 4 standing prompt adopted (Isaiah, 2026-10-08, on the supervisor's recommendation; by the P4-boot paste): `files/pass4/PASS4_BUILDER_PROMPT_2026-10-08.md`, SHA-256 `96327904ec55a1de5ad4f51b1cc27fc9b447b9b124a05243400523835e47984d`, with P4Q1 to P4Q8 (below). The Pass 3 prompt is retired.
> - P4-boot accepted (Isaiah, 2026-10-08, on the supervisor's recommendation; recorded by the P4-0b paste): a new builder session found the standing prompt by its hash; read-only; no commit. Report `reports/P4_reports/p4_boot.txt`.
> - P4Q1 (Isaiah, 2026-10-08, on the supervisor's recommendation): Order.
>   - The confirmation script is written and validated on synthetic data only, and committed, before any computation that relates a predictor to a target on the dev panel.
>   - The first such computation is the dev run (P4Q6). Isaiah sanctions it in a later message against the SHA-256 of the committed script and configuration; the sanction carries that message's date.
>   - Until then, the dev panel is used only for predictor-only, target-only and gap-only statistics and structural facts (row and date counts, missingness), each named by an item.
>   - A change to the script or configuration after the dev run is recorded with its reason and listed for disclosure.
> - P4Q2 (Isaiah, 2026-10-08, on the supervisor's recommendation): Code placement.
>   - Existing files under `ofilt/`, `tools/` and `build/`, and the spec, change only where a later message lists the change. In particular, the six C7-hashed files (`ofilt/drift/inference.py`, `sim.py`, `forecast.py`, `fctests.py`, `models/linear.py`, `tools/c7_mc.py`) stay byte-identical, so the C7 report stays valid.
>   - New code goes in new files named by items.
>   - A robustness design starts from the output of `inference.build_design`, the guarded path, and appends or re-arranges columns on the same rows, aligned by `Design.index`. New code never calls or names the unguarded design core.
>   - Regressors outside the forecasting allowlist come from an inference-only allowlist holding exactly the columns P33 and AM-05 name for the robustness rows. A static test shows that no forecasting code uses it. Columns are selected by explicit name only.
> - P4Q3 (Isaiah, 2026-10-08, on the supervisor's recommendation): The panel is passed in.
>   - The script's analysis takes a loaded panel and its provenance. Its loaders are the simulator (synthetic), `io.load_dev` (dev, verified by the spec's hash) and, for Pass 6, `io.load_confirm`.
>   - In Pass 4, `load_confirm` is called only in refusal tests that patch `io.ACCESS_LOG_PATH` to a temporary file and `io.DATA_DIR` to an empty folder, as `test_io` and `test_guard_p46` do. `TS.blinded()` alone does not redirect `io`'s log.
>   - No new file under `ofilt/` or `tools/` contains the literal name of either tag (`test_docs_d3b`).
> - P4Q4 (Isaiah, 2026-10-08, on the supervisor's recommendation): The gaps are filled blind.
>   - A read-only audit maps every pre-registered output and every robustness row to its defining text (spec, AM-xx, P-decisions) and its code entry point, and lists every detail those texts leave open.
>   - Isaiah decides each gap before the dev run. The decisions go into a committed confirmation configuration, hash-pinned and read by the script, which refuses any other.
>   - The frozen spec is not edited. The pre-registration cites the configuration.
> - P4Q5 (Isaiah, 2026-10-08, on the supervisor's recommendation): Recovery criteria are stated in advance, in the item that runs the synthetic dry run.
>   - The setup: the confirmation calendar and the AM-03 target; b = 0 and at least one b ≠ 0; a known break at 2024-11-05 for the post-2024 row.
>   - The criteria: every output present and finite, or marked not applicable by design; two runs byte-identical apart from runtime fields.
> - P4Q6 (Isaiah, 2026-10-08, on the supervisor's recommendation): The dev run.
>   - One run of the committed script on the dev panel (SHA-256 `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68`), sanctioned as in P4Q1, outside the suite; its outputs and report committed.
>   - Its forecasting part appends to `RUN_REGISTRY.jsonl`, so that commit rewrites `test_docs_d3b`'s empty-registry assertion to the new state by decision, under the test-change protocol. `BLIND_FIT_LOG` stays at 7 lines, and the run asserts it.
>   - Who launches the run, the builder or Isaiah in Terminal, is decided after the synthetic dry run has timed it at dev length.
> - P4Q7 (Isaiah, 2026-10-08, on the supervisor's recommendation): No exploratory extras are planned. Any other dev computation needs its own decision, a named committed script and recorded outputs, and joins the disclosure list.
> - P4Q8 (Isaiah, 2026-10-08, on the supervisor's recommendation): Records.
>   - PASS4_STATUS.md has Pass 3's sections plus a Disclosure list.
>   - Reports of Pass 4 items are copied to `reports/P4_reports/`, and those of Pass 3 items to `reports/P3_reports/`.
>   - Decisions P82 onward go in `docs/DECISIONS_P82_onward.md`, pinned in `tests/test_docs_p2.py` when written.
>   - PASS3_STATUS.md is closed and never edited again, so DQ6's records rule holds trivially and does not apply to PASS4_STATUS.md. `docs/P3_RUN_CONFIG.json` keeps refusing every run.
> - P4-0b accepted (Isaiah, 2026-10-08, on the supervisor's recommendation; recorded by the P4-1 paste, whose step a.1 printed that date): checkpoint `795385fa709f4cf6c8e7f441d879cc1c1b89e46b`. Its deviation and its rerun under the rerun-once rule are in Deviations. Report `reports/P4_reports/p4_0b.txt`.
> - P4-1 accepted (Isaiah, 2026-10-09, on the supervisor's recommendation; recorded by the P4-2 paste): the read-only audit of P4Q4, with 71 rows (45 outputs and 26 rules) and 22 gaps; its AUDIT, CITES and FILES checks True; no commit. Report `reports/P4_reports/p4_1.txt`; the audit `reports/P4_reports/p4_1_audit.md`.
> - The M2 derivation (the supervisor, 2026-10-08; a routing record, not a decision):
>   - Written blind on 2026-10-08 in a separate chat of the Project, from the prompt `docs/P4_M2_prompt.md`, which allowed no data file, no Project code, no web search and no project-knowledge search, and named the passages to read.
>   - The supervisor chat checked the derivation and reran its check script: the output reproduced the note's table line for line (282 lines), ending `M2 CHECK: True`.
>   - Committed at P4-2 as `docs/P4_M2_note.md`, with its check `docs/P4_M2_check.py` and its prompt; their SHA-256 are in the Disclosure list. It informs P4Q17 and the flags F4-3 and F4-4.
> - P4Q9 to P4Q31 (Isaiah, 2026-10-09, on the supervisor's recommendation): P4Q9 to P4Q30 decide the gaps G1 to G22 of `reports/P4_reports/p4_1_audit.md`, in order, by the options lettered there; P4Q31 states the contingency rules. All are written into `docs/P4_CONFIRM_CONFIG.json`, version 1.
>   - P4Q9 (G1, option a): f's two periods. The confirmatory f is one joint fit on the confirmation rows dated 2022-01-01 to 2022-12-31, with its own T and DK lag; the descriptive f is one joint fit on the rows dated 2023-01-01 to 2026-03-05. Disclosed with it: the 2022 fit has about a quarter of T_conf, so its DK-normal intervals are not calibrated at its T.
>   - P4Q10 (G2, option a): on dev, f is one joint fit on the whole dev estimation sample, labelled a dev stand-in. f's two periods are not applicable on dev by design and are exercised on synthetic data.
>   - P4Q11 (G3, option a): the rolling-250 β is the past-only slope over the last 250 eligible rows (non-excluded, lag 1 day, continued across samples), as AM-05 defines the rolling-500 β and `targets.past_beta` computes it.
>   - P4Q12 (G4, option a): AM-05's reporting form (b with and without the change on the same rows, next to the full-sample primary b) also applies to `beta_rolling_250`, `copx_to_fcx` and `raw_target`. The four exclusion rows, the post-2024 row and the per-ticker row report their own estimates next to the full-sample primary b.
>   - P4Q13 (G5, option a): `copx_to_fcx` uses the primary rows with a finite `fcx_oc`.
>   - P4Q14 (G6, option b): `xau_control` and `mechanism_session_fx_gotobi` use the primary rows on which every added column is finite, and report the rows and dates dropped, as the EWJ row does.
>   - P4Q15 (G7, option b): the per-ticker row is one pooled DK fit with `usdjpy_ret` and `eurusd_ret` both ticker-specific, so its point estimates equal per-stock regressions; Holm across the three two-sided p-values of the `usdjpy_ret` slopes.
>   - P4Q16 (G8, option a): tier (ii)'s condition (3) is signed: b_with / b_without ≥ 0.5 on point estimates. It fails if the two differ in sign, or if b_without is zero or not finite.
>   - P4Q17 (G9, option c): no tier-(iii) claim.
>     - H3 (â₂, its DK SE and two-sided p) and the metals rows (`copx_to_fcx` with and without the swap on the same rows; `xau_control` with and without XAU; `raw_target`, with the gap between its â₂ and the primary â₂) are reported without a tier-(iii) reading.
>     - The pre-stated reading: a₂ is the session drift on EUR/USD conditional on `usdjpy_ret`, SPY and COPX; its sign is not attributed to the metals channel (`docs/P4_M2_note.md`, Propositions 1, 2 and 5). P32's tier (iii) is not used.
>     - Option (b) was not available, because the pre-registration follows the dev run (P4Q1).
>   - P4Q18 (G10, option b): tier (i)'s wording is P32's, "overnight USD/JPY predicts session drift".
>   - P4Q19 (G11, option a): D2.7's wording. Equivalence at the primary SESOI licenses only "no drift exploitable net of costs", with the results at the low and high SESOI beside it; a null H1 is read against MDE80 (0.2471). The sentences of P23 and PLAN §1.4 are not used.
>   - P4Q20 (G12, option a): at the confirmation, each `walk_forward` call runs on the joined dev and confirmation rows, and its comparisons, `report_all` items, importance and economic evaluation use only the evaluation rows on confirmation dates, the setting c_CW,cal was calibrated for.
>   - P4Q21 (G13, option a): in the dev run, every dev forecast row enters. The confirmation-date restriction is exercised on synthetic data, and on dev Clark–West is shown against both the normal reference and c_CW,cal, as exploratory.
>   - P4Q22 (G14, option a): M0 is added to M7's `walk_forward` call, so M7's OOS R² against M0 is reported; M0 reads no feature, so the call's sample is unchanged.
>   - P4Q23 (G15, option a): permutation importance is computed and reported for M7 only, against its noise column.
>   - P4Q24 (G16, option b): the economic evaluation reports, pooled, the break-even of M3, of M2 and their difference, next to the primary, low and high mean round trips, and the mean net P&L per name-day under each of the three cost cases.
>   - P4Q25 (G17, option b): at the confirmation, the tick terms are recomputed by D2.4's and D2.5's rules on the confirmation rows' own open and close prices. The locked SESOI is unchanged.
>   - P4Q26 (G18, option a): the D4.3 window deviations are not examined on dev (P4Q7).
>   - P4Q27 (G19, option a): every `walk_forward` call uses the spec seed.
>   - P4Q28 (G20, option b): the dry run's recovery criterion adds numeric tolerances for b̂ and b_post against the known values to P4Q5's criteria, stated in the dry-run item's message before the run.
>   - P4Q29 (G21, option a): the dry run's draws use the spec seed plus a new offset block, disjoint from the B7, B7b, C7 and sealed-run blocks (D4.5's pattern); the offset is set in the dry-run item.
>   - P4Q30 (G22, option a): what the forward holdout evaluates is fixed in the pre-registration (Pass 5).
>   - P4Q31 (contingencies; P13(c)): the confirmation run never stops to ask.
>     - A row with no rows, a rank-deficient design, or a non-finite estimate or SE that it reports is reported as not estimable, with its reason and its row and date counts, and the run continues.
>     - A ratio with a zero or non-finite denominator is undefined, and a criterion that needs it fails.
>     - In a Holm family, a member that is not estimable enters with p = 1, so the family size is unchanged.
>     - A claim whose inputs include a not-estimable result is not made.
> - P4-2 accepted (Isaiah, 2026-10-11, on the supervisor's recommendation; recorded by the P4-3 paste): checkpoint `7828e79207acbaa9b8919077b50da1449d6783c9`, made by P4-2's second run.
>   - The first run (2026-10-09) stopped correctly at b.1 (`B1 CHECK: False`): the kit folder `files/pass4/p4_2_kit` was empty, and the five kit files and the message file were in `files/pass4` itself (the run's own listing). It changed nothing in REPO.
>   - The rerun message (SHA-256 `3fac2abeeb07a021e0675bd2b1030e679ebafbb6147691e117bf8727ec8b941f`) recorded Isaiah's decision, on the supervisor's recommendation, to rerun P4-2 in full. Its account of the first run, that the kit folder held a sixth file (the message), was the supervisor's misreading; the first run's own output is the record. At the rerun the kit folder held exactly the five kit files, each with its SHA-256 (the rerun's b.1).
>   - Report `reports/P4_reports/p4_2.txt`: the rerun message, the first run's report in full, and the rerun's steps.
> - P4Q32 (Isaiah, 2026-10-11, on the supervisor's recommendation): the full-schema simulator (T3), as `docs/P4_SIM_SPEC.md` specifies it.
>   - A new module, `ofilt/drift/sim_full.py`, generates the panel directly: a dev-like and a confirmation-like frame, each with exactly the 60 schema columns in the dev panel's order and shaped as `io.load_dev` returns a panel, with provenance `synthetic` and the truth in `attrs`; and an events table shaped as `io.load_events_firm` returns one. It reads and writes no file. `sim.py` is unchanged.
>   - The truth is structural. The hedge and the abnormal parts are generated separately, and `y_oc` is β_i times `y_1306_oc` plus the abnormal part. By default the hedge's open-to-close return is independent of the design and of the abnormal part, and the hedge gap loads on no FX regressor, so the AM-03 target that `targets.add_targets` builds recovers b, b_post and a₂, and `cc_abn` recovers δ_cc, up to estimation noise. A knob gives the hedge an FX loading; the truth then gives only the structural slopes.
>   - Calendars: the confirmation dates are `calendar.confirmation_calendar()`; the dev history is the weekdays from 2015-01-06 to 2021-12-30 less a stated rule-based holiday set (1,714 dates), replaceable by an argument. The synthetic events give T_conf = 1013 by construction. The break at 2024-11-05 applies to b (b_post = b + Δ) and to the TSE close (15:00 to 15:30 JST), which sets the window and session columns.
>   - A default scenario with small, stated missingness, and a not-estimable preset that triggers the paths of P4Q14 and P4Q31.
>   - Tests: the new file `tests/test_p4_sim_full.py`, with exactly the 20 tests the specification lists. Their seeds are the spec seed plus 8,000,000 plus k, k below 1,000, disjoint from every earlier block.
>   - Not chosen: raw files pushed through the frozen build (the route of `tests/p2_synth.py`); a target built from the true β instead of by `targets.add_targets`; the real dev dates read from the panel.
>   - The specification is version 2 (Isaiah, 2026-10-11, on the supervisor's recommendation, option B). Version 1 (SHA-256 `6b500f4b30aece4be6d375ada094fc5cfde0f43260f32aba7a086f3db38a8e81`) was never committed: P4-3's step c.1, in its third run, found `n225_bars` of kind f in the dev panel that `io.load_dev` returns, where version 1's Table D gave i, and P4-3 stopped before any code was written. Version 2 records kind f; adds the knob `n225_missing`, default (3, 3): nights with no Japan 225 window record, on which the build leaves the four Nikkei columns empty, so that AM-05's rule making such a night ineligible for the Nikkei-proxy row is exercised on synthetic data; and writes in two readings the builder recorded (test 7's tolerance; `boj_day` in 2026). Its §10 lists the changes. Not chosen: the kind alone (option A). The runs of P4-3 are recorded at P4-4.
> - P4Q33 (Isaiah, 2026-10-11, on the supervisor's recommendation): one structural contact with the dev panel (P4Q1).
>   - One read-only script of P4-3 (step c.1) and one test (`test_dev_panel_kinds_and_guard` in `tests/test_p4_sim_full.py`) read the dev panel through `io.load_dev` and the firm events through `io.load_events_firm`, each verified by its hash, for their column names, the columns' order and each column's dtype kind only.
>   - The test also lets `io.load_dev` register the real targets in the guard's fingerprint registry, as the existing tests that call it do, so that `blind.require_unblinded` then checks the simulator's frames against them.
>   - No value is printed, compared or computed beyond these. Both are listed in the Disclosure list.
> - No date gates (Isaiah, 2026-10-11): from P4-3's message version 2 on, a block records the date its first command prints and uses it as the decision date. A records edit is checked before the commit by a date-independent template hash (its result with the placeholder kept), and the supervisor checks the dated result after the commit.
> - P4-3 accepted (Isaiah, 2026-10-11, on the supervisor's recommendation; recorded by the P4-4p paste): checkpoint `b0e7327dd3685b376215866375a6e213080426bf`, made by P4-3's fourth run.
>   - Accepted with it: the builder's reading of test 11 (it replays the module's row-level generator, whose draw order the module states, to check `range_lag1` exactly, and verifies the replay against `gap_resid`), and test 12's check of §8.3's formulas on S1 with Sc1, stronger than §9.3's default S0 with `Scenario()`, under which b and Δ are 0.
>   - The first three runs and their causes are in Deviations, P4-3. Report `reports/P4_reports/p4_3.txt`: the fourth run's steps, with the third run's report in full, which holds the first two.
> - P4Q34 (Isaiah, 2026-10-11, on the supervisor's recommendation; recorded by the P4-4p paste): P4-4 is split into three items, each with its own specification kit, checked by the supervisor before handover, and its own checkpoint.
>   - P4-4a: the inference rows (O1 to O28, R1 to R8) and the shared pieces: loading the confirmation configuration and pinning it by a test; the joined dev and confirmation frame; P4Q31's contingency rule, with "no rows" detected before `subset_design`; AM-05's Nikkei-proxy filter, a night with no Japan 225 record being ineligible; and the output document's schema for all 71 audit IDs.
>   - P4-4b: forecasting and the economic evaluation (O29 to O45, R9).
>   - P4-4c: the run script and the claims (R10 to R26): the end-to-end script, the claim tiers and wording rules, the two-run byte-identity rule, the registry routing, the `io.load_confirm` refusal tests and the static test of the inference-only allowlist.
>   - Not chosen: P4-4 as one item.
> - P4-4p accepted (Isaiah, 2026-10-11, on the supervisor's recommendation; recorded by the P4-4a paste): read-only, no commit. It ran every library call P4-4a makes on two simulator frames (a recovery scenario and `Scenario.not_estimable()`), with `OFILT_DATA_DIR` set to an empty folder and no module of `io` imported. It found three facts that P4Q35 follows: `build_design`'s `exclude` replaces the spec's exclusion flags rather than adding to them; `secondary_family_tests` raises as a whole when one member is not estimable; and `subset_design` with no row raises numpy's `ValueError`, not `DesignError`. Its deviation is in Deviations. Report `reports/P4_reports/p4_4p.txt`.
> - P4Q35 (Isaiah, 2026-10-11, on the supervisor's recommendation): the confirmation module's inference rows, as `docs/P4_CONFIRM_INF_SPEC.md` specifies them.
>   - A new module, `ofilt/drift/confirm_inference.py`, computes the 36 inference rows (O1 to O28, R1 to R8) on a dev frame, or on the joined dev and confirmation frames with inference on the confirmation dates, and returns one document with an entry for each of the 71 audit IDs, P4-4b's and P4-4c's left pending. It reads only the configuration, pinned by its SHA-256, and writes no file. No C7-hashed file changes.
>   - P4Q31's rules are applied by one helper: "no rows" is checked before any subset; design errors, rank deficiency and non-finite results make a row not estimable, with its reason; a not-estimable Holm member enters with p = 1; an undefined ratio fails. The exclusion rows pass the spec's flags with their own column. The four secondary members are fitted one by one. The rows that add regressors report b with and without on the same rows (R8), their columns appended to `build_design`'s output by row. Infinite Fieller endpoints are written as null, so that the document serialises without NaN or infinity.
>   - Tests: the new file `tests/test_p4_confirm_inference.py`, with exactly the 23 tests the specification lists, on simulator frames only, never labelled real. Their seeds are the spec seed plus 8,100,000 plus k, k below 1,000, disjoint from every earlier block.
>   - Not chosen: calling `secondary_family_tests` for the family (it cannot apply P4Q31's Holm rule); changing `inference.py` (C7-hashed).
>   - The specification is version 2. Version 1 (SHA-256 `0605d405be56e901abe1ea4d35102851dfd260bc28c10307629764ef4b76097d`) was never committed: P4-4a's first run stopped at b.2, before any code, because it asked for `usdjpy_ret`'s summary in O6's design, where `fx_asymmetry` replaces `usdjpy_ret` by `e_pos` and `e_neg`. Version 2 gives O6 those two summaries and writes in the builder's eight other readings of that run; its §10 lists the changes.
> - Resolve and record, for P4-4a (Isaiah, 2026-10-11, on the supervisor's recommendation): where the specification is unclear or cannot be met as written, the builder resolves the point by the reading closest to its purpose and records it in the report, and stops only if the resolution would change what a test asserts, a quantity a row computes, or a rule of the item's message. Whether it becomes standing is decided at P4-4b.

## Test results

- P4-0b: the suite ran inside this item's checkpoint (`checkpoint: P4-0b`): `Ran 285 tests in 337.073s`, `OK (skipped=6)`. Report `reports/P4_reports/p4_0b.txt`.
- P4-2: the suite ran inside this item's checkpoint (`checkpoint: P4-2`): `Ran 285 tests in 301.101s`, `OK (skipped=6)`; it rewrote `reports/B6_coverage.json`, and checkpoint.sh restored it. Report `reports/P4_reports/p4_2.txt`.
- P4-3: the suite ran inside this item's checkpoint (`checkpoint: P4-3`): `Ran 305 tests in 348.129s`, `OK (skipped=6)`; it rewrote `reports/B6_coverage.json`, and checkpoint.sh restored it. Report `reports/P4_reports/p4_3.txt`.
- P4-4p: read-only; no suite run.
- P4-4a: before this record was written, the new file `tests/test_p4_confirm_inference.py` passed on its own (`Ran 23 tests`, `OK`), and so did the static test modules `test_schema`, `test_sim_b5`, `test_docs_d3b` and `test_docs_d6`. The suite runs inside this item's checkpoint (`checkpoint: P4-4a`); its result is in the report `/tmp/p4_4a.txt`, copied at the next checkpoint. Expected: `Ran 328 tests`, `OK (skipped=6)`.

## Test changes

- P4-3: one new test file, `tests/test_p4_sim_full.py`, with 20 tests (P4Q32, P4Q33). No existing test changed. The suite grows from 285 to 305 tests.
- P4-4a: one new test file, `tests/test_p4_confirm_inference.py`, with 23 tests (P4Q35). No existing test changed. The suite grows from 305 to 328 tests.

## Flags

Flags open at the end of Pass 3 stay recorded in `PASS3_STATUS.md`, Flags (closed). Pass 4's:
- F4-1 (carried from P3-8c): `test_docs_d3` and `test_docs_d3b` assert Pass 3's end state (`BLIND_FIT_LOG` 7 lines; `RUN_REGISTRY.jsonl` empty). The dev run's commit changes them by decision (P4Q6).
- F4-2 (carried from P3-8c and the handoffs): DATA_PROVENANCE §4.5 needs the entries of the fifth supervisor chat, of the two supervisor chats that began on 2026-10-08 (with `PASS3_SUPERVISOR_HANDOFF_6_2026-10-08.md` and with `PASS4_SUPERVISOR_HANDOFF_1_2026-10-08.md`), of the M2 derivation chat (its attestation is §10 of `docs/P4_M2_note.md`), of the supervisor chat that began on 2026-10-09 (with `PASS4_SUPERVISOR_HANDOFF_2_2026-10-08.md`) and of the supervisor chat that began on 2026-10-11 (with `PASS4_SUPERVISOR_HANDOFF_3_2026-10-11.md`), and PROJECT_SETUP's chat-uploads line needs updating. Both go in through the documentation kit (P4-7), with their pins moved.
- F4-3 (from `docs/P4_M2_note.md`, Proposition 4): b is only approximately the yen-specific pass-through. Holding `eurusd_ret` fixed does not hold the dollar fixed, so any underpriced dollar-wide channel that the controls do not span loads on `usdjpy_ret`; a channel whose fair value falls when the dollar strengthens, such as the metals cascade, pushes b down. So "b < 0 means overreaction" and "b = 0 means fully priced" need a qualifier, and f inherits the term. A positive b̂ is conservative with respect to the cascade, not with respect to yen-correlated news. H1 as a test is unchanged. For the pre-registration (Pass 5).
- F4-4 (from `docs/P4_M2_note.md`, Proposition 6, and P4Q17 to P4Q19): the documentation kit (P4-7) corrects PLAN §1.4 (the tier-(i) wording, the tier-(iii) row, and the null and equivalence wording) and PLAN §7 (M2 derived; A′(i) and (vi) qualified). P15's "common weight" reading of a₂ = 0, which does not hold as stated, is qualified by a decision in `docs/DECISIONS_P82_onward.md`, and DATA_DICTIONARY's line on `eurusd_ret` ("makes b the yen-specific pass-through") is qualified as approximate.

## Blinding attestation

- P4-0a: no data file opened; committed files read through git only; nothing computed on the dev panel. The snapshot holds the committed tree, in which no data-like file is tracked.
- P4-boot: read-only; no data file opened; no suite run.
- P4-0b: no script of this item opens a data file or computes on the dev panel; the checkpoint's suite reads `panel_dev.csv` only through its structural and target-only tests; `OFILT_RUN_SEALED` unset in every command; no tag created, moved or deleted.
- P4-1: read-only; REPO's files read as text; no module of `ofilt` imported; no data file opened; no suite run.
- P4-2: no script of this item opens a data file or computes on the dev panel; the checkpoint's suite reads `panel_dev.csv` only through its structural and target-only tests; the configuration and the M2 files hold no real-data result (the note's numbers come from its synthetic check, which this item does not run); `OFILT_RUN_SEALED` unset in every command; no tag created, moved or deleted.
- P4-3: under P4Q33, one read-only script (step c.1, run in P4-3's third run, which stopped on its result, and again in its fourth) and one test (`test_dev_panel_kinds_and_guard`) read the dev panel through `io.load_dev` and the firm events through `io.load_events_firm`, each verified by its hash, for their column names, order and dtype kinds only; the test also lets `io.load_dev` register the real targets in the guard's fingerprint registry. No value printed, compared or computed beyond these. No other script of this item opens a data file. The simulator draws every value from seeded generators and reads no file. The checkpoint's suite reads `panel_dev.csv` only through its structural and target-only tests and that test. `OFILT_RUN_SEALED` unset in every command; no tag created, moved or deleted.
- P4-4p: read-only; every Python command ran with `OFILT_DATA_DIR` set to an empty folder, which was still empty at the end; no module of `io` imported and no data file opened; every frame came from the simulator; nothing written in REPO; `OFILT_RUN_SEALED` unset in every command; no tag created, moved or deleted.
- P4-4a: no script of this item opens a data file or computes on the dev panel; the new module reads only the configuration and writes no file; the new test file runs on simulator frames only, never labelled real, with `OFILT_DATA_DIR` set to an empty folder when run on its own; the checkpoint's suite reads `panel_dev.csv` only through its structural and target-only tests and P4-3's `test_dev_panel_kinds_and_guard`; `OFILT_RUN_SEALED` unset in every command; no tag created, moved or deleted.

## Deviations

- P4-0b (recorded at P4-2, from its report's "Deviations and notes", items 1 and 2):
  - A deviation from the standing prompt's Environment rule: one text edit of `/tmp/p4_0b_b2.py` ran as `python3 -` from a heredoc, without the venv activated in that command and without `env -u OFILT_RUN_SEALED`. It replaced two strings in that script before b.2's only run; it read no data and wrote nothing else; `OFILT_RUN_SEALED` was absent from the session. Every later item tells the builder to edit scripts with its file-editing tool.
  - Under the rerun-once rule: a.2's first run stopped in the builder's own helper, whose exactly-one lookup was stricter than the message, which legitimately states the tag sentence twice (steps a.2 and d.3). The fix scoped the lookups to step a, and the second run passed; both runs are in the report. (Corrected at P4-3, Isaiah, 2026-10-11: this line had ended "The cause was the message, not the code", which contradicted P4-0b's report, item 2.)
- P4-2 (recorded at P4-3, from its report's "deviations and notes"):
  - The first run's STOP at b.1 and the rerun under Isaiah's decision: see the Decision log, P4-2 accepted.
  - A deviation in the rerun's step 1: besides the two message files that step names, it did not move the rerun's own files (`/tmp/p4_2_run2*`: the step-0 date capture, written before step 1, and step 1's script and output), which would otherwise have been filed under the first run. The rerun message's list of exceptions was incomplete; the builder's reading kept the two runs' records apart and is accepted.
  - A note: before writing b.2's script, one read-only inline command printed the kit configuration's top-level keys and the shape of three of its sections (Python's json module, under `env -u OFILT_RUN_SEALED` in the venv). It wrote nothing, and it is printed in the report.
- P4-3 (recorded at P4-4a, from its reports):
  - Run 1 (message `0568bbec88c8cb8f8eaba9b6d34b11fcb31e5ebadbe8dff8d13842c46159c1bc`) stopped at a.1, its date gate: the message accepted 2026-10-09 and 2026-10-10, and the paste fell on 2026-10-11. The cause was the supervisor's message; it led to the decision on date gates (Decision log).
  - Run 2 (message `9a79fa80bcbf8edccd18d9c497e9165e017a2968e5422afdbc70d4b6ba5e3d0a`, its dates corrected) stopped at b.1 (`B CHECK: False`): the kit folder `files/pass4/p4_3_kit` did not exist, the two kit files being in `files/pass4` itself. The cause was the supervisor's setup commands, which had not created it.
  - Run 3 (rerun message `88e046ce5ab29d1e727818fc925d51a5bd9f35a0391b098eb072cdc81bc90e3d`) stopped at c.1 (`C1 CHECK: False`): the dev panel's `n225_bars` has kind f, where the specification's Table D, taken from the chat interface's column types, gave i. Corrected by the specification's version 2 (Decision log, P4Q32).
  - Run 4 (rerun message `3142b58bfedcabcd32ef223f549da962cb55ddb0ad60fbff74f4cce55f942928`, under P4-3's message version 2, `db97a0ac994940d91c287997c82fba7dec875be61b89995eac02f8f8b23b537b`) made the checkpoint, with no deviation; its notes are accepted with P4-3 (Decision log).
  - No run changed anything in REPO before it stopped. The builder's handling of the earlier runs' `/tmp` files (step 1 of each rerun, and run 2's own reading where its message was silent) kept each run's records apart and is accepted.
- P4-4p (recorded at P4-4a, from its report's "deviations and notes"):
  - A deviation in step c: the builder did not re-read `inference.py`, `targets.py` and `calib.py` within the item, having read them earlier in the same session; they were unchanged since P3-2b (`inference.py` is C7-hashed) and the tree was clean. Accepted.
  - A note: three extra calls, labelled as such, showed that `exclude` replaces the spec's exclusion flags (Decision log, P4-4p accepted).
- P4-4a, its first run (message `9de0de9c289504666be3bfaa9a827888e1b4bd34eb12669738aafa947b42f24d`): stopped at b.2 before writing any code, on the specification's version 1 (Decision log, P4Q35). The cause was the supervisor's specification. The run changed nothing in REPO; its report is in the second run's.

## Disclosure list

For the pre-registration (Pass 5; P4Q8):
- `docs/DECISIONS_P71_onward.md`, "Carried to the pre-registration" (13 items), by reference.
- Items 1 to 4 of P58's list (`docs/DECISIONS_P58_onward.md`), by reference.
- P32's disclosures (`docs/DECISIONS_P14_onward.md`; PLAN §2.3), by reference.
- The tag `spec-dev-v1`: annotated, tag object `cee3b49e81d16f1f32e546cac9524b209ac1e493` on `f5271c03481b7514a1ec4b7e739fb85fbce8a774`.
- The confirmation configuration `docs/P4_CONFIRM_CONFIG.json`, version 1 (P4-2), SHA-256 `5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd`.
- The M2 derivation, written blind before the dev run (P4Q17; F4-3, F4-4): `docs/P4_M2_note.md` (SHA-256 `a4812e85b6feabc838473ce47a97ce6c4fe88eec7a91762f442cb978b933ec22`), its check `docs/P4_M2_check.py` (SHA-256 `faa4f6c15699658b191618598b9ce2bd18eaa4d6cd6304ba5b1a920bf7dd27a4`) and its prompt `docs/P4_M2_prompt.md` (SHA-256 `594a1a39358e970f9439a98a14430ae36a7244cb037d89f9d61e432649d614a1`).
- P32's tier (iii) is not used (P4Q17).
- Pass 4's computations on the dev panel: P4-3's structural reading under P4Q33 (step c.1's script `/tmp/p4_3_c1.py`, printed in P4-3's report, and the test `test_dev_panel_kinds_and_guard`): the column names, their order and each column's dtype kind, of the dev panel and of the firm events; no value. The kind of `n225_bars` (f, where version 1 of the specification gave i) implies at least one empty value in the dev panel, as the build writes that column; the specification's version 2 follows it.
- The full-schema simulator's specification `docs/P4_SIM_SPEC.md` (P4Q32), version 2, SHA-256 `972b7fd69fcfabbad8ec46347d36ad89ac7d370b55074424174f51d5f688acc4`; its version 1, SHA-256 `6b500f4b30aece4be6d375ada094fc5cfde0f43260f32aba7a086f3db38a8e81`, was never committed.
- The confirmation module's inference specification `docs/P4_CONFIRM_INF_SPEC.md` (P4Q35), version 2, SHA-256 `a7ebb94f003c3b893e96b222b796ea9fda09c849217c526bfdfc8d2b6be51f65`; its version 1, SHA-256 `0605d405be56e901abe1ea4d35102851dfd260bc28c10307629764ef4b76097d`, was never committed.
- P4-4p's probe of the inference calls (report `reports/P4_reports/p4_4p.txt`): simulator frames only; no data file opened.
- The two supervisor chats that began on 2026-10-08 received P4-0a's snapshot, which includes the committed reports of earlier steps that read the dev panel (aggregates and counts only, as committed); their DATA_PROVENANCE §4.5 entries are F4-2.
