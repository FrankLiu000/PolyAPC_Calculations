# Enhanced sampling — Mg²⁺ desolvation/approach free energy (bare vs poly)

**Goal.** The gating free energy the MLFF was built for: the reversible work to bring the
[Mg₂(μ-Cl)₃·6THF]⁺ cation from the bulk-electrolyte basin (~9 Å off the electrode) toward the Mg(0001)
surface, shedding its first solvation shell — **bare vs poly**. AIMD cannot reach this (rare, activated,
ns-scale); the MLFF + umbrella sampling can. The electron-transfer/plating step stays DFT (hybrid).

## Collective variable & method
- **CV** = z-height of the cation-Mg core COM above the slab top layer (the approach coordinate;
  desolvation happens implicitly as the surface displaces the THF/Cl shell). The slab is held rigid
  (these are fixed-electrode electrolyte potentials), so z_ref is constant.
- **Umbrella sampling**: harmonic bias ½k(CV−z0)² per window; reconstruct F(z) by WHAM. Self-contained
  in ASE + MACE — **no PLUMED dependency** (avoids a kernel-build on this box). Coordination numbers
  (Mg–O THF, Mg–Cl) and cluster integrity (Mg–Mg) are tracked along z = the desolvation read-out.
- Scripts: `umbrella.py` (one window), `wham.py` (1D WHAM → `*_pmf.dat`), `run_umbrella.sh` (driver),
  `fig_pmf.py` (figure).

## ⚠ Hard constraint: the current MLFFs only cover the equilibrium basin
The Round-1/2 training data spans cation height **8.2–9.6 Å (bare) / 8.6–9.5 Å (poly)** — **0 frames
below 6 Å** (the AIMD never approached). So:
- Windows at **~8–10 Å are in-distribution** (trustworthy) → the validation pilot lives here.
- Windows **below ~8 Å are extrapolation** → the PMF there is **not reliable** until active learning
  labels near-surface configs. `umbrella.py` logs electrolyte |F|max as a crude extrapolation flag;
  `wham.py` reports frames > 12 eV/Å to queue for DFT.

## Staged plan
- **Stage 0 — validate machinery (in-distribution pilot, DONE/here).** Windows z0 = 8.0–10.0 Å, bare.
  Confirms bias holds, histograms overlap, WHAM reconstructs a sensible basin around ~9 Å. Result below.
- **Stage 1 — active learning down the approach coordinate.** Add windows stepping toward the surface
  (z0 → 7, 6, … 2 Å), each started from the previous window's final frame (steered). `umbrella.py`
  flags high-|F| frames → `al_queue.xyz` → **push to EPYC** for DFT single-points (`bin/label_forces.py`,
  slab-masked) → append to `dataset_train.xyz` → re-fine-tune. Iterate until a **committee** (3–5 seeds,
  trained per system — Step "committee" below) has low σ_F along the whole path.
- **Stage 2 — converged F(z), bare vs poly.** Full window set with the active-learned model; report the
  desolvation **barrier + well depth + CN profile**, bare vs poly, with replicate windows + SEM. This is
  the quantitative gating result (does the poly network raise the desolvation barrier / shift the shell).
- **Hybrid reduction.** Hand near-surface desolvated snapshots back to EPYC for short CHARGE−2 DFT/AIMD
  (the actual e⁻ transfer) — the MLFF cannot change oxidation state.

## Committee (uncertainty, prerequisite for Stage 1)
Train 3–5 seeds per system (vary `--seed` in `run_train.sh`); during biased MD, σ_F across the committee
flags extrapolation (σ_F ≳ 150 meV/Å) → that's the AL trigger. Cheap on this GPU (each seed ≈ the
100-epoch runs already done). Not yet built — first task of Stage 1.

## Pilot result (Stage 0 — machinery VALIDATED, 2026-06-16)
Bare, 5 windows z0 = 8.0–10.0 Å (k=1.0 eV/Å², 6 ps/window, 2 ps discarded, 1005 samples), WHAM:
- **Windows land on target** (⟨cv⟩ = 8.05, 8.49, 8.95, 9.46, 10.00 Å; σ≈0.11–0.18 Å) — the bias works.
- **F(z): shallow basin, min ~8.4 Å, span ≈ 7.6 kJ/mol** over the sampled 8–10 Å (≈3 kT — physical for a
  freely-fluctuating equilibrium cation; matches the unbiased 8.2–9.6 Å spread). Profile is *noisy* — the
  pilot is short and overlap is thin at k=1.0/0.5 Å spacing; production needs ~0.25–0.3 Å spacing (or
  k≈0.4) + longer windows (`fig_pmf_bare.png`).
- **First shell intact** across 8–10 Å (Mg–O ≈ 6.0 = the 6-THF shell, Mg–Cl ≈ 5.7) — **no desolvation in
  the equilibrium region**, as expected; desolvation only sets in near the surface (Stage 1).
- **Extrapolation flag: 0/1005 frames > 12 eV/Å** → 8–10 Å is genuinely in-distribution; the single model
  is trustworthy here. (Below ~8 Å it will not be — Stage 1.)
- WHAM bug fixed: under-sampled edge bins (counts < `--mincount`) are masked (they made an apparent
  ~1716 kJ/mol artifact; the well-sampled barrier is 7.6 kJ/mol).

**Verdict: the umbrella+WHAM pipeline is built and validated.** It is ready to drive the desolvation
profile; the scientifically-meaningful near-surface region needs the Stage-1 active-learning loop
(committee + EPYC DFT labeling) before its PMF can be trusted.

## Stage 1a — committee + σ_F extrapolation detector (BUILT + VALIDATED, 2026-06-16)
Committees of **3 members/system** (production seed 20260616 + two new seeds s2/s3, identical recipe,
60 ep; member binaries local in `run_{bare,poly}_s{2,3}/`, RMSE_F 144–158 all). `committee_uncertainty.py`
computes per-atom force std across members; σ_F(frame) = max over the electrolyte atoms. `run_committee.sh`
trains them; `umbrella.py` now also dumps a trajectory (`*_traj.xyz`) for queueing.

**σ_F discriminates extrapolation — cleanly for bare, noisily for poly:**

| committee | in-dist σ_F (held-out, ~9 Å) | near-surface σ_F (pull to ~4.6–4.9 Å) | separation | thresh |
|---|---|---|---|---|
| **bare** (172 at) | mean 49, max 124 | **mean 1713, max 2844** | ~35× (no overlap) | 150 → 0/53 FP, 21/21 TP |
| **poly** (276 at) | mean 115, max 362 | mean 314, max 512 | ~2.7× (**overlaps**) | 150 → 8/44 FP |

The single model's |F| looked benign (~3.5 eV/Å) through both pulls — only the committee reveals the
extrapolation. **Bare detector is clean** (threshold 150 meV/Å, 0 false positives, 100% recall on the
pulled frames). **Poly detector is noisier**: its in-distribution baseline is ~2× higher and overlaps the
near-surface range — genuine higher epistemic uncertainty of the larger/more-flexible POSS system (~440
frames covering many more DOF), not just under-convergence (poly s2/s3 RMSE_F 152/154 ≈ bare's). → the
poly AL loop needs **more committee members / more training data** and a **higher per-system threshold
(~400 meV/Å)** before σ_F is reliable; report poly σ_F-flagging as provisional.

**First AL queues written:** `al_queue_bare.xyz` (21 frames, σ_F 884–2844 — high-confidence) +
`al_queue_poly.xyz` (21 frames, σ_F 176–512 — provisional) — near-surface configs for EPYC to DFT-label.

## Stage 1b — the active-learning loop (next, needs EPYC)
1. **Push** `al_queue_{bare,poly}.xyz` → EPYC labels them (`bin/label_forces.py`, n_slab=64 slab-mask) →
   appends to `dataset_{train,poly_train}.xyz` → pushes back.
2. **Retrain** the committee on the extended data; re-run a deeper steered pull; re-flag.
3. **Iterate** (steer toward smaller z each round) until σ_F stays < ~150 meV/Å along the whole approach
   coordinate — then the umbrella windows down to ~2 Å are trustworthy.
4. **Stage 2:** converged desolvation F(z), barrier + CN profile, **bare vs poly**. Hybrid: hand the
   final near-surface desolvated snapshots to EPYC for the DFT reduction step.
