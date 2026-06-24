# -*- coding: utf-8 -*-
"""Comprehensive depth-resolved XPS (all core levels), published battery-SEI style:
raw = open-circle scatter, Shirley background, semi-transparent GL(30) fitted peaks,
black envelope; stacked 0/10/20 nm; bare (left) vs poly (right). NOT AI-generated."""
import sys
sys.path.insert(0, r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad")
from angew_style import *
import xps_helper as X
import matplotlib.pyplot as plt

OUT=r"D:/20260602_polyAPC_data/Angewandte_Research_Article/figures/Fig3b_XPS_multielement"
REGIONS=[("Al2p",(70,78),"Al 2p"),("Si2p",(98,106),"Si 2p"),("Cl2p",(195,205),"Cl 2p"),
         ("Mg1s",(1299,1309),"Mg 1s"),("O1s",(527,537),"O 1s"),("C1s",(281,292),"C 1s")]
nrow=len(REGIONS)
fig=plt.figure(figsize=(W2,1.46*W2))
gs=fig.add_gridspec(nrow,2,hspace=0.45,wspace=0.10,left=0.055,right=0.86,top=0.965,bottom=0.045)

for ri,(reg,win,lab) in enumerate(REGIONS):
    for ci,sample in enumerate(("bare","poly")):
        ax=fig.add_subplot(gs[ri,ci])
        X.panel(ax,reg,sample,C,win=win)
        if ri==0: ax.set_title(("bare-APC" if sample=="bare" else "poly-APC"),fontsize=8,pad=4,
                               color=(C["bare_d"] if sample=="bare" else C["poly"]),fontweight="bold")
        if ci==0:
            ax.set_ylabel(lab,fontsize=8,fontweight="bold")
        if ri==nrow-1: ax.set_xlabel("Binding energy (eV)")
        ax.tick_params(labelsize=6)

# legend (shared, right margin)
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
handles=[Line2D([0],[0],ls="none",marker="o",mfc="none",mec="0.45",ms=4,label="raw data"),
         Line2D([0],[0],color="black",lw=1,label="envelope (fit)"),
         Line2D([0],[0],color="0.6",lw=1,label="Shirley bkg."),
         Patch(fc=C["Al"],alpha=0.45,label="reduced (Al$^0$/Si$^0$)"),
         Patch(fc=C["poly"],alpha=0.45,label="oxidized (Al$^{3+}$/Si–O, etc.)")]
fig.legend(handles=handles,loc="center right",fontsize=6.2,frameon=False,
           bbox_to_anchor=(1.0,0.5),handlelength=1.6)
fig.text(0.46,0.985,"Depth-resolved XPS core levels (etch 0 / 10 / 20 nm, stacked)",
         ha="center",fontsize=8.5,fontweight="bold")
import os; os.makedirs(os.path.dirname(OUT),exist_ok=True)
save_pub(fig,OUT,dpi_tiff=450)
print("Multi-element XPS figure done")
