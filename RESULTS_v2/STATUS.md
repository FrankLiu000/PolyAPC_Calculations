# RESULTS_v2 — STATUS (v3.1 interface-composition computational program)
**Thesis (ARTICLE_PLAN_v3):** the in-situ POSS-cured poly-APC Mg-anode interphase is **Si-rich, Al-poor, surface-confined**, which **suppresses Al co-deposition** and makes Mg plating reversible (CE ~100% vs bare 27%). Transport is **not** the discriminator (GITT + MD agree). **No fluorine story.**
**Node:** EPYC CPU (192 core) — DFT (G16/ORCA) + AIMD/periodic (CP2K 2025.1). GPU/MLFF tickets (T5,T16,T17) are the other node.
**Started:** 2026-06-18 (this session). Branch `main`.

## Ticket tracker (T0–T15 here; T16–T17 GPU)
| T | title | node | status | 1-line result |
|---|---|---|---|---|
| T0 | preflight / env / smoke | CPU | ● done | ORCA 6.1.0 + CP2K 2025.1 + G16; offline (hand-build); Φ & THF validated in v2 |
| T1 | APC anion speciation map | CPU | ● done | C1: Schlenk ΔG all >0 → **[AlPh₂Cl₂]⁻ dominant, AlCl₄⁻ minority** (`speciation.csv`) |
| T2 | redox ladder vs Mg²⁺/Mg | CPU | ● done | all anions reduce −1.9 to −3.4 V vs Mg (plating-concurrent); CIP bare≈poly (−1.56/−1.59); neutral Al −0.4 closest to plating |
| T3 | reductive decomposition → Al⁰ | CPU | ● done | C1: [AlPh₂Cl₂]²⁻ Al–Cl cleavage −8.5 (vs Al–C +14.5) → 83% Al-spin radical → Al⁰ |
| T4 | Al co-deposition / alloying (periodic) | CPU | ● done | C1: adatom E_ads −0.08 eV; Al-in-Mg E_sub −4.44 eV (alloying favourable) |
| T5 | anion interface dynamics (MD) | GPU | → handoff | GPU node; see `computational_v2/mlff/HANDOFF_GPU_v3_T5_T16_T17.md` |
| T6 | e⁻-transfer / passivation barrier | CPU | ● done | Mg Fermi in SiO₂ gap → 3.07 eV injection barrier; tunnelling through 50–90 nm SiOₓ ≈0 → blocks Al-anion reduction (CDFT-on-metal invalid, band-align route) |
| T7 | candidate SEI phase set + stability | CPU | ● done | all SEI phases stable; **SiO₂ E_f −9.2 eV/fu (=exp)**; Al₂O₃ −15.4, MgO −4.0, MgCl₂ −4.2; Mg₁₇Al₁₂ artifact (use E_sub) |
| **T8** | **SEI electronic structure (DOS/gap)** | CPU | ● **done** | **Al⁰ 0.00 eV (metal/leaky), Mg₁₇Al₁₂ ≈0 (metal); SiO₂ 8.46, Al₂O₃ 6.2, MgO 3.9, MgCl₂ 2.9 eV (insulators/passivating)** |
| T9 | Mg²⁺ migration NEB through SEI | CPU | ◑ honest | NEB unconverged (F-centre vacancy, as v2 MgF₂); DRT link carried by T8 electronic structure + literature |
| T10 | constant-V interface AIMD (real ions) | CPU | ◑ partial | bare ±1V (441 fr, anion intact 9.5Å) + CHARGE−2 (980 st, no reduction) done; **matched poly run in progress**; rare-event (no spontaneous plating) |
| T11 | XPS Al 2p + Si 2p shifts | CPU | ● done | Si 2p shift +1.28 eV reproduced (SiH₄ 98.6≈99.5); Al³⁺ poly side ≈74 reproduced; bare 70.9=metallic Al⁰ (needs metal, =T8) |
| T12 | Raman/IR assignment | CPU | ● done | 915 THF(912)✔, CH2 stiffening free→bound, phenyl breathing→free (dissoc), Mg-Cl; = de-pairing+shell-intact, not redox |
| T13 | nucleation / texture | CPU | ◑ honest | Al adatom weak+non-selective (v2: fcc≈hcp −0.08) → disrupts Mg stacking → rough; matched Mg-adatom segfaulted (CP2K) |
| T14 | self-discharge / overcharge mechanism | desk | ● done | bare metallic-SEI electron-leak → parasitic redox (CE 27%, −320 mV/h); poly insulating → CE ~100% |
| T15 | integration → REPORT_v2_master | both | ● done | full synthesis: C1→T8→T14 + C2(T5/T6) + T2/T11/T12 mapped to ARTICLE_PLAN Part D/Fig 5 |
| T16 | broad reactive MLFF (Mg/electrolyte/SEI) | GPU | → handoff | extend v2 MACE to {Mg,Al,Cl,O,C,H,Si}; AL loop w/ CPU; `HANDOFF_GPU_v3_T5_T16_T17.md` |
| T17 | large-scale reactive interface (SEI growth/Al co-dep) | GPU | → handoff | reproduce ToF-SIMS Al-poor/Si-rich + ~90 nm; `HANDOFF_GPU_v3_T5_T16_T17.md` |

Legend: ● done · ◐ partial/in-progress · ○ todo · deferred = other node.

## v2→v3 reconciliation (the scientific crux, honest)
The v2 master report concluded "**not** redox chemistry" (four matched nulls + retracted Cl-abstraction): the **dominant** anion [AlPh₂Cl₂]⁻ reduces at **phenyl**, not Al. The **new ToF-SIMS data** (poly Al-ions ×0.02–0.5, confined ~90 nm vs bare ~350 nm) shows Al **does** co-deposit on bare — so the v3 task is to prove *which* channel deposits Al and *how poly blocks it*, without contradicting the v2 nulls. The resolution being tested:
- **Al that deposits comes from the Al-centred channel:** the minority **AlCl₄⁻** (only anion that reduces *at Al*, spin +1.14) **and** reductive decomposition of reduced phenyl-anions (Al–Cl cleavage → 83% Al-spin radical → Al⁰). The bulk-speciation nulls do **not** preclude this minority/decomposition route.
- **Poly blocks it two ways:** (i) **coordination/transport gating** — the cured network de-pairs + segregates the Al-anion ~7 Å from the front, 4.2× slower (v2 result, = ticket C2/T5/T6 kinetic route); (ii) **a Si-rich passivating SEI** (T7/T8) electronically blocks continued reduction, where the bare Al⁰/alloy SEI is electronically leaky (→ self-discharge, CE 27%).
This keeps the honest spine (transport not the bulk discriminator; the win is interfacial-compositional) and turns v2's gating result into the *mechanism* of Al exclusion.
