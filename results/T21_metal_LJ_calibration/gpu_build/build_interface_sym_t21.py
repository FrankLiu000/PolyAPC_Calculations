#!/usr/bin/env python3
"""T21 SYMMETRIC two-slab builder — DFT-CALIBRATED FREE wall (EPYC T21).
Replaces the UFF+POSRES placeholder: MgEl = mg_metal.itp cohesive LJ (sigma 0.29436 nm,
eps 18.103 kJ/mol) so the slab SELF-COHERES; only the OUTER (vacuum-facing) layer of each
slab is weakly anchored (POSRES k=1000, moleculetype MGE_A), the surface + inner layers are
FREE. All MgEl-electrolyte cross terms come from mg_nbfix.itp ([nonbond_params], NOT the
combining rule). Two Mg(0001) slabs + electrolyte between, tight box (vacuum added later for 3dc).
usage: build_interface_sym_t21.py <elec.gro> <elec_top> <outdir> <nlayers>
"""
import sys, os, math
from ase.build import hcp0001
A_MG=3.209; C_MG=5.211; GAP=0.25; BACK_SEAM=0.30
MGE_SIG=0.29436; MGE_EPS=18.1032        # T21 mg_metal.itp (DFT-anchored cohesive LJ)
ANCHOR_K=1000; ANCHOR_THRESH=0.13       # weak anchor on the outermost (vacuum-facing) layer only
NBFIX="/lyz/Claude_workplace/polyAPC/storyT5/sym/mg_nbfix.itp"

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
    z_e=th+GAP; z_s2=z_e+ext+GAP; box_z=z_s2+th+BACK_SEAM; shift=z_e-ezmin
    # classify slab atoms: anchor the OUTERMOST layer of each slab (vacuum-facing), free the rest
    anc=[]; free=[]
    for (x,y,z) in s:                       # slab1 (bottom); vacuum-facing layer = z~0
        (anc if z < ANCHOR_THRESH else free).append((x,y,z))
    for (x,y,z) in s:                       # slab2 (top, +z_s2); vacuum-facing layer = z~th
        (anc if z > th-ANCHOR_THRESH else free).append((x,y,z+z_s2))
    nA=len(anc); nF=len(free)
    out=[title+" + 2x Mg0001 FREE slab (T21 calibrated wall)",str(nslab*2+len(elines))]; ri=0
    for (x,y,z) in anc+free:                 # anchored atoms FIRST (match [molecules] MGE_A,MGE), all resname MGE
        ri+=1; out.append("%5d%-5s%5s%5d%8.3f%8.3f%8.3f"%((ri%99999)+1,"MGE","MgEl",(ri%99999)+1,x,y,z))
    for a,(x,y,z) in zip(elines,exyz):
        out.append(a[:20]+"%8.3f%8.3f%8.3f"%(x,y,z+shift)+a[44:])
    out.append("%10.5f%10.5f%10.5f"%(Lx,Ly,box_z))
    open(os.path.join(outdir,"interface.gro"),"w").write("\n".join(out)+"\n")
    # electrode itp: MGE (free) + MGE_A (anchored, weak POSRES), both resname MGE
    open(os.path.join(outdir,"mgslab.itp"),"w").write(
        "[ moleculetype ]\n; name  nrexcl\nMGE      1\n[ atoms ]\n   1 MgEl 1 MGE MgEl 1 0.0000 24.30500\n\n"
        "[ moleculetype ]\n; name  nrexcl\nMGE_A    1\n[ atoms ]\n   1 MgEl 1 MGE MgEl 1 0.0000 24.30500\n"
        "#ifdef POSRES_SLAB\n[ position_restraints ]\n   1 1 %d %d %d\n#endif\n"%(ANCHOR_K,ANCHOR_K,ANCHOR_K))
    # top: inject MgEl atomtype (T21) + NBFIX include, then mgslab; [molecules] MGE_A nA, MGE nF
    srcdir=os.path.dirname(os.path.abspath(etop))
    atline=("MgEl     12    24.30500  0.0000  A  %.6e  %.6e ; Mg(0001) DFT-cohesive free-slab (T21 mg_metal)\n"%(MGE_SIG,MGE_EPS))
    T=[]; injected=False
    for ln in open(etop):
        st=ln.strip()
        if st.startswith("#include"):
            inc=st.split('"')[1]; inc_abs=inc if os.path.isabs(inc) else os.path.normpath(os.path.join(srcdir,inc))
            if not injected: T.append(atline); T.append('#include "%s"\n'%NBFIX); injected=True
            T.append('#include "%s"\n'%inc_abs)
        elif st.startswith("[") and "system" in st.lower():
            T.append('#include "%s"\n\n'%os.path.abspath(os.path.join(outdir,"mgslab.itp"))); T.append(ln)
        else: T.append(ln)
    res=[]; inmol=False
    for ln in T:
        res.append(ln)
        if ln.strip().lower().startswith("[ molecules") or ln.strip().lower()=="[molecules]": inmol=True; continue
        if inmol and ln.strip() and not ln.strip().startswith(";"):
            res.insert(len(res)-1,"MGE_A    %d\nMGE      %d\n"%(nA,nF)); inmol=False
    open(os.path.join(outdir,"system.top"),"w").write("".join(res))
    print("T21 SYM build -> %s : 2x slab %d Mg (anchor %d outer / free %d), strain %.1f%%,%.1f%%"%(outdir,nslab,nA,nF,100*strain[0],100*strain[1]))
    print("  MgEl LJ sigma=%.5f eps=%.4f (cohesive); NBFIX for all MgEl-electrolyte; box %.2fx%.2fx%.2f"%(MGE_SIG,MGE_EPS,Lx,Ly,box_z))

if __name__=="__main__": main()
