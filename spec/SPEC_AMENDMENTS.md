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

## AM-03 (2026-10-05, Isaiah): the hedge is 1306 (P18)

**Change.** `target.hedge_oc_column`: `y_topix_oc` (placeholder) -> `y_1306_oc`, the open->close
return of NEXT FUNDS TOPIX ETF (1306). Its gap pair is `ao_1306_gap_adj`, adjusted with 1306's own
distributions (P39, P47; Flag 6 fixed on the hedge leg).

Decided at the Pass 2 decision checkpoint (Isaiah, 2026-10-05): D8 (a), with the zero-gap gate passed (reports/P2_3b_d8_gate.md); D9, expanding β retained.

**Lines (exact):**
```jsonl
{"id": "AM-03", "line": 14, "old": "  hedge_oc_column: y_topix_oc          # PLACEHOLDER; 1306 open->close after Pass 2", "new": "  hedge_oc_column: y_1306_oc           # AM-03 (P18): 1306 open->close; gap pair ao_1306_gap_adj"}
```

## AM-04 (2026-10-05, Isaiah): panel hashes after the Pass 2 rebuild (P10 superseded)

**Change.** Both panel hashes become the P2-4 outputs (60 columns: the 41 old ones plus 19 appended,
P50, P51). The old-column sources follow Isaiah's decision of 2026-10-05: dev = the original
`panel_dev.csv` (`736636…`); sealed = the frozen build run on the Mac (`138e5e21…`), Flag 16.
BLIND_FIT_LOG lines 1–6 keep referring to `736636…`, which is archived under its hash
(`DATA/archive/panel_dev_736636031ca1.csv`).

**Lines (exact; the new hashes filled from `MANIFEST.json` of `build_out/p2_20261006T002928Z`, the accepted P2-4 build):**
```jsonl
{"id": "AM-04", "line": 4, "old": "  dev_panel_sha256: 736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42", "new": "  dev_panel_sha256: 36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68"}
{"id": "AM-04", "line": 7, "old": "  sealed_panel_sha256: 9c18a6c106356139a375ecd7b3e6eaa085d937341c02817021003a4451c6b826   # superseded after Pass 2 rebuild", "new": "  sealed_panel_sha256: b575272aad752b3af84abe109fa66edde421f7c99184c9d1885bacdce64f06d1   # AM-04: Pass 2 rebuild (60 columns); supersedes 9c18a6c1… (P10)"}
```

## AM-05 (2026-10-05, Isaiah): Pass 2 robustness rows (P33 list; P41, P42, P48, P49, P56; D7, D9)

This consolidates the planned AM-05 (Nikkei proxy) and AM-06 (robustness list): both change spec line 42, and each line carries one record.

Common to every row below: the primary design, target, β, exclusions and inference method, as fixed at spec-dev-v1. Added market controls have ticker-specific slopes (P19). Each row reports b with and without its change on the same rows, next to the full-sample primary b, with the DK lag rule at T = that row's estimation dates.

- beta_rolling_500: the target's β is the past-only rolling β over the last 500 eligible rows (non-excluded rows, lag 1 day, continued across samples) instead of the expanding β. Rows: those with a finite rolling-500 β (every confirmation row).
- ewj_yen_denominated: adds ewj_oc_jpy (P49). Rows: primary rows with a finite ewj_oc_jpy (dev: 3 nights dropped; confirmation: none). Not a tier-(ii) check.
- xau_control: adds xau_ret (P41). Rows: all primary rows. No staleness filter: stale XAU endpoints occur only at global gold closures, where the last price is the true price.
- nikkei_proxy_p42: adds n225_ret (P42). Rows: nights with n225_stale_start_min ≤ 5 and n225_stale_end_min ≤ 5; a night with no Japan 225 bar is ineligible. Tier-(ii) criterion (P32, P56): claim tier (ii) only if H1 is rejected and, on the eligible confirmation nights, b with n225_ret (1) has the sign of the primary b̂, (2) rejects b = 0 at 5% two-sided under the primary inference method, and (3) is at least half of b without n225_ret on the same nights.
- mechanism_session_fx_gotobi (not tradable; PLAN §6, §9.2): adds c_usdjpy_sess_ret and c_eurusd_sess_ret (common slopes, as the FX block), gotobi_day (common) and usdjpy_ret × gotobi_day (common). Rows: all primary rows. Reports b, the two session-FX coefficients and the interaction, with DK SEs. Descriptive; outside every claim tier and the Holm family.
- ewj_yen_denominated_REQUIRES_PASS2 is renamed ewj_yen_denominated: Pass 2 built the column.

**Lines (exact):**
```jsonl
{"id": "AM-05", "line": 42, "old": "  others: [beta_rolling_250, raw_target, copx_to_fcx, ewj_yen_denominated_REQUIRES_PASS2, exclusion_d_plus_2, exclude_audit_flag, exclude_boj_day, exclude_sq_major, post_2024_11_05_indicator_CONFIRMATION_ONLY, per_ticker_slopes_holm]", "new": "  others: [beta_rolling_250, beta_rolling_500, raw_target, copx_to_fcx, ewj_yen_denominated, xau_control, nikkei_proxy_p42, mechanism_session_fx_gotobi, exclusion_d_plus_2, exclude_audit_flag, exclude_boj_day, exclude_sq_major, post_2024_11_05_indicator_CONFIRMATION_ONLY, per_ticker_slopes_holm]"}
```
