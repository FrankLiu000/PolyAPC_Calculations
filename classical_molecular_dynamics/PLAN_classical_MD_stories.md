# Classical-MD story plan — driven by the wet-lab data (poly-APC vs bare-APC)

**Scope.** This is the *next round* of classical molecular-dynamics work, framed as
hypothesis-driven **stories** that each map a concrete wet-lab observable onto a specific
MD investigation. It builds on — and does **not** re-derive — the completed campaign in
`handoff_for_agent/`, whose central result is already established and validated:

> **σ_poly > σ_bare is de-pairing-driven, with ion mobility preserved in a swollen gel.**
> (free-carrier fraction f: 0.167→0.247 bare→swollen-8-POSS; D preserved at ≈98 % of bare;
> σ ∝ f·D ≈ ×1.44.)

Runs execute on **LYZ-ROG** (GROMACS 2025.1). This document is the shared plan that syncs
via GitHub. Three story lines are in scope — **(A) tighten the σ story, (B) spectroscopy
population mapping, (C) mechanics & morphology** — plus a protocol appendix.

> **Force-field caveats carried from the existing campaign (apply to every story below):**
> non-polarizable OPLS-AA; Mg/Cl **scaled charges** (Mg +1.2, bridging Cl −0.467); APC
> cation/anion are *bonded complexes* (inner 3 THF / 3 Cl exchange suppressed); reported
> interaction energies are **short-range only** (PME-reciprocal not decomposed). → all
> classical numbers are *effective/trend-level*, not ab-initio.

---

## 0. Observable → story matrix

| Wet-lab probe | Measurement (bare → poly) | Story | MD observable produced | Confidence |
|---|---|---|---|---|
| Conductivity σ | σ_poly > σ_bare | **A** | σ∝f·D, σ_coll, ionicity, Eₐ | High (extends a done result) |
| in-situ DRT R_ct | higher but **stable** over 30 cyc; ~4.4× slow | **A** | D(T), Eₐ → R_ct magnitude+stability | Medium |
| Raman 999→1002 cm⁻¹ (+8 %) | anion → "free" position | **B** | free-anion fraction | High |
| Raman 181 cm⁻¹ (×2.0) / 276 cm⁻¹ (−30 %) | Mg–Cl dissociated up / bridge down | **B** | dissociated-vs-bridged Mg–Cl populations | High |
| Raman 1483→1486 cm⁻¹ (+3.2) | coordinated-THF stiffening | **B** | bound-THF fraction, residence time, RDF sharpness | Medium |
| SEM smooth vs dendritic; CCD 3.0 mA cm⁻²; cycle life 842/3344 | poly dendrite-free, mechanically robust | **C** | shear modulus, mesh size ξ, swelling, percolation | Medium–exploratory |

Cross-checks against existing data live in `handoff_for_agent/` (`rdf/`, `solvation/`,
`transport/`, `interaction_energies/`); Raman in `../Raman/peak_assignments.csv`; DRT in
`../in_situ_DRT/`; electrochemistry/SEM in `../HANDOFF_computational_v2_Al_and_wetlab.md`.

### Explicitly OUT of scope for classical MD (→ DFT/AIMD v2 campaign)
The **Al 2p XPS split (70.88 → 73.98 eV)**, MgF₂ / triflate-derived SEI formation, any
**bond breaking, electron transfer, or constant-potential electrode** dynamics. These are
chemistry that a non-reactive classical FF cannot represent; they are already routed to the
`computational_v2/` Gaussian+CP2K program. This plan deliberately stays on the
**structure / transport / mechanics** axis where classical MD is predictive.
(Electrode-interface PMF and a deeper t+ mechanism study were considered and **deprioritized**
for this round.)

---

## Story A — Tighten & de-risk the conductivity story

**Wet-lab anchor.** Measured σ_poly > σ_bare; in-situ DRT shows poly R_ct higher but
**stable** across 30 cycles, consistent with the ~4.4× transport slowdown in the (dense)
gel and a non-growing interphase.

**Why now (open gaps in the existing result).**
- Collective σ is **very noisy** (bare ranged 0.036–0.169 mS cm⁻¹, single-config); the σ
  claim currently rests on the two *robust* observables (contact-pairing + self-D), not σ_coll.
- The swollen-8-POSS resolution rests on only **2 × 50 ns**.
- The 4→16-POSS de-pairing trend is **confounded**: loading (4→16) co-varies with cure
  conversion (69 %→100 %), so "total coordinating-O" is the real variable, not POSS count.
- No temperature dependence → cannot yet rationalize the R_ct **magnitude** or its **stability**.

**Hypotheses.**
1. With adequate sampling, σ_poly/σ_bare firms to ≈1.4 (the f·D estimate) *with error bars*.
2. Free-carrier f scales with **total coordinating oxygen = loading × conversion**, not raw
   POSS count → the loading/conversion confound, once separated, collapses onto one curve.
3. Eₐ(poly) ≈ Eₐ(bare) in the swollen regime → the higher DRT R_ct is **carrier-number-
   limited**, not a higher migration barrier, and is stable because speciation is intact.

**MD work.**
1. **Swollen replicates:** 8-POSS swollen → **5 × 100 ns** (independent seeds) → tighten f,
   D(cat/an), and σ∝f·D with SEM error bars (supersedes the 2 × 50 ns).
2. **Large low-crosslink cell:** rebuild the swollen gel at **≈2–4× box** (≈150–300k atoms),
   compute σ_coll by **Einstein–Helfand** with block averaging + ionicity σ_coll/σ_NE to
   beat finite-size/correlation noise; report whether σ_coll magnitude now matches f·D.
3. **Deconfounding matrix** (each ≥3×100 ns):
   - 4-POSS at **100 % conversion** vs the existing **69 %** (loading fixed, conversion varied);
   - **matched-conversion loading scan** 4 / 8 / 16 POSS at a single conversion;
   - **swollen vs dense at matched composition** (free-THF count fixed) → isolate confinement
     from chemistry.
   Read out f, D, Mg–polymer-O contact for each.
4. **Arrhenius:** D(T) and σ(T) at ~5 temperatures (273–333 K) for bare and swollen-poly →
   Eₐ; relate to DRT R_ct magnitude and its cycle-to-cycle stability.

**Predicted signatures / deliverables.** A transport table with SEM; a single f-vs-(loading×
conversion) master curve; an σ(T)/Eₐ figure; an explicit statement of whether σ_coll (now
de-noised) corroborates the f·D mechanism. **Decision value:** converts the de-pairing story
from "two robust proxies" to a directly defensible σ with errors.

**Confidence/caveats.** High that f and D tighten; medium that σ_coll magnitude converges
(collective transport is intrinsically noisy even in large cells); Eₐ is FF-effective.

---

## Story B — Spectroscopy population mapping (Raman ↔ MD populations)

**Wet-lab anchor (`../Raman/peak_assignments.csv`).**
- **999 → 1002 cm⁻¹** anion phenyl breathing, **+2.9 cm⁻¹, +8 % intensity** → anion shifts
  toward the **free** position (de-association).
- **181 cm⁻¹** Mg–Cl (dissociated) **×2.0 intensity**; **276 cm⁻¹** [Mg₂Cl₃]⁺ bridge **−30 %**.
- **1483 → 1486 cm⁻¹** coordinated-THF CH₂ deformation **+3.2 cm⁻¹** (shell stiffening).
- **915 cm⁻¹** THF ring-breathing ≈ unchanged (internal reference).

**Why now.** The existing campaign reported a single "contact-pairing %"; it never tied the
**individual Raman bands** to distinct MD population order-parameters. Each band reports a
*different* equilibrium, so each is a separate, falsifiable cross-check.

**Hypothesis.** The bare→poly intensity/shift trend of each band is tracked monotonically by
a corresponding MD population computed from the existing/extended trajectories.

**MD work — define and compute, across all 4 systems:**
1. **Free-anion fraction** — fraction of [Ph₂AlCl₂]⁻ with **no** Mg–anion-Cl contact (first-
   shell cutoff from the Mg–AnCl RDF minimum) ↔ **999→1002 +8 %**. Already implied by
   pairing % (83.3→75.3 %); recast explicitly as "free-anion population".
2. **Dissociated vs bridged Mg–Cl** — classify each Mg by whether it sits in an intact
   [Mg₂(μ-Cl)₃] bridge vs a dissociated/terminal Mg–Cl, using Mg–Cl(bridge) coordination and
   Mg–Mg distance ↔ **181 cm⁻¹ ×2.0** (dissociated up) and **276 cm⁻¹ −30 %** (bridge down).
3. **Bound-vs-free THF** — Mg first-shell THF-O occupancy (CN), plus **bound-THF residence
   time / exchange rate** (survival autocorrelation) and **Mg–O RDF first-peak sharpness**
   (height/FWHM) ↔ **1483 +3.2** (a tighter, more constrained coordinated-THF stiffens).
4. **Correlation table:** ΔRaman(band) vs ΔMD-population(system), with the 915 cm⁻¹ band as
   the null control (should map to ~no population change).

**Deliverable.** `handoff_for_agent`-style `solvation/` outputs extended with these four
order-parameters + a **Raman-band ↔ MD-population correlation table** validating each
assignment.

**Confidence/caveats.** High for bands 1–2 (populations, which classical FF captures);
**medium** for the 1483 cm⁻¹ stiffening — classical MD supplies the *structural driver*
(occupancy, residence time, shell sharpness), but the **+cm⁻¹ frequency shift itself is a
DFT job** (computational_v2 P3 Raman). State this boundary explicitly in the writeup so the
band assignment is not over-claimed.

---

## Story C — Mechanics & morphology (new story)

**Wet-lab anchor.** Post-30-cycle SEM: poly deposits **smooth and dendrite-free**, bare is
**rough/dendritic**; CCD stable to **3.0 mA cm⁻²**; Mg‖Mo₆S₈ cycle life **842 @ 0.5C / 3344
@ 1C**; in-situ DRT shows **no impedance growth** (mechanically stable bulk/interphase).

**Why now.** The campaign has characterized *transport and speciation* but never the
**network's mechanical/structural** properties — yet the most visible wet-lab difference is
*morphological*. This is a genuinely new, non-duplicative story.

**Hypothesis.** A **percolating elastic POSS network** with nm-scale mesh supplies a shear
modulus and flux-homogenizing tortuosity that **mechanically suppresses dendrites**
(**Monroe–Newman** stability criterion: a separator/electrolyte with shear modulus
G′ ≳ ~½ G_Mg stabilizes the metal interface), while the **swollen THF channels** keep ions
mobile (Story A). I.e. poly buys mechanical dendrite-suppression *without* the mobility
penalty of a dense gel.

**MD work.**
1. **Network topology & mesh:** strand-length distribution between junctions; POSS-junction
   spacing (campaign notes ~4.5 nm); crosslink density; mesh/correlation length ξ from the
   polymer **structure factor** S(q) and/or pore-size distribution; **free-THF channel
   percolation** (connected-cluster analysis of the solvent sub-phase) — does a percolating
   liquid-like channel survive at swollen loading but pinch off when dense?
2. **Mechanical moduli:** shear modulus G and bulk modulus K vs POSS loading (4/8/16) via
   **(a)** stress-fluctuation (Born + kinetic + fluctuation terms) in NPT/NVT, and/or
   **(b)** small finite-strain box deformations (affine shear/tension, fit stress–strain);
   **swelling ratio** from equilibrium solvent uptake.
3. **(Optional) flux-homogeneity proxy:** spatial variance of ion displacement across the
   cell as a coarse dendrite-nucleation surrogate (lower variance ⇒ more uniform plating).

**Predicted signatures / deliverables.** modulus(loading) and ξ(loading) and swelling tables;
a statement of whether the swollen gel sits **above** the Monroe–Newman G′ threshold while
retaining a percolating THF channel — i.e. the structural explanation for *smooth deposition +
high CCD + long life at preserved σ*. Figures: S(q)/mesh, stress–strain, modulus-vs-loading.

**Confidence/caveats.** Exploratory. Classical moduli are **FF-dependent** (OPLS + scaled
charges) → report **trends across loading**, not absolute GPa values; small boxes truncate
**long-wavelength** mechanics (the very modes dendrites exploit) → treat ξ and G as
finite-size-limited; dendrite suppression is **inferred via the modulus criterion**, not
directly simulated (true dendrite growth needs electrodeposition modeling beyond equilibrium
MD). Frame as a mechanistic hypothesis with a quantitative modulus estimate, not proof.

---

## Appendix — simulation & analysis protocols

Conventions match the existing `handoff_for_agent/` (GROMACS 2025.1; OPLS-AA self-contained
`[defaults]`+`[atomtypes]`, comb-rule 3, fudgeLJ=fudgeQQ=0.5; PME; Mg +1.2 / Cl −0.467
scaled). Reuse the four committed systems (`00_bareAPC`, `01_polyAPC_4POSS_gel`,
`02_polyAPC_8POSS_swollen`, `03_polyAPC_16POSS_dense`) as starting points; the real
`em/nvt/npt/prod.mdp` and topologies live on LYZ-ROG.

**Common pipeline.** `gmx grompp -maxwarn 8` → `gmx mdrun`; equilibration EM → NVT → NPT
(Parrinello–Rahman barostat, v-rescale/Nosé–Hoover thermostat, 1 fs) before each production
run; trajectories regenerated locally (gitignored), only small analysis outputs committed.

| Story | Systems / variants | Ensemble & length | Key analysis |
|---|---|---|---|
| **A** | swollen-8 ×5 seeds; large swollen cell (≈2–4× box); deconfound set (4@100 %, 4/8/16 matched-conv, swollen/dense matched-comp); T-scan 273–333 K | NPT 300 K prod, **5×100 ns** (swollen), ≥3×100 ns (deconfound), 5 T-points | `gmx msd` (D, Einstein 20–80 ns window); `gmx current` / Einstein–Helfand + block avg (σ_coll, ionicity vs `gmx ... ` N-E); f from first-shell contact; Arrhenius fit of ln D, ln σ vs 1/T |
| **B** | the 4 base systems (+ swollen replicates from A) | reuse A's prod trajectories (no new runs needed beyond A) | `gmx rdf`/`gmx coord` (Mg–AnCl, Mg–Clb, Mg–O) → contact cutoffs; custom Python for free-anion / bridged-vs-dissociated / bound-THF populations; survival-autocorrelation for THF residence time; RDF peak height/FWHM |
| **C** | 4/8/16-POSS gels (dense & swollen) | NPT 300 K equilibration; deformation runs (series of fixed-strain NVT) or long NPT for stress fluctuations | polymer S(q) & pore-size (mesh ξ); connected-cluster percolation of free-THF; shear/bulk modulus via stress-fluctuation and/or finite-strain (`gmx energy` pressure tensor `Pres-XX..ZZ`, `deform`/box-scaling); swelling ratio |

**Output layout (mirror the existing handoff so downstream agents/wet-lab integration find it):**
```
handoff_for_agent/
  transport/      ← A: D(T), σ(T), ionicity, replicate tables
  solvation/      ← B: free-anion / bridged-Mg–Cl / bound-THF populations + Raman map
  mechanics/      ← C (new): modulus(loading), mesh ξ, swelling, percolation
  reports/        ← per-story writeups + updated COMPARISON / SYNTHESIS_descriptors
```

**Validation gates.** D from a converged (linear) MSD window only; σ_coll reported with block-
average error and the ionicity ratio (never a bare magnitude); populations cross-checked against
the existing `solvation/*.txt`; moduli reported as loading-trends with the FF caveat stated.

---

## Priority & sequencing
1. **Story A** first — highest payoff, lowest risk, closes the flagged σ_coll / replicate /
   confound gaps and produces the trajectories Story B reuses.
2. **Story B** next — largely *analysis* on A's trajectories; cheap, high-confidence,
   directly validates the Raman assignments.
3. **Story C** last — most novel and most exploratory; needs new deformation/large-box runs
   and the most careful caveating.

Al-redox / SEI chemistry remains with the DFT/AIMD v2 campaign (`../computational_v2/`,
`../REPORT_polyAPC_v2_master.md`); this plan is the classical-MD complement on the
structure/transport/mechanics axis.
