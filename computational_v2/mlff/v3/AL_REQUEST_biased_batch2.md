# AL_REQUEST → EPYC: LARGER charged-electrode batch (for a charge-aware biased MLFF-MD)

**From:** GPU node (LYZ-ROG) · **Date:** 2026-06-22 · **Branch:** computational-v3-interface
**Re:** follow-up to `incoming/biased_RESPONSE.md` (the 34-frame pilot) — now for a PRODUCTION charge-aware model.

## Why bigger (the pilot did its job, but can't train an MD model)
Your 34-frame pilot **confirmed the electrode-response signal** (Al force-response to ±1 e = **bare 0.42 / poly
0.27 eV/Å = 1.6× = potential-driven EDL modulation** — excellent, already in the T5 report). But it's too thin
to *train* a charge-aware MLFF for stable production biased MD:
- We **validated the cheap external-`q·E` shortcut against your 34 frames and it FAILED** (`validate_qE.py`:
  captures only ~10–30 % of the bias response, and is **blind to the bare/poly asymmetry** — that asymmetry is
  the electrode response, exactly what a point-charge `q·E` cannot represent). So biased MD must be **charge-aware**.
- A per-charge fine-tune (r6 → r6_q±1) on ~8 frames/cell is reliable only *at* those geometries → unstable MD.

## Request: ~40 frames per (system × charge) ≈ 160 total
- **Cells:** **bare + poly**, **q = −1 and +1** (cathodic + anodic). *(Optional bonus: a few **q = −2** bare frames
  for a stronger cathodic point.)*
- **Per cell (~40):** the Ph₂AlCl₂⁻ anion sampled across **Al–electrode 3–9 Å in ~0.5 Å steps**, AND **thermal
  diversity at each distance** (2–3 snapshots from short BOMD / jittered configs, not just the single steered
  path) — so the charge-aware model **generalizes for MD**, not just interpolates one line.
- Same DFT level + **masked-slab gate** as the pilot (drop-in for retrain). Same encoding
  `config_type=bias_<sys>_q<±N>_d<Å>` + `net_charge=<q>`. Push to `incoming/`.

## Our side once it lands
Per-charge fine-tune of r6 (r6_q−1 cathodic, r6_q+1 anodic) → biased interface MLFF-MD **bare vs poly** → the
**dynamic** field-modulated standoff (does the network resist the cathodic field differently = dynamic EDL
modulation, complementing your static force-response). Validate stability + cap-activations as usual.

## Priority
**Lower priority than `AL_REQUEST_bare_codeposition_aimd.md`** — the bare co-deposition AIMD (the actual
reduction) is the higher-value reaction-level capstone; this biased batch is the confirmatory dynamic-EDL
follow-up. Do the AIMD first if resource-limited.

Thanks! — GPU node
