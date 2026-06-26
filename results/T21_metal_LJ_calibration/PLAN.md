# T21 — DFT-anchored LJ calibration: Mg metal ↔ APC electrolyte (for classical MD)

**Goal:** parameters to bring the Mg(0001)|APC-electrolyte interface into the GROMACS classical MD
(currently bulk-only). Scope (PI): **full DFT-anchored calibration, relaxable slab.** All DFT = CP2K
PBE-D3, GTH-PBE-q10, consistent with the AIMD (T10). Working dir `/CH/poly_v2/ljcal/`.

## Validation targets (from AIMD/MLFF T5/T17)
| contact | target |
|---|---|
| bridging Cl⁻ → nearest slab-Mg (min) | ~3.90 Å |
| reducible Al (anion) → electrode | 4.58 ± 0.19 Å |
| cation Mg⁺ → nearest slab-Mg | 5.64 Å |

## Phase A — Mg–Mg metal LJ (relaxable slab) → fit 12-6 ε,σ
DFT references (running):
- **Bulk hcp EOS** (5 isotropic volumes, MP 6×6×4) → a0, c0, V0, bulk modulus B, E_bulk/atom.
- **Isolated Mg atom** (Γ, big box) → cohesive energy E_coh = E_atom − E_bulk/atom.
- **(0001) slab** (3×3×4, 36 Mg, MP 3×3×1) → surface energy γ = (E_slab − N·E_bulk/atom)/(2A).
Fit 12-6 LJ (Mg_m–Mg_m) to {a0/NN-distance, E_coh or γ, B} — INTERFACE-FF style. **Caveat:** a single
12-6 LJ cannot match c/a + elastic + surface simultaneously for hcp; EAM-in-LAMMPS is the higher-fidelity
route for a truly relaxable metal — flagged, LJ delivered as requested.

## Phase B — Mg_m ↔ electrolyte cross-LJ → fit + NBFIX
DFT E_int(z) = E(slab+X) − E(slab) − E(X), rigid z-scan (~5–6 pts) on the frozen Mg(0001) slab for:
- **Cl⁻** (anion standoff — primary), **THF via O** (solvent contact), **Mg²⁺** (cation height).
Fit Mg_m ε,σ (comb-rule 3 / geometric) to each well-depth + r_min; use `[ nonbond_params ]` **NBFIX**
for Mg_m–Cl and Mg_m–O where geometric mixing fails. Keep OPLS electrolyte + scaled charges
(Mg +1.2 / Cl −0.467) fixed.

## Validate + deliver
Run GROMACS slab+electrolyte MD → reproduce 3.90 / 4.58 / 5.64 Å + interfacial RDF. Deliver:
`mg_metal.itp` (atomtype + LJ), NBFIX block, fit report (DFT refs, fitted params, validation), and the
honest non-polarizable/image-charge caveat (constant-potential electrode = follow-up).

## ★ SCOPE LOCKED — FREE SLAB (PI, 2026-06-26)
PI: **free (relaxable) slab**, and the GPU rebuilds the sym-interface accordingly (replacing its current
UFF + POSRES k=50000 wall). So **both phases are needed and compose cleanly:**
- **Phase A (Mg–Mg metal LJ) — PRIMARY:** sets `Mg_m` σ/ε so the free slab is cohesive + relaxes realistically
  (fit to bulk a/c, cohesive energy, (0001) surface energy). Anchor only the **bottom 1–2 layers** (weak POSRES)
  to hold slab position / mimic bulk; top surface FREE (the AIMD convention). Deliver FIRST so the GPU can rebuild.
- **Phase B (Mg_m–electrolyte cross-LJ):** the same `Mg_m` σ/ε generates the cross terms via comb-rule 3; add
  **NBFIX** for Mg_m–Cl & Mg_m–O to match the DFT E_int(z) standoff (NBFIX overrides ONLY the cross pair, leaving
  Mg–Mg untouched). Validate vs 3.90/4.58/5.64 Å.
- **Honest caveat (free hcp metal):** a 12-6 LJ can't match c/a + elastic anisotropy + surface energy
  simultaneously — the free LJ slab relaxes/vibrates realistically but is energetically approximate. **EAM
  (LAMMPS) is the higher-fidelity route for a free metal**; 12-6 LJ delivered because the production MD is GROMACS.
- **Why it matters:** the GPU's UFF-wall run gives anion **enrichment** vs the MLFF/AIMD **depletion/standoff**;
  the calibrated free-slab wall tests whether enrichment→depletion (reconciling the models).

## Status — DONE (2026-06-27)
- **Phase A ✅** `mg_metal.itp`: Mg–Mg σ=0.29436 nm, ε=18.10 kJ/mol (E_coh 1.616 eV, a₀ 3.209; γ(0001)=0.544 J/m²).
  UFF ε was 39× too weak → why their slab needed POSRES. Caveat: B ~2.4× high; elastic/phonons qualitative.
- **Phase B ✅** `mg_electrolyte_nbfix.itp` + the **ion-metal finding** (the real result):
  DFT E_int(z) → **THF neutral = clean vdW well −0.68 eV @ 2.2 Å (MgEl–O_thf NBFIX, solid)**; **Cl⁻ = image-charge
  (effective LJ only, RMSE 0.55 eV)**; **Mg²⁺ = reduced/electrodeposited (−13.5 eV, not a pair)**.
- **HEADLINE:** a neutral fixed-charge LJ wall (UFF or DFT-calibrated) **cannot** represent ion-metal
  (image-charge + charge-transfer) — only neutral THF is LJ-fittable. The classical(enrich)–vs–MLFF(deplete)
  discrepancy is **rooted there**, not in a bad ε. Wall fixes solvent structure; **charged-interface verdict needs
  constant-potential electrodes (LAMMPS fix electrode/MetalWalls) or the MLFF** — MLFF/AIMD stays the ion reference.
