# DECISIONS.md addendum, part 2 — Pass 1 (analysis machine), October 2026

These continue `DECISIONS_ADDENDUM.md` (P01–P13) and are ready to merge into `docs/DECISIONS.md`; renumber on merge if needed. Format as in P01–P13: a bold title with status, then the decision, *Reason* and *Effect*.

Status values:
- **ADOPTED (Isaiah, 2026-10-01):** decided and implemented in `ofilt/drift/` and/or `spec/analysis_spec_dev_v1.yaml`.
- **ADOPTED, PENDING …:** decided, but a named input arrives later (costs, Pass 2 data).
- **PLANNED:** decided, not yet implemented (Pass 2 or later).
- **ADVISOR QUESTION:** not a decision; to be settled with the thesis advisor.

Coverage:
- D1: P14–P21 (estimand, hypotheses, target, hedge, controls, allowlist, inference).
- D2: P22–P28 (tails and influence, equivalence, f, secondary family, forecasting ladder, walk-forward protocol, validation).
- D3: P29–P35 (blinding, power, prior exposure and claim wording, robustness list, Pass 2 and Pass 4 plans).
- D3b: P36 (pass sequencing and tag semantics).

Sources: the spec (`spec/analysis_spec_dev_v1.yaml`, status DRAFT until the `spec-dev-v1` tag), `spec/SPEC_AMENDMENTS.md` (AM-01, AM-02), and the decision log in `PASS1_STATUS.md`. Where an entry's *Reason* restates the Pass 1 brief rather than a recorded analysis, it says so. The spec governs whenever this file and the spec differ.

---

**P14: One primary estimand; H1 (ADOPTED (Isaiah, 2026-10-01)).**
For stock i on Tokyo day t, the primary regression is

  abn_oc_{i,t} = α_i + b · usdjpy_ret_t + a₂ · eurusd_ret_t + s_i · spy_oc_t + c_i · copx_oc_t + ε_{i,t},

with ticker fixed effects and no global intercept, the FX block **common** across tickers, and the two controls **ticker-specific** (spec `model`). The primary estimand is the pooled common coefficient **b** on `usdjpy_ret`.
- **H1:** b ≠ 0, two-sided at α = 0.05 (spec `inference.test`, `alpha`). This settles the PLAN §1.3 choice between one- and two-sided tests in favour of two-sided.
- **Meaning of b.** Because `eurusd_ret` is in the design, Frisch–Waugh–Lovell gives b as the slope on the part of `usdjpy_ret` orthogonal to `eurusd_ret` (and to the controls and fixed effects). It is therefore the session drift per unit of **yen-specific** overnight USD/JPY move, holding the dollar-wide move fixed. The sign table of PLAN §1.2 still applies: b > 0 means underreaction (the stock keeps drifting in the FX-implied direction during the session), b < 0 means overreaction, and b = 0 means the auction priced the move.
- The study has **one** estimand and one primary specification. The PLAN/README "two specifications, never mix their columns" framing is retired (see P16).

*Reason:* a single pre-specified test avoids forking paths. Including EUR/USD separates the dollar-wide component, which the cascade argument says is priced differently (P15), from the yen-specific one.
*Effect:* supersedes PLAN §1.2–1.3 (H1 on the raw e_t), §3.3 (control list; see P19) and §3.6 (the projection-based split; see P15). The coefficient name is pinned in `spec.model.h1_parameter = usdjpy_ret`.

**P15: H3 restated as a test of the EUR/USD coefficient (ADOPTED (Isaiah, 2026-10-01)).**
**H3:** a₂ = 0 in the P14 regression (spec `model.h3_parameter = eurusd_ret`), reported with its DK SE. This replaces PLAN §3.6, which built e^$ = γ̂·eurusd_ret and e^¥ = e − e^$ from a development-sample projection.
- **Algebra.** Write usdjpy_ret = γ·eurusd_ret + e^¥. Then b·usdjpy_ret + a₂·eurusd_ret = b·e^¥ + (bγ + a₂)·eurusd_ret. The coefficient on the dollar-wide component is b^$ = bγ + a₂. So a₂ = 0 is exactly the restriction that dollar-wide and yen-specific USD/JPY moves carry the **same** session drift per unit of USD/JPY: the "common weight" auction of PLAN §7 M2. The cascade model predicts a₂ ≠ 0.
- **Conditional reading.** a₂ is identified relative to two modelling choices: (i) EUR/USD as the proxy for the dollar-wide move, and (ii) COPX in the design. COPX absorbs the US-session metals channel, so a₂ measures differential pass-through **not** explained by COPX's US-session return. A different dollar proxy (for example DXY) or metals control would change a₂'s meaning, and both are fixed before the tag.
- No estimated projection γ̂ enters the test, so PLAN §7 M3's generated-regressor issue does not arise for H3.

*Reason:* the restated test is algebraically equivalent to comparing b^$ with γ·b^¥ in the same regression. It needs no nuisance estimate and no development-sample fit carried into confirmation.
*Effect:* supersedes PLAN §1.3 H3 and §3.6. PLAN §7 M2 should derive its sign prediction for a₂ (equivalently for b^$ − γb^¥).

**P16: The auction-conditional specification is retired as a mispricing test (ADOPTED (Isaiah, 2026-10-01)).**
H2 (PLAN §1.3, §3.5: add the realised gap `ao_gap_adj` and `ao_topix_gap` to the regression) is retired. The `ao_` columns are never model features; `schema.AT_OPEN` refuses them. They are used only to build the gap and close-to-close targets for the decomposition and for f (see the f entry below).
- **Evidence (B6, synthetic noisy-auction simulation, n = 2,000,000; δ = 0.5, k = 1/3).** Suppose the auction **fully** prices FX (ρ = 1), but its price carries noise η that reverts during the session. Then the pre-open regression gives b = −0.003 (truth 0), while the auction-conditional regression gives 0.162. That spurious "underreaction" matches its analytic value k·δ = 0.167.
  - With partial pricing (ρ = 0.7), the pre-open regression gives 0.154 against the true (1 − ρ)δ = 0.15. The auction-conditional regression gives 0.269 against its biased analytic value 0.267.
  - Replacing the gap by its surprise (the gap orthogonalised on pre-open information) reproduces the pre-open coefficient exactly (to 1e-16), so it adds nothing.

*Reason:* conditioning on a regressor that contains reverting auction noise manufactures a positive coefficient even when the auction prices FX correctly. A "mispricing test" built that way rejects for the wrong reason.
*Effect:* supersedes PLAN §1.3 H2, §3.5 and P04's auction-conditional specification. README's two-spec framing goes (D4). `schema.py` documents the AT_OPEN refusal reason.

**P17: Target, past-only expanding β on non-excluded rows, and the A7 criterion (ADOPTED (Isaiah, 2026-10-01)).**
The target is abn_oc_{i,t} = y_oc_{i,t} − β_{i,t−1}·hedge_oc_t (spec `target`). The definition of β_{i,t−1}:
- per ticker, the past-only **expanding** OLS slope of y_oc on hedge_oc;
- min_periods 250 and lag 1 day: β for day t uses data through t − 1 only;
- estimated on **non-excluded** rows (not earnings/news D, D+1; finite target and hedge);
- continued across the dev → confirmation boundary, so confirmation days use all prior data.

The rolling 250-day β is a robustness row (`beta_rolling_250`).

A7 decision: the window is chosen by hedged-return variance on the **common** rows where every candidate β exists, not on each window's own rows. On own rows, rolling-500 beat expanding for 5711 by 0.025% (11,659.7 vs 11,662.6 bp²), but that cell had 1,140 rows against 1,168. On common rows, expanding is lowest for all three stocks (5711: 11,639.9 vs 11,659.7). Isaiah kept the expanding β; the own-rows table is kept for transparency.

*Reason:* a past-only β uses no confirmation information at any date. This is stricter than PLAN §3.1's "estimate once on dev", which leaves a dev-fitted β stale for four confirmation years. Comparing windows on unequal row sets confounds window choice with sample composition.
*Effect:* supersedes PLAN §3.1 (primary β) and the fixed-β option in P05; README rule 3 is unchanged in spirit (past data only). Implemented in `targets.past_beta`, which reproduces Isaiah's reference code bit for bit (A7a). Look-ahead perturbation tests: A8 for β and targets, C7 for predictions.

**P18: Hedge instrument: 1306 after Pass 2, with a fallback fixed before the tag; raw target secondary (ADOPTED (Isaiah, 2026-10-01); switch and A7 rerun PLANNED for Pass 2).**
- `target.hedge_oc_column` is `y_topix_oc` as a **placeholder**. In Pass 2 it becomes the open→close return of the TOPIX ETF **1306** (NEXT FUNDS TOPIX ETF), built from daily OHLC with a split/dividend check.
- **Switch-before-tag rule (Isaiah, 2026-10-01):** "If 1306 daily data cannot be obtained, or fails its Pass 2 checks (split/dividend adjustment, open-auction timing), the primary target switches to the raw open->close return before the spec-dev-v1 tag, never after. The abnormal target is then reported as secondary using the TOPIX index with the staleness caveat."
- The switch must also add 1306's gap pairing to `targets.HEDGE_GAP_FOR`, which deliberately raises for any hedge other than TOPIX. It must dividend-adjust the hedge legs per Flag 6, including 1306's own annual ex-date. The B7b preview is re-run as the binding Pass 4 size/power run on the rebuilt data (AM-02).
- **A7 rerun on 1306 (ADOPTED for Pass 2, Isaiah, 2026-10-01).** The criterion is the same target-only one as A7: the variance of the hedged return, with all windows compared on common rows. Expanding stays primary unless it loses on common rows; if it loses, STOP and flag. This is a nuisance choice with no FX involved.
- **Secondary target:** `raw_oc` (= y_oc, spec `target.secondary`), with the decomposition b_raw ≈ mean(β)·b_mkt + b_abn. Here b_mkt is the hedge's open→close return regressed on the date-level version of the same design (time-series NW, same lag rule). The identity is exact on a balanced panel with constant β (B3, gap 7e-16).

*Reason:* the hedge leg must be tradable at the auction and the close, as the economic evaluation requires. The TOPIX **index** print at 09:00 includes constituents that have not yet traded, which makes it stale (Pass 2 runs an index-staleness test). Fixing the hedge, and its fallback, before the tag removes a degree of freedom that could otherwise be exercised after seeing results.
*Effect:* the binding size/power numbers, the A7 table and the panel hashes all change in Pass 2. `spec-dev-v1` is tagged only after that rebuild (status line of the spec).

**P19: Primary controls: SPY and COPX, ticker-specific; EWJ out; FCX as robustness; no lags or dummies (ADOPTED (Isaiah, 2026-10-01)).**
- **Primary controls:** `spy_oc` and `copx_oc` (summed US open→close over the NY sessions inside the dark window, P11), with **ticker-specific** slopes. COPX is fixed as the metals proxy. This replaces PLAN §3.3's "COPX or FCX chosen on development data by a pre-stated rule".
- **EWJ is out of the primary design.** EWJ is USD-denominated, so its US-session return contains the USD/JPY move over the US session, part of the regressor itself. Controlling for it would absorb part of b mechanically. A **yen-denominated** EWJ (EWJ return plus US-session USD/JPY) is the robustness row `ewj_yen_denominated_REQUIRES_PASS2`, because it needs US-session USD/JPY from the Pass 2 FX pull.
- **FCX** enters only as the robustness swap `copx_to_fcx`.
- **No lags, calendar dummies or window-structure terms in the primary.** PLAN §3.3 listed `gap_adj_lag1`, `oc_lag1`, `window_hours`, a no-US-session dummy, and BoJ/SQ/ex-dividend dummies; none is in the primary. BoJ and major-SQ days are robustness exclusions (`exclude_boj_day`, `exclude_sq_major`). Window length enters the secondary family (`fx_x_longwindow`, P-entry for the secondary family below).

*Reason:* EWJ's exclusion is mechanical: its USD leg overlaps the regressor. For the rest (Isaiah, 2026-10-01): "A control belongs in the primary design only if it is correlated with overnight FX AND predicts the drift. Lagged returns fail the first condition in practice (dev abnormal-drift autocorrelation is at most |0.075| at lags 1-5, and overnight FX is close to unpredictable from yesterday's stock returns), so they cost degrees of freedom without removing bias. SQ/BoJ/ex-dividend dummies shift the intercept and are uncorrelated with FX, so they move to robustness." The figures are Isaiah's and were not recomputed in Pass 1: a target autocorrelation, or a relation between FX and lagged stock returns, on real data is outside Pass 1's blinding rules. Fixing COPX avoids a development-data choice rule whose input would partly be the target.
*Effect:* supersedes PLAN §3.3. The spec's `require_nonmissing` = [usdjpy_ret, eurusd_ret, spy_oc, copx_oc, beta].

**P20: An explicit feature allowlist supersedes README rule 2 (ADOPTED (Isaiah, 2026-10-01)).**
README rule 2 ("features come from unprefixed columns") is replaced by explicit frozensets in `ofilt/drift/schema.py`. Every one of the 41 panel columns sits in exactly one group:

| Group | Count | Role |
|---|---|---|
| KEYS | 2 | identifiers |
| PRE_OPEN_FEATURES | 20 | allowed as features |
| EXCLUSION_FLAGS | 2 | sample filters only |
| INFORMATIONAL | 1 | recorded, not used |
| ROBUSTNESS_ONLY | 1 | `audit_flag` |
| AT_OPEN | 3 | the `ao_` columns |
| TARGET_INPUTS | 2 | outcomes |
| PROVENANCE | 10 | QA and price columns |
| CONTEMPORANEOUS | 0 | placeholder for Pass 2 |

- Model features may come only from PRE_OPEN_FEATURES, from six named derived features (long_window, jumpshare, rv_per_bar, e_pos, e_neg, no_us_session; deterministic row-wise, no estimated parameters), or from the synthetic `noise_N01`, which the model generates itself.
- The only non-PRE_OPEN source a derived feature may read is `usdjpy_bars`, as the denominator of rv_per_bar (Flag 1).
- Unknown columns are refused everywhere (fail closed), and nothing selects columns by prefix or pattern.
- `open`, `close`, `prev_close` (unprefixed, but auction or target prices) and `audit_flag` (unprefixed, but outcome-selected, P08) are **forbidden** as features.

*Reason:* rule 2 would have admitted `open`, `close`, `prev_close` and `audit_flag`. A pattern rule fails silently when a column is added.
*Effect:* README rule 2 and the README/DATA_DICTIONARY "unprefixed = pre-open" wording change (D4, D5). `select_features` is the only production path for features, and `walk_forward` enforces it.

**P21: Inference, the Pass 4 size rule (AM-02) and T_conf = 1013 (ADOPTED (Isaiah, 2026-10-01)).**
- **Estimator and inference.** Pooled OLS with ticker fixed effects. Driscoll–Kraay standard errors: date-summed scores, Bartlett kernel, lag ⌊4(T/100)^{2/9}⌋ with T = unique dates in the estimation sample (7 at T = 1708, 6 at T = 1013). No small-sample correction, normal reference, two-sided 5% (spec `inference`).
- **Size rule (AM-02).** In Pass 4, run 5000 dev-calibrated simulations at b = 0 with T = T_conf. The rejection rate must lie in [3.5%, 6.5%]; otherwise primary inference switches to a stationary block bootstrap (mean block 5). That choice is made before the tag. This amends 2000 sims at an unstated T.
- **T_conf = 1013** (`ofilt.drift.calendar`, B7a): 1,019 confirmation trading days from a hard-coded TSE holiday list, minus the 6 dates on which all three tickers are excluded. Each ticker loses 34 rows; exclusions are otherwise ticker-specific. The inputs are calendar data and 2022+ event release dates only (sanctioned); the same mapping reproduces the dev panel's earnings/news flags exactly. Pass 2 cross-checks the calendar against the rebuilt sealed panel's dates (dates only).

*Reason:* DK suits N = 3 tickers with large T and strong same-day cross-correlation. AM-02: the B7 pilot implied a true size near 6% at confirmation length, so 2000 reps (MC SE about 0.5 pp) could flip the rule by noise alone; 5000 reps gives about 0.3 pp. The earlier pilot length of 983 also understated T. Neither change uses information about b.
*Effect:* supersedes PLAN §3.4's open bandwidth rule. `spec.SIZE_RULE` pins the amended text, the verbatim-diff test enforces it, and a test ties "1013" in the rule to `calendar.T_CONF`.

---

*Part 2 (D2): P22–P28.*

**P22: Tails and influence: Huber, winsorised FX, and a date-level influence curve replace the named crisis windows (ADOPTED (Isaiah, 2026-10-01)).**
The pre-listed robustness rows for heavy tails and influential dates (spec `robustness`):
- **Huber.** M-estimation with c = 1.345 and a **fixed** scale of 1.4826 × MAD of the OLS residuals, solved by IRLS, with a DK sandwich using the same kernel and lag. As c → ∞ it reproduces OLS-DK (B2, 1e-12).
- **Winsorised FX.** `usdjpy_ret` and `eurusd_ret` are clipped at their development 0.5% / 99.5% quantiles. The values are fixed in the spec: usdjpy [−1.6482588843e-02, 1.4399911615e-02], eurusd [−1.6324806371e-02, 1.5438152188e-02]. These are predictor-only statistics (A6), so no target information enters.
- **Influence curve.** For k = 0 … 20, b is re-estimated after deleting the k most influential **dates**. Influence is the exact date-deletion change in b (closed form, equal to brute-force refits to 1e-12). The ranking is fixed once on the full sample and not recomputed as dates are removed; n_dates and the DK lag are recomputed for each k.

PLAN §6 robustness item 3 (exclude March 2020, 2024-08-01 → 08-09 and 2025-04-02 → 04-11) is **removed**.

*Reason:* the named windows were picked because they are known large-move episodes. The two 2024–2025 windows come from earlier looks at what is now the confirmation period: the M1 rebuild found its in-sample gap beta concentrated in them, and PLAN §11 lists their dominance as a risk (prior exposure, PLAN §2). Excluding them would condition the robustness check on previously seen outcomes. The influence curve asks the same question ("is b driven by a few dates?") mechanically, for whichever dates turn out to matter, and Huber and winsorisation cover tail shape.
*Effect:* supersedes PLAN §6 item 3 and the crisis-window row of PLAN §11. The full robustness list is P33.

**P23: Equivalence test: TOST, SESOI pending costs (ADOPTED, PENDING COSTS (Isaiah, 2026-10-01)).**
If H1 does not reject, "the auction fully prices overnight FX" is claimed only through a two one-sided tests (TOST) procedure at α = 0.05. Equivalent means both one-sided p < α, or equivalently the (1 − 2α) CI lies inside (−SESOI, +SESOI).
- The SESOI is `PENDING_COSTS`. It is set from the Pass 4 cost model (TSE tick-size schedule plus a stated spread, PLAN §4) as the smallest drift a market-on-open / market-on-close strategy could exploit net of costs.
- **Viability** (whether TOST can reach a conclusion at T_conf) is decided in Pass 4, after costs are priced and the simulator is run (spec `equivalence.viability`). `Spec.sesoi()` raises `SpecPendingError` until then, so no code path can run TOST with an invented SESOI.
- Flag 4 (the coarse price grid for 5706 and 5711 before their 1:10 consolidations) feeds the cost model.

*Reason:* PLAN §1.4 treats a well-powered null as a finding. A non-rejection alone cannot support "fully priced"; an equivalence bound can, but only once the bound is economically meaningful.
*Effect:* sharpens PLAN §1.4 and §5 ("a null is interpreted against the minimum detectable effect"). TOST is implemented and tested (B2).

**P24: Fraction unpriced f (ADOPTED (Isaiah, 2026-10-01)).**
- **Definition:** f = b / δ_cc. Here δ_cc is the loading of the close-to-close abnormal return (`cc_abn` = gap_abn + abn_oc) on the **same** design and sample. The identity δ_cc = δ_gap + b holds exactly (B3, 1e-12), so f is the share of the total overnight-FX response that is still unpriced at the open.
- **Estimation:** b and δ_cc come from one stacked fit with a joint DK covariance (`fit_joint`).
- **Intervals:** delta method and Fieller. The Fieller set can be bounded, two rays or the whole real line when δ_cc is weakly identified, and all three are reported as such.
- **Status: confirmatory for 2022 only; descriptive for 2023–2026** (spec `fraction_unpriced.status`).
- Flag 6 applies: `gap_abn` and `cc_abn` carry a mechanical TOPIX ex-dividend error on about two days a year. The fix (dividend-adjust the hedge leg, or compute f on the raw target) is decided in Pass 2.

*Reason:* δ_cc contains the FX → opening-gap loading. Math 86 (January 2023 – March 2026) and the M1 rebuild already examined that relationship on 2023+ data (PLAN §2), so f is fresh only for 2022. The open→close relationship behind H1 has never been examined on any data.
*Effect:* PLAN §7 M1's quantities (1 − ρ_e)δ and the auction-conditional version map onto b and f. The retired H2 (P16) is not needed to measure how much is unpriced.

**P25: Secondary family (Holm) with moderator main effects, AM-01 (ADOPTED (Isaiah, 2026-10-01)).**
There are four secondary tests. Each adds one term to the primary design and tests one coefficient, and Holm's correction is applied across the four (spec `secondary_family_holm`):

| Member | Added to the primary design | Tested |
|---|---|---|
| `fx_x_longwindow` | `long_window` + `usdjpy_ret × long_window` (long_window = 1[window_hours > 18], i.e. multi-night windows) | the interaction |
| `fx_x_jumpshare` | `jumpshare` + `usdjpy_ret × jumpshare` (jumpshare = clip((rv − bv)/rv, 0, 1)) | the interaction |
| `fx_x_highrv` | `highrv` + `usdjpy_ret × highrv` (highrv = 1[usdjpy_rv / usdjpy_bars > 1.2950114214e-08], the development median of rv per bar, A6, predictor-only) | the interaction |
| `fx_asymmetry` | `usdjpy_ret` replaced by (max(e, 0), min(e, 0)) | equal slopes |

The main effects are spec amendment AM-01: without them, an interaction coefficient is biased whenever the moderator shifts mean drift and is correlated with e × moderator. M4 in the forecasting ladder carries the same terms, with an expanding past-median highrv threshold.
*Reason and Effect:* as in `spec/SPEC_AMENDMENTS.md` AM-01. These replace PLAN §3.3's "exploratory" FX × volatility interaction with a pre-registered, multiplicity-controlled family.

**P26: Forecasting ladder and comparisons (ADOPTED (Isaiah, 2026-10-01); M7 exploratory).**
Models (spec `forecast.models`; implemented in `ofilt/drift/models/`):

| Model | Definition |
|---|---|
| M0 | zero forecast |
| M1 | prevailing (training-fold) mean per ticker |
| M2 | ticker FE + ticker-specific `spy_oc`, `copx_oc` + `eurusd_ret` |
| M3 | M2 + `usdjpy_ret`. Its design is the primary inference design, so its in-fold coefficients equal `inference.pooled_ols` (1e-12). |
| M4 | M3 + the AM-01 moderators and interactions + min(e, 0) (18 coefficients) |
| M5 | ridge on the M4 design; FE unpenalised by in-fold within-ticker demeaning; α = n_train × {1e-4 … 1}, tuned on the last 250 training dates |
| M7 | `HistGradientBoostingRegressor`, **exploratory** (C4); details in P27 |

- **M6 is dropped.** It is absent from the spec ladder. Per PLAN §13, a filter-type model with constant parameters reduces to the recursive regression already in M3. Whether Lemma K (Kalman/OLS equivalence) stays in the mathematical component is an ADVISOR QUESTION, not a decision (D4).
- **M2 includes EUR/USD.** So CW of M3 vs M2 adds `usdjpy_ret` alone, holding the dollar-wide move fixed. That makes it the real-time counterpart of H1 (P14).

Comparisons (spec `forecast.comparisons`):

| Role | Test |
|---|---|
| Primary | Clark–West, M3 vs M2, one-sided |
| Secondary | CW M4 vs M3; CW M5 vs M3; CW M7 vs M1; Diebold–Mariano M7 vs M1 (two-sided; positive favours M7) |
| Reported for all models | OOS R² vs M0 and vs M1, pooled and per ticker; Pesaran–Timmermann per ticker and on the equal-weighted portfolio, next to the training-window base rate |
| Importance | permutation by whole dates within each fold's test block, 20 repeats, calibrated against a noise column |

- **Test aggregation** (spec): per-row loss differential → mean across tickers within each date → Newey–West (Bartlett) on the date series, lag rule with T = unique evaluation dates, normal reference.
- **Interim wording on H1 vs CW (Isaiah, 2026-10-01; Flag 12 option (c), with (b) as interim text):** "H1 and the CW forecast test may disagree; disagreement is not by itself evidence against H1. The expected joint behaviour is quantified in Pass 4." The Pass 4 joint simulation is task T3 in P35.
- Note: DM between nested models (M7 vs M1) has a non-standard null distribution and tends to under-reject. CW for the same pair is the nested-appropriate test; both are reported as specified.

*Reason:* a ladder of nested linear models isolates what usdjpy_ret adds (M3 vs M2), then what moderators add (M4) and what shrinkage changes (M5). M7 checks for nonlinear structure without being able to drive the confirmatory claim.
*Effect:* supersedes PLAN §4's statistical evaluation ("Clark–West of the full model against the controls-only model") with the explicit ladder. The economic evaluation of PLAN §4 is unchanged and is priced in Pass 4.

**P27: Walk-forward protocol and forecasting machinery (ADOPTED (Isaiah, 2026-10-01)).**
- **Scheme** (spec `forecast`): expanding window, pooled across tickers, refit every 21 panel dates, scaling in fold only, thresholds past-only.
- **First forecast (C1 fold-start correction).** `min_train_dates = 500` counts **eligible** training dates: dates with at least one row that has a finite target, is not excluded and has its feature sources. Fold 0 therefore trains on exactly 500 usable dates. The β warm-up dates (about 258 at the start of dev, no target) do not count. Under the old rule fold 0 had about 240 usable dates, which biased the comparison against larger models.
- **Training rows** exclude `excl_inference` (earnings and standalone news on D and D+1; Flag 11, resolved). Those days are always in the past at each training date, and this matches H1's estimation sample.
- **Evaluation rows** exclude earnings D, D+1 and standalone news D+1 only (spec `sample.forecast_eval_exclusion`). Unscheduled news on day D cannot be known before the open, so a real-time forecaster would face it, and it stays in.
- **One sample per call.** All models in one `walk_forward` call share the fold geometry, training rows and evaluation rows (the union of their feature sources), so paired tests compare identical rows. M7 needs all 20 PRE_OPEN sources; `ewj_oc` is NaN on 3 dev dates. It is therefore run in its own call with its comparator M1, so that it does not shrink M0–M5's sample.
- **Information firewall, enforced by the engine** (`forecast.walk_forward`):
  - the blinding guard runs first;
  - features come only through the allowlist (P20);
  - fit sees rows strictly before the fold's first test date;
  - predict never sees the target.
- **M7 details** (C4):
  - early_stopping=False set explicitly, because sklearn's default turns early stopping on above 10k rows with a random, non-temporal split;
  - fixed learning_rate 0.03, min_samples_leaf 100, l2 1.0;
  - grid max_depth {2, 3} × max_iter {50, 100, 200, 400}, tuned on the last 250 training dates;
  - the `noise_N01` column is generated by the model from the fold seed;
  - `random_state` = fold seed (inert in this configuration).
- **Run registry** (C6): every `walk_forward` call appends one strict-JSON line to `RUN_REGISTRY.jsonl`, or raises. The line records run id, UTC time, git commit, spec and data hashes, models, grids, per-fold chosen hyperparameters and output path.

*Reason:* the protocol makes every forecast a genuine real-time forecast and makes every comparison paired and logged.
*Effect:* implements PLAN §4. Engine and models are tested on synthetic data only (P28).

**P28: Validation of the forecasting machinery, synthetic only (ADOPTED (Isaiah, 2026-10-01)); Flag 12 open.**
Slow tier (`OFILT_SLOW=1`, run detached; results in `reports/C7_mc.json`, bands re-asserted by the default suite, staleness tied to code hashes):

| Check | Result | Band |
|---|---|---|
| CW size, nested null (b = 0), 300 reps, T_eval ≈ 1013 | **2.67%** (Wilson [1.36%, 5.17%]) | [2%, 9%] |
| CW power, b = 0.4, 200 reps | 100% (Wilson [98.1%, 100%]) | ≥ 80% |
| CW power, b = 0.25 (the B7b MDE80 level), 200 reps, informational | **89.5%** (Wilson [84.5%, 93.0%]) | none |

On the same 200 b = 0.25 panels, in-sample H1 on the last 1013 dates has power 87.5% two-sided and 94.0% one-sided. The two tests agree in 170 of 175 H1-significant runs (`reports/C7_h1_same_dgp.json`).

Default suite:
- Pesaran–Timmermann size: 4.6% (1000 independent sign series; band [3%, 7%]).
- Look-ahead perturbation: predictions on dates ≤ τ are bit-identical when all later targets and features are replaced by noise (M1–M5, and M7 with M1). A block-level leak is caught.
- M7: positive OOS R² on a planted nonlinear signal; mean OOS R² −0.011 on pure noise.
- Permutation importance ranks the planted feature first, with the noise column near 0.

**Flag 12 (open; decided with Flag 10 at the Pass 4 freeze; currently option (i), keep as is):** CW under expanding estimation is conservative here (2.67% at nominal 5%), which costs power but not validity.
*Reason:* these are the properties the confirmation run relies on, checked on data with known truth before any real forecast exists.
*Effect:* the synthetic Gaussian results are not the binding numbers. Pass 4 repeats the size and joint (H1, CW) checks on dev-calibrated draws (P35).

---

*Part 3 (D3): P29–P35.*

**P29: Blinding architecture (ADOPTED (Isaiah, 2026-10-01)).**
- **Rule.** No computation whose output relates FX columns (`usdjpy_*`, `eurusd_*`, derived FX features) to target columns (`y_*` and anything built from them) is run on real data, with exactly one exception (below). Allowed on real data: hashes, schema checks, predictor-only statistics, and the target-only hedge statistics of A7.
- **Tag gates** (`blind.require_unblinded`, called first by every public entry point that touches a target). Provenance comes from `df.attrs` or an explicit kwarg, and the two must agree.

  | Provenance | Requirement |
  |---|---|
  | `synthetic` | passes, subject to the fingerprint check below |
  | `dev_real` | `spec-dev-v1` must be an ancestor of HEAD |
  | `confirm_real` | `spec-dev-v1` **and** `prereg-v1` must be ancestors of HEAD |
  | missing or unknown | refused (fail closed) |

  `io.load_confirm` is gated by `prereg-v1` and logs every attempt. In this repo the gate falls back to `_guards_fallback.py`, which fails closed; reconciling it with `ofilt.guards.check_access` happens at merge (Flag 5).
- **The one exception: the sealed blind fit** (`sim._sealed_blind_fit`; Flag 8, option (i)). Every condition is tested:
  - (a) one private function regresses the real target on the FULL primary design;
  - (b) the coefficient vector exists only in local scope and is never returned, printed, logged, stored or attached to any object (AST-checked);
  - (c) it returns exactly {residuals, fitted control component (FE + controls, no FX), row index};
  - (d) the simulator output (`DevCalibrator` draws: stationary-bootstrap whole dates, y_sim = fitted controls + b_sim·e + a₂,sim·eur + residuals) contains no real target column and passes the fingerprint guard;
  - (e) every call is recorded.

  The residuals and fitted controls do not depend on b, so the simulator cannot leak the real b. Blinding is procedural, not cryptographic: recovering b would need the real y itself.
- **Opt-in.** A real-data sealed fit runs only with `OFILT_RUN_SEALED=1`. Without it the function refuses **before** logging, and `tools/checkpoint.sh` unsets the variable.
- **Record.** `BLIND_FIT_LOG` (committed) gets one JSONL line per executed call. **dev_real lines: 6, all legitimate:** lines 1–3 from the B5 real-data sealed-fit tests (`test_sim_b5`, run with `OFILT_RUN_SEALED=1`); lines 4–5 from `tools/report_B7.py` (line 4's process was killed before producing any output); line 6 from `tools/report_B7b.py`. All six are on `panel_dev.csv`. No further real sealed fit is sanctioned until Pass 4.
- **Fingerprint check (FROZEN).** A row-aligned (date, ticker, mantissa) registry of real target values is checked against frames labelled synthetic. It is a safety net against mislabelling, not an adversarial defence (Flag 2); the real protection is the tag gates, the allowlist (P20) and the forbidden target names.
- **Stage C** ran every forecasting model and test on synthetic panels only (P28).

*Reason:* the specification and every tool were written without seeing any relation between FX and the target in real data. That is what makes the later tags meaningful.
*Effect:* the pre-registration discloses the six sealed fits, what each returned, and that no FX coefficient on real data has been computed or seen in Pass 1.

**P30: Power statement (ADOPTED as PREVIEW (Isaiah, 2026-10-01); binding run in Pass 4).**
B7b PREVIEW: one sealed fit; dev-calibrated draws at T = T_conf = 1013; DK lag 6.

| Quantity | Result |
|---|---|
| H1 size at b = 0 (5000 reps) | **6.04%** (Wilson 95% MC [5.41%, 6.73%]); no flag under the AM-02 rule |
| H3 size | 5.92% |
| Pooled H1 coverage | 93.91% (DK SE/sd 0.960, bias ≈ 0) |
| H1 power at b = 0.10 / 0.25 / 0.40 (1000 reps each) | **22.5% / 78.2% / 98.5%** |
| **MDE80** | **b = 0.257** at T = 1013 (probit interpolation, cross-checked) |

- The MDE is in units of b: session log return per unit of overnight log USD/JPY return. It replaces PLAN §5's rough minimum detectable correlation (≈ 0.088). A null H1 is interpreted against MDE80 and, once the SESOI exists, through TOST (P23), never as "no effect".
- **Forecast test (synthetic, C7c):** CW power 89.5% at b = 0.25 on Gaussian synthetic panels. That is not comparable with the 78.2% above, which comes from a different DGP. On a common DGP, H1 and CW agree in about 97% of H1-significant runs (P28).
- **Interim wording (verbatim):** "H1 and the CW forecast test may disagree; disagreement is not by itself evidence against H1. The expected joint behaviour is quantified in Pass 4."
- **Binding:** the size, power and MDE numbers are re-run on the Pass 2 rebuild (1306 hedge) in Pass 4 (P35 T1, T2). The preview numbers are not used for any decision except advance notice.

*Reason:* power at plausible effects is limited (PLAN §5). Stating the MDE in the estimand's own units, from simulations that keep the real residual dependence, makes a null result interpretable.
*Effect:* supersedes PLAN §5's table. The pre-registration reports the binding version.

**P31: Flag 10 note: a simulation-calibrated critical value is a Pass 4 option (OPEN; decided jointly with Flag 12 at the Pass 4 freeze).**
Under dev-calibrated dependence, DK SEs slightly understate dispersion at confirmation length: SE/sd 0.954 at T = 983 and 0.960 at T = 1013, which puts H1 size near 6%. AM-02 remains the decision mechanism: if 5000 reps fall outside [3.5%, 6.5%], primary inference switches to a stationary block bootstrap. If the true size is 6.04%, a 5000-rep binding run exceeds 6.5% by MC noise alone with probability 0.086; at the preview interval's top (6.73%) the probability is 0.742.
- **Option, not adopted:** replace the normal critical value by the dev-calibrated null distribution's quantile. That option is decided together with Flag 12, where CW is conservative (2.67% at nominal 5% on synthetic panels).

*Reason:* both flags concern finite-sample calibration of a pre-registered test, so they should be decided by one rule, before the relevant tag, without outcome information.
*Effect:* none until Pass 4.

**P32: Prior-exposure disclosure and claim wording (ADOPTED (Isaiah, 2026-10-01)).**
- **Prior exposure (disclose in the pre-registration):**
  - Math 86 (January 2023 – March 2026) and the M1 rebuild examined overnight FX → the opening **gap** inside what is now the confirmation period, so confirmation is not fresh for gap questions. That is why f is confirmatory for 2022 only (P24).
  - The relationship between FX and the **open→close** drift (H1, H3) has never been examined on any data.
  - Pass 1 ran six sealed fits whose FX coefficients were never computed into any output (P29).
- **What b ≠ 0 licenses.** Overnight USD/JPY partly carries overnight Japan-equity news: it co-moves with overnight risk sentiment and Japanese equity futures. So a significant b shows only that information correlated with the overnight USD/JPY move is not fully priced at the 09:00 auction for these miners.
  - An **exposure** claim (the miners' FX exposure is what is mispriced) additionally needs a control for overnight Japan-equity news, i.e. a Nikkei proxy (P34; availability unverified).
  - A **cascade** claim (the indirect dollar → metals → miner channel is underweighted) additionally needs H3 (a₂ ≠ 0 in the predicted direction, P15) and the metals evidence (the COPX control and its robustness rows, plus XAU as robustness).
  - Without these, the wording is limited to "overnight USD/JPY predicts session drift".

*Reason:* the confirmatory test identifies b, not its channel. The claim wording must not outrun the identification.
*Effect:* PLAN §1.4 and the write-up use these three tiers (predicts / exposure / cascade).

**P33: Pre-listed robustness rows (ADOPTED (Isaiah, 2026-10-01)); anything else is labelled exploratory.**
From spec `robustness`, each reported next to the primary:

| Row | Content |
|---|---|
| Tails and influence (P22) | Huber (c = 1.345, fixed MAD scale); winsorised FX; date-level influence curve, k = 0 … 20 |
| `beta_rolling_250` | rolling past-only β instead of expanding |
| `raw_target` | raw open→close (also the secondary target, with the decomposition, P18) |
| `copx_to_fcx` | FCX replaces COPX |
| `ewj_yen_denominated_REQUIRES_PASS2` | yen-denominated EWJ added (needs US-session USD/JPY) |
| `exclusion_d_plus_2` | D, D+1, D+2 exclusion; β stays estimated under the primary exclusion (Flag 3) |
| `exclude_audit_flag` | outcome-identified audit dates removed (P08: robustness only) |
| `exclude_boj_day`, `exclude_sq_major` | BoJ announcement days / major SQ days removed (P19) |
| `post_2024_11_05_indicator_CONFIRMATION_ONLY` | indicator for dates from 2024-11-05 |
| `per_ticker_slopes_holm` | per-stock b with Holm across the three (H4) |

- **`post_2024_11_05_indicator`:** from 2024-11-05 the TSE close moved to 15:30, so the session is 30 minutes longer and the dark window 30 minutes shorter. **Form (Isaiah, 2026-10-01):** main effect + interaction with `usdjpy_ret`, with post = 1[date ≥ 2024-11-05], i.e. the P14 design plus `post` and `usdjpy_ret × post`. Report b_pre = the coefficient on `usdjpy_ret`, and b_post = b_pre + the coefficient on `usdjpy_ret × post`, with its DK SE from the covariance of the two. This is a robustness row only, outside the Holm family (P25). It is confirmation-only by construction: the development sample ends in 2021, so `post` is identically 0 there. *Implementation:* not yet in `inference.py`; it is added with the confirmation script before `prereg-v1`, and tested on synthetic data in the P13(b) dry run.

Relation to PLAN §6:
- items 1, 2, 4, 5, 7 and 9 are kept as the rows above;
- item 3 (named crisis windows) is removed (P22);
- item 6 (winsorised target) is replaced by Huber plus winsorised FX;
- item 8 (long-window interactions) moved to the secondary family (P25).

*Reason:* a closed list keeps the robustness section from becoming a garden of forking paths.
*Effect:* supersedes PLAN §6.

**P34: Pass 2 data plan (PLANNED (Isaiah, 2026-10-01)).**
Every pull is capped at **2026-03-05**; the forward holdout (P13a) is untouched until `prereg-v1`.
1. **Session FX 09:00 → close** (USD/JPY, EUR/USD; Dukascopy, same conventions). These are post-open columns for the mechanism extension (PLAN §9 item 2), schema group CONTEMPORANEOUS, and are never pre-open features.
2. **US-session USD/JPY** (the NY open → close span of each US session in the window). Needed for the yen-denominated EWJ row.
3. **1306 daily OHLC** (source to be confirmed; if Bloomberg, the same adjustment settings as Book2), with a split/dividend check and an open-auction timing check. This feeds the hedge switch with its fallback (P18) and the A7 rerun on 1306 (P18).
4. **Index-staleness test** of the TOPIX index's 09:00 print against 1306's auction price. It supports the P18 reason and the staleness caveat in the fallback.
5. **Flag 6 fix:** dividend-adjust the hedge legs of `gap_abn` and `cc_abn`, including 1306's own ex-date, or compute f on the raw target (decided in Pass 2).
6. **Gotobi flag:** a calendar flag for Tokyo gotobi fixing days (dates ending in 5 or 0, plus month-end), predictor-only. **[VERIFY]** the holiday-roll convention.
7. **Optional Nikkei proxy** (an overnight Nikkei CFD or futures series). **[VERIFY]** source, licence and timestamps before use. It enables the exposure-claim control (P32).
8. **XAU (gold) robustness only:** USD gold over the dark window, as a metals-channel robustness row.
9. **Rebuild and hashes.** `build_panel.py` is rerun. The sealed panel's hash changes and supersedes `9c18a6c1…` in the spec. The new sealed file is written and hashed without being read.
10. **Calendar cross-check.** `calendar.confirmation_calendar()` (1,019 days; T_conf = 1013) is compared with the rebuilt sealed panel's **date column only**.

*Reason:* each item serves a decided entry (P18, P19, P24, P32, P33) or a robustness row. None is chosen on outcomes.
*Effect:* after Pass 2, A7 and the B7b preview are rerun, the spec's hashes are updated, and the calibration pass (P35; P36 step 3) can start.

**P35: Pass 4 plan (PLANNED (Isaiah, 2026-10-01)).**
This is the **calibration pass**, step 3 of P36 (called "Pass 4" in earlier entries and in the spec's size rule). Each task is decided by a stated rule while dev is still blinded, before `spec-dev-v1` (P36).
- **T1. Binding size run (AM-02):** 5000 dev-calibrated sims at T_conf = 1013 on the rebuilt panel. If the rate lies in [3.5%, 6.5%], keep DK + normal; otherwise use a stationary block bootstrap (mean block 5).
- **T2. Binding power and MDE80** (the B7b design on the rebuilt panel). Reported in the pre-registration (P30).
- **T3. Joint (H1, CW) distribution (Isaiah, 2026-10-01):** dev-calibrated draws at b ∈ {0, 0.10, 0.25}, in the **confirmation structure**. CW's walk-forward trains on a dev-length history and evaluates on T_conf dates; H1 is estimated on the T_conf dates only, from the same simulated series. The pre-registration states the resulting cross-tab (both significant / H1 only / CW only / neither). Implementation note: `walk_forward` runs on DevCalibrator draws with target `y_sim` and masks all False.
- **T4. Flags 10 and 12, jointly:** keep the normal reference, or use simulation-calibrated critical values for H1 and CW (P31).
- **T5. Cost model → SESOI → TOST viability** (P23). Uses the TSE tick-size schedule plus a stated spread, with the coarse early-dev price grids of 5706 and 5711 (Flag 4). It also fixes the economic evaluation's cost assumption and break-even.
- **T6. Flag 4 checks:** Huber and winsorisation behaviour on the coarse-grid stocks in early dev.
- **T7.** Every outcome of T1–T6 is written into the pre-registration (S4) before `prereg-v1`.

*Reason:* all of these are calibration or nuisance decisions. They must be made from simulations, costs and calendars, not from the real b.
*Effect:* the sealed-fit exception (P29) is used again for T1–T3, with Isaiah's explicit sanction, from one DevCalibrator if possible.

---

*Part 3b (D3b): P36.*

**P36: Pass sequencing and tag semantics (ADOPTED (Isaiah, 2026-10-01); resolves Flag 13).**
The order of work is fixed as follows. The two tags are the only unblinding events.
1. **Pass 1 complete:** merge `ofilt/drift/` into the real repo, reconcile `ofilt.guards` (Flag 5), and run the suite locally.
2. **Pass 2, data and rebuild:** the P34 items, the A7 rerun on 1306 (P18), the index-staleness test, the calendar cross-check, the Flag 6 fix, and new hashes.
3. **Calibration pass, with dev still blinded by the guard:** P35 tasks T1–T6 on dev-calibrated simulations via the sealed-fit exception (P29). That covers the binding AM-02 size run, the joint (H1, CW) cross-tab, Flags 10 and 12, and the SESOI with TOST viability. Each decision is written into the spec as an AM-xx amendment.
4. **Tag `spec-dev-v1`.** From this tag, the inference and calibration choices (estimator, SEs or critical values, the size-rule outcome, SESOI) are **LOCKED**. Any later change to them is a labelled deviation per P13(c).
5. **Dev first look (exploratory):** the primary, secondaries, robustness rows and forecasting ladder on real dev data, plus the P13(b) confirmation dry run on dev.
6. **Pre-registration S4** (prior-exposure disclosure, P32; advisor sign-off) → tag `prereg-v1`.
7. **Confirmation run, once;** the forward holdout later (P13a).

- **Tag semantics, as implemented (`blind.REQUIRED_TAGS`):** `dev_real` computations relating FX to targets need `spec-dev-v1`, and `confirm_real` needs `spec-dev-v1` and `prereg-v1`. Before step 4, the only real-data computation combining FX and targets is the sealed fit with its conditions (P29), so the calibration pass sees no real b.
- **Note 1: the dry run comes after the first tag.** The P13(b) dry run runs the confirmation script end to end on `panel_dev.csv` and therefore computes dev b. It belongs after `spec-dev-v1` (step 5), not in the calibration pass. Its synthetic half, recovering a known b, can run at any time.
- **Note 2: SESOI needs Isaiah's cost inputs before step 3.** The inputs are commission, MOO/MOC auction impact, the 1306 hedge leg, and short borrow. Without them, T5 cannot set the SESOI, and TOST viability (P23) cannot be decided before the lock.
- **Pass 3 needs no separate entry.** The calibration pass (step 3) is what earlier entries call "Pass 4"; this list supersedes any other pass numbering.

*Reason:* calibration and nuisance choices made after seeing real dev results would be a forking path. With this order every such choice is made blind, then locked by the tag the guard already enforces.
*Effect:* resolves Flag 13. PLAN.md §8 milestones are rewritten to this order (D4). AM-02's "decided before tag" means before `spec-dev-v1`.
