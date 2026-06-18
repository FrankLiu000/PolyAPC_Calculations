#!/usr/bin/env python3
"""build_structures.py — generate starting geometries for the poly-APC v2 campaign.

Writes into computational_v2/common/struct/:
  * molecular fragments (.xyz): the Schlenk APC anion ladder, neutrals, solvents,
    triflate species, and the Mg cation, derived from the repo MD seed .pdb files
    (real [AlPh2Cl2]- and [Mg2Cl3(THF)6]+ geometries) + geometric/RDKit construction.
  * periodic phases (.cif + .xyz): Mg hcp, Al fcc, MgO, MgF2, MgCl2, Al2O3, AlF3,
    Mg17Al12 (beta), Mg(0001) slabs (3x3x4 and 4x4x4), Al-adatom slabs, dilute
    Al-in-Mg substitution, and bare/poly interface boxes.

These are *starting* geometries: G16 (opt) and CP2K (CELL_OPT/GEO_OPT) refine them.
Run from anywhere; paths are resolved relative to this file.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
STRUCT = HERE.parent / "common" / "struct"
SEEDS = (REPO / "classical_molecular_dynamics" / "handoff_for_agent"
         / "structures" / "representative_solvation")

STRUCT.mkdir(parents=True, exist_ok=True)
BUILT: dict[str, str] = {}   # filename -> formula/description, for verification

# --------------------------------------------------------------------------- #
# PDB helpers
# --------------------------------------------------------------------------- #
_TWO_LETTER = {"CL": "Cl", "MG": "Mg", "AL": "Al", "SI": "Si"}


def _elem_from_name(name: str) -> str:
    a = "".join(c for c in name if c.isalpha())
    if a[:2].upper() in _TWO_LETTER:
        return _TWO_LETTER[a[:2].upper()]
    return a[0].upper()


def read_pdb_residue(pdb: Path, resname: str):
    """Return list of (element, np.array([x,y,z])) for a given residue name."""
    atoms = []
    for line in pdb.read_text().splitlines():
        if not line.startswith("ATOM"):
            continue
        if line[17:20].strip() != resname:
            continue
        elem = line[76:78].strip()
        if not elem:
            elem = _elem_from_name(line[12:16].strip())
        xyz = np.array([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        atoms.append((elem, xyz))
    return atoms


def write_xyz(name: str, atoms, comment: str):
    p = STRUCT / f"{name}.xyz"
    lines = [str(len(atoms)), comment]
    for el, xyz in atoms:
        lines.append(f"{el:2s} {xyz[0]:14.6f} {xyz[1]:14.6f} {xyz[2]:14.6f}")
    p.write_text("\n".join(lines) + "\n")
    formula = _formula([el for el, _ in atoms])
    BUILT[p.name] = f"{formula} | {comment}"


def _formula(elems):
    from collections import Counter
    c = Counter(elems)
    return "".join(f"{e}{c[e]}" for e in sorted(c))


# --------------------------------------------------------------------------- #
# Geometry primitives for Al-centred species
# --------------------------------------------------------------------------- #
TET = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float)
TET /= np.linalg.norm(TET, axis=1, keepdims=True)
TRIG = np.array([[1, 0, 0], [-0.5, np.sqrt(3) / 2, 0], [-0.5, -np.sqrt(3) / 2, 0]], float)

D_ALCL = 2.15   # Al-Cl bond, Angstrom
D_ALC = 1.97    # Al-C(ipso) bond


def _rot_align(a, b):
    """Rotation matrix sending unit vector a onto unit vector b (Rodrigues)."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = float(np.dot(a, b))
    if np.linalg.norm(v) < 1e-8:
        return np.eye(3) if c > 0 else -np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1 / (1 + c))


def phenyl_template():
    """Harvest a rigid C6H5 group + its Al->ipso axis from the ANI residue."""
    atoms = read_pdb_residue(SEEDS / "bare_contact_ion_pair.pdb", "ANI")
    # ANI ordering: Al, Cl1, Cl2, CA0..CA5, HA1..HA5, CB0..CB5, HB1..HB5
    al = atoms[0][1]
    ring = atoms[3:14]              # CA0(ipso C) ..CA5, HA1..HA5  -> 6 C + 5 H
    ipso = ring[0][1]
    axis = (ipso - al)
    axis /= np.linalg.norm(axis)
    # store relative to ipso
    rel = [(el, xyz - ipso) for el, xyz in ring]
    return rel, axis


_PHEN_REL, _PHEN_AXIS = phenyl_template()


def place_phenyl(center, direction):
    """Return a phenyl group attached to an Al at `center` along unit `direction`."""
    R = _rot_align(_PHEN_AXIS, direction)
    ipso_pos = center + direction * D_ALC
    return [(el, ipso_pos + R @ rel) for el, rel in _PHEN_REL]


def build_al_species(name, ligands, geom, charge, comment):
    """ligands: list of 'Cl' or 'Ph' matched to geom direction vectors."""
    dirs = geom[: len(ligands)]
    atoms = [("Al", np.zeros(3))]
    for lig, d in zip(ligands, dirs):
        d = d / np.linalg.norm(d)
        if lig == "Cl":
            atoms.append(("Cl", d * D_ALCL))
        else:  # phenyl
            atoms.extend(place_phenyl(np.zeros(3), d))
    write_xyz(name, atoms, f"{comment} (charge {charge:+d})")


# --------------------------------------------------------------------------- #
# RDKit organics
# --------------------------------------------------------------------------- #
def build_rdkit(name, smiles, charge, comment):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        raise RuntimeError(f"RDKit could not parse {name}: {smiles}")
    m = Chem.AddHs(m)
    if AllChem.EmbedMolecule(m, randomSeed=0xC0FFEE) != 0:
        AllChem.EmbedMolecule(m, useRandomCoords=True, randomSeed=1)
    AllChem.MMFFOptimizeMolecule(m)
    conf = m.GetConformer()
    atoms = [(a.GetSymbol(), np.array(conf.GetAtomPosition(i)))
             for i, a in enumerate(m.GetAtoms())]
    write_xyz(name, atoms, f"{comment} (charge {charge:+d})")
    return atoms


def build_mgcl_thf():
    """[MgCl(THF)]+ : THF (RDKit) + Mg on the O, Cl on Mg."""
    thf = build_rdkit("_thf_tmp", "C1CCOC1", 0, "tmp")
    (STRUCT / "_thf_tmp.xyz").unlink(missing_ok=True)
    BUILT.pop("_thf_tmp.xyz", None)
    o_idx = [i for i, (el, _) in enumerate(thf) if el == "O"][0]
    o = thf[o_idx][1]
    cen = np.mean([x for _, x in thf], axis=0)
    out = (o - cen)
    out /= np.linalg.norm(out)            # point away from ring centroid
    mg = o + out * 2.05
    cl = mg + out * 2.25
    atoms = list(thf) + [("Mg", mg), ("Cl", cl)]
    write_xyz("MgCl_THF_cation", atoms, "[MgCl(THF)]+ (charge +1)")


# --------------------------------------------------------------------------- #
# Periodic phases via pymatgen
# --------------------------------------------------------------------------- #
def write_periodic():
    from pymatgen.core import Structure, Lattice

    def emit(name, struct, desc):
        struct.to(filename=str(STRUCT / f"{name}.cif"))
        # also an xyz of the conventional cell for quick viewing
        cart = struct.cart_coords
        atoms = [(str(s.specie), cart[i]) for i, s in enumerate(struct.sites)]
        write_xyz(name, atoms, desc)
        BUILT[f"{name}.cif"] = f"{struct.composition.reduced_formula} | {desc}"

    # Mg hcp
    emit("Mg_hcp", Structure.from_spacegroup(
        194, Lattice.hexagonal(3.209, 5.211), ["Mg"], [[1/3, 2/3, 1/4]]),
        "Mg metal hcp (mu_Mg reference)")
    # Al fcc (mu_Al reference)
    emit("Al_fcc", Structure.from_spacegroup(
        225, Lattice.cubic(4.0495), ["Al"], [[0, 0, 0]]),
        "Al metal fcc (mu_Al reference)")
    # MgO rocksalt
    emit("MgO", Structure.from_spacegroup(
        225, Lattice.cubic(4.212), ["Mg", "O"], [[0, 0, 0], [0.5, 0, 0]]),
        "MgO rocksalt")
    # MgF2 rutile
    emit("MgF2", Structure.from_spacegroup(
        136, Lattice.tetragonal(4.625, 3.052), ["Mg", "F"],
        [[0, 0, 0], [0.303, 0.303, 0]]), "MgF2 rutile (poly-specific SEI)")
    # MgCl2 (CdCl2 type, R-3m)
    emit("MgCl2", Structure.from_spacegroup(
        166, Lattice.hexagonal(3.636, 17.67), ["Mg", "Cl"],
        [[0, 0, 0], [0, 0, 0.25]]), "MgCl2 (CdCl2-type)")
    # Al2O3 corundum
    emit("Al2O3", Structure.from_spacegroup(
        167, Lattice.hexagonal(4.759, 12.991), ["Al", "O"],
        [[0, 0, 0.3522], [0.3064, 0, 0.25]]), "alpha-Al2O3 corundum")
    # AlF3 (R-3c, rhombohedral perovskite-like)
    emit("AlF3", Structure.from_spacegroup(
        167, Lattice.hexagonal(4.93, 12.45), ["Al", "F"],
        [[0, 0, 0], [0.430, 0, 0.25]]), "AlF3 rhombohedral")
    # Mg17Al12 (beta, I-43m, alpha-Mn type, 58 atoms): Mg on 2a,8c,24g; Al on 24g
    a = 10.56
    emit("Mg17Al12", Structure.from_spacegroup(
        217, Lattice.cubic(a),
        ["Mg", "Mg", "Mg", "Al"],
        [[0, 0, 0], [0.317, 0.317, 0.317],
         [0.356, 0.356, 0.042], [0.090, 0.090, 0.278]]),
        "Mg17Al12 beta (alpha-Mn type, approx Wyckoff -> CELL_OPT on node)")


def write_slabs_and_interfaces():
    from ase.build import hcp0001, add_adsorbate
    from ase.io import write as ase_write

    def ase_to_xyz(name, atoms_obj, desc):
        syms = atoms_obj.get_chemical_symbols()
        pos = atoms_obj.get_positions()
        write_xyz(name, list(zip(syms, pos)), desc)
        ase_write(str(STRUCT / f"{name}.cif"), atoms_obj)
        BUILT[f"{name}.cif"] = f"{atoms_obj.get_chemical_formula()} | {desc}"

    # Mg(0001) 3x3x4 = 36 Mg (reproduces prior Phi=3.97 eV slab)
    slab36 = hcp0001("Mg", size=(3, 3, 4), a=3.209, c=5.211, vacuum=12.0)
    ase_to_xyz("Mg0001_3x3x4", slab36, "Mg(0001) 3x3x4 slab (36 Mg)")

    # Mg(0001) 4x4x4 for interfaces (C ~ 35-40 A with vacuum)
    slab44 = hcp0001("Mg", size=(4, 4, 4), a=3.209, c=5.211, vacuum=16.0)
    ase_to_xyz("Mg0001_4x4x4", slab44, "Mg(0001) 4x4x4 slab (interface base)")

    # Al adatom on Mg(0001) at the four high-symmetry sites
    site_xy = {
        "ontop": (0.0, 0.0),
        "bridge": (slab36.cell[0][0] / 6, 0.0),
        "fcc": (slab36.cell[0][0] / 3, slab36.cell[1][1] / 3),
        "hcp": (2 * slab36.cell[0][0] / 3, slab36.cell[1][1] / 3),
    }
    for site, (dx, dy) in site_xy.items():
        s = slab36.copy()
        add_adsorbate(s, "Al", height=2.3, position=(dx, dy))
        ase_to_xyz(f"Mg0001_Al_{site}", s, f"Al adatom on Mg(0001), {site} site")

    # Dilute Al-in-Mg substitution (replace one surface Mg with Al)
    sub = slab36.copy()
    top_idx = int(np.argmax(sub.get_positions()[:, 2]))
    sub[top_idx].symbol = "Al"
    ase_to_xyz("Mg0001_AlSub", sub, "dilute Al-in-Mg substitution (1 surface Mg->Al)")

    # Interface boxes: slab + MGC cation + ANI anion + a couple of THF in vacuum.
    def stack(extra_atoms, name, desc):
        s = slab44.copy()
        ztop = s.get_positions()[:, 2].max()
        from ase import Atoms
        els = [e for e, _ in extra_atoms]
        pos = np.array([p for _, p in extra_atoms])
        pos -= pos.mean(axis=0)
        pos[:, 2] += ztop + 6.0 + (pos[:, 2].max() - pos[:, 2].min())
        pos[:, 0] += s.cell[0][0] / 2
        pos[:, 1] += s.cell[1][1] / 2
        s += Atoms(symbols=els, positions=pos)
        ase_to_xyz(name, s, desc)

    cation = read_pdb_residue(SEEDS / "bare_contact_ion_pair.pdb", "MGC")
    anion = read_pdb_residue(SEEDS / "bare_contact_ion_pair.pdb", "ANI")
    stack(cation + anion, "iface_bare",
          "bare interface: Mg(0001) + [Mg2Cl3(THF)6]+ + [AlPh2Cl2]- (F-free)")

    # poly interface: full cation + full anion (from poly_contact_ion_pair) PLUS
    # a carved polymer network (NET/TMS) fragment from poly_polymer_coordinated.
    cip_pdb = SEEDS / "poly_contact_ion_pair.pdb"
    cat_p = read_pdb_residue(cip_pdb, "MGC")
    an_p = read_pdb_residue(cip_pdb, "ANI")          # full 25-atom [AlPh2Cl2]-
    net_pdb = SEEDS / "poly_polymer_coordinated.pdb"
    net = read_pdb_residue(net_pdb, "NET") + read_pdb_residue(net_pdb, "TMS")
    stack(cat_p + an_p + net, "iface_poly",
          "poly interface: Mg(0001) + cation + [AlPh2Cl2]- + POSS/polyether(NET)+TMS")


# --------------------------------------------------------------------------- #
def main():
    # --- molecular: APC Schlenk ladder + neutrals (geometric construction) ---
    build_al_species("AlCl4m", ["Cl"] * 4, TET, -1, "AlCl4- tetrahedral")
    build_al_species("AlPhCl3m", ["Ph", "Cl", "Cl", "Cl"], TET, -1, "AlPhCl3-")
    build_al_species("AlPh3Clm", ["Ph", "Ph", "Ph", "Cl"], TET, -1, "AlPh3Cl-")
    build_al_species("AlPh4m", ["Ph"] * 4, TET, -1, "AlPh4-")
    build_al_species("AlCl3", ["Cl"] * 3, TRIG, 0, "AlCl3 trigonal planar")
    build_al_species("AlPh3", ["Ph"] * 3, TRIG, 0, "AlPh3 trigonal planar")

    # AlPh2Cl2- : use the real MD geometry (ANI residue)
    ani = read_pdb_residue(SEEDS / "bare_contact_ion_pair.pdb", "ANI")
    write_xyz("AlPh2Cl2m", ani, "[AlPh2Cl2]- (from MD seed) (charge -1)")

    # cation [Mg2Cl3(THF)6]+ from the MGC residue
    mgc = read_pdb_residue(SEEDS / "bare_contact_ion_pair.pdb", "MGC")
    write_xyz("Mg2Cl3_THF6_cation", mgc, "[Mg2Cl3(THF)6]+ (from MD seed) (charge +1)")

    # bridged Mg-(mu-Cl)-Al contact ion pair (neutral overall: cation+anion)
    cip = (read_pdb_residue(SEEDS / "bare_contact_ion_pair.pdb", "MGC")
           + read_pdb_residue(SEEDS / "bare_contact_ion_pair.pdb", "ANI"))
    write_xyz("Mg_Cl_Al_ionpair", cip, "Mg-(mu-Cl)-Al contact ion pair (charge 0)")

    # --- molecular: solvents / triflate (RDKit) ---
    build_rdkit("THF", "C1CCOC1", 0, "tetrahydrofuran")
    build_rdkit("Me2O", "COC", 0, "dimethyl ether (network-O model)")
    build_rdkit("OTfm", "C(F)(F)(F)S(=O)(=O)[O-]", -1, "triflate CF3SO3-")
    build_rdkit("TMSOTf", "C[Si](C)(C)OS(=O)(=O)C(F)(F)F", 0, "TMS triflate")
    build_mgcl_thf()

    # --- periodic phases + slabs + interfaces ---
    write_periodic()
    write_slabs_and_interfaces()

    # manifest for verification
    (HERE.parent / "common" / "struct_manifest.json").write_text(
        json.dumps(BUILT, indent=2, sort_keys=True))
    print(f"[build_structures] wrote {len(BUILT)} structure entries to {STRUCT}")
    for k in sorted(BUILT):
        print(f"  {k:28s} {BUILT[k]}")


if __name__ == "__main__":
    sys.exit(main())
