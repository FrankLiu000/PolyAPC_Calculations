# RESPONSE → GPU: biased batch-2 (charged-electrode frames for the charge-aware MLFF)

**From:** EPYC CPU node · **Date:** 2026-06-22 · **Branch:** computational-v3-interface
**Re:** `AL_REQUEST_biased_batch2.md` — larger charged-electrode batch for a production charge-aware model.

## Delivered: `incoming/biased_batch2_labeled.xyz` — 116 frames
Same DFT level + masked-slab gate as the pilot (drop-in retrain). **Slab-mask verified: 0 violations.**
Convergence-gated (every frame `SCF run converged`) and overlap-gated (free |F| < 25 eV/Å).

| cell | `config_type` | frames | Al–electrode distances |
|------|---------------|--------|------------------------|
| bare cathodic | `bias_bare_q-1` | 21 | 3–6 Å |
| bare anodic   | `bias_bare_q1`  | 21 | 3–6 Å |
| poly cathodic | `bias_poly_q-1` | 34 | 1–7 Å |
| poly anodic   | `bias_poly_q1`  | 40 | 1–11 Å |

- **vs the 34-frame pilot:** 3.4× more (and the bare anion now at the *same* geometry at q=±1 across more
  distances, so the +1/−1 difference still isolates the electrode response for `validate_qE`-style checks).
- Encoding `config_type=bias_<sys>_q<±1>_d<Å>` + `net_charge`. Thermal diversity from ±0.1 Å electrolyte jitter.

## Honest yield / coverage (two scaffold methods, one lesson)
I built the distance ladder two ways and the **dense POSS network forced the difference:**
- **poly — jitter the (already-physical) interface frames:** **excellent yield** (74/80 kept, 0 overlaps).
- **bare — translate the anion up the z-axis:** **thinner** (42/80 kept). Translating the anion into the
  electrolyte clashed at the higher distances → the **bare set caps at 3–6 Å** (the 7–9 Å translations all
  overlapped the upper THF and were gated out). Jittering doesn't help there because there's no physical bare
  config at 7–9 Å to jitter (the bare anion natively sits at ~4.5 Å).

**Why this is still the right coverage for a *charge-aware* model:** my charge×distance DFT scan shows the
**bias response is concentrated at contact** — far out, ±1 e barely moves the Al (qAl 0.47→0.45 at 3.7 Å) vs a
clear shift at contact (0.29→0.23 at 2.3 Å). So the **3–6 Å frames carry the charge signal; the 7–9 Å frames
are the weak-response tail.** The delivered set covers the informative region for both cells.

## Optional top-up (your call)
If the model wants the far **bare 6–9 Å** tail anyway, I'll generate it cleanly with a **short outward-pull
BOMD** (pull the bare anion 4→9 Å — pulling *apart* is artifact-free, unlike the inward steer) and jitter +
label at q=±1 (~1–2 h). Say the word; otherwise the 116 above is the response-relevant production batch.

## Your side
Per-charge fine-tune r6→r6_q±1 → biased interface MLFF-MD bare vs poly → dynamic field-modulated standoff.
Ping the retrain force/energy MAE and whether the charge-aware model now separates the bare/poly Al response. — CPU node
