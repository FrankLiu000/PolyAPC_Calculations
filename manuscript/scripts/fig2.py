# -*- coding: utf-8 -*-
"""Figure 2 - battery performance (positive results). Angew double-column.
Li-Fig5-aligned: capacity+CE vs cycle (open markers/cycle), charge/discharge voltage
profiles at selected cycles; PLUS my symmetric V-t and bare/poly contrast (kept).
Scripted plots of measured data (NOT AI-generated). CVD-safe palette + shape coding."""
import sys, csv
sys.path.insert(0, r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad")
from angew_style import *
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (enables projection='3d')
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=r"D:/20260602_polyAPC_data"
SC=r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad/mo6s8_out"
OUT=ROOT+"/Angewandte_Research_Article/figures/Fig2_performance"
def rd(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))
def col(rows,k,t=float): return np.array([t(r[k]) for r in rows])

b05=rd(ROOT+"/MgMo6S8_0.5C_cycle/results/data/percycle_bare_0p5C.csv")
p05=rd(ROOT+"/MgMo6S8_0.5C_cycle/results/data/percycle_poly_0p5C.csv")
p1c=rd(ROOT+"/MgMo6S8_1C_cycle/results/data/percycle_poly_1C.csv")
prof=rd(SC+"/profiles_poly_1C.csv")
tp=rd(ROOT+"/MgMg/results/data/SPE_poly_trace_downsampled.csv")
tb=rd(ROOT+"/MgMg/results/data/LE_bare_trace_downsampled.csv")

def twin_fix(ax,ax2): ax.tick_params(axis="y",which="both",right=False); ax2.tick_params(axis="x",which="both",top=False)

# 3-row layout. Row 2 (panel e) is now a 3D scatter "cube" and needs a tall,
# roughly-square footprint: the cube lives in gs[2,0:2], with the confidence
# key + provenance note stacked in the narrow right column gs[2,2].
#   row 0: (a)(b)(c) cycling + voltage profiles
#   row 1: (d) Mg||Mg symmetric V-t  -- full width
#   row 2: (e) 3D (cycle x rate x CE) Pareto cube + legend/notes column
fig=plt.figure(figsize=(W2,1.62*W2))
gs=fig.add_gridspec(3,3,height_ratios=[1.0,0.82,1.62],hspace=0.42,wspace=0.42,
                    left=0.07,right=0.945,top=0.975,bottom=0.045)

def cap_panel(ax,rowsets,title,xmax,cut=None,ref=None):
    for rows,sty,fc in rowsets:
        c=col(rows,"cycle"); d=col(rows,"dis_spec_mAhg")
        m=c<=cut if cut else np.ones(len(c),bool)
        ax.plot(c[m],d[m],ls="none",marker=sty,ms=2.3,mfc="none",mec=fc,mew=0.55,markevery=1)
    ax.set_xlim(0,xmax); ax.set_ylim(0,110)
    ax.set_xlabel("Cycle number"); ax.set_ylabel("Capacity (mAh g$^{-1}$)")
    ax.set_title(title,pad=3)
    ax2=ax.twinx(); ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(True)
    for rows,sty,fc in rowsets:
        c=col(rows,"cycle"); ce=col(rows,"CE_pct"); m=(ce>90)&(ce<102)&(c<=cut if cut else True)
        ax2.plot(c[m],ce[m],ls="none",marker=sty,ms=1.6,mfc=C["accent"],mec="none",alpha=0.7,markevery=1)
    ax2.set_ylim(40,103); ax2.set_ylabel("CE (%)",color=C["accent"]); ax2.tick_params(axis="y",colors=C["accent"])
    twin_fix(ax,ax2); return ax2

# (a) 0.5C poly vs bare
ax=fig.add_subplot(gs[0,0])
cap_panel(ax,[(p05,"o",C["poly"]),(b05,"s",C["bare"])],"Mg‖Mo$_6$S$_8$, 0.5C",900)
ax.text(440,64,"poly",color=C["poly"],fontsize=6.2,fontweight="bold")
ax.text(250,22,"bare",color=C["bare_d"],fontsize=6.2,fontweight="bold")
panel_label(ax,"a")

# (b) 1C poly to 1592
ax=fig.add_subplot(gs[0,1])
cap_panel(ax,[(p1c,"o",C["poly"])],"Mg‖Mo$_6$S$_8$, 1C",1680,cut=1592,ref=48.7)
ax.axvline(1592,ls=(0,(4,2)),color="black",lw=0.7); ax.text(1560,92,"1592 cyc\n>80%",fontsize=5.4,ha="right")
panel_label(ax,"b")

# (c) charge/discharge voltage profiles at selected cycles (Li Fig5b)  -- ADDED
ax=fig.add_subplot(gs[0,2])
cycles=[5,100,500,1000,1500]
shades=["#9ecae1","#6baed6","#3182bd","#08519c","#08306b"]
for cy,sh in zip(cycles,shades):
    sub=[r for r in prof if int(r["cycle"])==cy]
    for branch in ("D","C"):
        seg=[(float(r["spec_mAhg"]),float(r["V"])) for r in sub if r["state"].endswith(branch)]
        if seg:
            seg=np.array(seg)
            ax.plot(seg[:,0],seg[:,1],color=sh,lw=0.8)
ax.set_xlim(0,55); ax.set_ylim(0.2,2.0)
ax.set_xlabel("Specific capacity (mAh g$^{-1}$)"); ax.set_ylabel("Voltage (V)")
ax.set_title("Voltage profiles, 1C (poly)",pad=3)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([0],[0],color=s,lw=1.4,label=f"{c}") for c,s in zip(cycles,shades)],
          fontsize=5.2,loc="lower left",title="cycle",title_fontsize=5.4,handlelength=1.4,ncol=2,columnspacing=0.7)
panel_label(ax,"c")

# (d) Mg||Mg symmetric V-t (KEPT - Li lacks this in Fig5) -- now spans the full row
ax=fig.add_subplot(gs[1,0:3])
th_b=col(tb,"t_h"); V_b=col(tb,"V"); th_p=col(tp,"t_h"); V_p=col(tp,"V")
ax.plot(th_p,V_p,color=C["poly"],lw=0.35,label="poly-APC")
ax.plot(th_b,V_b,color=C["bare"],lw=0.35,label="bare-APC")
ax.axhline(0,color="0.75",lw=0.5,zorder=0)
ax.annotate("short-circuit\n(cyc 420)",xy=(840,-0.05),xytext=(960,-0.50),fontsize=5.8,color=C["ink"],ha="center",
            arrowprops=dict(arrowstyle="->",color=C["ink"],lw=0.7))
ax.text(1490,0.50,"poly-APC: 2022 h, 1011 cyc, short-free",color=C["poly"],fontsize=6.2,fontweight="bold",ha="center")
ax.set_xlim(0,2100); ax.set_ylim(-0.7,0.7)
ax.set_xlabel("Time (h)"); ax.set_ylabel("Voltage (V)")
ax.set_title("Mg‖Mg symmetric cell, 0.5 mA cm$^{-2}$ / 0.5 mAh cm$^{-2}$",pad=3)
ax.legend(loc="lower left",ncol=2,fontsize=6.2,handlelength=1.4,columnspacing=1.0)
axin=ax.inset_axes([0.40,0.64,0.20,0.31])
for th,V,cl in [(th_p,V_p,C["poly"]),(th_b,V_b,C["bare"])]:
    w=(th>=100)&(th<=110); axin.plot(th[w],V[w],color=cl,lw=0.6)
axin.set_xlim(100,110); axin.set_ylim(-0.35,0.35); axin.set_title("100–110 h",fontsize=5.4,pad=1)
axin.tick_params(labelsize=5); axin.set_xlabel("t (h)",fontsize=5,labelpad=1); axin.set_ylabel("V",fontsize=5,labelpad=1)
panel_label(ax,"d",x=-0.065)

# (e) 3D scatter "cube": cycle number (x) x rate (y) x Coulombic efficiency (z).
# Real CSV values only. Honest rendering: position = the three dimensions,
# fill = confidence, this-work = blue stars. matplotlib's 3D log scaling is
# unreliable, so x and y are plotted as log10(value) with custom tick labels.
# Conclusion landed: poly-APC Mg||Mo6S8 sits on the 3D Pareto front of
# (cycle life, rate, CE) -- highest CE among long-cycle Mg full cells, at a
# practical 1C, between the ultralow-rate early benchmark (Aurbach) and the
# extreme-rate longest-cycle outlier (MLCC).
from matplotlib.lines import Line2D as _L2D
# 11 authoritative points: (label, first_author, year, cycle, rate_C, CE, confidence, this_work)
PTS=[
    ("this work 1C","this work",2026, 1592, 1.0,  99.9,"hero",True),
    ("this work 0.5C","this work",2026, 842, 0.5,  99.9,"hero",True),
    ("Aurbach 2000","Aurbach",2000,    2000, 0.05, 99.5,"high",False),
    ("Mohtadi 2012","Mohtadi",2012,      40, 1.0,  94.0,"med", False),
    ("Kim 2011","Kim",2011,             300, 0.2,  98.5,"med", False),
    ("Pan 2016","Pan",2016,            1000, 1.0,  99.2,"high",False),
    ("Yoo 2017","Yoo",2017,             400, 1.0,  99.0,"high",False),
    ("Nguyen 2020","Nguyen",2020,       100, 0.1,  99.4,"high",False),
    ("PTB gel 2023","(quasi-solid)",2023,250, 0.5, 95.0,"med", False),
    ("MLCC 2023","Fan",2023,          10000, 50.0, 99.0,"med", False),
    ("Yang 2026","Yang",2026,           500, 0.5,  99.5,"low", False),
]
def lx(v): return np.log10(float(v))   # x = log10(cycle)
def ly(v): return np.log10(float(v))   # y = log10(rate)
# confidence -> fill (shape+fill so it survives grayscale): high=dark, med=gray, low=open
CONF_FC={"high":C["ink"],"med":"#AFAFAF","low":"white"}
Z0=93.5                                # cube floor (z-min) -- stems drop to here

axb=fig.add_subplot(gs[2,0:2],projection="3d")
axb.set_box_aspect((1.0,1.0,0.95))     # roughly cubic
axb.view_init(elev=20,azim=-58)
# Pull the 3D cube out to fill its cell (mplot3d leaves wide internal margins);
# grow leftward/upward into the empty corner so ticks+labels stay readable.
_p=axb.get_position()
axb.set_position([_p.x0-0.045, _p.y0-0.050, _p.width+0.075, _p.height+0.060])

# axis ranges (plotted in log10 for x,y)
X_TK=[10,100,1000,10000]; Y_TK=[0.05,0.1,1,10,50]
xlo,xhi=lx(8),lx(14000); ylo,yhi=ly(0.04),ly(60); zlo,zhi=Z0,100.3
axb.set_xlim(xlo,xhi); axb.set_ylim(ylo,yhi); axb.set_zlim(zlo,zhi)

# --- faint vertical stems from each point to the cube floor (z=Z0): depth cue ---
for lab,fa,yr,cyc,rate,ce,conf,tw in PTS:
    axb.plot([lx(cyc),lx(cyc)],[ly(rate),ly(rate)],[Z0,ce],
             color="0.55",lw=0.45,ls="-",zorder=1,alpha=0.7)
    axb.scatter([lx(cyc)],[ly(rate)],[Z0],s=3,marker=".",color="0.6",zorder=1)  # floor foot

# --- 3D Pareto front: non-dominated trio (this-work-1C, Aurbach, MLCC) ---
PF=[("this work 1C",1592,1.0,99.9),("Aurbach 2000",2000,0.05,99.5),("MLCC 2023",10000,50.0,99.0)]
pfx=[lx(c) for _,c,_,_ in PF]; pfy=[ly(r) for _,_,r,_ in PF]; pfz=[z for *_,z in PF]
# faint translucent triangular surface spanning the trio
tri=Poly3DCollection([list(zip(pfx,pfy,pfz))],facecolor=C["green"],alpha=0.13,
                     edgecolor="none",zorder=2)
axb.add_collection3d(tri)
# bold connecting line through the three non-dominated cells
axb.plot(pfx,pfy,pfz,color=C["green"],lw=1.6,ls="-",zorder=5,solid_capstyle="round")

# --- literature points (open/gray/dark by confidence) ---
for lab,fa,yr,cyc,rate,ce,conf,tw in PTS:
    if tw: continue
    fc=CONF_FC.get(conf,"white")
    axb.scatter([lx(cyc)],[ly(rate)],[ce],s=26,marker="o",
                facecolor=fc,edgecolor=C["ink"],linewidths=0.7,depthshade=False,zorder=6)

# --- this-work stars (hero): drawn last so they sit on top ---
for lab,fa,yr,cyc,rate,ce,conf,tw in PTS:
    if not tw: continue
    axb.scatter([lx(cyc)],[ly(rate)],[ce],s=200,marker="*",
                facecolor=C["poly"],edgecolor="white",linewidths=0.9,depthshade=False,zorder=10)

# --- short author-year text labels near key points (small offsets, 3D text) ---
# offsets hand-tuned in data space (dz in CE-%, ddx/ddy in log10 units) to clear
# both the markers and the star cluster at high CE.
TXT={  # label -> (dz, ddx, ddy, ha, color)
    "Aurbach 2000": (-1.10,  0.10, 0.00,"left",  C["ink"]),   # drop below to clear stars
    "MLCC 2023":    (-1.25, -0.02,-0.12,"right", C["ink"]),   # drop below + toward viewer, clear front line
    "Pan 2016":     (-1.35, -0.06, 0.00,"right", C["ink"]),
    "Nguyen 2020":  ( 0.70, -0.06, 0.00,"right", C["ink"]),
    "Yang 2026":    (-1.05,  0.00,-0.10,"center",C["ink"]),
}
for lab,fa,yr,cyc,rate,ce,conf,tw in PTS:
    if lab in TXT:
        dz,ddx,ddy,ha,cl=TXT[lab]
        axb.text(lx(cyc)+ddx,ly(rate)+ddy,ce+dz,f"{fa} {yr}",fontsize=5.0,color=cl,
                 ha=ha,va="center",zorder=11)
# "this work" label above-left of the star pair, clear of "Pareto front"
axb.text(lx(700)-0.05,ly(0.6),99.9+1.05,"this work",fontsize=6.2,color=C["poly"],
         fontweight="bold",ha="right",va="center",zorder=12)
# Pareto-front label, ride along the trio (mid-segment toward MLCC, above the line)
axb.text(lx(4200),ly(12),99.0+0.95,"Pareto front",fontsize=5.6,color=C["green"],
         fontweight="bold",ha="center",va="center",zorder=11)
# "better ->" cue toward the favorable corner (high cycle, high rate, high CE)
axb.text(lx(150),ly(30),100.1,"better →",fontsize=5.8,color="#444444",
         style="italic",ha="left",va="center",zorder=11)

# --- axes: custom log10 ticks + labels ---
axb.set_xticks([lx(v) for v in X_TK]); axb.set_xticklabels(["10","100","1k","10k"])
axb.set_yticks([ly(v) for v in Y_TK]); axb.set_yticklabels(["0.05","0.1","1","10","50"])
axb.set_zticks([94,96,98,100])
axb.set_xlabel("Cycle number",labelpad=-4,fontsize=7.0)
axb.set_ylabel("Rate (C)  ·  1C=128.8 mA g$^{-1}$",labelpad=-3,fontsize=6.4)
axb.set_zlabel("CE (%)",labelpad=-5,fontsize=7.0)
axb.tick_params(axis="x",pad=-2.5,labelsize=6.0)
axb.tick_params(axis="y",pad=-2.5,labelsize=6.0)
axb.tick_params(axis="z",pad=0.5,labelsize=6.0)
# Title as text2D (axes-fraction) so growing the 3D box doesn't clip set_title.
axb.text2D(0.52,0.99,"Mg full-cell benchmark cube: cycle × rate × CE",
           transform=axb.transAxes,fontsize=8.0,ha="center",va="top")

# light panes, subtle gridlines, thin axis lines (Angew restraint)
for pane in (axb.xaxis,axb.yaxis,axb.zaxis):
    pane.pane.set_facecolor((1,1,1,0.0)); pane.pane.set_edgecolor((0.6,0.6,0.6,0.4))
    pane.pane.set_alpha(0.04); pane._axinfo["grid"].update(color="#D7DBE0",linewidth=0.4)
    pane.line.set_linewidth(0.7); pane.line.set_color("0.5")

# panel label: Axes3D.text() has a 3D signature, so use text2D (axes-fraction)
axb.text2D(0.02,0.94,"e",transform=axb.transAxes,fontsize=10,fontweight="bold",
           va="bottom",ha="left")

# ---- legend / notes column (gs[2,2]): confidence key + provenance note ----
axl=fig.add_subplot(gs[2,2]); axl.axis("off")
conf_handles=[
    _L2D([0],[0],marker="*",ls="none",ms=12,mfc=C["poly"],mec="white",mew=0.6,label="this work"),
    _L2D([0],[0],marker="o",ls="none",ms=6,mfc=C["ink"],mec=C["ink"],mew=0.7,label="high conf."),
    _L2D([0],[0],marker="o",ls="none",ms=6,mfc="#AFAFAF",mec=C["ink"],mew=0.7,label="med conf."),
    _L2D([0],[0],marker="o",ls="none",ms=6,mfc="white",mec=C["ink"],mew=0.7,label="low / unconf."),
    _L2D([0],[0],color=C["green"],lw=1.6,label="Pareto front"),
    _L2D([0],[0],color="0.55",lw=0.7,label="stem → (cycle, rate)"),
]
leg=axl.legend(handles=conf_handles,loc="upper center",fontsize=6.0,handlelength=1.6,
               labelspacing=0.85,handletextpad=0.7,borderpad=0.8,framealpha=1.0,
               edgecolor="#BBBBBB",facecolor="white",bbox_to_anchor=(0.5,0.98),
               title="confidence key",title_fontsize=6.4)
leg.get_frame().set_linewidth(0.6)
axl.add_artist(leg)
axl.text(0.5,0.30,"non-aqueous Mg-metal full cells;\nvalues as reported (Table S1);\nopen = not independently confirmed",
         transform=axl.transAxes,fontsize=4.8,color="#666666",ha="center",va="top",linespacing=1.5)

import os; os.makedirs(os.path.dirname(OUT),exist_ok=True)
save_pub(fig,OUT)
print("Figure 2 reworked (added voltage profiles; kept symmetric V-t)")
