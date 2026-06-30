#!/usr/bin/env python3
"""Fixed-face (faceA=lower inner, faceB=upper inner) near-surface anion+cation density
under +0.3V/nm field, for bare AND poly, in two windows (full 50-200ns, tail 130-200ns).
Unlike twoface's poly RICH/POOR (which chases the fluctuating network), this uses FIXED
faces so the trend is interpretable. Answers: does poly's cathode (faceB) accumulate like bare's?"""
import sys, glob, os, numpy as np, MDAnalysis as mda
ST="/lyz/Claude_workplace/polyAPC/storyT5"
def fixed_face(sysdir, t0):
    base=os.path.join(ST,"sym",sysdir,"field.xtc")
    parts=sorted(glob.glob(base.replace('.xtc','.part*.xtc')))
    xs=[x for x in [base]+parts if os.path.exists(x)]
    u=mda.Universe(os.path.join(ST,"sym",sysdir,"em3dc.gro"), xs)
    slab=u.select_atoms("resname MGE"); anion=u.select_atoms("resname ANI"); cation=u.select_atoms("resname MGC")
    z=np.sort(slab.positions[:,2]/10.0); gaps=np.where(np.diff(z)>1.0)[0]
    s1max=z[:gaps[0]+1].max(); s2min=z[gaps[0]+1:].min()  # lower face top, upper face bottom
    area=u.dimensions[0]*u.dimensions[1]/100.0
    aA=aB=cA=cB=n=0
    for ts in u.trajectory:
        if ts.time/1000.0 < t0: continue
        az=anion.positions[:,2]/10.0; cz=cation.positions[:,2]/10.0
        aA += ((az>s1max)&(az<s1max+0.6)).sum(); aB += ((az<s2min)&(az>s2min-0.6)).sum()
        cA += ((cz>s1max)&(cz<s1max+0.6)).sum(); cB += ((cz<s2min)&(cz>s2min-0.6)).sum()
        n+=1
    return aA/(area*n), aB/(area*n), cA/(area*n), cB/(area*n), n
for sysdir in ["bare_t21","poly_t21"]:
    for t0,win in [(50,"50-200ns"),(130,"130-200ns")]:
        aA,aB,cA,cB,n=fixed_face(sysdir,t0)
        print(f"{sysdir} {win}: anion faceA={aA:.4f} faceB(cathode)={aB:.4f} ratio={aB/max(aA,1e-9):.2f}x | cation A={cA:.4f} B={cB:.4f} ratio={cB/max(cA,1e-9):.2f}x  (nfr={n})")
