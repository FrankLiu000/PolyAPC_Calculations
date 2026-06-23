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

**Status:** ▶ GPU **DISPATCHED** 2026-06-24.
