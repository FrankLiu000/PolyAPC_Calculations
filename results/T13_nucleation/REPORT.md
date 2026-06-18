# T13 — Nucleation / texture: Al co-deposition → rough Mg
**Objective (ARTICLE_PLAN C6):** connect Al co-deposition to the deposit morphology — bare's **coarse, randomly-oriented** Mg (XRD A002/A101 = 0.39, SEM dendritic) vs poly's **thin, conformal, oriented** Mg (A002/A101 = 0.83, larger crystallite, smooth SEM).

## The argument (grounded in the periodic adatom energetics)
Texture is set by whether the growth surface **templates ordered Mg stacking** (→ oriented/smooth) or is **disrupted by heterogeneous adsorbates** (→ random/rough). The decisive computed quantity is the **adatom site-selectivity** on Mg(0001):

**Al adatom on Mg(0001)** (`al_codeposition_periodic.txt`, v2, relaxed):
| site | E_ads (eV) |
|---|---|
| fcc / hcp / bridge | **−0.083 (all degenerate)** |
| ontop | +0.135 |

⇒ **Al binds weakly and NON-selectively** — fcc, hcp and bridge are degenerate to ~1 meV. An adsorbate with no site preference provides **no epitaxial/stacking template**: it pins at random positions and **disrupts the layer-by-layer Mg(0001) stacking**, seeding **3-D / randomly-oriented (rough) growth**. This is the bare case — co-deposited Al⁰ (C1) acts as a texture-randomising heterogeneity.

By contrast, **clean Mg homoepitaxy** is strong and site-selective (Mg–Mg cohesive ≈ 1.5 eV/atom; the hcp stacking sequence is templated by the substrate), giving **oriented, conformal layer growth** — the poly case (Al-free surface → A002/A101 = 0.83, smooth).

So: **bare** co-deposits Al → non-templating heterogeneity → coarse/random Mg (dendrite-prone); **poly** excludes Al → clean Mg homoepitaxy → thin/oriented/smooth Mg. Composition (Al in/out) → morphology.

## Honesty — what did and didn't compute
- The **Al-adatom selectivity (the key quantity) is the robust v2 periodic result** and carries the argument.
- A **fresh matched Mg-adatom calculation (fcc vs hcp binding) was attempted but hit a reproducible CP2K segmentation fault** in the post-SCF phase for the 37-Mg adatom slab — across GEO_OPT, single-point, restart-off, reduced ADDED_MOS, and PRINT_LEVEL LOW (6 variants). This is a **technical/code failure, not a physics result**; it is documented here rather than worked around with a fabricated number (consistent with the campaign's treatment of the unconverged MgF₂ NEB / CDFT). The Mg-homoepitaxy strength/selectivity is taken from the established Mg–Mg cohesion + literature.
- Inputs (incl. the segfaulting decks) in `inputs/` for reproducibility.

**Feeds** ARTICLE_PLAN Fig 4 (XRD texture / SEM) ↔ Fig 5; Part D (XRD row). Depends on: C1 (Al co-deposits).
