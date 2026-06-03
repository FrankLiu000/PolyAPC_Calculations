# Handoff — DFT + AIMD study of poly-APC vs liquid APC (for integration with wet-lab data)

**Scope:** quantum-chemistry (molecular DFT + ESP/surface analysis) and periodic DFT / ab-initio MD
at the Mg(0001) interface, for the Mg-ion gel electrolyte **poly-APC** (in-situ TMSOTf-cured
octakis(glycidyl)-POSS in APC = PhMgCl/MgCl₂ + AlCl₃ in THF) vs **liquid APC**.
Carrier cation = **[Mg₂(μ-Cl)₃(THF)₆]⁺**, anion = **[AlPh₂Cl₂]⁻**.

> **⚠️ Classical MD is NOT in this handoff** — a separate agent prepared the classical-MD (transport /
> diffusion / transference / solvation-shell) handoff. Transport numbers are *quoted* below only where
> the DFT/AIMD story depends on them; treat the MD handoff as the source of record for those.

All heavy compute was run under **SLURM**. Level of theory:
- **Molecular DFT:** B3LYP-D3(BJ)/def2-TZVP // def2-SVP, **SMD(THF)**; ESP on the ρ=0.001 a.u. vdW
  surface (Multiwfn). Free energies G = E[TZVP] + Gcorr[SVP freq], 298 K (every minimum freq-verified).
- **Periodic / AIMD:** CP2K, PBE-D3, DZVP-MOLOPT/GTH, Fermi smearing; Mg(0001) slab.

---

## The story in one paragraph
poly-APC's measured advantage is **structural / interfacial / safety-driven, not transport**. The cured
POSS network is **segregated from the ions** (Mg stays a fully THF/Cl-solvated [Mg₂Cl₃(THF)₆]⁺, ~7 Å from
the polyether), so bulk Mg²⁺ transport actually **slows ~4.4×** with **t₊ unchanged (0.50)** [MD handoff].
The network is **electrochemically benign** (the anion, not any cured group, sets the oxidation limit; the
POSS cage is the most oxidation-resistant component), it **immobilises ~⅓ of the THF** (less free-solvent
activity → safer, self-standing gel), and at the anode the electrolyte **contacts Mg intact with no
spontaneous decomposition**. The desolvation bottleneck that gates plating (last-THF removal, ΔG ≈ +20
kcal/mol) is broken **electronically by the electron transfer at the plating front (−16 kcal/mol)** — an
intrinsic effect common to both electrolytes — with a **barrierless network-O-for-THF substitution** as a
secondary interfacial assist.

---

## Key quantitative results (cross-check targets for wet-lab data)

### 1. Electrochemical window — DFT vertical IP/EA, SMD(THF)
| species | oxidation onset (IP, eV) | role |
|---|---|---|
| **[AlPh₂Cl₂]⁻ anion** | **6.18 (lowest)** | sets anodic limit (known APC weakness) |
| polyether arm | 7.18 | as stable as THF (7.30) |
| **POSS cage (Si₈O₁₂)** | **8.72 (highest)** | most oxidation-resistant; inert scaffold |
→ *Curing introduces no group easier to oxidise than the anion.* Map to: measured anodic stability / CV.

### 2. Mg²⁺ coordination — DFT
- ESP donor strength V_S,min: network ether/-OH O = **−46** vs free THF **−36** kcal/mol (cage −10, non-coordinating).
- THF binding to the cation ≈ **−21 kcal/mol (ΔE)**; Mg–O(network) ≈ −22 → near-degenerate Mg donors.
- Ion-pair association in THF ≈ **0 kcal/mol** (heavily solvent-screened → APC already dissociated).
- Oligomer host screen: glycidyl-ether ≈ PEO (−45…−47, moderate/optimal); crowns/poly-DOL over-bind (trap).

### 3. Desolvation free-energy ladder — DFT ΔG (298 K) — `figures/01`, `data/free_energy_ladder.txt`
- Dimer [Mg₂Cl₃(THF)₆]⁺ per-THF loss: **+9.3 → +9.5 → +17.1 kcal/mol** (inner THF tightest).
- **Rate-limiting last-THF removal, three routes:**
  - dissociative (cation): **+19.9** (the bottleneck)
  - **reduction-coupled** (e⁻ from electrode): **+3.9** → **−16.0 kcal/mol vs cation**
  - **network-O relay (ether-for-THF swap): +5.6, BARRIERLESS** (no TS — `opt=ts` slides to product; scans trap no maximum)
- Dimer μ-Cl₃ split barrier ‡2 ≈ **≥23 kcal/mol** (dissociative, no TS). Map to: overpotential / plating kinetics.

### 4. Mg(0001) interface — periodic DFT + 5.6 ps AIMD — `figures/11`, `data/mg_slab_workfunction.txt`
- Work function Φ = **3.97 eV** (vs expt 3.66) — slab validated.
- Static adsorption: THF/ether/anion physisorb molecularly; **none decompose at 0 K** → SEI is activated.
- **5.6 ps AIMD:** Mg carrier reaches surface contact (~3.1 Å) **intact in both** electrolytes, **no
  spontaneous decomposition**; **no statistically meaningful APC-vs-poly approach difference** (the 0.6 ps
  pilot's "buffering" claim was retracted). Poly-APC carrier samples **lower interfacial coordination**
  (desolvates more readily at the electrode — weak, single-trajectory). Map to: SEI/CE, interfacial behaviour.

---

## Honest bounds / caveats (please carry these forward)
- Bulk transport conclusions (D, t₊, segregation) are from **classical MD → separate handoff**, not DFT.
- Reduction-coupling / relay use a **mononuclear [MgCl(THF)ₙ] surrogate**; the dimer cascade uses the real
  [Mg₂Cl₃(THF)₆]⁺. Ether modelled as **Me₂O**. Numbers carry ±few kcal/mol.
- The interface AIMD is **neutral** (no applied potential): a *field-driven* plating simulation needs
  **constant-potential / grand-canonical DFT** (left as the proper next step; cheaper hacks shown to fail).
- Small imaginary modes on floppy clusters (THF −36, dimer ~−20 cm⁻¹) are pseudorotation artifacts; ΔG impact negligible.

---

## File guide
| file | what it is |
|---|---|
| `REPORT_polyAPC_master.md` | **the integrated narrative + conclusions** (read this first; includes a Section 1 MD recap whose source of record is the MD handoff) |
| `REPORT_polyAPC_DFT.md` | detailed molecular-DFT report (species, ESP, binding, windows) |
| `DESOLVATION_mechanism_plan.md` | stepwise desolvation mechanism, intermediates/TS hypotheses, verification plan |
| `data/free_energy_ladder.txt` | numeric ΔG ladder (the values behind figure 01) |
| `data/RESULTS_table.txt` | per-species E/Gcorr/HOMO-LUMO + binding-energy table |
| `data/mg_slab_workfunction.txt` | Mg(0001) work function |
| `figures/01_free_energy_ladder.png` | **desolvation ΔG ladder** (A: dimer cascade; B: last-THF eased 3 ways) |
| `figures/02_ESP_vdW_surfaces_montage.png` | ESP-coloured vdW surfaces (all key species) |
| `figures/03–07_ESP_*.png` | individual ESP surfaces: cation, anion, THF, polyether, POSS cage |
| `figures/08_descriptor_volcano.png` | descriptor screen (why our chemistry is near-optimal) |
| `figures/09_oligomer_host_screen.png` | oligomer host binding screen (glycidyl-ether vs PEO/crowns) |
| `figures/10_hopping_barrier_vs_spacing.png` | Mg–O↔Mg–O hop barrier vs O···O spacing |
| `figures/11_interface_AIMD_5ps.png` | 5.6 ps Mg(0001)‖electrolyte AIMD (APC vs poly-APC) |
| `figures/12_interface_AIMD_pilot.png` | 0.6 ps pilot AIMD (superseded by 11; kept for reference) |

*Raw Gaussian `.log/.fchk`, CP2K trajectories, cubes and parsers live in `/CH/Claude_Workplace/dft/` and
`/CH/Claude_Workplace/cp2k/` (not copied here — multi-GB). Ask if any raw output is needed.*
