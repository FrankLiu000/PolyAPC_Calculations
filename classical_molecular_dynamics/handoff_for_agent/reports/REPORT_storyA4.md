# Story A.4 — Arrhenius D(T) → activation energy

**Date:** 2026-06-11 · **Machine:** LYZ-ROG (GROMACS 2025.1) · Story A, Arrhenius item.

## Protocol
5 temperatures (273/288/298/313/333 K) × {bare-APC, 8-POSS swollen}. Per (T, system):
50 ns NPT pre-eq (re-equilibrate density+pairing at T, from the A.1/A.2 converged frames) →
100 ns NVT production. D(T) = avg(cation, anion) from `gmx msd` (fit 20–80 ns); σ(T) from
`gmx current`. Fit ln D vs 1/T.

## Results
| T (K) | D bare | D swollen | (×10⁻⁵ cm²/s) |
|---|---|---|---|
| 273 | 0.019 | 0.014 | |
| 288 | 0.029 | 0.014 | |
| 298 | 0.028 | 0.027 | |
| 313 | 0.059 | 0.036 | |
| 333 | 0.101 | 0.038 | |

| system | Eₐ | fit |
|---|---|---|
| bare-APC | **21.4 kJ/mol = 0.222 eV** | R² = 0.94 |
| 8-POSS swollen | **14.8 kJ/mol = 0.154 eV** | R² = 0.84 |

## Interpretation
The swollen gel's **bulk Mg-migration barrier is not elevated above bare** (if anything lower).
→ Confirms hypothesis 3: the experimentally higher poly DRT **R_ct is not a higher bulk-migration
barrier** — it is carrier-number- and/or **interfacial-desolvation**-limited (the latter is DFT/AIMD
scope, per the solvation-vs-desolvation distinction). A low, liquid-like Eₐ in the swollen gel is
consistent with the **A.2 Stokes–Einstein decoupling**: ions migrate through liquid-like THF channels
(low barrier), decoupled from the viscous polymer matrix.

## Caveats
- **swollen Eₐ is the soft number**: swollen D is small/slow → noisier MSD (288 K point flat, R²=0.84).
  Read as "swollen barrier ≈ bare or lower", not precisely 14.8.
- **σ(T) too noisy for an Arrhenius** (collective σ from single 100 ns cells scatters 0.010–0.049
  non-monotonically) → D(T)→Eₐ is the usable measure; σ(T) kept for the record.
- Single run per (T, system); replicates per T would tighten Eₐ to publication grade.

## Files
- `transport/RESULTS_arrhenius.txt` · `scripts/arrhenius_fit.py`
- Trajectories (10 × 100 ns) regenerable on LYZ-ROG (`prod/arrhenius/run_arrhenius.sh`); gitignored.
