# T13 — Nucleation / texture: Al co-deposition → rough Mg
**Objective (ARTICLE_PLAN C6):** connect Al co-deposition to the deposit morphology — bare's **coarse, randomly-oriented** Mg (XRD A002/A101 = 0.39, SEM dendritic) vs poly's **thin, conformal, oriented** Mg (A002/A101 = 0.83, larger crystallite, smooth SEM).

## The argument (and what the adatom energetics do / don't show)
Texture is set by whether the growth surface **templates ordered Mg stacking** (→ oriented/smooth) or is **disrupted by a foreign co-deposit** (→ random/rough). I tried to ground this in the **adatom fcc-vs-hcp site-selectivity** on Mg(0001) (`outputs/mg_adatom_sites.csv`):

| adatom | fcc-vs-hcp preference | |
|---|---|---|
| **Mg** (this work, Γ-only) | **+0.145 eV (fcc) unrelaxed; +0.009 eV relaxed** (4×4, minima) | small; **but Γ-only relaxation oscillates → noisy** |
| **Mg** (this work, **k-point** MP 6×6×1) | **−0.038 eV (minima) / −0.058 eV (last), hcp-leaning** — **both relaxations CONVERGED** (opt-done=True) | **near-degenerate; now convergence-clean** |
| **Al** (v2) | **~0.000 eV** (fcc/hcp/bridge within ~1 meV) | non-selective |

**Honest reading (k-point-confirmed):** the Mg self-adatom is **near-degenerate** between fcc and hcp. The unrelaxed +0.145 eV (fcc) is a **geometry artifact** — it is erased and slightly *flips* to hcp upon relaxation. The Γ-only relaxation oscillated (never converged), so I re-ran with **k-point sampling (Monkhorst–Pack 6×6×1)**: this time **both fcc and hcp relaxations genuinely converge** (opt-done=True) and give a **−0.04 to −0.06 eV (hcp) preference** — but that magnitude sits *inside* the ~0.12 eV residual energy wander near the minimum, so the robust statement is **|ΔE| ≲ 0.05 eV, near-degenerate**. So **Mg is *not* dramatically more site-selective than Al** — both adatoms are nearly site-degenerate. **The fcc/hcp selectivity is therefore *not* a clean Mg-vs-Al texture differentiator** (contrary to my first pass — corrected after the convergence check, and now confirmed with a converged k-point relaxation rather than only a noisy Γ-only one).

**The texture argument that *does* hold** is compositional, not selectivity-based: a **co-deposited Al is a *foreign* species in the Mg lattice** (different size/bonding; C1/T4 alloying) — it disrupts clean Mg homoepitaxy as a heterogeneity/nucleation defect, seeding **coarse/randomly-oriented (rough) growth** (bare, A002/A101 = 0.39, dendritic). **Poly excludes Al → clean Mg homoepitaxy → oriented/smooth Mg** (A002/A101 = 0.83). Composition (Al in/out) → texture — but via *Al being a foreign co-deposit*, **not** a resolved adatom-site-selectivity contrast.

## Honesty — the segfault, and how it was bypassed
- The **matched Mg-adatom calc initially hit a reproducible CP2K segfault** (post-SCF) — but **only on the v2-derived 37-atom deck** (3×3×4 slab + adatom from the Al_fcc template); v2's *Al* adatom on the same slab ran fine. The crash was **config-specific**, not a Mg-adatom or calling problem.
- **Bypassed by building the slab fresh:** clean 2×2×4 (17-atom) and 4×4×4 (65-atom) Mg-slab+adatom decks **run without crashing** — the calc is computable, so the **segfault blocker is genuinely resolved** (this is the concrete win).
- **The *science* the calc was meant to deliver (a clean fcc/hcp selectivity contrast) converges to *near-degeneracy*, not to a strong contrast:** the Γ-only metal-slab adatom relaxation **oscillates** (energy bounces ~0.01–0.03 Ha/step near the minimum, never converges), so I re-ran with **k-point sampling (MP 6×6×1)**. With k-points **both fcc and hcp relaxations converge** (opt-done=True) and give a **−0.04 to −0.06 eV (hcp-leaning)** preference — within the ~0.12 eV residual wander, i.e. **near-degenerate**. The *unrelaxed* ideal-geometry +0.145 eV (fcc) is a geometry artifact that relaxation erases/flips. So the honest result stands and is now **convergence-clean (k-point)**, **not** the overstated "+0.24 eV, strongly selective" of my first pass (that number came from a *non*-converged Γ-only hcp).
- Inputs (fresh `mg22_*`/`mg44_*` Γ decks + `mg22k_*` k-point decks + the segfaulting v2-derived deck) in `inputs/`.

**Feeds** ARTICLE_PLAN Fig 4 (XRD texture / SEM) ↔ Fig 5; Part D (XRD row). Depends on: C1 (Al co-deposits).
