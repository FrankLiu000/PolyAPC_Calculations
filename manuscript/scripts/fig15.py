# -*- coding: utf-8 -*-
"""Figures 1 & 5 - computation, JPCC-style: molecular structures + MD/interface boxes
alongside energetics/DOS/redox. Structures rendered from DFT/MD .xyz (ball-and-stick).
Scripted plots of computed data (NOT AI-generated). CVD-safe quantitative panels."""
import sys, csv
sys.path.insert(0, r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad")
from angew_style import *
import mol_render as M
import matplotlib.pyplot as plt
import numpy as np

ROOT=r"D:/20260602_polyAPC_data"
CV3=ROOT+"/PolyAPC_Calculations-computational-v3-interface/PolyAPC_Calculations-computational-v3-interface"
ST=CV3+"/computational_v2/common/struct/"
FOUT=ROOT+"/Angewandte_Research_Article/figures"
def rd(p):
    with open(p,encoding="utf-8") as f: return list(csv.DictReader(f))
RLH=r"$\rightleftharpoons$"

# ============================================================ FIGURE 1
redox=rd(CV3+"/results/T2_redox_ladder/outputs/redox_ladder_vsMg.csv")
fig=plt.figure(figsize=(W2,0.66*W2))
gs=fig.add_gridspec(2,2,height_ratios=[1.05,1.0],hspace=0.34,wspace=0.26,
                    left=0.06,right=0.96,top=0.93,bottom=0.11)

# (a) cation structure
ax=fig.add_subplot(gs[0,0],projection="3d")
M.render(ax,ST+"Mg2Cl3_THF6_cation.xyz",view=(16,-60),zoom=1.12)
ax.set_title("[Mg$_2$Cl$_3$(THF)$_6$]$^+$ cation",fontsize=7.5,pad=-2)
ax.text2D(0.0,0.93,"a",transform=ax.transAxes,fontsize=10,fontweight="bold")
# (b) dominant anion
ax=fig.add_subplot(gs[0,1],projection="3d")
els=M.render(ax,ST+"AlPh2Cl2m.xyz",view=(20,-70),zoom=1.12)
ax.set_title("[AlPh$_2$Cl$_2$]$^-$ dominant anion",fontsize=7.5,pad=-2)
ax.legend(handles=M.legend_handles(["Mg","Al","Cl","O","C","H"]),fontsize=5,loc="upper right",
          bbox_to_anchor=(1.12,1.02),handletextpad=0.1,labelspacing=0.18,borderpad=0.2)
ax.text2D(0.0,0.93,"b",transform=ax.transAxes,fontsize=10,fontweight="bold")

# (c) Schlenk speciation
ax=fig.add_subplot(gs[1,0])
sch=["2 AlPh$_2$Cl$_2^-$\n"+RLH+" AlPhCl$_3^-$+AlPh$_3$Cl$^-$",
     "2 AlPhCl$_3^-$\n"+RLH+" AlCl$_4^-$+AlPh$_2$Cl$_2^-$",
     "2 AlPh$_3$Cl$^-$\n"+RLH+" AlPh$_2$Cl$_2^-$+AlPh$_4^-$"]
dG=[1.1,4.5,3.2]; y=np.arange(3)[::-1]
ax.barh(y,dG,color=C["poly"],hatch=HATCH["poly"],edgecolor="white",lw=0.6,height=0.6)
for yi,v in zip(y,dG): ax.text(v+0.15,yi,f"+{v}",va="center",fontsize=6)
ax.set_yticks(y); ax.set_yticklabels(sch,fontsize=5.0); ax.set_xlim(0,5.6)
ax.set_xlabel(r"Schlenk $\Delta G$ (kcal mol$^{-1}$)")
ax.set_title("AlPh$_2$Cl$_2^-$ dominant ($\\Delta G>0$)",pad=3)
panel_label(ax,"c",x=-0.50)

# (d) redox ladder
ax=fig.add_subplot(gs[1,1])
D={r["species"]:float(r["E_red_vs_Mg_V"]) for r in redox}
groups={"anions":["AlCl4m","AlPhCl3m","AlPh2Cl2m","AlPh3Clm","AlPh4m"],
        "neutrals":["AlCl3 (neutral)","AlPh3 (neutral)"],
        "ion pair":["AlPh2Cl2- . cation CIP (bare, EA_vert)","AlPh2Cl2- . cation CIP (poly)"]}
short={"AlCl3 (neutral)":"AlCl$_3$","AlPh3 (neutral)":"AlPh$_3$",
       "AlPh2Cl2- . cation CIP (bare, EA_vert)":"CIP bare","AlPh2Cl2- . cation CIP (poly)":"CIP poly",
       "AlCl4m":"AlCl$_4^-$","AlPhCl3m":"AlPhCl$_3^-$","AlPh2Cl2m":"AlPh$_2$Cl$_2^-$",
       "AlPh3Clm":"AlPh$_3$Cl$^-$","AlPh4m":"AlPh$_4^-$"}
ax.axhspan(-2.05,0.05,color=C["Al"],alpha=0.09,lw=0)
ax.axhline(0,color="black",lw=1.0)
ax.text(2.5,0.10,"Mg$^{2+}$/Mg plating",fontsize=5.6,va="bottom",ha="center",fontweight="bold")
xc={"anions":0.6,"neutrals":1.7,"ion pair":2.7}
for g,mem in groups.items():
    for i,s in enumerate(mem):
        v=D[s]; xx=xc[g]+(i-len(mem)/2)*0.16
        ax.plot([xx-0.07,xx+0.07],[v,v],color=(C["poly"] if g!="neutrals" else C["Al"]),lw=2.0,solid_capstyle="round")
        ax.annotate(short.get(s,s),xy=(xx,v),xytext=(xx,v-0.12),fontsize=4.3,ha="center",va="top",color=C["ink"])
ax.text(1.7,-0.28,"neutral Al → easiest reduced",fontsize=5.0,color=C["bare_d"],ha="center")
ax.set_xlim(0,3.4); ax.set_ylim(-3.7,0.7); ax.set_xticks([])
ax.set_ylabel("$E_{red}$ (V vs Mg$^{2+}$/Mg)")
ax.set_title("Al species reduce near plating",pad=3)
panel_label(ax,"d",x=-0.12)
import os; os.makedirs(FOUT,exist_ok=True)
save_pub(fig,FOUT+"/Fig1_electrolyte_redox"); plt.close(fig); print("Fig1 done")

# ============================================================ FIGURE 5
gaps=rd(CV3+"/results/T8_sei_electronic/outputs/t8_gaps.csv")
fig=plt.figure(figsize=(W2,1.04*W2))
gs=fig.add_gridspec(3,2,height_ratios=[1.0,0.92,0.92],hspace=0.40,wspace=0.26,
                    left=0.085,right=0.96,top=0.95,bottom=0.065)

# (a) interface MD box
ax=fig.add_subplot(gs[0,0],projection="3d")
M.render(ax,ST+"iface_bare.xyz",view=(8,-90),zoom=1.0,no_metal_bonds=True)
ax.set_title("Interface model: Mg(0001) + cation + Al-anion",fontsize=7,pad=-2)
ax.text2D(0.0,0.95,"a",transform=ax.transAxes,fontsize=10,fontweight="bold")
# (b) Al co-deposition / alloying structures
ax=fig.add_subplot(gs[0,1],projection="3d")
M.render(ax,ST+"Mg0001_AlSub.xyz",view=(10,-90),zoom=1.0,no_metal_bonds=True)
ax.set_title("Al substitution in Mg(0001) ($\\Delta E_{sub}=-4.44$ eV)",fontsize=7,pad=-2)
ax.legend(handles=M.legend_handles(["Mg","Al"]),fontsize=5.2,loc="upper right",
          bbox_to_anchor=(1.10,1.0),handletextpad=0.1)
ax.text2D(0.0,0.95,"b",transform=ax.transAxes,fontsize=10,fontweight="bold")

# (c) reduction energetics
ax=fig.add_subplot(gs[1,0])
ax.bar([0,1],[-8.5,14.5],color=[C["poly"],C["bare"]],hatch=[HATCH["poly"],HATCH["bare"]],
       edgecolor="white",lw=0.6,width=0.6)
ax.axhline(0,color="black",lw=0.8)
for i,v in zip([0,1],[-8.5,14.5]): ax.text(i,v+(1.2 if v>0 else -1.2),f"{v:+.1f}",ha="center",
                                            va=("bottom" if v>0 else "top"),fontsize=6.5)
ax.set_xticks([0,1]); ax.set_xticklabels(["Al–Cl\ncleavage","Al–C\ncleavage"],fontsize=6.5)
ax.set_ylabel(r"$\Delta G$ (kcal mol$^{-1}$)"); ax.set_ylim(-14,20)
ax.set_title("Reduced anion → Al–Cl scission → Al$^0$",pad=3)
panel_label(ax,"c")

# (d) SEI band gaps
ax=fig.add_subplot(gs[1,1])
order=["Al_fcc","Mg17Al12","MgCl2","MgO","Al2O3","SiO2"]
nm={"Al_fcc":"Al$^0$","Mg17Al12":"Mg$_{17}$Al$_{12}$","MgCl2":"MgCl$_2$","MgO":"MgO","Al2O3":"Al$_2$O$_3$","SiO2":"SiO$_2$"}
G={r["phase"]:float(r["band_gap_eV"]) for r in gaps}
vals=[G[p] for p in order]; cols=[C["bare"] if G[p]<1 else C["poly"] for p in order]
ax.bar(range(len(order)),vals,color=cols,edgecolor="white",lw=0.6,width=0.66)
for i,v in enumerate(vals): ax.text(i,v+0.18,f"{v:.1f}",ha="center",fontsize=5.6)
ax.set_xticks(range(len(order))); ax.set_xticklabels([nm[p] for p in order],fontsize=6)
ax.set_ylabel("Band gap (eV)"); ax.set_ylim(0,9.6)
ax.set_title("Bare Al$^0$ leaky · Si-rich poly insulating",pad=3)
panel_label(ax,"d")

# (e) network exclusion
ax=fig.add_subplot(gs[2,0])
ax.bar([0,1],[47.5,24.7],color=[C["Al"],C["poly"]],hatch=[HATCH["Al"],HATCH["poly"]],edgecolor="white",lw=0.6,width=0.55)
for i,v in zip([0,1],[47.5,24.7]): ax.text(i,v+1.5,f"{v:.1f}%",ha="center",fontsize=6.5)
ax.set_xticks([0,1]); ax.set_xticklabels(["Al-anion","cation"],fontsize=6.5)
ax.set_ylabel("network-associated (%)"); ax.set_ylim(0,60)
ax.set_title("POSS network sequesters Al-anion",pad=3)
ax.text(0.5,0.80,"anion 4.2× slower in gel;\n$e^-$ injection barrier 3.07 eV",
        transform=ax.transAxes,fontsize=5.4,ha="center",color=C["ink"],
        bbox=dict(boxstyle="round,pad=0.3",fc="#F2F4F6",ec="none"))
panel_label(ax,"e")

# (f) computed-vs-measured validation
ax=fig.add_subplot(gs[2,1]); ax.axis("off")
ax.text(0.5,0.96,"Spectroscopic validation (computed → measured)",ha="center",fontsize=6.3,fontweight="bold",transform=ax.transAxes)
rows=[("Al 2p Al$^{3+}$ (poly)","Al(OH)$_3$ ref → 74.0 eV (meas 73.98)"),
      ("Al 2p Al$^0$ (bare)","molecular 73.4 → ~73.0 eV metallic (meas)"),
      ("Si 2p siloxane (poly)","computed shift +1.28 eV (meas +2.2)"),
      ("Raman 915 cm$^{-1}$","THF 912; phenyl→free (de-pairing)")]
yy=0.80
for a,b in rows:
    ax.text(0.03,yy,"•",fontsize=8,color=C["poly"],transform=ax.transAxes)
    ax.text(0.08,yy,a,fontsize=5.6,fontweight="bold",transform=ax.transAxes,va="center")
    ax.text(0.08,yy-0.085,b,fontsize=5.0,color=C["ink"],transform=ax.transAxes,va="center")
    yy-=0.205
panel_label(ax,"f",x=-0.02)
save_pub(fig,FOUT+"/Fig6_interface_mechanism"); print("Fig6 interface-mechanism done")
