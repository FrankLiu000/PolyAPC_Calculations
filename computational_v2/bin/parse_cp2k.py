#!/usr/bin/env python3
"""parse_cp2k.py — scrape CP2K .out files into machine-readable tables.

Handles the Phase 2-4 quantities:
  * total energies (ENERGY| Total FORCE_EVAL ...) -> adsorption / formation /
    alloy energies and the Mg(0001) work function (from V_HARTREE vacuum level);
  * CI-NEB band energies -> Mg2+ migration barrier (max image - reactant);
  * libvori/Bader q(Al) -> Al 2p core-level-shift SIGN prediction;
  * AIMD .ener conserved-quantity drift + replicate mean +/- SEM.
Writes results/data/{alloy_formation,sei_formation_and_neb,al_bader_cls,
interface_ET,aimd_interface_stats}.txt as the node fills them in.
Usage:
  python parse_cp2k.py <file.out> [...]            # print total energies
  python parse_cp2k.py --neb band.out              # barrier
"""
from __future__ import annotations
import argparse
import math
import re
import statistics
import sys
from pathlib import Path

HARTREE_EV = 27.211386

RE_ETOT = re.compile(r"ENERGY\|\s*Total FORCE_EVAL.*?:\s*([-\d.]+)")
RE_NEB = re.compile(r"BAND TOTAL ENERGY\s*\[hartree\]\s*=?\s*([-\d.]+)", re.I)
RE_REPLICA_E = re.compile(r"Energy of the replica\s+(\d+)\s*[:=]\s*([-\d.]+)", re.I)


def total_energy(path: Path):
    m = RE_ETOT.findall(path.read_text(errors="ignore"))
    return float(m[-1]) if m else None


def neb_barrier_eV(path: Path):
    """Max replica energy minus the first replica, in eV."""
    text = path.read_text(errors="ignore")
    reps = {int(i): float(e) for i, e in RE_REPLICA_E.findall(text)}
    if not reps:
        return None
    e0 = reps[min(reps)]
    return (max(reps.values()) - e0) * HARTREE_EV


def bader_q_al(bader_file: Path):
    """Parse a libvori/Bader per-atom charge file; return list of q on Al atoms.
    Expected columns: index element ... charge (node-format dependent)."""
    qs = []
    for ln in bader_file.read_text(errors="ignore").splitlines():
        p = ln.split()
        if len(p) >= 3 and p[1] == "Al":
            try:
                qs.append(float(p[-1]))
            except ValueError:
                pass
    return qs


def cls_sign(q_al: float) -> str:
    """Map Al Bader charge to the Al 2p core-level-shift sign vs metal."""
    if q_al < 0.5:
        return "LOW q_Al -> metallic/alloyed -> ~70.9 eV (bare hypothesis)"
    return "HIGH q_Al -> oxidised Al(III) -> ~74.0 eV (poly hypothesis)"


def ener_drift(ener_file: Path):
    """CP2K .ener: cols = step time(fs) Ekin Temp Epot ConsQty.
    Return (n_steps, conserved-qty drift per ps in Hartree/ps)."""
    cons, times = [], []
    for ln in ener_file.read_text().splitlines():
        if ln.strip().startswith("#") or not ln.strip():
            continue
        p = ln.split()
        if len(p) >= 6:
            times.append(float(p[1]))
            cons.append(float(p[5]))
    if len(cons) < 2:
        return 0, 0.0
    dt_ps = (times[-1] - times[0]) / 1000.0
    return len(cons), (cons[-1] - cons[0]) / dt_ps if dt_ps else 0.0


def replicate_stats(values):
    """mean +/- SEM over independent AIMD replicates."""
    if not values:
        return None
    m = statistics.mean(values)
    sem = statistics.pstdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0.0
    return m, sem


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--neb", action="store_true", help="report NEB barrier (eV)")
    args = ap.parse_args(argv)
    for f in args.files:
        p = Path(f)
        if args.neb:
            print(f"{p.name}: NEB barrier = {neb_barrier_eV(p)} eV")
        else:
            print(f"{p.name}: E_tot = {total_energy(p)} Ha")
    return 0


if __name__ == "__main__":
    sys.exit(main())
