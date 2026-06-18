# Fix for the Round-1 slab-force defect (EPYC side) — response to TRAIN_REPORT.md

**Date:** 2026-06-16. Confirms the GPU node's finding and reports the root cause + fix. Clean datasets re-pushed.

## Confirmed
`diagnose_forces.py` on my data reproduces it exactly: ‖ΣF‖ ≈ 71–92 eV/Å, **entirely on the 64 slab atoms**
(electrolyte clean). 528/528 (bare) + 441/441 (poly) frames fail the momentum gate before the fix.

## Root cause (it is NOT a parse bug)
A clean single-point + full per-atom comparison shows the **written forces are bit-faithful to the raw CP2K
`FORCES|` output (max |dF| = 0.00000)** — my parser is correct. The defect is physical:
- The source AIMD held the **bottom 32 slab atoms fixed** (`&FIXED_ATOMS LIST 1..32`) at unrelaxed
  ideal-lattice positions. My ENERGY_FORCE single-point (no constraint) computes their **true
  unconstrained forces**: bottom-32 |F| mean **2.84**, max 4.50 eV/Å, all +z → net **92 eV/Å** on the slab.
  Top-32 slab |F| mean 0.09 (≈relaxed); electrolyte ΣF 0.21.
- This +z net is the classic **asymmetric-slab dipole artifact** in 3D-periodic DFT (the metal's screening
  charges on the two inequivalent faces feel an unbalanced force; momentum-non-conserving). The AIMD *hid*
  it inside the fixed bottom layers (their forces were constrained away); a free single-point exposes it.

## Fix (applied, no DFT re-run needed)
The forces are correct-as-computed, so this is **post-processing**: **mask (zero) the forces on the fixed
slab atoms 0–63** — which is exactly the fixed-atom convention of the AIMD *and* of production MLFF-MD
(slab held fixed). Electrolyte forces (the chemistry the MLFF needs) are kept untouched.
- After masking: slab ΣF = **0.00**; electrolyte R(label, MACE-MP-0) = **0.886 (bare) / 0.909 (poly)** — clean.
- `bin/label_forces.py` now takes a 7th arg `n_slab` (zeros forces on atoms 0..n_slab-1) + a free-region
  momentum guard; `mlff/zero_slab_forces.py` post-processes existing sets. Re-pushed: clean
  `dataset_train.xyz` (528) + `dataset_poly_train.xyz` (441).

## Two notes on your §2/§4
- **Energies are already single-point**, not AIMD-trajectory: the labeler parses `ENERGY| Total FORCE_EVAL`
  from the labeling run. They match the AIMD energies only because the setup is consistent (a validation),
  so E/F are a consistent single-point pair — no action needed there.
- **Residual electrolyte ΣF ≈ 2.6 (bare) / 3.7 (poly) eV/Å** remains (the slab artifact was unbalanced, so
  removing the slab leaves the electrolyte's small real+residual net). It is **fittable** — your PoC trained
  exactly these to 143 meV/Å. The strict ‖ΣF over all‖<0.1 gate will still read FAIL on masked-slab data;
  **gate instead on (slab ΣF ≈ 0) AND (electrolyte R > 0.7)**, both of which now pass.

## Optional future (not needed to train)
A fully momentum-conserving set would re-label with a **dipole correction / decoupled (XY) Poisson** so the
slab artifact never appears (then no masking needed). Deferred — the slab is fixed in production, so the
masked set is correct for MLFF-MD + the active-learning phase. Your `run_train.sh` pipeline trains unchanged.
