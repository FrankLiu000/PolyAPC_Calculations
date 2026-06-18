#!/usr/bin/env python3
"""build_mlff_dataset.py — subsample CP2K AIMD *-pos-1.xyz into an extended-XYZ
training-set SCAFFOLD for an MLFF (energies only; FORCES PENDING via DFT single-points).

CP2K pos-xyz comment line carries the energy:  'i = N, time = T, E = <Ha>'.
We convert to eV and write extended-XYZ with a Lattice (triclinic hexagonal cell).
Force labels are NOT in these files (no &PRINT FORCES was set) -> the produced
.xyz has positions+energy only; a follow-up DFT single-point pass must add forces
before this is a usable MLFF training set. This script exists to (a) quantify/curate
the available configurations and (b) be the input list for the force-labeling pass.

Usage: build_mlff_dataset.py <out.xyz> <stride> <traj1:Natoms:Lattice> [traj2:...] ...
  Lattice as 9 space-free comma list 'ax,ay,az,bx,by,bz,cx,cy,cz'
"""
import sys

HA2EV = 27.211386245988


def parse_E(comment):
    # 'i = 0, time = 0.0, E = -4590.0149'
    for tok in comment.replace(",", " ").split():
        pass
    parts = comment.split("E")
    try:
        return float(parts[-1].split("=")[-1]) * HA2EV
    except (ValueError, IndexError):
        return None


def harvest(traj, nat, lattice, stride, fout, sys_label):
    kept = 0
    with open(traj) as fh:
        fi = 0
        while True:
            h = fh.readline()
            if not h:
                break
            try:
                n = int(h.split()[0])
            except (ValueError, IndexError):
                break
            comment = fh.readline()
            lines = [fh.readline() for _ in range(n)]
            if any(not x for x in lines):
                break
            if n != nat:
                fi += 1
                continue
            if fi % stride == 0:
                E = parse_E(comment)
                if E is not None:
                    fout.write("%d\n" % n)
                    fout.write('Lattice="%s" Properties=species:S:1:pos:R:3 '
                               'energy=%.6f config_type=%s pbc="T T T"\n'
                               % (" ".join(lattice.split(",")), E, sys_label))
                    for ln in lines:
                        p = ln.split()
                        fout.write("%-2s %s %s %s\n" % (p[0], p[1], p[2], p[3]))
                    kept += 1
            fi += 1
    return kept


if __name__ == "__main__":
    out, stride = sys.argv[1], int(sys.argv[2])
    total = 0
    with open(out, "w") as fo:
        for spec in sys.argv[3:]:
            traj, nat, lat = spec.split(":")
            label = traj.split("/")[-1].replace("-pos-1.xyz", "")
            k = harvest(traj, int(nat), lat, stride, fo, label)
            print("  %-28s N=%s  kept %d frames (stride %d)" % (label, nat, k, stride))
            total += k
    print("  TOTAL %d frames -> %s  (ENERGY ONLY; forces pending DFT single-points)" % (total, out))
