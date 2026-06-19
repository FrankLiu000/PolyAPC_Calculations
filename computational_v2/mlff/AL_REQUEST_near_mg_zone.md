# AL REQUEST (GPU→CPU): characterize the near-Mg zone so the bare interface runs to ns
## Why
The bare [Ph2AlCl2]- anion approaches the Mg(0001) anode to ~2-4 A (the near-Mg / reductive zone) in
MLFF-MD, but DFT training only thinly covers it (T10 AIMD sampled ~9.5-15 A; one AL round added 8 frames
@~4-5 A → stable to 50 ps but NOT ns). The MLFF is unstable there → the bare interface MD NaN's, can't
reach the ns timescale poly runs at. This zone is ALSO where the chemistry is (Cl/Al transfer to Mg,
Al co-deposition). Need it densely, cleanly DFT-characterized.

## What I need (priority order; full electrolyte = 64-Mg slab + cation + [Ph2AlCl2]- + THF)
1. **Anion approach ladder (intact):** anion COM at z = 2.0,2.5,3.0,3.5,4.0,5.0,6.0,8.0 A above the top Mg
   layer; ~6-10 thermally-sampled configs per height → ~60-80 frames. **Best: a short steered/umbrella
   AIMD pulling the anion 8→2 A, DFT-labeled along the path** — that gives the actual dynamical configs the
   MLFF-MD visits (what makes MD stable).
2. **Lateral + orientation diversity** at 2-4 A: anion over atop/bridge/hollow Mg; Cl-down vs Ph-down. ~20 fr.
3. **Reactive onset at contact (~2-3 A):** Cl transferring to Mg + Al-Mg/deposition onset, WITH the full
   electrolyte (not the isolated-fragment Cl-strip/deposition sets). ~15-20 fr.

## Constraints (heed the round-3 lesson)
- Slab forces MASKED (maskidx.json, first-64 atoms), SINGLE-POINT energies, k-point DFT (metal slab; your
  deposition-set level). config_type = `near_mg_bare_h<height>` (e.g. near_mg_bare_h30).
- **MODERATE, PHYSICAL perturbations — NOT extreme jitter.** The r3 set's |F|~32-35 eV/A jitter frames
  over-stiffened the model: it PASSED force MAE (30.8 meV/A) but went DYNAMICALLY UNSTABLE (bare MD NaN'd).
  Keep |F| in the physical range (≲15 eV/A); sample real thermal/reaction configs, not artificial rattles.
- (poly near-surface NOT needed — the network holds the poly anion at ~9 A, well-sampled.)

## Seeds provided
`al_seed_near_mg.xyz` — the actual near-Mg geometries (anion ~2.5-5.5 A) my MLFF-MD visited. Perturb / run
short AIMD around these and DFT-label.

## Acceptance / loop
Label → push `near_mg_bare_*_labeled.xyz` to `mlff/incoming/` → I retrain → bare interface runs stable to
ns (matches poly) → matched ns comparison + enables the reactive deposition/SEI-growth (T17 full).
