# P6_RUN_CRITERIA: the sanction, the gate, the run and the checks after it (P6-1; the pre-registration's §7; P6Q5 to P6Q9)

**Version 1.**
- **Who wrote it, and when.** The first Pass 6 supervisor chat wrote it on 2026-10-12, from handoff H11, before any run it describes.
- **How it is fixed.** P6-0 commits it as `docs/P6_RUN_CRITERIA.md`, before the sanction, and records its SHA-256 in `PASS6_STATUS.md`. No test pins it (P6Q4).
- **Change.** Nothing in it may change once committed. A failed check is a STOP, not an edit.
- **What governs.** `docs/PREREG_v1.md` §7 governs. A difference between this file and §7 is a STOP.
- **Restating.** P6-1's message restates sections 2 to 6 and cites this file by SHA-256. So the gate's criteria are stated in the item's message and fixed in a committed file before the run (§7.3; P6-boot R14).

Names used below:
- **S**, the sanctioned HEAD: the commit P6-0 makes.
- **G**, the gate's commit: the commit `tools/checkpoint.sh "P6-1 part 1"` makes. The run is made at G.
- **D1**: P6-1's date, printed by its first command.

## 1. What runs

- **The code.** The run uses the code and configuration as committed at the tag and unchanged at S. The sanction names three of these files:
  - `tools/p6_confirm_run.py`, `5b3922d79bb0a6d093dccf2aff5f1aaf3f869e8d93c900ac6fb3a6c74eaf5b7f`;
  - `ofilt/drift/confirm_run.py`, `998912c5c9e89ca14fde5e1ca1811ff3f3e4ac65dd36b29b61debffab8e9eaf3`;
  - `docs/P4_CONFIRM_CONFIG.json`, `5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd`.

  The run also uses every other file of the pre-registration's Appendix A, at Appendix A's SHA-256.
- **The command.** It is §7.4's, verbatim. Its SHA-256 as a string (the text between the backticks, UTF-8, no newline) is `1b34bf5c0a8d1f55245963329eaa3ec00bb927801187bbcca5cf6b25c45d2aa9`:

  `env -u OFILT_RUN_SEALED bash -c 'source "$HOME/venvs/ofilt_p2/bin/activate" && cd "$HOME/Desktop/FX_Project/ofilt_pass1" && export OFILT_DATA_DIR="$HOME/Desktop/FX_Project/data" && OFILT_P6_CONFIRM_RUN=P6-1 caffeinate -dimsu python -B tools/p6_confirm_run.py --out reports/P6_runs/confirm'`
- **The outputs.** The command writes `reports/P6_runs/confirm/`: `document.json`, `manifest.json` and `runtime.json`. It also writes `ACCESS_LOG` at REPO's root, and two lines appended to `RUN_REGISTRY.jsonl`.

## 2. The sanction (§7.2; P6Q5)

- **The file.** The sanction is the file `~/Desktop/FX_Project/files/pass6/sanction/P6_SANCTION.txt`, outside REPO. Isaiah creates it with a Terminal command the supervisor gives him after reviewing P6-0's report. Running that command is his sanction.
  - The command refuses to write anything unless HEAD is S, the tree is clean, S is on GitHub, and the three files have the SHA-256 of section 1.
  - It fills `Date:` from `date +%F`.
  - It prints the file's SHA-256.
- **The text.** Exactly nine lines, UTF-8, each ending in a newline, nothing else:

  ```
  SANCTION of the confirmation run, ofilt/drift (Pass 6, item P6-1; docs/PREREG_v1.md §7.2)
  Date: <YYYY-MM-DD>
  By: Isaiah Choi
  HEAD: <S, 40 hex>
  tools/p6_confirm_run.py: 5b3922d79bb0a6d093dccf2aff5f1aaf3f869e8d93c900ac6fb3a6c74eaf5b7f
  ofilt/drift/confirm_run.py: 998912c5c9e89ca14fde5e1ca1811ff3f3e4ac65dd36b29b61debffab8e9eaf3
  docs/P4_CONFIRM_CONFIG.json: 5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd
  Criteria: docs/P6_RUN_CRITERIA.md <the SHA-256 of this file, as PASS6_STATUS.md records it at S>
  I sanction one run of tools/p6_confirm_run.py, by the command of docs/PREREG_v1.md §7.4, at the gate of the criteria file above. Any further run is a dated, labelled deviation that I decide.
  ```

- **The checks (verdict `SANCTION CHECK`).** P6-1 checks the file by script:
  - its nine lines match the form above;
  - `Date:` is a valid calendar date;
  - `HEAD:` is S;
  - the three hashes are section 1's;
  - `Criteria:` names this file's SHA-256 as recorded at S, which also equals `git show S:docs/P6_RUN_CRITERIA.md`'s.
- **The builder's part.** The builder never writes or edits the sanction. P6-1 copies it with `cp -p` to `docs/P6_SANCTION.txt` and checks that the copy is byte-identical.

## 3. The gate (§7.3; P6Q6)

### 3.1 Before the gate's checkpoint (verdict `PRE CHECK`)

- **REPO's state.**
  - HEAD is S.
  - The tree is clean (`git status --porcelain --untracked-files=all` prints nothing).
  - S is on a remote-tracking branch; P6-1's setup script has also checked it with `git ls-remote`.
- **The tags.**
  - `git tag -l` is `pass1-final prereg-v1 spec-dev-v1`.
  - `prereg-v1` is annotated, object `148b742e097c0ed6945992b7707d928ad21b4d37`, on `8341ffd930caea6e0327e8fcac90fc2e34652962`.
- **The logs.**
  - No name starting `ACCESS_LOG` exists in REPO outside `.git`, and `reports/P6_runs/` does not exist.
  - `BLIND_FIT_LOG` has 7 lines and `0cdedae9662221145dd3b9f4baecacc7431d17706d01f6cef19cce10c0f83383`; `RUN_REGISTRY.jsonl` has 2 lines and `9c6cb9c68538215cab8ae5c91f582e695757165bc4de5e033c8c61d49a9f542c`.
- **The environment.** `OFILT_RUN_SEALED` and `OFILT_P6_CONFIRM_RUN` are absent from the session.

### 3.2 The gate's checkpoint (P5Q2 rule 2; P6Q2)

- **What it commits.** P6-1 makes the records of part 1. P6-1's message lists them, and they are exactly these three:
  - `docs/P6_SANCTION.txt`, the sanction's copy;
  - `PASS6_STATUS.md`, from the template P6-1's message gives, recording the sanction and P6-0's acceptance;
  - `reports/P6_reports/p6_0.txt`, P6-0's report.
- **The command.** Then `tools/checkpoint.sh "P6-1 part 1"` runs, in the standing prompt's form, with the background option.
- **What it must give.** `Ran 398 tests` and `OK (skipped=6)`, and a `commit <G>` line. Restoring `reports/B6_coverage.json` is expected (Flag 16).

### 3.3 After the checkpoint, before the command (verdict `GATE CHECK`)

- **G1, the commit.** HEAD is G, the checkpoint's printed commit, and its only parent is S.
- **G2, its files.** `git diff --name-only S G` lists exactly `PASS6_STATUS.md`, `docs/P6_SANCTION.txt` and `reports/P6_reports/p6_0.txt`.
- **G3, the hashes at G.** Each is checked twice: as the working-tree bytes, and as `git show G:<path>`.
  - The three files of section 1 have their SHA-256.
  - All 40 files of Appendix A have the table's SHA-256, the table being parsed from `docs/PREREG_v1.md` at G.
  - `docs/PREREG_v1.md` itself has `79447ba199ce2360fb1fc8c51ae5d0eea3c20ba2645d6167c17ba1e1792f35e6`.
  - This file has the SHA-256 recorded at S.
- **G4, the sanction.** `docs/P6_SANCTION.txt` at G is byte-identical to the sanction file and passes section 2's checks.
- **G5, the tags.** As in 3.1, and `prereg-v1`'s commit is an ancestor of G.
- **G6, the tree.** The tree is clean.
- **G7, the suite.** The checkpoint's output holds `Ran 398 tests`, `OK (skipped=6)` and the commit line of G.
- **G8, the logs.** No `ACCESS_LOG*` name exists in REPO, `reports/P6_runs/confirm` does not exist, and both logs are as in 3.1.
- **G9, the environment.** `OFILT_RUN_SEALED` and `OFILT_P6_CONFIRM_RUN` are absent from the session.
- **G10, the command.** The command text P6-1's message gives has `1b34bf5c0a8d1f55245963329eaa3ec00bb927801187bbcca5cf6b25c45d2aa9`, and so does the one line of `docs/PREREG_v1.md` at G that contains `OFILT_P6_CONFIRM_RUN=P6-1 caffeinate`.
- **G11, the registration.** `PASS5_STATUS.md` at G records `https://osf.io/3mr5h`. This is §7.1's precondition that the registration is filed and recorded.

**The gate.** The command runs only if `SANCTION CHECK`, `PRE CHECK` and `GATE CHECK` are all True, and the checkpoint succeeded. Otherwise the item stops before the panel is requested.

## 4. The command (§7.4; hard rule 3)

- **How it runs.** Once, as the command tool's own command with its background option, verbatim. Nothing else runs in REPO until its completion notice.
- **Its output.** The builder transcribes the captured output and exit status into `/tmp/p6_1_run_output.txt` with the editor.
- **The crash rule (§7.5).**
  - Once `io.load_confirm` has logged GRANTED, the opening counts, whatever follows.
  - If the run fails, or a check of section 5 fails, P6-1 stops. Part 2 does not run, nothing the run wrote is deleted, moved or edited, and Isaiah decides.
  - A refusal before any load (exit 2 with a `REFUSED:` line) writes nothing; it is reported, and the item stops.

## 5. After the command (verdict `POST CHECK`)

- **P1, the exit and the printout.** The exit status is 0. The output holds exactly three path lines, `reports/P6_runs/confirm/<name> <sha256>`, for `document.json`, `manifest.json` and `runtime.json` in that order, and each printed SHA-256 equals the file's.
- **P2, the folder.** `reports/P6_runs/confirm/` holds exactly those three files.
- **P3, the document.** `document.json` parses with Python's `json`, with `NaN` and `Infinity` refused.
  - It has the 71 row ids of `ofilt.drift.confirm_inference.ROW_IDS`, in order.
  - No row is `pending`. Its `mode` is `confirmation` and its `provenance` `confirm_real`.
  - Every row that is `not_estimable` or `not_applicable` is listed with its reason. That is a report, not a failure (P4Q31's contingencies).
- **P4, the manifest.** `manifest.json`'s `mode` and `provenance` equal the document's. Its `config_sha256` is section 1's configuration hash, and its `cost_inputs_sha256`, `analysis_spec_sha256` and `specifications` hashes equal Appendix A's for those files.
- **P5, the access log.**
  - `ACCESS_LOG` is the only `ACCESS_LOG*` name in REPO outside `.git`, at REPO's root.
  - It holds exactly one line: JSON, `result` `GRANTED`, `tag` `prereg-v1`, `head` G.
  - Its `guard` is reported, not a criterion.
- **P6, the registry.** `RUN_REGISTRY.jsonl` has 4 lines.
  - Its bytes up to the second newline have `9c6cb9c68538215cab8ae5c91f582e695757165bc4de5e033c8c61d49a9f542c`, so the two dev lines are untouched.
  - Line 3's `run_id` is `runtime.json`'s `run_ids.main`, and line 4's is `run_ids.m7`. Both lines have `provenance` `confirm_real` and `git_commit` G.
  - Their `git_dirty` values are reported as written; False then True is expected.
- **P7, the tree.** HEAD is still G. `git status --porcelain --untracked-files=all` lists exactly:
  - ` M RUN_REGISTRY.jsonl`;
  - `?? ACCESS_LOG`;
  - `?? reports/P6_runs/confirm/document.json`, `?? reports/P6_runs/confirm/manifest.json` and `?? reports/P6_runs/confirm/runtime.json`.

  With `--untracked-files=no`, it lists only ` M RUN_REGISTRY.jsonl`. That is P86's reading (P6Q8): with the registry excluded, the tracked tree was clean at both forecasting calls.
- **P8, the files that must not change.** `BLIND_FIT_LOG` and the tags are unchanged. The other 39 files of Appendix A have their SHA-256.

**What P6-1's report prints.** These are printed after the run, so they are read only after it:
- `document.json`, `manifest.json`, `runtime.json` and `ACCESS_LOG`, in full;
- the two new registry lines without their `folds` (each with its count of folds);
- every verdict.

## 6. Part 2: §7.6's test changes and the post-run checkpoint (P6Q7; verdict `PART2 CHECK`)

**When.** Part 2 runs only if `POST CHECK` is True.

**The kit.** It is in `~/Desktop/FX_Project/files/pass6/p6_1/tests/`, supervisor-written and sandbox-tested on both sides of a simulated run, and in eight inconsistent post-run states, in which it fails. It is installed with `cp -p`. Each changed test's base must have the SHA-256 below before the install.

| Path | Base SHA-256 (at the tag and at S) | Kit SHA-256 |
|---|---|---|
| `tests/run_state.py` | (new; must not exist) | `cac0340a9486e15fa53be85f4625760d75f742a00bf8d0557699622eea730b24` |
| `tests/test_docs_d3b.py` | `33c975d82230818b81872bce1acaf73a43cbf4c0171e59a8a1240897b658de20` | `40d62035bb764bdeda0d7e0e6aa171cfaa3c34a5d0d963bc8de785301a8ebb96` |
| `tests/test_p4_confirm_forecast.py` | `470fdf23c601ee24a5e5110eac74eb655064181042143aaac9b9f9d1b0c7ef52` | `419658008d1471d59fff52704bab41bc08e1a094fbea869be3559f6fd3af3665` |
| `tests/test_p4_confirm_run.py` | `69d74d062ba87d5fc5d23b919d4c7d4162074ed80c08279efb963a3b15374913` | `792ac94e58f7c84f1dbd50f29f6553298ab24cc0460de96344846e180445abc1` |

**The changes.** They are made under the test-change protocol, with each changed line carrying a comment that cites P6-1 and P6Q7:
- `tests.test_docs_d3b.TestP36.test_lock_amendments_and_nothing_real_before_the_tag`, `tests.test_p4_confirm_forecast.TestConfirmForecast.test_registry_routing` and `tests.test_p4_confirm_run.TestConfirmRun.test_script_synthetic_twice`. Their two registry assertions hold, unchanged, until the run. Once `ACCESS_LOG` exists, `run_state.check_registry_after` asserts instead:
  - the dev run's two `dev_real` lines;
  - then the confirmation run's two `confirm_real` lines, main then m7, with the run ids of `reports/P6_runs/confirm/runtime.json`.
- `tests.test_p4_confirm_run.TestConfirmRun.test_load_confirm_refused_and_logged`. `no_access_log_in_repo()` holds, unchanged, until the run. After it, `run_state.check_access_log_after` asserts:
  - one `ACCESS_LOG`, at REPO's root, with one GRANTED line for `prereg-v1`;
  - its head is the commit of both `confirm_real` lines, descending from the tag and an ancestor of HEAD.

**Recording.** §7.6 pre-states these changes. They are recorded in `PASS6_STATUS.md` twice: under Test changes (old → new), and under Deviations as a dated, labelled entry "pre-stated by the pre-registration's §7.6", which is not a departure from it (P6Q7 as clarified at P6-0).

**The order.**
1. The kit is installed.
2. The three changed modules run on their own: `tests.test_docs_d3b`, `tests.test_p4_confirm_forecast` and `tests.test_p4_confirm_run` give 31 tests, OK.
3. The records of part 2 are written, from the template P6-1's message gives.
4. `tools/checkpoint.sh "P6-1 part 2"` runs, with the background option, and must give `Ran 398 tests` and `OK (skipped=6)`.

**What the commit holds.** Its `git add -A` commits exactly these files:
- the three outputs, `ACCESS_LOG` and `RUN_REGISTRY.jsonl`;
- the four test files;
- `PASS6_STATUS.md`.

**After the commit, by script.**
- The tree is clean.
- The commit's only parent is G.
- `git diff --name-only G HEAD` lists exactly the files above.
- Nothing under `ofilt/`, `tools/`, `spec/` or `build/` changed.
- `ACCESS_LOG` is tracked.
- `BLIND_FIT_LOG` and the tags are unchanged.

If any of this fails, the item stops. Nothing the run wrote is deleted, and Isaiah decides.

## 7. Not part of P6-1

- The prose reading of the results, §7.7's report of every row in §4's wording, follows Pass 6 (the write-up).
- P6-2 records the run's facts (hashes, run ids, `ACCESS_LOG`'s line) in `PASS6_STATUS.md`, the decision file and P92's refresh.
- The forward holdout (§8) has its own plan.
