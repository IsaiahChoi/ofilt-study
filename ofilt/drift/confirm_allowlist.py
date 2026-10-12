"""The inference-only allowlist (P4-4c1; P4Q2), as docs/P4_CONFIRM_CLAIMS_SPEC.md (version 1), section 2, specifies.

Constants only. INFERENCE_ONLY_REGRESSORS are the panel columns that the robustness rows of P33 and AM-05 add as
regressors and that the forecasting allowlist does not hold; INFERENCE_ONLY_FILTERS are the columns used only to
select the rows of robustness rows; COST_INPUTS_ONLY are the columns used only by the economic evaluation's costs.
FORECASTING_MODULES lists the forecasting code, which a static test shows never names a column of INFERENCE_ONLY.
The derived terms of the robustness rows (post, its interaction, the gotobi interaction, the ticker-specific FX block)
are design columns, not panel columns, and are not listed.
"""
from __future__ import annotations

INFERENCE_ONLY_REGRESSORS = frozenset({"ewj_oc_jpy", "xau_ret", "n225_ret", "gotobi_day", "c_usdjpy_sess_ret",
                                       "c_eurusd_sess_ret"})
INFERENCE_ONLY_FILTERS = frozenset({"n225_stale_start_min", "n225_stale_end_min", "audit_flag", "excl_d2"})
COST_INPUTS_ONLY = frozenset({"open", "close"})
INFERENCE_ONLY = INFERENCE_ONLY_REGRESSORS | INFERENCE_ONLY_FILTERS | COST_INPUTS_ONLY
FORECASTING_MODULES = ("ofilt/drift/forecast.py", "ofilt/drift/fctests.py", "ofilt/drift/models/__init__.py",
                       "ofilt/drift/models/linear.py", "ofilt/drift/models/ridge.py", "ofilt/drift/models/gbm.py",
                       "ofilt/drift/confirm_forecast.py")
