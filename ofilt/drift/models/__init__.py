"""Forecasting models (Stage C). Use them ONLY through forecast.walk_forward, which
enforces blinding, the feature allowlist and the information firewall."""
from .linear import M0, M1, M2, M3, M4, MODEL_SPEC_STRINGS, linear_design  # noqa: F401
from .ridge import M5, M5_SPEC  # noqa: F401
from .gbm import M7, M7_SPEC  # noqa: F401

REGISTRY = {"M0": M0, "M1": M1, "M2": M2, "M3": M3, "M4": M4, "M5": M5, "M7": M7}
