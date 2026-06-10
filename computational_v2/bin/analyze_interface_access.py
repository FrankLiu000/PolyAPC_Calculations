#!/usr/bin/env python3
"""analyze_interface_access.py — matched bare-vs-poly anion-access statistics.

For each interface AIMD trajectory (CP2K *-pos-1.xyz), tracks per frame:
  * Al height above the plating front (Al z  -  mean z of the 16 top-layer slab Mg)
  * minimum Al-to-SLAB-Mg distance (first 64 atoms only; the cation Mg2Cl3 core
    must NOT be counted - earlier analysis conflated them)
  * anion integrity on the final frame (Al-Cl / Al-C bond lengths)

Geometry conventions (both interfaces):
  slab Mg      = atoms 0..63
  anion        = atoms 147..171 (0-based; Al = atom 147)
  cell         = A (12.836, 0, 0); B (6.418, 11.116, 0); C 72 A  (PBC xy only here)

Usage: python3 analyze_interface_access.py <traj.xyz> <label> [out_prefix]
Writes <out_prefix>_access.txt (per-frame) and prints a summary block to stdout.
"""
import sys
import numpy as np

A = np.array([12.836, 0.0, 0.0])
B = np.array([6.418, 11.116, 0.0])
N_SLAB_MG = 64
AL_IDX = 147
ANION = list(range(147, 172))


def frames(path):
    """Yield (symbols, coords) per frame; tolerate a truncated final frame."""
    with open(path) as fh:
        while True:
            line = fh.readline()
            if not line:
                return
            try:
                nat = int(line.split()[0])
            except (ValueError, IndexError):
                return
            fh.readline()  # comment
            syms, xyz = [], []
            ok = True
            for _ in range(nat):
                ln = fh.readline()
                if not ln:
                    ok = False
                    break
                p = ln.split()
                if len(p) < 4:
                    ok = False
                    break
                syms.append(p[0])
                xyz.append([float(p[1]), float(p[2]), float(p[3])])
            if not ok:
                return
            yield syms, np.array(xyz)


def min_image_xy(d):
    """Minimum-image displacement(s) in the triclinic xy cell (z untouched)."""
    d = np.atleast_2d(d).astype(float)
    for vec in (B, A):  # B first (it has an x component), then A
        n = np.round(d[:, 1] / vec[1]) if vec[1] else np.round(d[:, 0] / vec[0])
        d -= np.outer(n, vec)
    return d


def analyze(path, label, out_prefix=None):
    heights, mindists, last = [], [], None
    for syms, x in frames(path):
        if len(x) <= max(ANION):
            continue
        slab_z = np.sort(x[:N_SLAB_MG, 2])[-16:]  # top layer
        surf = slab_z.mean()
        al = x[AL_IDX]
        heights.append(al[2] - surf)
        d = min_image_xy(al - x[:N_SLAB_MG])
        d[:, 2] = al[2] - x[:N_SLAB_MG, 2]
        mindists.append(np.sqrt((d ** 2).sum(axis=1)).min())
        last = (syms, x)
    h, m = np.array(heights), np.array(mindists)
    if out_prefix:
        np.savetxt(out_prefix + "_access.txt", np.column_stack([h, m]),
                   header="Al_height_above_surface[A]  Al_nearest_slabMg_dist[A] (%s, %d frames)"
                          % (label, len(h)))
    half = len(h) // 2
    print("%-10s frames=%5d  height: mean %.2f sd %.2f min %.2f | last-half mean %.2f"
          % (label, len(h), h.mean(), h.std(), h.min(), h[half:].mean()))
    print("%-10s            slabMg : mean %.2f sd %.2f min %.2f | last-half mean %.2f"
          % ("", m.mean(), m.std(), m.min(), m[half:].mean()))
    if last is not None:
        syms, x = last
        al = x[AL_IDX]
        bonds = []
        for i in ANION:
            if i == AL_IDX:
                continue
            r = np.linalg.norm(x[i] - al)
            if r < 2.6:
                bonds.append("%s%d %.2f" % (syms[i], i, r))
        print("%-10s final-frame Al bonds (<2.6 A): %s" % ("", "; ".join(bonds) or "NONE"))
    return h, m


if __name__ == "__main__":
    traj, label = sys.argv[1], sys.argv[2]
    pref = sys.argv[3] if len(sys.argv) > 3 else None
    analyze(traj, label, pref)
