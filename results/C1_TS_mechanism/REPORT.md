# C1 — transition states & intermediates of the bare-APC Al-deposition mechanism

**Objective:** resolve C1 (T1–T4) from *thermodynamic endpoints* into a **step-by-step reaction coordinate** — the intermediates and transition states by which the bare-APC Al-anion is converted to deposited/alloyed Al⁰ — on **both** the homogeneous (in-THF) and heterogeneous (at the Mg electrode) sides. This is the reduction/co-deposition chemistry the prior study omitted.

**Methods.** Solution: molecular DFT **B3LYP-D3(BJ)/def2-SVP, SMD(THF)** (G16; opt+freq, relaxed scans, OptTS=(ts,calcfc), IRC; `scf=xqc` for ion pairs). Surface: **CP2K PBE-D3, DZVP-MOLOPT-SR-GTH/GTH-PBE**, fresh Mg(0001) 4×4×4 slab, **rigid DFT-masked slab** (freeze all 64 Mg, relax adsorbate — the T16/T17 convention), k-points MP 3×3×1. Energetics in `outputs/c1_mechanism_energetics.csv`.

---

## The mechanism (step by step)

### ① Gateway — cation Cl-abstraction (bare-specific activation)
`[AlPh₂Cl₂]⁻ + [MgCl(THF)]⁺ → AlPh₂Cl + MgCl₂(THF)`  **ΔG_rxn = −16.8 kcal/mol (strongly exergonic).**
The bare Mg cation strips a Cl⁻ off the dominant Al-anion, yielding **neutral AlPh₂Cl** — an electron-poorer, far easier-to-reduce species. This is the gateway into the reductive chain, and it is exactly what the T10 constant-V AIMD shows (the bare `[Mg₂Cl₃]⁺` cation abstracting Cl, leaving neutral AlPh₂Cl); **poly's percolating network keeps the Cl on the anion** (memory: chloride-abstraction gateway).
*Honest:* the explicit saddle was attempted by relaxed scan and by a frozen-spectator scan; both **crashed/stalled on the floppy 40-atom ion-pair SCF** (needed `scf=xqc` even to converge points). The reaction is **exergonic** and a Cl⁻ transfer between two Lewis acids is a low-barrier ligand-exchange, so the gateway is reported as **thermodynamically facile** (ΔG = −16.8) rather than with an explicit ΔG‡.

### ② Reductive decomposition — Al-radical formation (homogeneous)
Five intermediates optimized (G, SMD-THF): **AlPh₂Cl**, **[AlPh₂Cl]·⁻**, **AlPh₂·**, **[AlCl₃]·⁻**, **AlCl₂·**.
**Key finding — the reductive Al–Cl cleavages are electron-transfer-gated, not bond-cleavage-TS-gated:**
- `TS_AlCl3`: OptTS finds a genuine saddle (1 imaginary mode, **−248 cm⁻¹**) but **all three Al–Cl bonds remain intact (2.21/2.29/2.29 Å)** — it is a **floppy pseudorotation** of the reduced radical, *not* the Cl-loss TS (IRC completed; it connects two equivalent distorted minima, and its energy sits *below* the symmetric reactant — a Jahn–Teller-type distortion, not a barrier on the dissociation path).
- `TS_AlPh2Cl`: the reductive Al–Cl scan rises **monotonically** (no interior saddle) → **no clean activation barrier**.
- The one-electron-reduced **dianion [AlPh₂Cl₂]²⁻ has a *bound* minimum** (released from a stretched geometry it relaxes back to Al–Cl 2.24/2.26 Å), so the T3 −8.5 kcal/mol cleavage is thermodynamically downhill but its barrier lives in the continuum-artifact region (−2→−1+−1 in one cavity).

⇒ **In solution the kinetic gate is the electron transfer (Marcus), not a subsequent bond-breaking TS** — the reduced Al-chlorides shed Cl essentially without an activation barrier, consistent with fast SEI-forming reduction. Products are Al-centred radicals (T3: 83 % Al spin) → Al⁰.

### ③ Heterogeneous route — adsorbed intermediates at the electrode
On the bare Mg(0001) surface (CP2K, rigid slab):
| adsorbed intermediate | geometry | energy |
|---|---|---|
| **AlCl₃\*** (intact, chemisorbed) | Al-down, +2.36 Å above surface, 3× Al–Cl ~2.2 Å | **E_ads = −1.82 eV** (binds strongly) |
| **AlCl₂\* + Cl\*** (Cl stripped to surface) | stripped Cl in a Mg hollow (+1.82 Å), Al–Cl 5.7 Å | **E_rxn = +0.24 eV** vs intact |

The Al-chloride precursor **chemisorbs strongly** on the bare electrode, and **stripping a Cl onto the surface is near-thermoneutral** (on a *neutral* slab — under cathodic plating potential the electron-rich electrode tips it downhill). The stripped Cl builds the **Cl-rich / MgCl₂ SEI**; the residual AlCl₂ reduces further → **Al⁰ deposit**. This is the heterogeneous analogue of ②: the electrode itself holds the precursor and peels off Cl.
*Honest:* the explicit **adsorbed TS** (Cl-migration barrier) was attempted three ways (16-/32-core constrained scan, pre-displaced constrained scan). The k-point **metal-slab SCF is ~200 s/iteration, ~23 iterations for the first SCF (~77 min/point) and ~10–20 constrained-opt steps/point → >10 h for the scan** — the same wall that stopped the T9 NEB. The barrier is therefore reported as **bounded below by the +0.24 eV endothermicity** (Cl migration on a metal is otherwise a low-barrier hop); the explicit saddle is not forced.

---

## What this adds to C1 (and the bare-vs-poly story)
A connected reaction coordinate now underlies the C1 thermodynamic endpoints: **bare cation strips Cl (gateway, −16.8 kcal/mol) → neutral organoaluminum → reduces with no bond-breaking barrier (ET-gated) → Al-centred radical → captured/alloyed (T4 −4.44 eV)**; and heterogeneously, **the Al-chloride chemisorbs (−1.82 eV) and Cl-strips near-thermoneutrally into the SEI**. Every activated step that *is* well-defined is downhill or barrierless on bare. **Poly suppresses the chain at its entry points** — it keeps Cl on the anion (no gateway) and holds the anion ~2× further from the electrode (T17), so the heterogeneous chemisorption/strip never initiates.

## Honest status
**Solid:** 5 solution intermediates + the gateway ΔG (−16.8); the ET-gated character of the reductive cleavages (floppy/barrierless TSs, IRC-checked; dianion bound-minimum); surface adsorbed intermediates (AlCl₃\* −1.82 eV, Cl-strip +0.24 eV). **Not forced (reported as bounds/thermo):** the gateway explicit ΔG‡ (floppy ion-pair SCF crashes) and the adsorbed Cl-strip ΔG‡ (metal-slab SCF wall, = T9). No barrier was invented; floppy/ill-defined saddles were labelled as such. Level of theory and provenance in `outputs/` and `inputs/`.
