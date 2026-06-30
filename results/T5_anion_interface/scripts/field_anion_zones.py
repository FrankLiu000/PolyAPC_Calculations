#!/usr/bin/env python3
"""Anion density in 3 zones (near-faceA, bulk mid-gap, near-faceB) under +0.3V/nm field,
bare vs poly (discard 50ns). Looking for poly-favorable evidence: does the network keep
anion in the bulk (away from Mg electrodes)? Also reports total near-surface (both faces)."""
import glob, os, numpy as np, MDAnalysis as mda
ST="/lyz/Claude_workplace/polyAPC/storyT5"; t0=50.0
def zones(sysdir):
    base=os.path.join(ST,"sym",sysdir,"field.xtc")
    xs=[x for x in [base]+sorted(glob.glob(base.replace('.xtc','.part*.xtc'))) if os.path.exists(x)]
    u=mda.Universe(os.path.join(ST,"sym",sysdir,"em3dc.gro"), xs)
    slab=u.select_atoms("resname MGE"); anion=u.select_atoms("resname ANI")
    z=np.sort(slab.positions[:,2]/10.0); gaps=np.where(np.diff(z)>1.0)[0]
    s1max=z[:gaps[0]+1].max(); s2min=z[gaps[0]+1:].min()
    mid=(s1max+s2min)/2; area=u.dimensions[0]*u.dimensions[1]/100.0
    nA=nB=nblk=n=0
    for ts in u.trajectory:
        if ts.time/1000.0<t0: continue
        az=anion.positions[:,2]/10.0
        nA+=((az>s1max)&(az<s1max+0.6)).sum()
        nB+=((az<s2min)&(az>s2min-0.6)).sum()
        nblk+=((az>mid-1.5)&(az<mid+1.5)).sum()  # 3nm bulk window centered mid-gap
        n+=1
    return nA/(area*n), nB/(area*n), nblk/(area*n), n
print("system      near-A(anode)  near-B(cathode)  bulk(mid)   total-near(A+B)")
for sd in ["bare_t21","poly_t21"]:
    aA,aB,ablk,n=zones(sd)
    print(f"{sd:10s}  {aA:6.3f}         {aB:6.3f}          {ablk:6.3f}     {aA+aB:6.3f}   (nfr={n})")
