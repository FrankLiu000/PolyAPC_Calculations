# PBC-aware soft-core steric relaxer. Hold slab+anion fixed; disperse electrolyte off non-bonded
# overlaps (minimum-image!) while same-molecule bond springs keep molecules intact. The min-image
# convention is essential: atoms can overlap periodic images across the ~12.8x11.1 A xy boundaries.
import numpy as np
RCOV={"Al":1.21,"Cl":1.02,"C":0.76,"H":0.31,"O":0.66,"Si":1.11,"Mg":1.41}
def steric_relax(syms,X,nslab,anion,groups,M,niter=220,step=0.05,nb_target=1.45):
    X=np.array(X,float); n=len(syms); rcov=np.array([RCOV[s] for s in syms])
    M=np.array(M,float); Minv=np.linalg.inv(M)
    g=np.array(groups); same=(g[:,None]==g[None,:])
    fixed=np.zeros(n,bool); fixed[:nslab]=True
    for i in anion: fixed[i]=True
    free=(~fixed)[:,None]
    def mic(Xc):  # minimum-image pair vectors (n,n,3) + distances (n,n)
        D=Xc[:,None,:]-Xc[None,:,:]
        Df=D@Minv.T; Df-=np.round(Df); Dm=Df@M.T
        dist=np.linalg.norm(Dm,axis=2); 
        di=np.arange(n); dist[di,di]=9.9
        return Dm,dist
    Dm0,d0=mic(X); rsum=rcov[:,None]+rcov[None,:]
    bond=(d0<1.25*rsum)&same; np.fill_diagonal(bond,False)
    b0=np.where(bond,d0,0.0); eye=np.eye(n,dtype=bool)
    for _ in range(niter):
        Dm,dist=mic(X); U=Dm/(dist[:,:,None]+1e-9)
        ov=np.clip(nb_target-dist,0,None); ov[bond]=0.0; ov[eye]=0.0
        rep=(0.5*ov[:,:,None]*U).sum(axis=1)
        bd=np.where(bond,b0-dist,0.0); spr=(2.5*bd[:,:,None]*U).sum(axis=1)
        disp=(rep+spr)*free
        mag=np.linalg.norm(disp,axis=1,keepdims=True); cap=0.20
        disp=disp*np.where(mag>cap,cap/(mag+1e-9),1.0)
        X=X+step*disp*4
    return X.tolist()
