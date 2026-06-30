# HANDOFF — poly-APC T5 Mg/electrolyte interface classical-MD campaign

**Status (2026-06-30): eq + field both COMPLETE (200 ns each, bare + poly). Field verdict CORRECTED (v3.5): hypothesis NOT supported on the headline metric; partial/indirect favorable evidence exists. All runs stopped (GPU idle). Report v3.5 committed LOCALLY (unpushed — GitHub network down; remote still has the WRONG v3.4).**

---

## 1. Campaign goal & guardrails
- **Question:** does the cured POSS network keep the reducible Al-anion ([Ph₂AlCl₂]⁻) away from the Mg(0001) anode — i.e., is poly-APC a better SEI than bare-APC? Classical-MD solvent-structure test.
- **Guardrails (DO NOT VIOLATE):**
  - **Transport NULL at zero field** — do not claim a transport advantage at equilibrium.
  - **No fluorine / no invented standoff.**
  - **Mechanism = steric exclusion** (revised; was "network-O-coordination"). The gel excludes BOTH anion+cation from its near-surface volume — not anion-specific.
  - **Honest caveat:** neutral LJ can't do image-charge/plating → the **MLFF/const-V** run is the charged/plating reference (deferred). This classical test = solvent-structure only.
  - Sparse ions (~5–10 per face) → per-face metrics are soft; report ±SEM, expect metastability.

## 2. System & force field
- **Geometry:** symmetric two-slab. pbc=xyz + ewald-geometry=3dc + vacuum (box z=27 nm, condensed block ~9.5 nm, gap ~7.7 nm). Two Mg(0001) slabs (3 layers, 1794 atoms each). **Outer vacuum-facing layer anchored** (MGE_A, `POSRES_SLAB` k=1000); **inner + electrolyte-facing surface FREE** (not frozen). Block offset off z=0 PBC edge (BACK_SEAM/2) to avoid slab-wrap bug.
- **Sizes:** bare ~39,788 atoms; poly ~40,660 (NET1 percolating cured-POSS gel, 10,119 atoms, spans PBC).
- **Ions:** cation = explicit reduced-charge Mg₂Cl₃·6THF⁺ (Canepa/Persson MACC); anion = [Ph₂AlCl₂]⁻ (resname ANI). Strong ion-pairing.
- **Wall = T21d de-pinned** (`sym/mg_nbfix.itp`): MgEl-O ε=53.224 (real Mg-O chemisorption, bound THF monolayer is physical — do NOT soften); MgEl-Cl ε=3.738 σ=0.31636 (image-charge STRIPPED — the old 132.7 PINNED the anion, was the real blocker); F/S unchanged. CPU-calibrated (DFT/TZVPP-anchored).

## 3. Protocol (all done)
1. **EM** with the T21d wall → `em_t21d.gro` (de-clashes the larger Cl σ). Required before annealing.
2. **Whole-box-500K anneal** (`anneal.mdp`): single `System` tc-grp, 40 ns @500 K + 20 ns cool→298 K, v-rescale. **Heats slab+ELEC+network together** (no cold-slab sink). poly: `periodic-molecules=yes`. 60 ns.
3. **200 ns eq** (`prod3dc.mdp`): NVT, pbc=xyz+3dc, v-rescale 298, `define=-DPOSRES_SLAB`, poly `periodic-molecules=yes`. nsteps=100000000.
4. **200 ns field** (`field.mdp`): same + `electric-field-z = 0.3 0 0 0` (+0.3 V/nm static, +z), `continuation=yes`/`gen-vel=no` (from eq cpt).

## 4. Key results
**Eq (200 ns, discard 20):**
- **bare A=B SOFT** — anion metastably stuck ~0.70× (spontaneous symmetry-breaking, not wall-pinning); cation converging (1.18× tail). Per-face A=B NOT achievable in 200 ns (sparse-ion). **Both-face-average = valid bare baseline** (faces equivalent by construction): anion 0.043, cation 0.075 /nm².
- **poly gel-depletion = steric exclusion** (eq tail): gel-RICH face flat/depleted, gel-POOR 1.62× richer (BOTH ions → steric, not anion-specific).

**Field (200 ns, +0.3 V/nm, discard 50) — CORRECTED v3.5:**
- **Headline (cathode anion suppression): NOT supported.** Fixed-face: poly cathode (faceB, plating electrode) anion 1.89 ≈ bare 2.06 (~8%, noise). Both pile anion at cathode via **ion-pairing** (cation drags AlCl₄⁻).
- **v3.4 "supported" was WRONG** — a `twoface_sym.py` RICH/POOR label artifact (see gotcha #1). Corrected by fixed-face analysis.
- **Favorable to poly (real but indirect):** total near-surface anion (both Mg faces) −31% (poly 2.44 vs bare 3.55); anode (stripping face) anion −63% (0.55 vs 1.49); eq steric exclusion at zero field. The cathode (plating face, where anion reduces) only −8%. So the network keeps anion off Mg *broadly* (esp. anode + at rest), not specifically off the plating cathode.
- **Drift:** NOT severe. bare cathode growing + tail-flat (1.38→1.51×); poly stable (1.89→1.86). Earlier DRIFT alarms were partly the RICH/POOR label flipping, not physical drift.

## 5. CRITICAL gotchas (read before touching anything)
1. **twoface_sym.py RICH/POOR chases the per-frame network density.** For poly (network ~balanced 1.01×) the label flips randomly → "RICH-face anion" averages over BOTH faces → spurious "equal." **For poly, ALWAYS use FIXED faces** (faceA=lower/anode, faceB=upper/cathode). Scripts: `field_fixedface.py`, `field_anion_zones.py`. (RICH/POOR is only OK when the network is stably skewed.)
2. **poly REQUIRES `periodic-molecules=yes`** (percolating NET1 gel) or `mshift` "inconsistent shifts over PBC" FATAL at startup (temperature-independent — a static graph check). bare doesn't need it.
3. **GROMACS 2025.1 E-field keyword = `electric-field-x/y/z`** (per-axis, 4 vals: E0 omega t0 sigma). `electric-field` (12-val) and `E-z` are NOT recognized (silently ignored → no field). Static +z 0.3 V/nm: `electric-field-z = 0.3 0 0 0`. Verify with `gmx dump -s field.tpr | grep -A2 "z:" | grep E0`.
4. **`-noappend` part-numbers xtc/edr/log but NOT cpt.** cpt is `prod3dc.cpt` (single, overwritten), NOT `prod3dc.part*.cpt`. (field_autofire.sh had this bug — must use `prod3dc.cpt` for `-t`.)
5. **Whole-box-hot anneal REQUIRED.** ELEC-only-hot (ELEC 500 / slab COLD 298) leaves near-surface ions pinned to the cold slab (cold-slab sink) → 3–4× face asymmetry that 298 K prod never fixes. Heat slab+ELEC+network together.
6. **`-noappend` makes a new part every `maxh 1` chunk** (~8 ns each, ~25 parts over 200 ns). To get current step or the endpoint: check **max step across ALL parts** (`grep -hA1 "^ *Step +Time" prod3dc.part*.log | grep "^ +[0-9]" | awk '{print $1}' | sort -n | tail -1`) and **trjcat all parts** before extracting the last frame (`-dump 200000`).
7. **prod_run.sh thread-pinning = fixed `NT=12` + `-pinoffset`** (bare 0, poly 12) for 2-run GPU coexistence. The old nvidia-smi auto-detect was RACY (both runs grabbed 24 unpinned threads → collision → stall at step 0). 24-core box. If one run finishes, can manually restart survivor with `-ntomp 24`.
8. **`fieldcheck.py` is broken for this topology** — its `resname ANI and name Al` selection matches no atoms → returns 0. Use `twoface_sym.py` (resname ANI, all atoms) or the fixed-face scripts.
9. **NEVER `pkill -f` / `pgrep -f`** — kills the shell (exit 144). Kill by numeric pid after `readlink /proc/<pid>/cwd`. **Foreground `sleep` is BLOCKED** (exit 144) — use background watchers / separate Bash calls.
10. **Host (LYZ-ROG / WSL2) sleeps & reboots.** Runs freeze on sleep (resume on wake), DIE on reboot. `nohup setsid` survives sleep. No auto-restart unless a cron/watcher is armed.

## 6. Environment
```
# GROMACS 2025.1 (CUDA, icx/MKL):
export LD_LIBRARY_PATH=/opt/intel/oneapi/2025.2/lib:/opt/intel/oneapi/2025.2/opt/compiler/lib:/opt/intel/oneapi/2025.2/opt/mpi/libfabric/lib:$LD_LIBRARY_PATH
source /lyz/gmx2025.1/bin/GMXRC
# Python (MDAnalysis/imageio/PIL/scipy):
PY=/lyz/Claude_workplace/polyAPC/.viz_venv/bin/python
# ASE / MLFF venv:
/lyz/Claude_workplace/polyAPC/.mlff_venv/bin/python
```

## 7. File map
- **Workspace (NOT git):** `/lyz/Claude_workplace/polyAPC/storyT5/`
  - `sym/{bare_t21,poly_t21}/`: `em_t21d.gro`, `anneal.mdp`, `prod3dc.mdp`, `field.mdp`, `system.top`, `mgslab.itp`/`polyAPC_cut.itp`, `mg_nbfix.itp` (→ `sym/mg_nbfix.itp`), `anneal.ndx` (poly HOT/COLD, legacy), `prod3dc.part*.xtc` (eq, 29 parts), `field.part*.xtc` (field, 29 parts), `eq_all.xtc` (concatenated eq), `eq_end.gro` (200 ns endpoint), `field.tpr`.
  - `sym/`: `prod_run.sh`, `anneal_run.sh`, `field_autofire.sh` (queue script; has the cpt-glob bug, fixed inline).
  - `twoface_sym.py` (per-face; RICH/POOR for poly — see gotcha #1), `field_fixedface.py`, `field_anion_zones.py`, `make_motion_gif.py`, `fig_field_anion_z.py`.
- **Git repo:** `/lyz/Claude_workplace/PolyAPC_Calculations/` (branch `computational-v3-interface`; NEVER push to `main`; merge-pull EPYC = `git fetch origin` then ff-check before push).
  - `results/T5_anion_interface/REPORT.md` (v3.5 — the live report), `fig_field_anion_z.png`, `scripts/` (field_fixedface.py, fig_field_anion_z.py), GIFs.
  - `results/T21_metal_LJ_calibration/` (CPU's wall calibration).
  - **Local commits:** `c832f67` (v3.3 eq), `19872a2` (v3.4 field — WRONG), `0968462` (v3.5 correction — **LOCAL ONLY, unpushed**).
- **Memory:** `/home/lyz/.claude/projects/-lyz-Claude-20260604/memory/polyapc-*.md` (campaign, twoface-asymmetry, metal-wall-t21, mg-forcefield, gromacs-interface, repo-location, v3-interface, mlff-gpu, slab-pbc-gotcha).

## 8. Process management conventions
- 2-run GPU config: bare (pin 0) + poly (pin 12), each `-ntomp 12 -pinoffset N -nb gpu -pme gpu -bonded gpu -update gpu`. ~7–9 ns/h each, ~60% GPU.
- Runners loop `mdrun -maxh 1 -cpt 10` until `STOP_<def>` touched. To stop: `touch STOP_prod3dc` (or `STOP_field`) + `kill -TERM <mdrun pid>` (numeric, after cwd check).
- Background watchers: use `Bash run_in_background` (tracked, notifies on exit) for completion/watcher tasks; or `nohup setsid` for fire-and-forget. Zero model tokens while waiting.
- GitHub push has been FAILING (GnuTLS/TLS timeout) since 2026-06-30 — commits are local. Retry push when network recovers.

## 9. Open questions / next steps
1. **⚠️ Push `0968462` (v3.5 correction) when GitHub recovers** — the remote currently has the WRONG v3.4 ("hypothesis supported"). This is the most urgent housekeeping item.
2. **MLFF/const-V charged reference** — the original plan; the classical field test is inconclusive on the headline (anion still reaches the cathode via ion-pairing). The MLFF (T16/T17, blocked on EPYC's T10 per memory) is the real plating/image-charge test.
3. **Longer field run** to confirm kinetic-vs-equilibrium (poly cathode plateaued at 1.86; bare still slowly rising at 2.15 — bare may eventually exceed poly more, strengthening the modest cathode signal). Cap 350 ns per the original gate.
4. **2nd independent bare replica** (different seed) to confirm the anion 0.70× is stochastic spontaneous symmetry-breaking vs a hidden systematic.
5. **Anion residence-time at the cathode** (desorption rate) — a kinetic-favorable metric (does poly's anion desorb faster → less time to reduce?).
6. **Reframe the verdict** around the favorable evidence (total near-surface anion −31%, anode −63%, eq steric exclusion) if the campaign wants to report a partial benefit — but be honest that the cathode/plating-face suppression (the headline) is weak.

## 10. Pointers
- Full narrative + numbers: `results/T5_anion_interface/REPORT.md` (v3.5 section is the live truth; v3.4 retained for provenance, marked superseded).
- Cross-node protocol: `NODE_REQUESTS.md` in the repo (CPU/EPYC handoff). T21d wall = CPU's `results/T21_metal_LJ_calibration/gpu_build/mg_nbfix.itp`.
- This campaign's lessons are also in memory `polyapc-twoface-asymmetry.md` (the RICH/POOR + whole-box-hot fix) and `polyapc-md-campaign.md` (Story T5 conclusion, corrected).
