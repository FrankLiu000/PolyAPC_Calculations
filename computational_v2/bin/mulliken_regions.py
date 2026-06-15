#!/usr/bin/env python3
"""mulliken_regions.py — per-block Mulliken net charge summed by interface region.

Parses CP2K 'Mulliken Population Analysis' blocks from a .out file and reports,
for each block (= each MD print step), the net charge summed over:
  slab Mg   = atoms 1..64   (1-indexed CP2K; the metal electrode / e- reservoir)
  cationMg  = atoms 65..66  ([Mg2Cl3] dimer core; drop from +2 = Mg2+ reduction)
  catLig    = atoms 67..147 (cation Cl/THF ligands)
  anion     = atoms 148..172 ([AlPh2Cl2]-; Al=148)

Robust to the surrounding MD/SCF output: only accumulates atom lines between a
'Mulliken Population Analysis' header and the FIRST following 'Total charge'.

Usage: python3 mulliken_regions.py <cp2k.out>
"""
import sys
import re

SLAB, CAT, LIG, AN = (1, 64), (65, 66), (67, 147), (148, 172)
atom_re = re.compile(r"^\s*(\d+)\s+[A-Z][a-z]?\s")


def regions(path):
    blocks = []
    active = False
    chg = {}
    with open(path) as fh:
        for ln in fh:
            if "Mulliken Population Analysis" in ln:
                active, chg = True, {}
                continue
            if active and "Total charge" in ln:
                s = lambda lo, hi: sum(chg.get(a, 0.0) for a in range(lo, hi + 1))
                blocks.append((s(*SLAB), s(*CAT), s(*LIG), s(*AN)))
                active = False
                continue
            if active:
                m = atom_re.match(ln)
                if m:
                    try:
                        chg[int(m.group(1))] = float(ln.split()[-1])
                    except ValueError:
                        pass
    return blocks


if __name__ == "__main__":
    b = regions(sys.argv[1])
    if not b:
        print("  (no complete Mulliken block yet)")
        sys.exit()
    print("  block   slab Mg   cationMg   catLig    anion   (net charge, e)")
    for i, (sl, ca, li, an) in enumerate(b, 1):
        flag = "  <-- cationMg dropped from +2 (REDUCTION)" if ca < 1.5 else ""
        print("  %4d   %+7.3f   %+7.3f   %+7.3f   %+7.3f%s" % (i, sl, ca, li, an, flag))
    sl0, ca0, _, an0 = b[0]
    sl1, ca1, _, an1 = b[-1]
    print("  --- drift block1->last: slab %+.3f | cationMg %+.3f | anion %+.3f"
          % (sl1 - sl0, ca1 - ca0, an1 - an0))
