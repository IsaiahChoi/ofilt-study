# DECISIONS P82 onward: Pass 4, the dev first look and the P13(b) dry run (2026-10-08 to 2026-10-12; records written 2026-10-12)

This file continues `DECISIONS_P71_onward.md` (P71–P81), which continues `DECISIONS_P58_onward.md` (P58–P70), `DECISIONS_P37_onward.md` (P37–P57), `DECISIONS_P14_onward.md` (P14–P36) and `DECISIONS_ADDENDUM.md` (P01–P13).

Status vocabulary: as in `DECISIONS_P58_onward.md` (ADOPTED, ADOPTED PENDING, PROPOSED, EDITORIAL).

**The governing record is the Pass 4 decision log** (`PASS4_STATUS.md`, Decision log, entries P4Q1 to P4Q42 and the acceptances between them). Each entry below summarises one group of its decisions and names them by their opening words, in the log's order; where wording differs, the log governs. Evidence is in the files named in each entry, in `reports/P4_reports/` (every builder report of Pass 4, copied byte for byte) and in `PASS4_STATUS.md` (Test results, Test changes, Flags, Blinding attestation, Deviations, Disclosure list). The Pass 4 checkpoints are listed in `PASS4_STATUS.md`, Progress, each by its commit subject `checkpoint: P4-…`.

**Status index (2026-10-12).** Later entries resolve or supersede parts of earlier ones; the earlier text is left exactly as adopted.

| Earlier entry | Current status |
|---|---|
| P15, "a₂ = 0 is exactly the restriction that dollar-wide and yen-specific moves carry the same session drift per unit of USD/JPY", and its "common weight" auction | Qualified (P84): the equal-drift reading holds exactly only when the euro-specific drift loading is zero; a₂ = 0 reads as "the unspanned metals channel fully priced (given that)", not as a common-weight auction. H3 as a test is unchanged |
| P14 and PLAN §1.2, "b is the yen-specific pass-through", with "b = 0 means fully priced" and "b < 0 means overreaction" | Qualified (P85): b is approximately the yen-specific pass-through; an underpriced dollar-wide channel the controls do not span loads on b. H1 as a test is unchanged |
| P32, claim tier (iii), "the cascade" | Not claimed (P4Q17): H3 and the metals rows are reported without a tier-(iii) reading |
| P32, claim tiers (i) and (ii); P23 and PLAN §1.4 on a null and on equivalence | Worded and conditioned in the configuration (P4Q16, P4Q18, P4Q19): PLAN §1.4 (v2.6) |
| P13(b), the dry run | Made (P4-5): every criterion of `docs/P4_DRYRUN_CRITERIA.md` held |
| P36 step 5, the dev first look | Made (P4-6), once, under its sanction; exploratory, nothing claimed |

---

**P82: Pass 4 recorded (ADOPTED (Isaiah, 2026-10-08 to 2026-10-12, each on the supervisor's recommendation)).**

- **Order and sanction (P4Q1 to P4Q8):** the confirmation script was written and validated on synthetic data only, and committed, before any computation relating a predictor to a target on the dev panel; the dev run was sanctioned against the SHA-256 of the committed script, module and configuration, conditional on the dry run's pre-stated criteria (P4Q40). No exploratory extra was made (P4Q7, P4Q41).
- **The audit and the configuration (P4Q9 to P4Q31):** every pre-registered output and robustness row mapped to its defining text and code entry point (`reports/P4_reports/p4_1_audit.md`); each gap decided into `docs/P4_CONFIRM_CONFIG.json` (SHA-256 `5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd`), which the script reads and pins.
- **The simulator (P4Q32, P4Q33):** `ofilt/drift/sim_full.py`, a full-schema simulator with known parameters, a break at 2024-11-05 and δ_cc, against `docs/P4_SIM_SPEC.md`.
- **The confirmation code (P4Q34 to P4Q39):** four modules (`confirm_inference`, `confirm_forecast`, `confirm_economic`, `confirm_claims`, with `confirm_allowlist`), the assembler `confirm_run` and the script `tools/p4_confirm_run.py`, each against its specification in `docs/`; the six C7-hashed files unchanged.
- **The dry run, the gate and the dev run (P4Q40):** `docs/P4_DRYRUN_CRITERIA.md` committed before any run; four synthetic runs at confirmation length met every criterion; the dev run was made once, after the gate, its outputs committed in `reports/P4_runs/dev/` and its two registry lines in `RUN_REGISTRY.jsonl`; three registry tests rewritten by decision (P4Q6).
- **The records (P4Q41, P4Q42):** the disclosure list of everything seen on dev (T6) in `PASS4_STATUS.md`; this documentation kit.

**P83: The M2 derivation adopted for the documents (ADOPTED (Isaiah, 2026-10-12, on the supervisor's recommendation; P4Q42)).**

- `docs/P4_M2_note.md` (the blind derivation of 2026-10-08) is the reference for M2, for how a₂ and b are read, and for P4Q17's choice of option (c).
- PLAN §7 states M2 as derived, and qualifies A′(i) and A′(vi) (P85); PLAN §1.4 states the claim tiers and the null and equivalence wording as the configuration fixes them.

**P84: P15's reading of a₂ = 0 qualified (ADOPTED (Isaiah, 2026-10-12, on the supervisor's recommendation; P4Q42; `docs/P4_M2_note.md`, Proposition 6)).**

- P15's identity b·u + a₂·v = b·e^¥ + (bγ + a₂)·v stands.
- "a₂ = 0 is exactly the restriction that dollar-wide and yen-specific moves carry the same session drift per unit of USD/JPY" holds exactly when the drift loading on the euro-specific factor is zero, with "dollar-wide" meaning the part the controls do not span. Otherwise a₂ = 0 neither implies nor is implied by equal per-unit drift.
- The "common weight" auction does not give a₂ = 0: with a common partial-adjustment share below one, the dollar-wide move carries an extra fair-value channel. a₂ = 0 reads as the unspanned metals channel fully priced (given a zero euro-specific loading), and a₂ cannot compare the pricing of metals with that of translation.
- H3, the two-sided test of a₂ = 0, is unchanged; its sign is not attributed to the metals channel (P4Q17).

**P85: The reading of b qualified (ADOPTED (Isaiah, 2026-10-12, on the supervisor's recommendation; P4Q42; `docs/P4_M2_note.md`, Proposition 4; flags F4-3 and F4-4)).**

- Holding `eurusd_ret` fixed does not hold the dollar fixed, so b is approximately, not exactly, the yen-specific pass-through: any underpriced dollar-wide channel the controls do not span loads on `usdjpy_ret`.
- A channel whose fair value falls when the dollar strengthens, such as the metals cascade, pushes b down. So b < 0 can arise without overreaction and b = 0 without full pricing; a positive b is conservative with respect to the cascade, not with respect to yen-correlated news. f = b/δ_cc inherits the same term.
- A′(i) (b = (1 − ρ)δ) and A′(vi) hold when the unspanned dollar-wide channels are fully priced, or when EUR/USD is an exact dollar proxy.
- H1, the two-sided test of b = 0, is unchanged; only its reading changes. PLAN §1.2 and §7 and DATA_DICTIONARY's line on `eurusd_ret` carry the qualifier. The pre-registration's wording of the reading (F4-3) is Pass 5's.

**P86: The registry's `git_dirty` (ADOPTED (Isaiah, 2026-10-12, on the supervisor's recommendation; P4Q42; flag F4-5)).**

- A registry line records `git_dirty`, which reads the tracked files. `RUN_REGISTRY.jsonl` is itself tracked, so the second call of a run that appends to it records `git_dirty` True with no change to any code (at the dev run: the main call False, the M7 call True).
- `git_dirty` is read with the registry file itself excluded. Pass 6's run note repeats this.

**P87: This refresh (EDITORIAL (Isaiah, 2026-10-12; P4Q42)).**

- PLAN v2.6 (the status block, the companion files, §1.2, §1.3, §1.4, §7 and the change log), DATA_DICTIONARY's line on `eurusd_ret`, and this file, with their pins in `tests/test_docs_d4.py`, `tests/test_docs_d5.py` and `tests/test_docs_p2.py` moved under the test-change protocol.
- DATA_PROVENANCE §4.5 (F4-2), PROJECT_SETUP and the Pass 4 Project upload list follow in the last Pass 4 item, P4-7c.
