# T10 — Constant-potential interface AIMD with the real cation + Al-anion
**Objective (ARTICLE_PLAN C4):** Mg(0001) + electrolyte containing the **actual [Mg₂Cl₃(THF)₆]⁺ cation AND an Al-anion**, **bare vs poly**, under a **constant-potential (Dirichlet) field** — observe whether the Al-anion reduces/deposits on bare and is suppressed on poly.
**Method:** CP2K 2025.1, PBE-D3, DZVP-MOLOPT-SR-GTH/GTH-PBE, EPS_SCF 1e-5, NVT 300 K, 1 fs. Two-plate Dirichlet constant-voltage counter-electrode (implicit Poisson, V_D = ±1 V over ~47 Å ≈ 0.043 V/Å), Fermi-smeared, ADDED_MOS 400 — **field machinery validated** (v2 `bias_pilot_verdict.txt`: 50/50 steps, 0 SCF fails).

## Result so far
**Bare — ±1 V field, 441 frames (done, `bias_prod_bare.txt`):**
| quantity | value |
|---|---|
| Al-anion height off front | mean **9.46 Å** (min 9.31; last-half 9.47) — **stays solvent-separated** |
| cation Mg⁺ height / nearest slab-Mg | 8.59 / **5.64 Å** |
| Al–Cl148 / Al–Cl149 bonds | 2.24 / 2.21 Å, **frac>3 Å = 0.00 → intact** |

**Bare — CHARGE −2 + field explicit-electron run, ~980 steps (done):** the cation Mg stays **+2.06–2.08 over ~270 steps — no spontaneous reduction**.

**Poly — ±1 V field, matched run: IN PROGRESS** (job launched this session; 282-atom POSS-network interface; constant-V Poisson + SCF converging — produces frames slowly, resumable).

## Interpretation (honest)
Under an applied ±1 V field **and** with 2 extra electrons (CHARGE −2), the bare Al-anion **stays intact and ~9.5 Å off the plating front and does not reduce** on the accessible ps. This is the **rare-event result**: interfacial Al reduction/plating is an **activated, overpotential-driven event not reachable by equilibrium/short AIMD** — *exactly* consistent with **T2** (no anion reduces above the Mg plating potential; reduction is plating-concurrent) and the reason the **MLFF desolvation-PMF** (v2 §7b) and the **band-alignment passivation** (T6) routes were built. The matched poly run (in progress) is expected to show the same anion segregation (the network holds it further out) — confirming that **neither system plates spontaneously**, and the bare-vs-poly difference is the *rate*/gating, not a spontaneous AIMD event.

## Honesty / status — **partial**
- Bare field (441 frames) + bare CHARGE−2 (980 steps) **done**; **matched poly field run in progress** (single trajectory; the plan's ≥2 replicas × bare+poly not yet complete).
- Idealised constant-**VOLTAGE** Dirichlet counter-electrode, **not** grand-canonical constant-µ (CP2K 2025.1 lacks ESM/GC-SCF) — flagged.
- The activated reduction itself is **not** captured (rare event) — the deliverable is the **negative result** (no spontaneous plating, anion held off the front) + its consistency with T2/T6/T8; the reductive step stays DFT/hybrid.

**Provenance:** `bias_prod_bare.txt`, `biasprod_bare_access.txt` (v2); poly run `P0d_interface/inp/bias_prod_poly*` (in progress). Feeds ARTICLE_PLAN Fig 5; pairs with T2 (plating-concurrent reduction), T6/T8 (why poly suppresses it).
