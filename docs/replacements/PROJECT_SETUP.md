# What goes in the Claude Project, and why (October 2026, after Pass 1)

This supersedes the October 2026 (pre-Pass-1) version.

## Correction to the earlier version (kept)

An earlier version said project files cannot be loaded or computed on. That is wrong for sessions with code execution: project files are on disk at `/mnt/project/` and load normally with pandas. The reasons for keeping raw data out of the project are different, and they are stronger.

## Why raw data stays out

1. **It is not needed.** Models use only `panel_dev.csv`. Raw files matter only for rebuilding the panel: the Pass 2 rebuild (P34), the post-open-FX mechanism version, or the intraday extension. For those, attach them to that single conversation and rerun `build_panel.py`.
2. **The holdout depends on it.** `Book2.xlsx`, both Dukascopy files, the Pass 2 pulls and `panel_confirm_SEALED.csv` all contain 2022–2026 data. Anything in the project is readable in every future session. A sealed file inside the project is sealed only by convention.
3. **Reproducibility does not require it.** `MANIFEST.json` holds the SHA-256 of every input and output. Anyone with the raw files can rerun the scripts and prove they get an identical panel.

Keep the raw files on your machine plus one backup.

## Why the code repo stays out

The analysis machine is a git repository, not project files: `ofilt/drift/`, `spec/`, `tests/`, `tools/`, `docs/`, `reports/`, `BLIND_FIT_LOG`, `RUN_REGISTRY.jsonl` and `PASS1_STATUS.md`. A session that works on it gets the repo as an attached tarball and returns an updated tarball, as Pass 1 did.

- **Git history is the source of truth.** Project copies are read-only snapshots that drift from it.
- **The blinding guard needs the git tags.** `spec-dev-v1` and `prereg-v1` must be ancestors of HEAD, so it only works inside the repo.
- **The two logs are append-only and must not fork.** `BLIND_FIT_LOG` (sealed fits) and `RUN_REGISTRY.jsonl` (every walk-forward run) should only be appended to; two copies of the repo would produce two diverging logs.

## In the project

`README.md`, `PROJECT_SETUP.md`, `PLAN.md` (v2.1), `DATA_PROVENANCE.md`, `DATA_DICTIONARY.md`, `MANIFEST.json`, `DECISIONS_ADDENDUM.md` (P01–P13), `DECISIONS_P14_onward.md` (P14–P36), `panel_dev.csv`, `build_panel.py`, `make_events.py`, `events.py`, `events_firm.csv`, `events_boj.csv`, `pull_dukascopy.py`, and the Math 86 paper.

After Pass 1, replace `README.md`, `PLAN.md`, `DATA_DICTIONARY.md` and `PROJECT_SETUP.md` with the versions in the repo's `docs/replacements/` (each has a `.diff` against the previous project copy), and add `DECISIONS_P14_onward.md` from `docs/`. After Pass 2, replace `panel_dev.csv`, `MANIFEST.json`, `DATA_PROVENANCE.md` and the event files with the rebuilt versions.

## Removed from the project (superseded; they would mislead future sessions)

| File | Why |
|---|---|
| `fx_dark_window_features.csv` | HistData-based; its window end included the bar labeled 08:59 (a price at 09:00:00); covers 2023–2026 |
| `build_windows.py` | Replaced by `build_panel.py` (it used a naive business-day calendar and the same endpoint problem) |
| `histdata_tz.py` | HistData retired; mis-corrects the autumn 2025 window |
| `slim_encode.py` | Compressed the HistData masters, which are no longer used |
| `MASTER_README__1_.md` | Described the HistData masters; replaced by `README.md` |
| `Plan` (v2.0) | Replaced by `PLAN.md` v2.1 |

## Never in the project

- `panel_confirm_SEALED.csv`, in any build, including the Pass 2 rebuild.
- `Book2.xlsx`, `usdjpy_dukascopy_*.csv`, `eurusd_dukascopy_*.csv`, and the HistData masters.
- The Pass 2 raw pulls: 1306 OHLC, session and US-session FX, a Nikkei proxy, XAU.
- Any forward-holdout data (after 2026-03-05), before and after `prereg-v1`.
