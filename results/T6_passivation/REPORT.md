# T6 — Electron-transfer / passivation barrier (Si-rich layer blocks Al-anion reduction)
**Objective (ARTICLE_PLAN C2):** does the poly Si-rich (SiOₓ/POSS) contact layer **kinetically block** electron transfer to an approaching Al-anion (vs the bare surface)?
**Method (robust route):** band alignment + tunneling, built from **computed** quantities — Mg(0001) work function Φ = 3.97 eV (v2-validated), SiO₂ band gap 8.46 eV (**T8**, this session) — plus the established SiO₂ electron affinity χ ≈ 0.9 eV. *(A direct constrained-DFT electron-transfer calc through a SiOₓ-on-Mg slab was not pursued: v2 showed CDFT/Becke is invalid on the Fermi-smeared metal — `interface_ET.txt` — and the Mg-slab+adsorbate hit a reproducible CP2K segfault, T13. Band alignment is the defensible route.)*

## Result (`outputs/` — band alignment vs vacuum, eV)
| level | energy |
|---|---|
| SiO₂ conduction-band min (CBM = −χ) | −0.90 |
| **Mg Fermi (−Φ)** | **−3.97** |
| SiO₂ valence-band max (VBM) | −9.36 |

**The Mg Fermi level sits *inside* the SiO₂ gap** (−9.36 < −3.97 < −0.90) → there are **no SiOₓ electronic states at the metal Fermi level** for an electron to occupy. Electron injection from Mg into the SiOₓ requires **+3.07 eV** (Fermi → SiO₂ CBM), so transfer to the anion is **tunnelling-limited**:

| SiOₓ thickness | transmission T ≈ exp(−2κd), κ = 0.90 Å⁻¹ |
|---|---|
| 0.5 nm | ~1×10⁻⁴ |
| 1 nm | ~2×10⁻⁸ |
| 5 nm | ~10⁻³⁹ |
| **50–90 nm (poly ToF-SIMS)** | **≈ 0** |

## Interpretation
- **Poly:** the Si-rich SiOₓ/POSS layer is a **wide-gap insulator whose gap straddles the Mg Fermi level** → it presents a **~3 eV electron-injection barrier**, and across the measured **50–90 nm** poly interphase the electron transmission is **vanishing**. Electron transfer to the Al-anion is **kinetically blocked** → Al-anion reduction is **suppressed** → Al-poor interphase. This is the **passivation half of "why poly is Al-poor"** (the kinetic/transport half is C2/T5 — the network also segregates the anion ~7 Å off the front).
- **Bare:** the SEI contains a **metallic phase** (Al⁰/Mg–Al alloy, gap 0, T8) — the Mg Fermi lies **in a band**, *no* injection barrier → electrons reach the anion freely → reduction proceeds (→ parasitic, T14).

So the **Si-in/Al-out composition is also an electron-transfer gate**: poly's insulating SiOₓ blocks the electron; bare's metallic SEI conducts it. Same physics as T8/T14, now as a **transfer barrier**.

## Honesty
- Band alignment uses the **computed** Mg Φ (v2) and SiO₂ gap (T8) + a **literature** SiO₂ electron affinity (χ ≈ 0.9 eV, ±0.3) — so the 3.07 eV barrier carries ~±0.3 eV; the **conclusion (Fermi-in-gap → tunnelling-limited → blocked over 50–90 nm) is robust** to that uncertainty (the tunnelling is exponential).
- Simple rectangular-barrier WKB tunnelling (order-of-magnitude); the real amorphous SiOₓ/POSS has traps/defects that could add hopping — but a 50–90 nm wide-gap layer is a strong electronic barrier regardless.
- **No direct SiOₓ-on-Mg CDFT** (invalid on metal / segfault) — flagged.

**Provenance:** Mg Φ (v2), SiO₂ gap (T8 `t8_gaps.csv`), tunnelling in `outputs/`. Feeds ARTICLE_PLAN Fig 5 (passivation route). Depends on: T8.
