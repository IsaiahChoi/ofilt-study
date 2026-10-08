# Research Plan v2.5: Is overnight FX fully priced at the Tokyo open?

**Owner:** Isaiah Choi. **Executor:** Claude, with Isaiah as decision-maker.

**Status:** 2026-10-07.
- Pass 1 (the analysis machine) is complete. Its final repository was lost, and Stage C4–D was rebuilt from the C3 checkpoint (2026-10-04/05). The rebuilt repository is the canonical study repository (P45).
- Pass 2 inputs are pulled and verified. The pre-flight decisions of 2026-10-05 are recorded as P45–P57.
- Pass 2 (data and rebuild) is complete: the 60-column panels were built on macOS arm64, the hedge is 1306 (AM-03), the switch commit applied AM-03 to AM-05, and the C7 rerun on the Mac reproduced every rejection decision (D16). Its decisions are P58–P70.
- Pass 3 (calibration, dev still blinded) is complete. One sanctioned sealed fit (`BLIND_FIT_LOG` line 7) calibrated the inference on dev-calibrated simulations. DK with the normal reference is kept for H1 (5.82% at b = 0, inside AM-02's band); the primary Clark–West comparison uses its calibrated critical value (AM-09); TOST is viable at the primary SESOI (AM-07); and the switch froze the spec (AM-10). Its decisions are P71–P81.
- Next: the `spec-dev-v1` tag.

**Supersedes:** v2.4 (2026-10-06), which superseded v2.3 (2026-10-05), v2.2 (2026-10-04), v2.1 (Pass 1, item D4b, `docs/replacements/PLAN.md`) and v2.0. Archive all five. If any wording differs, the decision log (P01–P81) and `spec/SPEC_AMENDMENTS.md` govern.

**Companion files:**

| File | Contents |
|---|---|
| `README.md` | Pipeline and session rules |
| `DATA_DICTIONARY.md` | Schema groups |
| `DATA_PROVENANCE.md` | What was verified, including §4 on Pass 2 inputs |
| `PASS2_INPUTS.json` | Hashes |
| `DECISIONS_ADDENDUM.md` | P01–P13 |
| `DECISIONS_P14_onward.md` | P14–P36 |
| `DECISIONS_P37_onward.md` | P37–P57 |
| `DECISIONS_P58_onward.md` | P58–P70 |
| `DECISIONS_P71_onward.md` | P71–P81 |
| `PASS2_HANDOFF.md` | How to run Pass 2 |
| `PASS2_ADDENDUM.md` | Corrections to the handoff for the rebuilt repo; builder prompt A′; reference numbers B′ |
| `PASS1_STATUS.md`, `REBUILD_VERIFICATION.md` | The Pass 1 build record, and the rebuilt repo checked against the adopted text |

Marks used below:
- **[PREREG]**: fixed in the pre-registration.
- **[ADVISOR]**: needs the advisor.
- **[CAL]**: decided in Pass 3 (calibration), before `spec-dev-v1`.
- **[P2]**: decided in Pass 2.

---

## 0. How to use this document

| § | Contents |
|---|---|
| 1 | Question, estimand, hypotheses |
| 2 | Data, samples, holdout structure, Pass 2 inputs |
| 3 | The exact model (primary, secondary, mechanism) |
| 4 | Forecasting layer and economic evaluation |
| 5 | Power (preview numbers; binding run in Pass 3) |
| 6 | Robustness list (pre-listed; anything else is exploratory) |
| 7 | Mathematical component [ADVISOR] |
| 8 | Passes and milestones (P36 order, P44 naming) |
| 9 | Out of scope |
| 10 | Operating rules for Claude |
| 11 | Risks and open flags |
| 12 | References (all [UNVERIFIED]) |
| 13 | Change log |

---

## 1. Question, estimand, hypotheses

### 1.1 The question

USD/JPY trades through the night while the Tokyo Stock Exchange is closed, and the 09:00 opening auction (itayose) should price the overnight information. For three FX-exposed non-ferrous miners, does the auction price overnight FX **fully**, or does the stock keep absorbing it during the session?

The miners are **5713** Sumitomo Metal Mining, **5711** Mitsubishi Materials and **5706** Mitsui Kinzoku.

The study tests *whether* FX is fully priced by the open, not *how fast*. The daily panel sees only the open and the close; speed is out of scope (§9).

### 1.2 The estimand (P14)

For stock i on Tokyo day t:

$$r^{abn}_{i,t} = \alpha_i + b\,e_t + a_2\,\text{eur}_t + \theta_i^\top x_{i,t} + \varepsilon_{i,t}, \qquad r^{abn}_{i,t} = y^{oc}_{i,t} - \hat\beta_{i,t-1}\, h^{oc}_t$$

**Outcome:**
- $y^{oc}$ is the open→close log return.
- $h^{oc}$ is the **hedge** open→close return: the 1306 ETF (P18; AM-03). The P18 fallback did not fire.
- $\hat\beta_{i,t-1}$ is a past-only **expanding** β, estimated on non-excluded rows, lagged one day, and never restarted at the confirmation boundary (P17).

**Regressors:**
- $e_t$ is the dark-window USD/JPY log return (`usdjpy_ret`; positive means the yen weakened).
- $\text{eur}_t$ is `eurusd_ret`.
- $x_{i,t}$ is `spy_oc` and `copx_oc`, with **ticker-specific** slopes (P19).
- $\alpha_i$ is a ticker fixed effect; there is no global intercept.

**Reading b.** With EUR/USD in the design, Frisch–Waugh–Lovell makes **b the yen-specific pass-through**, with no generated regressor:

| Value | Meaning |
|---|---|
| b = 0 | The auction fully priced FX |
| b > 0 | Underreaction, the cascade prediction |
| b < 0 | Overreaction |

**Relative to the market.** Because the target is abnormal, b measures underreaction *relative to the market*. The decomposition b_raw ≈ mean(β) · b_mkt + b_abn is reported, with its approximation gap (P18, B3).

### 1.3 Hypotheses

**H1 (primary).** b ≠ 0 in the design above, pooled across the three miners. Two-sided test at α = 0.05 [PREREG]. The inference method is decided in Pass 3 [CAL] (§3.4): DK with the normal reference (P79).

**H2: RETIRED (P16).** The auction-conditional specification, which adds the realized gap, is not a mispricing test. Under an efficient but noisy auction, its FX coefficient equals kδ > 0, with k = V_η/(V_f + V_η). Conditioning on the gap *surprise* instead reproduces the pre-open b exactly.
- Numerical check (B6), at ρ = 1: auction-conditional coefficient 0.162, against kδ = 0.167.
- The surprise version equals the pre-open b to 1e-16.

The `ao_` columns are used only in the decomposition and the hedge.

**H3 (secondary, restated, P15).** a₂ = 0: dollar-wide and yen-specific moves are priced alike. Here b^$ = b·γ + a₂. The test is conditional on EUR/USD being the dollar proxy, and on COPX absorbing the US-session commodity response.

**H4 (descriptive).** Per-ticker slopes, Holm-corrected across the three stocks.

**Secondary family (P25, AM-01).** Four tests, Holm-corrected across the family. Each one is the primary design plus a moderator main effect plus its interaction with $e_t$:

| Test | Interaction |
|---|---|
| Long window | e × 1[window_hours > 18] |
| Jump share | e × clip((rv − bv)/rv, 0, 1) |
| High RV | e × 1[rv_per_bar > dev median] |
| Asymmetry | e⁺ and e⁻ with equal-slopes contrast; no moderator main effect needed |

**Fraction unpriced (P24).** f = b / δ_cc, where δ_cc = δ_gap + b is the close-to-close loading. Joint Driscoll–Kraay covariance, with delta-method and Fieller intervals. **Confirmatory for 2022 only**, descriptive for 2023–2026, because of prior exposure (§2.3).

**Equivalence (P23).** A TOST test against a smallest effect of interest (SESOI) derived from trading costs. The primary SESOI is 0.8652 (low 0.07152, high 2.719), from the cost model (P72; AM-07). TOST is viable at T_conf under DK-normal (D2.6; P79) [CAL].

### 1.4 What counts as success

H1 is tested once, under the frozen specification, with power reported, and the result is reported whatever its sign.

A well-powered null is a finding: "the auction prices overnight FX for FX-exposed miners". It is made sharper by the equivalence test when that test is viable. A significant b that survives the controls motivates the intraday extension.

**Claim tiers (P32):**

| Tier | Claim | What it needs |
|---|---|---|
| (i) | "overnight USD/JPY predicts the drift" | H1 alone |
| (ii) | "the exposure channel" | H1 plus the Nikkei-proxy robustness check (§6), because USD/JPY partly carries overnight Japan-equity news. The pass criterion is fixed with D7, before `spec-dev-v1` (P56) |
| (iii) | "the cascade" | (ii) plus H3 plus the metals controls |

---

## 2. Data, samples, holdout

### 2.1 Panels

`panel_dev.csv` and `panel_confirm_SEALED.csv` are built by `build/pass2/build_panel_p2.py`, which runs the frozen `build/pass1/build_panel.py` and appends 19 columns (P51).
- One row per stock per TSE trading day.
- Every column belongs to exactly one schema group (`DATA_DICTIONARY.md`; `ofilt/drift/schema.py`).

| Sample | Span | Size | Use |
|---|---|---|---|
| Development | 2015-01-06 → 2021-12-30 | 1,708 days, 5,124 rows | Selection, calibration, power, dry run |
| Confirmation | 2022-01-04 → 2026-03-05 | 1,019 days, 3,057 rows | Run once after `prereg-v1`. Sealed. Estimation dates T_conf = **1,013** (6 dates have all three tickers excluded; `calendar.py`). |
| Forward holdout (P13a) | After 2026-03-05 | Grows | Pulled only after `prereg-v1`; evaluated once; a sanity check, not a second test |

The sealed panel's hash (P10: `9c18a6c1…`) is **superseded by the Pass 2 rebuild**; the new hashes are in AM-04 (P67). Old columns (the hybrid, P59): dev's 41 are the original `736636…` strings; sealed's come from the frozen build run on the Mac (`138e5e21…`), because the original sealed file is not available on the Mac and the Mac cannot reproduce its bytes (Flag 16). Byte identity of the sealed old columns with `9c18a6c1…` cannot be demonstrated, and the pre-registration discloses this (§8, Pass 5).

### 2.2 Pass 2 inputs (pulled and verified 2026-10-04; DATA_PROVENANCE §4)

| Input | Status | Role |
|---|---|---|
| 1306 ETF daily OHLC (Bloomberg) | Verified; calendar identical to the miners. Settings check resolved by attestation (D2; P60) | **Primary hedge** (P18; AM-03) |
| 1306 dividends | Corrected copy (÷10, relabelled). The ÷10 factor is **confirmed** (P47): the issuer's 1:10 split took effect 2026-04-01, after the panel ends, and the ÷10 amounts equal Nomura's published distributions | Flag 6 fix on the hedge gap |
| TOPIX total-return close | Verified; TPXDDVD Index (D3; P60) | Fallback-path Flag 6 fix only (P40) |
| XAU/USD 1-minute (Dukascopy, bid) | Verified | Robustness control (P41) |
| Japan 225 CFD 1-minute (Dukascopy, bid) | Verified; **08:59 JST price fresh from 2018-04-13** (DATA_PROVENANCE §4.3) | Nikkei proxy for the exposure claim (P42) |
| USD/JPY and EUR/USD masters | Unchanged; offer side confirmed **bid** (P37) | Dark-window FX, plus the new session FX and US-session FX |

Computed in Pass 2, with no new pulls:
- **Session FX**, 09:00 → close JST (`CONTEMPORANEOUS`; never a feature). The close is 15:00 JST through 2024-11-04 and 15:30 from 2024-11-05; the sample has no half-day sessions;
- **US-session USD/JPY**, and from it a yen-denominated EWJ. The window is NY 09:30–16:00 ET, or 13:00 ET on the 23 NYSE early-close days (P49);
- **XAU and Japan 225 dark-window returns**, with endpoint staleness;
- **the gotobi flag** (definition P48);
- **1306 columns**, including its dividend-adjusted gap.

### 2.3 Prior exposure (disclose in the pre-registration; P32)

Math 86 (January 2023 – March 2026) and the M1 rebuild examined **gap**-on-FX relationships inside the confirmation period. In particular, the M1 gap beta was concentrated in 2024–2025 crisis windows.

The **open→close** relationship has never been examined on any data. The confirmation sample is therefore fresh for H1 and H3, but not for gap-based quantities, which is why f is confirmatory for 2022 only.

---

## 3. Model specification

### 3.1 Target

The primary target is abnormal open→close with the 1306 hedge and an expanding past-only β (P17, P18). The β window was chosen on hedge efficiency alone, using no FX data and comparing all windows on common rows. Expanding won for all three tickers on the TOPIX hedge. **Rerun on 1306 in Pass 2 (D9; P65):** on common rows, rolling-500 was marginally lower for 5706 and 5711; expanding was kept, and rolling-500 was added as a robustness row (`beta_rolling_500`, AM-05).

**Fallback rule (P18, verbatim):** "If 1306 daily data cannot be obtained, or fails its Pass 2 checks (split/dividend adjustment, open-auction timing), the primary target switches to the raw open->close return before the spec-dev-v1 tag, never after. The abnormal target is then reported as secondary using the TOPIX index with the staleness caveat."

The fallback did not fire: 1306 passed its Pass 2 checks (P47; D8 (a), P64).

The raw target is a pre-registered secondary in every case.

### 3.2 Exclusions

| Sample | Rule |
|---|---|
| Inference | Exclude days D and D+1 of 決算短信 (earnings releases) and standalone news (P07) |
| Forecast evaluation | Excludes earnings D and D+1, and news D+1 only, because unscheduled news on day D isn't knowable before the open |
| Forecast training | Excludes the inference set (Flag 11) |

`boj_day` and `mech_flag` are kept. `audit_flag` is robustness only (P08).

### 3.3 Controls (P19)

SPY and COPX, with ticker-specific slopes.

**Reason (verbatim):** "A control belongs in the primary design only if it is correlated with overnight FX AND predicts the drift. Lagged returns fail the first condition in practice (dev abnormal-drift autocorrelation is at most |0.075| at lags 1-5, and overnight FX is close to unpredictable from yesterday's stock returns), so they cost degrees of freedom without removing bias. SQ/BoJ/ex-dividend dummies shift the intercept and are uncorrelated with FX, so they move to robustness."

**Left out of the primary design:**
- **EWJ:** it is USD-denominated, so its US-session return contains the US-session USD/JPY move. A yen-denominated EWJ goes into robustness after Pass 2.
- **FCX:** robustness only.

### 3.4 Estimator and inference (P21)

Pooled OLS, with Driscoll–Kraay standard errors:
- Bartlett kernel; lag ⌊4(T/100)^{2/9}⌋ with T = unique estimation dates (6 at T_conf);
- normal reference; no small-sample correction.

**Binding size rule (AM-02):** if the rejection rate at b = 0 over 5,000 dev-calibrated simulations at T_conf falls outside [3.5%, 6.5%], primary inference switches to a stationary block bootstrap. This is decided in Pass 3 [CAL].

The Pass 3 options (Flags 10 and 12, decided jointly) [CAL]:
1. Driscoll–Kraay with normal critical values;
2. the bootstrap;
3. a critical value taken from the b = 0 simulation itself.

**Outcome (Pass 3, P79).** DK-normal rejected 291 of 5,000 draws at b = 0 (5.82%), inside [3.5%, 6.5%], so option 1 is kept and AM-02's bootstrap branch is not taken (AM-08 unused). Clark–West's normal reference rejected 66 of 2,000 (3.30%), outside the band, so the primary forecast comparison uses its calibrated critical value, 1.411608406163672 (AM-09).

### 3.5 Tails and influence (P22)

OLS on unwinsorized data is primary. Pre-registered robustness:
- **Huber** M-estimator (c = 1.345, MAD scale);
- **FX winsorized** at the dev 0.5%/99.5% quantiles;
- an **influence curve**, removing the k = 1…20 most influential dates in a fixed full-sample ranking.

These replace v2.0's named crisis windows, which were chosen with knowledge of the outcomes.

---

## 4. Forecasting layer and economic evaluation (secondary; P26–P28)

### 4.1 Model ladder

| Model | Definition |
|---|---|
| M0 | Zero forecast |
| M1 | Prevailing mean per ticker |
| M2 | Controls + EUR/USD (the nested null for H1) |
| M3 | Primary design |
| M4 | M3 + the AM-01 terms |
| M5 | Ridge on M4 |
| M7 | Shallow gradient boosting on the 20 PRE_OPEN features + ticker one-hot + noise column (exploratory) |

M6 (a Kalman filter on time-varying β) is dropped.

### 4.2 Walk-forward protocol

- Expanding window. The first forecast comes after 500 **eligible** training dates (the C1 correction); refit every 21 dates.
- Pooled estimation; in-fold scaling only.
- Every model in one call shares the same rows. Comparisons are paired.
- Every run is logged in the run registry.

### 4.3 Tests

| Test | Use |
|---|---|
| Clark–West (one-sided) | Nested comparisons; M3 vs M2 is primary |
| Diebold–Mariano | Non-nested comparisons |
| Pesaran–Timmermann | Direction, always shown next to the training base rate |
| OOS R² | vs M0 and M1 |
| Permutation importance | Date-unit, calibrated against the noise column |

### 4.4 Validated behaviour (synthetic; C7)

These numbers come from the rebuilt repository (P54). The lost original run's figures are shown in brackets for the record.

- Clark–West size: **3.00%** (9/300, Wilson [1.59%, 5.60%]) at nominal 5% [original: 2.67%]. It is conservative (Flag 12).
- Power: **89.5%** at b = 0.25 and 100% at b = 0.4 (identical in both runs).
- On a common data-generating process, Clark–West rejects in 175 of 175 H1-significant runs [original: 170 of 175].
- The Pass 2 rerun on the Mac (D16; P68) reproduced every rejection count and every per-replication rejection decision; in `C7_mc.json`, 2,772 of the 2,846 floats other than `runtime_s` differ only in the last bits (Flag 16).

**Interim wording (verbatim):** "H1 and the CW forecast test may disagree; disagreement is not by itself evidence against H1. The expected joint behaviour is quantified in Pass 4."

Here "Pass 4" means Pass 3, calibration, under P44's naming. The joint cross-tab in the confirmation structure is a Pass 3 task.

### 4.5 Economic evaluation

A market-on-open → market-on-close trade in the miners, hedged with 1306 sized by β. That is four auction executions per day.

**Cost inputs needed before Pass 3 [CAL]**, each with a primary value and a sensitivity range:
- commission per side, for the miners and for 1306, including consumption tax;
- auction impact per side;
- the cost of an intraday short;
- the notional assumed.

SESOI = round-trip cost / mean |partialled overnight FX|. The denominator uses predictor data only.

**Pass 3 (P72).** The inputs are Isaiah's (2026-10-06; `docs/P3_COST_INPUTS.json`). The mean round trip per name-day, 24.5961 bp (low 2.0333, high 77.2878), over mean |ẽ| = 28.4288 bp gives SESOI 0.8652 (low 0.07152, high 2.719).

---

## 5. Power (PREVIEW; binding run in Pass 3)

The B7b preview: dev-calibrated simulations, T_conf = 1,013, one sealed fit, on the TOPIX hedge. The binding Pass 3 run uses the 1306 hedge (AM-03).

| b | 0 (size) | 0.10 | 0.25 | 0.40 |
|---|---|---|---|---|
| H1 rejection rate | **6.04%** [5.41%, 6.73%] | 22.5% | 78.2% | 98.5% |

- The minimum detectable effect at 80% power is **b ≈ 0.257**, roughly the case where a third or more of the miner-relative FX information is unpriced at the open.
- Driscoll–Kraay SE/sd = 0.960.

All of this is rerun in Pass 3 on the rebuilt panel with the 1306 hedge, and the binding numbers go into the pre-registration. A null is interpreted against the minimum detectable effect and, when viable, the equivalence test; never as "no effect".

**Binding numbers (Pass 3, P79).** Dev-calibrated simulations on the 1306 hedge, T_conf = 1,013, one sealed fit (`BLIND_FIT_LOG` line 7), DK with the normal reference:

| b | 0 (size) | 0.10 | 0.25 | 0.40 |
|---|---|---|---|---|
| H1 rejection rate | **5.82%** [5.20%, 6.50%] | 21.2% | 80.9% | 99.5% |

- The minimum detectable effect at 80% power is **b = 0.2471** (probit interpolated; 0.2425 and 0.2400 by the normal approximations).
- Clark–West (M3 against M2) with its calibrated critical value rejects 5.0%, 31.0% and 90.4% at b = 0, 0.10 and 0.25 (T3).
- TOST at the primary SESOI declares equivalence in 5,000 of 5,000 draws at b = 0, and in 296 of 5,000 (5.92%) at b = +SESOI.

---

## 6. Robustness (pre-listed; P33)

1. Exclusion window D, D+1, D+2 (β stays under the primary exclusion).
2. Audit candidates excluded.
3. Tail handling (§3.5): Huber, FX winsorized, the influence curve.
4. FCX in place of COPX.
5. Rolling-250 β in place of the expanding β; and rolling-500 β (`beta_rolling_500`, AM-05; D9).
6. The raw target, with the decomposition.
7. Per-ticker slopes (Holm).
8. Excluding BoJ days; excluding major SQ (futures settlement) days.
9. **The post-2024-11-05 TSE session change** (confirmation only): design + post + e × post, reporting b_pre and b_post. Outside the Holm family. Implemented with the confirmation script before `prereg-v1`.
10. **Yen-denominated EWJ** as an added control (after Pass 2; the US-session USD/JPY leg follows P49). AM-05: `ewj_oc_jpy` with ticker-specific slopes, on the primary rows where it is finite.
11. **The XAU dark-window return** as an added control (P41). AM-05: `xau_ret` with ticker-specific slopes, on all primary rows, with no staleness filter.
12. **The Nikkei proxy** (Japan 225 CFD dark-window return) as an added control, **only on nights where both window endpoints are at most 5 minutes stale** (P42, adopted, D7; P63): 929 of the 1,708 dev nights (40 in 2015-H1, the rest from 2018-04-13) and 999 of the 1,019 confirmation nights are eligible. This check underwrites claim tier (ii). Its amendment compares b with and without the control on the same eligible nights, and states the operational tier-(ii) criterion before `spec-dev-v1` (P56). AM-05: `n225_ret` with ticker-specific slopes, b reported with and without it on the eligible nights.
13. **The gotobi flag** (Tokyo-fix flow days) in the mechanism specification (§9.2). Definition (P48): the 5th, 10th, 15th, 20th, 25th and 30th, plus month-end; a nominal date that is not a trading day moves to the preceding trading day. AM-05 (`mechanism_session_fx_gotobi`): adds `c_usdjpy_sess_ret` and `c_eurusd_sess_ret` (common slopes), `gotobi_day` (common) and `usdjpy_ret` × `gotobi_day` (common); descriptive, outside every claim tier and the Holm family.

**Mechanism specification (not tradable):** primary + session USD/JPY and EUR/USD (09:00 → close). It separates "FX keeps moving and the stock follows contemporaneously" from "the stock lags FX" (problem 1.6 in the original analysis).

**Every robustness amendment** (AM-05) states its exact design, its slopes (common or ticker-specific) and its estimation sample before `spec-dev-v1` (P56).

---

## 7. Mathematical component [ADVISOR]

Each result needs a statement, a proof, its assumptions, and a numerical check.

**A′: replaces the thesis plan's Proposition A [ADVISOR QUESTION].** Proposition A, a cross-sectional exposure slope, can't be identified with N = 3. A′ is v2.0's M1, extended:

- (i) Under a partial-adjustment auction, the pre-open b = (1 − ρ)δ, and b = 0 under an efficient but noisy auction.
- (ii) The naive auction-conditional FX coefficient equals kδ even when the auction is efficient, so it is not a mispricing test.
  - k = V_η/(V_f + V_η), where V_η is the variance of the auction noise η (the part of the gap that reverts during the session) and V_f is the variance of the non-FX fair-value change entering the gap (other overnight news), both conditional on the controls.
  - k is Proposition C's signal-extraction weight.
- (iii) Conditioning on the gap surprise reproduces the pre-open b exactly (FWL).
- (iv) f = b/δ_cc = 1 − ρ.
- (v) The omitted-variable bias when the non-FX factor is only partly spanned by the controls. This is the formal reason for the Nikkei-proxy caveat.
- (vi) The abnormal target measures relative underreaction: b = (1 − ρ)δ_i − β_i(1 − ρ^M)δ_M.

Parts (i)–(iii) are verified numerically in B6; (iv) matches P24.

**M2.** The sign prediction is derived for the *conditional* coefficient a₂ (EUR/USD, given COPX), including the condition on κ under which dollar-wide and yen-specific pass-through have opposite signs.

**M3 (rescoped).** The γ projection is gone, and β is now past-only expanding. M3 becomes: validity of confirmation inference when the target is built with a past-only estimated β (a generated target whose estimation error vanishes), plus a Murphy–Topel-type correction for when that fails.

**M4.** Consistency of Driscoll–Kraay for pooled fixed effects with N = 3 and large T, and the effective-sample-size expression. Numerical checks:
- B6: DK = NW on the equal-weighted portfolio to 1e-8; coverage 95.2% at T = 1,708;
- B7b: SE/sd 0.960 at T_conf.

**OOS penalty lemma: replaces Lemma K [ADVISOR QUESTION].** R²_OOS ≈ R² − k/n under OLS. M6 was dropped, so Lemma K (Kalman filter = recursive OLS under constant parameters) lost its empirical anchor.

Verified in B6 as simulated mean OOS R² vs the formula R² − k/n (R² = 0.0025, n_train = 1,700, 300 reps):

| k | Simulated | Formula |
|---|---|---|
| 1 | +0.00168 | +0.00191 |
| 10 | −0.00295 | −0.00338 |

The lemma justifies the parsimonious ladder and explains Math 86's negative OOS R².

**Proposition B (gap-robust bipower CLT).** Keep. It underpins `usdjpy_bv` and the jump-share interaction. Caveat: Dukascopy's flat rollover bars (0.6–0.7%) bias BV down and the jump share up.

**Proposition C (signal extraction).** Keep. It underlies A′(ii) and the high-RV and jump-share sign predictions.

**Advisor questions:**
1. Does A′ replace Proposition A?
2. Does the OOS lemma replace Lemma K?
3. Do A′, M2–M4, the lemma and Propositions B and C together meet the honors proof requirement?
4. Is this three-miner study the thesis?

---

## 8. Passes and milestones (P36 order; P44 naming)

| Pass | Contents | Done when | Stop point |
|---|---|---|---|
| 1 | Analysis machine | **Complete** (2026-10-02): 171 tests, 5 skipped by default; 6 sealed fits. Stage C4–D rebuilt 2026-10-05 (P45): 205 tests, 4 skipped in the sandbox and 5 on the Mac; the same 6 sealed fits | — |
| 2 | Data and rebuild (`PASS2_HANDOFF.md`) | **Complete** (2026-10-06): see below; run as corrected by `PASS2_ADDENDUM.md` (P51); decisions P58–P70 | Yes, at every decision point, including one combined decision checkpoint before the switch commit |
| 3 | Calibration, dev still blinded | **Complete** (2026-10-07): one sealed fit (`BLIND_FIT_LOG` line 7); the selection and the switch (AM-07, AM-09, AM-10); decisions P71–P81 | Each AM-xx |
| — | **Tag `spec-dev-v1`** | Inference and calibration **locked** | — |
| 4 | Dev first look (exploratory) + P13(b) dry run | Confirmation script recovers a known b on simulated data, runs end to end on dev; post-2024 row implemented | Yes |
| 5 | Pre-registration (S4) | Prior exposure disclosed, sealed hash recorded, the sealed panel's old-column provenance disclosed (P59), advisor sign-off → **tag `prereg-v1`** | Yes |
| 6 | Confirmation | Sealed panel opened once; every pre-registered output produced. Forward holdout after that (P13a) | — |

**Pass 2 is done when:**
- the inputs pass their hash checks;
- the new columns are built and tested;
- the old columns are unchanged;
- the sealed panel's dates are cross-checked against the calendar;
- A7 is rerun on 1306 and the staleness test is run (both dev only; the staleness reading follows P55);
- the hedge switch and the new hashes are recorded as AM-xx, approved at one decision checkpoint and applied in one switch commit (P51);
- the C7 slow tier has been rerun once and has reproduced every replication within the D16 criterion (P68), which replaces P51's "bit for bit" for this rerun because of Flag 16; on the Mac, the slow tier's two bit-identity tests pass against the Mac report;
- the docs are updated.

**Pass 3 is done when** the following are run on dev-calibrated simulations through **one** sanctioned sealed fit, with each outcome written as an AM-xx:
- the binding size run;
- the joint H1/CW cross-tab;
- the Flag 10/12 decisions;
- the SESOI and equivalence viability;
- power.

P35 lists these as tasks T1–T7; consult it for the exact numbering.

Dates are set with the advisor; v2.0's dates are only indicative.

---

## 9. Out of scope (possible extensions after confirmation; each needs its own mini pre-registration)

1. **Speed:** first-hour intraday horizons; this needs intraday equity bars.
2. **Mechanism:** post-open FX around the 09:55 Tokyo fix. This partly enters as the §6 mechanism specification, using the session FX columns from Pass 2.
3. **Cross-section:** exporters and domestic firms as comparison groups for the cascade claim.
4. **The archived multi-market filtering programme** (Plan v1.1).

---

## 10. Operating rules for Claude

1. **Dev only until `prereg-v1`.** Never request, reconstruct or analyse 2022+ outcome data, or anything after 2026-03-05.
   - 2022+ event release **dates** and calendar data are allowed.
   - In Pass 2, the sealed panel is **written** by the build and checked only by dates, counts and hashes.
2. **Blinding.** No computation whose output relates any predictor to any target on real data. Predictors here include FX, XAU, Japan 225, the US controls and session FX.
   - The **one** exception is the sealed blind fit, under its tested conditions (P29), opt-in through `OFILT_RUN_SEALED=1`. Each run must be sanctioned explicitly and counted in `BLIND_FIT_LOG`.
   - Allowed: hashes; structural checks; predictor-only statistics; target-only statistics without predictors (such as A7); gap-only statistics on dev (such as the staleness test).
3. **Features** come only from the schema allowlist (`select_features`). `open`/`close`/`prev_close`/`audit_flag` are never features. New Pass 2 predictors go in `PRE_OPEN_ROBUSTNESS` (P43, adopted as P50). Session FX is `CONTEMPORANEOUS`.
4. **Nuisance quantities** are fitted past-only or on dev only.
5. **Spec changes** need Isaiah's instruction and an AM-xx entry. The spec is pinned in `spec.py`.
6. **Report** every pre-registered result, including nulls.
   - Accuracy always appears next to its base rate.
   - Nested comparisons use Clark–West.
   - Importance is permutation-based only.
7. **Never cite an unverified reference.**
8. **Stop** at every decision point in `PASS2_HANDOFF.md`, at each AM-xx, at `spec-dev-v1`, and at `prereg-v1`.
9. **Raw data and the code repository never go in the Claude Project.** Sessions receive the repo as a tarball or, in Claude Code, from the local clone. Raw files need not be uploaded to chats either. When a supervisor chat must verify them, it hashes them and reads nothing beyond what the check needs (DATA_PROVENANCE §4.5). No session ever opens or prints a raw or sealed file (P51).

---

## 11. Risks and open flags

| Risk / flag | Mitigation |
|---|---|
| Low power at plausible effects (MDE80 0.2471, binding; P79) | Interpret against the MDE; the equivalence test (viable, P79); the forward holdout adds data |
| **Flag 6:** TOPIX ex-dividend error in hedge gaps | Fixed in Pass 2: 1306 gap with its own dividends; the TOPIX total-return component on the fallback path |
| **Flag 10:** DK slightly oversized (~6%) at T_conf | RESOLVED (P79): 5.82% on the binding run, inside AM-02's band; DK-normal kept |
| **Flag 12:** CW conservative (3.00% in the rebuild; 2.67% in the original run; P54) | RESOLVED (P79): 3.30% on the binding run; the primary comparison uses c_CW,cal (AM-09) |
| **Flag 5:** guard signature | RESOLVED. The canonical repo has no external guard, and a conjunctive fail-closed adapter guards against one appearing (P45, P46) |
| **Flags 2 and 4:** fingerprint check is a mislabelling net only; coarse early-dev ticks for 5706/5711 | Frozen; Flag 4 feeds the cost model and the Huber/winsor behaviour |
| 1306 dividend factor (P39) | RESOLVED. Issuer documentation and published distributions confirm ÷10 (P47); the settings check is resolved by attestation (D2; P60) |
| **Flag 16:** platform floating point (the Pass 1 panels were built on x86_64; the Mac differs in the last bit) | Hashes prove identity only on the same platform; across platforms, tolerance checks stated in advance (DATA_PROVENANCE §5.2; P58) |
| Pass 1 verification tests pin Pass 1 state, and any spec amendment invalidates the C7 report | Test-change protocol, the `pass1-final` tag, one batched switch commit and one C7 rerun (P51) |
| Exposure to sealed data through file viewers in an agentic session | No raw or sealed file is ever opened or printed; scripts print only counts, hashes and permitted dev statistics; sealed output lives outside the repo and the Project (P51) |
| **Japan 225 coverage** (P42) | P42 adopted (D7): 929 dev / 999 confirmation nights |
| β or the hedge unstable across samples | Expanding β carried across samples; rolling-250 and rolling-500 robustness rows (AM-05) |
| Unscheduled firm news left in the sample | Accepted by design (P08); audit-exclusion robustness |
| Math component judged insufficient | Advisor questions in §7, raised early |
| Forking paths | One primary test; pre-listed robustness; one-shot rule (P13c); run registry; calibration done before any dev result is seen (P36) |

---

## 12. References (all [UNVERIFIED]; confirm before citing)

- Lou, Polk & Skouras (2019), *JFE*: overnight versus intraday returns.
- Hong & Stein (1999), *JF*: gradual information diffusion.
- Cohen & Frazzini (2008), *JF*: economic links.
- Madhavan & Panchapagesan (2000), *RFS*: price discovery in auctions.
- Barclay & Hendershott (2003), *RFS*: after-hours price discovery.
- Driscoll & Kraay (1998), *REStat*: spatially dependent panel inference.
- Clark & West (2007), *J. Econometrics*.
- Clark & McCracken: nested forecast tests.
- Diebold & Mariano (1995), *JBES*.
- Pesaran & Timmermann (1992), *JBES*.
- Murphy & Topel (1985), *JBES*: generated regressors.
- Huber (1964): robust M-estimation.
- Fieller (1954): ratio intervals.
- Schuirmann (1987): TOST.
- Politis & Romano (1994): stationary bootstrap.
- Barndorff-Nielsen & Shephard (2004): bipower variation.
- Bodnar & Gentry (1993), *JIMF*: FX exposure of Japanese industries.
- Ito & Yamada (2017), *Journal of International Economics* 109: 214–234, "Puzzles in the Tokyo fixing in the forex market: Order imbalances and bank pricing" (NBER WP 22820): the Tokyo-fix order imbalance and payment-day effects. Bibliographic details checked 2026-10-05; read the paper before citing its findings.

---

## 13. Change log

**v2.4 → v2.5 (2026-10-07)**
- Pass 3 recorded as P71–P81: the builder prompt and the one sealed fit (P71); the cost inputs and the SESOI (P72); inference and the joint rule (P73); the run's design and its tool (P74); T6's outputs (P75); the rehearsals (P76); DQ5, DQ6, salvage and the launcher (P77); the sanction and the seventh sealed fit (P78); the selection (P79); the switch (P80); this refresh (P81).
- The status block, the companion files and §1.3, §3.4, §4.5, §5, §8 and §11 updated to match.

**v2.3 → v2.4 (2026-10-06)**
- Pass 2 recorded as P58–P70: the environment and Flag 16 (P58); the old-column sources (P59); the settings check by attestation and the TOPIX total-return ticker (P60); the build and its acceptance (P61); corrected input records (P62); D7, D8, D9 and D10 (P63–P66); AM-03 to AM-05 and the switch (P67); the C7 rerun on the Mac (P68); the repository and the accepted deviations (P69); this refresh (P70).
- The status block, the companion files and §1.2, §2.1, §2.2, §3.1, §4.4, §5, §6, §8, §11 updated to match: hedge 1306 (AM-03); the β comparison on 1306 and the `beta_rolling_500` row (D9); AM-05's design of the robustness rows; P42 adopted (D7); the C7 criterion (D16); the sealed old-column disclosure; a Flag 16 risk row.

**v2.2 → v2.3 (2026-10-05)**
- Pre-flight decisions recorded as P45–P57:
  - the rebuilt repo is canonical (P45), behind a conjunctive guard (P46);
  - the 1306 ÷10 factor is confirmed (P47);
  - the gotobi definition (P48) and the US-session window with NYSE early closes (P49) are fixed;
  - the column names and groups are fixed (P50);
  - Pass 2 runs append-only, with one decision checkpoint, one switch commit and the test-change protocol (P51);
  - the blinding list is extended (P52);
  - Flags 14 and 15 are accepted as implemented (P53);
  - the citable rebuilt numbers are recorded (P54);
  - the staleness-test reading rule (P55) and the robustness-amendment standards (P56) are fixed in advance.
- The status block, the companion files and §1.4, §2.2, §4.4, §6, §8, §10, §11 and §12 updated to match. The Ito & Yamada reference is completed. `PASS2_ADDENDUM.md` is added to the companion files.

**v2.1 → v2.2 (2026-10-04)**
- Pass 2 inputs pulled and verified: §2.2 and DATA_PROVENANCE §4. Offer side confirmed bid (P37); pull procedure patched (P38).
- 1306 hedge data accepted, with corrected dividends pending CACS (P39); TOPIX total return as a fallback input (P40); XAU (P41); Japan 225 with its coverage rule PROPOSED (P42).
- New predictors kept out of the primary allowlist (P43, PROPOSED).
- Pass renaming (P44). §5 now lists the binding Pass 3 items; §6 adds items 9–13; §8 adds the Pass 2/3 completion criteria.

**v2.0 → v2.1 (Pass 1, P14–P36)**
- One estimand (yen-specific b via FWL); H2 retired; H3 restated.
- Expanding past-only β, with the A7 rule on common rows; 1306 hedge with the fallback rule.
- Controls trimmed (EWJ out); explicit allowlist replacing prefix rules.
- Driscoll–Kraay plus the AM-02 size rule at T_conf = 1,013; tails and influence curve replacing the named crisis windows.
- TOST; f confirmatory for 2022 only; secondary family with AM-01 main effects.
- Forecasting ladder (M6 dropped) and walk-forward protocol; blinding architecture with the sealed-fit exception.
- Power preview; claim tiers; robustness list; the P36 sequencing; the §7 rescope (A′, OOS lemma).

**v1.1 → v2.0:** scope reduced to Japan, three miners and one linear model; target changed from the opening gap to open→close; Dukascopy FX; Driscoll–Kraay; math results M1–M4.
