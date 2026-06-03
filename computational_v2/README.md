# computational_v2 — poly-APC v2 run-ready campaign package

This directory is the **portable, run-ready package** for the poly-APC v2 Aluminium /
SEI / spectroscopy campaign (Gaussian 16 + CP2K + Multiwfn). It is generated and
syntax/structure-validated in a lightweight (web) session; the heavy DFT/AIMD is
executed later on the SLURM/EPYC node, whose run workspace is `/CH/poly_v2/`.

See `../PLAN_polyAPC_v2_computational.md` (full plan) and
`../HANDOFF_computational_v2_Al_and_wetlab.md` (scientific brief).
Numbers land in `../REPORT_polyAPC_v2_master.md` (scaffold with `[[NODE-FILL]]`).

## What is here (built/validated locally — no DFT run)

```
bin/   setup_env.sh  run_g16.sh  run_cp2k.sh  throttle.sh        # orchestration
       build_structures.py  ase2cp2k.py                          # geometries
       gen_g16_inputs.py  gen_cp2k_inputs.py                      # input generators
       mwfn_batch.sh  parse_g16.py  parse_cp2k.py                 # analysis
       make_live_figures.py                                       # live figures
common/struct/   *.xyz (molecular)  *.cif/*.xyz (periodic)        # 48 structures
common/struct_manifest.json                                       # built inventory
P0a_speciation/gjf/  P0b_redox/gjf/  P1_SEI/gjf/  P3_raman/gjf/   # 124 G16 inputs
P0c_periodic/inp/  P0d_interface/inp/                             # 21 CP2K templates
manifest.txt                                                      # throttle job list
results/data/    raman_peaks.csv (live) + NODE-FILL *.txt         #
results/figures/ raman_experimental, drt_*, md_anion_rdf (live)   #
```

The package is **regenerable**: `python bin/build_structures.py && python bin/gen_g16_inputs.py
&& python bin/gen_cp2k_inputs.py && python bin/make_live_figures.py`.

## Deploy & run on the /CH node

1. **Deploy:** `rsync -a computational_v2/ /CH/poly_v2/` then `cd /CH/poly_v2`.
2. **Env:** `bash bin/setup_env.sh` (login node only; builds the Miniconda `build` env
   used by the generators/parsers — *not* G16/CP2K, which are site binaries).
3. **Phase 0 smoke tests (before the big run):**
   - G16 `bare0` (MgCl) → Normal termination + `.fchk`.
   - CP2K `mg_slab` → reproduce Φ = 3.97 eV (workfunction from `V_HARTREE_CUBE`).
   - 50-step restart of `md_apc` on 64 and 96 ranks → measured s/step (fixes AIMD rank count).
   - Multiwfn ESP on a prior `ANI.fchk` → reproduce the prior anion ESP.
   - ASE/pymatgen build sanity: re-run `bin/build_structures.py`; 1-step CP2K GEO_OPT via `bin/ase2cp2k.py`.
   - ORCA `wB97X-D/def2-TZVPD` SP on `AlCl4m`.
4. **Phase 1 (molecular, parallel):** `bash bin/throttle.sh manifest.txt` — packs the 124
   G16 jobs onto the 96 physical cores (Σcores ≤ 96), chaining `opt → tzvp` and
   `parent → ox/red` via `--dependency=afterok`. Restart-tagged species reuse prior `.chk`.
5. **Multiwfn batch:** `bash bin/mwfn_batch.sh P0b_redox/gjf/*.fchk` (ESP/Fukui/spin/QTAIM).
6. **Phases 2–4 (CP2K, one job at a time):** for each template,
   `sbatch --ntasks=64 bin/run_cp2k.sh <name>` (chain AIMD `--dependency=afterany`).
   Insulating SEI phases: run `RUN_TYPE CELL_OPT` then resubmit `GEO_OPT`. Before running
   the interface methods, set the `{ANION_ATOM_LIST}` (CDFT) and `&FIXED_ATOMS LIST`
   (bottom 2 Mg layers) from the actual slab/interface indices. NEB: prepare the 7
   replica `*_img{0..6}.xyz` endpoints (vacancy/interstitial) on the node.
7. **Parse → data:** `python bin/parse_g16.py P0a_speciation/gjf P0b_redox/gjf P3_raman/gjf`
   and `python bin/parse_cp2k.py P0c_periodic/inp/*.out` (and `--neb` for barriers) →
   fills `results/data/*`; then fill the `[[NODE-FILL]]` markers in the report.

## Caveats baked into the templates
- G16 `.gjf` carry the route line `#p B3LYP/def2SVP EmpiricalDispersion=GD3BJ opt freq
  SCRF=(SMD,Solvent=Tetrahydrofuran) int=ultrafine` (+ def2-TZVP SP; ωB97X-D/M06-2X/def2-TZVPD variants).
- CP2K `.inp` use PBE-D3 + DZVP-MOLOPT-SR-GTH/GTH-PBE; metals get Fermi smearing (500 K),
  insulators none. `@INCLUDE '<name>.coord.inc'` pulls geometry from `common/struct`.
- Structures are *starting* geometries (G16 `opt`, CP2K `CELL_OPT/GEO_OPT` refine them);
  `Mg17Al12` uses approximate α-Mn Wyckoff positions → CELL_OPT on node.
- Bare interface is **F/triflate-free** (locked decision); poly carries the POSS-polyether
  network and the OTf/TMSOTf SEI channel.
