# T14 — Self-discharge / overcharge mechanism (why bare CE = 27 %, poly ~100 %)
**Objective (ARTICLE_PLAN C6 / Part A4):** explain, from the computed potentials (C1/T2–T3) and SEI electronics (T8), bare's **CE 27 %, OCV turnover ~1.29 V, −320 mV/h self-discharge** and why the Si-rich passivating SEI suppresses it in poly. Mechanistic synthesis — no new compute.

## The mechanism (grounded in computed numbers)
**Bare — a self-sustaining parasitic loop:**
1. **An Al-anion reduces at the cation-paired plating front** (C1): the minority **AlCl₄⁻** reduces *at Al* (spin +1.14), and reduced [AlPh₂Cl₂]²⁻ undergoes **Al–Cl cleavage (ΔG −8.5 kcal/mol)** to an 83 %-Al-spin radical → **Al⁰**; cation-pairing makes the anion **8× more reducible** (EA 0.06→0.51 eV). Al⁰ **alloys into Mg (E_sub −4.44 eV)**.
2. **The resulting SEI contains a metallic phase** — Al⁰ (**band gap 0.00 eV**) and Mg–Al alloy (≈0, states at E_F) — i.e. it is **electronically conductive (T8)**.
3. **Because the interphase conducts electrons, reduction does not self-limit:** electrons keep reaching fresh Al-anion at the buried interface even at open circuit → **continuous parasitic anion reduction**. This is a **chemical electron leak**: charge is consumed without reversible Mg plating/stripping → **CE 27 %** (167 mAh g⁻¹ charge vs 46 discharge) and an **open-circuit potential that sags −320 mV/h** as the parasitic reaction self-discharges the cell. The OCV turnover ~1.29 V marks the onset of the parasitic anion-reduction shuttle.

**Poly — the loop is broken at two points:**
1. **Less Al-anion arrives** (C2, v2 transport gating): the cured network de-pairs the electrolyte and segregates the Al-anion ~7 Å from the front (4.2× slower), starving step 1.
2. **The SEI is an insulator** (T8): the Si-rich **SiOₓ (gap 8.5 eV)** + MgO/MgCl₂ interphase has **no metallic phase** → it **electronically passivates** the anode. Electron transfer to any anion that does arrive is blocked → the parasitic loop **self-limits**. Result: **CE ~100 %**, OCV relaxes only −100 mV to a **stable** value.

## The decisive link: composition → electronics → reversibility
| | bare | poly |
|---|---|---|
| SEI contains metallic phase? | **yes (Al⁰/Mg–Al alloy, gap 0)** | **no (all wide-gap)** |
| interphase electronically… | **leaky** | **passivating** |
| parasitic anion reduction | sustained (electron leak) | self-limiting |
| **CE / self-discharge** | **27 % / −320 mV/h** | **~100 % / −100 mV stable** |

The **Si-in/Al-out compositional switch is an electronic switch** (T8) that converts a leaky, parasitic interphase into a passivating one — this is the computational origin of the reversibility data, **with no transport advantage invoked** (bulk D equal, MD+GITT).

## Honesty
Mechanistic synthesis built on computed quantities (C1 redox + T8 gaps); the electron-leak picture is the standard interpretation of a metallic-inclusion SEI. Absolute parasitic rates not computed (would need explicit interfacial electron-transfer kinetics, T10/T6). PBE gaps qualitative (T8 caveats). No fluorine channel invoked.

**Feeds** ARTICLE_PLAN Fig 2 (reversibility) ↔ Fig 5 (computation) reconciliation and Part D (GITT/CV row). Depends on: C1, T8.
