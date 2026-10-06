# DECISIONS P58 onward: the Pass 2 build, the decision checkpoint and the switch (2026-10-05; records refreshed 2026-10-06)

This file continues `DECISIONS_P37_onward.md` (P37–P57), which continues `DECISIONS_P14_onward.md` (P14–P36) and `DECISIONS_ADDENDUM.md` (P01–P13).

Status vocabulary:
- **ADOPTED** (Isaiah, date)
- **ADOPTED, PENDING** a named check
- **PROPOSED** (awaiting Isaiah)
- **EDITORIAL** (naming only; no methodological content)

Every entry restates the Pass 2 decision log (`PASS2_STATUS.md`, Decision log), quoting it verbatim where marked. Evidence is in the reports named in each entry, in `DATA_PROVENANCE.md` §4–§5 and in `PASS2_STATUS.md`. Hashes are in `PASS2_INPUTS.json` and `MANIFEST.json`.

**Status index (2026-10-06).** Later entries resolve or supersede parts of earlier ones; the earlier text is left exactly as adopted.

| Earlier entry | Current status |
|---|---|
| P39 (b), settings check | Resolved by attestation, P60 (D2). Not by a re-pull, and never "reproduced" |
| P40, TOPIX total-return ticker | Resolved: TPXDDVD Index, P60 (D3) |
| P42, Japan 225 usage rule | ADOPTED, P63 (D7). Coverage restated on the miners' calendar (DATA_PROVENANCE §4.3) |
| P10, sealed hash | Superseded by AM-04, with the hybrid old-column sources (P59, P67) |
| P51, "every replication bit for bit", for the C7 rerun | Replaced by the D16 criterion (P68) |
| P39 and PASS2_HANDOFF §5.1, "13.6–21%" | Holds for dev ex-dates only; the 2022+ boolean is False (P62; DATA_PROVENANCE §4.4) |
| P41, "Gaps only at weekends and the Christmas and New Year closures" | Also the 11 Good Friday closures, 2015–2025 (P62; DATA_PROVENANCE §4.2) |
| P48, "Its exact design is set in AM-06"; P56, "Every robustness amendment (AM-05, AM-06)" | Every Pass 2 robustness row is in AM-05, including `mechanism_session_fx_gotobi`; the id AM-06 is unused (D12; P67). This applies to every mention of AM-06 in PASS2_HANDOFF.md and PASS2_ADDENDUM.md |
| P49, "`usdjpy_us_ret` = 0.0 exactly when `us_n_sessions` = 0" | Amended: 0.0 wherever `us_n_sessions` = 0, and finite wherever it is > 0; 4 dev and 2 confirmation nights with sessions sum to exactly 0.0 (P61) |
| P51, "the frozen original build must reproduce `7366…` and `9c18…` on the Mac" | Not met, because of Flag 16, and explained; replaced by Isaiah's Mac-baseline acceptance, `656d5117…` / `138e5e21…` (P58) |
| P56, whether yen-denominated EWJ is also a tier-(ii) check | Decided with D7: a robustness row, not a tier-(ii) check (P63) |

**Amendments to PASS2_ADDENDUM recorded here** (the addendum stays unedited):
1. A′ paths: "FX Project" → `FX_Project`, with KIT under `files/` (P58).
2. A′ environment: "Isaiah's venv (myenv)" → `~/venvs/ofilt_p2`; numpy ≥ 2 (Rule C amended; P58).
3. A′ P2-0b: the `7366…`/`9c18…` acceptance failed by Flag 16, and the failure is explained. The acceptance became "the repo's frozen build reproduces the Mac hashes" (True, True) (P58).
4. A′ P2-1: "amounts equal the RAW sheet ÷ 10 exactly" → the stored corrected amounts are used; in binary, RAW ÷ 10 differs in the last bit on 1 of 11 rows (P61, P62).
5. A′ P2-2: the assertion "usdjpy_us_ret == 0.0 if and only if us_n_sessions == 0" → the amended rule, plus the MANIFEST count (P61).
6. A′ P2-4 (b): `9c18a6c10635…` → `138e5e21…` (P59).
7. A′ P2-4 (e): "Japan 225 is fresh ≥ 95% from 2018-07" → the half-year table of DATA_PROVENANCE §4.3, which the P2-4 panels reproduce in every half-year (`reports/P2_4_acceptance.md` (e)) (P62).
8. B′ rows: Japan 225 restated (DATA_PROVENANCE §4.3). The test suite has 238 tests at P2-2 (246 after the switch, P67). "Repo… no tags" → `pass1-final` (P69).
9. Every mention of AM-06 (§1, §4, §5, A′ P2-3a): the Pass 2 robustness rows are all in AM-05, and the id AM-06 is unused (P67).

---

**P58: Pass 2 environment and Flag 16 (ADOPTED (Isaiah, 2026-10-05; Rule C and the dev comparison on the supervisor's recommendation)).**

*Decision log, verbatim:*

> - Environment (Isaiah, 2026-10-05): Pass 2 runs in ~/venvs/ofilt_p2 (macOS arm64, Python 3.12.4), pinned to the library versions of a Claude sandbox on 2026-10-05; the certification environment's versions are unrecorded. Suite: 205, OK, skipped=5. The suite needs numpy 2 or later (test_models_c3.py:68 fails on numpy 1.26).
>
> - (Isaiah, 2026-10-05, on the supervisor's recommendation) Rule C amended: ofilt_p2 is the Pass 2 environment, because the build mismatch is identical in every Mac environment. conda myenv is not used again.
>
> - (Isaiah, 2026-10-05, on the supervisor's recommendation) The dev comparison of the Mac rebuild against the Pass 1 dev panel was approved (dev only), with its EXPLAINED rule fixed in advance. Result: EXPLAINED.
>
> - P2-0b acceptance (Isaiah, 2026-10-05; replaces A′'s): rows 5,124 / 3,057 and spans as in MANIFEST; the frozen build's dev output hashes to 656d5117a7d0027f7ba7d2cc8d16236fcc9258af384363c8be4577ce15933bd4 and its sealed output to 138e5e2104d5ebf6e9616edc55ca00f548e38be604365bd47932e1716f4d9d19. Any mismatch: STOP. On success the EXPLAINED dev comparison carries over, because the bytes are the same.

**Flag 16 (platform floating point),** as recorded in PASS2_STATUS:

> 16. Platform floating point: the original panels were built on x86_64 with AVX-512; Mac rebuilds differ in the last bit (both Mac environments give identical panels); the B6 report differs under both Mac BLAS libraries.
>     - Evidence (supervisor, 2026-10-05): the original dev panel's ao_gap_raw equals numpy's AVX-512 SIMD float64 log on all 5,124 rows and differs from the C-library log on 223 rows, by 1 ulp each.
>     - Evidence (builder): Mac rebuild vs the original dev panel, ao_gap_raw differs as strings in 222 cells, max 1 ulp; dev comparison EXPLAINED. B6 diffs: under Accelerate, mean_b, sd_b and se_over_sd change in the last 1–2 digits; under OpenBLAS, also mean_se. Coverage 0.952 unchanged.

- **The dev comparison** (`OUT/diag_compare_20261005T204658Z/compare_dev.py`): the 23 non-log columns are string-identical; the 18 log-derived columns agree within 1e-8 relative, with the largest relative difference 2.273e-13; single-log columns differ by at most 1 ulp, and rv/bv by up to 1,876 ulps. **Verdict: EXPLAINED** (DATA_PROVENANCE §5.2).
- **P2-0b re-scoped.** The baseline run executed early as an environment diagnostic (D1). Under Isaiah's rule the frozen build reproduced the Mac baseline exactly: dev `656d5117a7d0027f7ba7d2cc8d16236fcc9258af384363c8be4577ce15933bd4`, sealed `138e5e2104d5ebf6e9616edc55ca00f548e38be604365bd47932e1716f4d9d19` (P2-0b ACCEPTED; checkpoint `090fc2198de2d9ea5f2591ff422cd79b565d6c92`).
- **`tools/checkpoint.sh`** carries the supervisor's D.2 additions (venv check and interpreter print; pre-suite status and diff hash; B6 restore or abort) and passes extra arguments as extra commit-message paragraphs. Implementation note, verbatim:

> - (P2-0e, implementation) `tools/checkpoint.sh` calls bare `python`, because `test_sim_b5` pins the literal `env -u OFILT_RUN_SEALED python -m unittest discover`. It therefore requires an activated venv (`VIRTUAL_ENV` set, and `command -v python` equal to `$VIRTUAL_ENV/bin/python`). Extra arguments after the item id become extra commit-message paragraphs, used for the commit attribution trailer.

- **B6 restoration.** Every suite run rewrites `reports/B6_coverage.json` (float noise; Flag 16). It is restored with `git checkout` or by `tools/checkpoint.sh`, which aborts on any other change.

*Evidence:* PASS2_STATUS (Progress, environment diagnostics D1–D4; Test results, dev comparison and P2-0b); DATA_PROVENANCE §5.1–§5.2; checkpoints `a102ed1753f20344bb9ec8ae73e37d73ab6d57e0` (P2-0) and `090fc2198de2d9ea5f2591ff422cd79b565d6c92` (P2-0b).

*Effect:* hashes prove identity only on the same numerical platform. A cross-platform rebuild is checked against a tolerance rule stated in advance. No record claims that the Pass 1 panels can be rebuilt byte for byte on the Mac.

---

**P59: Old-column sources: the hybrid (ADOPTED (Isaiah, 2026-10-05)).**

*Decision log, verbatim:*

> - Old-column source after Flag 16 (ADOPTED, Isaiah, 2026-10-05). The Mac cannot reproduce the original panel bytes (Flag 16), and the original sealed file (9c18…) is not available.
>   - Dev: the 41 old columns are the original panel_dev.csv (736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42), read as strings and hash-verified before use. P2-4 acceptance (a) is unchanged.
>   - Sealed: the 41 old columns come from the frozen build run on the Mac in ofilt_p2. Their reference is the Mac baseline hash 138e5e2104d5ebf6e9616edc55ca00f548e38be604365bd47932e1716f4d9d19. P2-4 acceptance (b) becomes: the sealed 41-column projection hashes to that value.
>   - Evidence of equivalence: the frozen code and every input are hash-verified; the dev comparison of the Mac output against 736636… is EXPLAINED (differences only in the 18 log-derived columns; largest relative difference 2.273e-13); rows, dates and spans are equal.
>   - Byte identity of the sealed old columns with 9c18… cannot be demonstrated; this is disclosed in the pre-registration. P10's hash is superseded by AM-04, as already planned.
>   - The P2-4 MANIFEST records the platform, the source of the old columns for each panel, and both reference pairs (736636… / 656d5117a7d0027f7ba7d2cc8d16236fcc9258af384363c8be4577ce15933bd4, and 9c18… / 138e5e2104d5ebf6…).

- The original sealed file (`9c18a6c1…`) is not available anywhere on the Mac.
- P2-4 acceptance (a), the dev 41-column projection hashes to `736636031ca1…`: True. Acceptance (b), the sealed 41-column projection hashes to `138e5e2104d5…`: True (`reports/P2_4_acceptance.md`).
- MANIFEST.json records both reference pairs: dev `73663603…` (original) / `656d5117…` (Mac frozen build); sealed `9c18a6c1…` / `138e5e21…`.

*Pre-registration disclosure* (carried below): byte identity of the sealed old columns with `9c18a6c1…` cannot be demonstrated; the sealed old columns come from the Mac frozen build; the dev comparison bounds the size of platform differences.

*Evidence:* `reports/P2_4_acceptance.md`; MANIFEST.json (`old_columns`); DATA_PROVENANCE §5.3; PASS2_INPUTS.json (`baseline_outputs`, `mac_frozen_build_outputs`).

---

**P60: Settings check by attestation; the TOPIX total-return series (ADOPTED (Isaiah, 2026-10-05); resolves P39 (b) and P40).**

*Decision log, verbatim:*

> - D2 / P39(b) (Isaiah, 2026-10-05): Book2.xlsx and the 1306 sheet of newbloombergdata_fixed.xlsx were both pulled with the JT suffix and the PASS2_HANDOFF Appendix E settings, per Isaiah's statement. The 1A cell-for-cell re-pull was not run. P2-1 proceeds on this statement.
>
> - D3 / P40 (Isaiah, 2026-10-05): the TOPIX total-return series is TPXDDVD Index. Records only.

- The adjustment settings are corroborated by the data for both files (DATA_PROVENANCE §2, §4.4; P47). The suffix itself cannot be identified from daily data. A 1A re-pull remains optional; if one is ever run and fails, D2's remedy applies (PASS2_HANDOFF §6, item 2).
- *Wording guard.* P39 (b) was resolved by Isaiah's statement, not by a re-pull. No record may say that a suffix "reproduced" or "matched" Book2.
- TPXDDVD Index is TOPIX's dividend-included (gross total-return) index; it is used only on the fallback path (P40).

*Evidence:* DATA_PROVENANCE §4.4 ("Resolved (2026-10-05)"); PASS2_INPUTS.json (`newbloombergdata_fixed.xlsx` status).

---

**P61: Build design, assertions and acceptance (ADOPTED (Isaiah, 2026-10-05; P2-4, the tool fix and the P2-5 details on the supervisor's recommendation)).**

*Decision log, verbatim:*

> - P2-2 design constraints (Isaiah, 2026-10-05; recorded now, no code until P2-2):
>   - build_panel_p2.py takes the original dev panel as an input path and verifies its hash is 736636… wherever it lives (after the switch commit it is DATA/archive/panel_dev_736636031ca1.csv). It uses that file's strings for dev's 41 old columns. For the sealed side it uses the frozen build's output, which must hash to 138e5e21…. It also asserts that the frozen build's dev output hashes to 656d5117…, so every run is shown to be the verified one.
>   - *.csv is git-ignored, so synthetic test fixtures must be generated inside the tests, never committed as CSV files.
>
> - P2-2 additions (Isaiah, 2026-10-05):
>   - Reuse the frozen helpers in build/pass1/build_panel.py by import; compute xau_* and n225_* with the frozen fx_windows; never edit build/pass1/; re-implement a helper only when it cannot be reused as is, and add a test of identical output to the frozen function on synthetic inputs.
>   - 1306 distributions use the stored corrected amounts of the `1306 dividends` sheet; RAW ÷ 10 is never recomputed.
>   - Build-time assertions: the number of NY sessions summed for usdjpy_us_ret equals the frozen build's us_n_sessions on every row; the XAU and Japan 225 window instants equal the panel's window_start_utc and window_end_utc on every row.
>   - MANIFEST.json also records platform.platform(), platform.machine(), sys.version and the SHA-256 of the original dev panel used as dev's old-column source.
>   - Unit tests compare log-derived values within an explicit tolerance, or use values exact by construction; never bit-identical floats across platforms (Flag 16).
>
> - P2-2 accepted (Isaiah, 2026-10-05).
>
> - usdjpy_us_ret assertion amended (Isaiah, 2026-10-05; replaces A′'s 'usdjpy_us_ret == 0.0 if and only if us_n_sessions == 0'): usdjpy_us_ret == 0.0 wherever us_n_sessions == 0, and finite wherever us_n_sessions > 0. Reason: on a night with US sessions the summed return is exactly 0.0 whenever the USD/JPY bid at the NY close equals the bid at the NY open, so the 'only if' half would fail on legitimate data. The zero-session nights stay pinned by the row-by-row check that the sessions summed equal us_n_sessions. MANIFEST reports, per panel, the number of nights with sessions whose sum is exactly 0.0 (a count).
>
> - XAU / Japan 225 ts_utc format (P2-2 flag, resolved by the supervisor): the registered pull_dukascopy.py (6d9464f8…) converts ts_utc to timezone-aware UTC before writing, the same form as the FX masters, so the frozen load_fx should read them. If not, P2-4 stops at load time; there is no silent path.
>
> - P2-4 accepted (Isaiah, 2026-10-05, on the supervisor's recommendation). Build build_out/p2_20261006T002928Z; MANIFEST git head 34f61dbb49a14bdb1965e20fab71ded33057509b (= checkpoint: P2-3a); dev 36f7dd69…, sealed b575272a… (full hashes in MANIFEST); old-column projections 736636… and 138e5e21…; 72 build assertions; acceptance (a)–(g) True. The committed reports/P2_4_acceptance.md stays the run-time record and is not regenerated.
>
> - Acceptance-tool fix adopted (Isaiah, 2026-10-05, on the supervisor's recommendation): in tools/p2_4_accept.py the check "MANIFEST git head is this checkout's HEAD" becomes two checks (the MANIFEST head is an ancestor of HEAD; build/ and docs/PASS2_INPUTS.json are unchanged from the MANIFEST head to HEAD), both heads printed; the tool writes reports/P2_4_acceptance.md only with an explicit --write-report flag, never used.
>
> - P2-5 operational details, fixed before any P2-5 script runs (Isaiah, 2026-10-05, on the supervisor's recommendation): as written in the supervisor message of 2026-10-05, item 2, including the P55 estimator (OLS with an intercept, centred R², Newey–West on the reverse slope), the one-row-per-date rule, the sample definitions, and the self-checks with their STOP rules.

- **Exact-zero US-session nights.** 4 dev and 2 confirmation nights have sessions whose summed return is exactly 0.0 (MANIFEST). All were verified as genuine equal bids: the sessions recomputed equal `us_n_sessions`, the recomputed sums are exactly 0.0, and every session's open and close resolve to distinct, fresh bars (`reports/P2_5_dev_checks.md` §2.4).
- **MANIFEST git state and the command-line refusal** (P2-2b, Isaiah, 2026-10-05). MANIFEST records `git rev-parse HEAD` and whether `git status --porcelain -- build/ docs/PASS2_INPUTS.json` is empty; the command line refuses to run when it is not. The P2-4 build ran on the committed tree: head `34f61dbb49a14bdb1965e20fab71ded33057509b` (checkpoint: P2-3a), clean True.
- **The P2-4 build:** `build_out/p2_20261006T002928Z/`; dev `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68` and sealed `b575272aad752b3af84abe109fa66edde421f7c99184c9d1885bacdce64f06d1`, 60 columns each; MANIFEST.json `1345c0772777b87e9d5fcc01794340231c04068f383330762e68ff3ef468e8bd`; 72 build assertions; acceptance (a)–(g) True.

*Evidence:* `reports/P2_4_acceptance.md`; MANIFEST.json; `reports/P2_5_dev_checks.md` §2.4; DATA_PROVENANCE §5.4; checkpoints `791a6b80c8e70f008cccd165d6abaf769f08e691` (P2-2), `564e254a6214c0cd1256ef978b6d9694392e95fa` (P2-2b), `b61f341133baac68580701119609cb85c423338a` (P2-4), `c7a369343af8301d2b98df35c97a976a94e92991` (P2-4b).

---

**P62: Input records corrected (ADOPTED (Isaiah, 2026-10-05): P2-1 accepted with its five mismatches to be corrected at P2-6; the 2.3 resolution on the supervisor's recommendation).**

*Decision log, verbatim:*

> - P2-0b accepted (Isaiah, 2026-10-05): the frozen build reproduced the Mac baseline exactly (dev 656d5117…, sealed 138e5e21…). P2-1 accepted: 27 of 32 comparisons match; the 5 mismatches are errors in DATA_PROVENANCE §4 / Appendix B′ (Japan 225 calendar convention and coverage wording; XAU Good Friday closures), to be corrected at P2-6. Supervisor cross-check (dev, gap-only): on all 7 dev ex-dates the dividend-adjusted 1306 gap equals the TOPIX gap within 0.24 pp, so the ÷10 factor holds in every year.
>
> - The 2.3 STOP is resolved (Isaiah, 2026-10-05, on the supervisor's recommendation). The supervisor's reference table was wrong, not the panel.
>   - Its 1306 column for 2017 and 2019–2021 was built from 2-decimal simple percentages (÷10 yield minus the ex-day open drop, from DATA_PROVENANCE §4.4). Its 2016 and 2018 values match no single definition.
>   - The panel's ao_1306_gap_adj equals the independent recomputation from the raw sheet to 1e-12.
>   - Corrected table (log gaps, %; 1306 / TOPIX): 2015-07-08 −0.30 / −0.41; 2016-07-06 −1.64 / −1.55; 2017-07-06 0.00 / −0.04; 2018-07-06 +0.78 / +0.55; 2019-07-08 −0.17 / −0.26; 2020-07-09 −0.13 / −0.09; 2021-07-08 −0.22 / −0.15. The largest difference is 0.23 pp. D8's conclusion (÷10 holds every year) is unchanged.

Corrections, made in DATA_PROVENANCE at P2-6 (P70):
- **Japan 225 restated on the miners' calendar** (§4.3). The 08:59 JST price is stale on every Tokyo day from 2015-H2 through 2018-04-12, fresh on every Tokyo day from 2018-04-13 to 2018-06-29, and fresh on 97.6–100% of Tokyo days in every later half-year. On the miners' calendar the trailing 60-day share first reaches 95% on 2018-07-05 (2018-07-02 was a Mon–Fri figure).
- **XAU Good Friday closures** (§4.2): the gaps over 6 h include the 11 Good Friday closures, 2015–2025.
- **1306 "13.6–21%"** (§4.4): it holds on the 7 dev ex-dates only; for the four 2022+ ex-dates the boolean is False. The ÷10 factor rests on the issuer and the published distributions (P47).
- **RAW ÷ 10** (§4.4): in binary floating point it differs from the stored corrected amount in the last bit on 1 of the 11 rows; the build uses the stored corrected amounts (P61).
- **The 2.3 STOP and the corrected ex-date table** (§4.4; `reports/P2_5_resolutions.md`): the largest difference between the 1306 adjusted gap and the TOPIX gap is 0.23 pp, not 0.24 pp.

*Evidence:* `reports/P2_1_inputs.md`; `reports/P2_4_acceptance.md` (e); `reports/P2_5_dev_checks.md` §2.3; `reports/P2_5_resolutions.md`; checkpoint `6e04632fdb12ab621acb7694f0efa667fbcb8d92` (P2-1).

---

**P63: D7, the Japan 225 rule (ADOPTED (Isaiah, 2026-10-05, on the supervisor's recommendation); resolves P42).**

*Decision log, verbatim:*

> - D7 (Isaiah, 2026-10-05, on the supervisor's recommendation): P42 adopted. The Nikkei-proxy row uses only nights where n225_stale_start_min ≤ 5 and n225_stale_end_min ≤ 5, applied night by night, with no contiguity requirement. A night with no Japan 225 bar is ineligible. Dev: 929 of 1,708 nights (40 in 2015-H1, the rest from 2018-04-13). Confirmation: 999 of 1,019. Identical at 4, 5 and 10 minutes.
>   - Tier-(ii) criterion (P32, P56): claim tier (ii) only if H1 is rejected and, on the eligible confirmation nights, b with n225_ret (1) has the sign of the primary b̂, (2) rejects b = 0 at 5% two-sided under the primary inference method, and (3) is at least half of b without n225_ret on the same nights.
>   - Yen EWJ is a robustness row, not a tier-(ii) check.

- The rule and the criterion are written into AM-05's `nikkei_proxy_p42` row (P67).
- Eligible nights by half-year, the threshold sensitivity (4, 5 and 10 minutes) and the endpoint staleness bins are in `reports/P2_5_dev_checks.md` §2.4 (confirmation side: counts only). Seven dev nights, one in each half-year from 2015-H1 to 2018-H1, have no Japan 225 bar in the window.

*Evidence:* `reports/P2_5_dev_checks.md` §2.4; DATA_PROVENANCE §4.3.

---

**P64: D8, 1306 open-auction timing (ADOPTED (Isaiah, 2026-10-05, on the supervisor's recommendation), conditional on the zero-gap gate, which passed).**

*Decision log, verbatim:*

> - D8 (Isaiah, 2026-10-05, on the supervisor's recommendation): option (a), conditional on the zero-gap gate (reports/P2_3b_d8_gate.md). Evidence: the ÷10 factor holds on every dev ex-date (corrected table; largest difference 0.23 pp); the 1306 gap tracks the TOPIX gap (R² 0.914) and is the fresher of the two (P55); the tick-grid rule flagged (R = 1.541 > 1.5). The flag is driven by 2021's mixed grid (14 of 245 moves on 0.05; 2015–2020 alone R = 1.43; a uniform 0.1 grid gives 1.38). It is recorded as flagged, and the gate decides. Option (c), the intraday PX_OPEN check, is recorded as a forward-holdout check after the confirmation run.
>
> - D8 zero-gap gate (fixed before it ran): on one row per dev date, Z = the dates with ao_1306_gap_raw == 0 (84); "no evidence of stale 1306 opens" if at most 2 dates of Z fall in the top quintile (Q5) of |ao_topix_gap| over all 1,708 dev dates; otherwise STOP before the switch (D8 reopens).
>
> - D8 zero-gap gate result (item 1; `reports/P2_3b_d8_gate.md`): 0 of the 84 zero-gap dates are in the top quintile of |ao_topix_gap| (the rule allowed at most 2), so D8 (a) stands. Z by quintile Q1–Q5: 72/12/0/0/0; |ao_topix_gap| over Z: median 0.066%, maximum 0.306%.

- **Option (a)** (PASS2_HANDOFF D8): treat the check as passed on documented exchange convention plus consistency evidence.
- **The tick rule** (fixed before it ran; PASS2_STATUS Flags, verbatim):

> - (P2-5c, **D8 flag**) 1306 tick grid (hedge prices only, dev; `tools/p2_5_tick_1306.py`, rule fixed beforehand): the grid is 0.1 in 2015–2020 and 0.05 in 2021 (every year 100% on its grid). Counts at −2/−1/0/+1/+2 steps: 58/60/84/49/78; R = 1.541 > 1.5, so flagged for D8 under the rule. The dev zero-step count is 84, as in 2.3.

- **The gate** (`tools/p2_3b_d8_zero_gate.py`; gap-only, dev): Z by quintile of |ao_topix_gap| (Q1–Q5) = 72/12/0/0/0; maximum |ao_topix_gap| over Z = 0.306%. The zero-gap dates are tick coincidences on quiet mornings, not stale opens.

*Evidence:* `reports/P2_5_dev_checks.md` §2.3; `reports/P2_5_resolutions.md`; `reports/P2_3b_d8_gate.md`; DATA_PROVENANCE §4.4; checkpoints `4a6e82d5d7230486b79c6f89415061264bb3bd0f` (P2-5c) and `b9bf6f3d2e7b11243af6d626713417b5c87423b8` (P2-3b).

---

**P65: D9, the β window on 1306 (ADOPTED (Isaiah, 2026-10-05, on the supervisor's recommendation); P17 unchanged).**

*Decision log, verbatim:*

> - D9 stays OPEN for the decision checkpoint (Isaiah, 2026-10-05). Nothing about the β window is decided in this message; items 2–5 of the supervisor message of 2026-10-05 (after the P2-5 report) collect what D9 needs.
>
> - Supervisor's error: the previous message described A7 table (a) as "own rows". PASS2_ADDENDUM A′ P2-5's table (a) is β on all rows. It is requested now, as a supplement.
>
> - D9 (Isaiah, 2026-10-05, on the supervisor's recommendation): the expanding β is retained as primary (P17 unchanged). Reasons: the common-row margins (5706 0.41%, 5711 0.02%, 5713 −0.01%; pooled 0.18%) are within the comparison's sensitivity: with β on all rows, expanding is lowest for 5711 and 5713, and on the TOPIX hedge expanding beat rolling-500 for every ticker; rolling-500 would leave 780 fewer dev rows with β (4,350 → 3,570; first β 2017-02-16 instead of 2016-01-26); it would need code changes in spec.py and targets.py; every confirmation row has a β under either method; the choice is target-only and blind to b. Rolling-500 becomes the robustness row beta_rolling_500 (AM-05).

- **The D9 STOP** (P2-5, check 2.1; PASS2_STATUS Flags, verbatim):

> - (P2-5, **D9 STOP**, for Isaiah) A7 on 1306: on common rows, rolling-500 has a lower hedged variance than expanding for 5706 and 5711; expanding is lowest only for 5713. Under P17/P18, expanding stays primary only if it wins on common rows for every ticker, so this is Isaiah's nuisance choice (D9), before `spec-dev-v1`. Target-only.

- **The A7 tables on 1306** (target-only, dev; bp²): decision table (b), common rows, rolling-500 against expanding: 5706 22,609.8 vs 22,703.6; 5711 11,137.6 vs 11,139.7; 5713 17,055.7 vs 17,053.5 (`reports/A_hedge_efficiency_1306.md`). The TOPIX self-check reproduced the committed TOPIX tables cell for cell.
- **The supplement** (`reports/A_hedge_efficiency_1306_supplement.md`): table (a′), β on all rows, expanding is lowest for 5711 and 5713; β coverage on all dev rows, expanding 4,350 of 5,124 rows from 2016-01-26 and rolling-500 3,570 rows from 2017-02-16; the TOPIX self-check (774 rows without β) holds.
- **The β code audit** (P2-5c; PASS2_STATUS Flags): rolling-500 is not reachable by spec lines alone; it would need code changes in `spec.py` and `targets.add_targets`.

*Evidence:* the two A7 reports; PASS2_STATUS Flags (P2-5, P2-5c); AM-05 (`beta_rolling_500`); checkpoints `563521d12d705f8c599ebe4b938ea19f73893cf5` (P2-5) and `4a6e82d5d7230486b79c6f89415061264bb3bd0f` (P2-5c).

---

**P66: D10, the index-staleness result (ADOPTED (Isaiah, 2026-10-05, on the supervisor's recommendation); read under P55).**

*Decision log, verbatim:*

> - D10 (Isaiah, 2026-10-05, on the supervisor's recommendation): staleness is established in both samples (reverse-slope 95% CIs [1.1578, 1.2559] and [1.1575, 1.2548]; brackets [0.7571, 0.8286] and [0.7579, 0.8291]). The TOPIX 09:00 print carries about 76–83% of the fresh market gap. Documentation only: it qualifies the fallback's staleness caveat (P18) and changes nothing in the primary analysis.

- The estimator, samples and lag rule are P55's, fixed before the test ran (P61, the P2-5 operational details). Sample (i): 1,687 dev dates with no miner ex-day and no 1306 ex-date, g_I = `ao_topix_gap`; sample (ii): all 1,708 dev dates, g_I = `ao_topix_gap_tradj`; R² 0.9137 and 0.9141.

*Evidence:* `reports/P2_5_dev_checks.md` §2.2 (gap-only, dev); DATA_PROVENANCE §4.4.

---

**P67: D12 and the switch (ADOPTED (Isaiah, 2026-10-05, on the supervisor's recommendation; P2-3b accepted 2026-10-06)).**

*Decision log, verbatim:*

> - D12 (Isaiah, 2026-10-05, on the supervisor's recommendation): AM-03 (line 14) and AM-04 (lines 4, 7) as drafted in docs/P2_switch_drafts.md §3. AM-05 is one amendment for every Pass 2 robustness row on line 42. It consolidates the planned AM-05 (Nikkei proxy) and AM-06 (robustness list), because both change line 42 and each line carries one record. The id AM-06 is unused.
>
> - The DATA_DICTIONARY draft is approved (Isaiah, 2026-10-05, on the supervisor's recommendation), with two corrections (the n225_ret row's eligibility sentence; "No staleness filter (AM-05)" in the XAU row).
>
> - The test-change table is approved (Isaiah, 2026-10-05, on the supervisor's recommendation): rows 1–7, 9, 11–19 and 21 as drafted, with rows 3, 8 and 10 citing AM-05 in place of AM-06; plus new rows 25–28. Row 23 is approved: decisions P58 onward go in a new docs/DECISIONS_P58_onward.md, at P2-6. Row 22 (test_docs_p2 pins) belongs to P2-6.
>
> - The FX_NAMES diff (P52) is approved as drafted (Isaiah, 2026-10-05, on the supervisor's recommendation).
>
> - blind.VALUE_EXEMPT growing with AT_OPEN is approved (Isaiah, 2026-10-05, on the supervisor's recommendation). Its definition (PRE_OPEN_FEATURES | AT_OPEN) is unchanged; the A4 rationale applies to the 1306 gaps; the row-aligned check still covers them.
>
> - P2-3b accepted (Isaiah, 2026-10-06, on the supervisor's recommendation): commit b9bf6f3d2e7b11243af6d626713417b5c87423b8, including the row-21 citing comment and the other recorded deviations.

- **The amendments** (`spec/SPEC_AMENDMENTS.md`): AM-03 (spec line 14, the hedge is 1306), AM-04 (lines 4 and 7, the P2-4 panel hashes) and AM-05 (line 42, the Pass 2 robustness rows). AM-06 is unused.
- **DATA_DICTIONARY:** the 60-column version, SHA-256 `14f9e1ac8348e5a9dc1b56961f4589a4d7630aa85e17efd575a1c9a4f8e25de5`.
- **The test-change table:** rows 1–19 and 21 of `docs/P2_switch_drafts.md` §5 (rows 3, 8 and 10 citing AM-05), plus rows 25–28; every change old → new in PASS2_STATUS, Test changes. The suite after the switch: 246 tests, OK (skipped=5).
- **The switch commit:** `b9bf6f3d2e7b11243af6d626713417b5c87423b8`. Spec SHA-256 `0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee408561f68f96fd94d3b0f9`. The dev panel in DATA is the P2-4 dev panel, `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68`; the Pass 1 dev panel is archived as `data/archive/panel_dev_736636031ca1.csv` (`736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42`), so `BLIND_FIT_LOG` lines 1–6 stay verifiable.

*Evidence:* `docs/P2_switch_drafts.md`; `spec/SPEC_AMENDMENTS.md`; PASS2_STATUS (Test changes; Test results); DATA_PROVENANCE §5.5.

---

**P68: D16, the one C7 rerun, on the Mac (ADOPTED (Isaiah, 2026-10-05, on the supervisor's recommendation); replaces P51's "bit for bit" for this rerun).**

*Decision log, verbatim:*

> - D16 (Isaiah, 2026-10-05, on the supervisor's recommendation): the one C7 rerun runs on the Mac (ofilt_p2) inside the switch, before the commit. For this rerun, P51's "every replication bit for bit" is replaced by the supervisor's item 4 criterion (same structure and keys; every integer, boolean, string and null identical except key.spec_sha256, which must equal the edited spec's SHA-256; every float equal or within 1e-9 relative; every per-replication rejection flag and summary count identical), because of Flag 16. The regenerated report becomes the study's C7 record on the Mac platform; the slow tier's two bit-identity tests then run on the Mac against it.
>
> - D16 criterion (iii) amended (Isaiah, 2026-10-05, on the supervisor's recommendation): the wall-clock field runtime_s, in both reports/C7_mc.json and reports/C7_h1_same_dgp.json, is information only and is excluded from (iii).
>   - Reason: it records elapsed time (618.21 s in the sandbox, 316.75 s on the Mac), not a computed result, so no rerun can match it. The supervisor's criterion should have excluded it.
>   - Every other value met the criterion as written: (i), (ii) and (iv) passed; in C7_mc.json, 2,772 of the 2,846 other floats differ only in the last bits (Flag 16), with a largest relative difference of 4.4e-11; in C7_h1_same_dgp.json, no other float differs.

- **The rerun** (P2-3b, item 4): `tools/c7_mc.py --budget 90` in four foreground chunks, synthetic only. The first comparison failed (iii) only on `runtime_s` (STOP; PASS2_STATUS Flags); after the amendment, `tools/p2_3b_c7_compare.py` gave (i)–(iv) PASS for both reports: 2,846 floats compared in C7_mc.json, 2,772 differing only in the last bits, largest relative difference 4.418784327352831e-11; 2,148 rejection flags and summary counts identical.
- **The slow tier on the Mac:** `tests.test_validation_c7` with `OFILT_SLOW=1` ran 6 tests, OK, including `test_first_reps_bit_identical` and `test_last_reps_bit_identical` against the Mac report.
- The regenerated `reports/C7_mc.json` and `reports/C7_h1_same_dgp.json` are the study's C7 record on the Mac platform. Every rejection count of P54 is unchanged.

*Evidence:* the two C7 reports (commit `b9bf6f3d2e7b11243af6d626713417b5c87423b8`); `tools/p2_3b_c7_compare.py`; PASS2_STATUS (Flags, Test results); DATA_PROVENANCE §5.2.

---

**P69: Repository, accepted deviations and the dry run (ADOPTED (Isaiah, 2026-10-05; parts on the supervisor's recommendation)).**

*Decision log, verbatim:*

> - P45 private-remote deviation closed 2026-10-05 (Isaiah): private GitHub repo IsaiahChoi/ofilt-study created; main (4a6e82d5d7230486b79c6f89415061264bb3bd0f) and tag pass1-final (81905c1b576d24bdac2c96e2ab76429e0a1d24d1) pushed by Isaiah; remote refs verified against local hashes with git ls-remote. The builder "no push" rule is unchanged.
>
> - The switch dry run asked about in docs/P2_switch_drafts.md §5 is adopted as P2-5b (Isaiah, 2026-10-05, on the supervisor's recommendation): a scratch clone with the drafts applied as written (AM-03 and AM-04 only; test-change rows 1–7, 9, 11–19 and 21) and the full suite run on the P2-4 dev panel. Nothing from it is committed.
>
> - Deviation accepted (Isaiah, 2026-10-05, on the supervisor's recommendation): checks 2.2–2.4 were run after the D9 STOP, which is acceptable because they do not depend on the β window.
>
> - P2-5c deviations accepted (Isaiah, 2026-10-05, on the supervisor's recommendation): the tick diagnostic run after the flag, and Pass A run twice.
>
> - (P2-0g, implementation) Both gates run the fallback check first. The external guard is consulted only if the fallback grants. A grant requires the return value to be identical to `None` or `True`: `np.True_`, 1 and "granted" are denials. `io._check_access` now raises `AccessDenied` for every external-guard failure; before, the guard's own exception propagated. The `guard` field of an ACCESS_LOG line still reads `ofilt.guards` whenever an external guard is importable (unchanged).

- **The tag** `pass1-final` (P2-0 d): lightweight, on `81905c1b576d24bdac2c96e2ab76429e0a1d24d1`, the unchanged Pass 1 HEAD (P51). The builder created no other tag and pushed nothing.
- **The P2-5b dry run** (PASS2_STATUS Progress): Scratch clone of HEAD `4a6e82d` (remote removed; tag pass1-final only), scratch DATA = the P2-4 dev panel + the two event files (hash-verified; no sealed panel). Drafts applied as written (AM-03 and AM-04 only; test-change rows 1–7, 9, 11–19, 21; row 16 with a TOPIX spec copy). Suite: Ran 246 tests, FAILED (failures=3, errors=1, skipped=5). One failure EXPECTED (C7 report staleness), three UNEXPLAINED (Flags). `reports/A_hedge_efficiency.md` byte-identical; clone BLIND_FIT_LOG 6, RUN_REGISTRY 0 bytes. Patch `/tmp/p2_switch_dryrun_A.patch` (18 files, no .csv), copied to `files/p2_5b/`. Pass B not run (item 3 (iv): not spec-only). Clone and scratch DATA deleted; REPO unchanged.

**Deviations accepted in Pass 2** (PASS2_STATUS, Deviations, verbatim; grouped by the acceptance that covers them):

- **Recorded at P2-0; P2-0 accepted (Isaiah, 2026-10-05; PASS2_STATUS Progress, P2-0 i):**
  - Pre-flight item 8 was done with organize_raw_inputs.py (copy mode; originals untouched) instead of organize_raw_inputs.sh. P2-0a's hash check is the integrity control.
  - P2-0b's baseline run executed early as an environment diagnostic (D1); the hashes differ in both Mac environments (Flag 16).
  - `.gitignore` has `.DS_Store` as a sixth pattern (supervisor D.1, approved deviation).
  - `tools/checkpoint.sh` has the supervisor's D.2 additions beyond A′ P2-0e (venv check and interpreter print; pre-suite status and diff hash; B6 restore or abort). Beyond those, it passes extra arguments as extra commit-message paragraphs (for the attribution trailer).
  - The D2 suite run used A′'s command with `-v` added (verbosity only), so that skipped tests are named.
- **Recorded at P2-0b; P2-0b accepted (Isaiah, 2026-10-05; Decision log):**
  - The P51 build-code pin test was moved from P2-0 to P2-0b, where `build/pass1/` is created (added in P2-0b).
  - P2-0b's acceptance rule is Isaiah's of 2026-10-05 (the Mac baseline hashes), replacing A′'s (Flag 16).
- **Recorded at P2-1; P2-1 accepted (Isaiah, 2026-10-05; Decision log):**
  - P2-1 goes beyond A′'s bullet list in three ways, all calendar-only or boolean-only: the DATA_PROVENANCE §4.6 calendar facts (NYSE early closes, gotobi counts and rolls, the confirmation-calendar cross-check), the cell-for-cell check of the fixed workbook against the original pull, and the dev-only Japan 225 weekday-calendar diagnostic.
  - `tools/p2_1_inputs.py` was revised after its first run (21 of 26 matching), once its output had been seen:
    - "RAW ÷ 10 exactly" now uses decimal equality of the stored values, with the float result still shown;
    - XAU gaps now have a Good Friday category; the literal DATA_PROVENANCE row is kept and still False;
    - a dev-only weekday-calendar diagnostic was added for Japan 225.
    One criterion changed: "exactly" went from binary float equality to decimal equality of the stored values, which turned that row from False to True; the float result is still printed. No other criterion changed, and no row was removed. Six rows were added (26 → 32), and five of them are True: two XAU gap rows and three of the four weekday-calendar diagnostic rows.
- **Recorded at P2-2; P2-2 accepted (Isaiah, 2026-10-05; Decision log):**
  - P2-2 design choices beyond A′'s text (for review):
    - `build()` takes an `Expect` (hashes, counts, early-close list) so the tests can run it end to end on synthetic inputs. The command line always uses `real_expect()`: hashes from `docs/PASS2_INPUTS.json`, the Mac baseline hashes of Isaiah's 2026-10-05 decision, 11 distribution rows, gotobi 529 / 319 and the 23 P49 dates.
    - Extra build-time assertions: the original dev panel's columns, and its dates and tickers row for row, equal the frozen dev output's; `us_n_sessions` is whole; every written panel's old columns re-read equal the original strings.
    - The frozen build runs in a temporary folder inside the output folder, which is removed afterwards. Only `panel_dev.csv`, `panel_confirm_SEALED.csv` and `MANIFEST.json` remain.
    - The build reads only the three needed sheets of the fixed workbook.
- **Accepted explicitly (Isaiah, 2026-10-05, on the supervisor's recommendation): "checks 2.2–2.4 were run after the D9 STOP":**
  - P2-5: after the D9 STOP in 2.1, checks 2.2–2.4 were still run, because they are gap-only or predictor-count checks that do not depend on the beta window. After the 2.3 STOP, 2.4 was run for the same reason. Item 3 (P2-5b) was not run, as instructed ("only if item 2 raised no STOP"). The two 2.3 diagnostics were run after the STOP, outside the committed scripts.
- **Accepted explicitly (Isaiah, 2026-10-05, on the supervisor's recommendation): "the tick diagnostic run after the flag, and Pass A run twice":**
  - P2-5c, item 4: after the D8 flag, a diagnostic outside the fixed rule (uniform 0.1 grid; count of 2021 differences off it) was run, to give the flag its context. Its output is `/tmp/p2_0/p2_5c_tick_diag.out`, quoted in Flags. The rule's reading (R = 1.541, flag) stands.
  - P2-5b: Pass A was run twice. In the first run, the clone's post-suite git status and the counter checks were printed but not saved to a file. The second run (same clone procedure, apply script and suite) saved them in `/tmp/p2_0/p2_5b_rerun.out`. It reproduced the first run: the same 246 tests and the same failure list, and a byte-identical patch. Both clones and scratch DATA folders were deleted.
- **P2-3b, accepted (Isaiah, 2026-10-05, on the supervisor's recommendation), "including the row-21 citing comment and the other recorded deviations":**
  - P2-3b, item 2b: the drafts' AM-03 and AM-04 headings had a `⟨date⟩` placeholder; it was filled with 2026-10-05.
  - P2-3b, item 2c: the AM-05 heading was formed from the first sentence of the given text ("## AM-05 (2026-10-05, Isaiah): Pass 2 robustness rows (P33 list; P41, P42, P48, P49, P56; D7, D9)"); the rest of the text follows it verbatim.
  - P2-3b, item 2e: some lines carry citing comments that the dry-run patch did not have (test_docs_d1 rows 7 and 9, test_docs_d5 row 13, test_lookahead row 16; listed in `/tmp/p2_3b/patch_compare.out`). Row 21's line in test_docs_d4 had no comment citing its entry, in the dry run and in item 2. The comment ("Isaiah 2026-10-05, row 21") was added after the 4c STOP; comment only.
  - P2-3b, item 4b: the four chunks ran in one foreground command, each as `env -u OFILT_RUN_SEALED OFILT_SLOW=1 OFILT_DATA_DIR=… python tools/c7_mc.py --budget 90` (the `env -u` keeps the rule's unset variable explicit).
  - P2-3b, item 4c: from its first version, the comparison tool also printed an information-only line (floats other than runtime_s). It changed no verdict.

**Recorded, with no separate acceptance entry in the Decision log:** P2-5, 2.1, the first run of `tools/report_A7_1306.py` stopped at the TOPIX self-check because of a parser bug in the script; the parser was fixed and the rerun passed (PASS2_STATUS, Deviations).

*Evidence:* PASS2_STATUS (Progress, Decision log, Deviations); `git tag -l` (`pass1-final` only); the checkpoint commits.

---

**P70: Documentation refresh of Pass 2 (EDITORIAL; the PLAN v2.4 refresh, the numbering P58–P70 and the retirement of the two supervisor files decided by Isaiah, 2026-10-06, on the supervisor's recommendation).**

*Decision log, verbatim:*

> - PLAN is refreshed to v2.4 in P2-6 (Isaiah, 2026-10-06, on the supervisor's recommendation).
>
> - The two supervisor files in the Claude Project, PASS2_SUPERVISOR_HANDOFF_2026-10-05.md and PASS2_P2-6_RECORDS_REGISTER.md, are retired from the Project at the Pass 2 upload (Isaiah, 2026-10-06, on the supervisor's recommendation).
>
> - The decision entries are numbered P58–P70, as outlined in item 2 of the P2-6 message (Isaiah, 2026-10-06, on the supervisor's recommendation).
>
> - P2-6 drafts approved (Isaiah, 2026-10-06, on the supervisor's recommendation), with the corrections in item 1 of the supervisor message of 2026-10-06. PASS2_SUPERVISOR_HANDOFF_P2-6.md is also retired from the Claude Project at the Pass 2 upload, with the two supervisor files already listed.

- **Updated** (2026-10-06):
  - DATA_PROVENANCE: corrections to §4.2–§4.5 (P62); the settings check and the TOPIX ticker resolved (P60); the 1306 open-auction timing, the corrected ex-date table and the staleness result (P64, P66); new §5, the Pass 2 build (P58, P59, P61, P67, P68);
  - PASS2_INPUTS.json: local layout, statuses, the Mac reference outputs (`mac_frozen_build_outputs`) and the Pass 2 outputs (`pass2_outputs`). No existing key and no existing hash changed;
  - README, PROJECT_SETUP and PLAN v2.4;
  - DATA_DICTIONARY was updated earlier, in the switch commit (P67).
- **New:** this file.
- **Unchanged:** PASS2_HANDOFF.md, PASS2_ADDENDUM.md and DECISIONS_P37_onward.md stay as adopted; their amendments are recorded here.
- **Pins moved** (old → new in PASS2_STATUS, Test changes): `test_docs_p2` (DATA_PROVENANCE, PASS2_INPUTS.json, README, PROJECT_SETUP and PLAN; a new pin for this file; test-change row 22); `test_docs_d4` (the README and PLAN prefixes, PLAN's first line and its Supersedes line); `test_docs_d6` (the PROJECT_SETUP prefix, its title and `PLAN.md` (v2.4)).
- **Retired from the Claude Project at the Pass 2 upload:** `PASS2_SUPERVISOR_HANDOFF_2026-10-05.md`, `PASS2_P2-6_RECORDS_REGISTER.md` and `PASS2_SUPERVISOR_HANDOFF_P2-6.md`, superseded by this file and `PASS2_STATUS.md` (PROJECT_SETUP, "Removed").

---

**Carried to the pre-registration (Pass 5)**

1. **Sealed old-column provenance.** Byte identity with `9c18a6c1…` cannot be demonstrated. The sealed old columns come from the Mac frozen build (`138e5e21…`). The dev comparison bounds the size of platform differences (DATA_PROVENANCE §5.2; P59).
2. **Platform.** State the platform of each panel. Cross-platform verification is by tolerance, not by hash (Flag 16; P58).
3. **P39 (b).** It was resolved by Isaiah's attestation, not by the 1A re-pull (P60).
4. **Real-data contact.** Every Pass 2 session's real-data contact, supervisor and builder, 2026-10-04 to 2026-10-06, goes into the disclosure (DATA_PROVENANCE §4.5; the PASS2_STATUS attestation).
