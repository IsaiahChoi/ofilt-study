"""The confirmation module, the claim and rule rows (P4-4c1; P4Q38), as docs/P4_CONFIRM_CLAIMS_SPEC.md (version 1)
specifies.

`claim_rows` computes the 17 rows that confirm_inference.ITEM_OF gives to P4-4c (R10 to R26) from a document whose
P4-4a and P4-4b rows are filled, and `fill` writes them into it in place of its pending entries. Most rows record a
rule fixed before Pass 4, with its outcome and source; R10, R11, R14 and R21 read their decisions off rows already
computed; R12 adds the one quantity this module computes from the frames, the gap between the raw and the abnormal
target's a2 on O17's rows (section 4). `rows_from` is the pure part, which reads only the document and that gap.
`licensed` says when a claim is made: only on the confirmation panel (mode confirmation, provenance confirm_real); on
dev and on synthetic documents a claim's arithmetic is reported, never claimed (D14 P36 step 5). A claim whose inputs
include a not-estimable result is not made (P4Q31). The module reads the configuration through
confirm_inference.load_config, writes no file and draws no random number.
"""
from __future__ import annotations

import math
from typing import Any, Callable

import numpy as np
import pandas as pd

from . import blind, inference, targets
from .confirm_forecast import _check_inputs
from .confirm_inference import ITEM_OF, ROW_IDS, STATUSES, _plain, load_config
from .spec import Spec

ROWS = ("R10", "R11", "R12", "R13", "R14", "R15", "R16", "R17", "R18", "R19", "R20", "R21", "R22", "R23", "R24",
        "R25", "R26")
INTERIM_WORDING = "H1 and the CW forecast test may disagree; disagreement is not by itself evidence against H1"
ONE_SHOT_RULE = ("the confirmation panel is opened once, by the pre-registered script; any later change is a dated, "
                 "labelled deviation")
REPORTING_RULES = ("report every pre-registered result, including nulls", "accuracy always next to its base rate",
                   "nested comparisons by Clark-West", "importance permutation-based only")
A2_GAP_ROWS = {"H3": "O2", "copx_to_fcx": "O18", "xau_control": "O20", "raw_target": "O17"}


def licensed(doc: dict) -> bool:
    """True exactly when the document is the confirmation run on the confirmation panel."""
    return doc.get("mode") == "confirmation" and doc.get("provenance") == blind.CONFIRM_REAL


# ------------------------------------------------------------------ entries and contingencies (section 4)
class _NotEstimable(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _all_finite(x: Any) -> bool:
    if isinstance(x, float):
        return math.isfinite(x)
    if isinstance(x, dict):
        return all(_all_finite(v) for v in x.values())
    if isinstance(x, list):
        return all(_all_finite(v) for v in x)
    return True


def _row(rid: str, compute: Callable[[], tuple]) -> dict:
    """One entry: compute returns (status, values, reason); a not-estimable input or a non-finite float makes the
    row not estimable. Counts are None in every row."""
    try:
        status, values, reason = compute()
    except _NotEstimable as e:
        status, values, reason = "not_estimable", None, e.reason
    if status not in STATUSES or status == "pending":
        raise ValueError(f"{rid}: status {status!r}")
    values = _plain(values)
    if not _all_finite(values):
        status, values, reason = "not_estimable", None, "non-finite estimate"
    return {"id": rid, "item": ITEM_OF[rid], "status": status, "values": values, "reason": reason,
            "n_rows": None, "n_dates": None, "lag": None}


def _input(doc: dict, rid: str) -> dict:
    """The values of an input row, or the row is not estimable from it."""
    e = doc["rows"][rid]
    if e["status"] != "estimated":
        raise _NotEstimable(f"input {rid} not estimable: {e['reason']}")
    return e["values"]


def _if_estimated(doc: dict, rid: str, key: str):
    e = doc["rows"][rid]
    return e["values"][key] if e["status"] == "estimated" else None


def _summary(c: dict) -> dict:
    """docs/P4_CONFIRM_INF_SPEC.md section 4.4's summary of a parameter."""
    return {"estimate": float(c["estimate"]), "se": float(c["se"]), "z": float(c["z"]), "p": float(c["p"]),
            "ci": [float(c["ci"][0]), float(c["ci"][1])]}


# ------------------------------------------------------------------ R12's a2 gap: the frame C and the two fits
def _frame_C(dev, events, confirm, spec: Spec) -> pd.DataFrame:
    """The inference frame C exactly as confirm_inference.infer builds it (its specification, sections 3.3, 3.4)."""
    if confirm is not None:
        J = pd.concat([dev, confirm], ignore_index=True)
        J.attrs = {"provenance": blind.provenance_of(confirm)}
    else:
        J = dev.copy()
    T = targets.add_masks(targets.add_targets(J, spec), events, spec)
    if confirm is None:
        return T
    C = T.loc[(T["date"] >= confirm["date"].min()).to_numpy()]
    C.attrs = dict(T.attrs)
    return C


def _a2_gap(C: pd.DataFrame, spec: Spec) -> dict:
    """G of section 4, R12: a2 of the raw and of the abnormal target on the rows of O17 (D0's rows that the raw
    target's design also holds), and their difference; or {"status": "not_estimable", "reason"}."""
    h3 = spec.h3_parameter
    try:
        D0 = inference.build_design(C, spec)
        Dr = inference.build_design(C, spec, target="raw_oc")
        keep = np.isin(D0.index, Dr.index)
        if not keep.any():
            return {"status": "not_estimable", "reason": "no rows"}
        abn = inference.subset_design(D0, keep)
        raw = inference.subset_design(Dr, np.isin(Dr.index, abn.index))
        ra, rr = inference.fit_dk(abn, spec), inference.fit_dk(raw, spec)
    except inference.DesignError as e:
        return {"status": "not_estimable", "reason": str(e)}
    a2_abn, a2_raw = _summary(ra.param(h3)), _summary(rr.param(h3))
    G = {"a2_raw": a2_raw, "a2_abn": a2_abn, "difference": a2_raw["estimate"] - a2_abn["estimate"],
         "n_rows": int(rr.n), "n_dates": int(rr.T)}
    if not _all_finite(G):
        return {"status": "not_estimable", "reason": "non-finite estimate"}
    return G


# ------------------------------------------------------------------ the rows (section 4)
def _r10(doc, cfg, L):
    h1 = _input(doc, "R4")["reject"]
    c = cfg["claims"]["tier_i"]
    return "estimated", {"wording": c["wording"], "requires": c["requires"], "h1_rejected": h1, "licensed": L,
                         "claimed": bool(L and h1), "decision": "P4Q18"}, None


def _r11(doc, cfg, spec, L):
    h1 = _input(doc, "R4")["reject"]
    b_primary = _input(doc, "O1")["fit"]["estimate"]
    o21 = _input(doc, "O21")
    b_with, b_without, p_with = o21["with"]["estimate"], o21["without"]["estimate"], o21["with"]["p"]
    c1 = b_with != 0 and b_primary != 0 and (b_with > 0) == (b_primary > 0)
    c2 = p_with < spec.alpha
    ratio = b_with / b_without if (math.isfinite(b_without) and b_without != 0) else None
    c3 = ratio is not None and ratio >= 0.5          # a negative ratio (signs differ) is below 0.5 (P4Q16)
    return "estimated", {"wording": cfg["claims"]["tier_ii"]["wording"], "h1_rejected": h1, "b_primary": b_primary,
                         "b_with": b_with, "b_without": b_without, "p_with": p_with, "ratio": ratio,
                         "condition_1": bool(c1), "condition_2": bool(c2), "condition_3": bool(c3),
                         "eligible_dates": o21["eligible_dates"], "licensed": L,
                         "claimed": bool(L and h1 and c1 and c2 and c3), "decision": "P4Q16"}, None


def _r12(cfg, a2_gap):
    t = cfg["claims"]["tier_iii"]
    return "fixed", {"claimed": False, "report_without_tier_reading": t["report_without_tier_reading"],
                     "a2_reading": t["a2_reading"], "rows": dict(A2_GAP_ROWS), "a2_gap": a2_gap,
                     "decision": "P4Q17"}, None


def _r14(doc, cfg, viable, L):
    o10, o11 = _input(doc, "O10"), _input(doc, "O11")
    eq = cfg["claims"]["equivalence"]
    primary = o10["equivalent"]
    return "estimated", {"wording": eq["wording"], "viable": viable, "equivalent_primary": primary,
                         "equivalent_low": o11["low"]["equivalent"], "equivalent_high": o11["high"]["equivalent"],
                         "licensed": L, "claimed": bool(L and viable and primary), "beside": eq["beside"],
                         "mde80": cfg["constants"]["mde80"], "decision": "P4Q19"}, None


def _r20(doc):
    h1, cw = _if_estimated(doc, "R4", "reject"), _if_estimated(doc, "O36", "reject_calibrated")
    agree = (h1 == cw) if (h1 is not None and cw is not None) else None
    return "fixed", {"wording": INTERIM_WORDING, "binding_description": "the T3 cross-tab", "h1_rejected": h1,
                     "cw_reject_calibrated": cw, "agree": agree, "source": "PLAN 4.4; P79"}, None


def _r21(doc, cfg):
    h1 = _input(doc, "R4")["reject"]
    return "estimated", {"h1_rejected": h1, "null": not h1, "rule": cfg["claims"]["null_h1"]["rule"],
                         "mde80": cfg["constants"]["mde80"], "equivalence_row": "R14", "decision": "P4Q19"}, None


def _r23(doc):
    if doc.get("provenance") == blind.CONFIRM_REAL:
        return "fixed", {"rule": ONE_SHOT_RULE, "source": "P13(c)"}, None
    return "not_applicable", None, "the one-shot rule applies to the confirmation panel only"


def _r26(doc):
    others = [rid for rid in ROW_IDS if rid not in ROWS]
    return "fixed", {"rules": list(REPORTING_RULES),
                     "pending_rows": [rid for rid in others if doc["rows"][rid]["status"] == "pending"],
                     "not_estimable_rows": [rid for rid in others if doc["rows"][rid]["status"] == "not_estimable"]}, \
        None


def rows_from(doc: dict, a2_gap: dict, *, spec: Spec | None = None) -> dict:
    """Every row of section 4 read from the document, with R12's gap passed in; {id: entry} for exactly ROWS."""
    spec = spec or Spec.load()
    cfg = load_config()
    L = licensed(doc)
    viability = spec.value("equivalence.viability")
    viable = isinstance(viability, str) and viability.startswith("viable")
    compute = {
        "R10": lambda: _r10(doc, cfg, L),
        "R11": lambda: _r11(doc, cfg, spec, L),
        "R12": lambda: _r12(cfg, a2_gap),
        "R13": lambda: ("fixed", {"viability": viability, "viable": viable, "recomputed": False,
                                  "source": "P3-5; AM-07"}, None),
        "R14": lambda: _r14(doc, cfg, viable, L),
        "R15": lambda: ("fixed", {"h1_method": "dk_normal", "cw_reference": "calibrated",
                                  "c_cw_cal": cfg["constants"]["c_cw_cal"], "recomputed": False,
                                  "source": "P3-5"}, None),
        "R16": lambda: ("fixed", {"rule": "DK-normal, selected for H1, applies to every other pre-registered DK test",
                                  "reference": spec.value("inference.reference"), "source": "D3.5"}, None),
        "R17": lambda: ("fixed", {"selected_for_confirmation": False, "recomputed": False,
                                  "source": "P73; P79"}, None),
        "R18": lambda: ("fixed", {"recomputed": False, "not_examined_on_dev": cfg["not_examined_on_dev"]["items"],
                                  "decision": "P4Q26", "source": "P75"}, None),
        "R19": lambda: ("fixed", {"rows_flagged": [], "recomputed": False, "source": "P3-5"}, None),
        "R20": lambda: _r20(doc),
        "R21": lambda: _r21(doc, cfg),
        "R22": lambda: ("fixed", {"spec_seed": spec.seed, "walk_forward_seed": "the spec seed (P4Q27)",
                                  "fold_seed": "seed + 1000 * fold", "m7_noise": "default_rng([fold seed, stream])",
                                  "importance": "default_rng([fold seed, 2, repeat])"}, None),
        "R23": lambda: _r23(doc),
        "R24": lambda: ("fixed", {"recovery": cfg["dry_run"]["recovery"]["rule"],
                                  "seeds": cfg["dry_run"]["seeds"]["rule"], "item": "P4-5",
                                  "decisions": ["P4Q28", "P4Q29"]}, None),
        "R25": lambda: ("not_applicable", None, cfg["forward_holdout"]["rule"] + " (P4Q30); outside Pass 4"),
        "R26": lambda: _r26(doc),
    }
    return {rid: _row(rid, compute[rid]) for rid in ROWS}


def claim_rows(doc: dict, dev, events, confirm=None, *, spec: Spec | None = None) -> dict:
    """{id: entry} for exactly ROWS, for a document computed on these frames (section 3)."""
    _check_inputs(dev, confirm)
    mode = "confirmation" if confirm is not None else "dev"
    if doc.get("mode") != mode:
        raise ValueError(f"the document's mode is {doc.get('mode')!r}; these frames give {mode!r}")
    provenance = blind.provenance_of(confirm if confirm is not None else dev)
    if doc.get("provenance") != provenance:
        raise ValueError(f"the document's provenance is {doc.get('provenance')!r}; these frames give {provenance!r}")
    spec = spec or Spec.load()
    return rows_from(doc, _a2_gap(_frame_C(dev, events, confirm, spec), spec), spec=spec)


# ------------------------------------------------------------------ fill
def fill(doc: dict, rows: dict) -> dict:
    """A copy of the document (made with _plain) with each entry of `rows` in place of the pending P4-4c entry."""
    if set(rows) != set(ROWS) or len(rows) != len(ROWS):
        raise ValueError("rows must hold exactly the IDs of ROWS")
    out = _plain(doc)
    for rid in ROWS:
        old, new = out["rows"][rid], rows[rid]
        if old.get("status") != "pending" or old.get("item") != "P4-4c":
            raise ValueError(f"{rid}: the document's entry is not a pending P4-4c entry")
        if new.get("id") != rid or new.get("item") != "P4-4c":
            raise ValueError(f"{rid}: the new entry's id or item does not match")
        out["rows"][rid] = _plain(new)
    return out
