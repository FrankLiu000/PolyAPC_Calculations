# EPYC RESPONSE → Windows: DOS/PDOS for SEI phases + Mg|SEI band alignment (Fig 5d)

**From:** EPYC CPU/DFT node · **Date:** 2026-06-23 · **Re:** `REQUEST_EPYC.md` (Fig 5d upgrade).

## Delivered (`results/T8b_DOS/outputs/`)
### 1. Total DOS + element PDOS — all 7 T8 phases
`<phase>_dos.csv` (columns `E_minus_Ef_eV, totalDOS, pdos_<elem>…`) + `dos_meta.json` (E_F, VBM, CBM,
authoritative T8 gap, element list, σ). Built from CP2K **Γ-point** single-points on the **T8 relaxed geoms**
(reused `inputs/*_kp.inp`), `&PDOS COMPONENTS NLUMO -1`, **Gaussian σ = 0.10 eV**.
- **Metals (Al_fcc, Mg17Al12, Mg_hcp): referenced to E_F; finite totalDOS at E_F** (11.3 / 20.5 / 1.0 states/eV)
  → **gapless, electron-leaky** — shade these "leaky".
- **Insulators (SiO2, Al2O3, MgO, MgCl2): referenced to VBM; a clean gap above VBM** → **passivating** — shade
  "blocking". Element character is exactly what the figure needs (e.g. SiO2 VB = **O 2p**, CB onset = **Si**;
  Al⁰ states at E_F are **Al s/p**).
- **Why Γ-point (important):** CP2K 2025.1 **`&PDOS` does not support k-points** (verified — produces no `.pdos`).
  Γ is rigorous for the insulators (and matches T8's Γ gaps for Al2O3/MgO/MgCl2 exactly). For the **metals**,
  the gaplessness is the robust point (fractional occupations put states at E_F); the **authoritative metal/
  insulator gaps remain T8's k-point values** (`t8_authoritative_gap_eV` in the meta: Al_fcc 0.00, Mg17Al12 0.18,
  SiO2 **8.46**). The Γ-DOS for SiO2 shows ~7.1 eV (Γ underestimate) — render the curve but **label the gap 8.46**.

### 2. Mg | SEI band alignment (passivation, T6 route)
`iface_MgSiOx_alignment.csv` — vacuum-referenced band edges (Mg E_F = −Φ = −3.97 eV; oxide CBM = −χ, VBM =
CBM − gap_T8) + the **electron-injection barrier (E_F → CBM)**:

| phase | role | e⁻-injection barrier | verdict |
|---|---|---|---|
| **SiO2** | **poly SEI** | **3.07 eV** | **BLOCKS** (Mg E_F sits in the SiO₂ gap) |
| Al2O3 / MgO / MgCl2 | oxide/salt | 2.6 / 3.1 / 3.5 eV | block |
| **Al⁰ / Mg17Al12** | **bare SEI (metallic)** | **0 eV** | **LEAKY** (states at Mg E_F) |

This is the one-line passivation story: **bare's metallic Al⁰/alloy is degenerate with the Mg Fermi level →
electrons flow → continued reduction/self-discharge; poly's Si-rich SiOₓ puts Mg E_F deep in an 8.5 eV gap →
3.07 eV injection barrier → passivated.** Reproduces T6 (3.07 eV) with the DOS to back it.

**Honest note on the contact slab:** I delivered the **band-alignment** (the route T6 deliberately chose), NOT a
Mg(0001)|SiOₓ contact-slab PDOS — because T6 found a direct slab calc impractical (CDFT/Becke invalid on the
Fermi-smeared metal; the Mg-slab+adsorbate hits a reproducible CP2K segfault = T13; + the metal-slab SCF wall).
The alignment-vs-vacuum is the defensible, established method and gives the same physics. **If you specifically
need a contact-slab PDOS *image*, say so and I'll attempt a ~1–2 nm SiO₂/Mg(0001) single-point — but flag it as
higher-risk/slower per T6.**

## Fig 5d render guidance
Overlay the 7 total-DOS curves (or a representative 4: Al⁰, Mg17Al12, SiO2, Al2O3); shade metals red ("leaky,
DOS at E_F") vs insulators blue ("passivating, gap"); add the element-PDOS fill per phase; inset = the
band-alignment bar (Mg E_F line crossing the metallic SEI but landing in the SiO₂ gap, 3.07 eV arrow).
Scripts: `make_dos.py` (parser/broadener) + the `*_gpdos.inp` provenance. (T17 snapshot for a Fig 5 panel:
secondary — ping if wanted.)
