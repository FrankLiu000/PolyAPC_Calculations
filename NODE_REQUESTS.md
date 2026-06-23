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
