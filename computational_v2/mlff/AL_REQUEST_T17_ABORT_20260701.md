# AL REQUEST (GPU→CPU): DFT-label guarded T17 bare near-contact abort frames

Date: 2026-07-01  
Priority: high for T17 publication-level MLFF-MD stability and DFT validation  
Source commit: `06c2b66` plus follow-up request files

## CPU scheduling note

Submitted on the CPU node as Slurm job `1741` (`t17_abort_label`), but deliberately placed **after** the
T23 AIMD publication-gate queue:

```text
scontrol update JobId=1741 Dependency=afterany:1737
```

where `1737` is `t23_post`, which itself depends on the active/pending T23 release and hold-release jobs.
This keeps T23 AIMD as the CPU priority; the T17 labels start only after the T23 chain has finished and
post-processing has run.

## Why

The guarded T17 neutral bare replicate
`bare_neutral_seed2026070101_500ps` reached the near-contact region and then correctly aborted at the
first force-cap event:

```text
abort step = 8450
t = 4.225 ps
reason = force-cap events=1
```

This means the current MLFF still has a near-contact extrapolation gap. These frames are not production
evidence, but they are exactly the active-learning payload needed before another 500 ps / ns-scale T17
production attempt. The scientific target is to make the bare run stable in the Al-anion approach zone,
then compare matched bare vs poly without relying on force caps.

## Input frames

```text
computational_v2/mlff/incoming/t17_bare_seed2026070101_abort_unlabeled.xyz
frames = 9
atoms/frame = 172
charge = 0
lattice CSV = 12.836,0.0,0.0,6.418,11.116,0.0,0.0,0.0,55.0
fixed slab convention = first 64 Mg atoms, forces must be masked to 0
```

Geometry coverage:

| frame | t / ps | Al-slab min / A | Mg <3.2 A | Al-Cl <2.8 A | shortest Al-Cl / A | 2nd Al-Cl / A |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 3.500 | 5.477 | 0 | 2 | 2.194 | 2.349 |
| 1 | 3.600 | 5.424 | 0 | 2 | 2.280 | 2.290 |
| 2 | 3.700 | 5.157 | 0 | 2 | 2.155 | 2.398 |
| 3 | 3.800 | 4.894 | 0 | 2 | 2.170 | 2.294 |
| 4 | 3.900 | 4.673 | 0 | 2 | 2.253 | 2.263 |
| 5 | 4.000 | 4.348 | 0 | 2 | 2.114 | 2.219 |
| 6 | 4.100 | 4.126 | 0 | 2 | 2.180 | 2.250 |
| 7 | 4.200 | 3.744 | 0 | 2 | 2.283 | 2.331 |
| 8 | 4.225 | 3.818 | 0 | 2 | 2.429 | 2.565 |

Interpretation: these are intact-anion near-contact frames approaching the Mg electron-transfer front, not
Al0/Mg-Al deposition frames yet. They are needed to harden the MLFF before production; DFT/AIMD remains
responsible for oxidation-state evidence.

## Requested CPU/DFT task

Run CP2K PBE-D3 ENERGY_FORCE single-points at the existing MLFF labeling level:

- `DZVP-MOLOPT-SR-GTH` / `GTH-PBE`;
- `CUTOFF 400`, `REL_CUTOFF 50`;
- Fermi smearing for the metal slab;
- charge `0`;
- slab forces masked: atoms `0..63` / first 64 atoms;
- output extxyz with `energy`, `forces`, and `scf_converged` tags.

Suggested command after pulling this branch on the CPU node:

```bash
cd /CH/<PolyAPC_worktree>/computational_v2/P0d_interface/inp
cp label_sp_template.inp /tmp/t17_abort_label_20260701/
cd /tmp/t17_abort_label_20260701

export CP2K_BIN=/CH/cp2k-2025.1/exe/local/cp2k.psmp
export CP2K_DATA_DIR=/CH/cp2k-2025.1/data
export SLURM_NTASKS=${SLURM_NTASKS:-64}

python3 /CH/<PolyAPC_worktree>/computational_v2/bin/label_forces.py \
  /CH/<PolyAPC_worktree>/computational_v2/mlff/incoming/t17_bare_seed2026070101_abort_unlabeled.xyz \
  172 0 12.836,0.0,0.0,6.418,11.116,0.0,0.0,0.0,55.0 \
  /CH/<PolyAPC_worktree>/computational_v2/mlff/incoming/t17_bare_seed2026070101_abort_labeled.xyz \
  9 64
```

If the CPU worktree is not under `/CH/<PolyAPC_worktree>`, first locate it with `find /CH -maxdepth 3 -type d -name PolyAPC_Calculations`.

## Return artifacts

Commit or copy back:

```text
computational_v2/mlff/incoming/t17_bare_seed2026070101_abort_labeled.xyz
computational_v2/mlff/incoming/t17_bare_seed2026070101_abort_LABEL_REPORT.md
```

The report should include:

- number of frames labelled;
- SCF convergence per frame;
- max electrolyte force per frame and any free-region net-force warnings;
- DFT vs current-MLFF force MAE on these 9 frames if convenient;
- optional but useful: Mulliken/Hirshfeld/Bader qAl, Al-slab min, Al-Cl distances.

## How GPU will use it

1. Add labelled frames to the T16/T17 dataset via `computational_v2/mlff/v3/assemble_dataset.py`.
2. Retrain a new model, keeping a held-out subset of these near-contact frames.
3. Require DFT force/energy MAE on this near-contact abort set before any renewed 500 ps / ns T17 production.
4. Re-run matched bare vs poly only after cap=0/no-abort short probes pass.
