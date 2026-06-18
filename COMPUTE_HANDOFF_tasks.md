# COMPUTE HANDOFF — executable tasks for the next agent (Claude Code, compute node)
**Repo contents you were given:** this file + `ARTICLE_PLAN_v3_interface_composition.md` (the scientific spec — **read it first**).
**You are:** a Claude Code agent on a compute node. Pull this repo, set up the environment (T0), then work the tickets **T1 → T15** in dependency order, committing results as you go.

---

## 0. MISSION (one paragraph)
Explain, from first principles, **why the in-situ POSS-cured "poly-APC" Mg-anode interphase is Si-rich and Al-poor**, and why that makes Mg plating reversible. The wet-lab (ToF-SIMS + XPS + XRD + CV/GITT) is already done and summarised in `ARTICLE_PLAN…md`; your job is the **comprehensive computational half** that the prior study missed: the **reduction / co-deposition chemistry of the APC aluminium anion**, why the POSS network excludes Al, the SEI it builds, and the spectroscopic fingerprints. Every result must map to an article figure/claim (see ARTICLE_PLAN Part D).

## 1. HARD CONSTRAINTS (do not violate)
1. **Story = Si (↑) and Al (↓) interface composition.** **NO fluorine / triflate / MgF₂ narrative.** F-bearing species may appear only in completeness checks, never as a story element or figure.
2. **Compute EVERYTHING in §T (no triage).** This is the "comprehensive" job the PI asked for.
3. **Always bare vs poly in parallel** (every quantity reported as a pair + Δ).
4. **Keep the honest spine:** bulk Mg²⁺ transport is NOT the discriminator (MD + GITT already agree: D ≈ 8–9×10⁻¹⁵ cm² s⁻¹ both; t₊=0.50). The advantage is interfacial-compositional. Do not invent a transport advantage.
5. **No fabrication.** Where you build a model (slab, SEI, cluster), label it a model and record how it was built. Frequency-verify minima (NImag=0); converge & replicate; report uncertainties.
6. **Reproduce the key XPS target:** the Al 2p chemical-state split **70.88 eV (bare, Al⁰/alloy) vs 73.98 eV (poly, Al³⁺)** must fall out of C1/C5, or you must explain why not.

## 2. REPO / DATA MAP
- `ARTICLE_PLAN_v3_interface_composition.md` — spec, target numbers (Part A), compute↔data map (Part D), caveats (Part E).
- **Raw experimental data is large and may NOT be in this git repo.** You do not need it to run calculations — the *targets to reproduce* are tabulated in the ARTICLE_PLAN. **Build all input structures yourself** (specs in each ticket).
- **Seed structures needed from the experimental repo** (request the PI to add to `seeds/` if absent): `classical_molecular_dynamics/handoff_for_agent/structures/{00_bareAPC, 01_polyAPC_4POSS_gel}/*.gro,*.top,*.itp` (for C2/C4 interface MD) and `…/representative_solvation/*.pdb` (cation/ion-pair seeds). Everything else you generate.

## 3. COMPUTE INFRASTRUCTURE & TOOLING (two nodes)
**Use the right node per task — every ticket is tagged [CPU] / [GPU] / [both].**
- **CPU node → DFT + AIMD.** Molecular DFT (ORCA/Gaussian, **B3LYP-D3(BJ)/def2-TZVP//def2-SVP, SMD(THF)**; ωB97X-D/M06-2X cross-checks; Multiwfn), periodic DFT + CI-NEB + **ab-initio MD** (CP2K PBE-D3 DZVP-MOLOPT/GTH; constant-potential), core-level & Raman/IR.
- **GPU node → classical MD + MLFF.** GROMACS-GPU (OPLS; the seed `.top/.itp`) for non-reactive structure/transport; **MLFF** (machine-learning force field) for **reactive, DFT-accurate, large-cell / long-time** interface & SEI simulation — fine-tune a foundation model (**MACE-MP-0**, CHGNet/M3GNet) or train NequIP/Allegro/DeePMD over {Mg,Al,Cl,O,C,H,Si}.
- **Cross-node active-learning loop:** CPU produces DFT/AIMD **reference labels** (T4, T7, T10) → GPU **trains/fine-tunes the MLFF** (T16) → GPU runs **production** (T17) → high-uncertainty configs go **back to CPU** for DFT labelling → retrain. Pass small artifacts via this git repo; pass trajectories via a shared store; **record dataset + model versions**.

**Node allocation:**
| node | tickets |
|---|---|
| **CPU (DFT/AIMD)** | T0, T1, T2, T3, T4, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15 |
| **GPU (MD/MLFF)** | T0, T5, T13 (stats), **T16, T17** |

## 4. CONVENTIONS (so results are git-friendly & reproducible)
- Write to `results/<TID>_<shortname>/` with subfolders `inputs/ outputs/ structures/ figures/` and a **`REPORT.md`** (objective, method+exact parameters, key numbers as a table, figures, acceptance-criteria check, provenance: code+version+date).
- Structures as `.xyz` (molecular) / `.cif` (periodic) so figures can be regenerated.
- Machine-readable results as `.csv`/`.json` next to each figure.
- One commit per ticket: `T<id>: <result one-liner>` (e.g., `T3: Al-anion reduction ladder — AlPhCl3- most reducible, −0.7 V vs Mg`).
- Maintain a top-level **`RESULTS_v2/REPORT_v2_master.md`** that integrates findings into the ARTICLE_PLAN's Fig 5/Part D structure; update it after each ticket.
- Keep a running `RESULTS_v2/STATUS.md` checklist (ticket → done/blocked + 1-line result).

---

## T — TASK TICKETS

### T0 — [both] Preflight & sanity (do first)
- **Do:** read `ARTICLE_PLAN…md` fully; inventory available codes (`which orca cp2k vasp gmx python`); create `results/` + `RESULTS_v2/STATUS.md`. Reproduce **one** prior number as a smoke test: optimise THF in SMD(THF) at the baseline level and confirm sane geometry/energy; build a Mg(0001) slab and **reproduce Φ ≈ 3.97 eV** (prior value) to validate the periodic setup.
- **DoD:** STATUS.md created; code list recorded; Φ within ~0.1 eV of 3.97 eV (or discrepancy explained). 
- **Blocks:** everything periodic (T6–T12).

### ===== C1 — Aluminium speciation & reduction (CORE) =====

### T1 — [CPU·DFT] APC anion speciation map
- **Build & optimise** (SMD-THF, baseline DFT; freq-verify): anions **AlCl₄⁻, AlPhCl₃⁻, AlPh₂Cl₂⁻, AlPh₃Cl⁻, AlPh₄⁻**; neutrals **AlCl₃, AlPh₃**; (Ph = C₆H₅). Also the **cation [Mg₂(μ-Cl)₃(THF)₆]⁺** (seed from representative_solvation pdb or build).
- **Compute** relative ΔG(298 K) and the **Schlenk-type Ph/Cl redistribution** equilibria (e.g. 2 AlPh₂Cl₂⁻ ⇌ AlPhCl₃⁻ + AlPh₃Cl⁻); estimate the dominant anion population in APC.
- **DoD / output:** `speciation.csv` (species, ΔG, relative population), a level-of-theory note, and a 1-paragraph "dominant/most-labile anion" conclusion. **Revisit the prior 6.18 eV anodic-limit claim** with the real dominant anion.
- **Feeds:** Fig 1 (electrolyte), Fig 5.

### T2 — [CPU·DFT] Oxidation & reduction ladder (redox potentials vs Mg²⁺/Mg)
- For every T1 species: **vertical & adiabatic IP and EA**; convert to **potentials referenced to Mg²⁺/Mg** (compute Mg²⁺/Mg reference consistently; document the absolute→Mg conversion). Cross-check anion EAs with ωB97X-D/M06-2X.
- **DoD:** `redox_ladder.csv` + a potential-ladder figure (Mg²⁺/Mg, each anion oxidation & reduction). Identify which anion is **reduced before/around Mg plating potential** (the Al-co-deposition precursor).
- **Feeds:** Fig 5; the Al-co-deposition hypothesis.

### T3 — [CPU·DFT] Anion reductive-decomposition pathways → Al⁰ precursor
- For the most reducible anion(s) from T2, map **stepwise reductive decomposition** ΔG: e.g. [AlPhₓClᵧ]⁻ + e⁻ → … → loss of Ph⁻/Cl⁻ → low-valent Al → **Al⁰** (or AlClₓ). Identify the thermodynamically accessible route to deposited Al.
- **DoD:** `reduction_pathway.json` (steps + ΔG) + `.xyz` of each intermediate + a reaction-coordinate figure.
- **Feeds:** Fig 5; explains bare's metallic/alloyed Al (XPS 70.9 eV).

### T4 — [CPU·DFT] Al co-deposition / Mg–Al alloying (periodic)
- **Mg(0001) slab** (validated in T0). Compute: **Al adatom** adsorption (fcc/hcp hollow), **Al substitution** (surface & subsurface), **dilute Al-in-Mg** solution energy, and **Mg₁₇Al₁₂ (β)** formation energy. Reference chemical potentials (Mg bulk, Al bulk). Compare **ΔG(Al⁰ deposition/alloying) vs ΔG(Mg⁰ deposition)** at the plating front.
- **DoD:** `alloying_energetics.csv` + `.cif`s + verdict: is Al co-deposition/alloying thermodynamically favourable on bare? 
- **Feeds:** Fig 4–5; explains rough bare Mg (XRD random/coarse) + the Al⁰/alloy XPS state.

### ===== C2 — Why POSS excludes Al (LINCHPIN) =====

### T5 — [GPU·MD] Anion dynamics at the network interface (MD)
- **GROMACS** interface MD, **bare (liquid) vs poly (cured network)** (seeds: the .gro/.top/.itp). Build/relax an electrode-adjacent slab of electrolyte. Measure for the **Al-anion**: near-surface concentration profile, **residence time** in the interfacial zone, and **approach flux** to the anode plane; contrast with cation. (Recall anion D is 4.2× slower in the gel.)
- **DoD:** `anion_interface_dynamics.csv` + profiles figure + conclusion: does the network sterically/electrostatically **sequester the Al-anion from the reductive front**?
- **Feeds:** Fig 5 (kinetic suppression route).

### T6 — [CPU·DFT] Electron-transfer / passivation barrier (DFT)
- Build a **SiOₓ/POSS surface layer** on Mg(0001) (model the cured network's contact layer). Compute the **electron availability / transfer barrier** to an approaching Al-anion **with vs without** the SiOₓ/POSS layer (e.g., constrained-DFT electron transfer, or barrier of anion reduction at the covered vs bare surface).
- **DoD:** barrier table + DOS/charge-transfer figure + verdict: does the Si-rich layer **kinetically block** Al-anion reduction?
- **Feeds:** Fig 5 (passivation route). Depends: T0.

### ===== C3 — SEI composition, electronics, Mg²⁺ transport =====

### T7 — [CPU·DFT] Candidate SEI phase set (build + stability)
- Build periodic models: **MgO, MgCl₂, SiO₂(α-quartz)+POSS-cage, Al(fcc), Al₂O₃(corundum), Mg₁₇Al₁₂**, + a representative organic (THF-decomposition) fragment. Compute **formation energies** vs reference chem potentials (pymatgen convex-hull style).
- **DoD:** `sei_phase_stability.csv` + `.cif`s. Define the **poly SEI = SiOₓ/POSS + MgClₓ + MgO + organics** and **bare SEI = Al/AlOₓ(+Mg–Al) + MgClₓ + MgO + organics**.

### T8 — [CPU·DFT] SEI electronic structure (passivation quality)
- For each SEI phase/composite: **band gap / DOS**, electron-tunnelling tendency. Test the hypothesis: **Al-rich bare SEI is electronically leakier → continued parasitic reduction → self-discharge**; **Si-rich poly SEI is a better insulator/passivator**.
- **DoD:** DOS/gap table + figure + link to GITT (CE 27% vs ~100%, −320 mV/h self-discharge).
- **Feeds:** Fig 5; explains GITT/CV reversibility & self-discharge.

### T9 — [CPU·DFT] Mg²⁺ migration through the SEI (NEB)
- **CI-NEB** Mg²⁺ migration barriers (vacancy/interstitial) through the dominant poly vs bare SEI phases. Relate to **in-situ DRT** (poly higher-but-stable interfacial impedance).
- **DoD:** `mg_migration_barriers.csv` + NEB profiles. Conclusion: does the Si-rich poly SEI give a higher-but-stable Mg²⁺ barrier consistent with DRT?

### ===== C4 — Constant-potential interface AIMD (real ions) =====

### T10 — [CPU·AIMD] Interface AIMD with the real cation + Al-anion
- **CP2K** (or VASP) Mg(0001) + electrolyte containing the **actual [Mg₂Cl₃(THF)₆]⁺ AND an Al-anion**, **bare vs poly (network present)**, **constant-potential / charged-electrode** (fixes the prior neutral-surrogate, single-trajectory limitation). ≥ a few ps; **replicate** (≥2 trajectories each).
- **DoD:** trajectories + analysis (`aimd_interface.csv`): does the **Al-anion reduce/deposit on bare** and is it **suppressed on poly**? Mg approach distance, interfacial coordination, any bond-breaking. Snapshots for Fig 5. **Save all frames+energies+forces as MLFF training data for T16.**
- **Depends:** T0 (slab), T1 (anion), T5/T6 (network layer). **Honest caveats** documented (potential control, sampling).

### ===== C5 — Spectroscopy validation =====

### T11 — [CPU·DFT] XPS core-level shifts (Al 2p, Si 2p)
- Compute **relative core-level binding-energy shifts**: **Al 2p** for Al⁰/Mg–Al-alloy vs Al³⁺(oxide/chloride) — **target the 70.9 vs 74.0 eV (Δ≈3.1 eV) split**; **Si 2p** for elemental vs siloxane Si–O–Si. Use ΔSCF (molecular references) and/or final-state core-hole (periodic SEI). Reference/align consistently.
- **DoD:** `xps_shifts.csv` comparing computed Δ to measured (Al 2p 3.1 eV; Si 2p ~2 eV). This **validates the SEI assignment**.
- **Feeds:** Fig 3/5.

### T12 — [CPU·DFT] Raman/IR assignment
- Analytic frequencies + Raman activities (Gaussian/ORCA; or CP2K DFPT) for **free vs Mg-coordinated THF**, the **anion species**, a **polyether arm**, and the **POSS cage**. Assign the experimental **915 cm⁻¹ (retained)** and **1002→1034 cm⁻¹ shift**; rationalise the free/bound-THF change.
- **DoD:** `raman_assignment.csv` (mode → wavenumber → species) + an overlay figure vs the measured bands.
- **Feeds:** Fig 5; corroborates "first-shell preserved, network modes added."

### ===== C6 — Close the loop to performance =====

### T13 — [CPU·DFT +GPU·MLFF stats] Nucleation & texture (Al-free vs Al-containing surface)
- Compute Mg **adatom binding / surface-diffusion barriers** and heterogeneous-nucleation tendency on a clean vs **Al-decorated/alloyed** Mg(0001). Link to **XRD texture** (bare random/coarse vs poly oriented/conformal) and SEM (dendritic vs smooth).
- **DoD:** energetics table + a short argument connecting Al co-deposition → rough/random Mg; Al exclusion → oriented/smooth Mg.

### T14 — [CPU·desk] Self-discharge / overcharge mechanism
- Using T2/T3/T8: argue the **parasitic anion redox / shuttle** that explains bare's **CE 27%, OCV turnover ~1.29 V, −320 mV/h self-discharge**, and why the Si-rich passivating SEI suppresses it in poly. (Mechanistic synthesis, grounded in computed potentials & SEI electronics.)
- **DoD:** a `RESULTS_v2/` section + a mechanism schematic.

### T15 — [both] Integration & figure data
- Assemble `RESULTS_v2/REPORT_v2_master.md` mapping every computed result onto **ARTICLE_PLAN Part D** and **Fig 5**; export all figure-ready `.csv`/`.xyz`/`.cif`; write the "what reproduced / what didn't / open questions" summary.
- **DoD:** master report complete; STATUS.md all green; the Al-poor/Si-rich thesis either supported (with the numbers) or honestly qualified.

---

### ===== C7 — MLFF acceleration (GPU node) =====

### T16 — [GPU·MLFF] Train & validate an MLFF for Mg / electrolyte / SEI
- **Assemble training set** from CPU references: AIMD frames (T10), SEI phases & Mg–Al alloys (T4, T7), molecular/cluster single-points (T1). Elements {Mg, Al, Cl, O, C, H, Si}.
- **Fine-tune a foundation MLFF** (MACE-MP-0 / CHGNet / M3GNet) or train NequIP/Allegro/DeePMD. **Active learning:** committee/uncertainty → high-σ configs sent to CPU (CP2K/VASP) for labels → retrain until converged.
- **DoD:** model + `mlff_validation.csv` (energy & **force MAE** vs held-out DFT; target force MAE ≲ 50 meV/Å), learning curve, dataset+model version. **Must reproduce T10 AIMD** (Mg approach; Al reduction-or-not). 
- **Depends:** T4, T7, T10.

### T17 — [GPU·MLFF] Large-scale reactive interface, SEI growth & Al co-deposition
- With the validated MLFF, run **large-cell, long-time reactive MD** of Mg(0001)|electrolyte, **bare vs poly (network present)** under plating conditions. Quantify: **Al-anion reduction & Al co-deposition on bare vs suppression on poly**; **SEI nucleation/growth & composition vs depth (Si-rich vs Al-rich)**; deposit morphology/texture; event statistics. *(This reaches the scales single-trajectory AIMD cannot — it is how you actually reproduce the ToF-SIMS Al-poor/Si-rich + confinement result.)*
- **DoD:** trajectories + `mlff_interface.csv` (Al deposition amount/rate, SEI composition–depth profile, Mg morphology) that **reproduces ToF-SIMS Al-poor/Si-rich + ~90 nm confinement**; spot-validate configs against DFT; honest caveats (MLFF accuracy, applied conditions). Feeds Fig 5/6.
- **Depends:** T16, T10, T5, T6.

## 5. DEFINITION OF DONE (project)
- T0–T17 committed, each with a `REPORT.md` + machine-readable outputs + structures.
- The **Al co-deposition (bare) vs suppression (poly)** mechanism is quantified (T2–T4, T10) and the **Si-rich/Al-poor** composition is explained (T5–T8).
- The **XPS Al 2p split** (T11) and **Raman shifts** (T12) are reproduced or explained.
- `REPORT_v2_master.md` integrates everything into the ARTICLE_PLAN's narrative — **Si in, Al out; transport equal; reversibility is the win.**
- **MLFF (T16–T17) is DFT-validated** (force/energy MAE reported; uncertain configs active-learned) and **reproduces the ToF-SIMS Al-poor/Si-rich + confinement** result.
- **No fluorine story anywhere.** Honest caveats retained (Part E of the plan).

## 6. GUARDRAILS (repeat)
No F/triflate narrative · compute everything · bare-vs-poly always · transport is not the discriminator (don't invent one) · frequency/convergence-verify, replicate AIMD, report uncertainties · build-models-are-labelled-as-models · **MLFF results never reported without DFT cross-checks (report MAE; active-learn high-σ configs)** · use the right node per ticket tag · revisit the 6.18 eV anodic-limit claim · cite methods/refs in each REPORT.md.

*Start: T0 → T1. The paper hinges on Al-poor / Si-rich. Read `ARTICLE_PLAN_v3_interface_composition.md` before T1.*
