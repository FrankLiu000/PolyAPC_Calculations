# -*- coding: utf-8 -*-
"""Figure 7 - Top-down computational design rule for the Mg-anode interphase.
Turns the validated mechanism into a 4-descriptor screen (JPCC/EES-style design map).
All numbers are REAL computed values (T2 redox, T5 sequestration, T8/T8b band alignment).
Open symbols = node-predicted candidate chemistries (T18 screen, pending). NOT AI-generated."""
import sys, csv, json, os
sys.path.insert(0, r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad")
from angew_style import *
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon as MplPoly
import numpy as np

REPO=r"D:/20260602_polyAPC_data/PolyAPC_repo"
DOS=REPO+"/results/T8b_DOS/outputs/"
OUT=r"D:/20260602_polyAPC_data/Angewandte_Research_Article/figures/Fig7_design_rule"
def rd(p):
    with open(p,encoding="utf-8") as f: return list(csv.DictReader(f))
align={r["phase"]:r for r in rd(DOS+"iface_MgSiOx_alignment.csv")}
meta=json.load(open(DOS+"dos_meta.json",encoding="utf-8"))

fig=plt.figure(figsize=(W2,0.92*W2))
gs=fig.add_gridspec(2,2,height_ratios=[1.0,0.92],hspace=0.46,wspace=0.34,
                    left=0.075,right=0.965,top=0.93,bottom=0.075)

# ---------- (a) descriptor scorecard radar: poly vs bare ----------
ax=fig.add_subplot(gs[0,0],projection="polar")
labels=["D1\ninterphase\nredox stability","D2\ne$^-$-injection\nbarrier",
        "D3\nanion\nsequestration","D4\ncation\ntransport"]
poly=[0.95,0.88,0.95,0.60]; bare=[0.12,0.00,0.06,0.60]
real_p=["SiO$_x$\n(no Al$^0$)","3.07 eV","47.5%\n4.2$\\times$","t$_+$0.50"]
real_b=["Al$^0$\n~50%","0 (metal)","none","t$_+$0.50"]
N=len(labels); ang=np.linspace(0,2*np.pi,N,endpoint=False)
angc=np.concatenate([ang,ang[:1]])
def close(v): return v+v[:1]
ax.plot(angc,close(poly),color=C["poly"],lw=1.6,marker="o",ms=3.5,label="poly-APC")
ax.fill(angc,close(poly),color=C["poly"],alpha=0.18)
ax.plot(angc,close(bare),color=C["bare"],lw=1.4,ls=(0,(5,2)),marker="s",ms=3.2,label="bare-APC")
ax.fill(angc,close(bare),color=C["bare"],alpha=0.13)
ax.set_xticks(ang); ax.set_xticklabels(labels,fontsize=5.6)
ax.set_yticks([0.25,0.5,0.75,1.0]); ax.set_yticklabels([],fontsize=4)
ax.set_ylim(0,1.05); ax.tick_params(pad=0.5)
ax.grid(color=C["grid"],lw=0.6)
for a,vp,rp in zip(ang,poly,real_p):
    ax.text(a,vp+0.07,rp,fontsize=4.3,color=C["poly"],ha="center",va="center",fontweight="bold")
# tie cue on D4
ax.annotate("transport: tie\n(not the discriminator)",xy=(ang[3],0.60),xytext=(ang[3],0.30),
            fontsize=4.3,color=C["ink"],ha="center",va="center")
ax.legend(loc="upper right",bbox_to_anchor=(1.20,1.16),fontsize=5.6,handlelength=1.4)
ax.set_title("Design-descriptor scorecard",fontsize=7.5,pad=14)
fig.text(0.075,0.955,"a",fontsize=10,fontweight="bold")

# ---------- (b) top-down screening funnel ----------
ax=fig.add_subplot(gs[0,1]); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,10)
tiers=[
 (9.3,"Candidate library",  "curing / passivator chemistries $\\times$ anion families",  "#DCE6F1","CPU+GPU"),
 (7.2,"Tier 1  molecular DFT","anion $E_{red}$ (D1) $\\cdot$ group$\\to$Mg, group$\\to$anion binding (D3,D4)","#CFE0EE","CPU/MLFF"),
 (5.1,"Tier 2  periodic DFT", "Mg|SEI band alignment $\\to$ e$^-$-injection barrier (D2)","#BFD6E8","CPU"),
 (3.0,"Tier 3  reactive MLFF-MD","sequestration + Al co-deposition suppression (D3 validate)","#AFCBE2","GPU"),
]
wtop=9.0
for i,(yc,t,sub,col,node) in enumerate(tiers):
    f=1-0.16*i; w=wtop*f; x0=5-w/2
    if i<len(tiers)-1:
        f2=1-0.16*(i+1); w2=wtop*f2
        poly=MplPoly([[x0,yc-0.55],[x0+w,yc-0.55],[5+w2/2,yc-1.55],[5-w2/2,yc-1.55]],
                     closed=True,fc=col,ec="white",lw=1.0)
        ax.add_patch(poly)
    ax.text(5,yc-0.05,t,ha="center",va="center",fontsize=6.2,fontweight="bold",color=C["ink"])
    ax.text(5,yc-0.40,sub,ha="center",va="center",fontsize=4.5,color=C["ink"])
    ax.text(9.4,yc-0.1,node,ha="right",va="center",fontsize=4.6,style="italic",color=C["poly"])
# hit
ax.add_patch(plt.Rectangle((3.0,0.55),4.0,1.05,fc=C["green"],ec="white",lw=1.0,alpha=0.9))
ax.text(5,1.07,"Validated hit: POSS $\\to$ Si-rich insulating interphase",
        ha="center",va="center",fontsize=5.6,fontweight="bold",color="white")
ax.annotate("",xy=(5,1.7),xytext=(5,2.3),arrowprops=dict(arrowstyle="-|>",color=C["ink"],lw=1.2))
ax.set_title("Top-down screening workflow",fontsize=7.5,pad=2)
fig.text(0.55,0.955,"b",fontsize=10,fontweight="bold")

# ---------- (c) SEI electronic selection map (real 6-phase scatter) ----------
ax=fig.add_subplot(gs[1,0])
disp={"SiO2":("SiO$_2$",C["green"],"*",  "poly hit"),
      "Al2O3":("Al$_2$O$_3$",C["bare"],"s",None),
      "MgO":("MgO","#56B4E9","^",None),
      "MgCl2":("MgCl$_2$","#CC79A7","D",None),
      "Al_fcc":("Al$^0$",C["bare_d"],"v","bare"),
      "Mg17Al12":("Mg$_{17}$Al$_{12}$",C["bare_d"],"v","bare")}
# region shading
ax.axhspan(0,1.0,color=C["bare"],alpha=0.07,lw=0)
ax.axvspan(0,1.0,color=C["bare"],alpha=0.07,lw=0)
ax.add_patch(plt.Rectangle((1.0,1.0),3.0,8.5,fc=C["green"],alpha=0.06,lw=0))
ax.text(0.18,0.55,"leaky\n(metallic SEI)",fontsize=5.0,color=C["bare_d"],fontweight="bold")
ax.text(3.45,8.0,"passivating\n(wide-gap insulator)",fontsize=5.0,color=C["green"],
        fontweight="bold",ha="right")
for ph,(nm,col,mk,tag) in disp.items():
    bar=float(align[ph]["e_injection_barrier_eV"]); g=meta[ph]["t8_authoritative_gap_eV"]
    ms=12 if mk=="*" else 7
    ax.scatter([bar],[g],s=(150 if mk=="*" else 55),marker=mk,color=col,
               edgecolor="black",lw=0.6,zorder=5)
    dy=0.45 if ph!="Mg17Al12" else -0.75
    dx=0.0 if ph not in("Al_fcc",) else 0.0
    ax.annotate(nm,(bar,g),xytext=(bar+0.12,g+dy),fontsize=5.6,fontweight="bold",color=col)
    if tag=="poly hit":
        ax.annotate("validated top hit (poly)",(bar,g),xytext=(bar-0.05,g-1.4),
                    fontsize=5.0,color=C["green"],ha="center",
                    arrowprops=dict(arrowstyle="-",color=C["green"],lw=0.6))
# pending node candidates (open slots, NOT data)
ax.scatter([],[],s=45,marker="o",facecolor="none",edgecolor="0.45",lw=0.9,
           label="node-predicted candidates\n(borosiloxane, phosphazene,\npolyether-siloxane, Al-alkoxide; T18)")
ax.legend(loc="lower right",fontsize=4.6,handlelength=1.0,borderpad=0.3,labelspacing=0.3)
ax.set_xlim(-0.3,4.0); ax.set_ylim(-0.5,9.3)
ax.set_xlabel("e$^-$-injection barrier  $\\Phi_{inj}$ (eV)   [D2]")
ax.set_ylabel("band gap  $E_g$ (eV)")
ax.set_title("SEI electronic selection map",pad=3)
panel_label(ax,"c")

# ---------- (d) design rule + validation ----------
ax=fig.add_subplot(gs[1,1]); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,10)
ax.text(5,9.4,"Design rule",ha="center",fontsize=7.5,fontweight="bold",color=C["ink"])
ax.text(5,8.3,"maximize  $\\Phi_{inj}$ (e$^-$ block) $+$ anion sequestration\nat fixed cation transport",
        ha="center",va="center",fontsize=5.4,color=C["ink"],
        bbox=dict(boxstyle="round,pad=0.4",fc="#F2F4F6",ec="none"))
def row(y,col,pred,meas):
    ax.add_patch(plt.Rectangle((0.3,y-0.7),3.9,1.4,fc=col,ec="white",lw=0.8,alpha=0.18))
    ax.text(2.25,y,pred,ha="center",va="center",fontsize=4.9,color=col if col!=C["poly"] else C["poly"],fontweight="bold")
    ax.annotate("",xy=(5.7,y),xytext=(4.3,y),arrowprops=dict(arrowstyle="-|>",color=col,lw=1.3))
    ax.text(4.98,y+0.45,"predicts",ha="center",fontsize=4.4,style="italic",color=C["ink"])
    ax.add_patch(plt.Rectangle((5.8,y-0.7),3.9,1.4,fc=col,ec="white",lw=0.8,alpha=0.10))
    ax.text(7.75,y,meas,ha="center",va="center",fontsize=4.9,color=C["ink"])
row(6.1,C["poly"],"poly: $\\Phi_{inj}$=3.07 eV\n+ 47.5% sequestered",
    "Al$^{3+}$ flat ~5 at%\n1592 cyc @1C, CE~100%")
row(3.9,C["bare"],"bare: $\\Phi_{inj}$=0 (leaky)\nno sequestration",
    "Al$^0$ $\\uparrow$ to ~10 at%\ndies ~270 cyc")
ax.text(2.25,7.05,"predicted (descriptor)",ha="center",fontsize=4.8,style="italic",color=C["ink"])
ax.text(7.75,7.05,"measured (experiment)",ha="center",fontsize=4.8,style="italic",color=C["ink"])
ax.text(5,1.6,"top-down design loop closes:\nscreen $\\to$ predict $\\to$ validate",
        ha="center",va="center",fontsize=5.0,color=C["green"],fontweight="bold")
ax.set_title("Validation against experiment",fontsize=7.5,pad=2)
fig.text(0.55,0.49,"d",fontsize=10,fontweight="bold")

os.makedirs(os.path.dirname(OUT),exist_ok=True)
save_pub(fig,OUT)
print("Fig7 (top-down design rule) done")
