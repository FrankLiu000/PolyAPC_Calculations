#!/usr/bin/env python3
"""Anion number-density vs z under +0.3V/nm field, bare vs poly.
Uses reference em3dc.gro slab faces to avoid trajectory-wrapped Mg atoms shifting
the face markers. Reads field.part*.xtc (discard t0 ns), wraps z, bins /nm^3."""
import sys, glob, os, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, MDAnalysis as mda
ST="/lyz/Claude_workplace/polyAPC/storyT5"; OUT="/lyz/Claude_workplace/PolyAPC_Calculations/results/T5_anion_interface"
t0=50.0  # discard first 50ns (field equilibration)
def anion_rho(sysdir, label, color):
    base=os.path.join(ST,"sym",sysdir,"field.xtc")
    parts=sorted(glob.glob(base.replace('.xtc','.part*.xtc')))
    xs=[x for x in [base]+parts if os.path.exists(x)]
    gro=os.path.join(ST,"sym",sysdir,"em3dc.gro")
    u=mda.Universe(gro, xs)
    anion=u.select_atoms("resname ANI"); slab=u.select_atoms("resname MGE")
    Lz=u.dimensions[2]/10.0; area=u.dimensions[0]*u.dimensions[1]/100.0
    DZ=0.1; edges=np.arange(0,Lz+DZ,DZ); zc=edges[:-1]+DZ/2; H=np.zeros(len(zc))
    nfr=0
    for ts in u.trajectory:
        if ts.time/1000.0 < t0: continue
        az=np.mod(anion.positions[:,2]/10.0, Lz)
        h,_=np.histogram(az,bins=edges); H+=h; nfr+=1
    rho=H/(area*DZ*nfr)
    ref=mda.Universe(gro)
    z=np.sort(ref.select_atoms("resname MGE").positions[:,2]/10.0)
    n=len(z)//2
    s1max=z[:n].max(); s2min=z[n:].min()
    plt.plot(zc,rho,color,label=f"{label} (nfr={nfr})",lw=1.8)
    return zc,rho,s1max,s2min
plt.figure(figsize=(7,4.5))
zb,rb,s1b,s2b=anion_rho("bare_t21","bare", "crimson")
zp,rp,s1p,s2p=anion_rho("poly_t21","poly","steelblue")
for s1max,s2min,lab in [(s1b,s2b,"bare"),(s1p,s2p,"poly")]:
    plt.axvline(s1max,color='0.6',ls=':',lw=0.8); plt.axvline(s2min,color='0.6',ls=':',lw=0.8)
plt.xlabel("z (nm)"); plt.ylabel("anion number density (/nm$^3$)")
plt.title(f"Anion rho(z) under +0.3 V/nm field (discard {t0:.0f} ns); dotted = slab inner faces")
plt.legend(); plt.tight_layout()
plt.savefig(f"{OUT}/fig_field_anion_z.png",dpi=110)
print(f"WROTE {OUT}/fig_field_anion_z.png with reference slab-face markers")
