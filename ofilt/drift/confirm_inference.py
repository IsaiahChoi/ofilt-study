"""The confirmation module, inference rows (P4-4a; P4Q35), as docs/P4_CONFIRM_INF_SPEC.md (version 2) specifies.

`infer` computes the 36 inference rows of the audit (reports/P4_reports/p4_1_audit.md, section 1: O1 to O28 and R1 to
R8) and returns the output document, with one entry for each of the 71 audit IDs; the rows of P4-4b and P4-4c stay
`pending`. The provenance pair is checked first, and the blinding guard runs on both frames before any target is built
(section 3.2). Every design comes from inference.build_design or the library functions that call it; a derived design
(section 6) re-arranges build_design's output. Every row goes through one helper, `_row`, which applies the
contingencies of section 5 (P4Q31), so the run never stops to ask. The module reads one file, the configuration, whose
SHA-256 it pins; it writes no file and draws no random number.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from typing import Any, Callable

import numpy as np
import pandas as pd

from . import blind, calib, inference, targets
from .spec import REPO_ROOT, Spec

CONFIG_PATH = REPO_ROOT / "docs" / "P4_CONFIRM_CONFIG.json"
CONFIG_SHA256 = "5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd"
TICKERS = ("5706", "5711", "5713")
ROW_IDS = (("O1", "R1", "R2", "R3", "R4", "R5", "O2", "O3", "O4", "O5", "O6", "R6")
           + tuple(f"O{i}" for i in range(7, 29)) + ("R7", "R8")
           + tuple(f"O{i}" for i in range(29, 36)) + ("R9",)
           + tuple(f"O{i}" for i in range(36, 46)) + tuple(f"R{i}" for i in range(10, 27)))
_P4A = frozenset([f"O{i}" for i in range(1, 29)] + [f"R{i}" for i in range(1, 9)])
_P4B = frozenset([f"O{i}" for i in range(29, 46)] + ["R9"])
ITEM_OF = {i: "P4-4a" if i in _P4A else "P4-4b" if i in _P4B else "P4-4c" for i in ROW_IDS}
STATUSES = ("estimated", "not_estimable", "not_applicable", "fixed", "pending")
SECONDARY_ROWS = ("O3", "O4", "O5", "O6")          # in the order of inference.SECONDARY_TERMS
WITH_WITHOUT_ROWS = ("O15", "O16", "O17", "O18", "O19", "O20", "O21", "O22")
EXCLUSION_ROWS = (("O23", "exclusion_d_plus_2", "excl_d2"), ("O24", "exclude_audit_flag", "audit_flag"),
                  ("O25", "exclude_boj_day", "boj_day"), ("O26", "exclude_sq_major", "sq_major"))
R3_RULE = "Bartlett kernel, L = floor(4 (T/100)^(2/9))"


# ------------------------------------------------------------------ configuration and plain types
def load_config(path=None) -> dict:
    """The configuration's decoded content; ValueError unless its SHA-256 is CONFIG_SHA256 and its rows are ROW_IDS."""
    p = CONFIG_PATH if path is None else type(CONFIG_PATH)(path)
    data = p.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != CONFIG_SHA256:
        raise ValueError(f"configuration {p} has SHA-256 {digest}, not {CONFIG_SHA256}")
    cfg = json.loads(data.decode("utf-8"))
    if not isinstance(cfg.get("rows"), dict) or tuple(cfg["rows"]) != ROW_IDS:
        raise ValueError("the configuration's rows are not ROW_IDS, in order")
    return cfg


def _iso(x) -> str:
    return pd.Timestamp(x).strftime("%Y-%m-%d")


def _plain(x: Any) -> Any:
    """The plain-typed form of section 4.3: str, int, float, bool, None, list or dict; dates as YYYY-MM-DD."""
    if x is None or isinstance(x, str):
        return x
    if x is pd.NaT:
        return None
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return float(x)
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)):
        return [_plain(v) for v in x]
    if isinstance(x, (pd.Timestamp, np.datetime64)):
        return None if pd.isna(x) else _iso(x)
    raise TypeError(f"no plain form for {type(x).__name__}")


def _all_finite(x: Any) -> bool:
    if isinstance(x, float):
        return math.isfinite(x)
    if isinstance(x, dict):
        return all(_all_finite(v) for v in x.values())
    if isinstance(x, list):
        return all(_all_finite(v) for v in x)
    return True


def _endpoint(x) -> float | None:
    x = float(x)
    return None if math.isinf(x) else x


def _interval(ci) -> list:
    if len(ci) and isinstance(ci[0], (tuple, list, np.ndarray)):
        return [_interval(c) for c in ci]
    return [_endpoint(x) for x in ci]


def encode_fraction(fr: dict) -> dict:
    """The plain-typed form of a dict that inference.fraction_from or fraction_unpriced returns (section 4.3): each
    infinite endpoint of the Fieller set is None; its kind says the shape."""
    return {"f": float(fr["f"]), "se_delta": float(fr["se_delta"]),
            "ci_delta": [float(fr["ci_delta"][0]), float(fr["ci_delta"][1])],
            "fieller": {"kind": str(fr["fieller"]["kind"]), "ci": _interval(fr["fieller"]["ci"])},
            "t_denominator": float(fr["t_denominator"]), "b": float(fr["b"]), "delta_cc": float(fr["delta_cc"]),
            "alpha": float(fr["alpha"])}


def to_json(doc) -> str:
    return json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


# ------------------------------------------------------------------ the contingencies (section 5)
class _NotEstimable(Exception):
    """A contingency of section 5 met inside a row: the row is not estimable, with its reason and counts."""

    def __init__(self, reason: str, n_rows: int | None = None, n_dates: int | None = None):
        super().__init__(reason)
        self.reason, self.n_rows, self.n_dates = reason, n_rows, n_dates


@dataclasses.dataclass
class _Out:
    status: str
    values: Any = None
    reason: str | None = None
    n_rows: int | None = None
    n_dates: int | None = None
    lag: int | None = None


def _counts(r) -> dict:
    return {"n_rows": int(r.n), "n_dates": int(r.T), "lag": int(r.lag)}


def _row(rid: str, compute: Callable[[], _Out]) -> dict:
    """The one helper of section 5: computes a row's entry and applies the contingencies."""
    try:
        out = compute()
    except _NotEstimable as e:
        out = _Out("not_estimable", None, e.reason, e.n_rows, e.n_dates, None)
    except inference.DesignError as e:
        out = _Out("not_estimable", None, str(e))
    values = _plain(out.values)
    if not _all_finite(values):
        out = _Out("not_estimable", None, "non-finite estimate", out.n_rows, out.n_dates, out.lag)
        values = None
    return {"id": rid, "item": ITEM_OF[rid], "status": out.status, "values": values, "reason": out.reason,
            "n_rows": _plain(out.n_rows), "n_dates": _plain(out.n_dates), "lag": _plain(out.lag)}


def _pending(rid: str) -> dict:
    return {"id": rid, "item": ITEM_OF[rid], "status": "pending", "values": None, "reason": None,
            "n_rows": None, "n_dates": None, "lag": None}


def _restrict(design, mask):
    """Section 6's restriction, after the no-rows check (subset_design with no row raises a numpy ValueError)."""
    mask = np.asarray(mask, dtype=bool)
    if not mask.any():
        raise _NotEstimable("no rows", 0, 0)
    return inference.subset_design(design, mask)


def _derive(design, new_cols, new_names, drop=()):
    """Section 6's derived design: the columns named in `drop` removed, the new ones appended, then the rank check.
    Appending is np.column_stack([design.X, *new]) as section 6 writes it; a removal uses np.delete, which also keeps
    the C layout (the layout changes the last bits of the fit)."""
    gone = [j for j, n in enumerate(design.names) if n in drop]
    X = np.column_stack([np.delete(design.X, gone, axis=1) if gone else design.X, *new_cols])
    names = tuple(n for n in design.names if n not in drop) + tuple(new_names)
    derived = dataclasses.replace(design, X=X, names=names)
    if np.linalg.matrix_rank(derived.X) < derived.X.shape[1]:
        raise _NotEstimable("rank-deficient design", len(derived.y), int(derived.T))
    return derived


def _summary(c: dict) -> dict:
    """Section 4.4's summary of a parameter or contrast."""
    return {"estimate": float(c["estimate"]), "se": float(c["se"]), "z": float(c["z"]), "p": float(c["p"]),
            "ci": [float(c["ci"][0]), float(c["ci"][1])]}


def _param(r, name: str) -> dict:
    return _summary(r.param(name))


def _tost(t: dict) -> dict:
    return {k: t[k] for k in ("p", "p_lower", "p_upper", "equivalent", "ci", "sesoi", "alpha")}


# ------------------------------------------------------------------ one run
class _Run:
    """The frames, the configuration and the primary design and fit of one call of infer (sections 3 and 6)."""

    def __init__(self, spec: Spec, cfg: dict, mode: str, C, C250, C500, periods: dict):
        self.spec, self.cfg, self.mode = spec, cfg, mode
        self.C, self.C250, self.C500, self.periods = C, C250, C500, periods
        self.h1 = spec.h1_parameter
        self.D0 = self.r0 = None
        try:
            self.D0 = inference.build_design(C, spec)
            self.r0 = inference.fit_dk(self.D0, spec)
            p = self.r0.param(self.h1)
            self.base_reason = None if (math.isfinite(p["estimate"]) and math.isfinite(p["se"])) \
                else "non-finite estimate"
        except inference.DesignError as e:
            self.D0 = self.r0 = None
            self.base_reason = str(e)

    def need(self):
        """D0 and r0, or the row is not estimable with their reason (section 5, rows built on the primary fit)."""
        if self.base_reason is not None:
            raise _NotEstimable(self.base_reason)
        return self.D0, self.r0

    def fit(self, design):
        return inference.fit_dk(design, self.spec)

    def at(self, design, column: str) -> np.ndarray:
        """Frame values at the design's rows (section 6's row masks and added columns)."""
        return self.C.loc[design.index, column].to_numpy(dtype=float)

    def ticker_specific(self, design, column: str):
        v = self.at(design, column)
        return [v * (design.tickers == t) for t in TICKERS], [f"{column}:{t}" for t in TICKERS]

    # ---- O1, R1 to R5, O2
    def o1(self) -> _Out:
        _, r0 = self.need()
        return _Out("estimated", {"param": self.h1, "fit": _param(r0, self.h1)}, **_counts(r0))

    def r1(self) -> _Out:
        return _Out("fixed", {"target": "abn_oc", "beta": self.C.attrs["targets"]})

    def r2(self) -> _Out:
        D0, r0 = self.need()
        c_dates = np.unique(self.C["date"].to_numpy(dtype="datetime64[ns]"))
        none_in_d0 = int(np.setdiff1d(c_dates, np.unique(D0.dates)).size)
        t_conf = self.cfg["frame"]["confirmation"]["t_conf"] if self.mode == "confirmation" else None
        return _Out("estimated", {"exclusion_flags": list(self.spec.inference_exclusion_flags),
                                  "require_nonmissing": list(self.spec.require_nonmissing),
                                  "rows": len(D0.y), "dates": int(D0.T), "dates_all_excluded": none_in_d0,
                                  "t_conf_expected": t_conf,
                                  "matches_t_conf": None if t_conf is None else bool(D0.T == t_conf)}, **_counts(r0))

    def r3(self) -> _Out:
        D0, r0 = self.need()
        return _Out("fixed", {"rule": R3_RULE, "T": int(D0.T), "lag": int(r0.lag)}, **_counts(r0))

    def r4(self, o1: dict) -> _Out:
        if o1["status"] != "estimated":
            raise _NotEstimable(o1["reason"])
        _, r0 = self.need()
        alpha, p = self.spec.alpha, o1["values"]["fit"]["p"]
        return _Out("estimated", {"alpha": alpha, "p": p, "reject": bool(p < alpha)}, **_counts(r0))

    def r5(self) -> _Out:
        return _Out("fixed", {"method": "DK-normal", "decision": "D3.4"})

    def o2(self) -> _Out:
        _, r0 = self.need()
        h3 = self.spec.h3_parameter
        return _Out("estimated", {"param": h3, "fit": _param(r0, h3)}, **_counts(r0))

    # ---- O3 to O6 and R6
    def secondary(self, term: str) -> _Out:
        r = self.fit(inference.build_design(self.C, self.spec, secondary=term))
        values = {"member": term, "tested": _summary(r.contrast(inference.SECONDARY_TESTED[term]))}
        if term == "fx_asymmetry":        # e_pos and e_neg replace usdjpy_ret in this design
            values["e_pos"], values["e_neg"] = _param(r, "e_pos"), _param(r, "e_neg")
        else:
            values["h1"] = _param(r, self.h1)
        return _Out("estimated", values, **_counts(r))

    @staticmethod
    def holm_family(p) -> dict:
        """A Holm family's p-values, a not-estimable member entering with p = 1 (section 5)."""
        return {"p": [float(x) for x in p], "p_holm": [float(x) for x in inference.holm(p)]}

    def r6(self, entries: list) -> _Out:
        p = [e["values"]["tested"]["p"] if e["status"] == "estimated" else 1.0 for e in entries]
        values = {"members": list(SECONDARY_ROWS), **self.holm_family(p),
                  "not_estimable": [e["id"] for e in entries if e["status"] != "estimated"]}
        return _Out("estimated", values)

    # ---- O7 and O8
    def fraction_part(self, F, lo: str, hi: str) -> dict:
        part = {"status": "estimated", "reason": None, "from": lo, "to": hi, "b": None, "delta_cc": None,
                "f_defined": False, "f": None, "se_delta": None, "ci_delta": None, "fieller": None,
                "t_denominator": None, "n_rows": None, "n_dates": None, "lag": None}
        try:
            J = inference.fit_joint(F, self.spec)
        except inference.DesignError as e:
            part.update(status="not_estimable", reason=str(e))
            return part
        b, d, _ = J.pair(self.h1)
        part.update(n_rows=int(J.n), n_dates=int(J.T), lag=int(J.lag))
        if not (math.isfinite(b) and math.isfinite(d)):
            part.update(status="not_estimable", reason="non-finite estimate")
            return part
        part.update(b=float(b), delta_cc=float(d), f_defined=bool(d != 0.0))
        if part["f_defined"]:
            fr = encode_fraction(inference.fraction_unpriced(J, self.h1))
            if not (math.isfinite(fr["f"]) and math.isfinite(fr["se_delta"])):
                part.update(status="not_estimable", reason="non-finite estimate", f_defined=False)
                return part
            part.update({k: fr[k] for k in ("f", "se_delta", "ci_delta", "fieller", "t_denominator")})
        return part

    def o7(self) -> _Out:
        if self.mode == "confirmation":
            fc, fd = self.cfg["f"]["confirmatory"], self.cfg["f"]["descriptive"]
            main = self.fraction_part(self.periods["confirmatory"], fc["from"], fc["to"])
            values = {"confirmatory": main,
                      "descriptive": self.fraction_part(self.periods["descriptive"], fd["from"], fd["to"])}
        else:
            main = self.fraction_part(self.C, _iso(self.C["date"].min()), _iso(self.C["date"].max()))
            main["label"] = self.cfg["f"]["dev"]["label"]
            values = {"dev_stand_in": main}
        counts = {k: main[k] for k in ("n_rows", "n_dates", "lag")}
        return _Out(main["status"], values, main["reason"], **counts)

    def o8(self) -> _Out:
        f = self.cfg["f"]
        if self.mode != "confirmation":
            return _Out("not_applicable", None, f["dev"]["periods"])
        return _Out("fixed", {"confirmatory": [f["confirmatory"]["from"], f["confirmatory"]["to"]],
                              "descriptive": [f["descriptive"]["from"], f["descriptive"]["to"]],
                              "disclosure": f["disclosure"]})

    # ---- O9 to O14
    def o9(self) -> _Out:
        dec = inference.decomposition(self.C, self.spec)
        counts = _counts(self.r0) if self.base_reason is None else {}
        return _Out("estimated", {k: float(v) for k, v in dec.items()}, **counts)

    def o10(self) -> _Out:
        _, r0 = self.need()
        sesoi = self.cfg["constants"]["sesoi"]["primary"]
        return _Out("estimated", _tost(inference.tost_result(r0, self.h1, self.spec, sesoi=sesoi)), **_counts(r0))

    def o11(self) -> _Out:
        _, r0 = self.need()
        s = self.cfg["constants"]["sesoi"]
        return _Out("estimated", {k: _tost(inference.tost_result(r0, self.h1, self.spec, sesoi=s[k]))
                                  for k in ("low", "high")}, **_counts(r0))

    def o12(self) -> _Out:
        D0, _ = self.need()
        rh = inference.fit_huber(D0, self.spec)
        return _Out("estimated", _param(rh, self.h1), **_counts(rh))

    def o13(self) -> _Out:
        W = calib.winsorise_fx(self.C, self.spec)
        rw = self.fit(inference.build_design(W, self.spec))
        return _Out("estimated", _param(rw, self.h1), **_counts(rw))

    def o14(self) -> _Out:
        D0, r0 = self.need()
        curve = inference.influence_curve(D0, self.spec)
        return _Out("estimated", {"curve": curve.to_dict("records")}, **_counts(r0))

    # ---- O15 to O22: with and without on the same rows (R8)
    def with_without(self, name: str, without, derived, extra: Callable | None = None) -> _Out:
        """`extra`, if given, maps the `with` fit to the row's further values."""
        D0, r0 = self.need()
        rw, rd = self.fit(without), self.fit(derived)
        values = {"name": name, "primary": _param(r0, self.h1), "with": _param(rd, self.h1),
                  "without": _param(rw, self.h1), "dropped_rows": len(D0.y) - int(rd.n),
                  "dropped_dates": int(D0.T) - int(rd.T)}
        if extra is not None:
            values.update(extra(rd))
        return _Out("estimated", values, **_counts(rd))

    def rebuilt(self, name: str, frame, target: str = "abn_oc") -> _Out:
        """O15 to O17: the design built again (another beta or target); both fits on the rows of D0 and of it."""
        D0, _ = self.need()
        Dr = inference.build_design(frame, self.spec, target=target)
        without = _restrict(D0, np.isin(D0.index, Dr.index))
        derived = _restrict(Dr, np.isin(Dr.index, without.index))
        return self.with_without(name, without, derived)

    def augmented(self, name: str, mask_of: Callable, columns_of: Callable, drop=(), extra=None) -> _Out:
        """O18 to O22: D0 restricted by the row's mask (without), and the derived design on those rows (with)."""
        D0, _ = self.need()
        without = _restrict(D0, mask_of(D0))
        cols, names = columns_of(without)
        return self.with_without(name, without, _derive(without, cols, names, drop), extra)

    def finite(self, *columns):
        return lambda design: np.logical_and.reduce([np.isfinite(self.at(design, c)) for c in columns])

    def o15(self) -> _Out:
        return self.rebuilt("beta_rolling_250", self.C250)

    def o16(self) -> _Out:
        return self.rebuilt("beta_rolling_500", self.C500)

    def o17(self) -> _Out:
        return self.rebuilt("raw_target", self.C, target="raw_oc")

    def o18(self) -> _Out:
        return self.augmented("copx_to_fcx", self.finite("fcx_oc"), lambda d: self.ticker_specific(d, "fcx_oc"),
                              drop=tuple(f"copx_oc:{t}" for t in TICKERS))

    def o19(self) -> _Out:
        return self.augmented("ewj_yen_denominated", self.finite("ewj_oc_jpy"),
                              lambda d: self.ticker_specific(d, "ewj_oc_jpy"))

    def o20(self) -> _Out:
        return self.augmented("xau_control", self.finite("xau_ret"), lambda d: self.ticker_specific(d, "xau_ret"))

    @staticmethod
    def nikkei_mask(values: Callable[[str], np.ndarray]) -> np.ndarray:
        """n225_stale_start_min <= 5, n225_stale_end_min <= 5 and a finite n225_ret; a missing value fails."""
        return ((values("n225_stale_start_min") <= 5) & (values("n225_stale_end_min") <= 5)
                & np.isfinite(values("n225_ret")))

    def o21(self) -> _Out:
        C = self.C
        eligible = self.nikkei_mask(lambda c: C[c].to_numpy(dtype=float))
        n_eligible = int(C.loc[eligible, "date"].nunique())
        return self.augmented("nikkei_proxy_p42", lambda d: self.nikkei_mask(lambda c: self.at(d, c)),
                              lambda d: self.ticker_specific(d, "n225_ret"),
                              extra=lambda rd: {"eligible_dates": n_eligible})

    def o22(self) -> _Out:
        added = ("c_usdjpy_sess_ret", "c_eurusd_sess_ret", "gotobi_day")
        product = f"{self.h1}:gotobi_day"

        def columns_of(d):
            return ([self.at(d, c) for c in added] + [self.at(d, self.h1) * self.at(d, "gotobi_day")],
                    list(added) + [product])

        return self.augmented("mechanism_session_fx_gotobi", self.finite(*added), columns_of,
                              extra=lambda rd: {"coefficients": {n: _param(rd, n) for n in list(added) + [product]}})

    # ---- O23 to O28 and R7
    def exclusion(self, name: str, extra: str) -> _Out:
        _, r0 = self.need()
        excluded = list(self.spec.inference_exclusion_flags) + [extra]
        r = self.fit(inference.build_design(self.C, self.spec, exclude=excluded))
        return _Out("estimated", {"name": name, "excluded_columns": excluded, "fit": _param(r, self.h1),
                                  "primary": _param(r0, self.h1)}, **_counts(r))

    def o27(self) -> _Out:
        if self.mode != "confirmation":
            return _Out("not_applicable", None,
                        self.cfg["robustness"]["post_2024_11_05_indicator_CONFIRMATION_ONLY"]["on_dev"])
        D0, r0 = self.need()
        brk = np.datetime64(pd.Timestamp(self.cfg["constants"]["post_break_date"]))
        post = (D0.dates >= brk).astype(float)
        inter = f"{self.h1}:post"
        rd = self.fit(_derive(D0, [post, self.at(D0, self.h1) * post], ["post", inter]))
        return _Out("estimated", {"b_pre": _param(rd, self.h1), "interaction": _param(rd, inter),
                                  "b_post": _summary(rd.contrast({self.h1: 1.0, inter: 1.0})),
                                  "primary": _param(r0, self.h1)}, **_counts(rd))

    def o28(self) -> _Out:
        D0, r0 = self.need()
        fx = list(self.spec.fx_block)
        cols, names = [], []
        for c in fx:
            cc, nn = self.ticker_specific(D0, c)
            cols += cc
            names += nn
        rd = self.fit(_derive(D0, cols, names, drop=tuple(fx)))
        return _Out("estimated", {"slopes": {t: _param(rd, f"{self.h1}:{t}") for t in TICKERS},
                                  "primary": _param(r0, self.h1)}, **_counts(rd))

    def r7(self, o28: dict) -> _Out:
        if o28["status"] == "estimated":
            p = [o28["values"]["slopes"][t]["p"] for t in TICKERS]
        else:
            p = [1.0] * len(TICKERS)
        return _Out("estimated", {"tickers": list(TICKERS), **self.holm_family(p)})

    def r8(self) -> _Out:
        return _Out("fixed", {"rule": self.cfg["robustness"]["reporting_form"]["with_and_without_rule"],
                              "rows": list(WITH_WITHOUT_ROWS)})


# ------------------------------------------------------------------ the entry point
def _rows_of(frame, keep) -> pd.DataFrame:
    out = frame.loc[keep]
    out.attrs = dict(frame.attrs)
    return out


def infer(dev, events, confirm=None, *, spec=None) -> dict:
    """The output document of section 4 for the dev frame alone (dev mode) or with the confirmation frame."""
    p_dev = blind.provenance_of(dev)
    if confirm is None:
        if p_dev not in (blind.SYNTHETIC, blind.DEV_REAL):
            raise ValueError(f"dev mode needs a synthetic or dev_real frame, got provenance {p_dev!r}")
    else:
        p_conf = blind.provenance_of(confirm)
        if (p_dev, p_conf) not in ((blind.SYNTHETIC, blind.SYNTHETIC), (blind.DEV_REAL, blind.CONFIRM_REAL)):
            raise ValueError(f"refused provenance pair ({p_dev!r}, {p_conf!r})")
    blind.require_unblinded(dev)
    if confirm is not None:
        blind.require_unblinded(confirm)
    spec = spec or Spec.load()
    cfg = load_config()

    if confirm is not None:
        mode = "confirmation"
        J = pd.concat([dev, confirm], ignore_index=True)
        J.attrs = {"provenance": blind.provenance_of(confirm)}
    else:
        mode = "dev"
        J = dev.copy()
    T = targets.add_masks(targets.add_targets(J, spec), events, spec)
    T250 = targets.add_targets(J, spec, method="rolling", window=250)
    T500 = targets.add_targets(J, spec, method="rolling", window=500)
    periods = {}
    if mode == "confirmation":
        keep = (T["date"] >= confirm["date"].min()).to_numpy()
        C, C250, C500 = _rows_of(T, keep), _rows_of(T250, keep), _rows_of(T500, keep)
        for part in ("confirmatory", "descriptive"):
            lo, hi = (pd.Timestamp(cfg["f"][part][k]) for k in ("from", "to"))
            periods[part] = _rows_of(C, ((C["date"] >= lo) & (C["date"] <= hi)).to_numpy())
    else:
        C, C250, C500 = T, T250, T500

    run = _Run(spec, cfg, mode, C, C250, C500, periods)
    rows: dict = {}
    rows["O1"] = _row("O1", run.o1)
    rows["R1"] = _row("R1", run.r1)
    rows["R2"] = _row("R2", run.r2)
    rows["R3"] = _row("R3", run.r3)
    rows["R4"] = _row("R4", lambda: run.r4(rows["O1"]))
    rows["R5"] = _row("R5", run.r5)
    rows["O2"] = _row("O2", run.o2)
    for rid, term in zip(SECONDARY_ROWS, inference.SECONDARY_TERMS):
        rows[rid] = _row(rid, lambda term=term: run.secondary(term))
    rows["R6"] = _row("R6", lambda: run.r6([rows[i] for i in SECONDARY_ROWS]))
    for rid in ("O7", "O8", "O9", "O10", "O11", "O12", "O13", "O14") + WITH_WITHOUT_ROWS:
        rows[rid] = _row(rid, getattr(run, rid.lower()))
    for rid, name, extra in EXCLUSION_ROWS:
        rows[rid] = _row(rid, lambda name=name, extra=extra: run.exclusion(name, extra))
    rows["O27"] = _row("O27", run.o27)
    rows["O28"] = _row("O28", run.o28)
    rows["R7"] = _row("R7", lambda: run.r7(rows["O28"]))
    rows["R8"] = _row("R8", run.r8)

    return {"module": "confirm_inference", "spec_version": 1, "config_sha256": CONFIG_SHA256, "mode": mode,
            "provenance": J.attrs["provenance"],
            "dates": {"first": _iso(C["date"].min()), "last": _iso(C["date"].max()), "n": int(C["date"].nunique())},
            "rows": {rid: rows[rid] if ITEM_OF[rid] == "P4-4a" else _pending(rid) for rid in ROW_IDS}}
