# AL_REQUEST → EPYC: bare Al co-deposition AIMD (the reductive event MLFF cannot do)

**From:** GPU node (LYZ-ROG) · **Date:** 2026-06-21 · **Branch:** computational-v3-interface
**For:** close the v3 co-deposition mechanism — directly simulate the bare Al³⁺→Al⁰ reduction/deposition.

## Why (what the MLFF showed and why it can't go further)
Matched MLFF-MD (r6, 0.5fs+cap, **500 ps**) puts the bare Ph₂AlCl₂⁻ anion **poised at the reductive front
but intact and UNREACTED**: min Al–electrode 3.90 Å, mean 4.58 Å, **nCl = 2 the entire run (no Cl-strip),
0 % of frames < 3.5 Å, force-cap fired 0×.** That is the MLFF ceiling — MACE is a conservative FF with no
electron transfer, so the actual Al³⁺→Al⁰ reduction is beyond it. The reaction only ever appeared as the
**pre-cap blow-ups at ~3.2 Å** (the model hitting reactive territory it can't represent).
Indirect evidence of co-deposition is strong — wet-lab **ToF-SIMS Al⁰ in the bare SEI**, and your
**biased-DFT force-response (Al 1.6× more field-reducible in bare than poly)**. **What's missing is the
dynamic reduction itself**, which is CP2K/AIMD's domain.

## Request: bare-interface Born–Oppenheimer AIMD that captures the reduction
- **System:** bare Mg(0001)|electrolyte (t17 bare cell, 172 atoms = 64-Mg slab + [Mg₂Cl₃(THF)₆]⁺ +
  Ph₂AlCl₂⁻), or your equivalent T10 bare cell.
- **Driving force:** **cathodic charged slab** (excess electrons, net q = −1 to −2 e — the reductive/plating
  condition, same charged-slab machinery as your biased batch). Provides the reduction driving force within
  AIMD reach.
- **Start close:** from a **close-approach config (Al ~3–3.5 Å)** so the event is accessible on the ps AIMD
  timescale — use your `bias_bare_q-1_d3` frame, or the **2 MLFF close-approach frames committed here:
  `mlff/v3/t17/al_queue_bare_closeapproach.xyz` (~3.2 Å)**.
- **Run:** BOMD, NVT ~300–350 K, **same DFT level as prior batches** (PBE-D3, DZVP-MOLOPT-SR-GTH/GTH-PBE,
  CUTOFF 400/REL 50, Fermi smearing), a few ps (or until reduction observed). Your SCF-hardened
  `label_sp_template.inp` mixing is a good starting point for the charged cell.
- **Track / report (the deliverable):** Al–electrode distance vs t; **Al oxidation state** (Bader/Hirshfeld/
  Mulliken charge + spin on Al vs t — does it trend +→0 = reduction?); Al–Cl bonds (Cl-stripping order);
  Al–Mg bond formation (deposition); phenyl release. **Key question: does Al⁰ deposit, and by what steps**
  (Cl-strip → reduce → deposit? phenyl loss first? concerted?).
- **(Stretch) poly contrast** if affordable: same setup with the POSS network — does the network prevent the
  reduction by keeping the anion out of reach? (276 atoms — only if cheap; **bare is the priority**.)

## Output
Trajectory + charge/bonding-vs-time analysis → push to `incoming/` (`bare_codep_aimd_RESPONSE.md` + traj).
This closes the v3 chain: **MLFF approach → AIMD reduction → SEI composition (ToF-SIMS/XPS).**

Thanks — coordinates with the T5 interface work (matched standoff 1.9× + your biased 1.6×). — GPU node
