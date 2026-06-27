# Open node requests (poll this on fetch)

| date | node | request | status |
|---|---|---|---|
| 2026-06-23 | **EPYC** (CP2K) | DOS/PDOS for 7 phases + Mg\|SEI band alignment → `results/T8b_DOS/`. | ✅ **DONE** (9be8e81; rendered into Fig 6 d/e — real DOS curves + band alignment, 3.07 eV SiO₂ block) |

*(GPU: no action required now. Optional: dump a representative T17 reactive-interface frame — bare Al co-deposited vs poly clean — for a Fig 5 snapshot.)*

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
