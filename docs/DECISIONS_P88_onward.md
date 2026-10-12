# DECISIONS P88 onward: Pass 5, the pre-registration and the tag `prereg-v1` (2026-10-12; records written 2026-10-12)

This file continues `DECISIONS_P82_onward.md` (P82–P87), which continues `DECISIONS_P71_onward.md` (P71–P81), `DECISIONS_P58_onward.md` (P58–P70), `DECISIONS_P37_onward.md` (P37–P57), `DECISIONS_P14_onward.md` (P14–P36) and `DECISIONS_ADDENDUM.md` (P01–P13).

Status vocabulary: as in `DECISIONS_P58_onward.md` (ADOPTED, ADOPTED PENDING, PROPOSED, EDITORIAL).

**The governing record is the Pass 5 decision log** (`PASS5_STATUS.md`, Decision log: P5Q1 to P5Q19, "P5Q3 clarified", the acceptances, the tag and the OSF registration). Each entry below summarises one group of its decisions; where wording differs, the log governs. Evidence is in the files each entry names and in `reports/P5_reports/`, which holds every builder report of Pass 5 (P5-4's report follows at Pass 6's first item).

**Unlike earlier decision files, this one is not pinned by a test (P92).** Its SHA-256 is recorded in `PASS5_STATUS.md`'s Decision log, and Pass 6 pins it when it refreshes the pinned documents.

**Status index (2026-10-12).** Later entries resolve or supersede parts of earlier ones. The earlier text is left exactly as adopted.

| Earlier entry | Current status |
|---|---|
| P36 step 6 and PLAN §8 (Pass 5), "advisor sign-off → tag `prereg-v1`" | Met in the acting-advisor sense only (P90). There was no independent advisor review, as the pre-registration's §9.9 discloses |
| P13(c), the one-shot rule | Fixed in the pre-registration's §0 and §7, and in code: `tools/p6_confirm_run.py` refuses while `ACCESS_LOG` exists (P89) |
| P13(a) and P4Q30, the forward holdout | Fixed: the pre-registration's §8 (P90) |
| P85 and flag F4-3, the pre-registration's wording of b's reading | Worded: the pre-registration's §4.4. F4-3 closed (P90) |
| P86, `git_dirty` | Carried into the pre-registration's §7.6 |
| PLAN §8, Pass 5 | Done: `prereg-v1` on `8341ffd930caea6e0327e8fcac90fc2e34652962`, and the OSF registration `osf.io/3mr5h` (P91) |

---

**P88: Pass 5's process (ADOPTED (Isaiah, 2026-10-12, each on the supervisor's recommendation; P5Q1 to P5Q10, P5Q3 clarified)).**

- **The standing prompt.** `files/pass5/PASS5_BUILDER_PROMPT_2026-10-12.md` (SHA-256 `0398c3c7…`) was adopted by the P5-boot paste and retired the Pass 4 prompt. P5-boot was read-only. It checked REPO against the H10 snapshot's manifest, byte for byte, and the builder independently found the same four tag-dependent tests as the supervisor.
- **Checkpoints only at critical junctures (P5Q2).** A full suite runs only:
  1. before a change to code or tests beyond documentation pins;
  2. right before and after a real-data run or sanction gate;
  3. before a tag, and after it where tests depend on it;
  4. at a pass's close, if no suite has run since the last code change.

  Everything else is committed after the documentation test modules. Pass 5 ran three suites, at P5-1, P5-2 and P5-3: `Ran 398 tests`, `OK (skipped=6)` each time.
- **The sealed panel (P5Q3, as clarified on 2026-10-12).**
  - `io.load_confirm` runs only in tests.
  - The guard is a throwaway repository, never REPO's own guard, or the function is replaced by a recorder.
  - The data path lies inside a new temporary folder that holds no data file, and the log is temporary.
  - A throwaway repository may carry stand-in tags, so that the grant path is tested.
  - The clarification followed P5-1's first run, which stopped correctly on the earlier, narrower wording. The cause was the supervisor's wording.
- **Records (P5Q7).** `PASS5_STATUS.md` was opened at P5-1, and `PASS4_STATUS.md` was closed. P5-4 amends the pin clause (P92).

**P89: The confirmation script and the both-sides tag tests (ADOPTED (Isaiah, 2026-10-12, on the supervisor's recommendation; P5Q4, P5Q5, P5Q15, P5Q16; `docs/P5_CONFIRM_SCRIPT_SPEC.md`, version 1)).**

- **`tools/p6_confirm_run.py`** (SHA-256 `5b3922d7…`) is the script that will open the confirmation panel. It was written before the tag, so that the pre-registered script is the one that opens it (P13(c)).
  - It refuses an existing `--out`, a missing sanction (`OFILT_P6_CONFIRM_RUN=P6-1`) and an existing `ACCESS_LOG`.
  - It loads the dev panel and the events first, then the confirmation panel through the guarded `io.load_confirm`.
  - It assembles the document with the unchanged `confirm_run`.
- **Its seven tests** include an equivalence check: the same synthetic frames through this script and through the dev run's script give byte-identical `document.json` and `manifest.json`. The dev run's script and every shared module are unchanged.
- **The tag-state tests.** The four tests that failed with `prereg-v1` present now assert both sides of it:
  - `test_docs_d3`'s `test_tag_gates`;
  - `test_docs_d3b`'s `test_tag_semantics_as_implemented`;
  - `test_io`'s `test_denied_and_logged`;
  - `test_p4_confirm_run`'s test 8.

  `tests/tag_state.py` gained `prereg_tagged`, `check_prereg_tag` and `io_blinded`. `tests/test_p5_tag_state.py` exercises the tagged side on throwaway repositories.
- **The supervisor wrote and sandbox-checked every file, and the builder installed them by `cp -p`** (P5-1). The suite grew from 386 to 398 tests.

**P90: The pre-registration (ADOPTED (Isaiah, 2026-10-12, on the supervisor's recommendation; P5Q6, P5Q11 to P5Q14, P5Q17, P5Q18)).**

- **The document.** `docs/PREREG_v1.md` (SHA-256 `79447ba199ce2360fb1fc8c51ae5d0eea3c20ba2645d6167c17ba1e1792f35e6`), drafted by the supervisor chat. It fixes:
  - the computation, by reference to the code and configuration at the tag (§0; Appendix A, 40 files by SHA-256);
  - the readings and claims and their wording (§4): tier (i); tier (ii) and the reading of its failure; no tier (iii); the null against MDE80; the joint reading of significance and equivalence; b's qualifier with S1 to S3 (F4-3, closed); the borderline rule at the size-adjusted critical value 2.0041;
  - power from the design (§3);
  - the Pass 6 run note (§7: preconditions, sanction, gate, command, crash rule, `ACCESS_LOG`, `git_dirty`);
  - the forward holdout (§8: H1 only, 2026-03-06 to 2026-09-30, never pooled);
  - the disclosure (§9, the dev first look's numbers among them).
- **Its review.** `docs/PREREG_v1_REVIEW.md` (SHA-256 `74d149f5…`) is an advisor-style review by the same supervisor chat. It recommends sign-off, and it is not independent.
- **The sign-off.** Isaiah signed off as acting advisor (P5Q11) by the P5-2 paste. P36 step 6's advisor sign-off is met in that sense only, and the document discloses that no independent advisor reviewed it (§9.9).
- **The decisions file P01 to P13.** `docs/DECISIONS_ADDENDUM.md` (P01–P13), until then only in the Project, was added to the repository byte for byte (P5Q18). So the tagged commit holds every decision file.
- **The rehearsal.** Before the tag, the tag-dependent tests ran in a clone of the commit to be tagged, carrying a local annotated `prereg-v1`, with no remote and an empty data folder: 25 tests, `OK (skipped=1)`. P5-3 then ran them with the tag present in REPO.

**P91: The tag and the external registration (ADOPTED (Isaiah, 2026-10-12)).**

- **The tag.** Isaiah created the annotated tag `prereg-v1` in Terminal, after the supervisor's review of P5-2, with a guarded command, and pushed it to GitHub.
  - Tag object: `148b742e097c0ed6945992b7707d928ad21b4d37`.
  - Commit: `8341ffd930caea6e0327e8fcac90fc2e34652962` (`checkpoint: P5-2`).
  - Tagger time: 2026-10-12 15:31:27 −04:00. The tagger identity is the repository's local git identity (`ofilt-pass1`); the message names the sign-off.
  - From the tag on, the guard grants `confirm_real`. Every change to code or tests is a dated, labelled deviation (P13(c)). The confirmation panel is opened only by Pass 6's sanctioned run.
- **The external registration.** Isaiah filed an embargoed OSF registration (Open-Ended template), `https://osf.io/3mr5h`, on 2026-10-12.
  - It holds the pre-registration, its review, the repository's tracked tree at the tag (`git archive`), and a hash file with the tag object, the commit and the documents' SHA-256.
  - The embargo is to end on or before 2030-10-01; it can be ended early.
  - The pre-registration's §7.1 precondition (filed and its identifier recorded before the Pass 6 sanction) is met by this entry.

**P92: The pinned documents left for Pass 6 (ADOPTED (Isaiah, 2026-10-12, on the supervisor's recommendation; P5Q19)).**

- **Why.** `tests/test_docs_p2.py` pins `docs/replacements/PLAN.md`, `docs/DATA_PROVENANCE.md`, `docs/replacements/PROJECT_SETUP.md` and `docs/replacements/README.md` byte for byte. After the tag, refreshing any of them, or pinning a new document, would change a test, and that is a labelled deviation (P13(c)) before the confirmation is run.
- **What Pass 5 does instead.** Its record lives in files no test reads: `PASS5_STATUS.md` and this file, whose SHA-256 `PASS5_STATUS.md` records.
- **Deferred to Pass 6's records,** together with the test changes Pass 6 needs anyway by decision (the `ACCESS_LOG` the run creates; flag F5-1):
  - PLAN v2.7;
  - DATA_PROVENANCE §4.5's Pass 5 entries, carried until then in `PASS5_STATUS.md`'s Disclosure list;
  - README's status block (flag F5-2);
  - PROJECT_SETUP's upload list (given meanwhile in the Pass 5 supervisor handoff);
  - this file's pin.
- **What it supersedes.** P5Q1's scope of P5-4, and P5Q7's clause "pinned in `tests/test_docs_p2.py` when written (P5-4)".
- **Not chosen:** refreshing them now as labelled documentation-pin deviations. That would put the first deviations against the pre-registration on record before the run, and gain nothing.
