# Agent Handoff — poly-APC classical-MD results (Stories A.1 / A.2 / A.4 / B / C)

**For:** Claude agents who will *use, extend, or integrate* these classical-MD results
(downstream analysis, wet-lab/DFT integration, paper-writing, or continuing the campaign).
**Campaign status:** complete 2026-06-11. A.3 (deconfound) deliberately skipped — optional refinement, not essential.
**➜ LATEST (2026-06-11 review round):** see `AGENT_HANDOFF_2026-06_review.md` + `reports/REVIEW_2026-06_MD_reexamination.md`
— QC audit, 2-D/3-D descriptor heat-maps, charge-robustness re-sim (Story E done), and next stories (D/F/H/G).
**Repo / branch:** `FrankLiu000/PolyAPC_Calculations`, branch **`computational-v2-package`**
(NB: "computational-v2-package" is a *branch*, not a separate repo). Read this whole file before running anything.

---

## 0. TL;DR — the one result to cite

A cured **glycidyl-POSS / poly(THF) network** raises the ionic conductivity of the APC Mg electrolyte
(cation **[Mg₂(μ-Cl)₃·6THF]⁺**, anion **[Ph₂AlCl₂]⁻**, THF) by **de-pairing ions** — converting contact
ion pairs (CIP) to free, solvent-separated carriers (SSIP) — **not** by speeding ion motion. The extra
free carriers (×3.4) raise σ even though mobility *drops* ~1.6×; net **σ_swollen/σ_bare ≈ 2×**. Ions stay
mobile because they travel in **abundant, percolating, swollen THF channels that are decoupled from the
viscous polymer matrix** (the gel is ~7.4× more viscous than bare, yet D drops only ~2× → fractional
Stokes–Einstein). This one mechanism is corroborated independently across **speciation, transport,
spectroscopy, and morphology**, and reproduces the wet-lab σ_poly>σ_bare + dendrite-free deposition.

**It also corrected the prior campaign:** the earlier "swollen mobility preserved at ~98% of bare" was an
under-sampling artifact (2×50 ns), and ion-pairing equilibrates *slowly* (tens of ns), which had made the
old contact-pairing numbers inconsistent.

> All MD numbers are **effective / trend-level** (non-polarizable OPLS-AA; Mg/Cl **scaled charges**;
> short-range-only energies). Use them for trends and mechanism, not as ab-initio magnitudes.

---

## 1. Where everything lives

| what | path |
|---|---|
| The plan (stories A/B/C) | `classical_molecular_dynamics/PLAN_classical_MD_stories.md` |
| Per-story narratives | `…/handoff_for_agent/reports/REPORT_story{A1,A2,A4,B,C}.md` |
| Transport numbers (D, σ, ionicity, η, Eₐ) | `…/handoff_for_agent/transport/RESULTS_story{A1,A1_converged,A2,arrhenius,walden}.txt` |
| Speciation / Raman populations / residence | `…/handoff_for_agent/solvation/RESULTS_{speciation_ssip_cip_agg,residence_time,storyB}.txt`, `storyA1_contact_pairing_drift.txt` |
| Mechanics / morphology | `…/handoff_for_agent/mechanics/RESULTS_storyC.txt` |
| Reusable analysis scripts | `…/handoff_for_agent/scripts/` |
| Original campaign manifest | `…/handoff_for_agent/MANIFEST.md` (4 base systems, FF, prior results) |
| Raman band data | `Raman/peak_assignments.csv` |
| **Compute box (LYZ-ROG)** | `/lyz/Claude_workplace/polyAPC/` — trajectories, run scripts, mdp, the 4 systems |
| **Local git clone** | `/lyz/Claude_workplace/PolyAPC_Calculations/` (this branch) |

**Trajectories are NOT in git** (too large, gitignored). They live on LYZ-ROG under `prod/` and are
regenerable via the committed run scripts. Only small analysis outputs + reports are committed.

---

## 2. Results by stage (numbers you can use)

**A.1 — transport & de-pairing** (`6b303e8`). swollen-8 + bare, 5×100 ns each, NVT 298 K.
D_bare 0.053, D_swollen 0.033 (×10⁻⁵ cm²/s) → **swollen ÷1.6**; t₊≈0.50 both. Converged free-carrier
**f = 0.046 (bare) / 0.155 (swollen)**; speciation **CIP→SSIP +10.9 pts**, negligible AGG. Ion-pair
residence **τ_c > 25 ns (frozen)** → σ gain is carrier-number, not exchange-rate. **σ∝f·D ≈ 2.1 ± 0.3**.

**A.2 — large-cell σ_coll + viscosity** (`8e0e9f1`). 2×2×2 tiled swollen cell (303k atoms, 200 ns).
**σ_coll 0.012 ± 0.004 S/m; ionicity σ_coll/σ_NE = 0.228** (~2× bare ~0.10) → corroborates de-pairing.
Viscosity **bare 1.4 / swollen 10.4 cP (×7.4)**; **strong Stokes–Einstein decoupling** (D∝η^−0.3…−0.5).
Walden ionicity swollen 0.115 ≫ bare 0.008 (trend-level).

**A.4 — Arrhenius** (`d6d6549`). 5 T (273–333 K). **Eₐ bare 21.4 / swollen 14.8 kJ/mol** (0.22/0.15 eV).
Swollen bulk migration barrier **not elevated** → the high experimental poly DRT R_ct is
carrier-number / interfacial-desolvation limited, **not** a higher bulk-migration barrier.

**B — Raman ↔ MD population** (`c90a14e`). Across the 4 base systems, the three speciation bands are each
tracked monotonically by the matching MD population (correct direction): 999/1002 ↔ free-anion 0.05→0.39;
181 ↔ dissociated 0.36→0.47; 276 ↔ bridged [Mg₂Cl₃] 0.64→0.53. 1483 (THF stiffening) ↔ Mg–O first-shell
**sharper** (peak g 67→109, CN flat ~3). 915 cm⁻¹ behaves as a null.

**C — mechanics / morphology** (`b424d0b`). Free-THF phase **percolates in ALL systems** (pinch-off
refuted); the differentiator is **swelling** (8-swollen 5.14 vs 16-dense 3.06 free-THF/nm³). Static moduli
not reliably obtainable here (see gotchas); the usable mechanical property is the A.2 viscosity.

---

## 3. How to USE / extend these results

- **Just need numbers?** Read `transport/`, `solvation/`, `mechanics/` `RESULTS_*.txt` (machine-readable) and
  the `reports/REPORT_*.md` (narrative + caveats). Don't re-derive — they're final.
- **Re-run / extend on LYZ-ROG:** the run scripts are `prod/{run_storyA1.sh, large_swollen8/run_storyA2.sh,
  viscosity/run_viscosity_walden.sh, arrhenius/run_arrhenius.sh}`; analysis scripts under `scripts/`
  (`agg_*`, `solvation.py`, `speciation_ssip_cip_agg.py`, `residence_time.py`, `raman_populations.py`,
  `network_morphology.py`, `arrhenius_fit.py`, `walden.py`, `contact_timeseries.py`). They're idempotent /
  resumable and self-configure the environment.
- **The 4 base systems** (structures in `handoff_for_agent/structures/`): `00_bareAPC`, `01_polyAPC_4POSS_gel`,
  `02_polyAPC_8POSS_swollen`, `03_polyAPC_16POSS_dense`. On LYZ-ROG: `prod/bare`, **`prod/poly` = the 4-POSS
  gel (NOT swollen-8)**, `prod/swollen8`, and the 16-dense trajectory is `poss16/prod.xtc` (50 ns).
- **Commit convention:** small outputs + reports only; mirror the `handoff_for_agent/{reports,transport,
  solvation,mechanics,scripts}/` layout; trajectories stay gitignored.

---

## 4. Conventions & GOTCHAS (read before running anything)

1. **GROMACS env (will bite you):** `gmx` 2025.1 (`/lyz/gmx2025.1`) is **icx/MKL-built** → it needs the
   Intel oneAPI runtime or it dies instantly with `error while loading shared libraries: libimf.so`.
   `.bashrc`'s `oneapi-vars.sh` line is **commented out**, and cron/systemd give a bare env. Always:
   `export LD_LIBRARY_PATH=/opt/intel/oneapi/2025.2/lib:/opt/intel/oneapi/2025.2/opt/compiler/lib:$LD_LIBRARY_PATH`
   then `source /lyz/gmx2025.1/bin/GMXRC`, and gate with a `gmx --version` check before any long run.
2. **Ion-pairing equilibrates slowly** (~tens of ns; bare ~80 ns, swollen ~40 ns to plateau). Use **≥50 ns
   pre-eq**, and read contact-pairing / f from the **converged window only** (e.g. 70–100 ns). A 20–80 ns
   MSD-fit window overlaps the drift for short-pre-eq runs (mild D overestimate).
3. **WSL restart kills `--user` services** (`Linger=no`) — and a full WSL shutdown kills everything. For
   long unattended runs, drive them with a **cron watchdog** (see `prod/arrhenius/watchdog.sh`: cron survives
   restarts and re-launches the flock-guarded, resumable run script; self-removes on DONE; skips on FAILED),
   and checkpoint often (`-cpt 10`). Keep WSL alive for the campaign duration.
4. **Run convention:** production = **NVT @ 298 K** (2 fs, PME, h-bond constraints, v-rescale) from
   NPT-pre-equilibrated coords — matches the committed campaign so σ/D stay comparable. Two small systems
   run **2-up on the one GPU**: `-ntmpi 1 -ntomp 12 -nb gpu -pme gpu -bonded gpu -update gpu -pin on
   -pinoffset 0|12`. One big system: `-ntomp 24`.
5. **`gmx current` (σ_coll):** select the **System** group (group 0, **NO `-n` index**), `-nojump`, parse
   stdout `sigma=…` (S/m). Collective σ is **intrinsically very noisy** → block-average and report the
   **ionicity ratio (σ_coll/σ_NE)**, never a bare magnitude.
6. **`gmx energy -vis` (viscosity):** **prompts for the box volume** on NVT edrs (pipe it in). Units differ:
   `-vis` (Green–Kubo) is in **cP**; `-evisco` (Einstein) is in **Pa·s** (kg m⁻¹ s⁻¹). In `visco.xvg`
   col1=Shear, col2=Bulk; in `evisco.xvg` col4 = averaged shear. (This caused a unit bug — now fixed in `walden.py`.)
7. **Scaled charges:** Mg +1.2, bridging Cl −0.467; APC cation/anion are *bonded complexes* (no inner THF/Cl
   exchange). The bare topology carries a harmless **−0.008 e** net-charge residual → grompp with `-maxwarn 8`.
8. **Don't compute moduli from c-rescale NPT volume fluctuations** — the barostat damps fluctuations ~75× →
   unphysical K (thousands of GPa). A real G/K needs Parrinello–Rahman or finite-strain runs.

---

## 5. Solid vs. trend-level (don't over-claim)

- **Solid / directional:** D, t₊; the de-pairing trend (CIP→SSIP, f bare<swollen<dense); ionicity ~2× bare;
  viscosity ratio ×7.4 and the SE-decoupling; the Raman↔population *directions*; free-THF percolation.
- **Trend-level / soft:** absolute σ_coll magnitude (noisy); swollen Eₐ (R²=0.84, noisy D(T)); absolute
  Walden ionicity (aqueous-KCl ref + 20 ns σ_coll); σ(T) Arrhenius (too noisy — use D(T)); free-anion is a
  per-Mg proxy. **Do not use** the volume-fluctuation moduli.

## 6. Open follow-ups (optional, none blocking)
- A **matched bare large-cell σ_coll** would make the ionicity comparison fully apples-to-apples.
- A reliable **shear/bulk modulus** needs dedicated Parrinello–Rahman / finite-strain deformation runs.
- A **finer channel-width / tortuosity** metric (the 0.70 nm percolation cutoff reads all systems as continuous).
- **A.3 deconfound matrix** (build 4-POSS@100% vs 69%, matched-conversion 4/8/16, swollen-vs-dense) if a
  paper needs the loading-vs-conversion deconvolution — ~1–2 weeks; build via `scripts/cure.py`/`cure_full.py`.

## 7. Boundary with the DFT/AIMD workstream (`computational_v2/`)
Classical MD owns **structure / transport / speciation / ion-pairing / morphology** (non-reactive). **Out of
scope → DFT/AIMD (Gaussian/CP2K), already in `computational_v2/`:** Al redox & 2p XPS, MgF₂/SEI formation,
bond-breaking / electron transfer, constant-potential electrode & interfacial-desolvation PMF, and the actual
**Raman frequency shifts** (`computational_v2/P3_raman/`). When the experimental DRT R_ct is high but the MD
bulk migration barrier is low (Story A.4), the difference is interfacial desolvation — a DFT question, not MD.
