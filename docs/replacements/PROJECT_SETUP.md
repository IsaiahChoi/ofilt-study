# What goes in the Claude Project, and why (October 2026, after Pass 1; refreshed 2026-10-05)

This supersedes the earlier October 2026 versions: the pre-Pass-1 one, and the after-Pass-1 one of 2026-10-02.

## Correction to the earlier version (kept)

An earlier version said project files cannot be loaded or computed on. That is wrong for sessions with code execution: project files are on disk at `/mnt/project/` and load normally with pandas. The reasons for keeping raw data out of the project are different, and they are stronger.

## Why raw data stays out

1. **It is not needed.** Models use only `panel_dev.csv`. Raw files matter only for rebuilding the panel: the Pass 2 rebuild (P34), the post-open-FX mechanism version, or the intraday extension. Those rebuilds run locally, in Claude Code on the Mac, where the build verifies every input hash. Raw files are not attached to chats for this (see "Chat uploads").
2. **The holdout depends on it.** `Book2.xlsx`, both Dukascopy files, the Pass 2 pulls and `panel_confirm_SEALED.csv` all contain 2022–2026 data. Anything in the project is readable in every future session. A sealed file inside the project is sealed only by convention.
3. **Reproducibility does not require it.** `MANIFEST.json` holds the SHA-256 of every input and output. Anyone with the raw files can rerun the scripts and prove they get an identical panel.

Keep the raw files on your machine plus one backup.

## Why the code repo stays out

The analysis machine is a git repository, not project files: `ofilt/drift/`, `spec/`, `tests/`, `tools/`, `docs/`, `reports/`, `BLIND_FIT_LOG`, `RUN_REGISTRY.jsonl` and `PASS1_STATUS.md`. A session that works on it gets the repo as an attached tarball and returns an updated tarball, as Pass 1 did. Pass 2 works on the local clone in Claude Code.

**The canonical repository is the rebuilt Pass 1 repository (P45).** FX-Project is the archive of the Math 86 work and is not merged into it. The canonical repo is pushed to a private remote only. No panel, raw file or build output is ever committed to it.

- **Git history is the source of truth.** Project copies are read-only snapshots that drift from it.
- **The blinding guard needs the git tags.** `spec-dev-v1` and `prereg-v1` must be ancestors of HEAD, so it only works inside the repo.
- **The two logs are append-only and must not fork.** `BLIND_FIT_LOG` (sealed fits) and `RUN_REGISTRY.jsonl` (every walk-forward run) should only be appended to; two copies of the repo would produce two diverging logs.

## In the project

**Plan and status:**
- `README.md`, `PROJECT_SETUP.md`, `PLAN.md` (v2.3);
- `PASS2_HANDOFF.md`, `PASS2_ADDENDUM.md`;
- `PASS1_STATUS.md` (stored as `PASS1_STATUS__2_.md`), `REBUILD_VERIFICATION.md`.

**Decisions:** `DECISIONS_ADDENDUM.md` (P01–P13), `DECISIONS_P14_onward.md` (P14–P36), `DECISIONS_P37_onward.md` (P37–P57).

**Data documentation:** `DATA_PROVENANCE.md`, `DATA_DICTIONARY.md`, `MANIFEST.json`, `PASS2_INPUTS.json`.

**Data and code:** `panel_dev.csv`, `build_panel.py`, `make_events.py`, `events.py`, `events_firm.csv`, `events_boj.csv`, `pull_dukascopy.py`.

**Background:** the Math 86 paper.

The Pass 1 replacement documents are already in place. The `.diff` files an earlier version of this document promised were never rebuilt (REBUILD_VERIFICATION D6).

After Pass 2:
- replace `panel_dev.csv`, `MANIFEST.json`, `DATA_DICTIONARY.md`, `DATA_PROVENANCE.md`, `PASS2_INPUTS.json` and the build scripts with the rebuilt versions;
- add the Pass 2 status file and reports.

The event files do not change in Pass 2.

## Chat uploads

A file uploaded to a chat is not a Project file, but it stays in that chat.
- Raw files were uploaded twice so that a supervisor chat could verify them (2026-10-04 and 2026-10-05).
- Both times they were hashed, and only integrity, predictor-only, calendar or dividend facts were read (DATA_PROVENANCE §4.5).
- There is no need to do this again: the Pass 2 build runs on the Mac and verifies every hash itself.
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

## Never in the project (and never pushed to any git remote)

- `panel_confirm_SEALED.csv`, in any build, including the Pass 2 rebuild.
- `Book2.xlsx`, `usdjpy_dukascopy_*.csv`, `eurusd_dukascopy_*.csv`, and the HistData masters.
- The Pass 2 raw pulls: 1306 OHLC, session and US-session FX, a Nikkei proxy, XAU.
- Any forward-holdout data (after 2026-03-05), before and after `prereg-v1`.
