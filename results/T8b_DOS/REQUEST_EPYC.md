# EPYC REQUEST (Windows→CPU): DOS / PDOS for SEI phases + Mg|SiOₓ band alignment

**Node:** EPYC (CP2K, k-point DFT). **Branch:** computational-v3-interface. **Requested:** 2026-06-23.
**Purpose:** upgrade article **Fig 5d** from band-gap *bars* → publication (JPCC-style) **DOS/PDOS curves**, and
add a **band-alignment** panel for the passivation story (Mg Fermi level inside the SiO₂ gap → electron-
injection barrier). T8 saved only `t8_gaps.csv` (gap scalars); the full DOS was never exported.

## Why (figure-driven)
Reviewers/PI flagged the computational figures as too monotonous. SEI electronic structure is the C3/T8
story (**Al⁰/Mg₁₇Al₁₂ metallic & leaky vs SiO₂/Al₂O₃/MgO/MgCl₂ insulating & passivating**). A DOS/PDOS
overlay is the standard, compelling way to show it. The band gaps already exist (`t8_gaps.csv`); we now need
the **curves** + an interface band alignment.

## What I need (priority order)
1. **Total DOS + element-projected PDOS** for the six T8 phases — reuse the **relaxed geometries + existing
   inputs** in `results/T8_sei_electronic/inputs/*_kp.inp` (Al_fcc, Mg17Al12, MgCl2, MgO, Al2O3, SiO2; +Mg_hcp
   reference). Just add CP2K `&PRINT &PDOS … &END` (+ `&DOS` or post-process from MO eigenvalues), single-point
   on the relaxed structure (cheap — no re-relax). Gaussian-broaden σ≈0.1 eV.
   - **Output (machine-readable):** `results/T8b_DOS/outputs/<phase>_dos.csv` with columns
     `E_minus_Ef_eV,totalDOS,pdos_<elem>…`; energies referenced to **E_F** (metals) or **VBM** (insulators);
     record E_F, VBM, CBM in `dos_meta.json`. This drops straight into a `fig5d_dos.py` overlay.
2. **Mg(0001) | SiOₓ interface band alignment (passivation, T6):** PDOS of a Mg(0001)+thin-SiO₂ contact slab
   (reuse the T6 band-align model if present) projected on (i) Mg slab, (ii) SiOₓ layer → show **Mg E_F sits in
   the SiO₂ gap**, with the **electron-injection barrier ≈3.07 eV** (E_F → SiO₂ CBM). Output
   `iface_MgSiOx_pdos.csv` (+ the barrier value). If the T6 slab needs rebuilding, a ~1–2 nm SiO₂ on Mg(0001)
   single-point PDOS is sufficient.
3. *(optional, if cheap)* same alignment for **Mg|Al₂O₃** and a **Mg|Al⁰** contact** (to contrast leaky-metal vs
   insulator) — one panel showing why bare (Al⁰) leaks electrons and poly (SiOₓ) blocks them.

## Constraints
- k-point DFT for the metals (Al_fcc, Mg17Al12, Mg_hcp); your T8 `_kp.inp` level. Reference all energies to E_F.
- Keep it single-point on relaxed geoms — this is a **printing/post-processing** job, not new optimization.
- Machine-readable CSV + a one-line provenance (code+version+date) per the repo convention.

## Acceptance / loop
Push `results/T8b_DOS/outputs/*_dos.csv` + `dos_meta.json` (+ interface PDOS) to the branch. I (Windows) then
render `Fig5d_DOS` (total DOS + PDOS overlay, metals shaded leaky / insulators shaded passivating) and the
band-alignment inset, replacing the band-gap bar panel.

*(No GPU/MLFF action needed for this request. If a representative reactive-interface snapshot — bare Al co-
deposited vs poly clean — can be dumped from the T17 trajectory for a Fig 5 panel, that would help, but it is
secondary.)*
