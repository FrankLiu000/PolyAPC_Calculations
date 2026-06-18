#!/usr/bin/env python3
"""fig_abstraction_maps.py — 2D heatmaps of the chloride-abstraction gateway from
the matched interface AIMD trajectories (DESCRIPTIVE sampling density, NOT free energy).

Fig 1 (fig_abstraction_density.png): 2D log-density in the plane
    x = d(Al - Cl149)        (anion integrity coordinate)
    y = d(Cl149 - nearest cation Mg)   (abstraction coordinate)
  bare vs poly side by side.
Fig 2 (fig_bond_barcode.png): Al-ligand bond distances vs time (Cl x2, ipso C x2),
  bare vs poly stacked — the 0.17 ps abstraction and poly's recovering excursions.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/CH/poly_v2/bin")
from analyze_interface_access import frames

INP = "/CH/poly_v2/P0d_interface/inp/"
FIG = "/CH/poly_v2/results/figures/"
AL, CL1, CL2, C1, C2 = 147, 148, 149, 150, 161
CATMG = [64, 65]

data = {}
for tag, fn in [("bare", "aimd_bare-pos-1.xyz"), ("poly", "aimd_poly-pos-1.xyz")]:
    rec = []
    for syms, x in frames(INP + fn):
        al, cl = x[AL], x[CL2]
        rec.append([np.linalg.norm(al - cl),
                    min(np.linalg.norm(cl - x[m]) for m in CATMG),
                    np.linalg.norm(x[CL1] - al),
                    np.linalg.norm(x[C1] - al),
                    np.linalg.norm(x[C2] - al)])
    data[tag] = np.array(rec)
    print(tag, data[tag].shape)

# ---------- Fig 1: sampling-density map ----------
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6), sharex=True, sharey=True)
xe = np.linspace(1.8, 10.0, 165)
ye = np.linspace(2.0, 4.5, 101)
for ax, tag in zip(axes, ["bare", "poly"]):
    d = data[tag]
    H, _, _ = np.histogram2d(d[:, 0], d[:, 1], bins=[xe, ye])
    Hm = np.ma.masked_where(H == 0, H)
    pc = ax.pcolormesh(xe, ye, np.log10(Hm).T, cmap="viridis", shading="auto")
    ax.set_title("%s  (10 ps, unbiased AIMD)" % tag)
    ax.set_xlabel(r"d(Al $-$ Cl$_{149}$)  /  $\AA$")
    cb = fig.colorbar(pc, ax=ax, pad=0.02)
    cb.set_label(r"log$_{10}$ frame count")
axes[0].set_ylabel(r"d(Cl$_{149}$ $-$ nearest cation Mg)  /  $\AA$")
axes[0].annotate("intact anion", xy=(2.4, 3.1), ha="left", fontsize=9)
axes[0].annotate("abstracted: neutral AlPh$_2$Cl\n(Cl rides the cation, d$\\approx$2.4 $\\AA$)", xy=(6.4, 3.4), ha="center", fontsize=9)
fig.suptitle("Chloride-abstraction gateway — sampling density (NOT a free-energy surface)", y=1.00)
fig.tight_layout()
fig.savefig(FIG + "fig_abstraction_density.png", dpi=300, bbox_inches="tight")
print("wrote fig_abstraction_density.png")

# ---------- Fig 2: bond barcode ----------
fig, axes = plt.subplots(2, 1, figsize=(9.5, 5.6), sharex=True, sharey=True)
labels = [r"Al$-$Cl$_{148}$", r"Al$-$Cl$_{149}$ ($\mu$-Cl)", r"Al$-$C$_{ipso,1}$", r"Al$-$C$_{ipso,2}$"]
cols = ["#1f77b4", "#d62728", "#7f7f7f", "#bcbd22"]
for ax, tag in zip(axes, ["bare", "poly"]):
    d = data[tag]
    t = np.arange(len(d)) / 1000.0
    for k, (lab, c) in enumerate(zip(labels, cols)):
        ax.plot(t, d[:, [2, 0, 3, 4][k]], lw=0.6, color=c, label=lab)
    ax.axhline(3.0, color="k", ls=":", lw=0.8)
    ax.set_ylabel(r"r  /  $\AA$")
    ax.text(0.99, 0.92, tag, transform=ax.transAxes, ha="right", fontweight="bold")
axes[0].legend(ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, 1.25), frameon=False)
axes[0].annotate("abstraction at 0.17 ps", xy=(0.4, 4.5), xytext=(1.8, 6.5),
                 arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=9)
axes[1].set_xlabel("t  /  ps")
axes[1].set_ylim(1.5, 10)
fig.tight_layout()
fig.savefig(FIG + "fig_bond_barcode.png", dpi=300, bbox_inches="tight")
print("wrote fig_bond_barcode.png")
