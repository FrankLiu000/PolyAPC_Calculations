# GPU handoff — reactive training frames (close the "is it reactive?" gap)

## Why
T16/T17's `apc_v3_broad` was trained + validated **only on intact-anion (non-reactive)
frames** (the T10 AIMD had no spontaneous reduction; the AL frames were near-surface but
intact). The T17 production runs sampled **no bond-breaking** (anion keeps both Cl; closest
approach 3.3 Å bare > alloying). So the "reactive MLFF" label was not yet earned.

## What's here
`reactive_bare_clstrip_labeled.xyz` — **11 DFT-labeled REACTIVE frames** = the surface
Cl-stripping reaction `[AlPh2Cl2]- + Mg(0001) -> AlPh2Cl + Cl*`, constructed in the **real
172-atom T10 bare cell** (from the closest-approach AL frame, anion-Al 4.26 A):
- 9 Cl-stripping path frames: **Al-Cl breaks 2.28 -> 3.21 A** while the stripped **Cl binds
  a surface Mg (Cl-Mg 3.67 -> 2.40 A)** — the SEI-forming bond-breaking step.
- 2 thermal-jitter frames (off-equilibrium diversity).
- (4 Al-approach/jitter frames were DROPPED — construction clashes, 75-134 eV/A.)

Format = identical to the AL queue: CP2K PBE-D3 single-point + forces, Gamma-point,
**slab-masked n_slab=64** (slab forces = 0.000 verified), `config_type=react_bare_*` tags,
172-atom cell, charge 0.

## How to use
1. **Add to the T16 training set** and retrain `apc_v3_broad` (these are the first
   bond-broken configs it will see).
2. **Validate on the reactive regime** — hold out a couple of the `clstrip_*` frames and
   report force/energy MAE on them (the current 30.7 meV/A is intact-anion only).
3. **Then re-run T17 with a cathodic drive** (charged slab / overpotential): the reactive
   model + driving force should show the **bare** anion Cl-stripping + Al depositing, while
   **poly** does not — the real reactive payoff (C1 DFT says bare is favorable: gateway
   -16.8 kcal/mol, surface strip +0.24 eV, alloying -4.44 eV).

## Honest caveat
These are **unrelaxed constructed-path** configs — the ~+5 eV rise along the path is
geometric strain, NOT the true barrier (the DFT reference barrier is in
`results/C1_TS_mechanism/`: surface strip +0.24 eV). They are **force/energy labels at
diverse reactive geometries** (correct for training), not a relaxed reaction profile.
Next increments (same recipe): full Al-Cl dissociation, the gateway Cl-transfer, multiple
surface sites, and relaxed NEB images once a reactive model exists to cheaply pre-relax them.
