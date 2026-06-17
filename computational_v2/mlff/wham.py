#!/usr/bin/env python3
"""wham.py — 1D WHAM on umbrella windows -> desolvation/approach free energy F(z), with error bars.

Reads window_*.dat (umbrella.py output; header carries z0/k/kT). Discards equilibration,
histograms the CV, iterates the WHAM equations. With --boot N, block-bootstraps the per-window
samples N times for statistical error bars on F(z). Writes <out>_pmf.dat (z, F_eV, F_kJ, counts, err_kJ).

Usage: python wham.py <out_prefix> <w1.dat> [w2.dat ...] [--equil N --bins M --mincount C --boot B]
"""
import sys
import numpy as np

argv = sys.argv[1:]; opts = {}; args = []
i = 0
while i < len(argv):
    if argv[i].startswith("--"):
        opts[argv[i]] = argv[i + 1]; i += 2
    else:
        args.append(argv[i]); i += 1
out = args[0]; files = args[1:]
EQUIL = int(opts.get("--equil", 2000)); NBINS = int(opts.get("--bins", 60))
MINCOUNT = int(opts.get("--mincount", 5)); BOOT = int(opts.get("--boot", 0))

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

allcv = np.concatenate([w["cv"] for w in wins])
edges = np.linspace(allcv.min() - 0.1, allcv.max() + 0.1, NBINS + 1); ctr = 0.5 * (edges[:-1] + edges[1:])
z0s = np.array([w["z0"] for w in wins]); ks = np.array([w["k"] for w in wins])
Vbias = np.array([0.5 * k * (ctr - z0) ** 2 for z0, k in zip(z0s, ks)])   # (nwin, nbins)

def wham_core(cv_list):
    H = np.array([np.histogram(c, edges)[0] for c in cv_list]); N = H.sum(1)
    f = np.zeros(len(cv_list)); expf = np.exp(-Vbias / kT); Hsum = H.sum(0)
    for it in range(100000):
        denom = (N[:, None] * np.exp(f[:, None] / kT) * expf).sum(0)
        rho = Hsum / np.where(denom > 0, denom, 1e-300); rho /= rho.sum()
        fnew = -kT * np.log((rho[None, :] * expf).sum(1) + 1e-300); fnew -= fnew[0]
        if np.max(np.abs(fnew - f)) < 1e-6:
            break
        f = fnew
    F = -kT * np.log(rho + 1e-300); F[Hsum < MINCOUNT] = np.nan; F -= np.nanmin(F)
    return F, Hsum

F, counts = wham_core([w["cv"] for w in wins])
F_kJ = F * 96.485

# --- block-bootstrap error bars ---
err_kJ = np.full(NBINS, np.nan)
if BOOT:
    NB = 8                                                  # blocks per window (respect autocorrelation)
    boots = []
    rng = np.random.default_rng(20260617)
    for b in range(BOOT):
        cvb = []
        for w in wins:
            blocks = np.array_split(w["cv"], NB)
            pick = rng.integers(0, NB, NB)
            cvb.append(np.concatenate([blocks[j] for j in pick]))
        Fb, _ = wham_core(cvb)
        boots.append(Fb * 96.485)
    err_kJ = np.nanstd(np.array(boots), axis=0)

# --- first/second-half convergence check ---
def half(sel):
    return wham_core([w["cv"][sel(len(w["cv"]))] for w in wins])[0] * 96.485
F1 = half(lambda n: slice(0, n // 2)); F2 = half(lambda n: slice(n // 2, n))
both = np.isfinite(F1) & np.isfinite(F2)
conv = np.nanmax(np.abs(F1 - F2)[both]) if both.any() else np.nan

np.savetxt(f"{out}_pmf.dat", np.column_stack([ctr, F, F_kJ, counts, err_kJ]),
           header="z_A  F_eV  F_kJmol  counts  err_kJmol")
print(f"WHAM: {len(wins)} windows, {int(counts.sum())} samples, kT={kT:.4f} eV, boot={BOOT}, equil={EQUIL}")
fin = np.isfinite(F)
zmin = ctr[fin][np.argmin(F[fin])]
span = F_kJ[fin].max() - F_kJ[fin].min()
emax = np.nanmax(err_kJ[fin]) if BOOT else float('nan')
print(f"F(z): range {ctr[fin].min():.2f}-{ctr[fin].max():.2f} A; min at z={zmin:.2f} A; "
      f"span={span:.1f} kJ/mol; max boot-err={emax:.1f} kJ/mol")
print(f"convergence (max |F_firsthalf - F_secondhalf|) = {conv:.1f} kJ/mol "
      f"({'CONVERGED' if conv < 10 else 'still drifting' if conv==conv else 'n/a'})")
print("window  z0   <cv>   <MgO>  <MgCl>  Nsamp")
for w in wins:
    print(f"  {w['z0']:5.1f} {w['cv'].mean():6.2f} {w['mgO'].mean():6.2f} {w['mgCl'].mean():6.2f} {len(w['cv']):6d}")
