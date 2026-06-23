# HANDOFF — writing the poly-APC paper (wet + dry lab combined)

**You are the article-writing agent.** Your job: turn the re-analysed wet-lab data + the completed
computation into one coherent manuscript. Everything you need is below; source files are mapped at the end.
The two governing specs are `ARTICLE_PLAN_v3_interface_composition.md` (wet-lab + narrative + figure plan) and
`RESULTS_v2/REPORT_v2_master.md` (computational proof). This handoff fuses them and tells you what to lead with,
what each figure shows, the exact numbers, and the lines you must NOT cross.

---

## 1. The thesis (one sentence, do not drift from it)
**Polymerising APC in-situ with POSS does not change how fast Mg²⁺ moves; it changes *what the Mg-anode
interphase is made of* — converting an Al-rich, dendrite-prone, parasitic SEI into a thin, Si-rich, Al-poor,
passivating layer — and that compositional switch is what makes Mg plating reversible (CE ~100 % vs 27 %).**

Working title: *"Interphase-by-design in magnesium batteries: an in-situ POSS network builds a silicon-rich,
aluminium-poor interphase that suppresses Al co-deposition."*

**Logical spine (the whole paper):** composition (Fig 3) explains performance (Fig 2) and morphology (Fig 4);
computation (Fig 5) explains the composition; the design rule (Fig 6) generalises it. **Transport is explicitly
NOT the discriminator** (proven three ways) — that is the paper's honest spine, not a weakness to hide.

## 2. HARD CONSTRAINTS (violating any of these breaks the paper)
1. **Interface story = Si (↑) / Al (↓) ONLY. NO fluorine / triflate / MgF₂ narrative.** F-species may exist in
   the data but are not a story element.
2. **Transport is NOT the win.** Mg²⁺ diffusion is equal (GITT poly 9 vs bare 8 ×10⁻¹⁵ cm²/s; MD poly 4.4×
   *slower*; t₊ = 0.50 both). Never invent a rate advantage. The win is interfacial-compositional.
3. **Always bare vs poly in parallel.**
4. **"poly has less Al" is a DEPTH + CHEMICAL-STATE claim, not a surface-at% claim** — state it precisely
   (see §6 caveat 1). XPS surface Al at% is actually similar (poly 4.11 vs bare 3.83).
5. **No fabrication.** Label models as models; PBE gaps are qualitative; report the honest ranges/caveats in §6.

---

## 3. WET-LAB EVIDENCE (the measured facts the paper rests on)
APC ≡ AlCl₃ + PhMgCl in THF → cation **[Mg₂(μ-Cl)₃(THF)₆]⁺**, anion family **[AlₓPhᵧClᵤ]⁻** (dominant
**[AlPh₂Cl₂]⁻**). bare = Mg cycled in liquid APC; poly = Mg cycled in POSS-polymerised APC.

- **ToF-SIMS (Fig 3 centrepiece)** — poly/bare negative-ion ratios, separator-corrected:
  - **Si ↑↑:** Si⁻ ×20, SiO₂⁻ ×30, SiO₃⁻ ×34 (POSS network).
  - **Al ↓↓:** AlO⁻ ×0.13, AlO₂⁻ ×0.26, Al⁻ ×0.08, **Al₂⁻ ×0.02**, Al₂O₃⁻ ×0.21, MgAlO⁻ ×0.18, C₂Al⁻ ×0.35.
  - **Depth (signal-half):** bare AlO⁻ **350 nm** vs poly **92 nm** → poly confines the SEI to a sharp ~50–90 nm
    surface layer; bare's Al penetrates 3–4× deeper. Mg/Cl/O comparable; poly slightly more organic.
- **XPS (chemical state)** — **the decisive single number is the Al 2p split: bare 70.88 eV (reduced/metallic/
  alloyed Al⁰, co-deposited) vs poly 73.98 eV (oxidised Al³⁺ residue)** — survives charge referencing (C1s
  differs only 0.06 eV). Si 2p: bare 99.5 eV/0.88 at% vs poly 101.7 eV/3.66 at% (×4.2, siloxane POSS).
- **XRD (deposit morphology)** — both metallic hcp-Mg, **no MgO, no crystalline Al/Mg–Al** (co-deposited Al is
  amorphous/SEI-bound). bare random/coarse (A002/A101 = 0.39); poly **texture-enhanced, conformal** (0.83 ≈ 2–3×
  random), larger crystallite. Use XRD only for Mg morphology (it can't see amorphous/dilute Al).
- **CV + GITT (performance)** — **CE: poly ~100 % (GITT 106 %) vs bare 27 %.** bare **self-discharges −320 mV
  (up to −540) per 1 h rest**, OCV turns over ~1.29 V then sags; poly relaxes −100 mV to a stable OCV. CV
  |i_pa/i_pc| poly ≈1.0 vs bare 1.2–1.34. **Mg²⁺ D near-identical (9 vs 8 ×10⁻¹⁵)** → transport not the lever.
- **Supporting (all consistent):** SEM bare dendritic / poly smooth; Aurbach CE poly 95.2 %, bare soft-short;
  CCD poly stable to 3.0 mA/cm² vs bare 3.1 V breakdown; cycling poly 842 cyc@0.5C / 3344@1C; DRT poly
  higher-but-**stable** interfacial impedance; Raman: Mg first-shell THF/Cl coordination preserved, gel adds
  polyether/POSS modes (915 retained, 1002→1034 shift).

## 4. DRY-LAB / COMPUTATIONAL EVIDENCE (what each result proves — all DFT-/AIMD-/MLFF-validated)
**One-paragraph proof:** bare-APC has a complete thermodynamically accessible route to deposited/alloyed Al⁰
(C1); poly blocks it by (i) coordination/transport gating that segregates the anion from the front and (ii) a
Si-rich passivating SEI that is a wide-gap insulator where bare's is metallic and leaky (C2/C3). Composition
explains reversibility — with no transport advantage.

- **C1 — Al deposits on bare (`results/C1_Al_reduction/`, `C1_TS_mechanism/`):** speciation puts **[AlPh₂Cl₂]⁻
  dominant, AlCl₄⁻ minority**; the **minority AlCl₄⁻ is the only anion that reduces *at Al*** (Al-spin +1.14;
  cation-pairing → 8× more reducible), AND the **reduced dominant anion decomposes** ([AlPh₂Cl₂]²⁻ Al–Cl cleavage
  ΔG −8.5 kcal/mol → 83 %-Al-spin radical → Al⁰); Al⁰ then **alloys into Mg (E_sub −4.44 eV)** → the 70.9 eV
  state. Mechanism: a **cation Cl-abstraction gateway (ΔG −16.8 kcal/mol)** makes a neutral, easier-to-reduce
  AlPh₂Cl; the reductive Al–Cl cleavages are **electron-transfer-gated, not bond-TS-gated** (the reduced
  chlorides shed Cl ~barrierless). On Mg(0001) the precursor chemisorbs (E_ads −1.82 eV) and surface Cl-strip is
  near-thermoneutral (+0.24 eV). *This is why the v2 "four nulls" don't contradict deposition — they concerned
  the dominant anion's primary site (phenyl); Al comes from the minority + decomposition channels.*
- **C3/T8 — SEI electronic structure (the keystone, `results/T8_sei_electronic/`):** k-point band gaps — **bare
  SEI carries metallic Al⁰ (0.00 eV) / Mg₁₇Al₁₂ alloy (~0.18 eV) → electron-leaky → sustains parasitic reduction
  → self-discharge/CE 27 %**; **poly SEI's Si-rich SiOₓ is a wide-gap insulator (SiO₂ 8.46 eV) → passivates →
  reversible/CE 100 %.** This is the *compositional* origin of reversibility.
- **C2 — why poly is Al-poor (T5/T6):** three anion-exclusion mechanisms — (i) general electrostatic EDL (both
  systems), (ii) **poly-specific kinetic network sequestration** (anion 2× more network-associated, **4.2×
  slower**, t₊ 0.50), (iii) **poly-specific electron-transfer passivation** (3.07 eV injection barrier over the
  SiOₓ interphase).
- **T16/T17 — reactive MLFF + interface MD (the direct simulation):** a DFT-validated MACE-MP-0 reactive MLFF
  (force MAE **30.7 meV/Å**) runs the *poly* interface that classical MD cannot; matched 500 ps MD shows the
  network holds the Al-anion **~1.65× further** from the electrode (`slabMin` poly 7.57 vs bare 4.58 Å).
- **★ The bias/EDL story — THREE independent lines converge (1.6–1.7×):** structural standoff **1.65×** (neutral
  MLFF) + static biased-DFT force-response **1.6×** (Al force responds to ±1e bias 0.42 bare vs 0.27 eV/Å poly) +
  dynamic field-modulated standoff **1.7×** (charge-conditioned MACE+LES under cathodic q=−2: bare 4.58→5.53 vs
  poly 7.57→9.21 Å). **Bare co-deposition AIMD:** the reductive ET is **contact-gated at ~2.5 Å** — not
  spontaneous, fires only when the anion is forced into contact; spin≈0 (metallic incorporation). This is the
  reaction-level capstone: bare *reaches* the reduction zone, poly is held ~3 Å beyond it.
- **Spectroscopy reproduced:** **T11** reproduces the **Al 2p 70.9/74.0 split** (metallic Al⁰ vs molecular Al³⁺)
  and **Si 2p 99.5/101.7** (elemental vs siloxane); **T12** assigns the Raman (915 THF C–O–C retained = shell
  intact, not redox). **T13** texture: a co-deposited Al is a *foreign* species disrupting Mg homoepitaxy (rough
  bare) — and Mg-adatom site-selectivity is **near-degenerate** (k-point −0.04 eV), so texture is *compositional*,
  not a site-energy effect. **T14** ties the leaky bare SEI to self-discharge.

## 5. COMPUTE ↔ WET-LAB MAP (cite this in Fig 5 / the SI; it's the paper's logic)
| Wet-lab observable | Computational explanation |
|---|---|
| ToF-SIMS Al ↓ (×0.02–0.5), confined ~90 nm | C1 (Al reducible on bare) + C2 (poly segregates ×4.2 slower) + C3/T8 (passivates) + T17 (1.65× standoff) |
| ToF-SIMS/XPS Si ↑ (×20–34 / ×4.2) | POSS/SiOₓ surface layer (T7) |
| **XPS Al 2p 70.9 vs 74.0 eV** | C1 + T4 + **T11** (metallic Al⁰ vs molecular Al³⁺ core-level shift) |
| XPS Si 2p 99.5 vs 101.7 eV | **T11** (elemental Si vs siloxane) |
| GITT CE 100 % vs 27 %, self-discharge −320 mV/h | **C3/T8** (bare metallic-leaky vs poly insulating) + C1 + T14 |
| GITT + MD Mg²⁺ D equal | honest spine — no transport advantage |
| XRD poly oriented/conformal vs bare coarse | **T13** (Al-as-foreign-codeposit; site-selectivity near-degenerate) |
| Raman 915 kept; 1002→1034 | **T12** (DFT vibrational assignment; coordination intact) |
| DRT poly higher-but-stable impedance | C3 (Mg²⁺ migration through thicker insulating poly SEI) |
| potential-driven EDL modulation | the 3-line bias result (1.6–1.7×) — static biased-DFT + dynamic charge-conditioned MD |

## 6. HONEST CAVEATS (write these precisely; reviewers will probe them)
1. **"Less Al" = depth-integrated + chemical-state, NOT surface at%.** Support it with ToF-SIMS depth (Al ions
   ×0.02–0.5, ~90 nm confinement) **and** the Al 2p state (oxidised residue vs metallic co-deposit) — never with
   surface at% (which is similar).
2. **XRD can't see amorphous/dilute Al** — no crystalline Mg–Al phase does NOT contradict co-deposition. XRD =
   Mg morphology only. Normalise by areal capacity before any "less Mg" claim.
3. **Boron = GF/D-separator artifact (exclude). Si has a separator baseline too** — only the poly excess
   (×20–34) is POSS.
4. **Computation is qualitative where flagged:** PBE/GTH band gaps underestimate (the metal-vs-insulator
   *distinction* is robust, the absolute SiO₂ 8.46 eV is inflated); periodic alloy/adatom ±0.1 eV; AIMD is
   constant-V not grand-canonical; one NEB (T9 Mg²⁺ barrier) hit a metal-slab SCF wall — carried by T8 + lit.
5. **The bias/EDL ratios carry a range** (structural 1.4–2.2×, headline ~1.65–1.7×; poly leg is slow-mode-limited)
   — report the range, not a false-precision single number. Three independent methods agreeing is the strength.

## 7. FIGURE PLAN (what data goes in each — full version in ARTICLE_PLAN Part B)
- **Fig 1 Concept & electrolyte** — in-situ POSS cure; APC speciation; hypothesis (anion reduction → Al
  co-deposition vs network suppression).
- **Fig 2 It works & it's reversible** — Aurbach CE, CCD, 0.5C/1C cycling, **GITT CE 100 % vs 27 % +
  self-discharge**, CV. Headline: reversibility, not rate.
- **Fig 3 Interphase composition (THE figure)** — ToF-SIMS ratio bars (Si ×20–34 ↑, Al ×0.02–0.5 ↓), depth
  profiles, 3-D maps; XPS Al 2p split (70.9/74.0) + Si 2p.
- **Fig 4 The deposit** — XRD texture + SEM (smooth vs dendritic) + EDS (Si-rich poly film).
- **Fig 5 Why: computation** — C1 reduction/co-deposition energetics + Mg-referenced potentials; C2 network
  suppression; C3/T8 SEI metal-vs-insulator gaps; T17 interface-MD standoff + the 3-line bias/EDL convergence;
  transport-equal (MD D, t₊) panel to kill the rate hypothesis; computed Al 2p/Si 2p shifts + Raman.
- **Fig 6 Mechanism & design rule** — integrated picture + "immobilise/segregate the reducible anion to engineer
  a benign, cation-derived, Si-passivated interphase."

## 8. FILE MAP
**Wet-lab data:** `ToF-SIMS/` (`processed/data/diagnostic_ions_corrected.csv`, `sei_depth.json`, figures) ·
`XRD_deposited_Mg/analysis_output/` · `Multi-Rate_CV+GITT/ANALYSIS_GITT_poly_vs_bare.md` + `analysis_outputs/` ·
prior `XPS/`, `Raman/`, `in_situ_DRT/`, `SEM+EDS_*`, electrochem `.txt`.
**Computation:** `RESULTS_v2/REPORT_v2_master.md` (the proof) + `STATUS.md`; per-ticket `results/<TID>/REPORT.md`
+ csv/json (C1_Al_reduction, C1_TS_mechanism, T5_anion_interface, T7/T8_sei_*, T11_xps, T12_raman, T13, T17_reactive);
MLFF + charged frames + the charge-conditioned recipe in `computational_v2/mlff/` (`incoming/*_labeled.xyz`,
`v3/CHARGE_CONDITIONED_MACE_recipe.md`); figures in `results/T5_anion_interface/fig_*.png`.
**Narrative spec:** `ARTICLE_PLAN_v3_interface_composition.md` (Parts A–E). Prior handoff
`HANDOFF_computational_v2_Al_and_wetlab.md` is superseded by the v3.1 framing.

**Where to start:** draft Fig 3 (ToF-SIMS + XPS composition) and the C1 reduction story first — the whole paper
hinges on **Al-poor / Si-rich**. Lead with composition, let performance and morphology follow, let computation
explain. No fluorine. No transport win.
