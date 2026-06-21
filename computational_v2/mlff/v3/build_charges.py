#!/usr/bin/env python3
"""Build a per-atom FF partial-charge array (for external-field MLFF-MD, F_z=q*E)
matching a t17 interface start.xyz atom order. First NSLAB atoms = frozen electrode
(charge 0). Remaining atoms = molecules (cation MGC [Mg2Cl3(THF)6]+, anion ANI
Ph2AlCl2-, THF, POSS/NET1, TMS) assigned in order from their GROMACS .itp [atoms].
Greedy longest-first template match + total-charge verification.

usage: build_charges.py <start.xyz> <out_charges.npy> [NSLAB=64]
"""
import sys, glob, numpy as np
from ase.io import read

start, out = sys.argv[1], sys.argv[2]
NSLAB = int(sys.argv[3]) if len(sys.argv) > 3 else 64
ITPDIR = "/lyz/Claude_workplace/polyAPC/mols"
POSS_ITPS = ["/lyz/Claude_workplace/polyAPC/poss16/cured.itp",
             "/lyz/Claude_workplace/polyAPC/poss8/cured.itp"]

# opls atom-type prefix -> element (order matters: Cl before C, Si before S)
def type2elem(t):
    t = t.replace("opls_", "").upper()
    for pre, el in [("MG","Mg"),("CL","Cl"),("AL","Al"),("SI","Si"),("ST","Si"),
                    ("S","Si"),("OW","O"),("OS","O"),("O","O"),("N","N"),("H","H"),("C","C")]:
        if t.startswith(pre): return el
    raise ValueError(f"unknown opls type {t}")

def parse_itp(path):
    """return (elements[list], charges[np.array]) for the molecule's [atoms]."""
    els, qs = [], []
    inatoms = False
    for line in open(path):
        s = line.split(";")[0].strip()
        if s.startswith("[") :
            inatoms = ("atoms" in s.lower()); continue
        if not inatoms or not s: continue
        c = s.split()
        if len(c) < 7 or not c[0].isdigit(): continue
        els.append(type2elem(c[1])); qs.append(float(c[6]))
    return els, np.array(qs)

# molecule templates (name -> (elements, charges)); longest first for greedy match
templates = {}
cands = [(nm, f"{ITPDIR}/{nm}.itp") for nm in ["MGC", "ANI", "TMS", "THF", "POS"]]
cands += [("NET1_"+p.split('/')[-2], p) for p in POSS_ITPS]
for nm, p in cands:
    if not glob.glob(p): continue
    try:
        els, qs = parse_itp(p)
        if els: templates[nm] = (els, qs)
    except Exception as e:
        print(f"  (skip template {nm}: {e})")
order = sorted(templates, key=lambda k: -len(templates[k][0]))  # longest first

at = read(start)
sym = list(at.get_chemical_symbols())
N = len(sym)
q = np.zeros(N)
q[:NSLAB] = 0.0  # frozen electrode
i = NSLAB
log = []; neutral = 0
while i < N:
    matched = None
    for nm in order:
        els, qs = templates[nm]
        L = len(els)
        if i + L <= N and sym[i:i+L] == els:
            q[i:i+L] = qs; matched = (nm, L); i += L; break
    if matched is None:
        # unmatched = neutral network/solvent (POSS/TMS/free-THF, net 0) -> q=0, advance 1
        q[i] = 0.0; neutral += 1; i += 1
    else:
        log.append(matched[0])

print(f"{start}: N={N} slab={NSLAB} matched={ {m:log.count(m) for m in set(log)} } neutral_atoms={neutral}")
print(f"  total charge = {q.sum():+.4f} (should be ~0) | non-slab charge = {q[NSLAB:].sum():+.4f}")
np.save(out, q)
print(f"  saved {out}")
