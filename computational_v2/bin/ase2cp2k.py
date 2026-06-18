#!/usr/bin/env python3
"""ase2cp2k.py — emit CP2K &CELL and &COORD blocks from a structure file.

Usage:
    python ase2cp2k.py common/struct/MgF2.cif        # periodic: &CELL + &COORD
    python ase2cp2k.py common/struct/THF.xyz --box 20 # molecular: cubic box

Prints the blocks to stdout so they can be pasted/included into a CP2K .inp
(the templates in P0c_periodic/inp & P0d_interface/inp reference these by an
@INCLUDE or by hand). Reads anything ASE understands (.xyz, .cif, .pdb).
"""
from __future__ import annotations
import argparse
import sys

from ase.io import read


def coord_block(atoms):
    out = ["    &COORD"]
    for sym, (x, y, z) in zip(atoms.get_chemical_symbols(), atoms.get_positions()):
        out.append(f"      {sym:2s} {x:14.6f} {y:14.6f} {z:14.6f}")
    out.append("    &END COORD")
    return "\n".join(out)


def cell_block(atoms, box=None):
    out = ["    &CELL"]
    if atoms.cell.rank == 3 and atoms.get_volume() > 1e-3 and box is None:
        a, b, c = atoms.cell[:]
        out.append(f"      A {a[0]:12.6f} {a[1]:12.6f} {a[2]:12.6f}")
        out.append(f"      B {b[0]:12.6f} {b[1]:12.6f} {b[2]:12.6f}")
        out.append(f"      C {c[0]:12.6f} {c[1]:12.6f} {c[2]:12.6f}")
        out.append("      PERIODIC XYZ")
    else:
        L = box or 20.0
        out.append(f"      ABC {L:.3f} {L:.3f} {L:.3f}")
        out.append("      PERIODIC NONE")   # isolated molecule (use with Poisson MT/wavelet)
    out.append("    &END CELL")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("structure")
    ap.add_argument("--box", type=float, default=None,
                    help="cubic box edge (Angstrom) for a non-periodic molecule")
    args = ap.parse_args(argv)
    atoms = read(args.structure)
    print(cell_block(atoms, box=args.box))
    print(coord_block(atoms))
    return 0


if __name__ == "__main__":
    sys.exit(main())
