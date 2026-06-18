#!/usr/bin/env python3
"""T17 DoD analysis: from the bare & poly reactive-interface trajectories, build the
SEI **composition-vs-depth** profile and the Al-deposition tally, then map onto the
ToF-SIMS observables — poly should be **Si-rich, Al-poor, shallow** vs bare **Al-rich,
deep**. Outputs t17_depth.csv + t17_profile.png + a poly/bare ratio verdict.

usage: analyze_t17.py <bare_traj.xyz> <poly_traj.xyz> [out_prefix] [tail_frac]
"""
import sys, numpy as np
from ase.io import read
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

bare_t, poly_t = sys.argv[1], sys.argv[2]
pref = sys.argv[3] if len(sys.argv)>3 else "t17"
tail = float(sys.argv[4]) if len(sys.argv)>4 else 0.5    # average over last 50%
DZ = 1.0          # Å depth bins
SPECIES = ["Al","Si","Mg_cat","Cl","O","C"]

def slab_and_profiles(traj):
    ats = read(traj, index=":"); ats = ats[int(len(ats)*(1-tail)):]
    sym = np.array(ats[0].get_chemical_symbols())
    mg = np.where(sym=="Mg")[0]
    z0 = ats[0].get_positions()[:,2]; zs = np.sort(z0[mg])
    gap = np.argmax(np.diff(zs)); slab_top = zs[:gap+1].max()
    cell = ats[0].cell[:]; area = np.linalg.norm(np.cross(cell[0],cell[1]))
    slab_Mg = mg[np.argsort(z0[mg])[:gap+1]]; cat_Mg = mg[np.argsort(z0[mg])[gap+1:]]
    Al=np.where(sym=="Al")[0]; Cl=np.where(sym=="Cl")[0]
    sel = {"Al":Al, "Si":np.where(sym=="Si")[0], "Mg_cat":cat_Mg,
           "Cl":Cl, "O":np.where(sym=="O")[0], "C":np.where(sym=="C")[0]}
    maxd=60.0; edges=np.arange(0,maxd,DZ); prof={s:np.zeros(len(edges)-1) for s in SPECIES}
    dep=0; nfr=len(ats)
    for at in ats:
        p=at.get_positions(); d = p[:,2]-slab_top
        for s,idx in sel.items():
            if len(idx)==0: continue
            h,_=np.histogram(d[idx], bins=edges); prof[s]+=h
        # Al deposition: at slab (<3.2 Å) and reduced (<=1 anion-Cl within 2.8)
        for a in Al:
            if np.linalg.norm(p[slab_Mg]-p[a],axis=1).min()<3.2 and (np.linalg.norm(p[Cl]-p[a],axis=1)<2.8).sum()<=1:
                dep+=1
    for s in prof: prof[s]/= (nfr*area*DZ)      # number density nm^-2-per-Å -> per Å^3 (areal)
    return edges[:-1]+DZ/2, prof, dep/nfr, area, len(Al)

def halfdepth(d, y):
    """depth where cumulative reaches half of total (ToF-SIMS x50 analogue)."""
    c=np.cumsum(y);
    if c[-1]<=0: return np.nan
    return d[np.searchsorted(c, c[-1]/2)]

dB, pB, depB, aB, nAlB = slab_and_profiles(bare_t)
dP, pP, depP, aP, nAlP = slab_and_profiles(poly_t)

# near-surface (first 10 Å) integrated populations -> ToF-SIMS-style poly/bare ratios
def near(prof,d,cut=10.0): return {s: prof[s][d<cut].sum() for s in SPECIES}
nb, npy = near(pB,dB), near(pP,dP)
print("=== T17 SEI composition-vs-depth (reactive MLFF) ===")
print(f"  Al deposited (mean/frame):   bare {depB:.2f}   poly {depP:.2f}   -> poly/bare {depP/max(depB,1e-9):.2f}")
print(f"  near-surface (<10Å) Al:      bare {nb['Al']:.3f}  poly {npy['Al']:.3f}  -> ratio {npy['Al']/max(nb['Al'],1e-9):.2f}  (ToF-SIMS Al ×0.02-0.5)")
print(f"  near-surface (<10Å) Si:      bare {nb['Si']:.3f}  poly {npy['Si']:.3f}  -> ratio {npy['Si']/max(nb['Si'],1e-9):.2f}  (ToF-SIMS Si ×20-34)")
print(f"  Al half-depth:               bare {halfdepth(dB,pB['Al']):.1f}Å  poly {halfdepth(dP,pP['Al']):.1f}Å  (ToF-SIMS 350 vs 92 nm)")
verdict = (npy['Al']<nb['Al']) and (npy['Si']>nb['Si'])
print(f"  ==> {'CONSISTENT with ToF-SIMS (poly Al-poor + Si-rich)' if verdict else 'NOT YET consistent — check sampling/model/driving'}")

# csv + figure
import csv
with open(f"{pref}_depth.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["depth_A"]+[f"{s}_bare" for s in SPECIES]+[f"{s}_poly" for s in SPECIES])
    for i,dd in enumerate(dB):
        w.writerow([round(dd,1)]+[round(pB[s][i],4) for s in SPECIES]+[round(pP[s][i] if i<len(dP) else 0,4) for s in SPECIES])
fig,ax=plt.subplots(1,2,figsize=(11,4.4))
for s,c in zip(["Al","Si"],["#c0392b","#27ae60"]):
    ax[0].plot(dB,pB[s],c=c,ls="--",label=f"{s} bare"); ax[0].plot(dP,pP[s],c=c,label=f"{s} poly")
ax[0].set_xlim(0,40); ax[0].set_xlabel("depth from electrode (Å)"); ax[0].set_ylabel("areal number density")
ax[0].set_title("(a) SEI composition vs depth"); ax[0].legend(frameon=False,fontsize=8)
x=np.arange(2); w=0.36
ax[1].bar(x-w/2,[nb['Al'],nb['Si']],w,color="#7f8c8d",label="bare")
ax[1].bar(x+w/2,[npy['Al'],npy['Si']],w,color="#2471a3",label="poly")
ax[1].set_xticks(x); ax[1].set_xticklabels(["Al near-surface","Si near-surface"])
ax[1].set_title("(b) ToF-SIMS analogue: Al-poor / Si-rich?"); ax[1].legend(frameon=False)
plt.tight_layout(); plt.savefig(f"{pref}_profile.png",dpi=150)
print(f"wrote {pref}_depth.csv + {pref}_profile.png")
