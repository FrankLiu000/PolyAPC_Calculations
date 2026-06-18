# CLAUDE.md — poly-APC computational project (entry point)

You are a Claude Code agent on a compute node. This repo is a **scientific compute assignment**.

## Start here (read in this order)
1. **`ARTICLE_PLAN_v3_interface_composition.md`** — the scientific spec: re-analysed wet-lab data, the article narrative, target numbers to reproduce, and the compute↔data map.
2. **`COMPUTE_HANDOFF_tasks.md`** — your executable task list (T0 → T15). Do T0 (preflight) first, then work in dependency order, committing per ticket.

## Mission (one line)
Compute *why* the in-situ POSS-cured "poly-APC" Mg-anode interphase is **Si-rich and Al-poor**, and why that (not ion transport) makes Mg plating reversible — centred on the **reduction/co-deposition chemistry of the APC Al-anion** that the prior study omitted.

## Hard constraints (do not violate)
- **Interface story = Si (↑) / Al (↓) only. NO fluorine/triflate/MgF₂ narrative.**
- **Compute everything in COMPUTE_HANDOFF_tasks.md §T — no triage.**
- **Always report bare vs poly in parallel.**
- **Transport is NOT the discriminator** (MD + GITT both give D ≈ 8–9×10⁻¹⁵ cm² s⁻¹; t₊=0.50). Do not invent a transport advantage.
- **No fabrication**: label models as models; frequency/convergence-verify; replicate AIMD; report uncertainties.
- **Reproduce-or-explain** the XPS Al 2p split: bare 70.88 eV (Al⁰/alloy) vs poly 73.98 eV (Al³⁺).

## Compute infrastructure (two nodes)
- **CPU node → DFT + AIMD** (ORCA/Gaussian molecular DFT; CP2K/VASP periodic, CI-NEB, ab-initio MD; core-level & Raman).
- **GPU node → classical MD + MLFF** (GROMACS-GPU for structure/transport; a fine-tuned foundation **MLFF** — MACE-MP-0 / CHGNet — for reactive, large-cell, long-time interface & SEI simulation).
- **Active-learning loop:** CPU makes DFT/AIMD labels → GPU trains MLFF → GPU runs production → high-uncertainty configs go back to CPU for labelling → retrain. **Every MLFF result must be DFT-validated (report force/energy MAE).** Each ticket in COMPUTE_HANDOFF_tasks.md is tagged [CPU]/[GPU]/[both].

## Conventions
- Results → `results/<TID>_<name>/` with `REPORT.md` + machine-readable `.csv`/`.json` + `.xyz`/`.cif`; integrate into `RESULTS_v2/REPORT_v2_master.md`; keep `RESULTS_v2/STATUS.md` updated; one commit per ticket.
- Baselines to match: DFT **B3LYP-D3(BJ)/def2-TZVP//def2-SVP, SMD(THF)**; periodic/AIMD **CP2K PBE-D3, Mg(0001), Φ≈3.97 eV**; MD **GROMACS (OPLS)**. Adapt to node-available codes and document. Run each ticket on its tagged node (CPU=DFT/AIMD, GPU=MD/MLFF).

## Data note
Raw experimental data is large and may not be in this repo — you don't need it; **targets to reproduce are tabulated in ARTICLE_PLAN Part A/D, and you build input structures yourself.** A few seed structures (MD `.gro/.top/.itp`, cation/ion-pair `.pdb`) are needed for T5/T10 — if absent, ask the PI to add them under `seeds/`.
