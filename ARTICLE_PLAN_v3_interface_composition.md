# poly-APC — new article narrative & computational plan (v3.1)
### Re-analysis of ALL wet-lab data, re-centred on **interface composition (ToF-SIMS + XPS)**.
### Thesis: *the cured POSS network re-programs the Mg-anode SEI to be **Si-rich and Al-poor**, suppressing Al co-deposition — an **interfacial-chemistry** win, not a transport win.*
### Scope note (per user): **do NOT build a fluorine/triflate story.** The interphase narrative is **Si (↑) and Al (↓)** only. **Computation = comprehensive: compute everything below (no triage).**

---

## 中文导读 (一页纸)
- **核心论点**：原位固化的 **POSS 网络**把镁负极界面层(SEI)的**化学组成**重编程为**薄、富 Si(POSS)、贫 Al** 的表层，并把 SEI 物种限制在锐利的表层(poly Al-氧化物半深度 ~92 nm vs bare ~350 nm)。这**抑制了液态 APC 中铝阴离子在负极被还原导致的 Al 共沉积**及随之而来的过充/自放电。
- **性能提升源于界面化学，而非离子输运**：GITT 与 MD 都给出**几乎相同的 Mg²⁺ 扩散系数**(GITT: poly 9×10⁻¹⁵ vs bare 8×10⁻¹⁵ cm²/s；MD: poly 反而慢 4.4×、t₊ 都 = 0.50)。真正差别是**可逆性/界面稳定性**(库仑效率 100% vs 27%，bare 每小时自放电 −320 mV)。
- **两条主线证据**：①界面组成(ToF-SIMS+XPS)——poly **富 Si(×20–34)、贫 Al(Al 类离子 ×0.02–0.5)**；②Al 化学态(XPS Al 2p **70.9 vs 74.0 eV**)——bare 是金属/合金态 Al(共沉积)，poly 只剩氧化态 Al³⁺ 残留。形貌(XRD 取向致密 vs 粗糙；SEM 光滑 vs 枝晶)与可逆性(GITT/CV)随之而来。
- **旧计算的硬伤**：只把 Al 当静态阴离子算了**氧化**(阳极极限 6.18 eV)，从未算**还原/共沉积**，没建 SEI，界面 AIMD 用了**不含 Al 的中性替身**。
- **新计算计划(全部都算)**：(C1)铝阴离子物种分布 + 还原电位 + Al 共沉积/Mg-Al 合金能量学；(C2)POSS 网络如何在动力学/热力学上阻断 Al 还原/排斥 Al；(C3)SEI(SiOₓ/POSS + MgClₓ + 氧化物 + 有机)电子绝缘性与 Mg²⁺ 输运；(C4)含真实离子的**恒电位界面 AIMD**;(C5)XPS(Al 2p / Si 2p)与 Raman 谱学指认验证;(C6)与 CE/自放电/形貌/枝晶的闭环。**不做不讲氟的故事。**

---

## PART A — RE-ANALYSIS OF ALL WET-LAB RESULTS (evidence base)
APC ≡ AlCl₃ + PhMgCl in THF → cation **[Mg₂(μ-Cl)₃(THF)₆]⁺**, anion family **[AlₓPhᵧCl_z]⁻**. poly-APC = APC polymerised in-situ with **POSS** (silsesquioxane network). Two electrodes compared throughout: **bare** (Mg cycled in liquid APC) vs **poly** (Mg cycled in polymerised APC).

### A1. ToF-SIMS (negative ions, Cs⁺ sputter, 50 µm FOV) — **the new centrepiece**
Element-filtered, separator-corrected (B = GF/D-separator artifact, excluded). poly/bare intensity ratios (`processed/data/diagnostic_ions_corrected.csv`):
| family | species (poly/bare ratio) | reading |
|---|---|---|
| **Si (POSS)** ↑ | Si⁻ **×20**, SiO₂⁻ **×30**, SiO₃⁻ **×34** | poly SEI strongly **Si-enriched** (POSS network) |
| **Al** ↓↓ | AlO⁻ **×0.13**, AlO₂⁻ ×0.26, Al⁻ ×0.08, **Al₂⁻ ×0.02**, Al₂O₃⁻ ×0.21, MgAlO⁻ ×0.18, C₂Al⁻ ×0.35 | poly SEI **Al-depleted** across every Al ion |
| Mg/Cl/O/organics | MgO⁻ ×1.6, MgCl⁻ ×2.0, Cl⁻ ×1.1, O⁻ ×1.06, C₂⁻ ×2.6 | comparable inorganic + slightly more organic in poly |
**Depth (x50, signal halves):** bare AlO⁻ **350 nm**, AlO₂⁻ 224 nm, total 275 nm; poly AlO⁻ **92 nm**, AlO₂⁻ 60 nm, SiO₂⁻ 57, SiO₃⁻ 48, total 206 nm. → **poly confines SEI species to a sharp ~50–90 nm surface layer; bare's Al penetrates ~3–4× deeper.**
**Net:** poly = **Si-rich, Al-poor, surface-confined** SEI; bare = **Si-poor, Al-rich, deep** SEI. *(Exactly the user's directed framing — robustly supported.)*

### A2. XPS (cycled Mg surface, ~nm) — chemical state of the same elements
| element | bare | poly | reading |
|---|---|---|---|
| **Si 2p** | 99.5 eV / **0.88 at%** | 101.7 eV / **3.66 at%** (×4.2) | poly = siloxane Si–O–Si (POSS) at surface |
| **Al 2p** | **70.88 eV** / 3.83 at% | **73.98 eV** / 4.11 at% | **3.1 eV split**: bare = reduced/metallic/**alloyed Al⁰** (co-deposited); poly = oxidised **Al³⁺** residue |
| Cl 2p | 198.4 / 2.86 | 198.2 / 2.82 | metal chloride |
| Mg 1s | 1303.9 / 16.48 | 1303.7 / 15.25 | Mg²⁺ |
| O 1s | 531.4 / 38.45 | 531.4 / 37.31 | organic/oxide |
| C 1s | 284.5 / 33.21 | 284.4 / 32.69 | THF-derived organics |
**Reconciles with ToF-SIMS:** XPS *surface* Al at% looks similar (poly slightly higher) because XPS samples only the top ~nm, where poly carries a thin oxidised-Al residue; **ToF-SIMS depth shows SEI-integrated Al is far lower in poly.** The decisive XPS signal is the **Al 2p chemical-state split** (Al⁰/alloy in bare vs Al³⁺ in poly) — survives charge referencing (C1s differs by only 0.06 eV).

### A3. XRD of deposited Mg (Mg@PP separator, Cu Kα)
Both = metallic hcp-Mg; **no MgO(200) 42.9°** → oxide-free deposits. **bare:** Mg(101) tallest, texture ≈ random (A002/A101 = 0.39), full higher-angle family → **coarse, randomly-oriented, protruding** Mg. **poly:** **texture-enhanced** (A002/A101 = 0.83 ≈ 2–3× random), larger apparent crystallite (~21 vs ~11 nm) → **thin, conformal, basal/prismatic-oriented** Mg ("the good sign"). **No crystalline Al / Mg–Al phase** → co-deposited Al in bare is **amorphous / SEI-bound** (seen by surface XPS/ToF-SIMS, not bulk XRD). *(Caveat: normalise by areal capacity before claiming "less Mg".)*

### A4. Multi-rate CV + GITT (Mg‖Mo₆S₈) — reversibility, and **D is NOT the discriminator**
- **Coulombic efficiency:** poly ≈ **100%** (GITT 106%), bare = **27%** (167 mAh g⁻¹ charge for 46 discharge). bare OCV **turns over ~1.29 V then sags**; bare **self-discharges −320 mV (up to −540) per 1 h rest**; poly relaxes −100 mV to a stable OCV.
- **CV:** poly |i_pa/i_pc| ≈ **1.0** vs bare **1.2–1.34**; poly OCP stable ~1.36 V vs bare collapsing **1.12 → 0.50 V**.
- **Mg²⁺ chemical diffusion (GITT):** poly **9×10⁻¹⁵**, bare **8×10⁻¹⁵ cm² s⁻¹** — **near-identical** → **bulk transport is NOT the difference**, independently confirming MD (poly 4.4× *slower*, t₊ = 0.50). Discriminator = **reversibility + interfacial stability**.

### A5. Earlier techniques (all consistent)
SEM: bare rough/dendritic, poly smooth. Aurbach CE: poly 95.2%, bare ≥100% soft-short. CCD: poly stable to 3.0 mA cm⁻², bare 3.1 V breakdown. Cycling: poly 842 cyc @0.5C / 3344 @1C, bare fades. In-situ DRT: poly higher-but-**stable** interfacial impedance. Raman: Mg²⁺ first-shell THF/Cl coordination **preserved**, gel adds polyether/POSS modes (915 retained, 1002→1034 shift). MD: D ↓4.4×, t₊ 0.50, cation segregated ~7 Å. Prior DFT: anion oxidation IP 6.18 eV; POSS most oxidation-resistant; desolvation ladder; ether-O migration relay.

### A6. The single coherent picture
**bare-APC:** Al-anion is **reduced at the Mg anode → Al co-deposits** (metallic/alloyed Al⁰; Al-rich SEI ~350 nm deep) → coarse, randomly-oriented Mg → dendrites, soft-shorts, **overcharge & self-discharge (CE 27%)**.
**poly-APC:** the cured POSS network builds a **thin, Si-rich, Al-poor, surface-confined SEI** that **suppresses Al-anion reduction / Al co-deposition** (only oxidised Al³⁺ residue) → thin, conformal, oriented Mg → smooth, **reversible (CE ~100%)**, stable, high CCD, long cycling.
**Transport is identical** (GITT & MD); the win is **interfacial composition (Si-rich, Al-poor).**

---

## PART B — THE NEW ARTICLE NARRATIVE (脉络)

**Working title:** *"Interphase-by-design in magnesium batteries: an in-situ POSS network builds a silicon-rich, aluminium-poor interphase that suppresses Al co-deposition."*

**One-sentence thesis:** Polymerising APC in-situ with POSS does not change how fast Mg²⁺ moves; it changes **what the Mg-anode interphase is made of** — converting an Al-rich, dendrite-prone, parasitic SEI into a thin, Si-rich, Al-poor passivating layer — and that compositional switch is what makes Mg plating reversible.

**Graphical abstract:** two anodes. bare: Al-anion + e⁻ → Al⁰ co-deposited (Al-rich deep SEI), rough Mg, dendrite/short. poly: POSS surface layer; Si-rich thin SEI; Al excluded (Al³⁺ only); smooth oriented Mg. Centre: "interphase re-programming — Si in, Al out."

**Figure plan:**
- **Fig 1 — Concept & electrolyte.** in-situ POSS cure schematic; APC speciation (cation / Al-anion); hypothesis (anion reduction → Al co-deposition vs network suppression).
- **Fig 2 — It works & it's reversible.** Aurbach CE (V–t), CCD, Mg‖Mo₆S₈ 0.5C/1C cycling, **GITT CE 100% vs 27% + self-discharge**, CV reversibility. Headline: reversibility, not rate.
- **Fig 3 — Interphase composition (CENTREPIECE).** ToF-SIMS poly/bare ratio bars (**Si ×20–34 ↑, Al ×0.02–0.5 ↓**), depth profiles (Al deep in bare vs confined in poly), 3-D ion maps; XPS **Al 2p split (70.9 vs 74.0 eV)** + Si 2p (POSS). *This figure is the paper.*
- **Fig 4 — The deposit.** XRD texture (poly oriented/conformal vs bare random/coarse) + SEM (smooth vs dendritic) + EDS map (Si-rich poly film). Composition → morphology.
- **Fig 5 — Why: computation.** Al-anion **reduction/co-deposition** energetics & potentials; POSS-network **suppression** mechanism; SEI electron-blocking & Mg²⁺ transport; constant-potential interface AIMD (Al reduces on bare, suppressed on poly); transport-equal (MD D, t₊) to kill the rate hypothesis; computed Al 2p / Si 2p shifts + Raman.
- **Fig 6 — Mechanism & design rule.** Integrated picture + generalisable principle ("immobilise/segregate the reducible anion to engineer a benign, cation-derived, Si-passivated interphase").

**Section spine:** composition (Fig 3) explains performance (Fig 2) and morphology (Fig 4); computation (Fig 5) explains the composition.

---

## PART C — COMPUTATIONAL PLAN (COMPREHENSIVE — compute ALL of it)
> Run **bare vs poly in parallel**. Keep prior baselines (MD: GROMACS OPLS, 3×100 ns; DFT: B3LYP-D3(BJ)/def2-TZVP//def2-SVP, SMD-THF; periodic/AIMD: CP2K PBE-D3, Mg(0001), Φ=3.97 eV). Extend, don't restart. **No fluorine/triflate narrative** — F-bearing species may appear in completeness checks but are not a story element.

**C1 — Aluminium speciation & REDUCTION (the missing core).**
- Enumerate/rank APC anions (AlCl₄⁻, AlPhCl₃⁻, AlPh₂Cl₂⁻, AlPh₃Cl⁻, AlPh₄⁻; neutral AlCl₃/AlPh₃; Mg–μCl–Al ion pairs) in SMD-THF; equilibrium distribution; identify the most reducible species. (Re-examine the prior 6.18 eV anodic-limit claim once the dominant anion is fixed.)
- Each species: **reduction (EA + stepwise reductive decomposition → Al⁰ precursor)** AND oxidation; place on a common scale vs Mg²⁺/Mg. Cross-check anion EAs with ωB97X-D or M06-2X.
- **Al co-deposition / alloying (periodic DFT):** Al adatom adsorption/insertion on Mg(0001); dilute Al-in-Mg substitution; Mg₁₇Al₁₂ formation; compare ΔG(Al⁰ deposition) vs ΔG(Mg⁰). Predict Al 2p state (metal/alloy ≈71 eV vs oxide ≈74 eV) → match XPS.

**C2 — Why POSS EXCLUDES Al (the linchpin).** Compute both routes:
- **Kinetic/transport:** MD of the cured-network interface — Al-anion **residence time, near-surface concentration & approach flux** to the anode, with vs without the network (anion D is 4.2× slower in the gel). Does the network sterically/electrostatically sequester the Al-anion from the reductive front?
- **Passivation/electron-blocking:** does the **SiOₓ/POSS** surface layer raise the **electron-transfer barrier** to the anion? Compute the Al-anion reduction barrier and electron availability with vs without the passivating layer.

**C3 — SEI composition, electronic structure & Mg²⁺ transport.** Build candidate SEIs — **poly: SiOₓ/POSS + MgClₓ + MgO + organics; bare: Al/AlOₓ(+Mg–Al) + MgClₓ + MgO + organics.** Compute formation energies/stability, **electronic structure (insulating = good passivation; leaky = continued parasitic reduction → self-discharge)**, and **Mg²⁺ migration barriers** through each (relate to DRT: poly higher-but-stable). Test: is the Al-rich bare SEI electronically leaky → parasitic reduction & self-discharge (GITT 27%)? Is the Si-rich poly SEI a better passivator?

**C4 — Constant-potential interface AIMD with REAL ions.** Redo Mg(0001) interface with the actual cation **and** an Al-anion, bare vs poly (network present), **constant-potential / charged-electrode** (fixes the prior neutral-surrogate, single-trajectory caveat). Observe Al-anion **reduction/deposition** on bare vs **suppression** on poly. Replicate for statistics.

**C5 — Spectroscopy validation (compute everything that ties to data).** Core-level shifts: **Al 2p** (Al⁰/Mg–Al vs Al³⁺ → reproduce 70.9/74.0 eV split) and **Si 2p** (siloxane). **Raman/IR** of free vs Mg-coordinated THF, anion species, polyether, POSS → assign 915 / 1002→1034 cm⁻¹ and the free/bound-THF change. (Optional ToF-SIMS fragment-stability rationalisation for Al-oxide vs Si-oxide ions.)

**C6 — Close the loop to performance.** Al co-deposition → heterogeneous Mg–Al nucleation/dendrites (nucleation + surface-diffusion energetics → XRD texture & SEM). Anion redox → overcharge/self-discharge (GITT 27% CE / OCV turnover). Si-rich passivating SEI → suppressed parasitics → CE ~100%. Reconcile that **bulk Mg²⁺ D is equal** (MD + GITT) so the entire advantage is located at the interface.

**Methods notes.** Bond-breaking (Al reduction) is out of classical-MD scope → AIMD/DFT for reactivity, MD only for anion dynamics/structure. Frequency- and convergence-verify; report ΔG(298 K); replicate AIMD.

---

## PART D — COMPUTE ↔ WET-LAB RECONCILIATION
| Wet-lab observable | Calculation that must explain it |
|---|---|
| ToF-SIMS: poly Al ↓ (×0.02–0.5), confined ~90 nm | C1 (Al reducible on bare) + C2 (poly suppresses) + C4 (AIMD) |
| ToF-SIMS/XPS: poly Si ↑ (×20–34 / ×4.2), siloxane | C3 (POSS/SiOₓ surface layer) |
| XPS Al 2p **70.9 (bare) vs 74.0 (poly)** | C1 + C5 (Al⁰/alloy vs Al³⁺ core-level shift) |
| XRD: poly oriented/conformal vs bare coarse/random | C6 (nucleation/texture: Al-free vs Al-containing surface) |
| GITT/CV: CE 100% vs 27%, self-discharge | C3 (electron-blocking SEI) + C1 (anion redox) |
| GITT + MD: Mg²⁺ **D equal** | already agree → advantage is interfacial, not bulk |
| DRT: poly higher-but-stable impedance | C3 (Mg²⁺ migration through the thicker/insulating poly SEI) |
| Raman 915 kept; 1002→1034 | C5 (DFT vibrational assignment) |

---

## PART E — CAVEATS & OPEN QUESTIONS
1. **"Less Al" is depth/chemical-state, not surface-at%.** XPS surface Al at% is similar (poly 4.11 vs bare 3.83); the claim "poly 界面 Al 更少" is supported by **(i)** ToF-SIMS depth-integrated Al ions ×0.02–0.5 + shallow confinement and **(ii)** the Al 2p state (oxidised residue vs metallic co-deposit). State it precisely this way.
2. **XRD can't see amorphous/dilute Al** — absence of a crystalline Mg–Al phase does NOT contradict Al co-deposition (surface/amorphous). Use XRD only for Mg morphology/texture.
3. **Boron is a GF/D-separator artifact — exclude.** Silicon has a separator baseline too; only the **poly excess** (×20–34) is POSS.
4. **XRD intensity ≠ amount** — confirm morphology at matched areal capacity.
5. **Honest spine:** transport is genuinely *not* the discriminator (triply shown: MD, GITT, CV). The paper's value is locating & explaining the **interfacial-compositional (Si-rich, Al-poor)** origin.

---

## FILE MAP (data sources)
- `ToF-SIMS/` — `HANDOFF.md` (M6 .itmx decode, element/separator rules; APC = AlCl₃+PhMgCl), `processed/data/diagnostic_ions_corrected.csv`, `sei_depth.json`, `processed/figures_decoded/`, `processed/scripts_m6/`.
- `XRD_deposited_Mg/` — `CLAUDE.md`, `analysis_output/` (peaklist_both.csv, scan_*.csv, figs, report).
- `Multi-Rate_CV+GITT/` — `ANALYSIS_GITT_poly_vs_bare.md` (CE 100% vs 27%, D equal, self-discharge), `analysis_outputs/cv_metrics.csv`, figs.
- (prior) `XPS/`, `Raman/`, `in_situ_DRT/`, `SEM+EDS_.../`, `DFT+AIMD/`, `classical_molecular_dynamics/`, electrochem `.txt`; plus `HANDOFF_computational_v2_Al_and_wetlab.md` (this v3.1 supersedes it).

*Start with C1 (Al reduction) and Fig 3 (ToF-SIMS+XPS composition). The whole paper hinges on Al-poor / Si-rich. No fluorine story. Compute everything in Part C.*
