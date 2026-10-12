# PASS6_STATUS: the confirmation run

Standing prompt: `files/pass6/PASS6_BUILDER_PROMPT_2026-10-12.md` (SHA-256 `2dfbdbb76897a1062a3fbc5fef42225851c6559fcb1548fbc50952a744e39121`), adopted by the P6-boot paste. `PASS5_STATUS.md` is closed (P6Q10).

## Progress

| Item | Status | Notes |
|---|---|---|
| Pass 6 | in progress | The confirmation run (PLAN §8, row 6; the pre-registration's §7). |
| P6-boot: a new builder session; the standing prompt found by its hash; read-only orientation | done; accepted by Isaiah 2026-10-12 | Read-only; no commit. Report `reports/P6_reports/p6_boot.txt`. |
| P6-0: P5-4 and P6-boot accepted; Pass 6 opened; P6Q1 to P6Q13 and their clarifications; the run's criteria | done; accepted by Isaiah 2026-10-12 | `records: P6-0` (`cd2344e8a42f58dc5c3edd7e9a17a1a558445fbe`), a records-only commit after the documentation modules (P6Q2); the commit the sanction names. Report `reports/P6_reports/p6_0.txt`. |
| P6-1: the sanction, the gate's checkpoint and the run (part 1); §7.6's test changes and the post-run checkpoint (part 2) | in progress | Part 1's checkpoint, `checkpoint: P6-1 part 1`, is the gate's commit G, at which the run is made (`docs/P6_RUN_CRITERIA.md` §3). Part 2 follows only if every post-run check holds. |
| P6-2: decisions P93 onward; P92's refresh; Pass 6 closed | to do | Records and documentation pins, after the documentation modules. |

## Next action

The gate's checkpoint (`checkpoint: P6-1 part 1`) is the commit at which the confirmation run is made, under `docs/P6_RUN_CRITERIA.md` §3 to §5 and the sanction `docs/P6_SANCTION.txt`. Part 2 follows only if every post-run check holds.

## Decision log

> - **P5-4 accepted** (Isaiah, 2026-10-12, on the supervisor's recommendation; recorded by the P6-0 paste).
>   - The commit: `records: P5-4 (P5-3 accepted; the OSF registration; P5Q19; decisions P88 to P92; Pass 5 closed)`, `6775d6ed737a5c57cb686ade28d11f30a99ebfe8`, parent `41f5de3e893fc833bc6a2c5323859ff405c30f14`. It was made with `git commit` after the seven documentation modules (26 tests, `OK (skipped=1)`).
>   - It was reviewed by the Pass 5 supervisor chat and again by the Pass 6 supervisor chat:
>     - every verdict True (A2_ENV, A3, A4, B1, B2, C, D, E), and no deviation;
>     - the commit holds exactly `PASS5_STATUS.md`, `docs/DECISIONS_P88_onward.md` and `reports/P5_reports/p5_3.txt`.
>   - `PASS5_STATUS.md` was `7941a9a21574620e3d4fe58f1a13e6dd49f235da460545c936e6806cb5b07f88`, recomputed by the Pass 5 supervisor.
>   - Report `reports/P5_reports/p5_4.txt`, SHA-256 `8c817e02e3b2f49f78226196b393724a37d1a4be07b0a4705ba45742c84ea0c4` (1,061 lines). It is identical to the copy kept in `files/pass5_tmp_keep/p5_4_final/` and to `/tmp/p5_4.txt` (P6-boot a.4).
> - **`PASS5_STATUS.md` closed** (P6Q10; by the P6-0 paste). It is never edited again.
> - **The Pass 6 standing prompt adopted** (Isaiah, 2026-10-12, on the supervisor's recommendation; by the P6-boot paste).
>   - `files/pass6/PASS6_BUILDER_PROMPT_2026-10-12.md`, SHA-256 `2dfbdbb76897a1062a3fbc5fef42225851c6559fcb1548fbc50952a744e39121`, written by the Pass 6 supervisor chat from handoff H11, with P6Q1 to P6Q13 below.
>   - The Pass 5 prompt is retired.
> - P6Q1 (Isaiah, 2026-10-12, on the supervisor's recommendation): the items.
>   - P6-boot is read-only. P6-0 is records, and the criteria file.
>   - Isaiah's sanction comes next.
>   - P6-1 is part 1 (the gate's checkpoint and the run) and part 2 (§7.6's test changes and the post-run checkpoint).
>   - P6-2 is the records and P92's refresh, and closes Pass 6.
>   - The run is item P6-1, matching the script's sanction value `OFILT_P6_CONFIRM_RUN=P6-1`.
>   - Not chosen: H11's numbering (the run as P6-2), and a separate post-run item.
> - P6Q2 (Isaiah, 2026-10-12): checkpoints only at critical junctures (P5Q2 continued).
>   - In Pass 6 the full suite runs twice, both inside P6-1: the gate's checkpoint, right before the run, and the post-run checkpoint.
>   - P6-0 and P6-2 commit after the documentation modules.
> - P6Q3 (Isaiah, 2026-10-12, on the supervisor's recommendation): the confirmation panel and the confirmation path.
>   - Until the run: P5Q3 as clarified.
>   - The run: once, by §7.4's command verbatim, after the sanction and the gate.
>   - After the run: P5Q3's test conditions again; `tools/p6_confirm_run.py` is never run again.
>   - No sealed fit (`BLIND_FIT_LOG` stays at 7 lines).
> - P6Q4 (Isaiah, 2026-10-12, on the supervisor's recommendation): before the run (§7.1).
>   - No file of code or tests, and no file of Appendix A, changes.
>   - Records, reports and new documents, pinned by no test, may be added.
>   - P92's refresh waits until after the run.
> - P6Q5 (Isaiah, 2026-10-12, on the supervisor's recommendation): the sanction (§7.2).
>   - Isaiah's dated text, naming this item's commit and the SHA-256 of the script, the assembler and the configuration, saved outside REPO by his own command.
>   - The builder never writes it. The gate reads it by script, and P6-1 copies it into REPO.
> - P6Q6 (Isaiah, 2026-10-12, on the supervisor's recommendation): the gate and the run's commit (§7.3; P4-5/6's model).
>   - The gate's checkpoint commits only the sanction's copy and the records of part 1. Its commit, whose only parent is the sanctioned HEAD, is the commit at which the run is made.
>   - The checks before the command are those of `docs/P6_RUN_CRITERIA.md` §3.
>   - Not chosen: a sanction issued after the gate's checkpoint; a suite without a commit.
> - P6Q7 (Isaiah, 2026-10-12, on the supervisor's recommendation): after the run (§7.6).
>   - P6-1 part 2 runs only if every post-run check holds. It installs the kit of §7.6's test changes, fixed by SHA-256 in the criteria file before the run.
>   - The post-run checkpoint commits the outputs, `ACCESS_LOG`, the registry, the tests and the records.
>   - If the run fails after GRANTED, part 2 does not run.
> - P6Q8 (Isaiah, 2026-10-12, on the supervisor's recommendation; P86; F5-3): `git_dirty` is read with `RUN_REGISTRY.jsonl` excluded. The recorded values are reported as written.
> - P6Q9 (Isaiah, 2026-10-12, on the supervisor's recommendation; F5-1): `ACCESS_LOG` is not added to `.gitignore`. It is committed as the record of the opening.
> - P6Q10 (Isaiah, 2026-10-12, on the supervisor's recommendation): records (P5Q7 continued).
>   - This file, and `PASS5_STATUS.md` closed.
>   - Reports copied to `reports/P6_reports/`, and P5-4's to `reports/P5_reports/p5_4.txt`.
>   - Decisions P93 onward in `docs/DECISIONS_P93_onward.md`, at P6-2.
> - P6Q11 (Isaiah, 2026-10-12, on the supervisor's recommendation): P92's refresh, at P6-2, after the run.
>   - It covers PLAN v2.7, DATA_PROVENANCE §4.5, README's status, PROJECT_SETUP's upload list, and the pins of the decision files P88 onward and P93 onward.
>   - Each pin move is a labelled documentation-pin deviation (P13(c)).
> - P6Q12 (Isaiah, 2026-10-12, on the supervisor's recommendation): code placement and resolve-and-record (P5Q8 and P5Q9 continued).
>   - No file under `ofilt/`, `tools/`, `spec/` or `build/` changes in Pass 6.
>   - Under `tests/`, only §7.6's changes (with one new helper module) and P6-2's documentation pins.
>   - Resolve-and-record never applies to the sanction, the gate, a criterion, the run, `ACCESS_LOG` or contact with data.
> - P6Q13 (Isaiah, 2026-10-12, on the supervisor's recommendation): process rules (P5Q10 continued).
>   - No date gates, and the records edits applied twice.
>   - Expected values read by script.
>   - The rerun-once rule for check scripts, never for the run's command.
>
> - **P6-boot accepted** (Isaiah, 2026-10-12, on the supervisor's recommendation; recorded by the P6-0 paste).
>   - Read-only. Message `b2fc20e5ae6b637de91768c28d2363300889cce8c51ac61043f2186be6637688`, at `6775d6ed…`.
>   - Every verdict True: A2_ENV, A3, A4, A5, A6 and ACCESSDEP MATCH.
>     - REPO's 253 tracked files equal the H11 manifest byte for byte.
>     - All 40 rows of Appendix A match in REPO and at `prereg-v1`.
>     - The run command is identical in the pre-registration and the standing prompt (`1b34bf5c…`).
>     - P5-4's 31 `/tmp` files are kept and match its report.
>   - ACCESSDEP MATCH True: the builder's own reading found the same four tests as the supervisor's reading and sandbox check.
>   - Accepted with it: its readings R1 to R21 and notes N1 to N6. There is no deviation.
>   - Report `reports/P6_reports/p6_boot.txt`, SHA-256 `ad5422a0cfb279698359a34c179292866b69a79b8d0d361e0f021d1579b370ca`, the copy kept in `files/pass6_tmp_keep/p6_boot_final/`.
> - **On P6-boot's readings** (Isaiah, 2026-10-12, on the supervisor's recommendation; by the P6-0 paste):
>   - **Hard rule 1 clarified (R11).** A "dev value" is a result of the dev first look, or any quantity relating a predictor to a target on dev: `reports/P4_runs/`, and the pre-registration's §3, §4 and §9.
>     - The frozen spec's predictor-only parameters quoted in §2 are not dev values in that sense. They are the high-RV threshold (the dev median of RV per bar) and the FX winsorisation quantiles.
>     - P6-boot's reading of them is recorded in the Disclosure list.
>   - **P6Q7 clarified (R12).** §7.1 counts any change to code or tests after the tag as a deviation, and §7.6 pre-states the change of the four tests.
>     - So that change is recorded twice: under Test changes, and under Deviations as a dated, labelled entry "pre-stated by the pre-registration's §7.6". That entry is not a departure from the pre-registration.
>     - P6-2's documentation pins are labelled deviations that are not pre-stated (P6Q11).
>     - This supersedes P6Q7's words "recorded as such, not as deviations".
>   - **P6Q5 and P6Q6 confirmed (R13).** The sanction's HEAD is HEAD when the sanction is written, this item's commit. The run is made at the gate's commit, its only child, under the checks of `docs/P6_RUN_CRITERIA.md` §3.
>   - **§7.3 (R14).** P6-1's message restates the gate's criteria and cites `docs/P6_RUN_CRITERIA.md` by SHA-256. So the criteria are stated in the item's message and fixed in a committed file before the run.
>   - **P6Q3's wording (R15).** "The only one that reaches REPO's guard" means `io`'s guard. `blind`'s tag gate reads REPO's tags in the suite and in the run's provenance check, as it always has.
> - **The run's criteria** (Isaiah, 2026-10-12, on the supervisor's recommendation; P6Q5 to P6Q9; by the P6-0 paste).
>   - `docs/P6_RUN_CRITERIA.md`, version 1, SHA-256 `ac973a1e6da258c0e48c4296ff83f0103c3a6dd13ad08d4c258b7844a4f902a0`. The supervisor chat wrote it before the run; this item commits it; no test pins it (P6Q4).
>   - It fixes the sanction's form, the gate, the post-run checks and part 2.
>   - Its §6 fixes, by SHA-256, the kit of §7.6's test changes: `tests/run_state.py` (new) and three changed test modules. The kit is placed in `files/pass6/p6_1/tests/` and installed only at P6-1 part 2.
>
> - **P6-0 accepted** (Isaiah, 2026-10-12, on the supervisor's recommendation; recorded by the P6-1 paste).
>   - The commit: `records: P6-0 (P5-4 and P6-boot accepted; Pass 6 opened; P6Q1 to P6Q13 and their clarifications; the run's criteria)`, `cd2344e8a42f58dc5c3edd7e9a17a1a558445fbe`, parent `6775d6ed737a5c57cb686ade28d11f30a99ebfe8`. Message `a2bc44883ce3915f6f7f0cf8017200fe00ffc5419746c02a9e9b9d4c80302109`.
>   - Every verdict True (A2_ENV, A3, A4, B1, B2, C, D, E). The commit adds exactly `PASS6_STATUS.md`, `docs/P6_RUN_CRITERIA.md`, `reports/P5_reports/p5_4.txt` and `reports/P6_reports/p6_boot.txt`; nothing under `ofilt/`, `tools/`, `tests/`, `spec/` or `build/` changed, and all 40 files of Appendix A are unchanged.
>   - The documentation modules gave 26 tests, `OK (skipped=1)`. `PASS6_STATUS.md` was `2b6942cd51abe4b69c13967342f7efe2e0b2c9b62dff5d38fa62a942c8d9e1c6`, recomputed by the supervisor.
>   - Accepted with it: its readings R1 to R16 and notes N1 to N7. N7: the assembler was rerun once under the rerun-once rule; no check and no verdict changed.
>   - Report `reports/P6_reports/p6_0.txt`, SHA-256 `7efafda407030bd88e552e2c9711e10b13a7ca5e73a5db813cc74e283f102a8e`, the copy kept in `files/pass6_tmp_keep/p6_0_final/`.
> - **On P6-0's readings** (Isaiah, 2026-10-12, on the supervisor's recommendation; by the P6-1 paste). P6-1's message states these readings, each within the criteria file's text; none changes a criterion, and no version 2 is made.
>   - R5: P1's "holds exactly three path lines" means exactly three lines of the path form, in that order. Any other line, such as a library warning, is printed in the report and is not a failure.
>   - R6: besides the editor's transcription, the check compares it with the command tool's own output file, if the tool reports one, and records that file's path and SHA-256.
>   - R7: P3's row ids are `ofilt.drift.confirm_inference.ROW_IDS`, read by importing that module in the post-run check (the import reads no data), and checked equal to the configuration's `rows`.
>   - R13: part 1's order is SANCTION CHECK and PRE CHECK; the three records; the gate's checkpoint; GATE CHECK; the command; POST CHECK.
> - **The confirmation run sanctioned** (Isaiah; P6Q5; `docs/P6_RUN_CRITERIA.md` §2; recorded by the P6-1 paste).
>   - `docs/P6_SANCTION.txt`, SHA-256 `123ad81ecd591796749daa25b8a78c25bdaf18a90dc25bd4f92f5dcd09d83cbe`, dated by its `Date:` line. It is a byte-identical copy of the file Isaiah wrote with his own Terminal command, outside REPO.
>   - It names HEAD `cd2344e8a42f58dc5c3edd7e9a17a1a558445fbe` (P6-0's commit), the SHA-256 of `tools/p6_confirm_run.py`, `ofilt/drift/confirm_run.py` and `docs/P4_CONFIRM_CONFIG.json`, and the criteria file `ac973a1e6da258c0e48c4296ff83f0103c3a6dd13ad08d4c258b7844a4f902a0`.
>   - It sanctions one run of `tools/p6_confirm_run.py`, by the command of the pre-registration's §7.4, at the gate of the criteria file. Any further run is a dated, labelled deviation that Isaiah decides.

## Test results

- P6-boot: read-only; no suite run.
- P6-0: the seven documentation modules (`test_docs_p2`, `test_docs_d3`, `test_docs_d3b`, `test_docs_d4`, `test_docs_d5`, `test_docs_d6`, `test_p5_tag_state`) passed before the records-only commit: 26 tests, `OK (skipped=1)`. No full suite (P6Q2).
- P6-1 part 1: the suite ran inside the gate's checkpoint (`checkpoint: P6-1 part 1`; P5Q2 rule 2), before the run. Its counts are in P6-1's report.

## Test changes

None yet. P6-1 part 2 makes §7.6's changes (P6Q7; `docs/P6_RUN_CRITERIA.md` §6).

## Flags

Flags open at the end of Pass 5 stay recorded in `PASS5_STATUS.md`, Flags (closed). Carried:
- F5-1: `ACCESS_LOG` is not in `.gitignore`. Handled by P6Q9; it closes at P6-1 part 2's commit.
- F5-2: README's status block is stale. It is refreshed at P6-2 (P6Q11).
- F5-3: `git_dirty` is read with the registry excluded (P6Q8). It closes at P6-1.

## Blinding attestation

- P6-boot:
  - Read-only. Files were read as text only from the reading list and the files its N4 names, through `git`, and as bytes for hashing.
  - All 253 tracked files were hashed as bytes, `reports/P4_runs/dev/document.json` among them, and nothing under `reports/P4_runs/` was read as text.
  - `RUN_REGISTRY.jsonl` was only hashed and counted.
  - No module of `ofilt` was imported, no test was run, and no data file was opened, listed or hashed.
  - The pre-registration was read except §3, §4 and §9. Its §2 holds two predictor-only parameters computed on dev (hard rule 1 as clarified).
  - `OFILT_RUN_SEALED` and `OFILT_P6_CONFIRM_RUN` were absent; no tag was created, moved or deleted.
- P6-0:
  - Records only: this file, the criteria file and two reports copied.
  - No data file was opened, nothing was computed on real data, and no full suite ran (P6Q2). The documentation modules read no data.
  - No file of code or tests changed, and no file of Appendix A (P6Q4).
  - `RUN_REGISTRY.jsonl` (2 lines) and `BLIND_FIT_LOG` (7 lines) are unchanged.
  - `OFILT_RUN_SEALED` and `OFILT_P6_CONFIRM_RUN` were unset; no tag was created, moved or deleted.
- P6-1 part 1, up to the command:
  - records only: the sanction's copy, this file and P6-0's report copied; no file of code or tests and no file of Appendix A changed (P6Q4);
  - the gate's checkpoint suite read the dev panel and the event files only through its existing tests; every call of `io.load_confirm` in it lay within P5Q3 as clarified, and no `ACCESS_LOG` appeared;
  - `RUN_REGISTRY.jsonl` (2 lines) and `BLIND_FIT_LOG` (7 lines) unchanged; `OFILT_RUN_SEALED` and `OFILT_P6_CONFIRM_RUN` absent; no tag created, moved or deleted.

## Deviations

- P6-0 (message `a2bc44883ce3915f6f7f0cf8017200fe00ffc5419746c02a9e9b9d4c80302109`; recorded at P6-1): none. Its N1, two scripts corrected with the editor before their first run, was not a rerun. Its N7, the assembler run a second time under the rerun-once rule, changed no check and no verdict. Accepted.
- P6-boot (message `b2fc20e5ae6b637de91768c28d2363300889cce8c51ac61043f2186be6637688`; recorded at P6-0): none. Its N2, a search script corrected with the editor before its first run, was not a rerun.

## Disclosure list

For the write-up. It continues `PASS5_STATUS.md`'s Disclosure list, by reference, which stands in full. Pass 6 adds:
- **The supervisor chat that began on 2026-10-12 with handoff H11.**
  - It read:
    - H11, the H11 snapshot and manifest, and the Project's documents, the dev document among them, by design, as earlier supervisor chats did;
    - `docs/PREREG_v1.md` in full;
    - the reports of P5-4 and P6-boot.
  - It hashed the Project's document copies, not its data files. The chat interface attached the column names, inferred types and row counts of the Project's three CSV files, which were ignored.
  - In its sandbox it ran synthetic tests only, on copies of the snapshot, with `OFILT_DATA_DIR` set to an empty folder and stand-in tags that existed only there:
    - the candidate test modules, on both sides of a simulated run;
    - §7.6's test kit, on both sides and in eight inconsistent post-run states.
  - It never ran `test_docs_d6`, and it opened no data file.
- **The P6-boot builder session.** It saw no dev result. Of the pre-registration it read every section except §3, §4 and §9. Its §2 holds two predictor-only parameters computed on dev (P6-boot R11). Nothing under `reports/P4_runs/` was read as text.
- **The criteria file.** `docs/P6_RUN_CRITERIA.md`, version 1, was written and committed before the run.
- **The P6-0 builder session.** Records only; it saw no dev result and opened no data file (P6-0's Blinding attestation).
- **The sanction.** `docs/P6_SANCTION.txt`, written by Isaiah after the criteria file and before the run.
