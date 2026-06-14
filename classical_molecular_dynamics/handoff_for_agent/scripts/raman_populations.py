#!/usr/bin/env python3
"""Story B -- MD population order-parameters for Raman-band mapping.

For one multiframe .gro + index, per Mg per frame, compute and aggregate:
  * free-anion proxy  = 1 - fraction(Mg with >=1 anion-Cl contact)   <-> 999/1002 cm-1 (+8%)
  * bridged fraction  = Mg in an intact [Mg2(mu-Cl)3] dimer
        (a Mg-Mg neighbour < R_MGMG AND >=2 bridging-Cl)             <-> 276 cm-1 (-30%)
  * dissociated frac  = 1 - bridged                                  <-> 181 cm-1 (x2.0)
  * bound-THF CN      = mean Mg-(THF O) first-shell coordination     <-> 1483 cm-1 (+3.2)
usage: raman_populations.py <multiframe.gro> <index.ndx> <label>
cutoffs (nm): Mg-anionCl 0.345, Mg-Clbridge 0.315, Mg-O 0.300, Mg-Mg 0.40
"""
import sys, math

R_ANCL, R_CLB, R_O, R_MGMG = 0.345, 0.315, 0.300, 0.40
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


def dist(a, b, box):
    s = 0.0
    for k in range(3):
        d = a[k] - b[k]; d -= box[k] * round(d / box[k]); s += d * d
    return math.sqrt(s)


g = read_ndx(ndx)
Mg = sorted(g["Mg"]); Clb = sorted(g["Clbridge"])
Othf = sorted(g["CoordO_THF"]); AnCl = sorted(g.get("AnionCl", []))
nfr = 0; paired = bridged = 0; thf_sum = 0.0; ntot = 0
for xs, box in frames(gro):
    nfr += 1
    for m in Mg:
        pm = xs[m]; ntot += 1
        if any(dist(pm, xs[j], box) < R_ANCL for j in AnCl):
            paired += 1
        ncl = sum(1 for j in Clb if dist(pm, xs[j], box) < R_CLB)
        mgmg = min((dist(pm, xs[j], box) for j in Mg if j != m), default=9.9)
        if mgmg < R_MGMG and ncl >= 2:
            bridged += 1
        thf_sum += sum(1 for j in Othf if dist(pm, xs[j], box) < R_O)

free_anion = 1 - paired / ntot
brid = bridged / ntot
print("%-14s frames=%d  free-anion=%.3f  bridged=%.3f  dissociated=%.3f  boundTHF_CN=%.2f"
      % (label, nfr, free_anion, brid, 1 - brid, thf_sum / ntot))
with open("analysis/raman_pop_%s.txt" % label, "w") as o:
    o.write("system %s  (%d frames, %d Mg-samples)\n" % (label, nfr, ntot))
    o.write("free_anion %.4f\nbridged %.4f\ndissociated %.4f\nboundTHF_CN %.4f\n"
            % (free_anion, brid, 1 - brid, thf_sum / ntot))
