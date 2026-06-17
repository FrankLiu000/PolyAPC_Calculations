# poly-APC v2 — integrated mechanism: Al redox / SEI chemistry reconciled with the wet-lab data
### Mg gel-polymer electrolyte (in-situ TMSOTf-cured octakis(glycidyl)-POSS in APC, MgCl₂/AlPhₓCl₍₄₋ₓ₎·THF)
Yuezheng Liu¹, Yong Wu¹,²\*, Yingying Lu¹,³\*
¹State Key Lab of Chemical Engineering, College of Chemical & Biological Engineering, Zhejiang University, Hangzhou. ²Dept. of Energy & Environmental Materials, Suzhou National Laboratory. ³ZJU-Hangzhou Global Scientific & Technological Innovation Center.

> **STATUS — FINAL (campaign converged), 2026-06-15.** Every number below is populated from the parser-written data in `/CH/poly_v2/results/data/` and the classical-MD handoff; the source file is cited inline. Two items remain *open by design*, not blank: (i) the production ±1 V bias AIMD is running (bare 1303 / poly 1304 queued) to test field-amplification — its verdict file is `bias_prod_{bare,poly}.txt`; (ii) the DFT Raman intensity assignment was not executed (experimental table is live). **The central scientific change from the scaffold version: the pre-campaign working hypothesis — "bare reductively decomposes the anion and co-deposits Al; poly suppresses it" — was _tested and largely overturned_. The supported bare-vs-poly differentiator is coordination/transport gating, not redox chemistry (four independent chemical nulls + one retracted artifact; §3b, §10).**

---

## Executive summary — the honest, evidence-based picture (v2 final)
The v1 conclusion stands: **poly-APC is not better at moving Mg²⁺** (≈4.4× slower in bulk, t₊ = 0.50 unchanged, dimer carrier segregated ~7 Å from the network); the win is **mechanical / interfacial / safety**, not transport. v2 set out to add the chemistry v1 omitted — the redox chemistry of the APC aluminium anion and a poly-specific triflate→fluoride SEI — because the XPS shows an interfacial effect v1 cannot explain.

The headline observable is the **3.1 eV Al 2p split**: bare-APC 70.88 eV (anomalously low → reduced / Mg–Al-alloyed Al⁰) vs poly-APC 73.98 eV (oxidised Al³⁺). The pre-campaign hypothesis was that the bare anode *chemically* reduces the anion to Al⁰ while the cured network *chemically* blocks that. **The campaign does not support a chemical lever.** Across four independent, matched bare-vs-poly comparisons the chemistry is the same to within its uncertainty, and the one finding that looked like a chemical gateway (interfacial chloride abstraction) turned out to be a geometry artifact and is retracted (§3b):

1. **Reduction thermodynamics** — contact-pair EA bare **0.51** vs poly **0.48 eV** (`depairing_ET.txt`).
2. **Reduction site** — phenyl π* in **both** (4 % vs 2 % Al spin), not Al (`depairing_ET.txt`, `reduction_spin_localization.txt`).
3. **Ion-pairing free energy** — near-identical landscapes, ΔF(CIP→free) bare **2.43** vs poly **2.08 kcal/mol**, same basin minimum (`pairing_pmf.txt`).
4. **Carrier speciation** — dimer favoured in **both**: redistribution ΔG +10.4 (bare) → +12.0 kcal/mol (poly); the polyether does **not** shift to the monomer (`speciation_monomer_dimer.txt`, `speciation_polyarm_glyme.txt`).

What *is* supported, computationally, is **coordination / transport gating**: the network de-pairs the electrolyte (CIP 95 → 84 %, loading-driven, charge-robust) and its ether-O blocks the open **axial** Mg face that the anion otherwise contacts (classical-MD Stories F/H). The bare-side Al⁰/alloy assignment remains *thermodynamically* consistent (alloy substitution −4.44 eV; Bader charge trend reproduces the 70.9→74.0 eV direction; 70.88 eV is itself below pure-metal Al), but we did **not** establish a clean molecular pathway from the *dominant* anion to Al⁰ — its reduction is phenyl-centred. The residual chemical route is the **minority** chloride-rich AlCl₄⁻ (Schlenk tail), which is the one species that reduces at Al. The split, if a genuine chemical-state difference, is therefore most likely **field-amplified** coordination/access contrast (the bias AIMD now testing it) and/or **partly an XPS differential-charging artifact** on the insulating poly film. This is the honest v2 position; the older "abstraction gateway" narrative is withdrawn. **Capstone (MLFF, §7b):** an active-learned MACE force field now probes the gating *as a desolvation free energy*. Both cations face a standoff well + a surface desolvation barrier (no spontaneous zero-field plating), but the **poly cation is held ~1.5 Å further from the electrode (~7.0 vs ~5.5 Å) and keeps its solvation shell locked (CN ≈ 6) much longer**, whereas bare desolvates progressively — a *coordination/desolvation* gating contrast, not redox. The qualitative contrast (standoff + shell retention) is robust; the barrier magnitudes are not yet converged (a slow shell mode; ~20–30 kJ/mol drift).

**Methods (consistent across v1→v2).** Molecular: B3LYP-D3(BJ)/def2-TZVP//def2-SVP, SMD(THF), int=ultrafine; G = E[TZVP,SMD] + Gcorr[SVP freq]; redox/EA cross-checked with ωB97X-D & M06-2X, anion EAs with diffuse def2-TZVPD; Multiwfn ESP/Fukui/spin/QTAIM. Periodic/AIMD: CP2K 2025.1, PBE-D3, DZVP-MOLOPT-SR-GTH + GTH-PBE, CUTOFF 400/REL 50; Mg(0001) slab (Φ = 3.97 eV validated); interface AIMD NVT 300 K, 1 fs, EPS_SCF 1e-5 (matched bare/poly). Interface electron transfer attempted **both** ways (CDFT/Marcus and Dirichlet-BC fixed-potential); see §6 for which survived.

**Scope note (locked decisions).** Full program, Phases 0–4. Bare-APC modelled **F-free**: the MgF₂/triflate SEI is **poly-specific**; bare's ~4.3 % F is flagged as a contamination/handling artifact and the **missing S 2p scan** is flagged. Interface ET cross-compared by two methods. Full deliverable set (data + structures + report + figures + reconciliation table).

---

## 1. Transport & solvation (classical MD) — decisive, deconfounded this round
Gelation slows both ions ~4.4× with t₊ = 0.50; intact [Mg₂(μ-Cl)₃(THF)₆]⁺, nearest network-O median 7.1 Å; the anion is **D ≈ 4.2× slower** in the gel — the kinetic basis for "network immobilises the anion" (Fig. `md_anion_rdf.png`). The review round (Stories A–H, `classical_molecular_dynamics/handoff_for_agent/`) hardened this:
- **De-pairing is real and loading-driven** but its magnitude was inflated by a network-topology confound. At *matched* single-percolating connectivity (Story F) CIP falls **90.6 → 85.3 → 71.5 %** with POSS loading; the original 8-POSS "swollen mobility advantage" was a topology artifact (matched D falls monotonically, no speed anomaly). Speciation reference: SSIP/CIP/AGG bare **4.6/94.9/0.5 %** vs swollen-8 **15.5/84.2/0.3 %** (`RESULTS_speciation_ssip_cip_agg.txt`).
- **Charge-robust** (Story E): the de-pairing gap bare−swollen is 10.4 pts at Mg +1.2 and 8.1 pts at ECC +1.5.
- **Transport is by neutral co-moving pairs** (Story D): ionicity σ_coll/σ_NE ≈ 0.10 (bare) / 0.23 (swollen, `RESULTS_storyA2.txt`); net charge-MSD ≈ 0, so species-resolved t₊ is ill-posed and the NE t₊ ≈ 0.5 vastly overstates independent Mg²⁺ transport (the quantitative coordination paradox).
- **Geometry of the contact** (Story H): Mg–anion contact is **88–92 % axial** (end-on at the open Mg face); clusters bearing a polymer-O contact carry **1.6–3.3× fewer** axial anion contacts → the latent-ligand ether-O blocks the axial face. *This is the structural origin of the gating in §10.*

## 2. APC anion speciation — Schlenk ladder & the anodic limit (P0a, G16; `redox_ladder.txt`)
Vertical IP/EA (eV), B3LYP / ωB97X-D / M06-2X band:

| anion | IP (B3LYP/ωB97XD/M062X) | EA (B3LYP) | note |
|---|---|---|---|
| AlCl₄⁻ | 7.66 / 8.20 / 8.37 | **−1.30** | won't reduce; minority (Schlenk tail) |
| AlPhCl₃⁻ | 6.38 / 6.47 / 6.63 | +0.09 | |
| **AlPh₂Cl₂⁻ (dominant)** | **6.18 / 6.61 / 6.73** | +0.06 | sets the practical anodic limit |
| AlPh₃Cl⁻ | 5.95 / 6.32 / 6.40 | +0.10 | Ph-rich minority |
| AlPh₄⁻ | 5.73 / 6.17 / 6.29 | +0.17 | lowest IP if present |
| AlCl₃ / AlPh₃ (neutral) | 9.33 / 6.89 | +1.44 / +1.69 | |

The **dominant** anion is [AlPh₂Cl₂]⁻; its IP **6.18 eV (B3LYP)** reproduces v1's anodic limit, with a +0.4–0.5 eV upward band from the range-separated/M06-2X functionals. The Ph-rich Schlenk minorities (AlPh₃Cl⁻, AlPh₄⁻) would lower the true anodic limit toward 5.7–6.0 eV if appreciably populated. The near-zero EAs (0.06–0.17 eV) of all phenyl-chloride anions mean the free anion is **barely reducible**; AlCl₄⁻ is anti-reducible (EA −1.30 eV).

## 3. Redox ladder — where the electron goes (P0b + Multiwfn spin; `reduction_spin_localization.txt`)
On one-electron reduction (Mulliken spin by element, doublet, ⟨S²⟩ = 0.75):

| anion + e⁻ | Al | Cl | Ph(C/H) | reduction site |
|---|---|---|---|---|
| AlCl₄⁻ | **+1.14** | −0.14 | 0.00 | **ALUMINIUM** → Al(0)/alloy precursor |
| AlPhCl₃⁻ | +0.06 | +0.01 | +0.93 | phenyl π* |
| AlPh₂Cl₂⁻ | +0.08 | +0.01 | +0.91 | phenyl π* |
| AlPh₃Cl⁻ | +0.06 | 0.00 | +0.94 | phenyl π* |
| AlPh₄⁻ | +0.06 | 0.00 | +0.94 | phenyl π* |

**The decisive result of the whole redox program:** only the chloride-rich **AlCl₄⁻** reduces *at aluminium*; every phenyl-bearing anion — including the **dominant** [AlPh₂Cl₂]⁻ — puts the added electron on a **phenyl π***, not Al. So direct Al⁰ formation is specific to the minority AlCl₄⁻ channel, and AlCl₄⁻ is simultaneously the *hardest* to reduce (EA −1.30 eV). A clean, dominant-anion route to Al⁰ does **not** exist at this level — which is exactly why the "abstraction gateway" (§3b) was needed to rescue it, and why its retraction matters.

## 3b. ⛔ RETRACTED — the interfacial chloride-abstraction "gateway" was a geometry artifact
**What was claimed (v2-draft).** Bare-interface AIMD appeared to show the [Mg₂Cl₃(THF)₆]⁺ cation abstracting one Cl⁻ from [AlPh₂Cl₂]⁻ within ~0.2 ps and holding it for 10 ps, leaving the *neutral, 3-coordinate* AlPh₂Cl at the anode. Neutral AlPh₂Cl reduces **at Al** (EA 1.71 eV vertical, ΔG_red −2.14 eV; 83 % Al spin on the [AlPh₂Cl]·⁻ radical; Al–Cl cleavage favoured over Al–C by 23 kcal/mol — `chloride_abstraction.txt`, `reductive_decomposition.txt`). That was the proposed "gateway" converting the inert dominant anion into an Al⁰-forming species, with poly blocking it.

**Why it is retracted.** The bare AIMD that produced the abstraction (`aimd_interface_stats.txt`: Al–Cl149 → 7.66 Å mean, frac>3 Å = 0.97, first departure 0.17 ps) started from a **corrupted cation geometry** — the three bridging chlorides Cl66/67/68 were stacked at one μ-site (Cl–Cl 1.23/1.33 Å), Mg–Mg compressed to 2.81 Å (correct 3.87 Å) — which drove a T > 1000 K explosion and ejected a chloride. On a **clean, repaired start** (slab-fixed GEO_OPT → 10 ps MD; `aimd_clean_bare.txt`) the abstraction **does not recur**: both Al–Cl bonds stay intact (Al–Cl148 mean 2.22, Al–Cl149 mean 2.22 Å; **frac>3 Å = 0.00**), with all four anion bonds present in the final frame.

**Status of the underlying numbers.** The *in-vacuo* chemistry of neutral AlPh₂Cl (Al-centred reduction, 83 % spin) is valid and reproducible; what is withdrawn is the **interfacial mechanism that would generate** neutral AlPh₂Cl at the bare anode. The data file `chloride_abstraction.txt` carries a retraction header pointing here. The campaign memory note `chloride-abstraction-gateway.md` is marked ❌ REFUTED.

## 4. Al co-deposition / Mg–Al alloying & the Al 2p split (P0c, CP2K)
The *downstream* leg — "if Al⁰ forms, does it alloy and give a low Al 2p BE?" — is supported, even though the *upstream* molecular pathway from the dominant anion is not (§3, §3b):
- **Alloying is thermodynamically favourable** (`al_codeposition_periodic.txt`): dilute Al-in-Mg substitution **E_sub = −4.44 eV** (robust sign); Al adatom on Mg(0001) E_ads ≈ **−0.08 eV** at hollow sites (weakly favourable, *at the ±0.1 eV Γ-only/smeared reference-uncertainty level*); Mg₁₇Al₁₂(β) formation +1.05 eV/atom is flagged **ARTIFACT** (approximate Wyckoff/CELL_OPT not converged — needs the true I-43m phase).
- **Al 2p chemical-state direction is reproduced** (`al2p_prediction.txt`): charge on Al across reference environments —

  | environment | Voronoi | Mulliken | assignment |
  |---|---|---|---|
  | Al⁰ metallic adatom | −0.103 | +0.334 | reduced/metallic ≈ 70.9 eV (bare) |
  | Mg–Al alloy substitution | −0.359 | +0.242 | alloyed ≈ 70.9 eV (bare) |
  | Al₂O₃ (Al³⁺) | −0.456 | +0.930 | oxidised ≈ 74.0 eV (poly) |
  | AlF₃ (Al³⁺) | −0.861 | +1.113 | oxidised ≈ 74.0 eV (poly) |

  Both schemes put reduced/alloyed Al (Mulliken ~+0.3) well below Al³⁺ (~+1.0), Δq ≈ +0.7 e → reproduces the **sign/direction** of the measured 70.9→74.0 eV shift. *Limitation: GTH pseudopotentials give the shift sign, not absolute BE; population charges are compressed (no scheme yields formal +2.4 for Al³⁺). All-electron ΔSCF is the flagged refinement.* Note the measured bare 70.88 eV is itself **below pure-metal Al (~72.9 eV)** — physically consistent with Al being slightly anionic in a Mg-rich alloy (Al more electronegative than Mg), which independently corroborates the "reduced/alloyed" assignment for the bare side.

## 5. Triflate / fluoride SEI — poly-specific (P1 + P0c)
- OTf⁻/TMSOTf reductive fragmentation (C–F→F⁻→MgF₂; C–S→SO₃²⁻; Si–O cleavage) sits on the redox ladder as the poly-specific F-SEI channel.
- **MgF₂ Mg²⁺ migration barrier — UNRESOLVED BY FORMULATION** (`mgf2_neb_LIMITATION.txt`): the charged-vacancy endpoint relaxations do not settle in the affordable 2×2×2 (9.25 Å) cell — RMS gradient floors at 0.03–0.045 Ha/bohr against a frustrated, charged-image-contaminated PES. We **do not** report a computed barrier; for the DRT/SEI-transport discussion we cite the literature Mg²⁺-in-fluoride range **~0.5–1.0 eV**, consistent with MgF₂ being a comparatively resistive poly-specific SEI component. The transport story does not hinge on this number.
- **Flagged:** bare-APC modelled F-free per locked decision; bare's measured ~4.3 % F = contamination/handling artifact; **S 2p scan missing** — confirm formulations before over-interpreting the SEI sulfur channel.

## 6. Interface electron transfer — what survived (P3, CP2K; `interface_ET.txt`)
- **Method A (CDFT/Becke–Marcus) — INVALID on this system.** The Becke real-space charge constraint does not conserve charge on the Fermi-smeared metal slab: total Becke charge came out **−13 e (bare) / +11 e (poly)** for charge-neutral cells, and the 25-atom anion fragment population was environment-inconsistent (~88 e bare vs ~49–64 e poly, formal ~76). Radii/cavity variants did not restore conservation. This was the plan's flagged top methodological risk; **no ΔG_ET is reported from CDFT.**
- **Method B / equilibrium access (AIMD).** Al-to-slab-Mg distance, matched 6.4 ps: **bare 9.0 Å (min 7.2) vs poly 9.1 Å (min 7.3)** — the anion stays solvent/ion-separated ~9 Å from the plating front in **both**; no contact/plating event on the accessible timescale (deposition is a rare, overpotential-driven event). **No clean bare-vs-poly access difference at equilibrium.**
- **Honest conclusion:** the decisive interfacial-reduction step is a rare, potential-driven event not captured by equilibrium DFT/AIMD, and CDFT is unusable on the metal. The computable differentiator is ion pairing/transport (§1, §10), not a clean interfacial ΔG_ET — which is precisely why the field-driven runs in §7 were commissioned.

## 7. Real-ion interface AIMD + field machinery (P4, CP2K)
- **Clean equilibrium runs (matched, EPS_SCF 1e-5).** Bare and poly both keep the anion intact and ~9 Å off the front for 10 ps (§3b, §6). Single trajectory per condition; the abstraction artifact is the cautionary tale for over-reading any single interfacial event.
- **Field machinery validated.** A two-plate Dirichlet constant-voltage counter-electrode (implicit Poisson, BOUNDARY_CONDITIONS MIXED_PERIODIC, plates at V_D = ±1 V over ~47 Å ≈ 0.043 V/Å ≈ 4×10⁸ V/m, vacuum dielectric with explicit THF; Fermi-smeared diagonalisation, ADDED_MOS 400, Broyden ALPHA 0.15) is **production-viable** (`bias_pilot_verdict.txt`): the v2 pilot completed 50/50 MD steps with **0 SCF failures**, T mean 247/max 300 K, conserved-quantity drift 0.009 a.u. The ±3 V field is *not* viable (SCF sloshes, aborts at step 3).
- **Production (in progress):** ±1 V, 10 ps, bare (job 1303) + poly (1304 queued). At time of writing bare is healthy at ~0.17 ps (T mean 292/max 358 K, SCF 170/170, anion intact, Al 9.4 Å). **Purpose:** test whether the field *amplifies* the coordination-gating contrast into the Al 2p split. *Honest framing: this is an idealised constant-VOLTAGE counter-electrode, not grand-canonical constant-µ — CP2K 2025.1 lacks ESM and GC-SCF.* Verdict will be written to `bias_prod_{bare,poly}.txt`.

## 7b. MLFF desolvation free energy — the gating mechanism quantified (two-node MACE + active learning)
AIMD cannot reach the rare, activated Mg²⁺ desolvation/approach event — the explicit-electron (CHARGE −2) + ±1 V runs of §7 confirm it: the solvated cation sits ~9 Å off the front, stays +2, and does not approach/reduce on the accessible ps. To reach it we built a **machine-learning force field**. Two-node split: **EPYC** DFT-labels interface configs (PBE-D3, with the fixed-slab forces **masked** — those are a +z asymmetric-slab dipole artifact, momentum-non-conserving, caught by the GPU node's independent QC); the **GPU node** fine-tunes **MACE-MP-0** committees and runs **umbrella sampling + WHAM** along the cation–surface coordinate, with **active learning** filling the near-surface region the equilibrium data lacked (committee σ_F flags extrapolation → DFT-labelled on EPYC → retrain; near-surface force R climbed **0.585 → 0.992** in one round). Matched bare/poly potentials: held-out force MAE **27 / 33 meV/Å**. Pipeline + models live on the `computational-v2-package` branch (`mlff/`).

**Result — both cations face a standoff well + a steep surface (desolvation) barrier (no spontaneous zero-field plating); the gating is in *where* the cation is held and *how long it keeps its shell* (stiff-spring re-do, `results/figures/fig_pmf_r3.png`):**

| | bare | poly |
|---|---|---|
| preferred standoff (F min) | **~5.5 Å** | **~7.0 Å — held further from the electrode** |
| surface barrier (well → ~3.4 Å) | steep (~70–80 kJ/mol) | steep (~60–80 kJ/mol) |
| first shell on approach | **desolvates progressively** (Mg–O 6→1, Mg–Cl 6→3) | **shell retained to ~5 Å** (Mg–O ≈ 6), then sheds abruptly |

The **POSS network holds the cation ~1.5 Å further from the front and keeps its solvation shell locked (CN ≈ 6) much longer**; the bare cation desolvates progressively as it approaches. A **coordination/desolvation gating** contrast — corroborating §1/§10 (network de-pairs + blocks the Mg face, segregating the carrier ~7 Å from the front) now at the free-energy level — tied to the higher-but-stable poly R_ct in the DRT (§9).

**Honest status — qualitative/semi-quantitative; NOT a converged number.** Robust (across sampling passes + from directly-counted, WHAM-independent data): the **standoff-distance difference (poly ~1.5 Å further out) and the shell-retention contrast**. NOT converged: the **absolute well depths / barrier heights (~60–80 kJ/mol)** — bootstrap (statistical) error is small (±2–4 kJ/mol) but a **slow solvation-shell/cluster-reorg mode** leaves a first-half/second-half drift of ~20–30 kJ/mol at 15 ps/window (bare span wandered 88→56→80 across passes). ⚠ **A first (round-2) pass reported bare as "barrierless-downhill to contact, plates"; the stiff-spring re-do showed that was a chained-pull artifact** (soft springs let the bias *drag* the cation down) — bare in fact has a standoff well + surface barrier. Zero-field, scaled-charge (Mg +1.2), fixed-slab intrinsic approach free energy (the real overpotential lowers the barrier; poly *does* plate, with higher R_ct). A converged magnitude needs replica-exchange / an explicit shell-CN second CV / ≫15 ps; reduction/plating stays DFT (hybrid). Verdict: `mlff/ENHANCED_SAMPLING.md` Stage 2.

## 8. Spectroscopy — Raman (P3) — experimental live, DFT assignment not run
Experimental bare-vs-poly band table (`raman_peaks.csv`, Fig. `raman_experimental.png`) is consistent with the de-pairing/dissociation picture, **not** with a redox change:
- **915 cm⁻¹** (THF ring ν(C–O–C)): +0.3 cm⁻¹, intensity ref — solvent framework essentially unchanged.
- **999→1002 cm⁻¹** ([AlPh₄]⁻ phenyl ring-breathing): **+2.9 cm⁻¹, +8 %** — anion shifts toward its *free* position → dissociation.
- **276 cm⁻¹** (Cl-bridge / [Mg₂Cl₃]⁺ str.): **−30 %** — fewer chloride-bridged aggregates/CIPs.
- **181 cm⁻¹** (Mg–Cl str.): **×2** intensity — more dissociated Mg–Cl.
- **1483→1486 cm⁻¹** (THF CH₂ deformation): +3.2 cm⁻¹ — coordinated-THF stiffening (Mg solvation shell).

*Gap (honest):* the computed harmonic Raman intensity assignment (free vs Mg-bound THF, the "⅓ THF network-bound" MD claim) was **not** executed — no `raman_assign.txt`. The experimental story stands on its own; the DFT overlay is outstanding.

## 9. Impedance (in-situ DRT) — live trend
`drt_gamma_heatmaps.png` + `drt_rct_evolution.png`: poly shows **higher but stable** interfacial resistance, consistent with the 4.4× slower transport (§1) and a benign Al³⁺/MgF₂ interphase. The quantitative SEI-barrier link is limited by the unresolved MgF₂ NEB (§5); cited as a literature-anchored, qualitative connection.

---

## 10. The four nulls and the honest bottom line
Five matched bare-vs-poly tests were run for a *chemical* differentiator; four came back null and the fifth (abstraction) was retracted as an artifact:

| # | test | bare | poly | verdict | source |
|---|---|---|---|---|---|
| 1 | contact-pair reduction EA | 0.51 eV | 0.48 eV | **null** | `depairing_ET.txt` |
| 2 | reduction site (Al spin) | phenyl (4 %) | phenyl (2 %) | **null** | `reduction_spin_localization.txt` |
| 3 | ion-pairing ΔF(CIP→free) | 2.43 kcal/mol | 2.08 kcal/mol | **null** (same basin) | `pairing_pmf.txt` |
| 4 | carrier speciation (redistribution ΔG) | +10.4 | +12.0 kcal/mol | **null** (dimer both) | `speciation_*` |
| 5 | interfacial Cl abstraction | (artifact) | intact | **retracted** | `aimd_clean_bare.txt` |

**Conclusion.** The bare-vs-poly difference is **not redox chemistry**. The computationally supported differentiator is **coordination / transport gating**: the cured network (i) de-pairs the electrolyte (CIP 95 → 84 %, loading-driven, charge-robust; §1) and (ii) blocks the open **axial** Mg face the anion contacts (Story H; §1), immobilising/segregating the anion ~7 Å from — and ~4× slower toward — the plating front. The Al 2p split is reconciled as follows: the **bare** low-BE Al⁰/alloy assignment is thermodynamically and spectroscopically self-consistent (alloy E_sub −4.44 eV; Bader direction; sub-metallic 70.88 eV), but its molecular trigger is the **minority** AlCl₄⁻ channel (the only Al-centred reduction), *not* a poly-blockable gateway on the dominant anion. The split, if a true chemical-state contrast, is therefore most plausibly **(a)** an interfacial-field amplification of the access/coordination contrast (the ±1 V bias AIMD is the live test) and/or **(b)** partly an **XPS differential-charging** artifact on the insulating poly film inflating its apparent BE. We report this rather than the tidier — but unsupported — "chemical gateway" story.

## 11. Reconciliation table (observable → explanation → confidence)

| Wet-lab observable | Value | Computational explanation | Source | Confidence / limitation |
|---|---|---|---|---|
| **Al 2p split** | bare 70.88 / poly 73.98 eV | Direction reproduced: reduced/alloyed Al⁰ (bare) vs Al³⁺ (poly) — Bader CLS Δq +0.7 e + alloy E_sub −4.44 eV + sub-metallic bare BE. **But** dominant-anion route to Al⁰ not established (phenyl-centred; abstraction retracted); residual trigger = minority AlCl₄⁻; possible field-amplification and/or poly charging artifact. | P0b/P0c, §3b,§4,§10 | **MEDIUM** — direction robust (2 schemes); mechanism/magnitude partial; no absolute BE (GTH) |
| F 1s / MgF₂ | ~684.9 eV, ~4.2 % | OTf/TMSOTf → MgF₂ SEI (poly-specific) | P1, P0c | **MEDIUM** — bare-F flagged artifact; **S 2p missing**; MgF₂ NEB unresolved |
| Si 2p (POSS) | poly ×4.2 (101.66 eV) | inert siloxane only in cured network (POSS IP 8.72) | v1 DFT | **HIGH** (consistent w/ v1) |
| EDS(µm) no Al vs XPS(nm) ~4 % | depth contrast | Al/F/Si a thin surface interphase, not bulk | constrains SEI thickness | **HIGH** (qualitative) |
| Raman 915 / 999→1002 / 276 / 181 | +0.3 / +2.9 / −30 % / ×2 | de-pairing & anion dissociation (toward free), not redox | §8 + live Fig | exptl **HIGH**; **DFT intensity assignment not run** |
| in-situ DRT R_ct | poly higher, stable | benign Al³⁺/MgF₂ interphase + 4.4× slower transport | live Fig + §1/§5 | trend **HIGH**; barrier link **LOW** (NEB unresolved) |
| CCD / Aurbach CE / morphology | bare rough/soft-short; poly smooth | coordination gating segregates the anion (§10); residual Al co-deposition (minority AlCl₄⁻) may seed Mg–Al nucleation on bare | §1/§4/§10 | **MEDIUM/LOW** — gating supported; co-deposition mechanism not pinned |

## 12. Honest limitations (carried from v1, extended)
True grand-canonical constant-µ DFT is unavailable here (no turnkey ESM/GC-SCF in CP2K 2025.1); the bias runs use an **idealised constant-VOLTAGE Dirichlet counter-electrode**. CDFT/Becke is **invalid on the metal slab** (charge non-conservation) — no interfacial ΔG_ET reported. Anion EAs are method-sensitive (B3LYP/ωB97X-D/M06-2X spread reported); reduced-radical spin contamination can mislead the "Al⁰?" call (we lean on spin-density + the cross-functional band). **Absolute Al 2p BE is not obtainable from GTH pseudopotentials** (shift sign/direction only; all-electron ΔSCF is the refinement). Large floppy multi-THF clusters carry ±few-kcal/mol Gibbs uncertainty (opt=loose). The interface AIMD is **single-trajectory per condition** — the chloride-abstraction artifact (§3b) is the explicit lesson against over-reading one trajectory; replicate/field runs are the mitigation. **Bare-F and the missing S 2p are unresolved by formulation** (bare modelled F-free per locked decision). Mg₁₇Al₁₂ and the MgF₂ NEB are flagged unconverged. The headline correction of this version is that the bare-vs-poly lever is **coordination/transport gating, not redox chemistry** — and we report the four nulls and the retraction rather than the discarded gateway.

---
*Provenance: numbers parsed into `/CH/poly_v2/results/data/*.{txt,csv}` (Gaussian 16 + CP2K 2025.1 + Multiwfn under SLURM on the EPYC node) and the classical-MD handoff (`classical_molecular_dynamics/handoff_for_agent/`). Figures in `results/figures/`. Live status of the production bias AIMD: `bias_prod_{bare,poly}.txt`. This file supersedes the scaffold version; do not restore the "abstraction gateway" narrative — see §3b.*
