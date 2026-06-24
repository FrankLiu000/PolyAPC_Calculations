# -*- coding: utf-8 -*-
"""Figure 6 - interface reduction, Al co-deposition & passivating SEI (DFT/AIMD), JPCC-style.
Now with REAL DOS/PDOS curves + Mg|SEI band alignment from EPYC (results/T8b_DOS). NOT AI-generated."""
import sys, csv, json, os
sys.path.insert(0, r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad")
from angew_style import *
import mol_render as M
import matplotlib.pyplot as plt
import numpy as np

REPO=r"D:/20260602_polyAPC_data/PolyAPC_repo"
ST=REPO+"/computational_v2/common/struct/"
DOS=REPO+"/results/T8b_DOS/outputs/"
OUT=r"D:/20260602_polyAPC_data/Angewandte_Research_Article/figures/Fig6_interface_mechanism"
def rd(p):
    with open(p,encoding="utf-8") as f: return list(csv.DictReader(f))
meta=json.load(open(DOS+"dos_meta.json",encoding="utf-8"))
ELEMC={"O":"#D14A3F","Si":"#009E73","Al":"#E69F00","Mg":"#56B4E9","Cl":"#CC79A7"}

fig=plt.figure(figsize=(W2,1.04*W2))
gs=fig.add_gridspec(3,2,height_ratios=[1.0,1.05,0.95],hspace=0.42,wspace=0.28,
                    left=0.085,right=0.96,top=0.95,bottom=0.065)

# (a) interface MD box
ax=fig.add_subplot(gs[0,0],projection="3d")
M.render(ax,ST+"iface_bare.xyz",view=(8,-90),zoom=1.0)
ax.set_title("Interface model: Mg(0001)+cation+Al-anion",fontsize=7,pad=-2)
ax.text2D(0.0,0.95,"a",transform=ax.transAxes,fontsize=10,fontweight="bold")
# (b) Al substitution in Mg
ax=fig.add_subplot(gs[0,1],projection="3d")
M.render(ax,ST+"Mg0001_AlSub.xyz",view=(10,-90),zoom=1.0)
ax.set_title("Al in Mg(0001): $\\Delta E_{sub}=-4.44$ eV",fontsize=7,pad=-2)
ax.legend(handles=M.legend_handles(["Mg","Al"]),fontsize=5.2,loc="upper right",bbox_to_anchor=(1.10,1.0),handletextpad=0.1)
ax.text2D(0.0,0.95,"b",transform=ax.transAxes,fontsize=10,fontweight="bold")

# (c) reduction energetics
ax=fig.add_subplot(gs[1,0])
ax.bar([0,1],[-8.5,14.5],color=[C["poly"],C["bare"]],hatch=[HATCH["poly"],HATCH["bare"]],edgecolor="white",lw=0.6,width=0.6)
ax.axhline(0,color="black",lw=0.8)
for i,v in zip([0,1],[-8.5,14.5]): ax.text(i,v+(1.2 if v>0 else -1.2),f"{v:+.1f}",ha="center",va=("bottom" if v>0 else "top"),fontsize=6.5)
ax.set_xticks([0,1]); ax.set_xticklabels(["Al–Cl\ncleavage","Al–C\ncleavage"],fontsize=6.5)
ax.set_ylabel(r"$\Delta G$ (kcal mol$^{-1}$)"); ax.set_ylim(-14,20)
ax.set_title("Reduced anion → Al–Cl scission → Al$^0$",pad=3)
panel_label(ax,"c")

# (d) DOS / PDOS overlay  (EPYC T8b)  -- leaky metals vs passivating insulators
ax=fig.add_subplot(gs[1,1])
phases=[("Al_fcc","Al$^0$"),("Mg17Al12","Mg$_{17}$Al$_{12}$"),("MgCl2","MgCl$_2$"),
        ("MgO","MgO"),("Al2O3","Al$_2$O$_3$"),("SiO2","SiO$_2$")]
OFF=1.18
for i,(ph,lab) in enumerate(phases):
    rows=rd(DOS+f"{ph}_dos.csv"); E=np.array([float(r["E_minus_Ef_eV"]) for r in rows])
    tot=np.array([float(r["totalDOS"]) for r in rows]); tot=tot/ (tot.max() or 1)
    off=i*OFF; ismet=meta[ph]["type"]=="metal"
    base=C["bare"] if ismet else C["poly"]
    ax.fill_between(E,off,tot+off,color=base,alpha=0.16,lw=0)
    for el in meta[ph]["elements"]:
        pd=np.array([float(r.get(f"pdos_{el}",0)) for r in rows]); pd=pd/((tot.max()*max(t for t in [1]) ) or 1)
        pdn=np.array([float(r.get(f"pdos_{el}",0)) for r in rows]);
    # element pdos fills (normalized to same scale as total)
    rawtot=np.array([float(r["totalDOS"]) for r in rows]); sc=1.0/(rawtot.max() or 1)
    for el in meta[ph]["elements"]:
        pd=np.array([float(r.get(f"pdos_{el}",0)) for r in rows])*sc
        ax.fill_between(E,off,pd+off,color=ELEMC.get(el,"#888"),alpha=0.55,lw=0)
    ax.plot(E,tot+off,color="black",lw=0.7)
    g=meta[ph]["t8_authoritative_gap_eV"]
    tag=f"{lab}  (metal)" if ismet else f"{lab}  $E_g$={g:.1f} eV"
    ax.text(7.6,off+0.5,tag,fontsize=5.4,ha="right",color=(C["bare_d"] if ismet else C["poly"]),fontweight="bold")
ax.axvline(0,color="black",lw=0.8,ls=(0,(4,2)))
ax.text(0.15,len(phases)*OFF-0.2,"$E_F$",fontsize=6)
ax.set_xlim(-9,8); ax.set_ylim(0,len(phases)*OFF+0.2)
ax.set_yticks([]); ax.set_xlabel("$E-E_F$ (eV)"); ax.set_ylabel("DOS (a.u.)")
ax.set_title("SEI density of states",pad=3)
ax.text(-8.5,1.2,"metallic →\nstates at $E_F$\n(leaky)",fontsize=5.0,color=C["bare_d"])
ax.text(-8.5,5.0,"insulating →\ngap at $E_F$\n(passivating)",fontsize=5.0,color=C["poly"])
panel_label(ax,"d")

# (e) Mg | SEI band alignment (EPYC)
ax=fig.add_subplot(gs[2,0])
al=rd(DOS+"../outputs/iface_MgSiOx_alignment.csv")
order=["SiO2","Al2O3","MgO","MgCl2","Al_fcc","Mg17Al12"]
nm={"SiO2":"SiO$_2$","Al2O3":"Al$_2$O$_3$","MgO":"MgO","MgCl2":"MgCl$_2$","Al_fcc":"Al$^0$","Mg17Al12":"Mg$_{17}$Al$_{12}$"}
A={r["phase"]:r for r in al}
EF=-3.97
for i,ph in enumerate(order):
    r=A[ph]; ismet=(r["chi_eV"]=="")
    if not ismet:
        cbm=float(r["CBM_vs_vac_eV"]); vbm=float(r["VBM_vs_vac_eV"])
        ax.add_patch(plt.Rectangle((i-0.36,vbm-2.2),0.72,2.2,color=C["poly"],alpha=0.30,lw=0))  # VB (occupied)
        ax.add_patch(plt.Rectangle((i-0.36,cbm),0.72,1.6,color="#BBBBBB",alpha=0.45,lw=0))       # CB
        ax.plot([i-0.36,i+0.36],[vbm,vbm],color=C["poly"],lw=1.0); ax.plot([i-0.36,i+0.36],[cbm,cbm],color="0.4",lw=1.0)
        bar=float(r["e_injection_barrier_eV"])
        ax.annotate("",xy=(i,cbm),xytext=(i,EF),arrowprops=dict(arrowstyle="->",color=C["red"],lw=0.8))
        ax.text(i+0.40,(EF+cbm)/2,f"{bar:.2f}",fontsize=5.2,color="black",va="center")
    else:
        ax.add_patch(plt.Rectangle((i-0.36,EF-1.4),0.72,2.8,color=C["bare"],alpha=0.45,lw=0))     # metallic states across E_F
        ax.text(i,EF+1.7,"leaky",fontsize=5.0,ha="center",color=C["bare_d"],fontweight="bold")
ax.axhline(EF,color="black",lw=1.1,ls=(0,(5,2)))
ax.text(len(order)-0.5,EF+0.18,"Mg $E_F$ (−3.97 eV)",fontsize=5.6,ha="right",fontweight="bold")
ax.set_xticks(range(len(order))); ax.set_xticklabels([nm[p] for p in order],fontsize=5.8)
ax.set_ylim(-11,0.5); ax.set_ylabel("E vs vacuum (eV)")
ax.set_title("Mg|SEI band alignment: e$^-$-injection barrier",pad=3)
ax.text(0,-10.4,"poly SiO$_2$: 3.07 eV blocks",fontsize=5.2,color=C["poly"],fontweight="bold")
panel_label(ax,"e")

# (f) network sequestration
ax=fig.add_subplot(gs[2,1])
ax.bar([0,1],[47.5,24.7],color=[C["Al"],C["poly"]],hatch=[HATCH["Al"],HATCH["poly"]],edgecolor="white",lw=0.6,width=0.55)
for i,v in zip([0,1],[47.5,24.7]): ax.text(i,v+1.5,f"{v:.1f}%",ha="center",fontsize=6.5)
ax.set_xticks([0,1]); ax.set_xticklabels(["Al-anion","cation"],fontsize=6.5)
ax.set_ylabel("network-associated (%)"); ax.set_ylim(0,60)
ax.set_title("POSS network sequesters Al-anion",pad=3)
ax.text(0.5,0.80,"anion 4.2× slower in gel;\nsupports the 3.07 eV block (d,e)",
        transform=ax.transAxes,fontsize=5.2,ha="center",color=C["ink"],
        bbox=dict(boxstyle="round,pad=0.3",fc="#F2F4F6",ec="none"))
panel_label(ax,"f")

os.makedirs(os.path.dirname(OUT),exist_ok=True)
save_pub(fig,OUT)
print("Fig6 (DOS + band alignment) done")
