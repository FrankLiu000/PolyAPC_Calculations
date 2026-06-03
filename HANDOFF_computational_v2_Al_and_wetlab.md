# HANDOFF — poly-APC, comprehensive computational re-analysis (v2)
### For: the next Claude agent.  From: the agent that built the experimental+MD+DFT+AIMD poster.
### Prime directive: treat **aluminium properly**, and re-derive the mechanism so it explains **all** the wet-lab observations — not just transport/solvation.

---

## 0. One-paragraph brief
poly-APC is an in-situ TMSOTf-cured octakis(glycidyl)-POSS gel-polymer electrolyte made inside APC (MgCl₂ / AlPhₓCl_(4−x) in THF). Wet-lab shows it beats liquid APC (Aurbach CE 95.2% vs a non-physical ≥100% soft-short; smooth vs dendritic Mg; CCD stable to 3.0 mA cm⁻²; 842 cyc @0.5C, 3344 cyc @1C on Mg‖Mo₆S₈). The previous computational study concluded the gain is **structural / interfacial / safety-driven, not transport** (gel is 4.4× slower, t₊=0.50 unchanged, cation [Mg₂Cl₃(THF)₆]⁺ segregated ~7 Å from the network). That conclusion is probably still broadly right — **but it ignored the redox chemistry of the APC anion (Al) and the triflate-derived fluoride SEI, which the XPS data show are first-order effects.** Your job: build the missing chemistry and reconcile it with every wet-lab result.

---

## 1. THE ALUMINIUM PROBLEM (highest priority)

### 1.1 What the wet lab actually shows (XPS Peak Table, charge-ref C1s≈284.5 eV both samples)
| element | bare-APC | poly-APC | note |
|---|---|---|---|
| **Al 2p (Peak BE)** | **70.88 eV** | **73.98 eV** | **3.1 eV split — the key clue** |
| Al 2p (at%) | 3.83 | 4.11 | Al is a *major* surface species in both |
| F 1s | 684.94 eV / 4.30 at% | 684.90 eV / 4.17 at% | ≈ MgF₂ (ionic Mg–F) in BOTH |
| Cl 2p | 198.40 / 2.86 | 198.24 / 2.82 | metal chloride (MgCl₂/Cl⁻) |
| Mg 1s | 1303.88 / 16.48 | 1303.74 / 15.25 | Mg²⁺ (oxide/halide) |
| O 1s | 531.41 / 38.45 | 531.39 / 37.31 | organic/oxide-rich |
| C 1s | 284.49 / 33.21 | 284.43 / 32.69 | THF-derived organics |
| Si 2p | 99.47 / 0.88 | 101.66 / 3.66 | POSS siloxane only in poly (×4.2) |

The C1s references differ by only 0.06 eV, so **the 3.1 eV Al 2p split is a genuine chemical-state difference, not charging.** Reference values: Al⁰ metal ≈ 72.7–72.9 eV; Al³⁺ (Al₂O₃/AlF₃/AlCl₃) ≈ 74–76 eV; Al in Mg–Al alloy shifts **below** metallic.

### 1.2 Interpretation / hypothesis to test computationally
- **bare-APC, Al 2p ≈ 70.9 eV (anomalously low)** → reduced / metallic / **Mg–Al alloyed** Al. i.e. the Al-bearing anion is **reductively decomposed at the Mg anode and Al co-deposits** (likely as Mg–Al alloy). Al co-deposition is a known APC pathology and is mechanistically consistent with the **rough, dendritic bare-Mg SEM** and the **soft-short Aurbach CE**.
- **poly-APC, Al 2p ≈ 74.0 eV** → **oxidised Al³⁺** (anion-/oxide-derived, NOT reduced). i.e. the cured network **suppresses anion reduction / Al co-deposition**, leaving a benign Al³⁺ interphase → **smooth Mg**, high CE.
- Mechanistic link you must establish: *network immobilises/positions the anion (MD already shows anion D is 4.2× slower in the gel) → lower anion flux & residence at the reductive plating front → Al-anion reduction is kinetically/thermodynamically disfavoured → Al stays oxidised.*

### 1.3 Why the previous calculations were inadequate on Al
The prior DFT treated Al **only** as a single static spectator anion **[AlPh₂Cl₂]⁻** and computed **only its oxidation** (vertical IP = 6.18 eV → anodic limit). It never considered: (a) the real APC **anion speciation** (Schlenk-type Ph/Cl redistribution), (b) **anion/Al reduction (EA, reductive decomposition)**, (c) **Al co-deposition / Mg–Al alloying** thermodynamics at the anode, (d) Al in the **interphase/SEI**, (e) Al in the **interface AIMD** (which used a *neutral MgCl₂·(THF) surrogate with no Al at all*). This is the central gap.

### 1.4 Concrete Al work plan
1. **Anion speciation (molecular DFT, SMD-THF, same level as before — see §6):** enumerate and rank ΔG of AlCl₄⁻, AlPhCl₃⁻, AlPh₂Cl₂⁻, AlPh₃Cl⁻, AlPh₄⁻, neutral AlCl₃/AlPh₃, and Mg–(μ-Cl)–Al bridged ion pairs; derive the equilibrium distribution and the Ph/Cl redistribution energetics. Determine which anion actually dominates and which is most reducible.
2. **Redox ladder:** for each species compute oxidation (IP) **and reduction (EA + reductive decomposition free energies)**, e.g. [AlPhₓCl_y]⁻ + e⁻ → fragments → Al⁰ precursor. Place Mg²⁺/Mg and the Al pathways on a common potential scale.
3. **Al co-deposition / alloying (periodic DFT):** Al adatom adsorption/insertion on Mg(0001); dilute Al-in-Mg substitution energy; Mg₁₇Al₁₂ (β) and Mg–Al solid-solution formation energies; compare the driving force for Al⁰ deposition vs Mg⁰. Predict the Al 2p state (metal/alloy vs oxide) for each case → match to 70.9 vs 74.0 eV.
4. **Interface AIMD/DFT WITH the real ions:** redo the Mg(0001) interface including the actual cation **and** an Al-anion, bare vs poly (network present). Compare anion approach/residence and whether the anion reduces. **Address the prior flagged limitation: do a constant-potential / charged-electrode treatment** (the prior neutral-surrogate, single-trajectory AIMD explicitly could not capture field-driven plating — see prior reports' caveats). Replicate trajectories for statistics.
5. **Deliverable:** an "Al story" figure set — speciation distribution, an oxidation/reduction potential ladder, an Al co-deposition energy diagram, and an interface snapshot — that predicts the bare-vs-poly Al 2p split.

---

## 2. OTHER WET-LAB RESULTS TO RECONCILE (the "rethink everything" part)

For each: the observation, the current (in)complete explanation, and what you must add.

### 2.1 Fluorine / triflate SEI — and a formulation puzzle
- **Obs:** F 1s ≈ 684.9 eV, ~4.2–4.3 at% in **both** bare and poly → an **MgF₂-type fluoride SEI** in both. Triflate (CF₃SO₃⁻) also carries S (note: **no S 2p scan was acquired** — flag to user).
- **Puzzle:** TMSOTf is the **poly curing initiator only**; classic APC (bare) has **no F source**, yet bare shows ~4.3% F. Either (a) both electrolytes share a triflate/fluorinated salt, (b) cross-contamination, or (c) the "bare" baseline is not triflate-free. **Ask the user to confirm the exact bare and poly formulations before over-interpreting.** This materially affects the SEI story.
- **To compute:** OTf⁻ / TMSOTf reductive decomposition at Mg(0001) → MgF₂ (+ S species); MgF₂/MgCl₂/MgO/Al-oxide SEI formation energies, stability, and Mg²⁺ migration barriers through these phases. MgF₂-rich SEI is usually favourable for Mg plating — quantify.

### 2.2 EDS (bulk) shows no Al; XPS (surface) shows ~4% Al
- **Obs:** EDS quant (depth ~µm) for both regions = C,O,F,Mg,Si,Cu only — **no Al**. XPS (depth ~nm) = ~4% Al.
- **Reading:** Al (and the F/Si interphase) is a **thin, surface-confined interphase species**, not a bulk deposit. This depth contrast is itself evidence the Al/F/Si chemistry lives in the SEI. Use it to constrain SEI thickness/coverage in your model. (EDS regions: region 1 = C/O/Si-rich film, Cu absent ≈ poly-coated surface; region 2 = Cu 78% ≈ exposed substrate ≈ bare. Confirm assignment.)

### 2.3 Raman — assign the real differences with DFT vibrations
- **Obs (corrected from the poster):** the Mg²⁺ first-shell coordination band (THF ring ~915 cm⁻¹) is **retained** in both, BUT the free-THF 915 band is relatively weaker in poly and a band **shifts 1002 → 1034 cm⁻¹** (polyether/POSS modes appear). Earlier this was wrongly called "no difference."
- **To compute:** DFT harmonic Raman/IR of free THF vs Mg-coordinated THF, the anion species, the polyether arm, and the POSS cage; assign 915 / 1002 / 1034 cm⁻¹ quantitatively and explain the free-vs-bound THF ratio change (MD says ~⅓ THF is network-bound — does Raman corroborate?).

### 2.4 In-situ DRT — connect impedance to SEI
- **Obs:** poly shows **higher but stable** interfacial impedance (R_ct), tracking the 4.4× slower transport (MD). 30-pulse operando evolution is non-growing for both.
- **To compute:** relate the computed SEI composition/thickness and Mg²⁺-through-SEI barriers (§2.1) to the measured R_ct magnitude and its stability; does the Al-free (poly) vs Al-co-deposited (bare) interphase explain the impedance and its stability?

### 2.5 CCD / Aurbach / morphology — tie to Al + dendrites
- **Obs:** bare = 3.1 V breakdown spike + soft-short CE + flaky dendritic Mg; poly = smooth, stable, dendrite-free.
- **Hypothesis to close:** Al co-deposition + heterogeneous Mg–Al nucleation roughens bare-Mg and seeds dendrites/soft-shorts; poly suppresses Al co-deposition and mechanically confines growth. Provide the energetic/kinetic argument (nucleation, alloy phases, surface diffusion) linking §1.3 to morphology.

---

## 3. WHAT ALREADY EXISTS (don't redo blindly — build on it)

### 3.1 Prior computational scope (keep & extend)
- **Classical MD** (GROMACS, OPLS-style FF, 3×100 ns NVT, 298 K, PME): cation [Mg₂Cl₃(THF)₆]⁺, anion **[AlPh₂Cl₂]⁻** (single species), THF, cured POSS-polyether network "NET1", TMS initiator. D from unwrapped MSD (20–80 ns), t₊ = D₊/(D₊+D₋). Results: D 0.051→0.011 (cat), 0.050→0.012 (an) ×10⁻⁵ cm²/s; t₊ 0.50; σ_coll 0.11→0.04 mS/cm; first shell 3 μ-Cl + ~3.16 THF-O + ~0.01 network-O; ion pairing 83→80%; nearest network-O median 7.1 Å.
- **Molecular DFT** B3LYP-D3(BJ)/def2-TZVP//def2-SVP, SMD(THF), Multiwfn ESP. Oxidation IP: anion 6.18 (lowest), polyether 7.18, THF 7.30, POSS 8.72 eV. THF binding −21 kcal/mol; ion-pair ≈0 (screened). Desolvation **free-energy ladder** (per-THF 9.3/9.5/17.1; last-THF routes dissociative 19.9, network-O relay 5.6 [barrierless], reduction-coupled 3.9 kcal/mol). Migration hop barrier 0.5→17.4 kcal/mol over 5.0→7.0 Å O···O.
- **Periodic/AIMD** CP2K PBE-D3, DZVP-MOLOPT/GTH, Fermi smearing, Mg(0001) slab. Φ = 3.97 eV. 5.6 ps interface AIMD, **neutral MgCl₂·(THF) surrogate (NO Al, single trajectory)**; Mg reaches contact (~3.09 bare / 3.14 poly Å), no spontaneous decomposition; poly carrier samples lower interfacial coordination (1.7 vs 2.5 O/Cl). **Prior reports explicitly flag: (i) field-driven plating needs constant-potential DFT; (ii) AIMD needs replicates + the real (charged) cluster.** ← address these.

### 3.2 File map (paths relative to project root `20260602_polyAPC_data/`)
- `DFT+AIMD/handoff_DFT_AIMD/` — `REPORT_polyAPC_master.md` (read first), `REPORT_polyAPC_DFT.md`, `DESOLVATION_mechanism_plan.md`, `data/` (free_energy_ladder.txt, RESULTS_table.txt, mg_slab_workfunction.txt), `figures/` (01–12 incl. ESP surfaces 03–07, interface AIMD 11–12).
- `classical_molecular_dynamics/handoff_for_agent/` — `reports/` (COMPARISON.md, ANALYSIS_REPORT.md, SYNTHESIS_descriptors.md, conductivity_explanation.md), `rdf/{bare,poly}/` (rdf_*.xvg, cn_*.xvg incl. cn_MgAnAl.xvg / cn_MgAnCl.xvg = the **anion** RDFs you'll need), `solvation/`, `transport/`, `interaction_energies/`, `structures/` (00_bareAPC, 01–03 poly gels with .gro/.top/.itp; `representative_solvation/*.pdb` incl. ion-pair & polymer-coordinated clusters).
- **Experimental (raw):** `XPS/.../{bare-APC,poly-APC}/` (per-element `*.VGD` + `1.xls`/`2.xls` with full spectra & Peak Table), `Raman/Raman.xlsx` (cols J/K/L = shift / raw / processed; 3 reps each), `in_situ_DRT/` (DRT_*_matrix.csv = 30 depths × 161 τ), `SEM+EDS_.../` (.tif + the EDS docx with element maps & quant tables), `Aurbach_Coulombic_Efficiency/`, `critical_current_density/`, `MgMo6S8_{0.5C,1C}_cycle/`, `MgMg/`, `MgCu/`, `Mg_transference_number/` (.cex now exported to **.txt**, Neware format; `Mg_transference_number/*.mdat` still binary — t₊ used MD value).
- **Poster + figure pipeline (mine):** the deliverable PDFs are in the project root (`poster_polyAPC_human_80x160.pdf`, `poster_polyAPC_80x160.pdf`). My figure scripts/data live in the session scratchpad (not persisted) — regenerate from raw if needed; all extraction recipes are documented in the poster figures.

---

## 4. PROPOSED COMPREHENSIVE PROGRAM (prioritised)

**P0 — Aluminium (see §1.4):** speciation → redox ladder → co-deposition/alloying → real-ion (constant-potential) interface. *This is the headline.*
**P1 — Triflate/fluoride SEI (§2.1):** decomposition pathways, MgF₂/MgCl₂/MgO/Al-oxide SEI energetics & Mg²⁺ transport; resolve the F-in-bare formulation question with the user.
**P2 — Integrated interphase model:** a single bare-vs-poly SEI model that reproduces the XPS quantities AND chemical states of Al, F, Cl, Mg, O, C, Si. This is the unifying deliverable.
**P3 — Spectroscopy assignment (§2.3):** DFT Raman/IR to assign 915/1002/1034 cm⁻¹ and free/bound-THF.
**P4 — Close the loop to performance (§2.4–2.5):** SEI ↔ DRT impedance; Al co-deposition ↔ dendrites/CCD/CE.
**P5 — Shore up prior caveats:** constant-potential interface; AIMD replicates; revisit whether the anion is really [AlPh₂Cl₂]⁻ or a different dominant species (may change the 6.18 eV anodic-limit claim).

### Suggested methods (extend consistently)
- Keep DFT at **B3LYP-D3(BJ)/def2-TZVP//def2-SVP, SMD(THF)**; use **ωB97X-D or M06-2X** cross-checks for redox/EA (range-separated is safer for anion EAs); frequency-verify every minimum (NImag=0) and report ΔG(298 K). Redox potentials vs Mg²⁺/Mg reference, with the same solvation model.
- Periodic/alloy DFT: **CP2K or VASP**, PBE-D3 (consider SCAN/+U sanity check); Mg(0001) slab consistent with the prior Φ=3.97 eV validation; for co-deposition use adatom/insertion + formation energies; for field-driven plating use **constant-potential (e.g. grand-canonical / effective-screening-medium)**.
- Classical MD: you may extend the FF to multiple anion species, but **bond-breaking Al reduction is out of classical scope — use AIMD/DFT**. Use MD only for anion dynamics/residence at the interface (bare vs gel).
- Always compute **bare vs poly** in parallel so every result is comparative.

---

## 5. DELIVERABLES (so it can drop into the poster)
1. `REPORT_polyAPC_v2_master.md` — updated integrated story (preserve the honest framing; add the Al/SEI chemistry).
2. New figures (publication-ready, bare-vs-poly): **Al speciation distribution; oxidation/reduction potential ladder (Mg vs Al vs OTf); Al co-deposition / Mg–Al alloy energy diagram; integrated SEI model schematic with XPS-matched composition; computed Raman assignment; constant-potential interface snapshots.**
3. A short **"reconciliation table"**: each wet-lab observable (Al 2p split, F/MgF₂, Si/POSS, EDS-vs-XPS depth, Raman shift, DRT, CCD/CE/morphology) → the computational explanation → confidence/limitation.
4. Machine-readable data (.txt/.csv) for every number, plus structure files (.xyz/.gro) for every new species/interface so figures can be rendered.

---

## 6. SCIENTIFIC-INTEGRITY GUARDRAILS (read this)
- **Do not fabricate.** Where data/coords don't exist, build a clearly-labelled *representative model* and say so. (The poster's ladder/AIMD structures are representative renders because no DFT/AIMD geometries were saved — preserve that honesty.)
- **Verify XPS charge referencing** (C1s→284.8) before quoting absolute Al/F/Mg BEs; the 3.1 eV Al split survives referencing, but confirm.
- **Flag, don't paper over, the F-in-bare and missing-S puzzles** — get the exact formulations from the user.
- **Reconcile depth sensitivity** (EDS µm vs XPS nm) explicitly.
- Keep the **honest mechanistic frame**: transport is *not* the win; but now show the Al/redox/SEI chemistry is a major, previously-missed part of the interfacial/safety story.
- Revisit the **6.18 eV "anodic limit"** claim if the dominant anion turns out not to be [AlPh₂Cl₂]⁻.
- Every computed energy: convergence- and frequency-checked; report uncertainties/replicates.

---

## 7. Author/affiliation (for any new report)
Yuezheng Liu¹, Yong Wu¹,²*, Yingying Lu¹,³*. ¹State Key Lab of Chemical Engineering, College of Chemical & Biological Engineering, Zhejiang University, Hangzhou. ²Dept. of Energy & Environmental Materials, Suzhou National Laboratory. ³ZJU-Hangzhou Global Scientific & Technological Innovation Center. Contact: frank.y.liu231@gmail.com

*End of handoff. Start with §1 (Aluminium) and `REPORT_polyAPC_master.md`.*
