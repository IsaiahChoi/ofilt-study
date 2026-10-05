# PASS 2 ADDENDUM (2026-10-05): corrections for the rebuilt repo, pre-flight decisions, builder prompt A′

**For:** the Pass 2 supervisor (a Claude chat in this Project) and, through Appendix A′, the builder (Claude Code on Isaiah's Mac).

**Read with:** `PASS2_HANDOFF.md` (2026-10-04). Where the two differ, this addendum governs, and the decision log (P01–P57) governs both. The decisions themselves are in `DECISIONS_P37_onward.md`, P45–P57; this document applies them.

---

## 0. Why this addendum exists

The handoff was written for the original Pass 1 repository, which was lost. The canonical repository is the rebuild (P45). It has the same decisions, a rebuilt Stage C4–D, and 33 added verification tests (`test_docs_d1`–`d6`). Seven facts about it change how Pass 2 runs. Each was verified on 2026-10-05.

1. **Test counts.** The suite is 205 tests with 4 skipped in the sandbox (229 s), not 171 with 5. On the Mac expect 5 skipped: `test_docs_d6` has a Project test that skips without `/mnt/project`.
2. **Pinned tests.** The verification tests pin exactly the Pass 1 state that Pass 2 must change: hashes, the hedge placeholder, schema counts, the robustness list and doc bytes. See §5.
3. **Spec changes invalidate C7.** The C7 report's staleness key includes the spec file's SHA-256. A comment-only spec edit on a scratch copy failed `test_bands_consistency_and_staleness`, so any amendment forces one slow-tier rerun (P51).
4. **Sandbox defaults.**
   - `io.DATA_DIR` defaults to `/mnt/project`.
   - `tools/checkpoint.sh` is hard-wired to `/home/claude/...` and `/mnt/user-data/outputs`.
   - macOS has no `setsid`.
5. **Guard fail-open path.** The guard adapter treated a non-raising external guard as a grant (P46).
6. **Ordering.**
   - Changing the schema before the panel exists breaks every real-dev test, because `io` demands an exact schema match and the spec hash.
   - AM-03's content depends on the P18 checks run in P2-5.
7. **Loose definitions.** The staleness-test reading, the US early closes, the gotobi convention and the completeness of the robustness designs were underspecified. P48, P49, P55 and P56 fix them.

---

## 1. Decisions of 2026-10-05

Isaiah adopted the supervisor's recommendations.

| Entry | Decision | Effect on Pass 2 |
|---|---|---|
| P45 | The rebuilt repo is canonical; it is not merged into FX-Project | Pre-flight item 6 becomes "suite green on the Mac"; build code moves into `build/` |
| P46 | Conjunctive, fail-closed tag gate | Resolves Flag 5. Four new guard tests in P2-0 |
| P47 | 1306 ÷10 confirmed by the issuer and its published distributions | Resolves D1; CACS is optional |
| P48 | Gotobi: the 5th, 10th, 15th, 20th, 25th and 30th plus month-end; roll to the preceding trading day; one flag | Resolves D4. Reference counts in B′ |
| P49 | US session 09:30–16:00 ET, or 13:00 on the 23 NYSE early closes; 0.0 when there is no session | New definition for `usdjpy_us_ret` and `ewj_oc_jpy` |
| P50 | Names and groups; staleness and bar counts go in PROVENANCE; 60 columns | Resolves D6 and P43 |
| P51 | Order, append-only build, one decision checkpoint, one switch commit, test-change protocol, `pass1-final` tag, one C7 rerun | Replaces handoff §7's order |
| P52 | `FX_NAMES` extended; `y_1306_oc` registered | A data-list exception to the Flag 2 freeze |
| P53 | Flags 14 and 15 accepted as implemented | No code change |
| P54 | The rebuilt validation numbers are the citable ones | Appendix B′ uses them |
| P55 | Staleness-test reading rule (a reverse-regression bracket) | Method for D10, fixed before the test runs |
| P56 | Robustness amendments must be operationally complete; same-sample comparisons; tier-(ii) criterion | Governs the AM-05 and AM-06 drafts |
| P57 | Documentation refresh | Doc-pin test changes pre-approved |

**Still open at the decision checkpoint:**
- D7: the P42 rule, the tier-(ii) criterion, and the yen-EWJ option;
- D8: 1306 open-auction timing, with default (a);
- D9: A7 on 1306;
- D10: the staleness result, read per P55;
- D12: the exact AM-03 to AM-06 texts.

**Still open with Isaiah:**
- D2, the settings-check suffix (P39b). This is **blocking**.
- D3, the TOPIX total-return ticker (P40). This is for records only.

---

## 2. Pre-flight status

This replaces handoff §6.

| # | Item | Status (2026-10-05) | Action |
|---|---|---|---|
| 1 | CACS split ratio | **Done** (P47) | Optional: run CACS and add its output to P39's record |
| 2 | Settings check (1A): suffix | **OPEN, blocking** | Isaiah reports which suffix reproduced Book2 exactly, and which suffix 1306 used |
| 3 | TOPIX total-return ticker | Open, not blocking | Isaiah states it; recorded in P40 and DATA_PROVENANCE §4.4 at P2-6 |
| 4 | Gotobi convention | **Done** (P48) | — |
| 5 | Guard (Flag 5) | **Done** (P45, P46) | The builder implements the conjunctive gate in P2-0 |
| 6 | Repo | **Changed** (P45) | Unzip the rebuilt repo to the REPO path. In P2-0 the builder confirms 205 tests, OK, 5 skipped, then tags `pass1-final`. Push to a **private** remote |
| 7 | Project docs current | **Done** for the 2026-10-04 set | Upload the 2026-10-05 documents to the Project: this addendum, PLAN v2.3, README, PROJECT_SETUP, DATA_PROVENANCE, DECISIONS_P37_onward, PASS2_INPUTS.json, and PASS2_HANDOFF with its banner |
| 8 | Raw files organised and hashed | Open | `bash organize_raw_inputs.sh` (dry run, then `--apply`); every line OK or MOVED |
| 9 | Claude Code environment | Open | Python 3.12 venv with pandas, numpy, scipy, scikit-learn, openpyxl and PyYAML. Create the DATA folder from the kit's `data/` |
| 10 | Cost inputs (Pass 3) | Not blocking | Start collecting (handoff §11) |
| 11 | Kit on the Mac | New | Unzip `pass2_kit_2026-10-05.zip` to the KIT path. `shasum -a 256 -c SHA256SUMS_2026-10-05.txt` must print OK for every file |

---

## 3. Corrections to the handoff, by section

- **§1–§2, Appendix B.**
  - Test counts and the C7 numbers are as in Appendix B′.
  - Flag 5 is resolved; Flags 14 and 15 are resolved (P53).
  - Flag 12 is unchanged (Pass 3).
- **§3, the non-negotiable rules.** Add:
  - **8.** No raw or sealed file is ever opened or printed by any viewer, in any session (P51).
  - **9.** Sealed outputs live outside the repo and the Project, and nothing data-like is committed (P45, P51).
- **§5, inputs.** `PASS2_INPUTS.json` now also lists the event files and the original build code, which the build must verify too.
- **§6.** Replaced by §2 above.
- **§7, the work plan.**
  - The order is replaced by §4 below.
  - The P2-2 table stands, with these amendments:
    - groups per P50, with staleness and bar counts in PROVENANCE;
    - `gotobi_day` per P48;
    - `usdjpy_us_ret` per P49, including early closes and the 0.0 rule;
    - session FX ends at the close of day t itself;
    - the build is append-only (P51).
  - The P2-5 staleness test follows P55.
  - The A7 report on 1306 is written to a new file. The TOPIX report stays unchanged.
  - Updating DATA_DICTIONARY moves into the switch commit, because `test_docs_d5` checks it against the schema.
- **§8, the decision register.** D1 → P47. D4 → P48. D5 → P45/P46. D6 → P50. D11 keeps its scope, but its rationale is corrected (P51).
- **§9, the verification protocol.** Add the checks in §6 below.
- **§10, pitfalls.** Add these:
  - macOS has no `setsid`.
  - Interactive zsh treats `#` as a literal, not a comment, so Isaiah's pasted commands must not contain inline comments.
  - Use `shasum -a 256`, not `sha256sum`.
  - Set `OFILT_DATA_DIR`.
  - `build_panel.py` reads the event files from its working directory.
  - The verification tests pin Pass 1 state (§5).
  - A spec edit invalidates C7.
- **Appendices A and B.** Replaced by A′ and B′. Templates C1–C4 still apply, with "Hard rules 1–7" referring to A′.

---

## 4. Revised execution order (P51)

| Step | What | Where it stops |
|---|---|---|
| P2-0 | Integrity, environment, `pass1-final` tag, portable checkpoint script, `.gitignore`, conjunctive guard, docs sync | Report |
| P2-0b | Baseline: the frozen original build reproduces `7366…` and `9c18…` | STOP on any mismatch |
| P2-1 | Validate the new inputs (reports only) | STOP if the settings-check suffix is still missing |
| P2-2 | Append-only build extension, with synthetic tests only | — |
| P2-3a | Drafts only: schema, targets, io, blind list, AM-03 to AM-06, DATA_DICTIONARY, test-change table | — |
| P2-4 | Rebuild into a fresh folder; acceptance (a)–(g) | STOP on any failure |
| P2-5 | Dev checks on the fresh panel through standalone scripts | **Decision checkpoint** |
| P2-3b | **One switch commit** with everything approved; full suite | — |
| C7 | One slow-tier rerun; every replication must be identical | STOP on any difference |
| P2-6 | Records (drafts of P58 onward, provenance, hashes, the Project upload list) | Report |
| P2-7 | Final suite and status | End of Pass 2 |

**What Isaiah decides at the checkpoint (supervisor prepares each item):**
- D7, with P56's standards;
- D8;
- D9;
- D10, read per P55;
- D12: the exact AM-03, AM-04, AM-05 and AM-06 lines;
- the DATA_DICTIONARY draft;
- the full test-change table;
- the `FX_NAMES` diff.

---

## 5. Test-change protocol and the known list (P51)

**The rules.**
1. The unchanged Pass 1 HEAD is tagged `pass1-final`. Checking it out reproduces the Pass 1 attestation.
2. An assertion that Pass 2 legitimately supersedes is rewritten to the new state, with a comment citing the superseding entry. It is never deleted without a replacement.
3. Every change is listed old → new in PASS2_STATUS "Test changes". Phase P2-0 changes are pre-approved by P57. Switch-commit changes are approved at the checkpoint.
4. A failure that this list does not explain is a STOP, not a test edit.

**Phase P2-0 (pre-approved, P57):**

| Test (line in the rebuilt repo) | Current assertion | New assertion | Entry |
|---|---|---|---|
| `test_docs_d4` (27) | README prefix `dc7983326fc4964e`; PLAN prefix `220fc762a511b13a` | the prefixes in `SHA256SUMS_2026-10-05.txt` | P57 |
| `test_docs_d4` (31) | PLAN starts `# Research Plan v2.2` | starts `# Research Plan v2.3` | P57 |
| `test_docs_d4` (32) | `Supersedes:** v2.1 (Pass 1, item D4b, …)` | the v2.3 line `Supersedes:** v2.2 (2026-10-04), which superseded v2.1 (Pass 1, item D4b, …)` | P57 |
| `test_docs_d4` (75) | `171 tests, 5 skipped by default` in §8 | unchanged; v2.3 keeps the phrase | — |
| `test_docs_d6` (23, 26) | PROJECT_SETUP prefix `d2afcf2a1fe90074`; old title | the new prefix; the title ending `refreshed 2026-10-05)` | P57 |
| `test_docs_d6` (54, 55) | lists `` `PLAN.md` (v2.1) ``; the Project PLAN starts with v2.2 | `` `PLAN.md` (v2.3) ``; v2.3 (Project-only test, skipped on the Mac) | P57 |
| new `test_docs_p2.py` | — | pins each kit doc copied into `docs/` to its SHA256SUMS entry | P57 |
| new guard tests | — | the four P46 cases | P46 |
| new build-code pin | — | `build/pass1/*` hashes equal `PASS2_INPUTS.json` | P51 |

**Switch commit (approved at the checkpoint):**

| Test (line) | Current assertion | New assertion | Entry |
|---|---|---|---|
| `test_spec` (35) | dev hash `736636…` | the new dev-panel hash | AM-04 |
| `test_spec` (101) | `hedge_oc_column == y_topix_oc` | `y_1306_oc` | AM-03 |
| `test_spec`, verbatim diff | lines {33, 43–46, 62}; ids {AM-01, AM-02} | plus the AM-03 to AM-06 lines and ids | AM-03 to AM-06 |
| `test_schema` (31, 35, sizes) | CONTEMPORANEOUS empty; 41 columns; sizes 20/10/3/0 | CONTEMPORANEOUS 2; 60 columns; PRE_OPEN 20 (unchanged), PROVENANCE 16, AT_OPEN 6, CONTEMPORANEOUS 2, PRE_OPEN_ROBUSTNESS 7 | P50 |
| `test_docs_d1` (98, 100) | hedge `y_topix_oc`; `HEDGE_GAP_FOR == {y_topix_oc: ao_topix_gap}` | `y_1306_oc`; both pairs | AM-03 |
| `test_docs_d1` (111) | `ewj_yen_denominated_REQUIRES_PASS2` in the robustness list | the AM-06 name | AM-06 |
| `test_docs_d1` (121, 127) | group counts with CONTEMPORANEOUS 0; 41 columns | the P50 counts; 60 | P50 |
| `test_docs_d3` (110) | exact robustness list | the AM-06 list | AM-06 |
| `test_docs_d3` (118) | sealed hash starts `9c18a6c1` | the new prefix | AM-04 |
| `test_docs_d3` (~66) | every BLIND_FIT_LOG panel hash equals the spec's dev hash | equals the Pass 1 dev hash `7366…`, as a constant: lines 1–6 are Pass 1 history | AM-04, P51 |
| `test_docs_d5` | DATA_DICTIONARY pin; 41 columns; the group table | the new pin; 60; the new table | P50 |
| `test_blind` (117) | `usdjpy_`/`eurusd_` columns ⊆ `FX_NAMES` | also every P52 column ⊆ `FX_NAMES` | P52 |
| `test_lookahead` | real-data look-ahead on `y_topix_oc` | add a `y_1306_oc` case (additive) | AM-03 |
| `test_validation_c7` | report key | unchanged; the report is regenerated by the rerun, never edited | P51 |

---

## 6. Supervisor verification additions (to handoff §9)

**At every checkpoint, check:**
- P2-0b's two hashes match exactly.
- After the switch commit, the C7 rerun's replications are identical to the previous report's, field by field. Only `key.spec_sha256` changes.
- The test changes match §5. Any extra change has a stated reason and your approval.
- The skip count is 5 on the Mac, and no new skip appears.
- `git tag -l` shows only `pass1-final`.
- The MANIFEST records library versions and the hashes of the build code.

**Additional red flags (stop immediately):**
- any viewer command on RAW, on OUT, or on a sealed panel;
- a test deleted;
- a test change not on the list;
- an edit under `build/pass1/`;
- a spec edit outside the approved batch;
- a background process left running.

---

## Appendix A′: Pass 2 builder prompt (replaces Appendix A)

Fill in the two ⟨…⟩ items, confirm the paths, then give Isaiah this text for Claude Code.

````markdown
# Pass 2: data and rebuild for the overnight-FX drift study (builder prompt A′, 2026-10-05)

You are building Pass 2 of a pre-registered study for Isaiah Choi, who makes every decision. Verify, don't assume. If anything is fatally wrong, say so and stop that item; never silently work around it. Accuracy beats speed. No hardening or refactoring beyond what an item asks for.

## Paths (Isaiah confirms; every path contains a space, so always quote it)
- REPO = "$HOME/Desktop/FX Project/ofilt_pass1": the canonical study repo (P45); git, branch main.
- RAW  = "$HOME/Desktop/FX Project/raw": raw inputs, flat, plus raw/checks/.
- DATA = "$HOME/Desktop/FX Project/data": OFILT_DATA_DIR; holds panel_dev.csv, events_firm.csv and events_boj.csv.
- KIT  = "$HOME/Desktop/FX Project/pass2_kit_2026-10-05": docs/, build/pass1/, data/, SHA256SUMS_2026-10-05.txt.
- OUT  = "$HOME/Desktop/FX Project/build_out": build outputs, one subfolder per run; outside the repo; holds sealed panels.

## Read first, in this order
1. KIT/docs/PASS2_ADDENDUM.md. It governs where it differs from the handoff; this prompt is its Appendix A′.
2. KIT/docs/PLAN.md (v2.3).
3. KIT/docs/DECISIONS_P37_onward.md (P37–P57).
4. KIT/docs/DATA_PROVENANCE.md §4.
5. REPO/docs/DECISIONS_P14_onward.md: P17, P18, P29, P34, P36.
6. REPO/PASS1_STATUS.md: the decision-log entries for A5, B5, C1, C6 and C7 only. Then REPO/docs/REBUILD_VERIFICATION.md, "Summary".
7. KIT/docs/PASS2_HANDOFF.md §7 (the P2-2 column table) and §8 (the decision register), for background.

Do not read the Math 86 PDF.

## Decisions already taken (Isaiah, 2026-10-05)
- P45–P57 as summarised in addendum §1.
- D11's scope stands: no change to inference/sim/forecast/models/fctests.
- Pending, do not guess:
  - settings-check suffix ⟨SUFFIX, e.g. "JT reproduced Book2; 1306 used JT"⟩ (P39b). If this is still unfilled when P2-1 reaches 1306, STOP.
  - TOPIX total-return ticker ⟨TICKER⟩ (P40). Records only.

## Hard rules
1. **Inputs.**
   - Before reading any data, verify KIT/SHA256SUMS_2026-10-05.txt with `shasum -a 256 -c` (run from KIT).
   - Then verify every hash in KIT/docs/PASS2_INPUTS.json: raw inputs, event files and original build code.
   - Any mismatch: STOP.
   - Never edit a raw file. Never download anything; this pass has no network step.
2. **Blinding.**
   - No computation whose output relates any predictor to any target on real data.
     - Predictors: usdjpy_*, eurusd_*, xau_*, n225_*, the US controls, ewj_oc_jpy and session FX.
     - Targets: y_*, and the abn/raw/gap/cc targets.
   - No sealed fit: OFILT_RUN_SEALED stays unset.
   - No walk_forward, build_design or inference call on real data.
   - Allowed on dev:
     - predictor-only statistics;
     - target-only statistics without predictors (A7);
     - gap-only statistics (the staleness test).
   - Anything on the confirmation side (2022+): dates, counts, hashes and booleans only.
3. **No viewing raw or sealed data.**
   - Never open, cat, head, tail, less, grep, preview or load-and-print any file under RAW or OUT, or any panel_confirm_SEALED.csv.
   - Inspect only through scripts that print counts, spans, hashes, booleans, or the dev statistics an item names: write the script, run it, read its summary.
4. **Frozen code.**
   - No change to:
     - ofilt/drift/inference.py, sim.py, forecast.py, models/* or fctests.py;
     - tools/c7_mc.py;
     - anything under REPO/build/pass1/.
   - PRE_OPEN_FEATURES stays exactly the 20 Pass 1 columns.
   - In blind.py, only the P46 tag-gate change and the P52 FX_NAMES list are allowed.
5. **Spec.** Changes happen only as AM-xx entries that Isaiah has approved. Draft them in P2-3a; apply them only in the P2-3b switch commit.
6. **Tests.** Follow the test-change protocol in addendum §5.
   - Rewrite an assertion that Pass 2 legitimately supersedes to the new state, with a comment citing the superseding entry.
   - Never delete a test without a replacement.
   - List every change old → new in PASS2_STATUS "Test changes".
   - Any failure that the §5 list does not explain: STOP.
7. **Stop** at every STOP, and whenever a decision isn't covered here.

## Environment (macOS)
- Use Isaiah's venv (myenv), Python 3.12. Record the python, pandas, numpy, scipy, scikit-learn, openpyxl and PyYAML versions in PASS2_STATUS; P2-4 writes them into the new MANIFEST.
- Suite: `cd "$REPO" && env -u OFILT_RUN_SEALED OFILT_DATA_DIR="$DATA" python -m unittest discover -s tests`.
  - Before any change, expect `Ran 205 tests … OK (skipped=5)`. The five skips are 2 sealed opt-in tests, 2 slow tests, and test_docs_d6's Project test.
  - Anything else: STOP and report.
- macOS has no `setsid`.
  - Keep every command inside your tool timeout.
  - Run the C7 slow tier in foreground chunks: `OFILT_SLOW=1 OFILT_DATA_DIR="$DATA" python tools/c7_mc.py --budget 90`, repeated until it prints COMPLETE.
  - Never leave a background process running.
- Commands for Isaiah to paste into zsh:
  - complete heredocs;
  - quoted paths;
  - no inline `#` comments.

## Checkpointing
- After each item:
  1. run the suite;
  2. commit (with tools/checkpoint.sh once P2-0e exists);
  3. update PASS2_STATUS.md with TARGETED edits only. Never re-emit the whole file.
- PASS2_STATUS.md sections: Progress, Next action, Decision log, Test results, Test changes, Flags, Blinding attestation, Deviations.
- Stop at the next item boundary when any of these holds:
  - you have written more than about 1,500 lines this response;
  - the next item is large;
  - 3 items are done this response;
  - you notice yourself re-printing large files.
- End each response with one line naming the next item.

## Items

### P2-0 Environment, integrity and setup (no data analysis)
a. **Hashes.** Verify SHA256SUMS and every PASS2_INPUTS.json hash (Hard rule 1). Report the hash table.
b. **Repo state.**
   - The tree is clean.
   - `git tag -l` lists neither spec-dev-v1 nor prereg-v1.
   - BLIND_FIT_LOG has 6 dev_real lines, and RUN_REGISTRY.jsonl is empty.
   - From REPO, `python -c "import ofilt, ofilt.drift.io as io; print(ofilt.__file__, io._external_check_access)"` prints the repo's own package and `None`.
c. **Data folder and suite.** DATA holds hash-verified copies of panel_dev.csv (736636…), events_firm.csv (61b562…) and events_boj.csv (8950b3…), taken from KIT/data. Run the suite: expect 205 tests, OK, skipped=5.
d. **Tag.** Tag the unchanged HEAD (81905c1) `pass1-final`, as a lightweight tag. Nothing else is ever tagged.
e. **Checkpoint script.** Rewrite tools/checkpoint.sh as a whole file:
   - repo root from `git rev-parse --show-toplevel`;
   - runs the suite under `env -u OFILT_RUN_SEALED`, with OFILT_DATA_DIR taken from the environment; refuses to run if it is unset;
   - commits as `checkpoint: <item>`;
   - no mirroring, no tarball;
   - keeps the literal `env -u OFILT_RUN_SEALED` and never contains `OFILT_RUN_SEALED=1` (two tests pin this).
f. **.gitignore.** Add `*.csv`, `*.csv.gz`, `*.gz`, `*.xlsx` and `build_out/`. Show with `git check-ignore` that a dummy panel file in the repo is ignored, then delete the dummy.
g. **Guard (P46).** Make the tag gate conjunctive in io._check_access and blind._tag_ok:
   - always run the fallback check;
   - additionally run the external guard if it is importable;
   - any exception, and any return other than None/True, is a denial.
   - New tests:
     - external returns False → denied;
     - external returns None while the tag is absent → denied;
     - external raises → denied;
     - both satisfied in a temporary repo → granted.
   - The existing guard tests stay unchanged and passing.
h. **Docs sync (P57).**
   - Copy KIT/docs/{PLAN,README,PROJECT_SETUP}.md over REPO/docs/replacements/.
   - Copy KIT/docs/{DECISIONS_P37_onward.md, PASS2_HANDOFF.md, PASS2_ADDENDUM.md, PASS2_INPUTS.json, DATA_PROVENANCE.md} to REPO/docs/.
   - Apply the phase-P2-0 test changes in addendum §5, and add tests/test_docs_p2.py.
i. **Report:** hashes, versions, suite summary, guard tests, test changes.

### P2-0b Baseline: reproduce the original build (before any new build code exists)
- **Freeze the original code.** Copy KIT/build/pass1/{build_panel.py, make_events.py, events.py} to REPO/build/pass1/, byte for byte. Add a test that pins their hashes to PASS2_INPUTS.json. These files never change.
- **Run it.**
  - Make a fresh working folder OUT/baseline_<UTC stamp>/work/ holding hash-verified copies of the two event files. The script reads them from its working directory.
  - Run the frozen build_panel.py from that folder, with raw = RAW and out = OUT/baseline_<stamp>/.
- **Accept only if:**
  - panel_dev.csv hashes to 736636031ca1… and panel_confirm_SEALED.csv to 9c18a6c10635…;
  - the rows are 5,124 / 3,057 and the spans match MANIFEST.
  - Print only the script's own outputs block.
- **On failure** (either hash differs): STOP. Change no code. Report the library versions; environment drift is the likely cause, and Isaiah decides.

### P2-1 Validate the new inputs (reports only)
Reproduce DATA_PROVENANCE §4. The numbers must match Appendix B′.
- **1306** (sheet `1306` of newbloombergdata_fixed.xlsx):
  - dates identical to the miners' calendar from Book2 (2,728);
  - OHLC consistent;
  - the six rows where open = close = previous close;
  - no split artifacts.
  - For 2022+: booleans and counts only.
- **1306 dividends:**
  - 11 rows, all of type Regular Cash;
  - amounts equal the RAW sheet ÷ 10 exactly;
  - dev amounts and implied yields as in B′;
  - 2022+: booleans only.
- **TOPIX total return:** its calendar is the miners' calendar plus 2020-10-01.
- **XAU:** 3,957,473 rows; the span; the gaps; the four outlier minutes.
- **Japan 225:** 3,314,917 rows; the share of fresh 08:59 prices by half-year; the 2018-07-02 changeover.
- **Settings check (P39b)** must be supplied. If it is missing, STOP after writing the report.
- Write reports/P2_1_inputs.md.

### P2-2 Build extension (code and synthetic tests only; no real-data run)
**Required design (append-only, P51).** REPO/build/pass2/build_panel_p2.py does the following:
1. It runs the frozen build/pass1/build_panel.py, exactly as in P2-0b, into a temporary folder.
2. It computes the new columns from the raw inputs, using pure functions in build/pass2/columns.py.
3. For each panel, it:
   - reads the old panel back with `dtype=str, keep_default_na=False`, so the 41 old columns stay as the original strings;
   - merges in the new columns by date;
   - asserts that the row count and row order are unchanged;
   - appends the 19 new columns to the right, in the order below;
   - writes the final panel.
4. It writes MANIFEST.json containing:
   - every input hash, including the event files;
   - the hashes of the build/pass1 and build/pass2 files;
   - the library versions;
   - output hashes, rows and spans;
   - the SHA-256 of each panel's 41-column projection, written with `to_csv(index=False)` from the string frame.

**New columns, in order** (names and groups P50; price-at-instant everywhere means the close of the last bar labeled ≤ X − 1 min, as in build_panel.price_at):

| # | column | definition | group |
|---|---|---|---|
| 1 | y_1306_oc | ln(close_t / open_t), 1306 | TARGET_INPUTS |
| 2 | ao_1306_gap_raw | ln(open_t / close_{t−1}), 1306 | AT_OPEN |
| 3 | ao_1306_gap_adj | ln(open_t / (close_{t−1} − D_t)), where D_t is the corrected 1306 distribution with ex-date t, else 0 | AT_OPEN |
| 4 | ao_topix_gap_tradj | ao_topix_gap + [ln(TR_t / TR_{t−1}) − ln(PR_t / PR_{t−1})]. TR is the `TOPIX optional` close and PR is Book2's TOPIX close, both after dropping 2020-10-01. Fallback path only | AT_OPEN |
| 5–7 | xau_ret, xau_rv, xau_bv | as usdjpy_ret/rv/bv, from the XAU minute file, over the same dark window | PRE_OPEN_ROBUSTNESS |
| 8 | n225_ret | the dark-window log return of the Japan 225 CFD, same rule | PRE_OPEN_ROBUSTNESS |
| 9 | usdjpy_us_ret | P49: the sum over the P11 NY session dates of ln(P(close_d) / P(open_d)). Open is 09:30 America/New_York; close is 16:00, or 13:00 on the B′ early-close dates. Exactly 0.0 when us_n_sessions = 0 | PRE_OPEN_ROBUSTNESS |
| 10 | ewj_oc_jpy | ewj_oc + usdjpy_us_ret; NaN exactly where ewj_oc is NaN | PRE_OPEN_ROBUSTNESS |
| 11 | gotobi_day | P48 | PRE_OPEN_ROBUSTNESS |
| 12–13 | c_usdjpy_sess_ret, c_eurusd_sess_ret | ln(P(t, close) / P(t, 09:00:00 JST)). The close is 15:00 JST for t ≤ 2024-11-04 and 15:30 for t ≥ 2024-11-05, by day t itself. Never a feature | CONTEMPORANEOUS |
| 14–16 | xau_bars, xau_stale_start_min, xau_stale_end_min | as the usdjpy_ provenance columns | PROVENANCE |
| 17–19 | n225_bars, n225_stale_start_min, n225_stale_end_min | as above | PROVENANCE |

**New build-time assertions (all must pass):**
- 1306 dates equal the miners' calendar; 1306 OHLC has no NaN; columns 1–3 are finite on every row.
- Exactly 11 dividend rows are used, all Regular Cash, and every ex-date is in the calendar.
- The TOPIX total-return dates equal the miners' calendar after dropping 2020-10-01.
- ewj_oc_jpy is NaN if and only if ewj_oc is NaN.
- usdjpy_us_ret == 0.0 if and only if us_n_sessions == 0, and it is finite otherwise.
- Every early-close date is a date in Book2's US calendar.
- gotobi_day sums to 529 on dev rows per ticker and 319 on sealed rows per ticker.
- Every staleness value and bar count is ≥ 0.
- The XAU and Japan 225 windows use exactly the usdjpy window instants.
- The session close is 15:30 JST exactly when t ≥ 2024-11-05.

**Unit tests**, on synthetic minute bars and calendars with known answers, covering:
- the dark-window bounds, including the 2024-11-05 close change;
- the price-at-instant rule;
- the session-FX window, by day t;
- NY DST transitions;
- NYSE early closes;
- nights with no US session;
- endpoint staleness;
- gotobi on the four month-crossing cases (B′), on February, and on a month whose 30th and 31st both fall on a weekend;
- the 1306 dividend-adjusted gap identity;
- ao_topix_gap_tradj on an ex-date;
- the string round-trip leaving old columns byte-identical.

### P2-3a Drafts for the switch commit (write them; apply nothing)
Write the following into docs/P2_switch_drafts.md:
- the schema.py diff per P50:
  - the new group PRE_OPEN_ROBUSTNESS, appended to GROUPS;
  - CONTEMPORANEOUS populated;
  - PROVENANCE, AT_OPEN and TARGET_INPUTS extended;
  - a test pinning PRE_OPEN_FEATURES and M7's feature list;
- targets.HEDGE_GAP_FOR += {y_1306_oc: ao_1306_gap_adj}; io registration of y_1306_oc; the blind.FX_NAMES list (P52);
- the spec amendments, as exact old/new lines in SPEC_AMENDMENTS JSONL form:
  - AM-03: the hedge column;
  - AM-04: both panel hashes, filled after P2-4;
  - AM-05 and AM-06: skeletons that meet P56, with their content marked ⟨decided at the checkpoint⟩;
- DATA_DICTIONARY.md for the 60-column panel;
- the complete test-change table: addendum §5 plus anything else found.

### P2-4 Rebuild into OUT/p2_<UTC stamp>/
Acceptance criteria. STOP on any failure.
- (a) The dev 41-column projection hashes to 736636031ca1…, computed in memory.
- (b) The sealed 41-column projection hashes to 9c18a6c10635…, computed in memory. Print the boolean only.
- (c) The sealed dates equal calendar.confirmation_calendar() (1,019). The dev dates are unchanged (1,708).
- (d) Rows: dev 5,124 and sealed 3,057; 60 columns in both.
- (e) New-column coverage is consistent with P2-1 and B′:
  - 1306 present on every row;
  - the NaN and 0.0 rules hold;
  - the gotobi counts match;
  - Japan 225 is fresh ≥ 95% from 2018-07;
  - XAU is nearly complete.
  - Sealed side: counts and booleans only.
- (f) Every original build assertion passes; they run inside the frozen build.
- (g) Every new build-time assertion passes.

Report counts, spans, hashes and booleans. Report nothing else from the sealed file.

### P2-5 Dev checks on the fresh dev panel (standalone scripts in tools/; reports only)
Each script must:
- verify the fresh MANIFEST's dev-panel hash;
- load only the columns listed below;
- assert that no predictor column is in its frame.

The checks:
- **A7 on 1306** (the P17/P18 rule).
  - Columns: date, ticker, y_oc, y_1306_oc, earn_flag, news_flag.
  - The same evaluation rows and windows {60, 120, 250, 500, expanding}, with β on non-excluded rows.
  - Two tables: (a) β on all rows; (b) the decision table, on common rows.
  - Write reports/A_hedge_efficiency_1306.md. The TOPIX report stays unchanged.
  - STOP and flag if expanding is not lowest on common rows for every ticker.
- **Index-staleness test** (P55).
  - Columns: date, ticker, ao_topix_gap, ao_topix_gap_tradj, ao_1306_gap_raw, ao_1306_gap_adj, exdiv_day. One row per date.
  - 1306 ex-dates are the dates where ao_1306_gap_adj ≠ ao_1306_gap_raw.
  - Sample (i): dev dates with no miner ex-day and no 1306 ex-date, using ao_topix_gap.
  - Sample (ii): all dev dates, using ao_topix_gap_tradj.
  - Report: b_IE, b_EI, R², N, the bracket [b_IE, b_IE/R²], and the reverse slope's 95% CI with Newey–West SEs at the spec's lag rule (T = number of dates).
  - Read the result per P55.
- **1306 evidence for P18 (D8):**
  - the dividend and split consistency (from P2-1);
  - the share of dev dates with ao_1306_gap_raw == 0, next to the same share for ao_topix_gap (gap-only).
- **Japan 225 eligibility** under the proposed P42 rule (both endpoints ≤ 5 minutes stale): dev counts by half-year; confirmation counts only.

Write reports/P2_5_dev_checks.md. Then **STOP for the decision checkpoint.**

### P2-3b Switch commit (only after Isaiah approves at the checkpoint)
Make one commit containing:
- schema, targets, io and the blind list;
- the approved AMs: spec lines plus SPEC_AMENDMENTS JSONL;
- DATA_DICTIONARY;
- the approved test changes;
- the panel switch:
  1. move DATA/panel_dev.csv to DATA/archive/panel_dev_736636031ca1.csv;
  2. copy the fresh dev panel to DATA/panel_dev.csv;
  3. leave the sealed panel in OUT.

The full suite must be green (skipped=5).

Then run the C7 slow tier once, in foreground chunks.
- Expected: every stored replication is identical to the previous report's, field by field; the summary is identical; only key.spec_sha256 changes.
- Any other difference: STOP.

### P2-6 Records
- Draft decision entries P58 onward, for Isaiah.
- Update DATA_PROVENANCE (the build) and PASS2_INPUTS.json (the new hashes).
- List the Project uploads: the new panel_dev.csv, MANIFEST.json, the updated docs and the build code. Never a sealed panel or a raw file.

### P2-7 Final suite and status
- Run the full suite: skipped=5, nothing else.
- Write the final PASS2_STATUS.md, with the attestation, the open flags, and the next actions for Pass 3: the cost inputs, the one sealed-fit sanction, and the calibration decisions.
````

---

## Appendix B′: reference numbers (replaces Appendix B)

**Samples and fixed constants**

| Quantity | Value | Source |
|---|---|---|
| Dev | 2015-01-06 → 2021-12-30; 1,708 dates; 5,124 rows; SHA-256 `736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42` | MANIFEST |
| Confirmation | 2022-01-04 → 2026-03-05; 1,019 dates; 3,057 rows; SHA-256 `9c18a6c106356139a375ecd7b3e6eaa085d937341c02817021003a4451c6b826` (pre-rebuild) | MANIFEST, P10 |
| T_conf | 1,013. The 6 dates with all three tickers excluded: 2022-02-09, 2022-08-09, 2024-08-08, 2025-02-13, 2025-08-08, 2025-11-11 | calendar.py |
| Dev exclusion rows | excl_inference 182; excl_d2 273; excl_forecast_eval 175; 774 rows without β | A5 |
| A6 constants | Winsor usdjpy [−1.6482588843e−02, 1.4399911615e−02]; eurusd [−1.6324806371e−02, 1.5438152188e−02]; rv_per_bar median 1.2950114214e−08 | spec |
| A7 (TOPIX hedge; bp²) | All-rows β, expanding: 24,052 / 11,662 / 17,750 (5706 / 5711 / 5713). Decision table on common rows, expanding: 24,030.2 / 11,639.9 / 17,983.9. No hedge: 29,603 / 15,855 / 22,955 | reports/A_hedge_efficiency.md |
| DK lag | 7 at T = 1,708; 6 at T = 983 or 1,013 | spec rule |

**Simulation and test results**

| Quantity | Value | Source |
|---|---|---|
| B7b preview | Size 6.04% [5.41, 6.73]; power 22.5 / 78.2 / 98.5% at b = 0.10 / 0.25 / 0.40; MDE80 0.257; SE/sd 0.960 | reports/B7b |
| C7 (rebuilt; P54) | CW size 3.00% (9/300) [1.59, 5.60]; power 100% (200/200) at b = 0.4; power 89.5% (179/200) [84.5, 93.0] at b = 0.25; same-panel H1 87.5% two-sided and 93.5% one-sided; CW rejects in 175 of 175 H1-significant runs; T_eval 1,012–1,013; lag 6 | reports/C7_mc.json |
| Test suite | 205 tests, OK, skipped=4 in the sandbox (229 s); skipped=5 expected on the Mac | 2026-10-05 run |
| Repo | HEAD `81905c1b576d24bdac2c96e2ab76429e0a1d24d1`; spec SHA-256 `9775a05ccf035c9ca3f769efe5e9ddaed068c1891b3de26940859f04fd7acae2`; no tags | 2026-10-05 |
| Sealed fits | 6 dev_real lines (B5 ×3; B7 ×2, one of them killed; B7b ×1) | BLIND_FIT_LOG |

**New inputs**

| Quantity | Value | Source |
|---|---|---|
| 1306 prices | 2,728 rows; calendar identical to the miners'; 6 coincidental stale rows | DATA_PROVENANCE §4.4 |
| 1306 dividends | 11 rows (7 dev, 4 confirmation). Dev corrected amounts in yen for 2015–2021: 2.30 / 2.73 / 2.60 / 3.05 / 3.33 / 3.29 / 3.66. Dev implied yields: 1.36 / 2.10 / 1.55 / 1.75 / 2.00 / 2.01 / 1.80% | DATA_PROVENANCE §4.4, P47 |
| XAU | 3,957,473 rows; 2015-01-01 23:00 → 2026-03-06 00:00 UTC; 4 outlier minutes, all kept | §4.2 |
| Japan 225 | 3,314,917 rows; 2015-01-02 00:00 → 2026-03-06 00:00 UTC. Fresh 08:59 share: 37% (2015-H1), about 0% (2015-H2 → 2018-H1), 97–99% after. Changeover 2018-07-02 | §4.3 |
| Gotobi (P48) | Dev 529 of 1,708 dates; by year 74 / 76 / 78 / 77 / 75 / 75 / 74. Confirmation 319 of 1,019. Month-crossing rolls: 2019-05-05→04-26, 2020-01-05→2019-12-30, 2021-05-05→04-30, 2025-01-05→2024-12-30 | §4.6 |
| NYSE early closes (P49) | 2015-11-27, 2015-12-24, 2016-11-25, 2017-07-03, 2017-11-24, 2018-07-03, 2018-11-23, 2018-12-24, 2019-07-03, 2019-11-29, 2019-12-24, 2020-11-27, 2020-12-24, 2021-11-26, 2022-11-25, 2023-07-03, 2023-11-24, 2024-07-03, 2024-11-29, 2024-12-24, 2025-07-03, 2025-11-28, 2025-12-24 | §4.6 |
| Panel after the rebuild | 60 columns: the 41 old ones unchanged plus 19 new ones | P50 |

**File hashes**

| File | SHA-256 | Source |
|---|---|---|
| build_panel.py (original) | `1fd59c0baa8de354053749cea91617f023a97bfa6d318e2287b4e1828b5b6b10` | PASS2_INPUTS.json |
| make_events.py | `3c0640fd4823e35a606780bbebfaeb7beefe40c28e388073352833fd6fdfdf31` | PASS2_INPUTS.json |
| events.py | `5180adf3c9750e86881d0275336ce898ed90ccc650195f2cb4df2e6e3ed135fa` | PASS2_INPUTS.json |
| events_firm.csv | `61b5629567dad37147078f4305d764587cd727fc45e257719158da3510984a4c` | spec |
| events_boj.csv | `8950b3c7add8b406727ed53b8e822153d67e343bfb65dc8f323328b0f372aa99` | spec |

---

## Appendix C′: supervisor attestation (chat of 2026-10-05)

All real-data contact in this chat:

1. **The test suite.** The rebuilt repo's default suite was run once on the Project's `panel_dev.csv`. These are Pass 1's own structural and target-only tests; `OFILT_RUN_SEALED` was unset, and `BLIND_FIT_LOG` was unchanged at 6 lines.
2. **A probe.** A comment-only spec edit was made on a scratch copy, and the C7 and spec tests were run on it. It read no data.
3. **Hashing.** Five uploaded files were hashed.
4. **The workbook.** The cell types of every sheet were counted; this loaded the price sheets, but none of their values was printed, summarised or used. The `1306 dividends` sheet was read (ex-dates, record dates, amounts; 2022+ as booleans against Nomura's published figures).
5. **Calendars.** Gotobi counts were computed from calendar data only: the dev panel's `date` column and the hard-coded confirmation calendar.

Nothing related any predictor to any target. No sealed value was read.
