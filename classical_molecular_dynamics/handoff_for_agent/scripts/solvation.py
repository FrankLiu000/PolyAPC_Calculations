#!/usr/bin/env python3
"""Mg first-shell solvation statistics from a multi-frame .gro (whole system).

Reads index groups (Mg, Clbridge, CoordO_THF, PolymerO, AnionCl) and counts, for
every Mg in every frame, the number of each species within element-specific
cutoffs (minimum-image PBC). Reports coordination-number distributions, the mean
CN per species, and the dominant solvation motif; writes per-instance shell
labels so representative clusters can be extracted.

usage: solvation.py <multiframe.gro> <index.ndx> <outprefix> [haspoly:0/1]
cutoffs (nm): Mg-Cl 0.315, Mg-O 0.300, Mg-anionCl 0.345
"""
import sys, math
from collections import Counter

R_CL=0.315; R_O=0.300; R_ANCL=0.345

def read_ndx(path):
    g={}; cur=None
    for line in open(path):
        s=line.strip()
        if s.startswith('['): cur=s.strip('[] ').strip(); g[cur]=[]
        elif s and cur: g[cur]+=[int(x) for x in s.split()]
    return {k:set(v) for k,v in g.items()}

def frames(gro):
    f=open(gro)
    while True:
        title=f.readline()
        if not title: break
        n=int(f.readline())
        xs=[None]*(n+1)   # 1-based
        for i in range(1,n+1):
            l=f.readline()
            xs[i]=(float(l[20:28]),float(l[28:36]),float(l[36:44]))
        box=[float(x) for x in f.readline().split()[:3]]
        yield xs, box

def mind(a,b,box):
    d2=0.0
    for k in range(3):
        d=a[k]-b[k]; d-=box[k]*round(d/box[k]); d2+=d*d
    return math.sqrt(d2)

def main():
    gro,ndx,out=sys.argv[1],sys.argv[2],sys.argv[3]
    haspoly=len(sys.argv)>4 and sys.argv[4]=="1"
    g=read_ndx(ndx)
    Mg=sorted(g["Mg"]); Clb=sorted(g["Clbridge"])
    Othf=sorted(g["CoordO_THF"]); AnCl=sorted(g.get("AnionCl",set()))
    Opoly=sorted(g.get("PolymerO",set())) if haspoly else []
    recs=[]; nfr=0
    for xs,box in frames(gro):
        nfr+=1
        for m in Mg:
            pm=xs[m]
            ncl=sum(1 for j in Clb if mind(pm,xs[j],box)<R_CL)
            no =sum(1 for j in Othf if mind(pm,xs[j],box)<R_O)
            npo=sum(1 for j in Opoly if mind(pm,xs[j],box)<R_O)
            nac=sum(1 for j in AnCl if mind(pm,xs[j],box)<R_ANCL)
            recs.append((nfr,m,ncl,no,npo,nac))
    # statistics
    import statistics as st
    def col(i): return [r[i] for r in recs]
    ncl,no,npo,nac=col(2),col(3),col(4),col(5)
    tot=[a+b+c for a,b,c in zip(ncl,no,npo)]   # Mg coordination (Cl+O ligands)
    with open(out+"_summary.txt","w") as o:
        o.write("Mg solvation statistics  (%d frames x %d Mg = %d samples)\n"%(nfr,len(Mg),len(recs)))
        o.write("cutoffs nm: Mg-Cl %.3f  Mg-O %.3f  Mg-anionCl %.3f\n\n"%(R_CL,R_O,R_ANCL))
        def line(name,v):
            o.write("  %-16s mean %5.2f  sd %4.2f   dist %s\n"%(
                name, st.mean(v), (st.pstdev(v) if len(v)>1 else 0),
                dict(sorted(Counter(v).items()))))
        line("Cl (bridge)",ncl); line("O (THF)",no)
        if haspoly: line("O (polymer)",npo)
        line("Cl (anion)",nac); line("total(Cl+O)",tot)
        motif=Counter((a,b,c) for a,b,c in zip(ncl,no,npo))
        o.write("\n  dominant motifs (Cl,Othf,Opoly) -> count [fraction]:\n")
        for k,v in motif.most_common(6):
            o.write("    %s : %d  [%.1f%%]\n"%(k,v,100*v/len(recs)))
        # anion association fraction (contact ion pairing)
        o.write("\n  Mg with >=1 anion-Cl contact: %.1f%%\n"%(100*sum(1 for x in nac if x>0)/len(recs)))
        if haspoly:
            o.write("  Mg with >=1 polymer-O contact: %.1f%%\n"%(100*sum(1 for x in npo if x>0)/len(recs)))
    # write per-instance records for representative extraction (frame, Mgatom, motif)
    with open(out+"_records.csv","w") as o:
        o.write("frame,mg_atom,n_Cl,n_Othf,n_Opoly,n_anionCl\n")
        for r in recs: o.write("%d,%d,%d,%d,%d,%d\n"%r)
    print(open(out+"_summary.txt").read())

if __name__=="__main__": main()
