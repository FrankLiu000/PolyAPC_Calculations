#!/usr/bin/env python3
"""run_md.py — MLFF-MD demonstration at the bare Mg(0001)/APC interface.

The payoff of the MLFF: dynamics AIMD physically cannot reach (~0.1 ps/day) run at GPU speed.
Starts from an equilibrated interface frame, fixes the bottom slab layer (electrode), runs NVT
Langevin @ 300 K / 1 fs (matching the AIMD protocol), and tracks the SAME observables the AIMD
analysis used so we can cross-check against the converged AIMD result (anion stays ~9 A off the
front, intact bonds on a clean start -- master report sec 6/7, sec 3b).

Usage: python run_md.py <model.model> <start.xyz|start.pdb> [n_steps] [out_prefix]
Writes <prefix>_traj.xyz and <prefix>_cv.csv (+ prints a running summary).
"""
import sys
import numpy as np
from ase.io import read, write
from ase import units
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.constraints import FixAtoms
from mace.calculators import MACECalculator

model   = sys.argv[1]
start   = sys.argv[2]
nsteps  = int(sys.argv[3]) if len(sys.argv) > 3 else 50000     # 50 ps @ 1 fs
prefix  = sys.argv[4] if len(sys.argv) > 4 else "md_bare"
DT_FS   = 1.0
T_K     = 300.0
LOG_EV  = 50      # log CVs every 50 steps (50 fs)
TRAJ_EV = 100     # write a frame every 100 steps (0.1 ps)

at = read(start)
at.calc = MACECalculator(model_paths=[model], device="cuda", default_dtype="float32")
sym = np.array(at.get_chemical_symbols()); pos = at.get_positions()

# --- robust atom identification (geometry-based, do not trust raw indices blindly) ---
i_Al = int(np.where(sym == "Al")[0][0])
cl_idx = np.where(sym == "Cl")[0]
d_AlCl = np.linalg.norm(pos[cl_idx] - pos[i_Al], axis=1)
anion_Cl = cl_idx[np.argsort(d_AlCl)[:2]]                  # 2 Cl bonded to Al
cation_Cl = np.array([c for c in cl_idx if c not in anion_Cl])  # 3 bridging mu-Cl
mg_idx = np.where(sym == "Mg")[0]
# cation Mg = the 2 Mg closest to the bridging chlorides; slab = the other 64
dist_to_catCl = np.array([np.linalg.norm(pos[m] - pos[cation_Cl], axis=1).min() for m in mg_idx])
cation_Mg = mg_idx[np.argsort(dist_to_catCl)[:2]]
slab_Mg = np.array([m for m in mg_idx if m not in cation_Mg])
zslab = pos[slab_Mg, 2]
print(f"identified: Al={i_Al}  anion_Cl={anion_Cl.tolist()}  cation_Cl={cation_Cl.tolist()}  "
      f"cation_Mg={cation_Mg.tolist()}  n_slab_Mg={len(slab_Mg)}")
print(f"slab z-range {zslab.min():.2f}-{zslab.max():.2f} A; cation Mg z={pos[cation_Mg,2]}")

# --- fix bottom slab layer (electrode anchor) ---
bottom = slab_Mg[zslab < (zslab.min() + 1.0)]
at.set_constraint(FixAtoms(indices=bottom.tolist()))
print(f"fixed bottom slab layer: {len(bottom)} Mg atoms (z<{zslab.min()+1.0:.2f})")
slab_top_z = zslab.max()

MaxwellBoltzmannDistribution(at, temperature_K=T_K)
dyn = Langevin(at, DT_FS * units.fs, temperature_K=T_K, friction=0.02)

cv = open(f"{prefix}_cv.csv", "w")
cv.write("step,t_ps,T_K,Epot_eV,Al_slab_min_A,Al_Cl1_A,Al_Cl2_A,muCl_max_A,n_anionCl_gt3A\n")
traj_frames = []

def log(step):
    p = at.get_positions(); T = at.get_temperature(); Ep = at.get_potential_energy()
    al_slab = np.linalg.norm(p[slab_Mg] - p[i_Al], axis=1).min()
    aCl = np.linalg.norm(p[anion_Cl] - p[i_Al], axis=1)
    # mu-Cl bridge: max cation_Mg--bridging-Cl min distance (bond stretch tracker)
    mucl = max(np.linalg.norm(p[cation_Mg] - p[c], axis=1).min() for c in cation_Cl)
    n_gt3 = int((aCl > 3.0).sum())
    cv.write(f"{step},{step*DT_FS/1000:.4f},{T:.1f},{Ep:.4f},{al_slab:.3f},"
             f"{aCl[0]:.3f},{aCl[1]:.3f},{mucl:.3f},{n_gt3}\n"); cv.flush()
    return T, al_slab, aCl, n_gt3

print(f"# starting {nsteps} steps ({nsteps*DT_FS/1000:.1f} ps) NVT {T_K}K dt={DT_FS}fs")
T0, al0, aCl0, _ = log(0)
print(f"  t=0.00ps  T={T0:.0f}K  Al-slab={al0:.2f}A  Al-Cl={aCl0[0]:.2f}/{aCl0[1]:.2f}A")
traj_frames.append(at.copy())
for step in range(1, nsteps + 1):
    dyn.run(1)
    if step % LOG_EV == 0:
        T, al, aCl, n_gt3 = log(step)
    if step % TRAJ_EV == 0:
        traj_frames.append(at.copy())
    if step % 2000 == 0:
        print(f"  t={step*DT_FS/1000:.2f}ps  T={T:.0f}K  Al-slab={al:.2f}A  "
              f"Al-Cl={aCl[0]:.2f}/{aCl[1]:.2f}A  anionCl>3A={n_gt3}")
        write(f"{prefix}_traj.xyz", traj_frames)   # checkpoint trajectory
write(f"{prefix}_traj.xyz", traj_frames)
cv.close()
print(f"# DONE wrote {prefix}_traj.xyz ({len(traj_frames)} frames) + {prefix}_cv.csv")
