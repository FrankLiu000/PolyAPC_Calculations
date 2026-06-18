#!/usr/bin/env python3
# T11: extract Al 2p / Si 2p core-level eigenvalues (initial-state, ~ -BE) from ORCA, compute chemical shifts.
import re,sys,csv
def last_orbital_block(path):
    txt=open(path).read()
    blocks=txt.split("ORBITAL ENERGIES")
    if len(blocks)<2: return None
    rows=[]
    for ln in blocks[-1].splitlines():
        m=re.match(r'\s*(\d+)\s+([\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s*$',ln)
        if m: rows.append((int(m.group(1)),float(m.group(2)),float(m.group(4))))  # idx,occ,E_eV
    return rows
def core2p(rows, lo, hi):
    # the 2p shell = the ~3 occupied orbitals with E in [lo,hi] eV
    cand=sorted([e for i,o,e in rows if lo<e<hi and o>1.5])
    if len(cand)<3: return None
    return sum(cand[:3])/3.0   # 3 lowest in window = the 2p triplet
mols={"AlH3":("Al",-95,-60),"AlF3":("Al",-95,-60),"AlOH3":("Al",-95,-60),
      "SiH4":("Si",-115,-90),"SiOH4":("Si",-115,-90)}
res={}
for m,(el,lo,hi) in mols.items():
    r=last_orbital_block("/CH/poly_v2/v3/t11_xps/%s.out"%m)
    if not r: print(m,"no block"); continue
    e2p=core2p(r,lo,hi); res[m]=(el,e2p)
    print("%-7s %s 2p eigenvalue = %8.2f eV  (~ -BE)"%(m,el,e2p))
# chemical shifts (BE = -eigenvalue): more oxidised -> more negative eig -> higher BE
print("\n=== Al 2p chemical shift (vs AlH3 low-oxidation) ; exp bare 70.9 -> poly 74.0 (D=3.1) ===")
if "AlH3" in res:
    base=res["AlH3"][1]
    for m in ["AlH3","AlOH3","AlF3"]:
        if m in res: print("  %-7s  BE(rel AlH3) = %+5.2f eV"%(m, -(res[m][1]-base)))
print("=== Si 2p chemical shift (vs SiH4 ~Si0) ; exp Si0 99.5 -> siloxane 101.7 (D=2.2) ===")
if "SiH4" in res:
    base=res["SiH4"][1]
    for m in ["SiH4","SiOH4"]:
        if m in res: print("  %-7s  BE(rel SiH4) = %+5.2f eV"%(m, -(res[m][1]-base)))
