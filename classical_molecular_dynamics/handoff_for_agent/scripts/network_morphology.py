#!/usr/bin/env python3
"""Story C -- free-THF channel percolation + swelling, across poly systems.

Connected-cluster (union-find) analysis of the free-THF sub-phase: two free THF are
'connected' if their oxygens are within R_CONN. The largest-cluster fraction is a
percolation proxy -- a system-spanning fraction => a continuous liquid channel that
keeps ions mobile (ties to low Ea / Stokes-Einstein decoupling); a fragmented phase
=> pinched-off solvent (confinement). Also reports free-THF count, box, density-proxy.

usage: network_morphology.py <multiframe.gro> <index.ndx> <label>
"""
import sys, math

R_CONN = 0.70
gro, ndx, label = sys.argv[1], sys.argv[2], sys.argv[3]


def read_ndx(p):
    g = {}; cur = None
    for line in open(p):
        s = line.strip()
        if s.startswith('['):
            cur = s.strip('[] ').strip(); g[cur] = []
        elif s and cur:
            g[cur] += [int(x) for x in s.split()]
    return g


def frames(p):
    f = open(p)
    while True:
        t = f.readline()
        if not t:
            break
        n = int(f.readline())
        xs = [None] * (n + 1)
        for i in range(1, n + 1):
            l = f.readline(); xs[i] = (float(l[20:28]), float(l[28:36]), float(l[36:44]))
        box = [float(x) for x in f.readline().split()[:3]]
        yield xs, box


class UF:
    def __init__(s, n): s.p = list(range(n))
    def find(s, a):
        while s.p[a] != a: s.p[a] = s.p[s.p[a]]; a = s.p[a]
        return a
    def union(s, a, b): s.p[s.find(a)] = s.find(b)


g = read_ndx(ndx)
SolO = sorted(g.get("SolventO", []))   # one O per free THF
R2 = R_CONN * R_CONN
fracs = []; nfr = 0; lastbox = None
for xs, box in frames(gro):
    nfr += 1; lastbox = box
    pts = [xs[i] for i in SolO]; N = len(pts)
    # cell list for O(N) neighbour search
    rc = R_CONN; ncell = [max(1, int(box[k] / rc)) for k in range(3)]
    cells = {}
    for i, p in enumerate(pts):
        c = tuple(int((p[k] % box[k]) / box[k] * ncell[k]) % ncell[k] for k in range(3))
        cells.setdefault(c, []).append(i)
    uf = UF(N)
    for c, members in cells.items():
        neigh = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    nc = ((c[0] + dx) % ncell[0], (c[1] + dy) % ncell[1], (c[2] + dz) % ncell[2])
                    neigh += cells.get(nc, [])
        for i in members:
            pi = pts[i]
            for j in neigh:
                if j <= i: continue
                pj = pts[j]; d2 = 0.0
                for k in range(3):
                    d = pi[k] - pj[k]; d -= box[k] * round(d / box[k]); d2 += d * d
                if d2 < R2: uf.union(i, j)
    from collections import Counter
    sz = Counter(uf.find(i) for i in range(N))
    fracs.append(max(sz.values()) / N)

frac = sum(fracs) / len(fracs)
V = lastbox[0] * lastbox[1] * lastbox[2]
print("%-10s free-THF=%d  box=%.2f nm  largest-channel frac=%.3f  (%s)"
      % (label, len(SolO), lastbox[0], frac,
         "PERCOLATING/continuous" if frac > 0.7 else "fragmented/pinched" if frac < 0.4 else "intermediate"))
open("analysis/netmorph_%s.txt" % label, "w").write(
    "system %s\nfree_THF %d\nbox_nm %.3f\nvolume_nm3 %.1f\nlargest_channel_frac %.4f\n"
    % (label, len(SolO), lastbox[0], V, frac))
