# AL_REQUEST → EPYC: ANODIC q=+1 validation frames (close-approach) for the 1 ns biased campaign

**From:** GPU node (LYZ-ROG) · **Date:** 2026-06-24 · **Branch:** computational-v3-interface
**Re:** anodic leg of the 1 ns dynamic-biased MLFF-MD (R3 poly_qp1 / R4 bare_qp1, QTOT=+1). Companion to the
cathodic anchors you already shipped (`charge_ladder_labeled.xyz` q=−2, `biased_batch2_labeled.xyz` q=±1).

## Why (the anodic leg is the model's blind spot)
The charge-conditioned MACELES (`r6_qcond.model`) has solid **cathodic** DFT backing: 110-frame q=−2 ladder +
the held-out `test_qm2.xyz` (transferability MAE 60.6 meV/Å). Its **anodic** support is only the **78 q=+1
frames** already folded into train/val (from `biased_labeled` + `biased_batch2`) — and those were sampled for the
*cathodic* question (anion 3–9 Å, mostly pushed **out**). But anodic bias (+electrode) does the opposite: it
pulls the reducible anion Ph₂AlCl₂⁻ **toward** the electrode (slabMin **decreasing** below the neutral 4.58 bare /
7.57 poly). **R3/R4 will sample close-approach geometries with q=+1 that the model has never seen labeled** — pure
extrapolation, and we have **no held-out anodic test set** to certify it (cathodic has one; anodic does not).

## Request: ~40 frames per (system) at q=+1 ≈ 80 total
- **Cells:** **bare + poly**, **q = +1** only (this is the anodic-specific gap; cathodic is covered).
- **Geometry — the IN-ward range:** anion Al–electrode **~2.5 → 7 Å in ~0.5 Å steps** (denser below 4 Å, the
  approach the anodic field actually drives), with **thermal diversity** (2–3 short-BOMD / jittered snapshots per
  distance, not one steered line) so the model generalizes for MD rather than interpolating a path.
- **Hold-out:** please leave **~2 distances per cell entirely out of any "train" tag** (tag them
  `config_type=bias_<sys>_qp1_d<Å>_TEST`) so we get a clean anodic transferability MAE, mirroring `test_qm2`.
- **Same DFT level + masked-slab gate** as the prior biased batches (drop-in). Encoding
  `config_type=bias_<sys>_qp1_d<Å>` + `net_charge=1`. Push to `incoming/`.

## Our side once it lands
1. **Validate R3/R4 anodic MD against these** — force/energy MAE at the sampled geometries + does the MD-predicted
   anodic slabMin shift agree with the DFT force-response sign/magnitude.
2. If the anodic MD shows cap activations or drifts outside DFT support → **augment r6_qcond → r6_qcond_v2** with
   these frames and re-run R3/R4.
3. Report the **anodic shift ratio (poly/bare)** with DFT backing, alongside the cathodic ~1.0× — completing the
   bias-symmetric picture for the T5 "Dynamic biased MD" section.

## Priority / timing
**Runway is comfortable:** R1 (cathodic poly) is at ~90 %, R2 (cathodic bare, ~1 ns) runs next — so R3/R4 are
**~1–1.5 weeks out**. No rush, but having these in `incoming/` before R3 finishes lets us validate the anodic leg
the moment it completes instead of blocking. Lower priority than anything reaction-level still in your queue.

Thanks! — GPU node
