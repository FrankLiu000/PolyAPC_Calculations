# Charge-conditioned MACE — recipe + data handoff (CPU→GPU)

**From:** EPYC CPU/DFT node · **Date:** 2026-06-22 · **For:** the dynamic biased MLFF-MD that both
naive routes failed (`9dfb5c5`). This is the CPU-side half (data + recipe); training is GPU work.

## Why the per-charge fine-tune failed, and what actually fixes it
`r6→r6_q−1` fit the q=−1 frames well (61.9 meV/Å) but ran away in MD. Root cause: it is a **localized
model with no notion of charge** — it memorised one charge state's PES and extrapolates catastrophically
the moment the biased MD drifts off those configs. The fix is not more q=−1 data; it is **one model that
takes the total charge Q as an input** so the *same* network represents E(R, Q) smoothly for all Q. That
requires training data where the **same geometry is seen at several total charges** — which a per-charge
split structurally cannot provide.

## Data I'm delivering (the charge ladder)
`incoming/biased_labeled.xyz` (34, q=±1) + `incoming/biased_batch2_labeled.xyz` (116, q=±1) **plus** a new
4-point **Q-ladder**: the 55 physical batch-2 geometries (21 bare + 34 poly, Al–electrode 3–7 Å) each now
labeled at **q ∈ {−2, −1, 0, +1}** (`incoming/charge_ladder_labeled.xyz`, landing shortly). Same DFT level,
slab-masked, convergence-gated. Each frame carries `net_charge=<q>` in `info` — that is the conditioning label.
- The ladder is the key new asset: per geometry you now have ∂E/∂Q and ∂F/∂Q sampled across −2→+1, i.e. the
  electrode-charging response the model must learn. q=−2 anchors the **plating** condition the MD targets.

## Architecture options (pick by what your MACE build supports; ranked)
1. **Total-charge global feature (simplest, recommended first).** Concatenate the scalar `Q` (per-config
   `net_charge`) to the invariant node features feeding the energy readout MLP (a few-line patch to the MACE
   readout). One model, all charges. Loss = energy + forces as usual; add a small Q-grad regulariser if needed.
   Train from the r6 checkpoint (warm start) on the union {batch-1, batch-2, ladder}.
2. **MACE + LES (Latent Ewald Summation)** — physically-grounded long-range/charge: learned latent atomic
   charges + Ewald sum with the net charge as the neutralising background. Use the `les`/CACE wrapper around
   the r6 short-range MACE; `total_charge` enters the Ewald term. Best if you also want correct image-charge/
   screening (the very effects `validate_qE` showed q·E misses).
3. **Your existing `field_feature_max_l` / electrostatic options** (the r6 Namespace already exposes these) —
   if they implement a charge/field embedding, drive them with `net_charge` and the same ladder data.

## Validation gates (the ones that matter)
- **Charge transferability (the decisive test the fine-tune fails):** train on q ∈ {−1, 0, +1}, **predict the
  held-out q = −2** geometries → force MAE should stay ≲ the single-charge MAE (~60 meV/Å). If it does, the
  model has learned the Q-response rather than memorised a charge state.
- **Per-charge held-out force/energy MAE** across −2…+1 (report the table).
- **Dynamic stability:** the cathodic biased interface MD (bare vs poly) must run the matched ns **without the
  runaway** — that's the end goal; ForceCap activations ≈ 0.
- Then the deliverable: the **dynamic field-modulated standoff** (does the network resist the cathodic field
  differently), completing the static EDL result (biased-DFT 1.6× + co-deposition AIMD).

## If you need more data
Say which charges/distances are thin and I'll extend the ladder (e.g. q=−2 bare 6–9 Å via the outward-pull
BOMD I have staged, or intermediate q=−0.5/+0.5 for a denser Q-axis). — CPU node
