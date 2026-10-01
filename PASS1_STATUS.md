# PASS1_STATUS.md

## Progress
| stage | item | status | one-line result |
|---|---|---|---|
| setup | repo + spec | done | git repo, verbatim spec + read-only VERBATIM copy, checkpoint script; input hashes verified |
| A | A1 spec.py | done | loader/validator/typed accessors; TO_FILL refused; 10 tests pass |
| A | A2 schema.py | done | 9 explicit frozensets cover all 41 panel columns exactly once; allowlist + derived map + `select_features` production path; 14 tests |
| A | A3 io.py | done | hash-verified `load_dev`/event loaders; `load_confirm` guarded by `prereg-v1` (raises here), logs every attempt; fallback guard fails closed; 8 tests |
| A | A4 blind.py | done | `require_unblinded` tag gate (dev_real: spec-dev-v1; confirm_real: + prereg-v1) + real-target fingerprint registry; threshold set after measuring tick-grid collisions (gap cols 21.9%); 13 tests |
| A | A5 targets.py | not-started | |
| A | A6 fill TO_FILL | not-started | |
| A | A7 hedge report | not-started | |
| A | A8 Stage A tests | not-started | |
| B | B1-B7 | not-started | |
| C | C1-C7 | not-started | |
| D | D1-D6 | not-started | |

## Next action
**A5**: write `ofilt/drift/targets.py`: past-only beta (expanding min 250 / rolling w on the last w eligible rows; eligible = non-excluded (earn_flag|news_flag == 0) with finite y and hedge; per ticker; ffill over all rows then shift(1) so beta_t uses eligible rows dated <= t-1; works on any concatenated panel so it "continues across samples"); `abn_oc`, `raw_oc`, `cc_abn`, `cc_raw` (same lagged beta, so delta_cc = delta_gap + b exactly); `excl_d2` (D..D+2 for TANSHIN+STANDALONE_NEWS from `events_firm.csv` on the panel calendar); `excl_forecast_eval` (TANSHIN D,D+1 + news D+1 only); register constructed targets with `blind.register_real_values` when provenance is real, then re-measure gap-column collision rates against the enlarged registry (must stay < 0.33). Tests: consistency of D/D+1 rebuild with panel `earn_flag`/`news_flag`, D+2 superset, eval mask subset, beta hand-check on synthetic, attrs preserved.

## Decision log (things decided mid-build, not re-derivable from the prompt alone)
- Repo = git repo at `/home/claude/ofilt_pass1`; the tarball includes `.git` so commits persist. Claude never creates tags `spec-dev-v1` or `prereg-v1` in this repo; guard tests use throwaway temp repos.
- `tools/checkpoint.sh "<item>"` runs tests, commits, mirrors to `/mnt/user-data/outputs/ofilt_pass1/`, tars `ofilt_pass1.tar.gz`. Resume: `tar -xzf ofilt_pass1.tar.gz -C /home/claude/`.
- `spec/analysis_spec_dev_v1.VERBATIM.yaml` is a read-only byte copy of the §3 spec; a test proves the live spec differs from it only on lines that contained `TO_FILL`.
- `spec.py` pins operational strings to the implemented values (estimator, se, kernel, lag_rule, small-sample=none, reference=normal, two-sided, CW M3-vs-M2 one-sided, permutation/date/noise importance, M7 early_stopping=false); rejects unknown/missing top-level keys and any `M6`. A YAML edit therefore cannot silently diverge from code.
- `spec.value(path)` refuses `TO_FILL` anywhere inside the requested subtree; `spec.raw(path)` is the unchecked accessor (validation/filling only). `sesoi()` raises `SpecPendingError` while `PENDING_COSTS`.
- (A2) `usdjpy_bars` stays in PROVENANCE as specified; it is permitted solely as the denominator of derived `rv_per_bar` (`PERMITTED_DERIVED_SOURCES = {usdjpy_bars}`); raw `usdjpy_bars` is refused as a feature (tested).
- (A2) Derived features (row-wise, no estimated parameters): `long_window` = 1[window_hours > 18], `jumpshare` = clip((rv-bv)/rv,0,1) with rv=0 -> 0, `rv_per_bar` = rv/bars, `e_pos`, `e_neg`, `no_us_session`. Estimated thresholds (rv_per_bar dev median; M4 expanding past median) are applied by the design builder/forecast engine, never in schema.
- (A2) `SYNTHETIC_FEATURES = {noise_N01}` (M7/importance calibration); must be supplied by the caller from a seeded RNG.
- (A2) `schema.select_features(df, cols)` is THE production path for model features (allowlist check, then build); the B1 design builder must use it. Ticker FE / one-hot are built from the `ticker` key by the design builder.
- (A2) A static test forbids pattern column selection anywhere in `ofilt/` (`filter(like=/regex=)`, `.str.startswith`, `startswith("ao_"|"y_"|...)`).
- TODO (A6, predictor-only): confirm normal dev nights have window_hours ≈ 17.983 and that `> 18` flags exactly the multi-night windows.
- (A3) Data dir defaults to `/mnt/project` (env `OFILT_DATA_DIR` overrides). `load_dev` returns rows sorted (date, ticker) with a fresh RangeIndex, ticker as str, and refuses schema drift (columns must equal the schema union), unexpected tickers, duplicate keys, and any date >= 2022-01-01.
- (A3) `load_confirm` has NO `repo=` parameter (it would let a caller point the guard at a throwaway repo holding a `prereg-v1` tag). The guard repo is the module constant `io._GUARD_REPO` (= repo root); tests patch it explicitly. The guard runs before any path is touched; every attempt appends one JSON line (utc, tag, DENIED/GRANTED, HEAD, guard used, caller, reason) to `ACCESS_LOG` at the repo root; tests patch that path.
- (A3) Guard choice: `ofilt.guards.check_access(tag)` if importable, else `_guards_fallback.check_access(tag, repo)`. Any exception from the external guard (including a signature mismatch) is a denial. Tag names must match `^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$`; resolution uses `refs/tags/<tag>^{commit}` so branches/HEAD expressions cannot satisfy it.
- (A3) Test invariant: while spec status is DRAFT, neither `spec-dev-v1` nor `prereg-v1` is an ancestor of HEAD in the main repo.
- (A4) `require_unblinded(df=None, *, provenance=None, arrays=None) -> str` (the `arrays=` mapping is an addition so numpy-input entry points can be fingerprint-checked). `synthetic` passes after the fingerprint check; `dev_real` needs `spec-dev-v1` ancestor of HEAD; `confirm_real` needs `spec-dev-v1` AND `prereg-v1`; missing/empty/non-str/unknown provenance raises; attrs vs kwarg conflict raises; non-DataFrame `df` raises. Guard selection mirrors io.py (external `ofilt.guards.check_access` if importable, any exception = denial; else fallback on `blind._GUARD_REPO` = repo root). Helpers: `mark_synthetic(df)`, `provenance_of(df)`.
- (A4) Fingerprint = set of 9-significant-digit decimal mantissas (sign- and power-of-ten-invariant) of finite nonzero values; mantissas with <= 5 significant digits are ignored (round prices, bar counts, grids). Registered at load: `y_oc`, `y_topix_oc` (via io hook, labels `dev_real:y_oc`, `dev_real:y_topix_oc`). Raw prices (`open/close/prev_close`) are NOT registered: integer prices are low-info and would false-positive against synthetic integer columns.
- (A4) Columns in `PRE_OPEN_FEATURES` are exempt from the check, because `oc_lag1`/`topix_oc_lag1` are lagged real targets and legitimately appear in dev-calibrated simulations (measured match 0.9998/0.9994). **B1 requirement:** the design builder must refuse any target column whose name is in the feature allowlist (closes the rename hole).
- (A4) Threshold MATCH_FRAC = 0.5, MIN_DISTINCT = 100 (changed from a first draft of 0.25/20 before checkpoint). Reason: exact tick-grid collisions -- measured fraction of distinct values matching the registry on dev: `ao_gap_adj` 0.219, `ao_gap_raw` 0.218, `ao_topix_gap` 0.002, all other non-exempt numeric columns 0; copies/subsets/rescalings ~1.0. A test pins gap-column fractions < 0.33.
- PLANNED (A5): close-to-close target for f uses the SAME lagged beta as the oc target: `cc_abn = (ao_gap_adj + y_oc) - beta_{t-1}*(ao_topix_gap + y_topix_oc)`, so the identity delta_cc = delta_gap + b holds exactly; `cc_raw = ao_gap_adj + y_oc` for the raw secondary. Rolling beta on non-excluded rows = last w eligible observations.
- PLANNED (B5) — critical for blinding: the blind residual fit must regress the target on the FULL primary design (FE + FX block + ticker-specific controls), discard the FX coefficients unseen, and return only residuals, the fitted CONTROL part (FE + controls, excluding FX), and the row index. Reason: if the fit used controls only, fitted+resid = real y, and a whole-date bootstrap keeps (y, e) pairs together, so y_sim at b_sim=0 would reproduce the real b. With the full-design fit, resid is orthogonal to e in-sample and y_sim = fitted_controls + b_sim*e + a2_sim*eur + resid* carries no information about the real b. Sim output must not contain real target columns (would trip the A4 fingerprint).

## Test results
| name | result | key number |
|---|---|---|
| test_blind (13 tests: dev_real raises in main repo; load_dev registers y_oc/y_topix_oc; synthetic passes incl. explicit kwarg/arrays; 9 fail-closed cases; attrs/kwarg conflict; mislabelled real panel raises (attrs and kwarg); bp-negated subset / percent / 2/3-real mix / arrays caught; real PRE_OPEN + bar counts + synthetic target pass; tick-grid collision margin; 50k t(5) false-positive rate; mantissa invariances; temp-repo tag gate incl. side-branch tag and prereg requirement) | pass | gap-col collision 0.219 < 0.5; t(5) false-positive frac < 1e-3 |
| test_spec (10 tests: load, verbatim-diff, accessors, TO_FILL refusal, sesoi pending, lag rule, 13 rejection cases) | pass | dk_lag(1708)=7, dk_lag(983)=6 |
| test_io (8 tests: dev load 5124 rows/1708 dates/str ticker/sorted; hash mismatch raises; events 163 rows by category + BoJ 98 + tampered-events raise; guard semantics in temp repo (ancestor/annotated/side-branch/missing/bad names/not-a-repo); main repo has no unblinding tags; load_confirm DENIED x2 logged; guard is the only gate (GRANTED in temp repo -> FileNotFoundError); no repo override param) | pass | load_confirm raises AccessDenied |
| test_schema (14 tests: disjoint groups, sizes 20/10/3/0, all 41 panel cols in exactly one group, unknown cols fail closed, every non-feature member refused, derived sources, derived values, production-path refusal, spec↔schema consistency, no pattern selection) | pass | 41/41 columns classified |

## Flags for Isaiah
1. (low, A2) `usdjpy_bars` is classified PROVENANCE, but `fx_x_highrv` and M4 need `usdjpy_rv/usdjpy_bars`. Handled by an explicit derived-feature allowance (decision log); no reclassification.
2. (low, A4) The fingerprint check is a mislabelling safety net, not adversarial-proof: it does not catch frames holding < 100 distinct real target values, nor real prices from which a target could be rebuilt. Real protection rests on the tag gate at every entry point, the feature allowlist, and the B1 target-name rule.
3. (low, A3) No `ofilt.guards` exists in this sandbox (fresh filesystem), so `_guards_fallback.py` will be used. When merging into the real repo, confirm the real `check_access` signature accepts a tag argument; the adapter fails closed (raises) on any signature mismatch.

## Blinding attestation
- A4: computed mantissa fingerprints of real `y_oc` and `y_topix_oc` (set of significands; no moments, no relations). Computed set-overlap fractions of every non-exempt numeric dev column against that set (diagnostic + tests): nonzero only for `ao_gap_adj` 0.219, `ao_gap_raw` 0.218, `ao_topix_gap` 0.002, `y_oc` 1.0, `y_topix_oc` 1.0; `oc_lag1` 0.9998 and `topix_oc_lag1` 0.9994 for the exemption rationale. FX return/RV/BV columns are exempt and were never overlapped against targets; FX provenance counts (`*_bars`, `*_stale_*`) were overlapped and are 0 (integer, low-info). Set membership only: no coefficient, correlation, or any target-FX quantity.
- SHA-256 of `panel_dev.csv`, `events_firm.csv`, `events_boj.csv` (all match spec).
- Read the panel header and dtype counts (3 rows, schema only). No statistics of any kind computed.
- A2 tests read the panel header only (`nrows=0`).
- A3: `load_dev` (hash, schema, key uniqueness, ticker set, date-scope check); A3 tests read row count, unique-date count, min/max date. `load_events_firm`/`load_events_boj` (hash, category counts, row counts). No statistics on any target or FX column.

## Deviations from the prompt
- None so far.
