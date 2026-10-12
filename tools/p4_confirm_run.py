"""P4-4c2 (P4Q39): the confirmation run script, as docs/P4_CONFIRM_RUN_SPEC.md (version 1), section 4, specifies.

  --source synthetic --seed INT [--scenario JSON] [--dev-dates N] --out DIR
      a simulated panel (ofilt.drift.sim_full, the absolute seed given; the scenario's keyword arguments as a JSON
      object, lists becoming tuples; the last N dates of its dev calendar); the forecasting calls record to the
      temporary synthetic registry.
  --source dev --out DIR
      the dev run of P4-6, only under its sanction (OFILT_P4_DEV_RUN=P4-6 in the environment): the dev panel and the
      firm events through their loaders, each verified by its hash; the forecasting calls record to
      RUN_REGISTRY.jsonl (P4Q6). Not run in P4-4c2.
  --source confirm --out DIR
      refused: the confirmation panel is not opened in Pass 4 (P4Q3; P13(c)).

Each branch is decided before anything is loaded or simulated. --out must not exist. The whole document is built by
confirm_run.build_document and written by confirm_run.write_outputs (document.json, manifest.json, runtime.json); the
script prints each file's path and SHA-256 and returns 0. A refusal prints one REFUSED line, writes nothing and
returns 2.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ofilt.drift import confirm_run, io, sim_full  # noqa: E402

EXIT_REFUSED = 2
CONFIRM_REFUSAL = ("REFUSED: the confirmation panel is not opened in Pass 4 (P4Q3; P13(c)); the confirmation run is "
                   "Pass 6's")
DEV_REFUSAL = "REFUSED: the dev run needs its sanction (P4-6): set OFILT_P4_DEV_RUN=P4-6"


def _dev_frames():
    # The sanction is checked first; without it nothing is called. Returns (dev, events, None) or None if refused.
    if os.environ.get(confirm_run.DEV_RUN_SANCTION_VAR) != confirm_run.DEV_RUN_SANCTION_VALUE:
        print(DEV_REFUSAL)
        return None
    dev = io.load_dev()
    events = io.load_events_firm()
    return dev, events, None


def _synthetic_frames(seed: int, scenario: dict, dev_dates: int | None):
    """(dev, events, confirm) of one simulation."""
    sc = sim_full.Scenario(**{k: tuple(v) if isinstance(v, list) else v for k, v in scenario.items()})
    dates = None if dev_dates is None else sim_full.dev_calendar()[-dev_dates:]
    out = sim_full.simulate(seed, sc, dev_dates=dates)
    return out.dev, out.events, out.confirm


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description="The confirmation run (P4Q39).")
    ap.add_argument("--source", required=True, choices=("synthetic", "dev", "confirm"))
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--scenario", default=None)
    ap.add_argument("--dev-dates", type=int, default=None)
    a = ap.parse_args(argv)
    if a.source == "confirm":
        print(CONFIRM_REFUSAL)
        return EXIT_REFUSED
    if a.source == "synthetic":
        if a.seed is None:
            ap.error("--seed is required with --source synthetic")
    elif a.seed is not None or a.scenario is not None or a.dev_dates is not None:
        ap.error("--seed, --scenario and --dev-dates are for --source synthetic only")
    if a.out.exists():
        print(f"REFUSED: --out {a.out} exists")
        return EXIT_REFUSED
    if a.source == "dev":
        frames = _dev_frames()
        if frames is None:
            return EXIT_REFUSED
    else:
        scenario = json.loads(a.scenario) if a.scenario is not None else {}
        if not isinstance(scenario, dict):
            ap.error("--scenario must be a JSON object")
        frames = _synthetic_frames(a.seed, scenario, a.dev_dates)
    assembled = confirm_run.build_document(*frames)
    hashes = confirm_run.write_outputs(a.out, assembled)
    for name in confirm_run.OUTPUT_FILES:
        print(f"{a.out / name} {hashes[name]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
