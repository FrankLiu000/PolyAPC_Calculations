#!/usr/bin/env python3
"""fig_mlff.py — figures for the MLFF train report.
  panel A: force parity (DFT vs MLFF) on the held-out test set  (parity_forces.npz)
  panel B: per-element force RMSE bar                            (eval_test.json)
  panel C: MLFF-MD CV timeseries (T, Al-slab dist, anion bonds)  (md_bare_cv.csv)
Writes <out> (default ../results/figures/fig_mlff_train.png).
"""
import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = sys.argv[1] if len(sys.argv) > 1 else "../results/figures/fig_mlff_train.png"
npz = np.load("parity_forces.npz", allow_pickle=True)
ev = json.load(open("eval_test.json"))
fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))

# A: force parity
fd = npz["f_dft"].ravel(); fm = npz["f_ml"].ravel()
ax[0].plot([fd.min(), fd.max()], [fd.min(), fd.max()], "k--", lw=1, zorder=1)
ax[0].scatter(fd, fm, s=2, alpha=0.25, color="#1f77b4", zorder=2)
ax[0].set_xlabel("DFT force component (eV/Å)"); ax[0].set_ylabel("MLFF force (eV/Å)")
ax[0].set_title(f"A. Force parity (held-out test)\nRMSE {ev['force_rmse_meV_per_A']:.1f} meV/Å, "
                f"R={ev['force_R']:.4f}")

# B: per-element force RMSE
pe = ev["force_rmse_per_element"]
els = list(pe.keys()); vals = [pe[e] for e in els]
ax[1].bar(els, vals, color="#ff7f0e")
ax[1].axhline(100, ls=":", color="g", label="100 meV/Å target")
ax[1].axhline(ev["force_rmse_meV_per_A"], ls="--", color="k",
              label=f"overall {ev['force_rmse_meV_per_A']:.0f}")
ax[1].set_ylabel("force RMSE (meV/Å)"); ax[1].set_title("B. Per-element force RMSE"); ax[1].legend(fontsize=8)

# C: MD CVs
try:
    import csv
    rows = list(csv.DictReader(open("md_bare_cv.csv")))
    t = np.array([float(r["t_ps"]) for r in rows])
    T = np.array([float(r["T_K"]) for r in rows])
    al = np.array([float(r["Al_slab_min_A"]) for r in rows])
    c1 = np.array([float(r["Al_Cl1_A"]) for r in rows])
    c2 = np.array([float(r["Al_Cl2_A"]) for r in rows])
    axc = ax[2]; axc.plot(t, al, color="#2ca02c", label="min Al–slab Mg")
    axc.plot(t, c1, color="#d62728", lw=1, label="Al–Cl(1)")
    axc.plot(t, c2, color="#9467bd", lw=1, label="Al–Cl(2)")
    axc.axhline(3.0, ls=":", color="gray", lw=0.8)
    axc.set_xlabel("t (ps)"); axc.set_ylabel("distance (Å)")
    axc.set_title(f"C. MLFF-MD ({t.max():.0f} ps, NVT 300 K)\n⟨T⟩={T.mean():.0f} K")
    axc.legend(fontsize=8, loc="center right")
except FileNotFoundError:
    ax[2].text(0.5, 0.5, "md_bare_cv.csv not found\n(run run_md.py)", ha="center", va="center")
    ax[2].set_title("C. MLFF-MD CVs")

plt.tight_layout()
plt.savefig(out, dpi=130)
print("wrote", out)
