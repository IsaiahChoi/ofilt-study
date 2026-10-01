# Spec amendments (before the `spec-dev-v1` tag)

Each amendment changes specific lines of `spec/analysis_spec_dev_v1.yaml` relative to the
read-only `spec/analysis_spec_dev_v1.VERBATIM.yaml`. The JSONL block under each entry is
machine-read by `tests/test_spec.py`: the live spec may differ from VERBATIM only on lines that
contained `TO_FILL` or on lines listed here with their exact old and new text.

## AM-01 (2026-10-01, Isaiah): moderator main effects in the secondary family and in M4

**Change.**
- `fx_x_longwindow` = primary + `long_window` + `usdjpy_ret:long_window`.
- `fx_x_jumpshare` = primary + `jumpshare` + `usdjpy_ret:jumpshare`.
- `fx_x_highrv` = primary + `highrv` + `usdjpy_ret:highrv`, with `highrv` = 1[rv_per_bar > spec dev median].
- `fx_asymmetry` is unchanged (the e_pos/e_neg split needs no main effect).
- M4 gains the same three main effects. Its highrv threshold is the expanding past median, so M4 stays aligned with the inference designs.

The tested coefficient in each family member is still the interaction only. Line 43 is a
comment-only change: its old text ("+ one term") would otherwise misdescribe the family.

**Reason.** An omitted moderator main effect biases the interaction coefficient whenever the
moderator shifts mean drift and is correlated with e x moderator, e.g. a nonzero mean of e on long
windows. The cost is one parameter per term.

**Lines (exact):**
```jsonl
{"id": "AM-01", "line": 43, "old": "secondary_family_holm:      # each = primary design + one term", "new": "secondary_family_holm:      # each = primary design + one tested interaction (+ its moderator main effect, AM-01)"}
{"id": "AM-01", "line": 44, "old": "  fx_x_longwindow: \"usdjpy_ret * 1[window_hours > 18]\"", "new": "  fx_x_longwindow: \"long_window + usdjpy_ret * long_window; long_window = 1[window_hours > 18]; test the interaction\""}
{"id": "AM-01", "line": 45, "old": "  fx_x_jumpshare: \"usdjpy_ret * clip((usdjpy_rv - usdjpy_bv)/usdjpy_rv, 0, 1)\"", "new": "  fx_x_jumpshare: \"jumpshare + usdjpy_ret * jumpshare; jumpshare = clip((usdjpy_rv - usdjpy_bv)/usdjpy_rv, 0, 1); test the interaction\""}
{"id": "AM-01", "line": 46, "old": "  fx_x_highrv: \"usdjpy_ret * 1[usdjpy_rv/usdjpy_bars > rv_per_bar_dev_median]\"", "new": "  fx_x_highrv: \"highrv + usdjpy_ret * highrv; highrv = 1[usdjpy_rv/usdjpy_bars > rv_per_bar_dev_median]; test the interaction\""}
{"id": "AM-01", "line": 62, "old": "    M4: \"M3 + e*1[long] + e*jumpshare + e*1[rv_per_bar > expanding past median] + min(e,0)\"", "new": "    M4: \"M3 + 1[long] + jumpshare + 1[rv_per_bar > expanding past median] + e*1[long] + e*jumpshare + e*1[rv_per_bar > expanding past median] + min(e,0)\""}
```

## AM-02 (2026-10-01, Isaiah): Pass 4 size rule at the confirmation length, 5000 reps

**Change.** `inference.size_rule`: 2000 dev-calibrated sims -> **5000**, evaluated at **T = T_conf**
(confirmation trading days minus dates on which all three tickers are excluded; 1013 per
`ofilt.drift.calendar`). The band [3.5%, 6.5%] and the fallback (stationary block bootstrap, mean
block 5, decided before the tag) are unchanged.

**Reasons.** (1) The B7 pilot implies a true size of about 6% at confirmation length, so with 2000 reps
(MC SE ~0.5 pp) simulation noise alone could flip the rule; 5000 reps gives ~0.3 pp. (2) The pilot's
983 understated T: exclusions are ticker-specific, only 6 dates drop entirely, and the expanding beta
carries over from dev, so T_conf = 1019 - 6 = 1013. Neither change uses information about b: the
inputs are simulation precision, the calendar and event dates.

**Lines (exact):**
```jsonl
{"id": "AM-02", "line": 33, "old": "  size_rule: \"Pass 4: rejection at b=0 over 2000 dev-calibrated sims must be in [3.5%, 6.5%]; else primary inference = stationary block bootstrap (mean block 5), decided before tag\"", "new": "  size_rule: \"Pass 4: rejection at b=0 over 5000 dev-calibrated sims at T = T_conf (confirmation trading days minus dates on which all three tickers are excluded; 1013 per ofilt.drift.calendar) must be in [3.5%, 6.5%]; else primary inference = stationary block bootstrap (mean block 5), decided before tag.\""}
```
