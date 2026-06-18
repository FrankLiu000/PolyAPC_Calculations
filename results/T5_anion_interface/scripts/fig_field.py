import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
N=np.genfromtxt("storyT5/analysis/zprofile_neutral.csv",delimiter=",",names=True)
F=np.genfromtxt("storyT5/analysis/zprofile_field.csv",delimiter=",",names=True)
fig,ax=plt.subplots(1,2,figsize=(11,4.3),sharey=True)
for a,(D,title) in zip(ax,[(N,"(a) neutral electrode — symmetric"),(F,"(b) +0.3 V/nm plating bias — double layer")]):
    a.plot(D["z_nm"],D["rho_anionAl"],color="#c0392b",lw=1.8,label="Al-anion")
    a.plot(D["z_nm"],D["rho_catMg"],color="#2471a3",lw=1.8,label="Mg-cation")
    a.axvspan(0,0.54,color="0.7",alpha=.5); a.set_xlabel("z (nm)  — electrode slab shaded")
    a.set_title(title,fontsize=10); a.legend(frameon=False,fontsize=8); a.set_xlim(0,D["z_nm"].max())
ax[0].set_ylabel("number density (nm$^{-3}$)")
ax[1].annotate("cathode:\nanion excluded\n(0.12×)",xy=(8.0,0.05),fontsize=8,color="#c0392b",ha="center")
ax[1].annotate("anode:\nanion piles up\n(0.78×)",xy=(0.95,0.25),fontsize=8,color="#c0392b")
plt.tight_layout(); plt.savefig("storyT5/fig_field.png",dpi=150)
print("wrote storyT5/fig_field.png")
