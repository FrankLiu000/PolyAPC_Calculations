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

fig=plt.figure(figsize=(W2,0.74*W2))
gs=fig.add_gridspec(2,3,height_ratios=[1,0.92],hspace=0.46,wspace=0.42,
                    left=0.07,right=0.945,top=0.95,bottom=0.10)

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

# (d) Mg||Mg symmetric V-t (KEPT - Li lacks this in Fig5)
ax=fig.add_subplot(gs[1,:])
th_b=col(tb,"t_h"); V_b=col(tb,"V"); th_p=col(tp,"t_h"); V_p=col(tp,"V")
ax.plot(th_p,V_p,color=C["poly"],lw=0.35,label="poly-APC")
ax.plot(th_b,V_b,color=C["bare"],lw=0.35,label="bare-APC")
ax.axhline(0,color="0.75",lw=0.5,zorder=0)
ax.annotate("short-circuit (cyc 420)",xy=(840,-0.05),xytext=(560,0.42),fontsize=6,color=C["ink"],
            arrowprops=dict(arrowstyle="->",color=C["ink"],lw=0.7))
ax.text(1500,0.42,"poly-APC: 2022 h, 1011 cyc, short-free",color=C["poly"],fontsize=6.5,fontweight="bold",ha="center")
ax.set_xlim(0,2100); ax.set_ylim(-0.7,0.7)
ax.set_xlabel("Time (h)"); ax.set_ylabel("Voltage (V)")
ax.set_title("Mg‖Mg symmetric cell, 0.5 mA cm$^{-2}$ / 0.5 mAh cm$^{-2}$",pad=3)
ax.legend(loc="lower left",ncol=2,fontsize=6.5,handlelength=1.6)
axin=ax.inset_axes([0.085,0.62,0.26,0.33])
for th,V,cl in [(th_p,V_p,C["poly"]),(th_b,V_b,C["bare"])]:
    w=(th>=100)&(th<=110); axin.plot(th[w],V[w],color=cl,lw=0.6)
axin.set_xlim(100,110); axin.set_ylim(-0.35,0.35); axin.set_title("100–110 h",fontsize=5.4,pad=1)
axin.tick_params(labelsize=5); axin.set_xlabel("t (h)",fontsize=5,labelpad=1); axin.set_ylabel("V",fontsize=5,labelpad=1)
panel_label(ax,"d",x=-0.045)

import os; os.makedirs(os.path.dirname(OUT),exist_ok=True)
save_pub(fig,OUT)
print("Figure 2 reworked (added voltage profiles; kept symmetric V-t)")
