# DECISIONS P93 onward: Pass 6, the confirmation run (2026-10-12; records written 2026-10-12)

This file continues `DECISIONS_P88_onward.md` (P88–P92), which continues `DECISIONS_P82_onward.md` (P82–P87), `DECISIONS_P71_onward.md` (P71–P81), `DECISIONS_P58_onward.md` (P58–P70), `DECISIONS_P37_onward.md` (P37–P57), `DECISIONS_P14_onward.md` (P14–P36) and `DECISIONS_ADDENDUM.md` (P01–P13).

Status vocabulary: as in `DECISIONS_P58_onward.md` (ADOPTED, ADOPTED PENDING, PROPOSED, EDITORIAL).

**The governing record is the Pass 6 decision log** (`PASS6_STATUS.md`, Decision log). It holds:
- P6Q1 to P6Q13, with their clarifications;
- the two criteria files and the two sanctions;
- D2 and its seven conditions;
- the acceptances.

Each entry below summarises one group of those decisions; where wording differs, the log governs. The evidence for each entry is in the files it names. P6-2 pins this file, and the Pass 5 decision file, in `tests/test_docs_p2.py` (P99).

**Status index (2026-10-12).** Later entries resolve or supersede parts of earlier ones. The earlier text is left exactly as adopted.

## P93. The Pass 6 standing prompt, P6Q1 to P6Q13, and their clarifications (ADOPTED; P6-boot, P6-0)

- **The standing prompt.** `files/pass6/PASS6_BUILDER_PROMPT_2026-10-12.md`, written from handoff H11, was adopted by the P6-boot paste together with P6Q1 to P6Q13. It covers:
  - the items;
  - checkpoints only at critical junctures;
  - the confirmation path;
  - nothing in code, tests or Appendix A changed before the run;
  - the sanction, the gate and the run's commit;
  - §7.6's test changes;
  - `git_dirty` and `ACCESS_LOG`;
  - the records, P92's refresh and the process rules.
- **P6-boot** checked REPO against H11's manifest byte for byte, checked Appendix A at HEAD and at the tag, and found the same four registry and `ACCESS_LOG` tests as the supervisor.
- **The clarifications of P6-boot's readings, recorded at P6-0:**
  - hard rule 1's "dev value" means a dev first-look result, or a quantity relating a predictor to a target on dev;
  - §7.6's test changes are recorded both as test changes and as deviations "pre-stated by §7.6";
  - the sanction names HEAD as it was when the sanction was written;
  - P6-1's message restates the gate's criteria;
  - P6Q3's "REPO's guard" means `io`'s.

## P94. The first criteria file and the first sanction (ADOPTED; P6-0, P6-1)

- **The criteria file.** `docs/P6_RUN_CRITERIA.md`, version 1, SHA-256 `ac973a1e6da258c0e48c4296ff83f0103c3a6dd13ad08d4c258b7844a4f902a0`, was written by the supervisor and committed before the run (P6-0, `cd2344e8…`). It fixes:
  - the sanction's form;
  - the gate (G1 to G11);
  - the post-run checks (P0 to P8);
  - part 2, with the first kit of §7.6's test changes, by SHA-256. That kit was never installed.
- **P6-0's four readings,** answered at P6-1 within the file's words: the three path lines, the tool's own output file, `ROW_IDS` by import, and part 1's order.
- **The first sanction.** `docs/P6_SANCTION.txt`, SHA-256 `123ad81ecd591796749daa25b8a78c25bdaf18a90dc25bd4f92f5dcd09d83cbe`, dated 2026-10-12. It names `cd2344e8…` and the three sanctioned hashes.

## P95. The first request of the confirmation panel, and its failure (ADOPTED; P6-1, P6-1b)

- **The run.** At the gate's commit G (`221507d01547869376e73cde51c20b86892bed95`), after every check had held (GATE CHECK's 59 checks; 398 tests, `OK (skipped=6)`), the builder ran the pre-registration's §7.4 command once, verbatim.
  - The dev panel and the events loaded and verified.
  - The guard granted `prereg-v1` and logged one GRANTED line (2026-10-12T23:38:45Z).
  - `io` then failed with `FileNotFoundError` when it tried to open `OFILT_DATA_DIR/panel_confirm_SEALED.csv` to hash it.
  - No byte of the sealed panel was read, and nothing was computed. No registry line and no output were written.
- **The opening counts (§7.5).** Its `ACCESS_LOG`, SHA-256 `c6eb0d5ecf89f2f6b705488c71b0c281154ba94008755731739a7c0ffadfbc03`, was committed unchanged by P6-1b (`3251106a…`).
- **The cause, from the records.**
  - Pass 2 left the sealed panel in `build_out/p2_20261006T002928Z/` by design (`PASS2_STATUS.md`, P2-6), and no later item placed a copy in the data folder.
  - The first criteria file had no presence check.
  - This was the supervisor's planning omission, not a builder's error.
- **P6-1's D1 was accepted** as a minor procedural deviation with no effect: a `sed -i` on a `/tmp` script during the gate's checkpoint.

## P96. D2: one second attempt (ADOPTED; P6-1b)

- **The decision.** Isaiah decided one second attempt as a labelled deviation from §7.5's one-shot rule, under seven conditions:
  1. the code, the configuration and Appendix A unchanged;
  2. the sealed panel placed by Isaiah and its hash verified;
  3. the first log renamed with its bytes unchanged;
  4. a revised kit of §7.6's test changes installed before the second run;
  5. a stat-only presence check;
  6. a second sanction;
  7. the first request reported beside the result.
- **The ground.** The first request read nothing of the confirmation sample, so the second cannot be informed by it.
- **Not chosen:**
  - no second attempt, with the confirmation recorded as not obtained;
  - a change to the script's one-shot check.
- **P6-1b's first message** stopped at a.4 on a supervisor's check error. The report form ends with the git status line, which was `?? ACCESS_LOG`. The message was re-issued with the check corrected; nothing in REPO changed in between.

## P97. The second attempt's preparation (ADOPTED; P6-1c)

- **The rename (D2 condition 3).** `git mv ACCESS_LOG reports/P6_runs/attempt1/ACCESS_LOG`, made in its own commit (`655b1af42830ac59af113b80c35d9ada08c5787c`, R100), with the bytes `c6eb0d5e…` unchanged. It supersedes hard rule 3 for that one file only.
- **The revised kit (D2 condition 4),** installed before the second run.
  - `tests/run_state.py` (new) pins the first log by path, SHA-256 and head.
  - It covers the four tests of `test_docs_d3b`, `test_p4_confirm_forecast` and `test_p4_confirm_run`.
  - Each test keeps its earlier assertion for the state before the second request.
- **The second criteria file.** `docs/P6_RUN2_CRITERIA.md`, SHA-256 `8a802f2953a7912b201b7d4deda45b70c844b8a8ba666235e96c57a465fbfc52`. It fixes:
  - the placement command and the eleven-line second sanction;
  - the presence check: `os.stat` of the one panel path, made twice;
  - the gate (G1 to G12), the post-run checks and part 2.
- **The checkpoint.** `checkpoint: P6-1c` (S2, `69d4ba2d414a6802ca22293f4ec6e0b724589e91`) ran 398 tests, `OK (skipped=6)`.

## P98. The confirmation run, at the second request (ADOPTED; P6-1d)

- **The placement and the second sanction.**
  - Isaiah's command copied `build_out/p2_20261006T002928Z/panel_confirm_SEALED.csv` into the data folder. It checked the SHA-256 `b575272aad752b3af84abe109fa66edde421f7c99184c9d1885bacdce64f06d1` (AM-04) and the build's `MANIFEST.json`, and printed hashes only.
  - The second sanction is `docs/P6_SANCTION2.txt`, SHA-256 `44021289dab169c757a426c037b8d1e7a1d5e782858aafe60fb333d57360ff32`, dated 2026-10-12.
- **The gate.** G2 (`1da6164024856b4bce437e6414862a9a7da174f3`) passed 64 checks, including the presence check twice, and 398 tests, `OK (skipped=6)`.
- **The run.** The pre-registration's §7.4 command ran once, verbatim, on 2026-10-13 from 02:35:01 to 02:40:56 UTC (354.6 s), and exited 0.
  - The outputs, in `reports/P6_runs/confirm/`:
    - `document.json` `8e24fa53fdbabd90a1f5768f1ab6fda603d45d0e7deaf347ef098b9166b03a19`;
    - `manifest.json` `a56e18247c197fa8985563809cf7999070904588a4808ee201d7bd84c42bd06d`;
    - `runtime.json` `f7b002fa9e8d7815a08e3fbe72213281f5aa4105449df66afbedbe3b111ede1b`.
  - `ACCESS_LOG` `ec003f2c9a47d84f3aa1b193ba5ee5e23bc582c5ae21edbb398fba85c64f4667` holds one GRANTED line at G2.
  - `RUN_REGISTRY.jsonl` `89d669cac68fa88df98041c78a06cede9c680a640b3c8bfd90a091b2c32777df` now has 4 lines. The two new ones are `673153b9e4484516b29265cdbcd145e9` (main) and `c8547454ec1644099a22c79d633afbc7` (m7), both `confirm_real` at G2, with `git_dirty` False then True.
  - POST CHECK passed all 49 checks.
- **The commit.** `checkpoint: P6-1d part 2` (`619bf39be5f324b95135bdabf6830de20d9cc7ab`) ran 398 tests, `OK (skipped=6)`, and holds the six files.
- **The claim rows, as the code reports them.** This is a record, not the write-up.
  - **H1 not rejected:** b̂ = 0.0954, DK SE 0.0946, p = 0.313, over 1,013 dates and 2,955 rows. R10 is not claimed, R11 is not claimed, and R12 makes no tier (iii) claim.
  - **R21.** The null is read against MDE80 = 0.2471.
  - **R14, claimed: "no drift exploitable net of costs".** TOST is equivalent at the primary SESOI 0.8652 and at the high SESOI 2.719, and not at the low SESOI 0.07152.
  - **R20.** H1 and the Clark–West test agree: M3 against M2, p = 0.424, not rejected at the calibrated value.
  - **R25** is not applicable; the forward holdout is evaluated separately (§8).
- **O45, the economic evaluation.** Its primary and high cost cases failed: "traded price 32210.0 exceeds the table's last bound 30000". Only the low cost case is computed. O45 is context and carries no claim (§4.6). The write-up must report the failure (Flag F6-2).
- **Both requests are on record.** The write-up reports the first beside this result (D2 condition 7).

## P99. Pass 6's records, P92's refresh, and Pass 6 closed (ADOPTED; P6-2)

- **P6-1d accepted.** The run's facts (P98) are recorded in `PASS6_STATUS.md`.
- **P92's refresh,** made after the run as P6Q11 decided:
  - `docs/replacements/PLAN.md` v2.7: the status block, §8 rows 4 to 6 and the change log;
  - `docs/DATA_PROVENANCE.md` §4.5: the Pass 5 and Pass 6 entries;
  - `docs/replacements/README.md`: its status block (F5-2) and the pass table;
  - `docs/replacements/PROJECT_SETUP.md`: the upload lists for after Pass 5 and after Pass 6;
  - the pins in `tests/test_docs_p2.py`, `test_docs_d4.py` and `test_docs_d6.py`, including this file and `DECISIONS_P88_onward.md`.

  Each pin move is a labelled documentation-pin deviation (P13(c)), made after the run and touching no computation.
- **Pass 6 is closed.** Next come the write-up (§7.7: every row, in §4's wording, with both requests reported) and the forward holdout (§8), each under its own plan, from handoff H12.
