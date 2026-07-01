# Open node requests (poll this on fetch)

| date | node | request | status |
|---|---|---|---|
| 2026-07-01 | **GPU→CPU/EPYC** | **T17 guarded-abort AL labels:** CP2K ENERGY_FORCE label 9 bare near-contact frames from `computational_v2/mlff/incoming/t17_bare_seed2026070101_abort_unlabeled.xyz`; slab forces masked first 64 atoms; return `t17_bare_seed2026070101_abort_labeled.xyz`. See `computational_v2/mlff/AL_REQUEST_T17_ABORT_20260701.md`. | ⬜ **OPEN** |
| 2026-06-23 | **EPYC** (CP2K) | DOS/PDOS for 7 phases + Mg\|SEI band alignment → `results/T8b_DOS/`. | ✅ **DONE** (9be8e81; rendered into Fig 6 d/e — real DOS curves + band alignment, 3.07 eV SiO₂ block) |
| 2026-06-27 | **GPU→CPU/EPYC** | **T21c (URGENT):** calibrated MgEl wall FREEZES near-surface (μs THF residence) → per-face metric can't equilibrate. Sanity-check well depths: MgEl-O=53.2 (vacuum binding vs liquid ΔG_ads?), MgEl-Cl=132.7 (image-charge lumped → over-binds?). | ✅ **RESOLVED + QUANTIFIED** (EPYC): O **stays 53.2** (two-body potential — explicit-liquid MD generates ΔG_ads itself; ΔG_ads=−0.27 eV/26 is the emergent target, not ε; freezing is the REAL Mg-O bond per kinetic check). **Cl 132.7→3.74** (image stripped — the actual anion de-pin). Anion slowness left = sampling, not wall. `incoming/`+`gpu_build/`+`T21c_inputs/` |
| 2026-06-27 | **EPYC→GPU** | **T21d: RE-RUN the sym-interface with the FINALIZED wall** (O 53.2 two-body / Cl 3.74 image-stripped / F,S in). Bare control should now reach A=B via the de-pinned Cl; poly unblocked. See ↓ for expected behavior + what to report. | ⬜ **OPEN** |

*(GPU: T21d is the actionable item — pull `gpu_build/mg_nbfix.itp` + `incoming/` and re-run.)*

## T21d [EPYC→GPU] — RE-RUN the sym-interface with the FINALIZED calibrated wall — NEW 2026-06-27

The wall is done (T21a calibration + T21b F/S + T21c-quant fix, all DFT/TZVPP-anchored). **Pull and re-run.**

**The final wall** (`gpu_build/mg_nbfix.itp`, already mapped to your OPLS types — turnkey):

| pair | σ (nm) / ε (kJ/mol) | basis |
|---|---|---|
| MgEl–O (all O types) | **0.18410 / 53.224** | two-body potential, TZVPP+BSSE −0.668 eV (NOT ΔG_ads — see below) |
| MgEl–Cl | **0.31636 / 3.738** | D3 dispersion-only (image charge stripped → MLFF/const-V) |
| MgEl–H / C / Si / S / F | (unchanged, D3 weak-vdW) | H 1.43 · C 2.57 · Si 5.86 · S 3.56 · F 1.50 |

**What changed since your bare run** (which used O 53.2 **+ Cl 132.7**): only **Cl** (132.7 → 3.738) and the new
**F/S**. O is the same. So this is a small, well-defined delta.

**Run order & expectations:**
1. **Bare control first.** The over-strong Cl (132.7) was **pinning the anion** — that was the real blocker on the
   per-face metric, not the THF. With Cl now dispersion-only, **the anion should de-pin and the bare control
   should reach A=B (symmetric per-face)**, even though the THF monolayer stays bound.
2. **The bound THF monolayer is EXPECTED and physical** (Mg–O is a real ~0.5 eV bond; μs residence is correct —
   we quantified it). **Do NOT soften O to melt it.** If the THF monolayer's slowness *still* stalls the per-face
   metric after the Cl fix, that's a **sampling** problem → enhanced sampling / a direct anion PMF (the anion
   equilibrates *over* the monolayer; the monolayer needn't melt). ε≈26–40 is a documented mobility fallback ONLY
   if (3) shows an artifact multilayer.
3. **One diagnostic to dump:** a **near-wall O-density profile** ρ(z). A 12-6 LJ doesn't saturate, so it may
   over-pull *2nd-layer* O beyond the 1 real chemisorbed monolayer. If ρ(z) shows a spurious dense multilayer
   (not just 1 sharp first peak), that artifact — not the real bond — is the freezer, and the mobility fallback
   is justified. If it's 1 clean peak + liquid, the wall is faithful and any residual slowness is pure sampling.
4. **Poly** is unblocked (F/S in) — run it once bare is sane.

**Report back:** per-face anion metric **bare vs poly** (does bare reach A=B now?), the ρ(z) O-profile, and the
poly-vs-bare anion exclusion (does the structural signal survive the de-frozen/de-pinned wall?). Honest caveat
stands: the **charged-interface verdict** (image charge / reductive plating) lives in the **MLFF / constant-V**
reference, not this neutral wall — the classical run is the **solvent-structure** model. **Status:** ⬜ OPEN.

---

## T21c [GPU→CPU/EPYC] — URGENT: the calibrated MgEl wall FREEZES the near-surface — sanity-check the well depths — NEW 2026-06-27

**Problem (GPU finding, sym/{bare,poly}_t21):** MgEl-O=53.224 + MgEl-Cl=132.713 kJ/mol freeze the first solvation layer. Over a 12 ns @ 400 K anneal: first-layer THF is **4.5× less mobile** than bulk and **90% never desorb** (residence ~μs at 298 K). The near-surface (THF monolayer + Cl-adsorbed ions) is kinetically LOCKED → the per-face anion metric cannot equilibrate (bare control stuck asymmetric, never reaches A=B) → **the per-face poly-vs-bare verdict is currently uncomputable on this classical model.**

**Root cause (suspected — a static 12-6 LJ mis-represents both):**
- **MgEl-O:** 53.2 is the DFT single-THF VACUUM binding (−0.668 eV). In the liquid the relevant quantity is the **adsorption FREE energy** (a THF must desolvate from bulk to adsorb) — much weaker. The full binding over-binds → frozen monolayer. Also chemisorption saturates (one monolayer); a non-saturating LJ keeps binding every approaching O.
- **MgEl-Cl:** 132.7 LUMPS the image-charge into a deep short-range well. Real image-charge is long-range (r⁻¹) and lets the ion slide laterally; the lumped LJ over-localizes → freezes the adsorbed anion in place.

**Questions for CPU/EPYC:**
1. Should MgEl-O be the condensed-phase ΔG_ads (e.g. PMF/metadynamics of one THF off Mg(0001) in liquid THF), not the −0.668 eV vacuum binding? Estimated ΔG_ads?
2. Is the Cl=132.7 image-charge-lumped static well defensible, or does it over-bind? Split the anion–metal into a weaker short-range LJ + an explicit image-charge / constant-potential term?
3. **Recommended REVISED effective MgEl-O & MgEl-Cl for the condensed phase**, OR confirm the adsorbing/charged interface fundamentally needs the MLFF/constant-potential reference and the classical T21 wall is solvent-structure-only with a frozen (non-equilibrating) monolayer.

**GPU meanwhile:** running a 0.5× sensitivity test (all MgEl-X ε halved: O→26.6, Cl→66.4, from the annealed config) — does a less-sticky wall mobilize the surface, equilibrate the bare control, and does any poly-vs-bare anion signal survive? Will report numbers.

### ✅ EPYC RESPONSE — T21c diagnosis CONFIRMED; condensed-phase wall landed — 2026-06-27

**Your diagnosis is correct on both counts** — the original O/Cl values are static single-adsorbate numbers misapplied as condensed-phase LJ wells. Revised values are in `incoming/mg_electrolyte_nbfix.itp` (and I updated your `gpu_build/mg_nbfix.itp` O/Cl mappings — pull-and-run):

| pair | OLD (froze) | **NEW (condensed dynamics)** | basis |
|---|---|---|---|
| **MgEl–O** | 0.18410 / **53.224** | 0.18410 / **26.000** (≈0.49×) | ΔG_ads, not vacuum binding (below) |
| **MgEl–Cl** | 0.18586 / **132.713** | 0.31636 / **3.738** (≈1/35) | D3 dispersion-only; image charge stripped |

**Q1 — MgEl-O: yes, use ΔG_ads, not the −0.668 eV vacuum binding.** Thermodynamic cycle: the adsorbing THF must **desolvate** from bulk (pay ≈½–1× ΔH_vap(THF)=+0.17 to +0.33 eV) and **lose translation/rotation** (−TΔS ≈ +0.10 to +0.20 eV). ΔG_ads ≈ −0.668 + 0.25 + 0.15 ≈ **−0.27 eV (range −0.20 to −0.35) ≈ 24–34 kJ/mol → ε≈26 (0.49×)**. Plus your saturation point: a 12-6 LJ doesn't saturate, but chemisorption is one monolayer — a deep non-saturating well keeps binding every approaching O. **Your 0.5× test (O→26.6) lands exactly on this estimate** — bless it for O. (The −0.668 eV TZVPP+BSSE number is still *correct* — just as a vacuum static binding, the wrong quantity for a liquid LJ ε.)

**Q2 — MgEl-Cl: yes, 132.7 over-binds; don't split, strip.** The image charge is long-range (r⁻¹) and **laterally flat** (depends only on z → the ion slides along the surface); lumping it into a deep short-range *site* well over-localizes and freezes the anion. For the neutral solvent-structure wall I **removed the image lumping** → bare D3 dispersion Mg-Cl (new DFT dimer, `B_cross/d3_MgCl`): **σ 0.31636 nm / ε 3.738 kJ/mol** (≈ your H/C/Si/S level). Note your 0.5× test only *halves* Cl (66.4) — still image-lumped, still sticky; **go to dispersion-only 3.738 for Cl**, not 0.5×.

**Q3 — recommendation: BOTH.** (a) The classical wall **is** a solvent-structure model — with the condensed O/Cl above it will **not** freeze, so the bare control should now reach A=B; re-run it. (b) The **anion–metal electrostatics (image charge / reductive plating) genuinely needs the MLFF / constant-potential reference** — that's where the charged-interface poly-vs-bare verdict lives (consistent with the T17 MACE+LES result), NOT the neutral LJ wall. If the structural poly-vs-bare anion signal **survives** the de-frozen wall → it's a real solvent-structure exclusion; if it **vanishes** → it was a freezing artifact and the verdict rests on the MLFF. Either outcome is informative. A one-THF-off-Mg(0001) PMF in liquid THF (GPU) would pin ΔG_ads beyond my cycle estimate. Status: ✅ **RESOLVED** — condensed wall delivered.

**Status:** ✅ RESOLVED 2026-06-27 (EPYC) — condensed-phase O/Cl in `incoming/` + `gpu_build/`; branch `computational-v3-interface`.

### ⚠️ T21c-quant — Mg-O QUANTIFIED → my first-pass "reduce O to 26" was an OVER-correction; reverted — 2026-06-27

I quantified Mg-O on the CPU (slab+THF binding scan + g16 gas-THF freq; `results/T21_metal_LJ_calibration/T21c_inputs/`). The number 26 was right *as a free energy* but **mis-assigned as the pair ε**. Key realization: **your interface MD is EXPLICIT-liquid**, so:

| quantity | value | role |
|---|---|---|
| **two-body Mg-O potential** | **−0.668 eV** (TZVPP+BSSE; raw TZVPP scan −0.735 @2.28 Å, BSSE 0.056) → ε **53.2** | the **pair LJ ε** (the liquid generates desolvation+entropy itself) |
| **ΔG_ads(liquid)** | **−0.27 eV ≈ 26 kJ/mol** (DFT binding + DFT S_gas=301 + Campbell-Sellers + ΔG_vap) | the **EMERGENT PMF** the MD should reproduce — a validation target, **NOT** ε |

In an explicit-liquid MD, baking ΔG_ads into ε **double-counts** the desolvation → under-binds. **Reverted O → 53.224** (`incoming/` + `gpu_build/`).

**The frozen THF monolayer is REAL, not a parameter bug.** Kinetic check: your observed *90 % no-desorb / 12 ns @ 400 K* requires a barrier **~0.4–0.55 eV = the two-body potential** (ΔG_ads's 0.26 eV → τ~2 ns @400 K → would NOT freeze). Mg–O is a genuine ~0.5 eV bond → a long-lived THF monolayer is correct. **So don't soften the real O bond to chase mobility.** The actual anion lever is **Cl** (kept stripped to dispersion-only 3.738 — the image-charge pin was the over-localizer); with Cl freed, the anion should equilibrate *over* the (physically) bound THF layer. If the THF monolayer's slowness still blocks the per-face metric → that's a **sampling** problem (enhanced sampling / a direct anion PMF), not a wall-depth problem.

**One thing for you to check:** a near-wall **O-density profile**. A 12-6 LJ doesn't saturate, so it over-pulls 2nd-layer O beyond the 1 real chemisorbed monolayer (+ σ=0.184 nm is short/stiff). If that *artifact* multilayer dominates the freezing (not the 1st layer), an effective O ε ~26–40 is a documented **mobility-prioritized fallback** (under-binds — label it as such). Status: ✅ **quantified; O reverted; Cl stripped stands.** *(Binding scan upgraded DZVP→TZVPP 2026-06-27: well −0.668 eV BSSE confirmed, ν 111 cm⁻¹; ε/ΔG_ads unchanged.)*

---

## T18 [both] — Descriptor screen for the interphase design rule (Figure 7) — NEW 2026-06-23

**Goal:** turn the validated poly-APC mechanism into a *predictive, falsifiable* top-down design rule. Compute the four design descriptors for a small library of candidate curing/passivator network chemistries so the Figure 7c selection map fills out with real predicted points (currently open symbols). This is the focused in-paper set (Option A); it is **NOT** the full high-throughput screen (Option B — on hold pending PI mark).

**Descriptors (match existing baselines):**
- **D1 — reductive co-deposition propensity** [EPYC, molecular DFT, B3LYP-D3(BJ)/def2-TZVP//def2-SVP, SMD(THF), as T2]: for each network fragment in the presence of the dominant electroactive anion — reduction potential vs Mg²⁺/Mg, LUMO/EA, and whether 1e⁻ reduction yields a metal-centred radical (Al–X scission ΔG). Flag *deposits conductive metal? yes/no*.
- **D2 — electron-injection barrier** [EPYC, periodic DFT, CP2K PBE-D3, as T8/T8b]: build each candidate's cured thin layer; band gap, electron affinity χ, CBM vs vacuum; Φ_inj = CBM − Mg E_F(−3.97 eV). Primary screen axis.
- **D3 — anion sequestration** [GPU, MLFF-MD gel box, as T5/T17]: fraction of aluminate anion network-associated + anion self-diffusion ratio (gel/liquid).
- **D4 — cation transparency** [GPU, same MD]: network-O ↔ Mg²⁺ first-shell coordination number (want ≈ 0).

**Candidate library (5):**

| # | candidate network | motif | predicted verdict (to test) |
|---|---|---|---|
| 1 | POSS / silsesquioxane | Si–O–Si | reference (validated; have) |
| 2 | borosiloxane | B–O–Si | strong (wide gap + Lewis-acid Cl⁻/anion binding) |
| 3 | phosphazene | P=N | moderate |
| 4 | polyether-siloxane | C–O–C / Si–O | moderate; risk: ether-O lowers D4 |
| 5 | aluminum alkoxide / alumoxane | Al–O | **FAIL control** (Al-rich → leaky/metallic) |

**Split:** EPYC → D1 + D2 for all 5. GPU → D3 + D4 for the top 3 (POSS, borosiloxane, + Al-alkoxide control for falsification). Every MLFF number DFT-validated (report force/energy MAE) per the active-learning rule.

**Deliverables → `results/T18_design_screen/`:** `outputs/<candidate>_descriptors.{csv,json}` (D1–D4 + provenance), `outputs/screen_summary.csv` (ranked), `REPORT.md`. These feed the Figure 7c open symbols and the "A Transferable Computational Design Rule" subsection.

**Status:** ⬜ OPEN — dispatched 2026-06-23 on branch `computational-v3-interface`.

---

## T19 [EPYC now; GPU gated] — Screen B, full descriptor screen (pre-registered) — NEW 2026-06-23

**Plan is frozen in `SCREEN_B_PREREGISTRATION.md` — read it first.** Library: `results/T19_screen_B/inputs/library_round1.csv` (N=40: 31 networks + 9 anions; generator `gen_library_B.py`; sha256 `bf56836cadce`).

### ▶ EPYC — execute NOW (Tiers 1 & 2)
- **Tier 1 — molecular DFT** [B3LYP-D3(BJ)/def2-TZVP//def2-SVP, SMD(THF), as T2] on **all 40** candidates:
  - **D1** — anion E_red vs Mg²⁺/Mg, LUMO/EA, 1e⁻ Al–X scission ΔG, metal-incorporation E_sub; flag *co-deposits conductive metal? yes/no*.
  - **D3-proxy** — counterpoise-corrected group→anion binding energy.
  - **D4-proxy** — group→Mg²⁺ binding vs THF→Mg²⁺.
  - PASS rule (to Tier 2): no conductive-metal co-deposition **and** D4-proxy weaker than THF→Mg²⁺ (see pre-reg §5).
- **Tier 2 — periodic DFT** [CP2K PBE-D3, GTH/MOLOPT, as T8/T8b] on the **31 network** cured-phases (Tier-1 survivors):
  - **D2** — gap, χ, CBM vs vacuum, Φ_inj = CBM − Mg E_F(−3.97 eV). PASS if Φ_inj ≥ 1.0 eV & gap ≥ 3.0 eV; STRONG if Φ_inj ≥ 2.5 eV.
- **Reuse T18** D1/D2 for the 5 overlapping candidates — do not recompute.
- **Deliverables → `results/T19_screen_B/outputs/`:** `tier1_descriptors.csv`, `tier2_bandalign.csv`, `screen_ranked.csv`, `design_map.{csv,png}`, `REPORT.md` (schema in pre-reg §9). Log all attrition; report uncertainties. **Validate the screen against controls** (POSS top quartile / Al-alkoxide bottom quartile, pre-reg §6, §10) — HALT and flag if either control fails.

### ⛔ GPU — Tier 3 GATED (do NOT start)
Reactive MLFF-MD (D3 sequestration + D4 CN) + active-learning loop — **on PI mark only; GPU node is busy.** Pre-reg §7. When released, validates the Tier-1 proxies on the shortlist.

**Status:** ▶ EPYC Tiers 1&2 **DISPATCHED** 2026-06-23 · ⛔ GPU Tier 3 **HELD** (awaiting PI mark).

---

## T20 [GPU] — Interfacial aluminate-anion concentration profile C(z) (manuscript re-framing panel "B") — NEW 2026-06-24

**Why:** re-framing per `APC_knowledge/` (Liu, *Adv. Mater.* **2022**, 34, 2201886 — uneven *stripping* is the killer, driven by **interfacial chlorine-containing complex-ion accumulation in pits**; the prescribed cure is to **homogenize the interfacial Cl-ion concentration**). This panel shows poly-APC's cured network achieves that homogenization/sequestration **structurally** (without stirring) — directly bridging our anion-sequestration result (T5) to the PI's own stripping framework.

**Goal:** from the **existing T5/T17 trajectories**, compute the steady-state number-density / concentration profile of the **aluminate anion** (and the [Mg₂(μ-Cl)₃(THF)₆]⁺ cation, reported in parallel) vs distance **z from the Mg(0001) front**, bare vs poly. Mirror Liu 2022 Fig 5e–g C(x).

**Deliverables → `results/T20_iface_profile/`:**
- `outputs/anion_density_profile.csv` — `z_angstrom, rho_anion_bare, rho_anion_poly, rho_cation_bare, rho_cation_poly` (normalized to bulk).
- `outputs/iface_accumulation_metrics.csv` — near-front (≤1 nm) anion enrichment ratio bare vs poly; depletion/standoff width (reuse T5 ~7–8 Å poly standoff); block-average error bars.
- `REPORT.md` — method, frame count, uncertainties. Label as classical-MD/MLFF **distribution** (model), not a reactive event.
- (optional) `outputs/Cz_profile.png` quick view.

**Method:** z-histogram of anion/cation centroid over equilibrated frames, both legs in parallel, block-average uncertainty. Reuse existing trajectories; only run a short extension if sampling is insufficient. **Distinct from the gated T19 Tier 3** (this is light trajectory post-processing, not the reactive screen).

**Status:** ✅ **DONE** 2026-06-24 (GPU) → `results/T20_iface_profile/` (REPORT + CSVs + `Cz_profile.png`).
Headline: reducible anion near-front occupancy (≤5 Å) **bare 98.8 % → poly 2.2 % (~44×)**; ion ordering
**inverts** (bare: anion 4.6 < cation 5.8 leads; poly: cation 5.2 < anion 6.8 → anion excluded); neither
reaches reductive contact (<2.5 Å) field-free = Liu-2022 homogenization achieved structurally.
⚠️ Surfaced: **poly neutral standoff is not cleanly equilibrated** (runs settle 6.8–10.3 Å, still drifting;
bare is tight at 4.6) — sign-robust, magnitude needs a PMF/multi-start. See `T5.../fig_equilibration.png`.
Also: the `fig_mechanism` ion-pair-separation numbers (7.8/9.9 Å) need re-derivation (bare cation Mg dissociates).

## T21 [EPYC->GPU] FINAL — REBUILD the sym-interface with the COMPLETE DFT-anchored wall — 2026-06-27

T21 calibration DONE. In `incoming/`: **`mg_metal.itp`** (Mg-Mg free-slab LJ) + **`mg_electrolyte_nbfix.itp`**
(all Mg-electrolyte cross terms) + the two RESPONSE.md. Please rebuild `build_interface_sym.py` with these:

1. **Free slab** (drop UFF + the k=50000 POSRES). MgEl atomtype = `mg_metal.itp` (sigma 0.29436 nm, eps 18.103
   kJ/mol). Anchor ONLY the bottom 1-2 layers (weak POSRES); surface free (AIMD convention). The cohesive eps now
   lets the slab self-cohere (UFF eps was 39x too weak -> that's why you needed POSRES).
2. **All Mg-electrolyte pairs via NBFIX** (`[ nonbond_params ]`, comb-rule 3) - do NOT use the combining rule for
   any MgEl-X (the cohesive eps doesn't transfer): MgEl-O 0.18410/53.22 (gold-std, TZVPP+BSSE) | MgEl-Cl
   0.18586/132.71 (effective) | MgEl-H 0.23683/1.43 | MgEl-C 0.32326/2.57 | MgEl-Si 0.33969/5.86. Map `O`->your
   THF/siloxane ether-O type, `Cl`->bridging Cl, etc.
3. **Omit** MgEl-Mg2+ (cation solvated, standoff via Mg-O) and MgEl-Al (shielded in [AlPh2Cl2]-; anion contacts
   via Cl/C/H).
4. **Then re-check the per-face enrichment.** Expect the stronger calibrated MgEl-O to change the THF<->wall
   competition that sets ion positions. HONEST CAVEAT: the neutral LJ wall still cannot capture the anion
   image-charge or the reductive plating - so if classical still disagrees with the MLFF depletion, that's the
   reason (constant-potential electrodes / the MLFF remain the reference for the charged-interface verdict), NOT a
   bad wall. Treat the calibrated classical run as the solvent-structure model.

Files: `mg_metal.itp`, `mg_electrolyte_nbfix.itp`, RESPONSEs; T21 plan `results/T21_metal_LJ_calibration/PLAN.md`.

## T21b [GPU->EPYC] — need MgEl-F + MgEl-S NBFIX to finish the poly rebuild — 2026-06-27

GPU rebuilt + validated the calibrated wall on **bare** (`results/T21_metal_LJ_calibration/gpu_build/build_interface_sym_t21.py` + `mg_nbfix.itp`): free slab self-coheres (NN 0.321 nm = LJ min r0=1.0903σ; only the outer/vacuum-facing layer weakly anchored MGE_A k=1000, surface free; 50 ps NVT layers intact, spread <0.03 nm), EM Potential now **−2.1e5 (physical)** vs old +2.3e5 UFF, NVT stable. MgEl-O/Cl/H/C/Si NBFIX mapped to the OPLS types and in. ✅ **bare is done.**

**BLOCKER for poly:** the POSS network NET1 uses two atom types with NO calibrated MgEl pair — **`opls_FC` (F, 3 atoms)** and **`opls_ST` (S, 1 atom)**. Without their NBFIX they fall to the cohesive combining rule (geometric of MgEl eps=18.1 → over-bind). Bare has neither (→ done); **poly is HELD** (PI directive 2026-06-27: hold for Mg-F/Mg-S).

**Request:** DFT-anchored **`MgEl-F` and `MgEl-S`** cross-LJ (sigma nm / eps kJ/mol, comb-rule 3), same format as the O/Cl/H/C/Si in `mg_electrolyte_nbfix.itp`. Trace (4 atoms, in the gel bulk not at the interface) → a **D3-dispersion weak-vdW** level (like your H/C/Si) is sufficient; no gold-standard needed. Drop into `incoming/` (append to `mg_electrolyte_nbfix.itp` or a small `mg_FS_nbfix.itp`); GPU maps to opls_FC/opls_ST and runs poly immediately. Status: ⬜ **OPEN**, dispatched 2026-06-27.

### ✅ EPYC RESPONSE — T21b FULFILLED, poly UNBLOCKED — 2026-06-27

Both pairs landed (D3 weak-vdW level, as requested). **In `incoming/mg_electrolyte_nbfix.itp`** (and I also filled your `gpu_build/mg_nbfix.itp` placeholders so you can pull-and-run):

| pair | map to | sigma (nm) | eps (kJ/mol) | provenance |
|---|---|---|---|---|
| **MgEl–F** | `opls_FC` | **0.29717** | **1.501** | ESTIMATED (D3/atomic-C6 trend; F GTH basis aborted). CF3 — most **inert** pair, lowest impact. |
| **MgEl–S** | `opls_ST` | **0.32326** | **3.556** | D3 dispersion (sulfonate S); S buried in –SO₂CF₃, low surface contact. |

Your placeholder guesses (F 0.30000/1.500, S 0.34000/5.000) were close — **F essentially exact**; **S** now D3-anchored, a touch softer/weaker. Both are weak vdW (≪ O 53.2, Cl 132.7); they do **not** touch the Si-up/Al-down interface story — the 4 F/S atoms sit in the NET1 gel bulk, not the reactive front, so this just stops them collapsing to the cohesive combining rule. **→ poly rebuild is GO.**

**Your `gpu_build/mg_nbfix.itp` mapping is VERIFIED ✔** (O/Cl/H/C/Si → correct OPLS types; cation/Al correctly omitted). **One forward caveat:** you map *all* O types (`opls_OS/OB/OE/OH/OT`) to the gold-standard ether-O well (53.224, −0.67 eV). That is correct for ether/THF/siloxane/hydroxyl O — but **sulfonate-O (triflate –SO₂–) is NOT ether-O**: if you ever add explicit TMSOTf/triflate-O to the model, the ether value will **over-bind** it (the sulfonate O is more diffuse / anionic-resonance delocalized) — use ~half, or scan an explicit triflate-O well. Not a blocker now (triflate is held out of the current NET1/poly_geom model). Status: ✅ **CLOSED**.
