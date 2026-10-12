"""P5-1 (P5Q5): the confirmation run script, as docs/P5_CONFIRM_SCRIPT_SPEC.md (version 1) specifies.

  python tools/p6_confirm_run.py --out DIR

The one run of Pass 6 (P13(c): the confirmation panel is opened once, by the pre-registered script). In order, it
refuses, writes nothing and returns 2:
  1. if DIR exists;
  2. unless OFILT_P6_CONFIRM_RUN=P6-1 is set (the run's own sanction, set only in Pass 6, on Isaiah's sanction);
  3. if io.ACCESS_LOG_PATH exists (any earlier request of the confirmation panel, granted or denied: a second run is a
     dated, labelled deviation, which Isaiah decides).
Then it loads the dev panel and the firm events through io.load_dev and io.load_events_firm, and the confirmation panel
through io.load_confirm, whose guard refuses until the pre-registration tag is an ancestor of HEAD; assembles the
document with confirm_run.build_document; writes it with confirm_run.write_outputs (document.json, manifest.json,
runtime.json); prints each file's path and SHA-256; and returns 0. Every other failure raises. The analysis is
confirm_run's, unchanged: given the same frames, this script and tools/p4_confirm_run.py write byte-identical
document.json and manifest.json files.
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ofilt.drift import confirm_run, io  # noqa: E402

EXIT_REFUSED = 2
CONFIRM_RUN_SANCTION_VAR = "OFILT_P6_CONFIRM_RUN"
CONFIRM_RUN_SANCTION_VALUE = "P6-1"
SANCTION_REFUSAL = "REFUSED: the confirmation run needs its sanction (Pass 6): set OFILT_P6_CONFIRM_RUN=P6-1"
ONE_SHOT_REFUSAL = ("REFUSED: {path} exists: the confirmation panel has been requested before; a second run is a "
                    "dated, labelled deviation (P13(c)), which Isaiah decides")


def _confirm_frames():
    """(dev, events, confirm), or None if refused. The sanction is checked first and the one-shot rule second; refused,
    nothing is loaded."""
    if os.environ.get(CONFIRM_RUN_SANCTION_VAR) != CONFIRM_RUN_SANCTION_VALUE:
        print(SANCTION_REFUSAL)
        return None
    if Path(io.ACCESS_LOG_PATH).exists():
        print(ONE_SHOT_REFUSAL.format(path=io.ACCESS_LOG_PATH))
        return None
    dev = io.load_dev()
    events = io.load_events_firm()
    confirm = io.load_confirm()
    return dev, events, confirm


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description="The confirmation run (P5Q5; Pass 6).")
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"REFUSED: --out {a.out} exists")
        return EXIT_REFUSED
    frames = _confirm_frames()
    if frames is None:
        return EXIT_REFUSED
    assembled = confirm_run.build_document(*frames)
    hashes = confirm_run.write_outputs(a.out, assembled)
    for name in confirm_run.OUTPUT_FILES:
        print(f"{a.out / name} {hashes[name]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
