# D4-proxy (cation transparency) — Tier-1 result

**Descriptor D4-proxy** (pre-reg §4): group→Mg²⁺ binding energy **vs** THF→Mg²⁺.
**PASS** = network donor binds Mg²⁺ **weaker** than THF (does not strip cation solvation; transport untouched).

## Method
B3LYP-D3(BJ)/def2-SVP, **SMD(THF)**, opt (g16). Bare Mg²⁺ is ill-posed in SMD, so the descriptor is
cast as a **ligand-exchange** that cancels the bare cation:

> [Mg–THF]²⁺ + L → [Mg–L]²⁺ + THF  ΔE_exch = [E(Mg–L)+E(THF)] − [E(Mg–THF)+E(L)]

ΔE_exch > 0 ⟹ L binds Mg²⁺ **weaker** than THF ⟹ **PASS D4** (transparent).

## Energies (Ha, dispersion-incl. final SCF)
| species | E (Ha) |
|---|---|
| THF | −232.293498 |
| Me₂O (ether donor) | −154.918302 |
| disiloxane (siloxane donor) | −657.689441 |
| [Mg–THF]²⁺ | −432.050524 |
| [Mg–Me₂O]²⁺ | −354.668266 |
| [Mg–disiloxane]²⁺ | −857.423415 |

## Result
| donor (proxy for) | ΔE_exch (kcal/mol) | verdict |
|---|---|---|
| **siloxane-O** (POSS / silsesquioxane) | **+14.47** | **PASS — strongly transparent** |
| **ether-O** (polyether-siloxane) | **+4.43** | **PASS — but marginal** |

**Gap = 10.0 kcal/mol.** Both donors bind Mg²⁺ *weaker* than THF (both formally PASS D4), but the
**siloxane-O is ~10 kcal/mol more transparent than ether-O**. Siloxane-O is a poor Lewis base (lone pairs
delocalize into Si σ*/d, near-linear Si–O–Si) → POSS does not compete with THF for the cation → transport
untouched (consistent with t₊=0.50 both, D≈8–9×10⁻¹⁵; transport is **not** the discriminator). Ether-O is
nearly as good a Mg²⁺ donor as THF itself (THF is a cyclic ether) → a polyether-rich network sits close to the
"strips solvation" line.

**Design-rule payload (confirms predicted ether risk):** the polyether-siloxane passes D2 (=SiO₂, 3.07 eV) but
is the **marginal** network on the transparency axis — siloxane (POSS) is the safer D4 choice. Recorded as a
falsifiable nuance, not a fail.
