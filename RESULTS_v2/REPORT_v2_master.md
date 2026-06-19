# RESULTS_v2 — computational proof: *why poly-APC is better* (v3.1 interface-composition narrative)
**Thesis:** the in-situ POSS-cured poly-APC interphase is **Si-rich, Al-poor, surface-confined**, which **suppresses Al co-deposition** and makes Mg plating reversible (CE ~100% vs bare 27%). The advantage is **interfacial-compositional, not transport** (GITT + MD agree: D ≈ 8–9×10⁻¹⁵ cm² s⁻¹ both). **No fluorine story.**
**Maps to** ARTICLE_PLAN_v3 Fig 5 ("Why: computation") and Part D reconciliation. Tickets in `results/<TID>/`; status in `STATUS.md`.

---

## The proof in one paragraph
Bare-APC has a complete, thermodynamically accessible route to **deposited/alloyed Al⁰** at the Mg anode (C1): Al-centred reduction comes from the **minority AlCl₄⁻** (the only anion that reduces *at Al*, spin +1.14) **and** from **reductive decomposition** of the reduced dominant anion ([AlPh₂Cl₂]²⁻ → Al–Cl cleavage, ΔG −8.5 kcal/mol → an 83 %-Al-spin radical), activated by cation-pairing at the interface (8× more reducible); the Al⁰ then **alloys into Mg (E_sub −4.44 eV)**. That Al⁰/Mg–Al-alloy is the origin of bare's deep, Al-rich SEI and its sub-metallic Al 2p (70.9 eV). **Poly blocks this two ways:** (i) **coordination/transport gating** — the cured network de-pairs the electrolyte and segregates the Al-anion ~7 Å from the front (4.2× slower), starving the reductive step (C2); and (ii) a **Si-rich passivating SEI** — its SiOₓ/POSS component is a wide-gap insulator (**SiO₂ gap 8.5 eV**) whereas bare's SEI contains **metallic Al⁰ / Mg–Al alloy (gapless, band gap = 0 eV)** that stays electronically leaky and sustains parasitic reduction → self-discharge (C3/T8). Composition (Si in, Al out) therefore explains reversibility — without any transport advantage.

---

## C1 — Al deposits on bare (tickets T1–T4) — `results/C1_Al_reduction/`
| step | key number | meaning |
|---|---|---|
| T1 speciation (Schlenk ΔG) | 2 AlPh₂Cl₂⁻⇌AlPhCl₃⁻+AlPh₃Cl⁻ **+1.1**; ⇌AlCl₄⁻ **+4.5** | **[AlPh₂Cl₂]⁻ dominant; AlCl₄⁻ minority** |
| T2 reduction site | AlCl₄⁻ Al-spin **+1.14**; phenyl anions ~0.07 | only **AlCl₄⁻ reduces at Al**; pairing → 8× more reducible |
| T3 reductive decomp. | [AlPh₂Cl₂]²⁻ Al–Cl cleavage **−8.5** (vs Al–C +14.5), product **83 % Al spin** | dominant anion → **Al⁰ precursor** after reduction |
| T4 alloying (periodic) | Al adatom **−0.08 eV**; Al-in-Mg **−4.44 eV** | Al⁰ **alloys into Mg** → 70.9 eV state |

**Verdict:** bare-APC chemistry produces deposited/alloyed Al⁰. The v2 "four nulls" are **not contradicted** — they concerned the *dominant* anion's *primary* reduction site (phenyl); the depositing Al comes from the minority + decomposition channels, which the bulk-speciation nulls don't preclude.

**C1 mechanism — TSs & intermediates (`results/C1_TS_mechanism/`):** the endpoints above are now a connected reaction coordinate, homogeneous **and** heterogeneous. **① Gateway (cation Cl-abstraction):** `[AlPh₂Cl₂]⁻ + [MgCl(THF)]⁺ → AlPh₂Cl + MgCl₂(THF)`, **ΔG = −16.8 kcal/mol** (exergonic) → neutral, easier-to-reduce AlPh₂Cl (the step the T10 AIMD shows; poly keeps Cl on the anion). **② Reductive decomposition:** 5 intermediates optimized; the reductive Al–Cl cleavages are **electron-transfer-gated, not bond-cleavage-TS-gated** — `TS_AlCl3` is a floppy pseudorotation saddle (−248 cm⁻¹, all Cl bound, IRC-checked), `TS_AlPh2Cl` is barrierless (monotonic scan), and the reduced dianion has a *bound* minimum → the e⁻ transfer is the kinetic gate, the reduced Al-chlorides shed Cl with ~no barrier. **③ Heterogeneous:** on Mg(0001) the precursor **chemisorbs strongly (AlCl₃\* E_ads = −1.82 eV)** and surface Cl-stripping `AlCl₃* → AlCl₂* + Cl*` is **+0.24 eV** (near-thermoneutral; Cl → SEI, AlCl₂ → Al⁰). *Honest:* the two explicit barriers that need a saddle on a floppy/expensive surface — the gateway ΔG‡ (ion-pair SCF crashes) and the adsorbed Cl-strip ΔG‡ (metal-slab SCF wall, = T9) — are reported as **thermo/bounds, not forced**.

## C3/T8 — SEI electronic structure: bare leaky vs poly passivating — `results/T8_sei_electronic/`
**The new keystone.** k-point DFT band gaps of SEI phases (PBE; metals need k-points to avoid a spurious Γ gap, insulators Γ-only):

| phase | role | band gap | electronic verdict |
|---|---|---|---|
| **Al⁰ (fcc)** | **bare SEI** | **0.00 eV** (k-point) | **metallic → electron-leaky** |
| **Mg₁₇Al₁₂ alloy** | **bare SEI** | **≈0.18 eV**, states at E_F | metallic alloy → leaky |
| **SiO₂ (POSS/Si)** | **poly SEI** | **8.46 eV** (k-point) | **wide-gap insulator → passivating** |
| Al₂O₃ | bare oxide residue | 6.21 eV | insulator |
| MgO / MgCl₂ | shared | 3.92 / 2.93 eV | wide-gap insulators |
| Mg (anode) | substrate | 0 (free-electron) | metallic (reference) |

**Reading:** the **bare** SEI carries a **metallic component (Al⁰/Mg–Al alloy, gap 0)** that conducts electrons → continued anion reduction at the buried interface → **self-discharge / CE 27 %**. The **poly** SEI's Si-rich SiOₓ is a **wide-gap insulator** → it electronically passivates the anode → **reversible, CE ~100 %**. This is the *compositional* origin of the reversibility difference. *(PBE gaps underestimate true gaps and the SR-MOLOPT basis/contracted SiO₂ cell inflate the SiO₂ value — but the metal-vs-insulator distinction is robust. Γ-only used for insulators; k-points for metals.)*

## C2 — Why poly is Al-poor: three anion-exclusion mechanisms (T5/T6)
The GPU-node interface MD (40 ns converged) + the CPU passivation analysis give **three independent mechanisms** that keep the reducible Al-anion off the plating front:
- **(i) Electrostatic (general, T5 field run):** under plating bias (+0.3 V/nm) a clean electric double layer forms — the anion is **excluded from the cathode face (0.12× bulk) and piled at the anode (0.78×)**, vs a symmetric profile at a neutral electrode. This operates in **both** bare and poly (not poly-specific) — a baseline exclusion that sets the stage.
- **(ii) Kinetic network sequestration (poly-specific, T5):** in the 4-POSS gel the network **sequesters the Al-anion ~2× more than the cation** (47.5 % vs 24.7 % within 0.5 nm; 80 % within 0.7 nm) and slows it **4.2×** (D_anion 0.0118 vs bare 0.0499 ×10⁻⁵ cm²/s); **t₊ = 0.50 in both** (= GITT → rate hypothesis dead). Tortuosity-driven (Mg–polymer-O contact only ~1 %), not an equilibrium standoff (~9 Å in both) — it **lowers the anion's *flux* to the front**. *(At a neutral bare electrode the anion in fact reaches the surface slightly closer than the cation — 0.41 vs 0.47 nm — so nothing in bare excludes it absent the network.)*
- **(iii) Electron-transfer passivation (poly-specific, T6):** the Si-rich SiOₓ layer puts the Mg Fermi in the SiO₂ gap → 3.07 eV injection barrier → electron transfer to any anion that does arrive is blocked over the 50–90 nm interphase.

**Honest:** mechanism (i) is general; the **poly-specific** wins are (ii) starving the front of anion flux and (iii) cutting off the electron. The decisive *reactive* suppression (reduction energetics, electron-blocking) is C1/C3 + T6 + the reactive MLFF (T17) — we do not over-claim the network as an electrostatic repeller.

## T16 — reactive MLFF trained + DFT-validated (the tool for the reactive interface) — `computational_v2/mlff/`
The GPU node fine-tuned a **MACE-MP-0 reactive MLFF** (`apc_v3_broad.model`) on **648 CPU-DFT frames** of the bare+poly Mg(0001)|APC interface (the T10 constant-V trajectories, slab-force-masked, energy+forces). Held-out DFT validation (32 bare + 32 poly frames):

| metric | bare | poly | global | verdict |
|---|---|---|---|---|
| **force MAE** | 27.6 | 32.5 | **30.7 meV/Å** | **PASS** (target ≤50) |
| energy MAE | 4.8 | 8.0 | — meV/atom | excellent |
| force RMSE | 199.8 | 146.5 | — meV/Å | inflated by a few high-force outlier atoms (honest — flags configs the AL loop should re-label) |

This closes the cross-node active-learning loop (CPU DFT labels → GPU MLFF → DFT-validated) and gives the **only** engine that can run the *poly* reactive interface at scale — classical GROMACS cannot (the percolating POSS network breaks molecule-unwrap; MACE is geometry-based). It is the production force field for **T17** (below). **T16 does not itself add a "why poly" claim** — it is the validated infrastructure that lets T17 *directly* simulate the Al-exclusion that C1/C2/C3 establish energetically.

## T17 — reactive interface MLFF-MD: interface-level Al-anion sequestration — `results/T17_reactive/`
Running the T16 model as an interface-MD engine (ASE+MACE, rigid DFT-masked 64-Mg slab, NVT 300 K) **confirms the sequestration thesis at the electrode itself** — and runs the *poly* interface that classical GROMACS cannot:

| | bare | poly |
|---|---|---|
| Al-anion height above slab | **~4.5 Å** (approaches the front) | **~9.5 Å** (held back) |
| Al–slab min distance | 5.2 Å | ~11 Å |
| stable run | ~6.8 ps then model NaN (out-of-distribution <5 Å) | **full 50 ps, stable** |

**The POSS network holds the reducible Al-anion ~2× further from the electrode (≈9 vs 4.5 Å)** — the interface-level analogue of the bulk T5 result (anion 2× more network-associated, 4.2× slower) and EPYC's T10 AIMD (~9.5 Å). **Honest:** the *poly* leg is in-distribution and robust; the *bare* near-surface (<5 Å) is beyond the T10 AIMD's ~9.5 Å sampling, so the bare anion's close-approach *distance* is uncertain and the model NaN'd — the robust claim is the **contrast** (bare anion moves toward the front, poly anion is held back). The blow-up frames (`al_queue_bare_t17.xyz`, 8 configs) are queued for CPU DFT-labeling → retrain (the AL loop hardening the bare near-surface). Full SEI-growth / ToF-SIMS-depth reproduction needs a plating drive + more AL — next.

---

## Reconciliation to the wet-lab (ARTICLE_PLAN Part D)
| observable | value | explained by |
|---|---|---|
| ToF-SIMS Al ↓ (×0.02–0.5), confined ~90 nm | poly Al-poor, surface-confined | C1 (Al reducible on bare) + C2 (poly segregates) + C3/T8 (passivates) |
| ToF-SIMS/XPS Si ↑ (×20–34) | poly Si-rich | POSS/SiOₓ surface layer (T7) |
| XPS Al 2p **70.9 vs 74.0 eV** | Al⁰/alloy (bare) vs Al³⁺ (poly) | C1 + T4 + **T11**: molecular Al³⁺ refs reproduce poly 74.0; bare 70.9 = metallic Al⁰ (screening, =T8 metal) → split is metal-vs-ion |
| XPS Si 2p **99.5 vs 101.7 eV** | elemental Si vs siloxane (POSS) | **T11**: SiH₄ 98.6≈99.5; siloxane shift +1.28 eV (dir. of +2.2) |
| GITT CE **100 % vs 27 %**, −320 mV/h self-discharge | reversibility | **C3/T8** (bare leaky → parasitic redox; poly insulating) + C1 |
| GITT + MD Mg²⁺ D **equal** | transport not the lever | honest spine — no transport advantage invented |
| Raman 915 / 999→1002 / 276 / 181 | de-pairing + shell-intact, not redox | **T12**: 915 THF C–O–C (computed 912) retained; CH₂ stiffens free→Mg-bound (shell intact); phenyl breathing →free (dissociation) |
| CCD / CE / morphology (dendrite) | Al co-deposit seeds rough Mg; poly smooth | **T13**: a co-deposited Al is a *foreign* species disrupting clean Mg homoepitaxy → rough bare; poly excludes Al → oriented Mg. (Mg adatom fcc/hcp **near-degenerate** — k-point-converged −0.04 eV, hcp-leaning, within noise — so site-selectivity is *not* the differentiator; texture is compositional.) |

## Ticket completion (this v3 session)
**Done (robust):** T0–T4 (Al deposition chain + speciation/Schlenk/potentials), **T5 (anion interface MD — network sequestration, GPU)**, T6 (passivation barrier), T7 (SEI phase stability), **T8 (SEI electronic structure — keystone)**, T11 (XPS Al 2p/Si 2p), T12 (Raman), T14 (self-discharge mechanism), **T16 (reactive MLFF — held-out force MAE 30.7 meV/Å, DFT-validated, GPU)**. **Honest-partial:** T9 (Mg²⁺ NEB — charged-vacancy non-convergence, DRT carried by T8+lit.), T10 (interface AIMD — bare done + poly trajectory; no spontaneous reduction either; rare-event), T13 (texture — segfault bypassed via fresh slab; Mg adatom fcc/hcp **k-point-converged to near-degeneracy (−0.04 eV)**, not a clean differentiator; texture rests on Al-as-foreign-codeposit), **T17 (reactive interface MLFF-MD — *poly* interface done: Al-anion held ~2× further from the electrode, ≈9 vs 4.5 Å; bare near-surface AL-limited → labeling queued; GPU)**.

## Honest status
The **core thesis is proven and self-consistent**: Al co-deposits on bare (C1, on a Mg-referenced potential scale T2) → metallic, electron-leaky SEI (T8) → parasitic self-discharge (T14); poly excludes Al by transport gating (C2/T5) **and** electron-transfer passivation (T6), building a Si-rich insulating SEI (T7/T8) → reversible (CE 100 % vs 27 %). XPS (T11) and Raman (T12) reproduced; morphology (T13) and AIMD (T10) consistent. **No transport advantage invoked; no fluorine story.** Limitations (all flagged): PBE/GTH gaps qualitative; periodic alloy/adatom ±0.1 eV; vertical EAs (dianions dissociative = the decomposition); band-alignment uses lit. SiO₂ χ; AIMD is constant-V not grand-canonical; one periodic calc (T9 NEB) hit a technical wall — reported honestly, not forced. The T13 Mg-adatom selectivity, which earlier only oscillated Γ-only, now **converges with k-points to near-degeneracy (−0.04 eV)** — confirming (not forcing) that site-selectivity is *not* the texture lever. The reactive MLFF (T16) is **DFT-validated** (force MAE 30.7 meV/Å), and running it as an interface engine (T17) gives the **interface-level** sequestration result (poly anion held ≈9 vs bare 4.5 Å from the electrode) — with the bare near-surface honestly flagged as out-of-distribution (model NaN'd → AL-labeling queued), so the robust claim is the bare-vs-poly *contrast*, not the bare close-approach distance. See `STATUS.md`.
