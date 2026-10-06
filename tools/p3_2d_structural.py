"""P3-2d R3: a structural check of the real-data construction path (PASS3_STATUS Decision log, the supervisor's review).

The dev panel is hash-checked against the registry before it is read, loaded with io.load_dev and built with
targets.add_targets (which registers the real targets in the fingerprint registry). A frame is built from it that
keeps exactly the columns _sealed_blind_fit and DevCalibrator read:
  date, ticker; the exclusion flags (spec.inference_exclusion_flags; inference.py:92 and :98);
  spec.require_nonmissing and the target abn_oc (inference.py:93-94, target "abn_oc" at sim.py:164);
  the predictors DevCalibrator copies (sim.PRED_COLUMNS, read at sim.py:203).
Of these, abn_oc (a constructed target) and beta (estimated from the target) are replaced by synthetic values on exactly
the rows where the real ones are present (seeded normal, sd 0.02, for abn_oc; 1.0 for beta), and stay missing elsewhere.
Every other column is dropped, including every y_* and ao_* column, open, close and prev_close. The frame's attrs are
replaced by provenance synthetic (blind.mark_synthetic), so the fingerprint guard checks the draw against the registered
real targets. One DevCalibrator is constructed with sim.BLIND_FIT_LOG_PATH at /tmp/p3_2d_struct/BLIND_FIT_LOG.
No real target value enters any computation. Prints only booleans and counts; writes reports/P3_2d_structural.md.
usage: python tools/p3_2d_structural.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from p3_0b_preflight import verify_panel  # noqa: E402
from ofilt.drift import blind as B  # noqa: E402
from ofilt.drift import calib as C  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

TARGET = "abn_oc"
REPLACED = ("abn_oc", "beta")
ABN_SD = 0.02
LOG_DIR = Path("/tmp/p3_2d_struct")
SEED = 20261006


def kept_columns(spec: Spec) -> list[str]:
    """The columns _sealed_blind_fit and DevCalibrator read, in a fixed order."""
    cols = ["date", "ticker"] + list(spec.inference_exclusion_flags) + list(spec.require_nonmissing) + [TARGET]
    cols += list(S.PRED_COLUMNS)
    return list(dict.fromkeys(cols))


def build_structural_frame(df: pd.DataFrame, spec: Spec, rng: np.random.Generator) -> pd.DataFrame:
    """The kept columns only; abn_oc and beta replaced by synthetic values where the real ones are present."""
    out = df[kept_columns(spec)].copy()
    out.attrs = {}
    present = {c: out[c].notna().to_numpy() for c in REPLACED}
    abn = np.full(len(out), np.nan)
    abn[present[TARGET]] = rng.normal(0.0, ABN_SD, int(present[TARGET].sum()))
    out[TARGET] = abn
    out["beta"] = np.where(present["beta"], 1.0, np.nan)
    return B.mark_synthetic(out)


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "reports" / "P3_2d_structural.md")
    a = ap.parse_args(argv)
    spec = Spec.load()
    cfg = json.loads((ROOT / "docs" / "P3_RUN_CONFIG.json").read_text(encoding="utf-8"))
    repo_log = ROOT / "BLIND_FIT_LOG"
    log_sha0 = sha_file(repo_log)
    path = IO.DATA_DIR / IO.DEV_FILE
    digest = verify_panel(path, spec)                                    # before the file is read
    dev = TG.add_targets(IO.load_dev(path, spec), spec)                  # registers the real targets
    frame = build_structural_frame(dev, spec, np.random.default_rng(SEED))
    del dev
    dropped_ok = not any(c.startswith(("y_", "ao_")) or c in ("open", "close", "prev_close") for c in frame.columns)
    LOG_DIR.mkdir(parents=True, exist_ok=False)
    S.BLIND_FIT_LOG_PATH = LOG_DIR / "BLIND_FIT_LOG"
    res = {}
    try:
        cal = S.DevCalibrator(frame, spec)                               # synthetic provenance: a temporary log line
        res["construction succeeded"] = True
    except Exception as e:                                               # class only
        res["construction succeeded"] = False
        res[f"construction error class {type(e).__name__}"] = False
        cal = None
    if cal is not None:
        res[f"T == {cfg['T_source']} (T = {cal.T})"] = int(cal.T) == int(cfg["T_source"])
        res[f"rows == {cfg['rows']} (rows = {int(cal._bounds[-1])})"] = int(cal._bounds[-1]) == int(cfg["rows"])
        y = cal.draw(0.0, 0.0, seed=SEED + 1, n_dates=int(cfg["T_conf"]))
        res["one draw (b = 0, seeded, n_dates = T_conf) passes the guard"] = B.require_unblinded(y) == B.SYNTHETIC
        res["the draw has exactly SIM_COLUMNS"] = tuple(y.columns) == S.SIM_COLUMNS
        f = C.fit_t(y, spec, "y_sim")
        res[f"calib.fit_t on the draw reports lag 6 (lag = {f['lag']})"] = int(f["lag"]) == 6
    recs = [json.loads(x) for x in S.BLIND_FIT_LOG_PATH.read_text(encoding="utf-8").splitlines() if x.strip()] \
        if S.BLIND_FIT_LOG_PATH.exists() else []
    res[f"the temporary log has 1 line with provenance synthetic ({len(recs)} line(s))"] = \
        len(recs) == 1 and recs[0].get("provenance") == B.SYNTHETIC
    res["the repository's BLIND_FIT_LOG is unchanged"] = sha_file(repo_log) == log_sha0
    res["the frame holds no y_*, ao_*, open, close or prev_close column"] = dropped_ok
    ok = all(res.values())
    L = ["# P3-2d structural check of the real-data construction path (R3)", "",
         f"Generated by `tools/p3_2d_structural.py`. Dev panel SHA-256 `{digest}` (checked against the registry before "
         "it was read); targets built by `targets.add_targets`, which registered the real targets. The frame keeps "
         f"{len(frame.columns)} columns ({', '.join(frame.columns)}); `abn_oc` and `beta` were replaced by synthetic "
         "values on exactly the rows where the real ones are present; the frame is labelled synthetic; one "
         "`DevCalibrator` was constructed with a temporary log. Booleans and counts only.", ""]
    L += [f"- {k}: {v}" for k, v in res.items()]
    L += ["", f"Gate (every boolean True): {ok}", ""]
    md = "\n".join(L)
    a.out.write_text(md, encoding="utf-8")
    print(md, end="")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
