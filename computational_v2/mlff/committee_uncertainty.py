#!/usr/bin/env python3
"""committee_uncertainty.py — active-learning force-uncertainty (σ_F) from a model committee.

For each frame, evaluates every committee member and computes the per-atom force std across
members; σ_F(frame) = max over the ELECTROLYTE atoms (64..) of that per-atom std (slab is masked).
Low σ_F = in-distribution (members agree); high σ_F = extrapolation (members diverge) = queue for DFT.

Usage: python committee_uncertainty.py <frames.xyz> <m1.model> <m2.model> [...] [--thresh 0.15] [--queue al_queue.xyz]
Prints per-frame σ_F + a summary; with --queue, writes frames with σ_F>thresh (eV/Å) for DFT labeling.
"""
import sys
import numpy as np
from ase.io import read, write
from mace.calculators import MACECalculator

argv = sys.argv[1:]; opts = {}; pos = []
i = 0
while i < len(argv):
    if argv[i].startswith("--"):
        opts[argv[i]] = argv[i + 1]; i += 2
    else:
        pos.append(argv[i]); i += 1
frames_file, models = pos[0], pos[1:]
thresh = float(opts.get("--thresh", 0.15))      # eV/Å; >this = flag for labeling
queue = opts.get("--queue")
N_SLAB = 64

calcs = [MACECalculator(model_paths=[m], device="cuda", default_dtype="float32") for m in models]
frames = read(frames_file, ":")
print(f"committee of {len(calcs)} on {len(frames)} frames from {frames_file} (thresh {thresh*1000:.0f} meV/Å)")

sig_max, flagged = [], []
for i, at in enumerate(frames):
    F = []
    for c in calcs:
        a = at.copy(); a.calc = c; F.append(a.get_forces())
    F = np.array(F)                                  # (M, natom, 3)
    per_atom = np.sqrt((F.std(axis=0) ** 2).sum(axis=1))   # (natom,) force-std magnitude
    s = float(per_atom[N_SLAB:].max())               # electrolyte max σ_F
    sig_max.append(s)
    if s > thresh:
        flagged.append(at)
    if i % max(1, len(frames) // 10) == 0:
        print(f"  frame {i}: σ_F(max,electrolyte) = {s*1000:.0f} meV/Å")

sig_max = np.array(sig_max)
print(f"\nσ_F (max electrolyte) over {len(frames)} frames: "
      f"mean={sig_max.mean()*1000:.0f}  median={np.median(sig_max)*1000:.0f}  "
      f"p95={np.percentile(sig_max,95)*1000:.0f}  max={sig_max.max()*1000:.0f} meV/Å")
print(f"flagged (>{thresh*1000:.0f} meV/Å): {len(flagged)}/{len(frames)}")
if queue and flagged:
    write(queue, flagged)
    print(f"wrote {len(flagged)} frames -> {queue} (push to EPYC for DFT labeling)")
