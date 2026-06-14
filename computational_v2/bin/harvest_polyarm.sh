#!/usr/bin/env bash
# harvest_polyarm.sh <tzvp_jid...> — Story G poly arm: does glyme (DME) shift monomer<->dimer?
set +u
RM=/CH/poly_v2/run_mol
OUT=/CH/poly_v2/results/data/speciation_polyarm_glyme.txt
for jid in "$@"; do for i in $(seq 1 720); do [ -z "$(squeue -h -j "$jid" -o '%i' 2>/dev/null)" ] && break; sleep 60; done; done
sleep 20
cd "$RM" || exit 9
python3 - > "$OUT" 2>&1 <<'PY'
import re
RM="/CH/poly_v2/run_mol/"
def Etz(f):
    e=None
    for l in open(RM+f,errors='ignore'):
        if "SCF Done:" in l:
            m=re.search(r"=\s*(-?\d+\.\d+)",l); e=float(m.group(1)) if m else e
    return e
def Gc(f):
    g=None
    for l in open(RM+f,errors='ignore'):
        if "Thermal correction to Gibbs Free Energy" in l: g=float(l.split("=")[-1])
    return g
# bare references (from Story G, B3LYP-D3BJ/def2-TZVP//SVP SMD-THF)
G_mono=-1822.759528; G_dimer=-3176.055250; G_THF=-232.476358
H=627.509
new={"DME":("DME_tzvp.log","DME.log"),
     "glyme_mono [MgCl(DME)(THF)3]+":("MgCl_DME_THF3_cation_tzvp.log","MgCl_DME_THF3_cation.log"),
     "glyme_dimer [Mg2Cl3(DME)(THF)4]+":("Mg2Cl3_DME_THF4_cation_r2_tzvp.log","Mg2Cl3_DME_THF4_cation_r2.log")}
G={}
print("# Story G POLY ARM — does a polyether-O (glyme=DME) shift the monomer<->dimer balance?")
print("# B3LYP-D3BJ/def2-TZVP//def2-SVP(opt=loose), SMD-THF.  Bare redistribution dG = +10.4 kcal/mol (dimer).")
print("# Differential glyme effect:  ddG = [G(glyme_mono)-G(mono)] - [G(glyme_dimer)-G(dimer)]  (THF,DME cancel)")
print("#   ddG<0 => glyme prefers the MONOMER => network shifts speciation toward monomer.\n")
print("%-34s %16s %14s %16s"%("species","E_tzvp(Ha)","Gcorr(Ha)","G(Ha)"))
print("%-34s %16s %14s %16.6f"%("mono  [MgCl(THF)5]+ (bare)","","",G_mono))
print("%-34s %16s %14s %16.6f"%("dimer [Mg2Cl3(THF)6]+ (bare)","","",G_dimer))
ok=True
for k,(t,o) in new.items():
    e=Etz(t); g=Gc(o)
    if e is None or g is None: print("%-34s MISSING (%s/%s)"%(k,e,g)); ok=False; continue
    G[k.split()[0]]=e+g; print("%-34s %16.6f %14.6f %16.6f"%(k,e,g,e+g))
if ok:
    ddG=((G["glyme_mono"]-G_mono)-(G["glyme_dimer"]-G_dimer))*H
    bind_m=(G["glyme_mono"]+2*G_THF-G_mono-G["DME"])*H
    bind_d=(G["glyme_dimer"]+2*G_THF-G_dimer-G["DME"])*H
    redist_poly=10.4+ddG
    print("\n# glyme binding (X + DME -> X.DME + 2THF):  monomer %.1f | dimer %.1f kcal/mol"%(bind_m,bind_d))
    print("ddG (differential, mono vs dimer) = %.1f kcal/mol"%ddG)
    print("=> effective redistribution dG in poly = 10.4 + (%.1f) = %.1f kcal/mol"%(ddG,redist_poly))
    if redist_poly<0:
        print("VERDICT: network FLIPS speciation -> MONOMER favoured in poly (genuine carrier-identity differentiator!)")
    elif ddG<-2:
        print("VERDICT: network shifts TOWARD monomer by %.1f kcal/mol but dimer still favoured (partial lever)"%(-ddG))
    else:
        print("VERDICT: network does NOT shift the balance -> dimer favoured in BOTH -> carrier identity is NOT the differentiator")
PY
echo "[harvest_polyarm] wrote $OUT"
