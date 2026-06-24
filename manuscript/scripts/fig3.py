# -*- coding: utf-8 -*-
"""Figure 3 - Si-rich / Al-poor interphase (CENTREPIECE). Angew double-column.
ToF-SIMS (ratio + depth + original 3D maps) + depth-resolved XPS Al 2p
(raw scatter + semi-transparent GL fits, 0/10/20 nm) + Al at%/metallic.
Measured data (NOT AI-generated). Other core levels: see multi-element XPS figure."""
import sys, csv, json
sys.path.insert(0, r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad")
from angew_style import *
import xps_helper as X
import matplotlib.pyplot as plt
import numpy as np

ROOT=r"D:/20260602_polyAPC_data"; OUT=ROOT+"/Angewandte_Research_Article/figures/Fig3_interphase"
def rd(p):
    with open(p,encoding="utf-8") as f: return list(csv.DictReader(f))
def col(rows,k,t=float): return np.array([t(r[k]) for r in rows])

ions=rd(ROOT+"/ToF-SIMS/processed/data/diagnostic_ions_corrected.csv")
dp_p=rd(ROOT+"/ToF-SIMS/processed/data/poly_depthprofile.csv")
dp_b=rd(ROOT+"/ToF-SIMS/processed/data/bare_depthprofile.csv")
sei=json.load(open(ROOT+"/ToF-SIMS/processed/data/sei_depth.json",encoding="utf-8"))
xdp=rd(ROOT+"/XPS/results/data/depth_profile_summary.csv")

fig=plt.figure(figsize=(W2,1.18*W2))
gs=fig.add_gridspec(3,6,height_ratios=[1.0,0.72,1.04],hspace=0.46,wspace=1.0,
                    left=0.075,right=0.965,top=0.95,bottom=0.065)

# ---- (a) XPS at% SEI composition - stacked 100% bar (Li Fig3i style) ----
ax=fig.add_subplot(gs[0,0:3])
ed={(r["sample"],int(r["etch"])):r for r in xdp}
ELEMS=[("at_O","O","#4292C6"),("at_Mg","Mg","#9ECAE1"),("at_C","C","#969696"),
       ("at_Al","Al",C["Al"]),("at_Cl","Cl",C["accent"]),("at_Si","Si",C["Si"]),("at_F","F","#D9D9D9")]
HATCHED={"Al":"...","Si":"///"}
bars=["bare","poly"]; x=np.arange(2)
vals={s:np.array([float(ed[(s,1)][k]) for k,_,_ in ELEMS]) for s in bars}   # 10 nm subsurface
for s in bars: vals[s]=vals[s]/vals[s].sum()*100.0
bottom={s:0.0 for s in bars}
for i,(k,nm,clr) in enumerate(ELEMS):
    for j,s in enumerate(bars):
        v=vals[s][i]
        ax.bar(x[j],v,bottom=bottom[s],color=clr,edgecolor="white",lw=0.5,width=0.62,
               hatch=HATCHED.get(nm,""))
        if v>4: ax.text(x[j],bottom[s]+v/2,f"{nm}",ha="center",va="center",fontsize=5.6,
                        color=("white" if nm in("O","C","Cl") else "black"))
        bottom[s]+=v
ax.set_xticks(x); ax.set_xticklabels(["bare-APC","poly-APC"],fontsize=6.8)
ax.set_ylim(0,100); ax.set_ylabel("XPS atomic % (10 nm SEI)")
ax.set_title("SEI composition: Al-poor poly",pad=3)
ax.annotate("Al 8.2→5.2 at%\n(poly Al-poor)",xy=(0.5,0.50),xycoords="axes fraction",
            fontsize=5.4,ha="center",color=C["Al"],fontweight="bold")
ax.text(0.5,-0.30,"Si enrichment is a ToF-SIMS result (×20–34); XPS Si near floor",
        transform=ax.transAxes,fontsize=5.0,ha="center",style="italic",color="0.3")
panel_label(ax,"a",x=-0.26)

# ---- (b) ToF-SIMS depth profiles (Li-style: log intensity vs depth, multi-ion, bare vs poly) ----
from matplotlib.lines import Line2D
ax=fig.add_subplot(gs[0,3:6])
ionset=[("AlO-",C["Al"],"AlO$^-$"),("SiO2-",C["Si"],"SiO$_2^-$"),("SiO3-",C["poly2"],"SiO$_3^-$")]
for key,cl,_ in ionset:
    ax.plot(col(dp_b,"depth_nm"),col(dp_b,key),color=cl,ls=(0,(5,2)),lw=1.05)   # bare dashed
    ax.plot(col(dp_p,"depth_nm"),col(dp_p,key),color=cl,ls="-",lw=1.15)         # poly solid
ax.set_yscale("log"); ax.set_xlim(0,400); ax.set_ylim(60,2.2e5)
ax.set_xlabel("Depth (nm)"); ax.set_ylabel("Intensity (counts)")
ax.set_title("ToF-SIMS depth profiles",pad=3)
h1=[Line2D([0],[0],color=cl,lw=1.6,label=lab) for _,cl,lab in ionset]
h2=[Line2D([0],[0],color="0.35",ls="-",lw=1.3,label="poly-APC"),
    Line2D([0],[0],color="0.35",ls=(0,(5,2)),lw=1.3,label="bare-APC")]
leg1=ax.legend(handles=h1,fontsize=5.3,loc="upper right",handlelength=1.5,ncol=3,
               columnspacing=0.8,handletextpad=0.4); ax.add_artist(leg1)
ax.legend(handles=h2,fontsize=5.3,loc="lower left",handlelength=1.9)
ax.annotate("Al deep & abundant (bare)",xy=(150,9.5e4),fontsize=5.2,color=C["Al"],fontweight="bold")
ax.annotate("Si enriched (poly)",xy=(95,7e3),fontsize=5.2,color=C["Si"],fontweight="bold")
panel_label(ax,"b",x=-0.18)

# ---- (c) ToF-SIMS original 3D ion maps (embedded) ----
ax=fig.add_subplot(gs[1,0:6])
im=plt.imread(ROOT+"/ToF-SIMS/results/figures/fig_3dmaps_realxy_decoded.png")
ax.imshow(im); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(True); s.set_linewidth(0.8)
ax.set_title("ToF-SIMS 3D ion maps (top: poly-APC; bottom: bare-APC; B = separator artifact)",
             fontsize=6.5,pad=2)
panel_label(ax,"c",x=-0.045)

# ---- (d) XPS Al 2p bare; (e) poly  (scatter + transparent GL fits, 3 depths) ----
axd=fig.add_subplot(gs[2,0:2]); X.panel(axd,"Al2p","bare",C,win=(70.5,77.5))
axd.set_xlabel("Binding energy (eV)"); axd.set_title("XPS Al 2p: bare-APC",pad=3,color=C["bare_d"],fontweight="bold")
axd.axvline(73.0,color=C["Al"],lw=0.5,ls=":"); axd.axvline(74.5,color=C["poly"],lw=0.5,ls=":")
axd.text(73.0,3.7,"Al$^0$",color=C["Al"],fontsize=6,ha="center",fontweight="bold")
axd.text(74.5,3.7,"Al$^{3+}$",color=C["poly"],fontsize=6,ha="center",fontweight="bold")
axd.tick_params(labelsize=6); panel_label(axd,"d",x=-0.12)

axe=fig.add_subplot(gs[2,2:4]); X.panel(axe,"Al2p","poly",C,win=(70.5,77.5))
axe.set_xlabel("Binding energy (eV)"); axe.set_title("XPS Al 2p: poly-APC",pad=3,color=C["poly"],fontweight="bold")
axe.axvline(73.0,color=C["Al"],lw=0.5,ls=":"); axe.axvline(74.5,color=C["poly"],lw=0.5,ls=":")
axe.tick_params(labelsize=6); panel_label(axe,"e",x=-0.10)

# ---- (f) Al at% & metallic Al0 vs depth ----
axf=fig.add_subplot(gs[2,4:6])
def xrows(s): r=[x for x in xdp if x["sample"]==s]; r.sort(key=lambda z:float(z["depth_nm"])); return r
for sample,cl,mk in [("bare",C["bare"],"s"),("poly",C["poly"],"o")]:
    r=xrows(sample); z=col(r,"depth_nm"); al=col(r,"at_Al"); al0=col(r,"Al0_metal_at%")
    axf.plot(z,al,color=cl,ls="-",marker=mk,ms=4,mfc=cl,mec="white",mew=0.5,lw=1.1,label=f"{sample}: total Al")
    axf.plot(z,al0,color=cl,ls=(0,(4,2)),marker=mk,ms=4,mfc="none",mec=cl,mew=0.8,lw=1.0,label=f"{sample}: metallic Al$^0$")
axf.set_xlim(-1,21); axf.set_ylim(0,11.5); axf.set_xticks([0,10,20])
axf.set_xlabel("Etch depth (nm)"); axf.set_ylabel("Concentration (at%)")
axf.set_title("Al rises & reduces in bare",pad=3)
axf.legend(fontsize=5.2,handlelength=1.8,loc="upper left")
panel_label(axf,"f",x=-0.18)

import os; os.makedirs(os.path.dirname(OUT),exist_ok=True)
save_pub(fig,OUT,dpi_tiff=450)
print("Figure 3 reworked")
