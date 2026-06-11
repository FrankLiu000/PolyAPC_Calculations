# Agent Handoff — review round (QC + heatmaps + new stories), 2026-06-11

**For:** the next Claude agent continuing the poly-APC classical-MD campaign.
**Read first:** the original `AGENT_HANDOFF.md` (campaign A.1/A.2/A.4/B/C) and the new
`reports/REVIEW_2026-06_MD_reexamination.md` (this round). This file tells you *what changed,
what is safe to reuse, and exactly what to do next*.
**Repo/branch:** `FrankLiu000/PolyAPC_Calculations`, branch **`computational-v2-package`**
(it is a *branch*, not a separate repo). This round = commit **c8925c3** (report + figs).

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
| `fig_*.py` | the 7 figures |
| `analyze_q15.py` | Story-E CIP comparison (+1.2 vs +1.5); `finalize_storyE.sh` ran it at 40 ns |

Reproduce a figure: `polyAPC/.viz_venv/bin/python analysis/review2026/fig_solv_pmf.py` (etc.).

---

## 3. Next stories — priority order, with concrete starting points

### ★ Story D — true (Onsager/correlated) transference  **[do first; analysis-only, no new sims]**
**Why:** the campaign's t₊≈0.5 used Nernst–Einstein D₊/(D₊+D₋), which **overestimates** transference by
ignoring ion–ion correlations (eNMR shows Mg²⁺ t₊≈0.22; correlations can even give negative t₊). Tests
whether "de-pairing → σ" is genuine charge separation or correlated/vehicular co-motion.
**How:** on `prod/large_swollen8/prod.xtc` (200 ns, proper 50-ns pre-eq) and the bare replicates, compute the
distinct (cross) diffusion terms ⟨Δrᵢ·Δrⱼ⟩ for ++/−−/+− (group COMs = MgCluster, Anion) and assemble the
Onsager L matrix; report t₊^corr and ionicity vs the NE value. The σ_coll/`gmx current` Einstein–Helfand
machinery from Story A.2 gives the diagonal; you add the cross terms (custom MDAnalysis script or
`gmx msd -mol` on group-COM trajectories). Expected: t₊^corr < 0.5.

### Story F — matched-connectivity scan  **[high value; needs new builds + runs]**
**Why:** deconfound POSS loading from network percolation (§0.3). Build tooling: `polyAPC/{cure,poss8,
poss16,build}/`. Build 4/8/16-POSS as **single percolating networks** (and a swollen-vs-dense matched-free-THF
pair); EM → **≥50 ns NPT** → 100 ns NVT (298 K, v-rescale, match `prod.tpr` settings); read CIP, D, t₊,
Mg–polymer-O. Hypothesis: at fixed connectivity, de-pairing collapses onto one curve vs loading×conversion,
while transport tracks percolation/tortuosity.

### Story H — bimodal CIP geometry  **[analysis-only]**
The new CDF/SDF (Fig 2b/3) show two contact modes: **equatorial bridging** (r≈0.2 nm, cosθ≈0) and **axial
end-on** (cosθ≈±1). Extend `extract_sdf.py` to classify each pair per frame and test whether the latent-ligand
polymer-O preferentially displaces the *axial* anion first (open coordination face) as loading rises.

### Story G — monomer vs dimer  **[NOT classical-MD → DFT/AIMD handoff]**
The FF hard-codes the dinuclear dimer as a bonded complex; Canepa/Persson (EES 2015) argue the **MgCl⁺
monomer** is the equilibrium-stable cation in THF. Classical MD *cannot* address this. Route to the
`computational_v2/` DFT/AIMD program: does swelling shift the monomer↔dimer balance / which carrier is mobilized?

---

## 4. Pitfalls / do-not-repeat
- Don't recompute the headline de-pairing result — it's solid and now charge-robust (§0.5).
- Don't trust c-rescale volume-fluctuation moduli (Story C caveat) — use Parrinello–Rahman or finite-strain.
- Don't take f/CIP from <50 ns or from a sub-window of the slow ion-pairing transient.
- Don't read absolute energies/kinetics as ab-initio — scaled-charge OPLS, short-range-only decomposition.
- Always state the 8-POSS connectivity caveat when comparing transport/mechanics across loading.
