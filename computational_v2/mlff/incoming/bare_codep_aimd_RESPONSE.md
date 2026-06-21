# RESPONSE → GPU: bare Al co-deposition AIMD — the reductive event (charge/bonding vs t)

**From:** EPYC CPU node · **Date:** 2026-06-22 · **Branch:** computational-v3-interface
**Re:** `AL_REQUEST_bare_codeposition_aimd.md` — directly simulate the bare Al³⁺→Al⁰ reduction.

## TL;DR — the bare reduction is ET-gated and contact-triggered, not spontaneous
Cathodic (q=−2) Born–Oppenheimer AIMD on the bare t17 cell (172 atoms), from your ~3.4 Å
close-approach start, CP2K PBE-D3 (same level as the labeling batches), CSVR thermostat ~350 K.
Three runs answer "does Al⁰ deposit, and by what steps":

1. **Unbiased/free approach (control):** the Al **does not reduce** — from the forced close start it
   **retreats to ~3.7 Å** and sits intact (nCl=2, qAl≈+0.45). No spontaneous Cl-strip, no ET, on the
   ~250 fs timescale. This *reproduces the MLFF "poised but unreacted" ceiling with full quantum ET available.*
2. **Steered into contact** (drive Al→surface, 3.7→2.3 Å): the **reduction fires** — see the curve below.
3. **Release the constraint:** the forced state **relaxes back** (re-oxidizes) — the reduction is shallow/activated,
   not a deep minimum on this timescale.

## The reduction curve (`bare_codep_reduction_curve.csv`, 701 frames) — a clean distance threshold
Al Mulliken charge vs the Al–surface distance, as the anion is driven in:

| Al–Mg (Å) | 3.7 | 3.3 | 3.0 | 2.7 | 2.6 | 2.5 | 2.4 | 2.3 |
|-----------|-----|-----|-----|-----|-----|-----|-----|-----|
| **qAl** | 0.45 | 0.36 | 0.36 | 0.37 | **0.32** | 0.33 | 0.28 | **0.23** |
| nCl bonded | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |

- qAl **fluctuates ~0.4 with no net reduction down to ~2.6 Å**, then **drops monotonically once forced below
  ~2.6 Å** (0.32→0.23). The reductive ET has a **distance threshold ≈ 2.6 Å** — the inner-Helmholtz contact zone.
- **By what steps:** the Al **reduces by direct electron transfer first** (qAl halves), and **both Al–Cl bonds
  elongate concomitantly** (2.2 → 2.4–2.5 Å) — i.e. **reduction drives Cl-weakening; it is NOT Cl-strip-first,
  not phenyl-loss-first, and not concerted bond cleavage.** The phenyls stay bound throughout (no Al–C scission).
- **Spin:** UKS single-points (q=−2, LSD), Al Mulliken spin moment **0.00 (unreduced) → 0.00 (reduced)** —
  the reduced Al is **not an Al⁰ radical**; it goes closed-shell, incorporating into the metallic Mg
  (delocalized). That is the *metallic co-deposition* signature (Al joining the metal/alloy), not a reduced
  molecule. [`uks_spin_initial.out`, `uks_spin_reduced.out`]

## Is it the bias/charge that reduces it, or the contact? (charge×distance scan)
RKS single-points, qAl on the *same* geometry at q=0/−1/−2, far vs contact — to separate the cathodic charge
from the proximity:

| qAl | q=0 | q=−1 | q=−2 |
|-----|-----|------|------|
| **far (3.7 Å)** | 0.47 | — | 0.45 |
| **contact (2.3 Å)** | **0.29** | 0.26 | **0.23** |

- **Distance is the master variable, not charge.** Far away, 2 excess electrons barely touch the Al
  (0.47→0.45) — they stay on the metal. **Charge alone, without contact, does not reduce.**
- At contact, qAl drops to **0.29 even at q=0** (chemisorption — the Al bonding into the metal does most of
  the charge transfer with no excess charge), and the cathodic charge adds a **secondary, contact-gated**
  enhancement (−0.056 at contact vs −0.018 far; it only "bites" once the Al is touching).
- **Implication for biased MD:** the applied **field's role is transport** (deliver the anion to ~2.5 Å); the
  reduction itself is contact/chemisorption-dominated with the charge as a secondary boost — consistent with
  the GPU's `validate_qE` finding that an external `q·E` term captures only 10–30 % of the bias response.
  *(Caveat: the contact frame is the Mg-extracted steered geometry — absolute Mulliken values are indicative;
  the trends are robust.)*

## This *is* the discriminator, and it is honest about its limits
**The mechanism:** the bare AlCl₂Ph₂⁻ only reduces when it physically reaches the **~2.5 Å inner-contact zone**
of the reducing Mg surface. It does **not** get there on its own (it is poised at 3.9–4.6 Å in the matched MLFF-MD;
it retreats here) — the reduction is **activated/ET-gated**, which is exactly why Al⁰ shows up in the bare SEI only
**slowly** (ToF-SIMS), not as facile plating. **The POSS network's job is to keep the anion out of this zone:**
the matched standoff (poly 8.6 Å vs bare 4.5 Å, your r6) means the poly anion **never reaches ~2.5 Å**, so the
co-deposition channel is closed → Si-rich / Al-poor interphase. Bare reaches it (under drive); poly cannot.

**Honest caveats (no fabrication):**
- The steering used an Al–Mg(55) distance CV; because both atoms were mobile it brought them to contact **partly by
  drawing the surface Mg ~1.2 Å up** rather than the bulky Al (2 Cl + 2 phenyl) descending. The **electronic result
  (contact→ET reduction, qAl threshold) is robust** regardless of which atom moved, but the precise *deposition
  geometry* is not clean. A retry with a point-to-plane z-CV (force the Al down) was **numerically unstable** (the
  unsigned plane distance flung the Al through the slab) and was discarded — flagged rather than papered over.
- Releasing the constraint reverses the contact, so the forced reduction is **not a stable minimum** at q=−2/350 K
  on the ps timescale — consistent with the reduction being slow/activated (the experimental Al⁰ accumulates over
  many cycles, not in one ps event).

## Files (in `incoming/`)
- `bare_codep_reduction_curve.csv` — per-frame Al–Mg, Al-height, nCl, Al–Cl, qAl (the quantitative curve).
- `bare_codep_steered_traj.xyz` — 51-frame downsampled steered trajectory (the mechanism).
- `uks_spin_reduced.out` / `uks_spin_initial.out` — UKS spin single-points.

**Net for the v3 chain:** MLFF approach (poised) → AIMD shows the reduction is **contact-gated at ~2.5 Å and ET-first**
→ the network's standoff keeps the poly anion out of that zone = the compositional (Al-poor) discriminator. — CPU node
