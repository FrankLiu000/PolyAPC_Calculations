#!/usr/bin/env python3
"""In-situ DRT analysis for MgMg symmetric cells (bareAPC vs pAPC)."""
import glob, os
import numpy as np
from scipy.optimize import nnls
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

OUT = "/sessions/practical-sleepy-darwin/mnt/outputs"
SHARE = "/sessions/practical-sleepy-darwin/mnt/in_situ_DRT"
AREA_CM2 = 1.0
Q_PER_PULSE = 0.5e-3 * 239.8 / 3.6   # mAh per galvanostatic pulse

CELLS = {
    "bareAPC": dict(zglob="ex1/Run01/*Step11_Rp*.z"),
    "pAPC":    dict(zglob="ex2/Run01/*Step10_Rp*.z"),
}

def parse_z(fp):
    started=False; f=[]; zr=[]; zi=[]
    for line in open(fp, encoding="latin-1"):
        if "End Experiment" in line: started=True; continue
        if started:
            p=line.split()
            if len(p)>=6:
                try: f.append(float(p[0])); zr.append(float(p[4])); zi.append(float(p[5]))
                except ValueError: pass
    return np.array(f), np.array(zr), np.array(zi)

def compute_drt(freq, zr, zi, lam=3e-3, n_per_dec=20):
    order=np.argsort(freq); f=freq[order]; Zr=zr[order]; Zi=zi[order]
    w=2*np.pi*f
    tmin=1.0/w.max()/10; tmax=1.0/w.min()*10
    M=int(round(np.log10(tmax/tmin)*n_per_dec))+1
    ln_tau=np.linspace(np.log(tmin),np.log(tmax),M); tau=np.exp(ln_tau); dln=ln_tau[1]-ln_tau[0]
    WT=np.outer(w,tau); denom=1.0+WT**2
    A_re=dln/denom; A_im=-dln*WT/denom
    N=len(f); A=np.zeros((2*N,M+1)); A[:N,0]=1.0; A[:N,1:]=A_re; A[N:,1:]=A_im
    b=np.concatenate([Zr,Zi]); mod=np.sqrt(Zr**2+Zi**2)
    wgt=np.concatenate([1/mod,1/mod]); Aw=A*wgt[:,None]; bw=b*wgt
    L=np.zeros((M-2,M+1))
    for i in range(M-2): L[i,i+1]=1.0; L[i,i+2]=-2.0; L[i,i+3]=1.0
    Aug=np.vstack([Aw,np.sqrt(lam)*L]); baug=np.concatenate([bw,np.zeros(M-2)])
    x,_=nnls(Aug,baug,maxiter=8000); Rinf=x[0]; gamma=x[1:]
    Zfit=A@x; Zfr=Zfit[:N]; Zfi=Zfit[N:]
    res=100*np.sqrt(np.mean(((Zfr-Zr)**2+(Zfi-Zi)**2)/mod**2))
    return tau,gamma,Rinf,(f,Zfr,Zfi,Zr,Zi),res

def process_cell(name,zglob):
    files=sorted(glob.glob(os.path.join(OUT,zglob)))
    taus=[];gammas=[];depth=[];resids=[];fits=[]
    for i,fp in enumerate(files):
        f,zr,zi=parse_z(fp); tau,g,Rinf,fit,res=compute_drt(f,zr,zi)
        taus.append(tau);gammas.append(g);depth.append((i+1)*Q_PER_PULSE/AREA_CM2)
        resids.append(res);fits.append(fit)
    return taus[0],np.array(depth),np.vstack(gammas),np.array(resids),fits

CMAP=LinearSegmentedColormap.from_list("drt",
    ["#08183a","#16476b","#1f8a9b","#5fd0a0","#d9f0a3","#fee08b","#f46d43","#a50026"])

TAU_DISP=(1e-4,1.5915)   # reliable window ~ 1/(2*pi*fmax) .. 1/(2*pi*fmin)
def heatmap(name,tau,depth,G,fname):
    sel=(tau>=TAU_DISP[0])&(tau<=TAU_DISP[1])
    tau_d=tau[sel]; Gd=G[:,sel]
    fig,ax=plt.subplots(figsize=(7.4,5.4)); vmax=np.percentile(Gd,99.0)
    pc=ax.pcolormesh(tau_d,depth,Gd,cmap=CMAP,vmin=0,vmax=vmax,shading="gouraud")
    ax.set_xscale("log")
    ax.set_xlabel(r"Relaxation time  $\tau$ (s)",fontsize=12)
    ax.set_ylabel(r"Charge depth (mAh cm$^{-2}$)",fontsize=12)
    ax.set_title(f"In-situ DRT  -  MgMg {name}",fontsize=13,pad=10)
    ax.set_xlim(tau_d[0],tau_d[-1]); ax.set_ylim(depth[0],depth[-1]); ax.tick_params(labelsize=10)
    cb=fig.colorbar(pc,ax=ax,pad=0.02); cb.set_label(r"$\gamma(\tau)$  ($\Omega$)",fontsize=11)
    fig.tight_layout()
    for d in (OUT,SHARE): fig.savefig(os.path.join(d,fname),dpi=220,bbox_inches="tight")
    plt.close(fig)

def export_csv(name,tau,depth,G):
    with open(os.path.join(SHARE,f"DRT_{name}_long.csv"),"w") as fh:
        fh.write("charge_depth_mAh_cm2,tau_s,gamma_ohm\n")
        for i,d in enumerate(depth):
            for j,t in enumerate(tau): fh.write(f"{d:.5f},{t:.6e},{G[i,j]:.6e}\n")
    with open(os.path.join(SHARE,f"DRT_{name}_matrix.csv"),"w") as fh:
        fh.write("charge_depth_mAh_cm2,"+",".join(f"{t:.4e}" for t in tau)+"\n")
        for i,d in enumerate(depth):
            fh.write(f"{d:.5f},"+",".join(f"{v:.5e}" for v in G[i])+"\n")

results={}
for name,cfg in CELLS.items():
    tau,depth,G,res,fits=process_cell(name,cfg["zglob"])
    heatmap(name,tau,depth,G,f"insitu_DRT_{name}.png"); export_csv(name,tau,depth,G)
    results[name]=(tau,depth,G,res,fits)
    print(f"{name}: {G.shape[0]} spectra, tau {tau[0]:.1e}-{tau[-1]:.1e}s, "
          f"depth {depth[0]:.3f}-{depth[-1]:.3f} mAh/cm2, fit resid mean {res.mean():.2f}% max {res.max():.2f}%")
print("done")

# ---- verification: measured vs reconstructed Nyquist for sampled cycles ----
fig,axes=plt.subplots(2,3,figsize=(13,8))
for col,name in enumerate(["bareAPC","pAPC"]):
    tau,depth,G,res,fits=results[name]
    for row,idx in enumerate([0,14,29]):
        ax=axes[col*0+ (0 if name=='bareAPC' else 1)][row] if False else axes[0 if name=='bareAPC' else 1][row]
        f,Zfr,Zfi,Zr,Zi=fits[idx]
        ax.plot(Zr,-Zi,'o',ms=3,label='meas',color='#1f77b4')
        ax.plot(Zfr,-Zfi,'-',lw=1.5,label='DRT fit',color='#d62728')
        ax.set_title(f"{name} cyc{idx+1} ({res[idx]:.1f}%)",fontsize=9)
        ax.set_xlabel("Z' (Ω)"); ax.set_ylabel("-Z'' (Ω)"); ax.axis('equal')
        if row==0 and col==0: ax.legend(fontsize=8)
fig.suptitle(f"DRT reconstruction check  (mean resid bare {results['bareAPC'][3].mean():.1f}%, pAPC {results['pAPC'][3].mean():.1f}%)")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"_fitcheck.png"),dpi=130)
print("verify saved; resid bare",round(results['bareAPC'][3].mean(),2),"pAPC",round(results['pAPC'][3].mean(),2))
