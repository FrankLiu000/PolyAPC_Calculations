# HANDOFF — poly-APC computational, v3 interface session (2026-06-23)

You are the EPYC **CPU/DFT-AIMD node**. The other node is **LYZ-ROG GPU (MLFF/MD)**. The two nodes share
**nothing but git** (branch `computational-v3-interface`, GitHub `FrankLiu000/PolyAPC_Calculations`). No SSH.
You "talk" to the GPU by committing files (it has its own monitor reading the repo); the GPU author shows as
`FrankLiu000`, you commit as `polyAPC computational`. **Every commit message ends with**
`Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Branch off `main` only if asked to PR; otherwise
commit straight to `computational-v3-interface`.

## What you're doing right now
Running a **30-min cron monitoring loop** (the recurring user prompt). Each cycle: (1) `git fetch --all`,
diff for new GPU commits since the baseline (look for `results/T17_reactive/*`, a new `al_queue_v3_*.xyz` to
DFT-label, or a new MLFF model/validation row — reconcile results into `RESULTS_v2/REPORT_v2_master.md`);
(2) `squeue -u $USER` job health. If both quiet → tight one-line "no change" and re-arm. **Baseline commit
to update each cycle is currently `e29073c`.** **HARD RULE: never resume job 1378** (poly field AIMD,
`/CH/poly_v2/P0d_interface/inp/bias_prod_poly`) — deliberately abandoned at ~50 min/step.

## Mission + hard constraints (do not violate)
Prove *why* the in-situ POSS-cured poly-APC Mg-anode interphase is **Si-rich / Al-poor**, and why that (NOT
ion transport) makes Mg plating reversible — centred on the **reduction/co-deposition chemistry of the APC
Al-anion**. Constraints: **Si↑/Al↓ story only, NO fluorine/MgF₂**; **transport is NOT the discriminator**
(D≈8–9e-15 cm²/s, t₊=0.50 both); **always bare vs poly in parallel**; **no fabrication** — label models as
models, convergence-verify, report uncertainties honestly. See `ARTICLE_PLAN_v3_interface_composition.md`,
`COMPUTE_HANDOFF_tasks.md`, `RESULTS_v2/{REPORT_v2_master.md,STATUS.md}`.

## ★ Scientific state — the bias/EDL arc is CLOSED (this session's spine)
The discriminator is **the network keeps the reducible Al-anion away from the reductive front**, confirmed by
**THREE independent lines that converge on one number** (now in the master report):
1. **Structural standoff 1.65×** — matched neutral MLFF-MD (GPU r6, 500 ps): bare `slabMin` 4.58 Å vs poly 7.57 Å
   (z-height ~4 Å in BOTH — misleading; the standoff is only in the 3D `slabMin`). Honest range 1.4–2.2× (poly slow-mode-limited).
2. **Static biased-DFT force-response 1.6×** — your `incoming/biased_labeled.xyz` (34 frames, q=±1): the force on
   the reducible Al responds to ±1e bias 0.42 (bare) vs 0.27 eV/Å (poly).
3. **Dynamic field-modulated standoff 1.7×** — the charge-conditioned MACELES (below): under cathodic q=−2 bias
   the standoff shifts bare 4.58→5.53 (+0.95) vs poly 7.57→9.21 Å (+1.64) = the network amplifies the
   field-driven exclusion ~1.7×.

**Bare co-deposition mechanism (your AIMD, now the T5 capstone):** the bare Al reduction is **ET-gated and
contact-triggered at ~2.5 Å** — NOT spontaneous (the anion retreats), NOT from proximity alone (intact at 2.8 Å),
fires only when forced into ~2.4 Å contact (qAl +0.47→+0.23, ET-first with both Cl elongating; spin≈0 =
metallic incorporation, not a radical). Charge×distance scan: distance is the master variable, the cathodic
charge a secondary contact-gated boost; the field's role is transport. Reversible/shallow on the ps scale →
consistent with Al⁰ accumulating slowly in the bare SEI (ToF-SIMS). `incoming/bare_codep_*`.

**The charge-conditioned MACE (latest, the payoff):** the GPU's two naive biased-MD routes failed (external
`q·E` captured 10–30 %; per-charge fine-tune fit static but ran away in MD). You supplied the fix: a 4-point
**Q-ladder** (55 interface geometries at q∈{−2,−1,0,+1}, `incoming/charge_ladder_labeled.xyz` + the q±1 batches)
+ a recipe (`mlff/v3/CHARGE_CONDITIONED_MACE_recipe.md`). The GPU trained **MACE+LES** on it; your **decisive
gate PASSED** (held-out q=−2 force MAE 60.6 meV/Å = single-charge), MD ran stable (cap=0, 100 ps) → the 1.7×
dynamic EDL above. This is the end of the bias/EDL thread.

## Infrastructure you'll reuse (all working, OMP-pinned)
- **DFT force-labeling:** `bin/run_labeling.sh <scaffold.xyz> <Nat> <CHARGE> <latticeCSV9> <out.xyz> <max> <n_slab>`
  → `bin/label_forces.py` runs CP2K Γ-point ENERGY_FORCE per frame from `mlff_v3_label/label_sp_template.inp`
  (PBE-D3, DZVP-MOLOPT-SR-GTH, CUTOFF 400/REL 50, Fermi smearing 500 K, **hardened mixing ALPHA 0.10/NBROYDEN 14**,
  ADDED_MOS 150). It **masks the bottom n_slab forces** (dipole artifact; n_slab=64 for both 172-atom bare &
  276-atom poly cells) and **tags every frame `scf_converged=T|F`** (gate on it; never ship F). Combine waiters
  (e.g. `biased/batch2_waiter.sh`) drop unconverged + overlap (free |F|>25) frames and re-tag
  `config_type=bias_<sys>_q<±N>_d<Å> net_charge=<q>`.
- **Throughput:** ALWAYS `export OMP_NUM_THREADS=1` (cp2k.psmp spawns OpenMP threads → oversubscription, ~15×
  slowdown). 2 streams of 48 cores (96-core node) is the sweet spot; 4 small jobs thrash memory bandwidth.
- **Steered/reactive AIMD:** `mlff_v3_label/steered/*` and `codep_aimd/*`. Pattern: explicit **A/B/C tilted cell**
  (b = `6.418 11.116 0`, NOT orthorhombic — the #1 blow-up cause), `&CONSTRAINT &FIXED_ATOMS LIST 1..32` (bottom
  2 layers; the CV atom must be mobile), `&COLLECTIVE COLVAR 1 INTERMOLECULAR TARGET … TARGET_GROWTH …`, **CSVR
  thermostat** (CSVR-8 absorbs exothermic reaction heat that overwhelms a loose Nosé), `EXTRAPOLATION ASPC` for
  fast MD SCF. Charged slab (CHARGE −n) = cathodic/reducing electrode.

## Hard-won lessons (read before re-doing anything)
- **Tilted cell or it explodes** — non-orthorhombic seeds; use A/B/C vectors, never `ABC … 90 90 90`.
- **`OMP_NUM_THREADS=1`** — else CP2K oversubscribes the node.
- **Scaffold building:** *jitter already-physical frames* (±0.08–0.1 Å on non-slab atoms) — DON'T translate the
  anion into a dense cell. Translating into the bare electrolyte clashed ~half the frames; translating into the
  poly POSS network clashed ALL of them. Jittering pilot poly frames = 0 overlaps.
- **Steering geometry artifact:** an Al–Mg *distance* CV with both atoms mobile can satisfy itself by *extracting
  the surface Mg upward* rather than moving the bulky anion down (check the z-trajectories). A point-to-plane z-CV
  is numerically unstable (flung the Al through the slab). The *electronic* result (contact→ET) was robust to this;
  the deposition *geometry* was not — flag such caveats, don't paper over.
- **Metal-slab SCF wall:** k-point Mg(0001) slab SCF ~200 s/iter → multi-step barriers (NEB/scans/GEO_OPT)
  impractical on the CPU node; use endpoints/bounds or hand to MLFF. Floppy reductive cleavages are ET-gated
  (no clean saddle) — report ΔG_rxn + the gating, don't force a fake TS.
- **k-points only where it matters:** bonded-Al/deposition configs need k-points (0.13 eV at h=2.0); far/intact
  anion is Γ≈k. Don't k-point everything.
- See also `/home/ls/.claude/.../memory/*.md`: aimd-eps-scf-consistency, mlff-slab-force-fix, metal-slab-scf-wall.

## Open / staged (nothing blocking)
- **Awaiting GPU** to do anything further with the charge-conditioned model (it's resolved; they may extend to
  SEI-growth/ToF-SIMS-depth, a 90-nm confinement reproduction, or denser bias magnitudes).
- **Staged but stopped:** a bare 6–9 Å **outward-pull BOMD** (`codep_aimd/bare_outpull.inp`) to fill the far
  distance tail of the charged-frame set — I cancelled it when the dynamic MD was resolved (frames had no
  consumer). Resume only if the GPU asks for far-distance bias data.
- If a new `al_queue_v3_*.xyz` lands → DFT-label it (slab-masked, OMP=1) and commit back, per the loop.

## Deliverables already in `incoming/` (DFT labels for the GPU)
biased_labeled.xyz (34, q±1) · biased_batch2_labeled.xyz (116, q±1) · charge_ladder_labeled.xyz (110, q=0/−2) ·
bare_codep_* (co-deposition AIMD) · near_mg_*/neutral_reactive_* (T17 AL hardening) · t10_react_* (T10).
Recipe: `computational_v2/mlff/v3/CHARGE_CONDITIONED_MACE_recipe.md`.

**Bottom line:** the v3 interface/EDL story is scientifically complete and triple-confirmed; CPU-side work is all
delivered. Keep the monitor warm, answer any new GPU AL request, and reconcile any T17/SEI result the GPU posts.
