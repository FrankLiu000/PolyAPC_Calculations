# T19 (Screen B) — top-down interphase design screen — REPORT (EPYC, in progress)

**Branch:** computational-v3-interface · **Started:** 2026-06-23 · Plan frozen in `SCREEN_B_PREREGISTRATION.md`.
EPYC executes Tier 1 (molecular DFT, all 40) + Tier 2 (periodic DFT, 31 network survivors); GPU Tier 3 gated.

## Status: campaign underway, staged controls-first
This is a ~71-calculation pre-registered campaign; structures are **built by hand** (no RDKit/obabel on this node)
so it proceeds in batches through the monitoring loop. Outputs accrue in `outputs/`; attrition logged; no silent caps.

### Tier 1 D4-proxy (cation transparency) — DONE (`tier1_mol/D4proxy/`)
Ligand-exchange [Mg–THF]²⁺ + L → [Mg–L]²⁺ + THF (B3LYP-D3/def2-SVP, SMD-THF; cancels ill-posed bare Mg²⁺).
**siloxane-O = +14.5 kcal/mol weaker than THF (strongly transparent, PASS); ether-O = +4.4 (PASS but marginal).**
→ Both pass D4, but POSS/siloxane is ~10 kcal/mol more transparent than polyether. **Confirms the predicted
polyether D4 risk** (it passes D2=SiO₂ but is the marginal network on transparency). Siloxane = ideal D4 donor;
consistent with t₊=0.50 both (transport not the discriminator). Recorded for B001–B008 (siloxane) and B016–B018
(polyether). Provenance: `D4proxy_result.md`, `d4proxy_energies.csv`.

### Reusable anchor (real results already in the scaffold)
- **Tier 1 D1 — 4 APC aluminates (B032–B035)** from **C1/T1** (B3LYP-D3/def2-TZVP//def2-SVP, SMD-THF): all reduce
  at Al → Al⁰ (AlCl₄⁻ spin +1.14 reduces *at* Al; [AlPh₂Cl₂]⁻ → reductive Al–Cl cleavage ΔG −8.5 → 83% Al-radical).
  → **co-deposit conductive metal = YES** (the in-narrative APC anions; the screen's "deposits metal" axis).
- **Tier 2 D2 — SiO₂ (POSS, B001–B008)** from **T8b**: gap 8.46 eV, χ 0.90, Φ_inj **3.07 eV → STRONG** (positive
  control H2). **Al₂O₃ (alumoxane, B029–B031)**: gap 6.21, Φ_inj 2.62 (D2 passes) **but the candidate FAILS via
  D1** (Al⁰ co-deposit, gapless metal) → negative control H3 (bottom quartile by the metal flag).

### Build queue (new DFT, controls-first)
- **Tier 1 D1:** 5 non-APC anions [BH₄⁻ (B036), TFSI⁻ (B039), carborane [CB₁₁H₁₂]⁻ (B038), 2 fluorinated borates
  (B037/B040)] + 31 network fragments (silsesquioxane variants, borosiloxane, phosphazene, …) — each: neutral opt,
  +1e⁻ reduced, E_red vs Mg²⁺/Mg, LUMO/EA, metal-centred-radical? + D3/D4 binding proxies.
- **Tier 2 D2:** ~22 new cured phases — borosilicate (B009–11), TiO₂·SiO₂ (B022–23), ZrO₂·SiO₂ (B024–25), GeO₂
  (B028), P-oxynitride / phosphosilicate (B012–15, B026–27), SiOC/SiC (B019–21), aluminosiloxane (B029–30).
  CP2K PBE-D3 band-align as T8/T8b → gap, χ, CBM_vac, Φ_inj.

### Pre-specified GO/NO-GO (do not skip)
Accept the descriptor set only if **POSS top quartile (H2)** AND **Al-alkoxide bottom quartile (H3)**; else HALT
and log (pre-reg §10). Falsifiable predictions to report regardless: borosiloxane/zirconosiloxane ≥ POSS (H4);
SiC-gap may FAIL gap≥3 (semiconductor); fluorinated/TFSI anions = comparators only (off-narrative, flagged).

## Outputs (schema = pre-reg §9)
`outputs/tier1_descriptors.csv` (seeded) · `outputs/tier2_bandalign.csv` (seeded) · `screen_ranked.csv`,
`design_map.{csv,png}`, `validation/mlff_mae.csv` (Tier 3) — to follow as batches complete.
