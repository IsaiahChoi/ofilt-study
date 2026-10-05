"""C7 slow tier (DECISIONS P28), synthetic only: Clark-West M3 vs M2 size and power on
Gaussian `sim.synthetic_panel` panels, and on the SAME panels the in-sample H1 test on the
last 1013 dates (the evaluation window), for the joint (H1, CW) cross-tab.

Design: each panel has N_DATES = 1513 dates (fold 0 trains on 500 eligible dates, so
T_eval ~ 1013); b in {0 (size, 300 reps), 0.40 (200), 0.25 (200)}, a2 = 0, p_excl = 0.02
(earnings-type exclusions; excl_inference = excl_forecast_eval = earn_flag). Per rep: one
walk_forward call with {M2, M3}; fctests.clark_west (one-sided, NW lag at T_eval); H1 =
inference.fit_dk on build_design of the last 1013 dates (two-sided, and one-sided b > 0).
Seed of rep r in cell c = spec seed + 3,000,000 + 100,000 c + r, so results do not depend
on how the run is chunked.

Resumable: state is saved to the partial file after every chunk of reps; a later call
resumes (refusing a partial written under a different config or different code). When
every cell is complete it writes reports/C7_mc.json and reports/C7_h1_same_dgp.json with
code hashes (staleness) and deletes the partial. Usage:
    OFILT_SLOW=1 python tools/c7_mc.py --budget 160      # repeat until it prints COMPLETE
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import fctests as FT  # noqa: E402
from ofilt.drift import forecast as F  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift.models import M2, M3  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

CODE_FILES = ("tools/c7_mc.py", "ofilt/drift/fctests.py", "ofilt/drift/forecast.py",
              "ofilt/drift/models/linear.py", "ofilt/drift/sim.py", "ofilt/drift/inference.py")
FULL = dict(n_dates=1513, h1_dates=1013, p_excl=0.02, seed_offset=3_000_000,
            cells=[["size", 0.0, 300], ["power_040", 0.40, 200], ["power_025", 0.25, 200]],
            bands={"size": [0.02, 0.09], "power_040_min": 0.80},
            out=["reports/C7_mc.json", "reports/C7_h1_same_dgp.json"], partial="reports/C7_mc.partial.json")


def code_hashes() -> dict:
    return {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in CODE_FILES}


def panel(seed: int, b: float, cfg: dict):
    df = S.synthetic_panel(cfg["n_dates"], b=b, seed=seed, p_excl=cfg["p_excl"])
    df["excl_inference"] = df.earn_flag == 1
    df["excl_forecast_eval"] = df.earn_flag == 1
    return B.mark_synthetic(df)


def one_rep(seed: int, b: float, cfg: dict, spec: Spec) -> dict:
    df = panel(seed, b, cfg)
    preds, _ = F.walk_forward(df, {"M2": M2, "M3": M3}, spec)
    cw = FT.clark_west(preds, "M3", "M2", spec)
    last = df[df.date >= np.sort(df.date.unique())[-cfg["h1_dates"]]]
    h1 = I.fit_dk(I.build_design(last, spec), spec).param(spec.h1_parameter)
    a = spec.alpha
    return dict(seed=int(seed), cw_stat=cw["stat"], cw_p=cw["p"], cw_reject=bool(cw["reject"]), T_eval=cw["T"],
                cw_lag=cw["lag"], h1_b=h1["estimate"], h1_z=h1["z"], h1_reject2=bool(h1["p"] < a),
                h1_reject1=bool(stats.norm.sf(h1["z"]) < a))


def config_key(cfg: dict, spec: Spec) -> dict:
    return dict(cfg=cfg, spec_seed=spec.seed, spec_sha256=spec.sha256, code=code_hashes())


def summarise(state: dict) -> tuple[dict, dict]:
    cfg = state["key"]["cfg"]
    cells = {}
    for name, b, n in cfg["cells"]:
        reps = state["reps"][name]
        k = sum(r["cw_reject"] for r in reps)
        h2 = [r for r in reps if r["h1_reject2"]]
        cells[name] = dict(b=b, reps=n, cw=FT.rate_summary(k, n),
                           h1_two_sided=FT.rate_summary(len(h2), n),
                           h1_one_sided=FT.rate_summary(sum(r["h1_reject1"] for r in reps), n),
                           agree_among_h1_two=[sum(r["cw_reject"] for r in h2), len(h2)],
                           crosstab={"h1_and_cw": sum(r["h1_reject2"] and r["cw_reject"] for r in reps),
                                     "h1_only": sum(r["h1_reject2"] and not r["cw_reject"] for r in reps),
                                     "cw_only": sum(r["cw_reject"] and not r["h1_reject2"] for r in reps),
                                     "neither": sum(not (r["h1_reject2"] or r["cw_reject"]) for r in reps)},
                           T_eval_range=[min(r["T_eval"] for r in reps), max(r["T_eval"] for r in reps)],
                           cw_lag=sorted({r["cw_lag"] for r in reps}))
    common = dict(key=state["key"], runtime_s=state["runtime_s"], label="synthetic Gaussian DGP (P28); not binding")
    mc = dict(common, cells=cells, reps={k: v for k, v in state["reps"].items()})
    h1 = dict(common, cell="power_025", **{k: cells["power_025"][k] for k in
                                           ("b", "reps", "cw", "h1_two_sided", "h1_one_sided", "agree_among_h1_two",
                                            "crosstab")})
    return mc, h1


def run(cfg: dict = FULL, budget: float = 160.0, root: Path = ROOT, spec: Spec | None = None) -> bool:
    """Run reps until done or the time budget is spent; True when the reports are written."""
    spec = spec or Spec.load()
    key = config_key(cfg, spec)
    part = root / cfg["partial"]
    if part.exists():
        state = json.loads(part.read_text())
        if state["key"] != key:
            raise RuntimeError(f"{part} was written under a different config or code; delete it to restart")
    else:
        state = dict(key=key, reps={name: [] for name, _, _ in cfg["cells"]}, runtime_s=0.0)
    t0, base = time.time(), float(state["runtime_s"])

    def save():
        state["runtime_s"] = base + (time.time() - t0)
        part.parent.mkdir(parents=True, exist_ok=True)
        part.write_text(json.dumps(state, allow_nan=False))

    for c, (name, b, n) in enumerate(cfg["cells"]):
        done = state["reps"][name]
        while len(done) < n and time.time() - t0 < budget:
            done.append(one_rep(spec.seed + cfg["seed_offset"] + 100_000 * c + len(done), b, cfg, spec))
            if len(done) % 10 == 0:
                save()
    save()
    if any(len(state["reps"][name]) < n for name, _, n in cfg["cells"]):
        return False
    mc, h1 = summarise(state)
    for path, obj in zip(cfg["out"], (mc, h1)):
        (root / path).write_text(json.dumps(obj, indent=1, allow_nan=False) + "\n")
    part.unlink(missing_ok=True)
    return True


if __name__ == "__main__":
    if os.environ.get("OFILT_SLOW") != "1":
        sys.exit("slow tier: set OFILT_SLOW=1")
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=160.0)
    done = run(budget=ap.parse_args().budget)
    st = json.loads((ROOT / FULL["partial"]).read_text()) if not done else None
    print("COMPLETE" if done else "PARTIAL " + json.dumps({k: len(v) for k, v in st["reps"].items()}), flush=True)
