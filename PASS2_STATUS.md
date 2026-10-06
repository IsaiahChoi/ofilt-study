# PASS2_STATUS.md

Pass 2 (data and rebuild), run per builder prompt A′ (`docs/PASS2_ADDENDUM.md`, Appendix A′) and the supervisor notes of 2026-10-05. Paths: REPO `~/Desktop/FX_Project/ofilt_pass1`, RAW `~/Desktop/FX_Project/raw`, DATA `~/Desktop/FX_Project/data`, KIT `~/Desktop/FX_Project/files/pass2_kit_2026-10-05`, OUT `~/Desktop/FX_Project/build_out`.

## Progress

| Item | Status | Notes |
|---|---|---|
| P2-0 a. Hashes | done | SHA256SUMS: 21/21 OK. Every PASS2_INPUTS.json hash matches (table in Test results) |
| P2-0 b. Repo state | done | Tree clean (bar a Finder `.DS_Store`); no tags; BLIND_FIT_LOG 6 dev_real lines; RUN_REGISTRY.jsonl empty; `ofilt.__file__` is this repo's, `io._external_check_access` is None |
| P2-0 c. DATA and suite | done | DATA created from KIT/data, 3/3 hash-verified. Suite in ofilt_p2: 205 tests, OK (skipped=5) (D2) |
| Environment diagnostics D1–D4 | done | D1 baseline build in both Mac envs: identical panels, both hashes differ from the baseline (Flag 16); dev comparison EXPLAINED |
| P2-0 d. Tag | done | `pass1-final`, lightweight, on 81905c1 |
| P2-0 e. checkpoint.sh | done | Rewritten whole; portable; supervisor additions D.2 a–d |
| P2-0 f. .gitignore | done | `*.csv`, `*.csv.gz`, `*.gz`, `*.xlsx`, `build_out/`, `.DS_Store`; dummy panel shown ignored, then deleted |
| P2-0 g. Guard (P46) | done | Conjunctive, fail-closed gate in `io._check_access` and `blind._tag_ok`; 4 new tests (`tests/test_guard_p46.py`); existing guard tests unchanged and passing |
| P2-0 h. Docs sync (P57) | done | 3 docs over `docs/replacements/`, 5 new in `docs/`, all byte-identical to SHA256SUMS; phase-P2-0 test changes applied; `tests/test_docs_p2.py` added |
| P2-0 i. Report | done | Checkpoint `checkpoint: P2-0`; accepted by Isaiah 2026-10-05 |
| P2-0b | done | `build/pass1/` frozen byte for byte, with its pin test (`tests/test_build_pass1_pin.py`). The frozen build in ofilt_p2 reproduced the Mac baseline (656d5117… / 138e5e21…); rows and spans equal MANIFEST. ACCEPTED under Isaiah's rule. Checkpoint `checkpoint: P2-0b` |
| P2-1 | done; accepted by Isaiah 2026-10-05 | `tools/p2_1_inputs.py` → `reports/P2_1_inputs.md`. Every input hash-verified before reading. 27 of 32 comparisons with B′ / DATA_PROVENANCE match; the 5 mismatches are documentation or definition differences (Flags, P2-1). Settings check (P39b) supplied. Checkpoint `checkpoint: P2-1` |
| P2-2 | done; accepted by Isaiah 2026-10-05 | `build/pass2/columns.py` (pure functions; frozen helpers reused by import) and `build/pass2/build_panel_p2.py` (append-only build; every A′ and Isaiah build-time assertion). Synthetic tests only (`tests/test_p2_columns.py`, `tests/test_p2_build.py`, helper `tests/p2_synth.py`); no real-data run. Checkpoint `checkpoint: P2-2` |
| P2-2b | done | Amendment to `build/pass2/build_panel_p2.py` only: the amended usdjpy_us_ret rule (`check_us_ret`) with the per-panel MANIFEST count of session nights summing to exactly 0.0; MANIFEST records `git rev-parse HEAD` and whether `git status --porcelain -- build/ docs/PASS2_INPUTS.json` is empty, and the command line refuses to run otherwise. 5 synthetic tests added. Checkpoint `checkpoint: P2-2b` |
| P2-3a | done | `docs/P2_switch_drafts.md`: schema (P50), HEDGE_GAP_FOR / io / FX_NAMES (AM-03, P52), AM-03 to AM-06 in SPEC_AMENDMENTS JSONL form (AM-04 to be filled after P2-4; AM-05/06 skeletons per P56), the 60-column DATA_DICTIONARY, and the test-change table (24 rows). Nothing applied. Checkpoint `checkpoint: P2-3a` |
| P2-4 | done; accepted by Isaiah 2026-10-05 | `build/pass2/build_panel_p2.py` on the committed tree (HEAD `34f61dbb49a14bdb1965e20fab71ded33057509b`) into `build_out/p2_20261006T002928Z/`: exit 0, 72 build-time assertions. `tools/p2_4_accept.py` → `reports/P2_4_acceptance.md`: (a)–(g) all True. AM-04's hashes filled in the drafts. Checkpoint `checkpoint: P2-4` |
| P2-4b | done | `tools/p2_4_accept.py`: the HEAD-equality check is replaced by "MANIFEST git head is an ancestor of HEAD" and "build/ and docs/PASS2_INPUTS.json unchanged from the MANIFEST head to HEAD" (both heads printed); it writes the report only with --write-report (never used). Rerun: exit 0, P2-4 ACCEPTED: True; the only difference from the committed report is the replaced head line. Full environment recorded. Checkpoint `checkpoint: P2-4b` |
| P2-5 | done with two STOPs (D9; 2.3 table); item 3 (P2-5b) not run | 2.1 `tools/report_A7_1306.py` → `reports/A_hedge_efficiency_1306.md`: the TOPIX self-check passed; **D9 STOP: expanding is not lowest on common rows for 5706 and 5711** (rolling-500 is). 2.2–2.3 `tools/p2_5_staleness.py`: P55 staleness established in both samples; **2.3 STOP: 4 of the 7 ex-date 1306 gaps differ from the supervisor's table by 0.01 at 2 decimals** (diagnostics in Flags). 2.4 `tools/p2_5_coverage.py`: no STOP. Reports in `reports/P2_5_dev_checks.md`. Checkpoint `checkpoint: P2-5` |

## Next action

STOP for the decision checkpoint (report `/tmp/p2_5_report.txt`). Item 3 (P2-5b, the switch dry run) was not run, because item 2 raised STOPs (D9; the 2.3 table). P2-3b is not started.

## Decision log

- D2 / P39(b) (Isaiah, 2026-10-05): Book2.xlsx and the 1306 sheet of newbloombergdata_fixed.xlsx were both pulled with the JT suffix and the PASS2_HANDOFF Appendix E settings, per Isaiah's statement. The 1A cell-for-cell re-pull was not run. P2-1 proceeds on this statement.
- D3 / P40 (Isaiah, 2026-10-05): the TOPIX total-return series is TPXDDVD Index. Records only.
- Environment (Isaiah, 2026-10-05): Pass 2 runs in ~/venvs/ofilt_p2 (macOS arm64, Python 3.12.4), pinned to the library versions of a Claude sandbox on 2026-10-05; the certification environment's versions are unrecorded. Suite: 205, OK, skipped=5. The suite needs numpy 2 or later (test_models_c3.py:68 fails on numpy 1.26).
- (Isaiah, 2026-10-05, on the supervisor's recommendation) Rule C amended: ofilt_p2 is the Pass 2 environment, because the build mismatch is identical in every Mac environment. conda myenv is not used again.
- (Isaiah, 2026-10-05, on the supervisor's recommendation) The dev comparison of the Mac rebuild against the Pass 1 dev panel was approved (dev only), with its EXPLAINED rule fixed in advance. Result: EXPLAINED.
- Old-column source after Flag 16 (ADOPTED, Isaiah, 2026-10-05). The Mac cannot reproduce the original panel bytes (Flag 16), and the original sealed file (9c18…) is not available.
  - Dev: the 41 old columns are the original panel_dev.csv (736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42), read as strings and hash-verified before use. P2-4 acceptance (a) is unchanged.
  - Sealed: the 41 old columns come from the frozen build run on the Mac in ofilt_p2. Their reference is the Mac baseline hash 138e5e2104d5ebf6e9616edc55ca00f548e38be604365bd47932e1716f4d9d19. P2-4 acceptance (b) becomes: the sealed 41-column projection hashes to that value.
  - Evidence of equivalence: the frozen code and every input are hash-verified; the dev comparison of the Mac output against 736636… is EXPLAINED (differences only in the 18 log-derived columns; largest relative difference 2.273e-13); rows, dates and spans are equal.
  - Byte identity of the sealed old columns with 9c18… cannot be demonstrated; this is disclosed in the pre-registration. P10's hash is superseded by AM-04, as already planned.
  - The P2-4 MANIFEST records the platform, the source of the old columns for each panel, and both reference pairs (736636… / 656d5117a7d0027f7ba7d2cc8d16236fcc9258af384363c8be4577ce15933bd4, and 9c18… / 138e5e2104d5ebf6…).
- P2-0b acceptance (Isaiah, 2026-10-05; replaces A′'s): rows 5,124 / 3,057 and spans as in MANIFEST; the frozen build's dev output hashes to 656d5117a7d0027f7ba7d2cc8d16236fcc9258af384363c8be4577ce15933bd4 and its sealed output to 138e5e2104d5ebf6e9616edc55ca00f548e38be604365bd47932e1716f4d9d19. Any mismatch: STOP. On success the EXPLAINED dev comparison carries over, because the bytes are the same.
- P2-2 design constraints (Isaiah, 2026-10-05; recorded now, no code until P2-2):
  - build_panel_p2.py takes the original dev panel as an input path and verifies its hash is 736636… wherever it lives (after the switch commit it is DATA/archive/panel_dev_736636031ca1.csv). It uses that file's strings for dev's 41 old columns. For the sealed side it uses the frozen build's output, which must hash to 138e5e21…. It also asserts that the frozen build's dev output hashes to 656d5117…, so every run is shown to be the verified one.
  - *.csv is git-ignored, so synthetic test fixtures must be generated inside the tests, never committed as CSV files.
- P2-0b accepted (Isaiah, 2026-10-05): the frozen build reproduced the Mac baseline exactly (dev 656d5117…, sealed 138e5e21…). P2-1 accepted: 27 of 32 comparisons match; the 5 mismatches are errors in DATA_PROVENANCE §4 / Appendix B′ (Japan 225 calendar convention and coverage wording; XAU Good Friday closures), to be corrected at P2-6. Supervisor cross-check (dev, gap-only): on all 7 dev ex-dates the dividend-adjusted 1306 gap equals the TOPIX gap within 0.24 pp, so the ÷10 factor holds in every year.
- P2-2 additions (Isaiah, 2026-10-05):
  - Reuse the frozen helpers in build/pass1/build_panel.py by import; compute xau_* and n225_* with the frozen fx_windows; never edit build/pass1/; re-implement a helper only when it cannot be reused as is, and add a test of identical output to the frozen function on synthetic inputs.
  - 1306 distributions use the stored corrected amounts of the `1306 dividends` sheet; RAW ÷ 10 is never recomputed.
  - Build-time assertions: the number of NY sessions summed for usdjpy_us_ret equals the frozen build's us_n_sessions on every row; the XAU and Japan 225 window instants equal the panel's window_start_utc and window_end_utc on every row.
  - MANIFEST.json also records platform.platform(), platform.machine(), sys.version and the SHA-256 of the original dev panel used as dev's old-column source.
  - Unit tests compare log-derived values within an explicit tolerance, or use values exact by construction; never bit-identical floats across platforms (Flag 16).
- P2-2 accepted (Isaiah, 2026-10-05).
- usdjpy_us_ret assertion amended (Isaiah, 2026-10-05; replaces A′'s 'usdjpy_us_ret == 0.0 if and only if us_n_sessions == 0'): usdjpy_us_ret == 0.0 wherever us_n_sessions == 0, and finite wherever us_n_sessions > 0. Reason: on a night with US sessions the summed return is exactly 0.0 whenever the USD/JPY bid at the NY close equals the bid at the NY open, so the 'only if' half would fail on legitimate data. The zero-session nights stay pinned by the row-by-row check that the sessions summed equal us_n_sessions. MANIFEST reports, per panel, the number of nights with sessions whose sum is exactly 0.0 (a count).
- XAU / Japan 225 ts_utc format (P2-2 flag, resolved by the supervisor): the registered pull_dukascopy.py (6d9464f8…) converts ts_utc to timezone-aware UTC before writing, the same form as the FX masters, so the frozen load_fx should read them. If not, P2-4 stops at load time; there is no silent path.

- P2-4 accepted (Isaiah, 2026-10-05, on the supervisor's recommendation). Build build_out/p2_20261006T002928Z; MANIFEST git head 34f61dbb49a14bdb1965e20fab71ded33057509b (= checkpoint: P2-3a); dev 36f7dd69…, sealed b575272a… (full hashes in MANIFEST); old-column projections 736636… and 138e5e21…; 72 build assertions; acceptance (a)–(g) True. The committed reports/P2_4_acceptance.md stays the run-time record and is not regenerated.
- Acceptance-tool fix adopted (Isaiah, 2026-10-05, on the supervisor's recommendation): in tools/p2_4_accept.py the check "MANIFEST git head is this checkout's HEAD" becomes two checks (the MANIFEST head is an ancestor of HEAD; build/ and docs/PASS2_INPUTS.json are unchanged from the MANIFEST head to HEAD), both heads printed; the tool writes reports/P2_4_acceptance.md only with an explicit --write-report flag, never used.
- P2-5 operational details, fixed before any P2-5 script runs (Isaiah, 2026-10-05, on the supervisor's recommendation): as written in the supervisor message of 2026-10-05, item 2, including the P55 estimator (OLS with an intercept, centred R², Newey–West on the reverse slope), the one-row-per-date rule, the sample definitions, and the self-checks with their STOP rules.
- The switch dry run asked about in docs/P2_switch_drafts.md §5 is adopted as P2-5b (Isaiah, 2026-10-05, on the supervisor's recommendation): a scratch clone with the drafts applied as written (AM-03 and AM-04 only; test-change rows 1–7, 9, 11–19 and 21) and the full suite run on the P2-4 dev panel. Nothing from it is committed.

**Open for the decision checkpoint**

- D7 (P42 rule; tier-(ii) criterion; yen-EWJ option), D8 (1306 open-auction timing; default (a)), D9 (A7 on 1306), D10 (staleness result, read per P55) and D12 (the exact AM-03 to AM-06 texts), as in PASS2_ADDENDUM §1 and §4.
- The drafts in `docs/P2_switch_drafts.md`: the schema, targets, io and FX_NAMES diffs; AM-03 to AM-06, including AM-05's line placement (one record per spec line); the DATA_DICTIONARY draft; the test-change table; and the points in its §6 (`blind.VALUE_EXEMPT` grows with AT_OPEN; whether to dry-run the switch on a scratch copy first).
- D16: where the C7 slow-tier rerun runs. The supervisor recommends a Claude sandbox, the stored report's platform, because the slow tier's bit-identity tests cannot pass on the Mac (Flag 16).
- (P2-0e, implementation) `tools/checkpoint.sh` calls bare `python`, because `test_sim_b5` pins the literal `env -u OFILT_RUN_SEALED python -m unittest discover`. It therefore requires an activated venv (`VIRTUAL_ENV` set, and `command -v python` equal to `$VIRTUAL_ENV/bin/python`). Extra arguments after the item id become extra commit-message paragraphs, used for the commit attribution trailer.
- (P2-0g, implementation) Both gates run the fallback check first. The external guard is consulted only if the fallback grants. A grant requires the return value to be identical to `None` or `True`: `np.True_`, 1 and "granted" are denials. `io._check_access` now raises `AccessDenied` for every external-guard failure; before, the guard's own exception propagated. The `guard` field of an ACCESS_LOG line still reads `ofilt.guards` whenever an external guard is importable (unchanged).

## Test results

**Environments** (A′ Environment; supervisor note A.3):

| | ofilt_p2 (Pass 2 environment) | conda myenv (diagnostics only; not used again) |
|---|---|---|
| Interpreter | `/Users/isaiahchoi/venvs/ofilt_p2/bin/python` | `/Applications/anaconda3/envs/myenv/bin/python` |
| sys.version | 3.12.4 (v3.12.4:8e8a4baf65, Jun  6 2024, 17:33:18) [Clang 13.0.0 (clang-1300.0.29.30)] | 3.9.18 \| packaged by conda-forge \| (main, Dec 23 2023, 16:35:41)  [Clang 16.0.6 ] |
| platform.machine() | arm64 | arm64 |
| pandas / numpy | 3.0.2 / 2.4.4 | 2.2.3 / 1.26.4 |
| scipy / scikit-learn | 1.17.1 / 1.8.0 | 1.13.0 / 1.6.1 |
| openpyxl / PyYAML | 3.1.5 / 6.0.3 | 3.1.5 / 6.0.1 |
| BLAS / LAPACK (numpy.show_config) | accelerate / accelerate | openblas64 0.3.23.dev / openblas64 |

pip freeze of ofilt_p2: `OUT/env/pip_freeze_ofilt_p2_20261005T200424Z.txt` (written only).

**Full environment of ofilt_p2** (P2-4b, Isaiah 2026-10-05; printed by script in the venv; the P2-4 MANIFEST, which lists 7 libraries and no BLAS, is not rebuilt):

```
interpreter: /Users/isaiahchoi/venvs/ofilt_p2/bin/python
python: 3.12.4 (arm64; macOS-26.6.2-arm64-arm-64bit)
pandas: 3.0.2
numpy: 2.4.4
scipy: 1.17.1
scikit-learn: 1.8.0
openpyxl: 3.1.5
PyYAML: 6.0.3
joblib: 1.5.3
threadpoolctl: 3.6.0
python-dateutil: 2.9.0.post0
numpy show_config blas: name=accelerate version=unknown
numpy show_config lapack: name=accelerate version=unknown
scipy show_config blas: name=Accelerate version=unknown
scipy show_config lapack: name=Accelerate version=unknown
threadpoolctl.threadpool_info(): 1 entries
  user_api=openmp internal_api=openmp version=None
```

**P2-0a integrity** (generated by script from the files and the registries):

| Group | File (location) | SHA-256 observed | Equals PASS2_INPUTS.json |
|---|---|---|---|
| raw input | `Book2.xlsx` (RAW) | `40c0a051397377cd328e424b502cfa7cf0c721f72073fec15f72dc7af26527b4` | True |
| raw input | `usdjpy_dukascopy_2015-01-01_2026-03-05.csv` (RAW) | `d25497d28862f20fa676ff41e8e0d29d1093684a55be17f0b1d8222db672b4cc` | True |
| raw input | `eurusd_dukascopy_2015-01-01_2026-03-05.csv` (RAW) | `7467495a8134afb372abe0cbe3fe6e16865368c0e5e06ea616a88abe9a3499c3` | True |
| raw input | `newbloombergdata_fixed.xlsx` (RAW) | `ca51235b9f7aa8380b725984636bff5a3ae7db816e4ab0e904e70a3d0054370d` | True |
| raw input | `newbloombergdata.xlsx` (RAW) | `2d91c756a0fc64216bd6d1dea7850f98f9326b15e8fa7050cdf62dbbcbe531cc` | True |
| raw input | `xauusd_dukascopy_2015-01-01_2026-03-05.csv.gz` (RAW) | `219c58a9713b16dfb64ea1a967ca19a39095f9f6c9cc085b3405a72683d9dbaf` | True |
| raw input | `jpn225_dukascopy_2015-01-01_2026-03-05.csv.gz` (RAW) | `4490bb473dbb372a13515c5e8a5be8d341d59cbb01910a2cb0f664c8fa3b9cf1` | True |
| raw input | `checks/usdjpy_dukascopy_2019-06-04_2019-06-04.csv.gz` (RAW) | `9c7bb9a063b98a5abdf57ca7aa419f6cc1b7b6f208968f0ac2cb5448c151b45e` | True |
| event file | `events_firm.csv` (KIT/data) | `61b5629567dad37147078f4305d764587cd727fc45e257719158da3510984a4c` | True |
| event file | `events_firm.csv` (DATA) | `61b5629567dad37147078f4305d764587cd727fc45e257719158da3510984a4c` | True |
| event file | `events_boj.csv` (KIT/data) | `8950b3c7add8b406727ed53b8e822153d67e343bfb65dc8f323328b0f372aa99` | True |
| event file | `events_boj.csv` (DATA) | `8950b3c7add8b406727ed53b8e822153d67e343bfb65dc8f323328b0f372aa99` | True |
| original build code | `build_panel.py` (KIT/build/pass1) | `1fd59c0baa8de354053749cea91617f023a97bfa6d318e2287b4e1828b5b6b10` | True |
| original build code | `make_events.py` (KIT/build/pass1) | `3c0640fd4823e35a606780bbebfaeb7beefe40c28e388073352833fd6fdfdf31` | True |
| original build code | `events.py` (KIT/build/pass1) | `5180adf3c9750e86881d0275336ce898ed90ccc650195f2cb4df2e6e3ed135fa` | True |
| baseline output | `panel_dev.csv` (KIT/data) | `736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42` | True |
| baseline output | `panel_dev.csv` (DATA) | `736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42` | True |
| code (pull) | `pull_dukascopy.py` | verified in session 1: the copies in `pass 2 data/` and `prepping for pass 2/` matched `6d9464f8…`; outside the current disk scope, so not re-hashed | True |

`shasum -a 256 -c SHA256SUMS_2026-10-05.txt` (run from KIT): 21/21 OK.

**D1, baseline build of the frozen original** (`KIT/build/pass1/build_panel.py`; raw = RAW; event-file copies hash-verified True in both runs; exit 0; no stderr). Both environments produce identical panels; rows and spans match the baseline (dev 5,124, 2015-01-06 → 2021-12-30; sealed 3,057, 2022-01-04 → 2026-03-05).

| Environment | Panel | SHA-256 | Equals baseline (PASS2_INPUTS.json) |
|---|---|---|---|
| ofilt_p2 | `diag_ofilt_p2_20261005T200713Z/panel_dev.csv` | `656d5117a7d0027f7ba7d2cc8d16236fcc9258af384363c8be4577ce15933bd4` | False |
| ofilt_p2 | `diag_ofilt_p2_20261005T200713Z/panel_confirm_SEALED.csv` | `138e5e2104d5ebf6e9616edc55ca00f548e38be604365bd47932e1716f4d9d19` | False |
| conda myenv | `diag_conda_20261005T200644Z/panel_dev.csv` | `656d5117a7d0027f7ba7d2cc8d16236fcc9258af384363c8be4577ce15933bd4` | False |
| conda myenv | `diag_conda_20261005T200644Z/panel_confirm_SEALED.csv` | `138e5e2104d5ebf6e9616edc55ca00f548e38be604365bd47932e1716f4d9d19` | False |

**Dev comparison** (`OUT/diag_compare_20261005T204658Z/compare_dev.py`; supervisor item 3): equal shape, equal column names and order, equal date and ticker columns all True. The 23 non-log columns are string-identical. In all 18 log-derived columns the empty-cell pattern is identical. The largest relative difference in any column is 2.273e-13, against the 1e-8 limit. Max ulps: 1 for single-log columns; usdjpy_rv 1876, usdjpy_bv 1473, fcx_oc 256, eurusd_rv 65, ewj_oc 8, copx_oc 4, spy_oc 2. Cells differing as strings, by column: usdjpy_ret 192, usdjpy_rv 489, usdjpy_bv 489, eurusd_ret 234, eurusd_rv 2718, spy_oc 201, ewj_oc 231, fcx_oc 177, copx_oc 192, gap_adj_lag1 222, oc_lag1 242, range_lag1 137, topix_oc_lag1 258, ao_gap_adj 222, ao_gap_raw 222, ao_topix_gap 276, y_oc 242, y_topix_oc 258. **Verdict: EXPLAINED.**

**P2-0b, baseline** (frozen `build/pass1/build_panel.py`, hash-verified; ofilt_p2; `OUT/baseline_20261005T214044Z/`; event-file copies from DATA hash-verified True; exit 0; wall 19 s; no stderr). Outputs block:

```
{
  "panel_dev.csv": {
    "sha256": "656d5117a7d0027f7ba7d2cc8d16236fcc9258af384363c8be4577ce15933bd4",
    "rows": 5124,
    "span": [
      "2015-01-06",
      "2021-12-30"
    ]
  },
  "panel_confirm_SEALED.csv": {
    "sha256": "138e5e2104d5ebf6e9616edc55ca00f548e38be604365bd47932e1716f4d9d19",
    "rows": 3057,
    "span": [
      "2022-01-04",
      "2026-03-05"
    ]
  }
}
```

Acceptance (Isaiah's rule):

```
panel_dev.csv: rows equal MANIFEST: True; span equals MANIFEST: True; file sha256 equals the outputs block: True; hash equals the Mac baseline: True
panel_confirm_SEALED.csv: rows equal MANIFEST: True; span equals MANIFEST: True; file sha256 equals the outputs block: True; hash equals the Mac baseline: True
P2-0b ACCEPTED
```

The bytes equal the D1 ofilt_p2 run's, so the EXPLAINED dev comparison carries over.

**P2-4, the Pass 2 build** (ofilt_p2; `python build/pass2/build_panel_p2.py --raw RAW --events DATA --orig-dev DATA/panel_dev.csv --out build_out/p2_20261006T002928Z/`; exit 0; no stderr):
- dev `panel_dev.csv`: SHA-256 `36f7dd6965034ce92fdc7d2d0444ae7d4e037782a7f05054abc34c77f7c42b68`, 5124 rows, 60 columns, 2015-01-06 → 2021-12-30; old-column projection `736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42`.
- sealed `panel_confirm_SEALED.csv`: SHA-256 `b575272aad752b3af84abe109fa66edde421f7c99184c9d1885bacdce64f06d1`, 3057 rows, 60 columns, 2022-01-04 → 2026-03-05; old-column projection `138e5e2104d5ebf6e9616edc55ca00f548e38be604365bd47932e1716f4d9d19`.
- 72 build-time assertions passed. The frozen `load_fx` read the XAU and Japan 225 files (the ts_utc format question is closed).
- Nights with US sessions summing to exactly 0.0: dev 4, sealed 2. A′'s original "if and only if" assertion would have failed.
- Acceptance (`tools/p2_4_accept.py`; full text in `reports/P2_4_acceptance.md`): every item True; **P2-4 ACCEPTED: True**.

**P2-5 dev checks** (ofilt_p2; panel `build_out/p2_20261006T002928Z/panel_dev.csv`, hash-verified against MANIFEST before every load; full text in `reports/A_hedge_efficiency_1306.md` and `reports/P2_5_dev_checks.md`):
- 2.1 A7 on 1306: the TOPIX self-check reproduced both committed TOPIX tables cell for cell (second run; see Deviations). `y_1306_oc` NaN 0. Decision table on common rows (5706 / 5711 / 5713):
  - | 500 | 22,609.8 [n=1150] | 11,137.6 [n=1140] | 17,055.7 [n=1152] |
  - | expanding | 22,703.6 [n=1150] | 11,139.7 [n=1140] | 17,053.5 [n=1152] |
  - | none | 29,686.3 [n=1150] | 15,811.2 [n=1140] | 23,217.0 [n=1152] |
  - Lowest is expanding for (5706, 5711, 5713): [False, False, True] → **D9 STOP**.
- 2.2 P55 (one row per date; N, b_IE, b_EI, R², identity gap, bracket, NW lag, SE, CI, reading):
  - | (i) no miner ex-day and no 1306 ex-date; g_I = ao_topix_gap | 1687 (0) | 0.7571 | 1.2068 | 0.9137 | 1.1e-16 | [0.7571, 0.8286] | 7 | 0.0250 | [1.1578, 1.2559] | staleness established |
  - | (ii) all dev dates; g_I = ao_topix_gap_tradj | 1708 (0) | 0.7579 | 1.2061 | 0.9141 | 0.0e+00 | [0.7579, 0.8291] | 7 | 0.0248 | [1.1575, 1.2548] | staleness established |
- 2.3: zero-gap share of dev dates: ao_1306_gap_raw 84 of 1708 (4.92%), ao_topix_gap 0. The 7 ex-date table differs from the supervisor's at 2 decimals on 2016-07-06, 2018-07-06, 2019-07-08 and 2021-07-08 (1306 column only) → **STOP**.
- 2.4: Dev totals: 1708 dates; no Japan 225 bar 7; start fresh 1530; end fresh 938; eligible 929. First eligible dev date 2015-01-06; last 2021-12-30. The end-fresh counts equal the P2-4 table; coverage as expected; the exact-zero nights (4 dev, 2 sealed) resolve to distinct bars. No STOP.

**Suite runs:**

| When | Environment | Result |
|---|---|---|
| Pre-decision diagnostic (session 1) | conda myenv | Ran 205, FAILED (failures=1: test_models_c3.test_m5_tuning, numpy 1.26 datetime64 hashing), skipped=5; 282.8 s |
| D2 (= P2-0c suite run) | ofilt_p2 | Ran 205 tests in 248.833s, OK (skipped=5); wall 259 s. Skips: test_docs_d6 test_project_claims (Project not mounted); test_sim_b5 TestRealDev ×2 (sealed opt-in); test_validation_c7 TestSlowReproduce ×2 (slow tier) |
| P2-0g targeted | ofilt_p2 | test_guard_p46 + test_io + test_blind + test_sim_b5 + test_docs_d3: Ran 45, OK (skipped=2, the sealed opt-in pair) |
| P2-0g, new tests vs `pass1-final` code (git archive in /tmp) | ofilt_p2 | test_guard_p46: FAILED (failures=8, errors=2), as intended: every "returns other than None/True" case and the "None while the tag is absent" case fail (fail-open); the "raises" cases error because the old `_check_access` let the guard's exception escape instead of raising AccessDenied; the granted case passes |
| P2-0h targeted | ofilt_p2 | test_docs_*: Ran 35, OK (skipped=1, the Project test) |
| P2-0, before the checkpoint commit (A′ command with `-v`) | ofilt_p2 | Ran 211 tests in 235.963s, OK (skipped=5); wall 238 s. Same five skips as D2. 211 = 205 + 4 (test_guard_p46) + 2 (test_docs_p2). The B6 rewrite was identical to D2's (deterministic under Accelerate) |
| P2-0 checkpoint (`tools/checkpoint.sh "P2-0"`) | ofilt_p2 | Ran 211 tests in 227.849s, OK (skipped=5). The script printed the B6 diff (identical to D2's), restored it, and committed `a102ed1753f20344bb9ec8ae73e37d73ab6d57e0` |
| P2-0b targeted | ofilt_p2 | test_build_pass1_pin: Ran 2, OK |
| P2-0b checkpoint (`tools/checkpoint.sh "P2-0b"`) | ofilt_p2 | Ran 213 tests in 218.559s, OK (skipped=5). 213 = 211 + 2 (test_build_pass1_pin). B6 diff identical to D2's, restored; committed `090fc2198de2d9ea5f2591ff422cd79b565d6c92` |
| P2-1 checkpoint (`tools/checkpoint.sh "P2-1"`) | ofilt_p2 | Ran 213 tests in 196.575s, OK (skipped=5). B6 diff identical to D2's, restored; committed `6e04632fdb12ab621acb7694f0efa667fbcb8d92` |
| P2-2 targeted (synthetic only) | ofilt_p2 | test_p2_columns + test_p2_build: Ran 25 tests, OK (19 + 6). The end-to-end synthetic build passed 72 build-time assertions (count from a rerun of the test fixture) |
| P2-2 checkpoint (`tools/checkpoint.sh "P2-2"`) | ofilt_p2 | Ran 238 tests in 214.023s, OK (skipped=5). 238 = 213 + 25 (test_p2_columns 19, test_p2_build 6). B6 diff restored by the script; committed `791a6b80c8e70f008cccd165d6abaf769f08e691` |
| P2-2b targeted (synthetic only) | ofilt_p2 | test_p2_columns + test_p2_build: Ran 30 tests, OK (19 + 11) |
| P2-2b checkpoint (`tools/checkpoint.sh "P2-2b"`) | ofilt_p2 | Ran 243 tests in 265.529s, OK (skipped=5). 243 = 238 + 5. B6 diff restored by the script; committed `564e254a6214c0cd1256ef978b6d9694392e95fa` |
| P2-3a checkpoint (`tools/checkpoint.sh "P2-3a"`) | ofilt_p2 | Ran 243 tests in 275.205s, OK (skipped=5). B6 diff restored by the script; committed `34f61dbb49a14bdb1965e20fab71ded33057509b` |
| P2-4 checkpoint (`tools/checkpoint.sh "P2-4"`) | ofilt_p2 | Ran 243 tests in 216.959s, OK (skipped=5). B6 diff restored by the script; committed `b61f341133baac68580701119609cb85c423338a` |

After each full run the suite rewrote `reports/B6_coverage.json` (float noise; Flag 16); it was restored with `git checkout` (D3) or by `tools/checkpoint.sh`.

**P2-1, input validation** (`python tools/p2_1_inputs.py <RAW>` in ofilt_p2; exit 0; wall 10 s; no stderr; full text in `reports/P2_1_inputs.md`):
- Inputs hash-verified before any read: Book2.xlsx, newbloombergdata_fixed.xlsx, newbloombergdata.xlsx, the XAU and Japan 225 files: all True.
- **Final run: 27 of 32 comparisons match.** The 5 that do not:
  - XAU gaps over 6 h, DATA_PROVENANCE §4.2 literal ("weekends, plus Christmas and New Year"): False. The other 11 gaps are the Good Friday closures of 2015–2025; none is unexplained.
  - Japan 225 fresh share, 2015-H2 → 2018-H1, "about 0%" (miners' calendar): False. 2018-H1 is 43.8%: the feed is fresh from 2018-04-13 onward.
  - Japan 225 fresh share, 2018-H2 onward, "97–99%" (miners' calendar): False. 2021-H1 is 100.0%; by counts, 2023-H1 (122/122) and 2026-H1 (41/41) are 100%.
  - Japan 225 changeover, 2018-07-02 (miners' calendar): 2018-07-05.
  - Diagnostic, Mon–Fri weekday calendar (dev): 2015-H2 → 2018-H1 "about 0%": False (2018-H1 43.1%). Its other three rows match: 2015-H1 37; changeover 2018-07-02; 2018-H2 → 2021-H2 within 97–99%.
- First run (before the script was revised; see Deviations): 21 of 26. The extra mismatch was "amounts = RAW ÷ 10" under binary float equality (1 of 11 rows differs in the last bit). The stored decimal values are exactly RAW ÷ 10.

## Test changes

Protocol: PASS2_ADDENDUM §5. Line numbers are those of the rebuilt repo at `pass1-final`.

| Test (line) | Old | New | Entry | Phase |
|---|---|---|---|---|
| `test_docs_d4` (11) | README prefix `dc7983326fc4964e`; PLAN prefix `220fc762a511b13a` | README `9596fe7d2de098c1`; PLAN `8030770119338ad8` (SHA256SUMS_2026-10-05.txt) | P57 | P2-0, pre-approved |
| `test_docs_d4` (31) | PLAN starts `# Research Plan v2.2` | starts `# Research Plan v2.3` | P57 | P2-0, pre-approved |
| `test_docs_d4` (32) | `Supersedes:** v2.1 (Pass 1, item D4b, …)` | `Supersedes:** v2.2 (2026-10-04), which superseded v2.1 (Pass 1, item D4b, …)` | P57 | P2-0, pre-approved |
| `test_docs_d4` (75) | `171 tests, 5 skipped by default` | unchanged (v2.3 keeps the phrase) | — | — |
| `test_docs_d6` (23) | PROJECT_SETUP prefix `d2afcf2a1fe90074` | `c137831848fb3956` | P57 | P2-0, pre-approved |
| `test_docs_d6` (26–27) | title ends `(October 2026, after Pass 1)` | title ends `(October 2026, after Pass 1; refreshed 2026-10-05)` | P57 | P2-0, pre-approved |
| `test_docs_d6` (54) | `` `PLAN.md` (v2.1) `` | `` `PLAN.md` (v2.3) `` | P57 | P2-0, pre-approved |
| `test_docs_d6` (55) | Project PLAN starts `# Research Plan v2.2` | starts `# Research Plan v2.3` (Project-only; skipped on the Mac) | P57 | P2-0, pre-approved |
| `test_docs_d4`, `test_docs_d6` docstrings | — | one added sentence each, citing P57 (comment only) | P57 | P2-0 |
| new `tests/test_docs_p2.py` | — | 2 tests: the 8 synced kit docs pinned to their SHA256SUMS lines | P57 | P2-0, pre-approved |
| new `tests/test_guard_p46.py` | — | 4 tests: external False (and other non-None/True values) denied; external None with the tag absent (then side-branch only) denied; external raises (incl. signature mismatch) denied; both satisfied in a temp repo granted | P46 | P2-0, pre-approved |
| new `tests/test_build_pass1_pin.py` | — | 2 tests: each `build/pass1/` file's SHA-256 equals its `code` entry in `docs/PASS2_INPUTS.json`; the folder holds exactly `build_panel.py`, `make_events.py` and `events.py` | P51 | P2-0b, pre-approved |

No test was deleted. Existing guard tests (`test_io`, `test_blind`, `test_docs_d3`) are unchanged.

**P2-2 additions** (new files; no existing assertion changed):

| File | Tests | What they pin | Entry |
|---|---|---|---|
| new `tests/test_p2_columns.py` | 19 | A′ P2-2 unit tests on synthetic bars and calendars: dark-window bounds and the 2024-11-05 close change; the price-at-instant rule; endpoint staleness; a night without bars; the session-FX window by day t; NY DST; NYSE early closes; nights with no US session (exactly 0.0); multi-session sums; gotobi on the four month-crossing rolls, February (leap and non-leap) and a month whose 30th and 31st fall on a weekend; the 1306 dividend-adjusted gap identity; the TOPIX TR component on an ex-date; stored 1306 amounts and cash types. Re-implemented routines equal the frozen code: `parse_price_sheet` and `parse_dividends` vs `load_workbook`; `dark_window_instants` vs `fx_windows`; `us_session_dates` vs `us_features`. The frozen helpers are reused by import, and `build/pass1/` stays untouched | P50, P48, P49, P51; Isaiah 2026-10-05 |
| new `tests/test_p2_build.py` | 6 | the string round-trip keeps old columns byte-identical; an unknown date is refused; end to end on synthetic inputs: outputs and MANIFEST (platform, libraries, input/event/code hashes, the original dev panel's hash, the old-column sources, the new-column list), dev old columns = the original panel's strings (not the frozen output), sealed old columns = the frozen output, new-column values against independent computations; refusals on a wrong input, original-dev or frozen-output hash, and on a non-empty output folder | P51; Isaiah 2026-10-05 |
| new `tests/p2_synth.py` (helper, not a test module) | — | generates the synthetic raw and event files in temporary folders (no committed fixture) | Isaiah 2026-10-05 |
| `tests/test_p2_build.py`, 5 tests added (P2-2b) | 5 | the amended usdjpy_us_ret rule: a session night summing to exactly 0.0 (equal bids at the NY open and close) passes and is counted; a nonzero value on a no-session night, and a NaN on a session night, are refused; the command line refuses when `build/` or `docs/PASS2_INPUTS.json` is not committed and runs when they are; `git_state` reports this repo's HEAD. The end-to-end test also checks MANIFEST's `git` block and the zero-sum counts | Isaiah 2026-10-05 (P2-2b) |

**Pending for the P2-3a test-change table** (Isaiah, 2026-10-05; for approval at the decision checkpoint; now rows 21–23 of `docs/P2_switch_drafts.md` §5):

| Test (line) | Current | Proposed | Reason |
|---|---|---|---|
| `test_docs_d4` (11, `DOCS`) | Project file name for README `"README__2_.md"` | `"README.md"` | The Project now holds `README.md`, so the byte comparison against the Project copy silently never runs in a sandbox |
| `test_docs_p2` (`PINNED`) | the 2026-10-05 kit hashes | old → new hash for every kit doc edited at P2-6: at least `docs/DATA_PROVENANCE.md` and `docs/PASS2_INPUTS.json`; `docs/replacements/README.md` and `PLAN.md` if they are refreshed. README line 16 still says "`PLAN.md` (v2.2) is the authoritative research plan", while its line 134 says v2.3 (checked 2026-10-05) | P2-6 records |
| — (proposal for Isaiah) | — | Decisions P58 onward go in a new `docs/DECISIONS_P58_onward.md`, so `docs/DECISIONS_P37_onward.md` keeps its pin | Keeps the P57 pin stable |

## Flags

16. Platform floating point: the original panels were built on x86_64 with AVX-512; Mac rebuilds differ in the last bit (both Mac environments give identical panels); the B6 report differs under both Mac BLAS libraries.
    - Evidence (supervisor, 2026-10-05): the original dev panel's ao_gap_raw equals numpy's AVX-512 SIMD float64 log on all 5,124 rows and differs from the C-library log on 223 rows, by 1 ulp each.
    - Evidence (builder): Mac rebuild vs the original dev panel, ao_gap_raw differs as strings in 222 cells, max 1 ulp; dev comparison EXPLAINED. B6 diffs: under Accelerate, mean_b, sd_b and se_over_sd change in the last 1–2 digits; under OpenBLAS, also mean_se. Coverage 0.952 unchanged.
- (info) No git remote is configured. P45's push to a private remote is Isaiah's step.
- (info) `oldfiles/pull_dukascopy.py` hashes `e0c48f778060a1d2…` (the pre-P38 version: naive datetimes, `utcnow()` cap, no XAU/JPN225). The registered hash `6d9464f8…` matches the copies in `pass 2 data/` and `prepping for pass 2/`. Not a build input.
- (P2-1, for review) Japan 225 freshness in B′ / DATA_PROVENANCE §4.3 matches a Mon–Fri weekday calendar, not the miners' (Tokyo) calendar that the build and P42 use. On the Tokyo calendar: 2015-H1 37.2%; 2018-H1 43.8%; the changeover (trailing 60-day share ≥ 95%) is 2018-07-05; some half-years are 100%. Under any calendar, the 08:59 JST price is fresh on every Tokyo day from 2018-04-13, so B′'s "about 0% (2015-H2 → 2018-H1)" holds only through 2017-H2. Relevant to D7 (P42 coverage) and to the P2-6 records.
- (P2-1, for review) DATA_PROVENANCE §4.2 lists XAU gaps over 6 h as weekends plus Christmas and New Year. The data also have the 11 Good Friday closures (2015–2025). Records only (P2-6).
- (P2-1, for review) DATA_PROVENANCE §4.4 says RAW amount / prior close is "13.6–21% on every ex-date". This holds on the 7 dev ex-dates (13.6–21.0%) but is False for the 2022+ ex-dates (boolean only; no value shown). P47's issuer check of the 2022–2025 amounts is unaffected. Records only (P2-6).
- (P2-1, info) 1306 RAW ÷ 10: the stored corrected amounts are decimal-exact, but binary-float RAW/10 differs from them in the last bit on 1 of 11 rows. The P2-2 build should use the stored corrected amounts (as `build_panel` does for the miners) and never recompute RAW/10.
- (P2-2, for decision before P2-4) A′'s build assertion "usdjpy_us_ret == 0.0 if and only if us_n_sessions == 0" is implemented literally. Its "only if" half fails whenever a night has US sessions but the summed log return is exactly 0.0. That happens when, on a one-session night, the USD/JPY bid at the NY close equals the bid at the NY open to the 0.001 tick. A rough estimate, not computed on data: a 6.5-hour move has a standard deviation of about 0.3% (about 350 ticks), so the chance of an exact repeat is about 0.1% per session; over about 2,500 one-session nights that is roughly 3 expected cases, so P2-4 would very likely STOP on it. Suggested replacement, for Isaiah's decision: "usdjpy_us_ret == 0.0 wherever us_n_sessions == 0, and finite wherever us_n_sessions > 0", and MANIFEST to report the count of nights with sessions and an exact 0.0 sum.
- (P2-2, risk at P2-4) `build/pass2` reads the XAU and Japan 225 files with the frozen `load_fx`, which needs timezone-aware `ts_utc` strings (as the USD/JPY master has). P2-1 parsed these files with `utc=True`, which accepts either form, so the format is untested until P2-4 (P2-2 has no real-data run). If they are naive, P2-4 stops at load time, and `load_fx` would need a tested re-implementation (Isaiah's rule 2a).
- (P2-2, info) The frozen build writes `us_n_sessions` as "1.0" (a float column: joining on the calendar's first day introduces a NaN). `build_panel_p2` reads it as a number and asserts it is whole on every row.
- (P2-4, info) The amended usdjpy_us_ret rule was needed: 4 dev and 2 sealed nights have US sessions whose summed return is exactly 0.0 (counts from MANIFEST).
- (P2-4, for review) `tools/p2_4_accept.py` checks "MANIFEST git head is this checkout's HEAD". That holds only until the post-build commit. A rerun after `checkpoint: P2-4` gave False on that one line, and therefore "P2-4 ACCEPTED: False"; every other line was identical. The rerun also overwrote `reports/P2_4_acceptance.md`, which was restored from the commit with `git checkout`. Git shows that the build's commit (MANIFEST head `34f61db…`) is an ancestor of HEAD and that `build/` and `docs/PASS2_INPUTS.json` are unchanged between them. Proposed fix, not applied (stop after P2-4): check that ancestry and the unchanged paths instead of equality with HEAD.
- (P2-5, **D9 STOP**, for Isaiah) A7 on 1306: on common rows, rolling-500 has a lower hedged variance than expanding for 5706 and 5711; expanding is lowest only for 5713. Under P17/P18, expanding stays primary only if it wins on common rows for every ticker, so this is Isaiah's nuisance choice (D9), before `spec-dev-v1`. Target-only.
- (P2-5, **2.3 STOP**, for the supervisor) On 4 of the 7 dev ex-dates, the 1306 adjusted gap at 2 decimals differs by 0.01 from the supervisor's table: 2016-07-06 −1.64 vs −1.63; 2018-07-06 +0.78 vs +0.79; 2019-07-08 −0.17 vs −0.16; 2021-07-08 −0.22 vs −0.21. The TOPIX column matches on all 7. The largest difference is 0.23 pp here, against 0.24 in the supervisor's table. Diagnostics (gap-only / hedge-only, dev; run after the STOP, outside the scripts):
  - the panel's ao_1306_gap_adj equals an independent recomputation ln(open_t/(close_{t−1} − D_t)) from the hash-verified raw 1306 sheet and its stored distributions on all 7 dates, to 1e-12 (to 4 decimals: −0.3004, −1.6359, +0.0000, +0.7843, −0.1655, −0.1309, −0.2201 %);
  - simple returns exp(g)−1 do not reproduce the supervisor's 1306 column either (3 of the 4 rows still differ), so the supervisor's column follows neither the log nor the simple definition exactly. The ÷10 conclusion is unaffected: every difference is within 0.24 pp.
- (P2-5, D7) Under P42 as proposed (both endpoints ≤ 5 min), 40 dev dates in 2015-H1 are eligible: the first eligible dev date is 2015-01-06, and the 2015-H2 → 2018-H1 dates are not eligible. Seven dev nights, one in each half-year from 2015-H1 to 2018-H1, have no Japan 225 bar in the window. Sealed: 999 of 1019 dates eligible.
- (info) PASS2_INPUTS.json `local_layout` and A′'s paths name `~/Desktop/FX Project/…` (with a space) and the kit at the top level; on the Mac the folder is `FX_Project` and the kit is under `files/`. To correct at P2-6 (records).

## Blinding attestation

- **No computation related any predictor to any target.** `OFILT_RUN_SEALED` was never set; BLIND_FIT_LOG is unchanged at 6 dev_real lines; RUN_REGISTRY.jsonl is empty.
- **RAW:** hashed (P2-0a). Read only by the frozen original build in the two D1 diagnostic runs. Never opened or printed.
- **DATA:** created from KIT/data. `panel_dev.csv` was read by the Pass 1 suite (structural and target-only tests) and by `compare_dev.py`.
- **OUT:** written: `env/pip_freeze_ofilt_p2_20261005T200424Z.txt`, `diag_conda_20261005T200644Z/`, `diag_ofilt_p2_20261005T200713Z/`, `diag_compare_20261005T204658Z/compare_dev.py`. Read: the SHA-256 of the four D1 panels; and `diag_ofilt_p2_20261005T200713Z/panel_dev.csv` by `compare_dev.py` (approved, dev only), which printed only booleans, per-column counts, ulp and relative-difference maxima, and the verdict. **No sealed panel was opened**; the two sealed D1 outputs were hashed only. The D1 runs printed only the build's outputs block (hashes, rows, spans) and per-panel booleans.
- **Directories searched for `pull_dukascopy.py`** (session 1, before the disk-scope rule; filename match only): one recursive `find` over `~/Desktop/FX_Project`, which traversed `files/`, `oldfiles/`, `ofilt_pass1/` (results filtered out), `pass 2 data/`, `prepping for pass 2/` and `raw/` (with `raw/checks/`), and all their subdirectories. A second `find`, depth 2, looked for `organize_raw_inputs*`. Three `pull_dukascopy.py` copies were hashed, and `oldfiles/` was diffed against `pass 2 data/` (code only).
- **Other searches (session 1):** directory names `myenv*` under `$HOME`, `/Applications/anaconda3/envs` and `/opt` (depth 5); a top-level listing of `~/Desktop/FX_Project`.
- **Since the disk-scope rule** (supervisor D.3): inside `~/Desktop/FX_Project` only REPO, KIT, DATA, RAW (hashing) and OUT (writing, plus the reads listed above) were used.
- **Code read:** KIT docs, the frozen `build_panel.py`, repo code and tests. Helper scripts and logs lived in `/tmp/p2_0/` (outside FX_Project).
- **Printed data:** none from RAW or OUT. Session 1 printed synthetic dates from a failing synthetic test (`masked_panel(800, seed=33)`).
- **P2-2:** code and synthetic tests only; no real-data run. The tests generate synthetic inputs in temporary folders outside the repo and run the frozen build on them. No file under RAW, DATA or OUT was read.
- **P2-4:** the build hash-verified every input, then read RAW, DATA's event files and the original dev panel, and wrote `build_out/p2_20261006T002928Z/`. Its printed output is hashes, rows, spans and a count. `tools/p2_4_accept.py` read both new panels in memory; for the sealed side it printed counts and booleans only (and the sealed span, from MANIFEST). It also hash-verified the raw Japan 225 file and read it for one dev date (2015-01-05). No panel value was printed; nothing related a predictor to a target.
- **P2-4 acceptance rerun** (to capture its exit code for the report): read the same files in the same way, printing counts and booleans only.
- **This message (P2-4b, P2-5; supervisor message of 2026-10-05)**, by category:
  - P2-4b: `tools/p2_4_accept.py` rerun (stdout only): both new panels read in memory; dev hashes and counts; sealed counts and booleans only. The raw Japan 225 file was read for one dev date (2015-01-05), as at P2-4.
  - 2.1: target-only (dev): y_oc, y_topix_oc, y_1306_oc and the two flags.
  - 2.2 and 2.3: gap-only (dev): the four gap columns and exdiv_day. The diagnostics after the 2.3 STOP were gap-only (ao_1306_gap_adj, ao_topix_gap) and hedge-only (the raw 1306 sheet and distributions, hash-verified, for the 7 dev ex-dates).
  - 2.4: predictor and provenance counts (dev) and counts and booleans (sealed); the raw USD/JPY master and Book2 calendars read by script, after hash checks, for bar labels and staleness on the 4 dev and 2 sealed exact-zero nights (no price printed; no sealed date printed).
  - Item 3 (P2-5b) was not run.
  - No computation related a predictor to a target. OFILT_RUN_SEALED unset; BLIND_FIT_LOG 6 dev_real lines.
- **Correction to P2-1 (found 2026-10-05, during P2-2):** the P2-1 report and the P2-1 line below say the fixed workbook's `README` sheet "was not read". In fact `pd.read_excel(sheet_name=None)` loaded it into memory with the other sheets (in P2-1's structure probe and in `tools/p2_1_inputs.py`), and its shape and dtypes were printed. Its contents were never printed or used. `build_panel_p2` reads only the `1306`, `1306 dividends` and `TOPIX optional` sheets.
- **P2-1:** `tools/p2_1_inputs.py` hash-verified each input, then read Book2 (calendar columns only), the fixed and original 1306 workbooks (the `README` sheet was not read), and the XAU and Japan 225 minute files. It printed only the report. Dev statistics are hedge-only (1306 dividends, yields, ex-day drops) or predictor-only (Japan 225 freshness shares). For 2022+, only dates, counts and booleans were printed: the 2022+ stale-row date was shown only as a boolean against DATA_PROVENANCE, and the outlier and gap timestamps are dates/times. A dev-only diagnostic run (Japan 225 freshness under alternative calendars and thresholds; dev half-years only) informed the script's final diagnostic rows. No target was read; nothing related a predictor to a target.
- **P2-0b:** the frozen build read RAW and wrote `OUT/baseline_20261005T214044Z/`. Only its outputs block (hashes, rows, spans) and the acceptance booleans were printed, and both panels were hashed. No panel was opened. The dev comparison was rerun once for the regenerated P2-0 report (`/tmp/p2_0_report.txt`), with the same approved script and output.

## Deviations

- Pre-flight item 8 was done with organize_raw_inputs.py (copy mode; originals untouched) instead of organize_raw_inputs.sh. P2-0a's hash check is the integrity control.
- P2-0b's baseline run executed early as an environment diagnostic (D1); the hashes differ in both Mac environments (Flag 16).
- `.gitignore` has `.DS_Store` as a sixth pattern (supervisor D.1, approved deviation).
- `tools/checkpoint.sh` has the supervisor's D.2 additions beyond A′ P2-0e (venv check and interpreter print; pre-suite status and diff hash; B6 restore or abort). Beyond those, it passes extra arguments as extra commit-message paragraphs (for the attribution trailer).
- The D2 suite run used A′'s command with `-v` added (verbosity only), so that skipped tests are named.
- The P51 build-code pin test was moved from P2-0 to P2-0b, where `build/pass1/` is created (added in P2-0b).
- P2-0b's acceptance rule is Isaiah's of 2026-10-05 (the Mac baseline hashes), replacing A′'s (Flag 16).
- P2-1 goes beyond A′'s bullet list in three ways, all calendar-only or boolean-only: the DATA_PROVENANCE §4.6 calendar facts (NYSE early closes, gotobi counts and rolls, the confirmation-calendar cross-check), the cell-for-cell check of the fixed workbook against the original pull, and the dev-only Japan 225 weekday-calendar diagnostic.
- `tools/p2_1_inputs.py` was revised after its first run (21 of 26 matching), once its output had been seen:
  - "RAW ÷ 10 exactly" now uses decimal equality of the stored values, with the float result still shown;
  - XAU gaps now have a Good Friday category; the literal DATA_PROVENANCE row is kept and still False;
  - a dev-only weekday-calendar diagnostic was added for Japan 225.
  One criterion changed: "exactly" went from binary float equality to decimal equality of the stored values, which turned that row from False to True; the float result is still printed. No other criterion changed, and no row was removed. Six rows were added (26 → 32), and five of them are True: two XAU gap rows and three of the four weekday-calendar diagnostic rows.
- P2-2 design choices beyond A′'s text (for review):
  - `build()` takes an `Expect` (hashes, counts, early-close list) so the tests can run it end to end on synthetic inputs. The command line always uses `real_expect()`: hashes from `docs/PASS2_INPUTS.json`, the Mac baseline hashes of Isaiah's 2026-10-05 decision, 11 distribution rows, gotobi 529 / 319 and the 23 P49 dates.
  - Extra build-time assertions: the original dev panel's columns, and its dates and tickers row for row, equal the frozen dev output's; `us_n_sessions` is whole; every written panel's old columns re-read equal the original strings.
  - The frozen build runs in a temporary folder inside the output folder, which is removed afterwards. Only `panel_dev.csv`, `panel_confirm_SEALED.csv` and `MANIFEST.json` remain.
  - The build reads only the three needed sheets of the fixed workbook.
- P2-5, 2.1: the first run of `tools/report_A7_1306.py` stopped at the TOPIX self-check because of a parser bug in the script. It kept only table lines starting with "| ", which drops the `|---|` separator, so the computed and committed lines were compared one line out of step. The printed lines showed every computed row equal to a committed row. Nothing was computed with y_1306_oc in that run. The parser was fixed to keep every table line, and the rerun passed the self-check. First-run output: `/tmp/p2_0/p2_5_a7_run1_parserbug.out`.
- P2-5: after the D9 STOP in 2.1, checks 2.2–2.4 were still run, because they are gap-only or predictor-count checks that do not depend on the beta window. After the 2.3 STOP, 2.4 was run for the same reason. Item 3 (P2-5b) was not run, as instructed ("only if item 2 raised no STOP"). The two 2.3 diagnostics were run after the STOP, outside the committed scripts.
