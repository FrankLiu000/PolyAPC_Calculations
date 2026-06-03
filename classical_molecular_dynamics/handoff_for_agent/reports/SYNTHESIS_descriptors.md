# poly-APC — deep synthesis & descriptor set

Synthesis across the MD campaign: **bare-APC → poly-APC (4 POSS) → poly-APC (16 POSS)**,
combining structure (RDF/CN), solvation statistics, energy-group decomposition, and diffusion.
Confidence tags: **[robust]** = converged / cross-validated / experiment-consistent;
**[trend]** = single-run or model-limited but internally consistent; **[hypothesis]** = interpretive.

---

## 1. The five higher-order stories

### Story 1 — "Speciation-transparent gel": solid form, liquid speciation  **[robust]**
The cured poly-THF/POSS network swells with the electrolyte **without touching the redox-active
species**. The iconic **[Mg₂(μ-Cl)₃·6THF]⁺** cluster is intact in every system (Mg–Cl CN = 3.0 at
0.25 nm, Mg–O CN ≈ 3 at 0.21 nm, total CN ≈ 6.2–6.3), matching XRD/AIMD. The gel changes the *form
factor* (liquid→quasi-solid, ρ 0.95→1.00 g cm⁻³) while preserving the *chemistry that makes APC
plate Mg reversibly*. **Descriptor: speciation-transparent / non-disruptive host.**

### Story 2 — Dual-mode solvation: the matrix is electrostatically silent but dispersively active  **[robust]**
The cation and anion are solvated by *opposite* physics:
- **Cation** = electrostatically solvated (Mg–Cl, Mg–O, ion-pairing Coulomb dominate; vdW minor).
- **Anion [Ph₂AlCl₂]⁻** = dispersively solvated (van der Waals with THF/polymer dominates, −69 kJ/mol;
  Coulomb to neutral partners only −8).
The polymer's Coulomb coupling to *both* ions is ~0 at low loading; it re-solvates them by **vdW**.
And it does so anion-preferentially (per-atom polymer-vdW −0.75 anion vs −0.52 cation).
**Descriptor: electrostatically-silent, dispersively-active, anion-philic matrix.**

### Story 3 — The cure turns a crosslinker into a distributed ligand ("latent-ligand network")  **[trend→robust]**
The deepest result. Glycidyl-POSS is not just a mechanical crosslinker: **every epoxide that opens
during cure becomes an ether/hydroxyl oxygen — a latent, weak Mg-coordinating site.** The cured
network is therefore a *distributed polydentate ligand* whose coordinating power scales with
**loading × conversion** (total opened-glycidyl O). The loading scan makes this explicit:

| | bare | 4-POSS | 16-POSS |
|---|---|---|---|
| Mg–polymer-O first-shell contact | — | 0.6% | **5.0%** |
| Mg↔polymer Coulomb (per cluster) | — | ≈0 | **−5.5** |
| contact ion pairing (Mg–anion) | 83% | 80% | **59%** |
| Mg↔anion Coulomb (per cluster) | −97 | −93 | **−69** |

As the latent ligands "switch on," they enter the Mg sphere and **out-compete the anion** → ion
pairing collapses 83→59%. **Descriptor: latent-ligand / self-chelating cured network.**

### Story 4 — The coordination paradox: de-pairing re-traps the cation  **[trend]**
The same oxygens that break the ion pair **tether the Mg cluster to the network**. So loosening the
ion pair does *not* liberate a fast Mg²⁺ — it swaps an anion partner for a matrix partner:
- t₊ ≈ 0.50 (bare) → 0.50 (4-POSS) → **~0.46** (16-POSS): no gain, slight dip.
- At 16-POSS the cation diffuses *slower* than the anion (D₊ < D₋) — the matrix anchors it.
**You cannot get "free Mg" and "fast Mg" from this chemistry simultaneously.**
**Descriptor: de-pairing–tethering anti-correlation (coordination paradox).**

### Story 5 — A non-selective molecular brake (transference is gel-invariant)  **[robust at 4-POSS, trend at 16]**
Gelation slows transport ~uniformly for cation and anion (×4 at 4-POSS, ×10 at 16-POSS), so the
**transference number is essentially invariant (~0.5)** — the network raises tortuosity/viscosity
without chemical selectivity between the ions' motion. A bigger network = a stronger brake, not a
better filter. **Descriptor: iso-mobility (non-selective) tortuosity brake.**

---

## 2. Descriptor set that highlights poly-APC

**Qualitative character labels**
- *Speciation-transparent gel* — preserves [Mg₂Cl₃·6THF]⁺.
- *Latent-ligand / self-chelating network* — cured glycidyl-O = distributed weak Mg ligands.
- *Electrostatically-silent, dispersively-active, anion-philic host.*
- *Coordination-paradox electrolyte* — de-pairing ⟂ cation mobility.
- *Iso-mobility tortuosity brake* — t₊-invariant under gelation.
- *Amphiphilic partitioned medium* — hydrophobic anion+POSS/poly-THF vs THF+Mg-cluster domains.
- *Junction-spaced percolated network* — POSS junctions (4.5–4.7 nm) bridged by poly-THF strands.

**Quantitative descriptors (poly-APC vs references)**

| descriptor | bare | poly-4 | poly-16 | meaning |
|---|---|---|---|---|
| Mg total coordination (Cl+O) | 6.16 | 6.16 | 6.31 | speciation preserved |
| Mg–Cl(bridge) CN | 3.0 | 3.0 | 3.0 | dinuclear core intact |
| contact-ion-pair fraction | 83% | 80% | 59% | **tunable de-pairing** |
| Mg–polymer-O contact | — | 0.6% | 5.0% | **latent-ligand activation** |
| Mg↔anion Coulomb (kJ/mol·cluster) | −97 | −93 | −69 | pairing strength |
| Mg↔polymer Coul / LJ | — | 0/−43 | −5.5/−65 | matrix coordination |
| anion vdW: THF / polymer | −69 / — | −50 / −19 | (−)/(−) | dispersive re-solvation |
| transference t₊ | 0.505 | 0.496 | ~0.46 | **gel-invariant** |
| ion mobility suppression | 1× | ~4× | ~10× | tortuosity brake |
| density (g cm⁻³) | 0.95 | 1.00 | — | quasi-solidification |
| free-THF (swelling) | 2120 | 1399 | 1220 | solvent uptake |

---

## 3. Design implication (the actionable insight)
poly-APC behaves as a **speciation-preserving, latent-ligand gel**: curing Glycidyl-POSS supplies
weak Mg-coordinating oxygens that can be *dialed up by loading/conversion* to break ion pairs — but
because those same oxygens tether the cation, **breaking the ion pair does not raise t₊; it lowers
mobility**. The lever that *would* raise Mg²⁺ transference is **anion-selective** binding (Lewis-
acidic B/Al anion receptors), not more cation-coordinating ether/OH. The Glycidyl-POSS chemistry is
ideal for a mechanically robust, speciation-safe host; it is *not*, by itself, a transference
enhancer.

## 4. Confidence & caveats
- **[robust]**: APC speciation, dual-mode solvation, the latent-ligand de-pairing trend, t₊≈0.5 at
  bare/4-POSS (replicated 3×100 ns).
- **[trend]**: 16-POSS numbers (single 50 ns, deeply sub-diffusive — ions move <1 nm/30 ns, so D/t₊
  are upper-bound/qualitative); 4→16 jump confounded with conversion (69%→100%).
- Model: classical, non-polarisable, scaled Mg/Cl charges; charged–charged Coulomb is short-range
  only. Trends/ratios trustworthy; absolute energies/kinetics effective.
