# Story A.2 — large-cell collective conductivity, ionicity & viscosity/Walden

**Date:** 2026-06-08 · **Machine:** LYZ-ROG (GROMACS 2025.1, RTX 4070 Ti SUPER) ·
**Scope:** Story A, large-cell σ_coll item of [`../../PLAN_classical_MD_stories.md`](../../PLAN_classical_MD_stories.md), plus a viscosity/Walden cross-check prompted by a solvation-vs-desolvation review.

## Objective
Test whether **de-noised collective conductivity** (large cell, Einstein–Helfand) corroborates the
carrier-number / de-pairing mechanism established in Story A.1, and add a viscosity/Walden ionicity cross-check.

## Large cell
2×2×2 `genconf` tiling of the 8-POSS swollen system (`structures/02_polyAPC_8POSS_swollen`) →
**303,536 atoms, 14.70 nm cubic**. Tiling is exact (`genconf -dist 0` reproduces the original PBC —
no broken network bonds; largest excluded-atom distance 0.571 nm, same as the single cell). EM-stable,
density 0.99 g/cm³. Protocol: **50 ns NPT pre-eq** (≥50 ns, per the A.1 ion-pairing-equilibration lesson)
→ **200 ns NVT production** @ 298 K.

## Results

### Collective conductivity (Einstein–Helfand, `gmx current`)
| quantity | value |
|---|---|
| σ_coll | **0.012 ± 0.004 S/m** (full-traj 0.012; 4×50 ns blocks −0.001 / 0.019 / 0.014 / 0.016) |
| D cation / anion | 0.020 / 0.022 ×10⁻⁵ cm²/s (fit 40–180 ns) |
| σ_NE (Nernst–Einstein) | 0.053 S/m |
| **ionicity σ_coll/σ_NE** | **0.228** |

**Corroborates de-pairing:** the swollen-gel ionicity (0.228) is **~2× the campaign's bare-APC value
(~0.08–0.13)**. Higher ionicity = more ions moving as independent carriers = exactly the CIP→SSIP
de-pairing of A.1 (×3.4 free carriers). Collective transport, measured directly, agrees with the
carrier-number mechanism. σ_coll is intrinsically noisy (blocks span −0.001…0.019) — reported with the
block error and the ionicity ratio, never a bare magnitude.

### Viscosity & Stokes–Einstein decoupling
20 ns NVT with frequent pressure tensor; η via `gmx energy -vis` (Green–Kubo shear) & `-evisco` (Einstein).
| | η (GK / Einstein) |
|---|---|
| bare-APC | 1.09 / 1.71 cP (≈ **1.4**) |
| 8-POSS swollen | 8.78 / 11.99 cP (≈ **10.4**) → **×7.4 more viscous** |

**Strong Stokes–Einstein decoupling:** η rises ×7.4 but ion D falls only ×1.6–2.5 (bare 0.053 →
swollen 0.021–0.033). SE (D ∝ 1/η) would predict a ×7.4 drop → ions are **~3× more mobile than the
viscosity implies** (fractional SE, D ∝ η^−0.3…−0.5). The swollen THF channels **decouple ion transport
from the polymer matrix's mechanical viscosity** → mechanical robustness (×7.4 η, dendrite-relevant →
Story C) *without* a proportional mobility penalty. This is the structural reason the de-pairing strategy wins.

### Walden cross-check
Walden ionicity (vs the aqueous-KCl ideal line): bare 0.008, swollen 0.115 → **swollen ≫ bare**,
independently corroborating the ionicity trend. *Absolute* Walden values are **trend-level only**
(short 20 ns single-cell σ_coll is noisy; aqueous KCl is a poor non-aqueous reference).

## Ion-pairing speciation & dynamics (article-prompted, on A.1 trajectories)
- **SSIP / CIP / AGG** (converged 70–100 ns): de-pairing is **CIP→SSIP** (+10.9 pts; bare 4.6 % / swollen
  15.5 % SSIP = free-carrier f), **negligible AGG** (~0.3–0.5 %).
- **Ion-pair residence time** (intermittent survival ACF): pairs kinetically **frozen** (τ_c > 25 ns) in both,
  swollen slightly *more* persistent → the σ gain is **carrier-number-driven, not exchange-rate**; the
  mobility penalty is **confinement** (Story C), not pair kinetics. These divalent Mg complexes sit in the
  rigid / whole-entity regime, unlike fast-hopping Li⁺.

## Synthesis
A.1 (de-pairing CIP→SSIP, ×3.4 free carriers, D ÷1.6) + A.2 (ionicity 0.228 ≈ 2× bare; η ×7.4 with strong
SE decoupling) + speciation/residence **all converge on one mechanism**: the cured POSS network raises σ by
increasing free-carrier *number* (thermodynamic de-pairing), while swollen THF channels keep ions mobile
despite a much more viscous, mechanically robust matrix.

## Caveats / follow-ups
- A.1's D (0.033; 20–80 ns fit overlapping the pairing drift) is a mild overestimate — A.2's properly
  pre-equilibrated D (0.021) is more reliable, confirming the A.1 caveat.
- No **matched** bare large-cell σ_coll (compared against the older bare estimate); a bare large cell would
  make the ionicity comparison apples-to-apples (easy add).
- σ_coll is noisy (collective transport); η ≈ ±30 % (GK vs Einstein, 20 ns); Walden absolute scale
  unreliable (aqueous reference). **Trends are robust; absolute magnitudes are trend-level.**

## Files
- `transport/RESULTS_storyA2.txt` (σ_coll, D, σ_NE, ionicity) · `transport/RESULTS_walden.txt` (η, Λ, Walden ionicity)
- `solvation/RESULTS_speciation_ssip_cip_agg.txt` · `solvation/RESULTS_residence_time.txt`
- `scripts/` — `agg_storyA2.py`, `walden.py`, `speciation_ssip_cip_agg.py`, `residence_time.py`
- Trajectories regenerable on LYZ-ROG (`run_storyA2.sh`, `run_viscosity_walden.sh`); gitignored (too large).
