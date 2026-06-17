#!/usr/bin/env python3
"""fig_pmf_compare.py — bare vs poly desolvation/approach PMF (the matched comparison).
  A: F(z) bare vs poly (kJ/mol) +/- bootstrap error, aligned to bulk (large-z) reference
  B: first-shell coordination vs z (Mg-O THF, Mg-Cl) bare vs poly = the desolvation read-out
Usage: python fig_pmf_compare.py [suffix=r2] [out.png]   (reads umb_{bare,poly}_<suffix>_*)
"""
import sys, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SUF = sys.argv[1] if len(sys.argv) > 1 else "r2"
OUT = sys.argv[2] if len(sys.argv) > 2 else "../results/figures/fig_pmf_compare.png"

def load(label):
    pmf = np.loadtxt(f"umb_{label}_pmf.dat")
    fin = np.isfinite(pmf[:, 1]) & (pmf[:, 3] > 5)
    z, F = pmf[fin, 0], pmf[fin, 2]
    ref = F[np.argmax(z)]; F = F - ref                       # align to bulk (largest-z) = 0
    err = pmf[fin, 4] if pmf.shape[1] > 4 else np.zeros_like(z)   # bootstrap err, already kJ/mol
    cn = []
    for w in glob.glob(f"umb_{label}/window_z*.dat"):
        d = np.loadtxt(w, comments="#"); m = d[:, 0] >= 4000
        if m.sum(): cn.append((d[m, 1].mean(), d[m, 2].mean(), d[m, 3].mean()))
    return z, F, np.array(sorted(cn)), err

fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))
col = {"bare": "#1f77b4", "poly": "#ff7f0e"}
for nm in ("bare", "poly"):
    lab = f"{nm}_{SUF}"
    try:
        z, F, cn, err = load(lab)
    except Exception as e:
        print(f"{lab}: {e}"); continue
    ax[0].plot(z, F, "-o", ms=3, color=col[nm], label=nm)
    if np.any(err > 0):
        ax[0].fill_between(z, F - err, F + err, color=col[nm], alpha=0.25)
    if len(cn):
        ax[1].plot(cn[:, 0], cn[:, 1], "-o", ms=3, color=col[nm], label=f"{nm} Mg–O")
        ax[1].plot(cn[:, 0], cn[:, 2], "--s", ms=3, color=col[nm], label=f"{nm} Mg–Cl")
ax[0].set_xlabel("cation–electrode height z (Å)"); ax[0].set_ylabel("F(z) (kJ/mol, bulk=0)")
ax[0].set_title(f"A. Desolvation/approach PMF ({SUF})\nbare vs poly ± bootstrap"); ax[0].legend(); ax[0].invert_xaxis()
ax[1].set_xlabel("cation–electrode height z (Å)"); ax[1].set_ylabel("first-shell coordination")
ax[1].set_title("B. Desolvation: coordination vs approach"); ax[1].legend(fontsize=8); ax[1].invert_xaxis()
plt.tight_layout(); plt.savefig(OUT, dpi=130)
print("wrote", OUT)
