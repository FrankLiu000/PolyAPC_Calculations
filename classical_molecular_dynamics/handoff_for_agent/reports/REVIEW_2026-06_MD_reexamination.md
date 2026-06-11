# Re-examination of the poly-APC classical-MD campaign — QC, new descriptors/heatmaps, and new stories
*review round, 2026-06-11 · LYZ-ROG · GROMACS 2025.1 · figures in `figs_review2026/`*

This is an independent audit of the committed classical-MD campaign (Stories A.1/A.2/A.4/B/C and
the five-story synthesis). It (1) re-checks the simulation set-up and structural integrity, (2) adds a
new 2-D/3-D descriptor + heat-map suite, (3) re-reads the old stories against the literature, and
(4) proposes new, falsifiable stories. The headline campaign result — **σ_poly > σ_bare is
de-pairing-driven with mobility preserved in the swollen gel** — survives the audit; two methodological
caveats are quantified and one new structural confound is found.

---

## 0. TL;DR

| Question asked | Verdict |
|---|---|
| Is the **box** reasonable? | **Yes.** 7.24–7.47 nm cubic, ~36–40 k atoms; cutoff 1.0 nm ≤ L/2, minimum-image satisfied. Large-cell cross-check 14.7 nm / 303 k atoms. |
| Is the **force field** reasonable? | **Yes, with a caveat.** OPLS-AA (comb-rule 3, fudge 0.5/0.5); scaled-charge Mg **+1.2** / μ-Cl −0.467. +1.2 is *more aggressive* than the ECC-canonical **+1.5** → a robustness run was launched (Story E). |
| **Thermostat / barostat**? | **Yes.** Production NVT 298 K, v-rescale (τ=0.5 ps): T = 298.0 ± 0.005 K, drift ~0.01 K. Pre-equilibration NPT used c-rescale (correct ensemble). |
| **Structural integrity** before/after? | **Intact.** [Mg₂(μ-Cl)₃·6THF]⁺ rigid (Mg–μCl 0.251 ± 0.002 nm over 100 ns); whole-system COM drift 0.66 Å; energies stable. |
| Do **polymer chains run out of the box**? | **No — that appearance is a PBC rendering artifact of a *correctly percolating* network** (see Fig 1). It is not a simulation error. |
| Anything **unreasonable → rebuild/re-simulate**? | Two caveats: **(a)** 1-ns NPT pre-eq is too short (bare density still climbing +50 kg/m³; ion-pairing needs tens of ns — already a campaign caveat); **(b) NEW: polymer connectivity is not matched across systems** (4- and 16-POSS are single percolating networks; **8-POSS "swollen" is fragmented**). A charge-robustness re-sim is running; a matched-connectivity rebuild is proposed (Story F). |

---

## Part I — Set-up & structural-integrity audit

### I.1 Box, force field, ensemble (all sound)
- **Box.** bare 7.246, 4-POSS 7.291, 8-POSS 7.349, 16-POSS 7.471 nm (cubic). r_vdw = r_coulomb = 1.0 nm
  ≤ L/2 ≈ 3.6 nm ⇒ minimum-image OK; PME for electrostatics; DispCorr=EnerPres. Large-cell σ_coll/η
  work used a 2×2×2 tiling (14.7 nm, 303 k atoms) — correct way to beat finite-size noise.
- **Force field.** Self-contained OPLS-AA `[defaults] nbfunc=1, comb-rule=3, fudgeLJ=fudgeQQ=0.5`.
  Mg σ enlarged to 0.22 nm to avoid collapse with the scaled charge — a standard pragmatic choice.
  Cluster net charge verified +1 (2×(+1.2) + 3×(−0.467) = +0.999); bare carries the documented
  harmless −0.008 e residual (handled by PME background).
- **Thermostat/barostat.** Production = **NVT 298 K, v-rescale τ=0.5 ps, 2 fs, h-bond LINCS** (confirmed
  in `prod.tpr`). Energy stats over 100 ns: T = 298.0 ± 0.005 K (drift ≈ 0.01 K); total-E drift
  −0.2 %; NVT pressure within ±55 bar of 0 (RMSD ~230 bar — normal). comm-mode = Linear (nstcomm 100).
  Pre-eq NPT used **c-rescale** (a correct-ensemble barostat) — note the campaign's own Story C flag
  that c-rescale fluctuation-based moduli are unreliable; that is a separate, already-stated caveat.

### I.2 The "polymer out of the box" question — resolved (Fig 1)
The poly-APC network (resname NET1) is a **single covalently-bonded molecule** (4-POSS: 10 119 atoms;
16-POSS: 14 678 atoms) whose extent **equals the box in all three axes** (ratio 1.000). Measured on
`prod/poly/prod.xtc` (100 ns):
- **211–314 intra-network bonds cross the periodic boundary** in steady state (2.1 % of 10 258 bonds).
  A percolating cross-linked gel is *supposed* to tile space through its periodic images — so when the
  molecule is drawn "whole" (un-wrapped from one atom), segments necessarily appear to shoot out of the
  cell (**Fig 1B**). Wrapped back into the cell, **every atom is inside** (**Fig 1A**). This is a drawing
  artifact, not an escaping/expanding polymer.
- **Network R_g = 3.59 ± 0.07 nm, flat over 100 ns** (no swelling or collapse; Fig 1C).
- **[Mg₂(μ-Cl)₃] core**: Mg–μCl nearest-3 distance = **0.251 ± 0.002 nm, flat** (Fig 1D) → dinuclear
  core and whole [Mg₂Cl₃·6THF]⁺ speciation intact throughout, matching the RDF CN = 3.0.
- whole-system COM drift = **0.66 Å over 100 ns** ⇒ no flying-ice-cube.

**Practical note for visualization:** render trajectories with `gmx trjconv -pbc atom -ur compact`
(or `-pbc whole` per *small* molecule only), never `-pbc mol/nojump` on the percolating NET1, or the
network will look like it explodes out of the box.

### I.3 Two real caveats
1. **Pre-equilibration too short (1 ns).** NPT density traces: 4-POSS plateaus at 1.000 g/cm³ (last-quarter
   drift small), but **bare is still compacting** (density 0.94→0.96 g/cm³, +50 kg/m³ over the run; not
   plateaued). The production NVT box is nonetheless within ~0.5 % of mechanical equilibrium (bare NVT
   pressure +45 bar, K≈1 GPa ⇒ ΔV/V≈0.45 %). The large cell (50 ns pre-eq) is properly converged
   (density drift −2.7 kg/m³). Ion-pairing itself equilibrates over tens of ns — already the campaign's
   key caveat. **Impact:** absolute D/η carry this uncertainty; ratios and the de-pairing mechanism do not.
2. **NEW — network connectivity is not matched across systems.** Largest polymer fragment: 4-POSS
   **10 119** atoms (percolates, 2.1 % bonds cross PBC), 16-POSS **14 678** (percolates), but
   **8-POSS "swollen" only 2 530** atoms (fragmented; extent 0.97 box; 0.8 % bonds cross). So the
   8-POSS system is modelled closer to a polymer *solution* than a percolating *gel*. The cross-system
   comparison therefore confounds **POSS loading** with **network topology / molecular weight** — this
   plausibly contributes to the 8-POSS swollen diffusing *faster* than the denser-network 4-POSS gel
   (D_cat 0.033 vs 0.011), beyond the "more free THF" explanation. → Story F.

**Re-simulation decision.** No emergency rebuild is warranted (the headline result rests on speciation/
RDF/contact statistics, which are robust). The highest-value re-sim — a **charge-scaling robustness run
(Mg +1.5)** — was launched (`prod/charge15/`, Story E). A matched-connectivity rebuild is recommended
as future work (Story F), not run here.

---

## Part II — New descriptor & heat-map suite (`figs_review2026/`)

All maps use the converged window (last 50 ns) pooled over the available replicates (bare ×5, 4-POSS ×3,
8-POSS ×5 seeds, 16-POSS ×1). Methods follow TRAVIS-style CDF/SDF best practice (Brehm et al.,
*J. Chem. Phys.* **152**, 164105, 2020) and PMF-by-inversion W(r) = −kT ln g(r).

| Fig | Descriptor (what is on the axes) | What it shows |
|---|---|---|
| **2a** `fig2a_gr_heatmap` | g(r) heat-strip, system × r, for Mg–Cl_anion / Mg–O_THF / Mg–O_polymer | de-pairing (anion peak dims 93→60) + latent-ligand activation + THF re-solvation across loading |
| **2b** `fig2b_cdf_*` | **radial–angular CDF** g(r, cosθ) around the Mg–Mg axis (anion-Cl, THF-O) | anion-Cl sits at an **equatorial bridging site** (r≈0.20 nm) **+ axial end-on lobes** (cosθ≈±1) **+ a structured outer shell** (r≈0.5 nm) |
| **3** `fig3_sdf3d` | **3-D spatial distribution function** (marching-cubes isosurfaces) around the rigid core | the THF "crown" and the red anion-Cl CIP lobes in 3-D; lobe density thins bare→16-POSS |
| **4a** `fig4a_pmf` | Mg–anion **PMF** W(r) + contact-pair CN bar | the contact **bond is not weakened** (well ≈ −11 kJ/mol, conserved); the **population collapses** (CN 0.95→0.58) ⇒ de-pairing is **competition/availability-driven**, not bond-weakening |
| **4b** `fig4b_fes2d` | **2-D free-energy surface** F(N_anionCl, N_outerO) | the de-paired basins drop in free energy with loading (bare 15 → 16-POSS 4 kJ/mol); in 16-POSS the O-coordinated de-paired state sits only ~1 kJ/mol above the CIP ground state — the **coordination paradox as a landscape** |
| **5** `fig5_interaction` | Mg-cluster ↔ {anion, solvent, polymer, initiator} short-range Coulomb & LJ matrix | the cluster **re-partitions** its interactions: Mg–anion Coulomb weakens (−97→−69 kJ/mol·cluster) while Mg–polymer LJ grows (0→−65) |
| **6** `fig6_fingerprint` | normalised **descriptor fingerprint**, 10 descriptors × 4 systems | one-glance summary of the whole loading ladder; the 8-POSS column also exposes its fragmented-network anomaly (low outer-THF, weak Mg–polymer LJ) |
| **7** `fig7_charge_robustness` | CIP% bar, bare vs swollen at Mg **+1.2** vs **+1.5** (Story E) | de-pairing gap preserved under ECC-canonical charge ⇒ conclusion robust to FF charge scaling |

**Two genuinely new structural insights from the maps**
- **The Mg–anion bond is conserved; only the population shifts** (Fig 4a). De-pairing here is *not* a
  weaker pair — it is Le-Chatelier competition from the latent-ligand oxygens. This refines the campaign's
  "de-pairing" language.
- **CIP geometry is bimodal** (Fig 2b/3): an equatorial bridging mode and an axial end-on mode. Which mode
  the latent-ligand O displaces first is an open, testable question (Story H).

---

## Part III — Review of the old stories (do they hold up?)

The five synthesis stories and A/B/C are **internally consistent and survive the audit**; my re-computed
numbers reproduce the campaign's (CIP: bare 94 %, 8-POSS 84 %, 16-POSS 57 %; Mg–anion Coulomb −97/−93/−69;
t₊≈0.5). Specific assessments:

- **Story 1 "speciation-transparent gel" [robust] — CONFIRMED.** Core intact in every system (Fig 1D, 2a).
- **Story 2 "dual-mode / anion-philic solvation" [robust] — CONFIRMED** by the interaction matrix (Fig 5):
  cation is Coulomb-solvated, anion vdW-solvated.
- **Story 3 "latent-ligand network" [trend→robust] — CONFIRMED and sharpened.** Fig 4a shows *why* the
  latent oxygens de-pair: they out-compete the anion at conserved pair-bond strength.
- **Story 4 "coordination paradox" [trend] — CONFIRMED and now visual** (Fig 4b): freed cations fall into a
  matrix-O-tethered basin instead of becoming fast free Mg²⁺. **Strongly supported by new literature**
  (eNMR, JACS 2024: Mg²⁺ t₊≈0.22 in PEO; apparent-high t₊ collapses once clustering is accounted for).
- **Story 5 "iso-mobility tortuosity brake / t₊-invariant" [robust@4, trend@16] — HOLDS, but flagged.** t₊
  was computed from the **Nernst–Einstein** ratio D₊/(D₊+D₋), which the literature shows **overestimates**
  transference by ignoring ion–ion correlations (can even mask negative transference). → Story D upgrades this.
- **A.1/A.2/A.4/B/C — HOLD.** The D-revision (swollen ÷1.6 slower than bare, superseding "D preserved"),
  the σ_coll/ionicity corroboration, Arrhenius (Ea swollen ≤ bare), Raman↔population mapping, and the
  free-THF-percolation/swelling mechanics are all consistent with the structural maps here. The **8-POSS
  connectivity confound (I.3.2)** is the one new asterisk on the transport/mechanics comparisons.

---

## Part IV — New story proposals

Priority order; **E is already running**, **D and H are pure analysis on existing trajectories**, **F needs new builds**.

### Story D — *True (Onsager) transference: is the conductivity gain real charge separation?* **[high value, analysis-only]**
**Anchor.** eNMR + Onsager-coefficient theory (Cresce/Schönhoff *JACS* 2024; Fong/McCloskey *Chem. Sci.*
2021; Balsara/Newman *JACS* 2022): Nernst–Einstein t₊ is an upper bound; ion correlations can collapse or
reverse it. The campaign's t₊≈0.5 is the *ideal* value.
**Hypothesis.** Because the freed Mg²⁺ is re-trapped (Story 4) and moves with correlated partners, the
*correlated* transference t₊^corr < t₊^NE, and the conductivity gain is partly **vehicular/correlated**, not
clean cation–anion separation.
**MD work (reuse `large_swollen8` + replicates).** Compute the full Onsager matrix L_{++}, L_{--}, L_{+-}
from collective charge-current correlations (the σ_coll machinery from A.2 already yields the diagonal
terms; add the distinct/cross MSD ⟨Δr_i·Δr_j⟩). Report t₊^corr and the ionicity-resolved transference,
bare vs swollen. **Decision value:** tells whether "de-pairing → σ" is genuine charge transport.

### Story E — *Force-field robustness of de-pairing (Mg +1.2 vs ECC-canonical +1.5)* **[RUNNING]**
**Anchor.** Kirby & Jungwirth *JCP* 2020 (ECC q = q/√ε_el ⇒ Mg²⁺ ≈ +1.5); +1.2 (factor 0.6) is more
aggressive; integer-charge non-polarizable MD over-pairs (arXiv 2308.05482). Reviewers will demand this.
**Hypothesis.** The *ordering* "swollen de-pairs relative to bare" is invariant to the Mg charge; only the
absolute CIP magnitudes shift (more pairing at +1.5).
**MD work (launched).** bare + 8-POSS swollen re-run at **Mg +1.5 / μ-Cl −0.667** (cluster charge preserved),
NVT 298 K, from the +1.2-equilibrated coords — `prod/charge15/`. Compare CIP% and the de-pairing gap.
**Result (converged, 40 ns NVT, last-10 ns window — Fig 7):** at +1.5 the bare system is essentially
unchanged (CIP 94.2→94.4 %, already near-saturated) while swollen pairs a little more (83.8→86.2 %), so the
**de-pairing gap bare−swollen narrows from 10.4 pts @+1.2 to 8.1 pts @+1.5 but stays clearly positive and in
the same direction**. ⇒ the "swollen de-pairs relative to bare" conclusion is **robust to the Mg charge**;
its *magnitude* is moderately charge-sensitive (gap 8–10 pts). Note the preliminary 8-ns read (gap 9.5)
slightly overstated it — the converged value is 8.1. Raw: `analysis/review2026/RESULTS_storyE.txt`.

### Story F — *Matched-connectivity scan: separate POSS loading from network topology* **[high value, needs builds]**
**Anchor.** I.3.2 (8-POSS is fragmented, 4/16-POSS percolate) + percolation-transport literature
(ACS Polymers Au 2022; Energy Storage Mater. 2024: percolating network → fast hopping; fragmented clusters
→ barriers). The plan's Story A.3 deconfounding was *skipped*.
**Hypothesis.** At **fixed, percolating connectivity**, de-pairing scales with total coordinating-O
(loading × conversion) — collapsing 4/8/16 onto one curve — while transport tracks **percolation/tortuosity**,
not loading per se. The 8-POSS "swollen advantage" is partly its disconnected polymer, not just swelling.
**MD work.** Rebuild 4/8/16-POSS at matched network connectivity (all single percolating networks) and a
matched-composition swollen-vs-dense pair (fixed free-THF); read out CIP, D, t₊, Mg–polymer-O. New EM→NPT
(≥50 ns, fixing caveat I.3.1)→NVT runs.

### Story H — *Bimodal CIP geometry: which contact de-pairs first?* **[novel, analysis-only]**
**Anchor.** The new radial-angular CDF/SDF (Fig 2b/3) resolve an **equatorial bridging** CIP and an
**axial end-on** CIP. Standard 1-D RDFs cannot see this.
**Hypothesis.** The latent-ligand polymer-O preferentially displaces the **axial** anion (open coordination
face) before the equatorial one; de-pairing is therefore geometrically selective.
**MD work.** Classify each contact pair as axial/equatorial per frame; track each population vs loading and
correlate with polymer-O insertion events. Pure analysis on existing trajectories.

### Story G (context, not classical-MD) — *Monomer vs dimer reality.*
Canepa/Persson *EES* 2015: at equilibrium the **MgCl⁺ monomer**, not the dimer [Mg₂Cl₃·6THF]⁺, is the
thermodynamically stable cation in THF/DME. The classical FF **hard-codes the dimer as a bonded complex**,
so it *cannot* address this equilibrium — a structural limitation of the whole campaign. **Hand this to the
DFT/AIMD v2 program:** does swelling the gel shift the monomer↔dimer balance? This reframes "which carrier
the gel mobilizes."

---

## Part V — Literature grounding (high-impact)

- **Speciation / de-pairing→σ:** Canepa et al. *EES* 8, 3718 (2015); Rajput, Persson et al. *JACS* 137,
  3411 (2015) — Mg pairs readily; weakening pairs liberates carriers. ✔ consistent with the campaign.
- **Coordination paradox / transference:** Cresce, Schönhoff et al. *JACS* 146 (2024); Fong/McCloskey
  *Chem. Sci.* (2021); Balsara/Newman *JACS* 144 (2022) — Mg²⁺ t₊ stays low/≈0.22, NE overestimates. ✔
  strongly supports Stories 4/5/D.
- **Dendrites / mechanics:** Monroe & Newman *JES* 152, A396 (2005) (G′ ≳ 2 G_metal); but cross-linked PEO
  suppresses Li dendrites at ~0.1 MPa (Khurana/Archer *JACS* 2014) — the criterion over-predicts; for Mg the
  bar is looser. Frames Story C honestly.
- **Mobility–viscosity decoupling:** Wang/Sokolov *PRL* 108, 088303 (2012) — supports A.2's Stokes–Einstein
  breakdown (η ×7.4, D only ×2).
- **FF caveat:** Kirby & Jungwirth *JCP* 153, 050901 (2020); Borodin *Chem. Rev.* 119, 7940 (2019) — Mg²⁺
  ECC ≈ +1.5; +1.2 needs the Story-E sensitivity check.
- **Visualization methods:** Brehm et al. (TRAVIS) *JCP* 152, 164105 (2020) — CDF/SDF standard followed here.

---

## Appendix — provenance
- Analysis code + figures: `polyAPC/analysis/review2026/` (descriptors.py, extract_sdf.py, integrity.py,
  fig_*.py); figures copied to `figs_review2026/`.
- Robustness re-sim: `polyAPC/prod/charge15/` (Mg +1.5; bare + 8-POSS; NVT 40 ns; run_q15.sh).
- Descriptors recomputed from `prod/{bare,poly,swollen8}` and `poss16/`; interaction energies from
  `analysis/{bare,poly,swollen8}/ene` + `poss16/ene` (gmx energygrps rerun, short-range only — PME-reciprocal
  not decomposed; scaled-charge OPLS ⇒ effective/trend-level, per the standing campaign caveat).
