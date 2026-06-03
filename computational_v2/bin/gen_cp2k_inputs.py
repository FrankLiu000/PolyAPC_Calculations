#!/usr/bin/env python3
"""gen_cp2k_inputs.py — generate CP2K input templates for poly-APC v2 (Phases 2-4).

Writes into:
  P0c_periodic/inp/   bulk CELL_OPT/GEO_OPT (SEI + alloy phases), Mg(0001) slab +
                      Al-adatom/substitution (E_ads, workfunction, Bader), CI-NEB
                      Mg2+ migration templates.
  P0d_interface/inp/  cp2k_cdft_marcus.inp (CDFT/Becke, N vs N+1 -> dG_ET, lambda),
                      cp2k_dirichlet_cpot.inp (fixed-potential charged slab + SCCS),
                      cp2k_aimd_realion.inp (NVT Nose real-ion interface AIMD).

Geometry for each job is emitted as a <name>.coord.inc (&CELL + &COORD) via the
ase2cp2k helpers and pulled in with @INCLUDE. Settings follow the validated prior
mg_slab.inp / md_apc.inp (PBE-D3, DZVP-MOLOPT-SR-GTH + GTH-PBE, CUTOFF 400/REL 50).
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

from ase.io import read as ase_read

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STRUCT = ROOT / "common" / "struct"
P0C = ROOT / "P0c_periodic" / "inp"
P0D = ROOT / "P0d_interface" / "inp"
P0C.mkdir(parents=True, exist_ok=True)
P0D.mkdir(parents=True, exist_ok=True)

# import cell_block/coord_block from ase2cp2k.py
_spec = importlib.util.spec_from_file_location("ase2cp2k", HERE / "ase2cp2k.py")
a2c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a2c)

# GTH-PBE potential q-values for the elements in this campaign
QVAL = {"H": 1, "C": 4, "O": 6, "F": 7, "Mg": 2, "Al": 3,
        "Si": 4, "S": 6, "Cl": 7}


def kinds(elements):
    out = []
    for el in sorted(set(elements)):
        out.append(f"      &KIND {el}\n"
                   f"        BASIS_SET DZVP-MOLOPT-SR-GTH\n"
                   f"        POTENTIAL GTH-PBE-q{QVAL[el]}\n"
                   f"      &END KIND")
    return "\n".join(out)


def write_coord_inc(name, struct_file, box=None):
    atoms = ase_read(struct_file)
    txt = a2c.cell_block(atoms, box=box) + "\n" + a2c.coord_block(atoms) + "\n"
    (struct_file.parent if False else (P0C if name.startswith(("bulk", "slab", "alloy", "neb"))
                                       else P0D))  # noqa: unused
    return atoms, txt


def _dft_block(cutoff=400, rel=50, smear=False, charge=0, added_mos=0,
               qs_extra="", dft_extra=""):
    """qs_extra is injected inside &QS (e.g. &CDFT); dft_extra inside &DFT
    (e.g. &POISSON, &SCCS) — both live under &DFT in CP2K."""
    smear_txt = ""
    if smear:
        smear_txt = f"""
      &SMEAR ON
        METHOD FERMI_DIRAC
        ELECTRONIC_TEMPERATURE [K] 500
      &END SMEAR
      ADDED_MOS {added_mos or 60}"""
    qs_inject = ("\n" + qs_extra) if qs_extra else ""
    dft_inject = ("\n" + dft_extra) if dft_extra else ""
    return f"""    &DFT
      BASIS_SET_FILE_NAME BASIS_MOLOPT
      POTENTIAL_FILE_NAME GTH_POTENTIALS
      CHARGE {charge}
      &MGRID
        CUTOFF {cutoff}
        REL_CUTOFF {rel}
      &END MGRID
      &QS
        EPS_DEFAULT 1.0E-12{qs_inject}
      &END QS
      &SCF
        SCF_GUESS ATOMIC
        EPS_SCF 1.0E-5
        MAX_SCF 60
        &OT ON
          MINIMIZER DIIS
          PRECONDITIONER FULL_SINGLE_INVERSE
        &END OT
        &OUTER_SCF ON
          MAX_SCF 20
          EPS_SCF 1.0E-5
        &END OUTER_SCF{smear_txt}
      &END SCF{dft_inject}
      &XC
        &XC_FUNCTIONAL PBE
        &END XC_FUNCTIONAL
        &VDW_POTENTIAL
          POTENTIAL_TYPE PAIR_POTENTIAL
          &PAIR_POTENTIAL
            TYPE DFTD3
            PARAMETER_FILE_NAME dftd3.dat
            REFERENCE_FUNCTIONAL PBE
          &END PAIR_POTENTIAL
        &END VDW_POTENTIAL
      &END XC
    &END DFT"""


def subsys(elements, inc_name):
    return f"""    &SUBSYS
      @INCLUDE '{inc_name}'
{kinds(elements)}
    &END SUBSYS"""


HEAD = """&GLOBAL
  PROJECT {proj}
  RUN_TYPE {run}
  PRINT_LEVEL MEDIUM
&END GLOBAL
"""


def write(path, text):
    path.write_text(text.rstrip() + "\n")


# --------------------------------------------------------------------------- #
def bulk(name, struct_file, metal):
    atoms = ase_read(struct_file)
    inc = f"{name}.coord.inc"
    write(P0C / inc, a2c.cell_block(atoms) + "\n" + a2c.coord_block(atoms) + "\n")
    els = atoms.get_chemical_symbols()
    # CELL_OPT first, then GEO_OPT (run CELL_OPT, then resubmit with RUN_TYPE GEO_OPT)
    txt = HEAD.format(proj=name, run="CELL_OPT") + f"""&FORCE_EVAL
  METHOD QS
{_dft_block(smear=metal, added_mos=80 if metal else 0)}
{subsys(els, inc)}
&END FORCE_EVAL
&MOTION
  &CELL_OPT
    OPTIMIZER LBFGS
    MAX_ITER 200
    KEEP_ANGLES .FALSE.
  &END CELL_OPT
  &GEO_OPT
    OPTIMIZER BFGS
    MAX_ITER 300
  &END GEO_OPT
&END MOTION
"""
    write(P0C / f"bulk_{name}.inp", txt)


def slab(name, struct_file, charge=0, workfunc=False, bader=False):
    atoms = ase_read(struct_file)
    inc = f"{name}.coord.inc"
    write(P0C / inc, a2c.cell_block(atoms) + "\n" + a2c.coord_block(atoms) + "\n")
    els = atoms.get_chemical_symbols()
    prints = ""
    if workfunc:
        prints += """
    &PRINT
      &V_HARTREE_CUBE
        STRIDE 2 2 1
      &END V_HARTREE_CUBE
    &END PRINT"""
    if bader:
        prints += """
    &PROPERTIES
      &RESP OFF
      &END RESP
    &END PROPERTIES
    ! libvori/Bader: run with -bader or post-process ELECTRON_DENSITY_CUBE
    &PRINT
      &E_DENSITY_CUBE
        STRIDE 2 2 2
      &END E_DENSITY_CUBE
    &END PRINT"""
    txt = HEAD.format(proj=name, run="GEO_OPT") + f"""&FORCE_EVAL
  METHOD QS
{_dft_block(smear=True, charge=charge, added_mos=120)}{prints}
{subsys(els, inc)}
&END FORCE_EVAL
&MOTION
  &GEO_OPT
    OPTIMIZER BFGS
    MAX_ITER 300
  &END GEO_OPT
  &CONSTRAINT
    &FIXED_ATOMS
      ! fix bottom two Mg layers (set indices on node from the slab geometry)
      LIST 1..18
    &END FIXED_ATOMS
  &END CONSTRAINT
&END MOTION
"""
    write(P0C / f"slab_{name}.inp", txt)


def neb(name, elements_hint):
    """CI-NEB template for Mg2+ migration through an SEI supercell (7 images).
    Endpoints (vacancy/interstitial start & end) are interpolated on the node;
    the replica coord files <name>_img{0..6}.coord.inc are referenced here."""
    reps = "\n".join(
        f"""    &REPLICA
      COORD_FILE_NAME {name}_img{i}.xyz
    &END REPLICA""" for i in range(7))
    txt = HEAD.format(proj=name, run="BAND") + f"""&FORCE_EVAL
  METHOD QS
{_dft_block(smear=False)}
    &SUBSYS
      ! &CELL + &KIND filled on node (supercell of the SEI phase)
{kinds(elements_hint)}
    &END SUBSYS
&END FORCE_EVAL
&MOTION
  &BAND
    BAND_TYPE CI-NEB
    NUMBER_OF_REPLICA 7
    K_SPRING 0.05
    &CI_NEB
      NSTEPS_IT 5
    &END CI_NEB
    &OPTIMIZE_BAND
      OPT_TYPE DIIS
      &DIIS
        MAX_STEPS 200
      &END DIIS
    &END OPTIMIZE_BAND
{reps}
  &END BAND
&END MOTION
"""
    write(P0C / f"neb_{name}.inp", txt)


# ---- P0d interface methods --------------------------------------------------
def cdft_marcus():
    atoms = ase_read(STRUCT / "iface_bare.xyz")
    inc = "iface_bare.coord.inc"
    write(P0D / inc, a2c.cell_block(atoms) + "\n" + a2c.coord_block(atoms) + "\n")
    els = atoms.get_chemical_symbols()
    # the Al-anion fragment atom list is set on node (atoms of [AlPh2Cl2]-)
    cdft = """        &CDFT
          TYPE_OF_CONSTRAINT BECKE
          &OUTER_SCF ON
            TYPE CDFT_CONSTRAINT
            OPTIMIZER NEWTON
            MAX_SCF 20
            EPS_SCF 1.0E-3
          &END OUTER_SCF
          &ATOM_GROUP
            ATOMS  {ANION_ATOM_LIST}     ! indices of the [AlPh2Cl2]- fragment
            COEFF 1.0
            CONSTRAINT_TYPE CHARGE
            ! states: TARGET = N (neutral anion) and N+1 (reduced) ->
            ! dG_ET and reorganisation energy lambda via the 4-point Marcus scheme
            TARGET 0.0
          &END ATOM_GROUP
          &BECKE_CONSTRAINT
            ADJUST_SIZE .TRUE.
            ATOMIC_RADII  Al 1.20  Cl 1.00  C 0.77  H 0.37
            CAVITY_CONFINE .TRUE.
            CAVITY_SHAPE VDW
          &END BECKE_CONSTRAINT
        &END CDFT"""
    txt = HEAD.format(proj="cdft_marcus", run="ENERGY") + f"""&FORCE_EVAL
  METHOD QS
{_dft_block(smear=True, added_mos=120, qs_extra=cdft)}
{subsys(els, inc)}
&END FORCE_EVAL
! ---- Marcus protocol (run as 4 jobs, bare AND poly): -----------------------
!  (1) state A geom, constraint N     -> E_AA
!  (2) state A geom, constraint N+1   -> E_AB
!  (3) state B geom, constraint N+1   -> E_BB
!  (4) state B geom, constraint N     -> E_BA
!  dG_ET = E_BB - E_AA ; lambda = 0.5*((E_AB-E_AA)+(E_BA-E_BB))
"""
    write(P0D / "cp2k_cdft_marcus.inp", txt)


def dirichlet_cpot():
    atoms = ase_read(STRUCT / "iface_bare.xyz")
    inc = "iface_bare.coord.inc"   # shared with cdft
    els = atoms.get_chemical_symbols()
    poisson_sccs = """      &POISSON
        POISSON_SOLVER IMPLICIT
        PERIODIC XYZ
        &IMPLICIT
          BOUNDARY_CONDITIONS MIXED_PERIODIC
          &DIRICHLET_BC
            &AA_PLANAR
              V_D 0.0          ! fixed electrode potential (scan on node)
              PARALLEL_PLANE XY
              X_XTNT 0.0 1.0
              Y_XTNT 0.0 1.0
              POSITION_OF_PLANE 2.0
            &END AA_PLANAR
          &END DIRICHLET_BC
        &END IMPLICIT
      &END POISSON
      ! ---- implicit THF solvent (SCCS) to screen the field ----
      &SCCS ON
        RELATIVE_PERMITTIVITY 7.43
        DERIVATIVE_METHOD CD3
        METHOD ANDREUSSI
      &END SCCS
      &PRINT
        &V_HARTREE_CUBE
        &END V_HARTREE_CUBE
      &END PRINT"""
    txt = HEAD.format(proj="dirichlet_cpot", run="ENERGY") + f"""&FORCE_EVAL
  METHOD QS
{_dft_block(smear=True, charge=0, added_mos=120, dft_extra=poisson_sccs)}
{subsys(els, inc)}
&END FORCE_EVAL
! NOTE: scan integer slab charges CHARGE = -2,-1,0,+1,+2 (capacitance/field
! response). DIRICHLET_BC / AA_PLANAR planar electrode at fixed potential is set
! under &DFT&POISSON&IMPLICIT on the node build; validate SCCS on neutral slab
! first. Cross-compare extracted ET energetics with the CDFT/Marcus numbers.
"""
    write(P0D / "cp2k_dirichlet_cpot.inp", txt)


def aimd_realion():
    for variant in ("bare", "poly"):
        atoms = ase_read(STRUCT / f"iface_{variant}.xyz")
        inc = f"iface_{variant}.coord.inc"
        write(P0D / inc, a2c.cell_block(atoms) + "\n" + a2c.coord_block(atoms) + "\n")
        els = atoms.get_chemical_symbols()
        txt = HEAD.format(proj=f"aimd_{variant}", run="MD") + f"""&FORCE_EVAL
  METHOD QS
{_dft_block(smear=True, added_mos=200)}
{subsys(els, inc)}
&END FORCE_EVAL
&MOTION
  &MD
    ENSEMBLE NVT
    STEPS 10000
    TIMESTEP 1.0
    TEMPERATURE 300
    &THERMOSTAT
      TYPE NOSE
      &NOSE
        TIMECON 50.0
      &END NOSE
    &END THERMOSTAT
  &END MD
  &CONSTRAINT
    &FIXED_ATOMS
      LIST 1..32   ! bottom 2 Mg layers of the 4x4x4 slab (set exact list on node)
    &END FIXED_ATOMS
  &END CONSTRAINT
&END MOTION
! >=3 replicates per condition (independent velocities); ~10 ps each;
! chain trajectories with --dependency=afterany so one AIMD runs at a time.
"""
        write(P0D / f"cp2k_aimd_realion_{variant}.inp", txt)


# --------------------------------------------------------------------------- #
def main():
    metals = {"Mg_hcp", "Al_fcc", "Mg17Al12"}
    insulators = ["MgF2", "MgCl2", "MgO", "Al2O3", "AlF3"]
    for name in list(metals) + insulators:
        bulk(name, STRUCT / f"{name}.cif", metal=name in metals)

    # Mg(0001) slab (workfunction reproduction) + Al adatom / substitution
    slab("Mg0001_3x3x4", STRUCT / "Mg0001_3x3x4.cif", workfunc=True, bader=True)
    for site in ("ontop", "bridge", "fcc", "hcp"):
        slab(f"Mg0001_Al_{site}", STRUCT / f"Mg0001_Al_{site}.cif", bader=True)
    slab("Mg0001_AlSub", STRUCT / "Mg0001_AlSub.cif", bader=True)

    for phase, els in (("MgF2", ["Mg", "F"]), ("MgCl2", ["Mg", "Cl"]),
                       ("MgO", ["Mg", "O"])):
        neb(phase, els)

    cdft_marcus()
    dirichlet_cpot()
    aimd_realion()

    n = len(list(P0C.glob("*.inp"))) + len(list(P0D.glob("*.inp")))
    print(f"[gen_cp2k_inputs] wrote {n} CP2K .inp templates "
          f"({len(list(P0C.glob('*.inp')))} periodic, {len(list(P0D.glob('*.inp')))} interface)")


if __name__ == "__main__":
    main()
