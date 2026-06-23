# -*- coding: utf-8 -*-
"""Lightweight ball-and-stick renderer for .xyz (no ASE). For JPCC-style molecular /
MD-box panels. CPK-ish element colours (standard for structures)."""
import numpy as np
CPK={"H":"#E8E8E8","C":"#4D4D4D","N":"#3050F8","O":"#E8413A","F":"#7FD13B",
     "Mg":"#54B847","Al":"#D98E5A","Si":"#2E8B74","P":"#FF8000","S":"#E6C700",
     "Cl":"#5BC85B","Cu":"#C77B30","B":"#FFB5B5"}
RCOV={"H":0.31,"C":0.76,"N":0.71,"O":0.66,"F":0.57,"Mg":1.41,"Al":1.21,
      "Si":1.11,"P":1.07,"S":1.05,"Cl":1.02,"Cu":1.32,"B":0.84}
RAD ={"H":0.30,"C":0.42,"N":0.40,"O":0.40,"F":0.38,"Mg":0.66,"Al":0.60,
      "Si":0.55,"S":0.52,"Cl":0.52,"Cu":0.60,"B":0.45}

def read_xyz(path):
    L=open(path,encoding="utf-8").read().splitlines()
    n=int(L[0].split()[0]); els=[]; xyz=[]
    for ln in L[2:2+n]:
        p=ln.split(); els.append(p[0]); xyz.append([float(p[1]),float(p[2]),float(p[3])])
    return els,np.array(xyz)

def render(ax, path, view=(18,-70), no_metal_bonds=True, scale=1.0, zoom=1.0, shadow=True):
    els,X=read_xyz(path); X=X-X.mean(0)
    # bonds
    bonds=[]
    n=len(els)
    for i in range(n):
        for j in range(i+1,n):
            d=np.linalg.norm(X[i]-X[j])
            ri,rj=RCOV.get(els[i],0.7),RCOV.get(els[j],0.7)
            if d<1.20*(ri+rj):
                if no_metal_bonds and els[i]=="Mg" and els[j]=="Mg": continue
                bonds.append((i,j))
    for i,j in bonds:
        ax.plot(*zip(X[i],X[j]),color="#5a5a5a",lw=1.1,zorder=2)
    # atoms (size by radius, depth-shaded)
    sizes=np.array([(RAD.get(e,0.4)*scale*46)**2*0.5 for e in els])
    cols=[CPK.get(e,"#AAAAAA") for e in els]
    ax.scatter(X[:,0],X[:,1],X[:,2],s=sizes,c=cols,edgecolors="black",linewidths=0.3,
               depthshade=shadow,zorder=3)
    ax.view_init(elev=view[0],azim=view[1])
    ax.set_box_aspect((np.ptp(X[:,0])+1,np.ptp(X[:,1])+1,np.ptp(X[:,2])+1))
    # tighten
    r=max(np.ptp(X,0))/2/zoom
    c=X.mean(0)
    ax.set_xlim(c[0]-r,c[0]+r); ax.set_ylim(c[1]-r,c[1]+r); ax.set_zlim(c[2]-r,c[2]+r)
    ax.set_axis_off()
    return els

def legend_handles(elements, COLS=None):
    from matplotlib.lines import Line2D
    seen=[e for e in dict.fromkeys(elements)]
    return [Line2D([0],[0],ls="none",marker="o",mfc=CPK.get(e,"#AAA"),mec="black",mew=0.3,
                   ms=5,label=e) for e in seen]
