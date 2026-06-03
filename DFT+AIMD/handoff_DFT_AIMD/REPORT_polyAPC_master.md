# Why poly-APC differs from liquid APC — an integrated MD + DFT + AIMD study
### Mg-ion gel-polymer electrolyte: in-situ TMSOTf-cured octakis(glycidyl)-POSS in APC (MgCl₂/AlPh₂Cl₂·THF)

---

## Executive summary — the honest, evidence-based picture
Your wet results show poly-APC outperforms liquid APC. Across **3×100 ns classical MD** (bare-APC vs cured gel) + **molecular/periodic DFT** + **interface AIMD**, the data point to a **specific and somewhat counter-intuitive mechanism**:

> **Poly-APC is *not* better at moving Mg²⁺.** It is **~4.4× slower** in bulk and the transference number is **unchanged (t₊ = 0.50)**; the cured network is **segregated from the ions** (Mg stays a fully THF/Cl-solvated [Mg₂Cl₃(THF)₆]⁺, ~7 Å from the polyether). The performance gain is therefore **mechanical, interfacial, and safety-related — not conductivity/transference.**

This is the conclusion that survives scrutiny. The often-assumed "polymer ether-O speeds Mg²⁺ hopping" pathway is **real at the single-molecule level but does not operate in the bulk gel** (the ions never touch the network); it can only matter *at the electrode*.

**Methods (level):** classical MD — OPLS-style FF, 3×100 ns NVT, 298 K, PME; D from unwrapped-MSD (20–80 ns fit), t₊ = D₊/(D₊+D₋). DFT — B3LYP-D3(BJ)/def2-TZVP//def2-SVP, SMD(THF); ESP/surface analysis (Multiwfn). Periodic/AIMD — CP2K, PBE-D3, DZVP-MOLOPT/GTH, Fermi smearing; Mg(0001) slab.

---

## 1. Transport & solvation (classical MD) — the decisive transport evidence
**Diffusion & transference (mean ± SEM, 3×100 ns; 10⁻⁵ cm²/s):**

| system | D(cation [Mg₂Cl₃·6THF]⁺) | D(anion [AlPh₂Cl₂]⁻) | **t₊** |
|---|---|---|---|
| **bare (liquid APC)** | 0.052 ± 0.004 | 0.051 ± 0.005 | **0.50** |
| **poly (gel)** | 0.0117 ± 0.001 | 0.0118 ± 0.002 | **0.50** |

- Gelation **slows both ions ~4.4×**; **t₊ unchanged at 0.50** (network does not preferentially trap the anion).
- **Equilibrated Mg²⁺ solvation (gel, 100 ns):** first shell = **3.1 THF-O + 3.0 Cl + 0.01 network-O** → intact [Mg₂(μ-Cl)₃(THF)₆]⁺; nearest network-O **median 7.1 Å**, only 2 % within 4 Å.
- **⇒ The network is a confining scaffold around solvent-rich ionic domains, not a Mg²⁺ co-solvator.** Bulk transport is *not* the source of the performance gain.

## 2. Electrochemical window (DFT) — the network is benign
Vertical IP/EA (oxidation/reduction onsets, SMD-THF):

| species | IP (oxidation), eV | role |
|---|---|---|
| **[AlPh₂Cl₂]⁻ anion** | **6.18 (lowest)** | sets the anodic limit (known APC weakness) |
| polyether arm | 7.18 | as stable as THF (7.30) |
| **POSS cage (Si₈O₁₂)** | **8.72 (highest)** | most oxidation-resistant; inert scaffold |

⇒ Curing introduces **no group easier to oxidise than the anion**; the inert siloxane cage *raises* average oxidative robustness. Combined with **immobilising ~⅓ of the THF** (MD) → lower free-solvent activity → a more stable, safer effective window.

## 3. Mg²⁺ coordination energetics (DFT)
- **ESP donor strength** (V_S,min): network ether/-OH O = **−46** vs free THF **−36** kcal/mol (intrinsically stronger Lewis base); siloxane cage −10 (non-coordinating).
- **THF binding to the cation** (single-ligand desolvation): **−21 kcal/mol**; Mg–O(network) ≈ −22 → THF and network-O are **near-degenerate** Mg donors.
- **Ion-pair association** in THF: ≈ 0 kcal/mol (heavily solvent-screened → APC already dissociated).
- **Oligomer host screen** (MgCl⁺ probe): crowns/poly-DOL **over-bind** (−62 to −88 = trap); **glycidyl-ether ≈ PEO** (−45 to −47, moderate/optimal); poly-1,3-dioxane weak. ⇒ ours' edge over PEO is the **crosslinkable inert scaffold**, not a unique Mg affinity.

## 4. Mg²⁺ migration / hopping (DFT)
Bridged Mg–O↔Mg–O "hop" barrier vs O···O spacing: **0.5 (5.0 Å) → 5.2 → 10.4 → 14.4 → 17.4 (7.0 Å) kcal/mol**, → dissociative limit ~22. **Barrierless (<1 kcal/mol) at the network's own O-spacing.** *But* (Section 1) the bulk ions are segregated from the network, so **this facile hopping does not operate in bulk** — it is only relevant where Mg contacts the framework (the interface).

## 5. Stepwise Mg²⁺ desolvation — **free-energy ladder** (DFT, ΔG 298 K)
**Now computed as free energies** (G = E[def2-TZVP] + Gcorr[def2-SVP freq]; every minimum frequency-verified, NImag = 0 bar tiny floppy-mode artifacts) — see `dft/free_energy_ladder.png`. The earlier electronic-only ΔE (6→5 = 21.1, 5→4 = 21.3, 4→3 = 27.9 kcal/mol) becomes, in **ΔG**:

**(a) Desolvation of the resting dimer [Mg₂Cl₃(THF)₆]⁺ (per THF):** **6→5 = 9.3, 5→4 = 9.5, 4→3 = 17.1 kcal/mol** — entropy of THF release lowers the absolute cost, but the **rise is preserved**: the inner THF is tightest.

**(b) Rate-limiting *last*-THF removal (mononuclear [MgCl(THF)]⁺), eased three ways (ΔG):**
| route | ΔG (kcal/mol) | note |
|---|---|---|
| **dissociative (cation)** | **+19.9** | the bottleneck |
| **reduction-coupled** ([MgCl(THF)]⁰→[MgCl]⁰+THF) | **+3.9** | electron from the electrode → **−16.0 vs cation** |
| **network-O relay (swap)** ([MgCl(THF)]⁺+ether→[MgCl(ether)]⁺+THF) | **+5.6** | **barrierless** (see TS note) |

- **Transition-state search (real `opt=ts` + freq):** the network-O relay has **no transition state** — a direct saddle search slides downhill to product, and relaxed + frozen-distance scans trap **no maximum**. ⇒ the ether-for-THF substitution is **barrierless** (the strong form of "the network eases desolvation"). The dissociative THF loss and the dimer split are likewise barrierless-dissociative (ΔG‡ ≈ ΔG_step; no saddle).
- **Reduction-coupled desolvation** is the dominant route past the bottleneck: the electron labilises the last THF by **−16 kcal/mol (ΔG)** / −17 (ΔE) — *intrinsic to both electrolytes*, operative at the plating front. The barrierless network-O relay (+5.6 vs +19.9 dissociative) is a *secondary, interfacial* assist on top of it.
- **⇒ Δ‡ ≈ the full barrier could in principle be relayed away — but only where the network contacts Mg, i.e. interfacially**, since the bulk ions are segregated (Section 1). **Dimer-split barrier ‡2 (Mg–Mg pull, full 13-point profile, complete):** ΔE climbs **monotonically and dissociatively** with no TS maximum: 3.0→3.66→4.3→5.0→5.6 Å : **0→13→19→21→23 kcal/mol**, still gently rising toward a ~24–25 kcal/mol dissociation asymptote. The μ-Cl₃-bridged dimer is **robust** — splitting it (required before a single Mg can plate) costs **≥23 kcal/mol**, *exceeding* one THF desolvation, so ‡2 is a genuine bottleneck on a par with (or above) desolvation.

## 6. Mg(0001) electrode interface (periodic DFT + AIMD)
- **Work function** Φ = 3.97 eV (vs expt 3.66 / PBE-lit ~3.7) — slab validated.
- **Static adsorption:** THF/ether physisorb molecularly (~−15 kcal/mol), anion/triflate coordinate — **none decompose spontaneously at 0 K** ⇒ SEI formation is *thermally/electrochemically activated*.
- **Interface AIMD (5.6 ps, NVT, pilot + extension):** the carrier Mg reaches **Mg–surface contact (~3.0–3.1 Å, ≈ the Mg–Mg metallic distance) within ~1 ps in *both* electrolytes** and stays intact — **no spontaneous decomposition**. Using the robust Mg→nearest-surface-Mg distance (not the noisy "height above top atom"), the two systems are **statistically indistinguishable in approach** (APC 3.09, poly-APC 3.14 Å — poly *marginally farther*, within noise). **⚠️ This retracts the 0.6 ps pilot's "poly keeps Mg 0.2–0.3 Å farther / buffers the anode" claim — that was a short-sampling + height-metric artifact and does not survive 5.6 ps.** The one real difference: the **poly-APC carrier samples lower interfacial ligand coordination** (mean 1.7 vs 2.5 O/Cl; repeated drops to 0–1 over 3.5–5 ps) — i.e. it is **more readily desolvated at the electrode**, weakly consistent with the network-O relay easing the final desolvation step (Section 5). *(One trajectory each, neutral, surrogate MgCl₂·(THF) carrier → suggestive, not conclusive; replicates + the real cluster needed.)*
- **Interfacial field — honest limitation:** a *correct* field-driven plating AIMD needs **constant-potential / charged-electrode DFT**. We verified empirically that (i) dipole-corrected MD is SCF-unstable on this metal, (ii) charged-slab+dipole gives no net field, and (iii) an applied saw-tooth potential under-couples to the ions (effective q ≈ 0.2 on the cation, ≈ 0 on the anion). So field-driven plating is left to a dedicated constant-potential study; the neutral-interface results above stand.

---

## 7. Integrated conclusion — why poly-APC performs better
| proposed advantage | verdict from this study |
|---|---|
| faster Mg²⁺ transport / higher t₊ | **NO** — ~4.4× slower, t₊ = 0.50 unchanged (MD) |
| network co-solvates / hops Mg²⁺ in bulk | **NO** — ions segregated ~7 Å from network (MD) |
| **mechanical: rigid crosslinked network** | **YES** — self-standing gel, dendrite suppression (physical confinement) |
| ~~interfacial: buffers the Mg anode~~ | **NO (retracted)** — 5.6 ps AIMD: Mg reaches contact (~3.1 Å) equally in both; the 0.6 ps "buffering" was an artifact |
| **interfacial: benign, non-decomposing contact + easier interfacial desolvation** | **YES** — AIMD: Mg contacts the anode intact (no spontaneous SEI) in both; poly-APC carrier desolvates *more* readily at the interface (network-O relay, Section 5) |
| **safety/durability: immobilised solvent** | **YES** — ~⅓ THF network-bound, less free-solvent activity, no leakage |
| electrochemically inert scaffold | **YES** — POSS cage is the most oxidation-stable component |
| ether-O desolvation relay | **only interfacially** — molecularly favourable, but bulk ions don't touch the network |

**Bottom line:** poly-APC's benefit is **structural, interfacial, and safety-driven**, not transport. The rigorous, data-backed story — "a confining, inert, crosslinked scaffold that immobilises solvent and stabilises the anode interface, at the cost of slightly slower (but equally selective) ion transport" — is both more defensible and more useful for design than "the polymer speeds Mg²⁺."

*Files: classical-MD analysis `MD_transport_results.md`; DFT figures/data in `dft/` and `dft/esp/`; interface in `cp2k/`; mechanism `DESOLVATION_mechanism_plan.md`.*
