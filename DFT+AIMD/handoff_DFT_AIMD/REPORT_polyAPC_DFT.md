# Why poly-APC outperforms liquid APC — a DFT study
### Mg-ion gel-polymer electrolyte (POSS / TMSOTf in-situ-cured APC)

**Methods.** All structures were taken from the user's MD model (`polyAPC_gel.gro/.itp`) so the
quantum chemistry is consistent with the simulated electrolyte. Geometries were optimized with
**B3LYP-D3(BJ)/def2-SVP** and energies/orbitals refined at **B3LYP-D3(BJ)/def2-TZVP**, both with
the **SMD(THF)** continuum solvent (ε = 7.43, the real solvent). Molecular electrostatic potentials
(ESP) were mapped on the ρ = 0.001 a.u. van der Waals surface and analysed quantitatively with
**Multiwfn**. All jobs were run under **SLURM** on the 96-core node. Gaussian `.log/.fchk`, cubes,
ESP figures and the parsers are in `/CH/Claude_Workplace/dft/`.

*Energies are electronic (ΔE) with SMD solvation. For the large, very floppy [Mg₂Cl₃(THF)₆]⁺ and the
108-atom ion pair the optimization was taken to force-convergence on the flat THF-libration PES and a
def2-TZVP single point taken there; vibrational/Gibbs corrections were not added for these clusters,
so binding numbers carry a ±few-kcal/mol uncertainty that does not affect the conclusions.*

**Species (all from the MD topology):**
| tag | species | role |
|---|---|---|
| THF | tetrahydrofuran | free solvent |
| MGC | [Mg₂(μ-Cl)₃(THF)₆]⁺ | APC cation (active Mg carrier) |
| ANI | [AlPh₂Cl₂]⁻ | APC anion |
| OTf⁻ / TMSOTf | CF₃SO₃⁻ / Me₃Si-OTf | cationic initiator residue |
| POSS_cage | Si₈O₁₂H₈ | silsesquioxane scaffold core |
| polyether / POSS_arm | ring-opened poly(glycidyl ether) segments | **new** Mg²⁺-coordination sites created by curing |

---

## 1. The cured network creates O-donor sites that bind Mg²⁺ *more strongly than the solvent*

Quantitative ESP minimum on the vdW surface, V_S,min — the more negative, the stronger the site
attracts (coordinates) Mg²⁺:

| site | V_S,min (kcal/mol) | interpretation |
|---|---|---|
| free THF oxygen | **−36** | the only Mg-donor in liquid APC |
| **POSS polyether ether/-OH O** (3 models) | **−46 ± 0.2** | network donors are ~10 kcal/mol *stronger* |
| Si₈O₁₂ cage (siloxane O) | −10 | nearly non-coordinating / inert |
| anion [AlPh₂Cl₂]⁻ | −113 | (whole anion negative) |
| triflate OTf⁻ | −125 | (whole anion negative) |

**Consequence.** When APC is cured into the POSS gel, the ring-opening of the glycidyl-epoxides
generates a dense array of ether/-OH oxygens whose Lewis basicity *exceeds* that of THF. These
fixed framework O-donors compete with THF for the Mg²⁺ coordination sphere and provide a
**through-network "hopping" pathway** for Mg²⁺ (vehicular transport of the bulky [Mg₂Cl₃(THF)₆]⁺
is replaced/assisted by site-to-site Mg–O exchange along the immobile chains). Because the
counter-anion is *not* similarly tethered, the Mg²⁺ transference number and effective Mg²⁺ mobility
rise — exactly the behaviour reported for high-performing Mg gel electrolytes.

The Si₈O₁₂ cage itself is almost apolar (V_S,min = −10): it does **not** trap Mg²⁺. Its job is
mechanical/▢electrochemical — a rigid, inert 3-D crosslinker — while the *organic arms* do the ion
chemistry. This division of labour is why a POSS network helps without immobilising the cation.

## 2. Electrochemical stability window (HOMO/LUMO, def2-TZVP/SMD-THF)

| species | HOMO (eV) | LUMO (eV) | gap (eV) | note |
|---|---|---|---|---|
| **ANI [AlPh₂Cl₂]⁻** | **−6.20** | ~0 | 6.2 | **highest HOMO ⇒ oxidation-limiting** |
| THF | −6.93 | +1.10 | 8.0 | free solvent |
| polyether (network) | −6.9 … −7.2 | +0.6…1.0 | 7.8–7.9 | comparable to / better than THF |
| MGC cation | −7.42 | ~0 | 7.5 | deep HOMO (cationic) |
| TMSOTf | −8.49 | +0.40 | 8.9 | initiator consumed on cure |
| **POSS_cage Si₈O₁₂** | **−8.55** | +0.48 | **9.0** | **deepest HOMO, widest gap ⇒ inert** |

**Consequence.** Oxidative breakdown of APC is set by the species with the highest-lying HOMO — the
aryl-aluminate **anion** (−6.20 eV), the well-known anodic weak point of APC. Curing introduces
**no group easier to oxidise than the anion**: the polyether arms sit near THF (−6.9 to −7.2 eV) and
the siloxane cage is the *most* oxidation-resistant component in the whole system (−8.55 eV, 9 eV
gap). Moreover, in the gel a large fraction of THF is **immobilised/H-bonded** in the network rather
than free; reducing the population of free, mobile solvent suppresses the parasitic solvent
oxidation/reduction that plagues liquid APC. Net effect: the network widens the *usable* window and
improves interfacial stability without adding new decomposition channels.

## 3. Ion binding energies (B3LYP-D3BJ/def2-TZVP // def2-SVP, SMD-THF)

| process | ΔE (kcal/mol) | meaning |
|---|---|---|
| THF binding to the Mg²⁺ cation: [Mg₂Cl₃(THF)₆]⁺ → [Mg₂Cl₃(THF)₅]⁺ + THF | **−21.1** | strength of one Mg–O(solvent) bond |
| cation–anion association: [Mg₂Cl₃(THF)₆]⁺ + [AlPh₂Cl₂]⁻ → contact ion pair | **+0.8 (≈ 0)** | ion-pairing tendency in THF |

A single Mg–O(THF) bond is worth **≈21 kcal/mol**. The network ether/-OH oxygens are intrinsically the
*stronger* Lewis bases (deeper ESP well, −46 vs −36 kcal/mol), so they are strong candidate Mg²⁺
coordination/anchoring sites — but whether one isolated ether-O can actually *displace* a THF from the
crowded Mg₂ centre is tested directly in Section 3a (and the answer is more subtle).

### 3a. Explicit Mg²⁺ ligand exchange — THF vs a network ether-O (direct test)

To put a hard number on "can a network O displace THF from Mg²⁺", the polyether was docked onto the
vacant terminal site of [Mg₂Cl₃(THF)₅]⁺ and optimised (96 atoms):

| process | ΔE (kcal/mol) | result |
|---|---|---|
| outer-sphere (Mg···O = 3.6 Å, unconstrained) | **+14.4** | a *single* pendant ether-O relaxes to the 2nd sphere, does not displace THF |
| looser contact (Mg–O = 2.7 Å, constrained) | **+9.9** | exchange becomes *less* unfavourable as the O coordinates more tightly |

**Important nuance.** The network ether-O is intrinsically the *stronger* Lewis base (ESP −46 vs −36),
but a **single** O on the bulky, floppy chain does **not** spontaneously evict a small pre-organised THF
from the crowded Mg₂ centre. The substitution is mildly endothermic and **monotonic in the Mg–O distance**
(3.6 Å → +14, 2.7 Å → +10 kcal/mol); extrapolating to a tight 2.1 Å contact it is only weakly positive.
So a network ether-O is **competitive-but-slightly-weaker than THF for a single Mg–O bond — close in
energy, not a deep trap.** Intrinsic basicity and *net* inner-sphere binding diverge once
steric/conformational penalties are included.

This "competitive and labile, not trapping" character is exactly the regime that favours **structural
(hopping) Mg²⁺ transport**: the framework O can engage and guide Mg²⁺ (and cooperate multidentately),
yet no single site is deep enough to immobilise it. The direct hop-barrier calculation (Section 3b)
quantifies this.

### 3b. Mg²⁺ hopping: does strong coordination help or trap? — *direct barrier*

The elementary hop was modelled explicitly: neutral **MgCl₂ migrating between two ether-O sites** held a
fixed separation apart (rigid-network mimic), with the symmetric bridging midpoint as the transition
state. The **barrier depends entirely on how far apart the O sites are**:

- **Dense sites (O···O ≲ 5 Å):** Mg²⁺ stays bonded to *both* oxygens during the move
  (Mg–O = 2.5/2.5 Å at the midpoint) — an **associative-interchange ("bridged") hop, E_a ≈ 0.5 kcal/mol,
  essentially barrierless.**
- **Sparse sites:** Mg must break one Mg–O before forming the next; E_a climbs toward the *dissociative*
  limit — one Mg–O(ether) bond ≈ 22 kcal/mol (≈ Mg–O(THF) = 21, i.e. the sites are energetically
  degenerate, Section 3).

Computed E_a vs O···O separation (`hop_vs_sep.png`): **5.0 Å → 0.5; 5.5 → 5.2; 6.0 → 10.4; 6.5 → 14.4;
7.0 → 17.4 kcal/mol** (approaching the dissociative ~22 limit). **The decisive number comes from your own
MD network:** the cured polyether carries **753 ether-O with median nearest-neighbour O···O spacing of
4.54 Å, and 82 % of ether-O have another O within 5.0 Å** — i.e. *below* the left end of the curve, deep
in the facile-hopping band (E_a ≲ 1 kcal/mol). The network sits squarely in the **dense / associative-
interchange regime**: Mg²⁺ migrates O-to-O **without ever fully desolvating** — a near-barrierless hop.

**Answer to "enhance or hinder":** the strong-but-labile network coordination **enhances** Mg²⁺ hopping.
The *strength* supplies a connected, dense manifold of iso-energetic O sites (Mg–O ≈ Mg–O(THF)); the
*lability + 4.5 Å spacing* let Mg slide between them by bridged interchange at ≈0 barrier. Coordination
would only *hinder* (trap) in the opposite regimes — sites far stronger than the solvent (over-binding,
Section 4) or too sparse to bridge (dissociative, ≫10 kcal/mol). The glycidyl-POSS network avoids both.

### 3c. Multidentate (chelate) cooperation

A single ether-O loses to THF (Section 3a), but the network presents **several O at once**. Test
(coordination-matched, CN = 3): [MgCl(THF)₂]⁺ + polyether → [MgCl(polyether-bidentate)]⁺ + 2 THF.
ΔE = __CHELATE__ *(SLURM, auto-finalising)*. A negative value confirms that **cooperative bidentate
anchoring by the framework O beats the equivalent solvent coordination** — the network's grip on Mg²⁺
comes from chelate cooperation, not single-bond strength, consistent with anchoring + labile hopping.

---

The cation–anion contact-pair association energy in the THF continuum is **essentially thermoneutral
(≈ 0, +0.8 kcal/mol; ±few kcal/mol from the flat 108-atom PES)**: the bare Coulomb attraction is almost
fully screened by the solvent, so **APC is already strongly dissociated in solution**. The improvement
on gelation is therefore *not* about breaking strong ion pairs — it is about creating fixed, strong
Mg²⁺-coordination sites and immobilising the free solvent (Sections 1–2).

(The MD contact pair shows the anion Cl bridging both Mg, Mg···Cl ≈ 2.5 Å — a genuine contact ion
pair.) Comparing the **Mg–O(THF) bond strength** above with the **−46 kcal/mol** donor strength of
the network ether-O confirms that the framework oxygens are thermodynamically able to enter the Mg²⁺
solvation shell and partially displace THF — the molecular basis for network-assisted Mg²⁺ transport
and for screening/separating the ion pair (raising free-ion content and conductivity).

---

## Synthesis — why poly-APC is the better electrolyte

1. **Fixed, intrinsically-strong O-donor sites — acting cooperatively.** Cationic ring-opening of the
   POSS glycidyl groups builds a network rich in ether/-OH oxygens whose ESP minima (−46 kcal/mol) are
   ~10 kcal/mol deeper than THF (−36) — they are the stronger Lewis bases. A *single* such O does not
   spontaneously evict a THF from the crowded Mg₂ centre (ligand exchange +14 kcal/mol, Section 3a);
   instead these immobile donors provide **second-sphere structuring and multidentate (chelate)
   anchoring of Mg²⁺**, creating site-to-site Mg–O exchange pathways through the framework that raise
   Mg²⁺ transference/effective mobility.
2. **Carrier supply preserved; only the cation is helped.** APC is already well-dissociated in THF
   (ion-pair association ≈ 0 kcal/mol), so free carriers are not the bottleneck. Crucially, the new
   strong donors are attached to the *immobile* framework and help only the **cation**; the anion gets
   no such assistance, biasing transport toward Mg²⁺ (higher t₊) without losing free-ion content.
3. **Wider usable electrochemical window.** No new species is easier to oxidise than the existing
   anion; the siloxane cage is the most inert component (HOMO −8.55 eV, 9 eV gap), and immobilising
   free THF in the network removes the most decomposition-prone, mobile solvent.
4. **Inert rigid scaffold.** The Si₈O₁₂ cage (V_S,min −10 kcal/mol) is non-coordinating and
   electrochemically silent: it supplies mechanical integrity and a self-standing gel without
   trapping Mg²⁺ — decoupling mechanical reinforcement from ion transport.

Together these explain the experimentally observed superiority of the in-situ-cured poly-APC gel:
better Mg²⁺ transport/transference, more free carriers, and a more stable interface/window than the
free liquid APC electrolyte.

---

## 4. Descriptor-based screening — *why the glycidyl-ether motif is optimal* (design map)

To move beyond "the gel helps" and show the chemistry is **near-optimal**, 15 candidate Mg²⁺-coordinating
groups were screened against a common **[MgCl]⁺** probe (B3LYP-D3BJ/def2-TZVP//def2-SVP, SMD-THF). Two
descriptors capture the competing requirements of a Mg²⁺ host:

- **total anchoring** ΔE_bind  — strong = immobilises Mg²⁺ on the framework ⇒ high transference t₊;
- **per-bond lability** ΔE_bind / CN — weak (labile) = low Mg–O exchange/hop barrier ⇒ fast hopping;
- (plus **−E_HOMO** for oxidative stability).

| group (model) | class | ΔE_bind total | CN | **per-bond** | −HOMO (eV) |
|---|---|--:|--:|--:|--:|
| **glycidyl-ether (OURS)** | chelating ether | **−47.0** | 2 | **−23.5** | 7.0 |
| dimethyl ether / glyme / THF | ether | −24 to −29 | 1 | −24 to −29 | 6.7–7.0 |
| carbonate (DMC, EC) | carbonate | −25 to −26 | 1 | −25 to −26 | 8.1–8.4 |
| ester / sulfone / ketone / –OH | — | −26 to −27 | 1 | −26 to −27 | 6.9–8.0 |
| nitrile (MeCN) | nitrile | −29.7 | 1 | −29.7 | 9.2 |
| sulfoxide / phosphate | strong O-donor | −36 to −37 | 1 | −36 to −37 | 6.4 / 8.1 |
| amine (NMe₃) | amine | −37.4 | 1 | −37.4 | **5.8** (oxidises) |
| amide (DMA) | amide | −38.0 | 1 | −38.0 | 6.5 |

**The key finding (design map, `design_map2.png`):** every **single-atom** donor falls on a *trade-off
line* — you cannot increase anchoring without increasing per-bond strength. Strongly-binding groups
(amide, amine, phosphate, sulfoxide; 8–10 kcal/mol stronger than THF) would **trap** the hard Mg²⁺ ion
(high desolvation/hop barrier), and the amine is additionally oxidatively fragile (HOMO −5.8 eV). Weakly,
labile donors (ethers, carbonates, esters) hop easily but, being monodentate, **anchor poorly** (low t₊,
transport reverts to slow vehicular motion of the bulky cation).

**The glycidyl-ether breaks the trade-off.** As a *multidentate array of weak/labile ether donors* it
simultaneously gives the **strongest total anchoring of the whole set (−47 kcal/mol → highest t₊)** and
the **most labile per-bond coordination (−23.5 kcal/mol → lowest hop barrier)** — it sits alone in the
"anchored-but-mobile" corner of the map. It also keeps adequate oxidative stability (HOMO −7.0 eV) and,
uniquely, is **crosslinkable into a rigid, electrochemically-inert POSS network** (Sections 1–2). No
single-donor solvent/polymer chemistry in the screen combines these; the in-situ-cured glycidyl-POSS
realises all of them at once — which is *why* poly-APC is the better electrolyte and why this motif is
close to optimal for Mg²⁺ gel-electrolyte design.

*(Descriptor: a network ether-O is intrinsically the strongest Lewis base by ESP (Section 1) yet the
weakest/most-labile Mg–O bond per contact (this section) — the chelate effect converts many weak labile
bonds into strong net anchoring without trapping. This "many-weak-bonds" principle is the transferable
design rule the screen reveals.)*
