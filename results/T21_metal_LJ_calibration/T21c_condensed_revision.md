# T21c — condensed-phase revision of the MgEl wall (fixes the GPU "frozen near-surface" finding)

**Node:** EPYC (CPU/DFT) · **Date:** 2026-06-27 · **Status:** ✅ RESOLVED

---
## ⚠️ UPDATE (T21c-quant, 2026-06-27) — Mg-O QUANTIFIED → O reverted to the two-body potential
The first pass below reduced **O 53.2 → 26** (ΔG_ads). After quantifying Mg-O on the CPU and noting the
interface MD is **explicit-liquid**, that was an **over-correction** and is **reverted**. Cl (132.7 → 3.738,
image stripped) **stands**. Summary:

| quantity | value | how | role |
|---|---|---|---|
| two-body Mg-O potential | **−0.668 eV** (TZVPP+BSSE @2.2 Å; raw TZVPP −0.735 @2.28 Å, BSSE 0.056) | `mgO_quantify.py` over the **TZVPP** slab+THF scan (`tz_sTHF_*`, replaces DZVP) + counterpoise ghost CP | **the pair LJ ε** (→ 53.2) for explicit liquid |
| frustrated stretch | ν ≈ **111 cm⁻¹** | curvature of the TZVPP well (rigid THF, m=72) | — |
| **ΔG_ads(liquid)** | **−0.27 eV ≈ 26 kJ/mol** | −0.668 eV + Campbell–Sellers (−TΔS=+35.1, S_gas=300.8 J/mol·K from g16 freq) + ΔG_vap(+3.7) | **emergent PMF / validation target — NOT ε** |

**Why ε stays 53.2 (two-body), not 26 (ΔG_ads):** in an explicit-liquid MD the solvent generates the
desolvation + entropy itself, so the pair LJ must be the two-body potential; baking ΔG_ads into ε
double-counts → under-binds. **The frozen monolayer is REAL:** the observed *90 % no-desorb/12 ns@400 K*
requires a barrier ~0.4–0.55 eV = the two-body well (ΔG_ads's 0.26 eV → τ~2 ns@400 K → would NOT freeze).
Mg–O is a genuine ~0.5 eV bond. The anion lever is **Cl** (stripped), not the THF O bond; residual anion
slowness = a **sampling** problem (enhanced sampling / direct anion PMF). A mobility-prioritized O ε≈26–40 is
a documented fallback only if a GPU near-wall O-density profile shows the non-saturating 12-6 over-binds a
spurious *multilayer* (vs the 1 real chemisorbed layer). Inputs: `T21c_inputs/{mgO_quantify.py, thf_gas2.gjf, tz_scan_energies.txt}`.

**Basis note (2026-06-27):** the binding scan was re-run at **TZVPP** (TZV2P-MOLOPT-PBE-GTH, replacing the
illustrative DZVP single-points). Raw TZVPP well −0.735 eV @2.28 Å; counterpoise BSSE 0.056 eV → **−0.668 eV**
(identical to the prior TZVPP+BSSE anchor). ν 118→**111 cm⁻¹**. ε(53.2), ΔG_ads(−0.27 eV) and every conclusion
are **unchanged** — already TZVPP+BSSE-anchored; the scan upgrade just makes the curve self-consistent.

*(The first-pass reasoning below is retained for the record; the O-specific "use 26" conclusion is superseded
by this update. The Cl analysis is unchanged and correct.)*
---

**Node:** EPYC (CPU/DFT) · **Date:** 2026-06-27 · **Status:** ✅ RESOLVED (O reverted per the update above)
**Trigger:** GPU (LYZ-ROG) T21c — the calibrated wall (MgEl-O 53.224 + MgEl-Cl 132.713 kJ/mol)
**freezes the first solvation layer** (first-layer THF 4.5× less mobile, 90% never desorb over 12 ns @ 400 K;
residence ~μs at 298 K) → the per-face anion metric cannot equilibrate (bare control stuck asymmetric).

## Diagnosis — both well depths CONFIRMED to over-bind in the condensed phase
The original O/Cl values are **static single-adsorbate** numbers (correct as such) **misapplied as
condensed-phase LJ wells** for a dynamics run.

### MgEl-O — vacuum binding, not adsorption free energy
ε=53.224 kJ/mol encodes the DFT **vacuum** single-THF binding (−0.668 eV, TZVPP+BSSE). In liquid THF the
relevant quantity is the **adsorption free energy** ΔG_ads. Thermodynamic cycle:

    ΔG_ads = ΔE_bind(vacuum)  +  desolvation penalty       +  (−TΔS_ads)
           = −0.668 eV        +  (0.5–1.0)·ΔH_vap(THF)      +  (+0.10 to +0.20 eV)
           = −0.668 eV        +  (+0.17 to +0.33 eV)        +  (+0.10 to +0.20 eV)
           ≈ −0.27 eV  (range −0.20 to −0.35)  ≈  24–34 kJ/mol

(ΔH_vap(THF) = 31.99 kJ/mol = 0.332 eV, experimental.) Plus a **saturation** point: a 12-6 LJ does not
saturate, but chemisorption is a single monolayer — a deep non-saturating well keeps binding every approaching
O, piling up the layer. **Recommended condensed-phase ε(Mg-O) ≈ 26 kJ/mol (0.49×).** σ unchanged (0.18410 nm).
This coincides with the GPU's independent 0.5× sensitivity test (O→26.6).

### MgEl-Cl — image charge lumped into a short-range site well
ε=132.713 kJ/mol (σ 0.18586) LUMPED the ion–metal **image charge** into a deep short-range well. The real
image potential is **long-range (r⁻¹) and laterally flat** (depends only on the surface-normal distance z), so
it lets the ion **slide** along the surface; the lumped short-range *site* well **over-localizes** → freezes
the adsorbed anion. For the neutral solvent-structure wall the image lumping is **removed** and Mg-Cl is set to
**bare D3 dispersion** (new dimer `B_cross/d3_MgCl`, E_disp(5 Å) = −3.6535e-4 Ha, same protocol as C/Si/S):

    σ(Mg-Cl) = √(σ_Mg·σ_Cl) = √(0.29436·0.340) = 0.31636 nm
    ε(Mg-Cl) = 3.738 kJ/mol            (vs 132.713 — a ~35× reduction)

The anion–metal electrostatic attraction (image charge / reductive plating) is **out of scope for a neutral
fixed-charge LJ wall** → it stays in the MLFF / constant-potential reference (where the T17 MACE+LES
charged-interface verdict already lives).

## Revised wall (condensed-phase dynamics)
| pair | OLD (froze) | **NEW** | note |
|---|---|---|---|
| MgEl–O  | 0.18410 / 53.224  | **0.18410 / 26.000** | ΔG_ads estimate (range 24–34) |
| MgEl–Cl | 0.18586 / 132.713 | **0.31636 / 3.738**  | D3 dispersion-only; image stripped |
| H,C,Si,S,F | (unchanged) | (unchanged) | already weak vdW, do not freeze |

Delivered in `computational_v2/mlff/incoming/mg_electrolyte_nbfix.itp` and the mapped
`results/T21_metal_LJ_calibration/gpu_build/mg_nbfix.itp` (opls_O*/opls_CL*).

## What this means (honest)
- The classical T21 wall is a **solvent-structure model**. With the condensed O/Cl it should **not** freeze →
  the bare control should reach A=B (symmetric). **GPU: re-run the bare control.**
- If the structural poly-vs-bare anion signal **survives** the de-frozen wall → real solvent-structure
  exclusion; if it **vanishes** → it was a freezing artifact and the verdict rests on the MLFF. Either is
  informative.
- ΔG_ads here is a thermodynamic-cycle **estimate**; a one-THF-off-Mg(0001) **PMF in liquid THF** (GPU) would
  pin it precisely. The −0.668 eV vacuum binding remains correct as a static number.

## Files
- `B_cross/d3_MgCl.inp` / `.out` — Mg-Cl D3 dimer (LSD, mult 2; D3 term is geometry-only).
- `B_cross/c6_mgcl.py` — C6→LJ conversion (reproduces the committed Mg-S 0.32326/3.556 as a check).
