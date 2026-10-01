"""A6: compute the two Stage-A spec values from PREDICTOR-ONLY dev statistics.

  robustness.winsorize_fx.values           = per-column numpy-linear quantiles at q
  secondary_family_holm.rv_per_bar_dev_median = median of usdjpy_rv / usdjpy_bars

Unit = one value per DATE (FX is market-wide: identical on the 3 ticker rows of a
date, asserted), over ALL dev dates (no event exclusions: those are ticker-
specific and FX is not). No target column is read.

usage:  python tools/fill_spec_A6.py           # print values and fill TO_FILL lines in place
        python tools/fill_spec_A6.py --check   # recompute and compare with the live spec
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift.spec import DEFAULT_SPEC_PATH, UNFILLED, Spec  # noqa: E402

FMT = ".10e"   # always has a dot and a signed exponent, so PyYAML types it as float
PREDICTOR_COLS = ["date", "usdjpy_ret", "eurusd_ret", "usdjpy_rv", "usdjpy_bars", "window_hours"]


def per_date_predictors():
    dev = IO.load_dev()
    p = dev[PREDICTOR_COLS]  # predictor-only projection; targets are never touched below
    if (p.groupby("date").nunique() > 1).any().any():
        raise SystemExit("FX predictors differ across tickers within a date")
    return p.drop_duplicates("date").reset_index(drop=True)


def compute(spec: Spec | None = None) -> dict:
    spec = spec or Spec.load()
    w = spec.raw("robustness.winsorize_fx")
    d = per_date_predictors()
    if not (d.usdjpy_bars > 0).all():
        raise SystemExit("usdjpy_bars must be > 0 on every dev date")
    vals = {c: [float(np.quantile(d[c].to_numpy(float), q)) for q in w["q"]] for c in w["cols"]}
    med = float(np.median((d.usdjpy_rv / d.usdjpy_bars).to_numpy(float)))
    return {"winsor": vals, "rv_per_bar_dev_median": med, "n_dates": int(len(d))}


def fmt(x: float) -> str:
    return format(x, FMT)


def fill(path: Path = DEFAULT_SPEC_PATH) -> dict:
    v = compute()
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    win = "{" + ", ".join(f"{c}: [{fmt(lo)}, {fmt(hi)}]" for c, (lo, hi) in v["winsor"].items()) + "}"
    done = set()
    for i, ln in enumerate(lines):
        if UNFILLED not in ln:
            continue
        if ln.lstrip().startswith("winsorize_fx:") and ln.count(UNFILLED) == 1:
            lines[i] = ln.replace(f"values: {UNFILLED}", f"values: {win}"); done.add("winsor")
        elif ln.lstrip().startswith("rv_per_bar_dev_median:") and ln.count(UNFILLED) == 1:
            lines[i] = ln.replace(UNFILLED, fmt(v["rv_per_bar_dev_median"])); done.add("rv")
        else:
            raise SystemExit(f"unexpected TO_FILL line {i + 1}: {ln.strip()}")
    if done != {"winsor", "rv"}:
        raise SystemExit(f"expected two TO_FILL lines, filled {sorted(done)}")
    path.write_text("".join(lines), encoding="utf-8")
    sp = Spec.load(path)  # re-validates types and content
    if sp.unfilled():
        raise SystemExit(f"still unfilled: {sp.unfilled()}")
    return v


def check(spec: Spec | None = None) -> bool:
    spec = spec or Spec.load()
    v = compute(spec)
    ok = all(fmt(a) == fmt(b) for c, (lo, hi) in v["winsor"].items()
             for a, b in zip((lo, hi), spec.winsor_bounds()[c]))
    return ok and fmt(v["rv_per_bar_dev_median"]) == fmt(spec.rv_per_bar_dev_median())


if __name__ == "__main__":
    if "--check" in sys.argv:
        print("spec matches recomputation:", check())
    else:
        print(fill())
