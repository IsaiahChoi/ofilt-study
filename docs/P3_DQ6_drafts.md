# DQ6 drafts (P3-3e): proposals, not applied

## 1. Header

Proposals for DQ6, the spec amendments of the Pass 3 switch. They are not applied and are not decisions. Isaiah decides on them after the supervisor's review of P3-3e, before the sanction. At P3-5, D3.4 and D2.6 select a branch mechanically from the sealed run's outputs; P3-6 applies it, with the run's values in place of the placeholders. Each placeholder names its source in `reports/P3_4_sealed_run.json` or in the configuration. The ids are fixed now so that the drafts do not depend on the outcome: an id whose branch is not selected stays unused, as AM-06 is.

## 2. The amendments

The headings, texts, templates and placeholder notes are the supervisor's (P3-3e message, section d), copied verbatim by script. The current lines are read from `spec/analysis_spec_dev_v1.yaml` (SHA-256 `0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee408561f68f96fd94d3b0f9`). The records are built by script in the form AM-02 and AM-05 use: `old` is the current line, `new` the template.

### AM-07 (always)

Proposed heading in `spec/SPEC_AMENDMENTS.md`:

```text
## AM-07 (<date>, Isaiah): the SESOI and TOST viability (D2.1 to D2.9; D2.6 applied at P3-5)
```

Text:

```text
Change. `equivalence.sesoi`: PENDING_COSTS becomes <S>, the primary SESOI of the cost model (D2.1 to D2.9; `reports/P3_1_sesoi.md`; approved by Isaiah 2026-10-06), exactly as the sealed run's configuration holds it. `equivalence.viability`: the outcome of D2.6 under the method that D3.4 selects. Reasons: P23 left both pending until costs were priced and the simulator run; Pass 3 did both, and D2.6 was fixed before the run. The low and high SESOIs, <SL> and <SH>, are reported beside the primary as sensitivity values.
```

#### Variant "viable"

Spec line 49, current:

```yaml
equivalence: {test: TOST, alpha: 0.05, sesoi: PENDING_COSTS, viability: "decided in Pass 4 after costs priced and simulator run"}
```

Proposed line 49 (template):

```yaml
equivalence: {test: TOST, alpha: 0.05, sesoi: <S>, viability: "viable (D2.6, P3-5): under <M>, P(equivalence | b = 0) = <P0> at the primary SESOI, and the rate at b = +SESOI is <PB>; low and high SESOI <SL> and <SH> reported"}
```

Record:

```jsonl
{"id": "AM-07", "line": 49, "old": "equivalence: {test: TOST, alpha: 0.05, sesoi: PENDING_COSTS, viability: \"decided in Pass 4 after costs priced and simulator run\"}", "new": "equivalence: {test: TOST, alpha: 0.05, sesoi: <S>, viability: \"viable (D2.6, P3-5): under <M>, P(equivalence | b = 0) = <P0> at the primary SESOI, and the rate at b = +SESOI is <PB>; low and high SESOI <SL> and <SH> reported\"}"}
```

#### Variant "not viable"

Spec line 49, current:

```yaml
equivalence: {test: TOST, alpha: 0.05, sesoi: PENDING_COSTS, viability: "decided in Pass 4 after costs priced and simulator run"}
```

Proposed line 49 (template):

```yaml
equivalence: {test: TOST, alpha: 0.05, sesoi: <S>, viability: "not viable (D2.6, P3-5): under <M>, P(equivalence | b = 0) = <P0> at the primary SESOI, and the rate at b = +SESOI is <PB>; TOST is descriptive only, the equivalence wording is not used, and a null H1 is read against MDE80 = <MDE>"}
```

Record:

```jsonl
{"id": "AM-07", "line": 49, "old": "equivalence: {test: TOST, alpha: 0.05, sesoi: PENDING_COSTS, viability: \"decided in Pass 4 after costs priced and simulator run\"}", "new": "equivalence: {test: TOST, alpha: 0.05, sesoi: <S>, viability: \"not viable (D2.6, P3-5): under <M>, P(equivalence | b = 0) = <P0> at the primary SESOI, and the rate at b = +SESOI is <PB>; TOST is descriptive only, the equivalence wording is not used, and a null H1 is read against MDE80 = <MDE>\"}"}
```

Placeholders:

```text
Placeholders: <S>, <SL>, <SH>: the configuration's primary, low and high SESOI, as written there. <M>: dk_normal, bootstrap or calibrated, as D3.4 selects for H1. <P0> and <PB>: cell 0's and cell 1's TOST rates at the primary SESOI under <M>. <MDE>: MDE80 under <M> (probit interpolated). Rates and MDE80 to four decimals.
```

### AM-08 (only if D3.4 selects a reference other than DK-normal for H1)

Proposed heading in `spec/SPEC_AMENDMENTS.md`:

```text
## AM-08 (<date>, Isaiah): the H1 inference method selected by D3.4 (AM-02 as extended by D3.4)
```

#### Variant "bootstrap"

Text:

```text
Change. `inference.reference`: normal becomes the D3.1 bootstrap. T1's DK-normal rate at b = 0 was <R_dk>, outside [3.5%, 6.5%], and the bootstrap's own rate was <R_boot>, inside it (D3.4). At the confirmation, H1 rejects if |t| > c_boot, the 0.95 order statistic of |t*| over 9,999 stationary-bootstrap resamples of whole dates (mean block 5; recentred t*; the original fit's DK lag), drawn from a generator seeded with 29261001 (the spec's seed + 9,000,000). The interval is b̂ ± c_boot·se, and TOST uses the 0.90 order statistic. Under D3.5 the same procedure applies to H3, the secondary family, H4 and the robustness rows; the pre-registration fixes each test's seed.
```

Spec line 30, current:

```yaml
  reference: normal
```

Proposed line 30 (template):

```yaml
  reference: {method: stationary_bootstrap, statistic: dk_t_recentred, B: 9999, mean_block: 5, seed: 29261001, level_test: 0.95, level_tost: 0.90, scope: D3.5}
```

Record:

```jsonl
{"id": "AM-08", "line": 30, "old": "  reference: normal", "new": "  reference: {method: stationary_bootstrap, statistic: dk_t_recentred, B: 9999, mean_block: 5, seed: 29261001, level_test: 0.95, level_tost: 0.90, scope: D3.5}"}
```

#### Variant "calibrated"

Text:

```text
Change. `inference.reference`: normal becomes DK with simulation-calibrated critical values for H1 and TOST. T1's DK-normal rate at b = 0 was <R_dk>, and the bootstrap's <R_boot>; both lie outside [3.5%, 6.5%] (D3.4). At the confirmation, H1 rejects if |t| > <C95>, c_cal(0.05), with the interval b̂ ± <C95>·se, and TOST uses <C90>, c_cal(0.10) (D3.3, amended: pooled over cells 0 to 4). Under D3.5 every other DK test keeps the normal reference.
```

Spec line 30, current:

```yaml
  reference: normal
```

Proposed line 30 (template):

```yaml
  reference: {h1_and_tost: calibrated, c_h1: <C95>, c_tost: <C90>, others: normal}
```

Record:

```jsonl
{"id": "AM-08", "line": 30, "old": "  reference: normal", "new": "  reference: {h1_and_tost: calibrated, c_h1: <C95>, c_tost: <C90>, others: normal}"}
```

Placeholders:

```text
Placeholders: <R_dk> and <R_boot>: cell 0's rejection rates under dk_normal and bootstrap. <C95> and <C90>: the pooled c_cal values at 0.95 and 0.90, written in full as the JSON holds them.
```

### AM-09 (only if D3.4 replaces Clark–West's normal reference)

Proposed heading in `spec/SPEC_AMENDMENTS.md`:

```text
## AM-09 (<date>, Isaiah): the Clark–West critical value selected by D3.4
```

Text:

```text
Change. `forecast.comparisons.primary_forecast` gains its calibrated one-sided critical value. T3's normal-reference rate at b = 0 was <R_cw>, outside [3.5%, 6.5%] (D3.4), so the primary comparison (M3 against M2) rejects if its Clark–West statistic exceeds <CCW>, c_CW,cal (D3.3: T3's cell at b = 0). The statistic is the one the sealed run calibrated (P3-3e, step c.2). The secondary comparisons keep the normal reference.
```

Spec line 66, current:

```yaml
    primary_forecast: {test: clark_west, unrestricted: M3, restricted: M2, sided: one}
```

Proposed line 66 (template):

```yaml
    primary_forecast: {test: clark_west, unrestricted: M3, restricted: M2, sided: one, reference: calibrated, critical_value: <CCW>}
```

Record:

```jsonl
{"id": "AM-09", "line": 66, "old": "    primary_forecast: {test: clark_west, unrestricted: M3, restricted: M2, sided: one}", "new": "    primary_forecast: {test: clark_west, unrestricted: M3, restricted: M2, sided: one, reference: calibrated, critical_value: <CCW>}"}
```

Placeholders:

```text
Placeholders: <R_cw>: cell 9's Clark–West rate under the normal reference. <CCW>: c_CW,cal, written in full as the JSON holds it.
```

### AM-10 (always)

Proposed heading in `spec/SPEC_AMENDMENTS.md`:

```text
## AM-10 (<date>, Isaiah): the spec frozen for spec-dev-v1
```

Text:

```text
Change. `status`: DRAFT becomes FROZEN, in the switch commit, after the other amendments of the switch. Isaiah tags spec-dev-v1 on the final Pass 3 records commit.
```

Spec line 2, current:

```yaml
status: DRAFT            # FROZEN only when Isaiah tags spec-dev-v1 (after the Pass 2 rebuild)
```

Proposed line 2 (template):

```yaml
status: FROZEN           # frozen at the Pass 3 switch (AM-10); Isaiah tags spec-dev-v1 on the final Pass 3 records commit
```

Record:

```jsonl
{"id": "AM-10", "line": 2, "old": "status: DRAFT            # FROZEN only when Isaiah tags spec-dev-v1 (after the Pass 2 rebuild)", "new": "status: FROZEN           # frozen at the Pass 3 switch (AM-10); Isaiah tags spec-dev-v1 on the final Pass 3 records commit"}
```

## 3. The `spec.py` validation changes

Each change follows AM-02's pattern: a module constant, compared by equality, with an `# AM-xx` comment. Each diff is against the current `ofilt/drift/spec.py` (SHA-256 `49c3c9fdcf04e298d88577be33e9bc0bc8a387f4c786d0000446726158e7917c`), is built by script and is not applied in REPO. The constants sit apart (AM-08's after `CANONICAL_LAG_RULE`, AM-09's after `FORBIDDEN_MODELS`), so that the AM-08 and AM-09 diffs apply together in either order, as the dry switches D2 and D3 do with `git apply`.

### AM-07

None. `validate` already accepts a positive float for `equivalence.sesoi` (spec.py:208-209), and `equivalence.viability` is not validated.

### AM-08, variant "bootstrap"

`inference.reference` is pinned to "normal" in `validate`'s `pinned` table (spec.py:171-175). The change adds the constant `REFERENCE` and pins `inference.reference` to it, in the same table and by the same equality comparison:

```diff
--- a/ofilt/drift/spec.py
+++ b/ofilt/drift/spec.py
@@ -30,6 +30,10 @@
 UNFILLED = "TO_FILL"
 PENDING = "PENDING_COSTS"
 CANONICAL_LAG_RULE = "floor(4*(T/100)**(2/9)), T = unique dates in estimation sample"
+REFERENCE = {  # AM-08 (<date>): inference.reference, the H1 method selected by D3.4 (variant "bootstrap")
+    "method": "stationary_bootstrap", "statistic": "dk_t_recentred", "B": 9999, "mean_block": 5,
+    "seed": 29261001, "level_test": 0.95, "level_tost": 0.90, "scope": "D3.5",
+}
 TOP_LEVEL_KEYS = frozenset({
     "spec_id", "status", "data", "sample", "target", "model", "inference",
     "fraction_unpriced", "robustness", "secondary_family_holm", "equivalence",
@@ -170,7 +174,7 @@
     inf = d["inference"]
     pinned = {"estimator": "pooled_ols", "se": "driscoll_kraay", "kernel": "bartlett",
               "lag_rule": CANONICAL_LAG_RULE, "small_sample_correction": "none",
-              "reference": "normal", "test": "two_sided"}
+              "reference": REFERENCE, "test": "two_sided"}  # AM-08
     for k, v in pinned.items():
         _require(inf.get(k) == v, f"inference.{k} = {inf.get(k)!r} is not what the code implements ({v!r})")
     _require(isinstance(inf["alpha"], float) and 0 < inf["alpha"] < 1, "inference.alpha must be in (0,1)")
```

### AM-08, variant "calibrated"

`inference.reference` is pinned to "normal" in `validate`'s `pinned` table (spec.py:171-175). The change adds the constant `REFERENCE` and pins `inference.reference` to it, in the same table and by the same equality comparison:

```diff
--- a/ofilt/drift/spec.py
+++ b/ofilt/drift/spec.py
@@ -30,6 +30,9 @@
 UNFILLED = "TO_FILL"
 PENDING = "PENDING_COSTS"
 CANONICAL_LAG_RULE = "floor(4*(T/100)**(2/9)), T = unique dates in estimation sample"
+REFERENCE = {  # AM-08 (<date>): inference.reference, the H1 method selected by D3.4 (variant "calibrated")
+    "h1_and_tost": "calibrated", "c_h1": <C95>, "c_tost": <C90>, "others": "normal",
+}
 TOP_LEVEL_KEYS = frozenset({
     "spec_id", "status", "data", "sample", "target", "model", "inference",
     "fraction_unpriced", "robustness", "secondary_family_holm", "equivalence",
@@ -170,7 +173,7 @@
     inf = d["inference"]
     pinned = {"estimator": "pooled_ols", "se": "driscoll_kraay", "kernel": "bartlett",
               "lag_rule": CANONICAL_LAG_RULE, "small_sample_correction": "none",
-              "reference": "normal", "test": "two_sided"}
+              "reference": REFERENCE, "test": "two_sided"}  # AM-08
     for k, v in pinned.items():
         _require(inf.get(k) == v, f"inference.{k} = {inf.get(k)!r} is not what the code implements ({v!r})")
     _require(isinstance(inf["alpha"], float) and 0 < inf["alpha"] < 1, "inference.alpha must be in (0,1)")
```

### AM-09

`validate` pins the whole `primary_forecast` value by equality (spec.py:222-224). The change pins it to the constant `PRIMARY_FORECAST`. `fctests.spec_comparisons` reads only its `test`, `sided`, `unrestricted` and `restricted` keys, and is unchanged.

```diff
--- a/ofilt/drift/spec.py
+++ b/ofilt/drift/spec.py
@@ -46,6 +46,10 @@
 M4_DEF = ("M3 + 1[long] + jumpshare + 1[rv_per_bar > expanding past median] + e*1[long] + e*jumpshare"
           " + e*1[rv_per_bar > expanding past median] + min(e,0)")
 FORBIDDEN_MODELS = frozenset({"M6"})  # time-varying Kalman model: DROPPED
+PRIMARY_FORECAST = {  # AM-09 (<date>): the primary comparison with the Clark-West critical value D3.4 selects
+    "test": "clark_west", "unrestricted": "M3", "restricted": "M2", "sided": "one",
+    "reference": "calibrated", "critical_value": <CCW>,
+}
 _HEX64 = re.compile(r"^[0-9a-f]{64}$")
 _DAY_TOKEN = re.compile(r"^D(?:\+(\d+))?$")
 
@@ -220,7 +224,7 @@
     m7 = f["models"]["M7"]
     _require(m7["fixed"]["early_stopping"] is False, "M7 early_stopping must be explicitly false")
     pf = f["comparisons"]["primary_forecast"]
-    _require(pf == {"test": "clark_west", "unrestricted": "M3", "restricted": "M2", "sided": "one"},
+    _require(pf == PRIMARY_FORECAST,  # AM-09
              "primary forecast comparison must be one-sided Clark-West M3 vs M2")
     for comp in f["comparisons"]["secondary"]:
         _require(isinstance(comp, list) and len(comp) == 3 and comp[0] in ("clark_west", "diebold_mariano")
```

### AM-10

None. `validate` accepts `status` DRAFT or FROZEN (spec.py:133), so the amended line validates as it stands. That check still accepts DRAFT after the switch. If the supervisor wants the validation to reject DRAFT too, the one-line change is `d["status"] == "FROZEN"` at spec.py:133. It is not proposed here and not applied in the dry switches.

## 4. The confirmation-code plan

Facts (P3-3d, step c): no confirmation entry point exists yet (`io.load_confirm` has no caller outside tests). The normal reference is fixed in code (`inference.Result.contrast`, `inference.tost`, `fctests._differential_test`), and `inference.reference` is read only by `spec.validate`.
Proposal:
- The switch changes no code beyond `spec.py`'s validation (DQ7). No C7-hashed file changes in any branch.
- The runners that apply the frozen method are written in Pass 4, for the dev first look, with tests, before any dev_real inference. They are reused at the confirmation under prereg-v1.
- DK-normal: the existing `inference.fit_dk`, `Result.param` and `inference.tost_result`.
- Calibrated (AM-08): `calib.fit_t`; `calib.rejects(t, c_h1)`; the interval b̂ ± c_h1·se; `calib.tost_declares(b, se, sesoi, c_tost)`.
- Bootstrap (AM-08): `calib.bootstrap_test` for H1, and `calib.tost_declares` with its `c_boot_90`. H3 and the other tests D3.5 names need the same procedure on their own design and parameter, which `calib.py` does not yet provide (`bootstrap_test` drops H3's t*). It is added in Pass 4, appended to `calib.py` so that every existing function stays byte-identical.
- Clark–West (AM-09): reject if `fctests.clark_west(...)["stat"]` exceeds `critical_value` (one-sided, strict); a helper is added in Pass 4. The secondary comparisons keep `fctests`' normal p-values.

## 5. The dry switches

Run in scratch clones of REPO at HEAD `1fd79933b16ae98344a9b58abd1f21a4e5dd8198` (remote removed; never pushed; deleted afterwards). The full logs are in the P3-3e report.

**The base** (`/tmp/p3_3e_clone`, one local commit): `docs/P3_DQ5_line7.patch` applied; a dummy BLIND_FIT_LOG line 7 in `sim._log_blind_fit`'s format, with the field values the patch pins (read from the patch); `reports/P3_3_rehearsal2_run1.json` and `.md` copied to `reports/P3_4_sealed_run.json` and `.md` as stand-in outputs. The full suite as `tools/checkpoint.sh` runs it, not committed: Ran 280 tests in 319.803s; `OK (skipped=5)`.

**The stand-in values** (step c.4; `reports/P3_3_rehearsal2_run1.json`, synthetic): `<S>` 0.8652, `<SL>` 0.07152, `<SH>` 2.719 (the configuration); `<C95>` 1.9682196566770376, `<C90>` 1.6458098946190225, `<CCW>` 1.3990565217868869; `<R_dk>` 0.0518, `<R_boot>` 0.0470, `<R_cw>` 0.0310; per method `<P0>`, `<PB>`, `<MDE>`: dk_normal 1.0000, 0.0516, 0.2074; bootstrap 1.0000, 0.0504, 0.2091; calibrated 1.0000, 0.0516, 0.2077; `<date>` 2026-10-07. Rates and MDE80 to four decimals; `<C95>`, `<C90>` and `<CCW>` in full. The values do not match each branch's premise; only the form of the lines is under test.

Each dry switch starts from the base commit (a clone of the base clone) and applies, in one local commit: its spec lines; its `spec/SPEC_AMENDMENTS.md` sections (heading, filled text, `**Lines (exact):**` and the record; the placeholder notes are guidance and are not copied); and section 3's `spec.py` diffs, filled and applied with `git apply`. No test was changed.

### D1: DK-normal, Clark-West normal, viable

- Amendments: AM-07 ("viable"), AM-10; `<M>` = dk_normal.
- `spec.py` diffs applied: none.
- The spec check (`/tmp/p3_3e_speccheck.py`):

```text
ofilt.drift.spec imported from /private/tmp/p3_3e_clone_D1/ofilt/drift/spec.py; under the clone: True
Spec.load() validates: True; status 'FROZEN'; equivalence.sesoi 0.8652; inference.reference 'normal'; primary_forecast {'test': 'clark_west', 'unrestricted': 'M3', 'restricted': 'M2', 'sided': 'one'}
  Spec.sesoi() = 0.8652; spec sha256 bc3e1e1b1e8dbdf43d148f2f47f35f2cda69862ebf179ed80dbce472609dd8e1
spec line count 70 (REPO 70): equal: True
spec lines changed against REPO: [2, 49]
VERBATIM sha256 9007339534c0f31aae65487d5b879bcc5070c2e7dc78da4587c6ecfd9d3d91ec; unchanged (equal to REPO's): True
SPEC CHECK: True
```

- The suite: Ran 276 tests in 334.439s; `FAILED (failures=8, errors=2, skipped=6)`. Failing or erroring tests (innermost tests/ frame; first line of the message):

  - ERROR: `test_3_configuration` (`test_p3_sealed_run.TestConfig.test_3_configuration`), tests/test_p3_sealed_run.py:114: `ValueError: spec SHA-256 differs from the C7 key's (registry)`
  - ERROR: `setUpClass` (`test_p3_sealed_run.TestTinyRuns`), tests/test_p3_sealed_run.py:172: `FileNotFoundError: [Errno 2] No such file or directory: '/var/folders/8y/j_cfd0q14gzbf_m_rylpx4zh0000gp/T/tmp22ff0slx/tmp1/out/P3_4_sealed_run.json'`
  - FAIL: `test_p23_tost_pending_costs` (`test_docs_d2.TestP22toP25.test_p23_tost_pending_costs`), tests/test_docs_d2.py:41: `AssertionError: {'test': 'TOST', 'alpha': 0.05, 'sesoi': 0.8652} != {'test': 'TOST', 'alpha': 0.05, 'sesoi': 'PENDING_COSTS'}`
  - FAIL: `test_lock_amendments_and_nothing_real_before_the_tag` (`test_docs_d3b.TestP36.test_lock_amendments_and_nothing_real_before_the_tag`), tests/test_docs_d3b.py:35: `AssertionError: 'FROZEN' != 'DRAFT'`
  - FAIL: `test_refusals_and_pending_sesoi` (`test_inference_b2.TestTOST.test_refusals_and_pending_sesoi`), tests/test_inference_b2.py:110: `AssertionError: SpecPendingError not raised`
  - FAIL: `test_4_real_mode_refusals_read_no_data` (`test_p3_sealed_run.TestRealRefusals.test_4_real_mode_refusals_read_no_data`), tests/test_p3_sealed_run.py:155: `AssertionError: 3 != 2 : ABORTED: ValueError at line 119`
  - FAIL: `test_default_spec_loads` (`test_spec.TestSpecLoad.test_default_spec_loads`), tests/test_spec.py:32: `AssertionError: 'FROZEN' != 'DRAFT'`
  - FAIL: `test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines` (`test_spec.TestSpecLoad.test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines`), tests/test_spec.py:59: `AssertionError: Lists differ: [2, 4, 7, 14, 33, 42, 43, 44, 45, 46, 49, 62] != [4, 7, 14, 33, 42, 43, 44, 45, 46, 62]`
  - FAIL: `test_sesoi_pending` (`test_spec.TestToFillRefusal.test_sesoi_pending`), tests/test_spec.py:138: `AssertionError: SpecPendingError not raised`
  - FAIL: `test_bands_consistency_and_staleness` (`test_validation_c7.TestC7Report.test_bands_consistency_and_staleness`), tests/test_validation_c7.py:44: `AssertionError: {'cfg[354 chars]6': '0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5e[591 chars]8b'}} != {'cfg[354 chars]6': 'bc3e1e1b1e8dbdf43d148f2f47f35f2cda69862eb[591 chars]8b'}}`

### D2: bootstrap, Clark-West calibrated, viable

- Amendments: AM-07 ("viable"), AM-08 ("bootstrap"), AM-09, AM-10; `<M>` = bootstrap.
- `spec.py` diffs applied: AM-08, AM-09 (`git apply --check` and `git apply`: exit 0).
- The spec check (`/tmp/p3_3e_speccheck.py`):

```text
ofilt.drift.spec imported from /private/tmp/p3_3e_clone_D2/ofilt/drift/spec.py; under the clone: True
Spec.load() validates: True; status 'FROZEN'; equivalence.sesoi 0.8652; inference.reference {'method': 'stationary_bootstrap', 'statistic': 'dk_t_recentred', 'B': 9999, 'mean_block': 5, 'seed': 29261001, 'level_test': 0.95, 'level_tost': 0.9, 'scope': 'D3.5'}; primary_forecast {'test': 'clark_west', 'unrestricted': 'M3', 'restricted': 'M2', 'sided': 'one', 'reference': 'calibrated', 'critical_valu
  Spec.sesoi() = 0.8652; spec sha256 08fb1ebed13ab0b237d14d9149cb985d394c4a6a7e5ea3f55f9e88335d60238d
spec line count 70 (REPO 70): equal: True
spec lines changed against REPO: [2, 30, 49, 66]
VERBATIM sha256 9007339534c0f31aae65487d5b879bcc5070c2e7dc78da4587c6ecfd9d3d91ec; unchanged (equal to REPO's): True
SPEC CHECK: True
```

- The suite: Ran 276 tests in 322.163s; `FAILED (failures=9, errors=2, skipped=6)`. Failing or erroring tests (innermost tests/ frame; first line of the message):

  - ERROR: `test_3_configuration` (`test_p3_sealed_run.TestConfig.test_3_configuration`), tests/test_p3_sealed_run.py:114: `ValueError: spec SHA-256 differs from the C7 key's (registry)`
  - ERROR: `setUpClass` (`test_p3_sealed_run.TestTinyRuns`), tests/test_p3_sealed_run.py:172: `FileNotFoundError: [Errno 2] No such file or directory: '/var/folders/8y/j_cfd0q14gzbf_m_rylpx4zh0000gp/T/tmpg2_ua9zf/tmp1/out/P3_4_sealed_run.json'`
  - FAIL: `test_p21_inference_size_rule_calendar` (`test_docs_d1.TestP20P21.test_p21_inference_size_rule_calendar`), tests/test_docs_d1.py:145: `AssertionError: Tuples differ: ('dri[17 chars]ne', {'method': 'stationary_bootstrap', 'stati[122 chars].5'}) != ('dri[17 chars]ne', 'normal')`
  - FAIL: `test_p23_tost_pending_costs` (`test_docs_d2.TestP22toP25.test_p23_tost_pending_costs`), tests/test_docs_d2.py:41: `AssertionError: {'test': 'TOST', 'alpha': 0.05, 'sesoi': 0.8652} != {'test': 'TOST', 'alpha': 0.05, 'sesoi': 'PENDING_COSTS'}`
  - FAIL: `test_lock_amendments_and_nothing_real_before_the_tag` (`test_docs_d3b.TestP36.test_lock_amendments_and_nothing_real_before_the_tag`), tests/test_docs_d3b.py:35: `AssertionError: 'FROZEN' != 'DRAFT'`
  - FAIL: `test_refusals_and_pending_sesoi` (`test_inference_b2.TestTOST.test_refusals_and_pending_sesoi`), tests/test_inference_b2.py:110: `AssertionError: SpecPendingError not raised`
  - FAIL: `test_4_real_mode_refusals_read_no_data` (`test_p3_sealed_run.TestRealRefusals.test_4_real_mode_refusals_read_no_data`), tests/test_p3_sealed_run.py:155: `AssertionError: 3 != 2 : ABORTED: ValueError at line 119`
  - FAIL: `test_default_spec_loads` (`test_spec.TestSpecLoad.test_default_spec_loads`), tests/test_spec.py:32: `AssertionError: 'FROZEN' != 'DRAFT'`
  - FAIL: `test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines` (`test_spec.TestSpecLoad.test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines`), tests/test_spec.py:59: `AssertionError: Lists differ: [2, 4, 7, 14, 30, 33, 42, 43, 44, 45, 46, 49, 62, 66] != [4, 7, 14, 33, 42, 43, 44, 45, 46, 62]`
  - FAIL: `test_sesoi_pending` (`test_spec.TestToFillRefusal.test_sesoi_pending`), tests/test_spec.py:138: `AssertionError: SpecPendingError not raised`
  - FAIL: `test_bands_consistency_and_staleness` (`test_validation_c7.TestC7Report.test_bands_consistency_and_staleness`), tests/test_validation_c7.py:44: `AssertionError: {'cfg[355 chars]': '0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5ee[590 chars]8b'}} != {'cfg[355 chars]': '08fb1ebed13ab0b237d14d9149cb985d394c4a6a7e[590 chars]8b'}}`

### D3: calibrated, Clark-West calibrated, not viable

- Amendments: AM-07 ("not viable"), AM-08 ("calibrated"), AM-09, AM-10; `<M>` = calibrated.
- `spec.py` diffs applied: AM-08, AM-09 (`git apply --check` and `git apply`: exit 0).
- The spec check (`/tmp/p3_3e_speccheck.py`):

```text
ofilt.drift.spec imported from /private/tmp/p3_3e_clone_D3/ofilt/drift/spec.py; under the clone: True
Spec.load() validates: True; status 'FROZEN'; equivalence.sesoi 0.8652; inference.reference {'h1_and_tost': 'calibrated', 'c_h1': 1.9682196566770376, 'c_tost': 1.6458098946190225, 'others': 'normal'}; primary_forecast {'test': 'clark_west', 'unrestricted': 'M3', 'restricted': 'M2', 'sided': 'one', 'reference': 'calibrated', 'critical_value': 1.3990565217868869}
  Spec.sesoi() = 0.8652; spec sha256 543e77985a3d00074c538716d9a200ad1ae21268b02e57ba915fcf2ee2ac749a
spec line count 70 (REPO 70): equal: True
spec lines changed against REPO: [2, 30, 49, 66]
VERBATIM sha256 9007339534c0f31aae65487d5b879bcc5070c2e7dc78da4587c6ecfd9d3d91ec; unchanged (equal to REPO's): True
SPEC CHECK: True
```

- The suite: Ran 276 tests in 335.382s; `FAILED (failures=9, errors=2, skipped=6)`. Failing or erroring tests (innermost tests/ frame; first line of the message):

  - ERROR: `test_3_configuration` (`test_p3_sealed_run.TestConfig.test_3_configuration`), tests/test_p3_sealed_run.py:114: `ValueError: spec SHA-256 differs from the C7 key's (registry)`
  - ERROR: `setUpClass` (`test_p3_sealed_run.TestTinyRuns`), tests/test_p3_sealed_run.py:172: `FileNotFoundError: [Errno 2] No such file or directory: '/var/folders/8y/j_cfd0q14gzbf_m_rylpx4zh0000gp/T/tmpcn2yq4qv/tmp1/out/P3_4_sealed_run.json'`
  - FAIL: `test_p21_inference_size_rule_calendar` (`test_docs_d1.TestP20P21.test_p21_inference_size_rule_calendar`), tests/test_docs_d1.py:145: `AssertionError: Tuples differ: ('dri[17 chars]ne', {'h1_and_tost': 'calibrated', 'c_h1': 1.9[62 chars]al'}) != ('dri[17 chars]ne', 'normal')`
  - FAIL: `test_p23_tost_pending_costs` (`test_docs_d2.TestP22toP25.test_p23_tost_pending_costs`), tests/test_docs_d2.py:41: `AssertionError: {'test': 'TOST', 'alpha': 0.05, 'sesoi': 0.8652} != {'test': 'TOST', 'alpha': 0.05, 'sesoi': 'PENDING_COSTS'}`
  - FAIL: `test_lock_amendments_and_nothing_real_before_the_tag` (`test_docs_d3b.TestP36.test_lock_amendments_and_nothing_real_before_the_tag`), tests/test_docs_d3b.py:35: `AssertionError: 'FROZEN' != 'DRAFT'`
  - FAIL: `test_refusals_and_pending_sesoi` (`test_inference_b2.TestTOST.test_refusals_and_pending_sesoi`), tests/test_inference_b2.py:110: `AssertionError: SpecPendingError not raised`
  - FAIL: `test_4_real_mode_refusals_read_no_data` (`test_p3_sealed_run.TestRealRefusals.test_4_real_mode_refusals_read_no_data`), tests/test_p3_sealed_run.py:155: `AssertionError: 3 != 2 : ABORTED: ValueError at line 119`
  - FAIL: `test_default_spec_loads` (`test_spec.TestSpecLoad.test_default_spec_loads`), tests/test_spec.py:32: `AssertionError: 'FROZEN' != 'DRAFT'`
  - FAIL: `test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines` (`test_spec.TestSpecLoad.test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines`), tests/test_spec.py:59: `AssertionError: Lists differ: [2, 4, 7, 14, 30, 33, 42, 43, 44, 45, 46, 49, 62, 66] != [4, 7, 14, 33, 42, 43, 44, 45, 46, 62]`
  - FAIL: `test_sesoi_pending` (`test_spec.TestToFillRefusal.test_sesoi_pending`), tests/test_spec.py:138: `AssertionError: SpecPendingError not raised`
  - FAIL: `test_bands_consistency_and_staleness` (`test_validation_c7.TestC7Report.test_bands_consistency_and_staleness`), tests/test_validation_c7.py:44: `AssertionError: {'cfg[354 chars]6': '0320d6aaa19b0ed3cc34f50dd105df3d16d1c3c5e[591 chars]8b'}} != {'cfg[354 chars]6': '543e77985a3d00074c538716d9a200ad1ae21268b[591 chars]8b'}}`

Common to all three:
- The sixth skip is `tests/test_io.py:89-93` (`test_main_repo_has_no_unblinding_tags_while_draft`), which skips once the status is FROZEN ("spec frozen; tags expected"). A verbose run of `tests.test_io` and `tests.test_importance_registry_c6` in the D1 clone showed it.
- `TestTinyRuns.setUpClass` errors, so its four tests (5, 6, 9 and 15) do not run: 276 tests ran, not 280.
- `tests/test_docs_d3.py`'s DQ5 line-7 assertions pass in all three: they pin the pre-switch spec hash that line 7 records.
- `tests/test_spec.py:172` (`primary_cw_edit`) passes in D2 and D3: the AM-09 pin still rejects a two-sided primary comparison.

## 6. Draft test-change table

One row per test that fails or errors in any dry switch. "Asserts now" quotes REPO's test lines by script. The proposals are the builder's drafts: the smallest change that makes each test assert the amended state.

| Test (file:line) | Asserts now | Proposed after the switch | Branches | Follows |
|---|---|---|---|---|
| `tests/test_docs_d1.py:145` `test_p21_inference_size_rule_calendar` (FAIL) | `self.assertEqual((s.value("inference.se"), s.value("inference.small_sample_correction"),`<br>`s.value("inference.reference")), ("driscoll_kraay", "none", "normal"))` | the selected `inference.reference` in the third place, exactly as the AM-08 line writes it: variant "bootstrap": `{"method": "stationary_bootstrap", "statistic": "dk_t_recentred", "B": 9999, "mean_block": 5, "seed": 29261001, "level_test": 0.95, "level_tost": 0.9, "scope": "D3.5"}`; variant "calibrated": `{"h1_and_tost": "calibrated", "c_h1": <C95>, "c_tost": <C90>, "others": "normal"}`. Unchanged in D1. Lines 144 and 147-150 unchanged. | D2, D3 | AM-08 |
| `tests/test_docs_d2.py:41` `test_p23_tost_pending_costs` (FAIL at 41; 43 and 44-45 fail too once 41 passes) | `self.assertEqual({k: s.value(f"equivalence.{k}") for k in ("test", "alpha", "sesoi")},`<br>`{"test": "TOST", "alpha": 0.05, "sesoi": "PENDING_COSTS"})`<br>`self.assertIn("Pass 4", s.value("equivalence.viability"))`<br>`with self.assertRaises(SpecPendingError):`<br>`s.sesoi()` | P23's pending state ends at the switch. Post-switch form: `{"test": "TOST", "alpha": 0.05, "sesoi": <S>}`, with `<S>` read from `docs/P3_RUN_CONFIG.json`'s `sesoi.primary`; the viability begins with the branch's variant, "viable (D2.6, P3-5)" or "not viable (D2.6, P3-5)"; `s.sesoi() == <S>`. The PENDING_COSTS refusal stays tested by test_spec's mutation (below). | D1, D2, D3 | AM-07 |
| `tests/test_docs_d3b.py:35` `test_lock_amendments_and_nothing_real_before_the_tag` (FAIL at 35; 36 and 39 fail too once 35 passes) | `self.assertEqual(s.status, "DRAFT")`<br>`self.assertIn("FROZEN only when Isaiah tags spec-dev-v1", (ROOT / "spec" / "analysis_spec_dev_v1.yaml").read_text())`<br>`self.assertIn("decided before tag", SIZE_RULE)                          # = before spec-dev-v1 (P36)`<br>`heads = re.findall(r"^## (AM-\d\d) ", (ROOT / "spec" / "SPEC_AMENDMENTS.md").read_text(), re.M)`<br>`self.assertEqual(heads, ["AM-01", "AM-02", "AM-03", "AM-04", "AM-05"])   # AM-03, AM-04, AM-05 (row 27)` | The DRAFT lock (35-36) ends at the switch. Post-switch form: `s.status == "FROZEN"`; the YAML contains AM-10's comment "frozen at the Pass 3 switch (AM-10)"; `heads` is AM-01 to AM-05 followed by the switch's ids in order (D1: AM-07, AM-10; D2 and D3: AM-07, AM-08, AM-09, AM-10). Lines 37 and 40-42 unchanged (41 is 7 after DQ5). | D1, D2, D3 | AM-10 (35-36); every amendment of the branch (39) |
| `tests/test_inference_b2.py:110` `test_refusals_and_pending_sesoi` (FAIL) | `with self.assertRaises(SpecPendingError):`<br>`I.tost_result(res, "usdjpy_ret", spec)` | `tost_result` without a SESOI uses the spec's: `r = I.tost_result(res, "usdjpy_ret", spec)` with `r["sesoi"] == <S>` (the configuration's `sesoi.primary`) and `r["alpha"] == 0.05` (`equivalence.alpha`). Lines 105-109 and 112 unchanged. The PENDING_COSTS refusal stays tested by test_spec's mutation (below). | D1, D2, D3 | AM-07 |
| `tests/test_p3_sealed_run.py:114` `test_3_configuration` (ERROR: `build_config` raises at p3_sealed_run.py:119, the spec's hash against the C7 key's) | `self.assertEqual(P.CONFIG_PATH.read_text(encoding="utf-8"), P.config_text(P.build_config()))`<br>`self.assertEqual(P.validate_config(CFG), [])` | The configuration binds the sealed run to the pre-switch spec, so this check's purpose ends at the run. After the switch's C7 rerun, `build_config` passes line 119, and `validate_config(CFG)` would return exactly `["key 'spec_sha256' differs from the registry"]` (builder's reading of p3_sealed_run.py:114-119 and 211-217; not run). Post-switch form of 114-115: the SHA-256 of `docs/P3_RUN_CONFIG.json` equals `reports/P3_4_sealed_run.json`'s `config_sha256`; the configuration's `spec_sha256` equals BLIND_FIT_LOG line 7's; and `validate_config(CFG)` returns exactly that one difference. Lines 116-127 unchanged. | D1, D2, D3 | every amendment (the spec's hash), after the C7 rerun |
| `tests/test_p3_sealed_run.py:153` `test_4_real_mode_refusals_read_no_data` (FAIL at 155: exit 3, "ABORTED: ValueError at line 119") | `r = subprocess.run([sys.executable, str(TOOL), "--real", "--expect-config-sha256", sha], cwd=str(ROOT),`<br>`env=env, capture_output=True, text=True, timeout=300)`<br>`self.assertEqual(r.returncode, P.EXIT_REFUSED, r.stdout + r.stderr)`<br>`self.assertIn(f"REFUSED: --real needs {P.SEALED_ENV}=1", r.stdout)` | After the C7 rerun, a fresh `--real` process is refused for the configuration before the mode check (`validate_config` at p3_sealed_run.py:386-388 runs before `mode_refusal` at 390-395): exit 2, "REFUSED: configuration: ..." (builder's reading; not run). Post-switch form: line 156 asserts `"REFUSED: configuration"` in place of the sealed-variable message. Lines 132-147, 155 and 157 unchanged: the tool still refuses and reads no data. | D1, D2, D3 | every amendment (the spec's hash), after the C7 rerun |
| `tests/test_p3_sealed_run.py:170` `TestTinyRuns.setUpClass` (ERROR: no output; tests 5, 6, 9 and 15 do not run) | `cls.res.append(tiny_run(o, tm, nd))`<br>`cls.out.append(o); cls.tmp.append(tm)`<br>`cls.js = [json.loads((o / f"{P.REAL_STEM}.json").read_text(encoding="utf-8")) for o in cls.out]` | The tool cannot run against the amended spec: it aborts at line 119 in the dry switches, and would refuse for the configuration after the C7 rerun. The tiny runs' purpose (exercising the tool before the sealed run) ends at the run. Post-switch form: one synthetic run that must be refused (exit 2, stdout starting "REFUSED: configuration", nothing written to `--out-dir`, the run's directory removed). Tests 5, 6, 9 and 15 retire; their evidence stays in the P3-2b to P3-3c records and the two rehearsals. | D1, D2, D3 | every amendment (the spec's hash), after the C7 rerun |
| `tests/test_spec.py:32` `test_default_spec_loads` (FAIL) | `self.assertEqual(sp.status, "DRAFT")` | `self.assertEqual(sp.status, "FROZEN")`. Lines 31 and 33-35 unchanged. | D1, D2, D3 | AM-10 |
| `tests/test_spec.py:59` `test_live_file_differs_from_verbatim_only_on_to_fill_or_amended_lines` (FAIL at 59; 60 fails too once 59 passes) | `self.assertEqual(sorted(amended), [4, 7, 14, 33, 42, 43, 44, 45, 46, 62])    # + AM-04: 4, 7; AM-03: 14; AM-05: 42 (row 3)`<br>`self.assertEqual({r["id"] for r in recs}, {"AM-01", "AM-02", "AM-03", "AM-04", "AM-05"})` | The amended lines and ids gain the branch's: D1 `[2, 4, 7, 14, 33, 42, 43, 44, 45, 46, 49, 62]` and ids + {AM-07, AM-10}; D2 and D3 `[2, 4, 7, 14, 30, 33, 42, 43, 44, 45, 46, 49, 62, 66]` and ids + {AM-07, AM-08, AM-09, AM-10}. The record checks at 44-58 pass in all three dry switches: the new records describe the files exactly. | D1, D2, D3 | every amendment of the branch |
| `tests/test_spec.py:137` `test_sesoi_pending` (FAIL) | `def test_sesoi_pending(self):`<br>`with self.assertRaises(S.SpecPendingError):`<br>`S.Spec.load().sesoi()` | `S.Spec.load().sesoi() == <S>` (the configuration's `sesoi.primary`), and the refusal is kept on a mutated spec: `_load_mutated(lambda d: d["equivalence"].__setitem__("sesoi", "PENDING_COSTS")).sesoi()` raises `SpecPendingError`. | D1, D2, D3 | AM-07 |
| `tests/test_validation_c7.py:43` `test_bands_consistency_and_staleness` (FAIL: the C7 key's `spec_sha256` is the pre-switch spec's) | `spec = Spec.load()`<br>`self.assertEqual(mc["key"], C.config_key(C.FULL, spec))` | No pin change: resolved by the C7 rerun in the switch commit (`tools/c7_mc.py` regenerates the C7 reports' key with the amended spec's hash; `config_key`, tools/c7_mc.py:74). `spec.py` is not among the C7-hashed code files (tools/c7_mc.py:42-43), so line 41 still passes. | D1, D2, D3 | every amendment (the spec's hash): C7 rerun |

Not failures, for the supervisor:
- `tests/test_io.py:89-93` skips once FROZEN (the sixth skip in each dry switch): its check, no unblinding tag while DRAFT, ends at the switch by design (AM-10). No change proposed.
- `tests/test_importance_registry_c6.py:188-192` asserts the committed run registry empty only while DRAFT; under FROZEN it passes without asserting. `tests/test_docs_d3b.py:42` still asserts it empty in every branch. No change proposed.
