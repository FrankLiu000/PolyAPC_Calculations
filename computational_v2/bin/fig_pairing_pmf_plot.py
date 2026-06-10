#!/usr/bin/env python3
"""Re-plot the pairing PMF from the saved histogram (pairing_pmf_hist.npz) — zoomed + annotated."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG = "/CH/poly_v2/results/figures/"
d = np.load(FIG + "pairing_pmf_hist.npz")
xe, ye = d["xe"], d["ye"]
xc, yc = 0.5 * (xe[:-1] + xe[1:]), 0.5 * (ye[:-1] + ye[1:])
kT = 0.0019872 * 300.0
Fmax = 4.5

stats = {}
for tag in ["bare", "poly"]:
    H = d[tag]; P = H / H.sum()
    cip = yc < 3.25; far = yc > 5.0
    stats[tag] = (P[:, cip].sum(), -kT * np.log(P[:, cip].sum() / P[:, far].sum()))

fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0), sharex=True, sharey=True)
for ax, tag in zip(axes, ["bare", "poly"]):
    H = d[tag]
    F = np.full_like(H, np.nan); m = H > 0
    F[m] = -kT * np.log(H[m]); F -= np.nanmin(F)
    pc = ax.pcolormesh(xe, ye, np.ma.masked_invalid(np.clip(F, 0, Fmax)).T,
                       cmap="RdYlBu_r", vmin=0, vmax=Fmax, shading="auto")
    ax.contour(xc, yc, np.clip(np.nan_to_num(F, nan=Fmax), 0, Fmax).T,
               levels=np.arange(0.5, Fmax, 0.5), colors="k", linewidths=0.4, alpha=0.45)
    pcip, dF = stats[tag]
    ax.set_title("%s   (3 $\\times$ 100 ns, 80 pairs, 300 K)" % tag)
    ax.text(0.97, 0.06, "P($\\mu$-Cl CIP) = %.1f%%\n$\\Delta F$(CIP$\\to$free) = %.2f kcal/mol"
            % (100 * pcip, -dF), transform=ax.transAxes, ha="right", fontsize=9,
            bbox=dict(fc="w", alpha=0.85, ec="0.6"))
    ax.set_xlabel(r"d(Al $-$ nearest cation Mg)  /  $\AA$")
    ax.axhline(3.25, color="0.3", ls="--", lw=0.7)
axes[0].set_ylabel(r"d(anion Cl $-$ nearest cation Mg)  /  $\AA$")
axes[0].annotate(r"$\mu$-Cl CIP basin", xy=(4.43, 2.43), xytext=(4.6, 4.2),
                 arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=9)
axes[0].set_xlim(3, 12); axes[0].set_ylim(2, 10)
cb = fig.colorbar(pc, ax=axes, pad=0.015)
cb.set_label(r"$-k_BT \ln P$  /  kcal mol$^{-1}$  (rel. to min)")
fig.suptitle("Ion-pairing free-energy landscape — classical FF (no bond-breaking: the DFT\n"
             "Cl-abstraction channel is invisible at this level); landscapes are NEARLY IDENTICAL", y=1.02)
fig.savefig(FIG + "fig_pairing_pmf.png", dpi=300, bbox_inches="tight")
print("wrote fig_pairing_pmf.png")
