# P4_CONFIRM_INF_SPEC: the confirmation module, inference rows (P4-4a; P4Q35)

Version 2, written by the supervisor chat that began on 2026-10-11, for P4-4a (P4Q34). Version 1 (SHA-256 `0605d405be56e901abe1ea4d35102851dfd260bc28c10307629764ef4b76097d`) was never committed: P4-4a's first run stopped at its step b.2 on row O6; §10 lists the changes. It specifies `ofilt/drift/confirm_inference.py` and its tests `tests/test_p4_confirm_inference.py`. P4-4a commits it as `docs/P4_CONFIRM_INF_SPEC.md`. A change after P4-4a is a new version of this file, recorded with its reason.

The module computes the 36 inference rows of the audit (`reports/P4_reports/p4_1_audit.md`, §1): O1 to O28 and R1 to R8. It also fixes the output document's schema for all 71 audit IDs, so that P4-4b (O29 to O45, R9) and P4-4c (R10 to R26) fill the rows left `pending` here. The texts it implements are the spec, its amendments, the audit and `docs/P4_CONFIRM_CONFIG.json` (version 1); where this file and those texts seem to differ, the builder stops and says where.

## 1. Rules for the code

### 1.1 Placement and imports
- One new module, `ofilt/drift/confirm_inference.py`, and one new test file, `tests/test_p4_confirm_inference.py`. No existing file changes, and no C7-hashed file changes (`inference.py`, `sim.py`, `forecast.py`, `fctests.py`, `models/linear.py`, `tools/c7_mc.py`).
- The module imports only `__future__`, `dataclasses`, `hashlib`, `json`, `math`, `typing`, `numpy`, `pandas`, and from the package `blind`, `calib`, `inference`, `targets` and `spec` (`Spec`, `REPO_ROOT`). It does not import `io`, `forecast`, `fctests`, `registry`, `models`, `sim`, `sim_full`, `calendar` or `schema`.
- It writes no file. Besides what `Spec.load` reads, it reads exactly one file, the configuration, with one `Path.read_bytes` call in `load_config`.
- It draws no random number. Its output is a deterministic function of its inputs.

### 1.2 Repository-wide static tests it must satisfy
- `tests/test_sim_b5.py`: the module never names the unguarded design core, in code, strings or docstrings. Every design comes from `inference.build_design` (or from the library functions that call it), and derived designs (§6) are made from `build_design`'s output.
- `tests/test_schema.py`: no column selection by prefix or pattern. Columns are named explicitly; ticker-specific names are built as `f"{column}:{ticker}"` from `TICKERS`.
- `tests/test_docs_d3b.py`: neither tag name appears in the module.
- `tests/test_docs_d6.py`: no file is written.

### 1.3 Read first (as text)
- `ofilt/drift/inference.py` in full; `targets.py` (`add_targets`, `add_masks`, `MASK_COLUMNS`); `calib.py` (`winsorise_fx`); `blind.py` (the provenance constants, `require_unblinded`); `spec.py` (the properties §7 uses).
- `docs/P4_CONFIRM_CONFIG.json` in full, and the audit's §1 rows O1 to O28 and R1 to R8.
- `ofilt/drift/sim_full.py` and `tests/test_p4_sim_full.py`, for the frames and the test conventions.
- P4-4p's report (`/tmp/p4_4p.txt`): the outcomes of every library call this module makes, on synthetic frames, including the exceptions of §5.

## 2. API

- `CONFIG_PATH = REPO_ROOT / "docs" / "P4_CONFIRM_CONFIG.json"`.
- `CONFIG_SHA256 = "5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd"`.
- `TICKERS = ("5706", "5711", "5713")`.
- `ROW_IDS`: the 71 audit IDs in the order of the configuration's `rows`.
- `ITEM_OF`: a dict from each ID to `"P4-4a"`, `"P4-4b"` or `"P4-4c"`: O1 to O28 and R1 to R8 are P4-4a's (36); O29 to O45 and R9 are P4-4b's (18); R10 to R26 are P4-4c's (17).
- `STATUSES = ("estimated", "not_estimable", "not_applicable", "fixed", "pending")`.
- `load_config(path=None) -> dict`: reads the bytes of `path` (default `CONFIG_PATH`); raises `ValueError` unless their SHA-256 is `CONFIG_SHA256` and the keys of the decoded `rows` are exactly `ROW_IDS`, in order; returns the decoded dict.
- `infer(dev, events, confirm=None, *, spec=None) -> dict`: the output document (§4). `spec=None` means `Spec.load()`.
- `encode_fraction(fr: dict) -> dict`: the plain-typed form (§4.3) of a dict that `inference.fraction_from` or `fraction_unpriced` returns: `f`, `se_delta`, `ci_delta`, `fieller` (`kind` and `ci`), `t_denominator`, `b`, `delta_cc` and `alpha`.
- `to_json(doc) -> str`: `json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=False) + "\n"`.

## 3. Frames and modes

### 3.1 Inputs
`dev` and `confirm` are frames shaped as `io.load_dev` returns a panel (the 60 schema columns, a RangeIndex). `events` is shaped as `io.load_events_firm` returns it. The inputs are never modified.

### 3.2 Provenance (checked first)
Before any other step, `infer` reads `attrs["provenance"]` of each frame and requires:
- without `confirm`: `dev` is `synthetic` or `dev_real`;
- with `confirm`: the pair (dev, confirm) is (`synthetic`, `synthetic`) or (`dev_real`, `confirm_real`).

Anything else raises `ValueError`. Then `blind.require_unblinded` runs on `dev` and on `confirm` (the events table carries no provenance and is not guarded). No step that computes or registers a target runs before these two checks.

### 3.3 The confirmation mode (with `confirm`)
- `J = pd.concat([dev, confirm], ignore_index=True)`, with `J.attrs = {"provenance": <confirm's provenance>}`.
- `T = targets.add_masks(targets.add_targets(J, spec), events, spec)`.
- `T250 = targets.add_targets(J, spec, method="rolling", window=250)` and `T500` with `window=500`.
- The inference frame `C` is the rows of `T` dated on or after the first date of `confirm`, with `C.attrs = dict(T.attrs)`. `C250` and `C500` are the same rows of `T250` and `T500`, attrs copied.
- The period frames: `C2022` is the rows of `C` dated from the configuration's `f.confirmatory.from` to `f.confirmatory.to`, and `C2326` those from `f.descriptive.from` to `f.descriptive.to`, attrs copied.

### 3.4 The dev mode (without `confirm`)
As §3.3 with `J = dev.copy()` (attrs kept) and `C` the whole of `T`. There are no period frames.

## 4. The output document

### 4.1 Top level
A dict with exactly these keys, in this order:
- `module` = `"confirm_inference"`; `spec_version` = 1; `config_sha256` = `CONFIG_SHA256`;
- `mode` = `"confirmation"` or `"dev"`; `provenance` = `J`'s provenance;
- `dates` = `{"first": ..., "last": ..., "n": ...}` of `C` (ISO dates, the number of distinct dates);
- `rows`: a dict with one entry per ID of `ROW_IDS`, in that order.

### 4.2 An entry
Exactly the keys `id`, `item`, `status`, `values`, `reason`, `n_rows`, `n_dates` and `lag`:
- `item` = `ITEM_OF[id]`; `status` is one of `STATUSES`;
- `values`: a dict for `estimated` and `fixed` entries, and for `not_estimable` and `not_applicable` entries that report a part (O7, R6, R7); otherwise `None`;
- `reason`: a string for `not_estimable` and `not_applicable`, else `None`;
- `n_rows`, `n_dates`, `lag`: the row count, the distinct-date count and the DK lag of the row's main fit, or `None` where there is none.

P4-4b's and P4-4c's entries are `pending`, with `values`, `reason`, `n_rows`, `n_dates` and `lag` all `None`.

### 4.3 Plain types
Every value in the document is a `str`, `int`, `float`, `bool`, `None`, list or dict (numpy scalars converted, tuples as lists, dates as `YYYY-MM-DD`). No number is NaN or infinite; `to_json` uses `allow_nan=False`.

The one place an infinite value arises is a Fieller set: `fraction_from` returns `kind` `"two_rays"` with `ci` ((−inf, lo), (hi, inf)), or `"real_line"` with (−inf, inf). `encode_fraction` writes each infinite endpoint as `None`, so `two_rays` becomes `[[None, lo], [hi, None]]` and `real_line` `[None, None]`; `kind` says which shape it is. A bounded set's `ci` is `[lo, hi]`.

### 4.4 A fit summary
For a parameter or contrast: `{"estimate", "se", "z", "p", "ci"}` from `Result.param` or `Result.contrast`, with `ci` a list of two floats.

## 5. Contingencies (P4Q31)

Every row is computed through one helper that applies these rules; the run never stops to ask.
- **No rows.** Before any `subset_design` or derived design, the row mask must keep at least one row. Otherwise the row is `not_estimable`, reason `"no rows"`, with `n_rows` 0, `n_dates` 0 and `lag` `None`. (`subset_design` with no row raises a numpy `ValueError`, not a `DesignError`; P4-4p.)
- **Design errors.** An `inference.DesignError` from a library call (no rows, rank deficiency, non-finite values, `rv_per_bar` undefined) makes the row `not_estimable`, with the error's message as the reason, and `n_rows`, `n_dates` and `lag` `None`.
- **Rank.** A derived design (§6) whose `X` has rank below its number of columns is `not_estimable`, reason `"rank-deficient design"`, with that design's row and date counts and `lag` `None`.
- **Non-finite results.** A reported estimate or SE that is not finite makes the row `not_estimable`, reason `"non-finite estimate"`. The infinite endpoints of a Fieller set are not results of this kind (§4.3).
- **Holm.** A member of a Holm family that is not estimable enters with p = 1, so the family size is unchanged (R6, R7). `inference.holm` is applied to the family's p-values.
- **Undefined ratio.** f is undefined when δ_cc is zero or not finite: the period's `f_defined` is `False` and its `f`, `se_delta`, `ci_delta`, `fieller` and `t_denominator` are `None`; `fraction_unpriced` is not called.
- **Rows built on the primary fit.** If D0 or r0 is not estimable, R3, R4 and every row of §7 that uses D0 or r0 is not estimable with D0's or r0's reason.
- Any other exception propagates: it is a bug, not a contingency.

## 6. Derived designs (the audit's §3; P4Q2)

- **Base.** `D0 = inference.build_design(C, spec)` and `r0 = inference.fit_dk(D0, spec)`: the primary design and fit.
- **Row masks.** A mask over a design's rows reads frame values at `design.index` (`frame.loc[design.index, column]`). Comparisons with a missing value are False.
- **Restriction.** After the no-rows check, `inference.subset_design(design, mask)`.
- **Appending a column.** `dataclasses.replace(design, X=np.column_stack([design.X, *new]), names=design.names + tuple(new_names))`, then the rank check of §5.
- **Replacing columns.** The named columns are removed from `X` and `names`, then the new columns appended.
- **Ticker-specific column.** For a column `c`: for each `t` of `TICKERS`, `c` times `1[ticker == t]`, named `f"{c}:{t}"`.
- **Common column.** One column, named by the column itself (or by `f"{a}:{b}"` for the product of `a` and `b`).
- **Fit.** `inference.fit_dk(design, spec)`, so the DK lag follows the spec's rule at that design's T.
- **With and without on the same rows** (R8): `without` is the fit of the restricted base design, `with` is the fit of the derived design on the same rows, and `primary` is r0's summary. `values` holds `name`, `primary`, `with`, `without` (each the H1 summary), `dropped_rows` and `dropped_dates` (against D0), and the entry's `n_rows`, `n_dates` and `lag` are the `with` fit's.

## 7. The rows

H1 = `spec.h1_parameter` (`usdjpy_ret`). "Summary" is §4.4's. `cfg` is the loaded configuration.

| ID | Status and values |
|---|---|
| O1 | Estimated: `{"param": H1, "fit": summary of H1 in r0}`; n_rows, n_dates and lag of r0. |
| R1 | Fixed: `{"target": "abn_oc", "beta": C.attrs["targets"]}` (as plain types). |
| R2 | Estimated: `{"exclusion_flags": list(spec.inference_exclusion_flags), "require_nonmissing": list(spec.require_nonmissing), "rows": len(D0.y), "dates": D0.T, "dates_all_excluded": <the dates of C with no row in D0>, "t_conf_expected": cfg["frame"]["confirmation"]["t_conf"], "matches_t_conf": D0.T == t_conf_expected}`. In the dev mode the last two are `None`. |
| R3 | Fixed: `{"rule": "Bartlett kernel, L = floor(4 (T/100)^(2/9))", "T": D0.T, "lag": r0.lag}`. |
| R4 | Estimated: `{"alpha": spec.alpha, "p": <O1's p>, "reject": p < alpha}`; not estimable, with O1's reason, if O1 is. |
| R5 | Fixed: `{"method": "DK-normal", "decision": "D3.4"}`. |
| O2 | Estimated: `{"param": "eurusd_ret", "fit": summary of eurusd_ret in r0}`. |
| O3 to O6 | One per member of `inference.SECONDARY_TERMS`, in order (O3 `fx_x_longwindow`, O4 `fx_x_jumpshare`, O5 `fx_x_highrv`, O6 `fx_asymmetry`): `D = build_design(C, spec, secondary=term)`, `r = fit_dk(D, spec)`; `{"member": term, "tested": summary of r.contrast(inference.SECONDARY_TESTED[term])}`, plus, for O3 to O5, `"h1"`: the summary of H1. O6's design replaces `usdjpy_ret` by `e_pos` and `e_neg`, so O6 has no `"h1"` and holds instead `"e_pos"` and `"e_neg"`, their summaries. |
| R6 | Estimated: `{"members": ["O3", "O4", "O5", "O6"], "p": [...], "p_holm": [...], "not_estimable": [...]}`, with p = 1 for a not-estimable member. |
| O7 | Confirmation mode: `values = {"confirmatory": P(C2022), "descriptive": P(C2326)}`, where P(F) is: `J = fit_joint(F, spec)`, `b, d, V = J.pair(H1)`, and, when δ_cc = d is defined, `encode_fraction(fraction_unpriced(J))`; P(F) holds `status` (`"estimated"` or `"not_estimable"`), `reason`, `from`, `to`, `b`, `delta_cc`, `f_defined`, `f`, `se_delta`, `ci_delta`, `fieller` (`{"kind", "ci"}`), `t_denominator`, `n_rows` (J.n), `n_dates` (J.T) and `lag`. The entry is `estimated` if the confirmatory part is, else `not_estimable` with its reason; n_rows, n_dates and lag are the confirmatory part's. Dev mode: `values = {"dev_stand_in": P(C)}`, where P(C) also holds `"label": "dev stand-in"` (P4Q10), and its `from` and `to` are C's first and last dates. |
| O8 | Confirmation mode, fixed: `{"confirmatory": [from, to], "descriptive": [from, to], "disclosure": cfg["f"]["disclosure"]}`. Dev mode: not applicable, reason `cfg["f"]["dev"]["periods"]`. |
| O9 | Estimated: `inference.decomposition(C, spec)` as a dict of floats. |
| O10 | Estimated: `tost_result(r0, H1, spec, sesoi=cfg["constants"]["sesoi"]["primary"])`: `p`, `p_lower`, `p_upper`, `equivalent`, `ci`, `sesoi`, `alpha`. |
| O11 | Estimated: `{"low": ..., "high": ...}`, the same at the low and high SESOI. |
| O12 | Estimated: summary of H1 in `fit_huber(D0, spec)`. |
| O13 | Estimated: `W = calib.winsorise_fx(C, spec)`; summary of H1 in `fit_dk(build_design(W, spec), spec)`. |
| O14 | Estimated: `inference.influence_curve(D0, spec)` with the default `k_max`: `{"curve": [one dict per row: k, date_removed (ISO or None), b, se, z, p, n_dates, lag]}`. |
| O15 | `beta_rolling_250`, with and without: `Dr = build_design(C250, spec)`; the mask keeps D0's rows whose index is in `Dr.index`; `without` is D0 on them; `with` is Dr restricted to the same index labels. |
| O16 | `beta_rolling_500`: as O15 with `C500`. |
| O17 | `raw_target`: as O15 with `Dr = build_design(C, spec, target="raw_oc")`. |
| O18 | `copx_to_fcx`: mask: `fcx_oc` finite; derived: `copx_oc:<t>` replaced by `fcx_oc:<t>` (ticker-specific). |
| O19 | `ewj_yen_denominated`: mask: `ewj_oc_jpy` finite; derived: ticker-specific `ewj_oc_jpy` appended. |
| O20 | `xau_control`: mask: `xau_ret` finite; derived: ticker-specific `xau_ret` appended. |
| O21 | `nikkei_proxy_p42`: mask: `n225_stale_start_min ≤ 5` and `n225_stale_end_min ≤ 5` and `n225_ret` finite (a night with no Japan 225 record is ineligible); derived: ticker-specific `n225_ret` appended. `values` also holds `eligible_dates`: the number of distinct dates of C on which the mask holds, before the exclusions and the primary's non-missing requirements. |
| O22 | `mechanism_session_fx_gotobi`: mask: `c_usdjpy_sess_ret`, `c_eurusd_sess_ret` and `gotobi_day` finite; derived: common `c_usdjpy_sess_ret`, `c_eurusd_sess_ret`, `gotobi_day` and `usdjpy_ret:gotobi_day` appended. `values` also holds `coefficients`: the summaries of those four in the `with` fit. Descriptive, outside every claim tier and Holm family. |
| O23 to O26 | Own estimates: `D = build_design(C, spec, exclude=list(spec.inference_exclusion_flags) + [extra])` with extra `excl_d2` (O23 `exclusion_d_plus_2`), `audit_flag` (O24), `boj_day` (O25) and `sq_major` (O26). `exclude` replaces the spec's flags (P4-4p), so they are always passed with it. `values`: `name`, `excluded_columns`, `fit` (summary of H1), `primary`. |
| O27 | `post_2024_11_05_indicator_CONFIRMATION_ONLY`: derived from D0 by appending common `post` = 1[date ≥ `cfg["constants"]["post_break_date"]`] and `usdjpy_ret:post`. `values`: `b_pre` (summary of H1), `interaction` (of `usdjpy_ret:post`), `b_post` (summary of the contrast with weights 1 on both), `primary`. Outside the Holm family. Dev mode: not applicable, reason `cfg["robustness"]["post_2024_11_05_indicator_CONFIRMATION_ONLY"]["on_dev"]`. |
| O28 | `per_ticker_slopes_holm`: derived from D0 by replacing `usdjpy_ret` and `eurusd_ret` with their ticker-specific versions (P4Q15). `values`: `slopes` = {ticker: summary of `usdjpy_ret:<t>`}, `primary`. |
| R7 | Estimated: `{"tickers": TICKERS, "p": [...], "p_holm": [...]}` across O28's three p-values; p = 1 for each if O28 is not estimable. |
| R8 | Fixed: `{"rule": cfg["robustness"]["reporting_form"]["with_and_without_rule"], "rows": ["O15", ..., "O22"]}`. |

## 8. Tests (`tests/test_p4_confirm_inference.py`: exactly these 23)

### 8.1 Seeds, scenarios and frames
- Seeds are S_k = `Spec.load().seed` + 8,100,000 + k, with k as listed: a block disjoint from every earlier one (P4-3's tests + 8,000,000 + k, P4-4p + 8,500,000 + k, both with k below 1,000).
- Scenarios of `sim_full`: **SA** = `Scenario(b=1.0, a2=0.6, delta_cc=1.5)`; **SB** = `Scenario(b=1.0, delta_post=-1.0, a2=0.6, delta_cc=1.5)`; **SC** = `Scenario(b=1.0, a2=0.6, delta_cc=1.5, c_usd_sess=0.5, c_eur_sess=-0.3, b_gotobi=0.4)`; **SD** = `Scenario(b=1.0, b_spread=(-0.3, 0.1, 0.2), a2=0.6, delta_cc=1.5)`; **SZ** = `Scenario()`; **SN** = `Scenario.not_estimable()`. In "(S_k, X)", S_k is the seed and X the scenario.
- Unless a test says otherwise, `doc = infer(out.dev, out.events, out.confirm)` with `out = sim_full.simulate(S_k, scenario)`. Documents and frames may be cached at module level. The file runs in under 180 s.
- "Recovers x" means |estimate − x| ≤ 5 · se, both from the entry.
- "Matches" means equal to the library call on the same inputs, exactly (floats compared with `==`).
- The tests never pass a frame labelled `dev_real` or `confirm_real` through a valid pair (§3.2), so no synthetic value is ever registered as real.

### 8.2 Where an expected value comes from
Expected row masks and counts are recomputed in the test from `C` and D0, which the test builds as §3.3 and §6 say, independently of the module's internals.

### 8.3 The 23 tests
1. `test_config_pin_and_refusal`: the file at `CONFIG_PATH` has SHA-256 `CONFIG_SHA256`; `load_config()` returns its decoded content; a copy with one byte changed, in a temporary folder, raises `ValueError`; the decoded `rows` keys are `ROW_IDS`.
2. `test_row_ids_and_items`: `ROW_IDS` has 71 distinct IDs; `ITEM_OF` gives 36 to P4-4a, 18 to P4-4b and 17 to P4-4c, exactly as §2 lists them.
3. `test_document_schema` (S0, SA): the top-level keys and their order; the rows in `ROW_IDS` order; every entry's keys; P4-4a's entries have a status other than `pending`; P4-4b's and P4-4c's are `pending` with every other field `None`.
4. `test_json_round_trip_and_determinism` (S1, SA): two `infer` calls give equal `to_json` text; `json.loads(to_json(doc)) == doc`; the text contains neither `NaN` nor `Infinity`. Also, `encode_fraction(inference.fraction_from(1.0, 0.05, V, 0.05))` with V = diag(0.01, 0.01) has `kind` `"two_rays"` and `ci` of the form `[[None, lo], [hi, None]]` with lo < hi, `encode_fraction(inference.fraction_from(0.01, 0.01, V, 0.05))` has `kind` `"real_line"` and `ci` `[None, None]`, and `json.dumps` of both with `allow_nan=False` succeeds.
5. `test_provenance_pairs_refused`: `ValueError` for (synthetic, `dev_real`), (synthetic, `confirm_real`), (`dev_real`, synthetic), a frame without provenance, and the dev mode with `confirm_real`; each raised before any target is built, so that `blind.registered_labels()` is the same before and after.
6. `test_inputs_unchanged` (S1, SA): `dev`, `confirm` and `events` are equal before and after `infer` (`pandas.testing`, exact), attrs included.
7. `test_primary_and_sample_rows` (S1, SA): O1 matches `fit_dk(build_design(C, spec), spec)` and recovers 1.0; O2 recovers 0.6; R2's `dates` is 1013, `dates_all_excluded` 6 and `matches_t_conf` True; R3's lag is 6; R4 rejects; R1, R3 and R5 are fixed.
8. `test_secondary_family_matches_library` (S1, SA): O3 to O6's tested summaries and R6's p and p_holm match `inference.secondary_family_tests(C, spec)`'s estimate, se, z, p and p_holm.
9. `test_secondary_family_not_estimable_member` (S2, SN): O5 is not estimable, its reason containing `rv_per_bar`; O3, O4 and O6 are estimated; R6's p has 1 in O5's place and its p_holm equals `inference.holm` of that list; `not_estimable` is `["O5"]`.
10. `test_fraction_unpriced_periods` (S1, SA; S3, SB): both periods are estimated with `f_defined` True; with SA both recover 1/1.5 (f against `se_delta`); with SB the confirmatory f recovers 1/1.5; each period matches `fraction_unpriced(fit_joint(F, spec))` on its rows; O8 is fixed with the configuration's periods.
11. `test_fraction_not_estimable_2022` (S2, SN): O7 is not estimable, its confirmatory part not estimable with a reason, its descriptive part estimated.
12. `test_decomposition_and_tost` (S4, SZ; S1, SA): O9 matches `decomposition(C, spec)`; with SZ, O10 is equivalent at the primary SESOI; O10 and O11 match `tost_result` at the three SESOIs, with SA.
13. `test_huber_winsorised_influence` (S1, SA): O12, O13 and O14 match the library calls of §7; O14's curve has 21 rows, k from 0 to 20, its first row's b equal to O1's estimate.
14. `test_rolling_beta_and_raw_rows` (S1, SA): for O15, O16 and O17, `with` and `without` have the same n_rows and n_dates, `without` matches D0 restricted to the same rows, `dropped_rows` equals len(D0.y) − n_rows, and both recover 1.0.
15. `test_fcx_ewj_xau_rows` (S1, SA): for O18, O19 and O20, n_rows equals the number of D0's rows where the masked column is finite, recomputed in the test; `with` and `without` have the same rows; both recover 1.0.
16. `test_nikkei_eligibility` (S1, SA): O21's n_rows equals the number of D0's rows meeting §7's mask, recomputed in the test; no date with a missing Japan 225 record is among them; both fits recover 1.0.
17. `test_mechanism_row` (S5, SC): O22's coefficients recover 0.5 (`c_usdjpy_sess_ret`), −0.3 (`c_eurusd_sess_ret`), 0.4 (`usdjpy_ret:gotobi_day`) and 0.0 (`gotobi_day`), and `with` recovers 1.0; its rows exclude exactly the session-missing dates' rows of D0.
18. `test_exclusion_rows` (S1, SA): for O23 to O26, n_rows equals len(D0.y) minus the number of D0's rows where the extra column is truthy, recomputed in the test, and is below O1's; each recovers 1.0; `excluded_columns` starts with the spec's flags.
19. `test_post_break_row` (S3, SB): O27's `b_pre` recovers 1.0 and `b_post` recovers 0.0; `b_post` matches the contrast of the derived design's fit.
20. `test_per_ticker_slopes_and_holm` (S6, SD): O28's slopes recover 0.7, 1.1 and 1.2 for 5706, 5711 and 5713; R7's p_holm equals `inference.holm` of the three p-values.
21. `test_not_estimable_preset_completes` (S2, SN): `infer` returns; O20 is not estimable with reason `"no rows"`; O22 is not estimable with reason `"rank-deficient design"`; every other P4-4a entry except O5 and O7 is estimated or fixed.
22. `test_dev_mode` (S1, SA): `infer(out.dev, out.events)` has mode `dev`; O1 recovers 1.0 on the dev dates; O7's `dev_stand_in` recovers 1/1.5; O8 and O27 are not applicable with the configuration's reasons; R2's `t_conf_expected` and `matches_t_conf` are `None`.
23. `test_module_source`, by `ast` on the module's source: imports only as §1.1 allows; no call of `open`, `read_csv`, `to_csv`, `write_text`, `write_bytes`, `to_parquet`, `to_pickle` or `to_excel`; exactly one call of `read_bytes`; none of the strings `load_dev`, `load_confirm`, `load_events` and `OFILT_DATA_DIR`; it defines `infer`, `load_config`, `encode_fraction`, `to_json`, `CONFIG_SHA256`, `CONFIG_PATH`, `ROW_IDS`, `ITEM_OF`, `STATUSES` and `TICKERS`, and `TICKERS` equals `sim.TICKERS` (imported by the test, not by the module).

## 9. Notes for the builder
- The probe (P4-4p) ran every library call of §7 on these simulator frames; its report shows their outputs, the DesignError messages of §5 and their run times (each well under a second).
- `secondary_family_tests` raises as a whole when one member is not estimable, so O3 to O6 are fitted one by one (§7). Test 8 checks that, when all four are estimable, the result is the library's to the last digit.
- If a test can pass only by departing from this file, or this file is wrong on a point a test depends on, stop and say which.

## 10. Changes from version 1

P4-4a's first run stopped at b.2 before writing any code: version 1 asked for the H1 summary in O6's design, where `fx_asymmetry` replaces `usdjpy_ret` by `e_pos` and `e_neg`, so `Result.param` raises a plain `ValueError`, which §5 lets propagate. This version:
- O3 to O6 (§7): O6 holds the summaries of `e_pos` and `e_neg` in place of `"h1"` (the builder's reading (b)).
- Writes in the builder's other readings of that run: O7's dev-mode `label`, `from` and `to` (§7); O21's `eligible_dates` (§7); `t_denominator` with the undefined ratio (§5); R4's reason and the rows built on the primary fit (§5, §7); the guard on `dev` and `confirm` only (§3.2); the counts of a not-estimable row (§5); the seeds of tests 4 and 6, and the scenario `Scenario()` renamed SZ so that S0 names only a seed (§8); R2's `dates_all_excluded` defined as the dates of C with no row in D0.
- Nothing else changes; no test asserts anything different.
