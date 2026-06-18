import numpy as np, tempfile, os
from ase.io import read
from ase.visualize.plot import plot_atoms
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

def load_noH(p):
    # rewrite gro as POSITION-ONLY (drop velocity cols) so mixed-velocity files read cleanly
    L=open(p).read().splitlines(); n=int(L[1])
    out=[L[0],L[1]]+[ln[:44] for ln in L[2:2+n]]+[L[2+n]]
    tf=tempfile.NamedTemporaryFile("w",suffix=".gro",delete=False); tf.write("\n".join(out)+"\n"); tf.close()
    at=read(tf.name); os.unlink(tf.name)
    at=at[[a.symbol!="H" for a in at]]                  # drop H
    at.positions[:,2]=np.mod(at.positions[:,2], at.cell[2,2])
    return at

fig, axes = plt.subplots(1, 2, figsize=(11, 8))
for ax,(p,title) in zip(axes, [("storyT5/bare/nptz.gro","bare-APC  |  Mg(0001)   (equilibrated)"),
                               ("storyT5/poly/interface.gro","poly-APC gel  |  Mg(0001)   (built; POSS network)")]):
    try:
        at=load_noH(p)
        plot_atoms(at, ax, rotation="-90x,0y,0z", radii=0.45)
        ax.set_title(f"{title}\n{len(at)} heavy atoms", fontsize=10)
        ax.set_xlabel("x (Å)"); ax.set_ylabel("z (Å) — electrode at top & bottom (PBC)")
    except Exception as e:
        ax.text(0.5,0.5,f"{title}\nERR: {e}",ha="center",transform=ax.transAxes,wrap=True)
plt.tight_layout(); plt.savefig("storyT5/box_snapshot.png", dpi=140, bbox_inches="tight")
print("wrote storyT5/box_snapshot.png")
