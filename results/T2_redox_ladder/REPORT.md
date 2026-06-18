# T2 — Reduction ladder referenced to Mg²⁺/Mg
**Objective (ARTICLE_PLAN C1):** place every APC species' reduction on a common scale vs **Mg²⁺/Mg**, identify which reduces near the Mg-plating potential (the Al-co-deposition precursor), cross-check EAs with ωB97X-D / M06-2X.
**Method:** vertical electron affinities (SMD-THF, def2-TZVP), 3 functionals. E°(red) vs Mg²⁺/Mg = EA − 2.07 V (Mg²⁺/Mg absolute = SHE 4.44 − 2.37 V). Vertical EAs (well-defined; the *adiabatic* dianions are dissociative — that fragmentation **is** the reductive decomposition of T3/C1).

## Result (`outputs/redox_ladder_vsMg.csv`)
| species | EA B3LYP / ωB97XD / M06-2X (eV) | E°(red) vs Mg²⁺/Mg |
|---|---|---|
| AlCl₄⁻ | −1.30 / −1.59 / −1.31 | **−3.37 V** (anti-reducible) |
| AlPh₂Cl₂⁻ (dominant) | +0.06 / −0.31 / −0.09 | **−2.01 V** |
| AlPhCl₃⁻ / AlPh₃Cl⁻ / AlPh₄⁻ | ~0.1 / ~−0.3 / ~0 | **−1.9 to −2.0 V** |
| **[AlPh₂Cl₂⁻·cation] CIP (bare)** | 0.51 | **−1.56 V** |
| **[AlPh₂Cl₂⁻·cation] CIP (poly)** | 0.48 | **−1.59 V** |
| AlCl₃ (neutral) | 1.44 | **−0.63 V** |
| **AlPh₃ (neutral)** | 1.69 | **−0.38 V** |

## Conclusions
1. **No free anion reduces above Mg plating** — all E° are 1.9–3.4 V *below* Mg²⁺/Mg. So the Al-anion is **not spontaneously pre-reduced**; Al co-deposition is **concurrent with Mg plating / overpotential-driven** (consistent with the rare-event field-AIMD, T10, where the anion stays intact ~9.5 Å off the front).
2. **Contact-pairing raises reducibility ~0.45 V** (free −2.0 → CIP −1.56 V) — reduction happens at the *cation-paired interface*, not on the free anion — but **bare (−1.56) and poly (−1.59) are identical**: the molecular reduction thermodynamics are **not** the bare-vs-poly lever (the v2 depairing null, confirmed). The difference is **access/gating (C2) + the SEI (T8)**, not the redox potential.
3. **The neutral Al species reduce closest to plating** (AlPh₃ −0.38, AlCl₃ −0.63 V) — so the operative co-deposition precursors are the **neutral/low-valent Al fragments produced by reductive decomposition** (T3: Al–Cl cleavage of the reduced anion → Al-centred radical → Al⁰), which reduce right at the plating front. This closes the C1 chain on a Mg-referenced scale.
4. Cross-functional band: range-separated/M06-2X give EAs ~0.3–0.5 eV **lower** than B3LYP for the phenyl anions (all near-zero) — the anions are **barely reducible** under any functional; the conclusion (anion reduction is plating-concurrent, identical bare/poly) is functional-robust.

## Honesty
Vertical EAs (adiabatic dianions dissociate → that *is* the decomposition, T3). Absolute Mg reference uses the standard SHE = 4.44 V convention (±0.1 V). The contact-pair EAs are from the matched bare/poly CIP (`depairing_ET.txt`). No fluorine species.

**Provenance:** `outputs/redox_ladder_vsMg.csv`; EAs from `g16_energies.csv` (ωB97XD/M06-2X par/red pairs) + `redox_ladder.txt` (B3LYP) + `depairing_ET.txt` (CIP). Feeds ARTICLE_PLAN Fig 5; pairs with C1/T3 (decomposition) and T10 (rare-event AIMD).
