#!/usr/bin/env python3
"""T5-sym — SYMMETRIC Mg(0001) | electrolyte | Mg(0001) sandwich for pbc=xy + 3dc.

Two 3-layer Mg(0001) slabs (POSRES) with the electrolyte between them. Built TIGHT
(no outer vacuum) so EM + NPT(pbc=xyz, semiisotropic-z) can squeeze out inter-slab
voids and set 1 bar; the symmetric OUTER vacuum for ewald-geometry=3dc is added
afterwards (gmx editconf -box .. -c) before switching to pbc=xy for NVT+production.
During the tight NPT the two slabs sit back-to-back across the z-PBC seam (a harmless
prep artifact, BACK_SEAM gap); editconf -c then centres the block and opens symmetric
vacuum on both outer faces. Result: two TRULY independent, equivalent interfaces (no
z-PBC wrap, no single slab encircled by one connected electrolyte) -> removes the poly
two-face segregation artifact.

usage: build_interface_sym.py <elec.gro> <elec_top> <outdir> <nlayers>
  elec.gro : equilibrated electrolyte ONLY (no slab), any box (its x,y set the area)
  elec_top : its .top WITHOUT a slab  (MgEl atomtype + MGE molecule injected here)
"""
import sys, os, math
from ase.build import hcp0001

A_MG=3.209; C_MG=5.211          # Mg(0001) a,c (Angstrom)
GAP=0.25                        # nm, slab-face <-> electrolyte contact gap
BACK_SEAM=0.30                  # nm, back-to-back slab gap across z-PBC (prep only)
MGE_SIG=0.26915; MGE_EPS=0.4644 # UFF Mg LJ (nm, kJ/mol)

def read_gro(p):
    L=open(p).read().splitlines(); n=int(L[1]); at=L[2:2+n]
    xyz=[(float(a[20:28]),float(a[28:36]),float(a[36:44])) for a in at]
    return L[0],at,xyz,[float(x) for x in L[2+n].split()]

def main():
    elec,etop,outdir,nlayers=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4])
    os.makedirs(outdir,exist_ok=True)
    title,elines,exyz,ebox=read_gro(elec); Lx,Ly=ebox[0],ebox[1]
    ax=A_MG/10.0; ay=A_MG*math.sqrt(3)/2/10.0
    nx=max(1,round(Lx/ax)); ny=max(2,round(Ly/ay)); ny+=ny%2
    slab=hcp0001('Mg',size=(nx,ny,nlayers),a=A_MG,c=C_MG,orthogonal=True)
    s=slab.get_positions()/10.0; sx,sy=slab.cell[0,0]/10,slab.cell[1,1]/10
    s[:,0]*=Lx/sx; s[:,1]*=Ly/sy; s[:,2]-=s[:,2].min()
    th=s[:,2].max(); nslab=len(s); strain=(Lx/sx-1,Ly/sy-1)
    ezmin=min(z for *_,z in exyz); ezmax=max(z for *_,z in exyz); ext=ezmax-ezmin
    # ---- tight z layout: slab1[0,th] | GAP | elec | GAP | slab2 | BACK_SEAM(=PBC seam) ----
    z_e=th+GAP; z_s2=z_e+ext+GAP; box_z=z_s2+th+BACK_SEAM; shift=z_e-ezmin
    ri=0
    out=[title+" + 2x Mg0001 (sym sandwich)",str(2*nslab+len(elines))]
    for (x,y,z) in s:                # slab1 (bottom)
        ri+=1; out.append("%5d%-5s%5s%5d%8.3f%8.3f%8.3f"%((ri%99999)+1,"MGE","MgEl",(ri%99999)+1,x,y,z))
    for (x,y,z) in s:                # slab2 (top)
        ri+=1; out.append("%5d%-5s%5s%5d%8.3f%8.3f%8.3f"%((ri%99999)+1,"MGE","MgEl",(ri%99999)+1,x,y,z+z_s2))
    for a,(x,y,z) in zip(elines,exyz):    # electrolyte (middle)
        out.append(a[:20]+"%8.3f%8.3f%8.3f"%(x,y,z+shift)+a[44:])
    out.append("%10.5f%10.5f%10.5f"%(Lx,Ly,box_z))
    open(os.path.join(outdir,"interface.gro"),"w").write("\n".join(out)+"\n")
    # ---- electrode moleculetype (1-atom MGE, POSRES) ----
    open(os.path.join(outdir,"mgslab.itp"),"w").write(
        "[ moleculetype ]\n; name  nrexcl\nMGE      1\n\n[ atoms ]\n"
        ";  nr type resnr residue atom cgnr  charge   mass\n"
        "   1 MgEl     1     MGE  MgEl    1    0.0000  24.30500\n\n"
        "#ifdef POSRES_SLAB\n[ position_restraints ]\n; ai funct   kx    ky    kz\n"
        "   1    1   50000 50000 50000\n#endif\n")
    # ---- combined top: absolutise includes, inject electrode atomtype + slab, prepend MGE(2x) ----
    srcdir=os.path.dirname(os.path.abspath(etop))
    atline=("MgEl     12    24.30500  0.0000  A  %.6e  %.6e"
            " ; Mg(0001) electrode, UFF LJ, frozen, q=0 (MODEL)\n"%(MGE_SIG,MGE_EPS))
    T=[]; injected=False
    for ln in open(etop):
        st=ln.strip()
        if st.startswith("#include"):
            inc=st.split('"')[1]; inc_abs=inc if os.path.isabs(inc) else os.path.normpath(os.path.join(srcdir,inc))
            if not injected: T.append(atline); injected=True
            T.append('#include "%s"\n'%inc_abs)
        elif st.startswith("[") and "system" in st.lower():
            T.append('#include "%s"\n\n'%os.path.abspath(os.path.join(outdir,"mgslab.itp"))); T.append(ln)
        else: T.append(ln)
    res=[]; inmol=False
    for ln in T:
        res.append(ln)
        if ln.strip().lower().startswith("[ molecules") or ln.strip().lower()=="[molecules]": inmol=True; continue
        if inmol and ln.strip() and not ln.strip().startswith(";"):
            res.insert(len(res)-1,"MGE      %d\n"%(2*nslab)); inmol=False
    open(os.path.join(outdir,"system.top"),"w").write("".join(res))
    print("SYM build -> %s"%outdir)
    print("  2x slab %d Mg (nx,ny,layers=%d,%d,%d); strain x,y=%.2f%%,%.2f%%; slab_thick=%.3f"%(nslab,nx,ny,nlayers,100*strain[0],100*strain[1],th))
    print("  tight box %.3f x %.3f x %.3f nm : slab1[0,%.2f] elec[%.2f,%.2f] slab2[%.2f,%.2f] seam=%.2f"%(Lx,Ly,box_z,th,z_e,z_e+ext,z_s2,z_s2+th,BACK_SEAM))
    print("  MGE total=%d ; elec_extent=%.3f"%(2*nslab,ext))
    print("  NEXT: EM -> NPT(pbc=xyz semiiso 1bar refcoord-scaling=com) -> editconf add vacuum -> pbc=xy ewald 3dc NVT")

if __name__=="__main__": main()
