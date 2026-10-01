# PASS1_STATUS.md

## Progress
| stage | item | status | one-line result |
|---|---|---|---|
| setup | repo + spec | done | git repo, verbatim spec + read-only VERBATIM copy, checkpoint script; input hashes verified |
| A | A1 spec.py | done | loader/validator/typed accessors; TO_FILL refused; 10 tests pass |
| A | A2 schema.py | done | 9 explicit frozensets cover all 41 panel columns exactly once; allowlist + derived map + `select_features` production path; 14 tests |
| A | A3 io.py | done | hash-verified `load_dev`/event loaders; `load_confirm` guarded by `prereg-v1` (raises here), logs every attempt; fallback guard fails closed; 8 tests |
| A | A4 blind.py | not-started | |
| A | A5 targets.py | not-started | |
| A | A6 fill TO_FILL | not-started | |
| A | A7 hedge report | not-started | |
| A | A8 Stage A tests | not-started | |
| B | B1-B7 | not-started | |
| C | C1-C7 | not-started | |
| D | D1-D6 | not-started | |

## Next action
**A4**: write `ofilt/drift/blind.py` with `require_unblinded(df=None, *, provenance=None)` and `register_real_values(values, label)`. Semantics are fixed in the decision log (PLANNED A4 entry): `synthetic` passes; `dev_real` needs tag `spec-dev-v1` ancestor of HEAD (use `_guards_fallback.is_ancestor_tag`); `confirm_real` additionally needs `prereg-v1`; missing/unknown provenance raises; explicit `provenance=` must match `df.attrs` when both exist; a frame claimed `synthetic` whose nonzero values in any column substantially match a registered real-target fingerprint raises. `io._register_real_targets` already calls `blind.register_real_values` via getattr, so once blind.py exists, `load_dev` registers `y_oc`/`y_topix_oc` automatically (verify this in the A4 tests). Tests: raises on real, passes on synthetic, fails closed on missing attrs, conflict raises, mislabelled real panel raises, temp-repo tag makes dev_real pass.

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
- PLANNED (A4): `require_unblinded` provenance values: `synthetic` passes; `dev_real` needs tag `spec-dev-v1` ancestor of HEAD; `confirm_real` needs `prereg-v1` too; missing/unknown raises. Explicit `provenance=` must agree with `df.attrs` when both present. Extra fail-closed check: real target values (y_oc, y_topix_oc, constructed targets) are fingerprinted at load/construction; a frame labelled `synthetic` whose column values substantially match a real fingerprint raises.
- PLANNED (A5): close-to-close target for f uses the SAME lagged beta as the oc target: `cc_abn = (ao_gap_adj + y_oc) - beta_{t-1}*(ao_topix_gap + y_topix_oc)`, so the identity delta_cc = delta_gap + b holds exactly; `cc_raw = ao_gap_adj + y_oc` for the raw secondary. Rolling beta on non-excluded rows = last w eligible observations.
- PLANNED (B5) — critical for blinding: the blind residual fit must regress the target on the FULL primary design (FE + FX block + ticker-specific controls), discard the FX coefficients unseen, and return only residuals, the fitted CONTROL part (FE + controls, excluding FX), and the row index. Reason: if the fit used controls only, fitted+resid = real y, and a whole-date bootstrap keeps (y, e) pairs together, so y_sim at b_sim=0 would reproduce the real b. With the full-design fit, resid is orthogonal to e in-sample and y_sim = fitted_controls + b_sim*e + a2_sim*eur + resid* carries no information about the real b. Sim output must not contain real target columns (would trip the A4 fingerprint).

## Test results
| name | result | key number |
|---|---|---|
| test_spec (10 tests: load, verbatim-diff, accessors, TO_FILL refusal, sesoi pending, lag rule, 13 rejection cases) | pass | dk_lag(1708)=7, dk_lag(983)=6 |
| test_io (8 tests: dev load 5124 rows/1708 dates/str ticker/sorted; hash mismatch raises; events 163 rows by category + BoJ 98 + tampered-events raise; guard semantics in temp repo (ancestor/annotated/side-branch/missing/bad names/not-a-repo); main repo has no unblinding tags; load_confirm DENIED x2 logged; guard is the only gate (GRANTED in temp repo -> FileNotFoundError); no repo override param) | pass | load_confirm raises AccessDenied |
| test_schema (14 tests: disjoint groups, sizes 20/10/3/0, all 41 panel cols in exactly one group, unknown cols fail closed, every non-feature member refused, derived sources, derived values, production-path refusal, spec↔schema consistency, no pattern selection) | pass | 41/41 columns classified |

## Flags for Isaiah
1. (low, A2) `usdjpy_bars` is classified PROVENANCE, but `fx_x_highrv` and M4 need `usdjpy_rv/usdjpy_bars`. Handled by an explicit derived-feature allowance (decision log); no reclassification.
2. (low, A3) No `ofilt.guards` exists in this sandbox (fresh filesystem), so `_guards_fallback.py` will be used. When merging into the real repo, confirm the real `check_access` signature accepts a tag argument; the adapter fails closed (raises) on any signature mismatch.

## Blinding attestation
- SHA-256 of `panel_dev.csv`, `events_firm.csv`, `events_boj.csv` (all match spec).
- Read the panel header and dtype counts (3 rows, schema only). No statistics of any kind computed.
- A2 tests read the panel header only (`nrows=0`).
- A3: `load_dev` (hash, schema, key uniqueness, ticker set, date-scope check); A3 tests read row count, unique-date count, min/max date. `load_events_firm`/`load_events_boj` (hash, category counts, row counts). No statistics on any target or FX column.

## Deviations from the prompt
- None so far.
