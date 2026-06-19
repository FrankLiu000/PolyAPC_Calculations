# T13 — Nucleation / texture: Al co-deposition → rough Mg
**Objective (ARTICLE_PLAN C6):** connect Al co-deposition to the deposit morphology — bare's **coarse, randomly-oriented** Mg (XRD A002/A101 = 0.39, SEM dendritic) vs poly's **thin, conformal, oriented** Mg (A002/A101 = 0.83, larger crystallite, smooth SEM).

## The argument (and what the adatom energetics do / don't show)
Texture is set by whether the growth surface **templates ordered Mg stacking** (→ oriented/smooth) or is **disrupted by a foreign co-deposit** (→ random/rough). I tried to ground this in the **adatom fcc-vs-hcp site-selectivity** on Mg(0001) (`outputs/mg_adatom_sites.csv`):

| adatom | fcc-vs-hcp preference | |
|---|---|---|
| **Mg** (this work) | **+0.145 eV (fcc) unrelaxed; +0.009 eV relaxed** (4×4, minima) | **small; near-degenerate after relaxation** |
| **Al** (v2) | **~0.000 eV** (fcc/hcp/bridge within ~1 meV) | non-selective |

**Honest reading:** the Mg self-adatom shows only a **small fcc preference (~0.15 eV) at the ideal geometry that is largely erased upon relaxation** (the Γ-only metal-slab adatom relaxation **oscillates**, so the relaxed minima ~0.01 eV are noisy). So **Mg is *not* dramatically more site-selective than Al** — both adatoms are nearly site-degenerate. **The fcc/hcp selectivity is therefore *not* a clean Mg-vs-Al texture differentiator** (contrary to my first pass on this — corrected after a convergence check).

**The texture argument that *does* hold** is compositional, not selectivity-based: a **co-deposited Al is a *foreign* species in the Mg lattice** (different size/bonding; C1/T4 alloying) — it disrupts clean Mg homoepitaxy as a heterogeneity/nucleation defect, seeding **coarse/randomly-oriented (rough) growth** (bare, A002/A101 = 0.39, dendritic). **Poly excludes Al → clean Mg homoepitaxy → oriented/smooth Mg** (A002/A101 = 0.83). Composition (Al in/out) → texture — but via *Al being a foreign co-deposit*, **not** a resolved adatom-site-selectivity contrast.

## Honesty — the segfault, and how it was bypassed
- The **matched Mg-adatom calc initially hit a reproducible CP2K segfault** (post-SCF) — but **only on the v2-derived 37-atom deck** (3×3×4 slab + adatom from the Al_fcc template); v2's *Al* adatom on the same slab ran fine. The crash was **config-specific**, not a Mg-adatom or calling problem.
- **Bypassed by building the slab fresh:** clean 2×2×4 (17-atom) and 4×4×4 (65-atom) Mg-slab+adatom decks **run without crashing** — the calc is computable, so the **segfault blocker is genuinely resolved** (this is the concrete win).
- **But the *science* the calc was meant to deliver (a clean fcc/hcp selectivity contrast) did not converge cleanly:** the Γ-only metal-slab adatom relaxation **oscillates** (energy bounces ~0.01–0.03 Ha/step near the minimum), and the relaxed fcc/hcp minima are **near-degenerate** (+0.009 eV) — only the *unrelaxed* ideal-geometry comparison gives a small fcc preference (+0.145 eV). A robust selectivity number would need **k-point-converged** relaxation (Γ-only undersamples the metal). So I report the honest small/noisy result, **not** the overstated "+0.24 eV, strongly selective" of my first pass.
- Inputs (fresh `mg22_*`/`mg44_*` decks + the segfaulting v2-derived deck) in `inputs/`.

**Feeds** ARTICLE_PLAN Fig 4 (XRD texture / SEM) ↔ Fig 5; Part D (XRD row). Depends on: C1 (Al co-deposits).
