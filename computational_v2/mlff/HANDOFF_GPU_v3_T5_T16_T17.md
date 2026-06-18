# GPU-node handoff — v3 tickets T5 / T16 / T17 (LYZ-ROG, RTX 4070 Ti SUPER 16 GB)
**Sync = git only** (FrankLiu000/PolyAPC_Calculations). **Pull branch `computational-v3-interface`** — it has the merged v2 MLFF pipeline (`computational_v2/mlff/`: models, datasets, AL/REUS scripts) **and** the v3 CPU results (`results/`, `RESULTS_v2/`). The EPYC (CPU) node DFT-labels configs + pushes; this GPU node trains MLFF + runs MD + pushes models/uncertain-configs back. **No SSH between nodes.**
**Read first:** `ARTICLE_PLAN_v3_interface_composition.md` (thesis), `RESULTS_v2/REPORT_v2_master.md` (what's proven), and the prior MLFF handoffs `HANDOFF_MLFF_2026-06-18.md` + `HANDOFF_GPU_mlff.md` (env, gotchas — **not repeated here**, heed them: `ps -C python` not pgrep; single GPU = serial; `expandable_segments:True`; `E0s=average`; slab forces masked; flock auto-resume).

## 0. Mission (one paragraph)
The CPU half **proved the v3.1 thesis** (Si-rich/Al-poor interphase suppresses Al co-deposition → reversible Mg; *not* transport): Al co-deposits on bare (C1/T2), gives a metallic electron-leaky SEI (T8) → self-discharge (T14); poly excludes Al by transport gating (T5-precursor) + electron-transfer passivation (T6) → insulating Si-rich SEI (T7/T8). **Your job = the scale the CPU can't reach:** (T5) quantify the anion's interfacial transport gating in real network MD; (T16) train a **broad reactive MLFF** {Mg,Al,Cl,O,C,H,Si} covering electrolyte+SEI+interface; (T17) run **large-cell, long-time reactive MLFF-MD** that **directly reproduces the ToF-SIMS Al-poor/Si-rich + ~90 nm confinement** — the experimental centrepiece. **Honest spine + no fluorine story** carry over.

---

## T5 — [GPU·GROMACS] Anion dynamics at the network interface
**Goal:** does the cured POSS network **sequester the Al-anion from the reductive front**? (the kinetic half of "Al-poor", complementing T6 passivation.)
**Seeds:** the classical-MD setup in `classical_molecular_dynamics/handoff_for_agent/structures/` (`{00_bareAPC, 01_polyAPC_*}` .gro/.top/.itp). **If the electrode-adjacent slab build is absent, request the PI add it to `seeds/`** (the COMPUTE_HANDOFF flagged this) — or build an electrode wall (frozen Mg(0001) plane or a repulsive wall) adjacent to the equilibrated electrolyte/gel box.
**Do (bare liquid vs poly cured network):** equilibrate an electrode-adjacent slab; over ≥50 ns measure for the **Al-anion**: (i) near-surface number-density profile ρ(z), (ii) **residence time** in the interfacial zone (<~8 Å), (iii) **approach flux** to the anode plane; contrast with the cation. (Anion D is already 4.2× slower in the gel — v2.)
**DoD:** `results/T5_anion_interface/anion_interface_dynamics.csv` + ρ(z)/residence figures + a 1-para conclusion (does the network sequester the Al-anion from the front?). Commit. Feeds Fig 5 (kinetic suppression) + master report C2.

---

## T16 — [GPU·MLFF] Broad reactive MLFF for Mg / electrolyte / SEI
**Goal:** one potential over **{Mg, Al, Cl, O, C, H, Si}** that is DFT-accurate for the electrolyte **and** the SEI/alloy/interface — the engine for T17. **Extend, don't restart:** the v2 electrolyte MLFFs `models/apc_{bare,poly}.model` + the fine-tune recipe (`run_train.sh`) + the committee/AL loop (`committee_uncertainty.py`) + REUS (`reus.py`) are your starting pipeline.
**Training data (see `v3_seeds/MANIFEST.md` for exact paths):**
- **Already labeled (reuse):** `dataset_train.xyz` (528), `dataset_poly_train.xyz` (441), `al_queue_*_labeled.xyz` — electrolyte, slab-masked.
- **NEW config space (needs CPU force-labels — the AL loop):** SEI phases (T7: MgO/MgCl₂/Al₂O₃/**SiO₂**/Mg₁₇Al₁₂), Mg–Al alloy + Al-on-Mg(0001) adatom/sub (T4), **reactive-interface AIMD frames** (T10 `bias_prod_bare-pos-1.xyz`, the CHARGE−2 deposition trajectory — re-label with forces), molecular anions/cation (T1).
- **The AL loop (cross-node):** GPU committee σ_F flags high-uncertainty configs → write `al_queue_v3_*.xyz` → **CPU DFT-labels** (PBE-D3/DZVP-MOLOPT-SR-GTH, **slab forces masked**, `bin/run_labeling.sh`) → push `*_labeled.xyz` → retrain. Iterate until force MAE plateaus.
**Recipe:** MACE-MP-0 medium fine-tune, `E0s=average` (NOT foundation — the GTH↔MACE-MP ~700 eV/atom offset), force-weighted, float32 OK for forces/MD. (Or NequIP/Allegro/DeePMD if MACE struggles on the wide composition.)
**DoD:** `models/apc_v3_broad.model` + `results/T16_mlff/mlff_validation.csv` (energy & **force MAE vs held-out DFT; target ≲ 50 meV/Å**), learning curve, dataset+model version. **Must reproduce the T10 AIMD** (Mg approach; anion stays intact/off-front; no spontaneous reduction) and the SEI-phase energetics (T7). Commit model + validation. **MLFF results are never reported without DFT cross-checks** (report MAE; active-learn high-σ).

---

## T17 — [GPU·MLFF] Large-scale reactive interface — SEI growth & Al co-deposition
**Goal (the centrepiece):** with the validated T16 MLFF, run **large-cell (10s of nm), long-time (ns) reactive MD** of Mg(0001)|electrolyte under plating conditions, **bare vs poly (network present)**, and **reproduce the ToF-SIMS result**.
**Do:** quantify, bare vs poly — **Al-anion reduction & Al co-deposition on bare vs suppression on poly**; **SEI nucleation/growth & composition-vs-depth (Si-rich vs Al-rich)**; deposit morphology/texture; event statistics. Apply plating overpotential (the CPU showed reduction is overpotential-driven, rare-event, T2/T10 — so drive it). **Spot-validate** representative reactive configs against CPU DFT (single-points → MAE).
**DoD:** trajectories + `results/T17_reactive/mlff_interface.csv` that **reproduces ToF-SIMS Al-poor/Si-rich + ~90 nm confinement** (poly AlO⁻ half-depth ~92 nm vs bare ~350 nm; poly Si ×20–34) — the experimental target. Honest caveats (MLFF accuracy off-distribution, applied conditions). Commit. Feeds Fig 5/6.
**Depends:** T16, T10 (frames), T5 (network), T6 (passivation context).

---

## CPU↔GPU data flow & what the CPU still owes you
| you (GPU) need | from CPU | status |
|---|---|---|
| electrolyte labeled set | `dataset_{,poly}_train.xyz` | ✅ committed |
| SEI/alloy/interface **force-labels** | CPU runs `run_labeling.sh` on `v3_seeds` configs (T4/T7/T10) | ⏳ **CPU AL task — request via `al_queue_v3_*.xyz`** |
| T10 interface frames (w/ forces) | re-label `bias_prod_bare-pos-1.xyz` (positions→forces) | ⏳ CPU |
| GROMACS interface seeds (T5) | `classical_molecular_dynamics/.../structures/` (+ electrode build) | ⚠ confirm/request from PI |
| poly field AIMD (T10 match) | `bias_prod_poly` | ⏳ running on CPU |

**Loop:** GPU trains/flags → CPU labels (slab-masked) → GPU retrains. Pass small artifacts via git; trajectories via a shared store; **record dataset+model versions** in each REPORT.

## Acceptance (project DoD for the GPU half)
- T5: anion interface dynamics quantified (does network sequester the anion?).
- T16: broad MLFF **DFT-validated** (force MAE reported, high-σ active-learned), reproduces T10 + T7.
- T17: reactive MD **reproduces ToF-SIMS Al-poor/Si-rich + ~90 nm confinement**, spot-validated vs DFT.
- No fluorine story; honest caveats; MLFF never reported without DFT cross-checks.
*Start: T16 (the engine) — assemble the labeled set + fine-tune; in parallel T5 (independent, GROMACS). T17 last.*
