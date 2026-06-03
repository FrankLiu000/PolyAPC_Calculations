# poly-APC v2 — Aluminium / SEI / Spectroscopy computational campaign (G16 + CP2K + Multiwfn under SLURM)

## Context

`HANDOFF_computational_v2_Al_and_wetlab.md` asks the next agent to re-derive the poly-APC mechanism so it explains **all** wet-lab data, not just transport. The prior study (transport-not-the-win; gel confines/immobilises) is broadly right but has a central chemistry gap: it treated the APC anion **only** as a static `[AlPh₂Cl₂]⁻` spectator and computed **only its oxidation** (IP 6.18 eV). It never addressed (a) APC **anion speciation** (Schlenk Ph/Cl redistribution), (b) **anion/Al reduction** and reductive decomposition, (c) **Al co-deposition / Mg–Al alloying**, (d) the triflate→**MgF₂ SEI**, or (e) a **real-ion, field-coupled interface**. The headline wet-lab clue is the **3.1 eV Al 2p XPS split** (bare 70.88 eV ≈ reduced/Mg–Al-alloyed Al; poly 73.98 eV ≈ oxidised Al³⁺), which the existing calculations cannot explain.

**Goal:** run a comprehensive Gaussian 16 (isolated/SMD molecular DFT) + CP2K (periodic DFT and AIMD on bulk and interfacial configurations) + Multiwfn campaign under SLURM that builds the missing Al/redox/SEI chemistry and reconciles it with every observable, producing data, a v2 report, and publication figures.

**User decisions (locked):** (1) **Full** program, Phases 1–4. (2) **Bare APC is classic, F-free** → model the MgF₂/triflate SEI as **poly-specific**; treat bare's ~4.3 % F as a contamination/handling artifact and flag it; flag the **missing S 2p scan**. (3) Interface electron transfer done **both** ways — CDFT/Marcus **and** Dirichlet-BC fixed-potential charged slab — and cross-compared. (4) **Full deliverables:** machine-readable data + structures, `REPORT_polyAPC_v2_master.md`, publication figures, and a reconciliation table.

## Environment & reusable assets (verified)

- **One SLURM node**, partition `CPU` (default, walltime unlimited, queue empty): AMD EPYC 9654, **96 physical cores / 192 threads, 377 GB RAM, no GPU**. Disk `/` 1.7 TB free; G16 scratch `/mnt/scratch_disk` 1.7 TB free.
- **Gaussian 16** `/CH/g16/g16` (profile `/CH/g16/bsd/g16.profile`, `formchk`, `GAUSS_SCRDIR=/mnt/scratch_disk/g16_scratch/...`). **CP2K 2025.1** `/CH/cp2k-2025.1/exe/local/cp2k.psmp` (libxc, ELPA, **CDFT/BECKE_CONSTRAINT, SCCS, Poisson MIXED_PERIODIC + DIRICHLET_BC/AA_PLANAR, BAND/NEB, libvori Bader — all present; no turnkey ESM**). **Multiwfn** `/CH/Multiwfn_3.8_dev_bin_Linux_noGUI/Multiwfn_noGUI` (`settings.ini` already wired to g16/orca). **ORCA 6.1.0** bonus for range-separated cross-checks. OpenMPI 5.0.6 toolchain.
- **CP2K data** `/CH/cp2k-2025.1/data/`: GTH-PBE potentials + DZVP-MOLOPT-SR-GTH (and `BASIS_MOLOPT_UZH` DZVP-MOLOPT-{PBE,PBE0,SCAN}-GTH) confirmed for Al/Cl/F/Mg/S/Si/C/O/H.
- **System Python is 3.6 + numpy/scipy only** (no ASE/pymatgen/conda). Network works → install user-space Miniconda + ASE/pymatgen/matplotlib (authorised: "install whatever necessary").
- **Reusable prior work** (read-only sources, do not modify):
  - Gaussian: `/CH/Claude_Workplace/dft/gjf/` (~295 templates incl. `MGC`=[Mg₂Cl₃(THF)₆]⁺, `ANI`=[AlPh₂Cl₂]⁻ anion, `OTf`, `TMSOTf`, `POSS_cage`, `polyether`, `bare0`=MgCl, plus `_ox/_red/a2diss/a3split/red1` redox + desolvation templates) and `/CH/Claude_Workplace/dft/runs/` (98 optimised `.chk`, 74 `.fchk`). Route line: `#p B3LYP/def2SVP EmpiricalDispersion=GD3BJ opt[=loose] freq[=noraman] SCRF=(SMD,Solvent=Tetrahydrofuran) int=ultrafine`, def2-TZVP single points.
  - CP2K: `/CH/Claude_Workplace/cp2k/` — `mg_slab.inp` (Mg(0001) 3×3×4 = 36 Mg, PBE-D3, CUTOFF 400/REL 50, Fermi 500 K, V_HARTREE_CUBE → Φ=3.97 eV), `md_polyapc.inp`/`md_apc*` (NVT Nosé 300 K, 1 fs, neutral surrogate, **no Al**), `_saw.inp` (failed saw-tooth field), `alcl4_*`/`otf_*`/`thf_*` geo-opts, `mg_slab-RESTART.wfn`, `build_slab.py`/`build_interface.py`.
  - **SLURM templates** `/CH/Claude_Workplace/dft/run_g16.sh`, `/CH/Claude_Workplace/cp2k/run_cp2k.sh` (both validated — adapt, don't rewrite).
  - Seed geometries: `/CH/Claude_Calcs_20260603/classical_molecular_dynamics/handoff_for_agent/structures/representative_solvation/*.pdb` (intact `[Mg₂Cl₃(THF)₆]⁺`, contact ion pairs with `[AlPh₂Cl₂]⁻`, polymer-coordinated; 108–134 atoms) and full gel `/CH/Claude_Workplace/polyAPC_gel.gro` (+`polyAPC_network_only.gro`).
- **AIMD cost anchor:** prior 124-atom PBE-D3/DZVP interface ran 8.4–9.0 s/MD-step on 32 ranks → plan **~5 s/step on 64 ranks** (calibrate in Phase 0).

## Working directory & SLURM orchestration

Campaign root `/CH/poly_v2/` (heavy scratch stays on `/mnt/scratch_disk`); raw data trees stay read-only. Layout:
```
/CH/poly_v2/{env,bin,common/struct,results/{data,figures}}
            P0a_speciation/ P0b_redox/ P1_SEI/ P3_raman/   (each: gjf/ runs/)
            P0c_periodic/ P0d_interface/                    (each: inp/ runs/ struct/)
```
- **G16 sizing** (cores tied to species, mirrors known-good prior headers): small ligands/anions (AlCl₄⁻, THF, OTf) **8c/14 GB**; medium (AlPh₂Cl₂⁻, AlPh₃Cl⁻, AlPh₄⁻, polyether, POSS) **16c/24 GB**; large clusters (MGC dimer, bridged pairs) **24–32c/48–64 GB**. Use **physical cores** in `%nprocshared` (no SMT for DFT). Per-job scratch `GAUSS_SCRDIR=/mnt/scratch_disk/g16_scratch/$NAME`.
- **Concurrency = 96 physical cores.** Pack the molecular fan-out as e.g. 6×16c or 12×8c. **One CP2K job at a time** at 64 (benchmark 96) ranks, `OMP_NUM_THREADS=1`.
- **Orchestration:** submit every G16 job `sbatch -c <n> bin/run_g16.sh <name>`; let SLURM core-accounting pack them, fronted by a small **throttle** (`bin/throttle.sh` reading a `manifest.txt` of `name ncores mem`, keeping Σcores ≤ 96). Chain `opt → freq → TZVP-SP` and `parent → ox/red SP` with `sbatch --dependency=afterok:$JID`. CP2K jobs: plain `sbatch --ntasks=64 bin/run_cp2k.sh <name>`, chained `--dependency=afterany` so exactly one AIMD runs at a time.

## Phase 0 — setup & smoke tests (½–1 day)

1. `bin/setup_env.sh`: install Miniconda → `conda create -n build python=3.11 ase pymatgen matplotlib`. **Login-node only, not sbatch.**
2. Copy/adapt `run_g16.sh` (per-job scratch, phase-parameterised `runs/`) and `run_cp2k.sh` (default `NP=64`).
3. **Smoke tests reusing known-good prior inputs:** (a) G16 `bare0` (MgCl) → Normal termination + `.fchk`; (b) CP2K `mg_slab.inp` on 64 ranks → reproduce Φ=3.97 eV; (c) **50-step restart of `md_apc.inp` on 64 and 96 ranks → measured s/step** (fixes AIMD rank count); (d) Multiwfn ESP on `/CH/Claude_Workplace/dft/runs/ANI.fchk` → reproduce prior anion ESP; (e) ASE/pymatgen build Mg-hcp + MgF₂-rutile → CP2K 1-step GEO_OPT via `bin/ase2cp2k.py`; (f) ORCA `wB97X-D/def2-TZVPD` SP on AlCl₄⁻.

## Phase 1 — molecular DFT (Gaussian 16 + Multiwfn) — CHEAP, ~1–2 days, fully parallel

Level of theory (consistent with prior + required cross-checks): **B3LYP-D3(BJ)/def2-TZVP // def2-SVP, SMD(THF), int=ultrafine**; `G = E[TZVP] + Gcorr[SVP freq]`, ΔG(298 K). **Redox/EA cross-checked with ωB97X-D and M06-2X; anion EAs additionally with diffuse def2-TZVPD.** Per-species pattern: `opt freq`@SVP → TZVP SP (+ functional/diffuse variants for redox). Restart from prior `.chk` where available (`ANI`, `MGC`, `OTf`, `TMSOTf`, `POSS_cage`, `polyether`, `bare0`).

- **P0a — APC anion speciation (Schlenk):** optimise+freq `AlCl₄⁻, AlPhCl₃⁻, AlPh₂Cl₂⁻ (restart ANI), AlPh₃Cl⁻, AlPh₄⁻`, neutral `AlCl₃/AlPh₃`, and **Mg–(μ-Cl)–Al bridged ion pairs** (seed from `*_contact_ion_pair.pdb` + `MGC.chk`; net charge bookkeeping per reaction). Compute ΔG of the redistribution ladder (`2 AlPh₂Cl₂⁻ ⇌ AlPhCl₃⁻ + AlPh₃Cl⁻`, `2 AlPhCl₃⁻ ⇌ AlCl₄⁻ + AlPh₂Cl₂⁻`, `AlCl₄⁻ ⇌ AlCl₃ + Cl⁻`) → **Boltzmann equilibrium distribution at 298 K**; identify the **dominant** and **most-reducible** anion → `results/data/speciation_dG.txt`. This re-tests the handoff's "is the dominant anion really `[AlPh₂Cl₂]⁻`, and is 6.18 eV still the anodic limit?"
- **P0b — redox ladder (the headline):** for every P0a species + Mg references: **vertical** IP/EA (q±1 SP at parent geometry, spin flipped) and **adiabatic** IP/EA (re-opt+freq the ion). **Reductive-decomposition ΔG** via relaxed-fragment energies and `opt=(modredundant)` bond-stretch scans (reuse `a2diss/a3split/red1` patterns): `[AlPhₓClᵧ]⁻ + e⁻ →` Al–Cl cleavage (`+ Cl⁻`, SEI-forming) or Al–C cleavage (`+ Ph•`), tracked toward an **Al(0)/Al-centred** product. Convert to **redox potentials vs Mg²⁺/Mg** via a Born–Haber/thermodynamic cycle in the same SMD level (compute `Mg²⁺(THF)₆ + 2e⁻ → Mg⁰` reference). One combined `results/data/redox_ladder.txt` placing Mg²⁺/Mg, every Al-anion reduction, AlCl₄⁻/Al⁰, and (poly-only) OTf⁻ reduction on one axis with the B3LYP/ωB97X-D/M06-2X spread as the uncertainty band.
- **P1 — triflate/F SEI molecular precursors (poly-specific):** `OTf⁻`/`TMSOTf` reductive fragmentation (`CF₃SO₃⁻ + e⁻ →` C–F cleavage `→ F⁻` (→MgF₂), C–S cleavage `→ SO₃²⁻`; `TMSOTf → Me₃Si• + OTf`); place on the redox ladder to test accessibility at the Mg plating potential. **Report F-SEI as poly-specific** (bare modelled F-free per user); flag bare-F artifact + missing S 2p scan.
- **P3 — Raman/IR:** B3LYP/def2-TZVP `opt freq` (full, **not** `noraman`), SMD-THF for IR + a gas-phase `freq` for robust **Raman activities**, on free THF vs Mg-bound THF (`[MgCl(THF)]⁺` model), polyether (`polyether`/`polyether_big`), POSS cage, and anion. Assign **915** (THF ring), **1002→1034** (polyether/POSS) cm⁻¹; report free/bound 915 intensity ratio vs the "⅓ THF network-bound" MD claim. Scale (~0.965) + Lorentzian-broaden in Multiwfn; overlay on `Raman/Raman.xlsx`.
- **Multiwfn batch** (stdin heredocs over each `.fchk`/`.out`, `bin/mwfn_*.sh`): ESP `V_S,min/max`; **Fukui f⁺/dual-descriptor** (most-reducible atom per anion); **spin density** of reduced radicals (is the unpaired electron on **Al** → Al⁰?); QTAIM charges; Raman spectrum export. Quality gates: `NImag=0` (tiny <30i cm⁻¹ floppy modes tolerated + reported); `<S²>` within 0.01 of S(S+1) else defer to ωB97X-D/M06-2X.

## Phase 2 — periodic DFT, bulk & surface (CP2K) — CHEAP–MEDIUM, ~1–2 days

Base settings from validated `mg_slab.inp` (PBE-D3, DZVP-MOLOPT-SR-GTH + GTH-PBE, CUTOFF 400/REL 50). Metals: Fermi smearing 500 K + ADDED_MOS. **Insulating SEI phases: no smearing, CELL_OPT then GEO_OPT.** Structures built via ASE/pymatgen (`bin/build_structures.py` + `ase2cp2k.py`) from known lattice constants — no external DB needed. SCAN/PBE0 MOLOPT cross-check where cheap.

- **Al co-deposition / Mg–Al alloy:** reuse Mg(0001) slab; **Al adatom** adsorption (fcc/hcp/bridge/top) `E_ads(Al)=E[slab+Al]−E[slab]−μ_Al(fcc)`; **co-deposition driving force** `=E_ads(Al)−E_ads(Mg)`; **dilute Al-in-Mg substitution**; **Mg₁₇Al₁₂ (β)** and solid-solution formation energies → `results/data/alloy_formation.txt`. Tests whether Al⁰/Mg–Al alloy is thermodynamically favoured (bare 70.9 eV hypothesis).
- **Al 2p chemical-state prediction:** **Bader charge** (libvori) on Al in metallic-adatom / alloyed / oxide(Al₂O₃)/fluoride(AlF₃) environments → map charge trend to **core-level-shift sign** (low q_Al → ~70.9 eV; high q_Al → ~74.0 eV), reproducing the 3.1 eV split. State the GTH-pseudopotential limitation (no absolute BE); optional **all-electron ΔSCF cluster** cross-check in ORCA/G16. → `results/data/al_bader_cls.txt`.
- **SEI phases + Mg²⁺ transport:** formation energies and relative stability of MgF₂(rutile, **poly-specific**), MgCl₂, MgO, Al₂O₃, AlF₃; **Mg²⁺ migration barriers** via CI-NEB (`&BAND`, 7 images) through MgF₂/MgCl₂/MgO supercells (vacancy/interstitial, large enough to avoid image interaction) → connects to DRT R_ct → `results/data/sei_formation_and_neb.txt`.

## Phase 3 — interface electron transfer (CP2K), BOTH methods cross-compared — MEDIUM–HARD, ~3–5 days

Build real-ion interfaces: Mg(0001) (enlarge to **4×4 lateral, C≈35–40 Å**) + intact cation `[Mg₂Cl₃(THF)₆]⁺` (from `*_octahedral_3Cl3O.pdb`) + an Al-anion (from `*_contact_ion_pair.pdb`) + THF; **poly** variant adds a carved ~50–100-atom POSS-polyether fragment from `polyAPC_gel.gro`. Bare is F/triflate-free (per user); poly carries the network (and OTf/TMSOTf for the SEI channel).

- **Method A — Constrained DFT / Marcus (robust, primary):** CDFT/BECKE_CONSTRAINT to constrain electron count on the Al-anion fragment at the interface (N vs N+1); extract **electron-transfer driving force ΔG_ET and reorganisation energy λ** for Mg→anion, **bare vs poly**. Directly answers "does the anion reduce, and is it harder in poly?"
- **Method B — Dirichlet-BC fixed-potential charged slab (field-driven, cross-check):** Poisson `MIXED_PERIODIC` + `&DIRICHLET_BC/&AA_PLANAR` planar electrode at fixed potential **+ SCCS implicit THF** (ε=7.43) to screen the field and cure the SCF instability that killed the prior saw-tooth; scan integer slab charges (±1, ±2) for the capacitance/field response at the ions. Validate SCCS on the neutral slab first.
- **Pilot:** explicit extra electron (`CHARGE -1` + background) short AIMD watching spin/charge localisation on the anion.
- **Cross-compare** A vs B (and vs the molecular EA/reductive-decomposition ladder from P0b). **Honest framing:** true grand-canonical constant-µ is unavailable (no ESM); CDFT λ/ΔG is the most transferable number, Dirichlet-BC is an idealised counter-electrode. → `results/data/interface_ET.txt`.

## Phase 4 — replicate, real-ion interface AIMD (CP2K) — EXPENSIVE, ~1.5–2 weeks, serial

Extend `md_apc.inp`: NVT Nosé 300 K, TIMECON 50 fs, 1 fs timestep, ASPC order 3, bottom 2 Mg layers fixed, `SCF_GUESS RESTART`. **≥3 replicates per condition** (independent initial velocities/packing) across **bare vs poly × neutral-surrogate vs real-ion(Al)**; target **~10 ps** each (~14–22 h on 64 ranks). Seed as in Phase 3. Analyse with replicate statistics (**mean ± SEM**): Mg→nearest-surface-Mg distance distribution, anion **approach/residence** at the plating front, and whether the anion **reduces/decomposes** (Bader/spin tracking) — bare (anion reaches front, reduces → Al co-deposits) vs poly (network immobilises anion → reduction suppressed → Al stays oxidised). Chain trajectories `--dependency=afterany` so one AIMD runs unattended at a time. Confirms/retracts prior single-trajectory findings (addresses the replicate caveat). → trajectories + `results/data/aimd_interface_stats.txt`.

## Deliverables (full set)

1. `REPORT_polyAPC_v2_master.md` — updated integrated story (preserve honest framing; add Al/redox/SEI chemistry), written into `/CH/Claude_Calcs_20260603/DFT+AIMD/v2_Al_wetlab/`.
2. Publication figures (bare-vs-poly): **Al speciation distribution; oxidation/reduction potential ladder (Mg vs Al vs OTf); Al co-deposition / Mg–Al alloy energy diagram; integrated SEI schematic (XPS-matched composition, F poly-specific); computed Raman assignment; CDFT + fixed-potential interface snapshots.**
3. **Reconciliation table:** each observable (Al 2p split, F/MgF₂, Si/POSS, EDS-vs-XPS depth, Raman shift, DRT, CCD/CE/morphology) → computational explanation → confidence/limitation.
4. Machine-readable `.txt/.csv` for every number + `.xyz/.cif` for every new species/interface (figures reproducible).

## Verification & quality gates

- Toolchain proven by the Phase-0 smoke tests before the big campaign.
- Molecular: `NImag=0`; `<S²>` gate; anion EA with diffuse + range-separated cross-check (report spread); redox potentials referenced to Mg²⁺/Mg in the same SMD level.
- Periodic: SCF to `EPS_SCF 1e-5`; NEB forces converged + climbing image at saddle (spot-check 7 vs 9 images); Bader-based Al 2p stated as a *shift* prediction.
- AIMD: NVT conserved-quantity drift check; **≥3 replicates**, mean ± SEM; field methods validated on neutral slab first.
- Compare bare vs poly for **every** result; no fabrication — missing coords → clearly-labelled representative models.

## Honest limitations (carry into report)

True grand-canonical constant-µ DFT unavailable here (Dirichlet-BC is idealised); anion EAs are method-sensitive; reduced-radical spin contamination can mislead the "Al⁰?" call (lean on spin-density + ωB97X-D); absolute Al 2p BE not obtainable from GTH pseudopotentials; large floppy clusters have ±few-kcal/mol Gibbs uncertainty; **bare-F and missing-S 2p** flagged as unresolved-by-formulation per user (bare modelled F-free).

## Critical files to create (under `/CH/poly_v2/`)

- `bin/setup_env.sh`, `bin/run_g16.sh`, `bin/run_cp2k.sh`, `bin/throttle.sh` (manifest-driven concurrency), `bin/build_structures.py` + `bin/ase2cp2k.py`, `bin/mwfn_batch.sh`, plus parsers in `bin/`.
- Molecular inputs in `P0a/P0b/P1/P3 .../gjf/` (patterned on the prior `gjf/` templates, restarting from prior `.chk`).
- Periodic templates `P0c_periodic/inp/` (bulk/slab/alloy/SEI/NEB) and `P0d_interface/inp/cp2k_cdft_marcus.inp`, `cp2k_dirichlet_cpot.inp`, `cp2k_aimd_realion.inp` (patterned on `mg_slab.inp`/`md_apc.inp`/`alcl4_s.inp`).
- Deliverables in `/CH/Claude_Calcs_20260603/DFT+AIMD/v2_Al_wetlab/` (report, figures, data, structures).
