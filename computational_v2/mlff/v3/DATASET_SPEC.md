# DATASET_SPEC — what EPYC must push to unblock the reactive MLFF (T16)
*The GPU node trains/produces the moment these land in `incoming/`. Read with `README_T16_T17.md`.*

## Format (all files: extended-XYZ, one block per frame)
```
<N>
Lattice="ax ay az bx by bz cx cy cz" Properties=species:S:1:pos:R:3:forces:R:3 energy=<eV> pbc="T T T" config_type=<tag>
<El>  x y z  fx fy fz
...
```
- **Units: eV and eV/Å** (ASE/MACE convention). Positions in Å.
- `energy` = **single-point total energy** of THAT geometry (NOT a loose AIMD-trajectory energy — that
  desyncs E from the geometry and corrupts energy training; this was the decisive v2 failure).
- `forces` = single-point forces of that geometry.
- `config_type` tag (used for stratified split + per-type MAE): one of
  `t10_react_bare`, `t10_react_poly`, `t4_alloy`, `t7_sei_<phase>`, `t1_cluster`.
- Elements across the whole set: **{Mg, Al, Cl, O, C, H, Si}** (Si only in poly/SEI).

## Force masking (MANDATORY — gate enforced on our side)
Frames with a **fixed/constrained Mg slab** carry a spurious **+z asymmetric-slab dipole force** on the held
atoms (net ‖ΣF‖ ~70–90 eV/Å, momentum-violating). **Zero the forces on every fixed slab atom** before export
(set fx=fy=fz=0 for the held layers) OR relabel with a symmetric/free slab so ‖ΣF‖<0.1. Mark the masked atoms
by listing their 0-based indices in a sidecar `*_maskidx.json` (`{"masked":[...]}`), OR put them first and
record the count in the comment as `n_slab_masked=<k>`. Our `assemble_dataset.py` re-checks ‖ΣF_electrolyte‖
and asserts the slab ΣF≈0 (`diagnose_forces.py` gate); frames failing the gate are dropped with a report.

## What to push, by ticket (priority order)

### T10 — REACTIVE interface AIMD  ← **CRITICAL PATH, push first**
Mg(0001) slab + the **real cation [Mg₂(μ-Cl)₃(THF)₆]⁺ AND an Al-anion** (dominant [Ph₂AlCl₂]⁻; include some
AlCl₄⁻/AlPhCl₃⁻ if sampled), **bare and poly (network present)**, **constant-potential / ±bias** as available.
- Want the **reactive region densely sampled**: Al-anion approaching the front, Cl/Ph dissociation, Al landing
  on the slab, the cation desolvating. Include the dull bulk-like frames too (baseline), but DO NOT skip the
  rare reactive frames — they are the whole point.
- Target: **≥300–500 frames/system** (bare, poly), single-points (can be every Nth AIMD step, re-evaluated as
  single-points). Replicate trajectories welcome (config_type stays the same).
- File names: `t10_react_bare.xyz`, `t10_react_poly.xyz` (+ `_maskidx.json` if used).

### T4 — Al co-deposition / Mg–Al alloying (periodic)
Al adatom on Mg(0001) (fcc/hcp/bridge/ontop), Al substitution (surface+subsurface), dilute Al-in-Mg, and a
small rattled set around each minimum (±0.1 Å, 5–10 configs each) so the MLFF learns the Al⁰/alloy basin.
`t4_alloy.xyz`. (Mg₁₇Al₁₂ optional — flag if the cell isn't converged.)

### T7 — SEI phases (periodic, + small rattles)
Bulk + slab of **MgO, MgCl₂, SiO₂(α-quartz)+POSS-cage, Al(fcc), Al₂O₃(corundum)**; a representative
THF-decomposition organic fragment. 10–20 rattled configs/phase for curvature. `t7_sei_<phase>.xyz`.
*(No fluorine phases — v3 guardrail.)*

### T1 — molecular clusters (single-points, gas/SMD-geometry, periodic box for MLFF)
The APC anions (AlCl₄⁻, AlPhCl₃⁻, AlPh₂Cl₂⁻, AlPh₃Cl⁻, AlPh₄⁻), neutrals (AlCl₃, AlPh₃), the cation, each with
a few rattled configs. Put each in a large periodic box (≥15 Å vacuum) so the MLFF graph is well-defined.
`t1_cluster.xyz`. (Charged species: note net charge in comment `charge=<q>`; we train neutral-cell energetics,
charged clusters inform local geometry/forces only.)

## Acceptance (our gate, automatic)
`assemble_dataset.py` reports per config_type: frame count, element coverage, energy/force ranges, the E0
least-squares estimate, ‖ΣF_slab‖ (must be ~0 after masking), and ‖ΣF_electrolyte‖ distribution. A run is
"trainable" when T10 (bare+poly) ≥300 frames each pass the gate; T4/T7/T1 strengthen but are not blocking for
a first model. **Reproduce-target:** the trained MLFF must reproduce a held-out T10 frame's Al-approach /
Al-reduction-or-not (validate_reactive.py) — that is the T16 DoD.

## Channel
EPYC pushes to the repo branch `computational-v3-interface` under `computational_v2/mlff/incoming/`
(small files via git; large trajectories via the shared store). Record dataset version (commit hash + date)
in each file's first-frame comment (`dataset_ver=<hash>`). GPU node pulls, assembles, trains, and pushes back
the model + validation + any AL queue.
