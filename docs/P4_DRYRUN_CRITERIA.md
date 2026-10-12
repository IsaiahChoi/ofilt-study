# P4_DRYRUN_CRITERIA: the synthetic dry run, its criteria, and the gate before the dev run (P4-5 and P4-6; P4Q40)

Version 1, written by the supervisor chat that began on 2026-10-11 with handoff H9, before any run it describes. P4-5/6 commits it as `docs/P4_DRYRUN_CRITERIA.md` at its first checkpoint, before the dev run. It states P4Q5's setup and criteria with P4Q28's tolerances and P4Q29's seeds, and the checks that must hold before and after the dev run (P4Q1, P4Q6). Nothing in it may change after a run has started; a failure is a STOP, not an edit.

## 1. What runs

- **The code:** `tools/p4_confirm_run.py` and the modules it calls, exactly as committed at `383cce639887871bc52f36c624cf3c3405769650` (P4-4c2): script SHA-256 `d4cd6edd3c341cfed8ecfb608cd17062254512a436463b688a8913a6e0455a5d`, `ofilt/drift/confirm_run.py` `998912c5c9e89ca14fde5e1ca1811ff3f3e4ac65dd36b29b61debffab8e9eaf3`, the configuration `docs/P4_CONFIRM_CONFIG.json` `5962c44cdc220afb7eee26d7dc91db30c0f4fa231578823799742b44ae4e15bd`. Every run is a plain command-line run of the script: no patch, no stand-in, the production M7 with its full grid.
- **The calendars:** the simulator's default dev calendar (1,714 dates) and the confirmation calendar (1,019 dates), so the confirmation part has the confirmation's length (P4Q5: "the confirmation calendar"). The target is the AM-03 target `abn_oc`, as in every run.
- **The seeds (P4Q29):** S_k = the spec seed (20261001) + 9,000,000 + k, a block disjoint from every earlier one (B7 + 100,000 to + 230,500; B7b + 1,000,000; C7 + 3,000,000; the P3-2a warp check + 4,000,000; the sealed run + 5,000,000 to about + 6,200,000; Pass 4's test blocks + 8,000,000 to + 8,600,999).

| Run | Folder (under `reports/P4_runs/dryrun/`) | Seed | `--scenario` | Known values (`sim_full.simulate(seed, scenario).truth`) |
|---|---|---|---|---|
| Z | `z` | S_1 | `{}` (b = 0) | b_pre = b_post = 0 |
| B | `b` | S_2 | `{"b": 0.5}` | b_pre = b_post = 0.5 |
| B again | `b_rerun` | S_2 | `{"b": 0.5}` | (for the two-run rule) |
| K | `k` | S_3 | `{"b": 0.5, "delta_post": -0.5}` | b_pre = 0.5, b_post = 0.0 (the break at 2024-11-05) |

Each is `tools/p4_confirm_run.py --source synthetic --seed S_k --scenario '<json>' --out reports/P4_runs/dryrun/<folder>`, with `OFILT_DATA_DIR` set to an empty folder. Their forecasting calls append to the temporary synthetic registry, never to `RUN_REGISTRY.jsonl` (P4Q6).

## 2. The criteria (P4Q5, P4Q28), checked by script

For each of the four runs:
- **C1** The script exits 0 and the folder holds exactly `document.json`, `manifest.json` and `runtime.json`; the printed SHA-256 of each equals the file's.
- **C2** The document holds the 71 IDs of `confirm_inference.ROW_IDS`, in order; no row is `pending` or `not_estimable`; the rows `not_applicable` are exactly R23 and R25 (by design: the one-shot rule and the forward holdout apply to neither a synthetic panel nor Pass 4); mode `confirmation`, provenance `synthetic`.
- **C3 (present and finite)** `document.json` parses with Python's `json`, contains neither `NaN` nor `Infinity`, and no `estimated` or `fixed` row has `values` None. A None inside a row's values is allowed only where a specification defines it (an unbounded Fieller endpoint, the directional test of a constant-sign forecast, a field that is None when its input is absent); every None leaf is listed in the report by its path, for review, without being a criterion, except under C5.
- **C4 (no claim)** R10's, R11's and R14's `claimed` are False and `licensed` is False (a synthetic panel licenses nothing).
- **C5 (the simulator's price level, stated in advance)** The simulator starts 5706 at a stored price of 3,000, which the cost file's price factor (1/10 from 2017-09-27) makes a traded price near 30,000 yen, the tick tables' last bound (P4-4b2, P4-4c2 reading R8). O45 must be `estimated` with its low case computed; its `cases_failed` must be either empty, or exactly `{primary, high}` with each reason starting `ValueError` and naming a table's last bound, and in the second case at least one 5706 traded price of the simulated confirmation frame must exceed 30,000 yen (recomputed by the check from `sim_full.simulate(S_k, scenario).confirm`'s `open` and `close` and the cost file's 5706 price factor, traded = stored ÷ factor; the evaluated rows are among these). Apart from the two failed cases' own entries, nothing in O45 may be None.
- **C6** The manifest's specifications, configuration, cost inputs and analysis spec hashes equal the pinned values; its mode and provenance equal the document's.
- **C7 (recovery, P4Q28)** With `truth` from `sim_full.simulate(S_k, Scenario(**scenario))` (recomputed by the check, synthetic):
  - runs Z and B: O1's `usdjpy_ret` estimate is within 4 standard errors (O1's own SE) of `truth["b_pre"]`, and `truth["b_pre"] == truth["b_post"]` equals the scenario's b;
  - runs B and K: O27's `b_pre` estimate is within 4 of its SEs of `truth["b_pre"]`, and its `b_post` estimate within 4 of its SEs of `truth["b_post"]`;
  - the tolerance, 4 standard errors, is fixed here before any run; with seven such comparisons a correct implementation fails one with probability below 0.1%.

Across the runs:
- **C8 (two runs, P4Q5)** `confirm_run.documents_equal("…/b", "…/b_rerun")` is True, and the two `runtime.json` differ.
- **C9 (registry)** The temporary synthetic registry gained exactly 8 lines (4 runs × 2 calls), each with provenance `synthetic`; `RUN_REGISTRY.jsonl` is still 0 bytes; `BLIND_FIT_LOG` is still 7 lines with its SHA-256; no name starting `ACCESS_LOG` exists in the repository.
- **C10 (timing, information only)** Each run's wall time is printed; the longest sets no criterion. The dev run is launched by the builder (P4Q40, answering P4Q6's open point).

**The gate:** the dev run starts only if every criterion C1 to C9 holds for every run (the check's verdict `DRY CHECK: True`) and the first checkpoint, which commits this file, the dry run's outputs and the records, succeeds.

## 3. Before the dev run (checked by script)

- HEAD is the first checkpoint's commit, its only parent is `383cce639887871bc52f36c624cf3c3405769650`, the tree is clean, and `git diff --name-only 383cce63… HEAD` lists only `PASS4_STATUS.md`, `docs/P4_DRYRUN_CRITERIA.md`, `reports/P4_reports/p4_4c2.txt` and files under `reports/P4_runs/dryrun/`.
- At HEAD, the script, `confirm_run.py`, the four other confirmation modules, the configuration, the cost inputs, the spec and the simulator have the SHA-256 they had at `383cce63…` (the sanctioned code).
- The dev panel `panel_dev.csv` in the data folder has SHA-256 `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68` (a hash only; the file is not otherwise read by the check), as the spec registry records.
- `RUN_REGISTRY.jsonl` is 0 bytes, `BLIND_FIT_LOG` 7 lines with its SHA-256, no ACCESS_LOG, and `reports/P4_runs/dev/` does not exist.

## 4. The dev run and what it must show

The one run (P4Q6): `OFILT_P4_DEV_RUN=P4-6` and `OFILT_DATA_DIR` the data folder, `tools/p4_confirm_run.py --source dev --out reports/P4_runs/dev`. Afterwards, checked by script:
- the script exits 0; the folder holds exactly the three files, with the printed hashes;
- the document holds the 71 IDs in order, none pending; mode `dev`, provenance `dev_real`; R10, R11 and R14 not claimed (the dev run licenses nothing: D14 P36 step 5); any row not estimable is listed with its reason (on real data P4Q31's contingencies may apply; this is reported, not a failure);
- `RUN_REGISTRY.jsonl` holds exactly 2 lines, each with provenance `dev_real`, whose run ids are `runtime.json`'s and whose `git_commit` is the first checkpoint's commit;
- `BLIND_FIT_LOG` is unchanged (7 lines, its SHA-256); no ACCESS_LOG exists; the confirmation loader was not called (the script never names it).

Then the three tests that assert an empty registry are rewritten to this state by decision (P4Q6), under the test-change protocol, and the second checkpoint commits the outputs, the registry, the tests and the records.
