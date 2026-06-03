#!/usr/bin/env python3
"""make_live_figures.py — figures/tables that complete NOW from data already in
the repo (no DFT/AIMD needed). The node later adds the DFT-derived overlays.

Produces in computational_v2/results/figures/:
  raman_experimental.png   bare-vs-poly Raman (mean +/- sd) with peak annotations
  drt_gamma_heatmaps.png   gamma(tau) vs charge-depth, bare vs poly
  drt_rct_evolution.png    integrated polarisation resistance vs depth
  md_anion_rdf.png         Mg<->anion(Al/Cl) RDF + coordination, bare vs poly
and results/data/raman_peaks.csv (assignment table, copied/normalised).
"""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
FIG = ROOT / "results" / "figures"
DATA = ROOT / "results" / "data"
FIG.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

# key bands to annotate (cm^-1) with short labels
RAMAN_BANDS = [(181, "Mg-Cl"), (276, "Cl-bridge"), (915, "THF ring"),
               (1002, "Ph (anion)"), (1033, "Ph C-H"), (1483, "coord-THF"),
               (1582, "Ph C=C")]


def fig_raman():
    df = pd.read_csv(REPO / "Raman" / "processed_spectra.csv")
    x = df["Raman_shift_cm-1"].to_numpy()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for col, sd, color, lab in (("bareAPC_mean", "bareAPC_sd", "#c0392b", "bare-APC"),
                                ("polyAPC_mean", "polyAPC_sd", "#2471a3", "poly-APC")):
        y = df[col].to_numpy()
        e = df[sd].to_numpy()
        ax.plot(x, y, color=color, lw=1.1, label=lab)
        ax.fill_between(x, y - e, y + e, color=color, alpha=0.18, lw=0)
    ymax = float(np.nanmax(df[["bareAPC_mean", "polyAPC_mean"]].to_numpy()))
    for pos, lab in RAMAN_BANDS:
        ax.axvline(pos, color="0.6", ls=":", lw=0.7)
        ax.text(pos, ymax * 1.01, f"{pos}\n{lab}", fontsize=6.5, rotation=90,
                ha="center", va="bottom")
    ax.set_xlabel("Raman shift (cm$^{-1}$)")
    ax.set_ylabel("intensity (baseline-corrected)")
    ax.set_title("Raman: bare-APC vs poly-APC (mean $\\pm$ s.d.)  "
                 "[DFT stick spectrum added on node]")
    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(top=ymax * 1.32)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "raman_experimental.png", dpi=160)
    plt.close(fig)
    # assignment table -> results/data
    pa = pd.read_csv(REPO / "Raman" / "peak_assignments.csv")
    pa.to_csv(DATA / "raman_peaks.csv", index=False)


def _load_drt_long(name):
    df = pd.read_csv(REPO / "in_situ_DRT" / f"DRT_{name}_long.csv")
    piv = df.pivot(index="charge_depth_mAh_cm2", columns="tau_s", values="gamma_ohm")
    return piv


def fig_drt():
    bare = _load_drt_long("bareAPC")
    poly = _load_drt_long("pAPC")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    vmax = max(bare.to_numpy().max(), poly.to_numpy().max())
    for ax, piv, title in ((axes[0], bare, "bare-APC"), (axes[1], poly, "poly-APC")):
        tau = piv.columns.to_numpy(dtype=float)
        depth = piv.index.to_numpy(dtype=float)
        im = ax.pcolormesh(np.log10(tau), depth, piv.to_numpy(),
                           shading="auto", cmap="viridis", vmin=0, vmax=vmax)
        ax.set_title(title)
        ax.set_xlabel(r"$\log_{10}\,\tau$ (s)")
    axes[0].set_ylabel("charge depth (mAh cm$^{-2}$)")
    fig.colorbar(im, ax=axes, label=r"$\gamma$ ($\Omega$)", fraction=0.04)
    fig.suptitle("In-situ DRT: distribution of relaxation times vs plating depth")
    fig.savefig(FIG / "drt_gamma_heatmaps.png", dpi=160)
    plt.close(fig)

    # integrated polarisation resistance ~ integral gamma d(ln tau) per depth
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for piv, color, lab in ((bare, "#c0392b", "bare-APC"), (poly, "#2471a3", "poly-APC")):
        tau = piv.columns.to_numpy(dtype=float)
        lnt = np.log(tau)
        _trap = getattr(np, "trapezoid", getattr(np, "trapz", None))
        rct = _trap(piv.to_numpy(), lnt, axis=1)
        ax2.plot(piv.index.to_numpy(dtype=float), rct, "o-", ms=3,
                 color=color, label=lab)
    ax2.set_xlabel("charge depth (mAh cm$^{-2}$)")
    ax2.set_ylabel(r"$\int \gamma\,\mathrm{d}\ln\tau$  ($\Omega$, $\propto R_{ct}$)")
    ax2.set_title("Interfacial resistance evolution (higher-but-stable in poly)")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(FIG / "drt_rct_evolution.png", dpi=160)
    plt.close(fig2)


def _read_xvg(path):
    xs, ys = [], []
    for ln in Path(path).read_text().splitlines():
        if ln.startswith(("#", "@")) or not ln.strip():
            continue
        p = ln.split()
        xs.append(float(p[0]))
        ys.append(float(p[1]))
    return np.array(xs), np.array(ys)


def fig_md_anion():
    base = REPO / "classical_molecular_dynamics" / "handoff_for_agent" / "rdf"
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    for sub, color in (("bare", "#c0392b"), ("poly", "#2471a3")):
        for fname, ls, lab in (("rdf_MgAnAl.xvg", "-", "Mg-Al"),
                               ("rdf_MgAnCl.xvg", "--", "Mg-Cl(anion)")):
            f = base / sub / fname
            if f.exists():
                x, y = _read_xvg(f)
                a1.plot(x * 10, y, ls, color=color, lw=1.1,
                        label=f"{sub}: {lab}")
        cn = base / sub / "cn_MgAnAl.xvg"
        if cn.exists():
            x, y = _read_xvg(cn)
            a2.plot(x * 10, y, "-", color=color, lw=1.2, label=f"{sub}")
    a1.set_xlabel("r ($\\AA$)")
    a1.set_ylabel("g(r)")
    a1.set_title("Mg$\\leftrightarrow$anion RDF (bare vs poly)")
    a1.legend(fontsize=7)
    a1.set_xlim(0, 8)
    a2.set_xlabel("r ($\\AA$)")
    a2.set_ylabel("coordination number")
    a2.set_title("Mg-Al(anion) running coordination")
    a2.legend(fontsize=7)
    a2.set_xlim(0, 8)
    fig.tight_layout()
    fig.savefig(FIG / "md_anion_rdf.png", dpi=160)
    plt.close(fig)


def main():
    fig_raman()
    fig_drt()
    fig_md_anion()
    figs = sorted(p.name for p in FIG.glob("*.png"))
    print(f"[make_live_figures] wrote {len(figs)} figures: {', '.join(figs)}")
    print(f"[make_live_figures] wrote {DATA/'raman_peaks.csv'}")


if __name__ == "__main__":
    main()
