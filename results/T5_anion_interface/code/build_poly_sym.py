#!/usr/bin/env python3
"""Poly SYMMETRIC two-slab sandwich (network surgery) for pbc=xyz + ewald 3dc + vacuum.
Two 3-layer Mg(0001) slabs (POSRES), the POSS gel + electrolyte centred between them.
The network percolates XY only: cross-z NET1 bonded terms are CUT so the gel is a
finite film in z (it would otherwise span the 3dc vacuum and explode). Small molecules
made whole; NET1 left wrapped for the cut detection. Built tight (vacuum added later).
usage: build_poly_sym.py <wrapped_elec.gro> <elec_top> <full_net_itp> <outdir> <nlayers>
"""
import sys, os, math
from ase.build import hcp0001
A_MG=3.209; C_MG=5.211; GAP=0.25; BACK_SEAM=0.30; MGE_SIG=0.26915; MGE_EPS=0.4644

def read_gro(p):
    L=open(p).read().splitlines(); n=int(L[1]); at=L[2:2+n]
    xyz=[[float(a[20:28]),float(a[28:36]),float(a[36:44])] for a in at]
    return L[0],at,xyz,[float(x) for x in L[2+n].split()]

def moltype_atomcounts(itp):
    lines=open(itp).read().splitlines(); res=[]; i=0; cur=None; cnt=0; insec=None
    def flush():
        if cur is not None: res.append([cur,cnt])
    while i<len(lines):
        s=lines[i].strip()
        if s.startswith('[') and 'moleculetype' in s:
            flush(); j=i+1
            while j<len(lines) and (not lines[j].strip() or lines[j].strip().startswith(';')): j+=1
            cur=lines[j].split()[0]; cnt=0; insec=None
        elif s.startswith('[') and 'atoms' in s: insec='atoms'
        elif s.startswith('['): insec=None
        elif insec=='atoms' and s and not s.startswith(';'): cnt+=1
        i+=1
    flush(); return res

def main():
    wrapped,etop,nitp,outdir,nlayers=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5])
    os.makedirs(outdir,exist_ok=True)
    title,elines,exyz,ebox=read_gro(wrapped); Lx,Ly,Lz0=ebox[0],ebox[1],ebox[2]
    apm={m:c for m,c in moltype_atomcounts(nitp)}
    order=[]; inmol=False
    for ln in open(etop):
        s=ln.strip()
        if s.lower().startswith('[ molecules'): inmol=True; continue
        if inmol and s and not s.startswith(';') and not s.startswith('['):
            order.append([s.split()[0],int(s.split()[1])])
    # make small molecules whole around their first atom; NET1 kept wrapped
    idx=0; net_atoms=apm['NET1']
    for nm,cn in order:
        na=apm[nm]
        for _ in range(cn):
            if nm!='NET1':
                ax,ay,az=exyz[idx]
                for k in range(idx,idx+na):
                    for d,(L,a0) in enumerate(zip((Lx,Ly,Lz0),(ax,ay,az))):
                        while exyz[k][d]-a0> L/2: exyz[k][d]-=L
                        while exyz[k][d]-a0<-L/2: exyz[k][d]+=L
            idx+=na
    # two slabs matched to box
    ax=A_MG/10.0; ay=A_MG*math.sqrt(3)/2/10.0
    nx=max(1,round(Lx/ax)); ny=max(2,round(Ly/ay)); ny+=ny%2
    slab=hcp0001('Mg',size=(nx,ny,nlayers),a=A_MG,c=C_MG,orthogonal=True)
    s=slab.get_positions()/10.0; sx,sy=slab.cell[0,0]/10,slab.cell[1,1]/10
    s[:,0]*=Lx/sx; s[:,1]*=Ly/sy; s[:,2]-=s[:,2].min()
    th=s[:,2].max(); nslab=len(s)
    zmin=min(p[2] for p in exyz); zmax=max(p[2] for p in exyz); ext=zmax-zmin
    z_e=th+GAP; z_s2=z_e+ext+GAP; box_z=z_s2+th+BACK_SEAM; shift=z_e-zmin
    out=[title+" + 2x Mg0001 (poly sym)",str(2*nslab+len(elines))]; ri=0
    for (x,y,z) in s: ri+=1; out.append("%5d%-5s%5s%5d%8.3f%8.3f%8.3f"%((ri%99999)+1,"MGE","MgEl",(ri%99999)+1,x,y,z))
    for (x,y,z) in s: ri+=1; out.append("%5d%-5s%5s%5d%8.3f%8.3f%8.3f"%((ri%99999)+1,"MGE","MgEl",(ri%99999)+1,x,y,z+z_s2))
    for a,(x,y,z) in zip(elines,exyz): out.append(a[:20]+"%8.3f%8.3f%8.3f"%(x,y,z+shift)+a[44:])
    out.append("%10.5f%10.5f%10.5f"%(Lx,Ly,box_z))
    open(os.path.join(outdir,"interface.gro"),"w").write("\n".join(out)+"\n")
    # cut cross-z NET1 bonded terms (wrapped z; NET1 is the FIRST electrolyte molecule)
    netz=[exyz[i][2] for i in range(net_atoms)]
    def spans_z(ids):
        zz=[netz[i-1] for i in ids]; return (max(zz)-min(zz))>Lz0/2
    lines=open(nitp).read().splitlines(); o=[]; i=0; in_net=False; sec=None; mt=0
    cut={'bonds':0,'pairs':0,'angles':0,'dihedrals':0}; nat={'bonds':2,'pairs':2,'angles':3,'dihedrals':4}
    while i<len(lines):
        ln=lines[i]; s=ln.strip()
        if s.startswith('[') and 'moleculetype' in s: mt+=1; in_net=(mt==1); sec=None; o.append(ln); i+=1; continue
        if s.startswith('['): nm=s.strip('[] ').split()[0]; sec=nm if nm in nat else None; o.append(ln); i+=1; continue
        if in_net and sec in nat and s and not s.startswith(';') and not s.startswith('#') and s.split()[0].lstrip('-').isdigit():
            ids=[int(x) for x in s.split()[:nat[sec]]]
            if spans_z(ids): cut[sec]+=1; i+=1; continue
        o.append(ln); i+=1
    open(os.path.join(outdir,"polyAPC_cut.itp"),"w").write("\n".join(o)+"\n")
    open(os.path.join(outdir,"mgslab.itp"),"w").write("[ moleculetype ]\n; name  nrexcl\nMGE      1\n\n[ atoms ]\n   1 MgEl     1     MGE  MgEl    1    0.0000  24.30500\n\n#ifdef POSRES_SLAB\n[ position_restraints ]\n   1 1 50000 50000 50000\n#endif\n")
    srcdir=os.path.dirname(os.path.abspath(etop))
    atline=("MgEl     12    24.30500  0.0000  A  %.6e  %.6e ; Mg(0001) electrode UFF frozen (MODEL)\n"%(MGE_SIG,MGE_EPS))
    T=[]; injected=False
    for ln in open(etop):
        s=ln.strip()
        if s.startswith('#include'):
            inc=s.split('"')[1]
            inc_abs=os.path.abspath(os.path.join(outdir,"polyAPC_cut.itp")) if ('polyAPC' in inc and inc.endswith('.itp')) else (inc if os.path.isabs(inc) else os.path.normpath(os.path.join(srcdir,inc)))
            if not injected: T.append(atline); injected=True
            T.append('#include "%s"\n'%inc_abs)
        elif s.startswith('[') and 'system' in s.lower():
            T.append('#include "%s"\n\n'%os.path.abspath(os.path.join(outdir,"mgslab.itp"))); T.append(ln)
        else: T.append(ln)
    res=[]; inmol=False
    for ln in T:
        res.append(ln)
        if ln.strip().lower().startswith('[ molecules'): inmol=True; continue
        if inmol and ln.strip() and not ln.strip().startswith(';'): res.insert(len(res)-1,"MGE      %d\n"%(2*nslab)); inmol=False
    open(os.path.join(outdir,"system.top"),"w").write("".join(res))
    print("poly sym build -> %s : 2x%d Mg, box %.2fx%.2fx%.2f nm, elec_ext=%.2f"%(outdir,nslab,Lx,Ly,box_z,ext))
    print("  NET1 cross-z CUT: bonds=%d pairs=%d angles=%d dih=%d (network now xy-percolating, z-finite)"%(cut['bonds'],cut['pairs'],cut['angles'],cut['dihedrals']))

if __name__=="__main__": main()
