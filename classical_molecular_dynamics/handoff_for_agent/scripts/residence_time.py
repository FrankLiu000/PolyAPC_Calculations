#!/usr/bin/env python3
"""Mg-anion ion-pair residence time via intermittent survival autocorrelation.

Prompted by the solvation/desolvation review: coordination EXCHANGE RATE (not just
static coordination) governs conductivity / transference. We quantify the Mg-anion
contact-ion-pair lifetime.

For each frame, the set of bound pairs P(t) = {(Mg i, anion-Cl j) : |r_ij| < R}.
Intermittent autocorrelation (Impey-Madden):
    C(tau) = < |P(t) ∩ P(t+tau)| / |P(t)| >_t
Reported: C(tau) curve + the 1/e correlation time (linear-interpolated), a proxy
for ion-pair lifetime / exchange rate. Larger tau_c = stiffer, slower-exchanging shell.

usage: residence_time.py <multiframe.gro> <index.ndx> <ns_per_frame> <label>
cutoff: Mg-anionCl 0.345 nm (matches solvation.py)
"""
import sys, math

R = 0.345
gro, ndx, nspf, label = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]


def read_ndx(path):
    g = {}; cur = None
    for line in open(path):
        s = line.strip()
        if s.startswith('['):
            cur = s.strip('[] ').strip(); g[cur] = []
        elif s and cur:
            g[cur] += [int(x) for x in s.split()]
    return g


def frames(path):
    f = open(path)
    while True:
        title = f.readline()
        if not title:
            break
        n = int(f.readline())
        xs = [None] * (n + 1)
        for i in range(1, n + 1):
            l = f.readline()
            xs[i] = (float(l[20:28]), float(l[28:36]), float(l[36:44]))
        box = [float(x) for x in f.readline().split()[:3]]
        yield xs, box


def d2(a, b, box):
    s = 0.0
    for k in range(3):
        d = a[k] - b[k]; d -= box[k] * round(d / box[k]); s += d * d
    return s


g = read_ndx(ndx)
Mg = sorted(g["Mg"]); AnCl = sorted(g["AnionCl"])
R2 = R * R
pairsets = []
for xs, box in frames(gro):
    P = set()
    for m in Mg:
        pm = xs[m]
        for j in AnCl:
            if d2(pm, xs[j], box) < R2:
                P.add((m, j))
    pairsets.append(P)

T = len(pairsets)
maxlag = T // 2
C = []
for tau in range(maxlag):
    num = den = 0
    for t in range(T - tau):
        p0 = pairsets[t]
        if p0:
            num += len(p0 & pairsets[t + tau]); den += len(p0)
    C.append(num / den if den else 0.0)

# 1/e correlation time (linear interpolation)
tau_c = None
for i in range(1, len(C)):
    if C[i] <= 1 / math.e:
        x0, x1, y0, y1 = (i - 1) * nspf, i * nspf, C[i - 1], C[i]
        tau_c = x0 + (y0 - 1 / math.e) / (y0 - y1) * (x1 - x0) if y0 != y1 else x1
        break

mean_pairs = sum(len(p) for p in pairsets) / T
with open(f"acf_{label}.xvg", "w") as o:
    o.write("# tau(ns)  C(tau)\n")
    for i, c in enumerate(C):
        o.write("%.3f %.4f\n" % (i * nspf, c))
print("%-12s frames=%d  <pairs/frame>=%.1f  C(1ns)=%.3f  C(5ns)=%.3f  tau_c(1/e)=%s ns"
      % (label, T, mean_pairs,
         C[min(int(1 / nspf), len(C) - 1)], C[min(int(5 / nspf), len(C) - 1)],
         "%.2f" % tau_c if tau_c else ">%.0f" % ((maxlag - 1) * nspf)))
