# P6_RUN2_CRITERIA: the second attempt at the confirmation run (D2; P6-1d; the pre-registration's §7)

**Version 1 of the second criteria file.**
- **Who wrote it, and when.** The Pass 6 supervisor chat, on 2026-10-12. It was written after the first request failed and before the second.
- **How it is fixed.** P6-1c commits it as `docs/P6_RUN2_CRITERIA.md` and records its SHA-256 in `PASS6_STATUS.md`. No test pins it.
- **Change.** Nothing in it may change once committed. A failed check is a STOP, not an edit.
- **What governs.** `docs/PREREG_v1.md` §7 and D2's seven conditions (`PASS6_STATUS.md`, Decision log) govern. A difference between them and this file is a STOP.
- **Restating.** P6-1d's message restates sections 2 to 6 and cites this file by SHA-256.
- **What it supersedes.** It supersedes `docs/P6_RUN_CRITERIA.md` for the second attempt only. That file stays the record of the first.

**What the first request did.** It was granted at G1 = `221507d01547869376e73cde51c20b86892bed95`. Then `io` failed with `FileNotFoundError` before it opened the sealed panel, because the file was not in the data folder. No byte was read and nothing was computed.

**What D2 changes for the second attempt:**
- the first request's `ACCESS_LOG` is renamed, its bytes unchanged, to `reports/P6_runs/attempt1/ACCESS_LOG`;
- the revised kit of §7.6's test changes is installed before the run;
- one stat-only presence check of the sealed panel is added;
- Isaiah copies the sealed panel into the data folder, verifies its SHA-256, and gives a second sanction.

The code, the configuration, every file of Appendix A and the command are unchanged.

Names used below:
- **S2**, the second sanctioned HEAD: the commit P6-1c's checkpoint makes.
- **G2**, the second gate's commit: the commit `tools/checkpoint.sh "P6-1d part 1"` makes. The second run is made at G2.
- **FIRST_LOG**: `reports/P6_runs/attempt1/ACCESS_LOG`, SHA-256 `c6eb0d5ecf89f2f6b705488c71b0c281154ba94008755731739a7c0ffadfbc03`, one line: GRANTED for `prereg-v1`, head G1.
- **PANEL**: `~/Desktop/FX_Project/data/panel_confirm_SEALED.csv`, the path `io` builds from `OFILT_DATA_DIR`.

## 1. What runs

- **The code.** The code and configuration as committed at the tag, unchanged at S2. The sanction names:
  - `tools/p6_confirm_run.py`, `5b3922d79bb0a6d093dccf2aff5f1aaf3f869e8d93c900ac6fb3a6c74eaf5b7f`;
  - `ofilt/drift/confirm_run.py`, `998912c5c9e89ca14fde5e1ca1811ff3f3e4ac65dd36b29b61debffab8e9eaf3`;
  - `docs/P4_CONFIRM_CONFIG.json`, `5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd`.

  It also uses every other file of the pre-registration's Appendix A, at Appendix A's SHA-256.
- **The command.** §7.4's, verbatim, the same as the first request's. Its SHA-256 as a string is `1b34bf5c0a8d1f55245963329eaa3ec00bb927801187bbcca5cf6b25c45d2aa9`:

  `env -u OFILT_RUN_SEALED bash -c 'source "$HOME/venvs/ofilt_p2/bin/activate" && cd "$HOME/Desktop/FX_Project/ofilt_pass1" && export OFILT_DATA_DIR="$HOME/Desktop/FX_Project/data" && OFILT_P6_CONFIRM_RUN=P6-1 caffeinate -dimsu python -B tools/p6_confirm_run.py --out reports/P6_runs/confirm'`
- **The outputs.**
  - `reports/P6_runs/confirm/`: `document.json`, `manifest.json` and `runtime.json`;
  - a new `ACCESS_LOG` at REPO's root;
  - two lines appended to `RUN_REGISTRY.jsonl`.

  FIRST_LOG is never touched again.

## 2. The second sanction (§7.2; D2 conditions 2 and 6)

- **Placing the panel first.** Before the sanction, Isaiah runs the supervisor's placement command.
  - It copies `build_out/p2_20261006T002928Z/panel_confirm_SEALED.csv` to PANEL with `cp -p`, after checking that the source has SHA-256 `b575272aad752b3af84abe109fa66edde421f7c99184c9d1885bacdce64f06d1` (AM-04) and that the build's `MANIFEST.json` records it.
  - It checks the copy's SHA-256.
  - It prints hashes only, and never any content.
- **The file.** The sanction is `~/Desktop/FX_Project/files/pass6/sanction/P6_SANCTION2.txt`, outside REPO, written by Isaiah's sanction command. That command refuses unless HEAD is S2, the tree is clean, S2 is on GitHub, the three files of section 1 and this file have their SHA-256, and PANEL has the pinned SHA-256. It fills `Date:` from `date +%F`.
- **The text.** Exactly eleven lines, UTF-8, each ending in a newline, nothing else:

  ```
  SANCTION of the second attempt at the confirmation run, ofilt/drift (Pass 6, item P6-1d; D2; docs/PREREG_v1.md §7.2)
  Date: <YYYY-MM-DD>
  By: Isaiah Choi
  HEAD: <S2, 40 hex>
  tools/p6_confirm_run.py: 5b3922d79bb0a6d093dccf2aff5f1aaf3f869e8d93c900ac6fb3a6c74eaf5b7f
  ofilt/drift/confirm_run.py: 998912c5c9e89ca14fde5e1ca1811ff3f3e4ac65dd36b29b61debffab8e9eaf3
  docs/P4_CONFIRM_CONFIG.json: 5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd
  Criteria: docs/P6_RUN2_CRITERIA.md <the SHA-256 of this file, as PASS6_STATUS.md records it at S2>
  Sealed panel: data/panel_confirm_SEALED.csv b575272aad752b3af84abe109fa66edde421f7c99184c9d1885bacdce64f06d1 (copied from build_out/p2_20261006T002928Z/ and hash-verified by this command)
  First request: reports/P6_runs/attempt1/ACCESS_LOG c6eb0d5ecf89f2f6b705488c71b0c281154ba94008755731739a7c0ffadfbc03 (granted at 221507d01547869376e73cde51c20b86892bed95; no byte of the sealed panel read)
  I sanction one second run of tools/p6_confirm_run.py (D2), by the command of docs/PREREG_v1.md §7.4, at the gate of the criteria file above. Any further run is a dated, labelled deviation that I decide.
  ```

- **The checks (verdict `SANCTION CHECK`).** P6-1d checks by script that the form and every fixed line are exactly as above. `Date:` must be a valid calendar date, `HEAD:` must be S2, and `Criteria:` must name this file's SHA-256 as recorded at S2 and as `git show S2:docs/P6_RUN2_CRITERIA.md` gives it.
- **The builder's part.** The builder never writes or edits the sanction. P6-1d copies it with `cp -p` to `docs/P6_SANCTION2.txt`.

## 3. The gate (§7.3)

### 3.1 Before the gate's checkpoint (verdict `PRE CHECK`)

- **REPO.** HEAD is S2, the tree is clean, and S2 is on a remote-tracking branch; the setup script also checks it with `git ls-remote`.
- **The tags.** `git tag -l` is `pass1-final prereg-v1 spec-dev-v1`. `prereg-v1` is annotated, object `148b742e097c0ed6945992b7707d928ad21b4d37`, on `8341ffd930caea6e0327e8fcac90fc2e34652962`.
- **The access logs.**
  - The names starting `ACCESS_LOG` in REPO outside `.git` are exactly FIRST_LOG.
  - FIRST_LOG has its SHA-256 and is tracked.
  - No `ACCESS_LOG` exists at REPO's root.
  - `reports/P6_runs/` holds exactly `attempt1/ACCESS_LOG`, and `reports/P6_runs/confirm` does not exist.
- **The logs.** `BLIND_FIT_LOG` has 7 lines and `0cdedae9662221145dd3b9f4baecacc7431d17706d01f6cef19cce10c0f83383`. `RUN_REGISTRY.jsonl` has 2 lines and `9c6cb9c68538215cab8ae5c91f582e695757165bc4de5e033c8c61d49a9f542c`.
- **The test kit.** Its four files have the SHA-256 of section 6.
- **The environment.** `OFILT_RUN_SEALED` and `OFILT_P6_CONFIRM_RUN` are absent.
- **The presence check (D2 condition 5).**
  - It is one `os.stat` of PANEL, the only contact with the data folder outside the suite and the command.
  - It must show a regular file.
  - It prints only `PANEL: present, regular file` or `PANEL: absent`.
  - Nothing is opened, read, listed, hashed or copied.

### 3.2 The gate's checkpoint

- **The records of part 1.** These are exactly three:
  - `docs/P6_SANCTION2.txt`, the copy of the sanction;
  - `PASS6_STATUS.md`, from the template P6-1d's message gives;
  - `reports/P6_reports/p6_1c.txt`, P6-1c's report.
- **The command.** Then `tools/checkpoint.sh "P6-1d part 1"` runs with the background option. It must give `Ran 398 tests`, `OK (skipped=6)` and one `commit <G2>` line.

### 3.3 After the checkpoint, before the command (verdict `GATE CHECK`)

- **G1, the commit.** HEAD is G2, and its only parent is S2.
- **G2, its files.** `git diff --name-only S2 G2` lists exactly the three records of 3.2.
- **G3, the hashes.** Each is checked in the working tree and at G2:
  - the three files of section 1;
  - all 40 files of Appendix A, the table parsed from `docs/PREREG_v1.md` at G2;
  - `docs/PREREG_v1.md` itself, `79447ba199ce2360fb1fc8c51ae5d0eea3c20ba2645d6167c17ba1e1792f35e6`;
  - this file, at the SHA-256 recorded at S2;
  - FIRST_LOG.
- **G4, the sanction.** `docs/P6_SANCTION2.txt` at G2 is byte-identical to the sanction file and passes section 2's checks.
- **G5, the tags.** As in 3.1, and `prereg-v1`'s commit and G1 are ancestors of G2.
- **G6, the tree.** The tree is clean.
- **G7, the suite.** The checkpoint's output holds `Ran 398 tests`, `OK (skipped=6)` and G2's commit line.
- **G8, the logs.** As in 3.1: the access logs, `reports/P6_runs/`, and the two logs.
- **G9, the environment.** `OFILT_RUN_SEALED` and `OFILT_P6_CONFIRM_RUN` are absent.
- **G10, the command.** The command text P6-1d's message gives has `1b34bf5c0a8d1f55245963329eaa3ec00bb927801187bbcca5cf6b25c45d2aa9`, and so does the one line of `docs/PREREG_v1.md` at G2 that contains `OFILT_P6_CONFIRM_RUN=P6-1 caffeinate`.
- **G11, the registration.** `PASS5_STATUS.md` at G2 records `https://osf.io/3mr5h`.
- **G12, the presence check.** 3.1's presence check is repeated. PANEL must be a regular file.

**The gate.** The command runs only if `SANCTION CHECK`, `PRE CHECK` and `GATE CHECK` are all True. Otherwise the item stops before the panel is requested again.

## 4. The command (§7.4; hard rule 3)

- **How it runs.** Once, as the command tool's own command with its background option, verbatim. While it runs, nothing else runs in REPO, and no shell command runs at all; the editor may write `/tmp` files.
- **Its output.** The builder writes the captured output and exit status into `/tmp/p6_1d_run_output.txt`. It also copies the tool's own output file, if the tool reports one, and the two are compared.
- **The crash rule (§7.5).** Once `io.load_confirm` has logged GRANTED, the second opening counts.
  - If anything fails after that, the item stops. Nothing the run wrote is deleted, moved or edited, and Isaiah decides.
  - A refusal before any load writes nothing; it is reported, and the item stops.

## 5. After the command (verdict `POST CHECK`)

- **P0, the command as run.** The command as transcribed has `1b34bf5c0a8d1f55245963329eaa3ec00bb927801187bbcca5cf6b25c45d2aa9`.
- **P1, the exit and the printout.**
  - The exit status is 0.
  - The output holds exactly three lines matching `^reports/P6_runs/confirm/(document|manifest|runtime)\.json [0-9a-f]{64}$`, in that order, and each printed SHA-256 equals the file's.
  - Any other line is printed in the report and is not a failure.
  - The transcription equals the tool's own output file, where there is one.
- **P2, the folders.** `reports/P6_runs/confirm/` holds exactly the three files, and `reports/P6_runs/` holds exactly `attempt1/` and `confirm/`.
- **P3, the document.** `document.json` parses with Python's `json`, with `NaN` and `Infinity` refused.
  - Its `rows` keys, in order, equal `ofilt.drift.confirm_inference.ROW_IDS` and the configuration's `rows` keys. The check may import that one module, which reads no data.
  - No row is `pending`. `mode` is `confirmation` and `provenance` is `confirm_real`.
  - Every row that is `not_estimable` or `not_applicable` is listed with its reason. That is a report, not a failure.
- **P4, the manifest.** `mode` and `provenance` are the document's. `config_sha256` is section 1's configuration hash. `cost_inputs_sha256`, `analysis_spec_sha256` and each `specifications` entry's `sha256` equal Appendix A's.
- **P5, the access logs.**
  - The names starting `ACCESS_LOG` in REPO outside `.git` are exactly `ACCESS_LOG` and FIRST_LOG.
  - FIRST_LOG is unchanged, with its SHA-256.
  - `ACCESS_LOG` at REPO's root holds exactly one line: JSON, `result` `GRANTED`, `tag` `prereg-v1`, `head` G2. Its `guard` is reported.
- **P6, the registry.** `RUN_REGISTRY.jsonl` has 4 lines.
  - Its bytes up to the second newline have `9c6cb9c68538215cab8ae5c91f582e695757165bc4de5e033c8c61d49a9f542c`.
  - Line 3's `run_id` is `runtime.json`'s `run_ids.main` and line 4's is `run_ids.m7`. Both have `provenance` `confirm_real` and `git_commit` G2.
  - Their `git_dirty` values are reported as written; False then True is expected.
- **P7, the tree.** HEAD is still G2. `git status --porcelain --untracked-files=all` lists exactly:
  - ` M RUN_REGISTRY.jsonl`;
  - `?? ACCESS_LOG`;
  - `?? reports/P6_runs/confirm/document.json`, `?? reports/P6_runs/confirm/manifest.json` and `?? reports/P6_runs/confirm/runtime.json`.

  With `--untracked-files=no`, it lists only ` M RUN_REGISTRY.jsonl` (P86; P6Q8).
- **P8, what must not change.** `BLIND_FIT_LOG` and the tags are unchanged, FIRST_LOG is unchanged, and Appendix A's other 39 files have their SHA-256.

**What P6-1d's report prints.** These are printed after the run:
- `document.json`, `manifest.json`, `runtime.json` and the new `ACCESS_LOG`, in full;
- the two new registry lines without their `folds` (each with its count);
- every verdict;
- the run's wall time.

## 6. Part 2: the post-run checkpoint (verdict `PART2 CHECK`)

**When.** Part 2 runs only if `POST CHECK` is True.

**The kit.** The revised kit of §7.6's test changes was installed at P6-1c, before the run (D2 condition 4). Part 2 installs nothing. The kit's files must still have these SHA-256:

| Path | Base SHA-256 (at the tag) | Kit SHA-256 (installed at P6-1c) |
|---|---|---|
| `tests/run_state.py` | (new) | `5ab0608114e465175161835a7169a93dbcce8a9a317ebd1f39f0210d4e4f3759` |
| `tests/test_docs_d3b.py` | `33c975d82230818b81872bce1acaf73a43cbf4c0171e59a8a1240897b658de20` | `a34a0350fac9dbfc3341f358bc61558c0ca92b77c04db50dbcf4f91063a7d44d` |
| `tests/test_p4_confirm_forecast.py` | `470fdf23c601ee24a5e5110eac74eb655064181042143aaac9b9f9d1b0c7ef52` | `06a15eec407b8ca582d6f9c8ab3b2dc7fd3e4938ed7ebdbed32f1ad032475939` |
| `tests/test_p4_confirm_run.py` | `69d74d062ba87d5fc5d23b919d4c7d4162074ed80c08279efb963a3b15374913` | `7ccb4561a765c0ad5d7ccc61b134f5769734f6a8670b9f3d34f822368f2711a0` |

**The order.**
1. The three changed modules run on their own against the real run's effects: `tests.test_docs_d3b`, `tests.test_p4_confirm_forecast` and `tests.test_p4_confirm_run` give 31 tests, OK.
2. The records of part 2 are written, from the template P6-1d's message gives.
3. `tools/checkpoint.sh "P6-1d part 2"` runs, and must give `Ran 398 tests` and `OK (skipped=6)`.

**What the commit holds.** Exactly `ACCESS_LOG`, `PASS6_STATUS.md`, `RUN_REGISTRY.jsonl` and the three outputs.

**After the commit, by script.**
- Its only parent is G2.
- Nothing under `ofilt/`, `tools/`, `tests/`, `spec/` or `build/` changed.
- `ACCESS_LOG` is tracked.
- FIRST_LOG, `BLIND_FIT_LOG` and the tags are unchanged.
- The tree is clean.

If any of this fails, the item stops. Nothing the run wrote is deleted, and Isaiah decides.

## 7. Not part of P6-1d

- The write-up reports every row, in §4's wording (§7.7). It reports both requests: the first, granted and failed before any read, beside the second's result.
- P6-2 records the run's facts and P92's refresh.
- The forward holdout (§8) has its own plan.
