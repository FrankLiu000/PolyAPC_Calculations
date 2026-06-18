#!/usr/bin/env python3
"""add_pbc_extxyz.py <in.xyz> [out.extxyz] — stamp the interface-cell PBC into a CP2K
xyz trajectory by rewriting every comment line in extended-XYZ form:
  Lattice="12.836 0 0 6.418 11.116 0 0 0 55" Properties=species:S:1:pos:R:3 i=.. time=.. E=..
Cell = the P0d interface cell (triclinic xy, c=55 A), identical for bare/poly/bare_r2.
Tolerates a truncated final frame (skipped). Default output: <in stem>.extxyz
NEVER run in-place on a trajectory CP2K still has open (bare_r2 while job 1242 runs).
"""
import re, sys, os

LATTICE = 'Lattice="12.836 0.0 0.0 6.418 11.116 0.0 0.0 0.0 55.0"'
PROPS = 'Properties=species:S:1:pos:R:3 pbc="T T T"'

def main():
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".extxyz"
    nfr = 0
    with open(src) as f, open(dst, "w") as o:
        while True:
            head = f.readline()
            if not head.strip():
                break
            nat = int(head.split()[0])
            comment = f.readline()
            body = [f.readline() for _ in range(nat)]
            if not body[-1].strip():  # truncated final frame
                break
            # CP2K comment: " i =  N, time =  T, E =  X" -> compact extxyz keys
            kv = dict(re.findall(r"(\w+)\s*=\s*([-\d.Ee+]+)", comment))
            extra = " ".join("%s=%s" % (k, v) for k, v in kv.items())
            o.write(head)
            o.write("%s %s %s\n" % (LATTICE, PROPS, extra))
            o.writelines(body)
            nfr += 1
    print("%s -> %s  (%d frames, PBC stamped)" % (src, dst, nfr))

if __name__ == "__main__":
    main()
