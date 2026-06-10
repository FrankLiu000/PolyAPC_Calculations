#!/usr/bin/env python3
"""fig_spin_maps.py — 2D projected spin-density heatmaps: where the incoming electron goes.

Panels: (a) intact [AlPh2Cl2]- + e- (vertical)  -> phenyl pi*
        (b) neutral AlPh2Cl + e- (vertical)     -> Al (52%)
        (c) [AlPh2Cl]·- relaxed (adiabatic)     -> Al (83%)
Projection: integrate spin density along the molecular axis of smallest extent.
Exact wavefunction property (UB3LYP/def2-TZVP, SMD-THF) — no sampling caveat.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm

RM = "/CH/poly_v2/run_mol/"
FIG = "/CH/poly_v2/results/figures/"
B2A = 0.529177

def read_cube(path):
    with open(path) as fh:
        fh.readline(); fh.readline()
        nat, *org = fh.readline().split()
        nat = int(nat); org = np.array(org[:3], float)
        ax = []
        npts = []
        for _ in range(3):
            p = fh.readline().split()
            npts.append(int(p[0])); ax.append(np.array(p[1:4], float))
        Z, pos = [], []
        for _ in range(abs(nat)):
            p = fh.readline().split()
            Z.append(int(p[0])); pos.append([float(p[2]), float(p[3]), float(p[4])])
        data = np.fromstring(fh.read(), sep=" ")
    return np.array(Z), np.array(pos), org, np.array(ax), np.array(npts), data.reshape(npts)

SYM = {1: "H", 6: "C", 13: "Al", 17: "Cl"}
panels = [
    ("spin_AlPh2Cl2m_red_vert.cub", "(a) intact [AlPh$_2$Cl$_2$]$^-$ + e$^-$ (vertical)\nelectron $\\to$ phenyl $\\pi^*$  (8% Al)"),
    ("spin_AlPh2Cl_n_redvert.cub", "(b) neutral AlPh$_2$Cl + e$^-$ (vertical)\nelectron $\\to$ Al  (52%)"),
    ("spin_frag_AlPh2Cl_tzvp.cub", "(c) [AlPh$_2$Cl]$^{\\bullet-}$ relaxed (adiabatic)\nAl-centred radical  (83%)"),
]
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6))
for ax_, (cub, title) in zip(axes, panels):
    Z, pos, org, axv, npts, rho = read_cube(RM + cub)
    # axis with smallest atomic extent -> projection axis
    ext = pos.max(0) - pos.min(0)
    k = int(np.argmin(ext))
    keep = [i for i in range(3) if i != k]
    step = np.array([np.linalg.norm(axv[i]) for i in range(3)])
    proj = np.abs(rho).sum(axis=k) * step[k]          # integrate |spin| along k
    # grid coordinates of the kept axes (cube axes are orthogonal here)
    u = (org[keep[0]] + np.arange(npts[keep[0]]) * step[keep[0]]) * B2A
    v = (org[keep[1]] + np.arange(npts[keep[1]]) * step[keep[1]]) * B2A
    pm = ax_.pcolormesh(u, v, proj.T, cmap="inferno",
                        norm=PowerNorm(0.4, vmin=0, vmax=0.45), shading="auto")
    pa, pb = pos[:, keep[0]] * B2A, pos[:, keep[1]] * B2A
    for z, a, b in zip(Z, pa, pb):
        if z == 1:
            continue
        s = SYM.get(z, str(z))
        ax_.plot(a, b, "o", ms=10 if s == "Al" else 5,
                 mfc="none", mec="cyan" if s == "Al" else "w", mew=1.4 if s == "Al" else 0.7)
        if s in ("Al", "Cl"):
            ax_.annotate(s, (a, b), xytext=(4, 4), textcoords="offset points",
                         color="cyan" if s == "Al" else "w", fontsize=9, fontweight="bold")
    ax_.set_title(title, fontsize=10)
    ax_.set_xlabel(r"$\AA$"); ax_.set_ylabel(r"$\AA$")
    ax_.set_aspect("equal")
fig.colorbar(pm, ax=axes, pad=0.015, shrink=0.85,
             label=r"$\int |\rho_{spin}|$ d$z'$  (e$^-$/$\AA^2$)")
fig.suptitle("Where the electron goes — chloride loss redirects reduction from phenyl to Al "
             "(UB3LYP/def2-TZVP, SMD-THF)", y=1.02)
fig.savefig(FIG + "fig_spin_redirection.png", dpi=300, bbox_inches="tight")
print("wrote fig_spin_redirection.png")
