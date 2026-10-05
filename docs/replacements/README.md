# Overnight FX and the Tokyo opening auction (October 2026)

**Status (2026-10-04).**
- **Done:** Pass 1, the analysis machine, completed 2026-10-02. Pass 2's inputs are pulled and verified.
- **Next:** the Pass 2 build (data and rebuild). It runs in Claude Code on Isaiah's Mac, following `PASS2_HANDOFF.md`.
- **Still open:** the pre-flight items in `PASS2_HANDOFF.md` §6.

## Current scope

`PLAN.md` (v2.2) is the authoritative research plan. It supersedes v2.1, v2.0 and the multi-market Plan v1.1. Where wording differs, the decision log and `spec/SPEC_AMENDMENTS.md` govern.

The decision log has three parts:
- `DECISIONS_ADDENDUM.md`: P01–P13, the panel build;
- `DECISIONS_P14_onward.md`: P14–P36, Pass 1;
- `DECISIONS_P37_onward.md`: P37–P44, Pass 2 inputs.

The plan's discipline applies throughout:
- the pre-registration and the holdout lock;
- reporting nulls;
- accuracy shown next to base rates;
- Clark–West for nested comparisons.

**Question.** Is overnight USD/JPY information fully priced by the 09:00 TSE opening auction for three FX-exposed non-ferrous miners (5713 Sumitomo Metal Mining, 5711 Mitsubishi Materials, 5706 Mitsui Kinzoku)? Or do the stocks keep absorbing it during the session?

**One estimand (P14).** The outcome is the abnormal open→close return y_oc − β̂·hedge_oc. β̂ is a past-only expanding estimate (P17). The hedge is the 1306 ETF after Pass 2; TOPIX is the placeholder until then, and P18 has a fallback rule. The outcome is pooled across the three stocks with ticker fixed effects and regressed on:
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
| 1 | Analysis machine (`ofilt/drift/`): 171 tests, 5 skipped by default; 6 sealed fits, none returning an FX coefficient | **Complete** (2026-10-02) |
| 2 | Data and rebuild (`PASS2_HANDOFF.md`). No sealed fit is sanctioned in this pass | Inputs verified; build next |
| 3 | Calibration, with dev still blinded by the guard: binding size run (AM-02), power and MDE, joint H1/CW cross-tab, Flags 10/12, SESOI and equivalence viability. Exactly one sanctioned sealed fit | — |
| — | **Tag `spec-dev-v1`**. Inference and calibration choices are locked from here | — |
| 4 | Dev first look (exploratory) + the P13(b) dry run | — |
| 5 | Pre-registration (prior-exposure disclosure, advisor sign-off) → tag `prereg-v1` | — |
| 6 | Confirmation, once. The forward holdout (after 2026-03-05) is evaluated later | — |

Older documents use other pass names; P44 maps them. In particular, AM-02's "Pass 4" means Pass 3.

## Pipeline

```
Raw inputs (kept LOCAL in ~/Desktop/FX Project/raw/; hashes in MANIFEST.json and PASS2_INPUTS.json)
  Book2.xlsx                                       Bloomberg: miners OHLC, TOPIX, SPY/EWJ/FCX/COPX, dividends
  usdjpy_dukascopy_2015-01-01_2026-03-05.csv       1-min, bid, true UTC, start-labeled
  eurusd_dukascopy_2015-01-01_2026-03-05.csv
  -- Pass 2 inputs --
  newbloombergdata_fixed.xlsx                      1306 OHLC + corrected dividends; TOPIX total return (fallback only)
  xauusd_dukascopy_2015-01-01_2026-03-05.csv.gz    robustness control (P41)
  jpn225_dukascopy_2015-01-01_2026-03-05.csv.gz    Nikkei proxy (P42: fresh at 08:59 JST only from ~2018-07-02)
        │   pull_dukascopy.py (patched, P38: UTC bounds, every request capped at 2026-03-05)
        ▼
make_events.py   ->  events_firm.csv, events_boj.csv
build_panel.py   ->  panel_dev.csv (2015-01-06 → 2021-12-30, 5,124 rows)
                     panel_confirm_SEALED.csv (2022-01-04 → 2026-03-05, 3,057 rows, LOCAL only)
                     MANIFEST.json (SHA-256 of all inputs and outputs)
        ▼
ofilt/drift/     analysis machine (code repo, not in this Project): schema allowlist, blinding guard,
                 past-only targets, DK inference, simulators, walk-forward forecasting, run registry
```

**To rebuild the current panel** (about 1 minute), run these from a folder that contains the event scripts:

```
python make_events.py
python build_panel.py "<dir with raw inputs>" "<out dir>"
```

Then compare the hashes with `MANIFEST.json`. Identical hashes prove an identical panel.

**Pass 2 extends the build.**
- **New columns:** the 1306 hedge return and gaps; XAU and Japan 225 dark-window returns with endpoint staleness; US-session USD/JPY and a yen-denominated EWJ; the gotobi flag; session FX (09:00 → close).
  - Names and groups follow the recommended default in `PASS2_HANDOFF.md` §7 (decision D6).
- **Acceptance:** the 41 existing columns must be unchanged in both panels (P2-4).
- **Hashes:** the rebuild supersedes the sealed hash `9c18a6c1…`, and the new hashes are recorded as an AM-xx entry.
- **Afterwards:** the new `panel_dev.csv` and `MANIFEST.json` come into this Project. The sealed panel never does.

**Pass 2 input status** (`PASS2_INPUTS.json`):

| Input | Status |
|---|---|
| Book2, USD/JPY, EUR/USD | Verified. Offer side confirmed bid (P37) |
| 1306 + TOPIX total return | Accepted. Dividends ÷10 is inferred; pending CACS confirmation (P39). The TOPIX total-return ticker is pending (P40) |
| XAU/USD | Verified (P41) |
| Japan 225 CFD | Verified, with a coverage limitation. The usage rule is PROPOSED (P42) |

## Files in this project

| File | Purpose |
|---|---|
| `panel_dev.csv` | The development data (Pass 1 panel, 41 columns; replaced after the Pass 2 rebuild). |
| `DATA_DICTIONARY.md` | Column definitions and the schema groups. |
| `DATA_PROVENANCE.md` | What was verified about every input, and how. §4 covers the Pass 2 inputs. |
| `MANIFEST.json` | Hashes of raw inputs, event files, and both panels. |
| `PASS2_INPUTS.json` | Hashes and status of every Pass 2 raw input, plus the pending pre-flight items. The build refuses to run on a mismatch. |
| `PASS2_HANDOFF.md` | How Pass 2 is run, verified and decided (supervisor's guide and the builder prompt). |
| `PLAN.md` | The research plan, v2.2 (authoritative). |
| `DECISIONS_ADDENDUM.md` | Decisions P01–P13. |
| `DECISIONS_P14_onward.md` | Decisions P14–P36 (Pass 1). Add it from the Pass 1 kit if it is not yet in the Project. |
| `DECISIONS_P37_onward.md` | Decisions P37–P44 (Pass 2 inputs; P42 and P43 PROPOSED). |
| `build_panel.py`, `make_events.py`, `events.py` | Reproducible build. |
| `events_firm.csv`, `events_boj.csv` | Event calendars (calendar data only, no outcomes). |
| `pull_dukascopy.py` | FX download script (patched version, P38). |
| `PROJECT_SETUP.md` | What belongs in this project and why. |
| Math 86 paper | Background only. |

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
   - New Pass 2 predictors go in `PRE_OPEN_ROBUSTNESS`, for robustness designs only. `PRE_OPEN_FEATURES` stays exactly the 20 Pass 1 columns (P43, recommended default).
   - Session FX is `CONTEMPORANEOUS` and is never a feature.
4. **Nuisance coefficients are fitted on past data only, or on dev only.** This covers the hedge β, standardisation moments, thresholds and tuning. The expanding β continues across the dev/confirmation boundary.
5. **Exclusions.**
   - The primary exclusions are `earn_flag` and `news_flag` (days D and D+1).
   - Forecast evaluation keeps unscheduled news on day D.
   - `audit_flag` is robustness only. `mech_flag` is informational.
6. **The spec changes only through AM-xx entries that Isaiah approves.** The spec is pinned in `spec.py`, and the verbatim-diff test enforces the amendments log. The fingerprint mechanism in `blind.py` is frozen.
7. **Reporting.**
   - Linear models are primary. Report every pre-registered result, including nulls.
   - Report accuracy next to its training-window base rate.
   - Use Clark–West for nested comparisons.
   - Use permutation importance by whole dates, calibrated against a noise column; never impurity importance.
   - Interim wording, verbatim: "H1 and the CW forecast test may disagree; disagreement is not by itself evidence against H1. The expected joint behaviour is quantified in Pass 4." Here "Pass 4" means Pass 3 (calibration) under P44.
8. **Raw data and the code repository never go in this Project.** The new `panel_dev.csv` and `MANIFEST.json` come in after Pass 2; the sealed panel never does.
9. **Stop for Isaiah's decision:**
   - at every decision point in `PASS2_HANDOFF.md` §8;
   - at each AM-xx;
   - at `spec-dev-v1`;
   - at `prereg-v1`.
