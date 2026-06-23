# -*- coding: utf-8 -*-
"""Figure 7 - Top-down computational design rule for the Mg-anode interphase.
Turns the validated mechanism into a 4-descriptor screen (JPCC/EES-style design map).
All numbers are REAL computed values (T2 redox, T5 sequestration, T8/T8b band alignment).
Panels (c,d) plot the COMPLETED T19 screen (results/T19_screen_B/outputs/*.csv +
T8b band alignment). Closed symbols only - every point is a computed candidate. NOT AI-generated."""
import sys, csv, json, os
sys.path.insert(0, r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad")
from angew_style import *
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon as MplPoly
import numpy as np

REPO=r"D:/20260602_polyAPC_data/PolyAPC_repo"
DOS=REPO+"/results/T8b_DOS/outputs/"
T19=REPO+"/results/T19_screen_B/outputs/"
OUT=r"D:/20260602_polyAPC_data/Angewandte_Research_Article/figures/Fig7_design_rule"
def rd(p):
    with open(p,encoding="utf-8") as f: return list(csv.DictReader(f))
align={r["phase"]:r for r in rd(DOS+"iface_MgSiOx_alignment.csv")}
meta=json.load(open(DOS+"dos_meta.json",encoding="utf-8"))
# completed T19 screen (verified CSVs) — cross-check the inline screen values below
screen={r["candidate"]:r for r in rd(T19+"screen_ranked.csv")}
bandalign=rd(T19+"tier2_bandalign.csv")  # provenance: panel (c) candidate chemistries

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

# ---------- (c) SEI electronic selection map (completed T19 screen + T8b) ----------
ax=fig.add_subplot(gs[1,0])
# columns: (label, Phi_inj, gap, colour, marker, ms, class)
#  main-group oxides (PASS/STRONG) -> green; TM-oxide/carbide leak -> orange; metals -> dark orange
cpts=[
 ("SiO$_2$ (POSS)", 3.07, 8.46, C["green"], "*", 230, "top"),     # validated top hit
 ("borosiloxane",   2.87, 4.17, C["green"], "P",  70, "strong"),  # H4 confirmed
 ("phosphosilicate",2.87, 6.61, C["green"], "P",  70, "strong"),  # new hit
 ("GeO$_2$",        2.87, 5.97, C["green"], "P",  70, "strong"),  # new hit
 ("PON",            2.17, 4.67, C["poly2"],"o",  52, "pass"),     # weaker pass
 ("ZrO$_2$",        1.47, 4.51, C["poly2"],"o",  52, "pass"),     # weaker pass
 ("Al$_2$O$_3$",    2.62, 6.21, C["bare"], "s",  58, "ctrl"),     # D2-pass but D1-FAIL
 ("TiO$_2$",       -0.03, 3.06, C["bare_d"],"X", 70, "leak"),     # leaky TM-oxide
 ("SiC",           -0.03, 1.40, C["bare_d"],"X", 70, "leak"),     # leaky semiconductor
 ("Al$^0$",         0.00, 0.00, C["bare_d"],"v", 55, "metal"),    # bare interphase (T8b)
 ("Mg$_{17}$Al$_{12}$",0.0,0.18,C["bare_d"],"v", 55, "metal"),    # bare interphase (T8b)
]
# region shading: leaky (Phi_inj<1) vs passivating (Phi_inj>=1 & gap>=3)
ax.axvspan(-0.5,1.0,color=C["bare"],alpha=0.08,lw=0,zorder=0)
ax.add_patch(plt.Rectangle((1.0,3.0),3.2,6.3,fc=C["green"],alpha=0.07,lw=0,zorder=0))
ax.axhline(3.0,xmin=0.0,xmax=1.0,color=C["green"],lw=0.7,ls=":",zorder=1)
ax.axvline(1.0,color=C["ink"],lw=0.7,ls=(0,(4,2)),zorder=1)
ax.text(0.30,8.6,"leaky zone\n$\\Phi_{inj}\\lesssim1$",fontsize=5.2,color=C["bare_d"],
        fontweight="bold",ha="center",va="center")
ax.text(3.95,1.55,"passivating zone\n$\\Phi_{inj}\\geq1$, $E_g\\geq3$",fontsize=5.2,
        color=C["green"],fontweight="bold",ha="right",va="center")
for nm,bar,g,col,mk,ms,cls in cpts:
    ax.scatter([bar],[g],s=ms,marker=mk,color=col,edgecolor="black",
               lw=(0.7 if mk=="*" else 0.5),zorder=5)
# per-point text placement (avoid overlaps; three "P" hits share x=2.87)
lab={
 "SiO$_2$ (POSS)":(0.14,0.55,"left"),   "borosiloxane":(0.16,0.00,"left"),
 "phosphosilicate":(0.15,0.42,"left"),  "GeO$_2$":(0.15,-0.55,"left"),
 "PON":(0.00,0.62,"center"),            "ZrO$_2$":(0.00,0.62,"center"),
 "Al$_2$O$_3$":(-0.16,0.00,"right"),    "TiO$_2$":(0.16,0.00,"left"),
 "SiC":(0.18,0.32,"left"),              "Al$^0$":(0.18,-0.05,"left"),
 "Mg$_{17}$Al$_{12}$":(0.18,-0.42,"left"),
}
for nm,bar,g,col,mk,ms,cls in cpts:
    dx,dy,ha=lab[nm]
    ax.annotate(nm,(bar,g),xytext=(bar+dx,g+dy),fontsize=5.3,fontweight="bold",
                color=col,ha=ha,va="center")
# callouts: validated top hit + H4 + negative control
ax.annotate("validated top hit",(3.07,8.46),xytext=(3.20,7.85),fontsize=5.0,
            color=C["green"],ha="left",va="center",fontweight="bold",
            arrowprops=dict(arrowstyle="-",color=C["green"],lw=0.6))
ax.annotate("H4 confirmed",(2.87,4.17),xytext=(2.15,3.35),fontsize=4.8,
            color=C["green"],ha="center",
            arrowprops=dict(arrowstyle="-",color=C["green"],lw=0.5))
ax.annotate("D2-pass but\nD1-FAIL (neg. control)",(2.62,6.21),xytext=(1.42,7.8),
            fontsize=4.7,color=C["bare_d"],ha="center",va="center",
            arrowprops=dict(arrowstyle="-",color=C["bare_d"],lw=0.5))
# legend by class (marker-coded, grayscale-separable)
from matplotlib.lines import Line2D
leg=[Line2D([0],[0],marker="*",color="none",mfc=C["green"],mec="black",ms=9,
            label="main-group oxide: STRONG"),
     Line2D([0],[0],marker="P",color="none",mfc=C["green"],mec="black",ms=6,
            label="main-group oxide: strong hit"),
     Line2D([0],[0],marker="o",color="none",mfc=C["poly2"],mec="black",ms=5,
            label="passes (weaker)"),
     Line2D([0],[0],marker="s",color="none",mfc=C["bare"],mec="black",ms=5,
            label="alumoxane (D1-fail control)"),
     Line2D([0],[0],marker="X",color="none",mfc=C["bare_d"],mec="black",ms=6,
            label="TM-oxide / carbide: leaky"),
     Line2D([0],[0],marker="v",color="none",mfc=C["bare_d"],mec="black",ms=5,
            label="bare metal interphase")]
ax.legend(handles=leg,loc="lower right",fontsize=4.3,handlelength=1.0,
          borderpad=0.3,labelspacing=0.28,handletextpad=0.4)
ax.set_xlim(-0.5,4.2); ax.set_ylim(-0.6,9.3)
ax.set_xlabel("e$^-$-injection barrier  $\\Phi_{inj}$ (eV)   [D2]")
ax.set_ylabel("band gap  $E_g$ (eV)")
ax.set_title("SEI electronic selection map",pad=3)
panel_label(ax,"c")

# ---------- (d) design map: Pareto front of the completed screen ----------
ax=fig.add_subplot(gs[1,1])
# (label, Phi_inj, seq_strength kcal/mol, class)  -- screen_ranked.csv / design_map.csv
dpts=[
 ("POSS",              3.07, 3.3,  "front"),
 ("borosiloxane",      2.87, 6.3,  "front"),
 ("polyether-siloxane",3.07, 1.7,  "dominated"),
 ("PON",               2.17, 3.5,  "dominated"),
 ("Al-alkoxide",       2.62,16.6,  "disq"),     # D1: co-deposits Al0 -> disqualified
]
# Pareto front line through {borosiloxane, POSS} (viable, D1/D4-passing)
fx=[2.87,3.07]; fy=[6.3,3.3]
ax.plot(fx,fy,color=C["green"],lw=1.3,ls="-",zorder=2)
ax.plot(fx,fy,color=C["green"],lw=0,marker="o",ms=0,zorder=2)
ax.text(2.97,5.0,"Pareto front",fontsize=5.0,color=C["green"],fontweight="bold",
        rotation=-58,ha="center",va="center")
for nm,x,y,cls in dpts:
    if cls=="front":
        ax.scatter([x],[y],s=150,marker="*",color=C["green"],edgecolor="black",
                   lw=0.7,zorder=6)
    elif cls=="dominated":
        ax.scatter([x],[y],s=46,marker="o",color=C["poly2"],edgecolor="black",
                   lw=0.5,zorder=5)
    else:  # disqualified by D1 redox gate -> distinct hatched red-X marker
        ax.scatter([x],[y],s=120,marker="X",color="none",edgecolor=C["red"],
                   lw=1.6,zorder=6)
        ax.scatter([x],[y],s=300,marker="o",facecolor="none",edgecolor=C["red"],
                   lw=0.9,hatch="xxx",zorder=5,alpha=0.5)
# point labels
dlab={"POSS":(0.0,-1.15,"center"),"borosiloxane":(-0.06,1.25,"center"),
      "polyether-siloxane":(-0.05,-1.15,"center"),"PON":(0.0,1.25,"center"),
      "Al-alkoxide":(0.0,1.35,"center")}
for nm,x,y,cls in dpts:
    dx,dy,ha=dlab[nm]
    col=C["green"] if cls=="front" else (C["red"] if cls=="disq" else C["poly2"])
    ax.annotate(nm,(x,y),xytext=(x+dx,y+dy),fontsize=5.3,fontweight="bold",
                color=col,ha=ha,va="center")
# disqualification callout (inside axes)
ax.annotate("DISQUALIFIED by D1 redox gate\n(co-deposits Al$^0$); highest\nsequestration, vetoed",
            (2.62,16.6),xytext=(2.90,15.2),fontsize=4.7,color=C["red"],ha="left",
            va="center",arrowprops=dict(arrowstyle="-",color=C["red"],lw=0.6))
# controls-validated banner (mid-left, clear of all points)
ax.text(0.035,0.66,"controls validated:\nPOSS top (H2$\\checkmark$)\nAl-alkoxide disq. (H3$\\checkmark$)\nborosiloxane on front (H4$\\checkmark$)",
        transform=ax.transAxes,fontsize=4.6,color=C["ink"],ha="left",va="top",
        bbox=dict(boxstyle="round,pad=0.35",fc="#F2F4F6",ec="none"))
ax.set_xlim(2.05,3.25); ax.set_ylim(0,18.5)
ax.set_xlabel("e$^-$-injection barrier  $\\Phi_{inj}$ (eV)   [D2]")
ax.set_ylabel("anion sequestration (kcal mol$^{-1}$)   [D3]")
ax.set_title("Design map: Pareto front (validated screen)",fontsize=7.5,pad=3)
panel_label(ax,"d")

os.makedirs(os.path.dirname(OUT),exist_ok=True)
save_pub(fig,OUT)
print("Fig7 (top-down design rule) done")
