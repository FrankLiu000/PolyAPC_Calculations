# -*- coding: utf-8 -*-
"""Stream Neware GBK per-point exports, aggregate per cycle for Mg||Mo6S8 cells."""
import csv, json, sys, os

FILES = {
    "bare_0p5C": r"D:/20260602_polyAPC_data/MgMo6S8_0.5C_cycle/MgMo6S8 LE 0.5C_033_6.txt",
    "poly_0p5C": r"D:/20260602_polyAPC_data/MgMo6S8_0.5C_cycle/MgMo6S8 SPE 0.5C_032_5.txt",
    "poly_1C":   r"D:/20260602_polyAPC_data/MgMo6S8_1C_cycle/MgMo6S8_polyAPC.txt",
}
OUT = r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad/mo6s8_out"
os.makedirs(OUT, exist_ok=True)

# column indices (0-based)
C_CUR, C_SPEC, C_CYC, C_STATE, C_QCHG, C_QDIS = 3, 5, 16, 18, 19, 20

def proc(name, path):
    # per cycle: max discharge spec (mAh/g), max charge spec, max Qdis uAh, max Qchg uAh
    cyc = {}  # cyc -> [dis_spec, chg_spec, dis_uAh, chg_uAh]
    n = 0
    with open(path, "r", encoding="gbk", errors="replace", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            n += 1
            if len(row) <= C_QDIS:
                continue
            try:
                c = int(row[C_CYC])
            except ValueError:
                continue
            st = row[C_STATE]
            try:
                spec = float(row[C_SPEC]); qchg = float(row[C_QCHG]); qdis = float(row[C_QDIS])
            except ValueError:
                continue
            d = cyc.get(c)
            if d is None:
                d = [0.0, 0.0, 0.0, 0.0]; cyc[c] = d
            # discharge rows
            if "D" in st and "C" not in st:  # RateD / D
                if spec > d[0]: d[0] = spec
            elif "C" in st:                   # RateC / C
                if spec > d[1]: d[1] = spec
            if qdis > d[2]: d[2] = qdis
            if qchg > d[3]: d[3] = qchg
    # write per-cycle csv
    rows = []
    for c in sorted(cyc):
        ds, cs, du, cu = cyc[c]
        ce = (ds/cs*100.0) if cs > 0 else 0.0   # discharge/charge CE
        rows.append((c, ds, cs, du, cu, ce))
    with open(os.path.join(OUT, f"percycle_{name}.csv"), "w", newline="", encoding="utf-8") as g:
        w = csv.writer(g)
        w.writerow(["cycle","dis_spec_mAhg","chg_spec_mAhg","dis_uAh","chg_uAh","CE_pct"])
        w.writerows(rows)
    # summary: peak discharge spec, retention curve, 80% crossing
    specs = [(c, ds) for (c, ds, cs, du, cu, ce) in rows if ds > 0]
    info = {"name": name, "n_rows": n, "n_cycles": len(rows), "last_cycle": rows[-1][0] if rows else None}
    if specs:
        # peak = max over cycles >=2 (skip cycle 1 formation noise); reference for retention
        cap = dict(specs)
        peak_c, peak_v = max(specs, key=lambda x: x[1])
        info["peak_cycle"] = peak_c
        info["peak_dis_spec_mAhg"] = round(peak_v, 3)
        # also report cycle-2 and cycle-5 capacities
        for ref in (1,2,3,5,10):
            if ref in cap: info[f"dis_spec_cyc{ref}"] = round(cap[ref],3)
        # 80% retention crossing relative to peak (first cycle after peak below 0.8*peak, sustained)
        thr = 0.8*peak_v
        cross = None
        ordered = sorted(specs)
        for (c, v) in ordered:
            if c >= peak_c and v < thr:
                cross = c; break
        info["thr80_mAhg"] = round(thr,3)
        info["cyc_at_80pct_retention"] = cross
        # capacity at a few milestone cycles
        for mc in (100,200,400,500,800,1000,1200,1500,1600,1800,2000,2500,3000):
            if mc in cap:
                info[f"retention_cyc{mc}_pct"] = round(cap[mc]/peak_v*100,1)
        # CE stats (cycles 5..last)
        ces = [ce for (c, ds, cs, du, cu, ce) in rows if c>=5 and cs>0 and ds>0]
        if ces:
            info["CE_median_pct"] = round(sorted(ces)[len(ces)//2],2)
    return info

summ = {}
for name, path in FILES.items():
    if not os.path.exists(path):
        summ[name] = {"error":"missing"}; continue
    print(f"processing {name} ...", flush=True)
    summ[name] = proc(name, path)
    print(json.dumps(summ[name], ensure_ascii=False, indent=2), flush=True)

with open(os.path.join(OUT,"summary.json"),"w",encoding="utf-8") as g:
    json.dump(summ, g, ensure_ascii=False, indent=2)
print("DONE")
