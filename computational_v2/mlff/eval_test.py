#!/usr/bin/env python3
"""eval_test.py — unbiased force/energy accuracy of the fine-tuned MLFF on the held-out TEST set.

Usage: python eval_test.py <model.model> [test.xyz]
Writes eval_test.json (+ parity_forces.npz) and prints a summary.
"""
import sys, json
import numpy as np
from ase.io import read
from mace.calculators import MACECalculator

model = sys.argv[1]
test = sys.argv[2] if len(sys.argv) > 2 else "mlff_test.xyz"
frames = read(test, ":")
nat = len(frames[0])
calc = MACECalculator(model_paths=[model], device="cuda", default_dtype="float32")

e_dft, e_ml, f_dft, f_ml, sym = [], [], [], [], []
for at in frames:
    e_dft.append(at.get_potential_energy())
    f_dft.append(at.get_forces())
    sym += at.get_chemical_symbols()
    at2 = at.copy(); at2.calc = calc
    e_ml.append(at2.get_potential_energy())
    f_ml.append(at2.get_forces())

e_dft = np.array(e_dft); e_ml = np.array(e_ml)
f_dft = np.concatenate(f_dft); f_ml = np.concatenate(f_ml); sym = np.array(sym)

# energy: fine-tuned model learns the CP2K offset -> raw error meaningful; also report relative
dE = e_ml - e_dft
e_mae_raw = np.abs(dE).mean() / nat * 1000          # meV/atom
e_rmse_rel = np.std(dE) / nat * 1000                # meV/atom, offset-removed
# forces
df = f_ml - f_dft
f_rmse = np.sqrt((df**2).mean()) * 1000             # meV/A (over all components)
f_mae = np.abs(df).mean() * 1000
# per-element force RMSE
per_el = {}
for el in sorted(set(sym)):
    m = sym == el
    per_el[el] = float(np.sqrt((df[m]**2).mean()) * 1000)
# region-resolved force RMSE (slab 0..63 vs electrolyte 64..171), repeated per frame
nfr = len(frames)
region = np.tile(np.where(np.arange(nat) < 64, "slab", "electrolyte"), nfr)
per_region = {r: float(np.sqrt((df[region == r]**2).mean()) * 1000) for r in ("slab", "electrolyte")}
# force-magnitude correlation
fmag_dft = np.linalg.norm(f_dft, axis=1); fmag_ml = np.linalg.norm(f_ml, axis=1)
R = float(np.corrcoef(fmag_dft, fmag_ml)[0, 1])

out = dict(model=model, test=test, n_frames=len(frames), natoms=nat,
           energy_mae_meV_per_atom_raw=float(e_mae_raw),
           energy_rmse_meV_per_atom_rel=float(e_rmse_rel),
           force_rmse_meV_per_A=float(f_rmse), force_mae_meV_per_A=float(f_mae),
           force_R=R, force_rmse_per_element=per_el, force_rmse_per_region=per_region)
json.dump(out, open("eval_test.json", "w"), indent=2)
np.savez("parity_forces.npz", f_dft=f_dft, f_ml=f_ml, e_dft=e_dft, e_ml=e_ml, sym=sym)
print(json.dumps(out, indent=2))
print(f"\nTARGETS: force RMSE <=50-100 meV/A  [{'PASS' if f_rmse<=100 else 'FAIL'}]; "
      f"energy <= few meV/atom (rel) [{'PASS' if e_rmse_rel<=5 else 'CHECK'}]")
