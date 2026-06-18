#!/usr/bin/env python3
"""reus.py — Hamiltonian replica-exchange umbrella sampling (serial, 1 GPU) for the desolvation PMF.

Fixes the slow-mode (solvation-shell reorg) non-convergence of plain umbrella sampling: N windows
(harmonic bias on cation-Mg COM z-height, rigid slab) run in a round-robin on the single GPU; every
`tau` fs we attempt config swaps between neighbouring windows (Metropolis on the bias energies),
which lets a window stuck in one shell state migrate to where it relaxes -> mixes the slow mode.
Writes window_z<z0>.dat per window (umbrella.py-compatible -> feed to wham.py). Records exchange rate.

Usage: reus.py <model> <init_label|start.xyz> <k> <tau_fs> <ncycles> <out_dir> <z0_1 z0_2 ...>
  init_label: reuse umb_<init_label>/window_z<z0>_last.xyz as per-window starts (else a single start.xyz).
"""
import sys, os, glob, re
import numpy as np
from ase.io import read, write
from ase import units
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.constraints import FixAtoms
from mace.calculators import MACECalculator

model, init = sys.argv[1], sys.argv[2]
K, TAU, NCYC, WD = float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
Z0 = [float(x) for x in sys.argv[7:]]
DT, T_K, LOG = 1.0, 300.0, 20
kT = units.kB * T_K
os.makedirs(WD, exist_ok=True)
calc = MACECalculator(model_paths=[model], device="cuda", default_dtype="float32")

# per-window start = NEAREST available umb_<init>/window_z*_last.xyz (else init treated as a start.xyz path)
_cands = glob.glob(f"umb_{init}/window_z*_last.xyz")
_czs = [(float(re.search(r'window_z([0-9.]+)_last', c).group(1)), c) for c in _cands]
def first_start(z0):
    if _czs:
        return min(_czs, key=lambda zc: abs(zc[0] - z0))[1]
    return init
at0 = read(first_start(Z0[0]))
sym = np.array(at0.get_chemical_symbols()); pos = at0.get_positions()
i_Al = int(np.where(sym == "Al")[0][0]); cl = np.where(sym == "Cl")[0]; mg = np.where(sym == "Mg")[0]
anion_cl = cl[np.argsort([at0.get_distance(i_Al, int(c), mic=True) for c in cl])[:2]]
cat_cl = np.array([c for c in cl if c not in anion_cl])
cat_mg = mg[np.argsort([min(at0.get_distance(int(m), int(c), mic=True) for c in cat_cl) for m in mg])[:2]]
slab = np.array([m for m in mg if m not in cat_mg]); O = np.where(sym == "O")[0]
z_ref = float(np.sort(pos[slab, 2])[-16:].mean())
print(f"# REUS {len(Z0)} windows k={K} tau={TAU}fs ncyc={NCYC} zref={z_ref:.2f} cat_mg={cat_mg.tolist()}", flush=True)

class UmbrellaZ:
    def __init__(s, idx, z0, k, zr): s.idx, s.z0, s.k, s.zr = np.asarray(idx), z0, k, zr
    def _cv(s, a): return a.get_positions()[s.idx, 2].mean() - s.zr
    def adjust_positions(s, a, n): pass
    def adjust_forces(s, a, f): f[s.idx, 2] += -s.k * (s._cv(a) - s.z0) / len(s.idx)
    def adjust_potential_energy(s, a): return 0.5 * s.k * (s._cv(a) - s.z0) ** 2
    def get_removed_dof(s, a): return 0

def cv_of(at): return at.get_positions()[cat_mg, 2].mean() - z_ref
def cn(at, cs, others, rc):
    return sum(int((np.array([at.get_distance(int(c), int(o), mic=True) for o in others]) < rc).sum()) for c in cs)

# build replicas (RESUMABLE: window_z<z0>_chk.xyz = checkpoint config; appends to .dat on resume)
reps, dyns, files, rsteps = [], [], [], []
for z0 in Z0:
    chk, dat = f"{WD}/window_z{z0}_chk.xyz", f"{WD}/window_z{z0}.dat"
    if os.path.exists(chk):                                    # RESUME this window
        at = read(chk); last = 0
        if os.path.exists(dat):
            for L in open(dat):
                if L[:1].isdigit(): last = int(L.split()[0])
        rsteps.append(last); f = open(dat, "a")
    else:                                                      # fresh
        at = read(first_start(z0)); rsteps.append(0); f = open(dat, "w")
        f.write(f"# z0={z0} k={K} kT={kT:.6f} zref={z_ref:.3f} cat_mg={cat_mg.tolist()}\n# step cv mgO mgCl mgmg fmax\n")
    at.calc = calc
    at.set_constraint([FixAtoms(indices=slab.tolist()), UmbrellaZ(cat_mg, z0, K, z_ref)])
    MaxwellBoltzmannDistribution(at, temperature_K=T_K)
    reps.append(at); dyns.append(Langevin(at, DT * units.fs, temperature_K=T_K, friction=0.02)); files.append(f)

start_cyc = min(rsteps) // TAU
step = start_cyc * TAU; n_acc = 0; n_try = 0
if start_cyc: print(f"# RESUMING from cycle {start_cyc} (step {step} fs)", flush=True)
for cyc in range(start_cyc, NCYC):
    for i in range(len(Z0)):                                   # advance every window by tau (round-robin)
        for _ in range(TAU // LOG):
            dyns[i].run(LOG)
            at = reps[i]; cvv = cv_of(at)
            fmax = np.linalg.norm(at.get_forces()[64:], axis=1).max()
            files[i].write(f"{step+(_+1)*LOG} {cvv:.4f} {cn(at,cat_mg,O,2.6)} {cn(at,cat_mg,cl,2.9)} "
                           f"{at.get_distance(int(cat_mg[0]),int(cat_mg[1]),mic=True):.3f} {fmax:.3f}\n")
        files[i].flush()
    step += TAU
    # neighbour exchanges (alternate even/odd pairs)
    for i in range(cyc % 2, len(Z0) - 1, 2):
        ci, cj = cv_of(reps[i]), cv_of(reps[i + 1]); zi, zj = Z0[i], Z0[i + 1]
        d = 0.5 * K * ((ci - zj) ** 2 + (cj - zi) ** 2 - (ci - zi) ** 2 - (cj - zj) ** 2)
        n_try += 1
        if d <= 0 or np.random.random() < np.exp(-d / kT):     # swap configs (pos+vel)
            pi, vi = reps[i].get_positions().copy(), reps[i].get_velocities().copy()
            reps[i].set_positions(reps[i + 1].get_positions()); reps[i].set_velocities(reps[i + 1].get_velocities())
            reps[i + 1].set_positions(pi); reps[i + 1].set_velocities(vi); n_acc += 1
    for i, z0 in enumerate(Z0):                                # checkpoint configs (reboot-resumable)
        write(f"{WD}/window_z{z0}_chk.xyz", reps[i])
    if cyc % 10 == 0:
        print(f"  cyc {cyc}/{NCYC} step {step} fs  exch_acc={n_acc}/{n_try} ({100*n_acc/max(n_try,1):.0f}%)", flush=True)
for f in files: f.close()
print(f"# REUS_DONE acc={n_acc}/{n_try} ({100*n_acc/max(n_try,1):.0f}%)", flush=True)
