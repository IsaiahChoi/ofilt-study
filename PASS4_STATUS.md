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
| P4-2 P4-0b and P4-1 accepted; P4Q9 to P4Q31; the confirmation configuration; the M2 note | done | `checkpoint: P4-2`. Report `/tmp/p4_2.txt`, copied at the next checkpoint; planned STOP: the supervisor reviews the report, then P4-3. |

## Next action

The supervisor reviews P4-2. Then P4-3, the full-schema simulator and its tests (T3).

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

## Test results

- P4-0b: the suite ran inside this item's checkpoint (`checkpoint: P4-0b`): `Ran 285 tests in 337.073s`, `OK (skipped=6)`. Report `reports/P4_reports/p4_0b.txt`.
- P4-2: the suite runs inside this item's checkpoint (`checkpoint: P4-2`). Its result is in the report `/tmp/p4_2.txt`, copied at the next checkpoint. Expected: `Ran 285 tests`, `OK (skipped=6)`.

## Test changes

None in Pass 4 so far.

## Flags

Flags open at the end of Pass 3 stay recorded in `PASS3_STATUS.md`, Flags (closed). Pass 4's:
- F4-1 (carried from P3-8c): `test_docs_d3` and `test_docs_d3b` assert Pass 3's end state (`BLIND_FIT_LOG` 7 lines; `RUN_REGISTRY.jsonl` empty). The dev run's commit changes them by decision (P4Q6).
- F4-2 (carried from P3-8c and the handoffs): DATA_PROVENANCE §4.5 needs the entries of the fifth supervisor chat, of the two supervisor chats that began on 2026-10-08 (with `PASS3_SUPERVISOR_HANDOFF_6_2026-10-08.md` and with `PASS4_SUPERVISOR_HANDOFF_1_2026-10-08.md`) and of the M2 derivation chat (its attestation is §10 of `docs/P4_M2_note.md`), and PROJECT_SETUP's chat-uploads line needs updating. Both go in through the documentation kit (P4-7), with their pins moved.
- F4-3 (from `docs/P4_M2_note.md`, Proposition 4): b is only approximately the yen-specific pass-through. Holding `eurusd_ret` fixed does not hold the dollar fixed, so any underpriced dollar-wide channel that the controls do not span loads on `usdjpy_ret`; a channel whose fair value falls when the dollar strengthens, such as the metals cascade, pushes b down. So "b < 0 means overreaction" and "b = 0 means fully priced" need a qualifier, and f inherits the term. A positive b̂ is conservative with respect to the cascade, not with respect to yen-correlated news. H1 as a test is unchanged. For the pre-registration (Pass 5).
- F4-4 (from `docs/P4_M2_note.md`, Proposition 6, and P4Q17 to P4Q19): the documentation kit (P4-7) corrects PLAN §1.4 (the tier-(i) wording, the tier-(iii) row, and the null and equivalence wording) and PLAN §7 (M2 derived; A′(i) and (vi) qualified). P15's "common weight" reading of a₂ = 0, which does not hold as stated, is qualified by a decision in `docs/DECISIONS_P82_onward.md`, and DATA_DICTIONARY's line on `eurusd_ret` ("makes b the yen-specific pass-through") is qualified as approximate.

## Blinding attestation

- P4-0a: no data file opened; committed files read through git only; nothing computed on the dev panel. The snapshot holds the committed tree, in which no data-like file is tracked.
- P4-boot: read-only; no data file opened; no suite run.
- P4-0b: no script of this item opens a data file or computes on the dev panel; the checkpoint's suite reads `panel_dev.csv` only through its structural and target-only tests; `OFILT_RUN_SEALED` unset in every command; no tag created, moved or deleted.
- P4-1: read-only; REPO's files read as text; no module of `ofilt` imported; no data file opened; no suite run.
- P4-2: no script of this item opens a data file or computes on the dev panel; the checkpoint's suite reads `panel_dev.csv` only through its structural and target-only tests; the configuration and the M2 files hold no real-data result (the note's numbers come from its synthetic check, which this item does not run); `OFILT_RUN_SEALED` unset in every command; no tag created, moved or deleted.

## Deviations

- P4-0b (recorded at P4-2, from its report's "Deviations and notes", items 1 and 2):
  - A deviation from the standing prompt's Environment rule: one text edit of `/tmp/p4_0b_b2.py` ran as `python3 -` from a heredoc, without the venv activated in that command and without `env -u OFILT_RUN_SEALED`. It replaced two strings in that script before b.2's only run; it read no data and wrote nothing else; `OFILT_RUN_SEALED` was absent from the session. Every later item tells the builder to edit scripts with its file-editing tool.
  - Under the rerun-once rule: a.2's first run stopped in its own helper's exactly-one lookup, because the message restated the tag sentence in step d.3. The fix scoped the lookups to step a, and the second run passed; both runs are in the report. The cause was the message, not the code.

## Disclosure list

For the pre-registration (Pass 5; P4Q8):
- `docs/DECISIONS_P71_onward.md`, "Carried to the pre-registration" (13 items), by reference.
- Items 1 to 4 of P58's list (`docs/DECISIONS_P58_onward.md`), by reference.
- P32's disclosures (`docs/DECISIONS_P14_onward.md`; PLAN §2.3), by reference.
- The tag `spec-dev-v1`: annotated, tag object `cee3b49e81d16f1f32e546cac9524b209ac1e493` on `f5271c03481b7514a1ec4b7e739fb85fbce8a774`.
- The confirmation configuration `docs/P4_CONFIRM_CONFIG.json`, version 1 (P4-2), SHA-256 `5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd`.
- The M2 derivation, written blind before the dev run (P4Q17; F4-3, F4-4): `docs/P4_M2_note.md` (SHA-256 `a4812e85b6feabc838473ce47a97ce6c4fe88eec7a91762f442cb978b933ec22`), its check `docs/P4_M2_check.py` (SHA-256 `faa4f6c15699658b191618598b9ce2bd18eaa4d6cd6304ba5b1a920bf7dd27a4`) and its prompt `docs/P4_M2_prompt.md` (SHA-256 `594a1a39358e970f9439a98a14430ae36a7244cb037d89f9d61e432649d614a1`).
- P32's tier (iii) is not used (P4Q17).
- Pass 4's computations on the dev panel: none so far.
- The two supervisor chats that began on 2026-10-08 received P4-0a's snapshot, which includes the committed reports of earlier steps that read the dev panel (aggregates and counts only, as committed); their DATA_PROVENANCE §4.5 entries are F4-2.
