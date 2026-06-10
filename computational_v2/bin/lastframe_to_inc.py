#!/usr/bin/env python3
"""lastframe_to_inc.py <traj.xyz> <out.coord.inc> — write the LAST frame of an xyz
trajectory as a CP2K &CELL+&COORD include (the interface cell). Used to hand a
GEO_OPT-relaxed geometry to the production MD as a clean starting structure."""
import sys

CELL = ("    &CELL\n      A   12.836    0.000    0.000\n"
        "      B    6.418   11.116    0.000\n      C    0.000    0.000   55.000\n"
        "      PERIODIC XYZ\n    &END CELL\n")

def main():
    src, out = sys.argv[1], sys.argv[2]
    lines = open(src).readlines()
    nat = int(lines[0].split()[0])
    blk = nat + 2
    nfr = len(lines) // blk
    last = lines[(nfr - 1) * blk:nfr * blk]
    body = last[2:2 + nat]
    with open(out, "w") as f:
        f.write(CELL)
        f.write("    &COORD\n")
        for l in body:
            t = l.split()
            f.write("      %-2s %14.6f %14.6f %14.6f\n"
                    % (t[0], float(t[1]), float(t[2]), float(t[3])))
        f.write("    &END COORD\n")
    print("lastframe_to_inc: %s frame %d -> %s (%d atoms)" % (src, nfr - 1, out, nat))

if __name__ == "__main__":
    main()
