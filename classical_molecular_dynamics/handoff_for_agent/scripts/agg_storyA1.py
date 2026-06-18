#!/usr/bin/env python3
"""Story A.1 aggregator.

Reads per-replicate MSD -mol xvgs and per-replicate solvation summaries for two
systems -- bare-APC (reps 1-5) and 8-POSS swollen gel (seeds 1-5) -- and reports:
  * D(cation), D(anion) mean +/- SEM (COM-MSD, fit 20-80 ns), in 1e-5 cm^2/s
  * transference t+ = D+/(D+ + D-)
  * mobility slowdown bare -> swollen8
  * free-carrier fraction f = 1 - (Mg-with-anion-Cl-contact fraction)
  * trend-level conductivity proxy  sigma ~ f * <D(cat,an)>  and its ratio
    (NB: collective sigma_coll with error bars is Story A.2, not A.1.)
Generalises analysis/agg_replicates.py to the swollen system and 5 replicates.
"""
import os, math, re

MSD_DIR  = "analysis/msd_storyA1"
SOLV_DIR = "analysis/solv_storyA1"
OUT      = "analysis/RESULTS_storyA1.txt"
SYS      = {"bare": [1, 2, 3, 4, 5], "swollen8": [1, 2, 3, 4, 5]}
GRPS     = ["MgCluster", "Anion"]
TAG      = {"MgCluster": "cation [Mg2Cl3.6THF]+", "Anion": "anion [Ph2AlCl2]-"}


def d_mean(path):
    """Mean per-molecule D from a gmx msd -mol xvg (col 1), in 1e-5 cm^2/s."""
    if not os.path.exists(path):
        return None
    v = []
    for l in open(path):
        if l[:1] in "@#&\n" or not l.strip():
            continue
        p = l.split()
        if len(p) >= 2:
            v.append(float(p[1]))
    return sum(v) / len(v) if v else None


def f_free(path):
    """Free-carrier fraction f = 1 - contact-pairing fraction, from solvation summary."""
    if not os.path.exists(path):
        return None
    m = re.search(r"Mg with >=1 anion-Cl contact:\s*([\d.]+)%", open(path).read())
    return 1.0 - float(m.group(1)) / 100.0 if m else None


def stats(vals):
    vals = [v for v in vals if v is not None]
    n = len(vals)
    if n == 0:
        return None, 0.0, 0
    m = sum(vals) / n
    sem = (math.sqrt(sum((x - m) ** 2 for x in vals) / (n - 1)) / math.sqrt(n)) if n > 1 else 0.0
    return m, sem, n


D = {(s, g): [d_mean(f"{MSD_DIR}/{s}_r{r}_{g}.xvg") for r in reps]
     for s, reps in SYS.items() for g in GRPS}
F = {s: [f_free(f"{SOLV_DIR}/{s}_r{r}_summary.txt") for r in reps]
     for s, reps in SYS.items()}

L = []
L.append("=" * 72)
L.append("STORY A.1 RESULTS  --  8-POSS swollen (5x100 ns)  vs  bare-APC (5x100 ns)")
L.append("NVT 298 K | COM-MSD fit 20-80 ns | D in 1e-5 cm^2/s | mean +/- SEM over reps")
L.append("=" * 72)
L.append("")

res = {}
for s, reps in SYS.items():
    for g in GRPS:
        m, sem, n = stats(D[(s, g)])
        res[(s, g)] = (m, sem)
        per = ["%.4f" % x if x is not None else "NA" for x in D[(s, g)]]
        L.append("  %-9s %-24s reps=%s -> D = %.4f +/- %.4f (n=%d)"
                 % (s, TAG[g], per, m or 0, sem or 0, n))
    dp, dm = D[(s, "MgCluster")], D[(s, "Anion")]
    tpl = [a / (a + b) for a, b in zip(dp, dm) if a and b]
    if tpl:
        tm, ts, _ = stats(tpl)
        L.append("  %-9s t+ = D+/(D++D-) per-rep=%s -> %.3f +/- %.3f"
                 % (s, ["%.3f" % x for x in tpl], tm, ts))
    fm, fs, fn = stats(F[s])
    per_f = ["%.3f" % x if x is not None else "NA" for x in F[s]]
    L.append("  %-9s free-carrier f (=1-contact)  per-rep=%s -> f = %.3f +/- %.3f (n=%d)"
             % (s, per_f, fm or 0, fs or 0, fn))
    L.append("")

L.append("  -- mobility slowdown  bare -> swollen8 --")
for g in GRPS:
    b, p = res[("bare", g)][0], res[("swollen8", g)][0]
    if b and p:
        L.append("     %-10s  x%.2f" % (g, b / p))
L.append("")


def sigma_proxy(s):
    fm, _, _ = stats(F[s])
    dc, da = res[(s, "MgCluster")][0], res[(s, "Anion")][0]
    if None in (fm, dc, da):
        return None
    return fm * (dc + da) / 2.0


sb, sp = sigma_proxy("bare"), sigma_proxy("swollen8")
L.append("  -- conductivity proxy  sigma ~ f * <D(cat,an)>  (trend-level; sigma_coll = Story A.2) --")
if sb and sp:
    L.append("     sigma(swollen8) / sigma(bare) = %.2f   [f*D ratio; cf. campaign estimate ~1.44]" % (sp / sb))
else:
    L.append("     (insufficient data for f*D ratio)")
L.append("")
L.append("  inputs: MSD=%s/  solvation=%s/" % (MSD_DIR, SOLV_DIR))

txt = "\n".join(L)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(txt + "\n")
print(txt)
