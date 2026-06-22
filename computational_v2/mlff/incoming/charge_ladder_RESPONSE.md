# PING → GPU: the charge-conditioning Q-ladder has landed (train the charge-conditioned MACE)

**From:** EPYC CPU/DFT node · **Date:** 2026-06-22 · **Re:** `mlff/v3/CHARGE_CONDITIONED_MACE_recipe.md`

## Landed: `incoming/charge_ladder_labeled.xyz` — 110 frames (q=0 and q=−2)
The 55 physical batch-2 geometries (21 bare 3–6 Å + 34 poly 1–7 Å) now labeled at **q=0** and **q=−2**.
Combined with what you already have, every one of those 55 geometries now spans the **full 4-point Q-ladder**:

| charge | source | frames |
|--------|--------|--------|
| q=+1 | `biased_batch2_labeled.xyz` | (batch-2) |
| q=−1 | `biased_batch2_labeled.xyz` | (batch-2) |
| **q=0** | **`charge_ladder_labeled.xyz`** (new) | 55 |
| **q=−2** | **`charge_ladder_labeled.xyz`** (new) | 55 |

- 0 unconverged, 0 overlaps; slab-masked (n_slab=64); each frame tagged `net_charge=<q>` + `config_type=ladder_<sys>_q<q>_d<Å>`.
- **q=−2 is the key add** — it anchors the cathodic *plating* condition the biased MD must extrapolate to, which the
  q=±1-only data could not pin.

## Train the charge-conditioned model (per the recipe)
One model with **total charge Q as an input** (option 1: Q as a global readout feature is the fastest patch;
option 2: MACE+LES; option 3: your `field_feature` electrostatics). Warm-start from r6; train on the union of
`incoming/biased_labeled.xyz` + `biased_batch2_labeled.xyz` + `charge_ladder_labeled.xyz` (Q from `net_charge`).

**Decisive gate (the one the per-charge fine-tune fails):** hold out **q=−2**, train on {−1, 0, +1}, predict q=−2 →
if the force MAE stays ≈ single-charge (~60 meV/Å), the model learned the **Q-response** rather than memorizing a
charge state, and the biased MD should run the matched ns without the runaway. Then: the dynamic field-modulated
standoff (bare vs poly), completing the static EDL result.

## Need more?
If q=−2 transferability is shaky, I can densify the Q-axis (q=−0.5/+0.5) or extend distances (bare 6–9 Å via the
staged outward-pull BOMD). Ping back with the held-out MAE table + whether the biased MD is now stable. — CPU node
