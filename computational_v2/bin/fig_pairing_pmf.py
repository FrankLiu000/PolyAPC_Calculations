#!/usr/bin/env python3
"""fig_pairing_pmf.py — genuine 2D ion-pairing free-energy landscape from classical MD.

F(x,y) = -kT ln P(x,y) + C with
  x = d(anion Al -> nearest cation Mg)        (pair separation)
  y = d(anion Cl -> nearest cation Mg)        (mu-Cl bridging coordinate)
accumulated over 80 ion pairs x 3 replicas x 100 ns (frames every 10 ps), bare vs poly.
This is the one statistically defensible free-energy heatmap in the campaign: equilibrium
force-field sampling with abundant recrossings. Caveats (printed on figure): FF level
(no bond breaking -> the DFT abstraction channel is invisible here); P not volume-corrected
(min-distance CVs have no simple Jacobian); relative basins/saddles are the meaningful content.

Atom-name trap: MGC THF carbons are named Cl01..Cl54 — select anion Cl by EXACT names Cl1 Cl2.
"""
import numpy as np

MD = "/CH/Claude_Workplace/Classical_MD/"
FIG = "/CH/poly_v2/results/figures/"
KT_KCAL = 0.0019872 * 300.0  # kcal/mol at 300 K
XE = np.linspace(3.0, 14.0, 166)
YE = np.linspace(2.0, 14.0, 181)
STEP = 2  # every 2nd frame (20 ps)


def accumulate(tag):
    import MDAnalysis as mda
    from MDAnalysis.lib.distances import distance_array
    H = np.zeros((len(XE) - 1, len(YE) - 1))
    for rep in ["prod", "rep2", "rep3"]:
        u = mda.Universe(MD + tag + "/prod.tpr", MD + tag + "/" + rep + ".xtc")
        al = u.select_atoms("resname ANI and name Al")
        cl = u.select_atoms("resname ANI and name Cl1 Cl2")
        mg = u.select_atoms("resname MGC and name Mg1 Mg2")
        nA = len(al)
        for ts in u.trajectory[::STEP]:
            dam = distance_array(al.positions, mg.positions, box=ts.dimensions)
            dcm = distance_array(cl.positions, mg.positions, box=ts.dimensions)
            x = dam.min(axis=1)
            y = dcm.reshape(nA, 2, -1).min(axis=(1, 2))
            h, _, _ = np.histogram2d(x, y, bins=[XE, YE])
            H += h
        print(tag, rep, "done; total samples %.2e" % H.sum(), flush=True)
    return H


def main():
    Hs = {tag: accumulate(tag) for tag in ["bare", "poly"]}
    np.savez(FIG + "pairing_pmf_hist.npz", bare=Hs["bare"], poly=Hs["poly"], xe=XE, ye=YE)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharex=True, sharey=True)
    Fmax = 4.5
    for ax, tag in zip(axes, ["bare", "poly"]):
        H = Hs[tag]
        F = np.full_like(H, np.nan)
        m = H > 0
        F[m] = -KT_KCAL * np.log(H[m])
        F -= np.nanmin(F)
        pc = ax.pcolormesh(XE, YE, np.ma.masked_invalid(np.clip(F, 0, Fmax)).T,
                           cmap="RdYlBu_r", vmin=0, vmax=Fmax, shading="auto")
        cs = ax.contour(0.5 * (XE[:-1] + XE[1:]), 0.5 * (YE[:-1] + YE[1:]),
                        np.clip(F, 0, Fmax).T, levels=np.arange(0.5, Fmax, 0.5),
                        colors="k", linewidths=0.4, alpha=0.5)
        ax.set_title("%s  (3 x 100 ns, 80 pairs, 300 K)" % tag)
        ax.set_xlabel(r"d(Al $-$ nearest cation Mg)  /  $\AA$")
        n = Hs[tag].sum()
        ax.text(0.02, 0.02, "N = %.1e samples" % n, transform=ax.transAxes, fontsize=8)
    axes[0].set_ylabel(r"d(anion Cl $-$ nearest cation Mg)  /  $\AA$")
    cb = fig.colorbar(pc, ax=axes, pad=0.015)
    cb.set_label(r"$-k_BT\,\ln P$  /  kcal mol$^{-1}$  (rel. to global min)")
    fig.suptitle("Ion-pairing free-energy landscape (classical FF; no bond-breaking — "
                 "the DFT Cl-abstraction channel is invisible at this level)", y=1.0)
    fig.savefig(FIG + "fig_pairing_pmf.png", dpi=300, bbox_inches="tight")
    print("wrote fig_pairing_pmf.png")


if __name__ == "__main__":
    main()
