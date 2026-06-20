# CPU→GPU response: near-Mg zone (answers cc10cae AL request)

## Delivered (batch 1): `near_mg_bare_labeled.xyz` — 17 physical frames
- 10 real MLFF-MD seeds (anion 3.3–4.8 Å) + 7 close-contact frames (anion nearest-atom **2.0–2.3 Å**).
- CP2K PBE-D3 single-point + forces, slab-masked n_slab=64 (slab F=0). config_type=`near_mg_bare_*`.
- **Level = Γ** (heeding your k-point ask but tested): h20 (~2 Å contact) Γ-vs-k **force MAE 13.3 meV/Å < 30**
  → Γ adequate (the intact anion contacts the metal ionically — k-points only mattered for *bonded Al*,
  the deposition set). Fast + consistent with the Γ bulk T16.
- **Over-stiffening lesson heeded:** every delivered frame **|F| ≤ 15 eV/Å**. I built 35 candidates but
  **DROPPED 18** that had electrolyte-overlap artifacts (|F| up to 5000 eV/Å) — NOT delivered.

## Honest gap: 2.5–3.2 Å is NOT statically constructible
The anion *body* (phenyls +1–2 Å above the contact atom → 3.5–5 Å) coincides with where the **cation + THF
sit** in this cell. Static translation of the anion into 2.5–3.2 Å therefore overlaps the electrolyte for
*every* seed/orientation (all 30 attempts rejected). The 2.0–2.3 Å frames work only because there the anion
is *below* the electrolyte. **This zone genuinely needs the electrolyte to rearrange = your gold-standard
steered/constrained AIMD**, which the static perturbation cannot reproduce.

## Recommended loop
1. **Retrain with batch 1** (the 2.0–2.3 Å contact frames are the actual MD-destabilizing zone) and re-run
   the bare interface. Batch 1 may already stabilize the near-contact region.
2. If the MD still destabilizes in **2.5–3.2 Å**, that's the signal to fund a **steered/constrained AIMD**
   (CPU): hold/pull the anion COM through 3.5→2.3 Å so the electrolyte accommodates, DFT-label the path
   (~5 h Γ on the bare cell). I can run that on confirmation — it's the only physical way to fill the gap.
