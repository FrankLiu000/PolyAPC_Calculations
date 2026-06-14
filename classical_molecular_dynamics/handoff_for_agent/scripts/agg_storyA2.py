#!/usr/bin/env python3
"""Story A.2 aggregation -- large-cell collective conductivity & ionicity.

Reads:
  sigma/cur_full.log, sigma/cur_<b>.log   gmx current Einstein-Helfand "sigma=" (S/m)
  msd/msd_cat.xvg, msd/msd_an.xvg          gmx msd -mol per-molecule D (1e-5 cm^2/s)
  prod.gro                                 last-frame box -> volume
Computes Nernst-Einstein sigma_NE and ionicity = sigma_coll / sigma_NE.
N_cation = N_anion = 640 (8x80), z = +/-1.
"""
import os, re, glob

E = 1.602176634e-19      # C
KB = 1.380649e-23        # J/K
T = 298.0
N_ION = 640              # cations = anions = 8 * 80


def sigma_from_log(path):
    if not os.path.exists(path):
        return None
    m = re.search(r"sigma\s*=\s*([0-9.eE+-]+)", open(path).read())
    return float(m.group(1)) if m else None


def d_mean(path):  # mean per-molecule D, in 1e-5 cm^2/s
    if not os.path.exists(path):
        return None
    v = [float(l.split()[1]) for l in open(path)
         if l[:1] not in "@#&\n" and l.strip() and len(l.split()) >= 2]
    return sum(v) / len(v) if v else None


def box_volume_m3(gro):
    last = [ln for ln in open(gro) if ln.strip()][-1]
    a, b, c = (float(x) for x in last.split()[:3])   # nm
    return (a * b * c) * 1e-27, (a, b, c)


def stats(vals):
    vals = [v for v in vals if v is not None]
    n = len(vals)
    if n == 0:
        return None, 0.0, 0
    m = sum(vals) / n
    import math
    sem = (math.sqrt(sum((x - m) ** 2 for x in vals) / (n - 1)) / math.sqrt(n)) if n > 1 else 0.0
    return m, sem, n


sig_full = sigma_from_log("sigma/cur_full.log")
blocks = sorted(glob.glob("sigma/cur_[0-9]*.log"))
sig_blocks = [sigma_from_log(p) for p in blocks]
sb_m, sb_sem, sb_n = stats(sig_blocks)

Dc = d_mean("msd/msd_cat.xvg")   # 1e-5 cm^2/s
Da = d_mean("msd/msd_an.xvg")
V, box = box_volume_m3("prod.gro")

sig_NE = None
if Dc is not None and Da is not None:
    # sigma_NE = e^2/(V kB T) * sum_i N_i z_i^2 D_i ; D in m^2/s = (1e-5 cm^2/s)*1e-9
    sig_NE = (E * E / (V * KB * T)) * N_ION * (Dc * 1e-9 + Da * 1e-9)

L = ["=" * 70,
     "STORY A.2 -- large-cell (2x2x2, ~303k atoms) collective conductivity",
     "NVT 298 K production; sigma_coll via Einstein-Helfand (gmx current)",
     "=" * 70, ""]
L.append("  box = %.3f x %.3f x %.3f nm   V = %.4e m^3" % (box[0], box[1], box[2], V))
L.append("")
L.append("  sigma_coll (Einstein-Helfand, S/m):")
L.append("     full trajectory : %s" % ("%.4f" % sig_full if sig_full is not None else "NA"))
L.append("     per 50ns block  : %s" % (["%.4f" % x if x is not None else "NA" for x in sig_blocks]))
L.append("     block mean+/-SEM: %.4f +/- %.4f  (n=%d)" % (sb_m or 0, sb_sem, sb_n))
L.append("")
L.append("  D (gmx msd, fit 40-180 ns, 1e-5 cm^2/s):")
L.append("     cation = %s   anion = %s" % ("%.4f" % Dc if Dc else "NA", "%.4f" % Da if Da else "NA"))
if sig_NE is not None:
    L.append("  sigma_NE (Nernst-Einstein, S/m) = %.4f" % sig_NE)
    ref = sig_full if sig_full is not None else sb_m
    if ref:
        L.append("")
        L.append("  IONICITY  sigma_coll / sigma_NE = %.3f" % (ref / sig_NE))
        L.append("     (campaign reported ionicity ~0.08-0.13 -> heavily ion-associated;")
        L.append("      does the de-noised large cell corroborate the f*D mechanism?)")
txt = "\n".join(L)
print(txt)
