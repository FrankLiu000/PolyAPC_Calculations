# EPYC -> GPU: DFT-anchored Mg metal LJ for the FREE slab (T21 Phase A)

Drop-in replacement for the UFF `MgEl` wall placeholder. **`mg_metal.itp`** (comb-rule 3):
- **sigma = 0.29436 nm, epsilon = 18.103 kJ/mol** (atomtype MgEl, charge 0, mass 24.305).
- Fit (PBE-D3, GTH-q10, consistent w/ AIMD): sigma <- hcp NN a0=3.209 A; epsilon <- E_coh=1.616 eV/atom
  (8.61*eps lattice-sum). EOS itself smearing-noisy -> sigma/eps anchored to lattice+cohesive (robust).

## Why this matters for your rebuild
- Your UFF eps (0.4644 kJ/mol) is **39x too weak** to cohere a FREE metal slab -> that's why you needed
  POSRES k=50000. With this **cohesive eps the slab self-coheres**; you can release the surface (anchor only
  bottom 1-2 layers weakly, AIMD convention).
- **CRITICAL: Mg-electrolyte pairs MUST NOT use the combining rule.** Geometric-combining the strong metallic
  eps would grossly over-attract the electrolyte (worse enrichment). Use the **Phase-B NBFIX** I'm computing
  next (DFT E_int(z) for Cl-/THF-O/Mg2+ -> [ nonbond_params ] for all Mg-electrolyte pairs, validated to the
  3.90/4.58/5.64 A standoff). NBFIX leaves Mg-Mg untouched. **Hold the per-face verdict until NBFIX lands.**

## Honest caveats (12-6 LJ, hcp metal)
- Bulk modulus over-predicted ~2.4x (LJ B~89 vs Mg 36.8 GPa); elastic anisotropy / c-a / phonons qualitative
  (pairwise Cauchy limit). Adequate for interfacial ion-distribution; for metal *mechanics*, EAM/MEAM-in-LAMMPS
  is higher fidelity (offered). Surface-energy cross-check vs the DFT slab in progress.
