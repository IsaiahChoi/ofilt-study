"""Forecasting models (Stage C). Use them ONLY through forecast.walk_forward, which
enforces blinding, the feature allowlist and the information firewall."""
from .linear import M0, M1, M2, M3, MODEL_SPEC_STRINGS, linear_design  # noqa: F401

REGISTRY = {"M0": M0, "M1": M1, "M2": M2, "M3": M3}
