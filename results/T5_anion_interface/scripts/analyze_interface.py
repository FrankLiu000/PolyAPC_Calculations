#!/usr/bin/env python3
"""T5 interface analysis: Al-anion vs Mg-cation distribution near the Mg(0001)
electrode. Computes the number-density profile rho(d) vs distance d from the
nearest electrode face (two faces folded via z-PBC), the bulk-normalised
enrichment rho(d)/rho_bulk, the near-surface populations, and (bare only, where
the liquid is fully dynamic) per-ion residence time and approach flux.

usage: analyze_interface.py <interface.gro> <prod.xtc> <label> <outdir> [t0_ns]
"""
import sys, numpy as np
import MDAnalysis as mda

gro,xtc,label,outdir = sys.argv[1:5]
t0 = float(sys.argv[5]) if len(sys.argv)>5 else 5.0   # discard first t0 ns (equilibration)
import os; os.makedirs(outdir, exist_ok=True)

u = mda.Universe(gro, xtc)
slab = u.select_atoms("resname MGE")
anion = u.select_atoms("resname ANI and name Al")
cation = u.select_atoms("resname MGC and name Mg1 Mg2")
# slab top face = top of the bottom slab (exclude any PBC-wrapped image atoms high up)
sz = slab.positions[:,2]; slab_top = sz[sz < sz.min()+30.0].max()/10.0   # nm (30 A window = real slab, skips wrapped image)
print(f"[{label}] slab_top={slab_top:.3f} nm ; anions={len(anion)} cations={len(cation)} frames={len(u.trajectory)}")

DBIN=0.02   # nm
def d_to_electrode(znm, Lz):
    z = np.mod(znm, Lz)
    return np.minimum(z - slab_top, Lz - z)   # nearest of the two faces

dt_ns=None; t_prev=None
acc_a=[]; acc_c=[]; Lzs=[]
res_track={}  # anion index -> list of (frame, d)
for ts in u.trajectory:
    t_ns = ts.time/1000.0
    if t_ns < t0: continue
    Lz = ts.dimensions[2]/10.0; Lx=ts.dimensions[0]/10.0; Ly=ts.dimensions[1]/10.0; Lzs.append(Lz)
    da = d_to_electrode(anion.positions[:,2]/10.0, Lz)
    dc = d_to_electrode(cation.positions[:,2]/10.0, Lz)
    acc_a.append(da); acc_c.append(dc)
    area=Lx*Ly
A=np.array(acc_a); C=np.array(acc_c)   # frames x N
nfr=len(A); Lx=Ly=u.dimensions[0]/10.0; Lzm=np.mean(Lzs); area=Lx*Ly
half=Lzm/2.0 - slab_top/2
edges=np.arange(0, half, DBIN)
def profile(M):
    h,_=np.histogram(M.ravel(), bins=edges)
    vol = 2*area*DBIN*nfr          # two faces
    return h/vol                   # number density nm^-3
ra=profile(A); rc=profile(C); dc_c=edges[:-1]+DBIN/2
# bulk reference = plateau in the middle third of the accessible slab
bulkmask=(dc_c>half*0.5)&(dc_c<half*0.95)
ra_bulk=np.median(ra[bulkmask]); rc_bulk=np.median(rc[bulkmask])
# near-surface populations (per nm^2, integrated to 0.8 nm) and enrichment
def nearpop(M,cut=0.8): return (M<cut).sum()/(2*area*nfr)   # ions per nm^2 within cut of a face
npa=nearpop(A); npc=nearpop(C)
# closest-approach distribution
amin=A.min(); cmin=C.min()
np.savetxt(f"{outdir}/profile_{label}.csv",
           np.column_stack([dc_c,ra,rc,ra/max(ra_bulk,1e-9),rc/max(rc_bulk,1e-9)]),
           header="d_nm,rho_anionAl_nm-3,rho_catMg_nm-3,enrich_anion,enrich_cation",delimiter=",",comments="")
print(f"[{label}] bulk rho: anion={ra_bulk:.4f} cation={rc_bulk:.4f} nm^-3")
print(f"[{label}] near-surface (<0.8nm) ions/nm^2: anion={npa:.4f} cation={npc:.4f}")
print(f"[{label}] closest approach over run: anion={amin:.3f} cation={cmin:.3f} nm")
# residence: fraction of time an anion stays within contact (d<0.8) -> survival
cut=0.8
inc=(A<cut)                       # frames x N boolean
occ=inc.mean()                    # fraction of (anion,frame) in contact
# mean contact-streak length (frames) -> residence
res=[]
for j in range(inc.shape[1]):
    col=inc[:,j];
    if not col.any(): continue
    # run lengths of True
    d=np.diff(np.concatenate([[0],col.view(np.int8),[0]]))
    starts=np.where(d==1)[0]; ends=np.where(d==-1)[0]
    res.extend((ends-starts).tolist())
dt=(np.diff([0]));
# frame dt
tt=[]
for ts in u.trajectory[:2]: tt.append(ts.time)
fdt=(tt[1]-tt[0])/1000.0 if len(tt)>1 else 0.005
mean_res=np.mean(res)*fdt if res else 0.0
print(f"[{label}] anion contact occupancy={occ:.3f}, mean contact residence={mean_res:.3f} ns (n_streaks={len(res)}), frame_dt={fdt:.4f} ns")
open(f"{outdir}/summary_{label}.txt","w").write(
    f"label={label}\nslab_top_nm={slab_top:.3f}\nframes_used={nfr}\nframe_dt_ns={fdt:.4f}\n"
    f"rho_bulk_anion_nm-3={ra_bulk:.4f}\nrho_bulk_cation_nm-3={rc_bulk:.4f}\n"
    f"nearsurf_anion_per_nm2={npa:.4f}\nnearsurf_cation_per_nm2={npc:.4f}\n"
    f"closest_anion_nm={amin:.3f}\nclosest_cation_nm={cmin:.3f}\n"
    f"anion_contact_occupancy={occ:.4f}\nanion_mean_residence_ns={mean_res:.3f}\n")
print(f"[{label}] wrote profile_{label}.csv + summary_{label}.txt")
