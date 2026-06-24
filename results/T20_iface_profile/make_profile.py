#!/usr/bin/env python3
"""T20 — interfacial aluminate-anion (and cation) concentration profile C(z) vs
distance z from the Mg(0001) front, bare vs poly, from EXISTING neutral T5/T17
matched trajectories. Bridges T5 anion-sequestration to Liu 2022 (AdvMat
2201886) Fig 5e-g: the cured network homogenizes/sequesters the interfacial
Cl-bearing anion STRUCTURALLY. Single ion pair per cell -> C(z) is the
equilibrium single-ion occupation density (PMF limit), normalized to bulk.
Light trajectory post-processing (CPU); does NOT touch the GPU R1 run."""
import sys, numpy as np
from collections import deque
import ase.io

T17="/lyz/Claude_workplace/PolyAPC_Calculations/computational_v2/mlff/v3/t17"
OUT="/lyz/Claude_workplace/PolyAPC_Calculations/results/T20_iface_profile/outputs"
NSLAB=64
RUNS={"bare":f"{T17}/bare_final_traj.xyz", "poly":f"{T17}/poly_final_traj.xyz"}
EQFRAC=0.20          # discard first 20% as equilibration
NBLOCK=5            # block-average error bars
BINW=0.5           # z bin width (A)
ZMAX=14.0          # interface cell: electrolyte film ~8A above front (no bulk plateau)
NEAR=5.0           # near-front accumulation threshold (A), 3D dist to electrode
REDUCT=2.5         # reductive contact zone (A, from AIMD capstone)

# covalent-only bond cutoffs (A) for the Al-rooted anion tree. Deliberately NO
# pair involving Mg or O -> the flood-fill cannot escape across the ionic
# Cl...Mg contact of the ion pair into the cation / THF (that leak made the
# natural_cutoffs version mis-assign atoms). Anion = Ph2AlCl2- = Al+2Cl+12C+10H.
COV={frozenset(p):c for p,c in {
    ("Al","C"):2.25,("Al","Cl"):2.75,("C","C"):1.85,("C","H"):1.30,("Cl","C"):2.0}.items()}

def anion_tree(pos, sym, Al, slab):
    """covalent component from Al through C/Cl/H bonds only (never Mg/O)."""
    seen={Al}; dq=deque([Al]); slabset=set(slab.tolist())
    while dq:
        i=dq.popleft()
        for j in range(len(sym)):
            if j in seen or j in slabset: continue
            c=COV.get(frozenset((sym[i],sym[j])))
            if c is not None and np.linalg.norm(pos[i]-pos[j])<c:
                seen.add(j); dq.append(j)
    return sorted(seen)

def analyse(sys_name, path):
    f0=ase.io.read(path, index=0)
    sym=np.array(f0.get_chemical_symbols()); pos=f0.get_positions()
    slab=np.arange(NSLAB); ztop=pos[slab,2].max()
    assert (sym[:NSLAB]=="Mg").all(), f"{sys_name}: first {NSLAB} not all Mg"
    Al=int(np.where(sym=="Al")[0][0])
    elyte_Mg=[i for i in range(NSLAB,len(sym)) if sym[i]=="Mg"]
    anion=anion_tree(pos, sym, Al, slab)
    # cation tracer = its 2 Mg(II) cores (indices 64,65): unambiguous, network-proof
    # (poly's "electrolyte minus anion" wrongly swept in the whole POSS network).
    cation=elyte_Mg
    print(f"\n[{sys_name}] {len(sym)} atoms; ztop={ztop:.2f}; Al idx={Al}; "
          f"anion={len(anion)} {dict(zip(*np.unique(sym[anion],return_counts=True)))} (expect 25 Al+2Cl+12C+10H); "
          f"cation-core=Mg{elyte_Mg}")

    # stream frames -> per-frame scalars. Cation tracer = its LEADING Mg (closest to
    # slab), robust to partial cation dissociation (in bare, one Mg drifts off to
    # ~32 A; the Mg2 centroid + ion-pair-sep are corrupted by it, so not headlined).
    an_z=[]; al_z=[]; al_3d=[]; caL_z=[]; caL_3d=[]; ca_drift=[]
    nframe=0
    for at in ase.io.iread(path, index=":"):
        p=at.get_positions()
        mg3=[np.linalg.norm(p[slab]-p[c],axis=1).min() for c in cation]
        lead=int(np.argmin(mg3))
        an_z.append(p[anion,2].mean()-ztop)
        al_z.append(p[Al,2]-ztop)
        al_3d.append(np.linalg.norm(p[slab]-p[Al],axis=1).min())
        caL_z.append(p[cation[lead],2]-ztop)             # leading cation-Mg height
        caL_3d.append(mg3[lead])                          # leading cation-Mg 3D approach
        ca_drift.append(max(mg3))                         # farthest cation-Mg (dissociation tracker)
        nframe+=1
    A={k:np.array(v) for k,v in dict(an_z=an_z,al_z=al_z,al_3d=al_3d,caL_z=caL_z,caL_3d=caL_3d,ca_drift=ca_drift).items()}
    eq=int(EQFRAC*nframe); A={k:v[eq:] for k,v in A.items()}; n=len(A["an_z"])
    print(f"         frames total={nframe} eq-drop={eq} used={n}")
    print(f"         anion-cen z : {A['an_z'].mean():6.2f} +/- {A['an_z'].std():.2f}  [min {A['an_z'].min():.2f} max {A['an_z'].max():.2f}]")
    print(f"         Al(reduc) z : {A['al_z'].mean():6.2f} +/- {A['al_z'].std():.2f}  | Al 3D-slabMin {A['al_3d'].mean():.2f}+/-{A['al_3d'].std():.2f} (T5; bare4.58/poly7.57)")
    print(f"         cation lead : z {A['caL_z'].mean():6.2f}  | 3D-slabMin {A['caL_3d'].mean():.2f}+/-{A['caL_3d'].std():.2f}  | farthest-Mg drift max {A['ca_drift'].max():.1f} A")
    A.update(name=sys_name, n=n); return A

def pdf(z, edges):
    """block-averaged probability density (integral=1 over the sampled range)."""
    bw=edges[1]-edges[0]
    P=np.array([np.histogram(b,bins=edges)[0]/len(b)/bw for b in np.array_split(z,NBLOCK)])
    return P.mean(0), P.std(0)

edges=np.arange(0, ZMAX+BINW, BINW); centers=0.5*(edges[:-1]+edges[1:])
res={s:analyse(s,p) for s,p in RUNS.items()}

cols={"z_angstrom":centers}; metrics=[]
for s in ("bare","poly"):
    r=res[s]
    an,an_e=pdf(r["an_z"], edges); ca,ca_e=pdf(r["caL_z"], edges)  # cation = leading Mg (robust)
    cols[f"rho_anion_{s}"]=an;  cols[f"rho_anion_{s}_err"]=an_e
    cols[f"rho_cation_{s}"]=ca; cols[f"rho_cation_{s}_err"]=ca_e
    metrics.append(dict(system=s,
        anion_cen_mean_z=r["an_z"].mean(), al_reduc_mean_z=r["al_z"].mean(),
        al_mean_3dmin=r["al_3d"].mean(), al_sd_3dmin=r["al_3d"].std(),
        al_min_3dmin=r["al_3d"].min(),                        # closest the anion ever gets
        cation_lead_mean_z=r["caL_z"].mean(), cation_lead_3dmin=r["caL_3d"].mean(),
        cation_maxdrift=r["ca_drift"].max(),                  # >> => a cation Mg dissociated
        anion_nearfront_frac=(r["al_3d"]<=NEAR).mean(),       # P(within 5A of electrode) = accumulation
        reduct_contact_frac=(r["al_3d"]<=REDUCT).mean()))     # P(within reductive 2.5A)

import csv
keys=list(cols.keys())
with open(f"{OUT}/anion_density_profile.csv","w",newline="") as fh:
    fh.write("# C(z) = probability density (integral=1) of ion centroid vs perpendicular distance z from Mg(0001) front.\n")
    fh.write("# Single ion pair per cell -> equilibrium single-ion occupation (PMF limit). NO bulk plateau in this\n")
    fh.write("# nanoscale interface film, so normalized to unit integral (not C/C_bulk). err = block std (NBLOCK=5).\n")
    w=csv.writer(fh); w.writerow(keys)
    for i in range(len(centers)): w.writerow([f"{cols[k][i]:.5g}" for k in keys])
mb,mp=metrics
with open(f"{OUT}/iface_accumulation_metrics.csv","w",newline="") as fh:
    w=csv.DictWriter(fh, fieldnames=list(mb.keys())); w.writeheader()
    for m in metrics: w.writerow({k:(f"{v:.4g}" if isinstance(v,float) else v) for k,v in m.items()})

enr=mb["anion_nearfront_frac"]/mp["anion_nearfront_frac"] if mp["anion_nearfront_frac"]>0 else float("inf")
print("\n=== METRICS ===")
for m in metrics: print("  ",{k:(round(v,3) if isinstance(v,float) else v) for k,v in m.items()})
print(f"\n  near-front (Al<= {NEAR}A 3D) anion accumulation: bare {mb['anion_nearfront_frac']:.3f}  poly {mp['anion_nearfront_frac']:.3f}  -> bare/poly = {enr:.2f}x")
print(f"  closest approach ever (min Al 3D):  bare {mb['al_min_3dmin']:.2f}  poly {mp['al_min_3dmin']:.2f} A")
print(f"  reductive contact (Al<=2.5A) frac:  bare {mb['reduct_contact_frac']:.4f}  poly {mp['reduct_contact_frac']:.4f}  (both ~0 = field-free safe)")
print(f"\nWROTE {OUT}/anion_density_profile.csv + iface_accumulation_metrics.csv")

# ---- figure ----
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
e3=np.arange(0,12.01,BINW); c3=0.5*(e3[:-1]+e3[1:])
fig,ax=plt.subplots(1,2,figsize=(11,4.4))
A=ax[0]
for s,col in (("bare","C0"),("poly","C3")):
    A.plot(centers,cols[f"rho_anion_{s}"],col,lw=2,label=f"anion {s}")
    A.fill_between(centers,cols[f"rho_anion_{s}"]-cols[f"rho_anion_{s}_err"],cols[f"rho_anion_{s}"]+cols[f"rho_anion_{s}_err"],color=col,alpha=.18)
    A.plot(centers,cols[f"rho_cation_{s}"],col,lw=1.3,ls="--",label=f"cation·Mg₂ {s}")
A.axvspan(0,REDUCT,color="0.85",label=f"reductive zone <{REDUCT} Å")
A.set_xlabel("z from Mg(0001) front (Å)"); A.set_ylabel("C(z)  (prob. density, ∫=1)")
A.set_title("Perpendicular C(z): anion (Ph₂AlCl₂⁻) vs cation·Mg₂",fontsize=10); A.set_xlim(0,ZMAX); A.legend(fontsize=8)
B=ax[1]
for s,col in (("bare","C0"),("poly","C3")):
    ha,_=np.histogram(res[s]["al_3d"],bins=e3,density=True)
    hc,_=np.histogram(res[s]["caL_3d"],bins=e3,density=True)
    B.plot(c3,ha,col,lw=2.2,label=f"anion·Al {s}: ⟨{res[s]['al_3d'].mean():.2f}⟩ Å")
    B.plot(c3,hc,col,lw=1.3,ls="--",label=f"cation·Mg {s}: ⟨{res[s]['caL_3d'].mean():.2f}⟩ Å")
B.axvspan(0,REDUCT,color="0.85"); B.axvline(NEAR,color="k",ls=":",lw=.8)
B.set_xlabel("ion–electrode 3D min distance (Å)"); B.set_ylabel("prob. density")
B.set_title(f"3D standoff & inversion: anion near-front {mb['anion_nearfront_frac']*100:.0f}%→{mp['anion_nearfront_frac']*100:.0f}% ({enr:.0f}×)",fontsize=10); B.set_xlim(0,12); B.legend(fontsize=7.5)
fig.suptitle("T20 — interfacial aluminate-anion C(z), bare vs poly (neutral, field-free)  ·  Liu 2022 Fig 5e–g analogue",fontsize=11,weight="bold")
fig.tight_layout(rect=(0,0,1,.96)); fig.savefig(f"{OUT}/Cz_profile.png",dpi=150)
print(f"WROTE {OUT}/Cz_profile.png")
np.save(f"{OUT}/_scalars.npy", {s:{k:res[s][k] for k in ("an_z","al_z","al_3d","caL_z","caL_3d","ca_drift")} for s in res}, allow_pickle=True)
print(f"  cation leading-Mg 3D:    bare {mb['cation_lead_3dmin']:.2f}  poly {mp['cation_lead_3dmin']:.2f} A  (cation reaches front in BOTH = transparency)")
print(f"  INVERSION: bare anion {mb['al_mean_3dmin']:.2f} < cation {mb['cation_lead_3dmin']:.2f} (anion leads) | poly anion {mp['al_mean_3dmin']:.2f} > cation {mp['cation_lead_3dmin']:.2f} (cation leads, anion excluded)")
print(f"  cation max-drift (dissoc): bare {mb['cation_maxdrift']:.1f} A (one Mg dissociates!) poly {mp['cation_maxdrift']:.1f} A (intact)")
