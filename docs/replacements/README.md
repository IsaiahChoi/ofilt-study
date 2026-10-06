# Overnight FX and the Tokyo opening auction (October 2026)

**Status (2026-10-06).**
- **Done:**
  - Pass 1, the analysis machine, completed 2026-10-02. Its final repository was lost, and Stage C4–D was rebuilt from the C3 checkpoint (205 tests). The rebuilt repository is the canonical study repository (P45).
  - Pass 2, data and rebuild, completed 2026-10-06 (decisions P58–P70):
    - the 60-column panels were built on macOS arm64 (P2-4) and accepted;
    - the hedge is the 1306 ETF (AM-03); the panel hashes are in AM-04, and the Pass 2 robustness rows in AM-05;
    - the switch commit applied them (P2-3b), and the C7 rerun on the Mac reproduced every rejection decision (D16).
  - The four items still open on 2026-10-05 were resolved that day: the settings check by attestation (D2); the TOPIX total-return series, TPXDDVD Index (D3); the raw files organised; the Mac environment, `~/venvs/ofilt_p2`.
- **Next:** Pass 3, calibration (cost inputs; one sanctioned sealed fit).

## Current scope

`PLAN.md` (v2.4) is the authoritative research plan. It supersedes v2.1, v2.0 and the multi-market Plan v1.1. Where wording differs, the decision log and `spec/SPEC_AMENDMENTS.md` govern.

The decision log has four parts:
- `DECISIONS_ADDENDUM.md`: P01–P13, the panel build;
- `DECISIONS_P14_onward.md`: P14–P36, Pass 1;
- `DECISIONS_P37_onward.md`: P37–P57, Pass 2 inputs and the pre-flight decisions;
- `DECISIONS_P58_onward.md`: P58–P70, the Pass 2 build, the decision checkpoint and the switch.

The plan's discipline applies throughout:
- the pre-registration and the holdout lock;
- reporting nulls;
- accuracy shown next to base rates;
- Clark–West for nested comparisons.

**Question.** Is overnight USD/JPY information fully priced by the 09:00 TSE opening auction for three FX-exposed non-ferrous miners (5713 Sumitomo Metal Mining, 5711 Mitsubishi Materials, 5706 Mitsui Kinzoku)? Or do the stocks keep absorbing it during the session?

**One estimand (P14).** The outcome is the abnormal open→close return y_oc − β̂·hedge_oc. β̂ is a past-only expanding estimate (P17). The hedge is the 1306 ETF (AM-03); the P18 fallback did not fire. The outcome is pooled across the three stocks with ticker fixed effects and regressed on:
- the dark-window returns `usdjpy_ret` and `eurusd_ret`, both with common slopes;
- the US open→close controls `spy_oc` and `copx_oc`, with ticker-specific slopes.

The primary estimand is **b**, the coefficient on `usdjpy_ret`. Because EUR/USD is in the design, b is the drift per unit of **yen-specific** overnight move (Frisch–Waugh–Lovell). Inference is pooled OLS with Driscoll–Kraay SEs, two-sided at 5%. The final calibration choice is made in Pass 3.

| Coefficient | Meaning |
|---|---|
| b = 0 | The auction fully priced FX (claimed only through the equivalence test, P23) |
| b > 0 | Underreaction (the cascade hypothesis) |
| b < 0 | Overreaction |

**Related hypotheses:**
- **H3** tests EUR/USD coefficient = 0: dollar-wide and yen-specific moves priced alike (P15).
- **The auction-conditional specification is retired** (P16): conditioning on the realised gap manufactures underreaction when the auction is noisy. The `ao_` columns are used only for the gap decomposition, the hedge, and the fraction unpriced f (P24).

**Claim tiers (P32):**

| Tier | Claim | What it needs |
|---|---|---|
| (i) | "overnight USD/JPY predicts the drift" | H1 |
| (ii) | the exposure channel | H1 plus the Nikkei-proxy robustness check |
| (iii) | the cascade | (ii) plus H3 and the metals controls |

This tests whether FX is fully priced at the open, not how fast. Speed needs intraday bars, which are a later extension.

## Pass sequence (P36 order; P44 names)

| Pass | Contents | Status |
|---|---|---|
| 1 | Analysis machine (`ofilt/drift/`): originally 171 tests, 5 skipped by default. Rebuilt C4–D: 205 tests, 4 skipped (5 on the Mac). 6 sealed fits, none returning an FX coefficient | **Complete** (2026-10-02; rebuilt 2026-10-05) |
| 2 | Data and rebuild (`PASS2_HANDOFF.md` + `PASS2_ADDENDUM.md`). No sealed fit is sanctioned in this pass | **Complete** (2026-10-06): 60-column panels built on macOS arm64; hedge 1306 (AM-03); the C7 rerun on the Mac reproduced every rejection decision (D16) |
| 3 | Calibration, with dev still blinded by the guard: binding size run (AM-02), power and MDE, joint H1/CW cross-tab, Flags 10/12, SESOI and equivalence viability. Exactly one sanctioned sealed fit | — |
| — | **Tag `spec-dev-v1`**. Inference and calibration choices are locked from here | — |
| 4 | Dev first look (exploratory) + the P13(b) dry run | — |
| 5 | Pre-registration (prior-exposure disclosure, advisor sign-off) → tag `prereg-v1` | — |
| 6 | Confirmation, once. The forward holdout (after 2026-03-05) is evaluated later | — |

Older documents use other pass names; P44 maps them. In particular, AM-02's "Pass 4" means Pass 3.

## Pipeline

```
Raw inputs (kept LOCAL in ~/Desktop/FX_Project/raw/; hashes in MANIFEST.json and PASS2_INPUTS.json)
  Book2.xlsx                                       Bloomberg: miners OHLC, TOPIX, SPY/EWJ/FCX/COPX, dividends
  usdjpy_dukascopy_2015-01-01_2026-03-05.csv       1-min, bid, true UTC, start-labeled
  eurusd_dukascopy_2015-01-01_2026-03-05.csv
  -- Pass 2 inputs --
  newbloombergdata_fixed.xlsx                      1306 OHLC + corrected dividends; TOPIX total return (fallback only)
  xauusd_dukascopy_2015-01-01_2026-03-05.csv.gz    robustness control (P41)
  jpn225_dukascopy_2015-01-01_2026-03-05.csv.gz    Nikkei proxy (P42: 08:59 JST price fresh from 2018-04-13)
        │   pull_dukascopy.py (patched, P38: UTC bounds, every request capped at 2026-03-05)
        ▼
make_events.py   ->  events_firm.csv, events_boj.csv
build_panel.py   ->  panel_dev.csv (2015-01-06 → 2021-12-30, 5,124 rows)
                     panel_confirm_SEALED.csv (2022-01-04 → 2026-03-05, 3,057 rows, LOCAL only)
                     MANIFEST.json (SHA-256 of all inputs and outputs)
build/pass2/build_panel_p2.py (Pass 2): runs the frozen build/pass1/build_panel.py, appends 19 columns,
                     and writes the 60-column panel_dev.csv and panel_confirm_SEALED.csv, and MANIFEST.json
        ▼
ofilt/drift/     analysis machine (code repo, not in this Project): schema allowlist, blinding guard,
                 past-only targets, DK inference, simulators, walk-forward forecasting, run registry
```

**To rebuild the current panels**, run this from the repository root:

```
python build/pass2/build_panel_p2.py --raw <raw dir> --events <dir with the event files> --orig-dev <original dev panel> --out <new empty folder>
```

It verifies every raw input, event file and frozen code file against `PASS2_INPUTS.json`, and the original dev panel against `736636…`, before reading them. It runs the frozen `build/pass1/build_panel.py` in a working folder that holds the event files. It refuses to run while `build/` or `docs/PASS2_INPUTS.json` has uncommitted changes.

Then compare the hashes with `MANIFEST.json`. Identical hashes prove an identical panel **on the same numerical platform**. The Pass 1 panels were built on x86_64 and are not reproducible byte for byte on macOS arm64; the Pass 2 panels were built on macOS arm64 (DATA_PROVENANCE §5, Flag 16). Across platforms, compare under a tolerance rule stated in advance.

**Pass 2 extended the build.**
- **New columns:** the 1306 hedge return and gaps; XAU and Japan 225 dark-window returns with endpoint staleness; US-session USD/JPY and a yen-denominated EWJ; the gotobi flag; session FX (09:00 → close).
  - Names and groups follow P50: the handoff's §7 default, with staleness and bar counts in PROVENANCE. The panel grew from 41 to 60 columns.
- **Design:** append-only (P51). The 41 old columns were read back as strings, and the new columns were appended to the right.
- **Old columns (the hybrid; Isaiah, 2026-10-05):** dev's are the original `736636…` strings; sealed's come from the Mac frozen build (`138e5e21…`). Byte identity with the original sealed file (`9c18a6c1…`) cannot be demonstrated, and the pre-registration discloses it.
- **Hashes:** the rebuild supersedes the sealed hash `9c18a6c1…`. The new hashes are in AM-04.
- **Afterwards:** the new `panel_dev.csv` and `MANIFEST.json` come into this Project. The sealed panel never does.

**Pass 2 input status** (`PASS2_INPUTS.json`):

| Input | Status |
|---|---|
| Book2, USD/JPY, EUR/USD | Verified. Offer side confirmed bid (P37) |
| 1306 + TOPIX total return | Accepted. The dividend ÷10 factor is confirmed by the issuer's split notice and its published distributions (P47). Settings check resolved by attestation (D2); TOPIX total return = TPXDDVD Index (D3) |
| XAU/USD | Verified (P41) |
| Japan 225 CFD | Verified, with a coverage limitation. Usage rule adopted (D7). |

## Files in this project

| File | Purpose |
|---|---|
| `panel_dev.csv` | The development data: the Pass 2 rebuild, 60 columns (hash in AM-04). |
| `DATA_DICTIONARY.md` | Column definitions and the schema groups. |
| `DATA_PROVENANCE.md` | What was verified about every input, and how. §4 covers the Pass 2 inputs. |
| `MANIFEST.json` | The P2-4 build manifest: hashes of the raw inputs, event files, build code and both 60-column panels. |
| `PASS2_INPUTS.json` | Hashes and status of every Pass 2 raw input, the Mac reference outputs and the Pass 2 outputs. The build refuses to run on a mismatch. |
| `PASS2_HANDOFF.md` | How Pass 2 is run, verified and decided (the supervisor's guide). |
| `PASS2_ADDENDUM.md` | Corrections to the handoff for the rebuilt repo; the 2026-10-05 decisions; builder prompt A′; reference numbers B′. Governs where it differs from the handoff. |
| `PASS1_STATUS.md` (stored as `PASS1_STATUS__2_.md`) | The Pass 1 build record. |
| `REBUILD_VERIFICATION.md` | The rebuilt repo checked against the adopted decision text, with every difference listed. |
| `PLAN.md` | The research plan, v2.4 (authoritative). |
| `DECISIONS_ADDENDUM.md` | Decisions P01–P13. |
| `DECISIONS_P14_onward.md` | Decisions P14–P36 (Pass 1). |
| `DECISIONS_P37_onward.md` | Decisions P37–P57: the Pass 2 inputs and the pre-flight decisions. |
| `DECISIONS_P58_onward.md` | Decisions P58–P70: the Pass 2 build, the decision checkpoint and the switch. |
| `build_panel.py`, `make_events.py`, `events.py` | The frozen Pass 1 build (`build/pass1/`), run unchanged by `build_panel_p2.py`. |
| `build_panel_p2.py`, `columns.py` | The Pass 2 build (`build/pass2/`): appends the 19 new columns (P51). |
| `events_firm.csv`, `events_boj.csv` | Event calendars (calendar data only, no outcomes). |
| `pull_dukascopy.py` | FX download script (patched version, P38). |
| `PROJECT_SETUP.md` | What belongs in this project and why. |
| `PASS2_STATUS.md` | The Pass 2 build record: progress, decision log, test results and changes, flags, blinding attestation, deviations. |
| Pass 2 reports | `P2_1_inputs.md`, `P2_4_acceptance.md`, `P2_5_dev_checks.md`, `P2_5_resolutions.md`, `A_hedge_efficiency_1306.md`, `A_hedge_efficiency_1306_supplement.md`, `P2_3b_d8_gate.md`, and the C7 reports regenerated on the Mac (`C7_mc.json`, `C7_h1_same_dgp.json`). |
| Math 86 paper | Background only. |

Retired at the Pass 2 upload (PROJECT_SETUP, "Removed"): `PASS2_SUPERVISOR_HANDOFF_2026-10-05.md`, `PASS2_P2-6_RECORDS_REGISTER.md` and `PASS2_SUPERVISOR_HANDOFF_P2-6.md`, superseded by `DECISIONS_P58_onward.md` and `PASS2_STATUS.md`.

## Rules for any session working in this project

1. **Use `panel_dev.csv` only.**
   - The split at 2022-01-01 is signed off (P10). The confirmation panel is deliberately absent: do not ask for it, reconstruct it, or analyse 2022+ outcome data until `prereg-v1` is tagged.
   - Data after 2026-03-05 is the forward holdout (P13). Do not pull it before `prereg-v1`, not even transiently: the patched pull script caps every request (P38).
   - 2022+ event release **dates** and calendars are allowed.
   - In Pass 2 the build **writes** the sealed panel and checks it only through dates, counts, hashes and in-memory equality booleans. It never prints or summarises sealed values.
2. **Blinding until `spec-dev-v1` (P29, P36).** No computation whose output relates any predictor to any target on real data. "Predictor" includes FX, XAU, Japan 225, the US controls and session FX.
   - **The one exception** is the sealed blind fit (`sim._sealed_blind_fit`). It is opt-in via `OFILT_RUN_SEALED=1`, must be sanctioned explicitly by Isaiah, is counted in `BLIND_FIT_LOG`, and returns no coefficient. None is sanctioned in Pass 2; Pass 3 gets exactly one.
   - **Allowed on real data:** hashes; structural checks; predictor-only statistics; target-only statistics without predictors (e.g. A7); gap-only statistics on dev (e.g. the index-staleness test).
   - Model and test code runs on synthetic panels until the tag.
3. **Features come only from the explicit allowlist** in `ofilt/drift/schema.py` (P20). This replaces the old rule "features come from unprefixed columns".
   - Every panel column is in exactly one schema group, and unknown columns are refused.
   - `open`, `close`, `prev_close` (auction or target prices) and `audit_flag` (outcome-selected) are **forbidden** as features even though they are unprefixed.
   - `ao_` and `y_` columns are never features.
   - New Pass 2 predictors go in `PRE_OPEN_ROBUSTNESS`, for robustness designs only. `PRE_OPEN_FEATURES` stays exactly the 20 Pass 1 columns (P43, adopted as P50).
   - Session FX is `CONTEMPORANEOUS` and is never a feature.
4. **Nuisance coefficients are fitted on past data only, or on dev only.** This covers the hedge β, standardisation moments, thresholds and tuning. The expanding β continues across the dev/confirmation boundary.
5. **Exclusions.**
   - The primary exclusions are `earn_flag` and `news_flag` (days D and D+1).
   - Forecast evaluation keeps unscheduled news on day D.
   - `audit_flag` is robustness only. `mech_flag` is informational.
6. **The spec changes only through AM-xx entries that Isaiah approves.** The spec is pinned in `spec.py`, and the verbatim-diff test enforces the amendments log. The fingerprint algorithm in `blind.py` is frozen. The only permitted `blind.py` changes are the conjunctive tag gate (P46) and the `FX_NAMES` list extension (P52).
7. **Reporting.**
   - Linear models are primary. Report every pre-registered result, including nulls.
   - Report accuracy next to its training-window base rate.
   - Use Clark–West for nested comparisons.
   - Use permutation importance by whole dates, calibrated against a noise column; never impurity importance.
   - Interim wording, verbatim: "H1 and the CW forecast test may disagree; disagreement is not by itself evidence against H1. The expected joint behaviour is quantified in Pass 4." Here "Pass 4" means Pass 3 (calibration) under P44.
8. **Raw data and the code repository never go in this Project.** The new `panel_dev.csv` and `MANIFEST.json` come in after Pass 2; the sealed panel never does. Raw files don't need to be uploaded to chats either, because Claude Code reads them locally. No session opens or prints a raw or sealed file (P51).
9. **Stop for Isaiah's decision:**
   - at every decision point in `PASS2_HANDOFF.md` §8;
   - at the Pass 2 decision checkpoint before the switch commit (P51);
   - at each AM-xx;
   - at `spec-dev-v1`;
   - at `prereg-v1`.
