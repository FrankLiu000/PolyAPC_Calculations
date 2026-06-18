#!/usr/bin/env python3
"""T5 — build the POLY Mg(0001)|gel interface (handles the percolating network).

NET1 is one covalent network that percolates across all PBC faces. To present a
free electrode surface (break z-periodicity) we (i) keep NET1 in its WRAPPED
(compact) configuration, (ii) DELETE the NET1 bonded terms that span z (they would
otherwise explode to ~7 nm bonds once z-PBC is broken), and (iii) hold NET1 with
its existing POSRES_POSS restraints (k=1000, semi-rigid breathing gel film). The
small molecules (MGC/ANI/TMS/THF) are made whole per-molecule. Slab + stack as in
build_interface.py (two Mg(0001) interfaces via z-PBC). The cut network is a MODEL
gel film (its bulk structure/POSS loading is preserved; only ~surface cross-z bonds
are severed). Valid for the EQUILIBRIUM near-surface anion distribution; network
*dynamics* are restrained, so residence/flux are read from the bulk (separate).

usage: build_poly_interface.py <wrapped.gro> <src_top> <src_itp> <outdir> <nlayers>
"""
import sys, os, math
from ase.build import hcp0001

A_MG=3.209; C_MG=5.211; GAP=0.25; MGE_SIG=0.26915; MGE_EPS=0.4644

def read_gro(path):
    L=open(path).read().splitlines(); n=int(L[1]); atoms=L[2:2+n]
    xyz=[[float(a[20:28]),float(a[28:36]),float(a[36:44])] for a in atoms]
    box=[float(x) for x in L[2+n].split()]
    return L[0],atoms,xyz,box

def moltype_atomcounts(itp):
    """ordered list of (molname, natoms) from each [moleculetype] [atoms] block."""
    lines=open(itp).read().splitlines(); res=[]; i=0; cur=None; cnt=0; insec=None
    def flush():
        if cur is not None: res.append([cur,cnt])
    while i<len(lines):
        s=lines[i].strip()
        if s.startswith('[') and 'moleculetype' in s:
            flush()
            # next non-comment line = name
            j=i+1
            while j<len(lines) and (not lines[j].strip() or lines[j].strip().startswith(';')): j+=1
            globals()['_tmp']=lines[j].split()[0]; cur=lines[j].split()[0]; cnt=0; insec=None
        elif s.startswith('[') and 'atoms' in s: insec='atoms'
        elif s.startswith('['): insec=None
        elif insec=='atoms' and s and not s.startswith(';'): cnt+=1
        i+=1
    flush()
    return res

def main():
    wrapped,src_top,src_itp,outdir,nlayers=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5])
    os.makedirs(outdir,exist_ok=True)
    title,elines,exyz,ebox=read_gro(wrapped)
    Lx,Ly,Lz0=ebox[0],ebox[1],ebox[2]
    counts=moltype_atomcounts(src_itp)            # [[NET1,10119],[MGC,83],...]
    # molecule order/counts from [molecules]
    order=[]; inmol=False
    for ln in open(src_top):
        s=ln.strip()
        if s.lower().startswith('[ molecules'): inmol=True; continue
        if inmol and s and not s.startswith(';') and not s.startswith('['):
            nm,cn=s.split()[0],int(s.split()[1]); order.append([nm,cn])
    apm={m:c for m,c in counts}
    # ---- slice atoms into molecules; un-tear small molecules (NET1 left wrapped) ----
    idx=0; net_atoms=apm['NET1']
    for nm,cn in order:
        na=apm[nm]
        for _ in range(cn):
            blk=range(idx,idx+na)
            if nm!='NET1':                         # make small molecule whole around its first atom
                ax,ay,az=exyz[idx]
                for k in blk:
                    for d,(L,a0) in enumerate(zip((Lx,Ly,Lz0),(ax,ay,az))):
                        while exyz[k][d]-a0> L/2: exyz[k][d]-=L
                        while exyz[k][d]-a0<-L/2: exyz[k][d]+=L
            idx+=na
    # ---- build slab matched to box, stack ----
    ax=A_MG/10.0; ay=A_MG*math.sqrt(3)/2/10.0
    nx=max(1,round(Lx/ax)); ny=max(2,round(Ly/ay)); ny+=ny%2
    slab=hcp0001('Mg',size=(nx,ny,nlayers),a=A_MG,c=C_MG,orthogonal=True)
    s=slab.get_positions()/10.0; sx,sy=slab.cell[0,0]/10,slab.cell[1,1]/10
    s[:,0]*=Lx/sx; s[:,1]*=Ly/sy; s[:,2]-=s[:,2].min()
    slab_top=s[:,2].max(); nslab=len(s)
    zmin=min(p[2] for p in exyz); zmax=max(p[2] for p in exyz)
    shift=(slab_top+GAP)-zmin; box_z=slab_top+GAP+(zmax-zmin)+GAP
    # ---- write interface.gro: slab, then electrolyte (NET1 first per order) ----
    out=[title+" + Mg0001 slab (poly)",str(nslab+len(elines))]
    for i,(x,y,z) in enumerate(s):
        rid=(i%99999)+1; out.append("%5d%-5s%5s%5d%8.3f%8.3f%8.3f"%(rid,"MGE","MgEl",rid,x,y,z))
    for a,(x,y,z) in zip(elines,exyz):
        out.append(a[:20]+"%8.3f%8.3f%8.3f"%(x,y,z+shift)+a[44:])
    out.append("%10.5f%10.5f%10.5f"%(Lx,Ly,box_z))
    open(os.path.join(outdir,"interface.gro"),"w").write("\n".join(out)+"\n")
    # ---- NET1 z (wrapped) for cross-z detection ----
    netz=[exyz[i][2] for i in range(net_atoms)]    # NOTE: exyz still pre-shift; wrapped frame
    def spans_z(ids):
        zz=[netz[i-1] for i in ids]                # itp atom indices are 1-based
        return (max(zz)-min(zz))>Lz0/2
    # ---- rewrite NET1 itp sections, dropping cross-z terms ----
    lines=open(src_itp).read().splitlines()
    o=[]; i=0; in_net=False; sec=None; cut={'bonds':0,'pairs':0,'angles':0,'dihedrals':0}
    natom_seen=0; mt_count=0
    nat={'bonds':2,'pairs':2,'angles':3,'dihedrals':4}
    while i<len(lines):
        ln=lines[i]; s=ln.strip()
        if s.startswith('[') and 'moleculetype' in s:
            mt_count+=1; in_net=(mt_count==1); sec=None; o.append(ln); i+=1; continue
        if s.startswith('['):
            nm=s.strip('[] ').split()[0]; sec=nm if nm in nat else None
            o.append(ln); i+=1; continue
        if (in_net and sec in nat and s and not s.startswith(';')
                and not s.startswith('#') and s.split()[0].lstrip('-').isdigit()):
            ids=[int(x) for x in s.split()[:nat[sec]]]
            if spans_z(ids): cut[sec]+=1; i+=1; continue   # drop this term
        o.append(ln); i+=1
    open(os.path.join(outdir,"polyAPC_cut.itp"),"w").write("\n".join(o)+"\n")
    # ---- electrode itp ----
    open(os.path.join(outdir,"mgslab.itp"),"w").write(
        "[ moleculetype ]\n; name  nrexcl\nMGE      1\n\n[ atoms ]\n"
        "   1 MgEl     1     MGE  MgEl    1    0.0000  24.30500\n\n"
        "#ifdef POSRES_SLAB\n[ position_restraints ]\n   1 1 50000 50000 50000\n#endif\n")
    # ---- combined top: replace the poly itp include with the CUT itp, inject electrode ----
    srcdir=os.path.dirname(os.path.abspath(src_top))
    atline=("MgEl     12    24.30500  0.0000  A  %.6e  %.6e ; Mg(0001) electrode UFF, frozen (MODEL)\n"%(MGE_SIG,MGE_EPS))
    T=[]; injected=False
    for ln in open(src_top):
        s=ln.strip()
        if s.startswith('#include'):
            inc=s.split('"')[1]
            inc_abs=os.path.abspath(os.path.join(outdir,"polyAPC_cut.itp")) if inc.endswith("polyAPC.itp") \
                    else (inc if os.path.isabs(inc) else os.path.normpath(os.path.join(srcdir,inc)))
            if not injected: T.append(atline); injected=True
            T.append('#include "%s"\n'%inc_abs)
        elif s.startswith('[') and 'system' in s.lower():
            T.append('#include "%s"\n\n'%os.path.abspath(os.path.join(outdir,"mgslab.itp"))); T.append(ln)
        else: T.append(ln)
    res=[]; inmol=False
    for ln in T:
        res.append(ln)
        if ln.strip().lower().startswith('[ molecules'): inmol=True; continue
        if inmol and ln.strip() and not ln.strip().startswith(';'):
            res.insert(len(res)-1,"MGE      %d\n"%nslab); inmol=False
    open(os.path.join(outdir,"system.top"),"w").write("".join(res))
    print("poly interface built: slab %d Mg (nx,ny=%d,%d), box %.3f x %.3f x %.3f nm"%(nslab,nx,ny,Lx,Ly,box_z))
    print("  NET1 cross-z terms cut: bonds=%d pairs=%d angles=%d dihedrals=%d"%(cut['bonds'],cut['pairs'],cut['angles'],cut['dihedrals']))
    print("  slab_top=%.3f shift=%.3f ; two interfaces ~%.2f and ~%.2f nm"%(slab_top,shift,slab_top+GAP,box_z-GAP))

if __name__=="__main__": main()
