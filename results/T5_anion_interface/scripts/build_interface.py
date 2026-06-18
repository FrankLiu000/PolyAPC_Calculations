#!/usr/bin/env python3
"""T5 — build a Mg(0001)|electrolyte interface for GROMACS (bare or poly).

Geometry: a frozen Mg(0001) slab at the bottom + the equilibrated electrolyte
above it, in a FULL 3D-periodic box. Through z-PBC this yields TWO equivalent
Mg(0001)|electrolyte interfaces (slab-top/elec-bottom and elec-top/slab-bottom),
with NO vacuum -> standard 3D PME, no evaporation. The slab is a non-reactive,
neutral, structureless-but-atomistic implicit electrode (UFF Mg LJ, q=0); it is
FROZEN in MD. This is a MODEL electrode for anion *dynamics* (concentration /
residence / flux), NOT a reactive/charged electrode (that is EPYC's T10/T4).

Mg(0001): a = 3.209 A, c = 5.211 A (experimental; matches EPYC's validated slab,
P0c_periodic/inp/slab_Mg0001_3x3x4.inp, Phi = 3.97 eV). Electrode LJ: UFF Mg
sigma = 0.26915 nm, eps = 0.4644 kJ/mol (Rappe 1992), comb-rule 3.

usage: build_interface.py <whole.gro> <src_top> <outdir> <nlayers>
  whole.gro : electrolyte made -pbc whole (cubic, equilibrated)
  src_top   : the electrolyte .top (its #includes are absolutised)
"""
import sys, os, math
from ase.build import hcp0001

A_MG = 3.209      # Angstrom, in-plane lattice
C_MG = 5.211      # Angstrom, hcp c
GAP  = 0.25       # nm, slab-face <-> electrolyte contact gap (each side)
MGE_SIG = 0.26915 # nm  (UFF Mg)
MGE_EPS = 0.4644  # kJ/mol

def read_gro(path):
    L = open(path).read().splitlines()
    title = L[0]; n = int(L[1])
    atoms = L[2:2+n]            # keep the raw lines (cols 0..44 = ids/names/xyz)
    box = [float(x) for x in L[2+n].split()]
    # parse z (and x,y) from fixed columns: x[20:28] y[28:36] z[36:44]
    xyz = [(float(a[20:28]), float(a[28:36]), float(a[36:44])) for a in atoms]
    return title, atoms, xyz, box

def main():
    whole, src_top, outdir, nlayers = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    os.makedirs(outdir, exist_ok=True)
    title, elines, exyz, ebox = read_gro(whole)
    Lx, Ly = ebox[0], ebox[1]
    # ---- slab: choose nx,ny (orthogonal hcp0001 surface cell = a x sqrt3*a) ----
    ax = A_MG/10.0; ay = A_MG*math.sqrt(3)/2/10.0   # nm (orthogonal hcp0001: x=a, y=a*sqrt3/2)
    nx = max(1, round(Lx/ax))
    ny = max(2, round(Ly/ay)); ny += ny % 2          # ASE requires ny even
    slab = hcp0001('Mg', size=(nx, ny, nlayers), a=A_MG, c=C_MG, orthogonal=True)
    s = slab.get_positions()/10.0                 # A -> nm
    sx, sy = slab.cell[0,0]/10.0, slab.cell[1,1]/10.0
    # rescale slab x,y to the electrolyte box (small frozen-lattice strain, labelled)
    s[:,0] *= Lx/sx; s[:,1] *= Ly/sy
    s[:,2] -= s[:,2].min()                          # slab bottom layer -> z=0
    slab_top = s[:,2].max()
    strain = (Lx/sx-1.0, Ly/sy-1.0)
    # ---- shift electrolyte so its bottom sits slab_top+GAP above the slab ----
    ezmin = min(z for _,_,z in exyz); ezmax = max(z for _,_,z in exyz)
    shift = (slab_top + GAP) - ezmin
    elec_extent = ezmax - ezmin
    box_z = slab_top + GAP + elec_extent + GAP      # PBC: elec-top + GAP = slab-bottom image
    nslab = len(s)
    # ---- write interface.gro : slab first, then electrolyte ----
    out = [title + " + Mg0001 slab", str(nslab + len(elines))]
    for i,(x,y,z) in enumerate(s):
        rid = (i % 99999) + 1
        out.append("%5d%-5s%5s%5d%8.3f%8.3f%8.3f" % (rid, "MGE", "MgEl", rid, x, y, z))
    for a,(x,y,z) in zip(elines, exyz):
        out.append(a[:20] + "%8.3f%8.3f%8.3f" % (x, y, z+shift) + a[44:])
    out.append("%10.5f%10.5f%10.5f" % (Lx, Ly, box_z))
    open(os.path.join(outdir,"interface.gro"),"w").write("\n".join(out)+"\n")
    # ---- electrode moleculetype (1-atom MGE of atomtype MgEl) ----
    open(os.path.join(outdir,"mgslab.itp"),"w").write(
        "[ moleculetype ]\n; name  nrexcl\nMGE      1\n\n"
        "[ atoms ]\n;  nr type resnr residue atom cgnr  charge   mass\n"
        "   1 MgEl     1     MGE  MgEl    1    0.0000  24.30500\n\n"
        "#ifdef POSRES_SLAB\n[ position_restraints ]\n; ai funct   kx    ky    kz\n"
        "   1    1   50000 50000 50000\n#endif\n")
    # ---- combined top: absolutise src #includes, inject atomtype + slab + molecule ----
    srcdir = os.path.dirname(os.path.abspath(src_top))
    atline = ("MgEl     12    24.30500  0.0000  A  %.6e  %.6e"
              " ; Mg(0001) electrode, UFF LJ, frozen, q=0 (MODEL)\n" % (MGE_SIG, MGE_EPS))
    T = []; injected = False
    for ln in open(src_top):
        st = ln.strip()
        if st.startswith("#include"):
            inc = st.split('"')[1]
            inc_abs = inc if os.path.isabs(inc) else os.path.normpath(os.path.join(srcdir, inc))
            if not injected:                 # inject electrode atomtype ONCE, before first include
                T.append(atline); injected = True
            T.append('#include "%s"\n' % inc_abs)
        elif st.startswith("[") and "system" in st.lower():
            T.append('#include "%s"\n\n' % os.path.join(os.path.abspath(outdir),"mgslab.itp"))
            T.append(ln)
        else:
            T.append(ln)
    # prepend MGE to [ molecules ]
    res = []; inmol = False
    for ln in T:
        res.append(ln)
        if ln.strip().lower().startswith("[ molecules") or ln.strip().lower()=="[molecules]":
            inmol = True; continue
        if inmol and ln.strip() and not ln.strip().startswith(";"):
            # first molecule line seen -> insert MGE before it
            res.insert(len(res)-1, "MGE      %d\n" % nslab); inmol = False
    open(os.path.join(outdir,"system.top"),"w").write("".join(res))
    # ---- index helper info ----
    print("system: %s" % whole)
    print("  box x,y = %.4f %.4f nm ; slab nx,ny,layers = %d,%d,%d -> %d Mg atoms"
          % (Lx, Ly, nx, ny, nlayers, nslab))
    print("  slab strain x,y = %.2f%%, %.2f%% (frozen LJ wall)" % (100*strain[0], 100*strain[1]))
    print("  slab_top = %.3f nm ; elec_extent = %.3f nm ; box_z = %.3f nm" % (slab_top, elec_extent, box_z))
    print("  two interfaces at z ~ %.2f (slab-top+gap) and ~ %.2f (PBC) nm" % (slab_top+GAP, box_z-GAP))
    print("  wrote interface.gro, system.top, mgslab.itp in %s" % outdir)

if __name__ == "__main__":
    main()
