# C1 — Aluminium speciation, reduction & co-deposition (tickets T1–T4)
**Objective (ARTICLE_PLAN Part C1):** establish, from first principles, that the APC aluminium anion **can be reduced to deposited/alloyed Al⁰ at the Mg anode** — the chemical origin of bare-APC's metallic/alloyed Al (XPS Al 2p 70.88 eV) and the thing poly must suppress.
**Method:** molecular DFT B3LYP-D3(BJ)/def2-TZVP//def2-SVP, SMD(THF); G = E[TZVP,SMD]+Gcorr[SVP freq]. Periodic CP2K PBE-D3, DZVP-MOLOPT-SR-GTH/GTH-PBE, Mg(0001) 3×3×4 slab. (Raw single-points computed in the v2 campaign; this ticket assembles them onto the v3 Al-co-deposition axis and adds the Schlenk equilibria.)

## T1 — Speciation: the dominant anion, and AlCl₄⁻ is a minority
Free energies G (Ha, SMD-THF) and **Schlenk ligand-redistribution** equilibria (`outputs/speciation.csv`):

| reaction (Al,Ph,Cl conserved) | ΔG (kcal/mol) | reading |
|---|---|---|
| 2 AlPh₂Cl₂⁻ ⇌ AlPhCl₃⁻ + AlPh₃Cl⁻ | **+1.1** | [AlPh₂Cl₂]⁻ slightly favoured (dominant) |
| 2 AlPhCl₃⁻ ⇌ **AlCl₄⁻** + AlPh₂Cl₂⁻ | **+4.5** | forming AlCl₄⁻ is uphill → **AlCl₄⁻ is a minority (Schlenk tail)** |
| 2 AlPh₃Cl⁻ ⇌ AlPh₂Cl₂⁻ + AlPh₄⁻ | **+3.2** | AlPh₄⁻ disfavoured |

All ΔG > 0 ⇒ the equilibrium **disfavours the extremes** and centres on the mixed phenyl-chloride anions, with **[AlPh₂Cl₂]⁻ dominant**. The anodic-limit weak point is its IP **6.18 eV (B3LYP; +0.4 eV range-separated)** — consistent with the prior value.

## T2 — Where the electron goes (reduction site)
One-electron reduction, UB3LYP/def2-TZVP SMD, Mulliken spin (`reduction_spin_localization.txt`):

| anion + e⁻ | Al spin | site |
|---|---|---|
| **AlCl₄⁻** | **+1.14** | **ALUMINIUM → Al⁰ precursor** |
| AlPhCl₃⁻ / AlPh₂Cl₂⁻ / AlPh₃Cl⁻ / AlPh₄⁻ | +0.06–0.08 | phenyl π* |

Only the **chloride-rich AlCl₄⁻ reduces at Al**; every phenyl-bearing anion (incl. the dominant one) reduces on a phenyl π*. Contact-pairing with the [Mg₂Cl₃(THF)₆]⁺ cation makes the anion **~8× more reducible** (vertical EA 0.06 → 0.51 eV; `depairing_ET.txt`) — i.e. reduction happens at the **cation-paired interface**, not on the free anion.

## T3 — Reductive decomposition → Al⁰ precursor (the bridge from the dominant anion)
The phenyl-π* reduction is not a dead end: the one-electron-reduced **[AlPh₂Cl₂]²⁻** decomposes (G in Ha, ΔG kcal/mol; `reductive_decomposition.txt`):

| step | ΔG | product |
|---|---|---|
| **Al–Cl cleavage** | **−8.5** | [AlPh₂Cl]·⁻ + Cl⁻ (Cl⁻→MgCl₂) |
| Al–C cleavage | +14.5 | [AlPhCl₂]·⁻ + Ph⁻ |

Al–Cl cleavage is favoured by **23 kcal/mol** and is exergonic; the product **[AlPh₂Cl]·⁻ carries 83 % of the spin on Al** (Al(II) radical) → the **direct precursor to Al⁰**. So even the dominant anion provides a reductive-decomposition route to Al-centred reduction once it is reduced at the paired interface.

## T4 — Al⁰ co-deposition / Mg–Al alloying (periodic)
Once Al⁰ forms it is captured by the Mg anode (`al_codeposition_periodic.txt`, Mg(0001) 3×3×4):

| process | energy | verdict |
|---|---|---|
| Al adatom (fcc/hcp hollow) | E_ads = **−0.08 eV** | weakly favourable vs bulk Al |
| **dilute Al-in-Mg substitution** | E_sub = **−4.44 eV** | **strongly favourable → alloying** |

⇒ deposited Al⁰ alloys into Mg, giving the **reduced/alloyed Al** state (sub-metallic Al 2p ≈ 70.9 eV — see T11). (Mg₁₇Al₁₂ formation flagged ARTIFACT in v2, not used.)

## Conclusion (C1)
A complete, thermodynamically accessible **bare-APC pathway to deposited/alloyed Al⁰** exists: Al-centred reduction comes from the **minority AlCl₄⁻** *and* from **reductive decomposition** of the reduced dominant anion (Al–Cl cleavage → 83 %-Al radical), activated by cation-pairing at the interface; the resulting Al⁰ **alloys into Mg (−4.44 eV)**. This is the chemistry that produces bare's Al-rich SEI / 70.9 eV Al 2p — and the channel poly must block (C2 transport gating + C3/T8 passivating SEI). It does **not** require contradicting the v2 nulls (those concerned the *dominant* anion's primary reduction site).

**Provenance:** `results/C1_Al_reduction/outputs/speciation.csv` (new, this ticket); v2 data `redox_ladder.txt`, `reduction_spin_localization.txt`, `depairing_ET.txt`, `reductive_decomposition.txt`, `al_codeposition_periodic.txt`. Level of theory as above. **Open refinement:** explicit reduction potentials vs Mg²⁺/Mg (adiabatic logs available; T2-extension).
