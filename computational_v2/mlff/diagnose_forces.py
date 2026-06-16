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

# --- momentum gate (foundation-independent, the decisive physical test) ---
net = np.array([np.linalg.norm(at.get_forces().sum(0)) for at in frames])
net_slab = np.array([np.linalg.norm(at.get_forces()[:n_slab].sum(0)) for at in frames])
net_rest = np.array([np.linalg.norm(at.get_forces()[n_slab:].sum(0)) for at in frames])
n_bad = int((net > 0.1).sum())
print(f"{fn}: {len(frames)} frames x {nat} atoms")
print(f"||sum F|| per frame: mean={net.mean():.2f} max={net.max():.2f} eV/A  "
      f"[{n_bad}/{len(frames)} exceed 0.1 eV/A -> {'FAIL' if n_bad else 'PASS'}]")
print(f"  net on slab(0..{n_slab-1}) mean={net_slab.mean():.2f} | on rest mean={net_rest.mean():.2f} eV/A")

# --- optional: per-region correlation vs the PBE foundation ---
try:
    from mace.calculators import mace_mp
    calc = mace_mp(model="medium", dispersion=False, default_dtype="float64", device="cpu")
    sl = np.arange(n_slab); el = np.arange(n_slab, nat)
    def R(a, b): return float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
    Rs, Re = [], []
    for at in frames[1:11]:                      # a handful is enough
        fd = at.get_forces(); a = at.copy(); a.calc = calc; ff = a.get_forces()
        Rs.append(R(fd[sl], ff[sl])); Re.append(R(fd[el], ff[el]))
    print(f"R(label,foundation) slab={np.mean(Rs):+.3f}  electrolyte={np.mean(Re):+.3f}  "
          f"(clean ~>0.7; corrupt ~0)")
except Exception as e:
    print(f"(foundation correlation skipped: {e})")

sys.exit(1 if n_bad else 0)
