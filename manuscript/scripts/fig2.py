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

fig=plt.figure(figsize=(W2,0.80*W2))
gs=fig.add_gridspec(2,3,height_ratios=[1,0.92],hspace=0.50,wspace=0.42,
                    left=0.07,right=0.945,top=0.955,bottom=0.095)

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

# (d) Mg||Mg symmetric V-t (KEPT - Li lacks this in Fig5) -- now spans 2 cols
ax=fig.add_subplot(gs[1,0:2])
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
axin=ax.inset_axes([0.40,0.66,0.27,0.30])
for th,V,cl in [(th_p,V_p,C["poly"]),(th_b,V_b,C["bare"])]:
    w=(th>=100)&(th<=110); axin.plot(th[w],V[w],color=cl,lw=0.6)
axin.set_xlim(100,110); axin.set_ylim(-0.35,0.35); axin.set_title("100–110 h",fontsize=5.4,pad=1)
axin.tick_params(labelsize=5); axin.set_xlabel("t (h)",fontsize=5,labelpad=1); axin.set_ylabel("V",fontsize=5,labelpad=1)
panel_label(ax,"d",x=-0.065)

# (e) Literature Pareto-front benchmark: cycle life vs CE (Mg full cells) -- ADDED
# Real values only (CSV); honest rendering: confidence -> marker fill, rate -> annotated.
axb=fig.add_subplot(gs[1,2])
def rd_lit(p):
    # tolerant reader: one literature `cathode` value contains an unquoted comma
    # (e.g. "1,4-PAQ (organic)"), which over-splits that row. Re-merge extra
    # field(s) into `cathode` so every column realigns. No values are altered.
    with open(p,encoding="utf-8") as f:
        rdr=csv.reader(f); hdr=next(rdr); n=len(hdr); ci=hdr.index("cathode")
        out=[]
        for cells in rdr:
            if not cells: continue
            if len(cells)>n:
                extra=len(cells)-n
                cells=cells[:ci]+[",".join(cells[ci:ci+1+extra])]+cells[ci+1+extra:]
            out.append(dict(zip(hdr,cells)))
        return out
lb=rd_lit(ROOT+"/PolyAPC_repo/results/lit_benchmark/mg_fullcell_benchmark.csv")
rows_ce=[r for r in lb if r["CE_pct"].strip().upper()!="NA"]   # CE-less rows are SI-table only
# confidence -> fill style (shape+fill so it survives grayscale): high=dark fill, med=gray, low=open
CONF_FC={"high":C["ink"],"med":"#B0B0B0","low":"none"}
def msz(rate):  # marker size grows ~ with log10(rate); keeps 0.05C small, 50C large
    return 4.0+2.3*np.log10(float(rate)*20.0+1.0)
# --- literature points ---
for r in rows_ce:
    if r["this_work"].strip()=="1": continue
    cyc=float(r["cycle"]); ce=float(r["CE_pct"]); rate=float(r["rate_C"]); conf=r["confidence"].strip()
    fc=CONF_FC.get(conf,"none")
    axb.plot(cyc,ce,marker="o",ls="none",ms=msz(rate),mfc=fc,mec=C["ink"],mew=0.7,zorder=3)
# --- Pareto frontier (non-dominated: maximise BOTH cycle and CE) over the plotted CE rows ---
pts=sorted([(float(r["cycle"]),float(r["CE_pct"])) for r in rows_ce])
front=[]
best_ce=-1e9
for cyc,ce in sorted(pts,key=lambda t:-t[0]):   # high cycle -> low; keep running max CE
    if ce>best_ce+1e-9:
        front.append((cyc,ce)); best_ce=ce
front=sorted(front)                              # ascending cycle for drawing
fx=[p[0] for p in front]; fy=[p[1] for p in front]
# extend the stepped front to the axis edges so the shaded non-dominated region reads clearly
fx_d=[fx[0]]+fx+[14000]; fy_d=[fy[0]]+fy+[fy[-1]]
axb.fill_between(fx_d,fy_d,92,step="pre",color=C["green"],alpha=0.10,lw=0,zorder=0)
axb.step(fx_d,fy_d,where="pre",color=C["green"],lw=1.2,ls=(0,(4,1.8)),zorder=2,alpha=0.95)
# --- anchor labels (first_author + year) + rate; offsets hand-tuned to avoid overlap ---
ANCH={"Aurbach 2000":(8,3,"left"),"MLCC 2023":(2,-13,"center"),"Pan 2016":(-7,-6,"right"),
      "Yoo 2017":(-7,-3,"right"),"Nguyen 2020":(-7,1,"right")}
RLAB={"Aurbach 2000":"0.05C","MLCC 2023":"50C","Pan 2016":"1C","Yoo 2017":"1C","Nguyen 2020":"0.1C"}
for r in rows_ce:
    lab=r["label"].strip()
    if lab in ANCH and r["this_work"].strip()!="1":
        cyc=float(r["cycle"]); ce=float(r["CE_pct"]); dx,dy,ha=ANCH[lab]
        axb.annotate(f"{r['first_author']} {r['year']}",xy=(cyc,ce),xytext=(dx,dy),
                     textcoords="offset points",fontsize=5.0,color=C["ink"],ha=ha,va="center",zorder=7)
        dyr=dy+(6 if dy>=0 else -5)
        axb.annotate(RLAB[lab],xy=(cyc,ce),xytext=(dx,dyr),textcoords="offset points",
                     fontsize=4.5,color="#666666",ha=ha,va="center",zorder=7)
# --- this-work stars (dominant): drawn last so they sit on top; labels splayed apart ---
tw=sorted([r for r in rows_ce if r["this_work"].strip()=="1"],key=lambda r:float(r["cycle"]))
# Stars are self-evidently "this work" (blue, large, in legend); keep only compact rate
# tags so the congested 99-100% / 400-2000-cyc zone stays readable. Tags go UP into the
# empty 100-101% band: 0.5C up-left, 1C up-right.
TWLAB={ "0.5":(-9,8,"right"), "1.0":(9,8,"left") }
for i,r in enumerate(tw):
    cyc=float(r["cycle"]); ce=float(r["CE_pct"]); rstr=r["rate_C"].strip()
    axb.plot(cyc,ce,marker="*",ls="none",ms=16,mfc=C["poly"],mec="white",mew=0.7,zorder=6,
             label="this work" if i==0 else None)
    dx,dy,ha=TWLAB.get(rstr,(0,8,"center"))
    axb.annotate(f"{rstr.rstrip('0').rstrip('.')}C",xy=(cyc,ce),xytext=(dx,dy),
                 textcoords="offset points",fontsize=5.6,color=C["poly"],fontweight="bold",
                 ha=ha,va="bottom",zorder=8)
axb.set_xscale("log")
axb.set_xlim(8,14000); axb.set_ylim(92,101)
axb.set_xlabel("Cycle number"); axb.set_ylabel("Coulombic efficiency (%)")
axb.set_title("Benchmark: cycle life vs CE",pad=3)
# legend: this-work star + confidence key (shape/fill) -- grayscale-separable
from matplotlib.lines import Line2D as _L2D
conf_handles=[_L2D([0],[0],marker="*",ls="none",ms=10,mfc=C["poly"],mec="white",mew=0.5,label="this work"),
              _L2D([0],[0],marker="o",ls="none",ms=5,mfc=C["ink"],mec=C["ink"],mew=0.7,label="high conf."),
              _L2D([0],[0],marker="o",ls="none",ms=5,mfc="#B0B0B0",mec=C["ink"],mew=0.7,label="med conf."),
              _L2D([0],[0],marker="o",ls="none",ms=5,mfc="none",mec=C["ink"],mew=0.7,label="low / unconf."),
              _L2D([0],[0],color=C["green"],lw=1.0,ls=(0,(5,2)),label="Pareto front")]
axb.legend(handles=conf_handles,loc="lower left",fontsize=4.7,handlelength=1.3,
           labelspacing=0.22,handletextpad=0.4,borderpad=0.3,framealpha=0.0,bbox_to_anchor=(-0.012,-0.012))
axb.text(0.985,0.25,"non-aqueous Mg-metal\nfull cells; values as\nreported (Table Sx);\nopen = not indep. confirmed",
         transform=axb.transAxes,fontsize=3.9,color="#666666",ha="right",va="top",linespacing=1.2)
panel_label(axb,"e",x=-0.165)

import os; os.makedirs(os.path.dirname(OUT),exist_ok=True)
save_pub(fig,OUT)
print("Figure 2 reworked (added voltage profiles; kept symmetric V-t)")
