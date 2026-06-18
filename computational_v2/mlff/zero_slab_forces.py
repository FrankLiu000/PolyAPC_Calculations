import sys
fn, nsl = sys.argv[1], int(sys.argv[2])
buf = open(fn).read().split('\n'); i=0; out=[]; nfr=0; badelem=0
while i < len(buf):
    if not buf[i].strip().isdigit(): break
    n=int(buf[i].split()[0]); out.append(buf[i]); out.append(buf[i+1])
    for k in range(n):
        p=buf[i+2+k].split()
        if k < nsl:
            if p[0]!='Mg': badelem+=1
            p[4]=p[5]=p[6]='0.000000'
        out.append("%-2s %s %s %s %s %s %s" % (p[0],p[1],p[2],p[3],p[4],p[5],p[6]))
    i+=2+n; nfr+=1
open(fn,'w').write('\n'.join(out)+'\n')
print(f"  {fn}: zeroed slab forces (atoms 0..{nsl-1}) in {nfr} frames; non-Mg in slab region: {badelem}")
