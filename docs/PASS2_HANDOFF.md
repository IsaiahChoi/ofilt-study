> **2026-10-05: read `PASS2_ADDENDUM.md` first.** This handoff was written on 2026-10-04 for the original Pass 1 repository, which was lost. The canonical repository is now the rebuild (DECISIONS P45). The addendum corrects this document for the rebuild, which has 205 tests, an invalidation of the C7 report by any spec amendment, and verification tests that pin Pass 1 state. It also records decisions P45–P57. The addendum replaces four parts of this document:
> - **§6** (pre-flight) is replaced by addendum §2.
> - **§7's order** is replaced by addendum §4.
> - **Appendix A** (the builder prompt) is replaced by **Appendix A′**.
> - **Appendix B** is replaced by **Appendix B′**.
>
> The rest of this document stands as written, read together with the addendum's §3 corrections.

# PASS 2 HANDOFF: directing, verifying and deciding the data-and-rebuild pass

**For:** a new Claude chat, inside the Claude Project "Stochastic Filtering Across Asian Markets", that will supervise Pass 2.
**From:** the chat that planned and supervised Pass 1 and pulled and verified the Pass 2 inputs.
**Date:** 2026-10-04.
**Read with:** `PLAN.md` v2.2, `DATA_PROVENANCE.md` (§4 is new), `DECISIONS_P37_onward.md`, `PASS2_INPUTS.json`, and the Pass 1 records (`docs/DECISIONS_P14_onward.md` and the final `PASS1_STATUS.md` in the repo).

---

## 0. How to use this document

You are the **supervisor**, not the builder. The build itself runs in **Claude Code on Isaiah's Mac**, using the prompt in Appendix A. The raw files are a few hundred MB, they are local, and they contain 2022+ data, so they cannot go in this Project.

Your job has four parts:

1. **Get Pass 2 started correctly.** Clear the pre-flight items in §6, then give Isaiah the Appendix A prompt with the placeholders filled in.
2. **Verify each checkpoint** the builder reports, using §9's checklist and the expected numbers in Appendix B.
3. **Prepare decisions for Isaiah.** At each decision point in §8, set out the evidence, the options and a recommendation with its reasoning. **Isaiah decides.** You draft paste-ready messages that carry his decisions to the builder.
4. **Protect the study.** Blinding (§3), the forward holdout, and the one-shot confirmation outrank speed, convenience and completeness. If something threatens them, say so plainly and stop the line.

### Working with Isaiah

- He wants thorough reasoning, explicit justification for every recommendation, and accuracy first.
- He wants fatal flaws flagged explicitly rather than worked around.
- He is comfortable going slowly.
- He runs commands himself in Terminal on macOS.
  - Give him complete, copy-pasteable blocks.
  - Use **heredocs** (`cat > file <<'EOF'`) for any multi-line code.
  - Never give partial function edits; earlier partial edits caused duplicated loops and IndentationErrors.
  - Quote paths: his project folder is `~/Desktop/FX Project/`, which contains a space.
- When you are wrong, say so, correct the record, and move on. The Pass 1 record has examples, such as the withdrawn Flag 12 sentence, a cross-DGP comparison error.

---

## 1. The study in one page

**Question.** Is overnight USD/JPY fully priced by the 09:00 Tokyo opening auction for three FX-exposed miners (5713, 5711, 5706), or do the stocks keep absorbing it during the session?

**Primary estimand (P14).** b, the pooled common coefficient on `usdjpy_ret` (the dark-window return from the previous TSE close to 08:59:00 JST) in this regression:
- **outcome:** abnormal open→close return, y_oc − β̂_{t−1} · hedge_oc;
- **hedge:** 1306 ETF after Pass 2 (TOPIX index until then);
- **β:** past-only expanding, estimated on non-excluded rows;
- **design:** ticker fixed effects (no intercept), common USD/JPY and EUR/USD slopes, and ticker-specific SPY and COPX slopes.

With EUR/USD in the design, b is the **yen-specific** pass-through, by FWL.

**Inference.** Pooled OLS with Driscoll–Kraay SEs. H1 is b ≠ 0, two-sided, α = 0.05. The final inference choice is made in Pass 3.

**Secondary analyses:**
- H3: EUR/USD coefficient = 0;
- a four-member interaction family with Holm correction;
- the fraction unpriced f;
- an equivalence test;
- the forecasting ladder M0–M5 + M7, with Clark–West as primary.

**Retired:** H2, the auction-conditional specification. It is biased under an efficient but noisy auction (P16).

**Samples:**
- dev 2015-01-06 → 2021-12-30: 1,708 dates, 5,124 rows;
- confirmation 2022-01-04 → 2026-03-05: 1,019 dates, 3,057 rows, T_conf = 1,013, sealed;
- forward holdout: after 2026-03-05, never pulled before `prereg-v1`.

**Power preview (B7b, TOPIX hedge).** Size 6.04% at nominal 5%. Power 78.2% at b = 0.25. MDE80 ≈ 0.257.

**Sequence (P36, P44).**
1. Pass 2: data and rebuild.
2. Pass 3: calibration, dev still blinded.
3. Tag `spec-dev-v1`; inference and calibration locked.
4. Pass 4: dev first look and dry run.
5. Pass 5: pre-registration → `prereg-v1`.
6. Pass 6: confirmation, once.

---

## 2. Where things stand (2026-10-04)

### Pass 1: complete (2026-10-02)

- **Package:** `ofilt/drift/` (spec, schema, io, blind, targets, calendar, inference, sim, forecast, models, fctests, registry).
- **Tests:** 171 in 22 modules, all passing; 5 skipped by default (2 sealed-fit real-data tests, 3 slow-tier Monte Carlo); about 3 minutes.
- **Spec amendments:** AM-01 (moderator main effects in the secondary family and M4) and AM-02 (size rule: 5,000 simulations at T_conf = 1,013).
- **Sealed fits so far:** 6 `dev_real` lines in `BLIND_FIT_LOG`, all sanctioned. None returned an FX coefficient.
- **Committed `RUN_REGISTRY.jsonl`:** empty.
- **Documents:** decisions P14–P36 in `docs/DECISIONS_P14_onward.md`, and replacement docs in `docs/replacements/`. v2.1 of PLAN is superseded by v2.2.

### Open flags (stable IDs)

| Flag | Status |
|---|---|
| 6 | TOPIX ex-dividend error → fixed in Pass 2 |
| 10 | DK slightly oversized → Pass 3, jointly with 12 |
| 12 | CW conservative → Pass 3 |
| 5 | Guard signature → resolve before Pass 2 |
| 2 | Fingerprint check is a mislabelling net only (frozen) |
| 4 | Coarse early-dev ticks |

Resolved: 1, 3, 7, 8, 9, 11, 13.

### Pass 2 inputs: pulled and verified in the handing-over chat

The details are in §5 and DATA_PROVENANCE §4.

### Not yet done by Isaiah (check in pre-flight, §6)

- Apply the Pass 1 replacement docs to the Project. This Project may still hold v2.0-era README, DATA_DICTIONARY and PROJECT_SETUP; that kit replaces PLAN.md separately.
- Merge the Pass 1 repo into his real repo.
- Reconcile Flag 5.
- The pending items in `PASS2_INPUTS.json`.

---

## 3. Non-negotiable rules (bring these into every builder message that touches data)

1. **No outcome data from 2022+, nothing after 2026-03-05.**
   - The Pass 2 build *writes* the sealed confirmation panel, and checks it only by **dates, counts, hashes and in-memory equality booleans**. It never prints or summarizes sealed values.
   - Event release dates and calendars for 2022+ are allowed.
2. **No computation whose output relates any predictor to any target on real data.** Predictors are FX, XAU, Japan 225, US controls and session FX.
   - **No sealed fit is sanctioned in Pass 2.** Pass 3 gets exactly one.
   - **Allowed on dev:** predictor-only statistics; target-only statistics without predictors (the A7 hedge-efficiency rerun); gap-only statistics (the staleness test).
3. **No `walk_forward`, no `build_design` fit, no inference call on real data** in Pass 2. The guards would refuse anyway, because `spec-dev-v1` doesn't exist. Do not work around them.
4. **The spec changes only through AM-xx entries that Isaiah approves.** The spec is pinned in `spec.py`, and the verbatim-diff test enforces the amendments log.
5. **The fingerprint mechanism is frozen** (Flag 2).
6. **Raw data never goes in the Claude Project.** The new `panel_dev.csv` and `MANIFEST.json` *do* go in after Pass 2; they are dev-only. The sealed panel never does.
7. **The forward holdout must not be touched, even transiently.** The patched `pull_dukascopy.py` caps every request (P38).

---

## 4. Pass naming (P44)

| Canonical | Meaning | Aliases in older text |
|---|---|---|
| Pass 2 | Data and rebuild | — |
| **Pass 3** | **Calibration** (dev still blinded) | "Pass 4", "the calibration pass" (AM-02 text, P35, Flags 10/12, interim H1/CW wording) |
| Pass 4 | Dev first look + P13(b) dry run (after `spec-dev-v1`) | "Pass 3" (early Pass 1 plans) |
| Pass 5 | Pre-registration → `prereg-v1` | "S4" |
| Pass 6 | Confirmation | — |

---

## 5. Pass 2 inputs: inventory, findings, hashes

Local layout: `~/Desktop/FX Project/raw/`, flat, because `build_panel.py` reads one directory. `organize_raw_inputs.sh` (kit folder 2) sets it up with hash verification.

| File (in `raw/`) | SHA-256 | Status and findings |
|---|---|---|
| `Book2.xlsx` | `40c0a051…27b4` | Unchanged since Pass 0. **Do not edit.** |
| `usdjpy_dukascopy_2015-01-01_2026-03-05.csv` | `d25497d2…b4cc` | Bid side confirmed (P37) |
| `eurusd_dukascopy_2015-01-01_2026-03-05.csv` | `7467495a…99c3` | Same procedure |
| `newbloombergdata_fixed.xlsx` | `ca51235b…370d` | **The build input.** Sheets: `1306` (OHLC); `1306 dividends` (÷10, `Regular Cash`); `1306 dividends RAW`; `TOPIX optional` (total-return close); `README` |
| `newbloombergdata.xlsx` | `2d91c756…31cc` | The original pull; provenance only |
| `xauusd_dukascopy_2015-01-01_2026-03-05.csv.gz` | `219c58a9…baf` | Clean (P41) |
| `jpn225_dukascopy_2015-01-01_2026-03-05.csv.gz` | `4490bb47…cf1` | Clean, but **fresh at 08:59 JST only from about 2018-07-02** (P42) |
| `checks/usdjpy_dukascopy_2019-06-04_2019-06-04.csv.gz` | `9c7bb9a0…45e` | Offer-side evidence |
| `pull_dukascopy.py` (code) | `6d9464f8…e4af` | Patched: UTC bounds, holdout cap, two new instruments (P38) |

Full hashes are in `PASS2_INPUTS.json`. The build must verify them all before reading anything.

### 5.1 1306: what was found, and why it matters

**Prices are fine.** The dates are identical to the miners' calendar (2,728); there are no NaNs; OHLC is consistent; there are no split artifacts. Six open = close = previous close rows all have a nonzero range, so they are coincidence on a 0.1 tick and were kept.

**Dividends were on a 10× basis.** The raw implied yields were 13.6–21%. Divided by 10, they match the actual ex-day opening drops:

| Ex-date | Amount ÷ prev close, ÷ 10 | Ex-day open drop |
|---|---|---|
| 2017-07-06 | 1.55% | 1.55% |
| 2019-07-08 | 2.00% | 2.16% |
| 2020-07-09 | 2.01% | 2.14% |
| 2021-07-08 | 1.80% | 2.01% |

One factor fits all 11 ex-dates (2015–2025). The split postdates 2025-07-09, and Bloomberg back-adjusted the prices but not DVD_HIST_ALL. **The factor is inferred, so CACS confirmation is pending.**

**The type `Distribution` would have been silently dropped** by `build_panel.CASH_TYPES`. Relabelling it fixes that without touching the miners' handling, which keeps their outputs byte-identical.

### 5.2 Japan 225: the coverage limitation in numbers

Share of Tokyo days whose 08:59 JST price is at most 5 minutes stale:

| Period | 2015-H1 | 2015-H2 → 2018-H1 | 2018-H2 onward |
|---|---|---|---|
| Share | 37% | about 0% | 97–99% |

In 2016–2017 the CFD had no bars from about 21:00 to 01:00 UTC.

Consequence: the Nikkei-proxy robustness check (claim tier ii) is effectively confirmation-period evidence plus about 3.5 years of dev. The P42 rule makes that mechanical.

### 5.3 What the handing-over chat computed on real data (blinding attestation addendum)

- **Structure:** hashes, sheet structure and dates of the Bloomberg file.
- **1306 checks:** OHLC booleans and counts; the stale-row dates, one of which (2023-10-06) is in confirmation.
- **1306 dividends:** dividend/price ratios, shown for dev ex-dates only and as pass/fail for 2022+.
- **XAU and Japan 225:** integrity, gaps, per-year counts, outlier minutes, including printed XAU closes around 2026-01-29 while checking an outlier.
- **Japan 225 staleness:** by year, including 2022+.

None of it involved a miner target. Record this in the Pass 2 status file's attestation.

---

## 6. Pre-flight: everything that must be true before the builder starts

Work through this with Isaiah. Every item has a check.

| # | Item | How to verify | If it fails |
|---|---|---|---|
| 1 | **CACS split ratio for 1306** | Isaiah runs `1306 JT Equity CACS <GO>` and reports the ratio and date | If ≠ 10, run `python regenerate_fixed_workbook.py --ratio <R>` (kit folder 2, run next to the original `newbloombergdata.xlsx`), then update its hash in `PASS2_INPUTS.json` |
| 2 | **Settings check (1A)** | Did the re-pulls of 5713 (2017-09-01 → 2017-10-31) and 5711 (2016-09-01 → 2016-10-31), pulled with the Appendix E formulas, match `Book2.xlsx` exactly? Which suffix, JT or JP? Was the same suffix used for 1306? | Neither matched: stop and diagnose (adjustment overrides, DPDF). 1306 used the other suffix: re-pull 1306 with the matching one, then redo the §5.1 checks (the builder's P2-1 does them) |
| 3 | **TOPIX total-return ticker** | Isaiah states the ticker used | Record it in P40 and DATA_PROVENANCE §4.4 |
| 4 | **Gotobi convention** | Isaiah confirms from a source he trusts. The usual convention: the 5th, 10th, 15th, 20th, 25th and the last day of the month; if one falls on a non-business day, the *preceding* business day. **[VERIFY]** | Use whatever he decides. It goes into an AM-xx/decision entry |
| 5 | **Guard signature (Flag 5)** | Isaiah pastes the `def check_access(...)` line from his real `ofilt/guards.py` | The builder adapts `_guards_fallback` / `io` / `blind` to call it correctly. **The tests must still show both tags absent and access denied** |
| 6 | **Pass 1 merged into the real repo** | In the repo: `env -u OFILT_RUN_SEALED python -m unittest discover -s tests -v` → 171 tests, 5 skipped, all passing | Fix the merge before any Pass 2 code |
| 7 | **Project docs current** | Project has `PLAN.md` v2.2, the updated `DATA_PROVENANCE.md`, `DECISIONS_P37_onward.md`, `PASS2_INPUTS.json`, `pull_dukascopy.py` (patched), and the Pass 1 replacements (`README.md`, `DATA_DICTIONARY.md`, `PROJECT_SETUP.md`, `DECISIONS_P14_onward.md`) | Isaiah uploads. Archive v2.0 and v2.1 of PLAN locally |
| 8 | **Raw files organized and hashed** | `bash organize_raw_inputs.sh` (dry run), then `--apply`; every line shows OK or MOVED | A hash mismatch means stop. Never "fix" a raw file by hand |
| 9 | **Claude Code environment** | Python 3.12, pandas, numpy, scipy, sklearn, openpyxl, PyYAML; repo clone; raw directory path known | Install with pip in his venv (`myenv`) |
| 10 | **Cost inputs started** (needed for Pass 3, not 2) | §11 table | Not blocking |

Items 1, 2 and 5 are **blocking**. Items 3 and 4 block only the tasks that use them.

---

## 7. Pass 2 work plan (what the builder does; Appendix A is the prompt)

Each stage has a goal, its tasks, acceptance criteria and a report to bring back. Stage boundaries are checkpoints. The builder commits after each item and updates `PASS2_STATUS.md` with **targeted edits**, never a whole-file rewrite.

### P2-0: Environment and integrity (no code changes)

- Verify every `PASS2_INPUTS.json` hash; refuse to continue on any mismatch.
- Run the Pass 1 suite: 171 tests, 5 skipped. Confirm `BLIND_FIT_LOG` has 6 dev_real lines and `RUN_REGISTRY.jsonl` is empty.
- Apply the Flag 5 adapter fix if needed, with tests.
- **Report:** the hash table, the test summary, and the guard decision.

### P2-1: Ingest and validate the new inputs (reports only; no panel changes)

Reproduce the handing-over chat's checks independently. The numbers must match Appendix B.

- **1306:** dates against Book2's miners' calendar; OHLC; stale rows; split artifacts.
- **1306 dividends:** fixed = RAW ÷ ratio; 11 rows; dev-period implied yields 1.36–2.10%, matching the ex-day drops. Confirmation-period rows: pass/fail only.
- **TOPIX total return:** calendar plus 2020-10-01.
- **XAU:** span, rows, per-year counts, gaps, outliers.
- **Japan 225:** the freshness-by-half-year table and the 2018-07-02 changeover.
- **Write** `reports/P2_1_inputs.md`.
- **Blinding:** dev values only. For 2022+, dates, counts and booleans only.

### P2-2: Builder extension (code and tests; synthetic fixtures only)

Extend `build_panel.py`, or add a module it calls, to produce the new columns. Proposed names and groups are the recommended default (D6). The builder may propose alternatives, which you check against P43.

| Column(s) | Definition | Schema group |
|---|---|---|
| `y_1306_oc` | ln(close/open), 1306, day t | TARGET_INPUTS |
| `ao_1306_gap_raw`, `ao_1306_gap_adj` | ln(open_t/close_{t−1}); adjusted version uses close_{t−1} − D_t with 1306 dividends | AT_OPEN |
| `xau_ret`, `xau_rv`, `xau_bv`, `xau_stale_start_min`, `xau_stale_end_min`, `xau_bars` | Same dark window and price-at-instant rule as `usdjpy_*` | PRE_OPEN_ROBUSTNESS (staleness and bars may be PROVENANCE, but P42-style rules must be able to read staleness) |
| `n225_ret`, `n225_stale_start_min`, `n225_stale_end_min`, `n225_bars` | Same dark window; Japan 225 CFD | PRE_OPEN_ROBUSTNESS |
| `usdjpy_us_ret` | Sum over the US sessions inside the window (NY dates t_prev … t−1, as in P11) of ln(USDJPY at NY close / at NY open), price-at-instant rule, DST-aware | PRE_OPEN_ROBUSTNESS |
| `ewj_oc_jpy` | `ewj_oc + usdjpy_us_ret` (yen-denominated EWJ); NaN where `ewj_oc` is NaN | PRE_OPEN_ROBUSTNESS |
| `gotobi_day` | Per Isaiah's convention (pre-flight item 4) | PRE_OPEN_ROBUSTNESS |
| `c_usdjpy_sess_ret`, `c_eurusd_sess_ret` | Price at 09:00:00 JST (close of the bar labeled 08:59) → price at the session close (15:00 JST to 2024-11-04; 15:30 JST from 2024-11-05) | CONTEMPORANEOUS (never a feature) |
| `ao_topix_gap_tradj` (fallback only) | `ao_topix_gap` + TOPIX dividend component (TR log return − price log return) | AT_OPEN; flagged fallback-only |

Unit tests use synthetic minute bars with known answers:
- the window bounds, including the 2024-11-05 close change;
- the price-at-instant rule (the bar labeled X−1 minute);
- DST for the NY session;
- endpoint staleness;
- the gotobi calendar on known dates;
- the dividend-adjusted gap identity.

**The builder does not touch** `inference.py`, `sim.py`, `forecast.py`, `models/*` or `fctests.py` (D11). That keeps the C7 slow-tier hashes valid, and the robustness designs belong to the confirmation-script work later.

### P2-3: Schema, targets, spec

- **`schema.py`:** add `PRE_OPEN_ROBUSTNESS` and populate `CONTEMPORANEOUS`. `PRE_OPEN_FEATURES` stays at **exactly the 20 Pass 1 columns** (add a test that pins them and M7's feature list). Every column still sits in exactly one group (the static test).
- **`targets.HEDGE_GAP_FOR`:** add `y_1306_oc → ao_1306_gap_adj`.
- **Spec amendments, drafted for Isaiah and not applied until he approves:**
  - **AM-03:** `target.hedge_oc_column: y_topix_oc → y_1306_oc` (plus pins and tests).
  - **AM-04:** `data.dev_panel_sha256` and `data.sealed_panel_sha256` → the new hashes after P2-4.
  - **AM-05**, if Isaiah adopts P42: the Nikkei-proxy rule as a robustness entry, "n225 control only where `n225_stale_start_min` ≤ 5 and `n225_stale_end_min` ≤ 5".
  - **AM-06**, robustness list additions: `xau_control`, `ewj_yen_denominated` (now available), `gotobi_mechanism`, the mechanism specification with session FX.
- **`io.load_dev`:** refuses schema drift, so it must accept the new column set only via the updated schema.

### P2-4: Rebuild

Run the extended build on `raw/` into a fresh output directory. It writes `panel_dev.csv`, `panel_confirm_SEALED.csv` and `MANIFEST.json`.

**Acceptance criteria. All must hold; any failure means STOP.**

- (a) **Old-column invariance, dev.** The 41 Pass 1 columns are **identical** to the current `panel_dev.csv`: value equality including NaN pattern, plus the SHA-256 of an old-column projection written with the original CSV settings equal to `7366…`.
- (b) **Old-column invariance, sealed.** An **in-memory** equality assertion against the sealed file produced by the *original* build code on the same inputs, printing only `True`/`False`. Better still, the old-column projection hash equals `9c18a6c1…`. **Never print or summarize sealed values.**
- (c) **Calendar cross-check.** The sealed panel's dates equal `calendar.confirmation_calendar()` (1,019 dates), and dev's are unchanged (1,708).
- (d) **Rows:** dev 5,124, sealed 3,057.
- (e) **New columns.** Coverage matches P2-1: XAU about complete; Japan 225 fresh ≥ 95% from 2018-07; 1306 present on every row; `ewj_oc_jpy` NaN exactly where `ewj_oc` is.
- (f) **Every build-time assertion of the original `build_panel.py` still passes.**

If (a) or (b) fails only because of CSV float formatting, prove it with a value comparison (dev) or an in-memory comparison (sealed) before proceeding. Never accept an unexplained change in old columns.

### P2-5: Dev-only analyses (stop afterwards for decisions)

- **A7 on 1306.** The P17 hedge-efficiency comparison with `y_1306_oc` as the hedge: windows {60, 120, 250, 500, expanding}; β on non-excluded rows; **common rows**; dev only; variance of the abnormal open→close return in bp². The rule: expanding stays primary unless it loses on common rows; **STOP and flag** if it loses for any ticker.
- **Index-staleness test.** On dev non-ex-dividend dates, regress `ao_topix_gap` on `ao_1306_gap_adj`, and the reverse; report slope, R² and N. Interpretation: a slope of the index gap on the ETF gap clearly below 1 means a stale index open, which caveats the TOPIX-index fallback. This test **documents**; the primary hedge is 1306 either way.
- **1306 checks for the P18 fallback rule:**
  - split/dividend adjustment: CACS ratio confirmed; adjusted dividends match the ex-day drops; no discontinuities;
  - open-auction timing: see D8.
- **Japan 225 coverage under the P42 rule:** the number of dev and confirmation nights eligible (counts only for confirmation).
- **Report:** `reports/P2_5_dev_checks.md`.

### P2-6: Records

- Draft decision entries P45 onward for everything decided in Pass 2.
- Apply the AM-xx amendments Isaiah approved, with pins and the verbatim-diff test updated.
- Update `DATA_DICTIONARY.md` (new columns and groups) and `DATA_PROVENANCE.md` (the build), and add the new hashes to `PASS2_INPUTS.json` or MANIFEST.
- **The new `panel_dev.csv` and `MANIFEST.json` go to the Project. The sealed panel never does.**

### P2-7: Final suite and status

- **Full suite:** expect 171 + new tests, with only the 5 known skips.
- **Slow tier:** if any C7-hashed file changed (it shouldn't, by D11), rerun it once, detached (about 9 minutes).
- **Final `PASS2_STATUS.md`:** attestation; open flags; next actions (Pass 3 inputs: costs, the sealed-fit sanction, decisions).

---

## 8. Decision register (prepare each one for Isaiah; his decision is final)

Each entry gives the trigger, the options, a recommended default with its reason, and what the decision changes.

**D1: CACS split ratio (pre-flight 1).**
- *Default:* if the ratio is 10, accept the corrected file as is.
- *If not:* regenerate with the true ratio, rerun P2-1's dividend checks, and update the hash.
- *Reason:* the amounts must be on the same share basis as the prices, or the hedge-gap dividend adjustment is wrong by the factor's error.

**D2: Settings-check suffix (pre-flight 2).**
- *Default:* proceed only if the 1306 suffix is the one that reproduced Book2 exactly.
- *Reason:* a different suffix can mean a different venue or composite, or different adjustments, so the hedge would be built differently from the miners.

**D3: TOPIX total-return ticker.** Record it. It is used on the fallback path only.

**D4: Gotobi convention.**
- *Default:* the previous business day for a gotobi date that falls on a holiday **[VERIFY]**.
- *Effect:* it defines `gotobi_day`, which is used only in the mechanism specification.

**D5: Guard signature (Flag 5).**
- *Default:* adapt the call to the real signature, and keep the fail-closed behaviour (any exception means denial).
- *Test:* in the real repo, `load_confirm` and `require_unblinded(dev_real)` still raise.

**D6: Column names and schema groups (P43).**
- *Default:* the §7 P2-2 table; `PRE_OPEN_FEATURES` unchanged.
- *Reason:* M7 uses the whole allowlist, and the shared-sample rule would shrink M7's sample because of the Japan 225 staleness and NaNs. A changed allowlist silently changes a Pass 1 specification.

**D7: Adopt the Japan 225 rule (P42)?**
- *Options:*
  - (a) adopt "both endpoints at most 5 minutes stale" as AM-05;
  - (b) a different threshold;
  - (c) drop the proxy and weaken claim tier (ii).
- *Default:* **(a)**.
- *Reason:* it's mechanical, it's stated before results, it keeps about 3.5 years of dev and almost all of confirmation, and 5 minutes is well inside the 08:59–09:00 buffer logic. Without the proxy, the exposure claim rests only on wording.

**D8: The 1306 "open-auction timing" check (P18).**
- *Problem:* verifying intraday that PX_OPEN is the 09:00 itayose print would need Bloomberg intraday bars. Those go back only months, which means **forward-holdout dates**, so they are forbidden.
- *Options:*
  - (a) treat the check as passed on documented exchange convention plus consistency evidence (P2-5: the 1306 gap tracks the TOPIX gap tightly; no excess open = previous close);
  - (b) treat it as failed and switch to the raw primary;
  - (c) defer the intraday check to after `prereg-v1` as a forward-holdout sanity check.
- *Default:* **(a), recording (c) as a post-confirmation check.**
- *Reason:* there is no admissible evidence of a timing problem, and the P18 rule's purpose (a tradable, non-stale hedge) is served.

**D9: A7 on 1306 outcome.** If expanding is lowest on common rows for all three tickers, keep it, as expected. Otherwise **STOP**: this is a nuisance choice to put to Isaiah. The criterion uses no FX, so either outcome is legitimate, but it must be decided before `spec-dev-v1`.

**D10: The staleness-test result.** Document only. A slope of the index gap on the 1306 gap clearly below 1 confirms the "staleness caveat" wording of the fallback secondary. It changes nothing in the primary analysis.

**D11: Pass 2 scope.**
- *Default:* no changes to inference, sim, forecast, models or fctests in Pass 2.
- *Reason:* it keeps the C7 slow-tier results valid without a rerun, and the robustness designs belong to the confirmation-script work.
- *Exception:* if Isaiah wants the robustness designs built now, accept a slow-tier rerun, about 9 minutes, detached.

**D12: Approve the AM-03, AM-04, AM-05 and AM-06 texts.** Show Isaiah the exact old and new lines. These are the only spec changes in Pass 2.

**D13: Old-column invariance fails.** **STOP, never proceed.** Diagnose CSV formatting, an input hash, or an unintended code change. A changed old column would invalidate Pass 1 calibration numbers and the A6 constants.

**D14: Project update after Pass 2.**
- *Default:* upload the new `panel_dev.csv` and `MANIFEST.json`, and the updated docs.
- Never upload the sealed panel or any raw file.

**D15: Cost inputs (for Pass 3).** Not decided in Pass 2, but start collecting them (§11).

---

## 9. Verification protocol (what to check in every builder report)

At each checkpoint, read the builder's `PASS2_STATUS.md` (Progress, Next action, Decision log tail, Flags, Attestation) and check:

1. **The suite is green, with only the known skips.** Any new skip must be justified.
2. **The blinding attestation lists every real-data computation since the last report.** None relates a predictor to a target. Confirmation-period outputs are only dates, counts, booleans and hashes.
3. **`BLIND_FIT_LOG` still has 6 dev_real lines** (no sealed fit in Pass 2), and `RUN_REGISTRY.jsonl` is still empty.
4. **The numbers match Appendix B** wherever they are reproductions.
5. **No unapproved spec edit.** The verbatim-diff test passes with only the approved AM-xx entries.
6. **Old columns are invariant** (P2-4) before any downstream step.
7. **Deviations are recorded.** Anything beyond the prompt appears under "Deviations" with a reason.

Red flags that warrant an immediate stop message:
- any printed statistic of a sealed-period target;
- any regression or correlation between a predictor and a target;
- a raw-file hash mismatch;
- `PRE_OPEN_FEATURES` changed;
- a sealed fit run;
- a pull past 2026-03-05;
- a hand-edited raw file;
- whole-file status rewrites, which waste the builder's context.

---

## 10. Pitfalls already met (avoid repeating them)

**Process:**
- **Resume messages that never got pasted.** The builder then follows only the original prompt. Always deliver prompt + resume message together, and check the status file to confirm the decisions landed.
- **Whole-file status rewrites** cost about 16k tokens each. Require targeted edits.
- **Builder over-engineering:** the Pass 1 fingerprint mechanism. Say "no hardening beyond the spec".

**Shell and Python:**
- **Partial code edits** duplicated loops. Give whole files or whole functions, via heredoc.
- **Indented code pasted into a shell** caused IndentationErrors. Use heredocs or script files.
- **Placeholder paths left in commands.** Quote paths with spaces.
- **macOS auto-decompressing `.gz`:** hash the exact file that is used.
- **Plain `nohup … &` dies with the tool call.** Use `setsid nohup … < /dev/null &` for long runs.

**Data:**
- **Dukascopy reads naive datetimes as local time.** It is fixed in the patched script; keep it.
- **Bloomberg dividend basis can differ from the price basis.** Always check implied yields against ex-day drops.
- **`CASH_TYPES` silently drops unknown dividend types.**

**Code and tests:**
- **pandas `attrs` drop silently.** Provenance is also passed by keyword (the A4 design).
- **The C7 slow-tier staleness check** hashes `c7_mc.py`, `fctests.py`, `forecast.py`, `models/linear.py`, `sim.py` and `inference.py`. Editing any of them forces a rerun.

**Reasoning:**
- **Cross-DGP comparisons mislead.** Compare tests on a common data-generating process (the withdrawn Flag 12 sentence).
- **The forward holdout can be touched transiently** by "download then trim" code. Cap at the request instead.

---

## 11. After Pass 2: Pass 3 (calibration) preview

Pass 3 runs on the rebuilt dev panel with the 1306 hedge, through **one** sealed fit that Isaiah sanctions explicitly. That will be dev_real line 7. It feeds:

- the binding AM-02 size run: 5,000 simulations at T_conf, band [3.5%, 6.5%];
- power at b ∈ {0.10, 0.25, 0.40} and the MDE;
- the joint H1/Clark–West cross-tab in the confirmation structure (Clark–West trains on dev-length history and evaluates on T_conf dates);
- the Flag 10/12 decisions: DK-normal, bootstrap, or simulation-calibrated critical values;
- the SESOI and TOST viability.

The task numbering is in P35 (T1–T7; T1 = size, T3 = joint cross-tab, T4 = Flags 10/12, T5 = SESOI/TOST). Each outcome becomes an AM-xx. Then **`spec-dev-v1`**.

**Cost inputs to collect from Isaiah** (primary value + low/high):

| Input | Notes |
|---|---|
| Notional per name (¥) | Your assumption; impact depends on it |
| Commission per side, miners | Including 10% consumption tax on commission [VERIFY broker schedule] |
| Commission per side, 1306 | Same |
| Auction impact per side, miners (bp) | Suggest 0 / 2 / 5 for sensitivity |
| Auction impact per side, 1306 (bp) | Same |
| Intraday short cost | Broker-specific; whether an open-to-close margin short pays a borrow or day-trade fee [VERIFY] |

Round trip = 2 × (miner commission + impact) + β × 2 × (1306 commission + impact) + short cost.

SESOI = round trip / mean |partialled overnight USD/JPY|. The denominator uses predictor data only.

**Earlier arithmetic:** at about 10 bp the equivalence test can declare equivalence when |b̂| < 0.18; at about 5 bp it essentially cannot.

---

## Appendix A: Pass 2 build prompt (for Claude Code on Isaiah's Mac)

Fill in `<REPO>` and `<RAW>` (expected `~/Desktop/FX Project/raw`), and the pre-flight answers marked ⟨…⟩, before giving it to Isaiah.

````markdown
# Pass 2: data and rebuild for the overnight-FX drift study

You are building Pass 2 of a pre-registered study for Isaiah Choi, who makes all decisions. Verify, don't assume. If anything is fatally wrong, say so and stop that item; never silently work around it. Accuracy beats speed.

## Context (read first)
- Repo: <REPO> (git; contains ofilt/drift from Pass 1, spec/, tests/, tools/, docs/, reports/, BLIND_FIT_LOG, RUN_REGISTRY.jsonl, PASS1_STATUS.md).
- Raw inputs: <RAW> (flat). Hashes: PASS2_INPUTS.json (copy in the repo's docs/ or the Claude Project).
- Read, in this order:
  1. docs/PLAN.md (v2.2);
  2. DATA_PROVENANCE.md §4;
  3. DECISIONS_P37_onward.md;
  4. docs/DECISIONS_P14_onward.md (P17, P18, P29, P34, P36);
  5. PASS1_STATUS.md: Decision log entries A5, B5, C1, C6, C7 only.
- Do not read the Math 86 PDF.

## Pre-flight answers (from Isaiah)
- CACS 1306 split: ratio ⟨10⟩, date ⟨…⟩ → the corrected dividend sheet is ⟨valid / must be regenerated⟩.
- Settings check: suffix ⟨JT|JP⟩ reproduced Book2 exactly; 1306 used ⟨same⟩.
- TOPIX total-return ticker: ⟨…⟩.
- Gotobi convention: ⟨5th/10th/15th/20th/25th/month-end; holiday → previous business day⟩.
- Guard signature: ⟨def check_access(...)⟩.
- Decisions already taken: ⟨D6 default; D7 adopt/pending; D8 (a); D11 default⟩.

## Hard rules
1. **Inputs:** verify every PASS2_INPUTS.json hash before reading; on a mismatch, STOP. Never edit raw files. Never download anything; there is no pull step in this pass.
2. **Blinding:** no computation whose output relates ANY predictor (usdjpy_*, eurusd_*, xau_*, n225_*, US controls, session FX) to ANY target (y_*, abn/raw/cc targets) on real data.
   - No sealed fit (OFILT_RUN_SEALED stays unset). No walk_forward or inference call on real data.
   - Allowed on dev: predictor-only stats; target-only stats without predictors (A7); gap-only stats (staleness test).
   - The sealed confirmation panel is WRITTEN by the build and checked only via dates, counts, hashes and in-memory equality booleans. Never print, summarize or plot sealed values.
3. **No change to:** ofilt/drift/inference.py, sim.py, forecast.py, models/*, fctests.py (keeps the C7 slow-tier hashes valid). Also no change to PRE_OPEN_FEATURES (exactly the 20 Pass 1 columns).
4. **Spec changes:** only as AM-xx entries that Isaiah has approved. Draft them; don't apply them until approved. The fingerprint mechanism in blind.py is frozen.
5. **Stop** at every point marked STOP, and whenever a decision isn't covered here.

## Checkpointing
- After each numbered item: run the suite (`env -u OFILT_RUN_SEALED python -m unittest discover -s tests -v`), commit, and update PASS2_STATUS.md with TARGETED edits (never re-emit the whole file). Sections: Progress, Next action, Decision log, Test results, Flags, Blinding attestation, Deviations.
- Stop at the next item boundary when any of these is true: you have written more than ~1,500 lines this response; the next item is large; 3 items are done this response; you notice yourself re-printing large files.
- End with one line naming the next item.
- Long runs: `setsid nohup ... < /dev/null &`.

## Items
- **P2-0** Verify hashes; run the suite (expect 171 tests, 5 skipped); confirm BLIND_FIT_LOG = 6 dev_real lines and RUN_REGISTRY empty. Adapt the guard to the real signature, keeping it fail-closed, with tests (load_confirm and dev_real unblinding still refused).
- **P2-1** Validate the new inputs, independently reproducing DATA_PROVENANCE §4:
  - 1306 calendar = the miners' calendar (2,728); OHLC; stale rows; no split artifacts;
  - dividends fixed = RAW / ratio, 11 rows, dev implied yields 1.36%–2.10% vs ex-day drops (2022+: pass/fail only);
  - TOPIX total return: calendar + 2020-10-01;
  - XAU: 3,957,473 rows, span, gaps, outliers;
  - Japan 225: 3,314,917 rows; fresh-08:59 share by half-year; the 2018-07-02 changeover.
  - Write reports/P2_1_inputs.md.
- **P2-2** Extend the build (build_panel.py or a module it calls) for the columns in PASS2_HANDOFF §7, P2-2 table, with Isaiah's naming decisions. Use the price-at-instant rule (close of the last bar labeled ≤ X − 1 min). Session FX starts at 09:00:00 JST (bar labeled 08:59) and ends at the session close (15:00 JST to 2024-11-04; 15:30 from 2024-11-05). The US session is NY 09:30–16:00 ET, DST-aware, for NY dates t_prev … t−1. Synthetic-fixture unit tests for every column.
- **P2-3** Schema: new PRE_OPEN_ROBUSTNESS group; CONTEMPORANEOUS populated; PRE_OPEN_FEATURES pinned by a test; every column in exactly one group. targets.HEDGE_GAP_FOR gains y_1306_oc → ao_1306_gap_adj. Draft AM-03 (hedge column), AM-04 (data hashes; filled after P2-4), AM-05 (Japan 225 rule, if adopted), AM-06 (robustness list) as exact old/new lines. STOP for approval.
- **P2-4** Rebuild into a fresh output directory. Acceptance criteria (STOP on any failure):
  - (a) the 41 Pass 1 columns of the new dev panel equal the old panel_dev.csv, with values and NaN pattern identical, and the old-column projection's SHA-256 = 736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42;
  - (b) the sealed old columns are equal, in memory, to the original build's sealed output on the same inputs (print a boolean only); ideally the projection hash = 9c18a6c106356139a375ecd7b3e6eaa085d937341c02817021003a4451c6b826;
  - (c) sealed dates == calendar.confirmation_calendar() (1,019); dev dates unchanged (1,708);
  - (d) rows: dev 5,124, sealed 3,057;
  - (e) new-column coverage consistent with P2-1;
  - (f) every original build assertion still passes.
  - Print only counts, spans and hashes for the sealed file.
- **P2-5** Dev-only checks:
  - A7 on 1306 (P17 rule; windows {60, 120, 250, 500, expanding}; β on non-excluded rows; common rows; bp² variance of the abnormal oc). STOP and flag if expanding is not lowest for every ticker.
  - Index-staleness test: ao_topix_gap on ao_1306_gap_adj, and the reverse, on dev non-ex-dividend dates (slope, R², N).
  - 1306 fallback-rule evidence (split/dividend consistency; gap tracking).
  - Japan 225 eligible-night counts under the proposed rule (confirmation: counts only).
  - Write reports/P2_5_dev_checks.md. STOP for Isaiah's decisions (D7–D10).
- **P2-6** Apply the approved AM-xx (pins, verbatim-diff test); add decision entries P45 onward; update DATA_DICTIONARY.md and DATA_PROVENANCE.md; record the new hashes (MANIFEST.json, PASS2_INPUTS.json).
- **P2-7** Full suite (the 5 known skips only); slow tier only if a C7-hashed file changed (it shouldn't). Final PASS2_STATUS.md with attestation, open flags, and next actions (Pass 3: cost inputs, a one-sealed-fit sanction, the decisions).
````

---

## Appendix B: Reference numbers (for verifying reproductions)

| Quantity | Value | Source |
|---|---|---|
| Dev | 2015-01-06 → 2021-12-30; 1,708 dates; 5,124 rows; SHA-256 `736636…6a42` | MANIFEST |
| Confirmation | 2022-01-04 → 2026-03-05; 1,019 dates; 3,057 rows; SHA-256 `9c18a6…b826` (pre-rebuild) | MANIFEST, P10 |
| T_conf | 1,013. The 6 all-ticker-excluded dates are 2022-02-09, 2022-08-09, 2024-08-08, 2025-02-13, 2025-08-08 and 2025-11-11 | calendar.py |
| Dev exclusion rows | excl_inference 182; excl_d2 273; excl_forecast_eval 175; 774 rows without β (warm-up) | A5 |
| A6 constants | Winsor usdjpy [−1.6482588843e−02, 1.4399911615e−02]; eurusd [−1.6324806371e−02, 1.5438152188e−02]; rv_per_bar median 1.2950114214e−08 | spec |
| A7 (TOPIX hedge, all-days β; bp²) | Expanding 24,052 / 11,662 / 17,750 (5706 / 5711 / 5713); no hedge 29,603 / 15,855 / 22,955 | reports/A_hedge_efficiency.md |
| DK lag | 7 at T = 1,708; 6 at T = 983 or 1,013 | spec rule |
| B7b preview | Size 6.04% [5.41, 6.73]; power 22.5 / 78.2 / 98.5% at b = 0.10 / 0.25 / 0.40; MDE80 0.257; SE/sd 0.960 | reports/B7b |
| C7 | CW size 2.67% [1.36, 5.17]; power 100% at b = 0.4 and 89.5% [84.5, 93.0] at b = 0.25; same-DGP H1 87.5%; agreement 170/175 | reports/C7_mc.json |
| 1306 | 2,728 rows, calendar identical; 6 coincidental stale rows; 11 dividends (7 dev, 4 confirmation); dev implied yields after ÷10: 1.36 / 2.10 / 1.55 / 1.75 / 2.00 / 2.01 / 1.80% (2015–2021) | DATA_PROVENANCE §4.4 |
| XAU | 3,957,473 rows; 2015-01-01 23:00 → 2026-03-06 00:00 UTC; 4 outlier minutes (kept) | §4.2 |
| Japan 225 | 3,314,917 rows; 2015-01-02 00:00 → 2026-03-06 00:00 UTC; fresh 08:59 share 37% (2015-H1), ~0% (2015-H2 to 2018-H1), 97–99% after; changeover 2018-07-02 | §4.3 |
| Sealed fits | 6 dev_real lines (B5 ×3, B7 ×2 with 1 killed, B7b ×1) | BLIND_FIT_LOG |

---

## Appendix C: Message templates

**C1. Resume or continue (same Claude Code session):**
> Continue Pass 2 at ⟨item⟩. Decisions since the last checkpoint: ⟨…⟩. Rules unchanged (Hard rules 1–5). Update PASS2_STATUS.md with targeted edits only.

**C2. Decision delivery:**
> Decisions (Isaiah, ⟨date⟩): D⟨n⟩ = ⟨choice⟩ because ⟨one-line reason⟩. Record each in the decision log as "(Isaiah, ⟨date⟩)". Draft or apply AM-⟨xx⟩ as ⟨exact text⟩. Then continue at ⟨item⟩.

**C3. Stop the line:**
> STOP. ⟨What was observed⟩ violates ⟨rule⟩. Do not proceed. Record it under Flags (new ID ⟨n⟩), list every computation since the last checkpoint in the attestation, and wait.

**C4. New session (if the Claude Code context runs out):** start a fresh Claude Code session in the repo, give it the Appendix A prompt again plus the C1 resume message, and tell it to read PASS2_STATUS.md first.

---

## Appendix D: What changed in this hand-off chat (2026-10-04), in one place

- Verified the Bloomberg 1306 / TOPIX-TR workbook. Produced the corrected copy (dividends ÷10, `Distribution` → `Regular Cash`, RAW sheet kept, README sheet) and its hashes.
- Patched `pull_dukascopy.py`: UTC bounds, forward-holdout cap, XAUUSD and JPN225. Confirmed bid side.
- Verified XAU and Japan 225. Found the Japan 225 coverage limitation and proposed the staleness rule.
- Wrote: PLAN v2.2; DATA_PROVENANCE §4 (and resolved its offer-side open item); DECISIONS P37–P44; PASS2_INPUTS.json; `organize_raw_inputs.sh`; and this document.

---

## Appendix E: Bloomberg formulas used (for re-pulls and the settings check)

**Settings check (1A).** Use a scratch workbook. Compare each sheet with `Book2.xlsx` cell for cell; it must be exact. Repeat with `JP` in place of `JT` if needed.

```
=BDH("5713 JT Equity","PX_OPEN,PX_LAST,PX_HIGH,PX_LOW","20170901","20171031","Dir=V","Dts=S","Sort=A","Days=T","Fill=B","CshAdjNormal=N","CshAdjAbnormal=N","CapChg=Y","UseDPDF=N")
=BDH("5711 JT Equity","PX_OPEN,PX_LAST,PX_HIGH,PX_LOW","20160901","20161031","Dir=V","Dts=S","Sort=A","Days=T","Fill=B","CshAdjNormal=N","CshAdjAbnormal=N","CapChg=Y","UseDPDF=N")
=BDH("TPX Index","PX_OPEN,PX_LAST","20170901","20171031","Dir=V","Dts=S","Sort=A","Days=T","Fill=B")
```

**1306 (as pulled; use the suffix that passed 1A):**

```
=BDH("1306 JT Equity","PX_OPEN,PX_LAST,PX_HIGH,PX_LOW","20150101","20260305","Dir=V","Dts=S","Sort=A","Days=T","Fill=B","CshAdjNormal=N","CshAdjAbnormal=N","CapChg=Y","UseDPDF=N")
=BDS("1306 JT Equity","DVD_HIST_ALL","DVD_START_DT=20150101","DVD_END_DT=20260305")
```

Override names can differ by terminal version **[VERIFY]**. If one is rejected, build the formula with **Spreadsheet Builder → Historical Data Table**, using these settings: capital changes Yes, normal cash No, abnormal cash No, non-trading days excluded.

After pulling: paste as values, delete any header rows, delete dividend rows with an ex-date after 2026-03-05, then hash the file.
