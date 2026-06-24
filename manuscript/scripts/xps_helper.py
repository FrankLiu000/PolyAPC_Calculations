# -*- coding: utf-8 -*-
"""Published-style XPS rendering: raw data as open-circle scatter, Shirley background,
semi-transparent GL(30) fitted component peaks, envelope. Depth-stacked (0/10/20 nm).
Convention per battery-SEI XPS literature (CasaXPS Shirley bg + GL(30) peak shape)."""
import csv, numpy as np
XR=r"D:/20260602_polyAPC_data/XPS/results/data"
def _rd(p):
    with open(p,encoding="utf-8") as f: return list(csv.DictReader(f))
PKT=_rd(XR+"/peak_table_all.csv")
FIT={"Al2p":_rd(XR+"/fit_Al2p.csv"),"Si2p":_rd(XR+"/fit_Si2p.csv")}
DEPTH={0:"0 nm",1:"10 nm",2:"20 nm"}

def gl(x,c,fwhm,eta=0.7):   # GL(30): 30% Gaussian -> eta(Lorentz)=0.7
    s=fwhm/2.3548; g=np.exp(-(x-c)**2/(2*s*s)); l=1/(1+((x-c)/(fwhm/2))**2)
    return eta*l+(1-eta)*g

def load(sample,region,etch):
    sp=_rd(XR+f"/spectra/{sample}_{region}_e{etch}.csv")
    be=np.array([float(r["BE_eV"]) for r in sp])
    cps=np.array([float(r["counts_per_s"]) for r in sp])
    bg=np.array([float(r["backgnd_cps"]) for r in sp])
    return be,cps,bg

def comps(sample,region,etch):
    """return list of (label, center, fwhm, area, is_metal)"""
    out=[]
    if region in FIT:
        for r in FIT[region]:
            if r["sample"]==sample and int(r["etch"])==etch:
                out.append((r["component"],float(r["BE_raw"]),float(r["FWHM"]),float(r["area"]),
                            ("Al0" in r["component"] or "Si(0)" in r["component"])))
    else:  # single fitted peak from peak table
        for r in PKT:
            if r["sample"]==sample and int(r["etch"])==etch and r["region"]==region:
                out.append(("",float(r["peak_BE_eV"]),float(r["fwhm_eV"]),float(r["height_cps"]),False))
    return out

def panel(ax, region, sample, COL, off_step=1.25, win=None, metal_c=None, ox_c=None, scatter_every=4):
    """Stacked depth profile for one region+sample. Returns (xlo,xhi)."""
    import matplotlib.pyplot as plt
    metal_c = metal_c or COL["Al"]; ox_c = ox_c or COL["poly"]
    xmins=[]; xmaxs=[]
    for etch in (0,1,2):
        be,cps,bg=load(sample,region,etch)
        if win: msk=(be>=win[0])&(be<=win[1]); be,cps,bg=be[msk],cps[msk],bg[msk]
        norm=np.nanmax(cps); off=etch*off_step
        # raw scatter (open circles)
        ax.plot(be[::scatter_every],(cps/norm)[::scatter_every]+off,ls="none",marker="o",
                ms=1.7,mfc="none",mec="0.45",mew=0.35,zorder=3)
        # background
        ax.plot(be,bg/norm+off,color="0.6",lw=0.5,ls="-",zorder=2)
        # components (semi-transparent fills) + envelope
        cs=comps(sample,region,etch)
        raw=np.zeros((len(cs),len(be)))
        for i,(lab,c,fw,ar,met) in enumerate(cs): raw[i]=ar*gl(be,c,fw)
        tot=raw.sum(0)
        scale=(np.nanmax(cps-bg))/np.nanmax(tot) if tot.max()>0 else 1.0
        for i,(lab,c,fw,ar,met) in enumerate(cs):
            cc=metal_c if met else ox_c
            ax.fill_between(be,bg/norm+off,(bg+raw[i]*scale)/norm+off,color=cc,alpha=0.45,lw=0,zorder=2)
        ax.plot(be,(bg+tot*scale)/norm+off,color="black",lw=0.8,zorder=4)
        ax.text(be.max(),off+0.30,DEPTH[etch],fontsize=5.0,color="0.3",ha="left",va="center")
        xmins.append(be.min()); xmaxs.append(be.max())
    ax.set_xlim(max(xmaxs),min(xmins))   # BE reversed
    ax.set_yticks([])
    return min(xmins),max(xmaxs)
