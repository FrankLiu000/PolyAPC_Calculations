# EPYC -> GPU: T21 Phase B - Mg wall <-> electrolyte cross-LJ + the ion-metal finding

## What is deliverable as a classical LJ wall (and what is NOT)
DFT E_int(z) (PBE-D3) for the 3 species approaching Mg(0001):

| species | DFT E_int(z) | classical LJ? |
|---|---|---|
| **THF (neutral)** | clean vdW well **-0.68 eV @ 2.2 A**, wall <2.0 A | **YES** -> `MgEl-O_thf` NBFIX (sigma 0.1841 nm, eps 53.2 kJ/mol) |
| **Cl-** | **image-charge**: monotone long-range attraction + contact well -1.8 eV; r^-1 tail | **EFFECTIVE only** (lumped, RMSE 0.55 eV) - flagged |
| **Mg2+** | **-13.5 eV = REDUCED by the metal** (electrodeposition), ~flat | **NO** - it's a reaction, not a pair |

## The headline finding (answers WHY classical != MLFF)
The ion-metal interaction is dominated by **image-charge (Cl-)** and **charge-transfer/reduction (Mg2+)** - both
need the metal's **electronic response**, which a **neutral fixed-charge LJ wall (UFF or DFT-calibrated alike)
cannot represent.** Only the **neutral solvent (THF)** is LJ-fittable. So:
- The classical-vs-MLFF **enrichment (UFF wall) vs depletion (MLFF standoff)** discrepancy is **rooted in the
  missing metal electronic response to the ions** - NOT a bad LJ epsilon. A better LJ wall improves the
  **solvent-wall** structure but **will not fully reconcile** the ion distribution with the MLFF.

## Recommended use
1. Free slab: **mg_metal.itp** (Mg-Mg cohesive LJ) - lets the slab self-cohere (drop POSRES; anchor bottom 1-2 layers).
2. Add **MgEl-O_thf NBFIX** (solid) - corrects the solvent-wall interaction (your UFF wall had this wrong).
3. Cl-: use the effective `MgEl-Cl` only if you must; know it misses the long-range image tail.
4. **For the definitive CHARGED interface (and the enrichment/depletion verdict): constant-potential electrodes**
   (LAMMPS `fix electrode` / MetalWalls) **or the MLFF (T17)** - the classical fixed-charge wall cannot capture the
   ion-metal electrostatics that drive it. Treat the calibrated classical run as the solvent-structure complement,
   with the **MLFF/AIMD standoff as the reference** for the ion distribution.
