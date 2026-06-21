# T5 — Anion interfacial sequestration (GPU/MD node)
### Does the cured POSS network keep the reducible Al-anion away from the Mg-anode reductive front?
*v3 ticket C2 "linchpin", GPU node. Pairs with EPYC's C1 reduction chemistry (T1–T4) and the reactive MLFF (T16/T17, blocked on EPYC's T10).*

> **Honest spine (do not violate):** bulk Mg²⁺ transport is NOT the discriminator (MD + GITT agree); the win is interfacial-compositional. This ticket asks a *kinetic* question about the **anion**: can it reach the anode to be reduced (→ Al co-deposition), and does the network impede that? It does **not** claim a transport advantage.

---
## ★ v3 UPDATE (2026-06-22) — Matched MLFF-MD interface: the standoff is REAL (updates R4's "null")

The reactive MLFF (T16/T17, model **r6**) finally enabled the **matched bare-vs-poly atomistic electrode
interface** that classical MD could not build (R4): MACE is geometry-based (no molecule unwrap), so the
percolating POSS network runs. **Matched r6 @ 0.5 fs + ForceCap60, 500 ps each, primary metric
`Al_slabMin` = 3D distance from the reducible Al to the nearest electrode Mg:**

| system | **Al–electrode min dist** | Al z-height | nCl | min | n |
|--------|--------------------------|-------------|-----|-----|---|
| **bare** | **4.58 ± 0.19 Å** | 4.18 Å | 2.00 | 3.90 Å | 16159 |
| **poly** | **7.57 ± 0.79 Å** | 3.67 Å | 2.00 | 5.52 Å | 16159 |

**→ ~1.65× standoff (gap 3.0 Å)** — the network holds the reducible anion ~3 Å further from the metal. (r5
`poly_ns` 486 ps cross-check: poly 10.3 Å ≈ 2.2×.) **This UPDATES R4 below** — the earlier "≈9 Å in both, null"
came from tiny single-ion cells; the matched interface shows a real standoff. *(Metric note: z-height is ~4 Å
in BOTH — misleading; the standoff is only visible in the 3D `slabMin`, the poly anion sits at similar height
but laterally/structurally offset.)*

- **Bare anion poised-but-UNreacted:** intact across the full stable 500 ps (nCl = 2 always, min 3.90 Å,
  **0 % of frames < 3.5 Å**, force-cap fired 0×). MLFF is conservative — it cannot do the Al³⁺→Al⁰ electron
  transfer; the reaction only appeared as the **pre-cap blow-ups at ~3.2 Å** (reactive onset beyond MLFF).
  **Reaction-level cross-check (EPYC AIMD, now in `RESULTS_v2/REPORT_v2_master.md`):** the reductive electron
  transfer is **contact-gated at ~2.5 Å — bare reaches that contact, poly is held ~3 Å beyond it** — and the ET
  itself is **rare-event** (no spontaneous reduction in the AIMD window). Independently confirms the MLFF picture
  (bare reaches the front / poly excluded) and locates the gate. A cathodic-DRIVEN AIMD to force the rare event
  is still requested (`AL_REQUEST_bare_codeposition_aimd.md`).
- **Independent EPYC biased-DFT cross (potential-driven EDL, `incoming/biased_RESPONSE.md`):** the force on the
  reducible Al responds to ±1 e bias **0.42 (bare) vs 0.27 eV/Å (poly) = 1.6× stronger in bare** — same bare/poly
  asymmetry as the structural standoff, independent line of evidence.
- **Honest convergence:** bare tight (σ 0.19 Å); **poly slow-mode-limited** (s1 ~8.6 / resumed seg2 ~7.0 Å;
  10–90 pct 6.5–8.6; range ~1.4–2.2× across model/window) — a slow oscillation, not a runaway. Headline ~1.65×;
  a pinned number needs multi-ns / enhanced sampling. The cheap external-`q·E` biased MD was **validated vs
  EPYC's 34 charged frames and FAILED** (captures only 10–30 %, blind to the bare/poly asymmetry) → any biased
  MLFF-MD must be **charge-aware**, not `q·E`.
- **Stability fix:** r6 = MACE-MP-0 FT + ZBL `pair_repulsion` + Agnesi (MAE 29 meV/Å); stable interface MD needs
  **0.5 fs** (reactive-front overshoot) **+ ForceCap60** (rare bulk spikes); cap ≈ 0 in production → physical.
- Figure `fig_matched_standoff.png`; code `mlff/v3/t17/final_analysis.py`, `mlff/v3/validate_qE.py`,
  `mlff/v3/build_charges.py`, driver `mlff/v3/interface_mlff_md.py` (argv6=dt, argv7=fcap, argv8=Efield).

---

## TL;DR
1. **Transport NULL confirmed for the canonical poly model** (4-POSS gel, never cleanly tested before — Story A.1 only did the swollen-8 artifact): D(cation) ×4.5 slower, D(anion) ×4.2 slower, **t₊ = 0.50 in both**, de-pairing f 0.046→0.13. Matches GITT (D≈equal) → kills the rate hypothesis.
2. **The cured network preferentially sequesters the Al-anion (bulk):** the anion is **~2× more network-associated than the Mg-cation** (47.5 % vs 24.7 % within 0.5 nm of the network; 80 % of anions within 0.7 nm) **and 4.2× slower**. The reducible anion is matrix-held and retarded.
3. **Bare reference (interface MD, 40 ns converged):** at a *neutral* electrode the **Al-anion reaches the Mg(0001) surface slightly closer than the cation** (closest approach 0.41 vs 0.47 nm; near-surface 0.033 vs 0.052 ions/nm²) — at equilibrium nothing excludes the anion from the bare anode.
4. **The network's sequestration is KINETIC** (slower + matrix-held → lower flux), **not an equilibrium standoff** — existing MLFF/AIMD put the anion ~9 Å off the front in **both** bare and poly (≈ null), and a poly *atomistic* interface is infeasible in classical MD (percolating network, below).
5. **NEW — under plating bias the anion is electrostatically excluded from the cathode** (40 ns, +0.3 V/nm field run): a clean electric double layer forms — anion **0.12× bulk at the cathode face vs 0.78× at the anode**, while the neutral electrode is symmetric (`fig_field.png`). → **Three independent mechanisms** keep the Al-anion off the plating front: **(i) electrostatic** field exclusion (this), **(ii) kinetic** network sequestration (#2), **(iii) electron-transfer passivation** by the Si-rich SEI (EPYC T6).

**Reconciles with v3:** the network's contribution to the Al-poor interphase is to **kinetically starve the anode of the reducible anion** (on top of the electrostatic bias-exclusion that operates even on bare); the decisive *reactive* suppression (reduction energetics, electron-blocking) is EPYC's C1/C3 + T6 + the reactive MLFF T17. We do not over-claim.

---

## Methods
**Systems.** Canonical bare-APC (`prod/bare`) and poly-APC = **4-POSS gel** (`prod/poly`), the campaign's equilibrated OPLS-AA boxes (3×100 ns replicates; cation [Mg₂(μ-Cl)₃(THF)₆]⁺, anion [Ph₂AlCl₂]⁻; scaled charges Mg +1.2).

**(1) Transport / de-pairing.** D via `gmx msd -mol` (COM, fit 20–80 ns, matched protocol, 3 reps each); t₊ = D₊/(D₊+D₋); free-carrier f = 1 − (Mg–anionCl contact fraction) from the **converged 70–100 ns** window (`analysis/solvation.py`; the slow ion-pairing equilibration is respected). Bare reused from Story A.1; poly computed here (`analysis/solv_poly_conv/`).

**(2) Bulk anion–network sequestration** (`storyT5/bulk_sequestration.py`, MDAnalysis on `prod/poly/prod.xtc`): per-frame minimum distance of each Al-anion and each Mg-cation to the covalent network (NET1, 10 119 atoms) and to its ether/POSS oxygens; contact fractions at 0.5 / 0.7 nm.

**(3) Bare Mg(0001) | electrolyte interface MD** (`storyT5/build_interface.py`, `analyze_interface.py`): a frozen, neutral, atomistic **Mg(0001) slab** (a = 3.209 Å matching EPYC's Φ=3.97 eV slab; 3 layers, 1794 Mg; UFF Mg LJ σ=0.269 nm ε=0.464 kJ/mol, q=0, comb-rule 3) + the equilibrated electrolyte in a **full-3D-PBC sandwich** (slab at bottom → two equivalent Mg(0001) interfaces via z-PBC; standard 3D PME, no vacuum/evaporation). EM → z-only NPT density-relax (slab position-restrained, refcoord-scaling=no) → **NVT 298 K, 40 ns** (frozen slab; `-nb/-pme/-bonded gpu`, *not* `-update gpu` — incompatible with frozen atoms). Density profile ρ(d) vs distance from the nearest electrode face (two faces folded), near-surface populations, closest approach, residence. *MODEL electrode: non-reactive, neutral implicit electrode — valid for ion approach/structure, not for reduction (that is EPYC's reactive AIMD/MLFF).*

## Results

### R1 — Transport null + de-pairing (canonical 4-POSS gel vs bare)
| metric (matched 20–80 ns, 3 reps) | bare | poly (4-POSS) | ratio |
|---|---|---|---|
| D cation [Mg₂Cl₃·6THF]⁺ (10⁻⁵ cm²/s) | 0.051 ± 0.004 | 0.011 ± 0.002 | **×4.5 slower** |
| D anion [Ph₂AlCl₂]⁻ | 0.050 ± 0.005 | 0.012 ± 0.002 | **×4.2 slower** |
| t₊ = D₊/(D₊+D₋) | 0.505 | 0.496 | **≈0.50 both** |
| free-carrier f (converged 70–100 ns) | 0.046 | 0.13 | de-pair ×2.8 |

Mg–polymer-O direct contact is only ~1 % → the de-pairing/sequestration is **matrix/tortuosity-driven, not direct cation–network binding.** Independently matches GITT (D ≈ 8–9×10⁻¹⁵ cm²/s both) → the rate hypothesis is dead.

### R2 — The network preferentially sequesters the Al-anion (bulk)
| (poly gel, bulk) | Al-anion | Mg-cation |
|---|---|---|
| median distance to network | **0.51 nm** | 0.55 nm |
| fraction within 0.5 nm of network (contact) | **47.5 %** | 24.7 % |
| fraction within 0.7 nm | **79.9 %** | — |
| median distance to ether/POSS-O | 0.71 nm | — |

The reducible anion sits in contact with the covalent matrix **~2× more often than the cation**, and diffuses **4.2× slower** than in bare. → in the gel the Al-anion is structurally held and kinetically retarded; its diffusive flux toward any reductive front is suppressed.

### R3 — Bare reference: the anion reaches the anode in the free liquid (40 ns)
Neutral Mg(0001) interface MD (NVT 298 K, **40 ns**, 8001 frames; 80 anions × 2 faces):
- The Al-anion profile shows the vdW depletion (<0.25 nm) then a **populated contact layer**; the anion's **closest approach (0.41 nm) is slightly closer than the cation's (0.47 nm)**, near-surface (<0.8 nm) populations anion 0.033 / cation 0.052 ions/nm². **No anion exclusion at a neutral Mg surface** — the anion freely contacts the anode in the liquid.
- Contrast partner to R2: with **no network** the anion contacts the anode; **with the network** (R1/R2) it is retarded (×4.2) and matrix-held (~2× the cation).

### R5 — Plating bias electrostatically excludes the anion from the cathode (40 ns field run)
A static **+0.3 V/nm** field (≈ the ±1 V/47 Å AIMD field, master §7) on the same bare interface drives a clean **electric double layer** the neutral run lacks (`fig_field.png`):

| anion density / bulk | neutral | +0.3 V/nm |
|---|---|---|
| anode face | 0.17 | **0.78** (anion accumulates) |
| **cathode face** | 0.20 | **0.12** (anion excluded) |
| cation at cathode / bulk | 0.15 | **0.40** (cation enriched) |

→ **Even on a bare electrode, plating polarization excludes the Al-anion from the cathode (the plating front) electrostatically** (0.12× bulk) while concentrating it at the counter-electrode — a *third*, field-driven exclusion mechanism on top of R2 (kinetic network sequestration) and EPYC's T6 (electron-transfer passivation), operating in the right direction for plating. *(Model: neutral frozen UFF wall + uniform field, no metal image-charge screening — the field is the physical lever, the double-layer response is the result.)*

### R4 — Equilibrium standoff is ≈ null, and a poly atomistic interface is infeasible
- Existing MLFF/AIMD (small single-ion cells): the anion sits **~9 Å off the front in *both* bare and poly** (master report §6) → the network does **not** create a larger *equilibrium* standoff. The effect is kinetic (R1/R2), not a thermodynamic surface repulsion.
- **A poly atomistic electrode interface cannot be built in classical MD:** NET1 is one covalent network percolating across every PBC face; a free electrode surface needs broken z-periodicity, but a percolating molecule has no consistent unwrap → GROMACS aborts (`mshift.cpp`, "inconsistent shifts over periodic boundaries"). Cutting the z-crossing bonds does not help (x,y percolation still breaks the shift map). Hence the network's anion effect is quantified in the **bulk** (where it is properly periodic) — R2.

## Honest caveats
- **Network = kinetic; bias = electrostatic (kept distinct).** The *network's* contribution is kinetic (slower + matrix-held → lower flux), **not** an equilibrium standoff (null in both at zero field). The electrostatic exclusion (R5) is a *separate* effect supplied by the applied plating bias even on bare — we don't conflate the two.
- **Model electrode.** Neutral, frozen, structureless-but-atomistic UFF Mg(0001) wall; non-reactive. Valid for ion approach/structure; the **reactive** Al-exclusion (reduction suppression, electron-blocking SEI) is EPYC's C1/C3 + reactive MLFF **T16/T17 (blocked on EPYC's T10)**.
- **No transport advantage invented** (guardrail honoured): bulk Mg²⁺ is *slower* in poly; the point is the *anion's* access to the anode.
- Interface bulk density ~5 % below the periodic reference (matched protocol → cancels in contrasts); residence/flux statistics are liquid-like and short — reported qualitatively.

## Provenance
Workspace `/lyz/Claude_workplace/polyAPC/storyT5/` — `build_interface.py`, `build_poly_interface.py` (infeasible, documented), `analyze_interface.py`, `bulk_sequestration.py`, `fig_T5.py`, `mdp/`, `bare/` (slab+interface+MD), `bulk/bulk_poly.json`, `analysis/profile_bare.csv`. Transport: `analysis/msd_rep/RESULTS.txt`, `analysis/solv_poly_conv/`. GROMACS 2025.1 (CUDA), LYZ-ROG. Figure `fig_T5.png`.
*Stage to branch `computational-v3-interface` (coordinate with EPYC) as `results/T5_anion_interface/` — NOT to `main`.*
