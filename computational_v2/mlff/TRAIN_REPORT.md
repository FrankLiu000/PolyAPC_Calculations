# MLFF Round-1 — training report & critical data-quality finding (LYZ-ROG GPU node)

**Date:** 2026-06-16. **Node:** LYZ-ROG (RTX 4070 Ti SUPER 16 GB, 24 CPU). **Stack:** mace-torch 0.3.16,
torch 2.6.0+cu124, ASE 3.28, venv `/lyz/Claude_workplace/polyAPC/.mlff_venv` (no conda on this box).
**Input:** `mlff/dataset_train.xyz` (528 bare-interface frames, 172 atoms: 64-atom Mg(0001) slab + one
[Mg₂(μ-Cl)₃·6THF]⁺/[Ph₂AlCl₂]⁻ ion pair) pushed by the EPYC node per `HANDOFF_GPU_mlff.md`.

## TL;DR
The full GPU MLFF pipeline (env, fine-tuning, eval, MLFF-MD, analysis, figures) is built and working.
**But Round-1 cannot train a valid force field as delivered: the force labels on the 64 Mg-slab atoms are
corrupt** (they carry a spurious net force ΣF ≈ 71 eV/Å — momentum non-conserving — and are uncorrelated
with the true PES, R = 0.10 vs the PBE foundation). **The electrolyte force labels (atoms 64–171) are clean**
(R = 0.886). Because a MACE model is a *conservative* field (F = −∂E/∂r), the unfittable slab forces floor
the force error at ≈ 1.05 eV/Å regardless of any hyperparameter. **Action: regenerate slab forces on the
EPYC side (§4).** A proof-of-concept electrolyte potential trained on the clean part is reported in §3.

## 1. Pipeline & environment (reusable)
- `run_train.sh` (fine-tune MACE-MP-0 medium), `prep_split.py` (held-out test split), `eval_test.py`
  (held-out RMSE), `select_md_start.py` (clean intact-anion start frame), `run_md.py` (NVT MLFF-MD with the
  bottom slab fixed), `run_validation.sh` (chains eval→MD→AIMD-matched analysis→figure), `fig_mlff.py`.
- Memory: the dense Mg metal slab (each slab Mg has ~12+ neighbours within MACE-MP's r_max=6 Å) makes a
  huge message-passing graph that pinned the 16 GB GPU. Fixed with `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`
  (16 GB → 3–6 GB) + batch 4. Disabled MACE's default multihead replay (10k Materials-Project configs —
  pointless for a single-system potential, diluted our signal ~20×). `E0s=average` absorbs the
  CP2K-GTH↔MACE-MP ~700 eV/atom reference offset (energy then fits to ~0.03 meV/atom).

## 2. The data-quality finding (why no MLFF would train)
**Symptom.** Energy fits to ~0.03 meV/atom, but force RMSE is stuck at ≈ 1.05 eV/Å — *identical* under
float32/float64, lr 0.001–0.04, weighted/Huber loss, and even **force-only** training (energy_weight=0,
so energy can't be the cause) and even on the **training** set (model can't memorise the forces). That is
the signature of force labels that are not a function of the geometry.

**Localisation (physics-based, foundation-independent).**

| quantity | slab Mg (atoms 0–63) | electrolyte (atoms 64–171) |
|---|---|---|
| ‖ΣF‖ per frame (must be ~0) | **70.7 eV/Å** (all of it) | 2.6 eV/Å (≈physical) |
| R(label, MACE-MP-0 force) | **+0.10** (uncorrelated) | **+0.886** (clean) |

All 528 frames violate ΣF=0 (mean 70.7, range 21–184; **0/528 below 1**). The defect is **entirely on the
Mg slab**; the electrolyte forces (the cation/anion/THF chemistry the MLFF actually needs) are correct.
Enforcing ΣF=0 by removing the net force does **not** rescue training (1073 → 1045) → the slab forces are
wrong per-atom, not merely a uniform offset.

**Likely cause.** The bottom slab layers were held fixed in the source AIMD; the force-labeling single-point
most plausibly mishandled the slab (constraint/fixed-atom forces, a frozen region, or a slab-specific
parsing error in the `&PRINT &FORCES` harvest). The energies in `dataset_train.xyz` are also the *AIMD-trajectory*
energies (smeared, loose SCF — "never cite for energetics" per `HANDOFF_v3 §3`), not single-point energies;
they are self-consistently fittable but should be replaced by the single-point energies for a clean E/F pair.

## 3. Proof-of-concept electrolyte potential (slab forces masked)
Because the slab is held fixed during MLFF-MD, its forces never drive dynamics. Zeroing the slab force
labels (`f[:64]=0`, `dataset_train_elec.xyz`) and training **force-only** on the clean electrolyte forces
yields a valid interface potential (the slab→electrolyte interaction lives in the *electrolyte* atoms'
physical force labels, so that physics is retained). This is a workaround pending §4, scoped to forces/MD
only (energies untrained → not for energetics).

**Result:** force RMSE drops from the stuck **~1045 meV/Å** (buggy, full data) to **~143 meV/Å** within a
few epochs — a ~7× improvement and direct confirmation that the electrolyte forces are clean and fittable
and the slab labels were the entire blocker. (Overall RMSE is electrolyte-dominated since the slab targets
are ~0; electrolyte-only RMSE ≈ 180 meV/Å.) Final held-out numbers + a stable fixed-slab MLFF-MD demo:
`[[follow-up commit]]`. Config: `E0s=average`, multihead off, float32+`expandable_segments`, batch 4,
weighted loss, `energy_weight=0`.

## 4. Recommended fix (EPYC force-labeling pipeline)
1. Re-run the force-labeling single-points with **no fixed/constrained atoms** (compute true Hellmann-Feynman+Pulay
   forces on all atoms), or verify the `&PRINT &FORCES` parse handles the slab region.
2. **Assert ‖ΣF‖ < ~0.1 eV/Å per frame** when writing the dataset (a one-line guard that would have caught this).
3. Write the **single-point energy** (not the AIMD energy) so E and F are a consistent pair.
4. Re-push `dataset_train.xyz`; the GPU pipeline here will fine-tune + validate unchanged.
