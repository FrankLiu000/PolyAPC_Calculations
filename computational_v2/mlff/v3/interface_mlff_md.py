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
from ase.calculators.calculator import Calculator, all_changes

class ForceCap(Calculator):
    """Clip per-atom |F| to fmax so a spurious model force-spike can't run the
    integrator away (training |F_el| tops out ~14 eV/Å; cap=60 is 4x real, so it
    is inert in normal dynamics and only fires on unphysical blow-up spikes).
    Counts cap/NaN events so we can verify the trajectory stayed physical."""
    implemented_properties = ["energy","forces","free_energy"]
    def __init__(self, base, fmax=60.0, charges=None, efield=0.0):
        Calculator.__init__(self); self.base=base; self.fmax=fmax; self.ncap=0; self.nnan=0
        self.q=charges; self.E=efield   # external z-field: F_z += q[e]*E[V/A] (= eV/A); cathodic E<0
    def calculate(self, atoms=None, properties=("energy","forces"), system_changes=all_changes):
        Calculator.calculate(self, atoms, properties, system_changes)
        a=atoms.copy(); a.calc=self.base
        e=a.get_potential_energy(); f=np.array(a.get_forces(),dtype=float)
        if not np.isfinite(f).all(): self.nnan+=1; f=np.nan_to_num(f,nan=0.0,posinf=self.fmax,neginf=-self.fmax)
        n=np.linalg.norm(f,axis=1); m=n>self.fmax
        if m.any(): self.ncap+=1; f[m]*=(self.fmax/n[m])[:,None]
        if self.E and self.q is not None: f[:,2]+=self.q*self.E   # external applied field on z
        if not np.isfinite(e): e=0.0
        self.results={"energy":float(e),"forces":f,"free_energy":float(e)}

model,start,label = sys.argv[1:4]
nsteps = int(sys.argv[4]) if len(sys.argv)>4 else 50000   # step count (time = nsteps*DT)
T_K    = float(sys.argv[5]) if len(sys.argv)>5 else 300.0
DT     = float(sys.argv[6]) if len(sys.argv)>6 else 1.0    # fs; 0.5 stabilizes reactive close-approach
FCAP   = float(sys.argv[7]) if len(sys.argv)>7 else 60.0   # eV/Å per-atom force cap (anti-blowup)
EFIELD = float(sys.argv[8]) if len(sys.argv)>8 else 0.0    # V/Å external z-field (0=off; cathodic<0)
QFILE  = sys.argv[9] if len(sys.argv)>9 else None          # per-atom charge .npy (required if EFIELD!=0)
QTOT   = float(sys.argv[10]) if len(sys.argv)>10 else 0.0   # total system charge -> charge-conditioned models (MACELES)
NSLAB  = 64
at = read(start)
at.info["charge"] = QTOT   # MACELES reads total_charge from info['charge']; inert for plain MACE (r6)
_charges = np.load(QFILE) if (EFIELD and QFILE) else None
at.calc = ForceCap(MACECalculator(model_paths=[model], device="cuda", default_dtype="float32"),
                   fmax=FCAP, charges=_charges, efield=EFIELD)
sym = np.array(at.get_chemical_symbols())
slab = np.arange(NSLAB); slab_top0 = at.get_positions()[slab,2].max()
at.set_constraint(FixAtoms(indices=slab.tolist()))   # rigid electrode (forces were DFT-masked)
Al = np.where(sym=="Al")[0]; Cl = np.where(sym=="Cl")[0]
O  = np.where(sym=="O")[0];  Si = np.where(sym=="Si")[0]
print(f"[{label}] {len(at)} atoms; slab(fixed)={NSLAB} Mg; Al={len(Al)} Cl={len(Cl)} O={len(O)} Si={len(Si)}; "
      f"Efield={EFIELD} V/A (charges={'on,sum%.2f'%float(_charges.sum()) if _charges is not None else 'off'})")
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
        h,d=log(step); print(f"  t={step*DT/1000:.0f}ps Al_height={h:.2f} Al-slab={d:.2f} A cap={at.calc.ncap} nan={at.calc.nnan}",flush=True); write(f"{label}_traj.xyz",frames)
write(f"{label}_traj.xyz",frames); cv.close(); print(f"# DONE {label}: {len(frames)} frames cap={at.calc.ncap} nan={at.calc.nnan}")
