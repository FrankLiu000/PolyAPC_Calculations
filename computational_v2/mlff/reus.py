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
import sys, os, glob, re, time
import numpy as np
from ase.io import read, write
from ase import units
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.constraints import FixAtoms
from ase.calculators.calculator import Calculator, all_changes
from mace.calculators import MACECalculator

model, init = sys.argv[1], sys.argv[2]
K, TAU, NCYC, WD = float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
Z0 = [float(x) for x in sys.argv[7:]]
DT = float(os.environ.get("REUS_DT_FS", "1.0"))
T_K = 300.0
LOG_FS = float(os.environ.get("REUS_LOG_FS", "20"))
LOG_STEPS = max(1, int(round(LOG_FS / DT)))
N_LOGS = int(round(TAU / LOG_FS))
if abs(LOG_STEPS * DT - LOG_FS) > 1e-9 or abs(N_LOGS * LOG_FS - TAU) > 1e-9:
    raise SystemExit(f"REUS_DT_FS={DT} and REUS_LOG_FS={LOG_FS} must divide tau={TAU} fs exactly")
kT = units.kB * T_K
FCAP = float(os.environ.get("REUS_FCAP", "60"))
MAX_ABS_CV = float(os.environ.get("REUS_MAX_ABS_CV", "25"))
MAX_FMAX = float(os.environ.get("REUS_MAX_FMAX", "200"))
os.makedirs(WD, exist_ok=True)
STATE = f"{WD}/reus_state.txt"
RUNNING = f"{WD}/reus_running.txt"
ABORT = f"{WD}/reus_abort.txt"

class ForceCap(Calculator):
    """Clip spurious MLFF force spikes before they run the REUS integrator away."""
    implemented_properties = ["energy", "forces", "free_energy"]

    def __init__(self, base, fmax=60.0):
        Calculator.__init__(self)
        self.base = base
        self.fmax = fmax
        self.ncap = 0
        self.nnan = 0

    def calculate(self, atoms=None, properties=("energy", "forces"), system_changes=all_changes):
        Calculator.calculate(self, atoms, properties, system_changes)
        a = atoms.copy()
        a.calc = self.base
        e = a.get_potential_energy()
        f = np.array(a.get_forces(), dtype=float)
        if not np.isfinite(f).all():
            self.nnan += 1
            f = np.nan_to_num(f, nan=0.0, posinf=self.fmax, neginf=-self.fmax)
        n = np.linalg.norm(f, axis=1)
        m = n > self.fmax
        if m.any():
            self.ncap += 1
            f[m] *= (self.fmax / n[m])[:, None]
        self.results = {"energy": float(e), "forces": f, "free_energy": float(e)}

calc = ForceCap(MACECalculator(model_paths=[model], device="cuda", default_dtype="float32"), fmax=FCAP)

def last_step(dat):
    """Last written MD step in a window .dat file."""
    if not os.path.exists(dat):
        return 0
    last = 0
    with open(dat) as fh:
        for line in fh:
            if line[:1].isdigit():
                last = int(float(line.split()[0]))
    return last

def truncate_dat(dat, keep_step):
    """Drop partially written rows beyond the last completed global cycle."""
    if not os.path.exists(dat):
        return
    with open(dat) as fh:
        lines = fh.readlines()
    kept = []
    for line in lines:
        if not line[:1].isdigit():
            kept.append(line)
            continue
        if int(float(line.split()[0])) <= keep_step:
            kept.append(line)
    with open(dat, "w") as fh:
        fh.writelines(kept)

def completed_state_step():
    if os.path.exists(STATE):
        try:
            with open(STATE) as fh:
                return int(float(fh.read().strip().split()[0]))
        except Exception:
            pass
    return None

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
print(
    f"# REUS {len(Z0)} windows k={K} tau={TAU}fs ncyc={NCYC} dt={DT:g}fs "
    f"log={LOG_FS:g}fs fcap={FCAP:g} zref={z_ref:.2f} cat_mg={cat_mg.tolist()}",
    flush=True,
)

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

def sanity_or_abort(cyc, window_i, step_fs, z0, cvv, fmax):
    bad = (
        (not np.isfinite(cvv))
        or (not np.isfinite(fmax))
        or abs(cvv) > MAX_ABS_CV
        or fmax > MAX_FMAX
    )
    if bad:
        msg = (
            f"{time.strftime('%F %T')} abort cycle={cyc} window_index={window_i} "
            f"step={step_fs} z0={z0} cv={cvv:.6g} fmax={fmax:.6g} "
            f"limits_abs_cv={MAX_ABS_CV} limits_fmax={MAX_FMAX}"
        )
        with open(ABORT, "w") as fh:
            fh.write(msg + "\n")
        raise RuntimeError(msg)

# build replicas (RESUMABLE: window_z<z0>_chk.xyz = checkpoint config; appends to .dat on resume)
reps, dyns, files, rsteps = [], [], [], []
dat_paths = [f"{WD}/window_z{z0}.dat" for z0 in Z0]
dat_steps = [last_step(p) for p in dat_paths]
state_step = completed_state_step()
resume_step = state_step if state_step is not None else (min(dat_steps) if dat_steps else 0)
resume_step = (resume_step // TAU) * TAU
if any(s != resume_step for s in dat_steps):
    print(f"# RESUME_TRUNCATE target_step={resume_step} dat_steps={dat_steps}", flush=True)
    for dat in dat_paths:
        truncate_dat(dat, resume_step)
for z0 in Z0:
    chk, dat = f"{WD}/window_z{z0}_chk.xyz", f"{WD}/window_z{z0}.dat"
    if os.path.exists(chk):                                    # RESUME this window
        at = read(chk); last = last_step(dat)
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
        with open(RUNNING, "w") as fh:
            fh.write(f"{time.strftime('%F %T')} cycle={cyc} step={step} window_index={i} z0={Z0[i]}\n")
        for _ in range(N_LOGS):
            dyns[i].run(LOG_STEPS)
            at = reps[i]; cvv = cv_of(at)
            fmax = np.linalg.norm(at.get_forces()[64:], axis=1).max()
            row_step = int(round(step + (_ + 1) * LOG_FS))
            sanity_or_abort(cyc, i, row_step, Z0[i], cvv, fmax)
            files[i].write(f"{row_step} {cvv:.4f} {cn(at,cat_mg,O,2.6)} {cn(at,cat_mg,cl,2.9)} "
                           f"{at.get_distance(int(cat_mg[0]),int(cat_mg[1]),mic=True):.3f} {fmax:.3f}\n")
            files[i].flush()
        files[i].flush()
        write(f"{WD}/window_z{Z0[i]}_chk.xyz", reps[i])
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
    with open(f"{STATE}.tmp", "w") as fh:
        fh.write(f"{step}\n")
    os.replace(f"{STATE}.tmp", STATE)
    print(
        f"  cyc {cyc+1}/{NCYC} step {step} fs  exch_acc={n_acc}/{n_try} "
        f"({100*n_acc/max(n_try,1):.0f}%) cap={calc.ncap} nan={calc.nnan}",
        flush=True,
    )
for f in files: f.close()
print(f"# REUS_DONE acc={n_acc}/{n_try} ({100*n_acc/max(n_try,1):.0f}%) cap={calc.ncap} nan={calc.nnan}", flush=True)
