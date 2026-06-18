#!/usr/bin/env python3
"""prep_split.py — validate dataset_train.xyz (ASE) and carve an independent held-out TEST set.

MACE's own --valid_fraction splits train_file into train+valid (used for early-stopping /
model selection). For an UNBIASED final force/energy RMSE we additionally hold out a TEST set
that MACE never sees. Output:
    mlff_train.xyz   -> given to mace_run_train (it further splits train/valid internally)
    mlff_test.xyz    -> evaluated post-hoc by eval_test.py (model never trained on it)

Caveat reported in TRAIN_REPORT: consecutive AIMD frames are time-correlated, so a random test
split is mildly optimistic (test frames sit near train frames in time). Stated honestly.

Usage: python prep_split.py [src.xyz] [test_fraction]
"""
import sys
import numpy as np
from ase.io import read, write

src = sys.argv[1] if len(sys.argv) > 1 else "dataset_train.xyz"
test_frac = float(sys.argv[2]) if len(sys.argv) > 2 else 0.10
prefix = sys.argv[3] if len(sys.argv) > 3 else "mlff"   # outputs <prefix>_train.xyz / <prefix>_test.xyz
SEED = 20260616

frames = read(src, ":")
n = len(frames)
print(f"loaded {n} frames from {src}")

# --- validation: energy + forces present, finite, lattice/pbc sane ---
nat = len(frames[0])
fmax_all, e_all, bad = [], [], 0
for i, at in enumerate(frames):
    e = at.get_potential_energy()          # extxyz energy=
    f = at.get_forces()                     # extxyz forces=
    if not (np.isfinite(e) and np.isfinite(f).all()):
        bad += 1
    if len(at) != nat:
        print(f"  !! frame {i} has {len(at)} atoms (expected {nat})")
    if not at.pbc.all():
        print(f"  !! frame {i} pbc not all-True: {at.pbc}")
    e_all.append(e)
    fmax_all.append(np.linalg.norm(f, axis=1).max())
e_all = np.array(e_all); fmax_all = np.array(fmax_all)
print(f"natoms/frame={nat}  non-finite frames={bad}")
print(f"energy: min={e_all.min():.3f} max={e_all.max():.3f} eV "
      f"(spread {1000*e_all.std()/nat:.2f} meV/atom, range {1000*(e_all.max()-e_all.min())/nat:.1f} meV/atom)")
print(f"per-frame |F|max: median={np.median(fmax_all):.2f} p95={np.percentile(fmax_all,95):.2f} "
      f"max={fmax_all.max():.2f} eV/A")
sym = frames[0].get_chemical_symbols()
from collections import Counter
print("composition:", dict(sorted(Counter(sym).items())))

# --- deterministic shuffle split ---
rng = np.random.default_rng(SEED)
idx = rng.permutation(n)
n_test = max(1, int(round(test_frac * n)))
test_idx = sorted(idx[:n_test].tolist())
train_idx = sorted(idx[n_test:].tolist())
write(f"{prefix}_train.xyz", [frames[i] for i in train_idx])
write(f"{prefix}_test.xyz",  [frames[i] for i in test_idx])
print(f"\nsplit -> {prefix}_train.xyz ({len(train_idx)})  {prefix}_test.xyz ({len(test_idx)})  seed={SEED}")
print(f"test |F|max range {fmax_all[test_idx].min():.2f}-{fmax_all[test_idx].max():.2f} eV/A "
      f"(covers force regime: {'YES' if fmax_all[test_idx].max() > np.percentile(fmax_all,90) else 'narrow'})")
