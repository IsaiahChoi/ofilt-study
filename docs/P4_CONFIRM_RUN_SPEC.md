# P4_CONFIRM_RUN_SPEC: the run script, the whole document, the two-run rule, the registry routing and the refusals (P4-4c2; P4Q39)

Version 1, written by the supervisor chat that began on 2026-10-11 with handoff H9, for P4-4c2. It specifies a library module `ofilt/drift/confirm_run.py`, a script `tools/p4_confirm_run.py`, and their tests `tests/test_p4_confirm_run.py`. P4-4c2 commits it as `docs/P4_CONFIRM_RUN_SPEC.md`. A change after P4-4c2 is a new version of this file, recorded with its reason.

The modules of P4-4a to P4-4c1 each fill part of one document. This item assembles it, writes it, and fixes the rules around the run: two runs on the same inputs give byte-identical documents apart from runtime fields (P4Q5); synthetic runs record to the temporary registry and the dev run to `RUN_REGISTRY.jsonl` (P4Q6); the confirmation panel is never opened in Pass 4, and `io.load_confirm` is called only in refusal tests (P4Q3, P13(c)); the dev run starts only on its own sanction (P4-6). The texts it implements: `PASS4_STATUS.md`'s P4Q3, P4Q5, P4Q6, P4Q35 to P4Q38; the specifications `docs/P4_CONFIRM_INF_SPEC.md`, `docs/P4_CONFIRM_FC_SPEC.md`, `docs/P4_CONFIRM_ECON_SPEC.md` and `docs/P4_CONFIRM_CLAIMS_SPEC.md`; `ofilt/drift/io.py` and `ofilt/drift/registry.py`.

## 1. Rules for the code

### 1.1 Placement and imports
- One new module, one new script, one new test file. No existing file changes; no C7-hashed file changes.
- `confirm_run.py` imports only `__future__`, `dataclasses`, `datetime`, `json`, `math`, `pathlib`, `time`, `typing`, and from the package `blind`, `spec` (`Spec`), `confirm_inference`, `confirm_forecast`, `confirm_economic` and `confirm_claims`. It does not import `io`, `registry`, `sim`, `sim_full`, `forecast`, `fctests`, `models`, `calendar` or anything under `tools/`.
- `confirm_run.py` reads no file itself (each module it calls reads what its specification says) and writes files only in `write_outputs` (§3.3).
- `tools/p4_confirm_run.py` may import `io` and `sim_full` in addition, and calls `io.load_dev` and `io.load_events_firm` only in the dev branch (§4). It never names `load_confirm`.

### 1.2 Static tests they must satisfy
As `docs/P4_CONFIRM_INF_SPEC.md` §1.2, for the module and for the script: `test_docs_d3b` scans `tools/` as well as `ofilt/`, so neither file may hold a tag's name. `test_docs_d6` forbids a `.csv` file with "confirm" in its name anywhere in the repository: the outputs are `.json` files.

### 1.3 Read first (as text)
`ofilt/drift/io.py` (`DATA_DIR`, `ACCESS_LOG_PATH`, `load_dev`, `load_events_firm`, `load_confirm`, `_log_access`), `ofilt/drift/registry.py` (`registry_path`, `record_run`), `ofilt/drift/_guards_fallback.py` (`check_access`), the four specifications named above, the four confirmation modules, `tools/p3_sealed_run.py` (its command-line form, as a model) and `tests/test_io.py` (how it patches `io`).

## 2. Constants of `confirm_run.py`

- `SPEC_FILES`: a tuple of `(path, version, sha256)` for the four specifications, as committed: `("docs/P4_CONFIRM_INF_SPEC.md", 2, "a7ebb94f003c3b893e96b222b796ea9fda09c849217c526bfdfc8d2b6be51f65")`, `("docs/P4_CONFIRM_FC_SPEC.md", 1, "a8d3a9c91ca7a3d6bf551f95a56e3e4cf43ec14ed6b4f0d450c751589f795bd6")`, `("docs/P4_CONFIRM_ECON_SPEC.md", 1, "42e1488330ae7bb3c947fb92a6958c851197aaad6d9e545a5e3ef81511432785")`, `("docs/P4_CONFIRM_CLAIMS_SPEC.md", 1, "b499e820c62961b79bfc0ec839d6014e918657f79071182104fbdc1f4d4dbbf2")`. A test checks them against the files.
- `OUTPUT_FILES = ("document.json", "manifest.json", "runtime.json")`.
- `DEV_RUN_SANCTION_VAR = "OFILT_P4_DEV_RUN"`, `DEV_RUN_SANCTION_VALUE = "P4-6"` (§4).

## 3. `confirm_run.py`: API

### 3.1 `build_document(dev, events, confirm=None, *, spec=None, factories=None) -> Assembled`
In order: `doc = confirm_inference.infer(dev, events, confirm, spec=spec)`; `calls = confirm_forecast.run_calls(dev, events, confirm, spec=spec, factories=factories)`; `doc = confirm_forecast.fill(doc, confirm_forecast.forecast_rows(calls))`; `doc = confirm_economic.fill(doc, confirm_economic.economic_row(calls, dev, events, confirm, spec=spec))`; `doc = confirm_claims.fill(doc, confirm_claims.claim_rows(doc, dev, events, confirm, spec=spec))`. Then `ValueError` unless the document holds exactly the 71 IDs of `confirm_inference.ROW_IDS`, in order, none pending. The provenance checks happen in `infer`, first (it is called first). `Assembled` is a dataclass `(doc, calls, runtime)`, where `runtime` = `{"utc_start", "utc_end", "wall_seconds", "run_ids": {"main": calls.main.run_id, "m7": calls.m7.run_id}}` (UTC times as ISO strings with a `Z`).

### 3.2 `manifest(doc, *, spec=None) -> dict`
Deterministic, from the document and constants only: `{"output": "the confirmation document of Pass 4 (P4Q35 to P4Q39)", "files": list(OUTPUT_FILES), "document_schema_version": doc["spec_version"], "document_schema_version_meaning": "the version of the document's schema, docs/P4_CONFIRM_INF_SPEC.md section 4.1; the specifications' own versions are under specifications", "specifications": [{"path", "version", "sha256"} for each of SPEC_FILES], "config_sha256": confirm_inference.CONFIG_SHA256, "cost_inputs_sha256": confirm_economic.COST_INPUTS_SHA256, "analysis_spec_sha256": spec.sha256, "mode": doc["mode"], "provenance": doc["provenance"], "dates": doc["dates"], "runtime_fields": "runtime.json only: utc_start, utc_end, wall_seconds and the registry's run ids; document.json and manifest.json are identical across runs on the same inputs (P4Q5)"}`. (This settles P4-boot2's note N8.)

### 3.3 `write_outputs(out_dir, assembled, *, spec=None) -> dict`
`out_dir` must not exist (`FileExistsError` otherwise); it is created with its parents. It writes `document.json` = `confirm_inference.to_json(doc)`, `manifest.json` and `runtime.json`, each `json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n"`, UTF-8, LF. It returns `{name: sha256 of the bytes written}` for the three files; it computes each hash from the bytes it wrote, not by reading the file back.

### 3.4 `documents_equal(a_dir, b_dir) -> bool`
True when `document.json` and `manifest.json` are byte-identical in the two folders. (It reads files: it is the one reading function of the module, used by P4-5's dry run and by the tests.) The §1.1 rule that the module reads no file applies to everything except this function and the files `Spec.load` and the called modules read.

## 4. `tools/p4_confirm_run.py`

`main(argv=None) -> int`, and `if __name__ == "__main__": sys.exit(main())`. Arguments:
- `--source {synthetic,dev,confirm}` (required) and `--out DIR` (required; must not exist).
- For `synthetic` only: `--seed INT` (required; the absolute seed passed to `sim_full.simulate`), `--scenario JSON` (default `{}`; the keyword arguments of `sim_full.Scenario`, lists becoming tuples), `--dev-dates N` (optional; the last N dates of `sim_full.dev_calendar()`).

Branches, each decided before anything is loaded or simulated:
- `confirm`: print `REFUSED: the confirmation panel is not opened in Pass 4 (P4Q3; P13(c)); the confirmation run is Pass 6's`, write nothing, return 2. No module of `io` is called.
- `dev`: the frames come from a function `_dev_frames()`, which first checks the sanction: unless the environment variable `DEV_RUN_SANCTION_VAR` equals `DEV_RUN_SANCTION_VALUE`, print `REFUSED: the dev run needs its sanction (P4-6): set OFILT_P4_DEV_RUN=P4-6` and return 2, having called nothing. With the sanction: `dev = io.load_dev()`, `events = io.load_events_firm()`, `build_document(dev, events)`; the forecasting calls then append to `RUN_REGISTRY.jsonl` (P4Q6). This branch is not run in P4-4c2.
- `synthetic`: `out = sim_full.simulate(seed, Scenario(**scenario), dev_dates=...)`, then `build_document(out.dev, out.events, out.confirm)`; the forecasting calls append to the temporary registry (`registry.SYNTHETIC_PATH`).
- Then `write_outputs`, and print one line per file: its path and SHA-256. Return 0.
- Unknown or missing arguments: argparse's usual exit (2).

## 5. Tests (`tests/test_p4_confirm_run.py`: exactly these 12)

### 5.1 Seeds, frames, registry and run time
- Seeds S_k = `Spec.load().seed` + 8,600,000 + k, k below 1,000 (disjoint from + 8,000,000 to + 8,500,000).
- Frames as P4-4c1's tests: `sim_full.simulate(S_k, Scenario(b=1.0, a2=0.6, delta_cc=1.5), dev_dates=sim_full.dev_calendar()[-900:])` with 5706's `open`, `close` and `prev_close` multiplied by 0.1 (in the script tests, `--scenario` and `--dev-dates 900` are passed, and 5706's prices are not scaled: §5.2 test 5 says how the costs are handled).
- The M7 stand-in of P4-4b2's tests (`ZeroM7`) replaces M7: in `build_document` through `factories={"M7": ZeroM7}`; in the script tests by `unittest.mock.patch.dict(models.REGISTRY, {"M7": ZeroM7})`, the script having no factories argument.
- `setUpModule` patches `registry.SYNTHETIC_PATH` and `registry.REAL_PATH` to a temporary folder and `io.ACCESS_LOG_PATH` to a file in it; `tearDownModule` undoes it. Every output folder is in a temporary directory.
- The file runs in under 180 s; the report gives its time.

### 5.2 The 12 tests
1. `test_build_document_complete` (S1): the document has the 71 IDs in order, none pending, each entry's item as `ITEM_OF`; `to_json` has no `NaN` or `Infinity` and round-trips; `licensed` is False (synthetic).
2. `test_two_builds_identical` (S1, built twice): `to_json` of the two documents is byte-identical, and so are their manifests; their `runtime` run ids differ.
3. `test_write_outputs` (S1): the three files exist and nothing else in the folder; `document.json`'s bytes are `to_json(doc)`; the returned hashes are the files' SHA-256; `manifest.json` and `runtime.json` parse; writing again to the same folder raises `FileExistsError`.
4. `test_manifest_pins`: each `(path, version, sha256)` of `SPEC_FILES` matches the file at REPO; `config_sha256` and `cost_inputs_sha256` match `docs/P4_CONFIRM_CONFIG.json` and `docs/P3_COST_INPUTS.json`; `analysis_spec_sha256` is `Spec.load().sha256`; the manifest's keys are exactly §3.2's.
5. `test_script_synthetic_twice` (S2): `main` run twice in process, `--source synthetic --seed S2 --scenario '{"b": 1.0, "a2": 0.6, "delta_cc": 1.5}' --dev-dates 900`, into two folders, with ZeroM7 patched into `models.REGISTRY`; both return 0; `documents_equal` is True; the runtime files differ; the patched synthetic registry gained exactly 4 lines and the patched real registry does not exist; `RUN_REGISTRY.jsonl` in REPO has 0 bytes. 5706's simulated prices are not scaled here, so O45 is estimated and, when any evaluated 5706 row has a traded price above 30,000 yen (recomputed in the test with the price factor of `docs/P3_COST_INPUTS.json`), its `cases_failed` holds exactly the primary and high cases (P4-4b2); the test checks that, whichever way the recomputation comes out.
6. `test_script_refuses_confirm`: with `io.load_confirm`, `io.load_dev` and `sim_full.simulate` patched to recorders, `main(["--source", "confirm", "--out", D])` returns 2, none of them is called, D does not exist, and the module-level patched ACCESS_LOG is unchanged (absent, or of the same size, before and after).
7. `test_script_refuses_dev_without_sanction`: with `OFILT_P4_DEV_RUN` removed from the environment (`mock.patch.dict(os.environ)`) and `io.load_dev` and `io.load_events_firm` patched to recorders, `main(["--source", "dev", "--out", D])` returns 2, neither is called, D does not exist. With `OFILT_P4_DEV_RUN` set to another value, the same.
8. `test_load_confirm_refused_and_logged` (P4Q3): with `io.ACCESS_LOG_PATH` patched, within the test, to a new file in its own temporary folder, and `io.DATA_DIR` to an empty temporary folder, `io.load_confirm()` raises `io.AccessDenied`; that ACCESS_LOG holds exactly one line, whose JSON has `result` "DENIED" and `tag` "prereg-v1"; no name starting `ACCESS_LOG` exists in REPO outside `.git`; the empty folder is still empty.
9. `test_registry_routing` (P4Q6): `registry.registry_path` gives `registry.SYNTHETIC_PATH` for `synthetic` and `registry.REAL_PATH` for `dev_real` and `confirm_real`, and raises `blind.BlindingError` for any other provenance; `registry.REAL_PATH`'s unpatched value (read from the module source by `ast`) is the repository's `RUN_REGISTRY.jsonl`.
10. `test_dev_mode_document` (S3, the dev frame alone, default dev calendar): `build_document(dev, events)` gives mode "dev", none pending, O8 and O27 not applicable, R23 and R25 not applicable, R10's `claimed` False.
11. `test_refused_pairs_before_anything` (S1's frames): the five refused provenance pairs of P4-4a's test 5 raise `ValueError` from `build_document`, with `blind.registered_labels()` unchanged and no registry line written.
12. `test_sources`, by `ast`: `confirm_run.py` imports only as §1.1 allows and calls `open`, `write_text` or `write_bytes` only inside `write_outputs` and `documents_equal`, and `read_bytes`, `read_text` or `open` for reading only inside `documents_equal`; neither file holds the string `load_confirm`; in the script, `load_dev` and `load_events_firm` are called only inside a function `_dev_frames`, whose first statement checks the sanction, and `_dev_frames` is called only where `--source` is `dev`.

## 6. Notes for the builder
- The item's message has a probe step (c.2): `build_document` on S1's frames with ZeroM7, printing each step's wall time, the statuses of the 71 entries, the manifest, the runtime dict, and the byte length and SHA-256 of `to_json(doc)` for two builds. It asserts nothing.
- The dev branch is written and statically tested now, and run only at P4-6, under that item's message and Isaiah's sanction.
- If a test can pass only by departing from this file, or this file is wrong on a point a test depends on, stop and say which.
