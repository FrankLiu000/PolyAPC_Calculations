# T9 — Mg²⁺ migration through the SEI (DRT link)
**Objective (ARTICLE_PLAN C3):** relate the **in-situ DRT** result (poly **higher-but-stable** interfacial impedance, R_ct) to Mg²⁺ transport through the poly (Si-rich) vs bare SEI.

## Attempt and honest outcome
A CI-NEB for Mg-vacancy migration in a 2×2×2 MgO supercell (63-atom, 7 replicas, neutral cell) was built and launched. **It did not converge** — the replicas failed to converge their SCF (the neutral Mg vacancy hosts a localised 2-electron F-centre that the smeared metal-style SCF cannot settle) — the **same class of failure the campaign documented for the MgF₂ NEB** (`mgf2_neb_LIMITATION.txt`: charged/defected-oxide endpoints don't relax in affordable cells). A converged Mg²⁺ migration barrier is **not reported** (no fabricated number), consistent with the project's honest stance.

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
