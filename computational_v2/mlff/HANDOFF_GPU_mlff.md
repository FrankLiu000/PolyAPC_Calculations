# MLFF handoff → LYZ-ROG GPU node (RTX 4070 Ti SUPER 16 GB)

**Sync = git** (FrankLiu000/PolyAPC_Calculations). EPYC produces DFT-labeled data + pushes; this node
fine-tunes + runs MLFF-MD on GPU + pushes models/uncertain-configs back. See `MLFF_PLAN.md` for scope
(MLFF nails coordination/transport/desolvation = the gating mechanism; electron-transfer/reduction stays
DFT — hybrid). Feasibility already shows MACE-MP-0 tracks our PES (R²=0.78) ⇒ **fine-tune, don't train from scratch**.

## Env (one-time, on the GPU box)
```
conda create -n mlff python=3.11 -y && conda activate mlff
pip install torch --index-url https://download.pytorch.org/whl/cu121   # CUDA build (NOT the cpu wheel)
pip install mace-torch ase
python -c "import torch; print(torch.cuda.is_available())"   # must be True
```

## Step 1 — pull the DFT-labeled training set
EPYC writes `mlff/dataset_train.xyz` (extended-XYZ: positions + `energy` + `forces`, eV / eV·Å⁻¹,
DFT = PBE-D3/DZVP-MOLOPT-SR-GTH, the AIMD level) once the force-labeling pass (Phase 1) runs.
```
git pull            # fetch mlff/dataset_train.xyz
```
(Until that exists, only the energy-only `dataset_scaffold*.xyz` are present — NOT trainable; forces required.)

## Step 2 — fine-tune MACE-MP-0 on GPU
```
mace_run_train \
  --name=apc_mlff --foundation_model=medium \
  --train_file=mlff/dataset_train.xyz --valid_fraction=0.10 \
  --energy_key=energy --forces_key=forces --E0s=foundation \
  --loss=weighted --energy_weight=1 --forces_weight=100 \
  --r_max=5.0 --batch_size=4 --max_num_epochs=300 --swa --device=cuda --default_dtype=float64
```
Targets: **force RMSE ≲ 50–100 meV/Å, energy ≲ few meV/atom** on the held-out 10 %.
Physical cross-checks (must reproduce): AIMD Mg–μCl ~2.5 Å / 6-coord cation; classical-MD de-pairing
& CIP↔SSIP PMF trends; molecular-DFT energetics. If forces are poor near the surface, that's the
extrapolation gap → Step 4.

## Step 3 — MLFF-MD production (GPU)
Run with ASE (`mace.calculators.MACECalculator`, md via ASE/i-PI) or export to LAMMPS (`mace` pair_style).
Enhanced sampling for the payoff: **metadynamics / umbrella on (Mg²⁺–surface z, first-shell coordination
number)** → desolvation free-energy profile + rate, **bare vs poly**, large cell + replicates. Hybrid for
the reduction step: hand near-surface desolvated snapshots back to EPYC for short CHARGE−2/AIMD (the actual e⁻ transfer).

## Step 4 — active learning (close the loop)
Train a small **committee** (3–5 seeds). During MLFF-MD, flag frames with high force-disagreement
(σ_F > ~150 meV/Å) → write `mlff/al_queue.xyz`, push to git. EPYC DFT-labels them (`bin/label_forces.sh`),
appends to `dataset_train.xyz`, pushes back; re-fine-tune. Iterate until the desolvation/near-surface
pathway is covered (committee σ stays low along the production CV).

## Notes
- 16 GB GPU is ample for ~300-atom cells / MACE-medium. Use `--batch_size` ↓ if OOM.
- Keep DFT level identical to EPYC labeling (don't mix references).
- Report force/energy RMSE + the cross-checks in `mlff/TRAIN_REPORT.md` and push.
