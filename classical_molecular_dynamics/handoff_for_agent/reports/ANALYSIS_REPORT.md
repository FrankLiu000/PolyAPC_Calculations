# poly-APC vs bare-APC — 50 ns MD analysis of Mg-cluster solvation & energetics

## Methods
- **Systems**: bare-APC = 80 [Mg₂(μ-Cl)₃·6THF]⁺ + 80 [Ph₂AlCl₂]⁻ + 2120 THF (36 200 atoms);
  poly-APC = same electrolyte embedded in the fully-cured POSS/poly-THF network
  (single covalent network `NET1`) + 6 TMSOTf (37 072 atoms).
- **Protocol**: EM → NPT pre-equilibration (298 K, 1 atm, 1 ns) → **NVT production 50 ns at 298 K**
  (dt 2 fs, PME, h-bond constraints, v-rescale). 12 CPU threads + GPU each, run in parallel.
  Equilibrated densities: bare 0.95, poly 1.00 g cm⁻³.
- **Analysis**: last 40 ns (first 10 ns discarded). RDFs/CN (`gmx rdf`), per-Mg first-shell
  statistics over 201 frames × 160 Mg = 32 160 samples (cutoffs Mg–Cl 0.315, Mg–O 0.300,
  Mg–anionCl 0.345 nm), and short-range non-bonded interaction energies by energy-group
  decomposition (rerun). FF: OPLS-AA-based (see ../PARAM_NOTES.md); Mg/Cl scaled charges.

## 1. Mg-cluster RDFs (first-peak position / coordination number to 0.35 nm)
| pair | bare peak (nm) | bare CN | poly peak (nm) | poly CN |
|---|---|---|---|---|
| Mg–Cl (bridge) | 0.250 | **3.00** | 0.250 | **3.00** |
| Mg–O (THF ligand) | 0.212 | **3.00** | 0.212 | **3.00** |
| Mg–O (all THF) | 0.212 | 3.17 | 0.212 | 3.16 |
| Mg–Cl (anion) | 0.244 | 0.84 | 0.244 | 0.80 |
| Mg–Al (anion) | 0.444 | 0.00 | 0.444 | 0.00 |
| Mg–O (polymer) | — | — | (none <0.35) | **0.01** |
| Mg–Mg (inter-cluster) | 1.12 | 0 | 1.13 | 0 |

→ The Mg first shell is **octahedral [Mg₂(μ-Cl)₃·6THF]⁺** — each Mg bound by **3 bridging Cl
(0.25 nm) + 3 THF O (0.21 nm)** — and is **identical in both systems**. Anions associate as
**contact ion pairs through their Cl** (Mg–Cl_anion 0.24 nm), never through Al (no inner-sphere
Al). The peak positions/heights are superimposable poly vs bare.

## 2. Mg first-shell solvation statistics (mean ± sd)
| species | bare-APC | poly-APC |
|---|---|---|
| Cl (bridge) | 3.00 ± 0.00 | 3.00 ± 0.00 |
| O (THF) | 3.16 ± 0.37 | 3.16 ± 0.36 |
| O (polymer) | — | 0.01 ± 0.08 |
| Cl (anion) | 0.84 ± 0.38 | 0.80 ± 0.41 |
| **total (Cl+O)** | **6.16 ± 0.37** | **6.16 ± 0.37** |

- Dominant motifs (n_Cl, n_THF-O, n_polymer-O): **(3,3,0) ≈ 84 %**, (3,4,0) ≈ 16 % — i.e. 6-fold
  octahedral with a labile 4th THF, in **both** systems.
- **Contact ion pairing**: Mg with ≥1 anion-Cl contact = **83.3 % (bare)** vs **79.8 % (poly)**.
- **Polymer in the first shell**: only **0.6 %** of Mg ever contact a polymer O (CN 0.01).
- Representative structures extracted to `representative/*.pdb` (cation + first-shell species):
  `*_octahedral_3Cl3O` (canonical), `*_contact_ion_pair`, `poly_polymer_coordinated` (the rare
  polymer-contacting Mg).

## 3. Mg-cluster non-bonded interaction energies (short-range, kJ/mol)
Totals over all 80 cations (per-cluster in brackets = total/80):
| interaction | bare-APC | poly-APC |
|---|---|---|
| Mg-clust ↔ Anion (Coul) | −7793 (−97) | −7472 (−93) |
| Mg-clust ↔ Anion (LJ) | −3511 (−44) | −3539 (−44) |
| Mg-clust ↔ Solvent THF (Coul) | −1233 (−15) | −1189 (−15) |
| Mg-clust ↔ Solvent THF (LJ) | **−12110 (−151)** | **−8819 (−110)** |
| Mg-clust ↔ Polymer (Coul) | — | +4 (≈0) |
| Mg-clust ↔ Polymer (LJ) | — | **−3436 (−43)** |
| Mg-clust ↔ Initiator TMSOTf (Coul) | — | −654 (−8) |
| Mg-clust ↔ Initiator TMSOTf (LJ) | — | −152 (−2) |
| Mg-clust ↔ Mg-clust (Coul, repulsive) | +73942 | +73892 |

(Coul-SR + LJ-SR by energy-group decomposition; PME-reciprocal part is delocalised and excluded.)

## 4. Are there major differences between poly-APC and bare-APC?
**The primary Mg solvation is unchanged; the differences are in the outer environment and ion pairing — all modest.**

1. **First-shell coordination — no change.** [Mg₂(μ-Cl)₃·6THF]⁺ is intact and octahedral
   (3 Cl + 3 THF, total CN 6.16) in both. The polymer **does not enter the Mg first shell**
   (0.6 % contact, CN 0.01) and does not displace THF or Cl. The gel is an *inert matrix* around
   intact, bulk-like APC clusters — consistent with a swollen gel-polymer electrolyte.
2. **Contact ion pairing slightly weakened** in poly-APC: anion-Cl contact drops 83 → 80 % and the
   Mg-clust↔anion Coulomb weakens (−97 → −93 kJ/mol per cluster). The network modestly loosens
   cation–anion pairing — marginally favourable for Mg²⁺ availability.
3. **Solvent ↔ polymer substitution in the outer shell.** Because ~720 THF were polymerised into
   the network, poly-APC has fewer free THF, so Mg-clust↔free-THF van der Waals drops sharply
   (−151 → −110 kJ/mol per cluster). This is **compensated by Mg-clust↔polymer LJ (−43)** plus a
   small initiator term (−10). Net environment stabilisation per cluster is essentially conserved
   (bare ≈ −308; poly ≈ −316 kJ/mol summed over anion+solvent+polymer+initiator).

**Bottom line:** at this loading the polymer network behaves as a near-inert, THF-swollen scaffold:
it preserves the native APC Mg-cluster solvation, slightly reduces contact ion pairing, and takes
over part of the second-shell solvation from free THF without coordinating Mg directly.

## 5. Literature consistency
The simulated Mg cluster reproduces the established APC structure — a dimeric
[Mg₂(μ-Cl)₃·6THF]⁺ with each Mg octahedrally bound by 3 bridging Cl + 3 THF and a labile
exchanging THF, plus contact ion pairing — as reported from single-crystal XRD and AIMD/CMD:
- Canepa et al., *Energy Environ. Sci.* **8**, 3718 (2015) — MACC/APC structure.
- Multivalent-electrolyte solvation review, *Top. Curr. Chem.* (2018), PMC5920006.

## 6. Caveats
- Classical, non-polarisable FF with scaled Mg/Cl charges (effective energetics, not ab-initio).
- APC complexes are bonded entities → ligand exchange of the bonded 3 THF/Cl is suppressed
  (the *4th* THF and anion association are free and are what the statistics above sample).
- Interaction energies are short-range (PME-reciprocal not decomposed); use for comparison, not
  absolute binding free energies.

## Files
- `COMPARISON.md` — auto-generated comparison tables.
- `bare/`, `poly/` — `rdf/` (rdf_*.xvg, cn_*.xvg) and `solv_summary.txt`.
- `representative/*.pdb` — representative Mg solvation structures.
- Trajectories/topologies: `prod/{bare,poly}/prod.{tpr,xtc}` (50 ns), `index.ndx`.

---

# Addendum — Anion ([Ph₂AlCl₂]⁻) interaction energies & the cation/anion contrast

Extracted from the same energy-group decomposition (per-anion = total/80, kJ/mol):

| anion interaction | bare-APC | poly-APC |
|---|---|---|
| ↔ free THF (LJ) | **−69.3** | **−50.2** |
| ↔ free THF (Coul) | −7.8 | −5.9 |
| ↔ Polymer (LJ) | — | **−18.7** |
| ↔ Polymer (Coul) | — | −2.8 |
| ↔ Initiator TMSOTf (LJ) | — | −1.4 |
| ↔ Initiator TMSOTf (Coul) | — | −0.7 |
| ↔ Mg-cluster (Coul, SR†) | −97.4 | −93.4 |
| ↔ Mg-cluster (LJ) | −43.9 | −44.2 |
| ↔ other anions (Coul, SR†) | −328.6 | −328.7 |
| ↔ other anions (LJ) | −8.8 | −9.1 |

†Coul-SR between two *net-charged* groups (anion–anion, Mg–anion) is the short-range
real-space part only; the PME-reciprocal part (which carries the net like-charge repulsion)
is delocalised and not in these numbers — interpret charged–charged Coulomb cautiously.
LJ terms and Coulomb with the *neutral* partners (THF, polymer, initiator) are fully meaningful.

## The story: the cation is solvated electrostatically, the anion dispersively
1. **The anion is a van-der-Waals-solvated species.** Its environment is dominated by **LJ**
   (free-THF −69 kJ/mol per anion) with only small Coulomb to neutral solvent (−8). This is the
   opposite of the Mg cluster, whose key stabilisations are electrostatic (Mg–Cl, Mg–O, and the
   −93…−97 ion-pairing Coulomb with the anion). Physically sensible: [Ph₂AlCl₂]⁻ is large,
   charge-diffuse and hydrophobic (two phenyls + Cl), so it is "solvated" by dispersion.

2. **The gel matrix re-solvates the anion almost perfectly — by van der Waals.** Going bare→poly,
   the anion loses free-THF LJ (−69 → −50, i.e. −19) and recovers essentially all of it from the
   **polymer (−18.7)** + initiator (−1.4): total vdW environment −69.3 (bare) ≈ **−70.3 (poly)**.
   Same pattern as the Mg cluster, but for the anion it is almost exclusively a vdW handover.

3. **The hydrophobic anion has the higher per-atom affinity for the (hydrophobic) network.**
   Polymer–anion LJ = **−0.75 kJ/mol per anion atom** vs polymer–Mg-cluster LJ = **−0.52 per
   cluster atom** — the phenyl-rich anion "wets" the POSS/poly-THF scaffold ~45 % more strongly
   per atom than the THF/Cl-clad cation does. (Both ions are equally *embedded* in the
   space-filling gel — 72/80 anions and 77/80 clusters lie within 0.45 nm of the network — so the
   distinction is energetic, not just geometric.)

4. **Consequence for the electrolyte.** The network is electrostatically near-silent toward both
   ions (Coul with polymer ≈ −3 anion, ≈ 0 cation) and acts as a **dispersive host that
   preferentially accommodates the anion** while leaving the Mg cluster a discrete,
   electrostatically-solvated, mobile [Mg₂Cl₃·6THF]⁺. Combined with the slightly weakened Mg–anion
   contact pairing (§2 main report), this is exactly the microscopic picture by which a
   hydrophobic gel matrix can immobilise/retain the bulky anion relative to the cation —
   the structural basis for improved Mg²⁺ transference in gel-polymer Mg electrolytes.

---

# Addendum 2 — Diffusion (MSD) & transference test

COM mean-squared-displacement diffusion coefficients (`gmx msd`, per-molecule COM for ions,
Einstein fit 5–30 ns of the 50 ns trajectories):

| species | bare-APC D | poly-APC D | slowdown |
|---|---|---|---|
| Mg-cluster [Mg₂Cl₃·6THF]⁺ (cation, +1) | 0.088 | 0.016 | **×5.4** |
| [Ph₂AlCl₂]⁻ (anion, −1) | 0.097 | 0.018 | **×5.3** |
| THF (solvent) | 1.12 | 0.41 | ×2.8 |

*(D in 10⁻⁵ cm² s⁻¹.)* Ideal transference number **t₊ = D₊/(D₊+D₋) = 0.475 (bare) → 0.471 (poly).**

## Verdict on the transference hypothesis — *not supported* (hypothesis tempered)
- **The gel slows everything, but does not discriminate cation vs anion.** Both ions slow by the
  *same* factor (~5.3–5.4×) on gelation, so **t₊ is essentially unchanged (~0.47)**. The solvent
  slows less (×2.8) because small THF threads through the network more easily than the bulky ion
  clusters.
- **So the energetic preference does *not* become a kinetic one.** The polymer's higher *per-atom*
  vdW affinity for the anion (Addendum 1) does **not** translate into preferential anion
  immobilisation — because both ions are equally *embedded* in the space-filling poly-THF/POSS
  network, which is chemically akin to the THF solvent and offers **no anion-specific anchoring
  sites**. It raises the medium viscosity roughly uniformly.
- t₊ < 0.5 in both (anion-dominated transport): the anion is more compact than the bulky
  six-THF-solvated dinuclear cation, so it is intrinsically the faster ion.

**Refined conclusion.** This poly-THF/POSS gel acts as an inert, viscosity-raising scaffold: it
preserves APC speciation, slightly loosens ion pairing, re-solvates both ions by van der Waals,
and **slows cation and anion equally → no Mg²⁺-transference gain**. Improving t₊ would require a
matrix with *anion-selective* binding (e.g., Lewis-acidic boron/aluminium anion receptors), not a
generic hydrophobic network.

**Caveats (important here):** 50 ns is short for a viscous gel — ions displace only ~1.5–3.6 nm,
so poly-APC D values are approximate and may be mildly sub-diffusive (Einstein fit → upper bound);
trestart = save-interval (statistics not fully independent). The *trend* (equal cation/anion
slowdown, unchanged t₊) is robust; absolute D and t₊ carry sizeable uncertainty. Longer runs and
replicas would tighten these.

---

# Addendum 3 — Tightened diffusion from 3×100 ns replicates

Replacing the single 50 ns estimate: **3 independent 100 ns replicates per system**
(rep1 extended + rep2/rep3 fresh velocities), COM-MSD with a longer **20–80 ns** Einstein
fit; D reported as **mean ± SEM across the 3 replicates**.

| species | bare-APC D | poly-APC D | slowdown |
|---|---|---|---|
| cation [Mg₂Cl₃·6THF]⁺ | **0.051 ± 0.004** | **0.0114 ± 0.0015** | ×4.5 |
| anion [Ph₂AlCl₂]⁻ | **0.050 ± 0.005** | **0.0118 ± 0.0023** | ×4.2 |

*(D in 10⁻⁵ cm² s⁻¹.)*

**Transference number t₊ = D₊/(D₊+D₋):  bare 0.505 ± 0.011  ·  poly 0.496 ± 0.014**

## Conclusion (now with error bars) — confirmed, and sharper
- **t₊ ≈ 0.50 in both systems, statistically indistinguishable** (0.505±0.011 vs 0.496±0.014):
  **the gel produces no Mg²⁺-transference gain.** This confirms the 50 ns result, with proper
  uncertainties.
- **Both ions slow by the same factor on gelation** (cation ×4.5, anion ×4.2 — equal within error):
  the poly-THF/POSS network raises viscosity uniformly; it does **not** differentially immobilise
  the anion despite its higher per-atom vdW affinity for the matrix (Addendum 1).
- With the better statistics, **D₊ ≈ D₋ within error** in both systems — the slight "anion-faster"
  hint from the single 50 ns run (t₊≈0.47) washes out; cation and anion diffuse at the same rate.
- Note the longer 20–80 ns fit window gives **lower absolute D** than the earlier 5–30 ns fit
  (0.05 vs ~0.09 bare; 0.011 vs ~0.017 poly) — the longer window samples the true diffusive
  regime and is the more reliable estimate; the *ratios and t₊* are robust to the window.

**Final verdict on transference:** raising the matrix viscosity (this generic poly-THF/POSS gel)
slows transport ~4–5× but does not change t₊ (~0.5). Improving Mg²⁺ transference requires an
**anion-selective** matrix (Lewis-acidic anion receptors), not a generic hydrophobic network.

---

# Addendum 4 — POSS-loading scan: does more crosslinker amplify ion-pair loosening?

Built a **16-POSS** variant (4× crosslinker, same 80/80 electrolyte, scaled initiator),
cured to **100% epoxide conversion + single connected network**, 30 ns NVT production,
contact-ion-pairing analysed over the last 20 ns.

| system | POSS | Mg–anion contact | Mg–anion CN | free THF | Mg–polymer-O contact | Mg↔anion Coul (per-cluster) | Mg↔polymer (Coul/LJ) |
|---|---|---|---|---|---|---|---|
| bare   | 0  | **83.3%** | 0.84 | 2120 | — | −97 | — |
| poly   | 4  | **79.8%** | 0.80 | 1399 | 0.6% | −93 | ≈0 / −43 |
| poly   | 16 | **58.8%** | 0.59 | 1220 | **5.0%** | **−69** | **−5.5 / −63** |

**Yes — de-pairing is strongly amplified** at 16 POSS: Mg–anion contact drops 80%→59%, and the
short-range Mg–anion Coulomb weakens −93→−69 kJ/mol per cluster. Two independent observables agree.

**Mechanism (revealed by the scan):** it is *not* the inert hydrophobic matrix per se — it's the
**oxygens from the opened glycidyl groups** (ether + hydroxyl) plus poly-THF backbone ethers
*coordinating Mg and screening/displacing the anion*. Evidence: Mg–polymer-O first-shell contact
rises 0.6%→5.0%, Mg↔polymer gains a real Coulomb term (≈0→−5.4) and stronger LJ (−43→−65), and the
Mg O-coordination rises (3.16→3.30 THF-O, total CN 6.16→6.35). At 16 POSS × 100% conversion there
are ~128 opened-glycidyl oxygens — enough cation-coordinating sites to matter. This matches the
earlier prediction that the *reliable* lever is cation-coordinating functionality, which the
glycidyl-derived O provide once abundant.

**Not a desolvation artefact:** free THF *decreased* (2120→1399→1220), which would push pairing
*up*; de-pairing occurs despite that, so the effect is genuine (and conservative).

**Caveats (important):**
- **Single 50 ns trajectory, not replicated** — the effect is large (24-point drop, 26 kJ/mol) so
  likely real, but a replicated run would firm up the magnitude.
- **Confounded with conversion/cure protocol:** the 4-POSS point was 69%-converted (even-dist cure);
  the 16-POSS is 100%-converted (full cure). So the jump reflects *loading × conversion* (i.e. the
  number of opened-glycidyl coordinating oxygens), not pure POSS count. A clean isolation would
  re-cure 4-POSS at 100% with the same protocol.
- Model caveats as before (scaled charges; SR-only Coulomb for charged pairs).

**Take-away:** the effect amplifies with crosslinker loading because curing the glycidyl-POSS
generates Mg-coordinating ether/OH oxygens; at high loading these compete with the anion and
substantially loosen contact ion pairing (80%→59%).

*(Updated: 16-POSS now run to **50 ns**, analysed over the last 40 ns / 32 160 samples — same protocol as bare & 4-POSS. Contact pairing 58.8% (was 56.3% on the shorter 30-ns window); trend unchanged.)*
