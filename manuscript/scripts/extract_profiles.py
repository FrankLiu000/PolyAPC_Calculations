# -*- coding: utf-8 -*-
"""Extract charge/discharge voltage profiles (V vs specific capacity) at selected cycles
from raw Neware GBK export, for Li-Fig5b-style plotting."""
import csv, json, os
SRC={"poly_1C":r"D:/20260602_polyAPC_data/MgMo6S8_1C_cycle/MgMo6S8_polyAPC.txt",
     "poly_0p5C":r"D:/20260602_polyAPC_data/MgMo6S8_0.5C_cycle/MgMo6S8 SPE 0.5C_032_5.txt"}
TARGET={"poly_1C":[5,100,500,1000,1500],"poly_0p5C":[5,100,300,600,840]}
OUT=r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad/mo6s8_out"
C_SPEC,C_V,C_CYC,C_STATE=5,7,16,18
for name,path in SRC.items():
    want=set(TARGET[name]); got={c:[] for c in want}
    with open(path,encoding="gbk",errors="replace",newline="") as f:
        r=csv.reader(f); next(r)
        for row in r:
            if len(row)<=C_STATE: continue
            try: c=int(row[C_CYC])
            except: continue
            if c not in want: continue
            st=row[C_STATE]
            if "Rate" not in st and st not in ("C","D","CCD","CC_DChg","CC_Chg"):
                pass
            try: spec=float(row[C_SPEC]); V=float(row[C_V])
            except: continue
            got[c].append((st,spec,V))
    # save
    with open(os.path.join(OUT,f"profiles_{name}.csv"),"w",newline="",encoding="utf-8") as g:
        w=csv.writer(g); w.writerow(["cycle","state","spec_mAhg","V"])
        for c in sorted(got):
            for st,spec,V in got[c]: w.writerow([c,st,spec,V])
    print(name, {c:len(got[c]) for c in sorted(got)})
print("done")
