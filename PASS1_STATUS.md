# PASS1_STATUS.md

## Progress
| stage | item | status | one-line result |
|---|---|---|---|
| setup | repo + spec | done | git repo, verbatim spec + read-only VERBATIM copy, checkpoint script; input hashes verified |
| A | A1 spec.py | done | loader/validator/typed accessors; TO_FILL refused; 10 tests pass |
| A | A2 schema.py | not-started | |
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
**A2**: write `ofilt/drift/schema.py` with explicit frozensets (no prefix matching) for PRE_OPEN_FEATURES (20 cols), EXCLUSION_FLAGS, INFORMATIONAL, ROBUSTNESS_ONLY, AT_OPEN (3 ao_ cols listed explicitly), TARGET_INPUTS, PROVENANCE (10 cols listed explicitly), KEYS, CONTEMPORANEOUS (empty), plus `assert_features_allowed(cols)` and a test that every one of the 41 `panel_dev.csv` columns falls in exactly one group. Handle `usdjpy_bars` (PROVENANCE) needed for `rv_per_bar` via an explicit DERIVED_FEATURES map (see decision log).

## Decision log (things decided mid-build, not re-derivable from the prompt alone)
- Repo = git repo at `/home/claude/ofilt_pass1`; the tarball includes `.git` so commits persist. Claude never creates tags `spec-dev-v1` or `prereg-v1` in this repo; guard tests use throwaway temp repos.
- `tools/checkpoint.sh "<item>"` runs tests, commits, mirrors to `/mnt/user-data/outputs/ofilt_pass1/`, tars `ofilt_pass1.tar.gz`. Resume: `tar -xzf ofilt_pass1.tar.gz -C /home/claude/`.
- `spec/analysis_spec_dev_v1.VERBATIM.yaml` is a read-only byte copy of the §3 spec; a test proves the live spec differs from it only on lines that contained `TO_FILL`.
- `spec.py` pins operational strings to the implemented values (estimator, se, kernel, lag_rule, small-sample=none, reference=normal, two-sided, CW M3-vs-M2 one-sided, permutation/date/noise importance, M7 early_stopping=false); rejects unknown/missing top-level keys and any `M6`. A YAML edit therefore cannot silently diverge from code.
- `spec.value(path)` refuses `TO_FILL` anywhere inside the requested subtree; `spec.raw(path)` is the unchecked accessor (validation/filling only). `sesoi()` raises `SpecPendingError` while `PENDING_COSTS`.
- PLANNED (A2): `usdjpy_bars` stays in PROVENANCE as specified, but is permitted solely as the denominator of the derived feature `rv_per_bar` via an explicit DERIVED_FEATURES -> source-columns map; raw `usdjpy_bars` is never a model feature.
- PLANNED (A3): data dir defaults to `/mnt/project` (env `OFILT_DATA_DIR` overrides). `load_confirm` calls the guard before touching any path; `ACCESS_LOG` path is module-level and patched to a temp file in tests.
- PLANNED (A4): `require_unblinded` provenance values: `synthetic` passes; `dev_real` needs tag `spec-dev-v1` ancestor of HEAD; `confirm_real` needs `prereg-v1` too; missing/unknown raises. Explicit `provenance=` must agree with `df.attrs` when both present. Extra fail-closed check: real target values (y_oc, y_topix_oc, constructed targets) are fingerprinted at load/construction; a frame labelled `synthetic` whose column values substantially match a real fingerprint raises.
- PLANNED (A5): close-to-close target for f uses the SAME lagged beta as the oc target: `cc_abn = (ao_gap_adj + y_oc) - beta_{t-1}*(ao_topix_gap + y_topix_oc)`, so the identity delta_cc = delta_gap + b holds exactly; `cc_raw = ao_gap_adj + y_oc` for the raw secondary. Rolling beta on non-excluded rows = last w eligible observations.
- PLANNED (B5) — critical for blinding: the blind residual fit must regress the target on the FULL primary design (FE + FX block + ticker-specific controls), discard the FX coefficients unseen, and return only residuals, the fitted CONTROL part (FE + controls, excluding FX), and the row index. Reason: if the fit used controls only, fitted+resid = real y, and a whole-date bootstrap keeps (y, e) pairs together, so y_sim at b_sim=0 would reproduce the real b. With the full-design fit, resid is orthogonal to e in-sample and y_sim = fitted_controls + b_sim*e + a2_sim*eur + resid* carries no information about the real b. Sim output must not contain real target columns (would trip the A4 fingerprint).

## Test results
| name | result | key number |
|---|---|---|
| test_spec (10 tests: load, verbatim-diff, accessors, TO_FILL refusal, sesoi pending, lag rule, 13 rejection cases) | pass | dk_lag(1708)=7, dk_lag(983)=6 |

## Flags for Isaiah
1. (low, A2) `usdjpy_bars` is classified PROVENANCE, but `fx_x_highrv` and M4 need `usdjpy_rv/usdjpy_bars`. Handled by an explicit derived-feature allowance (decision log); no reclassification.
2. (low, A3) No `ofilt.guards` exists in this sandbox (fresh filesystem), so `_guards_fallback.py` will be used. When merging into the real repo, confirm the real `check_access` signature accepts a tag argument; the adapter fails closed (raises) on any signature mismatch.

## Blinding attestation
- SHA-256 of `panel_dev.csv`, `events_firm.csv`, `events_boj.csv` (all match spec).
- Read the panel header and dtype counts (3 rows, schema only). No statistics of any kind computed.

## Deviations from the prompt
- None so far.
