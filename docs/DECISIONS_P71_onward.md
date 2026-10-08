# DECISIONS P71 onward: Pass 3, calibration with dev still blinded (2026-10-06 to 2026-10-07; records written 2026-10-07)

This file continues `DECISIONS_P58_onward.md` (P58–P70), which continues `DECISIONS_P37_onward.md` (P37–P57), `DECISIONS_P14_onward.md` (P14–P36) and `DECISIONS_ADDENDUM.md` (P01–P13).

Status vocabulary: as in `DECISIONS_P58_onward.md` (ADOPTED, ADOPTED PENDING, PROPOSED, EDITORIAL).

**The governing record is the Pass 3 decision log** (`PASS3_STATUS.md`, Decision log). Each entry below summarises one group of its decisions and names them by their opening words, in the log's order; where wording differs, the log governs. Evidence is in the files named in each entry, in `reports/P3_reports/` (every builder report of Pass 3, copied byte for byte) and in `PASS3_STATUS.md` (Test results, Test changes, Flags, Blinding attestation, Deviations).

**Status index (2026-10-07).** Later entries resolve or supersede parts of earlier ones; the earlier text is left exactly as adopted.

| Earlier entry | Current status |
|---|---|
| P23, the SESOI "PENDING the cost inputs" and its viability "decided in Pass 4" | SESOI 0.8652 (low 0.07152, high 2.719) from the cost model (P72); TOST viable at T_conf under DK-normal (P79); spec line 49 (AM-07; P80) |
| AM-02, P30 and P31, the binding size rule | Applied (P79): DK-normal rejects 291 of 5,000 draws (5.82%) at b = 0, inside [3.5%, 6.5%]; primary inference stays DK with the normal reference, and AM-08 is unused |
| P30 and PLAN §5, the preview MDE80 ≈ 0.257 on the TOPIX hedge | Superseded by the binding numbers on the 1306 hedge (P79): MDE80 0.2471 under DK-normal |
| Flag 10, DK slightly oversized (~6%) | Resolved by D3.4 (P73, P79): 5.82%, inside the band |
| Flag 12, Clark–West conservative | Confirmed on the binding run (66 of 2,000, 3.30%, below the band); the primary comparison uses c_CW,cal = 1.411608406163672 (AM-09; P79, P80) |
| P36 step 3, the calibration pass | Complete (P71–P80). Step 4, the tag `spec-dev-v1`, follows (P81) |
| P61, the P2-2b decision (the MANIFEST git state and the command-line refusal) attributed to Isaiah, 2026-10-05 | No Decision-log bullet in `PASS2_STATUS.md` records it. It is recorded there in Progress (the P2-2b row) and in Test changes (`tests/test_p2_build.py`, 5 tests added (P2-2b), Isaiah 2026-10-05). `DECISIONS_P58_onward.md` stays as adopted |
| PASS1_STATUS Flag 4, 5706's coarse 2015–2016 grid explained by the 1:10 consolidation ("capital-change-adjusted prices are 10x raw") | Corrected (P81). On the Pass 2 pull, 5706's stored prices equal traded prices before 2017-09-27 (factor 1) and are traded prices ÷ 10 from that date (the 10:1 split, ex-date 2026-09-29); its coarse early grid comes from the ¥1 tick on low traded prices. The 5711 extension (factor 10 before 2016-09-28) stands. Source: P3-0b, Part B (P72), and D2.4. `PASS1_STATUS.md` stays as recorded |

**The Pass 3 checkpoints** (all on `main`; the start is P2-7, `c9cea24fba787efc6411131d4314aa7e2e29a331`):

| Item | Commit |
|---|---|
| P3-0 | `2ac5a85b51d8604ccad84cf877baf45ff2d45f76` |
| P3-0b | `022260254ff9b76739120fd51eed8d0e22656397` |
| P3-1 | `8aba8df8ed33225071d4451741c2f7ab140ef18c` |
| P3-1b | `87aff1406356701396a3e99b7b2923257ba81d62` |
| P3-2a | `8bced4b38ff1365d15344267a6f57d38f270ee08` |
| P3-2b | `befb7da4a4d7fdd5fbcfca8a303110ee213e741e` |
| P3-2c | `b94d8a48fdce45e424cb772ff77d7941d60dde0b` |
| P3-2d | `1c48d381bb794e65d6532ba915ea782761ba58b2` |
| P3-3a | `cdded9b444ea889ef64859acf7883b89ffecf29b` |
| P3-3b | `56897128f2e93068b60747640a87ce4cd4148241` |
| P3-3c | `f5e6d281d1b95102fc19a6aab554d1af331d7828` |
| P3-3d | `1fd79933b16ae98344a9b58abd1f21a4e5dd8198` |
| P3-3e | `025d9c432b9592a5a062f24c07ccabd3bbf074c8` |
| P3-3f | `9629b6f766a63a0f2d7f030e57a0554e9bf42a83` |
| P3-4 | `b634cc04a73502821cd27850282659d683015b32` |
| P3-4b | `57ceb44c4ebf79ac086c9aec3c8bc5c2601f7822` |
| P3-5 | `5b33bd0fb9b9b993105af0116d734918e606e120` |
| P3-6a | `6338409a30f57758523de8ec47a004774c45c0cd` |
| P3-6b | `cfc1deff58658eed87d691cb9cb38c60ac55cb97` |
| P3-7a | `80147cf44b3fb8205f7d7a6ed67ec3a5ac1c05cd` |

The final records commit (P3-7b) and the tag commit (P3-8) are recorded in `PASS3_STATUS.md`.

---

**P71: The Pass 3 builder prompt and DQ1, the one sealed fit (ADOPTED (Isaiah, 2026-10-06; DQ1.1 to DQ1.7 and their clarifications on the supervisor's recommendation)).**

- **The one real sealed fit** is BLIND_FIT_LOG line 7: a single `DevCalibrator`, in a single foreground process that Isaiah launches in his own Terminal (mains power, lid open, `caffeinate -i`, `OFILT_RUN_SEALED=1` as a prefix to that one command, an explicit `--real`). The calibrator's state is never written, so the run is never chunked or resumed (DQ1.1).
- **Outputs are aggregates stated in advance:** counts, rates, Wilson intervals, means and standard deviations across replications, and named quantiles. No per-replication value, residual, fitted control, calibrator attribute, cache, pickle or figure is written or printed, because enough per-replication estimates would determine the residual vector (DQ1.2).
- **Verifiability (DQ1.3):** the script and its configuration are committed before the sanction; the real run refuses a dirty tree; it records HEAD and the hashes of the configuration, the dev panel and the spec; BLIND_FIT_LOG must hold 6 lines before, 7 right after the calibrator and 7 at the end; static tests; a target check.
- **Containment (DQ1.4):** a fixed task order, each task flushed when it completes, exceptions recorded by class and line only; a failed task would be salvaged by a second sanctioned fit with identical configuration and seeds.
- **Rehearsal (DQ1.5), scope (DQ1.6) and the separate sanction (DQ1.7):** two synthetic rehearsals with the populated fingerprint registry before the sanction, with the expected duration stated; T1, T2, T3, T5's TOST viability and T6, each under every method the rules can select; Isaiah sanctions line 7 later, against the committed configuration's SHA-256.
- **Standing rule:** a builder check script that fails because of its own bug may be fixed and rerun once; a second failure is a STOP.
- **The Pass 1 sealed-run reports** (B7, B7b) hold per-cell aggregates only (P3-0 step f).
- **Clarifications:** the tool's temporary run-registry directory; the import tests read the import statements; the rehearsal's target-only contact; the launch command's own check of untracked files (DQ1.3 clarification).

*Decision log (PASS3_STATUS.md):* "DQ1.1"; "DQ1.2"; "DQ1.3"; "DQ1.4"; "DQ1.5"; "DQ1.6"; "DQ1.7"; "Pass 3 builder prompt adopted"; "P3-0 accepted"; "Standing rule"; "P3-0 step f"; "Clarifications of DQ1"; "DQ1.3 clarification".

*Evidence:* the builder prompt `PASS3_BUILDER_PROMPT_2026-10-06.md` (SHA-256 `018c489ff53db0aa069881874e0c4faea0e165a2e23ba02b875963b034dfee36`; kept on the Mac in `files/pass3/`); `reports/P3_0_report.txt`.

---

**P72: The cost inputs, DQ2 and the SESOI (ADOPTED (Isaiah, 2026-10-06; DQ2 and the approval of the computation on the supervisor's recommendation)).**

- **Pre-flight facts (P3-0b):** the AM-03 estimation sample has 4,192 rows on 1,439 dates (2016-01-26 to 2021-12-30). Stored price = traded price × f, with f = 10 for 5711 before 2016-09-28, f = 2 for 5713 before 2017-09-27, f = 1 for 5706 before 2017-09-27 and 1/10 from that date, and f = 1 otherwise.
- **The cost inputs** (Isaiah, primary / low / high, fixed before any SESOI ingredient was computed): notional JPY 10,000,000 / 1,000,000 / 100,000,000; commission per side 4.3 / 0 / 8 bp for the miners and for 1306; auction impact per side 2 / 0.5 / 8 bp (miners) and 1.5 / 0.5 / 4 bp (1306); intraday short cost 0 / 0 / 1 bp a day. The source, Isaiah's cost note of 2026-10-06, stays outside the repository and the Project because it quotes post-dev prices.
- **DQ2 (D2.1 to D2.9):** ẽ, the residual of `usdjpy_ret` on the primary design's other regressors (predictor-only); β̄, the mean expanding past-only β (target-only); the round trip per name-day; the miners' and 1306's tick terms; D2.6, TOST viability; D2.7, the claim wording; D2.8, the economic evaluation; D2.9, fixity.
- **The SESOI, approved as computed (D2.9):** mean |ẽ| = 28.4288 bp; β̄ = 1.0333; mean round trip 24.5961 bp (low 2.0333, high 77.2878); SESOI 0.8652 (low 0.07152, high 2.719).

*Decision log (PASS3_STATUS.md):* "P3-0b accepted"; "Cost inputs"; "DQ2"; "P3-1 accepted"; "SESOI approved as computed".

*Evidence:* `docs/P3_COST_INPUTS.json`; `reports/P3_0b_preflight.md`; `reports/P3_1_sesoi.md`.

---

**P73: Inference: DQ3, the pooled critical values and the joint rule (ADOPTED (Isaiah, 2026-10-06, on the supervisor's recommendation)).**

- **D3.1 to D3.3:** the bootstrap test of AM-02's branch (the Driscoll–Kraay t, a stationary bootstrap of whole dates with mean block 5, recentred); its evaluation by the warp-speed method (Giacomini, Politis and White, 2013); the simulation-calibrated critical values c_cal and c_CW,cal.
- **D3.4, the joint T1/T4 rule (Flags 10 and 12),** applied at P3-5 to point estimates: H1 keeps DK-normal if its rate at b = 0 lies in [3.5%, 6.5%], else the bootstrap if its own rate does, else c_cal(0.05); Clark–West keeps the normal reference if its rate at b = 0 lies in the band, else c_CW,cal. **D3.5:** DK-normal or the bootstrap, when selected, applies to every other pre-registered DK test.
- **The G2 STOP (P3-2a):** the warp-speed gate G2 was mis-specified (one shared, estimated critical value makes the discordances run one way) and was replaced by G2′ before run 2; run 1 is kept as `reports/P3_2a_warp_check_run1.md`. Run 2 passed G1 and G2′.
- **D3.2 and D3.3 amended:** (b̂ − b)/se and t* do not depend on b, so c_boot and c_cal are pooled over cells 0 to 4 (13,000 draws). The warp-path gate (P3-2b) then found the warp-speed and inner draws on one code path (9 of 9 identity checks).

*Decision log (PASS3_STATUS.md):* "P3-1b accepted"; "DQ3"; "P3-2a step e, the G2 STOP"; "D3.2 and D3.3 amended"; "P3-2a accepted".

*Evidence:* `ofilt/drift/calib.py` and `tests/test_p3_calib.py`; `tools/p3_2a_warp_check.py`; `reports/P3_2a_warp_check.md`.

---

**P74: The run's design and its tool (ADOPTED (Isaiah, 2026-10-06 and 2026-10-07, on the supervisor's recommendation)).**

- **DQ4, the cells:** 0, T1 at b = 0 (5,000); 1, T5's boundary at b = +0.8652 (5,000); 2 to 4, T2 at b = 0.10, 0.25, 0.40 (1,000 each); 5 to 8, T6, full and early-window draws at b = 0 and 0.25 (1,000 each); 9 to 11, T3 on 2,452-date draws at b = 0, 0.10, 0.25 (2,000, 500, 500). Seeds disjoint from B7, B7b and C7; every DK and Newey–West lag 6; the outputs listed in D4.7.
- **DQ7, the code scope:** new code only (`calib.py`, the tool and their tests); the C7-hashed files, `spec.py`, `blind.py`, `io.py`, `registry.py`, `targets.py`, the guard and both builds unchanged until the switch.
- **The sealed-run tool** (`tools/p3_sealed_run.py`): synthetic, real, rehearsal and smoke modes; a stand-in with the real sample's shape; assertions in every mode; flushing after each task; no decision rule applied. The supervisor's full review added R1 (every real-mode check on line 7 rehearsed, the panel hash checked before the fit), R2 (no exception message printed) and R3 (a structural check of the real construction path with synthetic targets, `tools/p3_2d_structural.py`).
- **The rehearsal procedure** (`tools/p3_3_rehearse.sh`, two runs, in Isaiah's Terminal) and **the records rule** (`validate_config` rebuilds the configuration from Decision-log lines, so lines with its prefixes are reserved).
- **Facts:** K_early = 409 (K16 = 165); P3-2e, the last unexercised part of the real path, ruled out every failure after line 7.

*Decision log (PASS3_STATUS.md):* "DQ4"; "DQ7"; "Design of the sealed-run tool"; "P3-2b accepted"; "P3-2c accepted"; "The supervisor's review of the full sealed-run tool"; "The rehearsal procedure"; "The records rule"; "P3-2d accepted"; "P3-2e".

*Evidence:* `tools/p3_sealed_run.py` (`bd21c4503490aee0561c618f6ee02fd50e6be0dea4e5152f10d7579e4e609837`); `docs/P3_RUN_CONFIG.json` (`ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e`, regenerated at P3-3b, P75); `tests/test_p3_sealed_run.py`; `tools/p3_2b_preflight.py`; `reports/P3_2b_smoke.md`; `reports/P3_2d_structural.md`.

---

**P75: T6's outputs: the P9 finding and D4.3 amended (ADOPTED (Isaiah, 2026-10-07, on the supervisor's recommendation)).**

- **The finding (P3-3a, P9):** the calibrator's residuals are orthogonal to the design over the full sample only. Early-window draws, and estimators other than its OLS, are centred near b plus a real-data coefficient difference, so T6's mean bias, uncentred rejection rate and coverage would reveal FX–target information before `spec-dev-v1`.
- **D4.3a:** T6 writes only centred outputs: the centred rejection rate (b̄ held in memory only), sd(b̂), mean se, se/sd and Huber's mean share downweighted. **D4.3b, the flag rule:** a robustness row is flagged as unreliable on coarse-grid periods if its centred rate at b = 0 in cell 7 lies outside [3.5%, 6.5%].
- **D4.3a qualified:** winsorised OLS-DK depends on the early-window deviation at first order; in the supervisor's synthetic check the effect is small (the centred count moves by at most 6 in 1,000). Accepted with disclosure.
- The configuration was regenerated (`ca989095…`, P74), and the rehearsal script was bound to it by `--expect-config-sha256`.

*Decision log (PASS3_STATUS.md):* "D4.3 amended"; "The rehearsal script bound to the configuration"; "The records rule now also reserves the prefix"; "P3-3b accepted"; "D4.3a qualified".

*Evidence:* `PASS3_STATUS.md`, Flags (P3-3a); `tests/test_p3_sealed_run.py`, tests 14 to 16.

---

**P76: The rehearsals (records of 2026-10-07).**

- **Rehearsal 1,** 2026-10-07T00:12:19Z to 04:05:04Z at `1c48d38`: PASSED; 6,955.0 s and 7,004.9 s; the expected duration of the real run, stated before the sanction, about 2 hours. Its plausibility table found P9 False, which led to P75.
- **Rehearsal 2,** 2026-10-07T05:41:48Z to 09:27:07Z at `56897128`: PASSED; 6,757.6 s and 6,757.9 s, the two runs identical apart from runtime. The plausibility checks P1 to P11, stated before the run, were all True; P11 found every non-T6 cell byte-identical to rehearsal 1.

*Decision log (PASS3_STATUS.md):* "The rehearsal"; "P3-3a accepted"; "Rehearsal 2 on record"; "P3-3c accepted".

*Evidence:* `reports/P3_3_rehearsal.log` and `reports/P3_3_rehearsal_run1.json` (rehearsal 1); `reports/P3_3_rehearsal2.log` and `reports/P3_3_rehearsal2_run1.json` (rehearsal 2).

---

**P77: DQ5, DQ6, salvage and the launcher (ADOPTED (Isaiah, 2026-10-07, on the supervisor's recommendation)).**

- **DQ5:** the post-run checkpoint commits line 7 and the run's outputs and applies `docs/P3_DQ5_line7.patch` unchanged; lines 1 to 6 stay pinned as Pass 1's history by their prefix hash, and line 7 by its fields.
- **DQ6:** the switch's amendments as drafted in `docs/P3_DQ6_drafts.md` (AM-07 to AM-10, with variants), `spec.py`'s validation changes and the confirmation-code plan; section 6 as the switch's test-change plan; from the switch on, the configuration differs from a rebuild by its `spec_sha256` by design, and the records rule changes form.
- **Salvage, option (b):** no salvage path is added before the run, because a change to the tool would need a third rehearsal, and DQ1.4 stands. A failed task would need a new reviewed item that adds the salvage path (line 8, the identical configuration and seeds) and a new sanction.
- **The launcher** (`tools/p3_4_launch.sh`): it wraps the one sealed-run command with pre-checks and post-checks and changes nothing the run executes. It was tested statically, rehearsed in a scratch clone with refusal cases, and executed byte-identical by the supervisor against a stub tool in a fake repository.

*Decision log (PASS3_STATUS.md):* "DQ5"; "P3-3d accepted"; "The DQ6 drafts"; "P3-3e accepted"; "DQ6 decided"; "Salvage"; "The launcher"; "P3-3f accepted".

*Evidence:* `docs/P3_DQ5_line7.patch` (`8b4eaa35b45605566f3a1447b61647f0ee55252f82852091c8189e9f00e2977c`); `docs/P3_DQ6_drafts.md` (`9ad9b0941952dbaee6b45e53940d5f1ed8b206abdacc2198d60733e04d3697c3`); `tools/p3_4_launch.sh` (`d80296d490ea7cad5cdeb49cdfa7bb71f01edad1a4da6cf30f2f9ab0b51686ba`) and `tests/test_p3_launch.py`.

---

**P78: The sanction and the seventh sealed fit (ADOPTED (Isaiah, 2026-10-07, on the supervisor's recommendation; DQ1.7)).**

- **The sanction** is recorded in the commit `b634cc04a73502821cd27850282659d683015b32`, against the configuration `ca989095…`.
- **The run:** Isaiah's Terminal, on AC power, 2026-10-07T18:51:20Z to 20:45:12Z (1 h 54 min). Every pre-check was True; the tool printed `COMPLETE` with 0 errors, and the launcher exited 0.
- **BLIND_FIT_LOG line 7:** provenance dev_real; panel `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68`; spec `0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee408561f68f96fd94d3b0f9`; 5,124 input rows; caller `tools/p3_sealed_run.py`. It returned no coefficient.
- **The post-run checkpoint** (`57ceb44c4ebf79ac086c9aec3c8bc5c2601f7822`) committed line 7, the outputs and the launcher's log, and applied the DQ5 patch unchanged. The outputs were read for six structural keys only; their aggregates were first read at P3-5, under readings fixed beforehand.

*Decision log (PASS3_STATUS.md):* "The sanction"; "P3-4 accepted"; "The real sealed fit on record"; "P3-4b accepted".

*Evidence:* `reports/P3_4_sealed_run.json` (`65e68c8cf9a76afda05869e8772b345e49f30fa24bcad6790de28d6bcab58942`) and `.md` (`8acbece13ff366ba39a097cf927e9c168471eff190f7dc4eb8b3307fc00c29a9`); `reports/P3_4_launch.log` (`da76746b137a2dbc966b78ee99a7b2404e8f365e32608140b8c14de1e58eee67`).

---

**P79: The selection: the pre-stated rules applied (ADOPTED (Isaiah, 2026-10-07, on the supervisor's recommendation)).**

- **Applied by script at P3-5,** to the run's JSON, in exact integer arithmetic on the point estimates (a band test 35·n ≤ 1000·k ≤ 65·n).
- **H1 (D3.4):** DK-normal rejected 291 of 5,000 at b = 0 (5.82%; Wilson [5.20%, 6.50%]), inside the band: DK with the normal reference. AM-08 is unused.
- **Clark–West (D3.4):** the normal reference rejected 66 of 2,000 (3.30%), outside the band: c_CW,cal = 1.411608406163672 (95% interval [1.3296, 1.5280]; rank 1,900 of 2,000), AM-09.
- **TOST (D2.6):** viable under DK-normal: equivalence at b = 0 in 5,000 of 5,000 draws at the primary SESOI, and at b = +SESOI in 296 of 5,000 (5.92%). AM-07, variant "viable".
- **D4.3b:** no robustness row is flagged (cell 7, centred: 55, 57 and 52 of 1,000).
- **The binding numbers under DK-normal:** rejection 5.82%, 21.2%, 80.9% and 99.5% at b = 0, 0.10, 0.25 and 0.40; MDE80 0.2471 (probit interpolated; 0.2425 and 0.2400 by the normal approximations). The T3 cross-tab (H1 DK-normal × Clark–West calibrated; both, H1 only, CW only, neither): 62, 56, 38, 1,844 at b = 0; 108, 7, 47, 338 at b = 0.10; 417, 0, 35, 48 at b = 0.25.

*Decision log (PASS3_STATUS.md):* "The rules applied"; "P3-5 accepted"; "The selection approved".

*Evidence:* `reports/P3_5_selection.json` (`110a045e5ff6c2f0657fecd93c2c9d400c679599ffbde09354ea9f8f5bd207d3`) and `.md` (`33365cde94848b318986ca729deda60c7a3f7ff9ff877f940726430b4badee0d`).

---

**P80: The switch (ADOPTED (Isaiah, 2026-10-07, on the supervisor's recommendation)).**

- **Built and rehearsed whole in a scratch clone** (P3-6a), C7 rerun included, and written as `docs/P3_6_switch.patch` (`cd9d317db33ee04c8c627d1386565e3c5ad19f9ddeb511286c576a946515281a`); **applied unchanged** in the switch commit `cfc1deff58658eed87d691cb9cb38c60ac55cb97` (P3-6b).
- **The spec** is FROZEN, SHA-256 `feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26`: AM-07 (line 49, the SESOI and "viable"), AM-09 (line 66, the calibrated Clark–West critical value) and AM-10 (line 2, the status). `spec.py` validates AM-09's primary comparison.
- **The tests** changed as the patch lists, each to the amended state, with tests 5, 6, 9 and 15 of `tests/test_p3_sealed_run.py` retired and test 17 asserting the refusal (PASS3_STATUS, Test changes). From the switch on, the suite has 285 tests and 6 skips; the sixth is `test_io`'s check that no unblinding tag exists while the spec is DRAFT, which skips by design once it is FROZEN.
- **The one C7 rerun** passed D16's criterion (P68) for both reports and was bit-identical apart from `key.spec_sha256` and `runtime_s`.
- **The configuration** is unchanged and differs from a rebuild only by its `spec_sha256`, so the sealed-run tool refuses every run, real or synthetic.
- From P3-6b on, the builder ran in a new Claude Code session, oriented by a read-only message; nothing in the repository changed at the change of session.

*Decision log (PASS3_STATUS.md):* "The switch's C7 rerun"; "The switch patch"; "P3-6a accepted"; "The switch on record"; "P3-6b accepted"; "The new builder session".

*Evidence:* `spec/SPEC_AMENDMENTS.md`; `docs/P3_6_switch.patch`; `reports/C7_mc.json` (`72d4a6bc4ffa5084169cfa18534a7480c252afab1224b6dce5eb113d6a5d4b9a`) and `reports/C7_h1_same_dgp.json` (`5644e6168cd7c100a2fd01c6eaef3ecda9bb0542b30df34ff2a807e0a5ed7821`).

---

**P81: Documentation refresh of Pass 3 (EDITORIAL; the records, the PLAN v2.5 refresh and the Project upload list decided by Isaiah, 2026-10-07, on the supervisor's recommendation).**

- **Updated:** PLAN v2.5 (the status block, the companion files, §1.3, §3.4, §4.5, §5, §8, §11 and the change log); README; PROJECT_SETUP (its title date, the Project list and the Pass 3 upload); DATA_PROVENANCE §4.5 (the Pass 3 supervisor chats); `PASS3_STATUS.md`.
- **New:** this file.
- **Unchanged:** `PASS1_STATUS.md`, `PASS2_STATUS.md` and the earlier decision files stay as recorded; the P61 citation and the Flag 4 correction are rows of this file's status index.
- **Pins moved** (old → new in PASS3_STATUS, Test changes): `test_docs_p2` (DATA_PROVENANCE, PLAN, PROJECT_SETUP and README; a new pin for this file); `test_docs_d4` (the README and PLAN prefixes, PLAN's first line and its Supersedes line); `test_docs_d6` (the PROJECT_SETUP prefix, its title, `PLAN.md` (v2.5) and the Project's PLAN title).
- **The Pass 3 Project upload,** after the tag: as PROJECT_SETUP's "After Pass 3" list states. `PASS3_SUPERVISOR_HANDOFF_2026-10-06.md` is retired from the Project; the other Pass 3 handoffs were chat uploads only and stay on the Mac.
- **Next:** P3-8 makes the tests that read the repository's tags hold before and after `spec-dev-v1`, checks the guard in a scratch clone with the tag (dev_real granted; confirm_real still refused), and Isaiah creates the annotated tag on the final records commit.

*Decision log (PASS3_STATUS.md):* "The final records"; "P3-7a accepted"; "P3-7a2 accepted"; "The final Pass 3 records".

---

**Carried to the pre-registration (Pass 5)**

Items 1 to 4 of `DECISIONS_P58_onward.md`'s list stand, with P32's disclosures. Pass 3 adds:

1. **The seventh sealed fit** (BLIND_FIT_LOG line 7) and what it returned: aggregates over synthetic draws from the sealed calibrator only, no coefficient (P78, P79).
2. **The Pass 1 sealed-run reports** (B7, B7b) hold per-cell aggregates only; their per-cell means of simulated estimates are linear functionals of the residual vector given the seeds (P71).
3. **Platform:** the sealed run and the C7 rerun ran on macOS arm64; P58's platform items (Flag 16) apply to every Pass 3 number.
4. **Isaiah's cost note** (2026-10-06): approximate 2026 price levels, share counts and trading values for the miners and 1306. It is prior exposure, used in no computation, and kept outside the repository and the Project (P72).
5. **The cost sources** (P72; `docs/P3_COST_INPUTS.json`).
6. **D2.7, the claim wording:** the equivalence wording is an economic statement at the primary SESOI. At the low SESOI equivalence is impossible (0 of 5,000 at b = 0); at the high SESOI it is uninformative (5,000 of 5,000 even at b = +0.8652). State both beside it (P72, P79).
7. **The warp-speed reference and the G2 episode** (a mis-specified gate; run 1 kept as `reports/P3_2a_warp_check_run1.md`), and the pooling invariance behind the pooled critical values (P73).
8. **R1 to R3 and the structural check** (P74); **both rehearsals** and P11 (P76).
9. **The T6 leak finding, D4.3 amended and D4.3a qualified** (P75).
10. **The launcher and its stub verification** (P77).
11. **The selection and the notes on it** (P79): DK-normal is slightly liberal (5.82% [5.20%, 6.50%]; c_cal(0.95) = 2.0041 [1.9698, 2.0321] against 1.96; size-adjusted power 20.3%, 79.3% and 99.5%, MDE80 0.2521); the real residuals are noisier than the rehearsal's stand-in (pooled sd(b̂) about 0.0866 against about 0.074; se/sd 0.98 to 1.00 in cells 0 to 4); the primary SESOI is about 3.5 times MDE80 and 10 times sd(b̂); Clark–West's normal reference is conservative (3.30%), and the calibrated value restores 5.0% and raises power (31.0% against 24.4% at b = 0.10; 90.4% against 85.6% at 0.25), with a wide interval on 2,000 draws ([1.330, 1.528]); under the null, H1's and Clark–West's false positives overlap (62 of 2,000 jointly), and the cross-tab is the binding description of their agreement; T6's centred sizes are 4.4% to 5.7%, se/sd 0.99 to 1.03 and Huber's share downweighted about 0.19 to 0.21, with no D4.3b flag.
12. **P3-5's STOP episode:** a cosmetic second run of the rules script, then a comparison script with two bugs; a corrected structural comparison passed, and the committed selection files are the second run's (P79).
13. **Real-data contact:** every Pass 3 session's real-data contact, supervisor and builder, goes into the disclosure (DATA_PROVENANCE §4.5; PASS3_STATUS, Blinding attestation).
