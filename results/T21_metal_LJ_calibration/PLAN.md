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

## ★ RE-PRIORITIZED after GPU `c78fef4` (T5 v3.2, 2026-06-26)
The GPU built the **classical** Mg(0001)|electrolyte|Mg(0001) interface using a **UFF Mg wall placeholder**
(`MGE_SIG=0.26915 nm`, `MGE_EPS=0.4644 kJ/mol`) with the slab **POSRES k=50000** (restrained, not free).
Consequences:
- **Phase B (cross-LJ) is now PRIMARY** — it is the calibrated drop-in replacement for their UFF wall.
- **Phase A (Mg–Mg metal LJ) is DEMOTED** — under POSRES k=50000 the metal LJ barely matters (restraints
  pin the lattice). Keep the cheap bulk EOS for the record / for an eventual free slab; surface-energy slab
  doubles as the **bare-slab reference for Phase B** so it is not wasted.
- **Why it matters:** the classical UFF-wall run gives anion **enrichment** at the gel face — opposite in
  sign to the MLFF/AIMD **depletion/standoff**. A leading suspect is the un-calibrated UFF wall. Delivering a
  DFT-anchored MgEl wall (reproduces the 3.90/4.58/5.64 Å standoff) **tests whether a calibrated wall flips
  enrichment→depletion** and reconciles the two models.

## Status
- [running] Phase A bulk EOS + Mg atom + slab36 (slab36 = Phase-B bare-slab reference).
- [next, PRIMARY] Phase B E_int(z) scans (Cl⁻, THF-O, Mg²⁺ on Mg(0001)) → fit MgEl σ/ε + NBFIX → deliver
  drop-in replacement for the GPU's UFF wall → GPU re-runs the sym-interface with the calibrated wall.
