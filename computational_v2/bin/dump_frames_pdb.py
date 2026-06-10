#!/usr/bin/env python3
"""dump_frames_pdb.py <traj.xyz> <label> [out_dir] — write selected AIMD frames as PDB.

Frames: 0 ps (initial), 1, 2, 3, 4 ps, and the final frame (1 frame = 1 fs).
Cell -> CRYST1: a=b=12.836, c=55.0, alpha=beta=90, gamma=60 (hexagonal interface cell).
Residues (0-based atom indices, both interface systems):
  SLB 0..63 = Mg slab | MGC 64..146 = [Mg2Cl3(THF)6]+ | ANI 147..171 = [AlPh2Cl2]- (Al=147)
  NET 172.. = POSS/polyether network fragment (poly only)
"""
import sys, os
import numpy as np

sys.path.insert(0, '/CH/poly_v2/bin')
from analyze_interface_access import frames

PICKS_PS = [0, 1, 2, 3, 4]  # + final
CRYST = "CRYST1   12.836   12.836   55.000  90.00  90.00  60.00 P 1           1\n"

def resid(i):
    if i < 64: return "SLB", 1
    if i < 147: return "MGC", 2
    if i < 172: return "ANI", 3
    return "NET", 4

def write_pdb(path, syms, xyz, label, t_ps):
    with open(path, "w") as f:
        f.write("TITLE     %s interface AIMD t=%.3f ps (PBE-D3, NVT 300K)\n" % (label, t_ps))
        f.write(CRYST)
        counts = {}
        for i, (s, (x, y, z)) in enumerate(zip(syms, xyz)):
            rn, rs = resid(i)
            counts[(rs, s)] = counts.get((rs, s), 0) + 1
            name = ("%s%d" % (s, counts[(rs, s)]))[:4]
            f.write("HETATM%5d %-4s %3s A%4d    %8.3f%8.3f%8.3f  1.00  0.00          %2s\n"
                    % (i + 1, name, rn, rs, x, y, z, s.rjust(2)))
        f.write("END\n")

def main():
    traj, label = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else "/CH/poly_v2/results/structures/aimd_frames"
    os.makedirs(out, exist_ok=True)
    want = {p * 1000 for p in PICKS_PS}
    kept, last = {}, None
    for i, (syms, x) in enumerate(frames(traj)):
        if i in want:
            kept[i] = (syms, x.copy())
        last = (i, syms, x.copy())
    for i in sorted(kept):
        p = os.path.join(out, "%s_t%dps.pdb" % (label, i // 1000))
        write_pdb(p, *kept[i], label, i / 1000.0)
        print("wrote", p)
    i, syms, x = last
    p = os.path.join(out, "%s_final_t%.1fps.pdb" % (label, i / 1000.0))
    write_pdb(p, syms, x, label, i / 1000.0)
    print("wrote", p, "(final frame %d)" % i)

if __name__ == "__main__":
    main()
