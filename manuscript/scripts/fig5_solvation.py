# -*- coding: utf-8 -*-
"""Figure 5 - solvation structure, ion pairing, interaction energetics & desolvation
(classical MD + DFT), JPCC-style. All from existing computed data. NOT AI-generated."""
import sys, csv
sys.path.insert(0, r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad")
from angew_style import *
import mol_render as M
import matplotlib.pyplot as plt
import numpy as np

MD=r"D:/20260602_polyAPC_data/PolyAPC_repo/classical_molecular_dynamics/handoff_for_agent"
OUT=r"D:/20260602_polyAPC_data/Angewandte_Research_Article/figures/Fig5_solvation"
def xvg(path):
    x=[];y=[]
    for ln in open(path,encoding="utf-8",errors="replace"):
        if ln[:1] in "@#&" or not ln.strip(): continue
        p=ln.split()
        try: x.append(float(p[0])); y.append(float(p[1]))
        except: pass
    return np.array(x),np.array(y)

fig=plt.figure(figsize=(W2,0.70*W2))
gs=fig.add_gridspec(2,3,hspace=0.42,wspace=0.34,left=0.07,right=0.965,top=0.93,bottom=0.10)

# (a) Mg2+ first-shell solvation structure (3 uCl + 3 THF-O)
ax=fig.add_subplot(gs[0,0],projection="3d")
M.render(ax,MD+"/structures/representative_solvation/bare_octahedral_3Cl3O.pdb",view=(16,-65),zoom=1.15,no_metal_bonds=False)
ax.set_title("Mg$^{2+}$ first shell\n[Mg$_2$($\\mu$-Cl)$_3$(THF)$_6$]$^+$",fontsize=7,pad=-3)
ax.text2D(0.0,0.93,"a",transform=ax.transAxes,fontsize=10,fontweight="bold")
ax.legend(handles=M.legend_handles(["Mg","Cl","O","C","H"]),fontsize=4.8,loc="upper right",
          bbox_to_anchor=(1.13,1.0),handletextpad=0.1,labelspacing=0.16,borderpad=0.2)

# (b) Mg2+ RDF: THF-O, bridging-Cl, network-O (bare dashed, poly solid)
ax=fig.add_subplot(gs[0,1])
series=[("MgAllThfO",C["poly"],"Mg–O(THF)"),("MgClb",C["green"],"Mg–Cl($\\mu$)"),("MgPolyO",C["accent"],"Mg–O(network)")]
for key,clr,lab in series:
    for sysn,ls in [("bare",(0,(5,2))),("poly","-")]:
        import os
        p=f"{MD}/rdf/{sysn}/rdf_{key}.xvg"
        if os.path.exists(p):
            r,g=xvg(p); ax.plot(r*10,g,color=clr,ls=ls,lw=1.1)   # nm->Angstrom
ax.set_xlim(1.4,6); ax.set_ylim(0,98)
ax.set_xlabel("r (Å)"); ax.set_ylabel("g(r)")
ax.set_title("Mg$^{2+}$ radial distribution",pad=3)
from matplotlib.lines import Line2D
h1=[Line2D([0],[0],color=clr,lw=1.6,label=lab) for _,clr,lab in series]
h2=[Line2D([0],[0],color="0.35",ls="-",lw=1.3,label="poly"),Line2D([0],[0],color="0.35",ls=(0,(5,2)),lw=1.3,label="bare")]
lg=ax.legend(handles=h1,fontsize=5.2,loc="upper right",handlelength=1.5); ax.add_artist(lg)
ax.legend(handles=h2,fontsize=5.2,loc="center right",handlelength=1.8)
ax.text(3.1,30,"network-O absent\nfrom first shell",fontsize=5.2,color=C["accent"],fontweight="bold")
panel_label(ax,"b")

# (c) SSIP/CIP/AGG donut pies (bare, poly)
sub=gs[0,2].subgridspec(2,1,hspace=0.45)
spec={"bare":[4.6,94.9,0.5],"poly":[15.5,84.2,0.3]}
pcol=[C["poly"],C["bare"],C["red"]]; plab=["SSIP\n(free)","CIP","AGG"]
for i,(sysn,vals) in enumerate(spec.items()):
    axp=fig.add_subplot(sub[i])
    w,_=axp.pie(vals,colors=pcol,startangle=90,counterclock=False,
                wedgeprops=dict(width=0.42,edgecolor="white",lw=0.6))
    axp.text(0,0,f"{vals[0]:.0f}%\nfree",ha="center",va="center",fontsize=6,fontweight="bold",color=C["poly"])
    axp.set_title(f"{sysn}-APC",fontsize=6.5,pad=-2)
    if i==0: axp.text2D=None;
fig.add_subplot(gs[0,2]).axis("off")
fig.text(0.94,0.945,"ion pairing (SSIP/CIP/AGG)",fontsize=6,ha="right",fontweight="bold")
fig.text(0.80,0.5,"free carrier\n4.6→15.5%",fontsize=5.4,ha="center",color=C["poly"],fontweight="bold")
# panel label for c
fig.text(0.655,0.93,"c",fontsize=10,fontweight="bold")

# (d) interaction-energy decomposition (per Mg-cluster, kJ/mol)
ax=fig.add_subplot(gs[1,0])
cats=["Mg–anion\n(Coul)","Mg–anion\n(LJ)","Mg–THF\n(LJ)","Mg–net\n(LJ)"]
bare=[-97,-44,-151,0]; poly=[-93,-44,-110,-43]
x=np.arange(len(cats)); w=0.36
ax.bar(x-w/2,bare,w,color=C["bare"],hatch=HATCH["bare"],edgecolor="white",lw=0.5,label="bare")
ax.bar(x+w/2,poly,w,color=C["poly"],hatch=HATCH["poly"],edgecolor="white",lw=0.5,label="poly")
ax.axhline(0,color="black",lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(cats,fontsize=5.6)
ax.set_ylabel("interaction E (kJ mol$^{-1}$)"); ax.set_ylim(-170,30)
ax.set_title("Mg-cluster interactions",pad=3)
ax.legend(fontsize=5.6,loc="lower left",handlelength=1.2)
ax.text(0.97,0.06,"net −308 ‖ −316\n(THF→network swap)",transform=ax.transAxes,fontsize=5.0,
        ha="right",color=C["ink"])
panel_label(ax,"d")

# (e) desolvation free-energy level diagram (last-THF, 3 routes)
ax=fig.add_subplot(gs[1,1])
ax.plot([0,1],[0,0],color="black",lw=2,solid_capstyle="round")
ax.text(0.5,0.6,"[MgCl(THF)]$^+$",ha="center",fontsize=5.8)
routes=[("dissociative",19.9,C["bare"]),("network-O relay",5.6,C["poly"]),("reduction-coupled",3.9,C["green"])]
for i,(lab,dG,clr) in enumerate(routes):
    xx=2.0+i*0.05
    ax.plot([2,3],[dG,dG],color=clr,lw=2,solid_capstyle="round")
    ax.plot([1,2],[0,dG],color=clr,lw=0.8,ls=":")
    ax.text(3.05,dG,f"{lab}\n+{dG}",fontsize=5.2,va="center",color=clr,fontweight="bold")
ax.annotate("",xy=(2.5,3.9),xytext=(2.5,19.9),arrowprops=dict(arrowstyle="<->",color="0.4",lw=0.7))
ax.text(2.42,12,"−16 kcal/mol\n(electrode e$^-$)",fontsize=5.0,ha="right",color="0.3",rotation=90)
ax.set_xlim(-0.2,5.2); ax.set_ylim(-3,24); ax.set_xticks([])
ax.set_ylabel("$\\Delta G$ (kcal mol$^{-1}$)")
ax.set_title("Last-THF desolvation routes",pad=3)
panel_label(ax,"e")

# (f) first-shell coordination numbers
ax=fig.add_subplot(gs[1,2])
cn=["THF-O","Cl($\\mu$)","network-O"]; cb=[3.0,3.0,0.0]; cp=[3.0,3.0,0.006]
x=np.arange(3); w=0.36
ax.bar(x-w/2,cb,w,color=C["bare"],hatch=HATCH["bare"],edgecolor="white",lw=0.5,label="bare")
ax.bar(x+w/2,cp,w,color=C["poly"],hatch=HATCH["poly"],edgecolor="white",lw=0.5,label="poly")
for xi,(b,p) in enumerate(zip(cb,cp)):
    ax.text(xi-w/2,b+0.08,f"{b:.0f}" if b>=1 else f"{b:.0f}",ha="center",fontsize=5.6)
    ax.text(xi+w/2,p+0.08,f"{p:.3f}" if p<1 else f"{p:.0f}",ha="center",fontsize=5.6)
ax.set_xticks(x); ax.set_xticklabels(cn,fontsize=6)
ax.set_ylabel("first-shell coordination #"); ax.set_ylim(0,3.6)
ax.set_title("Intact cation; network excluded",pad=3)
ax.legend(fontsize=5.6,loc="upper right",handlelength=1.2)
panel_label(ax,"f")

import os; os.makedirs(os.path.dirname(OUT),exist_ok=True)
save_pub(fig,OUT)
print("Fig5 solvation done")
