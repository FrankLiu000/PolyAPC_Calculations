#!/usr/bin/env bash
# harvest_storyG.sh <tzvp_jid1> <tzvp_jid2> — monomer<->dimer speciation deltaG
set +u
RM=/CH/poly_v2/run_mol
OUT=/CH/poly_v2/results/data/speciation_monomer_dimer.txt
for jid in "$@"; do
  for i in $(seq 1 720); do [ -z "$(squeue -h -j "$jid" -o '%i' 2>/dev/null)" ] && break; sleep 60; done
done
sleep 20
cd "$RM" || exit 9
python3 - > "$OUT" 2>&1 <<'PY'
import re,math
RM="/CH/poly_v2/run_mol/"
def Etz(f):
    e=None
    for l in open(RM+f,errors='ignore'):
        if "SCF Done:" in l:
            m=re.search(r"=\s*(-?\d+\.\d+)",l)
            if m: e=float(m.group(1))
    return e
def Gcorr(f):
    g=None
    for l in open(RM+f,errors='ignore'):
        if "Thermal correction to Gibbs Free Energy" in l:
            g=float(l.split("=")[-1])
    return g
sp={
 "dimer+   [Mg2Cl3(THF)6]+":("Mg2Cl3_THF6_cation_tzvp.log","Mg2Cl3_THF6_cation_opt.log"),
 "cat_mono [MgCl(THF)5]+   ":("MgCl_THF5_cation_tzvp.log","MgCl_THF5_cation_lo.log"),
 "neu_mono [MgCl2(THF)4]   ":("MgCl2_THF4_neutral_tzvp.log","MgCl2_THF4_neutral.log"),
 "THF                      ":("THF_tzvp.log","THF_opt.log"),
}
G={}
print("# Monomer<->dimer speciation (Story G; B3LYP-D3BJ/def2-TZVP//def2-SVP, SMD-THF)")
print("# G = E[TZVP,SMD] + Gcorr[SVP freq];  reaction: [Mg2Cl3(THF)6]+ + 3 THF <-> [MgCl(THF)5]+ + [MgCl2(THF)4]")
print("# (Canepa/Persson: MgCl+ monomer favoured | Moss/FF: dimer.  dG<0 => monomers; dG>0 => dimer)\n")
print("%-26s %16s %14s %16s"%("species","E_tzvp(Ha)","Gcorr(Ha)","G(Ha)"))
ok=True
for k,(t,o) in sp.items():
    e=Etz(t); g=Gcorr(o)
    if e is None or g is None: print("%-26s  MISSING (%s / %s)"%(k,e,g)); ok=False; continue
    G[k.split()[0]]=e+g
    print("%-26s %16.6f %14.6f %16.6f"%(k,e,g,e+g))
if ok:
    dG=(G["cat_mono"]+G["neu_mono"]-G["dimer+"]-3*G["THF"])*627.509
    print("\ndG(redistribution) = %.1f kcal/mol"%dG)
    print("VERDICT: %s favoured (%s)"%(("MONOMERS","Canepa/Persson") if dG<0 else ("DIMER","Moss/FF assumption")))
    RT=0.0019872*298.15
    print("# note: bimolecular; sign/direction is the robust statement (standard-state/conc terms shift magnitude).")
    print("# Next: repeat in a polyether-O-rich micro-environment to test whether the network shifts the balance (Story G poly arm).")
PY
echo "[harvest_storyG] wrote $OUT"
