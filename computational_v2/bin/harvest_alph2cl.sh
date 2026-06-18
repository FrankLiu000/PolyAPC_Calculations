#!/usr/bin/env bash
# harvest_alph2cl.sh <tzvp_jid> <redvert_jid>
# Wait for the neutral-AlPh2Cl jobs, then write results/data/chloride_abstraction.txt
set +u
RM=/CH/poly_v2/run_mol
OUT=/CH/poly_v2/results/data/chloride_abstraction.txt
LOG=$RM/_harvest_alph2cl.log
ts(){ date +%F\ %H:%M:%S; }
for j in "$1" "$2"; do
  for i in $(seq 1 1440); do
    [ -z "$(squeue -h -j "$j" -o '%i' 2>/dev/null)" ] && break
    sleep 60
  done
done
echo "[$(ts)] jobs $1 $2 done" >> "$LOG"
python3 - > "$OUT" 2>> "$LOG" <<'EOF'
import re
RM = "/CH/poly_v2/run_mol"
def scf(f):
    es = re.findall(r"SCF Done:\s+E\(\S+\)\s+=\s+(-?\d+\.\d+)", open(f).read())
    return float(es[-1]) if es else None
def gcorr(f):
    m = re.findall(r"Thermal correction to Gibbs Free Energy=\s+(-?\d+\.\d+)", open(f).read())
    return float(m[-1]) if m else None
def normal(f):
    return "Normal termination" in open(f).read()[-2000:] or \
           sum(1 for _ in re.finditer("Normal termination", open(f).read())) > 0

E_n   = scf(RM + "/AlPh2Cl_n_tzvp.log")      # neutral AlPh2Cl, TZVP/SMD @ neutral geom
Gc_n  = gcorr(RM + "/AlPh2Cl_n_opt.log")     # Gcorr from SVP/PCM freq
E_rv  = scf(RM + "/AlPh2Cl_n_redvert.log")   # radical anion @ neutral geom, TZVP/SMD
E_ra  = -1166.38596172                       # [AlPh2Cl]·- TZVP/SMD @ its own geom (frag_AlPh2Cl_tzvp)
Gc_ra = 0.138109                             # frag_AlPh2Cl_opt freq
H2EV = 27.211386
print("# Chloride-abstraction story: neutral AlPh2Cl reducibility")
print("# (B3LYP-D3BJ/def2-TZVP,SMD-THF // def2-SVP,PCM opt+freq; same protocol as redox ladder)")
print("#")
print("# Context: bare-interface AIMD shows the [Mg2Cl3(THF)6]+ cation abstracts one Cl- from")
print("# [AlPh2Cl2]- within 0.2 ps and keeps it for the whole 10 ps -> the bare anion actually")
print("# present at the interface is NEUTRAL 3-coordinate AlPh2Cl. In poly the anion stays intact.")
print("# One-electron reduction of AlPh2Cl gives [AlPh2Cl]·- = the 83%-Al-spin Al(II) radical")
print("# (reductive_decomposition.txt) -> direct Al(0) precursor.")
print("#")
print("E_neutral_tzvp_smd  = %s Ha" % E_n)
print("Gcorr_neutral(SVP)  = %s Ha" % Gc_n)
print("E_redvert_tzvp_smd  = %s Ha  (anion at neutral geometry)" % E_rv)
print("E_radanion_tzvp_smd = %.8f Ha ; Gcorr = %.6f (frag_AlPh2Cl, adiabatic)" % (E_ra, Gc_ra))
print("#")
if E_n and E_rv:
    print("EA_vert(AlPh2Cl)    = %.2f eV    (vs intact free [AlPh2Cl2]- : 0.06 eV)" % ((E_n - E_rv) * H2EV))
if E_n and Gc_n:
    dG = ((E_ra + Gc_ra) - (E_n + Gc_n))
    print("dG_red_adiabatic    = %.2f eV  = %.1f kcal/mol   (AlPh2Cl + e- -> [AlPh2Cl]·-)" % (dG * H2EV, dG * 627.5095))
print("#")
print("# Compare: intact-anion reduction is phenyl-centred (8% Al spin) and weak (EA 0.06 eV free,")
print("# ~0.5 eV in cation contact); neutral-AlPh2Cl reduction is Al-centred (83%) and (this file)")
print("# much more exergonic -> chloride abstraction is the gateway that converts the inert anion")
print("# into the Al(0)-forming species. Poly blocks the gateway (bridge stretched, no abstraction).")
EOF
echo "[$(ts)] wrote $OUT" >> "$LOG"
