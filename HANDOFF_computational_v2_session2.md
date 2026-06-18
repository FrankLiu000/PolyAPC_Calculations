# Handoff — poly-APC v2 computational campaign (MLFF + interface + monitoring)
**Date:** 2026-06-18 · **Branch:** `computational-v2-package` · **HEAD = origin = `1c0ba82`**
**Repo:** github.com/FrankLiu000/PolyAPC_Calculations · **Authors:** polyAPC computational (Claude Opus 4.8, two nodes)

This continues `HANDOFF_computational_v2_Al_and_wetlab.md`. It records the state at the end of an
overnight/day monitoring session that (a) babysat the explicit-electron deposition AIMD, (b) merged and
reconciled two major GPU-node PMF pushes (stiff-spring hardening, then replica-exchange), and (c) kept the
two-node MLFF pipeline coherent in git. Honest framing throughout — magnitudes are flagged where not converged.

---

## 1. Bottom line (unchanged and now stronger)
The bare-vs-poly difference (incl. the 3.1 eV Al 2p XPS split) is **coordination / desolvation / transport
gating, NOT a redox-chemistry difference.** Four chemical nulls + the refuted chloride-abstraction artifact
stand. The MLFF desolvation PMF now confirms the gating **at the free-energy level**: both cations face a
standoff well + a steep surface desolvation barrier (neither plates spontaneously at zero field), but **poly
holds the cation ~1.5 Å further from the electrode (~7.0 vs bare ~5.5 Å) and keeps its solvation shell locked
(Mg–O CN≈6) much longer**, while bare desolvates progressively. This is the defensible, robust result.
Full narrative: `REPORT_polyAPC_v2_master.md` (esp. exec summary + §7b).

---

## 2. Git state — linear history on `computational-v2-package`
```
1c0ba82  v2 master report §7b: reconcile with REUS (replica-exchange) bare result   <- HEAD = origin
b80bc03  MLFF PMF: replica-exchange umbrella (REUS) engine + bare result (GPU)
e0ff2bb  master report §7b: correct capstone with hardened (stiff-spring) result
cd92ddb  MLFF PMF hardening: stiff-spring re-do + honest convergence verdict (GPU)
57f31a4  v2 master report: integrate MLFF desolvation-PMF capstone
6e77321  MLFF Stage-2: partial desolvation PMF (bare vs poly) — the gating result (GPU)
97653af  MLFF AL round-2: bare labeled (7/7 near-surface, slab-masked)
ea650c6  MLFF AL round-2: loop works (bare near-surface R 0.585->0.992)
771531c  MLFF Stage-1: strengthen poly committee (3->6) + self-calibrating sigma_F
37407e9  MLFF AL round-1: poly labeled (21/21, slab-masked)
6684f4b  MLFF AL round-1: bare labeled (21/21, slab-masked, elec R 0.941)
8701f02  MLFF AL round-1: DFT-labeled near-surface queues (bare+poly, slab-masked)
```
Working tree clean; local == origin. No outstanding merges.

---

## 3. MLFF desolvation PMF — current status (the headline science thread)
Three sampling generations, each more converged; **qualitative gating robust across all; magnitudes
converging but not final.** Verdict file: `computational_v2/mlff/ENHANCED_SAMPLING.md` (Stages 2 / 2b / 2c).

| Generation | What | Bare surface barrier | Convergence drift | Status |
|---|---|---|---|---|
| round-2 (6e77321) | plain US, soft springs | "barrierless → plates" | — | **ARTIFACT** (chained pull) |
| r3 (cd92ddb) | stiff springs k=3, 21 win, 15 ps | ~80 kJ/mol | 19 (bare)/30 (poly) | over-estimate, not converged |
| **REUS (b80bc03)** | replica-exchange, 28 win 4.0–9.4 Å, ~50% swap | **~50 kJ/mol ±12** | **12.5** (bare) | best estimate; residual ±12 |

- **Robust (cite freely, qualitative):** poly standoff ~7.0 Å vs bare ~5.5 Å; poly shell retention (CN≈6) to
  ~5 Å vs bare progressive desolvation (CN 6→1). Directly counted, WHAM-independent.
- **NOT converged (do not quote as final):** absolute barrier heights; a slow solvation-shell/cluster-reorg
  mode is only partly tamed by REUS. Full convergence needs **>>15 ps / a 2D shell-CN second CV**.
- **⚠ Correction recorded:** the round-2 "bare plates barrierlessly" that was briefly in §7b was a
  soft-spring chained-pull artifact; corrected in e0ff2bb. See memory `mlff-desolvation-pmf-status.md`.
- Figures: `computational_v2/results/figures/fig_pmf_r3.png` (hardened), `fig_pmf_compare.png`, `fig_pmf_bare.png`.

### >>> TOP PENDING ITEM: matched **poly REUS** is running on the GPU node.
When it lands (a new commit touching `ENHANCED_SAMPLING.md` / a poly REUS `.dat` / a figure), **surface it and
reconcile `REPORT_polyAPC_v2_master.md` §7b** with the matched bare-vs-poly REUS barrier pair. The §7b
honest-status paragraph already has an `Update (REUS …)` clause to extend.

---

## 4. Two-node architecture (sync = git ONLY; no SSH between nodes)
- **EPYC (this node, 96-core, CPU/CP2K):** DFT force-labeling (`bin/label_forces.py`), interface AIMD, the
  explicit-electron run. Pushes labeled data + report edits.
- **LYZ-ROG (GPU, RTX 4070 Ti SUPER 16 GB):** MACE-MP-0 fine-tune, MLFF-MD, umbrella/WHAM, **REUS** (`reus.py`),
  committee σ_F active-learning. Pushes models, PMF data, figures, `ENHANCED_SAMPLING.md`. **Note: this box
  rebooted mid-REUS once — `reus.py` is reboot-resumable (per-cycle `.dat` append + config checkpoints).**
- The `.model` files live on the GPU node; here we hold the scripts + datasets + figures it pushed.

---

## 5. Running / resumable CP2K jobs
- **Job 1321 — explicit-electron deposition AIMD (`bias_edep_bare_resume`)**: RUNNING, ~28.5 h, **step ~987**.
  CHARGE −2 + ±1 V field. Health all session: T oscillates **~260–355 K** around the 300 K setpoint
  (field-driven NVT; the thermostat bounds it — flag only a *sustained* climb past ~400 K), conserved qty
  flat-to-slow-creep, **0 ABORT**. **Cation Mg stays +2.06–2.08 over ~270 steps — NO spontaneous reduction**
  (the established rare-event result; this is *why* the MLFF/PMF route exists). Resumable from
  `P0d_interface/inp/bias_edep_bare-1.restart` (also a `_500.restart` checkpoint).
- **Field production run 1303 (`bias_prod_bare`)**: PAUSED, **resumable from `bias_prod_bare-1.restart`
  (step 440)**. STEPS 10000, 1 fs. Only one CP2K job runs at a time on the 96-core node, so this waits for the
  e⁻ run (or preempt it).

Resume idiom (node free):
```
cd /CH/poly_v2/P0d_interface/inp
cp bias_edep_bare-1.restart bias_edep_bare_resume.inp
sbatch --ntasks=96 /CH/poly_v2/bin/run_cp2k.sh bias_edep_bare_resume
```

---

## 6. Active-learning loop (DFT force-labeling on EPYC) — how to run a round
Datasets (in repo `computational_v2/mlff/`): `dataset_train.xyz` 528 (bare), `dataset_poly_train.xyz` 441 (poly);
AL round-1 `al_queue_{bare,poly}_labeled.xyz` 21 each; round-2 `al_queue_bare_r2_labeled.xyz` 7. Near-surface
force R climbed **0.585 → 0.992** in one AL round.

When the GPU pushes a NEW **unlabeled** `al_queue*.xyz` (NOT `*_labeled`):
1. `cp` the queue(s) from repo `computational_v2/mlff/` to the working tree `/CH/poly_v2/mlff/`.
2. Label **bare and poly in SEPARATE jobs** (per-output work dirs avoid `lblN.out` collisions):
   ```
   sbatch --ntasks=96 /CH/poly_v2/bin/run_labeling.sh /CH/poly_v2/mlff/<queue> \
       <172 bare | 276 poly> 0 "12.836,0,0,6.418,11.116,0,0,0,55" \
       /CH/poly_v2/mlff/<queue>_labeled.xyz <N> 64
   ```
   The trailing **`64` = n_slab**: forces on atoms 0–63 are **masked** (zeroed). This is mandatory — the fixed
   bottom slab's unconstrained single-point force is a +z asymmetric-slab dipole artifact (~92 eV/Å, momentum-
   non-conserving, unfittable). See memory `mlff-slab-force-fix.md`.
3. Verify with `diagnose_forces.py`: slab net force ≈ 0, electrolyte R > 0.7.
4. Commit + push. **Never re-label an already-`*_labeled` queue.**

---

## 7. Key files
- **Report:** `REPORT_polyAPC_v2_master.md` (repo root) — flagship; honest finding + §7b PMF capstone.
- **Labeling:** `/CH/poly_v2/bin/label_forces.py` (n_slab masking, per-output work dir, "FORCES|" parser,
  Ha/Bohr→eV/Å), `/CH/poly_v2/bin/run_labeling.sh`, `P0d_interface/inp/label_sp_template.inp`.
- **Analysis:** `/CH/poly_v2/bin/mulliken_regions.py` (region net charge; slab 1-64, cationMg 65-66, catLig
  67-147, anion 148-172; flags cationMg<1.5 as reduction), `analyze_interface_access.py`.
- **MLFF (GPU-authored, in `computational_v2/mlff/`):** `reus.py` (replica-exchange), `umbrella.py`, `wham.py`
  (bootstrap + convergence check), `committee_uncertainty.py`, `diagnose_forces.py`, `zero_slab_forces.py`,
  `ENHANCED_SAMPLING.md` (the running verdict), `TRAIN_REPORT.md`, `MLFF_PLAN.md`.
- **Interface inputs:** `P0d_interface/inp/bias_edep_bare*.inp` (CHARGE −2 + field), `bias_prod_bare*.inp` (field).
- **Memory (`~/.claude/projects/-CH-Claude-Calcs-20260603/memory/`):** `aimd-eps-scf-consistency`,
  `chloride-abstraction-gateway` (withdrawn), `explicit-electron-deposition`, `mlff-slab-force-fix`,
  `mlff-desolvation-pmf-status` (PMF generations + REUS).

---

## 8. Locked constraints (carry forward)
- Interface AIMD **EPS_SCF 1e-5** — do NOT tighten (matched bare/poly comparison).
- Bare APC modeled **F-free** (classic); MgF₂/triflate SEI is poly-specific. Bare-F + missing-S 2p flagged unresolved.
- MLFF labeling **must mask slab forces** (n_slab=64).
- AL queues live in repo `computational_v2/mlff/`; `cp` to `/CH/poly_v2/mlff/` before labeling. Bare+poly **separate** jobs.
- One CP2K job at a time on the 96-core node.
- Git commit messages end with: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- Honest framing mandatory; never `rm` an open output file; resumable restarts only.

---

## 9. Honest limitations (for the paper)
True grand-canonical constant-µ DFT unavailable (Dirichlet-BC is idealised); anion EAs method-sensitive;
absolute Al 2p BE not obtainable from GTH pseudopotentials; PMF is zero-field, scaled-charge (Mg +1.2),
fixed-slab **intrinsic** approach free energy (real overpotential lowers the barrier; poly *does* plate, just
with higher R_ct, consistent with the DRT); PMF **magnitudes not converged** (slow shell mode) — qualitative
gating is the deliverable, magnitudes semi-quantitative (~50 kJ/mol bare ±12 by REUS).

---

## 10. Resume the monitoring loop (if desired)
The session loop was stopped on request. To restart it, re-issue the `/loop` steady-state prompt (baseline
`1c0ba82`): each ~30 min it `git fetch`es, watches for the matched poly REUS / a new `al_queue*.xyz` /
further-converged PMF / final report (→ surface + reconcile §7b, or label a new AL round), babysits the e⁻ run
(T/SCF/cation; resume if it stops and the node is free), and re-arms. Update the baseline commit each cycle.

## 11. Immediate next steps (priority order)
1. **Matched poly REUS** (GPU, in flight) → surface + reconcile §7b with the bare-vs-poly REUS barrier pair.
2. Optionally push REUS further (longer / 2D shell-CN CV) for a fully converged magnitude — a major effort.
3. e⁻ run 1321: let it run or stop it and resume the **field production run 1303** (step 440) if the field
   channel is the priority — only one CP2K job fits on the node.
4. Any new GPU `al_queue*.xyz` → DFT-label (slab-masked, separate jobs) → push → GPU retrains.
