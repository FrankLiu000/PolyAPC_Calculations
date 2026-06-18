# RESULTS_v2 — STATUS (v3.1 interface-composition computational program)
**Thesis (ARTICLE_PLAN_v3):** the in-situ POSS-cured poly-APC Mg-anode interphase is **Si-rich, Al-poor, surface-confined**, which **suppresses Al co-deposition** and makes Mg plating reversible (CE ~100% vs bare 27%). Transport is **not** the discriminator (GITT + MD agree). **No fluorine story.**
**Node:** EPYC CPU (192 core) — DFT (G16/ORCA) + AIMD/periodic (CP2K 2025.1). GPU/MLFF tickets (T5,T16,T17) are the other node.
**Started:** 2026-06-18 (this session). Branch `main`.

## Ticket tracker (T0–T15 here; T16–T17 GPU)
| T | title | node | status | 1-line result |
|---|---|---|---|---|
| T0 | preflight / env / smoke | CPU | ◐ in progress | ORCA 6.1.0 + CP2K 2025.1 + G16 confirmed; offline (hand-build structures); Φ(Mg0001) & THF SMD validated in v2 |
| T1 | APC anion speciation map | CPU | ● done | C1: Schlenk ΔG all >0 → **[AlPh₂Cl₂]⁻ dominant, AlCl₄⁻ minority** (`speciation.csv`) |
| T2 | redox ladder vs Mg²⁺/Mg | CPU | ◑ qualitative | C1: only AlCl₄⁻ reduces at Al (+1.14); pairing 8×; **abs. potentials vs Mg = open refinement** |
| T3 | reductive decomposition → Al⁰ | CPU | ● done | C1: [AlPh₂Cl₂]²⁻ Al–Cl cleavage −8.5 (vs Al–C +14.5) → 83% Al-spin radical → Al⁰ |
| T4 | Al co-deposition / alloying (periodic) | CPU | ● done | C1: adatom E_ads −0.08 eV; Al-in-Mg E_sub −4.44 eV (alloying favourable) |
| T5 | anion interface dynamics (MD) | GPU | ○ deferred | GPU node (gmx absent here); v2 classical-MD has anion access/residence |
| T6 | e⁻-transfer / passivation barrier | CPU | ○ todo | NEW: SiOₓ/POSS layer on Mg(0001) |
| T7 | candidate SEI phase set + stability | CPU | ◑ partial | phases relaxed (incl. **α-quartz SiO₂ NEW, this session**); formation-energy table still to assemble |
| **T8** | **SEI electronic structure (DOS/gap)** | CPU | ● **done** | **Al⁰ 0.00 eV (metal/leaky), Mg₁₇Al₁₂ ≈0 (metal); SiO₂ 8.46, Al₂O₃ 6.2, MgO 3.9, MgCl₂ 2.9 eV (insulators/passivating)** |
| T9 | Mg²⁺ migration NEB through SEI | CPU | ○ todo | MgCl₂/MgO NEB decks exist; add SiO₂; (MgF₂ excluded — no-F) |
| T10 | constant-µ interface AIMD (real ions) | CPU | ◐ partial | bias machinery + bias_prod_bare exist; add Al-anion + poly + replicas |
| T11 | XPS Al 2p + Si 2p shifts | CPU | ◐ partial | Al 2p direction (Δq +0.7 e) done; **Si 2p NEW**; ΔSCF refinement flagged |
| T12 | Raman/IR assignment | CPU | ○ todo | NEW (v2 skipped); free vs Mg-bound THF, anion, polyether, POSS |
| T13 | nucleation / texture | CPU | ○ todo | NEW: Mg adatom binding+diffusion on clean vs Al-decorated Mg(0001) |
| T14 | self-discharge / overcharge mechanism | desk | ○ todo | synthesis from T2/T3/T8 |
| T15 | integration → REPORT_v2_master | both | ○ todo | map to ARTICLE_PLAN Part D / Fig 5 |

Legend: ● done · ◐ partial/in-progress · ○ todo · deferred = other node.

## v2→v3 reconciliation (the scientific crux, honest)
The v2 master report concluded "**not** redox chemistry" (four matched nulls + retracted Cl-abstraction): the **dominant** anion [AlPh₂Cl₂]⁻ reduces at **phenyl**, not Al. The **new ToF-SIMS data** (poly Al-ions ×0.02–0.5, confined ~90 nm vs bare ~350 nm) shows Al **does** co-deposit on bare — so the v3 task is to prove *which* channel deposits Al and *how poly blocks it*, without contradicting the v2 nulls. The resolution being tested:
- **Al that deposits comes from the Al-centred channel:** the minority **AlCl₄⁻** (only anion that reduces *at Al*, spin +1.14) **and** reductive decomposition of reduced phenyl-anions (Al–Cl cleavage → 83% Al-spin radical → Al⁰). The bulk-speciation nulls do **not** preclude this minority/decomposition route.
- **Poly blocks it two ways:** (i) **coordination/transport gating** — the cured network de-pairs + segregates the Al-anion ~7 Å from the front, 4.2× slower (v2 result, = ticket C2/T5/T6 kinetic route); (ii) **a Si-rich passivating SEI** (T7/T8) electronically blocks continued reduction, where the bare Al⁰/alloy SEI is electronically leaky (→ self-discharge, CE 27%).
This keeps the honest spine (transport not the bulk discriminator; the win is interfacial-compositional) and turns v2's gating result into the *mechanism* of Al exclusion.
