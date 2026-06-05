#!/usr/bin/env python3
"""Contact-pairing time series from a solvation.py *_records.csv.

contact(frame) = fraction of Mg with n_anionCl >= 1 ; f = 1 - contact.
Block-averages over `block_ns` windows to expose drift vs. convergence.

usage: contact_timeseries.py <records.csv> <ns_per_frame> <block_ns> [label]
"""
import sys, csv
from collections import defaultdict

rec, nspf, block = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
label = sys.argv[4] if len(sys.argv) > 4 else rec

byframe = defaultdict(list)
with open(rec) as fh:
    for row in csv.DictReader(fh):
        byframe[int(row["frame"])].append(int(row["n_anionCl"]))

frames = sorted(byframe)
per_frame = {fr: sum(1 for x in byframe[fr] if x > 0) / len(byframe[fr]) for fr in frames}

blocks = defaultdict(list)
for fr in frames:
    t = (fr - 1) * nspf
    blocks[int(t // block)].append(per_frame[fr])

print("=== %s : contact-pairing vs time (block=%g ns) ===" % (label, block))
print("   window(ns)   contact%%   f      (nframes)")
for b in sorted(blocks):
    v = blocks[b]
    m = sum(v) / len(v)
    print("   %3d-%-4d    %5.1f     %.3f   (%d)" % (b * block, (b + 1) * block, 100 * m, 1 - m, len(v)))

allv = list(per_frame.values())
M = sum(allv) / len(allv)
print("   FULL 0-%-4g  %5.1f     %.3f   (%d)   <-- trajectory-average"
      % (frames[-1] * nspf, 100 * M, 1 - M, len(allv)))
