# PASS5_STATUS: the pre-registration and the tag `prereg-v1`

Standing prompt: `files/pass5/PASS5_BUILDER_PROMPT_2026-10-12.md` (SHA-256 `0398c3c748d5a34d395306b0023ca287d19a6e0890d67c55207562eb496b7a03`), adopted by the P5-boot paste. `PASS4_STATUS.md` is closed (P5Q7).

## Progress

| Item | Status | Notes |
|---|---|---|
| Pass 5 | in progress | The pre-registration and the tag `prereg-v1` (PLAN §8, row 5). |
| P5-boot a new builder session; the standing prompt found by its hash; read-only orientation | done; accepted by Isaiah 2026-10-12 | Read-only; no commit. Report `reports/P5_reports/p5_boot.txt`. |
| P5-1 P4-7c and P5-boot accepted; Pass 5 opened; P5Q11 to P5Q17; the confirmation script and the tag-state tests | done | `checkpoint: P5-1`, made by its second run; the first stopped before b.1 (Decision log; Deviations). Report `/tmp/p5_1.txt`, copied at P5-2. |
| P5-2 the pre-registration installed and pinned; the tagged-clone rehearsal; the checkpoint Isaiah tags | to do | Full-suite checkpoint, then STOP for the tag. |
| P5-3 the tag verified; the full suite with the tag present; the tag recorded | to do | Full-suite checkpoint. |
| P5-4 decisions P88 onward, PLAN v2.7, README, DATA_PROVENANCE §4.5, PROJECT_SETUP and the upload list; Pass 5 closed | to do | Records-only commits after the documentation tests. |

## Next action

The supervisor drafts `docs/PREREG_v1.md` from P5Q11 to P5Q17. Isaiah reviews it as acting advisor (P5Q11), and P5-2 installs and pins it.

## Decision log

> - P4-7c accepted (Isaiah, 2026-10-12, on the supervisor's recommendation; recorded by the P5-1 paste): `records: P4-7c (P4-7b accepted; P4Q43; DATA_PROVENANCE §4.5, PROJECT_SETUP and the Pass 4 upload list; Pass 4 closed)`, commit `3c37f0aeb27665d7698e2d9a49d77157a811ec87`, made with `git commit` after the four documentation test modules (P4Q43). Its report is reviewed by the supervisor chat that began on 2026-10-11 with H9: every verdict True; the status file reproduced from the kit; no deviation. Report `reports/P4_reports/p4_7c.txt`, SHA-256 `647b4baad6e69fcbfe90be03d366b4eb387b0fd3b8c31530328445a55b1e24f9`, the copy kept in `files/pass4_tmp_keep/p4_7c_final/` (identical to `/tmp/p4_7c.txt`, P5-boot a.5). The full suite on its content runs at P5-1's checkpoint.
> - The Pass 5 standing prompt adopted (Isaiah, 2026-10-12, on the supervisor's recommendation; by the P5-boot paste): `files/pass5/PASS5_BUILDER_PROMPT_2026-10-12.md`, SHA-256 `0398c3c748d5a34d395306b0023ca287d19a6e0890d67c55207562eb496b7a03`, with P5Q1 to P5Q10, below. The Pass 4 prompt is retired.
> - P5Q1 (Isaiah, 2026-10-12, on the supervisor's recommendation): the items.
>   - P5-boot is read-only.
>   - P5-1: the acceptances, `PASS5_STATUS.md`, the confirmation script and the tag-state test changes, at a full-suite checkpoint.
>   - P5-2: the pre-registration installed and pinned and the tagged-clone rehearsal, at a full-suite checkpoint whose commit Isaiah tags.
>   - Then Isaiah creates the annotated tag `prereg-v1` in Terminal and pushes the branch and the tag.
>   - P5-3: the tag verified, the full suite with the tag present, the tag recorded.
>   - P5-4: the records and documents, and Pass 5 closed, by records-only commits.
>   - A message may split or merge items.
> - P5Q2 (Isaiah, 2026-10-12): checkpoints only at critical junctures. A full-suite checkpoint (`tools/checkpoint.sh`) runs only:
>   1. before committing any change to code or tests, beyond documentation pins;
>   2. right before and after any real-data run or sanction gate;
>   3. before creating a tag (and after it, where tests depend on the tag);
>   4. at the close of a pass, if no full suite has run since the last code change.
>
>   Everything else is committed with `git commit` after the documentation test modules that read those files pass (P4Q43's pattern); records-only items may be batched. Each message states which kind of commit it makes.
> - P5Q3 (Isaiah, 2026-10-12, on the supervisor's recommendation): the sealed panel and the confirmation path, in Pass 5 and until Pass 6's own sanction.
>   - Nothing opens, reads, lists, hashes or copies the sealed panel or any file under the data folder; its SHA-256 is AM-04's and is not recomputed.
>   - `io.load_confirm` is called only in tests, and only with `io._GUARD_REPO` pointed at a throwaway repository without the tags (or the function itself replaced by a recorder), `io.DATA_DIR` at an empty temporary folder and `io.ACCESS_LOG_PATH` at a temporary file. From P5-1 on, no test relies on REPO lacking `prereg-v1` for a refusal.
>   - No confirmation run is made.
>   - No sealed fit is made (`BLIND_FIT_LOG` stays at 7 lines), and `RUN_REGISTRY.jsonl` stays at its 2 lines.
> - P5Q4 (Isaiah, 2026-10-12, on the supervisor's recommendation): both sides of the tag, as P3-8b did for `spec-dev-v1`.
>   - Before the tag, every test whose result depends on `prereg-v1`'s presence in REPO is rewritten, under the test-change protocol, to assert both sides of it.
>   - `tests/tag_state.py` gains the `prereg-v1` helpers, tested against throwaway repositories.
>   - Before the tag, the tag-dependent tests run in a temporary clone carrying a local `prereg-v1`, with `OFILT_DATA_DIR` set to an empty folder.
>   - After the tag, the full suite runs in REPO.
> - P5Q5 (Isaiah, 2026-10-12, on the supervisor's recommendation): the confirmation script, written before the tag.
>   - It is a new script under `tools/`, specified at P5-1, so that the pre-registered script is the one that opens the sealed panel (P13(c)) and the pre-registration cites its SHA-256.
>   - It refuses without its own sanction, and the guard refuses it until `prereg-v1`.
>   - `tools/p4_confirm_run.py`, `ofilt/drift/confirm_run.py`, the confirmation modules, `confirm_allowlist.py`, the configuration and the frozen spec stay byte-identical, as the dev run's evidence (P4Q1).
> - P5Q6 (Isaiah, 2026-10-12, on the supervisor's recommendation): the pre-registration document.
>   - It is `docs/PREREG_v1.md`, written by the supervisor as a kit file after Isaiah's decisions and review, installed with `cp -p`, checked by SHA-256 and pinned. The builder never edits its wording.
>   - It cites by path and SHA-256 the frozen spec, the configuration, the specifications, the confirmation code and script, the decision files and the disclosure list.
>   - The commit that holds it, P5-2's checkpoint, is the commit tagged.
>   - Any external registration is Isaiah's, after the tag, and is recorded at P5-4.
> - P5Q7 (Isaiah, 2026-10-12, on the supervisor's recommendation): records.
>   - This file has `PASS4_STATUS.md`'s sections, and its Disclosure list continues Pass 4's.
>   - `PASS4_STATUS.md` is closed at P5-1 and never edited again.
>   - Each Pass 5 report is copied byte for byte to `reports/P5_reports/`, and P4-7c's to `reports/P4_reports/p4_7c.txt`.
>   - Decisions P88 onward go in `docs/DECISIONS_P88_onward.md`, pinned in `tests/test_docs_p2.py` (P5-4).
> - P5Q8 (Isaiah, 2026-10-12, on the supervisor's recommendation): code placement, P4Q2 continued.
>   - An existing file changes only where a message lists the change, and new code goes in new files named by items.
>   - The six C7-hashed files stay byte-identical.
>   - No new file under `ofilt/` or `tools/` contains either tag's name.
>   - A specification's import list is binding.
> - P5Q9 (Isaiah, 2026-10-12, on the supervisor's recommendation): resolve and record (standing since P4-4b1) continues. It never applies to the tag, to a sanction gate, to a criterion or to contact with data; there, any doubt is a STOP.
> - P5Q10 (Isaiah, 2026-10-12, on the supervisor's recommendation): Pass 4's process rules carry over.
>   - There are no date gates.
>   - Records edits are applied twice, undated against a template hash and then dated.
>   - Expected values are read by script.
>   - The rerun-once rule and the report form of the standing prompt apply.
> - P5-boot accepted (Isaiah, 2026-10-12, on the supervisor's recommendation; recorded by the P5-1 paste).
>   - Read-only; message `d8a26f3e2b2b1bbcdff667e1ecf0bd239dfc20cbc5aaf8b406be9a96f19e6d46`; at `3c37f0aeb27665d7698e2d9a49d77157a811ec87`.
>   - Every verdict True (A2_ENV, A3, A4, A5, B1, B2). REPO's 239 tracked files equal the H10 snapshot's manifest byte for byte.
>   - TAGDEP MATCH True: the builder's own reading found the same four tag-dependent tests as the supervisor's.
>   - Accepted with it: its readings R1 to R13 and notes N1 to N7, and its deviations D1 and D2 (Deviations).
>   - Report `reports/P5_reports/p5_boot.txt`, SHA-256 `04a6b6799338225b29fa88b763b6fa037e7fcfd99a072c8114c8691ca9c997d8` (1,631 lines; the kept copy and `/tmp/p5_boot.txt` identical, P5-1 a.4).
> - P5-1's first run (message `299375e6109d1429590475717982c2facbd385943c4dfb69c7820287b2b5e2f8`, 2026-10-12) stopped correctly before b.1. Before any change, it found that two unchanged test modules call `io.load_confirm` outside P5Q3's letter:
>   - `test_io::TestLoadConfirm::test_guard_is_the_only_gate`;
>   - `test_guard_p46::TestConjunctiveGate` (both in Pass 1 and 2's guard tests, P29, P46).
>
>   They use a throwaway guard repository that carries a stand-in `prereg-v1`, to test the grant path, and a `DATA_DIR` that is never created. It found too that the kit's P5-1 attestation ("refuses") would be false. It changed nothing in REPO. The cause was the supervisor's wording of P5Q3, which stated the condition more narrowly than its purpose. P5-1 is rerun in full under the clarification below (its rerun message's SHA-256 is the third line of P5-1's report, `reports/P5_reports/p5_1.txt`); the first run's `/tmp` files are kept in `files/pass5_tmp_keep/p5_1_run1/`.
> - P5Q3 clarified (Isaiah, 2026-10-12, on the supervisor's recommendation; recorded by the P5-1 rerun paste; option (a) of the first run's R7). It supersedes P5Q3's second bullet and governs every later item. P5Q3's other bullets stand.
>   - `io.load_confirm` is called only in tests, and only with `io._GUARD_REPO` pointed at a throwaway repository, never REPO's own guard, or with `io.load_confirm` itself replaced by a recorder.
>   - `io.DATA_DIR` points at a path inside a new temporary folder that holds no data file, whether empty or never created.
>   - `io.ACCESS_LOG_PATH` points at a temporary file.
>   - A throwaway repository may carry stand-in tags, so that the guard's grant path is tested. A grant there reaches only the empty temporary path and raises FileNotFoundError.
>   - No test's refusal relies on REPO's own tags.
>   - The purpose is unchanged: no test can reach the sealed panel or DATA, and no test's outcome depends on whether REPO carries `prereg-v1`.
>   - Not chosen: option (b), changing P29's and P46's guard tests, which already meet the purpose.
> - P5Q11 (Isaiah, 2026-10-12, on the supervisor's recommendation; D1): the pre-registration's form, its external registration and its review.
>   - The document is `docs/PREREG_v1.md` (P5Q6).
>   - After the tag, Isaiah files an embargoed registration on OSF. It holds the document, the tag object and commit, and the document's SHA-256. Its data-status answer states that the sealed panel exists and that its outcome relationship has not been examined, with the sealed fits and the gap-based prior exposure disclosed.
>   - P36 step 6's advisor sign-off: Isaiah acts as advisor, on an advisor-style review written by the supervisor chat. The pre-registration states that it had no independent advisor review. PLAN §8's and README's "advisor sign-off" are read accordingly. This is the decision P36 step 6 needed, made before the tag.
> - P5Q12 (Isaiah, 2026-10-12, on the supervisor's recommendation; D2; closes F4-3 when the document is installed): the reading of b, worded in the pre-registration as the supervisor drafted it.
>   - H1's test is unchanged.
>   - b is approximately the yen-specific pass-through, holding EUR/USD, SPY and COPX fixed.
>   - An underpriced dollar-wide channel the controls do not span also loads on b.
>   - A significant b̂ > 0 is conservative with respect to the metals cascade under S1 to S3, which the text names, but not with respect to yen-correlated news.
>   - A significant b̂ < 0 is reported as a negative loading, not as overreaction.
>   - A null is read against MDE80 = 0.2471, never as full pricing.
>   - f inherits the qualifier.
> - P5Q13 (Isaiah, 2026-10-12, on the supervisor's recommendation; D3): how the dev first look and the readings are stated.
>   - The headline dev numbers appear in a labelled disclosure section, the unfavourable ones included, with the chronology: the configuration (P4-2) and the frozen spec (`spec-dev-v1`) predate the dev run (P4-5/6).
>   - The primary power statement is the binding curve (P79). The dev-centred remark is labelled and second, with its caveat.
>   - The joint reading of a rejected H1 together with equivalence at the primary SESOI is stated in advance: a detectable drift too small to exploit net of costs.
>   - The 2022 f is worded as an estimate with its disclosed calibration caveat (P4Q9).
> - P5Q14 (Isaiah, 2026-10-12, on the supervisor's recommendation; D5): the pre-registration fixes Pass 6's run note. It fixes:
>   - the script and its SHA-256, and the command;
>   - Isaiah's separate sanction after the tag;
>   - a scripted gate modelled on P4-5/6, with full suites before and after the run (P5Q2, rule 2);
>   - that the builder launches the run, and its outputs go to `reports/P6_runs/confirm/`;
>   - the crash rule: once `io.load_confirm` has granted, the opening counts, and any rerun is a dated, labelled deviation reported beside the first result;
>   - that `git_dirty` is read with the registry file excluded (P86);
>   - and that `ACCESS_LOG`, which the run creates in REPO and which the script's one-shot check then reads, is committed as the record of the opening, the tests that forbid it being changed by decision in Pass 6.
> - P5Q15 (Isaiah, 2026-10-12, on the supervisor's recommendation; D6, and the advisor-style points on the script; recorded by the P5-1 paste): the confirmation script `tools/p6_confirm_run.py`, as `docs/P5_CONFIRM_SCRIPT_SPEC.md` (version 1) specifies it.
>   - It refuses an existing `--out`, a missing sanction (`OFILT_P6_CONFIRM_RUN=P6-1`) and an existing `ACCESS_LOG` (the one-shot rule in code).
>   - It loads dev, events and then the confirmation panel, and assembles and writes with `confirm_run`, unchanged.
>   - Its tests (`tests/test_p6_confirm_run.py`, 7) include the equivalence check: the same synthetic frames through this script and through `tools/p4_confirm_run.py` give byte-identical `document.json` and `manifest.json`.
>   - Supervisor-written and sandbox-checked; installed by `cp -p`.
>   - Not chosen: a confirm branch in `tools/p4_confirm_run.py`, which would change the dev run's script.
> - P5Q16 (Isaiah, 2026-10-12, on the supervisor's recommendation; D7; recorded by the P5-1 paste): the tag-state changes, as the specification's sections 4 and 5 give them.
>   - `tests/tag_state.py` gains `prereg_tagged`, `check_prereg_tag` and `io_blinded`, with the pin `PREREG_SHA256` set at P5-2.
>   - `tests/test_p5_tag_state.py` (5) tests them on throwaway repositories.
>   - The four tag-dependent tests assert both sides of `prereg-v1`.
>   - The tagged-clone rehearsal follows at P5-2.
> - P5Q17 (Isaiah, 2026-10-12, on the supervisor's recommendation; D8; P4Q30): the forward holdout.
>   - It evaluates H1 only: b̂, its DK SE, its two-sided p, and whether its sign agrees with the confirmation's.
>   - Its window is the trading days from 2026-03-06 to 2026-09-30.
>   - It is built and run after the confirmation run, under its own sanction, with the Pass 2 build extended and the event calendars extended (FY2025 FULL earnings, the 2026 BoJ meetings), and with the 5706 split checked (ex-date 2026-09-29; P13(a)).
>   - P64's intraday PX_OPEN check sits beside it where the data allow.
>   - It is reported as a sanity check that licenses no claim, and it is never pooled with the confirmation for any claim.

## Test results

- P5-boot: read-only; no suite run.
- P5-1: the new and changed modules passed on their own before the commit (`test_p5_tag_state` 5, `test_p6_confirm_run` 7, `test_docs_d3` 6, `test_docs_d3b` 2, `test_io` 8, `test_p4_confirm_run` 12), and the suite ran inside this item's checkpoint (`checkpoint: P5-1`). Its counts are in the report.

## Test changes

- P5-1 (P5Q15, P5Q16; the test-change protocol; each change carries a comment citing P5-1):
  - `tests/test_docs_d3.py`, `test_tag_gates`. Was: `assertNotIn("prereg-v1", tags)`; `confirm_real` always refused; the `['prereg-v1']` refusal whenever `spec-dev-v1` exists. Now: with `prereg-v1` present, `spec-dev-v1` exists and `check_prereg_tag` passes; `confirm_real` granted exactly when both tags exist; the `['prereg-v1']` refusal checked when only `spec-dev-v1` exists.
  - `tests/test_docs_d3b.py`, `test_tag_semantics_as_implemented`. Was: `assertFalse(B._tag_ok("prereg-v1"))`. Now: `B._tag_ok("prereg-v1") == TS.prereg_tagged()`, and with the tag present `check_prereg_tag` passes.
  - `tests/test_io.py`, `test_denied_and_logged`. Was: REPO's own guard. Now: `io._GUARD_REPO` patched to a throwaway repository without `prereg-v1`, and `io._external_check_access` to None. Assertions unchanged.
  - `tests/test_p4_confirm_run.py`, `test_load_confirm_refused_and_logged`. Was: REPO's own guard. Now: `tag_state.io_blinded()` added to its patches, and `tag_state` imported. Assertions unchanged.
  - `tests/tag_state.py` (a helper, not a test module): the `prereg-v1` helpers and `io_blinded` added; the existing helpers unchanged in behaviour.
  - New: `tests/test_p6_confirm_run.py` (7 tests) and `tests/test_p5_tag_state.py` (5 tests). The suite grows from 386 to 398 tests.

## Flags

Flags open at the end of Pass 4 stay recorded in `PASS4_STATUS.md`, Flags (closed). Pass 5's:
- F4-3 (carried): the pre-registration's wording of b's reading. It is decided by P5Q12 and closes when `docs/PREREG_v1.md` is installed (P5-2).
- F5-1: `ACCESS_LOG` is not in `.gitignore`.
  - The Pass 6 run creates it in REPO.
  - `tools/checkpoint.sh`'s `git add -A` would commit it, and `test_p4_confirm_run`'s test 8 asserts that no name starting `ACCESS_LOG` exists in REPO.
  - P5Q14 fixes its handling for Pass 6's run note.
- F5-2: README's status block is stale (it still names `spec-dev-v1` as next). P5-4 refreshes it.
- F5-3 (from P86): Pass 6's run note reads `git_dirty` with `RUN_REGISTRY.jsonl` excluded (P5Q14).

## Blinding attestation

- P5-boot:
  - read-only; files read as text, through `git` and as bytes for hashing;
  - every tracked file hashed as bytes against the H10 manifest, `reports/P4_runs/dev/document.json` among them, and nothing under `reports/P4_runs/` read as text;
  - `RUN_REGISTRY.jsonl` only hashed and counted;
  - no module of `ofilt` imported, no test run, no data file opened, listed or hashed;
  - `OFILT_RUN_SEALED` absent; no tag created, moved or deleted.
- P5-1:
  - no data file opened and nothing computed on real data by any script of this item;
  - the new and changed tests run on simulator frames and throwaway repositories only;
  - `io.load_confirm` is called only under P5Q3 as clarified. It refuses wherever the throwaway guard repository lacks the tags. It is granted only in throwaway repositories that carry stand-in tags (`test_io`'s `test_guard_is_the_only_gate` and `test_guard_p46`'s `test_both_satisfied_granted`), where it reaches no file and raises FileNotFoundError;
  - the checkpoint's suite reads `panel_dev.csv` only through its existing structural and target-only tests and P4-3's dtype test;
  - `RUN_REGISTRY.jsonl` unchanged (2 lines), `BLIND_FIT_LOG` unchanged (7 lines);
  - `OFILT_RUN_SEALED` unset in every command; no tag created, moved or deleted.

## Deviations

- P5-1, its first run (message `299375e6109d1429590475717982c2facbd385943c4dfb69c7820287b2b5e2f8`): stopped before b.1, changing nothing in REPO; the cause was the supervisor's wording of P5Q3 (Decision log). The builder's reading of the kit before b.1, which the message did not ask for (its R4 and N1), wrote nothing and is accepted. Its report is kept in `files/pass5_tmp_keep/p5_1_run1/` and printed in full in the second run's report.
- P5-boot (message `d8a26f3e2b2b1bbcdff667e1ecf0bd239dfc20cbc5aaf8b406be9a96f19e6d46`; recorded at P5-1, from its report):
  - D1: the first runs of a.2 to b.2 were made before the standing prompt was read. They typed the expected values, printed PASS rather than True in a.2 to a.5, were written by a shell heredoc, and ran Python without `env -u OFILT_RUN_SEALED`, the venv activated or `-B`. Every check passed. Each was rerun once in the prompt's form, with equal results, and both runs are in the report. Accepted, as P4-boot2's was.
  - D2: a.1's two outputs were printed to the session, not saved to a file. They are transcribed in R1. Accepted.

## Disclosure list

For the pre-registration (P5Q13), continuing `PASS4_STATUS.md`'s Disclosure list, by reference, which stands in full. Pass 5 adds:
- The supervisor chat that began on 2026-10-12 with handoff H10:
  - read the H10 snapshot and manifest, the Project's documents and the dev document, which shows the dev first look, by design;
  - hashed the Project's document copies, not its data files; the chat interface attached the column names, inferred types and row counts of `panel_dev.csv`, `events_firm.csv` and `events_boj.csv`, which were ignored;
  - ran, in its sandbox, synthetic tests of the P5-1 kit on a copy of the snapshot, with `OFILT_DATA_DIR` set to an empty folder and stand-in tags that existed only in that copy (`docs/P5_CONFIRM_SCRIPT_SPEC.md`, section 6);
  - no data file was opened, and no real data were computed on.
- The P5-boot builder session: no dev value seen (P5-boot's Blinding attestation).
- The confirmation script's specification `docs/P5_CONFIRM_SCRIPT_SPEC.md`, version 1, and the script `tools/p6_confirm_run.py`, both written after the dev run. The dev run's script and every shared module are unchanged (P5Q5).
