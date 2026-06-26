#!/usr/bin/env python3
"""Per-face near-surface ion density for the symmetric two-slab (pbc=xyz+3dc) geometry.
Plan A: examine the POLYMER-RICH and POLYMER-POOR electrode surfaces separately.
faceA/faceB = inner faces of the two slabs; for poly, the face with more POSS network
within 1 nm is labelled poly-RICH, the other poly-POOR (bare: symmetric, faceA/faceB).
Reports anion+cation areal density (/nm2, block-avg±SEM) per face with slope+[flat/DRIFT].
usage: twoface_sym.py <gro> <base_xtc> <label> [t0_ns]
"""
import sys, glob, os, numpy as np, MDAnalysis as mda
def chain(b): return [x for x in [b]+sorted(glob.glob(b.replace('.xtc','.part*.xtc'))) if os.path.exists(x)]
def blk(a, nb=10):
    a=np.asarray(a)
    if len(a)<nb: return a.mean(),(a.std(ddof=1)/np.sqrt(len(a)) if len(a)>1 else 0.0)
    bm=np.array([x.mean() for x in np.array_split(a,nb)]); return bm.mean(), bm.std(ddof=1)/np.sqrt(nb)
gro, base, label = sys.argv[1:4]; t0=float(sys.argv[4]) if len(sys.argv)>4 else 0.0
xs=chain(base)
if not xs: print(f"{label}: no trajectory yet"); sys.exit()
u=mda.Universe(gro, xs); slab=u.select_atoms("resname MGE")
al=u.select_atoms("resname ANI and name Al"); mg=u.select_atoms("resname MGC and (name Mg1 or name Mg2)")
net=u.select_atoms("(not resname MGE MGC ANI THF)"); has_net=len(net)>0
area=u.dimensions[0]/10*u.dimensions[1]/10
T=[]; rec={k:([],[]) for k in("anion","cation")}; netAB=[[],[]]
for ts in u.trajectory:
    sz=slab.positions[:,2]/10; mid=(sz.min()+sz.max())/2
    fA=sz[sz<mid].max(); fB=sz[sz>=mid].min()
    for k,sel in(("anion",al),("cation",mg)):
        z=sel.positions[:,2]/10
        rec[k][0].append(((z>fA)&(z-fA<0.8)).sum()/area); rec[k][1].append(((z<fB)&(fB-z<0.8)).sum()/area)
    if has_net:
        nz=net.positions[:,2]/10
        netAB[0].append(((nz>fA)&(nz-fA<1.0)).sum()); netAB[1].append(((nz<fB)&(fB-nz<1.0)).sum())
    T.append(ts.time/1000)
T=np.array(T); m=T>=t0
if m.sum()<10: m=np.ones(len(T),bool)
Tw=T[m]; span=Tw[-1]-Tw[0] if len(Tw)>1 else 1.0
if has_net:
    nA=np.mean(np.array(netAB[0])[m]); nB=np.mean(np.array(netAB[1])[m])
    labs=["poly-RICH","poly-POOR"] if nA>=nB else ["poly-POOR","poly-RICH"]
    netinfo=f" [net/1nm faceA={nA:.0f} faceB={nB:.0f}]"
else:
    labs=["faceA","faceB"]; netinfo=" [bare: faces equivalent]"
print(f"[{label}] t={T[-1]:.0f}ns window {Tw[0]:.0f}-{T[-1]:.0f}ns ({m.sum()} fr){netinfo}")
for k in("anion","cation"):
    A=np.array(rec[k][0])[m]; B=np.array(rec[k][1])[m]
    ma,sa=blk(A); mb,sb=blk(B)
    slA=np.polyfit(Tw,A,1)[0] if len(Tw)>5 else 0.0; slB=np.polyfit(Tw,B,1)[0] if len(Tw)>5 else 0.0
    pA="flat" if abs(slA)*span<=2*max(sa,1e-9) else "DRIFT"; pB="flat" if abs(slB)*span<=2*max(sb,1e-9) else "DRIFT"
    print(f"  {k:6s} {labs[0]}={ma:.4f}±{sa:.4f}[{pA}] | {labs[1]}={mb:.4f}±{sb:.4f}[{pB}]")
