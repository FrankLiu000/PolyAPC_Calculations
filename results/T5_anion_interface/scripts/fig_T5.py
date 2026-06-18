#!/usr/bin/env python3
"""T5 figure: (a) Al-anion vs Mg-cation density profile at the bare Mg(0001)
electrode; (b) bulk anion vs cation network-association in the poly gel;
(c) the transport-null + de-pairing (canonical 4-POSS gel vs bare).
usage: fig_T5.py <storyT5_dir> <out.png>"""
import sys, json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

d=sys.argv[1]; out=sys.argv[2]
fig,ax=plt.subplots(1,3,figsize=(15,4.4))

# (a) bare interface profile
try:
    P=np.genfromtxt(f"{d}/analysis/profile_bare.csv",delimiter=",",names=True)
    ax[0].plot(P["d_nm"],P["enrich_anion"],color="#c0392b",lw=2,label="Al-anion")
    ax[0].plot(P["d_nm"],P["enrich_cation"],color="#2471a3",lw=2,label="Mg-cation")
    ax[0].axhline(1,ls=":",c="grey"); ax[0].set_xlim(0,2.2)
    ax[0].set_xlabel("distance from Mg(0001) electrode  d (nm)")
    ax[0].set_ylabel(r"density / bulk  $\rho(d)/\rho_{bulk}$")
    ax[0].set_title("(a) bare interface: ion approach to the anode")
    ax[0].legend(frameon=False)
except Exception as e:
    ax[0].text(0.5,0.5,f"profile pending\n{e}",ha="center",transform=ax[0].transAxes)

# (b) bulk network association (poly)
try:
    B=json.load(open(f"{d}/bulk/bulk_poly.json"))
    cats=["in contact\n(<0.5 nm)","within\n0.7 nm"]
    an=[B["anion_frac_contact_network"],B["anion_frac_within_0p7"]]
    ca=[B["cation_frac_contact_network"],B.get("cation_frac_within_0p7",np.nan)]
    x=np.arange(2); w=0.36
    ax[1].bar(x-w/2,an,w,color="#c0392b",label="Al-anion")
    ax[1].bar(x+w/2,ca,w,color="#2471a3",label="Mg-cation")
    ax[1].set_xticks(x); ax[1].set_xticklabels(cats)
    ax[1].set_ylabel("fraction of ions associated w/ network")
    ax[1].set_title("(b) bulk gel: network sequesters the anion")
    ax[1].legend(frameon=False)
    ax[1].text(0.02,0.96,f"median anion–network {B['anion_median_dist_to_network_nm']:.2f} nm\n"
               f"vs cation {B['cation_median_dist_to_network_nm']:.2f} nm",
               transform=ax[1].transAxes,va="top",fontsize=8)
except Exception as e:
    ax[1].text(0.5,0.5,f"bulk pending\n{e}",ha="center",transform=ax[1].transAxes)

# (c) transport-null + de-pairing (canonical 4-POSS gel vs bare) -- FINAL numbers
labels=["D cation","D anion","free-carrier f"]
bare=[0.0508,0.0499,0.046]; poly=[0.0114,0.0118,0.13]
# normalise each metric to bare for a clean bar (show ratio); annotate raw
ratio_bare=[1,1,1]; ratio_poly=[poly[i]/bare[i] for i in range(3)]
x=np.arange(3); w=0.36
ax[2].bar(x-w/2,ratio_bare,w,color="#2471a3",label="bare")
ax[2].bar(x+w/2,ratio_poly,w,color="#c0392b",label="poly (4-POSS gel)")
ax[2].axhline(1,ls=":",c="grey")
ax[2].set_xticks(x); ax[2].set_xticklabels(labels)
ax[2].set_ylabel("value relative to bare")
ax[2].set_title("(c) transport NULL + de-pairing")
for i,(rp,b,p) in enumerate(zip(ratio_poly,bare,poly)):
    ax[2].text(i+w/2,rp+0.05,f"×{rp:.2f}",ha="center",fontsize=8)
ax[2].text(0.02,0.96,"D ×4.4 slower (kills rate hyp.);\nt₊=0.50 both; f de-pairs ×2.8",
           transform=ax[2].transAxes,va="top",fontsize=8)
ax[2].legend(frameon=False)

plt.tight_layout(); plt.savefig(out,dpi=150)
print("wrote",out)
