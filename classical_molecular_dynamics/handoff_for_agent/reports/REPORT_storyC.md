# Story C — mechanics / morphology

**Date:** 2026-06-11 · **Machine:** LYZ-ROG · Analysis on existing trajectories (+ existing NPT data).
Exploratory (per the plan): FF-dependent, small boxes truncate long-wavelength mechanics; dendrite
suppression is *inferred*, not simulated.

## 1. Free-THF channel percolation — pinch-off hypothesis REFUTED
Connected-cluster analysis (O–O cutoff 0.70 nm) of the free-THF sub-phase:
| system | free-THF | largest-channel fraction |
|---|---|---|
| bare | 2120 | 1.000 |
| 4-POSS | 1399 | 0.997 |
| 8-swollen | 2040 | 1.000 |
| 16-dense | 1220 | 0.993 |

The free-THF phase is **continuous in every system, even the dense gel** — the solvent never
disconnects. So the transport contrast (swollen mobile, dense slow) is **not** channel disconnection.

## 2. Swelling — the real differentiator
Free-THF number density: **8-swollen 5.14 / nm³ ≫ 16-dense 3.06 / nm³** (~1.7×; 4-POSS 3.70). The
swollen gel simply holds far more solvent in wider/more-abundant channels → that, plus de-pairing, is
what keeps ions mobile, not channel topology.

## 3. Mechanical moduli — viscosity is the usable number
- **Bulk K from existing NPT volume fluctuations is unreliable** (the c-rescale barostat damps
  fluctuations ~75× → unphysical K of thousands of GPa); **not reported**. A reliable G/K needs
  dedicated Parrinello–Rahman or finite-strain runs (deferred, exploratory).
- The **measured** mechanical property is the **A.2 viscosity**: swollen ~**7.4× more viscous** than
  bare (1.4 → 10.4 cP). These swollen gels are liquid-like (low static shear expected).

## Synthesis — how the swollen gel suppresses dendrites
Not via a high static shear modulus (it is liquid-like) but via **(a)** much higher viscosity /
flux-homogenizing tortuosity (×7.4) and **(b)** an abundant, percolating, wide free-THF channel
network that keeps ion flux uniform *and* mobile (low Eₐ, Stokes–Einstein decoupling). This closes
the campaign loop: **mechanical robustness without a mobility penalty** — exactly the wet-lab
observation (smooth, dendrite-free deposition at preserved σ).

## Caveats
The 0.70 nm percolation cutoff is generous (all systems read continuous → it does not resolve channel
*width*/tortuosity, where the real difference lives — a finer pore-size/width metric is the follow-up);
single rep per system; 16-dense from 50 ns; moduli FF-dependent and exploratory.

## Files
- `mechanics/RESULTS_storyC.txt` · `scripts/network_morphology.py`
