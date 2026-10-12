"""The confirmation run (P4-4c2; P4Q39), as docs/P4_CONFIRM_RUN_SPEC.md (version 1) specifies.

`build_document` assembles the whole confirmation document, in order: P4-4a's inference rows
(confirm_inference.infer, which checks the provenance pair and runs the guard first), P4-4b1's forecasting rows and
P4-4b2's economic row (one confirm_forecast.run_calls), and P4-4c1's claim and rule rows; it refuses a document with a
missing or pending row. `manifest` describes the document from its own fields and pinned constants; `write_outputs`
writes document.json, manifest.json and runtime.json into a new folder; `documents_equal` compares two such folders
without their runtime files (P4Q5: two runs on the same inputs give byte-identical documents and manifests). The
runtime fields (UTC times, wall time, the registry's run ids) live in runtime.json only. Each forecasting call records
to the registry its provenance selects (P4Q6). The module reads no file itself, except in documents_equal, and writes
files only in write_outputs.
"""
from __future__ import annotations

import dataclasses
import datetime
import json
import time
from pathlib import Path
from typing import Any

from . import confirm_claims, confirm_economic, confirm_forecast, confirm_inference
from .spec import Spec

SPEC_FILES = (
    ("docs/P4_CONFIRM_INF_SPEC.md", 2, "a7ebb94f003c3b893e96b222b796ea9fda09c849217c526bfdfc8d2b6be51f65"),
    ("docs/P4_CONFIRM_FC_SPEC.md", 1, "a8d3a9c91ca7a3d6bf551f95a56e3e4cf43ec14ed6b4f0d450c751589f795bd6"),
    ("docs/P4_CONFIRM_ECON_SPEC.md", 1, "42e1488330ae7bb3c947fb92a6958c851197aaad6d9e545a5e3ef81511432785"),
    ("docs/P4_CONFIRM_CLAIMS_SPEC.md", 1, "b499e820c62961b79bfc0ec839d6014e918657f79071182104fbdc1f4d4dbbf2"),
)
OUTPUT_FILES = ("document.json", "manifest.json", "runtime.json")
COMPARED_FILES = ("document.json", "manifest.json")
DEV_RUN_SANCTION_VAR = "OFILT_P4_DEV_RUN"
DEV_RUN_SANCTION_VALUE = "P4-6"
MANIFEST_OUTPUT = "the confirmation document of Pass 4 (P4Q35 to P4Q39)"
SCHEMA_VERSION_MEANING = ("the version of the document's schema, docs/P4_CONFIRM_INF_SPEC.md section 4.1; the "
                          "specifications' own versions are under specifications")
RUNTIME_FIELDS = ("runtime.json only: utc_start, utc_end, wall_seconds and the registry's run ids; document.json and "
                  "manifest.json are identical across runs on the same inputs (P4Q5)")


@dataclasses.dataclass
class Assembled:
    doc: dict
    calls: Any
    runtime: dict


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _sha256(data: bytes) -> str:
    """The SHA-256 of bytes. Section 1.1's import list holds no hashlib, so the hash function is reached through
    confirm_inference, which imports it to pin the configuration (a reading recorded at P4-4c2)."""
    return confirm_inference.hashlib.sha256(data).hexdigest()


def _dumps(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


# ------------------------------------------------------------------ section 3.1
def build_document(dev, events, confirm=None, *, spec: Spec | None = None, factories=None) -> Assembled:
    """The whole document for the dev frame alone (dev mode) or with the confirmation frame, and its runtime."""
    start, t0 = _utc(), time.perf_counter()
    doc = confirm_inference.infer(dev, events, confirm, spec=spec)
    calls = confirm_forecast.run_calls(dev, events, confirm, spec=spec, factories=factories)
    doc = confirm_forecast.fill(doc, confirm_forecast.forecast_rows(calls))
    doc = confirm_economic.fill(doc, confirm_economic.economic_row(calls, dev, events, confirm, spec=spec))
    doc = confirm_claims.fill(doc, confirm_claims.claim_rows(doc, dev, events, confirm, spec=spec))
    if list(doc["rows"]) != list(confirm_inference.ROW_IDS):
        raise ValueError("the document does not hold exactly the 71 IDs of ROW_IDS, in order")
    pending = [rid for rid, e in doc["rows"].items() if e["status"] == "pending"]
    if pending:
        raise ValueError(f"the document has pending rows: {pending}")
    runtime = {"utc_start": start, "utc_end": _utc(), "wall_seconds": time.perf_counter() - t0,
               "run_ids": {"main": calls.main.run_id, "m7": calls.m7.run_id}}
    return Assembled(doc, calls, runtime)


# ------------------------------------------------------------------ section 3.2
def manifest(doc: dict, *, spec: Spec | None = None) -> dict:
    """The manifest, from the document and constants only (deterministic)."""
    spec = spec or Spec.load()
    return {"output": MANIFEST_OUTPUT, "files": list(OUTPUT_FILES),
            "document_schema_version": doc["spec_version"], "document_schema_version_meaning": SCHEMA_VERSION_MEANING,
            "specifications": [{"path": p, "version": v, "sha256": h} for p, v, h in SPEC_FILES],
            "config_sha256": confirm_inference.CONFIG_SHA256, "cost_inputs_sha256": confirm_economic.COST_INPUTS_SHA256,
            "analysis_spec_sha256": spec.sha256, "mode": doc["mode"], "provenance": doc["provenance"],
            "dates": doc["dates"], "runtime_fields": RUNTIME_FIELDS}


# ------------------------------------------------------------------ sections 3.3 and 3.4
def write_outputs(out_dir, assembled: Assembled, *, spec: Spec | None = None) -> dict:
    """Writes the three files into a new folder; returns {name: SHA-256 of the bytes written}."""
    out = Path(out_dir)
    if out.exists():
        raise FileExistsError(f"{out} exists")
    out.mkdir(parents=True)
    texts = {"document.json": confirm_inference.to_json(assembled.doc),
             "manifest.json": _dumps(manifest(assembled.doc, spec=spec)),
             "runtime.json": _dumps(assembled.runtime)}
    hashes = {}
    for name in OUTPUT_FILES:
        data = texts[name].encode("utf-8")
        (out / name).write_bytes(data)
        hashes[name] = _sha256(data)
    return hashes


def documents_equal(a_dir, b_dir) -> bool:
    """True when document.json and manifest.json are byte-identical in the two folders."""
    a, b = Path(a_dir), Path(b_dir)
    return all((a / name).read_bytes() == (b / name).read_bytes() for name in COMPARED_FILES)
