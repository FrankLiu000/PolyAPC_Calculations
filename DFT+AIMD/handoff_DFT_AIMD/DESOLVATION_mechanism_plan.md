# Stepwise Mg²⁺ desolvation/deposition at the APC anode — mechanism & how the poly-APC network may ease it

## 0. The carrier and the problem
The mobile Mg carrier in APC (confirmed in your MD) is the chloro-bridged dimer **[Mg₂(μ-Cl)₃(THF)₆]⁺** with each Mg octahedral (3 μ-Cl + 3 THF). To plate one Mg⁰ the system must: **split the dimer, fully desolvate a Mg²⁺ (lose 3 THF + redistribute Cl), transfer 2 e⁻, and incorporate the adatom.** Mg²⁺ is small, hard, divalent ⇒ huge desolvation penalty (single Mg–O(THF) ≈ 21 kcal/mol from our DFT; 3 per Mg) → desolvation-coupled charge transfer is the rate-limiting, overpotential-setting step. This is *the* bottleneck of Mg anodes.

## 1. The elementary-step sequence (intermediates I, transition states ‡)

| step | process | intermediate / TS |
|---|---|---|
| S0 | migration of [Mg₂Cl₃(THF)₆]⁺ to the interface | (transport) |
| S1 | adsorption at the outer double layer | **I1**: [Mg₂Cl₃(THF)₆]⁺·(OHP) |
| S2 | partial desolvation (shed 1–2 outer THF entering the compact layer) | **‡1** THF dissociation; **I2**: [Mg₂Cl₃(THF)₄₋₅]⁺ |
| S3 | **dimer splitting** (μ-Cl₃ bridge redistributes) | **‡2** Cl-bridge cleavage; **I3**: [MgCl(THF)ₐ]⁺ + [MgCl₂(THF)_b] |
| S4 | monomer docks to Mg(0001) (Mg–surface bond forms) | **I4**: [MgClₓ(THF)_y]_ads |
| S5 | **charge transfer + final desolvation** (concerted): Mg²⁺ + 2e⁻ → Mg⁰, last THF/Cl leave | **‡3 — RATE-LIMITING** |
| S6 | Mg⁰ adatom diffusion → step/kink incorporation | **I5**: Mg adatom |

Released ligands: 6 THF + Cl⁻ (→ interphase or back to solution as AlCl₄⁻/Al-species).
The high barriers are **‡2 (dimer split)** and especially **‡3 (desolvation-coupled e⁻ transfer)** — where the *tightest* remaining THF/Cl must leave as the ion reduces.

## 2. How the poly-APC network could lower a step (hypotheses)
The unifying idea: **the network converts a high-barrier *dissociative* desolvation (Iᵈ) into a lower-barrier *associative-interchange* (Iₐ, "ligand-relay") desolvation, and pulls the equilibrium forward by capturing the leaving ligands.**

- **H1 — ligand relay / backside assist (lowers ‡1–‡3).** A framework ether-O attacks Mg *as* a THF leaves, so the TS has the incoming O partially bonded (associative interchange) instead of a bare under-coordinated Mg. **Direct evidence we already have:** the Mg–O↔Mg–O bridged "hop" is *barrierless* (<1 kcal/mol) when O sites are ≤5 Å apart (Section 3b), and THF↔network-O are near-degenerate (≈21 vs 22 kcal/mol). So a network-O within reach can take over a Mg–O bond at ~zero cost → it can relay desolvation.
- **H2 — leaving-group capture (lowers I2/I3 and late TSs).** Network ether/-OH H-bonds/coordinates the *released* THF and/or Cl⁻ (your MD shows ~33% of THF is network-associated), pulling desolvation forward (Le Chatelier) and stabilizing the desolvated intermediate.
- **H3 — confinement/pre-organization (lowers ΔG‡ entropically).** The rigid crosslinked network pins and pre-orients the cation near the interface, cutting the reorientational/translational entropy cost of the TS.
- **H4 — Cl⁻ shuttling (lowers ‡2).** Framework –OH stabilizes the bridging Cl as it's released, easing dimer splitting.
- **H5 — TS dielectric stabilization (lowers ‡3).** The polar ether environment stabilizes the partially-charged Mg^(2−δ)+ charge-transfer TS.

Net testable prediction: **lower ‡3 (and ‡2) for poly-APC ⇒ lower plating overpotential / faster kinetics**, *provided* the network is within coordinating reach at the interface (the bulk is segregated in the provisional MD — so the effect is expected to be **interfacial**, exactly where it matters).

## 3. Verification plan (layered: DFT cluster → AIMD interface → constant-potential)

### A. DFT cluster mechanism (static — the intrinsic energy landscape)
- **A1. Stepwise desolvation thermodynamics:** ΔG of [Mg₂Cl₃(THF)ₙ]⁺ → [Mg₂Cl₃(THF)ₙ₋₁]⁺ + THF, n = 6→3 (SMD-THF, ωB97X-D/def2-TZVP), **with vs without** a glyme/polyether fragment positioned to accept the vacated site → does the network lower each *intermediate*?
- **A2. TS search per step (QST3 / NEB + freq, IRC):** *dissociative* vs *network-assisted associative-interchange* TS (network-O bridging as THF leaves). Quantify **Δ‡ = ‡(dissoc) − ‡(assisted)** — the core barrier-lowering number.
- **A3. Dimer-splitting ‡2:** TS + ΔG for [Mg₂Cl₃(THF)ₓ]⁺ → monomers, ± network-O/–OH stabilizing the bridging Cl / under-coordinated monomer.
- **A4. Charge-transfer-coupled desolvation ‡3:** add 1–2 e⁻ to a Mg-monomer + small Mg-cluster ("electrode mimic"); locate the desolvation TS of the reducing ion, ± network; also Marcus reorganization energy λ ± network.

### B. AIMD interfacial free energy (dynamic, realistic — at Mg(0001))
- **B1. Desolvation free-energy profile:** metadynamics/umbrella with **CV = Mg first-shell coordination** (Σ THF-O + Cl), **APC vs poly-APC** → desolvation barrier ± network.
- **B2. 2-D FES:** CVs = (Mg→surface distance, Mg coordination) → the full plating-desolvation landscape; locate the TS ridge and the network's effect on it.
- **B3. Field / constant-potential AIMD:** drive the charged cation to the anode under the interfacial field (the saw-tooth field-AIMD now running is the first build; constant-potential GCDFT is the rigorous endpoint) → desolvation-coupled charge transfer in a real field.
- **B4. Transition-path sampling / committor analysis:** identify the true TS ensemble; decompose *which* network interaction (relay O, captured THF, Cl shuttle) stabilizes ‡3.

### C. Descriptors to report
Per-step ΔG and ΔG‡ (± network); **Δ(ΔG‡) of the rate-limiting ‡3**; network-O coordination number *at the TS*; leaving-THF/Cl capture; Marcus λ; and the predicted overpotential shift.

## 4. What we can do *now* vs what needs scale
- **Now (DFT cluster, robust, SLURM):** A1–A3 are directly doable with the molecular machinery already built (just add a glyme/polyether spectator and do constrained-opt/NEB). This alone tests H1/H2/H4 quantitatively.
- **Mid (AIMD):** B1/B2 metadynamics on the thin-film interface (feasible; CV = coordination number — well-posed, unlike the earlier ill-posed attempt because here the cation *is* O-solvated).
- **Big (constant-potential AIMD, B3/B4):** the rigorous electrochemical endpoint — larger cell + GCDFT; a dedicated effort.

**Cheapest highest-value first experiment:** A2 — the dissociative-vs-network-assisted desolvation TS on the real [Mg₂Cl₃(THF)₅]⁺ ± a polyether-O. If Δ‡ is large and negative, that is the molecular smoking gun that the network eases desolvation.
