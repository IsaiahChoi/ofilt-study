# Pre-registration v1: is overnight USD/JPY fully priced at the Tokyo open?

**Study:** ofilt/drift. **Author:** Isaiah Choi (Dartmouth College). **Document:** `docs/PREREG_v1.md`, fixed by the annotated git tag `prereg-v1` on the commit that holds it (P5Q6). Written 2026-10-12 by the supervisor chat of Pass 5 from Isaiah's decisions P5Q11 to P5Q17. It cites, by SHA-256 (Appendix A), every file that fixes a computation.

## 0. What this document does, and what governs

- **It fixes the confirmation run before the confirmation panel is opened:**
  - the one hypothesis test and its reading;
  - the secondary and robustness outputs and how each is read;
  - the claims each result licenses, and their exact wording;
  - the run procedure (§7);
  - the forward holdout (§8);
  - everything that was seen before this document (§9).
- **Computations are fixed by code, not by this text.**
  - Every number of the confirmation document is computed by the script and modules at the tag: `tools/p6_confirm_run.py`, `ofilt/drift/confirm_run.py` and the four confirmation modules.
  - They are read with the frozen spec, its amendments, the confirmation configuration `docs/P4_CONFIRM_CONFIG.json` (version 1) and the cost inputs (Appendix A).
  - If this text and the code at the tag disagree about a computation, the code governs, and the difference is reported as a dated note beside the result.
  - **Readings, claims and their wording are this document's.** The claim rows of the confirmation document (R10, R11, R12, R14, R21) apply the rules in code; this document gives their sentences.
- **The one-shot rule (P13(c)).** The confirmation panel is opened once, by the pre-registered script. Any later change to code or specification is reported as a dated, labelled deviation beside the original result. Every pre-registered result is reported whatever its sign or significance (R26).
- **Scope.** Three Tokyo-listed non-ferrous miners (5713 Sumitomo Metal Mining, 5711 Mitsubishi Materials, 5706 Mitsui Kinzoku), on the confirmation dates 2022-01-04 to 2026-03-05. A result is a statement about these three stocks in this period.

## 1. The question and the estimand

USD/JPY trades through the night while the Tokyo Stock Exchange is closed, and the 09:00 opening auction should price the overnight information. The question is whether the auction prices overnight USD/JPY **fully** for these miners, or whether the stock keeps absorbing it during the session (open → close). The daily panel sees only the open and the close, so speed is out of scope (PLAN §9).

**The design (P14; PLAN §1.2; spec as frozen at `spec-dev-v1`).** For stock i on Tokyo day t:

r^abn_{i,t} = α_i + b·e_t + a₂·eur_t + θ_iᵀ x_{i,t} + ε_{i,t}, where r^abn_{i,t} = y^oc_{i,t} − β̂_{i,t−1}·h^oc_t.

- **The target:**
  - y^oc is the open→close log return;
  - h^oc is the 1306 ETF's open→close return (AM-03);
  - β̂ is the past-only expanding OLS slope of y^oc on h^oc. It is estimated on non-excluded rows, lagged one day, needs at least 250 rows, and continues across the dev/confirmation boundary (P17).
- **The regressors:**
  - e_t is the dark-window USD/JPY log return (`usdjpy_ret`; positive means the yen weakened);
  - eur_t is `eurusd_ret`;
  - x is `spy_oc` and `copx_oc`, with ticker-specific slopes;
  - α_i is a ticker fixed effect, with no global intercept.
- **The estimation sample:**
  - earnings (決算短信) and standalone news days D and D+1 are excluded (P07);
  - the confirmation estimation dates number T_conf = 1,013, out of 1,019 confirmation days and 3,057 rows; six dates have every ticker excluded.
- **The estimator:**
  - pooled OLS;
  - Driscoll–Kraay standard errors, Bartlett kernel, lag ⌊4(T/100)^{2/9}⌋ (6 at T_conf);
  - normal reference, with no small-sample correction (P21).
  - DK-normal was kept because its binding size at b = 0 was 5.82%, inside AM-02's band [3.5%, 6.5%] (P79). It applies to every pre-registered DK test (D3.5).

## 2. The hypotheses and the outputs

**H1 (primary; O1, R1 to R5).** b ≠ 0, two-sided at α = 0.05, by DK-normal, in the design above, pooled across the three miners. H1 is tested once.

**H3 (secondary; O2).** a₂ = 0, two-sided at 5% in the same fit. Its reading is in §4.5.

**H4 (descriptive; O28, R7).** The per-ticker slopes on `usdjpy_ret`, each with its two-sided p-value, Holm-adjusted across the three. They come from one pooled DK fit with `usdjpy_ret` and `eurusd_ret` both ticker-specific (P4Q15).

**The secondary family (O3 to O6, R6; P25, AM-01).** Each member is the primary design plus a moderator's main effect and its interaction with e_t. The four two-sided p-values are Holm-adjusted together. The members:
- the long window, 1[window_hours > 18];
- the jump share, clip((rv − bv)/rv, 0, 1);
- high RV, 1[rv per bar > the dev median 1.2950114214e-08];
- asymmetry: e⁺ and e⁻ in place of e, with the equal-slopes contrast.

**The fraction unpriced (O7, O8; P24, P4Q9).** f = b/δ_cc, with δ_cc the close-to-close loading. It comes from one stacked fit with a joint DK covariance, with delta-method and Fieller intervals.
- f's estimate for 2022 (one fit on the rows dated 2022-01-01 to 2022-12-31) is the pre-registered f.
- The fit on 2023-01-01 to 2026-03-05 is descriptive.
- The 2022 fit has about a quarter of T_conf, so its DK-normal intervals are not calibrated at its length. f is reported as an estimate with its intervals, not as a test.

**Equivalence (O10, O11, R13, R14; P23, AM-07).** TOST against the smallest effect size of interest (SESOI) derived from trading costs, at α = 0.05.
- The primary SESOI is 0.8652: the mean round trip of 24.5961 bp per name-day over the mean |partialled overnight FX| of 28.4288 bp (P72).
- The results at the low (0.07152) and high (2.719) SESOI are reported beside it.
- TOST is viable at the primary SESOI (D2.6). It declared equivalence in 5,000 of 5,000 simulated draws at b = 0, and in 5.92% at b = +SESOI.

**The decomposition (O9).** b_raw ≈ mean(β)·b_mkt + b_abn, with its approximation gap.

**The robustness rows (O12 to O27; P22, P33, AM-05; the configuration's reporting form, P4Q12).** Each is reported next to the full-sample primary b. The rows that change a regressor, the β or the target report b with and without the change on the same rows. The rows:
- Huber (c = 1.345, MAD scale);
- FX winsorised at the dev 0.5%/99.5% quantiles;
- the influence curve (the k = 1 to 20 most influential dates removed, in one fixed full-sample ranking);
- β by rolling-250 and by rolling-500;
- the raw target;
- FCX in place of COPX;
- yen-denominated EWJ added;
- XAU added;
- the Japan 225 proxy added, on the nights whose endpoints are at most 5 minutes stale (999 of the 1,019 confirmation nights);
- the mechanism specification (session USD/JPY and EUR/USD, and the gotobi flag and its interaction, common slopes; not tradable);
- exclusion windows D to D+2;
- audit candidates, BoJ days and major SQ days, each excluded;
- the 2024-11-05 session change: post and e × post, reporting b_pre and b_post (confirmation only; outside every Holm family).

Anything not listed here or in the configuration is exploratory.

**The forecasting layer (secondary; O29 to O44, R9, R20; P26 to P28).**
- The ladder M0 to M5, plus M7 (gradient boosting; exploratory) in its own call.
- An expanding walk-forward: the first forecast after 500 eligible training dates, refits every 21 dates, in-fold scaling, one sample per call.
- Each call runs on the joined dev and confirmation rows. Its comparisons use only the evaluation rows on confirmation dates (P4Q20).
- **The primary forecast comparison** is Clark–West, M3 against M2, one-sided. It rejects if and only if its statistic exceeds c_CW,cal = 1.411608406163672 (AM-09).
- The other comparisons: Clark–West M4 against M3, M5 against M3 and M7 against M1 (normal reference); Diebold–Mariano M7 against M1.
- Also reported:
  - OOS R² against M0 and against M1;
  - Pesaran–Timmermann, beside the training-window base rate;
  - permutation importance for M7, by whole dates against its noise column.

**The economic evaluation (O45; P4Q24, P4Q25).** The every-day, β-hedged, market-on-open to market-on-close strategy that trades the sign of the forecast, for M3 and for M2.
- It reports the pooled break-even (mean gross P&L per name-day), the primary, low and high mean round trips, and the mean net P&L under each cost case.
- The tick terms are recomputed on the confirmation rows' own prices; the locked SESOI is unchanged.

**Contingencies (P4Q31).** The run never stops to ask.
- A row with no rows, a rank-deficient design, or a non-finite estimate or SE is reported as not estimable, with its reason and counts.
- A ratio with a zero or non-finite denominator is undefined, and a criterion that needs it fails.
- A not-estimable Holm member enters with p = 1.
- A claim whose inputs include a not-estimable result is not made.

## 3. Power (from the design; P79)

These are the binding numbers, from dev-calibrated simulations at T_conf = 1,013 on the 1306 hedge with DK-normal, made before any dev result was seen:

| b | 0 (size) | 0.10 | 0.25 | 0.40 |
|---|---|---|---|---|
| H1 rejection rate | 5.82% [5.20%, 6.50%] | 21.2% | 80.9% | 99.5% |
| Clark–West M3 v M2, at c_CW,cal | 5.0% | 31.0% | 90.4% | — |

- The minimum detectable effect at 80% power is **MDE80 = 0.2471** (probit-interpolated); size-adjusted, it is 0.2521. DK-normal is slightly liberal: c_cal(0.95) = 2.0041 against 1.96.
- A null H1 is read against this curve (§4.3).
- **Labelled remark, using a dev number (§9.6).** If the true b were the dev estimate, 0.245, the curve above would give power near 80%. That estimate is a single pre-specified number, not a selected maximum, but it is one noisy draw: its dev 95% interval [0.10, 0.39] spans power from about 20% to above 99%.
- The confirmation's standard error is expected to be larger than dev's 0.073, because dev had 1,439 estimation dates. The calibration's sd(b̂) at T_conf is about 0.087.

## 4. Claims and readings

The claim rows of the confirmation document compute each claim's arithmetic and set `licensed` only on the confirmation panel (provenance `confirm_real`). A claim is made only when its row is licensed and its inputs are all estimable. The sentences below are the only wordings used for those claims.

### 4.1 Tier (i): H1 rejected (R10; P4Q18)

The claim is **"overnight USD/JPY predicts session drift"**: in these three miners, information correlated with the overnight USD/JPY move is not fully priced at the 09:00 auction. This tier is sign-free. Without tier (ii) the wording stays here.

**Borderline results (a reading; H1's decision is unchanged).** DK-normal's calibrated 95% critical value at T_conf is 2.0041, not 1.96 (P79). If 1.96 < |z| ≤ 2.0041, H1 is rejected and tier (i) is claimed, but the result is reported as "significant at the nominal 5% level, not at the size-adjusted critical value".

### 4.2 Tier (ii): the exposure channel (R11; P32, AM-05, P4Q16)

This tier requires H1 rejected and, on the eligible confirmation nights (those whose Japan 225 endpoints are both at most 5 minutes stale), b with `n225_ret` added:
1. has the sign of the primary b̂;
2. rejects b = 0 at 5% two-sided by DK-normal;
3. satisfies b_with / b_without ≥ 0.5 on point estimates. This fails if the two differ in sign, or if b_without is zero or not finite.

The claim is then **"the exposure channel"**, in P32's sense: the part of the drift that survives a control for overnight Japan-equity news. It is read as the miners' FX exposure being incompletely priced at the open, beyond what overnight Japan-equity news carries. The proxy covers only eligible nights and only the news Japan 225 spans.

**If tier (ii) fails.** The wording stays at tier (i), and the result is reported as "the exposure channel is not established". If only condition 2 fails, with conditions 1 and 3 holding (the coefficient keeps its sign and at least half its size but loses significance), it is also reported as "power, not absorption". As on dev, this is not evidence against the exposure channel.

### 4.3 A null, and equivalence (R14, R21; P4Q19, D2.7)

- **A null H1** (p ≥ 0.05) is read against MDE80 = 0.2471: the design had about 80% power against b = 0.2471, so effects at or above that size are unlikely. It is never read as "no effect" or as full pricing.
- **Equivalence at the primary SESOI** licenses only **"no drift exploitable net of costs"**. It is reported beside whether TOST also declares equivalence at the low SESOI and at the high SESOI.
  - At the low SESOI, equivalence is practically impossible (0 of 5,000 draws at b = 0).
  - At the high SESOI, it is uninformative (5,000 of 5,000 even at b = +0.8652).
- **Both at once** (pre-stated, P5Q13): H1 may be rejected while TOST declares equivalence at the primary SESOI. The two claims are then compatible, and the joint reading is **"a detectable drift too small to exploit net of costs"**. Neither claim is reported without the other.
- **Neither:** H1 not rejected and no equivalence at the primary SESOI. The reading is "inconclusive at this sample size", stated with MDE80 and the TOST interval.

### 4.4 The reading of b (P85; F4-3; P5Q12; `docs/P4_M2_note.md`, Proposition 4)

H1 is the two-sided test of b = 0 at 5% by DK-normal; the M2 derivation does not change the test.
- b is **approximately** the yen-specific pass-through of overnight USD/JPY into the session drift, holding EUR/USD, SPY and COPX fixed. Holding EUR/USD fixed does not hold the dollar fixed. So any underpriced dollar-wide channel that the controls do not span also loads on b.
- **A significant b̂ > 0** is read as underreaction relative to the market (the target is abnormal against 1306). It is conservative with respect to the metals cascade, which pushes b down. That conservatism rests on three sign assumptions that cannot be checked before the data are seen:
  - S1: metals' dollar prices fall when the dollar strengthens;
  - S2: the miners are net long metal prices;
  - S3: no SPY–COPX collider.

  It is not conservative with respect to yen-correlated overnight news, which is what tier (ii) partly controls.
- **A significant b̂ < 0** is reported as a negative drift loading, not as overreaction. Under S1 to S3 an underpriced metals channel can produce it with the translation channel fully priced.
- **A null** is not full pricing (§4.3). Under S1 to S3, b = 0 can also arise from offsetting channels.
- **f = b/δ_cc** inherits the same qualifier. Its 2022 estimate is reported with its intervals and the calibration caveat of §2.

### 4.5 Tier (iii) and H3 (R12; P4Q17, P84)

- **No tier-(iii) claim is made.**
- H3 is reported without a tier-(iii) reading: â₂, its DK SE and its two-sided p.
- The metals rows are also reported without it:
  - `copx_to_fcx`, with and without the swap on the same rows;
  - `xau_control`, with and without XAU;
  - `raw_target`, with the gap â₂(raw) − â₂(abn).
- The pre-stated reading: a₂ is the session drift on EUR/USD conditional on `usdjpy_ret`, SPY and COPX, and its sign is not attributed to the metals channel. a₂ = 0 holds exactly as "dollar-wide and yen-specific moves carry equal drift" only when the euro-specific drift loading is zero (P84). Any underpriced channel whose fair value falls when the dollar strengthens gives the same sign and the same metals-row patterns.

### 4.6 Everything else

- **The secondary family:** a member with Holm-adjusted p < 0.05 is reported as heterogeneity of b along that moderator. It adds no claim tier.
- **H4:** descriptive, Holm-adjusted.
- **The robustness rows** are reported beside the primary. Apart from tier (ii)'s Japan 225 row, none creates, removes or rewords a claim.
- **The post-2024-11-05 row** is descriptive.
- **The forecasting layer is secondary.**
  - The primary comparison's rejection reads as "USD/JPY improves out-of-sample forecasts of session drift over the nested null M2".
  - The wording of R20 holds: "H1 and the CW forecast test may disagree; disagreement is not by itself evidence against H1". The T3 cross-tab (P79) is the binding description of their joint behaviour.
  - M7 is exploratory, and accuracy is always shown next to its base rate.
- **The economic evaluation** is the economic context of §4.3. It is not a claim of tradability.

## 5. What the confirmation document must contain

All 71 rows of `reports/P4_reports/p4_1_audit.md` (SHA-256 in Appendix A): O1 to O45 and R1 to R26, in the schema of `docs/P4_CONFIRM_INF_SPEC.md` §4.1.
- On the confirmation panel, O8 (f's two periods) and O27 (the post-2024 row) are computed. They are not applicable only on dev; a row may still be reported not estimable under §2's contingencies.
- R23 (the one-shot rule) and R25 (the forward holdout) are recorded as the code reports them. The forward holdout is evaluated separately (§8).
- The dry run (P4-5) showed the script produces every row, recovers a known b and b_post within 4 SE, and is byte-identical on rerun (`docs/P4_DRYRUN_CRITERIA.md`).
- The confirmation script `tools/p6_confirm_run.py` produces the same document as the dry-run script from the same frames (its test 6).

## 6. Inference rules fixed before Pass 4 (recorded in R13 to R19, R22)

- D2.6, TOST's viability.
- D3.2 to D3.5: the calibrated critical values, pooled over cells 0 to 4. DK-normal for every DK test.
- D4.3, the T6 robustness calibration, and D4.3b, its flag rule. No row is flagged.
- The seeds: the spec seed 20261001; walk-forward fold seeds seed + 1000·fold.

None of these is recomputed at the confirmation.

## 7. The run (Pass 6 run note; P5Q14)

1. **Preconditions.**
   - `prereg-v1` is an annotated tag on the commit holding this document, and HEAD descends from it.
   - The working tree is clean.
   - Every file of Appendix A has its SHA-256. Records, reports and documents added after the tag are allowed; any change to code or tests after the tag is a deviation.
   - Isaiah has filed the external registration (§10) and recorded its identifier.
2. **The sanction.** A separate message from Isaiah, dated, naming HEAD and the SHA-256 of `tools/p6_confirm_run.py`, `ofilt/drift/confirm_run.py` and the configuration, sanctions one run.
3. **The gate**, scripted in the Pass 6 item's message, with its criteria stated there before the run:
   - a full-suite checkpoint passes immediately before the run (P5Q2, rule 2);
   - the preconditions are rechecked by script;
   - `ACCESS_LOG` does not exist in REPO.

   If any check fails, the item stops before the panel is requested.
4. **The command.** The builder runs it, with the command tool's background option:

   `env -u OFILT_RUN_SEALED bash -c 'source "$HOME/venvs/ofilt_p2/bin/activate" && cd "$HOME/Desktop/FX_Project/ofilt_pass1" && export OFILT_DATA_DIR="$HOME/Desktop/FX_Project/data" && OFILT_P6_CONFIRM_RUN=P6-1 caffeinate -dimsu python -B tools/p6_confirm_run.py --out reports/P6_runs/confirm'`

   The script loads the dev panel and the events (each verified by its SHA-256), then requests the confirmation panel. The guard checks the tag; `io.load_confirm` verifies the panel's SHA-256 against AM-04's (`b575272a…`). It assembles the document and writes `document.json`, `manifest.json` and `runtime.json`.
5. **The crash rule.** Once `io.load_confirm` has logged GRANTED, the opening counts, whatever follows. If the run then fails (a hash mismatch, an exception), no result exists. The failure is reported, and any further attempt is a dated, labelled deviation that Isaiah decides, reported beside whatever it produces. The script itself refuses to run while `ACCESS_LOG` exists.
6. **After the run.**
   - The outputs are committed, with `ACCESS_LOG`, which records the opening (it is not ignored by git: flag F5-1).
   - Also committed: `RUN_REGISTRY.jsonl` (its two new `confirm_real` lines).
   - The tests that assert the absence of `ACCESS_LOG` or the registry's former content are changed by decision under the test-change protocol, and the full suite runs (P5Q2, rule 2).
   - A registry line's `git_dirty` is read with `RUN_REGISTRY.jsonl` itself excluded: the second call of a run records True because the first call appended to the tracked registry (P86).
7. **Reporting.** Every row is reported. The claims of §4 are made exactly when their rows are licensed, in this document's wording.

## 8. The forward holdout (P13(a); P4Q30; P5Q17)

- **When:** after the confirmation run. Its data are pulled only after `prereg-v1`, with the same Bloomberg settings and the same Dukascopy pull. The event calendars are extended (FY2025 FULL earnings onward; the 2026 BoJ meetings), and the 5706 10:1 split (ex-date 2026-09-29) is checked for a price discontinuity.
- **Window:** the trading days from 2026-03-06 to 2026-09-30.
- **What is evaluated:** H1's primary computation (O1's design, target and exclusions), with β continued across every earlier row, on the holdout dates alone, with DK-normal at the holdout's own T and lag. It reports b̂, its SE, its two-sided p, and whether its sign agrees with the confirmation's b̂. P64's intraday PX_OPEN check of the 1306 open is reported beside it where the data allow.
- **Reading:** a sanity check, not a second test.
  - Its power is low: roughly 19% at b = 0.25, by scaling sd(b̂) with 1/√T to about 140 dates. This is an approximation, not a calibrated run.
  - It licenses no claim, and it is never pooled with the confirmation for any claim.
  - Its code is written after the confirmation result is known, under its own short specification fixed before the holdout data are pulled. Its computation is the one fixed here.

## 9. Disclosure: everything seen before this document

1. **Prior exposure (P32; PLAN §2.3).** Isaiah's Math 86 project and the M1 rebuild examined overnight FX against the opening **gap** inside what is now the confirmation period (January 2023 to March 2026). The M1 gap beta was concentrated in the 2024–2025 crisis windows. The confirmation sample is therefore not fresh for gap-based quantities, which is why f is confirmatory for 2022 only. The **open→close** relationship (H1, H3) had never been examined on any data before the dev first look.
2. **The sealed blind fits (`BLIND_FIT_LOG`, 7 lines).**
   - Pass 1's six fits (on the original dev panel) and Pass 3's seventh (P78, on the rebuilt dev panel) ran on the dev panel through the sealed-fit exception (P29). None output an FX coefficient.
   - The seventh returned only aggregates over synthetic draws from the sealed calibrator, which calibrated the inference before any dev result was seen (P79).
   - The Pass 1 sealed-run reports hold per-cell aggregates only. Their per-cell means of simulated estimates are linear functionals of the residual vector, given the seeds (P71).
3. **The confirmation panel.**
   - It was built in Pass 2 and checked only through dates, counts, hashes and in-memory equality booleans; no value of it was printed or summarised. Its SHA-256 is `b575272aad752b3af84abe109fa66edde421f7c99184c9d1885bacdce64f06d1` (AM-04).
   - Its old columns come from the frozen build run on the Mac (`138e5e21…`). Their byte identity with the original sealed file (`9c18a6c1…`, P10) cannot be demonstrated; the dev comparison bounds the platform differences (P59; DATA_PROVENANCE §5.2).
   - Every panel was built on macOS arm64. Verification across platforms is by tolerance, not by hash (Flag 16; P58).
   - The 1306 settings check (P39(b)) was resolved by Isaiah's attestation (P60).
4. **Pass 3's carried items** (`docs/DECISIONS_P71_onward.md`, "Carried to the pre-registration", 13 items) stand in full, by reference. Among them:
   - Isaiah's cost note of 2026-10-06 held approximate 2026 price levels, share counts and trading values for the miners and 1306. That is confirmation-period information. It entered no computation and is kept outside the repository and the Project.
   - DK-normal is slightly liberal, and the real residuals are noisier than the rehearsal's stand-in.
   - Under the null, H1's and Clark–West's false positives overlap (62 of 2,000).
5. **Real-data contact by every session.** Every session's contact is recorded in DATA_PROVENANCE §4.5, `PASS2_STATUS.md` to `PASS5_STATUS.md` (Blinding attestation) and their Disclosure lists. Those lists stand in full.
6. **The dev first look** (Pass 4, P4-6, run once on 2026-10-12 under its sanction; exploratory; it licenses nothing). Source: `reports/P4_runs/dev/document.json` (Appendix A). It covers 2015-01-06 to 2021-12-30, with 4,192 estimation rows and 1,439 dates (DK lag 7).
   - **H1:** b̂ = 0.245, DK SE 0.073, p = 0.0008 (rejected at 5%); 95% interval [0.10, 0.39].
   - **Per ticker:** 5706 0.338 (p 0.0008), 5711 0.297 (p 0.001), 5713 0.104 (p 0.28; Holm 0.28).
   - **TOST:** equivalence declared at the primary SESOI (90% interval [0.125, 0.365]) and at the high SESOI; not at the low. Together with H1, dev would read "a detectable drift too small to exploit net of costs".
   - **H3:** â₂ = 0.141 (SE 0.089, p 0.11) on the abnormal target; 0.276 (p 0.017) on the raw target.
   - **The decomposition:** b_raw 0.216, b_mkt −0.039, mean β 1.03.
   - **f (the dev stand-in, one fit):** 0.446, with δ_cc 0.549 and Fieller [0.236, 0.620].
   - **The secondary family:** no member significant (smallest Holm p 0.73).
   - **The robustness rows:** b between 0.17 (the influence curve at k = 20) and 0.31 (EWJ added) throughout.
     - The session-FX mechanism row: b = 0.194, about a fifth absorbed.
     - The Japan 225 row: b_with 0.241 against b_without 0.244 (ratio 0.99), but p = 0.074. So tier (ii) would fail on dev even if it were licensed, through power, not absorption.
   - **Forecasting** (every dev forecast row, 2018-02-13 to 2021-12-30):
     - Clark–West M3 v M2: statistic 2.17, against c_CW,cal 1.41 (would reject).
     - Clark–West M7 v M1: 3.20. Diebold–Mariano M7 v M1: 1.23.
     - M7's permutation importance ranks `usdjpy_ret` 20th of 21, below its noise column.
   - **Economics:**
     - M3's break-even is 15.41 bp per name-day and M2's is 16.85 bp; adding USD/JPY lowered it by 1.44 bp.
     - The mean round trips are 24.70 bp (primary), 2.04 bp (low) and 73.20 bp (high).
     - M3's mean net P&L is −9.29 bp (primary), +13.37 bp (low) and −57.79 bp (high), each below M2's.
7. **The order of events.** The dev first look could not shape the analysis, because everything that fixes it came first:
   - The spec was frozen and tagged `spec-dev-v1` (annotated tag object `cee3b49e81d16f1f32e546cac9524b209ac1e493` on commit `f5271c03481b7514a1ec4b7e739fb85fbce8a774`).
   - Every open detail was then decided blind into the configuration, version 1 (committed at P4-2, `7828e79207acbaa9b8919077b50da1449d6783c9`).
   - The confirmation code was written and validated on synthetic data only. The dry run's criteria were committed before any run.
   - The dev run was made once, at `2971d8dbd75a92ffa97dcb4bfd6f24905f6af259`, after the dry run's gate.
   - Since then, no change has been made to the spec, the configuration, the confirmation modules or the dev run's script.
   - Written after the dev run: the decisions P82 to P87 (readings only: P84 and P85 qualify how a₂ and b are read, from a derivation written blind before the dev run, `docs/P4_M2_note.md`); this document's wording; and the confirmation script `tools/p6_confirm_run.py` (P5-1), which only loads the panels and calls the unchanged assembler.
8. **Who saw the dev results:** the Pass 4 builder session, the supervisor chats that began on 2026-10-11 (with handoff H9) and on 2026-10-12 (with H10), and Isaiah. Once the dev document was uploaded to the Project, every later session could see it.
9. **Review.** This document had **no independent advisor review**. Isaiah, the study's author, acts as its advisor and signs it off (P5Q11), on an advisor-style review written by the supervisor chat that drafted it (`docs/PREREG_v1_REVIEW.md`). His sign-off is recorded in `PASS5_STATUS.md`'s Decision log with this document's SHA-256. PLAN §8's and P36 step 6's "advisor sign-off" are met in that sense, and only that sense.
10. **Assistance.** The analysis code, the specifications, the simulations and this document were drafted by AI assistant sessions (Claude), directed and decided by Isaiah. Every decision is recorded with its reason in the decision files.

## 10. External registration (P5Q11)

After the tag, Isaiah files an embargoed registration on OSF. It holds this document, its SHA-256, the tag object and its commit, and the SHA-256 table of Appendix A. Its data-status answer says that the confirmation data exist, that their outcome relationship has not been examined, and that the contacts of §9 are disclosed. The registration's identifier is recorded in the repository before the confirmation run is sanctioned (§7.1).

## Appendix A: the files that fix the confirmation (SHA-256 at the tag)

| Path | SHA-256 | Role |
|---|---|---|
| `spec/analysis_spec_dev_v1.yaml` | `feb6005d62665f88fc8a6af883dab783c7f36f15e00df17f79f5b64627f29c26` | The frozen spec (AM-10) |
| `spec/SPEC_AMENDMENTS.md` | `c603206bd68ba225904fae8c30d25651c3c5c56afb8e8242f54cc52a85a52617` | AM-01 to AM-10 |
| `docs/P4_CONFIRM_CONFIG.json` | `5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd` | The confirmation configuration, version 1 (P4Q9 to P4Q31) |
| `docs/P3_COST_INPUTS.json` | `a2bbca432e5398a732c9c1bfb7a12106c5474a10b027d4aa1757f5a27c2f8dc6` | The cost inputs (P72) |
| `tools/p6_confirm_run.py` | `5b3922d79bb0a6d093dccf2aff5f1aaf3f869e8d93c900ac6fb3a6c74eaf5b7f` | The confirmation script (P5Q15) |
| `tests/test_p6_confirm_run.py` | `6c8d738e72dfcfe7b205b356e66fc3817ae2100d1f811df624d19839ad116f4f` | Its tests, including the equivalence check |
| `docs/P5_CONFIRM_SCRIPT_SPEC.md` | `7e817cd2ac27183dc6e07bd40bde128f289fc9aba47af254be977cbfe31397e8` | Its specification |
| `ofilt/drift/confirm_run.py` | `998912c5c9e89ca14fde5e1ca1811ff3f3e4ac65dd36b29b61debffab8e9eaf3` | The assembler |
| `ofilt/drift/confirm_inference.py` | `77e9233732448cd814cefe6ee408a2ab2b1edaf3a47d9118e0e2790dbc0f7de1` | The inference rows |
| `ofilt/drift/confirm_forecast.py` | `b0dbb0aa7147be06a10fa374c5d342c580597b50c8ef0ce5cecda452139a87ff` | The forecasting rows |
| `ofilt/drift/confirm_economic.py` | `caa065454cc229b6cf192a36795d6536557510e5a6a4a6112ccfa08ce4d01f73` | The economic evaluation |
| `ofilt/drift/confirm_claims.py` | `ac91c49f529d108f4ff62f40d8584cf329c10a0320862878b4bef66447d07ed8` | The claim and rule rows |
| `ofilt/drift/confirm_allowlist.py` | `2fd60f4e8f4e6bf9c21db3863854be89abf70f0d239abbd001f62a8468a154c1` | The inference-only allowlist |
| `ofilt/drift/inference.py` | `d040fc508d80fbd25619591de615137b9934a3089deeb5727a22fdae0801518b` | The estimator (C7-hashed) |
| `ofilt/drift/forecast.py` | `f816d277edec7e8d3fdbeffe03e3ac2461713ace4982b606163efec5a44b66e9` | The walk-forward engine (C7-hashed) |
| `ofilt/drift/fctests.py` | `b908b6dad0684a91b0fafea9a15ca13e538dc90bd0274579d26f7b1f61ed8066` | The forecast tests (C7-hashed) |
| `ofilt/drift/targets.py` | `85a12c252cd9c68a31bba5afb78d63db97f44fc7ed630959232e8c8cbed2beb1` | The targets and masks |
| `ofilt/drift/io.py` | `35946fbc15b8a6df05d1468d4dec91877a76568f7499271d393bc44827d0011a` | The loaders and the access guard |
| `ofilt/drift/blind.py` | `2d99f672673c8f1ba2157ab7629a45ced27a5018a197f8c907c6eef3c34d8d50` | The blinding guard |
| `tools/p4_confirm_run.py` | `d4cd6edd3c341cfed8ecfb608cd17062254512a436463b688a8913a6e0455a5d` | The dry-run and dev-run script |
| `docs/P4_CONFIRM_INF_SPEC.md` | `a7ebb94f003c3b893e96b222b796ea9fda09c849217c526bfdfc8d2b6be51f65` | Specification, version 2 |
| `docs/P4_CONFIRM_FC_SPEC.md` | `a8d3a9c91ca7a3d6bf551f95a56e3e4cf43ec14ed6b4f0d450c751589f795bd6` | Specification, version 1 |
| `docs/P4_CONFIRM_ECON_SPEC.md` | `42e1488330ae7bb3c947fb92a6958c851197aaad6d9e545a5e3ef81511432785` | Specification, version 1 |
| `docs/P4_CONFIRM_CLAIMS_SPEC.md` | `b499e820c62961b79bfc0ec839d6014e918657f79071182104fbdc1f4d4dbbf2` | Specification, version 1 |
| `docs/P4_CONFIRM_RUN_SPEC.md` | `4fe3712f0f3ffdcc6b87b6443e383c1d840c3d5d7fdcce210c5bf6322d916ab3` | Specification, version 1 |
| `docs/P4_DRYRUN_CRITERIA.md` | `3590035edb366eb46c1d076a3d7c4c2fdc60d9c43994b5a305181982ea071877` | The dry run's criteria |
| `reports/P4_reports/p4_1_audit.md` | `fb80a779f9e8c8926b6846c3fa77d44b8375619b0901799202ee451ff276a894` | The 71 outputs and rules |
| `docs/P4_M2_note.md` | `a4812e85b6feabc838473ce47a97ce6c4fe88eec7a91762f442cb978b933ec22` | The M2 derivation (P83) |
| `docs/replacements/PLAN.md` | `b1f34c1a60e2f2e0edf96fab7240fb777bf8e84c4eb9002b8820ad0fc8d097ca` | PLAN v2.6 |
| `docs/DECISIONS_ADDENDUM.md` | `09ad0d1114c46b2987eb981c47dd9967089e47f0965946d318b1b3124a9bec22` | P01 to P13 (added to the repository at P5-2) |
| `docs/DECISIONS_P14_onward.md` | `3d13201636ad459ce0bb61fb5e29385c2a7531cf7daad848d1a970706ca02dd0` | P14 to P36 |
| `docs/DECISIONS_P37_onward.md` | `b22bdc15ba5cae086738d7639ca8b95069bbb668b8d386de1a5c3a9a7e0175f1` | P37 to P57 |
| `docs/DECISIONS_P58_onward.md` | `e7874506706198850c9c680bf052859d6fcf453f511f6bc3ba5403dbef119131` | P58 to P70 |
| `docs/DECISIONS_P71_onward.md` | `c3eadc756e8d9754bb6ef289e7b7ba5d30a53ecec9182d53bd69fc5eb9fa1b83` | P71 to P81 |
| `docs/DECISIONS_P82_onward.md` | `0b31d97349f8e0fc1d48882923ed042e1268b59fa6cf68d7e87e383fbb696890` | P82 to P87 |
| `PASS4_STATUS.md` | `c33817f85575701440a838afdb9730e3833c292149672a85147ed51eacc4955f` | Pass 4's decision log and disclosure list (closed) |
| `docs/DATA_PROVENANCE.md` | `6af072591e2eff9cf83de9e78286b6545b3063c42d7a555073b45b3f26c561c6` | Real-data contact, to Pass 4 |
| `reports/P4_runs/dev/document.json` | `9a51863e6adda733397736724013e3cd71101328289629c9f29a40459dd64c92` | The dev first look (§9.6) |
| `BLIND_FIT_LOG` | `0cdedae9662221145dd3b9f4baecacc7431d17706d01f6cef19cce10c0f83383` | The seven sealed blind fits |
| `RUN_REGISTRY.jsonl` | `9c6cb9c68538215cab8ae5c91f582e695757165bc4de5e033c8c61d49a9f542c` | The dev run's two forecasting calls |

The panels:
- dev `panel_dev.csv`: `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68`;
- confirmation `panel_confirm_SEALED.csv`: `b575272aad752b3af84abe109fa66edde421f7c99184c9d1885bacdce64f06d1`.

Both are pinned in the spec (AM-04) and verified by `io` on every load. `PASS5_STATUS.md` is cited by path; its content at the tag records this document's adoption.
