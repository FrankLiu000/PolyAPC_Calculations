#!/usr/bin/env python3
"""fig_pmf_compare.py — bare vs poly desolvation/approach PMF (the matched comparison).
  A: F(z) bare vs poly (kJ/mol), aligned to their bulk (large-z) reference
  B: first-shell coordination vs z (Mg-O THF, Mg-Cl) bare vs poly = the desolvation read-out
Reads umb_{bare_r2,poly_r2}_pmf.dat + umb_{bare_r2,poly_r2}/window_*.dat
Writes ../results/figures/fig_pmf_compare.png
"""
import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(label):
    pmf = np.loadtxt(f"umb_{label}_pmf.dat")
    fin = np.isfinite(pmf[:, 1]) & (pmf[:, 3] > 5)
    z, F = pmf[fin, 0], pmf[fin, 2]
    F = F - F[np.argmax(z)]                       # align to bulk (largest-z) reference = 0
    cn = []
    for w in glob.glob(f"umb_{label}/window_z*.dat"):
        d = np.loadtxt(w, comments="#"); m = d[:, 0] >= 2000
        cn.append((d[m, 1].mean(), d[m, 2].mean(), d[m, 3].mean()))   # <cv>, <MgO>, <MgCl>
    cn = np.array(sorted(cn))
    return z, F, cn

fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))
col = {"bare_r2": "#1f77b4", "poly_r2": "#ff7f0e"}; name = {"bare_r2": "bare", "poly_r2": "poly"}
for lab in ("bare_r2", "poly_r2"):
    try:
        z, F, cn = load(lab)
    except Exception as e:
        print(f"{lab}: {e}"); continue
    ax[0].plot(z, F, "-o", ms=3, color=col[lab], label=name[lab])
    ax[1].plot(cn[:, 0], cn[:, 1], "-o", ms=3, color=col[lab], label=f"{name[lab]} Mg–O")
    ax[1].plot(cn[:, 0], cn[:, 2], "--s", ms=3, color=col[lab], label=f"{name[lab]} Mg–Cl")
ax[0].set_xlabel("cation–electrode height z (Å)"); ax[0].set_ylabel("F(z) (kJ/mol, bulk=0)")
ax[0].set_title("A. Desolvation/approach PMF (round-2 MLFF)\nbare vs poly, ~3.5–9.5 Å"); ax[0].legend(); ax[0].invert_xaxis()
ax[1].set_xlabel("cation–electrode height z (Å)"); ax[1].set_ylabel("first-shell coordination")
ax[1].set_title("B. Desolvation: coordination vs approach"); ax[1].legend(fontsize=8); ax[1].invert_xaxis()
plt.tight_layout(); plt.savefig("../results/figures/fig_pmf_compare.png", dpi=130)
print("wrote ../results/figures/fig_pmf_compare.png")
