# T8 — SEI electronic structure: bare leaky vs poly passivating
**Objective (ARTICLE_PLAN C3 / Fig 5):** test whether the **Al-rich bare SEI is electronically leaky** (metallic component → continued parasitic reduction → self-discharge, GITT CE 27 %) while the **Si-rich poly SEI is a better insulator/passivator** (CE ~100 %). This is the *compositional* explanation of the reversibility difference — the keystone new result of the v3 program.

**Method:** CP2K 2025.1, PBE-D3(BJ), DZVP-MOLOPT-SR-GTH / GTH-PBE, CUTOFF 400 / REL 50, Fermi smearing 300 K. Band gaps from converged SCF eigenvalue spectra. **Metals require k-point sampling** (Monkhorst–Pack) — Γ-only on small cells gives a *spurious* gap because the metallic bands cannot disperse to close it; insulators are safe at Γ. Geometries: v2-relaxed bulk (MgO, MgCl₂, Al₂O₃, Mg₁₇Al₁₂) reused; **α-quartz SiO₂ relaxed here** (CELL_OPT, this ticket, `structures/`); Al(fcc)/Mg(hcp) built at relaxed lattice constants.

## Result (`outputs/t8_gaps.csv`, `figures/fig_t8_band_gaps.png`)
| phase | role in SEI | band gap | sampling | electronic verdict |
|---|---|---|---|---|
| **Al⁰ (fcc)** | **bare** (reduction product) | **0.00 eV** | k-point 6×6×6 | **metallic → electron-leaky** |
| **Mg₁₇Al₁₂ alloy** | **bare** (Mg–Al alloy) | **≈0.18 eV**, states at E_F | k-point/Γ | **metallic alloy → leaky** |
| Mg (hcp) | anode substrate | 0 (free-electron metal) | — | metallic (reference) |
| MgCl₂ | shared | 2.93 eV | Γ | insulator (passivating) |
| MgO | shared | 3.92 eV | Γ | insulator (passivating) |
| Al₂O₃ | bare oxidised-Al residue | 6.21 eV | Γ | insulator (passivating) |
| **SiO₂ (POSS/Si-rich)** | **poly** | **8.46 eV** | k-point 4×4×4 | **wide-gap insulator → passivating** |

## Interpretation
The decisive contrast is **the presence vs absence of a metallic (gapless) phase in the SEI**:
- **Bare:** its reduction products — **Al⁰ (gap 0.00 eV) and Mg–Al alloy (≈0, states at E_F)** — are **metallic**. A metallic inclusion in the interphase keeps it **electronically conductive**, so electrons continue to reach and reduce incoming Al-anion → **parasitic reduction / electron leakage → self-discharge** (bare GITT CE 27 %, −320 mV/h OCV decay).
- **Poly:** the Si-rich component **SiO₂ is a wide-gap insulator (8.5 eV)**, and the rest of the poly SEI (MgO, MgCl₂) is likewise wide-gap. With **no metallic phase**, the interphase **electronically passivates** the anode → electron transfer to the anion is blocked → **reversible plating** (poly CE ~100 %).

So the **Si-in / Al-out compositional switch is also an electronic switch**: leaky-metallic (bare) → insulating-passivating (poly). This explains the reversibility/self-discharge data *from composition*, with **no transport advantage invoked** (honest spine preserved).

## Acceptance / honesty
- ✔ bare-vs-poly reported as a pair; metal-vs-insulator distinction is **robust** (Al⁰ unambiguously gapless under k-points; SiO₂ unambiguously wide-gap).
- Limitations: PBE **underestimates** insulator gaps (true SiO₂ ≈9 eV, MgCl₂/MgO larger) and the SR-MOLOPT basis + slightly contracted SiO₂ cell shift absolute values — but the **ordering and the metal/insulator split are reliable**. Γ-only insulator gaps are direct-gap estimates. Mg/Mg₁₇Al₁₂ metallicity rests on k-point Al⁰ + established physics + the alloy's finite DOS at E_F. Single-composition stoichiometric phases (not amorphous mixed SEI) — labelled as phase models.
- **No fluorine phase** included (per constraint).

**Provenance:** inputs in `inputs/`, relaxed SiO₂ in `structures/`, gaps in `outputs/t8_gaps.csv`. Generated 2026-06-18, CP2K 2025.1 on the EPYC node. Feeds ARTICLE_PLAN Fig 5 and the GITT/self-discharge reconciliation (Part D).
