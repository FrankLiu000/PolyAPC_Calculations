# T17 — reactive interface MLFF-MD (poly interface done)
*GPU node. Uses the T16 broad model (`models/apc_v3_broad.model`, force MAE 30.7 meV/Å).*

## The point
The **poly Mg(0001)|electrolyte interface** — infeasible in classical GROMACS (the percolating
gel breaks the `mshift` molecule-unwrap) — **runs cleanly with the MLFF**, because MACE is a
geometry-based neighbour graph with no molecule-unwrapping step. EPYC's T10 poly cell (276 atoms:
64-Mg slab + cation + [Ph₂AlCl₂]⁻ anion + THF + 1 POSS cage) is finite and in-distribution for T16.

## Method
ASE + MACE (`interface_mlff_md.py`), rigid 64-Mg slab (forces DFT-masked), NVT Langevin 300 K, 1 fs,
from EPYC's equilibrated T10 frame. Bare and poly run matched. Tracked: Al-anion height above slab,
Al–slab distance, anion Cl/O coordination, Al–Si(POSS) distance.

## Result — the network sequesters the Al-anion AT THE INTERFACE
| | bare | poly |
|---|---|---|
| Al-anion height above slab | **4.5 ± 0.2 Å** | **8.2 ± 1.0 Å** |
| Al–slab distance | 5.2 Å | 10.0 Å |
| run length (stable) | ~5 ps (then NaN, below) | **full 50 ps, stable** |

**The POSS network holds the reducible Al-anion ~2× further from the electrode (8.2 vs 4.5 Å).**
This is the **interface-level** confirmation of the sequestration thesis — complementing the bulk
result (T5: anion 2× more network-associated + 4.2× slower) and EPYC's T10 AIMD (poly anion
network-sequestered, ~9.5 Å). `fig_t17_poly_interface.png`.

## Honest caveats
- **poly leg is robust** (in-distribution, 50 ps stable, energy steady, anion intact).
- **bare leg is extrapolation-limited:** the bare anion approached and sat *stably* at 4.5 Å for ~5 ps,
  then the model NaN'd (6.8 ps) — the bare near-surface region (<~5 Å) is beyond the T10 AIMD's
  ~9.5 Å sampling, so it lacks DFT labels. The close-approach *distance* is therefore uncertain; what
  is robust is the **contrast** (bare anion moves toward the front, poly anion is held back).
- **Fix = the AL loop:** the blow-up frames are extracted to **`al_queue_bare_t17.xyz`** (8 near-approach
  configs, Al height ~4–5 Å) for EPYC to DFT-label → retrain → stable bare near-surface. This is the
  loop working as designed (uncertainty → label → harden).
- This is a reactive-PES surrogate at a fixed/neutral slab; true plating overpotential not applied.

## Provenance
`computational_v2/mlff/v3/`: `interface_mlff_md.py`, `t17/{bare,poly}_mlff_cv.csv`, model
`models/apc_v3_broad.model`. Outputs here + `al_queue_bare_t17.xyz`. T16 validation `v3/mlff_validation.csv`.
