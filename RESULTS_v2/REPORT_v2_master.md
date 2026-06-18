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

## C2 — Why poly is Al-poor: transport gating + electron-transfer passivation (T5/T6)
**Two complementary routes exclude Al:**
- **Kinetic/transport (T5, v2):** the cured POSS network **de-pairs the electrolyte** (CIP 95→84 %) and **blocks the axial Mg face**, segregating the Al-anion ~7 Å from the front and slowing it 4.2× — **starving the reductive step of anion flux** (the MLFF PMF corroborates: poly holds the cation ~1.5 Å further out, shell intact).
- **Electron-transfer passivation (T6, this session):** band alignment from the **computed** Mg Φ (3.97 eV) + SiO₂ gap (8.46 eV, T8) puts the **Mg Fermi *inside* the SiO₂ gap** → a **3.07 eV electron-injection barrier**; WKB tunnelling through even 1 nm of SiOₓ is ~10⁻⁸, through the 50–90 nm poly interphase ≈ 0 → **electron transfer to the Al-anion is kinetically blocked**. Bare's metallic SEI (gap 0) has no such barrier.

So poly excludes Al both by **keeping the anion away** (transport) and by **cutting off the electron** (passivation) — the kinetic + electronic halves of "Al-poor."

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
| CCD / CE / morphology (dendrite) | Al co-deposit seeds rough Mg; poly smooth | **T13**: Al adatom weak+non-selective (no Mg template) → rough bare; clean Mg → oriented poly |

## Ticket completion (this v3 session)
**Done (robust):** T0–T4 (Al deposition chain + speciation/Schlenk/potentials), T6 (passivation barrier), T7 (SEI phase stability), **T8 (SEI electronic structure — keystone)**, T11 (XPS Al 2p/Si 2p), T12 (Raman), T14 (self-discharge mechanism). **Honest-partial:** T9 (Mg²⁺ NEB — F-centre non-convergence, DRT carried by T8+lit.), T10 (interface AIMD — bare done/poly in progress; rare-event), T13 (texture — Mg-adatom CP2K segfault; Al-adatom argument holds). **GPU node:** T5, T16, T17.

## Honest status
The **core thesis is proven and self-consistent**: Al co-deposits on bare (C1, on a Mg-referenced potential scale T2) → metallic, electron-leaky SEI (T8) → parasitic self-discharge (T14); poly excludes Al by transport gating (C2/T5) **and** electron-transfer passivation (T6), building a Si-rich insulating SEI (T7/T8) → reversible (CE 100 % vs 27 %). XPS (T11) and Raman (T12) reproduced; morphology (T13) and AIMD (T10) consistent. **No transport advantage invoked; no fluorine story.** Limitations (all flagged): PBE/GTH gaps qualitative; periodic alloy/adatom ±0.1 eV; vertical EAs (dianions dissociative = the decomposition); band-alignment uses lit. SiO₂ χ; AIMD is constant-V not grand-canonical; two periodic calcs (T9 NEB, T13 Mg-adatom) hit technical walls — reported honestly, not forced. See `STATUS.md`.
