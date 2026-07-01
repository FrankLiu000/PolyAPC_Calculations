#!/usr/bin/env python3
"""T16 validation: force/energy MAE+RMSE of the trained MLFF vs held-out DFT
(target force MAE <= 50 meV/Å), per config_type, with parity plots. This is the
T16 DoD; reactive frames (t10_react_*) MAE matters most.

usage: validate_reactive.py <model.model> <test.xyz> [out_prefix] [--device cpu|cuda]
"""
import csv
import sys, numpy as np
from ase.io import read
from mace.calculators import MACECalculator
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

args = list(sys.argv[1:])
device = "cuda"
if "--device" in args:
    idx = args.index("--device")
    device = args[idx + 1]
    del args[idx:idx + 2]
model, test = args[0], args[1]
pref = args[2] if len(args)>2 else "t16_val"
calc = MACECalculator(model_paths=[model], device=device, default_dtype="float32")
ats = read(test, index=":")
rows={}; allF_ref=[]; allF_ml=[]; allE_ref=[]; allE_ml=[]
def get_E(at):
    if "energy" in at.info: return float(at.info["energy"])
    try: return float(at.get_potential_energy())
    except Exception: return np.nan
for at in ats:
    ct = at.info.get("config_type","unknown")
    Fref = at.arrays.get("forces")
    if Fref is None:
        try: Fref = at.get_forces()
        except Exception: Fref = None
    Eref = get_E(at)
    at2 = at.copy(); at2.calc = calc
    Eml = at2.get_potential_energy(); Fml = at2.get_forces()
    r = rows.setdefault(ct, dict(fe=[], ee=[], n=0)); r["n"]+=1
    if Fref is not None:
        r["fe"].append(np.abs(Fml-Fref)); allF_ref.append(Fref.ravel()); allF_ml.append(Fml.ravel())
    if np.isfinite(Eref):
        r["ee"].append((Eml-Eref)/len(at)); allE_ref.append(Eref/len(at)); allE_ml.append(Eml/len(at))

print(f"=== T16 validation: {model} on {test} ({len(ats)} frames), device={device} ===")
print(f"{'config_type':18s} {'n':>4s} {'F_MAE(meV/Å)':>13s} {'F_RMSE':>8s} {'E_MAE(meV/at)':>14s}")
worst=0
csv_rows=[]
for ct,r in sorted(rows.items()):
    fe=np.concatenate(r["fe"]) if r["fe"] else np.array([0.0])
    fmae=fe.mean()*1000; frmse=np.sqrt((fe**2).mean())*1000
    emae=np.mean(np.abs(r["ee"]))*1000 if r["ee"] else float("nan")
    print(f"{ct:18s} {r['n']:4d} {fmae:13.1f} {frmse:8.1f} {emae:14.1f}")
    csv_rows.append({"config_type": ct, "n": r["n"], "force_mae_mev_A": fmae, "force_rmse_mev_A": frmse, "energy_mae_mev_atom": emae})
    if ct.startswith("t10"): worst=max(worst,fmae)
allF_ref=np.concatenate(allF_ref) if allF_ref else np.array([])
allF_ml=np.concatenate(allF_ml) if allF_ml else np.array([])
gmae=np.abs(allF_ml-allF_ref).mean()*1000 if allF_ref.size else float("nan")
print(f"\nGLOBAL force MAE = {gmae:.1f} meV/Å   (target <= 50)   reactive(t10) worst = {worst:.1f}")
print(f"==> {'PASS' if gmae<=50 else 'NEEDS MORE DATA/TRAINING'} (T16 DoD: force MAE <=50 meV/Å)")
# parity
fig,ax=plt.subplots(1,2,figsize=(10,4.3))
if allF_ref.size:
    ax[0].scatter(allF_ref,allF_ml,s=1,alpha=0.3); lim=[allF_ref.min(),allF_ref.max()]
    ax[0].plot(lim,lim,"k--",lw=1); ax[0].set_xlabel("DFT force (eV/Å)"); ax[0].set_ylabel("MLFF force"); ax[0].set_title(f"force parity (MAE {gmae:.0f} meV/Å)")
if allE_ref:
    ax[1].scatter(allE_ref,allE_ml,s=8); lim=[min(allE_ref),max(allE_ref)]
    ax[1].plot(lim,lim,"k--",lw=1); ax[1].set_xlabel("DFT E/atom (eV)"); ax[1].set_ylabel("MLFF E/atom"); ax[1].set_title("energy parity")
plt.tight_layout(); plt.savefig(f"{pref}_parity.png",dpi=150)
print(f"wrote {pref}_parity.png")
with open(f"{pref}_metrics.csv", "w", newline="") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=["config_type", "n", "force_mae_mev_A", "force_rmse_mev_A", "energy_mae_mev_atom"],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(csv_rows)
print(f"wrote {pref}_metrics.csv")
