# T20 — Interfacial aluminate-anion concentration profile C(z), bare vs poly

**Node:** GPU (LYZ-ROG) · **Date:** 2026-06-24 · **Status:** ✅ DONE
**Dispatched by:** `NODE_REQUESTS.md` T20 (manuscript re-framing panel "B")

## Why
Re-frame the T5 anion-sequestration result into the PI's own stripping-killer framework
(Liu, *Adv. Mater.* **2022**, 34, 2201886): uneven **stripping** is the failure mode, driven by
**interfacial accumulation of chlorine-bearing complex ions**; the prescribed cure is to
**homogenize the interfacial anion concentration**. This panel shows the cured poly-APC network
achieves that homogenization **structurally** (no stirring), mirroring Liu Fig 5e–g C(x).

## Method
- **Trajectories (existing, neutral, field-free):** `bare_final_traj.xyz` (3956 frames) +
  `poly_final_traj.xyz` (1401 frames), matched MLFF model (t16_broad_r5), rigid 64-Mg(0001) slab.
  First 20 % discarded as equilibration; block-averaged (5 blocks) error bars.
- **Single ion pair per cell** → C(z) is the equilibrium **single-ion occupation density (PMF
  limit)**, not a many-ion concentration. The film is nanoscale (electrolyte ~8 Å above the front,
  **no bulk plateau**), so profiles are normalized to unit integral (∫C dz = 1), **not** C/C_bulk.
- **Tracers (assignment-robust):** anion = the covalent Ph₂AlCl₂⁻ unit (Al-rooted tree, 25 atoms =
  Al+2Cl+12C+10H) and its reducible **Al** center; cation = its **leading Mg(II)** (the cation Mg
  closest to the slab each frame). Distance to electrode reported as 3D min-distance to the slab
  (the physical metric) alongside perpendicular z (the Liu-style coordinate).

## Results (t > equilibration; field-free)

| observable | bare | poly |
|---|---|---|
| anion·Al — 3D min-distance to electrode | **4.58 ± 0.19 Å** | **6.81 ± 1.27 Å** |
| anion·Al — perpendicular z above front | 4.18 ± 0.18 Å | 5.37 ± 0.81 Å |
| anion — **near-front occupancy** (Al ≤ 5 Å, 3D) | **98.8 %** | **2.2 %** |
| anion — closest approach ever (min Al 3D) | 4.01 Å | 4.58 Å |
| anion — **reductive contact** (Al ≤ 2.5 Å) | **0 %** | **0 %** |
| cation — leading-Mg 3D min-distance | 5.78 ± 0.18 Å | 5.20 ± 0.92 Å |

**Headline — structural sequestration of the reducible anion.** The reducible Al sits within 5 Å of
the **bare** electrode **98.8 %** of the time but only **2.2 %** in **poly** — a ~**44×** drop in
near-front anion occupancy. The poly Al distribution (6.81 Å) and the bare one (4.58 Å) barely
overlap. This is the Liu-2022 "homogenize the interfacial anion" cure, realized **structurally** by
the cured network: the Cl-bearing aluminate is held out of the near-electrode zone without stirring.

**The inversion (mechanism).** Cation transparency is preserved — the cation's leading Mg reaches the
front **similarly in both** (5.78 vs 5.20 Å). Combined with the anion standoff this **inverts the
interfacial ion ordering**:
- **bare:** anion 4.58 Å **<** cation 5.78 Å → the *reducible* anion leads, closest to the electrode.
- **poly:** anion 6.81 Å **>** cation 5.20 Å → the *innocuous* Mg-cation leads; the reducible anion
  is excluded behind it.

That inversion is the field-free structural basis for suppressing anion reduction / Al co-deposition:
the network keeps the reducible species out of the reactive front while letting the plating cation in.

## Honest caveats / scope
1. **Perpendicular C(z) understates the standoff** (the T5 lesson): the anion *centroid* z is similar
   (bare 5.41 vs poly 5.62 Å) because part of the separation is **lateral**. The 3D min-distance
   (and the reducible-Al specifically) is the discriminating, physical metric — that is the headline.
2. **The 44× ratio is threshold-placed between the two peaks** (5 Å sits between bare 4.58 and poly
   6.81) and is therefore sensitive to the cutoff. The robust statements are the **+2.2 Å mean 3D
   shift** and the **near-non-overlapping distributions**; 44× is the occupancy expression of those.
3. **Field-free → both anions are "safe"** (0 % reductive contact). T20 is an equilibrium *distribution*
   (model), not a reactive event. The actual reduction discrimination appears under **driving** (the
   T5 charge-conditioned biased MD + the EPYC co-deposition AIMD, ~2.5 Å contact gate).
4. **⚠️ Poly standoff is NOT cleanly equilibrated** (see `../T5_anion_interface/fig_equilibration.png`).
   Bare snaps to 4.58 Å and stays (slope −0.01 Å/ns, σ 0.19); the **poly** anion–electrode distance is
   a slow/soft DOF — independent neutral runs settle anywhere from **6.8 to 10.3 Å** and still drift
   (`poly_final`, used here, is *still falling inward*, −8.9 Å/ns, from a far start). So T20's poly
   numbers (Al 6.81 Å, 44×) are **sign-robust but magnitude-uncertain**: every poly run keeps the anion
   well beyond bare's 4.6 Å (qualitative exclusion + inversion hold), but the precise standoff needs a
   PMF / multi-start equilibration to pin down. The bare leg and all *qualitative* T20 conclusions stand.
5. **Bare cation partially dissociates** in this trajectory — one cation Mg drifts to ~35 Å (poly:
   intact, ≤11 Å). Therefore the bare **cation centroid** and the **Al↔Mg₂ ion-pair separation** are
   **not reliable observables here** and are *excluded*; the robust **leading-Mg** tracer is used
   instead. ⚠️ **Reconciliation flag:** the ion-pair-separation numbers quoted in `fig_mechanism`
   (bare 7.8 / poly 9.9 Å) should be re-derived on a clean trajectory / dissociation-proof definition
   — T20 neither corroborates nor uses them. The T20 *anion* and *inversion* results are independent
   of this and stand.

## Deliverables → `results/T20_iface_profile/outputs/`
- `anion_density_profile.csv` — z (Å), C(z) anion & cation (leading-Mg) bare/poly + block-std errors.
- `iface_accumulation_metrics.csv` — 3D standoffs, near-front & reductive-contact fractions, cation
  drift, per system.
- `Cz_profile.png` — (left) perpendicular C(z); (right) 3D standoff + the anion/cation inversion.
- `make_profile.py` — reproducible analysis (CPU post-processing; did not touch the GPU R1 run).
