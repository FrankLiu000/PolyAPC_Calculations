#!/usr/bin/env python3
"""fig_pmf.py — desolvation umbrella-sampling figure.
  A: F(z) PMF (kJ/mol)                         (<label>_pmf.dat)
  B: per-window CV histograms (overlap check)  (umb_<label>/window_*.dat)
  C: coordination vs z (desolvation profile)   (Mg-O, Mg-Cl per-window means)
Usage: python fig_pmf.py <label> [out.png]
"""
import sys, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

label = sys.argv[1] if len(sys.argv) > 1 else "bare"
out = sys.argv[2] if len(sys.argv) > 2 else f"../results/figures/fig_pmf_{label}.png"
pmf = np.loadtxt(f"umb_{label}_pmf.dat")
wins = sorted(glob.glob(f"umb_{label}/window_z*.dat"), key=lambda f: float(f.split("_z")[-1][:-4]))

fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
fin = np.isfinite(pmf[:, 1]) & (pmf[:, 3] > 0)
ax[0].plot(pmf[fin, 0], pmf[fin, 2], "-o", ms=3, color="#1f77b4")
ax[0].set_xlabel("cation–electrode height z (Å)"); ax[0].set_ylabel("F(z) (kJ/mol)")
ax[0].set_title(f"A. Desolvation/approach PMF — {label}\n(in-distribution pilot; near-surface needs active learning)")
ax[0].invert_xaxis()

z0s, mgO, mgCl = [], [], []
for w in wins:
    z0 = float(w.split("_z")[-1][:-4]); d = np.loadtxt(w, comments="#")
    m = d[:, 0] >= 2000
    ax[1].hist(d[m, 1], bins=30, alpha=0.5, label=f"{z0:.1f}")
    z0s.append(d[m, 1].mean()); mgO.append(d[m, 2].mean()); mgCl.append(d[m, 3].mean())
ax[1].set_xlabel("CV z (Å)"); ax[1].set_ylabel("count")
ax[1].set_title("B. Window overlap"); ax[1].legend(fontsize=7, title="z0")

o = np.argsort(z0s); z0s = np.array(z0s)[o]; mgO = np.array(mgO)[o]; mgCl = np.array(mgCl)[o]
ax[2].plot(z0s, mgO, "-o", label="Mg–O (THF shell)", color="#2ca02c")
ax[2].plot(z0s, mgCl, "-s", label="Mg–Cl", color="#d62728")
ax[2].set_xlabel("cation–electrode height z (Å)"); ax[2].set_ylabel("first-shell coordination")
ax[2].set_title("C. Coordination vs approach (desolvation)"); ax[2].legend(fontsize=9); ax[2].invert_xaxis()
plt.tight_layout(); plt.savefig(out, dpi=130)
print("wrote", out)
