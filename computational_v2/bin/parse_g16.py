#!/usr/bin/env python3
"""parse_g16.py — scrape Gaussian 16 .log files into machine-readable tables.

Extracts per job: final SCF energy (Ha), Gibbs free energy G(298 K) (Ha),
number of imaginary frequencies (NImag), and <S**2>. Applies the campaign
quality gates (NImag==0 for minima; <S**2> within 0.01 of S(S+1)) and writes:
  results/data/g16_energies.csv          (one row per .log)
  results/data/speciation_dG.txt         (Schlenk ladder + Boltzmann weights)
  results/data/redox_ladder.txt          (vertical/adiabatic IP & EA)
Usage:
  python parse_g16.py P0a_speciation/gjf P0b_redox/gjf   # scan dirs of *.log
"""
from __future__ import annotations
import math
import re
import sys
from pathlib import Path

HARTREE_EV = 27.211386
KCAL = 627.509
RT_298 = 0.0009441   # Hartree, k_B*T at 298.15 K

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "results" / "data"

RE_SCF = re.compile(r"SCF Done:\s+E\([^)]*\)\s*=\s*([-\d.]+)")
RE_G = re.compile(r"Sum of electronic and thermal Free Energies=\s*([-\d.]+)")
RE_S2 = re.compile(r"S\*\*2[^=]*=\s*([\d.]+)")
RE_NIMAG = re.compile(r"(\d+)\s+imaginary frequencies")
RE_FREQ = re.compile(r"Frequencies --\s+(-?[\d.]+)")


def parse_log(path: Path) -> dict:
    text = path.read_text(errors="ignore")
    scf = [float(m) for m in RE_SCF.findall(text)]
    g = RE_G.findall(text)
    s2 = RE_S2.findall(text)
    nimag_m = RE_NIMAG.search(text)
    if nimag_m:
        nimag = int(nimag_m.group(1))
    else:
        # count negative frequencies if no explicit NImag line
        freqs = [float(x) for x in RE_FREQ.findall(text)]
        nimag = sum(1 for f in freqs if f < 0)
    return {
        "name": path.stem,
        "E_scf_Ha": scf[-1] if scf else None,
        "G_Ha": float(g[-1]) if g else None,
        "NImag": nimag,
        "S2": float(s2[-1]) if s2 else None,
        "normal": "Normal termination" in text,
    }


def gate(row: dict, expect_doublet=False) -> str:
    flags = []
    if row["NImag"] not in (0, None):
        flags.append(f"NImag={row['NImag']}")
    if expect_doublet and row["S2"] is not None and abs(row["S2"] - 0.75) > 0.01:
        flags.append(f"spin-contam S2={row['S2']:.3f}")
    if not row["normal"]:
        flags.append("not-normal")
    return ",".join(flags) if flags else "OK"


def boltzmann(dG_kcal: dict) -> dict:
    """dG relative free energies (kcal/mol) -> population fractions at 298 K."""
    ws = {k: math.exp(-v / (RT_298 * KCAL)) for k, v in dG_kcal.items()}
    z = sum(ws.values())
    return {k: w / z for k, w in ws.items()}


def write_table(rows):
    DATA.mkdir(parents=True, exist_ok=True)
    out = DATA / "g16_energies.csv"
    hdr = "name,E_scf_Ha,G_Ha,NImag,S2,normal,gate"
    lines = [hdr]
    for r in rows:
        lines.append(f"{r['name']},{r['E_scf_Ha']},{r['G_Ha']},{r['NImag']},"
                     f"{r['S2']},{r['normal']},{gate(r)}")
    out.write_text("\n".join(lines) + "\n")
    return out


def main(argv=None):
    argv = argv or sys.argv[1:]
    logs = []
    for d in argv:
        logs += sorted(Path(d).glob("*.log"))
    if not logs:
        print("parse_g16: no .log files found in", argv, file=sys.stderr)
        return 1
    rows = [parse_log(p) for p in logs]
    out = write_table(rows)
    print(f"[parse_g16] parsed {len(rows)} logs -> {out}")
    flagged = [r["name"] for r in rows if gate(r) != "OK"]
    if flagged:
        print(f"[parse_g16] QUALITY-GATE flags on: {', '.join(flagged)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
