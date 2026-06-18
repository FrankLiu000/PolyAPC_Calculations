#!/usr/bin/env python3
"""fig_matched.py — matched bare-vs-poly MLFF comparison figure.
  A: held-out force accuracy (MAE/RMSE/R) bare vs poly  (eval_bare.json, eval_poly.json)
  B: MLFF-MD Al-slab distance bare vs poly              (md_cmp_{bare,poly}_cv.csv)
  C: MLFF-MD anion Al-Cl bonds bare vs poly             (intactness)
Writes ../results/figures/fig_mlff_matched.png
"""
import json, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

b = json.load(open("eval_bare.json")); p = json.load(open("eval_poly.json"))
def cv(f):
    r = list(csv.DictReader(open(f)))
    return {k: np.array([float(x[k]) for x in r]) for k in
            ("t_ps", "T_K", "Al_slab_min_A", "Al_Cl1_A", "Al_Cl2_A")}
cb, cp = cv("md_cmp_bare_cv.csv"), cv("md_cmp_poly_cv.csv")

fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
# A: accuracy bars
metrics = ["force_mae_meV_per_A", "force_rmse_meV_per_A"]
labels = ["force MAE", "force RMSE"]
x = np.arange(len(labels)); w = 0.35
ax[0].bar(x - w/2, [b[m] for m in metrics], w, label=f"bare (R={b['force_R']:.3f})", color="#1f77b4")
ax[0].bar(x + w/2, [p[m] for m in metrics], w, label=f"poly (R={p['force_R']:.3f})", color="#ff7f0e")
ax[0].axhline(100, ls=":", color="g", lw=1)
ax[0].set_xticks(x); ax[0].set_xticklabels(labels); ax[0].set_ylabel("meV/Å")
ax[0].set_title("A. Held-out force accuracy (matched)"); ax[0].legend(fontsize=9)
# B: Al-slab distance
ax[1].plot(cb["t_ps"], cb["Al_slab_min_A"], color="#1f77b4", label="bare", lw=1)
ax[1].plot(cp["t_ps"], cp["Al_slab_min_A"], color="#ff7f0e", label="poly", lw=1)
ax[1].set_xlabel("t (ps)"); ax[1].set_ylabel("min Al–slab Mg (Å)")
ax[1].set_title(f"B. Anion–electrode distance\nbare ⟨{cb['Al_slab_min_A'].mean():.1f}⟩  poly ⟨{cp['Al_slab_min_A'].mean():.1f}⟩ Å")
ax[1].legend(fontsize=9)
# C: anion Al-Cl bonds (min of the two per frame)
bmin = np.minimum(cb["Al_Cl1_A"], cb["Al_Cl2_A"]); bmax = np.maximum(cb["Al_Cl1_A"], cb["Al_Cl2_A"])
pmin = np.minimum(cp["Al_Cl1_A"], cp["Al_Cl2_A"]); pmax = np.maximum(cp["Al_Cl1_A"], cp["Al_Cl2_A"])
ax[2].fill_between(cb["t_ps"], bmin, bmax, color="#1f77b4", alpha=0.4, label="bare Al–Cl range")
ax[2].fill_between(cp["t_ps"], pmin, pmax, color="#ff7f0e", alpha=0.4, label="poly Al–Cl range")
ax[2].axhline(3.0, ls=":", color="gray", lw=0.8, label="dissociation")
ax[2].set_xlabel("t (ps)"); ax[2].set_ylabel("Al–Cl (Å)")
ax[2].set_title("C. Anion integrity (both intact)"); ax[2].legend(fontsize=8)
plt.tight_layout()
plt.savefig("../results/figures/fig_mlff_matched.png", dpi=130)
print("wrote ../results/figures/fig_mlff_matched.png")
