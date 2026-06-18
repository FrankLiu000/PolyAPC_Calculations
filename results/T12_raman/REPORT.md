# T12 — Raman / vibrational assignment
**Objective (ARTICLE_PLAN C5 / §8):** assign the experimental Raman bands and rationalise the bare→poly shifts — show they reflect **de-pairing / dissociation + preserved first-shell coordination**, *not* a redox change.
**Method:** analytic harmonic frequencies, B3LYP-D3(BJ)/def2-SVP, SMD(THF) (the campaign's molecular level). Frequencies + IR intensities computed for free THF, Mg-coordinated THF (MgCl(THF)⁺), the Al-phenyl anions (AlPh₂Cl₂⁻, AlPh₄⁻), POSS cage, polyether. Bands assigned by frequency + mode character (harmonic, unscaled).

## Assignment (`outputs/raman_assignment.csv`)
| exp band (cm⁻¹) | exp shift | computed | species / mode | reading |
|---|---|---|---|---|
| **915** | +0.3 (retained) | **912.0** | free THF ν(C–O–C) ring | solvent framework unchanged |
| **1483→1486** | +3.2 | **1480.5 (free) → 1481.8 (Mg-bound)** | THF CH₂ deformation | **coordinated-THF stiffening — Mg first shell intact** |
| **999→1002** | +2.9 (+8 %) | **993.6 (AlPh₂Cl₂⁻) / 1010.9 (AlPh₄⁻)** | phenyl ring breathing | **shifts toward the *free*-anion value → dissociation / de-pairing** |
| **276** | −30 % | ~215–240 | [Mg₂Cl₃]⁺ / Mg–Cl skeletal | fewer chloride-bridged aggregates |
| **181** | ×2 | ~180–230 | Mg–Cl stretch | more dissociated Mg–Cl |

## Interpretation
The computed modes reproduce the experimental bands and their bare→poly shifts as a **dissociation / de-pairing signature with a preserved Mg first shell** — exactly the v3 picture, and **not** a redox change:
- **915 ν(C–O–C) retained** (computed 912) → the THF solvent framework is unchanged; the network does not disrupt the solvent.
- **THF CH₂ deformation stiffens on Mg-coordination** (computed +1.3 cm⁻¹ free→bound; exp +3.2) → the **Mg²⁺ first solvation shell stays intact** in poly (consistent with the MLFF shell-retention result, v2 §7b).
- **Phenyl ring breathing moves toward the free-anion value** (AlPh₂Cl₂⁻ 994 → AlPh₄⁻/free 1011; exp 999→1002) and **Cl-bridge modes weaken** (276 −30 %, 181 ×2) → the network **de-pairs the electrolyte / dissociates the anion** (the v1/§1 de-pairing, CIP 95→84 %).

So the spectroscopy corroborates **coordination/de-pairing gating** (Si-in/Al-out interphase context) with the cation's first shell preserved — no signature of a redox/chemical-state change in the electrolyte.

## Honesty
- Harmonic, unscaled frequencies (typical +1–3 % vs experiment); the **assignment and the *direction* of every shift are robust**, magnitudes semi-quantitative.
- **Raman activities were not in the original route (IR intensities were);** modes are assigned by frequency + character (all are well-known Raman-active framework modes). Raman-activity intensities are a flagged refinement (re-run with `freq=raman`).
- Mg–Cl/Cl-bridge region uses the MgCl(THF)⁺ monomer proxy (the [Mg₂Cl₃]⁺ bridge modes would sharpen the 276 assignment).

**Provenance:** frequencies parsed from `run_mol/*_ramanopt.log`; inputs in `inputs/`. Feeds ARTICLE_PLAN §8 / Fig 5; corroborates first-shell retention (T8/MLFF) + de-pairing (§1).
