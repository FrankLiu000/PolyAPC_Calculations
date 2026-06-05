# Story A.1 — conductivity story tightened & de-risked (swollen-8 vs bare-APC)

**Date:** 2026-06-05 · **Machine:** LYZ-ROG (GROMACS 2025.1, RTX 4070 Ti SUPER) ·
**Scope:** Story A.1 of [`../../PLAN_classical_MD_stories.md`](../../PLAN_classical_MD_stories.md).

## Objective
Replace the thin **2×50 ns** swollen-8 sampling with **5×100 ns** independent seeds (and extend
bare-APC to a matched 5×100 ns) to firm up D(cat/an), t₊, free-carrier f, and the f·D
conductivity proxy with error bars.

## Systems & protocol
- **8-POSS swollen gel** (`structures/02_polyAPC_8POSS_swollen`, 37 942 atoms) — 5 fresh seeds.
- **bare-APC** — reps 4–5 added to existing reps 1–3 → 5×100 ns matched reference.
- NVT 298 K, 2 fs, PME, h-bond constraints, v-rescale, from NPT-equilibrated coords (matches the
  committed campaign; OPLS-AA, Mg +1.2 / bridging-Cl −0.467 scaled charges).
- D: `gmx msd` COM-MSD, fit 20–80 ns. f = 1 − (Mg–anion-Cl first-shell contact fraction, 0.345 nm).

## Results (mean ± SEM, n = 5)
| | bare-APC | 8-POSS swollen | ratio |
|---|---|---|---|
| D cation [Mg₂Cl₃·6THF]⁺ (10⁻⁵ cm²/s) | 0.053 ± 0.003 | 0.033 ± 0.002 | ÷1.60 |
| D anion [Ph₂AlCl₂]⁻ (10⁻⁵ cm²/s) | 0.053 ± 0.004 | 0.033 ± 0.003 | ÷1.61 |
| t₊ = D₊/(D₊+D₋) | 0.502 ± 0.006 | 0.504 ± 0.008 | invariant |
| free-carrier f (converged 70–100 ns) | 0.046 ± 0.006 | 0.155 ± 0.005 | ×3.4 |
| **σ ∝ f·⟨D⟩ (swollen / bare)** | | | **2.10 ± 0.32** |

## Two findings that revise the prior story

### 1. Mobility is NOT preserved — swollen D is ÷1.6 vs bare
The earlier "swollen D preserved at ≈98 % of bare" rested on 2×50 ns, which cannot even support
the standard 20–80 ns MSD fit window. With 5×100 ns, swollen-8 self-diffusion is **~1.6× slower**
than bare (0.033 vs 0.053) — physically between the free bare liquid and the dense 4-POSS gel
(×4.5). So the σ gain is **de-pairing-dominated and partly offset by reduced mobility**, not
"de-pairing + preserved mobility".

### 2. Ion-pairing equilibrates slowly — prior contact-pairing numbers were unconverged
Contact-pairing **drifts** during production: both systems start ~57–64 % paired (from the
NPT-equilibrated structures) and associate over tens of ns.

| window (ns) | bare r1 | bare r4 | swollen s1 |
|---|---|---|---|
| 0–10 | 57 | 57 | 64 |
| 20–30 | 82 | 78 | 78 |
| 40–50 | 90 | 86 | 82 |
| 60–70 | 93 | 92 | 83 |
| 80–90 | 95 | 93 | 83 |
| 90–100 | 96 | 94 | 83 |

This one drift curve reconciles previously-contradictory contact numbers (the campaign's own
`solvation/` summary 49.7 % ≈ first ~5 ns; MANIFEST 83.3 % ≈ mid-window; a naive last-50 ns read
94 %) — **same cutoff, different points on an unconverged transient**. The 1 ns pre-equilibration
is far too short to equilibrate ion association (bare ~80 ns, swollen ~40 ns to plateau). Old and
new bare runs (r1 vs r4) drift identically → systematic and reproducible, not a seed artifact.

**Converged free-carrier fractions (70–100 ns):** bare 0.046 ± 0.006, swollen 0.155 ± 0.005 →
swollen de-pairs **~3.4×** vs bare — the de-pairing mechanism is real and *larger* than the
campaign's 1.48× f-ratio.

## Conclusion
σ_swollen > σ_bare is confirmed and firmed to **×2.1 ± 0.3** (f·D proxy): **de-pairing-driven**
(×3.4 free carriers) with a **mobility penalty** (÷1.6). t₊ ≈ 0.50, invariant. This revises the
under-sampled "preserved-mobility" picture while keeping the headline σ_poly > σ_bare conclusion.

## Caveats / follow-ups
- **D is fit over 20–80 ns, which overlaps the pairing drift** (esp. bare) → D is measured over a
  partly non-stationary state. Clean fix: **≥50 ns pre-equilibration** (or longer production), then
  fit D and read f in the converged window. *All subsequent stories (A.2/A.3/A.4) adopt ≥50 ns pre-eq.*
- 100 ns is marginal for bare f convergence (~80 ns to plateau, ~20 ns clean).
- σ here is the **f·D Nernst–Einstein-style proxy**; collective σ_coll (Einstein–Helfand) + ionicity
  is Story A.2.

## Files
- `transport/RESULTS_storyA1_converged.txt` — headline (converged f, σ = 2.10 ± 0.32)
- `transport/RESULTS_storyA1.txt` — raw aggregation (last-50 ns f; its 1.75 ratio understates because
  bare f is not converged in that window)
- `solvation/storyA1_contact_pairing_drift.txt` — the equilibration finding (time series)
- `scripts/` — `agg_storyA1_converged.py`, `contact_timeseries.py`, `solvation.py`, `agg_storyA1.py`
- Trajectories (5+5 × 100 ns) are regenerable on LYZ-ROG via `prod/run_storyA1.sh` (gitignored — too large).
