#!/usr/bin/env python3
"""committee_uncertainty.py — active-learning force-uncertainty (σ_F) from a model committee.

For each frame, evaluates every committee member and computes the per-atom force std across
members; σ_F(frame) = max over the ELECTROLYTE atoms (64..) of that per-atom std (slab is masked).
Low σ_F = in-distribution (members agree); high σ_F = extrapolation (members diverge) = queue for DFT.

Usage: python committee_uncertainty.py <frames.xyz> <m1.model> <m2.model> [...]
         [--thresh 0.15] [--calib <indist.xyz>] [--queue al_queue.xyz]
Prints per-frame σ_F + a summary; with --queue, writes frames with σ_F>thresh (eV/Å) for DFT labeling.
--calib <indist.xyz>: self-calibrate the per-system threshold from an in-distribution reference set
  (thresh = mean + 5·std of its σ_F, capped below at --thresh) — robust to a system's intrinsic σ_F baseline.
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

def sigf(frames):
    """per-frame max electrolyte committee force-std (eV/Å)."""
    s = []
    for at in frames:
        F = []
        for c in calcs:
            a = at.copy(); a.calc = c; F.append(a.get_forces())
        per_atom = np.sqrt((np.array(F).std(axis=0) ** 2).sum(axis=1))   # (natom,)
        s.append(float(per_atom[N_SLAB:].max()))
    return np.array(s)

# self-calibrate threshold from an in-distribution reference (handles per-system σ_F baseline)
calib = opts.get("--calib")
if calib:
    cs = sigf(read(calib, ":"))
    thresh = max(thresh, float(cs.mean() + 5 * cs.std()))
    print(f"calibrated from {calib}: in-dist σ_F mean={cs.mean()*1000:.0f} std={cs.std()*1000:.0f} "
          f"max={cs.max()*1000:.0f} -> thresh={thresh*1000:.0f} meV/Å")

frames = read(frames_file, ":")
print(f"committee of {len(calcs)} on {len(frames)} frames from {frames_file} (thresh {thresh*1000:.0f} meV/Å)")
sig_max = sigf(frames)
flagged = [frames[i] for i in range(len(frames)) if sig_max[i] > thresh]
print(f"σ_F (max electrolyte) over {len(frames)} frames: "
      f"mean={sig_max.mean()*1000:.0f}  median={np.median(sig_max)*1000:.0f}  "
      f"p95={np.percentile(sig_max,95)*1000:.0f}  max={sig_max.max()*1000:.0f} meV/Å")
print(f"flagged (>{thresh*1000:.0f} meV/Å): {len(flagged)}/{len(frames)}")
if queue and flagged:
    write(queue, flagged)
    print(f"wrote {len(flagged)} frames -> {queue} (push to EPYC for DFT labeling)")
