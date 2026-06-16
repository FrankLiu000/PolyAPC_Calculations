#!/usr/bin/env python3
"""select_md_start.py — pick a clean, intact-anion, equilibrium start frame for MLFF-MD.

Guards against the master-report sec 3b artifact (a corrupted cation start drove the
spurious chloride abstraction). Requirements for a good start:
  * both anion Al-Cl bonds intact: 2.0-2.6 A (correct triclinic min-image via ASE mic)
  * cation [Mg2(mu-Cl)3] core intact: each cation Mg within 2.9 A of >=2 bridging Cl
  * anion segregated from the slab front (Al-slab min >~6 A) = the converged AIMD basin
Among qualifying frames, pick the one closest to the AIMD-converged Al-slab ~9 A.
Writes md_start.xyz.
"""
import sys
import numpy as np
from ase.io import read, write

src = sys.argv[1] if len(sys.argv) > 1 else "dataset_train.xyz"
frames = read(src, ":")
best = None
for k, at in enumerate(frames):
    sym = np.array(at.get_chemical_symbols())
    i_Al = int(np.where(sym == "Al")[0][0])
    cl = np.where(sym == "Cl")[0]
    mg = np.where(sym == "Mg")[0]
    # mic distances Al->Cl
    dAlCl = np.array([at.get_distance(i_Al, int(c), mic=True) for c in cl])
    order = np.argsort(dAlCl)
    anion_cl = cl[order[:2]]; d_anion = dAlCl[order[:2]]
    if not (d_anion.max() < 2.6 and d_anion.min() > 2.0):
        continue                               # anion not intact -> skip (abstraction guard)
    cation_cl = cl[order[2:]]                  # 3 bridging mu-Cl
    # slab = 64 Mg with lowest z; cation Mg = 2 Mg nearest the bridging Cl
    z = at.get_positions()[mg, 2]
    # cation Mg: closest to bridging Cl
    dmgcl = np.array([min(at.get_distance(int(m), int(c), mic=True) for c in cation_cl) for m in mg])
    cation_mg = mg[np.argsort(dmgcl)[:2]]
    slab_mg = np.array([m for m in mg if m not in cation_mg])
    # cation core intact: each cation Mg bonded to >=2 bridging Cl (<2.9 A)
    intact = all(sum(at.get_distance(int(m), int(c), mic=True) < 2.9 for c in cation_cl) >= 2
                 for m in cation_mg)
    if not intact:
        continue
    al_slab = min(at.get_distance(i_Al, int(m), mic=True) for m in slab_mg)
    if al_slab < 6.0:
        continue                               # too close to front (not the equilibrium basin)
    score = abs(al_slab - 9.0)                 # prefer the AIMD-converged ~9 A
    if best is None or score < best[0]:
        best = (score, k, d_anion.copy(), al_slab)

if best is None:
    print("NO qualifying clean frame found"); sys.exit(1)
score, k, d_anion, al_slab = best
write("md_start.xyz", frames[k])
print(f"selected frame {k}/{len(frames)}: Al-Cl={d_anion[0]:.2f}/{d_anion[1]:.2f} A, "
      f"Al-slab(min)={al_slab:.2f} A -> md_start.xyz")
