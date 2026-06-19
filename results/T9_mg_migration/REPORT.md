# T9 — Mg²⁺ migration through the SEI (DRT link)
**Objective (ARTICLE_PLAN C3):** relate the **in-situ DRT** result (poly **higher-but-stable** interfacial impedance, R_ct) to Mg²⁺ transport through the poly (Si-rich) vs bare SEI.

## Attempt and honest outcome (incl. a thorough retry)
Mg-vacancy migration in a 2×2×2 MgO supercell (63-atom, 7 NEB replicas). Three routes were tried:
1. **Neutral-vacancy CI-NEB** (CHARGE 0): the neutral Mg vacancy hosts a localised 2-electron **F-centre** the smeared SCF **cannot converge** (0 SCF converged in 9 min) — stuck.
2. **Charged-vacancy CI-NEB** (CHARGE −2, the physically-correct Mg²⁺ vacancy — *no* F-centre): this **fixes the SCF** (a single-point converges in 15 steps ✓), but the 7-replica NEB is **impractically slow** (>1.5 h without completing the first band evaluation, ~7 cores/replica).
3. **Fast 2-point estimate** (CHARGE −2 endpoint relax + constrained midpoint-saddle): the SCF converges per point, but the **geometry optimisation oscillates ~2 eV/step and never settles** — the **charged-defect relaxation instability** (frustrated, charged-image-contaminated PES in the affordable cell). The resulting "barrier" is an artifact of unconverged geometries and is **not reported**.

**Verdict:** confirms the campaign's documented limitation (`mgf2_neb_LIMITATION.txt`) — a Mg²⁺ migration barrier is **not cleanly computable in an affordable charged MgO cell** (neutral → F-centre SCF; charged → unconverged/oscillating relaxation). A converged barrier would need a much larger cell + charge correction (Makov–Payne) — a major effort, not warranted since the DRT link is already carried (below). **No fabricated number.**

## What robustly answers the DRT question instead — T8 (electronic structure)
The DRT contrast (poly **higher-but-stable** R_ct; bare lower but unstable) is explained **without** a converged NEB, by the **SEI electronic structure (T8)** plus the established Mg²⁺-in-oxide literature:
- **Bare SEI is electronically leaky** (metallic Al⁰/Mg–Al-alloy, gap 0, T8). Its low interfacial impedance is **not benign Mg²⁺ conduction** — it is **electron leakage / parasitic reduction** (→ self-discharge, CE 27 %, T14). Low R_ct but **unstable**.
- **Poly SEI is an insulator** (SiO₂ 8.5 eV + MgO/MgCl₂, T8). Charge crosses it **only as Mg²⁺ ions** through a wide-gap, dense network → **higher R_ct, but stable/passivating** (no electronic leak). The **literature Mg²⁺-in-oxide/SiOₓ migration barrier (~0.5–1+ eV)** is consistent with a resistive-but-stable ionic interphase.

So poly's **higher-but-stable** R_ct = **ion-limited transport through a passivating insulator**, while bare's low-but-leaky impedance = **electronic conduction through a metallic SEI** — the same Si-in/Al-out, leaky→passivating switch as T8/T14.

## Honesty
- No computed Mg²⁺ barrier reported (NEB unconverged; charged-defect/F-centre problem in affordable cells — a documented, recurring limitation).
- The DRT link is carried by **T8 electronic structure** + literature ionic barriers — robust and already computed.
- Inputs (the NEB deck + 7 images) in `inputs/` for a future large-cell / charged-cell-corrected attempt.

**Feeds** ARTICLE_PLAN Part D (DRT row). Depends on: T7 (phases), T8 (electronic structure).
