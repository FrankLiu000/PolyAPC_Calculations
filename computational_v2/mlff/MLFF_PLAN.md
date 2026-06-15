# Machine-learning force field for poly-APC Mg electrodeposition — plan & honest scope

**Date:** 2026-06-16. **Context:** the explicit-electron deposition AIMD (job 1306, CHARGE −2 + field)
is at ~0.14 ps after ~10 h on 96 cores and shows the cation solvated ~9 Å out, unreduced — i.e. the
*event we want* (Mg²⁺ desolvation → approach → reduction/plating) is a **rare activated process on the
ns scale that AIMD physically cannot reach** (~0.1 ps/day at ~150–280 s/step). This is the textbook case
for an MLFF: DFT-accuracy forces at force-field speed (10³–10⁶× faster), unlocking ns trajectories,
enhanced sampling, and large cells.

## 1. What an MLFF can and cannot do for THIS problem (the honest part)
A standard MLFF learns the **Born–Oppenheimer PES at fixed electron count / oxidation state**. So:

- ✅ **Transport / solvation / desolvation / ion-pairing dynamics** — fixed-charge structural processes.
  This is *exactly* the campaign's converged differentiator: bare-vs-poly = **coordination/transport
  gating** (de-pairing CIP 95→84 %, polymer-O blocking the axial Mg face — classical-MD Stories F/H,
  done crudely with OPLS). An MLFF gives these at **DFT (PBE-D3) accuracy** and at the **ns / large-cell**
  scale needed for converged **free energies** (desolvation barrier, CIP↔SSIP PMF, anion access),
  bare vs poly. This elevates the story from "AIMD snapshots + scaled-charge-FF trends" to
  "DFT-accuracy free energies + rates."
- ❌ **The electron-transfer / reduction step** (Mg²⁺ + 2e⁻ → Mg⁰) and the **electrode potential** — a
  vanilla MLFF cannot change oxidation state or hold a Fermi level. Three ways to handle it:
  1. **Hybrid (recommended):** use the MLFF to overcome the slow desolvation/approach and *prepare*
     near-surface, partially-desolvated Mg²⁺ configurations, then hand those to **short DFT/AIMD**
     (or the CHARGE−2 cell) for the actual reduction. This directly fixes why 1306 is stuck: the cation
     never reaches the surface on the AIMD clock — let the MLFF carry it there.
  2. **Charge-aware 4th-gen MLFF** (Behler 4G-HDNNP with charge equilibration; CHGNet's magmom/charge
     channel) — research-grade, heavier; reserve as a stretch goal.
  3. **Constant-potential MLFF** (emerging) — bleeding-edge; not for now.

**Bottom line:** the MLFF is the bridge to the *gating* free energies (the supported mechanism), not a
magic "watch it plate" button. The reduction stays DFT.

## 2. Practical constraints on THIS node (verified 2026-06-16)
- **CPU-only** (96 cores / 377 GB RAM, **no GPU**). Equivariant-net *training* is GPU-centric → on CPU
  it's slow but feasible for **small datasets / fine-tuning**. **Inference (MD)** on CPU for ~200-atom
  cells is ~10–100 ms/step → **ns in hours–days**, still transformative vs 0.1 ps/day AIMD.
  **DeePMD-kit + LAMMPS** is the most CPU/throughput-friendly for *production* MD and is the likely
  production engine; **MACE** (incl. the **MACE-MP-0 foundation model**) is the fastest route to a
  first working potential and best for fine-tuning.
- **No forces were dumped** by any AIMD (`&PRINT FORCES` was never set). Energies are in the xyz comments
  (`E = … Ha`), but **forces — the dominant training signal (3N per frame) — must be recomputed via DFT
  single-points** on a curated subsample. This is the main data-prep cost and **needs the node (CP2K)**.
- **Data coverage gap:** existing AIMD only samples the *equilibrium basin* (cation 9 Å out). The configs
  we care about (desolvated, near-surface) are **not** in it → naive training extrapolates badly. **Active
  learning** (committee disagreement → DFT label → retrain) along steered/biased desolvation paths is
  **mandatory**, not optional.
- **Node contention:** force-labeling + training compete with job 1306. Non-disruptive prep (install,
  dataset curation, foundation-model tests) can run alongside; the DFT-labeling campaign needs a node
  decision (pause/keep 1306).

## 3. Phased plan
- **Phase 0 — setup & feasibility (non-disruptive; STARTED tonight).** Install MACE+torch(CPU)+ASE in
  the `build` env; curate the existing AIMD into an extended-XYZ scaffold (done: 529 bare + 441 poly
  energy-labeled frames, `dataset_scaffold*.xyz`); **feasibility test:** run the **MACE-MP-0 foundation
  model** on a slice of our bare trajectory and compare its *relative* energies to the DFT energies in
  the xyz comments (no new DFT needed). Decides whether a foundation model is even in the ballpark for
  this mixed metal+ionic+THF/ether system (foundation models trained on inorganic crystals often handle
  organics poorly — MACE-OFF is the organic counterpart; ours is multi-domain → likely needs bespoke data).
- **Phase 1 — force-labeled training set (needs node).** Add `&FORCE_EVAL &PRINT &FORCES` and recompute
  single-point energies+forces on ~1–2k curated frames (bare + poly + bias + the desolvation pathway).
  Subsample to decorrelate. Target ~2–5k labeled configs.
- **Phase 2 — train / fine-tune (CPU, overnight-scale).** Fine-tune MACE-MP-0 (transfer learning — far
  less data/compute than from-scratch) **or** train a compact MACE/DeePMD from scratch. Validate on a
  held-out set: target **force RMSE ≲ 50–100 meV/Å, energy ≲ few meV/atom**, and **reproduce the
  campaign's known results** (AIMD Mg–Cl distances/coordination, classical-MD de-pairing/PMF trends,
  molecular DFT energetics) as physical cross-checks.
- **Phase 3 — active learning.** MLFF-MD with an ensemble; committee disagreement flags extrapolation →
  DFT-label those configs → retrain. Iterate until the desolvation/approach pathway is covered.
- **Phase 4 — production science.** Long MLFF-MD + **enhanced sampling** (metadynamics / umbrella on the
  Mg²⁺–surface distance and first-shell coordination number) → **desolvation free-energy profile and
  rates, bare vs poly**, with replicate statistics and large cells. Spot-check the reduction step with
  DFT (hybrid, §1.1). This is the quantitative payoff: the gating mechanism as free energies.

## 3b. UPDATE 2026-06-16 — GPU node available + feasibility result
**Two-node architecture (user enabled the classical-MD GPU box).** The classical-MD node = LYZ-ROG
(RTX 4070 Ti SUPER 16 GB + 24 CPU, GROMACS, `.viz_venv`). It is a **separate machine synced via git**
(github FrankLiu000/PolyAPC_Calculations) — not SSH-reachable / not mounted from the EPYC node. So:
- **EPYC (96-core, CP2K, here):** DFT **force-labeling** single-points (the missing training signal),
  dataset curation, MACE-MP feasibility (CPU inference), and continuing AIMD. Pushes labeled data to git.
- **LYZ-ROG (GPU, via git):** MACE **training/fine-tuning** (GPU — fast, from-scratch now also viable)
  and **MLFF-MD production** (GPU inference → ns-scale, enhanced sampling). Pulls labeled data, pushes models.
This removes the CPU-only *training* bottleneck (§2). Force-labeling stays on EPYC (that's where CP2K is).

**Feasibility (MACE-MP-0 vs our DFT, CPU, 40 bare frames):** R = **0.882** (R² 0.78), mean-subtracted
relative-energy RMSE **6.05 meV/atom** — the foundation model already tracks the PES. ⇒ **fine-tune route**
(transfer-learn MACE-MP-0/medium on our labeled frames) rather than from-scratch. Caveat: energy-only,
equilibrium basin; forces + near-surface/desolvated configs (extrapolation) still need labeling + active learning.

## 4. What was done tonight (Phase 0, non-disruptive — 1306 untouched)
- Verified env: CPU-only, conda `build` (py3.11, ASE 3.28), 1.8 TB scratch.
- Launched MACE+torch(CPU) install into `build` (background).
- Curated `dataset_scaffold.xyz` (529 bare) + `dataset_poly_scaffold.xyz` (441 poly) — energy-labeled,
  forces pending. Harvester: `bin/build_mlff_dataset.py`.
- **Decision pending (user):** Phase 1 force-labeling + training need the node → keep 1306 running and
  do MLFF prep only, or pause 1306 (resumable from step 440) to start the DFT-labeling campaign.
