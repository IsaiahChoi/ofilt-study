# P5-1: the confirmation script and the tag-state tests (P5Q4, P5Q5)

Version 1, 2026-10-12. Written by the first Pass 5 supervisor chat. Unlike Pass 4's specifications, this one comes with its code: the supervisor wrote every file below, and checked them in its sandbox on a copy of the H10 snapshot, with `OFILT_DATA_DIR` set to an empty folder, on both sides of a stand-in `prereg-v1` tag that existed only in that copy. The builder installs the files with `cp -p`, checks them by SHA-256, runs them, and commits them at P5-1's checkpoint. The pre-registration cites the script by its SHA-256.

## 1. Why

- **The confirmation script.** `tools/p4_confirm_run.py` refuses `--source confirm` outright, and its refusal message says the confirmation run is Pass 6's. P13(c) says the confirmation panel "is opened once, by the pre-registered script", and that any later change to code is a dated, labelled deviation. So the script that opens the panel is written and tested before the tag, and the pre-registration names it (P5Q5).
- **The tag-state tests.** Four tests fail once `prereg-v1` is an ancestor of HEAD: P5-boot's c.2, TAGDEP MATCH True; reproduced in the supervisor's sandbox. Fixing them after the tag would itself be a code change after the pre-registration. So they assert both sides of the tag before it is made, and the side with the tag present is exercised beforehand on throwaway repositories (P5Q4).

## 2. Files

| Path | Kind | Section |
|---|---|---|
| `tools/p6_confirm_run.py` | new | 3.1 |
| `tests/test_p6_confirm_run.py` | new (7 tests) | 3.2 |
| `tests/tag_state.py` | changed (helper; not a test module) | 4.1 |
| `tests/test_p5_tag_state.py` | new (5 tests) | 4.2 |
| `tests/test_docs_d3.py`, `tests/test_docs_d3b.py`, `tests/test_io.py`, `tests/test_p4_confirm_run.py` | changed, under the test-change protocol | 5 |

Unchanged, byte for byte (P5Q5, P5Q8): `tools/p4_confirm_run.py`, `ofilt/drift/confirm_run.py` and every other file under `ofilt/`, the configuration, the frozen spec and the cost inputs. The suite grows from 386 to 398 tests; the six skips are unchanged.

## 3. The confirmation script

### 3.1 `tools/p6_confirm_run.py`

- Command: `python tools/p6_confirm_run.py --out DIR`.
- It refuses, writes nothing and returns 2, in this order:
  1. if DIR exists;
  2. unless `OFILT_P6_CONFIRM_RUN=P6-1` is set (the run's own sanction, set only in Pass 6 on Isaiah's sanction);
  3. if `io.ACCESS_LOG_PATH` exists. Any earlier request of the confirmation panel, granted or denied, leaves that file, so a second run is refused in code. A second run is a dated, labelled deviation, which Isaiah decides.
- Then, in `_confirm_frames`, it loads in order `io.load_dev()`, `io.load_events_firm()` and `io.load_confirm()`.
  - The guard of `io.load_confirm` refuses until `prereg-v1` is an ancestor of HEAD (`AccessDenied`, logged DENIED).
  - The dev files are loaded first, so a failure there happens before the confirmation panel is requested.
- It assembles the document with `confirm_run.build_document(dev, events, confirm)` and writes it with `confirm_run.write_outputs`. It prints each output file's path and SHA-256, and returns 0.
- Every other failure raises.
- It imports only `argparse`, `os`, `sys`, `pathlib.Path` and `ofilt.drift`'s `confirm_run` and `io`. It contains neither tag's name (`test_docs_d3b` scans `tools/`), nor `sim_full`.
- The manifest's `output` field is `confirm_run`'s constant, "the confirmation document of Pass 4 (P4Q35 to P4Q39)". `confirm_run.py` stays byte-identical, so the confirmation's manifest keeps that wording: it names the code's origin, not the run.

### 3.2 `tests/test_p6_confirm_run.py` (exactly these 7 tests)

Seeds: the spec seed + 8,700,000 + k. setUpModule patches `registry.SYNTHETIC_PATH`, `registry.REAL_PATH` and `io.ACCESS_LOG_PATH` to a temporary folder (the last never created). M7 is P4-4b2's zero stand-in.

1. `test_constants_and_texts`: checks four things.
   - The variable and value are `OFILT_P6_CONFIRM_RUN` and `P6-1`, distinct from the dev run's, and `EXIT_REFUSED` is 2.
   - The variable is absent from the suite's environment.
   - The script's source names neither tag, nor `sim_full`, `OFILT_RUN_SEALED` or `DATA_DIR`.
   - The sanction refusal text.
2. `test_refuses_without_sanction`: the variable absent, empty, `P6`, `P4-6` or `p6-1`. Return 2, no loader called (all three are recorders), no output folder, the exact refusal printed.
3. `test_refuses_when_access_log_exists`: an `ACCESS_LOG` that is empty, holds a DENIED line, or holds a GRANTED line. Return 2, no loader called, the log unchanged, the exact refusal printed.
4. `test_refuses_existing_out`: return 2, no loader called, the folder left empty.
5. `test_guard_refuses_without_the_tag`: the sanction set; the dev loaders replaced by recorders; the real `io.load_confirm` under `tag_state.io_blinded()`, with `io.ACCESS_LOG_PATH` and `io.DATA_DIR` temporary.
   - It raises `io.AccessDenied` after the dev loaders were called.
   - The log holds exactly one line, DENIED for `prereg-v1`.
   - No output folder is written, and the data folder stays empty.
6. `test_same_documents_as_the_p4_script`, the equivalence check that stands in for P13(b) on the new path.
   - One simulation is run through `tools/p4_confirm_run.py --source synthetic`, and the same frames through this script with its loaders replaced by stand-ins that return them.
   - Both return 0, and `confirm_run.documents_equal` holds: `document.json` and `manifest.json` are byte-identical.
   - The script prints its three files' paths and SHA-256, and the real registry and the ACCESS_LOG are untouched.
7. `test_sources`, by `ast`:
   - the import list is as section 3.1 gives it;
   - the three loaders are called, in that order and without arguments, only inside `_confirm_frames`;
   - `_confirm_frames`' first two statements are the sanction check and the ACCESS_LOG check, each an `if` that ends in `return` and calls no loader;
   - `_confirm_frames` is called once, in `main`, after `main`'s check of `--out`;
   - nothing opens, reads, writes or removes a file in the script itself.

## 4. The tag-state helpers

### 4.1 `tests/tag_state.py`

The existing helpers are unchanged in behaviour; `_git` now calls `_git_at(ROOT, …)`. Added:
- the constants `SPEC_TAG`, `PREREG_TAG`, `CONFIG_PATH`, `CONFIG_SHA256` (the configuration, version 1), `PREREG_PATH` (`docs/PREREG_v1.md`) and `PREREG_SHA256`.
  - `PREREG_SHA256` is `None` at P5-1. P5-2 sets it to the document's SHA-256 when it installs the document, as a documentation pin.
  - Until then `check_prereg_tag` fails. So a tag made before the pin fails the suite.
- `prereg_tagged(root=ROOT)`.
- `check_prereg_tag(tc, root=ROOT, prereg_sha256=None)`. It checks four things:
  - the tag is annotated;
  - its commit is an ancestor of HEAD;
  - `spec-dev-v1`'s commit is an ancestor of the tag's commit;
  - at the tag, the frozen spec, the configuration and the pre-registration have their pinned SHA-256.
- `io_blinded()`: as `blinded()`, and `io._GUARD_REPO` and `io._external_check_access` are patched to the same throwaway repository and None. It patches neither `io.ACCESS_LOG_PATH` nor `io.DATA_DIR`; the caller does (P5Q3).
- `tag_state` now imports `ofilt.drift.io` at module level. No test checks `sys.modules`.

### 4.2 `tests/test_p5_tag_state.py` (exactly these 5 tests)

The throwaway repositories hold copies of REPO's frozen spec and configuration and a stand-in document.
1. `test_constants`:
   - the tag names agree with `blind` and `io`;
   - the spec and the configuration in REPO have the pinned SHA-256, and the configuration is version 1;
   - `PREREG_PATH`;
   - `PREREG_SHA256` is None. At P5-2 this becomes the document's SHA-256, a documentation pin.
2. `test_prereg_absent_and_present`: `prereg_tagged` is False and then True. `check_prereg_tag` passes on a correct tag (annotated, after `spec-dev-v1`, an ancestor of HEAD, the right files).
3. `test_check_prereg_tag_refuses`: `check_prereg_tag` fails (AssertionError) for each of these:
   - a lightweight tag;
   - a tag off HEAD's history;
   - a tag before `spec-dev-v1`;
   - no `spec-dev-v1`;
   - a changed configuration at the tag;
   - no tag;
   - a wrong pin;
   - no pin;
   - a tag on a commit without the document.
4. `test_io_blinded_refuses_whatever_the_guard_repository_holds`: a stand-in for REPO with both tags grants `blind`'s check. Under `io_blinded()`, `io.load_confirm` refuses (DENIED logged to a temporary file, the data folder left empty), and the patches are restored afterwards.
5. `test_repo_state_both_sides`: REPO's own state.
   - `prereg_tagged()` equals `blind._tag_ok("prereg-v1")`.
   - With the tag present, `spec-dev-v1` exists too and `check_prereg_tag` passes.
   - The document exists in REPO if and only if its pin is set.

## 5. The four test changes (test-change protocol)

Each changed line carries a comment citing P5-1 (P5Q4). The state on both sides of `prereg-v1`, as P3-8b did for `spec-dev-v1`:

| Test | Was | Now |
|---|---|---|
| `test_docs_d3::TestP29Blinding::test_tag_gates` | `assertNotIn("prereg-v1", tags)`; `confirm_real` always refused; the `['prereg-v1']` refusal whenever `spec-dev-v1` exists | with the tag present, it follows `spec-dev-v1` and `check_prereg_tag` passes; `confirm_real` granted exactly when both tags exist; the `['prereg-v1']` refusal checked when only `spec-dev-v1` exists |
| `test_docs_d3b::TestP36::test_tag_semantics_as_implemented` | `assertFalse(B._tag_ok("prereg-v1"))` | `B._tag_ok("prereg-v1") == TS.prereg_tagged()`; with the tag present, `check_prereg_tag` passes |
| `test_io::TestLoadConfirm::test_denied_and_logged` | REPO's own guard, which refuses only while REPO lacks the tag | `io._GUARD_REPO` patched to a throwaway repository without `prereg-v1` (`make_temp_repo`) and `io._external_check_access` to None; assertions unchanged |
| `test_p4_confirm_run::TestConfirmRun::test_load_confirm_refused_and_logged` | as above | `tag_state.io_blinded()` added to its patches; `tag_state` imported; assertions unchanged |

## 6. What the supervisor ran (sandbox, synthetic only)

On a copy of the H10 snapshot committed to a throwaway git repository, with `pass1-final` and an annotated stand-in `spec-dev-v1` on that commit, and `OFILT_DATA_DIR` set to an empty folder:
- Before the changes, with a stand-in `prereg-v1`: the four tests failed (2 failures, 2 errors with FileNotFoundError on temporary paths), as P5-boot's R9 read.
- After the changes, without the tag: the two new modules, `test_docs_d3`, `test_docs_d3b` and `test_io`'s `TestGuardFallback` and `TestLoadConfirm` gave 25 tests, OK (skipped=1); all of `test_p4_confirm_run` gave 12 tests, OK.
- After the changes, with a simulated P5-2 (a stand-in document, its pin set, `test_p5_tag_state`'s first test moved to the pin) and a stand-in annotated `prereg-v1`: the same modules, plus `test_p4_confirm_run`'s tests 6 and 8, gave 27 tests, OK (skipped=1).
- The data folder stayed empty throughout, and no ACCESS_LOG appeared in the copy. The stand-in tags existed only in that copy, which the sandbox discards.
