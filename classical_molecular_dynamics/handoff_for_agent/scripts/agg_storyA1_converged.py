#!/usr/bin/env python3
"""Story A.1 -- CONVERGED re-aggregation.

D(cation/anion) are taken unchanged from analysis/msd_storyA1 (robust), but the
free-carrier f is recomputed from the CONVERGED 70-100 ns window
(analysis/solv_storyA1_conv) because contact-pairing drifts over the first
~40-80 ns (see analysis/contact_timeseries.py finding). Reports f mean +/- SEM,
the f*D conductivity proxy ratio, and a propagated error on that ratio.

NB: D itself is still fit over 20-80 ns, which overlaps the pairing drift -- that
caveat is NOT fixed here (needs longer pre-eq / longer runs); only f is corrected.
"""
import os, math, re

MSD_DIR  = "analysis/msd_storyA1"
SOLV_DIR = "analysis/solv_storyA1_conv"
OUT      = "analysis/RESULTS_storyA1_converged.txt"
SYS      = {"bare": [1, 2, 3, 4, 5], "swollen8": [1, 2, 3, 4, 5]}
GRPS     = ["MgCluster", "Anion"]
TAG      = {"MgCluster": "cation [Mg2Cl3.6THF]+", "Anion": "anion [Ph2AlCl2]-"}


def d_mean(path):
    if not os.path.exists(path):
        return None
    v = [float(l.split()[1]) for l in open(path)
         if l[:1] not in "@#&\n" and l.strip() and len(l.split()) >= 2]
    return sum(v) / len(v) if v else None


def f_free(path):
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

L = ["=" * 74,
     "STORY A.1 (CONVERGED f, 70-100 ns)  --  8-POSS swollen vs bare-APC, 5x100 ns",
     "D: COM-MSD fit 20-80 ns (1e-5 cm^2/s) | f: converged 70-100 ns window | mean +/- SEM",
     "=" * 74, ""]
res = {}
for s, reps in SYS.items():
    for g in GRPS:
        m, sem, n = stats(D[(s, g)])
        res[(s, g)] = (m, sem)
        L.append("  %-9s %-24s D = %.4f +/- %.4f (n=%d)" % (s, TAG[g], m or 0, sem or 0, n))
    fm, fs, fn = stats(F[s])
    res[(s, "f")] = (fm, fs)
    per_f = ["%.3f" % x if x is not None else "NA" for x in F[s]]
    L.append("  %-9s free-carrier f (70-100ns) per-rep=%s -> f = %.3f +/- %.3f (n=%d)"
             % (s, per_f, fm or 0, fs or 0, fn))
    L.append("")

L.append("  -- mobility slowdown  bare -> swollen8 --")
for g in GRPS:
    b, p = res[("bare", g)][0], res[("swollen8", g)][0]
    if b and p:
        L.append("     %-10s  x%.2f" % (g, b / p))
L.append("")


def sd(s):  # <D(cat,an)> and its SEM (avg of the two ion D's)
    dc, ec = res[(s, "MgCluster")]
    da, ea = res[(s, "Anion")]
    return (dc + da) / 2.0, math.hypot(ec, ea) / 2.0


L.append("  -- conductivity proxy  sigma ~ f * <D(cat,an)>  (trend-level; sigma_coll = Story A.2) --")
fb, efb = res[("bare", "f")]
fp, efp = res[("swollen8", "f")]
db, edb = sd("bare")
dp, edp = sd("swollen8")
if None not in (fb, fp, db, dp) and fb and db:
    ratio = (fp * dp) / (fb * db)
    rel = math.sqrt((efp / fp) ** 2 + (edp / dp) ** 2 + (efb / fb) ** 2 + (edb / db) ** 2)
    L.append("     f(bare)=%.3f+/-%.3f  f(swollen)=%.3f+/-%.3f" % (fb, efb, fp, efp))
    L.append("     <D>bare=%.4f  <D>swollen=%.4f" % (db, dp))
    L.append("     sigma(swollen)/sigma(bare) = %.2f +/- %.2f   [f*D ratio, propagated SEM]"
             % (ratio, ratio * rel))
    L.append("     (campaign estimate was ~1.44; de-pairing-dominated, partly offset by D loss)")
L.append("")
L.append("  CAVEAT: D fit window (20-80 ns) overlaps the pairing drift -> D is over a")
L.append("  non-stationary state; a clean fix needs >=50 ns pre-eq or longer production.")

txt = "\n".join(L)
open(OUT, "w").write(txt + "\n")
print(txt)
