# T16 / T17 — reactive-MLFF scaffold (GPU node, v3 interface-composition)
*Built ready-to-run while BLOCKED on EPYC's labels. Nothing here trains until the data lands.*

## Goal (the v3 DoD this serves)
A **reactive** machine-learning force field that reaches the scales single-trajectory AIMD cannot, to
**reproduce the ToF-SIMS result**: poly builds a **Si-rich, Al-poor, surface-confined** SEI (Al ions ×0.02–0.5,
Al depth 350→92 nm) by **suppressing Al-anion reduction / Al co-deposition** at the Mg anode, while bare
co-deposits metallic/alloyed Al⁰. T16 = train+validate the MLFF; T17 = run the large-cell reactive interface
(bare vs poly) and quantify Al-deposition + SEI composition-vs-depth.

## Why this is a NEW model (not the v2 one)
The v2 MLFF (`computational_v2/mlff/apc_{bare,poly}.model`) is **force-only, fixed-electrode, NON-reactive** —
valid for solvation/transport/desolvation, explicitly NOT electron-transfer/plating. T17 needs **reactive**
chemistry (Al-anion reductive decomposition → Al⁰/alloy, SEI formation), which requires **energy training**
(`EWEIGHT>0`) on **reactive DFT frames** that sample bond-breaking and Al deposition. Hence a fresh fine-tune
on EPYC's T10/T4/T7/T1 labels.

## Dependency graph (what unblocks what)
```
EPYC T1  (clusters, single-points) ─┐
EPYC T4  (Mg-Al alloy/co-deposition)─┤
EPYC T7  (SEI phases MgO/MgCl2/SiO2/Al/Al2O3/Mg17Al12)─┤→ [T16 assemble→train→validate] →[T17 produce→analyze]
EPYC T10 (REACTIVE interface AIMD, real cation+Al-anion, bare&poly, ±bias) ─┘     ↑                      │
        ^                                                                          └── AL loop (high-σ ───┘
        └────────────────────── EPYC labels the AL queue ─────────────────────────────  frames → EPYC)
```
**Critical path = EPYC T10** (reactive interface AIMD with the real Al-anion). T4/T7/T1 broaden coverage.

## Files (this dir)
| file | role | status |
|---|---|---|
| `DATASET_SPEC.md` | **the EPYC interface** — exact frames/format/masking/provenance EPYC must push | ready |
| `assemble_dataset.py` | ingest EPYC xyz → masked, gated, deduped train/val/test (ext-xyz) | ready |
| `train_reactive.sh` | MACE-MP fine-tune recipe (energy+forces, reactive, broader chemistry) | ready |
| `validate_reactive.py` | force/E MAE vs held-out DFT (target ≲50 meV/Å) + "reproduce T10" check | ready |
| `run_t17.py` | large-cell reactive interface MD (bare vs poly, plating conditions) | ready |
| `analyze_t17.py` | **the DoD** — Al-deposition count + SEI composition-vs-depth vs ToF-SIMS | ready |
| `al_loop.sh` | committee σ_F → AL queue for EPYC → retrain (wraps v2 `committee_uncertainty.py`) | ready |

## Execution order (when data lands)
1. EPYC pushes labeled xyz per `DATASET_SPEC.md` → `incoming/`.
2. `python assemble_dataset.py incoming/ data/` → `data/{train,val,test}.xyz` (+ gate report).
3. `EWEIGHT=1 ./train_reactive.sh` (smoke first: `EPOCHS=2 NAME=t16_smoke`).
4. `python validate_reactive.py models/t16.model data/test.xyz` → MAE + parity; must reproduce a T10 frame.
5. If σ_F high in T17 → `./al_loop.sh` writes `al_queue_*.xyz` for EPYC → relabel → re-assemble → retrain.
6. `python run_t17.py models/t16.model <bare_start.xyz> ... ` and `<poly_start.xyz>` → trajectories.
7. `python analyze_t17.py bare_traj.xyz poly_traj.xyz` → Al-deposition + depth profile → match ToF-SIMS.

## Start configs for T17 (note the poly advantage)
- **bare:** the T5 bare interface (`storyT5/bare/`, equilibrated Mg(0001)|electrolyte) converts directly to a
  T17 start (`gmx trjconv ... -o start.gro` → ASE → xyz). Reuse the large cell already built.
- **poly:** the classical T5 poly interface was *infeasible* (GROMACS `mshift` can't unwrap the percolating
  network). **The MLFF route does not have this limitation** — MACE evaluates per-interaction with PBC and
  never needs to make NET1 whole, so a poly Mg(0001)|gel interface **can** be run here. Build the poly start
  by stacking the slab on the wrapped poly box (`-pbc atom`, NET1 stays compact) and feed it straight to
  `run_t17.py`. This is a real reason the reactive-MLFF is the right tool for the poly interface.

## Honest scope (carry into the report)
- A short-range MLFF has **no explicit electrons / electrode potential**; it models the **reactive PES** that
  EPYC's DFT samples (Al-anion approach, Cl/Ph dissociation, Al onto the slab). True grand-canonical plating
  stays DFT/AIMD; T17 is a DFT-accurate **reactive-PES** surrogate at scale, spot-validated against DFT.
- Slab-bottom forces are a +z asymmetric-slab dipole artifact → **masked** (v2 lesson, `diagnose_forces.py` gate).
- Energies must be **single-point** (not loose AIMD-trajectory energies) or energy training corrupts (v2 lesson).
- Everything is **bare-vs-poly matched** + reports uncertainties; MLFF claims always carry a DFT cross-check.

*Env: `/lyz/Claude_workplace/polyAPC/.mlff_venv` (mace 0.3.16, torch 2.6+cu124, ASE 3.28). Always
`export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. Hold local until origin/computational-v3-interface.*
