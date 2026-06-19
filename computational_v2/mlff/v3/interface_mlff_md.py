#!/usr/bin/env python3
"""MLFF-MD of the Mg(0001)|electrolyte interface (bare OR poly) — the route that
works where classical GROMACS cannot (MACE is geometry-based: no molecule-unwrap,
so the percolating/POSS network is fine). Slab = first 64 atoms (EPYC convention,
the DFT-masked rigid electrode). Tracks the Al-ANION approach to the front.
usage: interface_mlff_md.py <model> <start.xyz> <label> [n_steps] [T_K]"""
import sys, numpy as np
from ase.io import read, write
from ase import units
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.constraints import FixAtoms
from mace.calculators import MACECalculator
model,start,label = sys.argv[1:4]
nsteps = int(sys.argv[4]) if len(sys.argv)>4 else 50000   # 50 ps @ 1 fs
T_K    = float(sys.argv[5]) if len(sys.argv)>5 else 300.0
NSLAB, DT = 64, 1.0
at = read(start); at.calc = MACECalculator(model_paths=[model], device="cuda", default_dtype="float32")
sym = np.array(at.get_chemical_symbols())
slab = np.arange(NSLAB); slab_top0 = at.get_positions()[slab,2].max()
at.set_constraint(FixAtoms(indices=slab.tolist()))   # rigid electrode (forces were DFT-masked)
Al = np.where(sym=="Al")[0]; Cl = np.where(sym=="Cl")[0]
O  = np.where(sym=="O")[0];  Si = np.where(sym=="Si")[0]
print(f"[{label}] {len(at)} atoms; slab(fixed)={NSLAB} Mg; Al={len(Al)} Cl={len(Cl)} O={len(O)} Si={len(Si)}")
MaxwellBoltzmannDistribution(at, temperature_K=T_K)
dyn = Langevin(at, DT*units.fs, temperature_K=T_K, friction=0.02)
cv = open(f"{label}_cv.csv","w")
cv.write("step,t_ps,T_K,Epot_eV,Al_height_A,Al_slabMin_A,Al_nCl,Al_nO,Al_SiMin_A\n")
frames=[]
def log(step):
    p=at.get_positions(); st=p[slab,2].max()
    a=Al[0]; h=p[a,2]-st; dsl=np.linalg.norm(p[slab]-p[a],axis=1).min()
    ncl=int((np.linalg.norm(p[Cl]-p[a],axis=1)<2.8).sum()); no=int((np.linalg.norm(p[O]-p[a],axis=1)<3.0).sum())
    dsi=(np.linalg.norm(p[Si]-p[a],axis=1).min() if len(Si) else np.nan)
    cv.write(f"{step},{step*DT/1000:.3f},{at.get_temperature():.1f},{at.get_potential_energy():.3f},{h:.3f},{dsl:.3f},{ncl},{no},{dsi:.3f}\n"); cv.flush()
    return h,dsl
h0,d0=log(0); frames.append(at.copy())
print(f"# {label}: {nsteps*DT/1000:.0f} ps NVT {T_K}K; Al height0={h0:.2f} Al-slab0={d0:.2f} A")
for step in range(1,nsteps+1):
    dyn.run(1)
    if step%50==0: log(step)
    if step%200==0: frames.append(at.copy())
    if step%5000==0:
        h,d=log(step); print(f"  t={step*DT/1000:.0f}ps Al_height={h:.2f} Al-slab={d:.2f} A"); write(f"{label}_traj.xyz",frames)
write(f"{label}_traj.xyz",frames); cv.close(); print(f"# DONE {label}: {len(frames)} frames")
