#!/usr/bin/env python3
"""umbrella.py — one umbrella-sampling window for the Mg2+ desolvation/approach free energy.

CV = z-height of the cation [Mg2(mu-Cl)3] core COM above the slab top layer (the approach
coordinate; desolvation happens implicitly as the cation nears the electrode). A harmonic bias
0.5*k*(CV - z0)^2 restrains the window; the slab is held rigid. Records CV + first-shell
coordination (Mg-O THF, Mg-Cl) + cluster integrity + a crude extrapolation flag (|F|max) so the
near-surface frames the run generates can be queued for DFT labeling (active learning).

Usage: python umbrella.py <model> <start.xyz> <z0_Ang> <k_eV/A2> <nsteps> <out_prefix>
Writes <out_prefix>.dat (CV timeseries, header carries z0/k/kT/zref for WHAM).
"""
import sys
import numpy as np
from ase.io import read, write
from ase import units
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.constraints import FixAtoms
from mace.calculators import MACECalculator

model, start = sys.argv[1], sys.argv[2]
z0, k = float(sys.argv[3]), float(sys.argv[4])
nsteps = int(sys.argv[5]); prefix = sys.argv[6]
DT_FS, T_K, LOG_EV, EQUIL, TRAJ_EV = 1.0, 300.0, 20, 2000, 200  # log 20fs; discard 2ps; save a frame every 200 fs
kT = units.kB * T_K

at = read(start)
at.calc = MACECalculator(model_paths=[model], device="cuda", default_dtype="float32")
sym = np.array(at.get_chemical_symbols()); pos = at.get_positions()
i_Al = int(np.where(sym == "Al")[0][0])
cl = np.where(sym == "Cl")[0]; mg = np.where(sym == "Mg")[0]
anion_cl = cl[np.argsort([at.get_distance(i_Al, int(c), mic=True) for c in cl])[:2]]
cat_cl = np.array([c for c in cl if c not in anion_cl])
cat_mg = mg[np.argsort([min(at.get_distance(int(m), int(c), mic=True) for c in cat_cl) for m in mg])[:2]]
slab = np.array([m for m in mg if m not in cat_mg])
O = np.where(sym == "O")[0]
z_ref = float(np.sort(pos[slab, 2])[-16:].mean())   # slab top-layer mean z (fixed slab -> constant)


class UmbrellaZ:
    """Harmonic bias on the z-height of cat_mg COM above z_ref."""
    def __init__(self, indices, z0, k, z_ref):
        self.idx = np.asarray(indices); self.z0 = z0; self.k = k; self.zr = z_ref
    def _cv(self, atoms):
        return atoms.get_positions()[self.idx, 2].mean() - self.zr
    def adjust_positions(self, atoms, new):
        pass
    def adjust_forces(self, atoms, forces):
        forces[self.idx, 2] += -self.k * (self._cv(atoms) - self.z0) / len(self.idx)
    def adjust_potential_energy(self, atoms):
        return 0.5 * self.k * (self._cv(atoms) - self.z0) ** 2
    def get_removed_dof(self, atoms):
        return 0

at.set_constraint([FixAtoms(indices=slab.tolist()), UmbrellaZ(cat_mg, z0, k, z_ref)])
MaxwellBoltzmannDistribution(at, temperature_K=T_K)
dyn = Langevin(at, DT_FS * units.fs, temperature_K=T_K, friction=0.02)

def cn(atoms, centers, others, rc):
    p = atoms.get_positions(); n = 0
    for c in centers:
        d = np.array([atoms.get_distance(int(c), int(o), mic=True) for o in others])
        n += int((d < rc).sum())
    return n

f = open(f"{prefix}.dat", "w")
f.write(f"# z0={z0} k={k} kT={kT:.6f} zref={z_ref:.3f} cat_mg={cat_mg.tolist()}\n")
f.write("# step  cv_A  mgO_cn  mgCl_cn  mgmg_A  Fmax_eVA\n")

def log(step):
    cv = at.get_positions()[cat_mg, 2].mean() - z_ref
    mgO = cn(at, cat_mg, O, 2.6); mgCl = cn(at, cat_mg, cl, 2.9)
    mgmg = at.get_distance(int(cat_mg[0]), int(cat_mg[1]), mic=True)
    fmax = np.linalg.norm(at.get_forces()[64:], axis=1).max()   # electrolyte |F|max (extrapolation proxy)
    f.write(f"{step} {cv:.4f} {mgO} {mgCl} {mgmg:.3f} {fmax:.3f}\n"); f.flush()
    return cv, fmax

print(f"# window z0={z0} k={k} zref={z_ref:.2f} cat_mg={cat_mg.tolist()} nsteps={nsteps}")
cv0, _ = log(0)
print(f"  start CV={cv0:.2f} A")
traj = []
for step in range(1, nsteps + 1):
    dyn.run(1)
    if step % LOG_EV == 0:
        cv, fmax = log(step)
        if not np.isfinite(cv) or fmax > 5e3:      # blow-up guard (deep extrapolation -> NaN); abort cleanly
            print(f"  ABORT step {step}: CV={cv} Fmax={fmax:.1f} (force blow-up / extrapolation singularity)")
            break
    if step % TRAJ_EV == 0 and step >= EQUIL:
        traj.append(at.copy())
    if step % 2000 == 0:
        print(f"  step {step} CV={cv:.2f} Fmax={fmax:.1f}")
if traj:
    write(f"{prefix}_traj.xyz", traj)
write(f"{prefix}_last.xyz", at)          # final equilibrated config -> start for the next (chained) window
f.close()
print(f"# DONE {prefix}.dat (discard first {EQUIL} steps as equilibration in WHAM)")
