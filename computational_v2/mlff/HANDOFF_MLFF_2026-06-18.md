# MLFF effort — full-state handoff (GPU node / LYZ-ROG), 2026-06-18

Single document to pick up the poly-APC MLFF work. Two-node split (see `HANDOFF_GPU_mlff.md`): **EPYC**
DFT-labels interface configs + pushes; **GPU node (LYZ-ROG, this box)** fine-tunes MACE + runs MD/enhanced
sampling + pushes back. Branch `computational-v2-package`, everything under `computational_v2/mlff/`.
Detail docs: **`TRAIN_REPORT.md`** (models + the data-bug story), **`ENHANCED_SAMPLING.md`** (the full PMF
saga, Stages 0–2c), master report **§7b** (the capstone, corrected). This file = the map + status + gotchas
+ next steps.

## 1. TL;DR status
- **DONE & solid:** matched bare+poly electrolyte MLFFs (committed); active-learning loop *demonstrated
  working* (near-surface force R **0.585→0.992** in one round); the **qualitative desolvation "gating"**
  result, now in master report §7b.
- **OPEN:** a *converged quantitative* desolvation **barrier**. The magnitude does **not** converge with
  straightforward umbrella sampling — there is a **slow solvation-shell/cluster-reorg mode**. Replica-exchange
  (REUS) helps (convergence drift 19→12.5 kJ/mol) but isn't fully converged; bare REUS done to 22 ps, poly
  REUS **stopped mid-run** (cycle ~7) per user request.
- **Robust scientific take:** poly holds the Mg cation **~1.5 Å further from the electrode (~7.0 vs ~5.5 Å)
  and keeps its solvation shell (CN≈6) much longer** → it gates desolvation/approach. Barrier *magnitude*
  ≈50 kJ/mol (bare) but **±~12 kJ/mol, not converged** — report as qualitative/semi-quantitative.

## 2. Map — where things live
- **Env:** venv `/lyz/Claude_workplace/polyAPC/.mlff_venv` (torch 2.6.0+cu124, mace-torch 0.3.16, ASE 3.28).
  No conda on this box. Always `export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`.
- **Models (committed):** `models/apc_bare.model`, `models/apc_poly.model` (6.6 MB; force-only, slab-masked,
  fixed-electrode electrolyte potentials). Round-2 / committee / REUS-init models in `run_*/` are **LOCAL +
  gitignored** (reproducible via the scripts below).
- **Data (committed):** `dataset_train.xyz` (bare 528), `dataset_poly_train.xyz` (poly 441) — slab forces
  masked. `al_queue_{bare,poly}_labeled.xyz` (round-1 near-surface, EPYC-labeled), `al_queue_bare_r2_labeled.xyz`
  (round-2). Derived splits / extended sets (`mlff_*_train.xyz`, `*_r2_train.xyz`) are local/gitignored.
- **Scripts:** `run_train.sh` (MACE fine-tune), `prep_split.py`, `select_md_start.py`, `eval_test.py`,
  `run_md.py` (NVT MD, rigid slab), `committee_uncertainty.py` (σ_F), `umbrella.py`+`wham.py`+`run_umbrella.sh`
  (umbrella+WHAM), `reus.py`+`run_poly_reus.sh` (replica-exchange US), `diagnose_forces.py` (data QC gate),
  `fig_*.py`. Figures → `../results/figures/fig_mlff_train.png`, `fig_mlff_matched.png`, `fig_pmf_*.png`.

## 3. Science — established vs open
- **Models (held-out, electrolyte forces; slab masked → ≈0):** bare MAE **27** meV/Å, R **0.913**; poly MAE
  **33**, R **0.951**. Matched recipe: force-only (`EWEIGHT=0`), `E0s=average`, multihead off, float32, k-rmax
  from foundation (6 Å), no-SWA, ~100 ep. Stable in NVT MD (anion intact, ~9 Å off front — reproduces AIMD).
- **Active learning (Stage 1, works):** committee σ_F flags near-surface extrapolation → EPYC DFT-labels →
  retrain. Round-2: bare near-surface **R 0.585→0.992** (RMSE 1222→258); steerable frontier advanced
  ~4.6→3.2 Å (bare). Poly extrapolates near-surface better (POSS-constrained) but its committee σ_F has a
  higher intrinsic baseline (needs more poly data; flagging provisional).
- **Qualitative gating (robust, from directly-counted coordination — WHAM-independent):** on approach, **bare
  desolvates progressively (Mg–O 6→1)** while **poly retains its full shell (Mg–O≈6) to ~5 Å**, and poly's
  free-energy well sits ~7 Å vs bare's ~5.5 Å. This is the coordination/transport gating of §1/§10 at the
  free-energy level. In master report §7b + exec summary.
- **PMF magnitude — NOT converged (the open problem):** plain umbrella drift 19–30 kJ/mol; the bare span
  wandered 88→56→80 kJ/mol across passes (round-2 5 ps → 12 ps soft-spring → r3 stiff-spring). ⚠ The round-2
  "bare barrierless-downhill, plates" was a **chained-pull artifact** (corrected). REUS (Stage 2c) lowers
  drift to 12.5 but residual remains. Best estimate: bare surface (desolvation) barrier ~50 kJ/mol ±~12.

## 4. REUS state + how to resume/finish
`reus.py` = self-contained Hamiltonian replica-exchange US (no PLUMED): N windows round-robin on the 1 GPU,
neighbour config swaps (Metropolis on bias energies) mix the slow mode; **reboot-resumable** (per-cycle
`window_z*_chk.xyz` checkpoints + `.dat` append). Current: k=1, 0.2 Å spacing, 28 windows 4.0–9.4 Å, tau=500
fs, ncyc=50 (25 ps), exchange ~30–50%.
- **Bare REUS:** `umb_bare_reus/` has 22 ps (cycle 44/50, reboot-interrupted; no `_chk` from that run so not
  resumable — re-run fresh if you want more). WHAM (`wham.py umb_bare_reus umb_bare_reus/window_z*.dat
  --equil 10000 --boot 100`) → span ~52, drift 12.5.
- **Poly REUS:** `umb_poly_reus/` partial (~cycle 7, stopped). **To finish:** `bash run_poly_reus.sh`
  (flock-guarded, resumes from `_chk`; ~11 h). Then `fig_pmf_compare.py reus ../results/figures/fig_pmf_reus.png`
  for the matched figure.
- **For a genuinely converged PMF** (if needed): the slow mode needs MORE than 25 ps REUS — extend ncyc
  (reus.py resumes), and/or add a **2D bias on (z, shell-CN)** to attack the slow DOF directly (not yet
  built; needs a differentiable coordination CV), and/or replicate seeds. Multi-day; convergence not guaranteed.

## 5. Operational gotchas (each cost real time — heed them)
- **Process checks: use `ps -C python` (name-based).** `pgrep -f <pattern>` matches your *own* command
  subshells → phantom "1/2/4 processes" + apparent "respawning". This wasted hours.
- **Single GPU ⇒ everything is SERIAL.** Never run two GPU jobs at once (OOM / mutual thrash).
- **`expandable_segments:True` is mandatory** — the dense 64-atom Mg slab (r_max 6 Å → huge graph) otherwise
  pins the 16 GB GPU.
- **`E0s=average`, not `foundation`** — the CP2K-GTH↔MACE-MP reference offset is ~700 eV/atom; foundation E0s
  forces the interactions to learn it → energy gradient spikes/destabilizes. float32 is fine for forces/MD.
- **Slab forces are masked (=0)** in all labeled data (fixed-slab artifact, see TRAIN_REPORT §2/§5); the slab
  is held rigid in MD. Never train on / expect physical slab forces.
- **The box REBOOTS mid-run** (e.g. 2026-06-18 12:57): `/tmp` clears, all processes + background waiters die;
  repo-dir outputs (`umb_*/*.dat`, `*_chk.xyz`) survive. `reus.py` resumes from checkpoints.
- **Auto-resume watchdog: MUST use flock.** `run_poly_reus.sh` has a flock guard; a cron watchdog
  (`watchdog_reus.sh`) without flock double-launched REUS → two procs thrashing the GPU (stuck 3 h). The cron
  was **removed**; re-add (now flock-safe) only if unattended reboot-autonomy is needed, and verify with
  `ps -C python` that exactly one runs.
- **WHAM (`wham.py`):** `--mincount` masks under-sampled bins (else WHAM blows up at edges → spurious huge
  barriers); `--boot N` gives statistical error bars; it prints the **first/second-half convergence drift** =
  the key convergence metric. Soft springs (k≤0.5) let deep windows collapse in the steep approach region
  (leaves gaps) → use **k≥1 + tight (≤0.3 Å) spacing**; for REUS, exchange overlap needs ~1–1.5σ spacing.
- **pkill self-match:** `pkill -f reus.py` matches its own wrapper → exit 144 + suppressed output. Use the
  `[r]eus.py` bracket trick, or kill by PID from `ps -C python`.

## 6. Next steps (prioritized)
1. **Decide qualitative vs quantitative.** The gating result is solid and already reported. A converged
   barrier *magnitude* is a major, uncertain additional effort (Stage-2c §4 above).
2. **If finishing the matched REUS PMF:** `bash run_poly_reus.sh` to complete poly (resumes), re-run bare REUS
   fresh for a matched length, WHAM both, `fig_pmf_compare.py reus`. Expect ~±12 kJ/mol residual unless you
   also extend sampling / add the 2D shell-CN CV.
3. **Hybrid reduction (the e⁻-transfer/plating step the MLFF cannot do):** hand near-contact desolvated
   snapshots (e.g. `al_queue_bare_r2_labeled.xyz` ~3.2 Å configs) to **EPYC** for CHARGE−2 DFT/AIMD.
4. **Strengthen poly:** more poly training data (denser POSS sampling) to lower its intrinsic committee σ_F
   baseline and sharpen its AL detector.

## 7. Commit trail (this effort, on computational-v2-package)
ad9810b (data-bug find) → 3af81fc (PoC) → bf7a64e (fix verified) → a043959 (matched models) → ff8e254
(matched MD) → 986fbd0 (enh-sampling setup) → f86b070 (committees+AL) → c88f2d8 (poly committee) → ea650c6
(AL round-2) → 6e77321 (Stage-2 PMF) → cd92ddb (PMF hardening) → e0ff2bb (§7b correction) → b80bc03 (REUS
engine + bare result) → [this handoff]. EPYC interleaved: AL labeling (8701f02, 6684f4b, 37407e9, 97653af),
§7b integration (57f31a4).
