# M2: the sign of the conditional EUR/USD coefficient a₂ (a blind derivation for the ofilt/drift study, 2026-10-08)

You are a mathematical-finance referee for Isaiah Choi's pre-registered study in this Project. Your one task is to derive PLAN §7's result **M2** and write it up as a note that can be committed before the study's development-sample run. You recommend; Isaiah decides, after a separate supervisor chat reviews your note. Accuracy beats speed. Work from first principles and check every step.

If the honest result is that the sign of a₂ is not determined, or is determined only under an assumption that cannot be checked before the data are seen, say so plainly. That is a valid and useful result. Do not choose or adjust assumptions in order to obtain a clean sign.

## 1. Blinding rules (absolute)
1. Never open, read, preview, grep, hash, list the contents of, load or search any data file: `panel_dev.csv`, `events_firm.csv` and `events_boj.csv` in `/mnt/project`, and any `.csv`, `.xlsx` or `.gz` file anywhere. If the interface attaches column names or row counts of such a file, ignore them.
2. Do not run or import any Project code (`build_panel.py`, `build_panel_p2.py`, `columns.py`, `events.py`, `make_events.py`, `pull_dukascopy.py`).
3. Do not use the `project_knowledge_search` tool, which can return data rows. Read Project files only with the file viewer or plain text tools, and only the passages listed in §2.
4. No web search. Literature you cite from your own knowledge is marked [UNVERIFIED].
5. State, estimate or calibrate no magnitude for these stocks, the TOPIX ETF or these FX series, whether from data or from memory of data. Work symbolically. Numerical checks use synthetic draws with parameter values you choose, labelled arbitrary.

## 2. What to read, and nothing else
In `/mnt/project`:
- `PLAN.md`, lines 69–137 (§1.2 to §1.4), 326–347 (§6) and 348–395 (§7).
- `DECISIONS_P14_onward.md`, lines 21–42 (P14, P15), 66–84 (P18, P19) and 296–335 (P32, P33).
- `DECISIONS_P37_onward.md`, lines 355–368 (P56).
- `DATA_DICTIONARY.md`, lines 30–40, 58–66 and 92–98.

Read nothing else in the Project. In particular, do not read the Math 86 PDF, any `P2_*` or `P3_*` file, `A_hedge_efficiency_1306*.md`, the `C7_*.json` files or any `*_STATUS*` file.

## 3. The setting (summarised from those passages; check it against them)
- **The firms.** Three Tokyo-listed non-ferrous miners: 5713 Sumitomo Metal Mining, 5711 Mitsubishi Materials and 5706 Mitsui Kinzoku. They sell dollar-priced metals and have yen costs.
- **The window.** The dark window runs from the previous Tokyo close (15:00 JST; 15:30 JST from 2024-11-05) to 08:59 JST on day t. The 09:00 opening auction then prices it.
- **The FX regressors.** `usdjpy_ret` and `eurusd_ret` are log returns over that window. Positive `usdjpy_ret` means the yen weakened; positive `eurusd_ret` means the dollar weakened. `xau_ret` is XAU/USD over the same window.
- **The US controls.** `spy_oc` and `copx_oc` (and `fcx_oc`) are sums of US-session open→close log returns inside the window, so they miss the hours outside the US session.
- **The target.** The primary target is abn_oc = y_oc − β̂·y_1306_oc: the stock's open→close return on day t, minus a past-only β times the open→close return of 1306, a TOPIX ETF. The raw target y_oc is a robustness row (`raw_target`).
- **The primary design (P14).** abn_oc = α_i + b·usdjpy_ret + a₂·eurusd_ret + s_i·spy_oc + c_i·copx_oc + ε. It has ticker fixed effects, the FX block common across tickers and the two controls ticker-specific, and is fitted by pooled OLS with Driscoll–Kraay errors. H1: b ≠ 0. H3: a₂ = 0, two-sided at 5%.
- **P15's algebra.** Write usdjpy_ret = γ·eurusd_ret + e^¥. Then the coefficient on the dollar-wide component is b^$ = bγ + a₂, and a₂ = 0 is the restriction that dollar-wide and yen-specific USD/JPY moves carry the same session drift per unit of USD/JPY. P15 says "the cascade model predicts a₂ ≠ 0".
- **P32's requirement.** The cascade claim (the indirect dollar → metals → miner channel is underweighted at the open) needs a₂ ≠ 0 **in the predicted direction**, plus "the metals evidence" (the COPX control and its robustness rows, plus XAU). No document yet states the direction.
- **The two metals robustness rows.**
  - `copx_to_fcx`: FCX replaces COPX, on the primary rows with a finite fcx_oc, reported with and without the swap on the same rows.
  - `xau_control`: adds xau_ret with ticker-specific slopes, on all primary rows, reported with and without it.
- **The decision your note informs** (the study's gap G9). The tier-(iii) criterion must be stated before the dev run. Either:
  - (a) H3's test with a direction, plus a stated requirement on `copx_to_fcx` and `xau_control`; or
  - (c) no tier-(iii) claim, with H3 and the metals rows reported without a tier-(iii) reading.
  
  Deferring the criterion until after the data are seen is not available.

## 4. What to derive
Build a minimal linear model and derive population (linear-projection) coefficients in closed form. Use the notation of PLAN §7 A′ where it applies (partial-adjustment shares ρ, fair-value loadings δ, signal-extraction weights k), and define every new symbol.

The model must contain at least:
- a dollar-wide factor, a yen-specific factor and a euro-specific factor, so that EUR/USD is an imperfect dollar proxy;
- dollar-priced metals with a dollar elasticity κ (κ's sign is one of your stated assumptions);
- the miners' channels: the translation of dollar revenue into yen, and the metals price, with operating leverage if it matters;
- pricing at the open: the auction prices a share of each channel's fair-value change, and the rest appears in the day's open→close return; the shares may differ by channel;
- COPX (and FCX) as a noisy view of the metals response that covers the US session only;
- SPY as the US equity control, and any other dollar-wide channel you judge material (global risk sentiment, for instance), with an argument for what SPY does and does not absorb;
- the hedge leg: 1306's own fair-value exposures to the same factors, including any non-dollar foreign revenue of the Japanese market, and its own pricing at the open. Take β as known and constant for the derivation, and say what changes when it is estimated.

Then derive and state, as numbered propositions with proofs:
1. **a₂ for the abnormal target.** Its value in the primary design, and its sign: exactly when the sign is determined under the cascade hypothesis, what it is, and what it is under the alternatives (the metals channel fully priced, or overweighted).
2. **a₂ for the raw target.** The same for the raw target, and the difference between the two targets.
3. **The κ condition.** When the dollar-wide pass-through (per unit of USD/JPY) and the yen-specific pass-through b have opposite signs, for both targets.
4. **The effect on b.** What the cascade channel does to b itself: whether any of it loads on usdjpy_ret, with what sign, and what that means for reading b's sign.
5. **The metals rows.** What the model predicts for a₂ in `copx_to_fcx` and in `xau_control` relative to the primary a₂ (the direction of change, and whether the sign is preserved), under the cascade and under its alternatives.
6. **P15's two statements.** Whether they hold in your model: that a₂ = 0 is the "common weight" auction, and that the cascade predicts a₂ ≠ 0. Report any disagreement; do not edit any document.

## 5. Numerical check
Write one Python script of your own (numpy only; no Project code, no data) that:
- draws synthetic samples from your model on a grid of parameter values, with a fixed seed;
- fits the primary design by OLS;
- compares every closed-form coefficient you derived with its simulated value.

Include cells where you predict the sign is determined and cells where you predict it is not. The script prints a table and the maximum absolute error. Its last line is `M2 CHECK: True` if every closed form matches within a tolerance you state in advance, otherwise `M2 CHECK: False`.

## 6. Criteria for tier (iii)
From your results, list the operational tier-(iii) criteria the derivation supports, as a lettered list, each mapped to the study's option (a) or (c). For each (a)-type criterion, give:
- what H3 must show (a two-sided rejection at 5% under the primary inference method, plus the sign);
- what `copx_to_fcx` and `xau_control` must show;
- whether `raw_target` must agree;
- the assumptions it rests on that cannot be checked before the data are seen.

Then recommend one, with reasons. If no criterion survives without such an assumption, recommend (c).

## 7. Deliverables
Create two files in `/mnt/user-data/outputs/` and present them.

**`P4_M2_note.md`**, with these sections:
1. Summary: the sign result and your recommended criterion, in a few sentences.
2. Assumptions, numbered.
3. Model.
4. Propositions and proofs.
5. The κ condition.
6. The metals rows.
7. Numerical check: the script's output table, and the script's name and SHA-256.
8. Criteria for tier (iii).
9. Limits.
10. Attestation: the files and line ranges you read, and that you opened no data file, ran no Project code, and used no web search and no `project_knowledge_search`.

**`P4_M2_check.py`**, the script.

**Format rules for both files**, because they may be committed to the study's repository:
- UTF-8, LF line endings, ending with exactly one newline;
- no triple backticks anywhere in the note (refer to the script by name, or indent code by four spaces);
- no real-data numbers;
- do not write the literal names of the study's git tags; say "the dev tag" or "the pre-registration tag".

**End your reply with:**
- the SHA-256 of each file;
- the check script's verdict line, as printed;
- a section headed "For the supervisor", containing:
  - the sign result, in one sentence;
  - your recommended criterion, in one sentence;
  - every place where you depart from, or question, a statement in the documents you read.
