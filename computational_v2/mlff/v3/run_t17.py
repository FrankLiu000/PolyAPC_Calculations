#!/usr/bin/env python3
"""T17 — large-cell REACTIVE interface MD with the validated T16 MLFF.
Runs Mg(0001)|electrolyte (bare OR poly) at GPU speed, tracking Al-anion approach,
reductive decomposition (Cl/Ph stripping), and Al deposition onto the slab, so
analyze_t17.py can build the SEI composition-vs-depth profile and test the ToF-SIMS
Al-poor/Si-rich result. Reactive PES surrogate (no explicit field/charge) — drive
plating by starting from near-surface (T10-sampled) configs; honest caveats in README.

usage: run_t17.py <model.model> <start.xyz> <label> [n_steps] [T_K]
writes <label>_traj.xyz (+ <label>_cv.csv). Spot-validate frames vs DFT before trusting.
"""
import sys, numpy as np
from ase.io import read, write
from ase import units
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.constraints import FixAtoms
from mace.calculators import MACECalculator

model, start, label = sys.argv[1], sys.argv[2], sys.argv[3]
nsteps = int(sys.argv[4]) if len(sys.argv) > 4 else 200000     # 200 ps @ 1 fs
T_K    = float(sys.argv[5]) if len(sys.argv) > 5 else 300.0
DT_FS, LOG_EV, TRAJ_EV = 1.0, 50, 200
R_DEP = 3.2   # Å : Al within this of a slab-Mg AND stripped of anion ligands = "deposited"

at = read(start)
at.calc = MACECalculator(model_paths=[model], device="cuda", default_dtype="float32")
sym = np.array(at.get_chemical_symbols()); pos = at.get_positions()
z = pos[:,2]

# --- electrode slab = the contiguous Mg block at low z (vs cation Mg, which sits in the electrolyte) ---
mg = np.where(sym=="Mg")[0]
zmg = z[mg]
# slab Mg cluster: those below the gap between slab-top and the electrolyte
order = mg[np.argsort(zmg)]; zs = np.sort(zmg)
gap = np.argmax(np.diff(zs)) if len(zs)>1 else len(zs)-1
slab_Mg = order[:gap+1]; cat_Mg = order[gap+1:]
slab_top = z[slab_Mg].max(); slab_bot = z[slab_Mg].min()
# fix the bottom 2 layers (≈ lowest 1.2 Å worth) -> rigid electrode bulk; surface free to accept Al
fixed = slab_Mg[z[slab_Mg] < slab_bot + 1.2]
at.set_constraint(FixAtoms(indices=fixed.tolist()))
Al = np.where(sym=="Al")[0]; Cl = np.where(sym=="Cl")[0]; Si = np.where(sym=="Si")[0]
print(f"[{label}] N={len(at)}  slab_Mg={len(slab_Mg)} (fixed {len(fixed)})  cat_Mg={len(cat_Mg)}  "
      f"Al={len(Al)} Cl={len(Cl)} Si={len(Si)}  slab_top={slab_top:.2f} Å")

MaxwellBoltzmannDistribution(at, temperature_K=T_K)
dyn = Langevin(at, DT_FS*units.fs, temperature_K=T_K, friction=0.02)
cv = open(f"{label}_cv.csv","w")
cv.write("step,t_ps,T_K,Epot_eV,n_Al_near(<3.2A),n_Al_deposited,min_Al_slab_A,mean_Al_height_A\n")
frames=[]

def al_state(p):
    """per-Al: nearest slab-Mg dist, and #Cl within 2.8 Å (anion ligation)."""
    near=[]; dep=0; heights=[]
    for a in Al:
        dsl = np.linalg.norm(p[slab_Mg]-p[a], axis=1).min()
        ncl = int((np.linalg.norm(p[Cl]-p[a], axis=1) < 2.8).sum())
        heights.append(p[a,2]-slab_top)
        if dsl < R_DEP: near.append(a)
        if dsl < R_DEP and ncl <= 1:      # at the slab AND stripped of its 2 anion-Cl = reduced/deposited
            dep += 1
    return len(near), dep, (min(np.linalg.norm(p[slab_Mg]-p[a],axis=1).min() for a in Al) if len(Al) else np.nan), np.mean(heights) if len(heights) else np.nan

def log(step):
    p=at.get_positions(); T=at.get_temperature(); Ep=at.get_potential_energy()
    nn,dep,dmin,hmean = al_state(p)
    cv.write(f"{step},{step*DT_FS/1000:.4f},{T:.1f},{Ep:.4f},{nn},{dep},{dmin:.3f},{hmean:.3f}\n"); cv.flush()
    return T,nn,dep,dmin

T0,nn0,dep0,dmin0=log(0); frames.append(at.copy())
print(f"# {label}: {nsteps} steps ({nsteps*DT_FS/1000:.0f} ps) NVT {T_K}K; Al-slab min {dmin0:.2f} Å")
for step in range(1,nsteps+1):
    dyn.run(1)
    if step%LOG_EV==0: T,nn,dep,dmin=log(step)
    if step%TRAJ_EV==0: frames.append(at.copy())
    if step%5000==0:
        print(f"  t={step*DT_FS/1000:.1f}ps T={T:.0f}K  Al_near={nn} Al_deposited={dep} min_Al-slab={dmin:.2f}Å")
        write(f"{label}_traj.xyz", frames)
write(f"{label}_traj.xyz", frames); cv.close()
print(f"# DONE {label}: {len(frames)} frames -> {label}_traj.xyz + {label}_cv.csv")
