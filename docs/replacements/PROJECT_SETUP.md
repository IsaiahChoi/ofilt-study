# What goes in the Claude Project, and why (October 2026, after Pass 1; refreshed 2026-10-12)

This supersedes the earlier October 2026 versions: the pre-Pass-1 one, and the after-Pass-1 one of 2026-10-02.

## Correction to the earlier version (kept)

An earlier version said project files cannot be loaded or computed on. That is wrong for sessions with code execution: project files are on disk at `/mnt/project/` and load normally with pandas. The reasons for keeping raw data out of the project are different, and they are stronger.

## Why raw data stays out

1. **It is not needed.** Models use only `panel_dev.csv`. Raw files matter only for rebuilding the panel: the Pass 2 rebuild (P34), the post-open-FX mechanism version, or the intraday extension. Those rebuilds run locally, in Claude Code on the Mac, where the build verifies every input hash. Raw files are not attached to chats for this (see "Chat uploads").
2. **The holdout depends on it.** `Book2.xlsx`, both Dukascopy files, the Pass 2 pulls and `panel_confirm_SEALED.csv` all contain 2022–2026 data. Anything in the project is readable in every future session. A sealed file inside the project is sealed only by convention.
3. **Reproducibility does not require it.** `MANIFEST.json` holds the SHA-256 of every input and output. Anyone with the raw files can rerun the scripts and prove they get an identical panel on the same numerical platform. Across platforms (Flag 16), the proof is a tolerance comparison stated in advance (DATA_PROVENANCE §5.2).

Keep the raw files on your machine plus one backup.

## Why the code repo stays out

The analysis machine is a git repository, not project files: `ofilt/drift/`, `spec/`, `tests/`, `tools/`, `docs/`, `reports/`, `BLIND_FIT_LOG`, `RUN_REGISTRY.jsonl` and `PASS1_STATUS.md`. A session that works on it gets the repo as an attached tarball and returns an updated tarball, as Pass 1 did. Pass 2 works on the local clone in Claude Code.

**The canonical repository is the rebuilt Pass 1 repository (P45).** FX-Project is the archive of the Math 86 work and is not merged into it. The canonical repo is pushed to a private remote only. No panel, raw file or build output is ever committed to it.

- **Git history is the source of truth.** Project copies are read-only snapshots that drift from it.
- **The blinding guard needs the git tags.** `spec-dev-v1` and `prereg-v1` must be ancestors of HEAD, so it only works inside the repo.
- **The two logs are append-only and must not fork.** `BLIND_FIT_LOG` (sealed fits) and `RUN_REGISTRY.jsonl` (every walk-forward run) should only be appended to; two copies of the repo would produce two diverging logs.

## In the project

**Plan and status:**
- `README.md`, `PROJECT_SETUP.md`, `PLAN.md` (v2.7);
- `PASS2_HANDOFF.md`, `PASS2_ADDENDUM.md`;
- `PASS1_STATUS.md` (stored as `PASS1_STATUS__2_.md`), `REBUILD_VERIFICATION.md`;
- `PASS2_STATUS.md` and the Pass 2 reports;
- `PASS3_STATUS.md` and the Pass 3 reports;
- `PASS4_STATUS.md` and the Pass 4 documents and outputs listed under "After Pass 4";
- `PASS5_STATUS.md`, `PASS6_STATUS.md`, the pre-registration and its review, and the Pass 5 and Pass 6 files listed under "After Pass 5" and "After Pass 6".

**Decisions:** `DECISIONS_ADDENDUM.md` (P01–P13), `DECISIONS_P14_onward.md` (P14–P36), `DECISIONS_P37_onward.md` (P37–P57), `DECISIONS_P58_onward.md` (P58–P70), `DECISIONS_P71_onward.md` (P71–P81), `DECISIONS_P82_onward.md` (P82–P87), `DECISIONS_P88_onward.md` (P88–P92), `DECISIONS_P93_onward.md` (P93–P99).

**Data documentation:** `DATA_PROVENANCE.md`, `DATA_DICTIONARY.md`, `MANIFEST.json`, `PASS2_INPUTS.json`.

**Data and code:** `panel_dev.csv`, `build_panel.py`, `make_events.py`, `events.py`, `build_panel_p2.py`, `columns.py`, `events_firm.csv`, `events_boj.csv`, `pull_dukascopy.py`.

**Background:** the Math 86 paper.

The Pass 1 replacement documents are already in place. The `.diff` files an earlier version of this document promised were never rebuilt (REBUILD_VERIFICATION D6).

To replace a Project file, delete the old copy first, then upload. Uploading over an existing name creates a `__2_` copy, as happened with README__2_ and PASS1_STATUS__2_, and the Project-comparison tests use exact names.

After Pass 2 (replaced at the Pass 2 upload, after P2-7):
- replaced: `panel_dev.csv`, `MANIFEST.json`, `DATA_DICTIONARY.md`, `DATA_PROVENANCE.md`, `PASS2_INPUTS.json`, `README.md`, `PROJECT_SETUP.md`, `PLAN.md`;
- added: `build/pass2/` `build_panel_p2.py` and `columns.py`, `DECISIONS_P58_onward.md`, `PASS2_STATUS.md` and the reports;
- the frozen `build_panel.py`, `make_events.py` and `events.py` are unchanged: `build_panel_p2.py` runs them.

The event files do not change in Pass 2.

After Pass 3 (replaced at the Pass 3 upload, after the `spec-dev-v1` tag):
- replaced: `README.md`, `PROJECT_SETUP.md`, `PLAN.md`, `DATA_PROVENANCE.md`, and `C7_mc.json` and `C7_h1_same_dgp.json` (regenerated at the switch, P80);
- added: `DECISIONS_P71_onward.md`, `PASS3_STATUS.md`, and the Pass 3 reports `P3_1_sesoi.md`, `P3_4_sealed_run.md` and `P3_5_selection.md`;
- retired: `PASS3_SUPERVISOR_HANDOFF_2026-10-06.md` ("Removed", below).

The data, event and build files do not change in Pass 3.

After Pass 4 (replaced at the Pass 4 upload, after P4-7c):
- replaced: `PROJECT_SETUP.md`, `PLAN.md` (v2.6), `DATA_PROVENANCE.md`, `DATA_DICTIONARY.md`;
- added: `DECISIONS_P82_onward.md`, `PASS4_STATUS.md`, `P4_M2_note.md`, `P4_CONFIRM_CONFIG.json`, `P4_DRYRUN_CRITERIA.md`, the audit `p4_1_audit.md`, and the dev run's document `reports/P4_runs/dev/document.json`, uploaded as `P4_dev_document.json`;
- the dev document holds the dev first look (P4-6). It is dev, not sealed, and it is disclosed in the pre-registration; once uploaded, every later session sees it.

The data, event and build files do not change in Pass 4. The confirmation code and its specifications stay in the repo.

After Pass 5 (uploaded at the start of Pass 6, from handoff H11's package):
- added: `PREREG_v1.md`, `PREREG_v1_REVIEW.md`, `PASS5_STATUS.md`, `DECISIONS_P88_onward.md`, `P5_CONFIRM_SCRIPT_SPEC.md`, `p6_confirm_run.py` and `test_p6_confirm_run.py`.

After Pass 6 (replaced at the Pass 6 upload, after P6-2):
- replaced: `README.md`, `PROJECT_SETUP.md`, `PLAN.md` (v2.7), `DATA_PROVENANCE.md`;
- added: `DECISIONS_P93_onward.md`, `PASS6_STATUS.md`, `P6_RUN_CRITERIA.md`, `P6_RUN2_CRITERIA.md`, and the confirmation document `reports/P6_runs/confirm/document.json`, uploaded as `P6_confirm_document.json`;
- the confirmation document holds the confirmation results. Once uploaded, every later session sees them, by design. The sealed panel itself never enters the Project.

## Chat uploads

A file uploaded to a chat is not a Project file, but it stays in that chat.
- Raw files were uploaded twice so that a supervisor chat could verify them (2026-10-04 and 2026-10-05).
- Both times they were hashed, and only integrity, predictor-only, calendar or dividend facts were read (DATA_PROVENANCE §4.5).
- There is no need to do this again: the Pass 2 build runs on the Mac and verifies every hash itself.
- The later supervisor chats (2026-10-05 and 2026-10-06) uploaded no raw file and worked on the Project copies only (DATA_PROVENANCE §4.5).
- The Pass 3 supervisor chats (2026-10-06 and 2026-10-07) uploaded no raw or data file: only supervisor handoffs, status files and builder reports (DATA_PROVENANCE §4.5). The Pass 3 handoffs stay on the Mac, outside the Project.
- The Pass 4 supervisor chats (2026-10-08 to 2026-10-12) uploaded no raw or data file: only supervisor handoffs, repository snapshots (code, documents and committed reports; no panel), status files and builder reports, which include the dev run's committed outputs (DATA_PROVENANCE §4.5). The Pass 4 handoffs stay on the Mac, outside the Project.
- Never upload the sealed panel to any chat.

## Removed from the project (superseded; they would mislead future sessions)

| File | Why |
|---|---|
| `fx_dark_window_features.csv` | HistData-based; its window end included the bar labeled 08:59 (a price at 09:00:00); covers 2023–2026 |
| `build_windows.py` | Replaced by `build_panel.py` (it used a naive business-day calendar and the same endpoint problem) |
| `histdata_tz.py` | HistData retired; mis-corrects the autumn 2025 window |
| `slim_encode.py` | Compressed the HistData masters, which are no longer used |
| `MASTER_README__1_.md` | Described the HistData masters; replaced by `README.md` |
| `Plan` (v2.0) | Replaced by `PLAN.md` v2.1 |
| `PASS2_SUPERVISOR_HANDOFF_2026-10-05.md` | Superseded by `DECISIONS_P58_onward.md` and `PASS2_STATUS.md`; its next-step instructions would mislead |
| `PASS2_P2-6_RECORDS_REGISTER.md` | Superseded by `DECISIONS_P58_onward.md` and `PASS2_STATUS.md`; its next-step instructions would mislead |
| `PASS2_SUPERVISOR_HANDOFF_P2-6.md` | Superseded by `DECISIONS_P58_onward.md` and `PASS2_STATUS.md`; its next-step instructions would mislead |
| `PASS3_SUPERVISOR_HANDOFF_2026-10-06.md` | Superseded by `DECISIONS_P71_onward.md` and `PASS3_STATUS.md`; its next-step instructions would mislead |

## Never in the project (and never pushed to any git remote)

- `panel_confirm_SEALED.csv`, in any build, including the Pass 2 rebuild.
- `Book2.xlsx`, `usdjpy_dukascopy_*.csv`, `eurusd_dukascopy_*.csv`, and the HistData masters.
- The Pass 2 raw pulls: 1306 OHLC, session and US-session FX, a Nikkei proxy, XAU.
- Any forward-holdout data (after 2026-03-05), before and after `prereg-v1`.
- Anything from `build_out/` other than `MANIFEST.json`; `~/.claude/settings.json` and `settings.json.bak`.
- Isaiah's cost note of 2026-10-06, which quotes 2026 prices (prior exposure; DECISIONS_P71_onward, carried item 4).
