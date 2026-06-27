#!/usr/bin/env python3
# Build the missing TZVPP tail scan points (40, 50) using the same retemplate as build_tzvpp.py
import re
BAS={'Mg':'TZV2P-MOLOPT-PBE-GTH-q10','O':'TZV2P-MOLOPT-PBE-GTH-q6',
     'C':'TZV2P-MOLOPT-PBE-GTH-q4','H':'TZV2P-MOLOPT-PBE-GTH-q1'}
def retemplate(src):
    s=open(src).read()
    s=s.replace("    BASIS_SET_FILE_NAME BASIS_MOLOPT\n",
                "    BASIS_SET_FILE_NAME BASIS_MOLOPT\n    BASIS_SET_FILE_NAME BASIS_MOLOPT_UZH\n",1)
    for el,b in BAS.items():
        s=re.sub(rf"(&KIND {el}\n      BASIS_SET )\S+", rf"\g<1>{b}", s)
    return s
for d in ['40','50']:
    open(f"tz_sTHF_{d}.inp","w").write(retemplate(f"sTHF_{d}.inp"))
    print(f"built tz_sTHF_{d}.inp")
