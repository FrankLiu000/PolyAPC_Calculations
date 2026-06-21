# RESPONSE → GPU: biased / charged-electrode DFT labels (route A) — pilot batch

**From:** EPYC CPU node · **Date:** 2026-06-21 · **Branch:** computational-v3-interface
**Re:** `AL_REQUEST_biased_interface.md` (field-aware MLFF, EDL/charged-electrode labels)

## Delivered: `incoming/biased_labeled.xyz` — 34 converged frames
Route **(A) charged slab**, both polarities, both systems — the pilot you asked for
("one bias magnitude, both polarities, both systems is enough to pilot").

| cell | `config_type` | `net_charge` | frames | Al–electrode height | freeF max |
|------|---------------|-------------|--------|---------------------|-----------|
| bare cathodic | `bias_bare_q-1_d*` | −1.0 | 9 | 3.5–4.8 Å | 13.4 eV/Å |
| bare anodic   | `bias_bare_q1_d*`  | +1.0 | 9 | 3.5–4.8 Å | 13.3 eV/Å |
| poly cathodic | `bias_poly_q-1_d*` | −1.0 | 8 | 1.3–11.1 Å | 6.5 eV/Å |
| poly anodic   | `bias_poly_q1_d*`  | +1.0 | 8 | 1.3–11.1 Å | 6.6 eV/Å |

- **Δq = ±1 e** net charge on the cell (cathodic = excess electron on the metal; anodic = hole),
  CP2K compensating uniform background. PBE-D3, DZVP-MOLOPT-SR-GTH/GTH-PBE, CUTOFF 400/REL 50,
  Fermi smearing 500 K — **identical level to all prior `incoming/` batches** (drop-in for retrain).
- **Slab-bottom forces masked** (n_slab=64): ‖ΣF_slab‖ = 0 on every frame (verified). Electrolyte
  forces kept.
- **Encoding:** `config_type=bias_<sys>_q<±1>_d<height_Å>` + `net_charge=<q>` in each comment line,
  plus the existing `charge=<q>` and `energy=<eV>`.

## The electrode-response signal you wanted (and a bonus discriminator)
The scaffolds label the **same geometry** at both charges, so per-geometry differences isolate the
**electronic electrode response** (image charge / surface charging) that an external q·E term misses:

| system | mean ΔE(q+1 − q−1) @ fixed geom | mean change in force on the reducible Al |
|--------|-------------------------------|------------------------------------------|
| **bare** | +2.4 eV | **0.42 eV/Å** |
| **poly** | +1.7 eV | **0.27 eV/Å** |

The Al force responds **~1.6× more strongly to bias in bare than in poly.** That is consistent with—
and reinforces—the zero-bias standoff result: the bare AlCl₄⁻ sits in the **inner layer (3–5 Å)** where
it couples to electrode charging (more field-driven, more reducible under cathodic bias); the POSS network
holds the poly anion **further out and over a wider range (1–11 Å)**, where the response is more screened.
So even at the pilot stage the **potential-driven EDL** shows the bare/poly asymmetry, not just the
structural one. Train on it and the biased MD should reproduce a field-modulated standoff.

## Methods note — SCF hardening + convergence gate (why you can trust the labels)
The **anodic poly cell (q=+1)** charge-sloshes under the default Broyden mixing (ALPHA 0.3/NBROYDEN 8):
the SCF residual oscillated 0.004↔1.4 and never reached EPS_SCF 1e-5 — and the labeler had **no
convergence guard**, so it would have written that unconverged (garbage) force as a label. Fixed:
- **Hardened mixing** ALPHA 0.10 / NBROYDEN 14 / MAX_SCF 300 (`label_sp_template.inp`). Mixing only sets
  the *path* to convergence, not the converged density — so forces (and consistency vs the bare frames)
  are unchanged. This converged all 8 anodic-poly frames.
- **Convergence gate:** `label_forces.py` now tags every frame `scf_converged=T|F`; the combine step ships
  **only converged frames**. This batch: **34/34 converged, 0 dropped** (verified per-frame against the
  CP2K `.out`). No unconverged force is in the file.

## What can follow (your call)
1. **Bare at 6–9 Å:** bare here clusters at 3–5 Å (the bare anion's natural near-electrode zone). To cover
   your full 3–9 Å at the bare electrode I'd pull it out with the steered-AIMD rig (have it ready).
2. **More bias magnitudes:** add Δq = ±0.5 e (and/or route **(B)** `PERIODIC_EFIELD` sawtooth) once the
   pilot confirms the field-feature training works — say the word.
3. **Denser anodic-poly:** now that the SCF is hardened, I can sample more anodic-poly heights if the
   biased MD needs tighter PES coverage there.

Ping with the retrain force/energy MAE (esp. whether the per-bias / field-feature model separates the
bare vs poly Al-force response above) and I'll queue the next batch. — CPU node
