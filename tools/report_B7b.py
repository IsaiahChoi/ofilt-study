"""B7b: size/power PREVIEW at T_conf (spec amendment AM-02).
PREVIEW at T_conf; binding run in Pass 4 after the 1306 rebuild changes the residuals.

  OFILT_RUN_SEALED=1 python tools/report_B7b.py                        # real dev: ONE sealed fit
  python tools/report_B7b.py --synthetic --size-reps 200 --power-reps 50  # dry run (temp log, /tmp)

All regressions are on SIMULATED targets from one DevCalibrator. The JSON is
rewritten after every cell, so partial results survive an interrupted run.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ofilt.drift import calendar as C  # noqa: E402
from ofilt.drift import inference as I  # noqa: E402
from ofilt.drift import io as IO  # noqa: E402
from ofilt.drift import sim as S  # noqa: E402
from ofilt.drift import targets as TG  # noqa: E402
from ofilt.drift.spec import Spec  # noqa: E402

LABEL = "PREVIEW at T_conf; binding run in Pass 4 after the 1306 rebuild changes the residuals"
POWER_GRID = (0.10, 0.25, 0.40)
BAND = (0.035, 0.065)
Z = float(stats.norm.ppf(0.975))


def wilson(k: int, n: int, z: float = Z) -> tuple[float, float]:
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(c - h), float(c + h)


def rate(x: np.ndarray) -> dict:
    k, n = int(x.sum()), len(x)
    p = k / n
    return dict(rate=p, k=k, n=n, mc_se=float(np.sqrt(p * (1 - p) / n)), wilson95=wilson(k, n))


def run_cell(cal, spec, reps, b_sim, seed0, T):
    out = {k: np.empty(reps) for k in ("b", "se_b", "p_b", "lo_b", "hi_b", "a", "se_a", "p_a", "lo_a", "hi_a")}
    for r in range(reps):
        y = cal.draw(b_sim, 0.0, seed=seed0 + r, n_dates=T)
        res = I.fit_dk(I.build_design(y, spec, target="y_sim"), spec)
        for tag, name in (("b", "usdjpy_ret"), ("a", "eurusd_ret")):
            p = res.param(name)
            out[tag][r], out[f"se_{tag}"][r], out[f"p_{tag}"][r] = p["estimate"], p["se"], p["p"]
            out[f"lo_{tag}"][r], out[f"hi_{tag}"][r] = p["ci"]
    return out


def calib(est, se, lo, hi, truth) -> dict:
    sd = float(np.std(est - truth, ddof=1))
    return dict(n=len(est), coverage=rate((lo <= truth) & (truth <= hi)), sd=sd, mean_se=float(np.mean(se)),
                se_over_sd=float(np.mean(se) / sd), bias=float(np.mean(est - truth)),
                bias_mc_se=float(sd / np.sqrt(len(est))))


def mde80(points: list[tuple[float, float]]) -> float | None:
    """Probit-scale linear interpolation of power(b) = 0.80 between bracketing grid points."""
    target = stats.norm.ppf(0.80)
    for (b0, p0), (b1, p1) in zip(points[:-1], points[1:]):
        if p0 <= 0.80 <= p1 and p1 > p0:
            q0, q1 = stats.norm.ppf(np.clip([p0, p1], 1e-6, 1 - 1e-6))
            return float(b0 + (target - q0) * (b1 - b0) / (q1 - q0))
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--size-reps", type=int, default=5000)
    ap.add_argument("--power-reps", type=int, default=1000)
    a = ap.parse_args()
    spec, T = Spec.load(), C.T_CONF
    seed_base = spec.seed + 1_000_000                       # disjoint from B7 (seed + 100000 .. + 230500)
    if a.synthetic:
        S.BLIND_FIT_LOG_PATH = Path(tempfile.mkdtemp()) / "BLIND_FIT_LOG"
        base = S.synthetic_panel(1708, b=0.4, a2=-0.2, seed=spec.seed + 7, p_excl=0.03)
        source, out = "SYNTHETIC STAND-IN (dry run)", Path("/tmp/B7b_size_preview_DRYRUN")
    else:
        base = TG.add_targets(IO.load_dev(), spec)
        source, out = "real dev residuals and fitted controls (ONE sealed blind fit)", ROOT / "reports" / "B7b_size_preview"
    log = S.BLIND_FIT_LOG_PATH
    n0 = len(log.read_text().splitlines()) if log.exists() else 0
    t0 = time.time()
    cal = S.DevCalibrator(base, spec)                       # the ONE sealed fit
    if len(log.read_text().splitlines()) - n0 != 1:
        raise SystemExit("expected exactly one sealed fit")
    cells = [("size", 0.0, a.size_reps)] + [("power", b, a.power_reps) for b in POWER_GRID]
    res, summary = {}, dict(label=LABEL, source=source, T=T, T_source=cal.T, lag=Spec.dk_lag(T),
                            seed_base=seed_base, cells=[])
    for ci, (kind, b, reps) in enumerate(cells):
        seed0 = seed_base + 100_000 * ci
        r = run_cell(cal, spec, reps, b, seed0, T)
        res[b] = r
        summary["cells"].append(dict(kind=kind, b_sim=b, reps=reps, seed0=seed0,
                                     reject_H1=rate(r["p_b"] < spec.alpha), reject_H3=rate(r["p_a"] < spec.alpha)))
        summary["elapsed_s"] = time.time() - t0
        out.with_suffix(".json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
        print(f"done {kind} b={b}: H1 reject {summary['cells'][-1]['reject_H1']['rate']:.4f}", flush=True)
    s0 = res[0.0]
    summary["size_calibration"] = dict(
        H1=calib(s0["b"], s0["se_b"], s0["lo_b"], s0["hi_b"], 0.0),
        H3=calib(s0["a"], s0["se_a"], s0["lo_a"], s0["hi_a"], 0.0))
    cat = lambda k: np.concatenate([res[b][k] for b in res])  # noqa: E731
    truth = np.concatenate([np.full(len(res[b]["b"]), b) for b in res])
    summary["pooled_calibration"] = dict(
        H1=calib(cat("b"), cat("se_b"), cat("lo_b"), cat("hi_b"), truth),
        H3=calib(cat("a"), cat("se_a"), cat("lo_a"), cat("hi_a"), np.zeros_like(truth)))
    pts = [(0.0, summary["cells"][0]["reject_H1"]["rate"])] + \
          [(c["b_sim"], c["reject_H1"]["rate"]) for c in summary["cells"][1:]]
    sd_pool = summary["pooled_calibration"]["H1"]["sd"]
    summary["mde80"] = dict(probit_interpolated=mde80(pts),
                            normal_approx_sd=float((Z + stats.norm.ppf(0.8)) * sd_pool),
                            normal_approx_mean_se=float((Z + stats.norm.ppf(0.8))
                                                        * summary["pooled_calibration"]["H1"]["mean_se"]))
    h1 = summary["cells"][0]["reject_H1"]
    flags = []
    if h1["wilson95"][0] > BAND[1]:
        flags.append("H1 size 95% MC interval lies entirely above 6.5%: the Pass 4 bootstrap fallback is LIKELY "
                     "(inference NOT switched now)")
    if h1["wilson95"][1] < BAND[0]:
        flags.append("H1 size 95% MC interval lies entirely below 3.5% (conservative); informational")
    summary["flags"], summary["elapsed_s"] = flags, time.time() - t0
    out.with_suffix(".json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

    def fr(x):
        return f"{x['rate']:.4f} (MC SE {x['mc_se']:.4f}; 95% MC [{x['wilson95'][0]:.4f}, {x['wilson95'][1]:.4f}])"

    def fc(c):
        return (f"{c['coverage']['rate']:.4f} (MC SE {c['coverage']['mc_se']:.4f}) | {c['se_over_sd']:.3f} | "
                f"{c['bias']:+.4f} ({c['bias_mc_se']:.4f}) | {c['sd']:.4f} | {c['mean_se']:.4f}")
    sc, pc, m = summary["size_calibration"], summary["pooled_calibration"], summary["mde80"]
    md = f"""# B7b: size and power at the confirmation length. **{LABEL}.**

Generated by `tools/report_B7b.py`. Source: {source}. One `DevCalibrator` (stationary bootstrap over
whole dates, mean block {cal.mean_block:g}) drawing T = **{T}** dates (= T_conf, `ofilt.drift.calendar`) from the
{cal.T} dev source dates; y_sim = fitted_controls* + b_sim e* + residuals*, a2_sim = 0. Primary design,
pooled OLS, DK Bartlett lag {summary['lag']}, normal reference, two-sided alpha {spec.alpha}. Seeds from
{seed_base} (disjoint from B7). Wilson score MC intervals.

## Size (b_sim = a2_sim = 0, {a.size_reps} reps). **{LABEL}.**

- H1 (usdjpy_ret) rejection: **{fr(h1)}**.
- H3 (eurusd_ret) rejection: {fr(summary['cells'][0]['reject_H3'])} (informational; the AM-02 rule is stated for b).
- AM-02 band [3.5%, 6.5%]: **{"; ".join(flags) if flags else "no flag (the H1 95% MC interval is not entirely outside the band)"}**.

| quantity | coverage of 95% CI | SE/sd | bias (MC SE) | sd | mean DK SE |
|---|---|---|---|---|---|
| H1, size cell | {fc(sc['H1'])} |
| H3, size cell | {fc(sc['H3'])} |
| H1, pooled over all {pc['H1']['n']} sims | {fc(pc['H1'])} |
| H3, pooled over all {pc['H3']['n']} sims | {fc(pc['H3'])} |

(Pooling is valid because b_hat - b_sim = [(X*'X*)^-1 X*' resid*]_e does not depend on b_sim.)

## Power ({a.power_reps} reps per b_sim, T = {T}). **{LABEL}.**

| b_sim | H1 rejection (MC SE; 95% MC) |
|---|---|
""" + "\n".join(f"| {c['b_sim']:.2f} | {fr(c['reject_H1'])} |" for c in summary["cells"]) + f"""

**MDE at 80% power:** {'not bracketed by the grid' if m['probit_interpolated'] is None else format(m['probit_interpolated'], '.3f')} (probit-scale interpolation between bracketing grid
points). Cross-checks: (z_0.975 + z_0.80) x sd(b_hat) = {m['normal_approx_sd']:.3f}; x mean DK SE =
{m['normal_approx_mean_se']:.3f}.

**Runtime:** {summary['elapsed_s']:.0f} s for {sum(c['reps'] for c in summary['cells'])} simulated fits.

**Blinding.** Exactly one sealed fit (asserted). Every regression is on a simulated target; no output
relates a real target to FX.
"""
    out.with_suffix(".md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
