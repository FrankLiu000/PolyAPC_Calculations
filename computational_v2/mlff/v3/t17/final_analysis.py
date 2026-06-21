#!/usr/bin/env python3
"""Final matched bare-vs-poly anion-standoff analysis (r6 @ 0.5fs+cap, 500ps each, segmented).
Pools s1+seg2 (drop 50ps equilibration/seg), Al_slabMin PRIMARY. Figure + printed summary."""
import numpy as np, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

def pool(files, col, teq=50.0):
    out=[]
    for f in files:
        d=np.genfromtxt(f, delimiter=",", skip_header=1)
        d=d[np.isfinite(d[:,3])]                      # drop any nan-energy rows
        out.append(d[d[:,1]>teq, col])
    return np.concatenate(out)

SM=5  # Al_slabMin col index (0-based: step0 t1 T2 Epot3 height4 slabMin5 nCl6 nO7 SiMin8)
HT=4; NCL=6; NO=7; SI=8
bare_f=["bare_final_s1_cv.csv","bare_final_cv.csv"]
poly_f=["poly_r6_s1_cv.csv","poly_r6_cv.csv"]

bsm=pool(bare_f,SM); psm=pool(poly_f,SM)
bht=pool(bare_f,HT); pht=pool(poly_f,HT)
bcl=pool(bare_f,NCL); pcl=pool(poly_f,NCL)
psi=pool(poly_f,SI)
# r5 cross-check
try: nssm=pool(["poly_ns_cv.csv"],SM); ns_ok=True
except Exception: ns_ok=False

ratio=psm.mean()/bsm.mean()
print("=============== MATCHED STANDOFF (r6@0.5fs+cap, 500ps each) ===============")
print(f"BARE  Al_slabMin = {bsm.mean():.2f} +/- {bsm.std():.2f} A  (n={bsm.size}, min={bsm.min():.2f})  | Al_height {bht.mean():.2f} | nCl {bcl.mean():.2f}")
print(f"POLY  Al_slabMin = {psm.mean():.2f} +/- {psm.std():.2f} A  (n={psm.size}, min={psm.min():.2f})  | Al_height {pht.mean():.2f} | nCl {pcl.mean():.2f} | Al-SiMin {psi.mean():.2f}")
print(f"STANDOFF ratio (poly/bare) = {ratio:.2f}x   |  gap = {psm.mean()-bsm.mean():.2f} A")
if ns_ok: print(f"x-check poly_ns (r5, 486ps): slabMin {nssm.mean():.2f} +/- {nssm.std():.2f} A (n={nssm.size})")
print(f"poly slabMin 10-90 percentile: {np.percentile(psm,10):.1f}-{np.percentile(psm,90):.1f} A (slow-mode spread)")

# ---- figure ----
os.makedirs("../../../results/T5_anion_interface", exist_ok=True)
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(11,4.2))
# panel 1: slabMin vs pooled sample index (concatenated production, both systems)
ax1.plot(np.arange(bsm.size)/bsm.size*500, bsm, color="#c0392b", lw=0.5, alpha=0.7, label=f"bare {bsm.mean():.1f}A")
ax1.plot(np.arange(psm.size)/psm.size*500, psm, color="#2471a3", lw=0.5, alpha=0.7, label=f"poly {psm.mean():.1f}A")
ax1.axhline(bsm.mean(),color="#c0392b",ls="--",lw=1); ax1.axhline(psm.mean(),color="#2471a3",ls="--",lw=1)
ax1.axhspan(0,3.2,color="grey",alpha=0.15); ax1.text(10,1.6,"reductive front\n(<~3.2 A)",fontsize=8,color="#555")
ax1.set_xlabel("production sample (scaled to 500 ps)"); ax1.set_ylabel("Al-electrode min distance (A)")
ax1.set_title(f"Matched interface MD (r6, 0.5fs+cap)\nstandoff {ratio:.2f}x"); ax1.legend(fontsize=9); ax1.set_ylim(2,11)
# panel 2: distributions
bins=np.linspace(2,11,46)
ax2.hist(bsm,bins=bins,color="#c0392b",alpha=0.6,density=True,label="bare")
ax2.hist(psm,bins=bins,color="#2471a3",alpha=0.6,density=True,label="poly")
ax2.axvline(3.2,color="grey",ls=":",lw=1.5); ax2.text(3.25,ax2.get_ylim()[1]*0.85,"reductive front",fontsize=8,rotation=90,color="#555")
ax2.set_xlabel("Al-electrode min distance (A)"); ax2.set_ylabel("density")
ax2.set_title("Anion standoff distribution\n(network excludes anion from the front)"); ax2.legend(fontsize=9)
plt.tight_layout(); plt.savefig("../../../results/T5_anion_interface/fig_matched_standoff.png",dpi=140)
print("saved fig_matched_standoff.png")
