#!/usr/bin/env python3
# T8 (corrected): k-point SCF for a PHYSICAL band gap / metallicity.
# Gamma-only on small cells gives spurious gaps for metals; Monkhorst-Pack fixes it.
# Transform each *_dos.inp -> *_kp.inp: drop &PDOS print, add &KPOINTS, print MO eigenvalues.
import re, os
BASE="/CH/poly_v2/v3/sei"
KGRID = {  # per-phase MP grid (denser along short axes)
 "Al_fcc":"6 6 6","Mg_hcp":"8 8 6","MgO":"5 5 5","MgCl2":"6 6 4",
 "Al2O3":"3 3 3","Mg17Al12":"3 3 3","SiO2":"4 4 4",
}
for proj,grid in KGRID.items():
    src=os.path.join(BASE,proj+"_dos.inp")
    if not os.path.exists(src):
        print("missing",src); continue
    t=open(src).read()
    t=t.replace(proj+"_dos","%s_kp"%proj)
    # remove the &PRINT ... &PDOS ... &END PRINT block (PDOS not valid with k-points)
    t=re.sub(r'\n\s*&PRINT\s*\n\s*&PDOS.*?&END PRINT','',t,flags=re.S)
    # insert &KPOINTS + MO-eigenvalue print right after the &QS ... &END QS block
    kp=("""    &KPOINTS
      SCHEME MONKHORST-PACK %s
      SYMMETRY OFF
      FULL_GRID OFF
      PARALLEL_GROUP_SIZE -1
    &END KPOINTS
    &PRINT
      &MO
        EIGENVALUES .TRUE.
        OCCUPATION_NUMBERS .TRUE.
        &EACH
          QS_SCF 0
        &END EACH
      &END MO
    &END PRINT"""%grid)
    t=re.sub(r'(\n\s*&END QS\n)', r'\1'+kp+'\n', t, count=1)
    open(os.path.join(BASE,proj+"_kp.inp"),"w").write(t)
    print("wrote",proj+"_kp.inp","grid",grid)
