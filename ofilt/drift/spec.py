"""Load, validate and access the drift analysis spec (spec/analysis_spec_dev_v1.yaml).

Design rules
------------
* The YAML is the single source of truth for every methodological choice.
  Code implements those choices; where a spec string *names* a rule the code
  implements (lag rule, estimator, kernel, ...), validation pins the string to
  the implemented value so that an edit to the YAML cannot silently diverge
  from the code. Fail closed: unknown top-level keys are rejected.
* ``TO_FILL`` values are permitted in the file during Stage A but are refused
  at analysis time: every accessor that would return one raises
  ``SpecIncompleteError``.
* ``PENDING_COSTS`` (equivalence SESOI) is refused by ``sesoi()`` with
  ``SpecPendingError``; the equivalence test is decided in Pass 4.
"""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEC_PATH = REPO_ROOT / "spec" / "analysis_spec_dev_v1.yaml"

UNFILLED = "TO_FILL"
PENDING = "PENDING_COSTS"
CANONICAL_LAG_RULE = "floor(4*(T/100)**(2/9)), T = unique dates in estimation sample"
TOP_LEVEL_KEYS = frozenset({
    "spec_id", "status", "data", "sample", "target", "model", "inference",
    "fraction_unpriced", "robustness", "secondary_family_holm", "equivalence",
    "forecast", "seeds",
})
REQUIRED_MODELS = frozenset({"M0", "M1", "M2", "M3", "M4", "M5", "M7"})
FORBIDDEN_MODELS = frozenset({"M6"})  # time-varying Kalman model: DROPPED
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_DAY_TOKEN = re.compile(r"^D(?:\+(\d+))?$")


class SpecError(ValueError):
    """The spec file is malformed or disagrees with what the code implements."""


class SpecIncompleteError(SpecError):
    """A TO_FILL value was requested at analysis time."""


class SpecPendingError(SpecError):
    """A value deliberately deferred to a later pass (e.g. PENDING_COSTS) was requested."""


@dataclass(frozen=True)
class BetaSpec:
    method: str            # 'expanding' | 'rolling'
    min_periods: int
    lag_days: int
    estimate_on: str       # 'non_excluded_rows' | 'all_rows'
    continue_across_samples: bool


@dataclass(frozen=True)
class ForecastExclusion:
    """Day offsets (relative to D = first trading day >= release date) excluded
    from forecast *evaluation*, by event category."""
    tanshin: tuple[int, ...]
    standalone_news: tuple[int, ...]


def dk_lag(T: int) -> int:
    """Bartlett bandwidth: floor(4*(T/100)**(2/9)), T = unique dates in the
    estimation sample (spec inference.lag_rule)."""
    if not isinstance(T, (int,)) or isinstance(T, bool) or T < 1:
        raise ValueError(f"T must be a positive int, got {T!r}")
    return int(math.floor(4.0 * (T / 100.0) ** (2.0 / 9.0)))


def _get(d: dict, path: str) -> Any:
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise SpecError(f"missing spec field: {path}")
        cur = cur[part]
    return cur


def _walk(x: Any, prefix: str = ""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from _walk(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _walk(v, f"{prefix}[{i}]")
    else:
        yield prefix, x


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SpecError(msg)


def _parse_day_tokens(tokens: Any, where: str) -> tuple[int, ...]:
    _require(isinstance(tokens, list) and len(tokens) > 0, f"{where} must be a non-empty list")
    out = []
    for t in tokens:
        m = _DAY_TOKEN.match(str(t))
        _require(m is not None, f"{where}: bad day token {t!r} (expected D or D+k)")
        out.append(int(m.group(1) or 0))
    _require(len(set(out)) == len(out), f"{where}: duplicate offsets")
    return tuple(sorted(out))


def validate(d: dict) -> None:
    """Structural and semantic validation. Raises SpecError on any problem."""
    _require(isinstance(d, dict), "spec must be a mapping")
    keys = set(d)
    _require(keys == TOP_LEVEL_KEYS,
             f"top-level keys mismatch: missing={sorted(TOP_LEVEL_KEYS - keys)} extra={sorted(keys - TOP_LEVEL_KEYS)}")
    _require(d["spec_id"] == "drift-dev-v1", f"unexpected spec_id {d['spec_id']!r}")
    _require(d["status"] in ("DRAFT", "FROZEN"), f"status must be DRAFT or FROZEN, got {d['status']!r}")

    for k in ("dev_panel_sha256", "events_firm_sha256", "events_boj_sha256", "sealed_panel_sha256"):
        v = _get(d, f"data.{k}")
        _require(isinstance(v, str) and _HEX64.match(v) is not None, f"data.{k} must be 64 lowercase hex")

    s = d["sample"]
    _require(isinstance(s["inference_exclude_rows_if"], list) and all(isinstance(c, str) for c in s["inference_exclude_rows_if"]),
             "sample.inference_exclude_rows_if must be a list of column names")
    fe = s["forecast_eval_exclusion"]
    _require(isinstance(fe, dict) and set(fe) == {"tanshin", "standalone_news"},
             "sample.forecast_eval_exclusion must have exactly keys tanshin, standalone_news")
    _parse_day_tokens(fe["tanshin"], "forecast_eval_exclusion.tanshin")
    _parse_day_tokens(fe["standalone_news"], "forecast_eval_exclusion.standalone_news")
    _require("beta" in s["require_nonmissing"], "require_nonmissing must include beta")

    t = d["target"]
    _require(t["primary"] == "abnormal_oc", "target.primary must be abnormal_oc")
    _require(t["secondary"] == "raw_oc", "target.secondary must be raw_oc")
    _require(isinstance(t["hedge_oc_column"], str), "target.hedge_oc_column must be a column name")
    b = t["beta"]
    _require(b.get("method") in ("expanding", "rolling"), "target.beta.method must be expanding|rolling")
    _require(isinstance(b.get("min_periods"), int) and b["min_periods"] > 1, "target.beta.min_periods must be int > 1")
    _require(isinstance(b.get("lag_days"), int) and b["lag_days"] >= 1, "target.beta.lag_days must be int >= 1 (past-only)")
    _require(b.get("estimate_on") in ("non_excluded_rows", "all_rows"), "target.beta.estimate_on invalid")
    _require(isinstance(b.get("continue_across_samples"), bool), "target.beta.continue_across_samples must be bool")

    m = d["model"]
    _require(m["fixed_effects"] == "ticker", "model.fixed_effects must be ticker")
    _require(isinstance(m["fx_block_common"], list) and len(m["fx_block_common"]) == 2, "fx_block_common must list 2 columns")
    _require(m["h1_parameter"] in m["fx_block_common"], "h1_parameter must be in fx_block_common")
    _require(m["h3_parameter"] in m["fx_block_common"], "h3_parameter must be in fx_block_common")
    _require(m["h1_parameter"] != m["h3_parameter"], "h1 and h3 parameters must differ")
    _require(isinstance(m["controls_ticker_specific"], list) and len(m["controls_ticker_specific"]) >= 1,
             "controls_ticker_specific must be a non-empty list")
    _require(not (set(m["controls_ticker_specific"]) & set(m["fx_block_common"])), "controls overlap the FX block")

    inf = d["inference"]
    pinned = {"estimator": "pooled_ols", "se": "driscoll_kraay", "kernel": "bartlett",
              "lag_rule": CANONICAL_LAG_RULE, "small_sample_correction": "none",
              "reference": "normal", "test": "two_sided"}
    for k, v in pinned.items():
        _require(inf.get(k) == v, f"inference.{k} = {inf.get(k)!r} is not what the code implements ({v!r})")
    _require(isinstance(inf["alpha"], float) and 0 < inf["alpha"] < 1, "inference.alpha must be in (0,1)")

    fu = d["fraction_unpriced"]
    _require(fu["ci"] == ["delta_method", "fieller"], "fraction_unpriced.ci must be [delta_method, fieller]")

    r = d["robustness"]
    _require(isinstance(r["huber"]["c"], float) and r["huber"]["c"] > 0, "robustness.huber.c must be > 0")
    w = r["winsorize_fx"]
    q = w["q"]
    _require(isinstance(q, list) and len(q) == 2 and 0 < q[0] < q[1] < 1, "winsorize_fx.q must be [lo, hi] in (0,1)")
    if w["values"] != UNFILLED:
        v = w["values"]
        _require(isinstance(v, dict) and set(v) == set(w["cols"]), "winsorize_fx.values must map each col")
        for c, lohi in v.items():
            _require(isinstance(lohi, list) and len(lohi) == 2 and all(isinstance(z, float) for z in lohi)
                     and lohi[0] < lohi[1], f"winsorize_fx.values[{c}] must be [lo, hi] floats, lo < hi")
    ic = r["influence_curve"]
    _require(ic["unit"] == "date" and isinstance(ic["k_max"], int) and ic["k_max"] >= 1, "influence_curve invalid")

    sf = d["secondary_family_holm"]
    _require(set(sf) == {"fx_x_longwindow", "fx_x_jumpshare", "fx_x_highrv", "fx_asymmetry", "rv_per_bar_dev_median"},
             "secondary_family_holm keys mismatch")
    if sf["rv_per_bar_dev_median"] != UNFILLED:
        v = sf["rv_per_bar_dev_median"]
        _require(isinstance(v, float) and v > 0, "rv_per_bar_dev_median must be a positive float")

    eq = d["equivalence"]
    _require(eq["test"] == "TOST", "equivalence.test must be TOST")
    _require(eq["sesoi"] == PENDING or (isinstance(eq["sesoi"], float) and eq["sesoi"] > 0),
             "equivalence.sesoi must be PENDING_COSTS or a positive float")

    f = d["forecast"]
    _require(f["scheme"] == "expanding", "forecast.scheme must be expanding")
    _require(isinstance(f["min_train_dates"], int) and f["min_train_dates"] > 0, "min_train_dates must be int > 0")
    _require(isinstance(f["refit_every_dates"], int) and f["refit_every_dates"] > 0, "refit_every_dates must be int > 0")
    _require(f["pooled_across_tickers"] is True, "forecast.pooled_across_tickers must be true")
    _require(f["scaling"] == "in_fold_only", "forecast.scaling must be in_fold_only")
    models = set(f["models"])
    _require(not (models & FORBIDDEN_MODELS), "M6 (time-varying Kalman) is DROPPED and must not appear")
    _require(models == REQUIRED_MODELS, f"forecast.models must be exactly {sorted(REQUIRED_MODELS)}")
    m7 = f["models"]["M7"]
    _require(m7["fixed"]["early_stopping"] is False, "M7 early_stopping must be explicitly false")
    pf = f["comparisons"]["primary_forecast"]
    _require(pf == {"test": "clark_west", "unrestricted": "M3", "restricted": "M2", "sided": "one"},
             "primary forecast comparison must be one-sided Clark-West M3 vs M2")
    for comp in f["comparisons"]["secondary"]:
        _require(isinstance(comp, list) and len(comp) == 3 and comp[0] in ("clark_west", "diebold_mariano")
                 and comp[1] in models and comp[2] in models, f"bad secondary comparison {comp!r}")
    imp = f["importance"]
    _require(imp["method"] == "permutation" and imp["unit"] == "date" and imp["calibration"] == "noise_column",
             "importance must be date-unit permutation calibrated to a noise column")
    _require(isinstance(d["seeds"].get("global"), int), "seeds.global must be int")


class Spec:
    """Validated, read-only view of the analysis spec."""

    def __init__(self, raw: dict, path: Path, sha256: str):
        validate(raw)
        self._raw = raw
        self.path = path
        self.sha256 = sha256

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Spec":
        p = Path(path) if path is not None else DEFAULT_SPEC_PATH
        data = p.read_bytes()
        raw = yaml.safe_load(data.decode("utf-8"))
        return cls(raw, p, hashlib.sha256(data).hexdigest())

    # ---------------------------------------------------------- generic
    def raw(self, path: str) -> Any:
        """Value at a dotted path, with no TO_FILL check (for validation/filling only)."""
        return _get(self._raw, path)

    def value(self, path: str) -> Any:
        """Value at a dotted path; refuses TO_FILL anywhere inside it."""
        v = _get(self._raw, path)
        bad = [p for p, x in _walk(v, path) if x == UNFILLED]
        if bad:
            raise SpecIncompleteError(f"spec field(s) still TO_FILL at analysis time: {bad}")
        return v

    def unfilled(self) -> list[str]:
        return [p for p, x in _walk(self._raw) if x == UNFILLED]

    def assert_analysis_ready(self) -> None:
        u = self.unfilled()
        if u:
            raise SpecIncompleteError(f"spec not ready for analysis; TO_FILL remains at {u}")

    # ---------------------------------------------------------- typed accessors
    @property
    def spec_id(self) -> str:
        return self._raw["spec_id"]

    @property
    def status(self) -> str:
        return self._raw["status"]

    @property
    def seed(self) -> int:
        return int(self._raw["seeds"]["global"])

    def data_hash(self, which: str) -> str:
        """which in {dev_panel, events_firm, events_boj, sealed_panel}."""
        return self.value(f"data.{which}_sha256")

    @property
    def inference_exclusion_flags(self) -> tuple[str, ...]:
        return tuple(self.value("sample.inference_exclude_rows_if"))

    @property
    def forecast_eval_exclusion(self) -> ForecastExclusion:
        fe = self.value("sample.forecast_eval_exclusion")
        return ForecastExclusion(
            tanshin=_parse_day_tokens(fe["tanshin"], "tanshin"),
            standalone_news=_parse_day_tokens(fe["standalone_news"], "standalone_news"))

    @property
    def require_nonmissing(self) -> tuple[str, ...]:
        return tuple(self.value("sample.require_nonmissing"))

    @property
    def hedge_oc_column(self) -> str:
        return self.value("target.hedge_oc_column")

    @property
    def beta(self) -> BetaSpec:
        b = self.value("target.beta")
        return BetaSpec(b["method"], int(b["min_periods"]), int(b["lag_days"]),
                        b["estimate_on"], bool(b["continue_across_samples"]))

    @property
    def fx_block(self) -> tuple[str, ...]:
        return tuple(self.value("model.fx_block_common"))

    @property
    def controls(self) -> tuple[str, ...]:
        return tuple(self.value("model.controls_ticker_specific"))

    @property
    def h1_parameter(self) -> str:
        return self.value("model.h1_parameter")

    @property
    def h3_parameter(self) -> str:
        return self.value("model.h3_parameter")

    @property
    def alpha(self) -> float:
        return float(self.value("inference.alpha"))

    @staticmethod
    def dk_lag(T: int) -> int:
        return dk_lag(T)

    @property
    def huber_c(self) -> float:
        return float(self.value("robustness.huber.c"))

    @property
    def influence_k_max(self) -> int:
        return int(self.value("robustness.influence_curve.k_max"))

    def winsor_bounds(self) -> dict[str, tuple[float, float]]:
        v = self.value("robustness.winsorize_fx.values")  # raises if TO_FILL
        return {c: (float(lo), float(hi)) for c, (lo, hi) in v.items()}

    def rv_per_bar_dev_median(self) -> float:
        return float(self.value("secondary_family_holm.rv_per_bar_dev_median"))

    def sesoi(self) -> float:
        v = self.value("equivalence.sesoi")
        if v == PENDING:
            raise SpecPendingError("equivalence.sesoi is PENDING_COSTS; TOST viability is decided in Pass 4")
        return float(v)

    def forecast(self, key: str) -> Any:
        return self.value(f"forecast.{key}")
