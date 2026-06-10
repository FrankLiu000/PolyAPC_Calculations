#!/usr/bin/env python3
"""Arrhenius fit of D(T) -> activation energy Ea, for bare vs swollen.

Reads per-(system,T,group) gmx msd -mol xvgs from analysis/arrhenius/, averages
cation+anion to D(T), fits ln D vs 1/T (least squares) -> Ea.
Relate Ea to the experimental DRT R_ct (bulk migration barrier vs interfacial).
"""
import os, math

R = 8.314462618          # J/mol/K
KB_eV = 8.617333262e-5   # eV/K
TEMPS = [273, 288, 298, 313, 333]
SYS = {"bare": "bare-APC", "swollen": "8-POSS swollen"}
DIR = "analysis/arrhenius"


def dmean(path):
    if not os.path.exists(path):
        return None
    v = [float(l.split()[1]) for l in open(path)
         if l[:1] not in "@#&\n" and l.strip() and len(l.split()) >= 2]
    return sum(v) / len(v) if v else None


def DT(sys, T):
    ds = [dmean(f"{DIR}/{sys}_T{T}_{g}.xvg") for g in ("MgCluster", "Anion")]
    ds = [d for d in ds if d]
    return sum(ds) / len(ds) if ds else None     # 1e-5 cm^2/s


def lsq(xs, ys):
    n = len(xs); sx = sum(xs); sy = sum(ys)
    sxx = sum(x * x for x in xs); sxy = sum(x * y for x, y in zip(xs, ys))
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    inter = (sy - slope * sx) / n
    # R^2
    ybar = sy / n; ss_tot = sum((y - ybar) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + inter)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
    return slope, inter, r2


L = ["=" * 64, "ARRHENIUS  D(T) -> Ea   (bare-APC vs 8-POSS swollen)",
     "D = avg(cation,anion) per T, 1e-5 cm^2/s; fit ln D vs 1/T", "=" * 64, ""]
for s, label in SYS.items():
    pts = [(T, DT(s, T)) for T in TEMPS]
    pts = [(T, d) for T, d in pts if d]
    L.append("  %s:" % label)
    for T, d in pts:
        L.append("     T=%d K  D=%.4f" % (T, d))
    if len(pts) >= 2:
        xs = [1.0 / T for T, _ in pts]
        ys = [math.log(d) for _, d in pts]
        slope, _, r2 = lsq(xs, ys)
        Ea_kJ = -slope * R / 1000.0
        Ea_eV = -slope * KB_eV
        L.append("     -> Ea = %.1f kJ/mol = %.3f eV   (R^2=%.3f, n=%d)" % (Ea_kJ, Ea_eV, r2, len(pts)))
    else:
        L.append("     (insufficient T points for a fit)")
    L.append("")
L.append("  NB: this is the BULK migration barrier; compare against (do not equate with)")
L.append("  the experimental DRT R_ct interfacial-desolvation barrier (solvation/desolvation).")
txt = "\n".join(L)
print(txt)
open("analysis/RESULTS_arrhenius.txt", "w").write(txt + "\n")
