#!/usr/bin/env python3
"""Walden-plot analysis: bare-APC vs 8-POSS swollen.

Combines shear viscosity eta (gmx energy: -evisco Einstein + -vis Green-Kubo, output
in cP) with collective conductivity sigma (gmx current, S/m) to place each electrolyte
on a Walden plot (log molar conductivity vs log fluidity) and read off the Walden
ionicity -- a viscosity-based cross-check of the sigma_coll/sigma_NE ionicity (A.2).
"""
import os, re

NA = 6.02214076e23
N_SALT = 80                       # 80 cation + 80 anion formula units / single cell
# 0.01 M aqueous KCl reference for the Walden ideal line (slope 1):
KCL_LAMBDA = 141.3                # S cm^2 / mol
KCL_ETA_cP = 0.8903              # cP
KCL_PHI = 1.0 / (KCL_ETA_cP / 100.0)        # Poise^-1  (=112.3)
IDEAL_K = KCL_LAMBDA / KCL_PHI               # Lambda_ideal[S cm^2/mol] = IDEAL_K * phi[P^-1]


def eta_cP(path, col=1):
    """Plateau (last 20%) of a gmx viscosity running xvg, in cP."""
    if not os.path.exists(path):
        return None
    ys = []
    for l in open(path):
        if l[:1] in "@#&\n" or len(l.split()) <= col:
            continue
        try: ys.append(float(l.split()[col]))
        except ValueError: pass
    if not ys:
        return None
    tail = ys[int(0.8 * len(ys)):]
    return sum(tail) / len(tail)


def sigma_from_log(path):
    if not os.path.exists(path):
        return None
    m = re.search(r"sigma\s*=\s*([0-9.eE+-]+)", open(path).read())
    return float(m.group(1)) if m else None


def box_V(gro):                   # m^3 from last-line box (nm)
    last = [l for l in open(gro) if l.strip()][-1]
    a, b, c = (float(x) for x in last.split()[:3])
    return a * b * c * 1e-27


def analyze(tag):
    eg = eta_cP(f"visco_{tag}.xvg", col=1)             # GK: col1 = Shear, already cP
    ee_pas = eta_cP(f"evisco_{tag}.xvg", col=4)        # Einstein: col4 = avg shear, in Pa s
    ee = ee_pas * 1000.0 if ee_pas is not None else None   # Pa s -> cP
    etas = [x for x in (eg, ee) if x]
    eta = sum(etas) / len(etas) if etas else None      # cP
    sig = sigma_from_log(f"cur_{tag}.log")    # S/m
    gro = f"visc_{tag}.gro"
    if None in (eta, sig) or not os.path.exists(gro):
        return dict(tag=tag, eg=eg, ee=ee, sig=sig, eta=eta, Lam=None, phi=None, ion=None)
    c = N_SALT / (box_V(gro) * NA)            # mol/m^3
    Lam = sig / c * 1e4                        # S cm^2 / mol
    phi = 1.0 / (eta / 100.0)                  # Poise^-1
    ion = Lam / (IDEAL_K * phi)                # Walden ionicity vs KCl
    return dict(tag=tag, eg=eg, ee=ee, sig=sig, eta=eta, Lam=Lam, phi=phi, ion=ion)


L = ["=" * 70,
     "WALDEN ANALYSIS -- bare-APC vs 8-POSS swollen (single cell, NVT 298 K)",
     "eta in cP (GK -vis & Einstein -evisco); sigma_coll via gmx current; Lambda=sigma/c",
     "=" * 70, ""]
r = {t: analyze(t) for t in ("bare", "swollen")}
for t in ("bare", "swollen"):
    d = r[t]
    L.append("  %s:" % ("bare-APC" if t == "bare" else "8-POSS swollen"))
    L.append("     eta  GK=%s  Einstein=%s cP" %
             ("%.3f" % d["eg"] if d["eg"] else "NA", "%.3f" % d["ee"] if d["ee"] else "NA"))
    if d["Lam"] is not None:
        L.append("     sigma_coll=%.4f S/m  Lambda=%.3f S cm^2/mol  fluidity=%.2f P^-1" %
                 (d["sig"], d["Lam"], d["phi"]))
        L.append("     Walden ionicity (vs KCl line) = %.3f" % d["ion"])
    L.append("")
if r["bare"]["Lam"] and r["swollen"]["Lam"]:
    L.append("  -- bare -> swollen --")
    L.append("     eta:        %.3f -> %.3f cP  (x%.2f)" %
             (r["bare"]["eta"], r["swollen"]["eta"], r["swollen"]["eta"] / r["bare"]["eta"]))
    L.append("     Lambda:     %.3f -> %.3f S cm^2/mol" % (r["bare"]["Lam"], r["swollen"]["Lam"]))
    L.append("     Walden ion: %.3f -> %.3f" % (r["bare"]["ion"], r["swollen"]["ion"]))
    L.append("")
    L.append("  Cross-check these Walden ionicities against sigma_coll/sigma_NE (RESULTS_storyA2.txt).")
txt = "\n".join(L)
print(txt)
open("RESULTS_walden.txt", "w").write(txt + "\n")
