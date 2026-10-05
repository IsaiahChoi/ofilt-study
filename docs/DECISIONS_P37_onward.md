# DECISIONS P37 onward: Pass 2 inputs (2026-10-04) and pre-flight decisions (2026-10-05)

This file continues `DECISIONS_P14_onward.md` (P14–P36, Pass 1), which continues `DECISIONS_ADDENDUM.md` (P01–P13).

Status vocabulary:
- **ADOPTED** (Isaiah, date)
- **ADOPTED, PENDING** a named check
- **PROPOSED** (awaiting Isaiah)
- **EDITORIAL** (naming only; no methodological content)

Evidence for every entry is in `DATA_PROVENANCE.md` §4. Hashes are in `PASS2_INPUTS.json`.

**Status index (2026-10-05).** Later entries resolve or supersede parts of earlier ones; the earlier text is left exactly as adopted.

| Earlier entry | Current status |
|---|---|
| P39 (a), CACS split ratio | Resolved by P47 |
| P39 (b), settings check | Still PENDING |
| P40, TOPIX total-return ticker | Still PENDING. The workbook holds values only, so the ticker can't be recovered from it |
| P42, Japan 225 usage rule | Still PROPOSED. Decided at the Pass 2 decision checkpoint (P51), under the standards of P56 |
| P43, new columns outside the allowlist | ADOPTED as P50 |
| P36 step 1 ("merge into the real repo, reconcile `ofilt.guards`") | Restated by P45 and P46 |
| Validation numbers quoted in P28, P30 and P31 | For citation, superseded by P54 |

---

**P37: Dukascopy offer side is bid (ADOPTED, 2026-10-04; closes the DATA_PROVENANCE §1 open item).**

*Evidence:* a fresh bid-side pull of USD/JPY for 2019-06-04 matched the master on 1,199 of 1,199 overlapping bars, close for close.

*Effect:* every new Dukascopy series (XAU, Japan 225) is pulled bid-side, and window returns are consistent across series.

---

**P38: Patched pull procedure (ADOPTED, 2026-10-04).**

`pull_dukascopy.py` (SHA-256 `6d9464f8…`) makes three changes:

1. **Request bounds are timezone-aware UTC,** converted to local clock time before the library call. This is needed because the library reads naive datetimes as local time: a naive 2019-06-04 00:00 request returned data from 04:00 UTC on a US-Eastern machine.
2. **Every request is capped at end_date + 1 day + 1 minute.** No forward-holdout data is downloaded, even transiently (P13). The previous version fetched each year up to the current time and trimmed afterwards.
3. **Instruments added:** `XAUUSD` = `INSTRUMENT_FX_METALS_XAU_USD`; `JPN225` = `INSTRUMENT_IDX_ASIA_E_N225JAP`.

*Why the masters are unaffected:* their yearly fetches are contiguous, so a local-time offset only shifts the year boundaries, not coverage. Their UTC labels were verified independently by the release-timing test (§1). A re-pull of a full day matches them bar for bar.

---

**P39: 1306 hedge data accepted; dividend sheet corrected (ADOPTED, PENDING the CACS split ratio).**

- **Prices** (`1306`) are accepted as pulled: 2,728 dates identical to the miners' calendar, OHLC consistent, no split artifact. The six open = close = previous close rows have nonzero ranges, so they are coincidental and kept.
- **Dividend amounts are divided by 10** in `newbloombergdata_fixed.xlsx` (SHA-256 `ca51235b…`).
  - *Reason:* Bloomberg's capital-change adjustment rescaled the prices for a split that postdates the last ex-date in the file (2025-07-09), but it did not rescale the DVD_HIST_ALL amounts. The raw implied yields are 13.6–21%; divided by 10, they match the observed ex-day opening drops.
- **Type `Distribution` is relabelled `Regular Cash`.**
  - *Reason:* `build_panel.CASH_TYPES` would silently drop `Distribution`, which would make the Flag 6 fix a no-op. The miners' handling is unchanged.
- **Provenance:** `1306 dividends RAW` keeps Bloomberg's original values. The original pull (`newbloombergdata.xlsx`, SHA-256 `2d91c756…`) is archived locally.
- **PENDING:**
  - (a) `1306 JT Equity CACS <GO>`: confirm the ratio is 10 and record the date. If the ratio differs, regenerate the corrected copy.
  - (b) The settings-check result: which suffix (`JT`/`JP`) reproduced `Book2.xlsx` exactly, and whether 1306 used it. If 1306 used the other suffix, re-pull it before Pass 2.

---

**P40: TOPIX total-return series (ADOPTED as a fallback input, PENDING its ticker).**

The `TOPIX optional` sheet is a total-return index (level 1,916.75 in January 2015, against about 1,431 for the price index). It carries the TSE outage row for 2020-10-01, which the build drops exactly as it does for TOPIX.

*Use:* only if the P18 fallback fires (raw primary, abnormal secondary on the TOPIX index). The TOPIX dividend component on day t is the total-return log return minus the price log return; it fixes Flag 6 on that path.

*PENDING:* record the ticker used.

---

**P41: XAU/USD accepted as a robustness control (ADOPTED, 2026-10-04).**

*Integrity:* 3,957,473 rows, 2015-01-01 23:00 → 2026-03-06 00:00 UTC. No nulls, duplicates or OHLC violations. Gaps only at weekends and the Christmas and New Year closures. Four 1-minute moves over 2%, all judged genuine and kept (DATA_PROVENANCE §4.2).

*Role:* a dark-window XAU return, as a robustness control only (P34). It is not in the primary design and not in the PRE_OPEN_FEATURES allowlist (see P43).

---

**P42: Japan 225 CFD accepted with a coverage limitation; usage rule PROPOSED.**

*Integrity:* clean (DATA_PROVENANCE §4.3). But the 08:59 JST price is at most 5 minutes stale on about 0% of Tokyo days from 2015-H2 to 2018-H1, against 97–99% from 2018-H2 onward. The trailing 60-day share first reaches 95% on 2018-07-02.

*PROPOSED rule, to be decided by Isaiah during Pass 2 and written into the spec as an AM-xx before `spec-dev-v1`:*
- The Nikkei-proxy control applies only on nights where **both** window endpoints are at most 5 minutes stale.
- Robustness designs that use it are estimated on those nights only.
- Dev coverage is therefore about 2018-07 → 2021-12, and confirmation coverage is almost complete.

*Why a pre-stated rule:* any choice of usable nights made after seeing results would be a forking path. The build records endpoint staleness in minutes, so the rule is mechanical.

---

**P43: New columns live outside the primary allowlist (PROPOSED; recommended default for Pass 2).**

Pass 2's new predictors go in a new schema group, `PRE_OPEN_ROBUSTNESS`, which only robustness designs may use. The predictors are the XAU and Japan 225 dark-window returns, their staleness, the US-session USD/JPY return, the yen-denominated EWJ and the gotobi flag.

`PRE_OPEN_FEATURES` stays exactly the 20 columns of Pass 1. Session FX (09:00 → close) goes in `CONTEMPORANEOUS` and is never a feature.

*Reason:* M7 uses the whole PRE_OPEN allowlist. Adding columns would change M7's inputs. Because of the shared-sample rule (P27), the Japan 225 NaNs/staleness would also shrink every M7 comparison sample. Both effects would silently alter a Pass 1 specification.

---

**P44: Pass naming (EDITORIAL, 2026-10-04).**

| Canonical name | P36 step | Aliases in earlier documents |
|---|---|---|
| Pass 2: data and rebuild | step 2 | — |
| **Pass 3: calibration** (dev still blinded) | step 3 | "Pass 4", "the calibration pass" (AM-02's size-rule text, P35, Flags 10/12) |
| Pass 4: dev first look + P13(b) dry run | step 5, after the `spec-dev-v1` tag (step 4) | "Pass 3" (early Pass 1 planning) |
| Pass 5: pre-registration → `prereg-v1` | step 6 | "S4" |
| Pass 6: confirmation (once); forward holdout later | step 7 | — |

The AM-02 spec text ("Pass 4: rejection at b=0 …") is pinned and left verbatim. Its "Pass 4" means Pass 3 (calibration) under this naming.

---

**P45: The rebuilt Pass 1 repository is the canonical study repository (ADOPTED (Isaiah, 2026-10-05); restates P36 step 1).**

- The repository rebuilt on 2026-10-04/05 (HEAD `81905c1`; 205 tests, 4 skipped in the sandbox) is the study's only analysis repository.
  - It is not merged into FX-Project, which remains the archive of the Math 86 work.
  - Nothing from FX-Project is imported. If a file is ever wanted from it, it comes in through a new decision entry.
- The build code moves into this repository in Pass 2:
  - the original `build_panel.py`, `make_events.py` and `events.py`, byte for byte and frozen, under `build/pass1/`;
  - the Pass 2 extension under `build/pass2/` (P51).
- The repository is pushed to a **private** remote after setup and at every stage boundary. Raw data, panels and build outputs are never committed (`.gitignore`; P51).
- P36 step 1 now reads: set up the canonical repo on the Mac (`OFILT_DATA_DIR`, a portable checkpoint script, the `pass1-final` tag) and run the suite there.

*Reason:* merging two unrelated histories would bring unknown files into the blinded repo, possibly including Math 86 analyses of confirmation-period gaps and a guard module of unknown semantics. The rebuilt repo's history is the Pass 1 provenance, and its tags gate code in the same repository.

*Effect:* Flag 5 is resolved (P46). Pre-flight item 6 becomes "the suite is green on the Mac: 205 tests, OK, 5 skipped". The fifth skip is `test_docs_d6`'s Project test, which needs `/mnt/project`.

---

**P46: Conjunctive, fail-closed tag gate (ADOPTED (Isaiah, 2026-10-05); resolves Flag 5).**

- Access for a tag requires both of the following:
  - the fallback check: the tag exists in this repository and its commit is an ancestor of HEAD;
  - if `ofilt.guards.check_access` is importable, that call returns `None` or `True` without raising. Any exception, and any other return value, is a denial.
- In the canonical repo no `ofilt.guards` exists, so the fallback alone decides. The conjunction is defence in depth: an external guard can only add restrictions.
- It is implemented in `io._check_access` and `blind._tag_ok`. That is the tag gate; the fingerprint algorithm stays frozen.
- New tests:
  - an external guard returning `False` is denied;
  - one returning `None` while the tag is absent is denied;
  - one that raises is denied;
  - both satisfied in a temporary repo is granted.
- The existing tests (both tags absent in the main repo; `load_confirm` refused and logged) must still pass.

*Reason:* the Pass 1 adapter treated "the external guard returned without raising" as a grant. A guard that returns `False` on denial, or a stub, would have unblinded dev and confirmation data.

---

**P47: The 1306 split ratio is confirmed by issuer documentation (ADOPTED (Isaiah, 2026-10-05); resolves P39 pending item (a)).**

- *The issuer.* Nomura Asset Management's notice for NEXT FUNDS TOPIX ETF (1306), and its timely disclosure of 2026-02-17: each unit was split into 10, with record date 2026-03-31 and effective date 2026-04-01.
- *The amounts.* The raw `DVD_HIST_ALL` amounts ÷ 10 equal Nomura's published split-adjusted distribution per unit in every year its monthly report lists:
  - 2021: 3.66 yen (dev);
  - 2022–2025: checked as booleans, all equal.
  - All 11 ex-dates fall in July, with record date 10 July each year.
- *Consistency.* The effective date is after the panel's last date (2026-03-05). That explains every earlier finding:
  - no split discontinuity in the 1306 prices;
  - Bloomberg's capital-change adjustment rescaled the prices but not the dividend amounts;
  - one ÷10 factor fits all 11 ex-dates.
- `1306 JT Equity CACS <GO>` is now an optional confirmation of Bloomberg's own record, not a blocker.

*Effect:*
- `newbloombergdata_fixed.xlsx` (`ca51235b…`) is ACCEPTED as the build input. P39 remains PENDING only for item (b), the settings check.
- The split falls inside the forward holdout. The P13(a) discontinuity checks therefore gain 1306, around its 2026-03-31 record date and 2026-04-01 effective date, alongside 5706's.

---

**P48: Gotobi flag definition (ADOPTED (Isaiah, 2026-10-05); resolves D4 and the inconsistency between P34 and PASS2_HANDOFF §6).**

- **Nominal dates.** For each calendar month: the 5th, 10th, 15th, 20th, 25th and 30th (where it exists), and the month's last calendar day.
- **Roll.** A nominal date that is not a TSE trading day moves to the **preceding** trading day, even if that day is in the previous month. The trading calendar is the miners' calendar (Book2), which stands in for Tokyo banking days.
- **Flag.** `gotobi_day_t` = 1 if at least one nominal date lands on trading day t, otherwise 0. It is a single flag (the union), in `PRE_OPEN_ROBUSTNESS` (P50).
- **Reference values** (calendar data only, computed 2026-10-05):
  - dev: 529 of the 1,708 dates (31.0%; 74–78 per year);
  - confirmation: 319 of the 1,019 dates (31.3%).
- **Month-crossing rolls.** Exactly four nominal dates move into the previous month, and the builder's tests include all four:
  - 2019-05-05 → 2019-04-26;
  - 2020-01-05 → 2019-12-30;
  - 2021-05-05 → 2021-04-30;
  - 2025-01-05 → 2024-12-30.

*Source.* Ito & Yamada (2017), *Journal of International Economics* 109: 214–234 (NBER WP 22820).
- They describe the heavy-payment days as the 5th, 10th, 15th, 20th, 25th and 30th plus the month's last trading day, and model them with separate dummies.
- P34's wording ("dates ending in 5 or 0, plus month-end") matches this; PASS2_HANDOFF §6 dropped the 30th.
- The source states no holiday rule, so the preceding-business-day roll (the usual Japanese payment convention) is Isaiah's choice.
- Rolling the last calendar day back is identical to taking the month's last trading day.

*Use:* the mechanism specification only (PLAN §6 item 13). Its exact design is set in AM-06 under P56.

---

**P49: US-session USD/JPY window (ADOPTED (Isaiah, 2026-10-05)).**

- **Definition.** `usdjpy_us_ret_t` = Σ ln(P(close_d) / P(open_d)), summed over the NY dates d of the P11 session set (t_prev ≤ d ≤ t − 1, from Book2's US calendar). Prices come from the USD/JPY master under the price-at-instant rule.
- **Session times.**
  - open_d = 09:30 America/New_York;
  - close_d = 16:00, or **13:00 on NYSE early-close days**, where SPY's and EWJ's last prices are 13:00 prints;
  - DST comes from the tz database.
- **Early-close days in the sample:** 23, checked 2026-10-05 against NYSE Group / ICE holiday-calendar releases. None fall in 2026-01-01 → 2026-03-05. The build asserts that each one is a date in the US calendar.
  - 2015: 2015-11-27, 2015-12-24
  - 2016: 2016-11-25
  - 2017: 2017-07-03, 2017-11-24
  - 2018: 2018-07-03, 2018-11-23, 2018-12-24
  - 2019: 2019-07-03, 2019-11-29, 2019-12-24
  - 2020: 2020-11-27, 2020-12-24
  - 2021: 2021-11-26
  - 2022: 2022-11-25
  - 2023: 2023-07-03, 2023-11-24
  - 2024: 2024-07-03, 2024-11-29, 2024-12-24
  - 2025: 2025-07-03, 2025-11-28, 2025-12-24
- **No session.** `usdjpy_us_ret` = 0.0 exactly when `us_n_sessions` = 0, matching P11's convention for the controls.
- **Yen EWJ.** `ewj_oc_jpy` = `ewj_oc` + `usdjpy_us_ret`. EWJ is priced in dollars, so adding the USD/JPY log return converts it to yen. It is NaN exactly where `ewj_oc` is NaN.

*Reason:* the FX leg must span the same interval as the equity prints it converts.

---

**P50: Names and schema groups of the new columns (ADOPTED (Isaiah, 2026-10-05); resolves P43 and D6).**

- `PRE_OPEN_FEATURES` stays exactly the 20 Pass 1 columns. A test pins it and M7's feature list.
- **New group `PRE_OPEN_ROBUSTNESS`** (robustness designs only; refused by `select_features`): `xau_ret`, `xau_rv`, `xau_bv`, `n225_ret`, `usdjpy_us_ret`, `ewj_oc_jpy`, `gotobi_day`.
- **`PROVENANCE`** gains `xau_bars`, `xau_stale_start_min`, `xau_stale_end_min`, `n225_bars`, `n225_stale_start_min`, `n225_stale_end_min`.
  - The P42 rule reads the staleness columns as a sample filter, the way `earn_flag` is read. They are never regressors.
  - This follows the `usdjpy_*` precedent.
- **Other groups:**
  - `TARGET_INPUTS` gains `y_1306_oc`;
  - `AT_OPEN` gains `ao_1306_gap_raw`, `ao_1306_gap_adj` and `ao_topix_gap_tradj` (the last on the fallback path only);
  - `CONTEMPORANEOUS` gains `c_usdjpy_sess_ret` and `c_eurusd_sess_ret`.
- **Definitions** follow PASS2_HANDOFF §7 (the P2-2 table), P48 and P49.
  - Session FX ends at the close of day t itself: 15:00 JST through 2024-11-04 and 15:30 from 2024-11-05.
  - TSE half-day sessions were abolished in 2009, so none occur in the sample (DATA_PROVENANCE §4.6).
- **Panel shape.** The panel grows from 41 to 60 columns. The 19 new columns are appended after the old 41, in the order given in PASS2_ADDENDUM Appendix A′.
- `inference.FORBIDDEN_TARGET_NAMES` is derived from the schema groups, so the new predictor groups are refused as targets without editing `inference.py`.

*Reason (P43):* M7 uses the whole `PRE_OPEN_FEATURES` allowlist. Adding columns to it would silently change a Pass 1 specification, and the shared-sample rule would let Japan 225 staleness shrink every M7 comparison.

---

**P51: How Pass 2 runs: append-only build, one decision checkpoint, one switch commit, test-change protocol (ADOPTED (Isaiah, 2026-10-05)).**

**Order.**
1. P2-0: setup and integrity, including a docs sync and the `pass1-final` tag.
2. P2-0b: baseline reproduction of the original build.
3. P2-1: input validation.
4. P2-2: build extension.
5. P2-3a: drafts only.
6. P2-4: rebuild into a fresh folder.
7. P2-5: dev checks on that fresh panel, through standalone scripts.
8. **One decision checkpoint**: D7–D10, D12 and the amendment texts, the test changes, and the DATA_DICTIONARY draft.
9. P2-3b: **one switch commit**.
10. The C7 rerun.
11. P2-6: records.
12. P2-7: final suite and status.

*Why this order:* `io` requires the panel's columns to equal the schema and its hash to equal the spec. Changing the schema before the rebuild, or the panel before AM-04, would break every real-dev test. AM-03's content also depends on the P18 checks run in P2-5.

**Baseline.** Before any build code changes, the frozen original build must reproduce `7366…` and `9c18…` on the Mac. If it does not, stop and diagnose the environment (library versions). No code is changed to force a match.

**Append-only build.** The frozen original produces the 41 old columns. The old panels are read back as strings and the new columns are appended to the right. The old-column projection is then byte-identical by construction, and the sealed acceptance check is a hash computed in memory, with no value comparison of sealed data.

**Switch commit.** It contains the schema, `HEDGE_GAP_FOR`, `io`, the `blind` list (P52), the approved amendments, DATA_DICTIONARY, the approved test changes, and the panel switch. The Pass 1 dev panel is archived under its hash, so `BLIND_FIT_LOG` lines 1–6 stay verifiable.

**C7 and D11 (corrected rationale).**
- The C7 report's staleness key includes the spec file's SHA-256, not only the six code files. A comment-only spec edit on a scratch copy failed the staleness test (2026-10-05).
- The amendment batch therefore forces exactly one slow-tier rerun. With unchanged code and seeds, every replication must reproduce bit for bit. Any difference is a STOP.
- D11's scope stands: no change to `inference`, `sim`, `forecast`, `models` or `fctests`.

**Test-change protocol.**
1. The unchanged Pass 1 HEAD is tagged `pass1-final`, a lightweight tag (the guard recognises only `spec-dev-v1` and `prereg-v1`). This keeps the Pass 1 attestation reproducible.
2. An assertion that Pass 2 legitimately supersedes is rewritten to the new state, with a comment citing the superseding entry. It is never deleted without a replacement.
3. Every change is listed old → new in PASS2_STATUS and approved at the checkpoint. The doc-pin changes caused by P57 are pre-approved.

**Builder hygiene.** No raw or sealed file is ever opened or printed by any viewer. Inspection runs only through scripts that print counts, spans, hashes, booleans or permitted dev statistics. Sealed outputs live outside the repository and the Project.

**macOS.** There is no `setsid`. Long runs use the resumable `--budget` chunks of `tools/c7_mc.py`, or Isaiah's own Terminal. The expected suite on the Mac is 205 tests, 5 skipped.

---

**P52: Blinding-hygiene list for the new predictors (ADOPTED (Isaiah, 2026-10-05); a data-list exception to the Flag 2 freeze).**

- `blind.FX_NAMES` lists the columns the fingerprint guard never compares with target values. It gains `xau_ret`, `xau_rv`, `xau_bv`, `xau_bars`, `xau_stale_start_min`, `xau_stale_end_min`, `n225_ret`, `n225_bars`, `n225_stale_start_min`, `n225_stale_end_min`, `usdjpy_us_ret`, `ewj_oc_jpy`, `c_usdjpy_sess_ret` and `c_eurusd_sess_ret`.
  - `gotobi_day` is a calendar flag, like `boj_day`, and is not added.
  - The pre-existing US controls keep their Pass 1 treatment.
- `test_blind`'s coverage check is extended to these columns.
- `io` registers `y_1306_oc` as a real target at load (label `dev_real:y_1306_oc`), as it already does for `y_oc` and `y_topix_oc`.
- The fingerprint algorithm, thresholds and exemptions are unchanged. Neither `io.py` nor `blind.py` is in the C7 hash list.

*Reason:* Pass 2's rule 2 counts these columns as predictors, so the guard must not compare their mantissas with targets. Without this change, `usdjpy_us_ret` would also fail the existing coverage test. Renaming columns to avoid that test would defeat its purpose.

---

**P53: Flags 14 and 15 are accepted as implemented (ADOPTED (Isaiah, 2026-10-05); resolves both).**

Flag 14 (C5):
- (a) Pesaran–Timmermann is one-sided, with "up" = value > 0. It is undefined when either series has a constant sign.
- (b) Diebold–Mariano uses squared-error loss.
- (c) Pooled OOS R² is pooled over rows.
- (d) The training-window base rate is the per-fold training up-share, averaged over the rows it applies to.
- (e) The fold log carries `train_up`.

Flag 15 (C6):
- (a) Whole dates are permuted among evaluation dates that have the same ticker set.
- (b) One permutation per (fold, repeat) is shared by all features.
- (c) "Exceeds noise" means a mean dMSE above the noise column's largest dMSE over the 20 repeats.
- (d) Synthetic runs go to a temporary registry; only real runs go to the committed `RUN_REGISTRY.jsonl`.
- (e) The data hash covers column names, dtypes and pandas row hashes.

*Reason:* each choice is defensible and consistent with the spec where the spec speaks. The tests use the spec's date-mean aggregation; OOS R² is descriptive. Any alternative would edit C7-hashed files.

---

**P54: Citable validation numbers after the rebuild (ADOPTED (Isaiah, 2026-10-05)).**

From now on, write-ups cite the rebuilt repository's numbers, because they are the ones the code reproduces:

| Quantity | Rebuilt value |
|---|---|
| Clark–West size | 3.00% (9/300, Wilson [1.59%, 5.60%]) |
| Clark–West power, b = 0.4 | 100% |
| Clark–West power, b = 0.25 | 89.5% (179/200, [84.5%, 93.0%]) |
| Same-panel H1 | 87.5% two-sided, 93.5% one-sided |
| Clark–West among H1-significant runs | rejects in 175 of 175 |
| Pesaran–Timmermann size | 4.3% one-sided, 4.5% two-sided |
| M7 mean OOS R² on pure noise | −0.0064 |

- The adopted text of P28, P30 and P31 is not edited. It reports the lost original runs, whose data-generating process is not recorded.
- Flag 12's reading (Clark–West is conservative) holds.
- PLAN v2.3 §4.4 shows the rebuilt numbers, with the original ones in brackets.

---

**P55: Reading rule for the index-staleness test (ADOPTED (Isaiah, 2026-10-05); fixed before the test is run; the method for D10).**

- **Model.**
  - The 1306 gap is g_E = g + v, and the TOPIX index gap is g_I = λg + u.
  - g is the fresh market gap. The noises v (from the 1306 auction and its premium) and u are uncorrelated with g and with each other.
  - λ is the variance-weighted average pass-through of the index open; λ < 1 means a stale index.
- **Identification.**
  - Noise in the 1306 gap attenuates the forward slope, so b_IE ≤ λ ≤ 1/b_EI, where b_IE is the slope of g_I on g_E and b_EI is the reverse slope.
  - Since b_IE · b_EI = R², the upper end of the bracket is b_IE / R².
  - A fresh index (λ = 1) implies b_EI ≤ 1.
- **Rule.** Staleness is **established** if the reverse slope's 95% confidence interval lies entirely above 1, which is the same as the upper end of the bracket being significantly below 1. Otherwise it is "not established", which is not a finding of freshness.
- **Report:** b_IE, b_EI, R², N, the bracket [b_IE, b_IE / R²], and the reverse slope's CI with Newey–West SEs at the spec's lag rule (T = number of dates).
- **Samples** (one row per date):
  - (i) dev dates with no miner ex-day and no 1306 ex-date, using `ao_topix_gap`;
  - (ii) all dev dates, using `ao_topix_gap_tradj`.
  - 1306 ex-dates are the dates where `ao_1306_gap_adj` ≠ `ao_1306_gap_raw`.

*Effect:* documentation only. It qualifies the staleness caveat of the fallback secondary (P18) and changes nothing in the primary analysis.

---

**P56: Standards for the robustness-design amendments (ADOPTED (Isaiah, 2026-10-05); their content is decided at the Pass 2 decision checkpoint).**

- Every robustness amendment (AM-05, AM-06) states, before `spec-dev-v1`:
  - the exact design: which terms are added, and whether their slopes are common or ticker-specific (the default for market controls is ticker-specific, as in P19);
  - the estimation-sample rule;
  - what is reported.
- A row that restricts the sample, such as the Japan 225 row under P42, reports b with and without the added control **on the same restricted rows**, next to the full-sample primary.
- The operational criterion for claim tier (ii) is written into AM-05 before `spec-dev-v1`.
- Whether yen-denominated EWJ, which covers every night, also serves as a tier-(ii) check is decided together with D7.

*Reason:* the robustness designs are implemented after the dev first look (PLAN §8, Pass 4), so any unstated detail would become a forking path. The Nikkei-proxy row underwrites claim tier (ii).

---

**P57: Documentation refresh of 2026-10-05 (EDITORIAL).**

- **Updated:**
  - PLAN v2.3;
  - README;
  - PROJECT_SETUP;
  - DATA_PROVENANCE (§4.4, §4.5 and a new §4.6);
  - PASS2_INPUTS.json (event files, original build code, statuses);
  - this file (P45–P57);
  - a pointer banner at the top of PASS2_HANDOFF.md.
- **New:** PASS2_ADDENDUM.md, which includes builder prompt A′ and reference numbers B′.
- The Ito & Yamada reference is completed in PLAN §12.
- The resulting changes to the doc pins in `test_docs_d4` and `test_docs_d6` are pre-approved (PASS2_ADDENDUM §5, phase P2-0).
