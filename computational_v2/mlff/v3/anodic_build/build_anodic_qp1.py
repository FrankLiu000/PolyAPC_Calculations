#!/usr/bin/env python3
"""Build ANODIC q=+1 close-approach scaffolds, FULLY PBC-AWARE (minimum-image everywhere).
Translate the Ph2AlCl2- anion (idx 147) to Al-electrode 2.5-7 A (denser <4 A); gentle rigid-molecule
jitter (bonds preserved); PBC soft-core steric relax disperses electrolyte off the intruding anion
*and* off periodic images. Filter: intact bonds + no min-image overlap. ~2 dist/cell held out _TEST.
usage: build_anodic_qp1.py <base.xyz> <Natoms> <sys> <out.xyz> <n_slab> <latticeCSV9>
"""
import sys, math, random
import numpy as np
random.seed(20260624)
from steric import steric_relax
RCOV={"Al":1.21,"Cl":1.02,"C":0.76,"H":0.31,"O":0.66,"Si":1.11,"Mg":1.41}
base,nat,sysname,out,nslab=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4],int(sys.argv[5])
lat=[float(x) for x in sys.argv[6].split(",")]
M=np.array([lat[0:3],lat[3:6],lat[6:9]]).T; Minv=np.linalg.inv(M)
lines=[l for l in open(base) if len(l.split())>=4 and l.split()[0] in RCOV]
rows=[l.split() for l in lines][:nat]
syms=[r[0] for r in rows]; X0=np.array([[float(r[1]),float(r[2]),float(r[3])] for r in rows])
assert len(syms)==nat
ALI=147
def dmat(X):  # min-image distance matrix
    D=X[:,None,:]-X[None,:,:]; Df=D@Minv.T; Df-=np.round(Df); d=np.linalg.norm(Df@M.T,axis=2)
    np.fill_diagonal(d,9.9); return d
rcov=np.array([RCOV[s] for s in syms]); rsum=rcov[:,None]+rcov[None,:]
# identification (anion, molecules, bonds) uses RAW distances on the clean base (compact, no PBC bridging)
d0=np.linalg.norm(X0[:,None,:]-X0[None,:,:],axis=2); np.fill_diagonal(d0,9.9)
nonbond=~(d0<1.3*rsum)   # non-bonded mask (for min-image overlap check, exclude real bonds)
# --- anion BFS (Al + 2Cl + 2 phenyl), tight element cutoffs, min-image ---
AN={"Al","Cl","C","H"}; CUT={("Al","Cl"):2.8,("Al","C"):2.3,("C","C"):1.75,("C","H"):1.30,("Al","H"):2.0,("Cl","C"):2.0}
def acut(a,b): return CUT.get((a,b)) or CUT.get((b,a)) or 1.6
anion={ALI}; fr=[ALI]
while fr:
    nf=[]
    for i in fr:
        for j in range(nat):
            if j in anion or syms[j] not in AN: continue
            if d0[i,j]<acut(syms[i],syms[j]): anion.add(j); nf.append(j)
    fr=nf
anion=sorted(anion); aset=set(anion)
sys.stderr.write(f"[{sysname}] anion {len(anion)} atoms\n")
elec=[i for i in range(nslab,nat) if i not in aset]
# --- electrolyte molecule grouping (covalent, min-image) ---
bondm=(d0<1.2*rsum)
seen=set(); mols=[]
for s in elec:
    if s in seen: continue
    comp=[]; st=[s]; seen.add(s)
    while st:
        u=st.pop(); comp.append(u)
        for v in elec:
            if v not in seen and bondm[u,v]: seen.add(v); st.append(v)
    mols.append(comp)
groups=[-1]*nat
for i in anion: groups[i]=-2
for gi,mol in enumerate(mols):
    for i in mol: groups[i]=gi
# tracked genuine bonds (within electrolyte) from base + their lengths
BONDS=[(i,j,d0[i,j]) for mol in mols for a_ in range(len(mol)) for b_ in range(a_+1,len(mol))
       for i,j in [(mol[a_],mol[b_])] if d0[i,j]<1.18*rsum[i,j]]
sys.stderr.write(f"[{sysname}] {len(mols)} molecules, {len(BONDS)} bonds tracked\n")
slabtop=X0[:nslab,2].max(); alz=X0[ALI,2]
DISTS=[2.5,2.75,3.0,3.25,3.5,3.75,4.0,4.5,5.0,5.5,6.0,6.5,7.0]; TEST={3.25,5.5}
NTRY=6; KEEP=3; BOND_TOL=0.10; MIN_OVERLAP=1.20

def rigid_jitter(X, T=0.12, ANG=6.0, NOISE=0.02):
    X=X.copy()
    for mol in mols:
        cx=X[mol].mean(axis=0)
        ax=np.random.randn(3); ax/=np.linalg.norm(ax) or 1.0; th=math.radians(random.uniform(-ANG,ANG))
        c,s=math.cos(th),math.sin(th); ux,uy,uz=ax
        R=np.array([[c+ux*ux*(1-c),ux*uy*(1-c)-uz*s,ux*uz*(1-c)+uy*s],
                    [uy*ux*(1-c)+uz*s,c+uy*uy*(1-c),uy*uz*(1-c)-ux*s],
                    [uz*ux*(1-c)-uy*s,uz*uy*(1-c)+ux*s,c+uz*uz*(1-c)]])
        tr=np.array([random.uniform(-T,T) for _ in range(3)])
        X[mol]=(R@(X[mol]-cx).T).T+cx+tr+np.random.uniform(-NOISE,NOISE,X[mol].shape)
    return X

def bonddev(X): return max((abs(np.linalg.norm((lambda v:v-np.round(v@Minv.T)@M.T)(X[i]-X[j]))-L) for i,j,L in BONDS), default=0.0)

fo=open(out,"w"); nframes=0; rep=[]; dropped=[]
an_idx=np.array(anion); el_idx=np.array(elec); slab_idx=np.arange(nslab)
for d in DISTS:
    cands=[]
    for t in range(NTRY):
        X=X0.copy(); X[an_idx,2]+=(slabtop+d)-alz
        X=rigid_jitter(X)
        X=np.array(steric_relax(syms,X.tolist(),nslab,anion,groups,M.tolist(),niter=400))
        dm=dmat(X)
        gmin=dm[nonbond].min()                          # min-image NON-BONDED contact (catch PBC overlaps, exclude bonds)
        mc=dm[np.ix_(an_idx,el_idx)].min()              # anion<->electrolyte
        ms=dm[np.ix_(an_idx,slab_idx)].min()            # anion<->slab
        bd=bonddev(X)
        cands.append((bd,gmin,mc,ms,X))
    clean=[c for c in cands if c[0]<=BOND_TOL and c[1]>=MIN_OVERLAP]
    clean.sort(key=lambda x:-x[1])
    tag=f"bias_{sysname}_qp1_d{d}"+("_TEST" if d in TEST else "")
    if not clean:
        dropped.append((d,min(c[0] for c in cands),max(c[1] for c in cands))); continue
    for bd,gmin,mc,ms,X in clean[:KEEP]:
        fo.write(f"{nat}\n{tag}\n")
        for s_,xyz in zip(syms,X): fo.write(f"{s_} {xyz[0]:.6f} {xyz[1]:.6f} {xyz[2]:.6f}\n")
        nframes+=1; rep.append((d,bd,gmin,mc,ms,"TEST" if d in TEST else "train"))
fo.close()
print(f"[{sysname}] wrote {nframes} clean frames -> {out}")
print(f"{'d':>5} {'bonddev':>7} {'gmin':>6} {'anEl':>6} {'anSlab':>7} tag")
for d,bd,gm,mc,ms,tg in rep: print(f"{d:5.2f} {bd:7.2f} {gm:6.2f} {mc:6.2f} {ms:7.2f} {tg}")
if dropped:
    print(f"[{sysname}] DROPPED {len(dropped)} distances (no clean frame): "+", ".join(f"d{d}(bd{bd:.2f},gmin{gm:.2f})" for d,bd,gm in dropped))
