#!/usr/bin/env python3
"""Animated NPT volume-convergence GIF from a GROMACS Box-Z .xvg.
args: <boxz.xvg> <label> <out.gif> <color>
"""
import sys, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, imageio.v2 as imageio
xvg, label, out, color = sys.argv[1:5]
d = np.array([[float(x) for x in l.split()] for l in open(xvg) if l.strip() and l[0] not in "@#&"])
t, z = d[:, 0], d[:, 1]
plateau = z[-max(1, int(len(z)*0.3)):].mean()
NF = 80; idx = np.unique(np.linspace(2, len(t), NF).astype(int))
zlo, zhi = z.min()-0.015, z.max()+0.015
frames = []
for k in idx:
    fig, ax = plt.subplots(figsize=(5.2, 3.7), dpi=100)
    ax.axhline(plateau, ls='--', color='0.55', lw=0.9, label=f'plateau {plateau:.3f} nm')
    ax.plot(t[:k], z[:k], '-', color=color, lw=1.6)
    ax.plot(t[k-1], z[k-1], 'o', color=color, ms=6)
    ax.set_xlim(t[0], t[-1]); ax.set_ylim(zlo, zhi)
    ax.set_xlabel('t (ps)'); ax.set_ylabel('box-z (nm)  ∝ volume')
    ax.set_title(f'{label} — NPT volume convergence\nt={t[k-1]:.0f} ps   box-z={z[k-1]:.3f} nm', fontsize=10)
    ax.legend(fontsize=8, loc='upper right'); ax.grid(alpha=.3)
    fig.tight_layout(); fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    frames.append(np.frombuffer(fig.canvas.buffer_rgba(), np.uint8).reshape(h, w, 4)[:, :, :3].copy())
    plt.close(fig)
frames += [frames[-1]] * 12
imageio.mimsave(out, frames, fps=12, loop=0)
print("WROTE", out, len(frames), "frames; plateau", round(plateau, 3), "nm")
