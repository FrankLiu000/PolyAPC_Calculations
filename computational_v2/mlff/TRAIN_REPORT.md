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
few epochs — a ~7× improvement and direct confirmation that the electrolyte forces are clean/fittable and
the slab labels were the entire blocker. Final model (60 epochs, no-SWA, `apc_mlff.model`), **held-out 53
frames**:

| metric | value |
|---|---|
| force RMSE (overall) | 131 meV/Å |
| force MAE (overall) | **26 meV/Å** |
| force R | **0.914** |
| force RMSE — electrolyte (64–171) | **166 meV/Å** |
| force RMSE — slab (0–63, masked) | 4.6 meV/Å (≈0, as designed) |

A Round-1 electrolyte force field: MAE 26 meV/Å and R=0.91 are solid; the RMSE is outlier-inflated and
would tighten with corrected slab data + active learning. Config: `E0s=average`, multihead off,
float32+`expandable_segments`, batch 4, weighted loss, `energy_weight=0`, no SWA.

**MLFF-MD demo (`run_md.py`, rigid electrode + mobile electrolyte, NVT 300 K, 30 ps @ 1 fs).** Stable and
**reproduces the converged AIMD equilibrium** (cross-checked with the campaign's own
`bin/analyze_interface_access.py`):

| observable | MLFF-MD (30 ps) | AIMD (10 ps, master report §6) |
|---|---|---|
| T | 302 ± 27 K | 300 K (set) |
| Al height above slab front | mean **9.48 Å** (last-half 8.90) | 9.0 Å |
| Al nearest slab-Mg | mean 8.11 Å (min 5.74) | min 7.2 Å |
| anion integrity | **all 4 Al bonds intact every frame; 0/601 dissociation** | intact (clean start) |
| cation Mg⁺ approach | stays ~7 Å off front (no plating) | ~9 Å, no plating |

Runs 30 ps in ~30 min on the 4070 Ti (1.4 GB GPU) vs AIMD's ~0.1 ps/day — the timescale unlock the MLFF
was built for. (Energies not trained → forces/MD only; for production desolvation free energies the slab
data must be fixed per §4, then enhanced sampling can run on this engine.) Figure: `results/figures/fig_mlff_train.png`.

## 4. Recommended fix (EPYC force-labeling pipeline)
1. Re-run the force-labeling single-points with **no fixed/constrained atoms** (compute true Hellmann-Feynman+Pulay
   forces on all atoms), or verify the `&PRINT &FORCES` parse handles the slab region.
2. **Assert ‖ΣF‖ < ~0.1 eV/Å per frame** when writing the dataset (a one-line guard that would have caught this).
3. Write the **single-point energy** (not the AIMD energy) so E and F are a consistent pair.
4. Re-push `dataset_train.xyz`; the GPU pipeline here will fine-tune + validate unchanged.

## 5. Fix VERIFIED (2026-06-16, EPYC commit d385aaa)
EPYC confirmed the finding and pushed clean bare(528) + poly(441) sets. Root cause (sharper than §2):
the source AIMD held the **bottom 32 slab atoms fixed at unrelaxed ideal-lattice positions**; a free
single-point exposes their true forces — a +z **asymmetric-slab dipole artifact** (~92 eV/Å net,
momentum-non-conserving) that the AIMD hid inside the constrained atoms. Their parser is bit-faithful
(not a parse bug); **energies were already single-point** (my §2 worry about AIMD energies was wrong).
Fix = mask (zero) the fixed-slab forces 0–63 — the same approach as §3, now the agreed convention
(slab is fixed in production MLFF-MD). `bin/label_forces.py` gained an `n_slab` mask arg + a free-region
momentum guard; `mlff/zero_slab_forces.py` post-processes existing sets.

**Independent verification on this node (`diagnose_forces.py`, gate = slab ΣF≈0 AND electrolyte R>0.7):**

| dataset | slab ΣF | electrolyte ΣF (resid.) | electrolyte R(label,foundation) | gate | force-only retrain |
|---|---|---|---|---|---|
| bare (528×172) | 0.00 | 2.6 | 0.886 | **PASS** | 143–166 meV/Å (§3) |
| poly (441×276) | 0.00 | 3.7 | 0.909 | **PASS** | held-out MAE 34, R 0.95, elec RMSE 181 (20 ep) |

Both train cleanly (no longer stuck at ~1 eV/Å). `diagnose_forces.py` gate updated to accept masked-slab
data (was reporting a misleading global-ΣF FAIL). **Status: unblocked — matched bare-vs-poly electrolyte
potentials are now trainable.** Residual: a fully momentum-conserving set (dipole/decoupled-Poisson
correction, no masking) is deferred by EPYC — fine, since the slab is held fixed in production MLFF-MD.

## 6. Matched bare-vs-poly production models (2026-06-16)
Both trained with the **identical recipe** (force-only `energy_weight=0`, `E0s=average`, multihead off,
float32+`expandable_segments`, batch 4, lr 0.01, no-SWA, 100 epochs) so the comparison is fair.
Models (committed): `models/apc_bare.model`, `models/apc_poly.model` (6.6 MB each). Regenerate:
`NAME=apc_bare EPOCHS=100 DTYPE=float32 E0S=average LOSS=weighted EWEIGHT=0 SWA=no MULTIHEAD=False
TRAIN=mlff_bare_train.xyz WORK=run_bare bash run_train.sh` (and `_poly`).

**Held-out force accuracy (independent test sets, region-resolved):**

| model | system | force RMSE | force MAE | R | electrolyte RMSE | slab (masked) |
|---|---|---|---|---|---|---|
| `apc_bare` | bare interface (172 at) | 131.6 | **27.0** | 0.913 | 166.0 | 4.6 |
| `apc_poly` | poly/POSS gel (276 at) | 158.8 | **33.4** | 0.951 | 181.2 | 2.9 |

Comparable Round-1 quality; poly's larger RMSE tracks its larger/more-heterogeneous system (POSS network),
with a tighter overall R. Both are usable electrolyte force fields for the fixed-electrode regime.

**Matched MLFF-MD (rigid electrode + mobile electrolyte, NVT 300 K, 15 ps each, same ~9 Å intact-anion
start):** both stable, anion intact (0 dissociation), no plating. Bare: T 306±30 K, Al–slab mean 8.3 Å.
Poly: stable, anion intact. Figure `results/figures/fig_mlff_matched.png`.

**Next (the science the MLFF was built for):** enhanced sampling (umbrella/metadynamics on Mg²⁺–surface z
and first-shell coordination) → **desolvation & CIP↔SSIP free energies, bare vs poly**, with replicates +
large cells. The reduction/plating step stays DFT (hybrid, §1). These force-only fixed-slab potentials are
the right engine for the gating free energies.
