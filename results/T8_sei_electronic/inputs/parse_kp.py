#!/usr/bin/env python3
# T8: min band gap over MP mesh, post-SCF-convergence. Metal => ~0 (leaky); insulator => wide gap (passivating).
import glob, os, csv
rows=[]
for f in sorted(glob.glob("/CH/poly_v2/v3/sei/*_kp.out")+glob.glob("/CH/poly_v2/v3/sei/*_g.out")):
    proj=os.path.basename(f).replace("_kp.out","").replace("_g.out","")
    txt=open(f).read().splitlines()
    conv=any("SCF run converged" in l for l in txt)
    # collect band gaps AFTER convergence line
    gaps=[]; fermi=None; seen=False
    for l in txt:
        if "SCF run converged" in l: seen=True
        if seen and "MO| Band gap:" in l:
            try: gaps.append(float(l.split()[-2]))
            except: pass
        if "MO| E(Fermi):" in l:
            try: fermi=float(l.split()[-2])
            except: pass
    if not gaps: continue
    g=min(gaps)
    verdict="METAL (electron-leaky)" if g<0.15 else "insulator (passivating)"
    rows.append((proj,round(g,2),round(fermi,2) if fermi else None,"yes" if conv else "NO",verdict))
print("%-12s %8s %8s %6s  %s"%("phase","gap_eV","Ef_eV","conv","verdict"))
for r in rows: print("%-12s %8.2f %8s %6s  %s"%(r[0],r[1],str(r[2]),r[3],r[4]))
with open("/CH/poly_v2/v3/sei/t8_gaps.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["phase","band_gap_eV","E_fermi_eV","scf_converged","verdict"]); w.writerows(rows)
print("\nwrote t8_gaps.csv")
