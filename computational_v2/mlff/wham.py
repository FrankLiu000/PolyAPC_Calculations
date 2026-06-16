#!/usr/bin/env python3
"""wham.py — 1D WHAM on umbrella windows -> desolvation/approach free energy F(z).

Reads window_*.dat (umbrella.py output; header carries z0/k/kT). Discards equilibration,
histograms the CV, iterates the WHAM equations, writes F(z) (kJ/mol, min shifted to 0) +
a coordination-number profile and an extrapolation-overlap report.

Usage: python wham.py <out_prefix> <window1.dat> [window2.dat ...]   ([opts: --equil N --bins M])
Writes <out_prefix>_pmf.dat and prints the barrier/well summary.
"""
import sys
import numpy as np

args = [a for a in sys.argv[1:] if not a.startswith("--")]
opts = {sys.argv[i]: sys.argv[i + 1] for i in range(len(sys.argv)) if sys.argv[i].startswith("--")}
out = args[0]; files = args[1:]
EQUIL = int(opts.get("--equil", 2000)); NBINS = int(opts.get("--bins", 60))

wins = []
for fn in files:
    z0 = k = kT = None
    for L in open(fn):
        if L.startswith("# z0="):
            d = dict(tok.split("=") for tok in L[2:].split() if "=" in tok and tok.split("=")[0] in ("z0", "k", "kT"))
            z0, k, kT = float(d["z0"]), float(d["k"]), float(d["kT"]); break
    data = np.loadtxt(fn, comments="#")
    m = data[:, 0] >= EQUIL
    wins.append(dict(z0=z0, k=k, cv=data[m, 1], mgO=data[m, 2], mgCl=data[m, 3], fmax=data[m, 5]))
kT = kT  # last header (all equal)

allcv = np.concatenate([w["cv"] for w in wins])
lo, hi = allcv.min() - 0.1, allcv.max() + 0.1
edges = np.linspace(lo, hi, NBINS + 1); ctr = 0.5 * (edges[:-1] + edges[1:])
H = np.array([np.histogram(w["cv"], edges)[0] for w in wins])     # (nwin, nbins)
N = H.sum(1)                                                       # samples/window
Vbias = np.array([0.5 * w["k"] * (ctr - w["z0"]) ** 2 for w in wins])   # (nwin, nbins)

# WHAM iteration
f = np.zeros(len(wins))
for it in range(100000):
    expf = np.exp(-Vbias / kT)                                    # (nwin,nbins)
    denom = (N[:, None] * np.exp(f[:, None] / kT) * expf).sum(0)   # (nbins,)
    rho = H.sum(0) / np.where(denom > 0, denom, 1e-300)
    rho /= rho.sum()
    fnew = -kT * np.log((rho[None, :] * expf).sum(1) + 1e-300)
    fnew -= fnew[0]
    if np.max(np.abs(fnew - f)) < 1e-6:
        f = fnew; break
    f = fnew
MINCOUNT = int(opts.get("--mincount", 5))
counts = H.sum(0)
F = -kT * np.log(rho + 1e-300)
F[counts < MINCOUNT] = np.nan                                     # mask under-sampled bins (WHAM blows up there)
F -= np.nanmin(F)
F_kJ = F * 96.485                                                 # eV -> kJ/mol

# CN profile + overlap/extrapolation report (per-window mean CN & |F|max along CV)
np.savetxt(f"{out}_pmf.dat", np.column_stack([ctr, F, F_kJ, H.sum(0)]),
           header="z_A  F_eV  F_kJmol  counts")
print(f"WHAM: {len(wins)} windows, {int(N.sum())} samples, {it} iters, kT={kT:.4f} eV")
print("window  z0   <cv>   <MgO>  <MgCl>  <|F|max>  Nsamp")
for w in wins:
    print(f"  {w['z0']:5.1f} {w['cv'].mean():6.2f} {w['mgO'].mean():6.2f} {w['mgCl'].mean():6.2f} "
          f"{w['fmax'].mean():8.2f} {len(w['cv']):6d}")
fin = np.isfinite(F)
print(f"F(z): range {ctr[fin].min():.2f}-{ctr[fin].max():.2f} A; "
      f"min at z={ctr[fin][np.argmin(F[fin])]:.2f} A; "
      f"max-min (apparent barrier) = {F_kJ[fin].max()-F_kJ[fin].min():.1f} kJ/mol")
hi_f = np.concatenate([w["fmax"] for w in wins])
print(f"EXTRAPOLATION WARNING: electrolyte |F|max mean={hi_f.mean():.1f} max={hi_f.max():.1f} eV/A; "
      f"frames >12 eV/A (likely untrained near-surface): {(hi_f>12).sum()}/{len(hi_f)} -> queue for DFT labeling")
