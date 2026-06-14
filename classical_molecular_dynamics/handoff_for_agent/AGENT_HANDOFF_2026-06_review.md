# Agent Handoff — review round (QC + heatmaps + new stories), 2026-06-11 (updated 2026-06-14: D/E/F/H DONE)

**For:** the next Claude agent continuing the poly-APC classical-MD campaign.
**Read first:** the original `AGENT_HANDOFF.md` (campaign A.1/A.2/A.4/B/C) and the new
`reports/REVIEW_2026-06_MD_reexamination.md` (this round). This file tells you *what changed,
what is safe to reuse, and exactly what to do next*.
**Repo/branch:** `FrankLiu000/PolyAPC_Calculations`, branch **`computational-v2-package`**
(it is a *branch*, not a separate repo). Commits: **c8925c3** (QC+heatmaps+proposals, Parts 0–V),
**a05961d** (this handoff), **b6461c2** (Story D/H/F results, Parts VI–VIII). All pushed.
**STATUS: the classical-MD review campaign is COMPLETE** — Stories D, E, F, H all done (see §3);
only G (monomer/dimer) remains and it is a DFT/AIMD handoff, not classical MD.

---

## 0. What this round established (don't redo these)

1. **QC verdict: the campaign set-up is sound.** Box (MIC ok), OPLS-AA (cluster net +1 verified),
   v-rescale thermostat (T=298.0±0.005 K), c-rescale NPT pre-eq, intact [Mg₂Cl₃·6THF]⁺ core
   (Mg–μCl 0.251±0.002 nm/100 ns), COM drift 0.66 Å. Energies stable. **No emergency rebuild needed.**
2. **"Polymer runs out of the box" is a NON-issue** — it is the PBC rendering of a *correctly
   percolating* crosslinked network (211–314 of NET1's bonds cross the periodic boundary; the network
   spans the cell by design). It is not an error. **Always visualize with `gmx trjconv -pbc atom -ur
   compact`; NEVER `-pbc mol`/`-pbc nojump` on NET1** or it looks exploded.
3. **NEW confound (act on this):** polymer connectivity is **not matched across systems**. Largest NET1
   fragment: 4-POSS **10 119** atoms (percolates), 16-POSS **14 678** (percolates), **8-POSS "swollen"
   only 2 530** (fragmented — a solution, not a gel). So loading is confounded with network topology;
   this likely inflates the 8-POSS "swollen mobility advantage." → **Story F.**
4. **Mechanistic refinement:** de-pairing is a **population shift at conserved pair-bond strength** (the
   Mg–anion PMF well is ~−11 kJ/mol across all loadings; only the contact *population* CN drops 0.95→0.58).
   Competition from latent-ligand oxygens, not a weaker bond. The coordination paradox is now a 2-D FES.
5. **Story E done (charge robustness):** at ECC-canonical **Mg +1.5** the de-pairing gap bare−swollen is
   **8.1 pts** vs **10.4 pts** at +1.2 → conclusion **robust to the Mg charge** (magnitude moderately
   charge-sensitive). Raw: `analysis/review2026/RESULTS_storyE.txt`; runs in `prod/charge15/` (40 ns, done).
6. **Pre-eq caveat reconfirmed:** the original 1-ns NPT pre-eq is too short (bare density still climbing);
   ion-pairing needs tens of ns. **Any new run must use ≥50 ns NPT pre-eq.**

Figures (committed, gitignored so force-added): `reports/figs_review2026/fig1–fig7*.png`.

---

## 1. Environment & gotchas (LYZ-ROG, this WSL box)

- **GROMACS 2025.1** at `/lyz/gmx2025.1` (CUDA, single RTX 4070 Ti SUPER 16 GB, 24 CPU). Two `mdrun`
  fit on the GPU concurrently (`-pinoffset 0|12`, ~150–180 ns/day each when paired).
- **oneAPI libs MUST be on `LD_LIBRARY_PATH` for any detached/cron job** or `gmx` dies with
  `libimf.so` missing. Use `/tmp/gmxenv.sh` pattern or prepend
  `/opt/intel/oneapi/2025.2/lib:/opt/intel/oneapi/2025.2/opt/compiler/lib:...` then `source GMXRC`.
- **Python plotting env: `polyAPC/.viz_venv`** (numpy, scipy, matplotlib, **MDAnalysis 2.10**, **skimage**).
  The system `python3` has NO pip — this venv was bootstrapped via get-pip.py. **Reuse it**, don't rebuild.
  `MDAnalysis.Universe(tpr, xtc)` reads the topology+trajectory directly; selections by `type opls_*`.
- **The repo `.gitignore` blanket-ignores `*.png`** (line 43). Commit figures with `git add -f`.
- **energygrps decomposition must run with `-nb cpu`** (GPU nonbonded can't decompose) — handy: it won't
  contend with GPU production runs. Example in `analysis/review2026/rerun_8poss_ene.sh`.
- Key index/selection facts: cluster = `resname MGC` (Mg = `type opls_MG`, bridging Cl = `opls_CLB`);
  anion-Cl = `resname ANI and type opls_CLA`; **solvent THF-O = `resname THF and type opls_OS`** (the inner
  6 THF are *bonded inside MGC*, not in `resname THF`); polymer-O = `resname NET1 and type opls_OS/OH/OE/OB`.

---

## 2. Where the review-round code lives

`polyAPC/analysis/review2026/` (local; not in repo):
| file | what |
|---|---|
| `descriptors.py` | per-Mg shell counts + g(r) → `desc_{sys}.npz` (de-pairing/PMF/fingerprint inputs) |
| `extract_sdf.py` | cluster-frame 3-D SDF + radial-angular CDF → `sdf_{sys}.npz` |
| `integrity.py` | structural-integrity QC (percolation/PBC/Rg/core) |
| `fig_*.py` | the heat-map figures (fig1–7) |
| `analyze_q15.py` | Story-E CIP comparison (+1.2 vs +1.5); `prod/charge15/` |
| `compute_storyD.py` | Story D — correlated/Onsager transference (`--out`, system filter; unwrap-before-COM) |
| `compute_storyH.py` | Story H — axial-vs-equatorial CIP classification |
| `compute_storyF.py` | Story F — matched-set CIP/D/t₊/Mg-polyO; reads `storyF/{4,8,16}poss/prod.*` |
| `storyF/run_storyF.sh` | Story F build+sim driver (cure_full → 50 ns NPT → 100 ns NVT, sequential) |

Reproduce a figure: `polyAPC/.viz_venv/bin/python analysis/review2026/fig_solv_pmf.py` (etc.).
13 figures total in `figs_review2026/` (fig1–7 + fig_storyD/H/F).

---

## 3. Stories — DONE this round (results in report Parts VI–VIII), + the one remainder

### ✅ Story D — true (Onsager/correlated) transference  **[DONE; report Part VI; `compute_storyD.py`]**
RESULT: **the transference is ill-posed for this electrolyte.** t₊^NE ≈ 0.49(bare)/0.47(swollen) reproduces
the campaign, but ionicity σ_coll/σ_NE ≪ 1 (bare ~0.10, swollen ~0.23 from A.2's validated gmx-current) →
cations+anions co-move as neutral pairs, net charge-MSD ≈ 0, so species-resolved t₊^corr is a 0/0
ill-conditioned ratio. NE t₊≈0.5 vastly overstates independent Mg²⁺ transport = quantitative coordination
paradox. **Bug fixed:** must `unwrap(compound='fragments')` before residue COM or self-diffusion is corrupted.
**Large-cell 640-ion cross-check ABANDONED — reading the 24 GB `large_swollen8` xtc with MDAnalysis OOM-crashes
the machine** (see §4). Conclusion rests on bare + 8-POSS-swollen (5 reps each).

### ✅ Story E — charge-scaling robustness (Mg +1.2 vs ECC +1.5)  **[DONE; `prod/charge15/`, fig7]**
de-pairing gap bare−swollen 10.4→8.1 pts → conclusion robust to the Mg charge.

### ✅ Story F — matched-connectivity scan  **[DONE; report Part VIII; `storyF/`, `compute_storyF.py`]**
Rebuilt 4/8/16-POSS as matched single percolating networks (`cure_full.py` budgets 225/450/900, 100% conv,
50 ns NPT pre-eq → 100 ns NVT; all POSS-comps=1, percolate). RESULTS: (1) de-pairing is **real/loading-driven**
— CIP 90.6→85.3→71.5 % at fixed connectivity (validates the campaign); (2) but the **magnitude was inflated**
by the confound (matched 16-POSS 71.5 % vs original 57.4 %); (3) the original **8-POSS "swollen mobility
advantage" was a TOPOLOGY artifact** — matched D falls monotonically 0.026→0.011→0.003, removing the 8-POSS
speed anomaly. Caveat: single replicate/system; self-MSD window-sensitive.

### ✅ Story H — bimodal CIP geometry  **[DONE; report Part VII; `compute_storyH.py`]**
Mg–anion contact is ~88–92 % **axial** (end-on at the open Mg face), not equatorial. Clusters bearing a
polymer-O contact carry 1.6–3.3× fewer axial anion contacts → the latent-ligand O blocks the axial face
(Story-3 mechanism localized).

### ⬜ Story G — monomer vs dimer  **[REMAINING — NOT classical-MD → DFT/AIMD handoff]**
The FF hard-codes the dinuclear dimer as a bonded complex; Canepa/Persson (EES 2015) argue the **MgCl⁺
monomer** is the equilibrium-stable cation in THF. Classical MD *cannot* address this. Route to the
`computational_v2/` DFT/AIMD program: does swelling shift the monomer↔dimer balance / which carrier is mobilized?
This is the **only** open item from the review round.

---

## 4. Pitfalls / do-not-repeat
- **⚠ NEVER load the `large_swollen8` 24 GB trajectory into MDAnalysis — it exhausts the 29 GB RAM and
  HARD-CRASHES/REBOOTS the machine** (happened 2026-06-14; killed every large-cell attempt). Use `gmx`
  streaming tools (trjconv/msd/current) for that cell only. Small systems (~38k atoms, ~1.5 GB) read fine.
- **⚠ Never chain background jobs with `while pgrep -f <name>`** — the waiter's own command line matches the
  pattern → infinite self-wait (created two zombie loops). Use sequential commands in one script, or marker files.
- When reading trajectories with MDAnalysis, you MUST `unwrap(compound='fragments')` before residue COM
  (else PBC-split molecules corrupt COM/self-diffusion — this was the Story-D bug). Wrap MDAnalysis reads in
  `( ulimit -v 6000000; … )` as an OOM backstop (but NOT gmx — CUDA needs the virtual address space).
- Don't recompute the headline de-pairing result — solid, charge-robust (§0.5), and loading-driven (Story F).
- Don't trust c-rescale volume-fluctuation moduli (Story C caveat) — use Parrinello–Rahman or finite-strain.
- Don't take f/CIP from <50 ns or from a sub-window of the slow ion-pairing transient.
- Don't read absolute energies/kinetics as ab-initio — scaled-charge OPLS, short-range-only decomposition.
- Report the **deconfounded** loading trends (Story F), and note the original 8-POSS swollen mobility was a
  topology artifact, when comparing transport/mechanics across loading.
