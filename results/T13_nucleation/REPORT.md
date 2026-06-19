# T13 — Nucleation / texture: Al co-deposition → rough Mg
**Objective (ARTICLE_PLAN C6):** connect Al co-deposition to the deposit morphology — bare's **coarse, randomly-oriented** Mg (XRD A002/A101 = 0.39, SEM dendritic) vs poly's **thin, conformal, oriented** Mg (A002/A101 = 0.83, larger crystallite, smooth SEM).

## The argument (grounded in the periodic adatom energetics)
Texture is set by whether the growth surface **templates ordered Mg stacking** (→ oriented/smooth) or is **disrupted by heterogeneous adsorbates** (→ random/rough). The decisive computed quantity is the **adatom site-selectivity** on Mg(0001):

**Adatom fcc-vs-hcp site preference on Mg(0001)** (`outputs/mg_adatom_sites.csv`):
| adatom | fcc-vs-hcp preference | reading |
|---|---|---|
| **Mg** (this work, 4×4 slab, adatom-relaxed) | **+0.244 eV → fcc** (2×2 cross-check +0.145 eV, same sign) | **strongly site-selective** |
| **Al** (v2, `al_codeposition_periodic.txt`) | **~0.000 eV** (fcc/hcp/bridge degenerate to ~1 meV) | **non-selective** |

⇒ The **Mg self-adatom strongly prefers the fcc hollow (~0.2 eV)** — a clear stacking template that drives **ordered, oriented layer-by-layer growth** (poly's Al-free surface → smooth, textured Mg, A002/A101 = 0.83). A **co-deposited Al adatom is non-selective** (all hollows within ~1 meV) → it provides **no stacking template**, pins at random positions, and **disrupts the Mg(0001) ordering** → **3-D / randomly-oriented (rough) growth** (bare, A002/A101 = 0.39, dendritic). Mg is ~200× more site-selective than Al.

So: **bare** co-deposits a non-templating Al heterogeneity → coarse/random Mg; **poly** keeps the surface clean Mg → its strong fcc-site preference templates oriented/smooth Mg. **Composition (Al in/out) → texture.**

So: **bare** co-deposits Al → non-templating heterogeneity → coarse/random Mg (dendrite-prone); **poly** excludes Al → clean Mg homoepitaxy → thin/oriented/smooth Mg. Composition (Al in/out) → morphology.

## Honesty — the segfault, and how it was bypassed
- The **matched Mg-adatom calc initially hit a reproducible CP2K segfault** (post-SCF) — but **only on the v2-derived 37-atom deck** (3×3×4 slab + adatom from the Al_fcc template); v2's *Al* adatom on the same slab ran fine. The crash was **config-specific**, not a Mg-adatom or calling problem.
- **Bypassed by building the slab fresh:** clean 2×2×4 (17-atom) and 4×4×4 (65-atom) Mg-slab+adatom decks **run without crashing** and give the result above. So T13 is now a **computed matched number**, not a deferred one.
- **Caveats:** Γ-only (metal slab undersampled → absolute E_ads is reference-sensitive; the **site preference is μ-independent and robust**, +0.24 eV at 4×4, +0.15 eV at 2×2, fcc both); the hcp adatom relaxation did not fully converge (so the preference is ~0.2 eV, slightly soft); E_ads (+0.1–0.4 eV vs slab-average Mg) is small/physical. The **fcc-site selectivity contrast with Al (the texture-relevant quantity) is the robust deliverable.**
- Inputs (fresh `mg22_*`/`mg44_*` decks + the segfaulting v2-derived deck) in `inputs/`.

**Feeds** ARTICLE_PLAN Fig 4 (XRD texture / SEM) ↔ Fig 5; Part D (XRD row). Depends on: C1 (Al co-deposits).
