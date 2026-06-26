#!/usr/bin/env python3
"""Side-view trajectory GIF for the SYMMETRIC two-slab (pbc=xyz+3dc+vacuum) geometry.
Crops z to the condensed block (both slabs + electrolyte), skipping the vacuum. Two Mg
slabs at top & bottom, electrolyte between. crimson=anion Al, green=Mg²⁺, grey=electrode,
orange/blue=POSS network (poly). gold bands = near-surface zones [face, +0.8nm].
args: <gro> <base_xtc> <label> <out.gif> [net]
"""
import sys, glob, os, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, imageio.v2 as imageio, MDAnalysis as mda
gro, base, label, out = sys.argv[1:5]; has_net = len(sys.argv) > 5 and sys.argv[5] == "net"
NF = 100
def chain(b): return [x for x in [b]+sorted(glob.glob(b.replace('.xtc', '.part*.xtc'))) if os.path.exists(x)]
u = mda.Universe(gro, chain(base))
slab = u.select_atoms("resname MGE"); al = u.select_atoms("resname ANI and name Al")
mg = u.select_atoms("resname MGC and (name Mg1 or name Mg2)"); thf = u.select_atoms("resname THF and name O*")
netO = u.select_atoms("(not resname MGE MGC ANI THF) and name O*") if has_net else None
netSi = u.select_atoms("(not resname MGE MGC ANI THF) and name Si*") if has_net else None
Lx = u.dimensions[0]/10
sz0 = slab.positions[:, 2]/10; zlo, zhi = sz0.min()-0.3, sz0.max()+0.3
nfr = len(u.trajectory); stride = max(1, nfr//NF)
def X(a): return a.positions[:, 0]/10
def Z(a): return a.positions[:, 2]/10
frames = []
for ts in u.trajectory[::stride]:
    sz = slab.positions[:, 2]/10; mid = (sz.min()+sz.max())/2
    fA = sz[sz < mid].max(); fB = sz[sz >= mid].min()
    fig, ax = plt.subplots(figsize=(4.2, 5.6), dpi=92)
    ax.axhspan(fA, fA+0.8, color='gold', alpha=.12, zorder=0); ax.axhspan(fB-0.8, fB, color='gold', alpha=.12, zorder=0)
    ax.scatter(X(slab), Z(slab), s=8, c='0.62', marker='s', zorder=2, label='Mg electrode')
    if has_net:
        ax.scatter(X(netO), Z(netO), s=3, c='tab:orange', alpha=.33, zorder=3, label='network O')
        ax.scatter(X(netSi), Z(netSi), s=4, c='tab:blue', alpha=.30, zorder=3, label='network Si')
    ax.scatter(X(thf), Z(thf), s=1.4, c='0.8', alpha=.4, zorder=2)
    ax.scatter(X(mg), Z(mg), s=22, c='tab:green', edgecolor='k', lw=.2, zorder=5, label='Mg²⁺')
    ax.scatter(X(al), Z(al), s=30, c='crimson', edgecolor='k', lw=.3, zorder=6, label='anion Al')
    ax.set_xlim(0, Lx); ax.set_ylim(zlo, zhi)
    ax.set_xlabel('x (nm)'); ax.set_ylabel('z (nm)  ⟂ electrodes')
    ax.set_title(f'{label}  t={ts.time/1000:.1f} ns  (symmetric 2-slab)', fontsize=9)
    ax.legend(loc='upper right', fontsize=6, framealpha=.9)
    fig.tight_layout(); fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    frames.append(np.frombuffer(fig.canvas.buffer_rgba(), np.uint8).reshape(h, w, 4)[:, :, :3].copy()); plt.close(fig)
imageio.mimsave(out, frames, fps=10, loop=0)
print(f"WROTE {out}  {len(frames)} frames  t_end={u.trajectory[-1].time/1000:.1f}ns  (total {nfr} frames)")
