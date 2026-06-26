# EPYC -> GPU: T21 Phase B - Mg wall <-> electrolyte cross-LJ + the ion-metal finding

## What is deliverable as a classical LJ wall (and what is NOT)
DFT E_int(z) (PBE-D3) for the 3 species approaching Mg(0001):

| species | DFT E_int(z) | classical LJ? |
|---|---|---|
| **THF (neutral)** | clean vdW well **-0.68 eV @ 2.2 A**, wall <2.0 A | **YES** -> `MgEl-O_thf` NBFIX (sigma 0.1841 nm, eps 53.2 kJ/mol) |
| **Cl-** | **image-charge**: monotone long-range attraction + contact well -1.8 eV; r^-1 tail | **EFFECTIVE only** (lumped, RMSE 0.55 eV) - flagged |
| **Mg2+ (bare)** | **-13.5 eV = reduced** | **moot** - the cation is NEVER bare (see below) |

### Correction (PI): the cation is solvated - it does NOT contact bare metal
The bare-Mg2+ reduction is the **desolvated end-state** (the activated plating step), not the approach. The real
cation is the bulky **[Mg2(mu-Cl)3(THF)6]+**; its THF/Cl shell holds it at the **~5.64 A standoff and it never
touches bare metal.** So that standoff is a **solvation/steric effect that CLASSICAL MD reproduces** via the
THF-shell<->wall interaction = the **MgEl-O_thf NBFIX above** - no special cation-metal term needed (correctly
omitted). Likewise the anion's Cl is **bonded in the chloroaluminate**, so the bare-Cl- scan **overstates** its
exposure/image-charge.

## The headline finding (refined)
Classical fixed-charge MD **CAN** handle the **neutral solvent** (THF, real LJ) and the **solvated cation**
(standoff = solvation/sterics via Mg-O). It **under-captures** only (a) the **anion's** long-range **image-charge**
(negative ion approaching the metal; partly mitigated because the Cl is bonded, not free) and (b) the **reductive
plating** chemistry (Mg2+ + 2e- -> Mg0) - both of which need the metal's electronic response.
- So the classical-vs-MLFF **enrichment vs depletion** gap is **not** mainly a cation-metal issue; suspect the
  **anion-metal image-charge + the (UFF-)mis-set solvent-wall**. The new **MgEl-O_thf NBFIX** (much stronger than
  UFF) changes the THF<->wall competition that sets where ions sit - **re-run with it before concluding.**

## Recommended use
1. Free slab: **mg_metal.itp** (Mg-Mg cohesive LJ) - lets the slab self-cohere (drop POSRES; anchor bottom 1-2 layers).
2. Add **MgEl-O_thf NBFIX** (solid) - corrects the solvent-wall interaction (your UFF wall had this wrong).
3. Cl-: use the effective `MgEl-Cl` only if you must; know it misses the long-range image tail.
4. **Cation: no special treatment** - solvated, standoff set by Mg-O solvation/sterics (classical OK).
5. **Anion image-charge + reductive plating** are what fixed-charge MD under-captures -> for those use
   **constant-potential electrodes** (LAMMPS `fix electrode` / MetalWalls) **or the MLFF (T17)**. Keep the
   **MLFF/AIMD standoff as the reference** for the anion distribution; treat the classical run (free slab +
   mg_metal + MgEl-O_thf NBFIX) as the **solvent-structure** model and **re-check the per-face enrichment with the
   stronger calibrated O-wall before any verdict.**
