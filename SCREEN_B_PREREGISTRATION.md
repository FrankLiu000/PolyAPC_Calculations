# Pre-Registration — Top-Down Computational Screen for the Mg-Anode Interphase
### Campaign **T19** ("Screen B")

| | |
|---|---|
| **ID** | T19 (Screen B) — full high-throughput, active-learning descriptor screen |
| **Branch** | `computational-v3-interface` |
| **Date pre-registered** | 2026-06-23 |
| **PI** | Frank Liu |
| **Relation to T18** | Extends/supersedes T18 (the in-paper Figure 7 5-candidate subset). T18 D1/D2 are **reused** for overlapping candidates; not recomputed. |
| **Purpose of pre-registration** | Fix the library, descriptors, thresholds, ranking, and analysis plan **before** any results exist, so hits cannot be selected post hoc. No-fabrication discipline (see §11). |

---

## 1. Objective
Convert the validated poly-APC design rule into a **predictive** screen over cured-network/passivator and reducible-anion chemistries. Output: a ranked candidate list, a design map (Pareto front), and falsifiable predictions for chemistries we have not synthesized.

## 2. Hypotheses (pre-specified, falsifiable)
- **H1 (rule).** A cured network that **maximizes the electron-injection barrier (D2) and anion sequestration (D3) at fixed cation transport (D4)**, and whose reduction **does not co-deposit a conductive metal (D1)**, yields a reversible Mg interphase.
- **H2 (positive control).** POSS/silsesquioxane → SiO₂ is recovered in the **top quartile**. If not → descriptor set rejected.
- **H3 (negative control).** Aluminum-alkoxide/alumoxane (Al–O) ranks in the **bottom quartile** (predicted FAIL: Al-rich, electronically leaky). If it ranks high → rule refuted.
- **H4 (new predictions).** Borosiloxane and zirconosiloxane networks **match or exceed** POSS.
- **H5 (transferability).** The screen rank-orders non-APC anions by reducibility consistent with their Al/B redox chemistry.

## 3. Candidate library
- **Round-1 library:** `results/T19_screen_B/inputs/library_round1.csv` — **N = 40** (31 network/passivator chemistries, 9 anion families).
- **Generator:** `results/T19_screen_B/inputs/gen_library_B.py` (deterministic). **sha256(library_round1.csv) = bf56836cadce…**
- **Two axes (one-at-a-time in Round 1):** (A) networks screened with the APC anion `[AlPh₂Cl₂]⁻` fixed; (B) anions screened with the POSS/SiO₂ network fixed.
- **Expansion:** the library may grow by active-learning rounds (§7). Round-k additions are **appended with provenance**, never replacing Round 1. Any change is logged in §12.

## 4. Descriptors & methods (frozen)

| ID | Descriptor | Definition | Method / code (match baseline) | Node | Tier |
|---|---|---|---|---|---|
| **D1** | reductive co-deposition propensity | anion E_red vs Mg²⁺/Mg; LUMO/EA; 1e⁻ Al–X scission ΔG; metal-incorporation E_sub | molecular DFT **B3LYP-D3(BJ)/def2-TZVP//def2-SVP, SMD(THF)** [T2] | **EPYC** | 1 |
| **D3-proxy** | anion sequestration (proxy) | counterpoise-corrected group→anion binding energy ΔE_bind | same molecular DFT | **EPYC** | 1 |
| **D4-proxy** | cation transparency (proxy) | group→Mg²⁺ binding energy vs THF→Mg²⁺ | same molecular DFT | **EPYC** | 1 |
| **D2** | electron-injection barrier | cured-phase gap, χ, CBM vs vacuum; Φ_inj = CBM − Mg E_F(−3.97 eV) | periodic DFT **CP2K PBE-D3, GTH/MOLOPT** [T8/T8b] | **EPYC** | 2 |
| **D3** | sequestration (ground truth) | network-associated anion fraction + anion D ratio (gel/liquid) | reactive **MLFF-MD** (MACE-MP-0 / CHGNet), DFT-validated | **GPU** | 3 (gated) |
| **D4** | transparency (ground truth) | network-O↔Mg²⁺ first-shell coordination number | same MLFF-MD | **GPU** | 3 (gated) |

## 5. Tiered funnel & acceptance thresholds (pre-specified)
- **Tier 1 (EPYC, all 40).** Compute D1 + D3-proxy + D4-proxy. **PASS** if: (i) D1 — does **not** co-deposit a conductive metal (the reduction-to-metal pathway is not both-favorable; anions are evaluated for which metal, if any, they yield); **and** (ii) D4-proxy — group→Mg²⁺ binding **weaker** than THF→Mg²⁺ (does not strip cation solvation). FAIL → recorded and dropped.
- **Tier 2 (EPYC, Tier-1 network survivors).** Compute D2. **PASS (passivating)** if **Φ_inj ≥ 1.0 eV AND gap ≥ 3.0 eV**; **STRONG** if **Φ_inj ≥ 2.5 eV**. Metals (Φ_inj ≈ 0) FAIL.
- **Tier 3 (GPU, shortlist — GATED on PI mark).** Validate **D3 ≥ 30 % associated AND anion slowdown ≥ 2×**; **D4 CN ≤ 0.1**. Confirms the Tier-1 proxies at scale.
- **No silent caps.** Every dropped candidate is logged with the failing descriptor; attrition is reported.

## 6. Ranking / success metric (pre-specified — no post-hoc weight fishing)
- **Primary:** **Pareto dominance** on (Φ_inj ↑, sequestration ↑) within the set passing **D1 (no metal)** and **D4 (transparent)**. Report the Pareto front.
- **Secondary composite (fixed weights):** `S = 0.45·n(Φ_inj) + 0.45·n(seq) + 0.10·[D1 pass]`, where `n` = min–max normalization over the library. Until Tier 3, `seq` = D3-proxy (Tier 1); after Tier 3, `seq` = MD sequestration.
- **Screen self-validation:** the descriptor set is accepted only if it recovers **POSS in the top quartile (H2)** and **Al-alkoxide in the bottom quartile (H3)**. GO/NO-GO.
- **No experimental label is fit.** Experiment (POSS validated; predicted hits/failures) is the **out-of-sample** test, not a training target.

## 7. Active-learning protocol (Tier 3 / GPU)
EPYC DFT/AIMD labels → GPU fine-tunes MLFF (MACE-MP-0 base; CHGNet cross-check) → GPU production → configs with force uncertainty above threshold returned to EPYC for labeling → retrain. **Convergence (loop-until-stable):** stop a round when (a) MLFF **force MAE ≤ 50 meV Å⁻¹** and **energy MAE ≤ 5 meV atom⁻¹** on held-out DFT, **and** (b) the Pareto front is unchanged across two consecutive rounds. Every MLFF-derived number is **DFT-validated and reported with MAE**.

## 8. Compute plan & node split
- **NOW → EPYC:** **Tier 1** (molecular DFT, all 40) + **Tier 2** (periodic DFT, 31 network survivors).
- **GATED (on PI mark) → GPU:** **Tier 3** reactive MLFF-MD + active-learning loop. *(GPU node currently busy.)*
- **Reuse:** T18 supplies D1/D2 for the overlapping candidates (POSS, borosiloxane, phosphazene, polyether-siloxane, Al-alkoxide) — do not recompute.

## 9. Deliverables & output schema → `results/T19_screen_B/`
- `outputs/tier1_descriptors.csv` — cand_id, D1 fields, D3proxy, D4proxy, pass flags
- `outputs/tier2_bandalign.csv` — cand_id, gap, chi, CBM_vac, Phi_inj, verdict
- `outputs/screen_ranked.csv` — cand_id, pareto_rank, S, control flags
- `outputs/design_map.{csv,png}` — Φ_inj vs sequestration with Pareto front
- `REPORT.md` — methods, attrition table, MAE, hits, **predicted failures**, uncertainties, deviations
- `validation/mlff_mae.csv` — Tier 3 (when ungated)

## 10. Stop / decision rules
- If **H2 fails** (POSS not top quartile) **or H3 fails** (Al-alkoxide not bottom quartile): **HALT**, revise the descriptor set, log the deviation (§12), and do **not** report hits as validated.
- Declare a **"hit"** only if it (i) passes all four descriptor filters and (ii) is Pareto-non-dominated.
- **Tier 3 proceeds only on explicit PI mark.**

## 11. Integrity / locked constraints
- **No fabrication.** Models are labeled as models; every MLFF number is DFT-validated (MAE reported); uncertainties reported; **predicted FAILURES reported alongside hits**.
- **Narrative untouched.** Screened candidates are **design hypotheses**, not claims about poly-APC's actual interphase (which remains **Si ↑ / Al ↓, no fluorine/triflate narrative**). Off-narrative anions (TFSI⁻, fluorinated borates) are **comparators only**, explicitly flagged in the library.
- **Transport is not the discriminator.** D4 is enforced as a **fixed constraint**, never an optimization axis.

## 12. Deviations log (append-only)
| date | change | reason |
|---|---|---|
| 2026-06-23 | pre-registration created; Round-1 library frozen (N=40, sha bf56836cadce) | campaign start |
