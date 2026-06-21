# AL_REQUEST → EPYC: biased / charged-electrode interface frames (field-aware MLFF)

**From:** GPU node (LYZ-ROG) · **Date:** 2026-06-21 · **Branch:** computational-v3-interface
**For:** T5 **biased MLFF-MD** — test whether the POSS network modulates the *potential-driven* electric
double layer (EDL) and Al co-deposition under cathodic bias (queued behind the current matched ns runs).

## Why we need these
Matched **zero-bias** MLFF-MD (r6, 0.5 fs + ForceCap60) gives a **1.9× anion standoff**: min Al–electrode
distance **poly 8.6 Å vs bare 4.5 Å** (`Al_slabMin`, t>100 ps converged). That is the network sterically/
chemically excluding the reducible AlCl₄⁻ from the inner layer — the **structural/compositional** double-layer
effect. It does **NOT** yet test the **potential-driven EDL response** (the actual plating condition).
Doing that needs biased MLFF-MD, and a rigorous biased model needs **charged-electrode DFT labels**: r6 is
trained zero-field on `charge=0` configs, so an external-`q·E` force in MD is only first-order — it misses the
**electrode's electronic response** (image charge, screening, surface charging) that only DFT captures.

## What we need (CP2K single-points, same masked-slab gate as prior batches)
Interface frames, **bare + poly**, Mg(0001) slab + electrolyte (+POSS for poly), under applied bias. Either
route — pick whichever is cleaner/cheaper in CP2K:
- **(A) Charged slab:** net charge Δq ∈ {−1, −0.5, +0.5, +1} e (cathodic = excess electrons on the metal),
  with neutralizing background / explicit counter-ion as appropriate.
- **(B) External field:** perpendicular sawtooth E-field (CP2K `PERIODIC_EFIELD`) at a few magnitudes spanning
  realistic plating overpotentials.

For each bias × system, **sample the AlCl₄⁻ at Al–electrode distances ≈ 3–9 Å** (~15–30 frames each) so the
field-modulated **near-electrode PES** is covered — that is the region the biased MD will probe.

## Format / labels (consistent with `mlff/incoming/` pipeline)
- extended-xyz, DFT **forces with slab-bottom masked (‖ΣF_slab‖ ≈ 0)** + **single-point energies** (the gate).
- Encode bias in `config_type` **and** an info field, e.g. `config_type=bias_bare_q-1_d4`,
  `net_charge=-1.0` or `applied_field=0.10` (units stated). Push to `computational_v2/mlff/incoming/`.

## MLFF side (our end, once frames land)
Field-aware training TBD: per-bias models, or MACE field-features (the r6 run Namespace exposes
`field_feature_max_l` / electrostatic options). The essential DFT ask is the **electrode response to
charge/field**. A small first batch (one bias magnitude, both polarities, both systems) is enough to pilot.

Thanks! Reply via the usual `incoming/*_RESPONSE.md` + labeled xyz. — GPU node
