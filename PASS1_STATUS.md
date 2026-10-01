# PASS1_STATUS.md

## Progress
| stage | item | status | one-line result |
|---|---|---|---|
| setup | repo + spec | done | git repo, verbatim spec + read-only VERBATIM copy, checkpoint script; input hashes verified |
| A | A1 spec.py | done | loader/validator/typed accessors; TO_FILL refused; 10 tests pass |
| A | A2 schema.py | done | 9 explicit frozensets cover all 41 panel columns exactly once; allowlist + derived map + `select_features` production path; 14 tests |
| A | A3 io.py | not-started | |
| A | A4 blind.py | not-started | |
| A | A5 targets.py | not-started | |
| A | A6 fill TO_FILL | not-started | |
| A | A7 hedge report | not-started | |
| A | A8 Stage A tests | not-started | |
| B | B1-B7 | not-started | |
| C | C1-C7 | not-started | |
| D | D1-D6 | not-started | |

## Next action
**A3**: write `ofilt/drift/_guards_fallback.py` (`check_access(tag, repo=None)` raises unless `git merge-base --is-ancestor <tag>^{commit} HEAD` succeeds; fail closed on any git error) and `ofilt/drift/io.py` (`load_dev()` verifies SHA-256 vs spec, reads ticker as str, parses date, asserts all dates < 2022-01-01, sets `attrs['provenance']='dev_real'`; `load_confirm()` calls the guard with `prereg-v1` BEFORE touching any path, appends a line to `ACCESS_LOG`, must raise here; event loaders verify their hashes). Tests: hash-mismatch raise, load_confirm raise + log line, guard pass/fail in a throwaway temp git repo.

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
- PLANNED (A3): data dir defaults to `/mnt/project` (env `OFILT_DATA_DIR` overrides). `load_confirm` calls the guard before touching any path; `ACCESS_LOG` path is module-level and patched to a temp file in tests.
- PLANNED (A4): `require_unblinded` provenance values: `synthetic` passes; `dev_real` needs tag `spec-dev-v1` ancestor of HEAD; `confirm_real` needs `prereg-v1` too; missing/unknown raises. Explicit `provenance=` must agree with `df.attrs` when both present. Extra fail-closed check: real target values (y_oc, y_topix_oc, constructed targets) are fingerprinted at load/construction; a frame labelled `synthetic` whose column values substantially match a real fingerprint raises.
- PLANNED (A5): close-to-close target for f uses the SAME lagged beta as the oc target: `cc_abn = (ao_gap_adj + y_oc) - beta_{t-1}*(ao_topix_gap + y_topix_oc)`, so the identity delta_cc = delta_gap + b holds exactly; `cc_raw = ao_gap_adj + y_oc` for the raw secondary. Rolling beta on non-excluded rows = last w eligible observations.
- PLANNED (B5) — critical for blinding: the blind residual fit must regress the target on the FULL primary design (FE + FX block + ticker-specific controls), discard the FX coefficients unseen, and return only residuals, the fitted CONTROL part (FE + controls, excluding FX), and the row index. Reason: if the fit used controls only, fitted+resid = real y, and a whole-date bootstrap keeps (y, e) pairs together, so y_sim at b_sim=0 would reproduce the real b. With the full-design fit, resid is orthogonal to e in-sample and y_sim = fitted_controls + b_sim*e + a2_sim*eur + resid* carries no information about the real b. Sim output must not contain real target columns (would trip the A4 fingerprint).

## Test results
| name | result | key number |
|---|---|---|
| test_spec (10 tests: load, verbatim-diff, accessors, TO_FILL refusal, sesoi pending, lag rule, 13 rejection cases) | pass | dk_lag(1708)=7, dk_lag(983)=6 |
| test_schema (14 tests: disjoint groups, sizes 20/10/3/0, all 41 panel cols in exactly one group, unknown cols fail closed, every non-feature member refused, derived sources, derived values, production-path refusal, spec↔schema consistency, no pattern selection) | pass | 41/41 columns classified |

## Flags for Isaiah
1. (low, A2) `usdjpy_bars` is classified PROVENANCE, but `fx_x_highrv` and M4 need `usdjpy_rv/usdjpy_bars`. Handled by an explicit derived-feature allowance (decision log); no reclassification.
2. (low, A3) No `ofilt.guards` exists in this sandbox (fresh filesystem), so `_guards_fallback.py` will be used. When merging into the real repo, confirm the real `check_access` signature accepts a tag argument; the adapter fails closed (raises) on any signature mismatch.

## Blinding attestation
- SHA-256 of `panel_dev.csv`, `events_firm.csv`, `events_boj.csv` (all match spec).
- Read the panel header and dtype counts (3 rows, schema only). No statistics of any kind computed.
- A2 tests read the panel header only (`nrows=0`).

## Deviations from the prompt
- None so far.
