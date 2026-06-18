#!/usr/bin/env python3
"""mace_feasibility.py — does the MACE-MP-0 foundation model track our DFT PES?
Reads energy-labeled frames (DFT energy in info['energy'], eV), computes MACE-MP-0
energies, and correlates MEAN-SUBTRACTED energies (absolute reference differs between
MACE-MP and CP2K-GTH, so only relative energy fluctuations are meaningful).
High R^2 -> foundation model is in the ballpark (fine-tune route); low -> bespoke training.
Usage: python mace_feasibility.py <dataset.xyz> <n_frames>
"""
import sys
import numpy as np
from ase.io import read

fn, nmax = sys.argv[1], int(sys.argv[2])
frames = read(fn, ":")
step = max(1, len(frames) // nmax)
frames = frames[::step][:nmax]
print(f"  loaded {len(frames)} frames from {fn}")

from mace.calculators import mace_mp
calc = mace_mp(model="small", dispersion=False, default_dtype="float64", device="cpu")

dft, mace = [], []
for i, at in enumerate(frames):
    try:
        e_dft = at.get_potential_energy()  # ASE stores extxyz energy= in a SinglePointCalculator
    except Exception:
        e_dft = at.info.get("energy")
    if e_dft is None:
        continue
    at.calc = calc
    e_mace = at.get_potential_energy()
    dft.append(e_dft); mace.append(e_mace)
    if i % 10 == 0:
        print(f"   frame {i}: DFT {e_dft:.3f}  MACE {e_mace:.3f} eV")

dft, mace = np.array(dft), np.array(mace)
n = len(dft); nat = len(frames[0])
d0, m0 = dft - dft.mean(), mace - mace.mean()
R = np.corrcoef(d0, m0)[0, 1]
rmse = np.sqrt(np.mean((d0 - m0) ** 2))
print(f"\n  === MACE-MP-0 vs DFT (PBE-D3/GTH), n={n}, {nat} atoms ===")
print(f"  DFT energy spread (sd):   {dft.std():.3f} eV ({1000*dft.std()/nat:.2f} meV/atom)")
print(f"  MACE energy spread (sd):  {mace.std():.3f} eV")
print(f"  correlation R:            {R:+.3f}   (R^2={R*R:.3f})")
print(f"  RMSE(mean-subtracted):    {rmse:.3f} eV ({1000*rmse/nat:.2f} meV/atom)")
print(f"  VERDICT: {'foundation model TRACKS the PES -> fine-tune route' if R>0.7 else 'weak match -> bespoke from-scratch training on GPU'}")
