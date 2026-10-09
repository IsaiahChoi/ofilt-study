#!/usr/bin/env python3
"""P4_M2_check.py: numerical check of the M2 closed forms (ofilt/drift study).

Synthetic data only. numpy only. No Project code, no data files.
Every parameter value below is ARBITRARY and chosen only to exercise the algebra.

Tolerances, fixed before the first run:
  TOL_ALG = 1e-9   closed form vs exact population projection (covariance algebra)
  TOL_MC  = 0.025  closed form vs Monte Carlo OLS, for every a2 and b
  TOL_P   = 0.05   closed form vs Monte Carlo, for the derived ratio p$ = b + a2/gamma
The verdict is True only if all three hold everywhere AND every sign that the
propositions declare determined is the sign of the closed form and of the
simulated value (a predicted 0 must satisfy |sim| <= TOL_MC), AND the Prop 5
ordering/attenuation predictions and the Prop 3 interval rule hold.
"""
import numpy as np

SEED, T, N = 20261008, 400_000, 3
TOL_ALG, TOL_MC, TOL_P = 1e-9, 0.025, 0.05
BURN = 1000  # rows dropped in the estimated-beta cell

BASE = dict(
    lam=1.0, Vs=0.4, Vn=0.6, VY=0.8, VE=0.5, lam_o=0.7, VCo=0.3,
    kappa=-1.0, Vmus=0.5, Vmun=0.5, kappaA=-0.8, VmuA=0.6, Cn=0.0,
    sigma=0.0, VG=0.7, VS=0.3,
    phiC=1.0, gC=0.8, VnuC=0.4, phiF=1.0, gF=1.0, VnuF=1.2,
    zD=0.0, zY=0.0, zE=0.0, VZ=0.5,
    dX=[0.6, 0.5, 0.55], rX=[0.5, 0.5, 0.5],
    dm=[0.8, 0.6, 0.7], rm=[0.5, 0.5, 0.5],
    dA=[0.3, 0.0, 0.1], rA=[0.5, 0.5, 0.5],
    nZ=[0.0, 0.0, 0.0], nR=[0.0, 0.0, 0.0],
    cXM=0.1, cEM=0.0, coM=0.0, cmM=0.0, cAM=0.0, nZM=0.0, nRM=0.0,
    beta=[0.9, 1.0, 1.1], beta_mode="known",
    Veta=0.2, VetaM=0.1, VepsM=0.3, beps=[1.0, 1.0, 1.0], Veps=0.3,
)

CELLS = [
    ("C01 cascade, all sign assumptions hold", {}),
    ("C02 metals fully priced", dict(rm=[1, 1, 1], rA=[1, 1, 1])),
    ("C03 metals overweighted", dict(rm=[1.5, 1.5, 1.5], rA=[1.4, 1.4, 1.4])),
    ("C04 cascade, kappa > 0", dict(kappa=0.8, kappaA=0.6)),
    ("C05 cascade, 1306 EUR/other-ccy underpriced (S4 fails)", dict(cEM=0.6, coM=0.3)),
    ("C06 no cascade, 1306 EUR overreacts (S4 fails)",
     dict(rm=[1, 1, 1], rA=[1, 1, 1], cEM=-0.4)),
    ("C07 no cascade, off-session risk (S5 fails)",
     dict(rm=[1, 1, 1], rA=[1, 1, 1], nZ=[0.5, 0.5, 0.5], nZM=0.2,
          zD=-0.4, zY=0.5, zE=0.1, nR=[0.3, 0.3, 0.3], nRM=0.1)),
    ("C08 cascade, SPY/COPX collider (S3 fails)",
     dict(sigma=-0.8, gC=1.5, VS=1.0, kappa=-0.05, Vn=0.05, dA=[0, 0, 0])),
    ("C09 cascade, gold/base co-movement (S6 fails)", dict(kappa=-0.5, Cn=0.45)),
    ("C10 strong cascade: b < 0 with cX > 0", dict(kappa=-3.0)),
    ("C11 translation fully priced, cascade", dict(rX=[1, 1, 1], cXM=0.0)),
    ("C12 estimated expanding beta, S4 fails", dict(cEM=0.3, beta_mode="estimated")),
    ("C13 near-perfect dollar proxy (V_E small)", dict(VE=0.01)),
    ("C14 FCX a cleaner metals view than COPX", dict(VnuF=0.05, gF=0.3)),
]

SHOCKS = ["Ds", "Dn", "Y", "E", "Co", "mus", "mun", "muAp", "G", "nuS", "nuC",
          "nuF", "Zp", "eta0", "eta1", "eta2", "etaM", "epsM", "eps0", "eps1", "eps2"]
FAT = {"Dn", "Y", "E", "Zp"}  # scaled Student-t(6) shocks; others Gaussian
IX = {s: k for k, s in enumerate(SHOCKS)}


def unpriced(p):
    f = lambda d, r: np.array(d, float) * (1 - np.array(r, float))
    return f(p["dX"], p["rX"]), f(p["dm"], p["rm"]), f(p["dA"], p["rA"])


# ---------------- closed forms (note, Lemmas 1-3) ----------------
def lemma2(p, ctl):
    """Unspanned dollar variance and partial covariances given (spy, ctl), ctl in {C, F}."""
    Vs, Vn, sig, VG, VS = p["Vs"], p["Vn"], p["sigma"], p["VG"], p["VS"]
    k, Vmus = p["kappa"], p["Vmus"]
    phi, g, Vnu = p["phi" + ctl], p["g" + ctl], p["Vnu" + ctl]
    S = sig**2 * Vs + VG + VS
    A = Vs * (VG + VS) / S
    B = g * sig * Vs * VS / S
    QS = VS * (sig**2 * Vs + VG) / S
    W = phi**2 * k**2 * A + 2 * phi * k * B + phi**2 * Vmus + Vnu + g**2 * QS
    X = phi * k * A + B
    U = sig * Vs * VS / S
    VDt = Vn + A - X**2 / W
    Ksig = Vn + (A * Vnu + A * g**2 * QS - B**2) / W
    chi = -g * sig * phi * Vs * VS * Vmus / (S * W)
    covDm = k * Ksig + chi
    covDR = U - X * (g * QS + phi * k * U) / W
    psi = phi**2 * (k**2 * A + Vmus) / W
    return dict(VDt=VDt, covDm=covDm, covDR=covDR, B=B, psi=psi, Ksig=Ksig, chi=chi)


def row_quantities(p, row):
    """Effective elasticities for design row in {P (primary), F (copx_to_fcx), X (xau_control)}."""
    L = lemma2(p, "F" if row == "F" else "C")
    VDt, kt_m, kt_R = L["VDt"], L["covDm"] / L["VDt"], L["covDR"] / L["VDt"]
    kt_A = p["kappaA"]
    ztD = p["zD"] * p["Vn"] / VDt  # invariant to adding XAU (Prop 5 proof)
    if row == "X":
        sA = p["VmuA"] / (p["kappaA"] ** 2 * VDt + p["VmuA"])
        VDt = VDt * sA
        kt_m = kt_m - p["kappaA"] * p["Cn"] / p["VmuA"]
        kt_A = None  # gold is a control: absorbed
    lam, VY, VE = p["lam"], p["VY"], p["VE"]
    Dl = lam**2 * VDt * VY + VDt * VE + VY * VE
    return dict(VDt=VDt, kt_m=kt_m, kt_R=kt_R, kt_A=kt_A, w=lam * VDt * VY / Dl,
                om=VY * (lam**2 * VDt + VE) / Dl, gam=-lam * VDt / (lam**2 * VDt + VE),
                ztD=ztD, B=L["B"], psi=L["psi"])


def loadings_fx(p, q, cX, cv, co, cm, cA, nZ, nR):
    """(theta_D~, theta_Y, theta_E) of a drift with the given unpriced channel loadings."""
    lam = p["lam"]
    tD = cX - lam * cv - p["lam_o"] * co + cm * q["kt_m"] + nZ * q["ztD"] + nR * q["kt_R"]
    if q["kt_A"] is not None:
        tD += cA * q["kt_A"]
    return tD, cX + nZ * p["zY"], cv + nZ * p["zE"]


def lemma1(p, q, th):
    tD, tY, tE = th
    Gam = tY - tD - p["lam"] * tE
    a2 = tE + q["w"] * Gam
    b = tY - (1 - q["om"]) * Gam
    return dict(a2=a2, b=b, pd=b + a2 / q["gam"], Gam=Gam, tY=tY, tE=tE)


def closed_form(p, beta_bar):
    cX, cm, cA = unpriced(p)
    out = {}
    for row in "PFX":
        q = row_quantities(p, row)
        raw = [lemma1(p, q, loadings_fx(p, q, cX[i], 0, 0, cm[i], cA[i],
                                        p["nZ"][i], p["nR"][i])) for i in range(N)]
        M = lemma1(p, q, loadings_fx(p, q, p["cXM"], p["cEM"], p["coM"], p["cmM"],
                                     p["cAM"], p["nZM"], p["nRM"]))
        r = {k: np.mean([d[k] for d in raw]) for k in raw[0]}
        a = {k: r[k] - beta_bar * M[k] for k in r}
        out[row] = dict(q=q, raw=r, M=M, abn=a)
    return out


# ---------------- loadings on unit shocks (exact moments and simulation) ----------------
def build(p, beta):
    cX, cm, cA = unpriced(p)
    e = lambda s, sd=1.0: sd * np.eye(len(SHOCKS))[IX[s]]
    r = np.sqrt
    Ds, Dn = e("Ds", r(p["Vs"])), e("Dn", r(p["Vn"]))
    D, Y, E = Ds + Dn, e("Y", r(p["VY"])), e("E", r(p["VE"]))
    u, v = D + Y, -p["lam"] * D + E
    xo = -p["lam_o"] * D + e("Co", r(p["VCo"]))
    mus, mun = e("mus", r(p["Vmus"])), e("mun", r(p["Vmun"]))
    muA = (p["Cn"] / r(p["Vmun"])) * e("mun") + e("muAp", r(p["VmuA"] - p["Cn"] ** 2 / p["Vmun"]))
    m, ms, a = p["kappa"] * D + mus + mun, p["kappa"] * Ds + mus, p["kappaA"] * D + muA
    Rs = p["sigma"] * Ds + e("G", r(p["VG"]))
    spy = Rs + e("nuS", r(p["VS"]))
    copx = p["phiC"] * ms + p["gC"] * Rs + e("nuC", r(p["VnuC"]))
    fcx = p["phiF"] * ms + p["gF"] * Rs + e("nuF", r(p["VnuF"]))
    Z = p["zD"] * Dn + p["zY"] * Y + p["zE"] * E + e("Zp", r(p["VZ"]))
    dM = (p["cXM"] * u + p["cEM"] * v + p["coM"] * xo + p["cmM"] * m + p["cAM"] * a
          + p["nZM"] * Z + p["nRM"] * Rs)
    h = dM - e("etaM", r(p["VetaM"])) + e("epsM", r(p["VepsM"]))
    ys = []
    for i in range(N):
        di = cX[i] * u + cm[i] * m + cA[i] * a + p["nZ"][i] * Z + p["nR"][i] * Rs
        ys.append(di - e("eta%d" % i, r(p["Veta"])) + p["beps"][i] * e("epsM", r(p["VepsM"]))
                  + e("eps%d" % i, r(p["Veps"])))
    if beta is None:  # population beta*: plim of the expanding beta
        beta = [float(y @ h / (h @ h)) for y in ys]
    return dict(u=u, v=v, spy=spy, copx=copx, fcx=fcx, xau=a, h=h, y=ys), beta


def exact(Lv, beta):
    out = {}
    for row, ctl in (("P", ["copx"]), ("F", ["fcx"]), ("X", ["copx", "xau"])):
        R = np.array([Lv["u"], Lv["v"], Lv["spy"]] + [Lv[c] for c in ctl])
        Sxx = R @ R.T
        co = lambda z: np.linalg.solve(Sxx, R @ z)[:2]
        raw = np.mean([co(Lv["y"][i]) for i in range(N)], axis=0)
        abn = np.mean([co(Lv["y"][i] - beta[i] * Lv["h"]) for i in range(N)], axis=0)
        out[row] = dict(raw=raw, abn=abn, M=co(Lv["h"]))
    return out


# ---------------- Monte Carlo ----------------
def draw(rng):
    Z = rng.standard_normal((len(SHOCKS), T))
    for s in SHOCKS:  # fixed order: set iteration order is not reproducible
        if s in FAT:
            Z[IX[s]] = rng.standard_t(6, T) / np.sqrt(1.5)
    return Z


def ols(X, y, cluster_T=None):
    XtX = X.T @ X
    coef = np.linalg.solve(XtX, X.T @ y)
    if cluster_T is None:
        return coef, None
    e = y - X @ coef
    s = (X * e[:, None]).reshape(-1, cluster_T, X.shape[1]).sum(axis=0)
    Bi = np.linalg.inv(XtX)
    return coef, np.sqrt(np.diag(Bi @ (s.T @ s) @ Bi))


def expanding_beta(y, h):
    n = np.arange(1, len(y) + 1, dtype=float)
    Sh, Sy, Shh, Shy = np.cumsum(h), np.cumsum(y), np.cumsum(h * h), np.cumsum(h * y)
    with np.errstate(invalid="ignore", divide="ignore"):
        bt = (Shy - Sh * Sy / n) / (Shh - Sh**2 / n)
    out = np.full(len(y), np.nan)
    out[1:] = bt[:-1]  # beta_{t-1}: past-only, lagged one day
    return out


def simulate(p, beta, rng):
    Lv, _ = build(p, beta)
    Zs = draw(rng)
    V = {k: Lv[k] @ Zs for k in ("u", "v", "spy", "copx", "fcx", "xau", "h")}
    ys = [Lv["y"][i] @ Zs for i in range(N)]
    keep = np.arange(T)
    if p["beta_mode"] == "estimated":
        bts = [expanding_beta(ys[i], V["h"]) for i in range(N)]
        keep = np.arange(BURN, T)
        yabn = [ys[i][keep] - bts[i][keep] * V["h"][keep] for i in range(N)]
        mean_bhat = float(np.mean([np.mean(b[keep]) for b in bts]))
    else:
        yabn = [ys[i][keep] - beta[i] * V["h"][keep] for i in range(N)]
        mean_bhat = None
    Tk = len(keep)
    S = {k: V[k][keep] for k in V}
    yraw = np.concatenate([ys[i][keep] for i in range(N)])
    yab = np.concatenate(yabn)
    out = {}
    for row, ctl in (("P", ["copx"]), ("F", ["fcx"]), ("X", ["copx", "xau"])):
        cols = [S["u"], S["v"], S["spy"]] + [S[c] for c in ctl]
        X = np.zeros((N * Tk, N + 2 + N * (1 + len(ctl))))
        for i in range(N):
            sl = slice(i * Tk, (i + 1) * Tk)
            X[sl, i] = 1.0
            X[sl, N], X[sl, N + 1] = S["u"], S["v"]
            for j, c in enumerate(cols[2:]):
                X[sl, N + 2 + j * N + i] = c
        cr, ser = ols(X, yraw, Tk)
        ca, sea = ols(X, yab, Tk)
        Xh = np.column_stack([np.ones(Tk)] + cols)
        cM, seM = ols(Xh, S["h"], Tk)
        Xg = np.column_stack([np.ones(Tk), S["v"], S["spy"]] + [S[c] for c in ctl])
        gam = ols(Xg, S["u"])[0][1]
        out[row] = dict(raw=(cr[N + 1], cr[N], ser[N + 1], ser[N]),
                        abn=(ca[N + 1], ca[N], sea[N + 1], sea[N]),
                        M=(cM[2], cM[1], seM[2], seM[1]), gam=gam)
        del X
    return out, mean_bhat


# ---------------- predictions from the propositions ----------------
def wsign(c):
    c = np.asarray(c, float)
    if np.all(c == 0):
        return 0
    if np.all(c >= 0):
        return 1
    if np.all(c <= 0):
        return -1
    return None


def predict(p, row, target, beta_bar):
    """Sign of a2 implied by Props 1-2 and 5, or '?' when an assumption fails."""
    k, kA = p["kappa"], p["kappaA"]
    sk = -1 if (k < 0 and kA < 0) else (1 if (k > 0 and kA > 0) else None)
    _, cm, cA = unpriced(p)
    S2 = all(d > 0 for d in p["dm"]) and all(d >= 0 for d in p["dA"])
    S3 = lemma2(p, "F" if row == "F" else "C")["B"] == 0
    S4 = target == "raw" or all(p[x] == 0 for x in ("cEM", "coM", "cmM", "cAM"))
    nz = np.array(p["nZ"]) - (beta_bar * p["nZM"] if target == "abn" else 0)
    nr = np.array(p["nR"]) - (beta_bar * p["nRM"] if target == "abn" else 0)
    S5 = np.all(nz == 0) and np.all(nr == 0)
    S6 = row != "X" or p["Cn"] == 0
    h = wsign(cm) if row == "X" else wsign(np.concatenate([cm, cA]))
    if None in (sk, h) or not (S2 and S3 and S4 and S5 and S6):
        return "?"
    s = -sk * h
    return {1: "+", 0: "0", -1: "-"}[s]


def main():
    rng = np.random.default_rng(SEED)
    lines, ok_all, maxerr, maxz, maxalg = [], True, 0.0, 0.0, 0.0
    hdr = "%-4s %-10s %10s %10s %10s %8s %7s %5s %3s" % (
        "cell", "quantity", "closed", "exact", "sim", "|c-s|", "SE", "pred", "ok")
    checks = []
    for name, ov in CELLS:
        p = dict(BASE, **ov)
        beta = None if p["beta_mode"] == "estimated" else list(p["beta"])
        Lv, beta = build(p, beta)
        bbar = float(np.mean(beta))
        cf, ex = closed_form(p, bbar), exact(Lv, beta)
        sim, mean_bhat = simulate(p, beta, rng)
        lines.append("")
        lines.append(name + ("   [beta* mean %.4f, mean beta_hat %.4f]" % (bbar, mean_bhat)
                             if mean_bhat is not None else ""))
        lines.append(hdr)
        tag = name.split()[0]
        for row, rname in (("P", "prim"), ("F", "fcx"), ("X", "xau")):
            for tgt in ("abn", "raw", "M"):
                c = cf[row][tgt]
                exb, exa2 = ex[row][tgt]  # exact() returns (b, a2) in regressor order
                sa2, sb, sea2, seb = sim[row][tgt]
                items = [("a2", c["a2"], exa2, sa2, sea2, TOL_MC),
                         ("b", c["b"], exb, sb, seb, TOL_MC)]
                if tgt != "M" and row == "P":
                    items.append(("p$", c["pd"], exb + exa2 / cf[row]["q"]["gam"],
                                  sb + sa2 / sim[row]["gam"], np.nan, TOL_P))
                for qn, cv, xv, sv, se, tol in items:
                    if row != "P" and (qn == "b" or tgt == "M"):
                        continue  # metals rows: report a2 for abn and raw only
                    pr = predict(p, row, tgt, bbar) if (qn == "a2" and tgt != "M") else ""
                    err, alg = abs(cv - sv), abs(cv - xv)
                    ok = err <= tol and alg <= TOL_ALG
                    if pr in ("+", "-"):
                        sgn = 1 if pr == "+" else -1
                        ok = ok and np.sign(cv) == sgn and np.sign(sv) == sgn
                    elif pr == "0":
                        ok = ok and abs(cv) <= TOL_ALG and abs(sv) <= TOL_MC
                    ok_all &= bool(ok)
                    maxerr = max(maxerr, err) if qn != "p$" else maxerr
                    maxalg = max(maxalg, alg)
                    if np.isfinite(se) and se > 0:
                        maxz = max(maxz, err / se)
                    lines.append("%-4s %-10s %10.5f %10.5f %10.5f %8.5f %7s %5s %3s" % (
                        tag, "%s_%s_%s" % (qn, tgt, rname), cv, xv, sv, err,
                        ("%.4f" % se) if np.isfinite(se) else "-", pr, "Y" if ok else "N"))
        # Prop 5 checks (only where the propositions make a prediction)
        for tgt in ("abn", "raw"):
            pP, pF, pX = (predict(p, r, tgt, bbar) for r in "PFX")
            aP, aF, aX = (cf[r][tgt]["a2"] for r in "PFX")
            sP, sF, sX = (sim[r][tgt][0] for r in "PFX")
            if pP in "+-" and pF == pP:
                qC, qF = cf["P"]["q"]["psi"], cf["F"]["q"]["psi"]
                rel = ">" if qF < qC else "<"
                f = (lambda x, y: abs(x) > abs(y)) if rel == ">" else (lambda x, y: abs(x) < abs(y))
                ok = f(aF, aP) and f(sF, sP)
                checks.append((tag, "Prop5 fcx %s: |a2_fcx| %s |a2_prim| (psi_F %.3f, psi_C %.3f)"
                               % (tgt, rel, qF, qC), ok))
            if pP in "+-" and pX == pP:
                ok = 0 <= aX / aP < 1 and 0 <= sX / sP < 1
                checks.append((tag, "Prop5 xau %s: 0 <= a2_xau/a2_prim < 1 (closed %.3f, sim %.3f)"
                               % (tgt, aX / aP, sX / sP), ok))
            # Prop 3 interval rule, in Gamma: b*p$ < 0 iff Gamma strictly between the roots
            c = cf["P"][tgt]
            om, gm = cf["P"]["q"]["om"], cf["P"]["q"]["gam"]
            rb, rp = c["tY"] / (1 - om), c["tY"] + c["tE"] / gm
            inside = min(rb, rp) < c["Gam"] < max(rb, rp)
            sb, sa2 = sim["P"][tgt][1], sim["P"][tgt][0]
            spd = sb + sa2 / sim["P"]["gam"]
            ok = inside == (c["b"] * c["pd"] < 0)
            if min(abs(c["b"]), abs(c["pd"])) > 3 * TOL_P:
                ok = ok and (inside == (sb * spd < 0))
            checks.append((tag, "Prop3 %s: opposite signs of b and p$ predicted %s" % (tgt, inside), ok))
    print("M2 numerical check  seed=%d  T=%d  N=%d  TOL_ALG=%g  TOL_MC=%g  TOL_P=%g"
          % (SEED, T, N, TOL_ALG, TOL_MC, TOL_P))
    print("Rows: q_target_row. targets abn (primary target), raw (raw_target), M (1306 own);")
    print("rows prim (primary design), fcx (copx_to_fcx), xau (xau_control).")
    print("pred: sign implied by Props 1, 2 and 5 ('?' = not determined: an assumption fails).")
    for ln in lines:
        print(ln)
    print("")
    print("Proposition checks")
    for tag, txt, ok in checks:
        ok_all &= bool(ok)
        print("%-4s %-78s %s" % (tag, txt, "Y" if ok else "N"))
    print("")
    print("max |closed - exact| = %.3e" % maxalg)
    print("max |closed - sim| (a2, b) = %.5f   max |closed - sim|/SE = %.2f" % (maxerr, maxz))
    print("M2 CHECK: %s" % bool(ok_all))


if __name__ == "__main__":
    main()
