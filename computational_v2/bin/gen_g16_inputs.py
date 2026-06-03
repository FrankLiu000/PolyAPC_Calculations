#!/usr/bin/env python3
"""gen_g16_inputs.py — generate the full Gaussian 16 input fan-out for poly-APC v2.

Writes .gjf files into:
  P0a_speciation/gjf/   Schlenk anion ladder + neutrals + cation  (opt->TZVP SP)
  P0b_redox/gjf/        vertical & adiabatic IP/EA, reductive-decomposition scans,
                        cross-check functionals (wB97XD, M062X), diffuse EA (TZVPD)
  P1_SEI/gjf/           OTf-/TMSOTf reductive fragmentation scans (poly-specific)
  P3_raman/gjf/         opt freq (SMD) + gas-phase freq=raman for Raman activities

and appends every job to computational_v2/manifest.txt (name ncores mem phase dep).

Level of theory (consistent with prior work):
  B3LYP-D3(BJ)/def2-TZVP // def2-SVP, SMD(THF), int=ultrafine.
Species with optimised geometries already on the /CH node (prior .chk) are emitted
as %oldchk restarts (geom=check guess=read); the rest carry explicit coordinates
from common/struct/*.xyz.
"""
from __future__ import annotations
from pathlib import Path

from ase.data import atomic_numbers
from ase.io import read as ase_read

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                       # computational_v2/
STRUCT = ROOT / "common" / "struct"
MANIFEST = ROOT / "manifest.txt"

DISP = "EmpiricalDispersion=GD3BJ"
SMD = "SCRF=(SMD,Solvent=Tetrahydrofuran)"
TIGHT = "int=ultrafine"
SVP = "B3LYP/def2SVP"
TZVP = "B3LYP/def2TZVP"

# species that already have an optimised .chk on the node -> restart, no coords
PRIOR_CHK = {"AlPh2Cl2m": "ANI", "Mg2Cl3_THF6_cation": "MGC",
             "OTfm": "OTf", "TMSOTf": "TMSOTf",
             "POSS_cage": "POSS_cage", "polyether": "polyether"}

_manifest_lines: list[str] = []


# --------------------------------------------------------------------------- #
def load(name):
    """Return (symbols, positions, charge) from common/struct/<name>.xyz.
    Charge is parsed from the comment line '(charge ±N)'."""
    p = STRUCT / f"{name}.xyz"
    atoms = ase_read(p)
    comment = p.read_text().splitlines()[1]
    charge = 0
    if "charge" in comment:
        tok = comment.split("charge")[1].strip().split(")")[0].strip()
        charge = int(tok.replace("+", ""))
    return atoms.get_chemical_symbols(), atoms.get_positions(), charge


def n_electrons(symbols, charge):
    return sum(atomic_numbers[s] for s in symbols) - charge


def mult_for(symbols, charge):
    return 1 if n_electrons(symbols, charge) % 2 == 0 else 2


def sizing(natoms, has_phenyl, big=False):
    if big or natoms > 100:
        return 32, "64GB"
    if natoms > 40:
        return 24, "48GB"
    if natoms > 15 or has_phenyl:
        return 16, "24GB"
    return 8, "14GB"


def write_gjf(phase, name, route, title, charge, mult, *,
              symbols=None, positions=None, oldchk=None, extra="", dep=None,
              ncores=None, mem=None):
    d = ROOT / phase / "gjf"
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"%chk={name}.chk"]
    if oldchk:
        lines.insert(0, f"%oldchk={oldchk}.chk")
    if ncores is None:
        has_ph = bool(symbols) and symbols.count("C") >= 6
        ncores, mem = sizing(len(symbols) if symbols else 30, has_ph)
    lines += [f"%nprocshared={ncores}", f"%mem={mem}", route, "", title, "",
              f"{charge} {mult}"]
    if symbols is not None and positions is not None:
        for s, (x, y, z) in zip(symbols, positions):
            lines.append(f"{s:2s} {x:14.6f} {y:14.6f} {z:14.6f}")
    lines.append("")
    if extra:
        lines.append(extra)
        lines.append("")
    (d / f"{name}.gjf").write_text("\n".join(lines) + "\n")
    _manifest_lines.append(f"{name} {ncores} {mem} {phase}" + (f" {dep}" if dep else ""))


# --------------------------------------------------------------------------- #
def opt_then_tzvp(phase, name, symbols, positions, charge):
    """opt freq @SVP  ->  def2-TZVP single point (chained afterok)."""
    mult = mult_for(symbols, charge)
    if name in PRIOR_CHK:
        route_opt = (f"#p {SVP} {DISP} opt freq {SMD} {TIGHT} geom=check guess=read")
        write_gjf(phase, f"{name}_opt", route_opt, f"{name} opt/freq (restart)",
                  charge, mult, oldchk=PRIOR_CHK[name], symbols=symbols)
    else:
        route_opt = f"#p {SVP} {DISP} opt freq {SMD} {TIGHT}"
        write_gjf(phase, f"{name}_opt", route_opt, f"{name} opt/freq SVP",
                  charge, mult, symbols=symbols, positions=positions)
    route_sp = f"#p {TZVP} {DISP} {SMD} {TIGHT} geom=check guess=read"
    write_gjf(phase, f"{name}_tzvp", route_sp, f"{name} def2-TZVP SP",
              charge, mult, oldchk=f"{name}_opt", symbols=symbols,
              dep=f"{name}_opt")
    return mult


def redox(name, symbols, charge):
    """Vertical IP/EA SPs (parent geometry), adiabatic opt+freq of each ion,
    functional/diffuse cross-checks, and reductive-decomposition scans."""
    base_mult = mult_for(symbols, charge)
    for tag, dq in (("ox", +1), ("red", -1)):
        q2 = charge + dq
        m2 = mult_for(symbols, q2)
        # vertical: parent geometry from <name>_opt.chk
        route_v = f"#p {TZVP} {DISP} {SMD} {TIGHT} geom=check guess=read"
        write_gjf("P0b_redox", f"{name}_{tag}_vert", route_v,
                  f"{name} vertical {tag} (q={q2:+d})", q2, m2,
                  oldchk=f"{name}_opt", symbols=symbols)
        # adiabatic: re-opt+freq the ion from the parent geometry
        route_a = f"#p {SVP} {DISP} opt freq {SMD} {TIGHT} geom=check guess=read"
        write_gjf("P0b_redox", f"{name}_{tag}_adia", route_a,
                  f"{name} adiabatic {tag} opt", q2, m2,
                  oldchk=f"{name}_opt", symbols=symbols, dep=f"{name}_tzvp")
        # cross-check functionals (single points at parent geometry)
        for fn, fname in (("wB97XD/def2TZVP", "wb97xd"),
                          ("M062X/def2TZVP", "m062x")):
            write_gjf("P0b_redox", f"{name}_{tag}_{fname}",
                      f"#p {fn} {DISP if 'wB97' not in fn else ''} {SMD} {TIGHT} "
                      f"geom=check guess=read".replace("  ", " "),
                      f"{name} {tag} {fname} SP", q2, m2,
                      oldchk=f"{name}_opt", symbols=symbols)
    # diffuse EA for anion reduction (extra electron needs diffuse functions)
    q_red = charge - 1
    write_gjf("P0b_redox", f"{name}_red_tzvpd",
              f"#p B3LYP/def2TZVPD {DISP} {SMD} {TIGHT} geom=check guess=read",
              f"{name} EA diffuse def2-TZVPD", q_red, mult_for(symbols, q_red),
              oldchk=f"{name}_opt", symbols=symbols)
    # reductive decomposition: stretch Al-Cl and Al-C(ipso) on the reduced anion
    decomp_scans(name, symbols, q_red)


def _first_index(symbols, target, after=0):
    for i, s in enumerate(symbols):
        if s == target and i >= after:
            return i + 1                  # Gaussian is 1-indexed
    return None


def decomp_scans(name, symbols, charge):
    """opt=(modredundant) bond-stretch toward Al-Cl / Al-C cleavage (SEI / Ph*)."""
    al = _first_index(symbols, "Al")
    if al is None:
        return
    mult = mult_for(symbols, charge)
    positions = ase_read(STRUCT / f"{name}.xyz").get_positions()
    cl = _first_index(symbols, "Cl")
    c = _first_index(symbols, "C")
    route = f"#p {SVP} {DISP} opt=modredundant {SMD} {TIGHT}"
    if cl:
        write_gjf("P0b_redox", f"{name}_red_AlClscan", route,
                  f"{name}+e- Al-Cl cleavage scan", charge, mult,
                  symbols=symbols, positions=positions,
                  extra=f"B {al} {cl} S 10 0.10")
    if c:
        write_gjf("P0b_redox", f"{name}_red_AlCscan", route,
                  f"{name}+e- Al-C cleavage scan", charge, mult,
                  symbols=symbols, positions=positions,
                  extra=f"B {al} {c} S 10 0.10")


# --------------------------------------------------------------------------- #
def p1_sei():
    """OTf- and TMSOTf reductive fragmentation (poly-specific F/S SEI precursors)."""
    for name, bonds in (("OTfm", [("C", "F", "C-F -> F-"), ("C", "S", "C-S -> SO3")]),
                        ("TMSOTf", [("Si", "O", "Si-O cleavage"),
                                    ("C", "F", "C-F -> F-")])):
        symbols, positions, charge = load(name)
        q = charge - 1                    # one extra electron (reductive)
        mult = mult_for(symbols, q)
        for a, b, desc in bonds:
            ia, ib = _first_index(symbols, a), _first_index(symbols, b)
            if ia and ib:
                write_gjf("P1_SEI", f"{name}_red_{a}{b}scan",
                          f"#p {SVP} {DISP} opt=modredundant {SMD} {TIGHT}",
                          f"{name}+e- {desc}", q, mult,
                          symbols=symbols, positions=positions,
                          extra=f"B {ia} {ib} S 10 0.10")


def p3_raman():
    """Raman/IR: opt freq (SMD, full) + gas-phase freq=raman for activities."""
    targets = ["THF", "MgCl_THF_cation", "AlPh2Cl2m", "polyether", "POSS_cage"]
    for name in targets:
        if name in PRIOR_CHK and not (STRUCT / f"{name}.xyz").exists():
            symbols, positions, charge = [], None, 0  # restart-only, coords unknown
            # use a generic medium size for restart-only species
            mult = 1
            route_opt = f"#p {TZVP} {DISP} opt freq {SMD} {TIGHT} geom=check guess=read"
            write_gjf("P3_raman", f"{name}_ramanopt", route_opt,
                      f"{name} opt/freq SMD (restart)", charge, mult,
                      oldchk=PRIOR_CHK[name], symbols=["C"] * 30, ncores=16, mem="24GB")
            write_gjf("P3_raman", f"{name}_ramangas",
                      f"#p {TZVP} {DISP} freq=raman {TIGHT} geom=check guess=read",
                      f"{name} gas-phase Raman activities", charge, mult,
                      oldchk=f"{name}_ramanopt", symbols=["C"] * 30,
                      ncores=16, mem="24GB", dep=f"{name}_ramanopt")
            continue
        symbols, positions, charge = load(name)
        mult = mult_for(symbols, charge)
        route_opt = f"#p {TZVP} {DISP} opt freq {SMD} {TIGHT}"
        write_gjf("P3_raman", f"{name}_ramanopt", route_opt,
                  f"{name} opt/freq SMD", charge, mult,
                  symbols=symbols, positions=positions)
        write_gjf("P3_raman", f"{name}_ramangas",
                  f"#p {TZVP} {DISP} freq=raman {TIGHT} geom=check guess=read",
                  f"{name} gas-phase Raman activities", charge, mult,
                  oldchk=f"{name}_ramanopt", symbols=symbols, dep=f"{name}_ramanopt")


# --------------------------------------------------------------------------- #
def main():
    speciation = ["AlCl4m", "AlPhCl3m", "AlPh2Cl2m", "AlPh3Clm", "AlPh4m",
                  "AlCl3", "AlPh3", "Mg2Cl3_THF6_cation", "Mg_Cl_Al_ionpair",
                  "OTfm", "TMSOTf", "THF", "Me2O", "MgCl_THF_cation"]
    # P0a + chained TZVP
    for name in speciation:
        symbols, positions, charge = load(name)
        opt_then_tzvp("P0a_speciation", name, symbols, positions, charge)

    # P0b redox ladder for the Al anions/neutrals + the Mg cation (reduction proxy)
    redox_species = ["AlCl4m", "AlPhCl3m", "AlPh2Cl2m", "AlPh3Clm", "AlPh4m",
                     "AlCl3", "AlPh3", "Mg2Cl3_THF6_cation"]
    for name in redox_species:
        symbols, _, charge = load(name)
        redox(name, symbols, charge)

    p1_sei()
    p3_raman()

    # header + write manifest
    hdr = ("# poly-APC v2 G16 job manifest  (name ncores mem phase [dep])\n"
           "# dep = afterok dependency jobname; throttle.sh keeps Sum(cores) <= 96\n")
    MANIFEST.write_text(hdr + "\n".join(_manifest_lines) + "\n")
    by_phase = {}
    for ln in _manifest_lines:
        by_phase[ln.split()[3]] = by_phase.get(ln.split()[3], 0) + 1
    print(f"[gen_g16_inputs] wrote {len(_manifest_lines)} G16 jobs -> manifest.txt")
    for ph, n in sorted(by_phase.items()):
        print(f"  {ph:18s} {n} jobs")


if __name__ == "__main__":
    main()
