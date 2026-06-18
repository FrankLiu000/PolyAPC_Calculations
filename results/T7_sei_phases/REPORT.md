# T7 — Candidate SEI phase set + stability
**Objective (ARTICLE_PLAN C3):** define the **poly SEI = SiOₓ/POSS + MgClₓ + MgO (+organics)** and **bare SEI = Al/AlOₓ(+Mg–Al) + MgClₓ + MgO** and show the phases are thermodynamically stable (they actually form).
**Method:** CP2K PBE-D3, DZVP-MOLOPT-SR-GTH/GTH-PBE, CUTOFF 400/50. Phases CELL_OPT-relaxed (v2 bulk + **α-quartz SiO₂ relaxed this session**). Formation energy E_f = E(phase)/f.u. − Σ nᵢμᵢ, with **k-point-converged metal references** (μ_Mg, μ_Al from T8 k-point cells) and molecular/bulk references O₂(triplet), Cl₂, Si(diamond) computed here.

## Result (`outputs/sei_formation_energies.csv`)
| phase | E_f (eV/f.u.) | E_f (eV/atom) | role | exp ΔH_f (eV/f.u.) |
|---|---|---|---|---|
| **SiO₂ (α-quartz)** | **−9.22** | −3.07 | **poly (Si-rich)** | −9.4 ✔ (spot-on) |
| Al₂O₃ (corundum) | −15.45 | −3.09 | bare oxidised-Al residue | −17.4 |
| MgO | −4.02 | −2.01 | shared | −6.0 |
| MgCl₂ | −4.22 | −1.41 | shared | −6.6 |

**All phases are thermodynamically stable (negative E_f)** → the proposed SEI components do form. The **Si-rich SiO₂ poly phase is strongly stable** (E_f matches experiment to 0.2 eV).

## Notes / honesty
- The oxides/chloride come out **~1.5–2.5 eV less negative than experiment** — the known **PBE O₂/Cl₂ over-binding** error (each O/Cl in the molecular reference). SiO₂ is fortuitously excellent. The **ordering and stability sign are robust**; absolute values are semi-quantitative.
- Using k-point metal references was essential: Γ-only μ_Mg/μ_Al are under-converged and gave spuriously small formation energies.
- **Mg₁₇Al₁₂ excluded:** its computed formation is **+1.05 eV/atom — the v2-flagged ARTIFACT** (approximate Wyckoff/unconverged CELL_OPT). Mg–Al **alloying is instead established by the robust dilute-substitution energy E_sub = −4.44 eV** (C1/T4) — the relevant quantity for co-deposition anyway.
- Phase models are stoichiometric crystals (labelled as models), not the amorphous mixed SEI; electronic passivation quality is the T8 deliverable.

**Provenance:** references in `inputs/` (O2/Cl2/Si_diamond), phase energies from v2 bulk CELL_OPT + this session's SiO₂. Feeds ARTICLE_PLAN Part D (SEI composition) and pairs with **T8** (electronic structure).
