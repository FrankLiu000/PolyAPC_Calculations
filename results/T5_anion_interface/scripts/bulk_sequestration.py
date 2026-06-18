#!/usr/bin/env python3
"""T5 (bulk route): how the cured network sequesters the Al-anion, measured in the
BULK gel where the percolating network is properly periodic (a free-surface slab
of the covalent network is infeasible in classical MD -- GROMACS mshift cannot
unwrap a percolating molecule). Quantifies, poly vs bare, the Al-anion's matrix
association and local crowding vs the Mg-cation, complementing the established
D(anion) 4.2x slowdown and de-pairing.

usage: bulk_sequestration.py <gro/tpr> <xtc> <label> <outdir> [stride]
"""
import sys, numpy as np
import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array, capped_distance

top,xtc,label,outdir = sys.argv[1:5]
stride = int(sys.argv[5]) if len(sys.argv)>5 else 200
import os; os.makedirs(outdir, exist_ok=True)
u = mda.Universe(top, xtc)
anion = u.select_atoms("resname ANI and name Al")
cation = u.select_atoms("resname MGC and name Mg1 Mg2")
net = u.select_atoms("resname NET1")
netO = u.select_atoms("resname NET1 and name O*")
haspoly = len(net) > 0
print(f"[{label}] anions={len(anion)} cations={len(cation)} network atoms={len(net)} netO={len(netO)} frames={len(u.trajectory)} stride={stride}")

def mind(sel, ref, box):
    if len(ref)==0: return None
    da = distance_array(sel.positions, ref.positions, box=box)
    return da.min(axis=1)/10.0   # nm

an_net=[]; ca_net=[]; an_netO=[]
contact_a=[]; contact_c=[]   # within 0.50 nm of any network atom
nfr=0
for ts in u.trajectory[::stride]:
    box=ts.dimensions
    if haspoly:
        da=mind(anion,net,box); dc=mind(cation,net,box); dao=mind(anion,netO,box)
        an_net.append(da); ca_net.append(dc); an_netO.append(dao)
        contact_a.append((da<0.50).mean()); contact_c.append((dc<0.50).mean())
    nfr+=1
out={"label":label,"frames":nfr}
if haspoly:
    an_net=np.concatenate(an_net); ca_net=np.concatenate(ca_net); an_netO=np.concatenate(an_netO)
    out.update(dict(
        anion_median_dist_to_network_nm=float(np.median(an_net)),
        cation_median_dist_to_network_nm=float(np.median(ca_net)),
        anion_median_dist_to_netO_nm=float(np.median(an_netO)),
        anion_frac_contact_network=float(np.mean(contact_a)),   # within 0.5 nm
        cation_frac_contact_network=float(np.mean(contact_c)),
        anion_frac_within_0p7=float((an_net<0.7).mean()),
        cation_frac_within_0p7=float((ca_net<0.7).mean()),
    ))
    print(f"[{label}] anion<->network: median {out['anion_median_dist_to_network_nm']:.3f} nm, "
          f"frac in contact(<0.5nm) {out['anion_frac_contact_network']:.3f}, frac<0.7nm {out['anion_frac_within_0p7']:.3f}")
    print(f"[{label}] cation<->network: median {out['cation_median_dist_to_network_nm']:.3f} nm, "
          f"frac in contact(<0.5nm) {out['cation_frac_contact_network']:.3f}")
    print(f"[{label}] anion<->ether/POSS-O: median {out['anion_median_dist_to_netO_nm']:.3f} nm")
else:
    print(f"[{label}] no network (bare reference) -- anion in free liquid")
import json
json.dump(out, open(f"{outdir}/bulk_{label}.json","w"), indent=2)
print(f"[{label}] wrote bulk_{label}.json")
