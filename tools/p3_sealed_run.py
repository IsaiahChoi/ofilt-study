"""P3 sealed-run tool (DQ1, DQ3, DQ4; PASS3_STATUS Decision log, "Design of the sealed-run tool").

Modes (one of):
  --synthetic (default)  a synthetic stand-in with a temporary BLIND_FIT_LOG, as tools/report_B7.py --synthetic;
  --rehearsal            synthetic, and also loads the dev panel (io.load_dev, targets.add_targets) to populate the
                         fingerprint registry (DQ1.5; P3-3 only);
  --real                 the one sanctioned sealed fit: only if OFILT_RUN_SEALED=1 is set for that command, the tree
                         is clean and --expect-config-sha256 equals docs/P3_RUN_CONFIG.json's SHA-256 (DQ1.7);
  --smoke N              synthetic only: every cell capped at N replications.
Utilities: --write-config writes docs/P3_RUN_CONFIG.json from the registry; --check-config validates it.

Start-up order: (1) the run's own temporary directory, set as tempfile.tempdir before any ofilt module is imported,
and registry.SYNTHETIC_PATH asserted inside it (DQ1.2); (2) the configuration validated (rebuilt from the registry
and compared) and, in real mode, the mode conditions checked before any data file is read; (3) exactly one
DevCalibrator. Tasks then run in the configured order (T1, T5 boundary, T2, the pooled critical values, T6, T3);
an exception in a task is recorded by class and line only and the next task runs; a failed assertion aborts.
Outputs: aggregates only (the configured whitelist), JSON and markdown rewritten after each flush, with runtime
fields in their own `runtime` section. No per-replication value is written or printed. No decision rule is applied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))                    # path only: no ofilt module is imported here
sys.path.insert(0, str(ROOT / "tools"))
CONFIG_PATH = ROOT / "docs" / "P3_RUN_CONFIG.json"
STATUS_PATH = ROOT / "PASS3_STATUS.md"
SPEC_PATH = ROOT / "spec" / "analysis_spec_dev_v1.yaml"
REAL_OUT = ROOT / "reports"
REAL_STEM = "P3_4_sealed_run"
SEALED_ENV = "OFILT_RUN_SEALED"
SCRIPT_NAME = "p3_sealed_run.py"
EXIT_REFUSED, EXIT_ABORTED = 2, 3
MAX_LIST = 20
REQUIRED_KEYS = ("T_conf", "T_source", "K_early", "a2", "cells", "cw_cal_cell", "dev_panel_sha256", "expected_lag",
                 "mean_block", "methods", "n_dates_T3", "outputs", "pooled_cells", "rows", "rules", "seeds", "sesoi",
                 "spec_sha256", "stand_in", "task_order")
OUTPUT_KEYS = sorted({
    "tool", "mode", "smoke", "config_sha256", "spec_sha256", "dev_panel_sha256", "head", "calibrator", "T_source",
    "rows", "cells", "cell", "task", "b", "replications", "n_dates", "window", "lag", "estimates", "mean_bias", "sd",
    "mean_se", "se_over_sd", "dk_normal", "bootstrap", "calibrated", "reject", "coverage", "tost", "primary", "low",
    "high", "k", "n", "rate", "wilson95", "h3", "own_quantiles", "c_boot", "c_cal", "c_boot_h3", "q95", "q90", "value",
    "interval", "rank", "rank_interval", "pooled", "estimators", "ols_dk", "huber_dk", "winsorised_ols_dk",
    "mean_share_downweighted", "mde80", "probit_interpolated", "normal_approx_sd", "normal_approx_mean_se", "t3",
    "c_cw_cal", "cw", "normal", "h1", "crosstab", "h1_method", "cw_method", "both", "h1_only", "cw_only", "neither",
    "walk_forward_calls", "registry_lines", "errors", "error_class", "line", "complete", "aborted", "runtime",
    "tasks", "seconds", "seconds_per_replication", "calibrator_seconds", "total_seconds"})


class AbortRun(Exception):
    """A failed run assertion: the run stops (DQ1.3, DQ1.4)."""


class Refused(Exception):
    """The run refuses to start (mode, configuration or tree)."""


# ====================================================================== pure helpers (no ofilt import)
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def _write_file(path: Path, text: str) -> None:
    """The only function that writes a file (it creates the parent directory if needed)."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8")


def _rule_lines() -> dict:
    """Rules copied verbatim from PASS3_STATUS.md's Decision log, and AM-02 from the spec (inference.size_rule)."""
    import yaml
    lines = STATUS_PATH.read_text(encoding="utf-8").splitlines()

    def one(prefix: str) -> str:
        hit = [l for l in lines if l.startswith(prefix)]
        if len(hit) != 1:
            raise ValueError(f"rule line {prefix!r} found {len(hit)} times")
        return hit[0]

    def block(prefix: str, sub: str) -> list:
        i = lines.index(one(prefix))
        out = [lines[i]]
        while i + 1 < len(lines) and lines[i + 1].startswith(sub):
            i += 1
            out.append(lines[i])
        return out

    d43 = one(">   - D4.3 T6.")
    flag = re.search(r"If an estimator's rate at b = 0 on early-window draws lies outside \[3\.5%, 6\.5%\], the "
                     r"pre-registration flags that robustness row as unreliable on coarse-grid periods\.", d43)
    if flag is None:
        raise ValueError("D4.3 flag sentence not found")
    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    return {"D2.6": [one(">   - D2.6 Viability")], "D2.7": [one(">   - D2.7 Claim wording")],
            "D3.4": block(">   - D3.4 The joint T1/T4 rule", ">     - "), "D4.3_flag": [flag.group(0)],
            "D3.2_D3.3_amended": block("> - D3.2 and D3.3 amended", ">   - "),
            "AM-02": [spec["inference"]["size_rule"]]}


def build_config() -> dict:
    """docs/P3_RUN_CONFIG.json's content, every registry value read by script."""
    import yaml
    from ofilt.drift import calendar as CAL                 # lazy: build/check only, never in run start-up
    spec_bytes = SPEC_PATH.read_bytes()
    spec_sha = sha256_bytes(spec_bytes)
    spec = yaml.safe_load(spec_bytes.decode("utf-8"))
    c7 = json.loads((ROOT / "reports" / "C7_mc.json").read_text(encoding="utf-8"))["key"]["spec_sha256"]
    if spec_sha != c7:
        raise ValueError("spec SHA-256 differs from the C7 key's (registry)")
    reg = json.loads((ROOT / "docs" / "PASS2_INPUTS.json").read_text(encoding="utf-8"))
    dev = reg["pass2_outputs"]["panel_dev.csv"]["sha256"]
    if dev != spec["data"]["dev_panel_sha256"]:
        raise ValueError("dev-panel hash: PASS2_INPUTS.json and the spec disagree")
    p0b = (ROOT / "reports" / "P3_0b_preflight.md").read_text(encoding="utf-8")
    t_source = int(re.search(r"^- Kept unique dates \(T_source\): \*\*(\d+)\*\*$", p0b, re.M).group(1))
    rows = int(re.search(r"^- Kept rows: \*\*(\d+)\*\*$", p0b, re.M).group(1))
    m = re.search(r"^- Kept dates with 1, 2 and 3 tickers: 1: (\d+), 2: (\d+), 3: (\d+)$", p0b, re.M)
    one_t, two_t, three_t = (int(x) for x in m.groups())
    p2b = (ROOT / "reports" / "P3_2b_preflight.md").read_text(encoding="utf-8")
    km = re.search(r"^- K, kept unique dates before (\d{4}-\d{2}-\d{2}): \*\*(\d+)\*\*$", p2b, re.M)
    k_early, k_date = int(km.group(2)), km.group(1)
    s1 = (ROOT / "reports" / "P3_1_sesoi.md").read_text(encoding="utf-8")
    sesoi = {c: float(re.search(rf"^\| {c} \|.*\| \*\*([0-9.eE+-]+)\*\* \|$", s1, re.M).group(1))
             for c in ("primary", "low", "high")}
    if sesoi != {"primary": 0.8652, "low": 0.07152, "high": 2.719}:      # approved four-significant-digit values
        raise ValueError(f"SESOI values {sesoi} differ from the approved ones")
    t_conf = int(CAL.T_CONF)
    n3 = t_source + t_conf
    cells = [dict(id=0, task="T1", b=0.0, replications=5000, n_dates=t_conf, window="full"),
             dict(id=1, task="T5_boundary", b=sesoi["primary"], replications=5000, n_dates=t_conf, window="full"),
             dict(id=2, task="T2", b=0.10, replications=1000, n_dates=t_conf, window="full"),
             dict(id=3, task="T2", b=0.25, replications=1000, n_dates=t_conf, window="full"),
             dict(id=4, task="T2", b=0.40, replications=1000, n_dates=t_conf, window="full"),
             dict(id=5, task="T6", b=0.0, replications=1000, n_dates=t_conf, window="full"),
             dict(id=6, task="T6", b=0.25, replications=1000, n_dates=t_conf, window="full"),
             dict(id=7, task="T6", b=0.0, replications=1000, n_dates=t_conf, window="early"),
             dict(id=8, task="T6", b=0.25, replications=1000, n_dates=t_conf, window="early"),
             dict(id=9, task="T3", b=0.0, replications=2000, n_dates=n3, window="full"),
             dict(id=10, task="T3", b=0.10, replications=500, n_dates=n3, window="full"),
             dict(id=11, task="T3", b=0.25, replications=500, n_dates=n3, window="full")]
    return {
        "spec_sha256": spec_sha, "dev_panel_sha256": dev, "T_source": t_source, "rows": rows,
        "K_early": k_early, "T_conf": t_conf, "n_dates_T3": n3, "sesoi": sesoi, "cells": cells,
        "mean_block": 5.0, "a2": 0, "expected_lag": 6, "pooled_cells": [0, 1, 2, 3, 4], "cw_cal_cell": 9,
        "stand_in": {
            "dates": t_source, "one_ticker_dates": one_t, "two_ticker_dates": two_t, "three_ticker_dates": three_t,
            "panel": "sim.synthetic_panel(T_source, b=0.4, a2=-0.2, seed=spec seed + 7, p_excl=0) as "
                     "tools/report_B7.py's stand-in, then abn_oc set missing on seeded rows "
                     "(numpy.random.default_rng(spec seed + 8)) so that the dates keep 1, 2 and 3 tickers as counted",
            "source": "reports/P3_0b_preflight.md (Part A)"},
        "seeds": {
            "spec_seed": int(spec["seeds"]["global"]), "outer_offset": 5000000, "cell_stride": 100000,
            "warp_offset": 50000,
            "outer": "spec seed + 5,000,000 + 100,000 * cell + replication (D4.5)",
            "warp": "outer seed + 50,000: calib.bootstrap_t_given_fit(draw, ..., numpy.random.default_rng(warp), "
                    "B=1) for cells 0 to 4",
            "early_window_positions": "calib.window_positions(K_early, n_dates, numpy.random.default_rng(outer seed))",
            "draw": "DevCalibrator.draw(b, 0.0, seed=outer seed, ...) creates numpy.random.default_rng(seed) "
                    "(sim.py:221) and uses it for the stationary-bootstrap positions only when positions is None "
                    "(sim.py:222); when positions are given (T6's early window) the generator is unused and the seed "
                    "is only recorded in attrs['truth'] (sim.py:235-237)",
            "walk_forward": "forecast.walk_forward(..., seed=outer seed) (M2 and M3 do not use it)"},
        "methods": {
            "alpha": float(spec["inference"]["alpha"]),
            "h1": {
                "dk_normal": "reject if |t| > z = scipy.stats.norm.ppf(1 - alpha/2), the quantile of "
                             "inference.Result.contrast (inference.py:208-212, whose p = 2 sf(|z|) < alpha is the "
                             "same decision); interval b +/- z se; TOST at scipy.stats.norm.ppf(1 - alpha), as "
                             "inference.tost (inference.py:341)",
                "bootstrap": "reject if |t| > c_boot(0.95), the order statistic of |t*| pooled over pooled_cells "
                             "(D3.1, D3.2 amended); interval b +/- c_boot(0.95) se; TOST at c_boot(0.90)",
                "calibrated": "reject if |t| > c_cal(0.95), the order statistic of |(b_hat - b)/se| pooled over "
                              "pooled_cells (D3.3 amended); interval b +/- c_cal(0.95) se; TOST at c_cal(0.90)"},
            "cw": {"normal": "one-sided: reject if p = scipy.stats.norm.sf(stat) < alpha (fctests.py:146-147)",
                   "calibrated": "reject if stat > c_CW,cal, the 0.95 order statistic of the Clark-West statistic "
                                 "over cw_cal_cell (D3.3)"},
            "h3": "dk_normal as for H1; bootstrap at c_boot_h3(0.95), the order statistic of |t*_h3| pooled over "
                  "pooled_cells (D3.5); H3 keeps the normal reference under c_cal",
            "t6": "OLS-DK (calib.fit_t), Huber-DK (inference.fit_huber on inference.build_design of the draw; c "
                  "and scale from the spec) and OLS-DK on calib.winsorise_fx of the draw; normal reference",
            "mde80": "calib.mde80 over cells 0, 2, 3, 4 (b = 0, 0.10, 0.25, 0.40) per H1 method; cross-checks "
                     "with sd(b_hat) and mean se pooled over pooled_cells",
            "order_statistics": "calib.order_stat (the ceil(level n)-th smallest) with calib.order_stat_interval"},
        "outputs": OUTPUT_KEYS,
        "rules": _rule_lines(),
        "task_order": [{"task": "T1", "cells": [0]}, {"task": "T5_boundary", "cells": [1]},
                       {"task": "T2", "cells": [2, 3, 4]}, {"task": "T6", "cells": [5, 6, 7, 8]},
                       {"task": "T3", "cells": [9, 10, 11]}],
        "early_window_before": k_date,
    }


def config_text(cfg: dict) -> str:
    return json.dumps(cfg, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def validate_config(cfg: dict) -> list:
    """Problems with a configuration: missing keys, or any difference from the configuration rebuilt now."""
    missing = [k for k in REQUIRED_KEYS if k not in cfg]
    if missing:
        return [f"missing key(s) {missing}"]
    rebuilt = build_config()
    return [f"key {k!r} differs from the registry" for k in sorted(set(rebuilt) | set(cfg)) if cfg.get(k) != rebuilt.get(k)]


def combo_refusal(*, real: bool, smoke, rehearsal: bool) -> str | None:
    """Mode combinations, checked first (before any import of ofilt or any data)."""
    if real and smoke is not None:
        return "--real cannot be combined with --smoke"
    if real and rehearsal:
        return "--real cannot be combined with --rehearsal"
    if smoke is not None and smoke < 2:
        return "--smoke needs N >= 2"
    return None


def mode_refusal(*, real: bool, smoke, rehearsal: bool, sealed_value, config_sha: str, expected_sha, dirty) -> str | None:
    """The reason to refuse, or None: the mode combinations, then, in real mode, the sealed environment variable,
    the expected configuration SHA-256 and the tree, in that order. It reads nothing itself."""
    reason = combo_refusal(real=real, smoke=smoke, rehearsal=rehearsal)
    if reason or not real:
        return reason
    if sealed_value != "1":
        return f"--real needs {SEALED_ENV}=1 for this command"
    if expected_sha is None or expected_sha != config_sha:
        return "--expect-config-sha256 does not equal the configuration file's SHA-256"
    if dirty:
        return "the working tree is dirty"
    return None


def check_log(path: Path, n_expected: int, panel_sha: str | None = None, caller: str | None = None) -> list:
    """Problems with BLIND_FIT_LOG: line count, all dev_real; and, if given, the last line's panel hash and caller."""
    recs = [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
    p = []
    if len(recs) != n_expected:
        p.append(f"{len(recs)} lines, expected {n_expected}")
    if any(r.get("provenance") != "dev_real" for r in recs):
        p.append("a line is not dev_real")
    if recs and panel_sha is not None and recs[-1].get("panel_sha256") != panel_sha:
        p.append("the last line's panel hash differs")
    if recs and caller is not None and caller not in str(recs[-1].get("caller", "")):
        p.append("the last line's caller does not name this script")
    return p


def seed_ranges(cfg: dict) -> list:
    """(lo, hi) offsets from the spec seed, inclusive, of every configured seed (outer and warp)."""
    s = cfg["seeds"]
    out = []
    for c in cfg["cells"]:
        lo = s["outer_offset"] + s["cell_stride"] * c["id"]
        out.append((lo, lo + c["replications"] - 1))
        if c["id"] in cfg["pooled_cells"]:
            out.append((lo + s["warp_offset"], lo + s["warp_offset"] + c["replications"] - 1))
    return out


def check_output(obj, allowed: set, path: str = "") -> list:
    """Problems: keys outside the whitelist, or lists longer than MAX_LIST."""
    p = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k not in allowed:
                p.append(f"key {path}/{k} not in the whitelist")
            p += check_output(v, allowed, f"{path}/{k}")
    elif isinstance(obj, list):
        if len(obj) > MAX_LIST:
            p.append(f"list {path} has {len(obj)} entries")
        for i, v in enumerate(obj):
            p += check_output(v, allowed, f"{path}[{i}]")
    return p


def _script_line(e: BaseException) -> int:
    tb = traceback.extract_tb(e.__traceback__)
    mine = [f for f in tb if f.filename.endswith(SCRIPT_NAME)]
    return int((mine or tb)[-1].lineno) if tb else -1


# ====================================================================== the run
def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--synthetic", action="store_true")
    g.add_argument("--real", action="store_true")
    ap.add_argument("--rehearsal", action="store_true")
    ap.add_argument("--smoke", type=int, default=None)
    ap.add_argument("--expect-config-sha256", default=None)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--write-config", action="store_true")
    ap.add_argument("--check-config", action="store_true")
    a = ap.parse_args(argv)
    if a.write_config or a.check_config:
        cfg = build_config()
        if a.write_config:
            if CONFIG_PATH.exists():
                print(f"REFUSED: {CONFIG_PATH} exists")
                return EXIT_REFUSED
            _write_file(CONFIG_PATH, config_text(cfg))
        problems = validate_config(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
        print(f"config {CONFIG_PATH.relative_to(ROOT)} SHA-256 {sha256_file(CONFIG_PATH)}; valid: {not problems}")
        return 0 if not problems else EXIT_REFUSED
    reason = combo_refusal(real=a.real, smoke=a.smoke, rehearsal=a.rehearsal)
    if reason:
        print(f"REFUSED: {reason}")
        return EXIT_REFUSED
    sys_tmp = Path(tempfile.gettempdir()).resolve()
    if a.real:
        if a.out_dir is not None:
            print("REFUSED: --real writes reports/P3_4_sealed_run.* and takes no --out-dir")
            return EXIT_REFUSED
        out_dir = REAL_OUT
    else:
        if a.out_dir is None:
            print("REFUSED: synthetic modes need --out-dir under /tmp")
            return EXIT_REFUSED
        out_dir = a.out_dir.resolve()
        if not (out_dir.is_relative_to(Path("/tmp").resolve()) or out_dir.is_relative_to(sys_tmp)):
            print("REFUSED: --out-dir must lie under /tmp (or the system temporary directory)")
            return EXIT_REFUSED
    # (1) the run's own temporary directory, before any ofilt import (DQ1.2)
    run_tmp = Path(tempfile.mkdtemp(prefix="p3_sealed_run_")).resolve()
    previous = tempfile.tempdir
    tempfile.tempdir = str(run_tmp)
    try:
        return _run(a, run_tmp, out_dir)
    except Refused as e:
        print(f"REFUSED: {e}")
        return EXIT_REFUSED
    except AbortRun as e:
        print(f"ABORTED at line {_script_line(e)} (before the first flush)")
        return EXIT_ABORTED
    finally:
        shutil.rmtree(run_tmp, ignore_errors=True)
        tempfile.tempdir = previous


def _run(a, run_tmp: Path, out_dir: Path) -> int:
    import importlib
    R = importlib.import_module("ofilt.drift.registry")
    if Path(R.SYNTHETIC_PATH).resolve().parent != run_tmp:
        raise AbortRun("registry.SYNTHETIC_PATH lies outside the run's temporary directory")
    import numpy as np
    from scipy import stats
    from ofilt.drift import calib as C
    from ofilt.drift import fctests as FT
    from ofilt.drift import forecast as F
    from ofilt.drift import inference as I
    from ofilt.drift import io as IO
    from ofilt.drift import sim as S
    from ofilt.drift import targets as TG
    from ofilt.drift.models import M2, M3
    from ofilt.drift.spec import Spec
    from p3_0b_preflight import verify_panel

    # (2) configuration and mode conditions, before any data file is read
    cfg_bytes = CONFIG_PATH.read_bytes()
    cfg_sha = sha256_bytes(cfg_bytes)
    cfg = json.loads(cfg_bytes.decode("utf-8"))
    problems = validate_config(cfg)
    if problems:
        raise Refused(f"configuration: {problems}")
    head, dirty = R.git_state()
    if a.real:
        reason = mode_refusal(real=True, smoke=a.smoke, rehearsal=a.rehearsal,
                              sealed_value=os.environ.get(SEALED_ENV), config_sha=cfg_sha,
                              expected_sha=a.expect_config_sha256, dirty=dirty)
        if reason:
            raise Refused(reason)
    spec = Spec.load()
    alpha = float(cfg["methods"]["alpha"])
    z2, z1 = float(stats.norm.ppf(1 - alpha / 2)), float(stats.norm.ppf(1 - alpha))
    lag6, h1n = int(cfg["expected_lag"]), spec.h1_parameter
    mode = "real" if a.real else ("rehearsal" if a.rehearsal else "synthetic")
    paths = (out_dir / f"{REAL_STEM}.json", out_dir / f"{REAL_STEM}.md")
    allowed = set(cfg["outputs"])
    t_start = time.time()
    state = {"tool": f"tools/{SCRIPT_NAME}", "mode": mode, "smoke": a.smoke, "config_sha256": cfg_sha,
             "spec_sha256": cfg["spec_sha256"], "dev_panel_sha256": cfg["dev_panel_sha256"], "head": head,
             "calibrator": None, "cells": [], "pooled": None, "mde80": None, "t3": None, "errors": [],
             "complete": False, "aborted": None, "runtime": {"tasks": [], "calibrator_seconds": None,
                                                              "total_seconds": None}}

    def flush():
        state["runtime"]["total_seconds"] = time.time() - t_start
        p = check_output(state, allowed)
        if p:
            raise AbortRun(f"output check: {p[:3]}")
        _write_file(paths[0], json.dumps(state, indent=1, sort_keys=True, allow_nan=False) + "\n")
        _write_file(paths[1], render_md(state))

    def assert_lag(lag, what):
        if int(lag) != lag6:
            raise AbortRun(f"{what}: lag {lag} != {lag6}")

    try:
        # ------------------------------------------------ data and the ONE calibrator
        if a.real:
            if spec.sha256 != cfg["spec_sha256"]:
                raise AbortRun("spec SHA-256 differs from the configuration")
            digest = verify_panel(IO.DATA_DIR / IO.DEV_FILE, spec)
            if digest != cfg["dev_panel_sha256"]:
                raise AbortRun("dev panel SHA-256 differs from the configuration")
            base = TG.add_targets(IO.load_dev(IO.DATA_DIR / IO.DEV_FILE, spec), spec)
            assert_am03_target(base, spec)
            log_path = S.BLIND_FIT_LOG_PATH
            p = check_log(log_path, 6)
            if p:
                raise AbortRun(f"BLIND_FIT_LOG before: {p}")
        else:
            real_log = ROOT / "BLIND_FIT_LOG"
            real_log_sha = sha256_file(real_log)
            S.BLIND_FIT_LOG_PATH = run_tmp / "BLIND_FIT_LOG"
            if a.rehearsal:
                digest = verify_panel(IO.DATA_DIR / IO.DEV_FILE, spec)
                if digest != cfg["dev_panel_sha256"]:
                    raise AbortRun("dev panel SHA-256 differs from the configuration")
                dev = TG.add_targets(IO.load_dev(IO.DATA_DIR / IO.DEV_FILE, spec), spec)   # registers real targets
                assert_am03_target(dev, spec)
                del dev
            base = stand_in(cfg, spec, S, np)
        t0 = time.time()
        cal = S.DevCalibrator(base, spec)                                   # the ONE sealed fit
        state["runtime"]["calibrator_seconds"] = time.time() - t0
        del base
        if a.real:
            p = check_log(log_path, 7, panel_sha=cfg["dev_panel_sha256"], caller=SCRIPT_NAME)
            if p:
                raise AbortRun(f"BLIND_FIT_LOG after the calibrator: {p}")
        assert_calibrator_shape(cal, cfg)
        state["calibrator"] = {"T_source": int(cal.T), "rows": int(cfg["rows"])}
        flush()

        cells = {c["id"]: c for c in cfg["cells"]}
        smoke = a.smoke

        def reps(c):
            return c["replications"] if smoke is None else min(c["replications"], smoke)

        def seed(c, r):
            s = cfg["seeds"]
            return spec.seed + s["outer_offset"] + s["cell_stride"] * c["id"] + r

        mem = {}                                                            # per-replication values, memory only

        def run_task(name, fn, n_cells):
            t = time.time()
            n_reps = 0
            try:
                n_reps = fn()
            except AbortRun:
                raise
            except Exception as e:                                          # class and line only (DQ1.4)
                state["errors"].append({"task": name, "error_class": type(e).__name__, "line": _script_line(e)})
            sec = time.time() - t
            state["runtime"]["tasks"].append({"task": name, "seconds": sec, "replications": n_reps,
                                              "seconds_per_replication": sec / n_reps if n_reps else None})
            flush()

        # ------------------------------------------------ cells 0 to 4 (T1, T5 boundary, T2)
        def h1_cell(cid):
            c = cells[cid]
            n = reps(c)
            v = {k: np.empty(n) for k in ("b", "se", "t", "t3", "ts", "ts3")}
            for r in range(n):
                s = seed(c, r)
                y = cal.draw(c["b"], float(cfg["a2"]), seed=s, n_dates=c["n_dates"])
                f = C.fit_t(y, spec, "y_sim")
                assert_lag(f["lag"], f"cell {cid} fit")
                w = C.bootstrap_t_given_fit(y, spec, np.random.default_rng(s + cfg["seeds"]["warp_offset"]),
                                            "y_sim", 1, f, cfg["mean_block"])
                v["b"][r], v["se"][r], v["t"][r], v["t3"][r] = f["b"], f["se"], f["t"], f["t_h3"]
                v["ts"][r], v["ts3"][r] = w["t_star"][0], w["t_star_h3"][0]
            mem[cid] = v
            out = cell_head(c, n)
            out["estimates"] = est_summary(v["b"], v["se"], c["b"])
            out["dk_normal"] = method_block(v, c["b"], z2, z1, cfg, cid, C)
            if cid == 0:
                out["h3"] = {"dk_normal": rate(int((np.abs(v["t3"]) > z2).sum()), n, C), "bootstrap": None}
            state["cells"].append(out)
            return n

        def task_cells(ids):
            def fn():
                tot = 0
                for cid in ids:
                    tot += h1_cell(cid)
                    flush()
                return tot
            return fn

        run_task("T1", task_cells([0]), 1)
        run_task("T5_boundary", task_cells([1]), 1)
        run_task("T2", task_cells([2, 3, 4]), 3)

        # ------------------------------------------------ pooled critical values (D3.2, D3.3 amended)
        def pooled():
            ids = cfg["pooled_cells"]
            if not all(i in mem for i in ids):
                raise RuntimeError("pooled cells incomplete")
            ts = np.abs(np.concatenate([mem[i]["ts"] for i in ids]))
            zc = np.abs(np.concatenate([(mem[i]["b"] - cells[i]["b"]) / mem[i]["se"] for i in ids]))
            ts3 = np.abs(np.concatenate([mem[i]["ts3"] for i in ids]))
            pool = {"cells": list(ids), "c_boot": qpair(ts, C), "c_cal": qpair(zc, C),
                    "c_boot_h3": {"q95": os_summary(ts3, 0.95, C)}}
            state["pooled"] = pool
            cb95, cb90 = pool["c_boot"]["q95"]["value"], pool["c_boot"]["q90"]["value"]
            cc95, cc90 = pool["c_cal"]["q95"]["value"], pool["c_cal"]["q90"]["value"]
            for out in state["cells"]:
                cid = out["cell"]
                if cid not in ids:
                    continue
                v, b = mem[cid], cells[cid]["b"]
                out["bootstrap"] = method_block(v, b, cb95, cb90, cfg, cid, C)
                out["calibrated"] = method_block(v, b, cc95, cc90, cfg, cid, C)
                out["own_quantiles"] = {"c_boot": qpair(np.abs(v["ts"]), C),
                                        "c_cal": qpair(np.abs((v["b"] - b) / v["se"]), C)}
                if cid == 0:
                    out["h3"]["bootstrap"] = rate(int((np.abs(v["t3"]) > pool["c_boot_h3"]["q95"]["value"]).sum()),
                                                  len(v["t3"]), C)
            mde_ids = [0, 2, 3, 4]
            sd = float(np.std(np.concatenate([mem[i]["b"] - cells[i]["b"] for i in ids]), ddof=1))
            mse = float(np.mean(np.concatenate([mem[i]["se"] for i in ids])))
            by = {o["cell"]: o for o in state["cells"]}
            state["mde80"] = {"cells": mde_ids}
            for m in ("dk_normal", "bootstrap", "calibrated"):
                state["mde80"][m] = C.mde80([cells[i]["b"] for i in mde_ids],
                                            [by[i][m]["reject"]["rate"] for i in mde_ids], sd=sd, mean_se=mse)
            return 0

        run_task("pooled", pooled, 0)

        # ------------------------------------------------ T6 (cells 5 to 8)
        def t6():
            tot = 0
            for cid in (5, 6, 7, 8):
                c = cells[cid]
                n = reps(c)
                v = {k: np.empty(n) for k in ("ob", "ose", "hb", "hse", "hsh", "wb", "wse")}
                for r in range(n):
                    s = seed(c, r)
                    if c["window"] == "early":
                        pos = C.window_positions(cfg["K_early"], c["n_dates"], np.random.default_rng(s),
                                                 cfg["mean_block"])
                        y = cal.draw(c["b"], float(cfg["a2"]), seed=s, positions=pos, n_dates=c["n_dates"])
                    else:
                        y = cal.draw(c["b"], float(cfg["a2"]), seed=s, n_dates=c["n_dates"])
                    f = C.fit_t(y, spec, "y_sim")
                    h = I.fit_huber(I.build_design(y, spec, target="y_sim"), spec)
                    fw = C.fit_t(C.winsorise_fx(y, spec), spec, "y_sim")
                    assert_lag(f["lag"], f"cell {cid} OLS")
                    assert_lag(h.lag, f"cell {cid} Huber")
                    assert_lag(fw["lag"], f"cell {cid} winsorised")
                    ph = h.param(h1n)
                    v["ob"][r], v["ose"][r] = f["b"], f["se"]
                    v["hb"][r], v["hse"][r], v["hsh"][r] = ph["estimate"], ph["se"], h.info["share_downweighted"]
                    v["wb"][r], v["wse"][r] = fw["b"], fw["se"]
                out = cell_head(c, n)
                out["estimators"] = {
                    "ols_dk": t6_block(v["ob"], v["ose"], c["b"], z2, C),
                    "huber_dk": dict(t6_block(v["hb"], v["hse"], c["b"], z2, C),
                                     mean_share_downweighted=float(np.mean(v["hsh"]))),
                    "winsorised_ols_dk": t6_block(v["wb"], v["wse"], c["b"], z2, C)}
                state["cells"].append(out)
                flush()
                tot += n
            return tot

        run_task("T6", t6, 4)

        # ------------------------------------------------ T3 (cells 9 to 11)
        wf_calls = [0]

        def t3():
            pool = state["pooled"]
            cb95 = pool["c_boot"]["q95"]["value"] if pool else None
            cc95 = pool["c_cal"]["q95"]["value"] if pool else None
            state["t3"] = {"c_cw_cal": None, "cells": [], "walk_forward_calls": 0, "registry_lines": None}
            tot, ccw = 0, None
            for cid in (9, 10, 11):
                c = cells[cid]
                n = reps(c)
                v = {k: np.empty(n) for k in ("b", "se", "t", "cw", "cwp")}
                for r in range(n):
                    s = seed(c, r)
                    y = cal.draw(c["b"], float(cfg["a2"]), seed=s, n_dates=c["n_dates"])
                    y["excl_inference"] = False
                    y["excl_forecast_eval"] = False
                    preds, _ = F.walk_forward(y, {"M2": M2, "M3": M3}, spec, target="y_sim", seed=s)
                    wf_calls[0] += 1
                    state["t3"]["walk_forward_calls"] = wf_calls[0]
                    cut = np.sort(y["date"].unique())[-cfg["T_conf"]]
                    sub = preds[preds["date"] >= cut]
                    FT.pair(sub, "M3", "M2")
                    cw = FT.clark_west(sub, "M3", "M2", spec)
                    assert_lag(cw["lag"], f"cell {cid} Clark-West")
                    f = C.fit_t(y[y["date"] >= cut], spec, "y_sim")
                    assert_lag(f["lag"], f"cell {cid} H1")
                    v["b"][r], v["se"][r], v["t"][r], v["cw"][r], v["cwp"][r] = f["b"], f["se"], f["t"], cw["stat"], cw["p"]
                if cid == cfg["cw_cal_cell"]:
                    state["t3"]["c_cw_cal"] = os_summary(v["cw"], 0.95, C)
                    ccw = state["t3"]["c_cw_cal"]["value"]
                h1 = {"dk_normal": np.abs(v["t"]) > z2,
                      "bootstrap": None if cb95 is None else np.abs(v["t"]) > cb95,
                      "calibrated": None if cc95 is None else np.abs(v["t"]) > cc95}
                cwd = {"normal": v["cwp"] < alpha, "calibrated": None if ccw is None else v["cw"] > ccw}
                out = cell_head(c, n)
                out["estimates"] = est_summary(v["b"], v["se"], c["b"])
                out["h1"] = {m: None if d is None else rate(int(d.sum()), n, C) for m, d in h1.items()}
                out["cw"] = {m: None if d is None else rate(int(d.sum()), n, C) for m, d in cwd.items()}
                out["crosstab"] = [{"h1_method": hm, "cw_method": cm, "both": int((hd & cd).sum()),
                                    "h1_only": int((hd & ~cd).sum()), "cw_only": int((~hd & cd).sum()),
                                    "neither": int((~hd & ~cd).sum())}
                                   for hm, hd in h1.items() if hd is not None
                                   for cm, cd in cwd.items() if cd is not None]
                state["t3"]["cells"].append(out)
                flush()
                tot += n
            return tot

        run_task("T3", t3, 3)

        # ------------------------------------------------ the run-registry directory (DQ1.2)
        reg = Path(R.SYNTHETIC_PATH)
        n_lines = len(reg.read_text(encoding="utf-8").splitlines()) if reg.exists() else 0
        others = sorted(p.name for p in run_tmp.iterdir() if p != reg and p.name != "BLIND_FIT_LOG")
        if n_lines != wf_calls[0] or others or (a.real and (run_tmp / "BLIND_FIT_LOG").exists()):
            raise AbortRun(f"run-registry directory: {n_lines} lines for {wf_calls[0]} calls; other entries {len(others)}")
        if state["t3"] is not None:
            state["t3"]["registry_lines"] = n_lines
        if a.real:
            p = check_log(log_path, 7, panel_sha=cfg["dev_panel_sha256"], caller=SCRIPT_NAME)
            if p:
                raise AbortRun(f"BLIND_FIT_LOG at the end: {p}")
        elif sha256_file(real_log) != real_log_sha:
            raise AbortRun("the repository's BLIND_FIT_LOG changed during a non-real run")
        state["complete"] = True
        flush()
        print(f"COMPLETE: {paths[0]} and {paths[1]}; errors: {len(state['errors'])}")
        return 0
    except AbortRun as e:
        state["aborted"] = {"error_class": "AbortRun", "line": _script_line(e)}
        try:
            flush()
        except AbortRun:
            pass
        print(f"ABORTED at line {_script_line(e)}")
        return EXIT_ABORTED


# ====================================================================== helpers used by the run
def assert_am03_target(df, spec) -> None:
    """The sealed fit's target is AM-03's: abn_oc on the spec's hedge (y_1306_oc) with the expanding past-only beta on
    non-excluded rows (targets.add_targets' record, targets.py:130-131)."""
    bs = spec.beta
    want = dict(method=bs.method, window=None, estimate_on=bs.estimate_on, hedge=spec.hedge_oc_column,
                lag_days=bs.lag_days, min_periods=bs.min_periods)
    if df.attrs.get("targets") != want or spec.hedge_oc_column != "y_1306_oc" or bs.method != "expanding" \
            or bs.estimate_on != "non_excluded_rows":
        raise AbortRun("the target is not AM-03's")


def assert_calibrator_shape(cal, cfg) -> None:
    """Source dates == T_source and rows == rows; the rows are read from the calibrator's private row bounds, here
    only."""
    if int(cal.T) != int(cfg["T_source"]) or int(cal._bounds[-1]) != int(cfg["rows"]):
        raise AbortRun("calibrator shape differs from the configured T_source and rows")


def stand_in(cfg, spec, S, np):
    """sim.synthetic_panel(T_source) with abn_oc removed on seeded rows: the configured 1-, 2- and 3-ticker dates."""
    st = cfg["stand_in"]
    df = S.synthetic_panel(int(st["dates"]), b=0.4, a2=-0.2, seed=spec.seed + 7, p_excl=0.0)
    rng = np.random.default_rng(spec.seed + 8)
    dates = np.sort(df["date"].unique())
    order = rng.permutation(len(dates))
    n1, n2 = int(st["one_ticker_dates"]), int(st["two_ticker_dates"])
    tick = df["ticker"].astype(str).to_numpy()
    tickers = sorted(set(tick))
    dvals = df["date"].to_numpy()
    drop = np.zeros(len(df), dtype=bool)
    for j, d in enumerate(dates[order[: n1 + n2]]):
        on = dvals == d
        pick = tickers[int(rng.integers(0, len(tickers)))]
        drop |= on & ((tick != pick) if j < n1 else (tick == pick))
    df.loc[drop, "abn_oc"] = np.nan
    return df


def rate(k: int, n: int, C) -> dict:
    lo, hi = C.wilson(int(k), int(n))
    return {"k": int(k), "n": int(n), "rate": k / n, "wilson95": [lo, hi]}


def os_summary(x, level: float, C) -> dict:
    k, lo, hi = C.order_stat_ranks(len(x), level)
    il, ih = C.order_stat_interval(x, level)
    return {"value": C.order_stat(x, level), "interval": [il, ih], "rank": k, "rank_interval": [lo, hi],
            "n": int(len(x))}


def qpair(x, C) -> dict:
    return {"q95": os_summary(x, 0.95, C), "q90": os_summary(x, 0.90, C)}


def est_summary(bhat, se, b) -> dict:
    import numpy as np
    sd = float(np.std(bhat, ddof=1))
    return {"mean_bias": float(np.mean(bhat - b)), "sd": sd, "mean_se": float(np.mean(se)),
            "se_over_sd": float(np.mean(se) / sd)}


def method_block(v, b, c95, c90, cfg, cid, C) -> dict:
    import numpy as np
    n = len(v["b"])
    out = {"reject": rate(int((np.abs(v["t"]) > c95).sum()), n, C),
           "coverage": rate(int((np.abs(v["b"] - b) <= c95 * v["se"]).sum()), n, C), "tost": None}
    if cid in (0, 1):
        out["tost"] = {k: rate(int(C.tost_declares(v["b"], v["se"], s, c90).sum()), n, C)
                       for k, s in cfg["sesoi"].items()}
    return out


def t6_block(bhat, se, b, z2, C) -> dict:
    import numpy as np
    n = len(bhat)
    return {"reject": rate(int((np.abs(bhat / se) > z2).sum()), n, C),
            "coverage": rate(int((np.abs(bhat - b) <= z2 * se).sum()), n, C),
            "estimates": est_summary(bhat, se, b)}


def cell_head(c, n) -> dict:
    return {"cell": c["id"], "task": c["task"], "b": c["b"], "replications": int(n), "n_dates": c["n_dates"],
            "window": c["window"], "lag": 6, "estimates": None, "dk_normal": None, "bootstrap": None,
            "calibrated": None}


def _f(x) -> str:
    return "-" if x is None else (f"{x:.4f}" if isinstance(x, float) else str(x))


def _r(d) -> str:
    return "-" if d is None else f"{d['k']}/{d['n']} = {d['rate']:.4f} [{d['wilson95'][0]:.4f}, {d['wilson95'][1]:.4f}]"


def render_md(state: dict) -> str:
    """Markdown view of the JSON aggregates; the runtime section comes last."""
    smoke = "" if state["smoke"] is None else f", smoke {state['smoke']}"
    L = [f"# P3 sealed run ({state['mode']}{smoke})", "",
         f"Generated by `{state['tool']}`. Configuration SHA-256 `{state['config_sha256']}`; spec "
         f"`{state['spec_sha256']}`; dev panel `{state['dev_panel_sha256']}`; HEAD `{state['head']}`. "
         "Aggregates only; no decision rule is applied here.", ""]
    if state["calibrator"]:
        L += [f"Calibrator: T_source {state['calibrator']['T_source']}, rows {state['calibrator']['rows']}.", ""]
    L += ["## Cells 0 to 4 (T1, T5 boundary, T2) and T6", "",
          "| Cell | Task | b | Reps | Window | DK-normal reject | Bootstrap reject | Calibrated reject | mean bias | sd | "
          "mean se | se/sd |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for o in state["cells"]:
        e = o.get("estimates") or {}
        if "estimators" in o:
            for name, blk in o["estimators"].items():
                es = blk["estimates"]
                L.append(f"| {o['cell']} | {o['task']} {name} | {o['b']} | {o['replications']} | {o['window']} | "
                         f"{_r(blk['reject'])} | - | - | {_f(es['mean_bias'])} | {_f(es['sd'])} | {_f(es['mean_se'])} | "
                         f"{_f(es['se_over_sd'])} |")
            continue
        L.append(f"| {o['cell']} | {o['task']} | {o['b']} | {o['replications']} | {o['window']} | "
                 f"{_r((o.get('dk_normal') or {}).get('reject'))} | {_r((o.get('bootstrap') or {}).get('reject'))} | "
                 f"{_r((o.get('calibrated') or {}).get('reject'))} | {_f(e.get('mean_bias'))} | {_f(e.get('sd'))} | "
                 f"{_f(e.get('mean_se'))} | {_f(e.get('se_over_sd'))} |")
    L.append("")
    if state["pooled"]:
        p = state["pooled"]
        L += ["## Pooled critical values (cells " + ", ".join(map(str, p["cells"])) + ")", ""]
        for k in ("c_boot", "c_cal"):
            for q in ("q95", "q90"):
                s = p[k][q]
                L.append(f"- {k} {q}: {s['value']:.6f} (rank {s['rank']} of {s['n']}; interval "
                         f"[{s['interval'][0]:.6f}, {s['interval'][1]:.6f}])")
        s = p["c_boot_h3"]["q95"]
        L += [f"- c_boot_h3 q95: {s['value']:.6f} (rank {s['rank']} of {s['n']})", ""]
    if state["mde80"]:
        L += ["## MDE80", ""] + [f"- {m}: {state['mde80'][m]}" for m in ("dk_normal", "bootstrap", "calibrated")] + [""]
    for o in state["cells"]:
        if o.get("dk_normal") and o["dk_normal"].get("tost"):
            L.append(f"TOST, cell {o['cell']}: " + "; ".join(
                f"{m}: " + ", ".join(f"{k} {_r(v)}" for k, v in (o[m] or {}).get("tost", {}).items())
                for m in ("dk_normal", "bootstrap", "calibrated") if o.get(m)))
        if o.get("h3"):
            L.append(f"H3, cell {o['cell']}: dk_normal {_r(o['h3']['dk_normal'])}; bootstrap {_r(o['h3']['bootstrap'])}")
    L.append("")
    if state["t3"]:
        t3 = state["t3"]
        L += ["## T3", "", f"c_CW,cal: {t3['c_cw_cal']}", f"walk_forward calls: {t3['walk_forward_calls']}; "
              f"registry lines: {t3['registry_lines']}", ""]
        for o in t3["cells"]:
            L.append(f"- cell {o['cell']} (b {o['b']}, {o['replications']} reps): H1 " + "; ".join(
                f"{m} {_r(v)}" for m, v in o["h1"].items()) + "; CW " + "; ".join(f"{m} {_r(v)}" for m, v in o["cw"].items()))
            for x in o["crosstab"]:
                L.append(f"  - {x['h1_method']} x {x['cw_method']}: both {x['both']}, H1 only {x['h1_only']}, "
                         f"CW only {x['cw_only']}, neither {x['neither']}")
        L.append("")
    L += ["## Status", "", f"- complete: {state['complete']}; aborted: {state['aborted']}; errors: {state['errors']}", "",
          "## Runtime", ""]
    rt = state["runtime"]
    L.append(f"- calibrator: {_f(rt['calibrator_seconds'])} s; total: {_f(rt['total_seconds'])} s")
    for t in rt["tasks"]:
        L.append(f"- {t['task']}: {_f(t['seconds'])} s for {t['replications']} replications "
                 f"({_f(t['seconds_per_replication'])} s each)")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
