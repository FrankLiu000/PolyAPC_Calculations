# poly-APC / bare-APC MD package — handoff for wet-lab integration

本目录汇总了支撑完整 MD 故事的所有文件（结构/拓扑、RDF、相互作用能、溶剂化统计、输运/电导），
供下游 agent 与 wet-lab 数据结合使用。This package contains the structure/topology files, RDFs,
interaction energies, solvation statistics, and transport/conductivity data that support the
coherent MD story. All GROMACS topologies are **self-contained** (validated with `gmx grompp`).

---

## 0. Systems (chemistry)
APC = all-phenyl-complex Mg electrolyte: cation **[Mg₂(μ-Cl)₃·6THF]⁺**, anion **[Ph₂AlCl₂]⁻**, solvent THF.
poly-APC = APC cured with **Glycidyl-POSS** (CAS 164017-77-0, octakis[3-(2-oxiranylmethoxy)propyl]-
octasilsesquioxane) + TMSOTf initiator → poly(THF)/POSS network (cationic ROP).

| dir | system | composition | cure | role |
|---|---|---|---|---|
| `structures/00_bareAPC` | bare-APC liquid | 80 cat + 80 an + 2120 THF | — | reference electrolyte |
| `structures/01_polyAPC_4POSS_gel` | cured gel, recipe loading | +4 POSS +6 TMSOTf | 100% conv, 1 network | "poly-APC" main model |
| `structures/02_polyAPC_8POSS_swollen` | **swollen gel** | +8 POSS, 2040 free THF | 100% conv, minimal grafting | **explains the conductivity result** |
| `structures/03_polyAPC_16POSS_dense` | high-loading dense gel | +16 POSS | 100% conv, dense | loading-scan extreme |

Force field: OPLS-AA–based, self-contained `[defaults]`+`[atomtypes]` in each `.top`; comb-rule 3,
fudgeLJ=fudgeQQ=0.5; Mg/Cl use **scaled charges** (Mg +1.2, bridging Cl −0.467). See FF caveats §5.
Each system folder has `.itp` (moleculetypes) + `.top` (master) + `.gro` (coords) + `index.ndx`;
production_final.gro = last frame of the analyzed production. (Trajectories `.xtc` are NOT included —
too large; regenerate from `.tpr` if needed.)

---

## 1. The consolidated story (key numbers)

**(a) Mg speciation — preserved, matches experiment.** Octahedral **[Mg₂(μ-Cl)₃·6THF]⁺**:
Mg–Cl peak 0.250 nm (CN 3.0), Mg–O(THF) 0.212 nm (CN 3.0), total CN ≈ 6.2. Identical in all systems
(polymer does not break the cluster). → `rdf/`, `structures/representative_solvation/*.pdb`.
Consistent with XRD/AIMD (Canepa et al., EES 2015).

**(b) Contact ion pairing — tunable, decreases with POSS loading/conversion:**
| | bare | 4-POSS | 8-POSS swollen | 16-POSS dense |
|---|---|---|---|---|
| Mg with anion-Cl contact | 83.3% | 79.8% | 75.3 ± 1.6% (2 reps) | 58.8% |
| free-carrier fraction f | 0.167 | 0.202 | 0.247 | 0.412 |
→ `solvation/`. Mechanism: cured glycidyl ether/OH oxygens coordinate Mg and displace the anion
(Mg–polymer-O contact rises 0.6%→5.0% from 4→16 POSS).

**(c) Solvation is dual-mode:** cation = electrostatically solvated (Mg–Cl/O + ion-pairing Coulomb);
anion [Ph₂AlCl₂]⁻ = dispersively solvated (vdW dominates). → `interaction_energies/`, report Addendum 1.

**(d) Transference number ~invariant:** t₊ = 0.505 ± 0.011 (bare), 0.496 ± 0.014 (4-POSS, 3×100 ns),
~0.46 (16-POSS). No Mg²⁺-transference gain. → `transport/diffusion_transference_replicates.txt`.

**(e) Conductivity (explains wet-lab σ_poly > σ_bare):** bare-APC is heavily **ion-associated**
(ionicity = σ_collective/σ_NE ≈ 0.08–0.13, i.e. only ~10% of Nernst–Einstein) → conductivity is
**carrier-number-limited, not mobility-limited**. The cured POSS oxygens **de-pair** the ions (more
free carriers) and, in a **swollen** gel, ion **mobility is preserved** (self-D ≈ 98% of bare:
0.0496/0.0490 vs 0.051/0.050) → σ ∝ f·D ≈ **×1.44 vs bare**, reproducing the experiment.
→ `reports/conductivity_explanation.md`, `transport/collective_conductivity.txt`.

---

## 2. Directory map
- `reports/` — human-readable synthesis:
  - `ANALYSIS_REPORT.md` (full: RDF, solvation, energies, diffusion + Addenda 1–4)
  - `conductivity_explanation.md` (**the σ_poly>σ_bare explanation**, with the swollen-gel resolution)
  - `SYNTHESIS_descriptors.md` (high-level stories + descriptor set for poly-APC)
  - `COMPARISON.md` (auto bare-vs-poly tables)
- `structures/` — topologies + coordinates (grompp-validated) + representative solvation PDBs
- `rdf/{bare,poly}/` — `rdf_*.xvg` (g(r)) and `cn_*.xvg` (running coordination number); pairs:
  MgClb (Mg–bridge Cl), MgLigO (Mg–ligand THF O), MgSolvO (Mg–free THF O), MgAllThfO, MgAnCl
  (Mg–anion Cl), MgAnAl, MgMg, MgPolyO (poly only)
- `interaction_energies/` — `gmx energy` group-decomposition logs (Coul-SR + LJ-SR per group pair)
- `solvation/` — per-Mg first-shell statistics (CN distributions, motifs, contact-pairing %)
- `transport/` — diffusion D, transference t₊ (replicates), collective conductivity / ionicity

---

## 3. Computed ↔ wet-lab observable mapping (for the integration)
| MD quantity (file) | maps to experimental probe | note |
|---|---|---|
| Mg speciation, RDF peaks, representative PDBs | Raman/IR band assignment, XRD, EXAFS/XANES | [Mg₂Cl₃·6THF]⁺ confirmed |
| **contact-ion-pair fraction / free-carrier f** (`solvation/`) | **ionic conductivity, Raman free-vs-paired anion ratio, NMR** | the σ-controlling variable |
| ionicity σ_coll/σ_NE (`transport/`) | Haven ratio / σ vs (n·D) discrepancy | APC ≈ 0.1 (highly associated) |
| self-diffusion D (`transport/`) | **PFG-NMR diffusion coefficients** | swollen gel D ≈ 98% of liquid |
| transference t₊ (`transport/`) | **Bruce–Vincent / e-NMR t₊** | ~0.5, ~invariant |
| interaction energies (`interaction_energies/`) | association trends, (qual.) stability/ESW | SR-only Coulomb (see caveats) |
| density (reports) | measured gel density | bare 0.95, gel 0.98–1.00 g/cm³ |
| network connectivity / crosslink density (`structures/`) | rheology, mechanical modulus, swelling ratio | single connected network |

**Headline for integration:** the experimental conductivity increase (σ_poly > σ_bare) is explained
by **ionic de-association** (POSS oxygens break APC's abundant ion pairs → more free carriers) with
**preserved mobility** in the swollen gel — NOT by faster diffusion. Cross-check against measured σ,
PFG-NMR D, and Raman ion-pair populations.

---

## 4. Suggested cross-checks with wet-lab data
1. **σ(poly)/σ(bare):** compare measured ratio to the f·D estimate (~1.4×); if Raman/NMR gives
   ion-pair populations, compare directly to the contact-pairing % here (83%→75%).
2. **PFG-NMR D:** compare Mg and anion D ratios (poly/bare). Model (swollen) predicts ≈ 1 (preserved).
3. **t₊ (Bruce–Vincent):** model predicts ~0.5, ~unchanged by gelation.
4. **Raman/IR:** Mg–Cl–Mg bridge, THF coordination, free vs contact anion — assignments from RDF/PDBs.

## 5. Caveats (read before quantitative use)
- Classical non-polarisable FF; Mg/Cl **scaled charges** → energetics are effective, not ab-initio.
- APC cation/anion are **bonded complexes** → inner 3 THF/3 Cl exchange suppressed (4th THF + anion
  association are free and sampled).
- Interaction energies are **short-range** (PME-reciprocal not decomposed); charged–charged Coulomb
  (Mg–anion, anion–anion) is SR-only → use for trends, not absolute binding.
- **Collective conductivity is very noisy** (single-config; bare ranged 0.036–0.169 mS/cm) → the
  conductivity claim rests on the two robust observables (contact pairing + self-D), not the
  collective σ magnitude.
- 4→16 POSS de-pairing is confounded with conversion (loading × conversion = total coordinating O).
- Small representative cells (~37–40k atoms); dense gels over-suppress mobility (model artifact);
  the **swollen 8-POSS model is the realistic one** for transport.
