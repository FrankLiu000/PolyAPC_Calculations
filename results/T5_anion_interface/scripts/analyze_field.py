# Field run: anion-Al & cation-Mg number density vs ABSOLUTE z (not folded), to expose the
# field-driven double layer. Compare neutral (symmetric) vs field (cathode/anode asymmetry).
import sys, numpy as np, MDAnalysis as mda
gro, xtc, label = sys.argv[1:4]
tail = float(sys.argv[4]) if len(sys.argv)>4 else 0.5
u = mda.Universe(gro, xtc)
slab = u.select_atoms("resname MGE"); anion=u.select_atoms("resname ANI and name Al")
cation=u.select_atoms("resname MGC and name Mg1 Mg2")
sz=slab.positions[:,2]; slab_top=sz[sz<sz.min()+30].max()/10
n=len(u.trajectory); start=int(n*(1-tail))
Lz=u.dimensions[2]/10; Lx=u.dimensions[0]/10; Ly=u.dimensions[1]/10
DZ=0.10; edges=np.arange(0,Lz+DZ,DZ); az=[]; cz=[]
for ts in u.trajectory[start:]:
    L=ts.dimensions[2]/10
    az.append(np.mod(anion.positions[:,2]/10, L)); cz.append(np.mod(cation.positions[:,2]/10, L))
az=np.concatenate(az); cz=np.concatenate(cz); nfr=n-start
ha,_=np.histogram(az,bins=edges); hc,_=np.histogram(cz,bins=edges)
vol=Lx*Ly*DZ*nfr; ra=ha/vol; rc=hc/vol; zc=edges[:-1]+DZ/2
# near each face (within 1 nm): bottom face = just above slab_top; top face = just below Lz
def nearface(r, lo, hi): return r[(zc>=lo)&(zc<hi)].mean()
bot_an=nearface(ra, slab_top, slab_top+1.0); bot_ca=nearface(rc, slab_top, slab_top+1.0)
top_an=nearface(ra, Lz-1.0, Lz);            top_ca=nearface(rc, Lz-1.0, Lz)
bulk_an=nearface(ra, slab_top+2.5, Lz-2.5);  bulk_ca=nearface(rc, slab_top+2.5, Lz-2.5)
print(f"[{label}] slab_top={slab_top:.2f} Lz={Lz:.2f} nm, frames={nfr}")
print(f"  bulk(mid):    anion {bulk_an:.3f}  cation {bulk_ca:.3f} nm^-3")
print(f"  BOTTOM face:  anion {bot_an:.3f}  cation {bot_ca:.3f}  (anion/bulk {bot_an/max(bulk_an,1e-9):.2f}, cation/bulk {bot_ca/max(bulk_ca,1e-9):.2f})")
print(f"  TOP face:     anion {top_an:.3f}  cation {top_ca:.3f}  (anion/bulk {top_an/max(bulk_an,1e-9):.2f}, cation/bulk {top_ca/max(bulk_ca,1e-9):.2f})")
cath = "TOP" if top_ca>bot_ca else "BOTTOM"; an_at_cath = top_an/max(bulk_an,1e-9) if cath=="TOP" else bot_an/max(bulk_an,1e-9)
print(f"  => cathode face = {cath} (cation-rich); anion there = {an_at_cath:.2f}x bulk  ({'DEPLETED' if an_at_cath<0.8 else 'not depleted'})")
np.savetxt(f"storyT5/analysis/zprofile_{label}.csv", np.column_stack([zc,ra,rc]),
           header="z_nm,rho_anionAl,rho_catMg", delimiter=",", comments="")
