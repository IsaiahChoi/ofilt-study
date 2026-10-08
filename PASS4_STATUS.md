# PASS4_STATUS: the dev first look and the P13(b) dry run

Standing prompt: `files/pass4/PASS4_BUILDER_PROMPT_2026-10-08.md` (SHA-256 `96327904ec55a1de5ad4f51b1cc27fc9b447b9b124a05243400523835e47984d`), adopted by the P4-boot paste. `PASS3_STATUS.md` is closed (P4Q8).

## Progress

| Item | Status | Notes |
|---|---|---|
| Pass 4 | in progress | The dev first look and the P13(b) dry run (PLAN §8, row 4). |
| P4-0a P3-9 accepted; the /tmp records kept; the snapshot staged for the supervisor chat | done; accepted by Isaiah 2026-10-08 | Run under the Pass 3 prompt; no commit. Report `reports/P4_reports/p4_0a.txt`. |
| P4-boot a new builder session; the standing prompt found by its hash | done; accepted by Isaiah 2026-10-08 | Read-only; no commit. Report `reports/P4_reports/p4_boot.txt`. |
| P4-0b Pass 4 opened; P3-8c, P3-9, P4-0a and P4-boot accepted; reports copied | done | `checkpoint: P4-0b`. Report `/tmp/p4_0b.txt`, copied at the next checkpoint; planned STOP: the supervisor reviews the report, then P4-1. |

## Next action

The supervisor reviews P4-0b. Then P4-1, the read-only audit of every pre-registered output and robustness row (P4Q4).

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

## Test results

- P4-0b: the suite runs inside this item's checkpoint (`checkpoint: P4-0b`). Its result is in the report `/tmp/p4_0b.txt`, copied at the next checkpoint. Expected: `Ran 285 tests`, `OK (skipped=6)`.

## Test changes

None in Pass 4 so far.

## Flags

Flags open at the end of Pass 3 stay recorded in `PASS3_STATUS.md`, Flags (closed). Pass 4's:
- F4-1 (carried from P3-8c): `test_docs_d3` and `test_docs_d3b` assert Pass 3's end state (`BLIND_FIT_LOG` 7 lines; `RUN_REGISTRY.jsonl` empty). The dev run's commit changes them by decision (P4Q6).
- F4-2 (carried from P3-8c and the handoff): DATA_PROVENANCE §4.5 needs the entries of the fifth supervisor chat and of the supervisor chat that began on 2026-10-08 with `PASS3_SUPERVISOR_HANDOFF_6_2026-10-08.md`, and PROJECT_SETUP's chat-uploads line needs updating. Both go in through the documentation kit (P4-7), with their pins moved.

## Blinding attestation

- P4-0a: no data file opened; committed files read through git only; nothing computed on the dev panel. The snapshot holds the committed tree, in which no data-like file is tracked.
- P4-boot: read-only; no data file opened; no suite run.
- P4-0b: no script of this item opens a data file or computes on the dev panel; the checkpoint's suite reads `panel_dev.csv` only through its structural and target-only tests; `OFILT_RUN_SEALED` unset in every command; no tag created, moved or deleted.

## Deviations

None in Pass 4 so far.

## Disclosure list

For the pre-registration (Pass 5; P4Q8):
- `docs/DECISIONS_P71_onward.md`, "Carried to the pre-registration" (13 items), by reference.
- Items 1 to 4 of P58's list (`docs/DECISIONS_P58_onward.md`), by reference.
- P32's disclosures (`docs/DECISIONS_P14_onward.md`; PLAN §2.3), by reference.
- The tag `spec-dev-v1`: annotated, tag object `cee3b49e81d16f1f32e546cac9524b209ac1e493` on `f5271c03481b7514a1ec4b7e739fb85fbce8a774`.
- The confirmation configuration's SHA-256: pending (P4-2).
- Pass 4's computations on the dev panel: none so far.
- The supervisor chat that began on 2026-10-08 received P4-0a's snapshot, which includes the committed reports of earlier steps that read the dev panel (aggregates and counts only, as committed); its DATA_PROVENANCE §4.5 entry is F4-2.
