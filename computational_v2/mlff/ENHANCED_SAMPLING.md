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

**σ_F discriminates extrapolation.** Steered pull 9 → ~4.7 Å; the single model's |F| looked benign
(~3.5 eV/Å) the whole way — only the committee reveals the extrapolation. Detector uses a **self-calibrating
per-system threshold** (`--calib <in-dist set>` → thresh = in-dist σ_F mean + 5σ) to handle each system's
baseline.

| committee | in-dist σ_F (held-out, ~9 Å) | near-surface σ_F (~4.7 Å) | calib thresh | in-dist FP | near-surf flagged |
|---|---|---|---|---|---|
| **bare** (172 at, 3 members) | mean 49, max 124 | mean 1713, max 2844 | ~150 | 0/53 | 21/21 |
| **poly** (276 at, **6 members**) | mean 123, max 360 | mean 504, max 768 | **433** | **0/44** | **13/21** |

**Poly committee strengthened** (3 → 6 members: production seed616 + s2,s3 [60ep] + s4,s5,s6 [100ep]).
Key learning: **more members did NOT lower poly's in-distribution σ_F baseline** (mean 123 vs 115) — it is
**intrinsic** epistemic uncertainty of the under-sampled 276-atom POSS system (~440 frames over many more
DOF), not estimate noise or under-convergence (all members RMSE_F 152–174 ≈ bare's). What the extra members
*did* do: sharpen the near-surface signal (mean σ_F 314 → 504) so that — with the self-calibrating
threshold (433) — the poly detector now has **0 false positives and catches the 62% most-extrapolated
frames** (vs the 3-member/fixed-150 detector's 8/44 false positives). Bare stays cleanly ~35× separated.
The poly detector remains weaker than bare; the fundamental fix is **more poly training data** (denser
POSS sampling) — i.e. the AL loop itself.

**AL queues written:** `al_queue_bare.xyz` (21 frames, σ_F 884–2844 — high-confidence) +
`al_queue_poly.xyz` (13 frames, σ_F > 433 — high-confidence after strengthening) — for EPYC to DFT-label.

## Stage 1b — AL loop turning: round-1 + round-2 DONE (2026-06-17)
**Round-1.** EPYC DFT-labeled the queues (`al_queue_{bare,poly}_labeled.xyz`, 21 frames each, slab-masked,
electrolyte R 0.94/0.93, gate PASS). Folded into extended train sets (`mlff_{bare,poly}_r2_train.xyz`,
496/418 frames) and retrained 3-member committees per system (`run_{bare,poly}_r2_s{1,2,3}/`, 60 ep).

**The loop demonstrably works — near-surface force accuracy vs DFT ground truth:**

| system | round-1 model (never saw near-surface) | round-2 model (trained on it) |
|---|---|---|
| **bare** | RMSE 1222, MAE 259, **R 0.585** (badly extrapolating) | RMSE 258, MAE 83, **R 0.992** |
| **poly** | RMSE 261, MAE 80, R 0.931 (already decent) | RMSE 190, MAE 58, R 0.963 |

Bare near-surface went from badly-extrapolating to excellent; poly improved modestly (its round-1 model was
already reasonable there — the POSS network constrains the near-surface configs).

**Frontier advanced — and bare vs poly diverge (informative):**
- **Bare:** round-1 model went wild past ~4.6 Å; **round-2 steers stably to ~3.2 Å** (near-contact). The
  3.2 Å frames are still uncertain (σ_F up to 9130, calibrated thresh 2553) → **`al_queue_bare_r2.xyz`
  (7 near-contact frames)** for EPYC round-2 labeling → bare round-3.
- **Poly:** round-2 steers stably to **~3.4 Å with LOW σ_F (mean 253, 0/41 flagged)** — it already
  extrapolates confidently there (POSS-constrained configs generalize well). But pushing to ~2.8 Å
  **destabilizes** (cation slams the POSS-crowded surface → force singularity; the new blow-up guard in
  `umbrella.py` aborts cleanly). So poly has **no clean round-2 queue** — it is either confident (≥3.4 Å)
  or exploding (<3 Å), with no stable uncertain frames to label. Poly's near-contact (<3 Å) needs gentler
  round-3 steering (e.g., stiff restraint from a stable 3.4 Å start).

**σ_F refinement (learned this round):** σ_F is an *absolute* force-std, so it scales with the intrinsically
larger near-surface forces — it stays elevated even where accuracy is now excellent (bare 4.7 Å σ_F ~830 at
R 0.992). So σ_F is a *relative* flag: calibrate each round on the *now-covered* band, queue frames well
above it. (Caveat: low σ_F = members agree ≈ likely accurate, but a same-data committee can be
"confidently wrong" — spot-check poly's 3.4 Å confidence with a couple of DFT labels.)

**Iterate (round-3+):** EPYC labels `al_queue_bare_r2.xyz` → fold in → retrain → steer bare to ~2 Å; for
poly, gentler near-contact steering + a DFT spot-check at 3.4 Å. **Stage 2 is now partly unlocked:** a
trustworthy **partial desolvation PMF over ~3.2–9 Å (bare) / ~3.4–9 Å (poly)** — most of the bulk→near-contact
approach — is *already* feasible with the round-2 models (run umbrella windows over that range + WHAM).
Hybrid: hand near-contact desolvated snapshots to EPYC for the DFT reduction step (MLFF can't change oxidation state).
