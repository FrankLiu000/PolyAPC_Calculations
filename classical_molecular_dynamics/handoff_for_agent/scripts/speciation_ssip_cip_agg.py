#!/usr/bin/env python3
"""SSIP / CIP / AGG speciation from solvation.py per-frame records.

Refines the binary free/paired f into the standard ion-pairing taxonomy
(prompted by the solvation-vs-desolvation review): classify each Mg per frame by
its number of anion-Cl first-shell contacts (n_anionCl):
    0   -> SSIP  (solvent/own-cluster only; the 'free carrier')
    1   -> CIP   (one contact ion pair with an anion)
    >=2 -> AGG   (aggregate; multiple anion contacts)
Reports population fractions (mean +/- SEM over 5 reps) for bare vs swollen-8,
from the converged 70-100 ns window.  free-carrier f == SSIP fraction.
"""
import csv, math, glob, os

REC = "analysis/solv_storyA1_conv"
SYS = {"bare": "bare-APC", "swollen8": "8-POSS swollen"}


def classify_file(path):
    n = {"SSIP": 0, "CIP": 0, "AGG": 0}
    tot = 0
    with open(path) as fh:
        for row in csv.DictReader(fh):
            a = int(row["n_anionCl"]); tot += 1
            n["SSIP" if a == 0 else "CIP" if a == 1 else "AGG"] += 1
    return {k: v / tot for k, v in n.items()} if tot else None


def stats(vals):
    vals = [v for v in vals if v is not None]
    n = len(vals); m = sum(vals) / n
    sem = (math.sqrt(sum((x - m) ** 2 for x in vals) / (n - 1)) / math.sqrt(n)) if n > 1 else 0.0
    return m, sem


L = ["=" * 64,
     "Mg-anion SPECIATION  (SSIP / CIP / AGG)  -- converged 70-100 ns",
     "per-Mg classification by # anion-Cl first-shell contacts; mean +/- SEM (n=5 reps)",
     "free-carrier f == SSIP fraction",
     "=" * 64, ""]
res = {}
for s, label in SYS.items():
    perrep = {c: [] for c in ("SSIP", "CIP", "AGG")}
    for f in sorted(glob.glob(f"{REC}/{s}_r*_records.csv")):
        fr = classify_file(f)
        if fr:
            for c in perrep:
                perrep[c].append(fr[c])
    L.append("  %s:" % label)
    res[s] = {}
    for c in ("SSIP", "CIP", "AGG"):
        m, sem = stats(perrep[c]); res[s][c] = m
        tag = {"SSIP": "SSIP (free)", "CIP": "CIP (pair)", "AGG": "AGG (aggreg.)"}[c]
        L.append("     %-14s %5.1f%% +/- %.1f%%" % (tag, 100 * m, 100 * sem))
    L.append("     %-14s %5.1f%%   (CIP+AGG)" % ("paired total", 100 * (res[s]["CIP"] + res[s]["AGG"])))
    L.append("")

L.append("  -- bare -> swollen-8 shift --")
for c, tag in (("SSIP", "SSIP/free"), ("CIP", "CIP"), ("AGG", "AGG")):
    b, p = res["bare"][c], res["swollen8"][c]
    L.append("     %-10s %5.1f%% -> %5.1f%%   (%+.1f pts)" % (tag, 100 * b, 100 * p, 100 * (p - b)))
print("\n".join(L))
open("analysis/RESULTS_speciation_ssip_cip_agg.txt", "w").write("\n".join(L) + "\n")
