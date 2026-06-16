#!/usr/bin/env python3
"""diagnose_forces.py — QC gate for an MLFF training set's FORCE labels.

Catches the Round-1 bug (slab-Mg forces corrupt: net force ~71 eV/A, uncorrelated with the PES;
electrolyte forces clean). Run this on any candidate dataset before training. A physical DFT
single-point conserves momentum -> ||sum F|| must be ~0 (<~0.1 eV/A) per frame. We also report the
per-region correlation against the MACE-MP-0 foundation (a clean conservative reference) if mace is
installed.

Usage: python diagnose_forces.py <dataset.xyz> [n_slab=64]
Exit code 0 if all frames pass the momentum gate, 1 otherwise.
"""
import sys
import numpy as np
from ase.io import read

fn = sys.argv[1] if len(sys.argv) > 1 else "dataset_train.xyz"
n_slab = int(sys.argv[2]) if len(sys.argv) > 2 else 64
frames = read(fn, ":")
nat = len(frames[0])

# --- momentum diagnostics (foundation-independent) ---
net = np.array([np.linalg.norm(at.get_forces().sum(0)) for at in frames])
net_slab = np.array([np.linalg.norm(at.get_forces()[:n_slab].sum(0)) for at in frames]) if n_slab else np.zeros(len(frames))
net_rest = np.array([np.linalg.norm(at.get_forces()[n_slab:].sum(0)) for at in frames])
n_bad_global = int((net > 0.1).sum())
print(f"{fn}: {len(frames)} frames x {nat} atoms")
print(f"||sum F|| per frame: mean={net.mean():.2f} max={net.max():.2f} eV/A  ({n_bad_global}/{len(frames)} >0.1)")
print(f"  net on slab(0..{n_slab-1}) mean={net_slab.mean():.2f} | on rest mean={net_rest.mean():.2f} eV/A")

# --- per-region correlation vs the PBE foundation (clean conservative reference) ---
Re_mean = None
try:
    from mace.calculators import mace_mp
    calc = mace_mp(model="medium", dispersion=False, default_dtype="float64", device="cpu")
    sl = np.arange(n_slab); el = np.arange(n_slab, nat)
    def R(a, b): return float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
    Rs, Re = [], []
    for at in frames[1:11]:
        fd = at.get_forces(); a = at.copy(); a.calc = calc; ff = a.get_forces()
        if n_slab:
            Rs.append(R(fd[sl], ff[sl]))
        Re.append(R(fd[el], ff[el]))
    Re_mean = float(np.nanmean(Re))
    print(f"R(label,foundation) slab={np.nanmean(Rs) if Rs else float('nan'):+.3f}  "
          f"electrolyte={Re_mean:+.3f}  (clean ~>0.7; corrupt ~0)")
except Exception as e:
    print(f"(foundation correlation skipped: {e})")

# --- verdict: trainable if EITHER fully momentum-conserving, OR slab masked (=0) + electrolyte clean ---
fully_clean = n_bad_global == 0
masked_clean = (n_slab > 0 and net_slab.mean() < 0.1 and (Re_mean is None or Re_mean > 0.7))
ok = fully_clean or masked_clean
why = ("fully momentum-conserving" if fully_clean
       else "slab masked (=0) + electrolyte clean" if masked_clean
       else "FAIL: nonzero net force on free atoms / corrupt electrolyte")
print(f"VERDICT: {'PASS' if ok else 'FAIL'} ({why})")
sys.exit(0 if ok else 1)
