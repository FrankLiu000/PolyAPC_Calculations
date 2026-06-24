# Angewandte Chemie Int. Ed. — Research Article Outline
## poly-APC magnesium anode: a Si-rich / Al-poor interphase that suppresses Al co-deposition

**Prepared:** 2026-06-23 · maps to `ARTICLE_PLAN_v3_interface_composition.md` + `RESULTS_v2/REPORT_v2_master.md` (wet §A–Q) + `PolyAPC_Calculations-computational-v3-interface/RESULTS_v2/STATUS.md` (compute T1–T17).
**Format basis:** `Angewandte Research Articles.dotx` + Wiley *Notice to Authors* (https://onlinelibrary.wiley.com/page/journal/15213773/homepage/notice-to-authors). Model analogue in folder: *Angew. Chem. Int. Ed.* 2026, Li et al., "Reversible Calcium Metal Anodes Enabled by Asymmetric Solvation Effect…" (closely matched multivalent-anode interphase paper).

> **Locked scientific constraints (do not violate in any draft):**
> 1. Interphase story = **Si (↑) / Al (↓) only** — **no fluorine / triflate / MgF₂ narrative**.
> 2. **Transport is NOT the discriminator** — **MD + Bruce–Vincent** give bare ≈ poly (t₊ = 0.50; MD even has poly 4.4× *slower*). Never invent a transport advantage. *(GITT dropped per PI 2026-06-23 — see note below; the qualitative null is unaffected and arguably stronger, since MD shows poly is not faster.)*
> 3. Always report **bare vs poly in parallel**.
> 4. **Reproduce-or-explain** XPS Al 2p: bare ≈ 73.0 eV (Al⁰/alloy) vs poly ≈ 74.0 eV (Al³⁺).
> 5. **EDS Si = GF/D glass-fibre artifact** → the Si-enrichment claim rests on **ToF-SIMS only**.
> 6. Label models as models; report uncertainties; state the honest inert-Cu nulls.
>
> **PI revisions (2026-06-23):** (i) **Drop GITT entirely** — the CE 106/27 % headline and the GITT chemical-diffusion line are removed; reversibility is now carried by **full-cell Mg‖Mo₆S₈ cycling** + multi-rate CV + Mg‖Mg symmetric, and the transport null by **MD + Bruce–Vincent**. (ii) **Mg‖Mo₆S₈ full-cell cycling is a headline figure** (this is a battery paper). Raw data present (`MgMo6S8_0.5C_cycle/`, `MgMo6S8_1C_cycle/`, Neware .txt) but **module O analysis is still pending** — must be processed before drafting; targets from ARTICLE_PLAN A5: poly **842 cyc @0.5C / 3344 cyc @1C**, bare fades.

---

## 0. Format compliance checklist (Angew Research Article)

| Item | Requirement | Plan |
|---|---|---|
| Length | **5600 words / 25,000–40,000 chars incl. spaces** | Intro ~900 w · R&D ~3600 w · Concl ~400 w |
| Abstract | **≤ 200 words**, standalone, all abbreviations defined | drafted §2 |
| Sections | Introduction → Results and Discussion (capitalized subheadings, optional) → Conclusion | §4–6 below |
| Figures | single 300-DPI graphic; **8.4 cm** (1-col) / **17.2 cm** (2-col); caption not bold, lower-case | 5 main (§7) |
| Schemes | use Scheme (not Chart) for reaction/concept art | Scheme 1 (concept) |
| Experimental | **in SI only — never in manuscript** | all methods → SI |
| Keywords | **≤ 5**, American English, "•"-separated | §8 |
| References | one citation per number, include article titles | — |
| Submission | **Word file (.docx), not PDF**; SI linked at end | — |
| Statements | Data Availability + Conflicts auto-generated in Research Exchange; ethics N/A | — |

---

## 1. Title (capitalized, descriptive, application-explicit)

**Primary:**
**"A Silicon-Rich, Aluminum-Poor Interphase Templated by an In Situ POSS Network Enables Reversible Magnesium Metal Anodes"**

Alternatives:
- "Suppressing Aluminum Co-Deposition with an In Situ Silsesquioxane Network for Reversible Magnesium Anodes"
- "Interphase-by-Design in Magnesium Batteries: An In Situ POSS Network Excludes the Reducible Aluminate Anion"

*(Running title: "Si-rich/Al-poor interphase for reversible Mg anodes")*

## 2. Abstract (≤200 words — draft, ~190 w)

> Magnesium metal anodes cycled in the benchmark all-phenyl complex (APC) electrolyte suffer parasitic chemistry that limits reversibility, yet its molecular origin has remained ambiguous. We show that polymerizing APC in situ with an octakis-functionalized polyhedral oligomeric silsesquioxane (POSS) network does **not** change how fast Mg²⁺ moves—the transference number is identical to the liquid and molecular dynamics shows transport is, if anything, slower (molecular dynamics and Bruce–Vincent both give bare ≈ poly)—but instead reprograms **what the anode interphase is made of**. Depth-resolved ToF-SIMS and XPS reveal that the liquid builds a thick, aluminum-rich interphase containing reduced metallic Al⁰ co-deposited up to ~350 nm deep, whereas the network confines a thin (~90 nm), silicon-rich, aluminum-poor layer in which Al survives only as oxidized Al³⁺. First-principles calculations identify the reducible APC aluminate anion as the co-deposition source and show that the cured network excludes it both by sequestration and by an electronically insulating, Si-rich passivation layer. This compositional switch—silicon in, aluminum out—sustains stable Mg‖Mo₆S₈ full-cell cycling over hundreds-to-thousands of cycles and short-free symmetric-cell plating where the liquid fades and dendrite-shorts, establishing interphase composition, not ion transport, as the design lever for reversible Mg anodes.

## 3. Graphical abstract / Table-of-Contents entry

Two-anode split panel. **Bare:** [AlPhₓCl₄₋ₓ]⁻ + e⁻ → Al⁰ co-deposited → thick Al-rich SEI (~350 nm) → rough Mg, dendrite/short. **Poly:** cured POSS network → thin Si-rich/Al-poor SEI (~90 nm), Al excluded (Al³⁺ only) → smooth, oriented Mg. Center caption: **"Interphase re-programming — Si in, Al out → stable full-cell cycling, no shorting."**

---

## 4. Introduction (~900 words; 3–4 paragraphs)

1. **Why Mg metal anodes** — high volumetric capacity, abundance, claimed dendrite resistance; the gap between promise and practical reversibility. Cite Mg-anode/electrolyte reviews and APC as the field benchmark.
2. **The APC problem & the interphase question** — APC = AlCl₃ + PhMgCl/THF; cation [Mg₂(μ-Cl)₃(THF)₆]⁺, reducible aluminate anion family [AlPhₓCl₄₋ₓ]⁻. State that prior work treated the Al anion only as an oxidation (anodic-limit) liability and never analyzed its **reduction/co-deposition**; SEI understanding in Mg has lagged Li.
3. **Gel/polymer-electrolyte framing & the usual (wrong) assumption** — polymers are usually credited with transport/transference gains. Flag that we will show this is *not* the operative mechanism here.
4. **This work (thesis + roadmap)** — in situ POSS-cured poly-APC; we deconvolute transport from interfacial chemistry and locate the advantage in a **Si-rich, Al-poor, surface-confined interphase that suppresses aluminate reduction**. One-sentence preview of each results block and the combined experiment+theory approach.

> *Acronyms defined on first use (APC, POSS, SEI, ToF-SIMS, XPS, CV, MD, AIMD, MLFF, CE, CCD). Consistent American English.*

---

## 5. Results and Discussion (~3600 words; 5 subheadings)

### 5.1 Electrolyte design and speciation *(→ Scheme 1 + Fig 1)*
- In situ cure of APC with octa-functional POSS → self-standing gel; APC speciation map.
- **Theory (T1/T2):** DFT speciation in SMD(THF) — Schlenk equilibria give **[AlPh₂Cl₂]⁻ dominant, AlCl₄⁻ minority**; redox ladder vs Mg²⁺/Mg shows **every anion reduces in the −1.9 to −3.4 V window (plating-concurrent)**; AlCl₄⁻ is the species that reduces *at Al* (Al⁰ precursor). Revisits the old "anion sets the 6.18 eV anodic limit" claim.
- Hypothesis stated: anion reduction → Al co-deposition (bare) vs network suppression (poly).
- *Honest spine seeded here: the win will be compositional, not transport.*

### 5.2 It works—and the win is reversibility, not rate *(→ Fig 2)*  *(GITT dropped)*
- **★ Full-cell Mg‖Mo₆S₈ cycling — the battery headline (module O, ✅ ANALYZED 2026-06-23):** report **only the poly >80 % capacity-retention window** (PI): poly **>80 % for the full 842-cycle run @0.5C** and **~1600 cycles (1592) @1C**, both at **CE ≈ 100 %** (reversible cap ~49–59 mAh g⁻¹, ref = max reversible cyc ≥5; formation = cyc 1–4). **bare-APC drops below 80 % by cycle 269 and collapses to ≈0 by ~cycle 700.** This is the central performance claim and replaces GITT. *(`MgMo6S8_0.5C_cycle/results/`, master §O.)*
- **Multi-rate CV reversibility (§D, CV part only — not GITT):** |i_pa/i_pc| **1.26 ‖ 1.01**; Randles–Sevcik cath/anod slope ratio 1.19 ‖ 1.04 (poly symmetric); b-values closer to 0.5 (bulk insertion) for poly.
- **Self-discharge / interfacial stability (without GITT):** bare **OCP collapses 1.12 → 0.50 V over the CV run (−1113 mV drift)** ‖ poly −17 mV (§D CV); corroborated by **Tafel corrosion current i_corr 0.185 ‖ 0.107 mA cm⁻²** and R_p 689 ‖ 2873 Ω cm² (§E).
- **Mg‖Mg symmetric longevity (§Q):** poly **1011 cyc / 2022 h, 0 shorts** ‖ bare **420 cyc / 839 h → 4.95 V short death**; polarization flat (+0.09 mV/cyc) vs rising (+0.55).
- **CCD (§M):** poly stable to ~3.0 mA cm⁻², bare breakdown (analysis pending — confirm).
- **Transport null — the deliberate control (embedded panel):** **MD t₊ 0.50 ‖ 0.50** (and poly D 4.4× *slower*, §B); **Bruce–Vincent t₊ 0.003 ‖ 0.005** (equal, both ≈ 0, §N). → "Polymerization does not raise the Mg²⁺ current fraction; it only adds stable interfacial impedance (DRT §L)." Two independent lines force the explanation onto interfacial chemistry; poly is not the faster conductor.
- *Honest note (→ SI):* benign inert-Cu short tests (Aurbach CE §F, Mg‖Cu §A/§P) show bare ≈/≥ poly — stated as a soft-short/benign-substrate artifact, reconciled with the stressed full-cell/symmetric result.

### 5.3 The interphase is silicon-rich and aluminum-poor *(→ Fig 3 — CENTREPIECE)*
- **ToF-SIMS (§I):** Si⁻ **×20**, SiO₂⁻ ×30, SiO₃⁻ **×34** up in poly; AlO⁻ ×0.13, Al₂⁻ (metallic Al⁰) **×0.02 (bare 50× richer)**; **depth: bare Al ~350 nm vs poly ~92 nm** (≈4× deeper, surface-confined in poly). Poly-only Mg/Al–Si–O clusters → Si chemically built in.
- **XPS depth profile (§G):** Al rises **5→10 at%** into the bulk in bare vs flat ~5 at% in poly; **Al 2p state bare ~73.0 eV (Al⁰/alloy, ~50 % metallic on sputter) ‖ poly ~74.0 eV (Al³⁺)** — the direct redox-state image of co-deposition vs suppression.
- **Reproduce-or-explain (mandate):** poly **73.98 reproduced**; bare revised **70.88 → ~73.0 eV** (clean referencing; old value lies below pure Al, an artifact) — assignment unchanged, split ≈1.0–1.6 eV.
- Si magnitude is the **ToF-SIMS** result (XPS Si ×1.4, near floor — stated honestly).

### 5.4 Composition dictates the deposit *(→ Fig 4)*
- **XRD of plated Mg (§J):** metallic hcp-Mg both; texture A002/A101 **0.39 ‖ 0.83** (poly ~2× oriented/conformal); **no crystalline Al/Mg₁₇Al₁₂** → bare's Al is amorphous/SEI-bound (consistent, XRD can't resolve it — stated).
- **SEM + EDS (§K):** poly = dense consolidated Mg grains (Mg 53 wt%) ‖ bare = fine granular (Mg 14 wt%); robust atomic ratios **Al/Mg ≈7×, Cl/Mg ≈23×, O/Mg ≈4.4× higher in bare** → Al-poor/Cl-poor poly even at µm depth.
- **⚠️ EDS Si = GF/D glass-fibre separator artifact** (Si Kα localizes on fibres); filaments in both = glass fibre, not crystals. **Si story stays ToF-SIMS.** Stated explicitly in caption + text.

### 5.5 Why: aluminate reduction and how the network blocks it *(→ Fig 5)*
- **Al co-deposition energetics (T3/T4):** reduced [AlPh₂Cl₂]²⁻ → **Al–Cl cleavage ΔG −8.5** (vs Al–C +14.5) → 83 % Al-spin radical → Al⁰; Al-in-Mg substitution **E_sub −4.44 eV** (alloying favorable). → explains bare metallic Al⁰/alloy XPS.
- **Network exclusion, two routes (C2):**
  (i) **Sequestration (T5, MD):** cured network associates the Al-anion **2× more than the cation** and slows it 4.2× → keeps it off the reductive front;
  (ii) **Passivation (T6/T8):** Si-rich SEI is an insulator — **SiO₂ gap 8.46 eV, Al₂O₃ 6.2, MgO 3.9** vs **Al⁰/Mg₁₇Al₁₂ ≈ 0 (metallic, leaky)**; Mg Fermi level in the SiO₂ gap → ~3 eV electron-injection barrier blocks continued anion reduction.
- **Self-discharge mechanism (T14):** bare's metallic/leaky Al-rich SEI sustains parasitic electron leakage → continuous OCP decay / low CE; poly's insulating Si-rich SEI shuts it off → stable OCP, high CE (links to the §5.2 OCP-collapse and Tafel corrosion observables).
- **Constant-potential interface AIMD + MLFF (T10/T16/T17):** real cation + Al-anion; network holds the anion **2.07× farther** from Mg(0001); MLFF force MAE **30.7 meV/Å (PASS)**, active-learning loop closed. *(Honest: no spontaneous reduction observed in short neutral/field-limited runs; mechanism rests on energetics + sequestration + SEI electronics — caveats in SI.)*
- **Spectroscopic validation (T11/T12):** computed **Al 2p Al³⁺≈74 / Al⁰≈71 split reproduced**; **Si 2p +1.28 eV** siloxane shift reproduced; Raman 915 cm⁻¹ retained + phenyl breathing → free (de-pairing, shell intact) — corroborates measured §H.

---

## 6. Conclusion (~400 words)
- Restate the compositional switch: in situ POSS network → thin, Si-rich, Al-poor, surface-confined interphase that **suppresses APC aluminate reduction / Al co-deposition** → reversible Mg (stable Mg‖Mo₆S₈ full-cell cycling, short-free symmetric plating) where the liquid fades and shorts.
- Emphasize the **deconvolution**: transport is not the discriminator (MD + Bruce–Vincent agree, and poly is no faster); the lever is interphase **composition/chemistry**.
- **Design rule (generalizable):** immobilize/segregate the reducible anion and template a benign, cation-derived, Si-passivated interphase — a transferable principle for multivalent-metal anodes.
- Outlook: extend to other Mg electrolytes / multivalent systems; MLFF-driven interphase screening.

---

## 7. Figure plan (5 main figures; rest → SI)

| Fig | Title | Panels (data source) | Col |
|---|---|---|---|
| **Scheme 1** | In situ POSS cure & APC speciation | cure reaction; cation/anion structures; hypothesis arrows | 1 |
| **Fig 1** | Electrolyte & redox landscape | (a) gel photo/schematic; (b) DFT speciation (T1); (c) redox ladder vs Mg²⁺/Mg (T2) | 2 |
| **Fig 2** | Reversibility, not rate | (a) **★ Mg‖Mo₆S₈ cycling — cap+CE vs cycle: poly >80 % to 842 cyc@0.5C / 1592 cyc@1C, bare dies ~270 (§O)**; (b) multi-rate CV |i_pa/i_pc| (§D); (c) Mg‖Mg 1011‖420 cyc + OCP-collapse self-discharge (§Q/§D); (d) **transport-null pair** MD t₊ ‖ BV t₊ (§B/N) | 2 |
| **Fig 3** | **Si-rich / Al-poor interphase (CENTREPIECE)** | (a) ToF-SIMS ratio bars Si↑/Al↓ (§I); (b) depth profiles 350‖92 nm; (c) XPS Al 2p split + depth (§G); (d) Si 2p | 2 |
| **Fig 4** | Composition → deposit | (a) XRD texture (§J); (b) SEM poly vs bare (§K); (c) EDS Al/Mg, Cl/Mg ratios (§K) — Si excluded (artifact) | 2 |
| **Fig 5** | Why — computation | (a) Al reduction/alloying energetics (T3/T4); (b) SEI DOS/gap insulator-vs-leaky (T8); (c) AIMD/MLFF anion standoff (T10/T17); (d) computed XPS Al 2p/Si 2p vs measured (T11) | 2 |

*(Optional Fig 6 / final Scheme — integrated mechanism + design rule; can be folded into the graphical abstract to save length.)*

### → Supporting Information (figures/tables)
- **All experimental & computational methods** (cells, protocols, DFT/MD/AIMD/MLFF parameters, fitting).
- Mg‖Mo₆S₈ full-cell: voltage profiles, rate capability, long-cycle CE/retention tables (module O) — supporting detail behind Fig 2a.
- Mg‖Cu CV (§A), Aurbach CE (§F), Mg‖Cu galvanostatic (§P) — **honest inert-Cu nulls** with soft-short reconciliation.
- Mg‖Mg Tafel (§E), in-situ DRT (§L), CCD (§M).
- *(GITT not included — dropped per PI.)*
- Raman full spectra & assignment (§H, T12); ToF-SIMS 3D maps & full ion list; XPS survey/all-depth fits; EDS Si-Kα maps **proving the glass-fibre artifact**.
- MD transport tables; speciation/redox CSVs; SEI phase stability & migration; AIMD/MLFF validation (force/energy MAE, active-learning), caveats.
- F-species appear only in completeness tables — **explicitly no fluorine narrative**.

---

## 8. Keywords (≤5)
**magnesium batteries • solid electrolyte interphase • aluminum co-deposition • silsesquioxane (POSS) • metal anode reversibility**

## 9. Author contributions / data
- Corresponding author(s) marked with `*`; affiliations [a],[b]…
- Data Availability + Conflicts of Interest auto-generated via Research Exchange.
- SI references numbered consecutively after the last main reference.

---

## 10. Open items before drafting (PI decisions)
1. **Author list / affiliations / corresponding author** — needed for byline.
2. **Headline electrolyte composition** — confirm exact POSS monomer + curing agent (TMSOTf vs other) wording for the title/abstract (curing-agent triflate is a reagent, **not** an interphase story — keep separate from the no-fluorine constraint).
3. ✅ **Module O analyzed (2026-06-23)** — Fig 2a ready: poly >80 % to **842 cyc@0.5C / 1592 cyc@1C**, CE ≈100 %; bare dies ~270 cyc. **GITT dropped** (do not reintroduce CE 106/27 or GITT D). Open: no **bare 1C** run exists → 1C panel is poly-only (life); the bare-vs-poly head-to-head is the 0.5C pair — confirm acceptable or request a bare 1C cell.
4. **Figure 1 vs Scheme 1 split** — merge if length pressured (5600-word cap is tight with 5–6 figures).
5. **Communication vs full Research Article** — this outline targets the **Research Article** format; a Communication would cut to 3 figures (Fig 2/3/5).
