# HANDOFF v3 — poly-APC computational campaign: results, retractions, and NEW STORIES

**To the next agent.** You inherit a completed-but-evolving Gaussian 16 + CP2K 2025.1 + Multiwfn
campaign (run workspace `/CH/poly_v2/`, package + deliverables in this repo, branch
`computational-v2-package`). Your job is different from v2's "execute the program":
**think of new stories** that explain the wet-lab observations, using (a) the calculations already
on disk — including one major finding made in the final hours, see §4 — and (b) a **new/upgraded
wet-lab dataset the user is preparing right now** (they are re-verifying the XPS data; see §7 for
exactly what to ask of it). Read `HANDOFF_computational_v2_Al_and_wetlab.md` for the scientific
background and `PLAN_polyAPC_v2_computational.md` for the original program.

**The central tension you must resolve:** the wet-lab headline is a 3.1 eV Al 2p XPS split
(bare 70.88 eV "reduced/alloyed Al⁰" vs poly 73.98 eV "Al³⁺"), but the molecular calculations say
the reduction *thermodynamics* of the intact anion are nearly identical in bare and poly
(EA 0.51 vs 0.48 eV) and *ligand-centred*, not Al-centred. So either the lever is chemical
speciation rather than ET energetics (§4 — currently the best candidate), or the wet-lab
assignment itself needs re-examination (§7). Possibly both.

---

## 1. Environment (verified working — do not re-derive)

- One SLURM node, partition `CPU`: 96 physical cores, 377 GB RAM. G16 `/CH/g16/g16`;
  CP2K `/CH/cp2k-2025.1/exe/local/cp2k.psmp`; Multiwfn noGUI; ORCA 6.1.0.
- Run scripts: `/CH/poly_v2/bin/run_g16.sh` (sbatch -c N, per-job scratch on
  `/mnt/scratch_disk`) and `run_cp2k.sh` (sbatch --ntasks=64). **Both carry
  `#SBATCH --time=4-00:00:00` — keep finite walltimes or SLURM backfill dies** (a running
  UNLIMITED job pushes pending start estimates to +1 year and idles the node).
- Standing user directives: keep all 96 cores busy whenever possible; routinely check SCF
  convergence and remediate; routinely clean scratch of dead jobs (`bin/clean_scratch.sh`);
  molecular protocol = **PCM in opt/freq + SMD in TZVP single points**; M06-2X takes GD3
  (not GD3BJ); all interface AIMD stays at **EPS_SCF 1e-5** (matched bare/poly comparison —
  user-locked, do not tighten).
- Molecular level: B3LYP-D3(BJ)/def2-TZVP(SMD-THF) // def2-SVP(PCM) opt+freq;
  G = E[TZVP,SMD] + Gcorr[SVP]. **Both sides of any reaction must use this same recipe** —
  a level-mixing bug once produced ΔG = −582 kcal/mol nonsense.
- Periodic: PBE-D3, DZVP-MOLOPT-SR-GTH/GTH-PBE, CUTOFF 400/REL 50, Fermi 500 K on metals.

## 2. Results inventory (all in `/CH/poly_v2/results/data/`, mirrored in `computational_v2/results/data/`)

| File | Headline | Confidence |
|---|---|---|
| `redox_ladder.txt` | Anion IPs 5.7–7.7 eV (anodic limit AlPh₄⁻ 5.73); intact-anion EAs ~0.1 eV (AlCl₄⁻ negative) | high (3 functionals) |
| `reduction_spin_localization.txt` | **Only AlCl₄⁻ reduces at Al** (spin +1.14); all Ph-containing anions reduce at phenyl π* (~0.93) | high |
| `reductive_decomposition.txt` | Reduced [AlPh₂Cl₂]²⁻: Al–Cl cleavage ΔG **−8.5** kcal/mol (Al–C +14.5); product [AlPh₂Cl]·⁻ has **83% spin on Al** = Al(II), direct Al⁰ precursor | high |
| `depairing_ET.txt` | CIP vertical EA: bare 0.51 ≈ poly 0.48 eV; free anion 0.06 eV. Cation contact (not pairing tightness) drives reducibility; **depairing is NOT a thermodynamic gate**. Caveat: computed on intact pairs — see §4 | high (for what it tests) |
| `chloride_abstraction.txt` | **NEW** — neutral AlPh₂Cl: EA_vert **1.71 eV** (intact free anion: 0.06), ΔG_red,adia **−2.14 eV**; vertical spin already 52% on Al (intact anion: 4–8%) | high (NImag=0, ⟨S²⟩ clean) |
| `aimd_interface_stats.txt` | **NEW** — matched 10 ps bare/poly access + Cl-abstraction tracking (auto-lands when job 1241 ends) | in flight |
| `al2p_prediction.txt` | Voronoi+Mulliken charge trend reproduces the *direction* of the 70.9→74.0 split (Δq ≈ +0.7 e); no absolute BEs (GTH) | medium (trend robust) |
| `al_codeposition_periodic.txt` | Al adatom on Mg(0001) −0.08 eV (marginal); **Al-in-Mg substitution −4.44 eV (alloying favourable — the robust statement)**; Mg₁₇Al₁₂ number is an artifact, ignore | medium |
| `interface_ET.txt` | RETRACTION + honest status of interfacial ET (read in full — §3) | n/a |
| `mgf2_neb_LIMITATION.txt` | No MgF₂ barrier computed (charged-defect PES won't converge in affordable cell); cite literature 0.5–1.0 eV | n/a |
| `raman_peaks.csv` | 181/276 cm⁻¹ Mg–Cl bands: poly = more dissociated, fewer Cl-bridged aggregates; 1002→ shift consistent with freer anion | high (experiment-anchored) |
| `g16_energies.csv` | Machine-readable E/G for every molecular species | — |

Geometry/trajectory assets: `/CH/poly_v2/P0d_interface/inp/aimd_{bare,poly}-pos-1.xyz` (10 ps each,
276-atom poly / 172-atom bare; **slab Mg = atoms 0..63, cation Mg = 64,65, Al = 147, anion =
147..171, all 0-based — the same in both**); analysis tool `bin/analyze_interface_access.py`
(PBC-correct, slab-Mg-only — an earlier metric mistakenly counted the cation Mg as "surface").
MD-sampled CIP seeds: `classical_molecular_dynamics/handoff_for_agent/structures/representative_solvation/`
(bare μ-Cl bridge 2.23/2.13 Å tight; poly 2.70/2.08 Å stretched, Mg–Al 4.11 vs 4.73 Å).

## 3. Retractions & hard limitations (do not re-trip these)

1. **CDFT/Becke on a metallic slab is invalid.** Becke partitioning does not conserve charge
   with Fermi-smeared slab states (total Becke charge −13/+11 e on *neutral* cells; fragment N₀
   environment-dependent: 88 vs 49–64 e for the same 25-atom anion). The previously quoted
   bare ΔE_ET = 1.33 eV is **retracted**. Method B (Dirichlet-BC fixed potential) was never run
   and likely shares pathologies — treat any interfacial ΔG_ET ambition with extreme suspicion
   on this hardware/method stack. Full post-mortem in `interface_ET.txt`.
2. **MgF₂ vacancy NEB**: charged Mg²⁺-vacancy endpoints never converge in a 9.25 Å cell
   (frustrated PES, BFGS ±2–3 eV oscillation, CG floors at RMS 0.03–0.045). No barrier is
   reported. Needs Schottky-neutral defect chemistry in a much larger cell, if ever.
3. **AIMD is structural sampling only** (EPS_SCF 1e-5 + smearing → ~0.08 Ha/ps drift; Nosé
   keeps configurations canonical). Never cite it for energy conservation or energetics.
4. Equilibrium AIMD shows **no plating/reduction event** in 10 ps and the anion stays ~7–9 Å
   from the slab in both systems — deposition is a rare, overpotential-driven event. Don't burn
   weeks hoping to "see" it; biased/rare-event methods would be needed (user has paused that).

## 4. THE NEW FINDING — the chloride-abstraction gateway (best current story)

Discovered in the final matched-trajectory analysis (this is why per-atom bond tracking matters):

- **Bare interface AIMD:** within **0.2 ps**, the [Mg₂Cl₃(THF)₆]⁺ cation **abstracts one Cl⁻**
  from [AlPh₂Cl₂]⁻ (Al–Cl149: mean 7.7 Å, >3 Å for 97% of the 10 ps run; the Cl ends bridging
  the two cation Mg at 2.41/2.56 Å). The "anion" present at the bare interface is therefore
  **neutral, 3-coordinate, Lewis-acidic AlPh₂Cl** — not [AlPh₂Cl₂]⁻ at all.
- **Poly interface AIMD:** the same μ-Cl bond stretches transiently (>3 Å in 6% of frames,
  max 3.91 Å) but **always returns** (final 2.29 Å). The anion stays intact for all 10 ps.

Why this closes the loop with the static chemistry already on disk:

1. One-electron reduction of neutral AlPh₂Cl gives [AlPh₂Cl]·⁻ — **exactly the 83%-Al-spin
   Al(II) radical** of `reductive_decomposition.txt`, the direct Al⁰ precursor.
2. A neutral Lewis acid is far easier to reduce than an anion — now quantified
   (`chloride_abstraction.txt`): **EA_vert(AlPh₂Cl) = 1.71 eV vs 0.06 eV** for the intact free
   anion (~28×), ΔG_red,adia = −2.14 eV, and the electron lands on Al already at the vertical
   point (52% spin, vs 4–8% for intact anions). Chloride loss redirects the incoming electron
   from phenyl π* to aluminium AND removes the Coulomb penalty.
3. Al⁰, once formed, alloys into Mg(0001) exergonically (−4.44 eV substitution) → **70.9 eV**.
4. Poly's stretched bridge (network-imposed, from classical MD and reproduced at DFT) blocks
   the abstraction → anion stays intact → reduction is weak and phenyl-centred (2–8% Al spin)
   → Al stays Al(III) → **74.0 eV**.

So the bare-vs-poly lever is **chemical speciation at the interface (Cl⁻ abstraction), not ET
thermodynamics** — consistent with the depairing result that intact-pair EAs are equal. It also
dovetails with `reduction_spin_localization.txt`: stripping Cl/Ph redistribution funnels toward
chloride-richer Al species, and AlCl₄⁻ is the only anion that reduces directly at Al.

**Caveats you must respect and test:** single trajectory per condition; the event happens at
0.2 ps so it may be encoded in the (MD-sampled, condition-representative) starting geometries —
that is fair (the geometry difference IS the bare/poly difference) but needs replication.
`bare_r2` (job 1242, fresh velocity seed) tests seed-sensitivity only. The decisive cheap test
is **molecular**: ΔG of `[Mg₂Cl₃(THF)₆]⁺ + [AlPh₂Cl₂]⁻ → Mg₂Cl₄(THF)₆ + AlPh₂Cl` (cluster,
standard protocol) with and without a coordinating polyether/POSS fragment on the cation.

## 5. In-flight jobs & armed harvests (check these FIRST)

| Job | What | Harvest |
|---|---|---|
| 1241 (R) | poly interface AIMD, step ~8.3k/10k, ends ~06-11 01:30 | `bin/harvest_interface_stats.sh 1241` armed → writes `aimd_interface_stats.txt` + per-frame `{bare,poly}_access.txt` automatically |
| 1242 (PD, after 1241) | bare_r2 replicate AIMD (SEED 2237), ~2.5 d | NOT auto-harvested. When done: `python3 bin/analyze_interface_access.py aimd_bare_r2-pos-1.xyz bare_r2` + the Cl148/Cl149 tracking block (copy from `harvest_interface_stats.sh`). **Key question: does the Cl⁻ abstraction recur?** |
| 1261→1262/1263 | neutral AlPh₂Cl opt+freq → TZVP SP + vertical reduction | DONE — `chloride_abstraction.txt` written (EA 1.71 eV; see §4) |

Routine duties while anything runs: `squeue`; `bin/scf_health.sh`; `bin/clean_scratch.sh`;
keep cores busy. Harvest logs: `P0d_interface/inp/_harvest_iface.log`, `run_mol/_harvest_alph2cl.log`.
(Past bug: wait-loops keyed to output-file greps caught stale files, and 8 h timeouts fired
early — the armed harvests are keyed to job IDs with 24–48 h loops.)

## 6. Candidate NEW STORIES (ranked; each with the test that kills or confirms it)

**S1 — "Poly blocks the chloride-abstraction gateway" (flagship, §4).**
   Compute: (a) molecular abstraction ΔG bare vs poly-mimic (cheap, decisive); (b) bare_r2
   recurrence; (c) optional 2nd poly replicate / a bare run started from a symmetrized bridge.
   Wet-lab: Cl 2p & Mg/Cl ratio in SEI (bare should be MgCl₂-richer); Raman 276 cm⁻¹
   (Cl-bridged aggregates — already trends right: −30% in poly).

> **On 2D free-energy heatmaps for S1 (user asked; answer: not yet, and not from this data).**
> A true F(CV₁,CV₂) map needs equilibrium recrossing statistics. The bare trajectory contains ONE
> irreversible abstraction event (0.2 ps) and the poly one basin + excursions — −kT·ln P on 10 ps
> of that is not a free energy and must not be presented as one. A real interfacial FES means 2D
> metadynamics/umbrella on the 276-atom DFT cell (weeks; the biased-AIMD class the user has
> paused). Cost-ordered substitutes: (1) the molecular 1D relaxed scan above (decisive, cheap);
> (2) a 2D *sampling-density* heatmap d(Al–Cl) vs d(Mg_cation–Cl) from the existing trajectories —
> good article figure, label it "sampling density (10 ps, unbiased)", never "free energy";
> (3) a 2D molecular constrained-opt surface (concerted-vs-stepwise detail) only if S1 survives
> the wet-lab check and the article needs it; (4) interfacial metadynamics last, only with the
> user's explicit go-ahead.

**S2 — "Speciation funnel: only AlCl₄⁻ deposits Al".**
   Repeated Cl⁻ abstraction + Schlenk redistribution enriches chloride-rich anions near the bare
   electrode; AlCl₄⁻ is the unique reduce-at-Al species (+1.14 spin). Compute: Schlenk ladder
   including the *neutral* species (AlPh₂Cl, AlPhCl₂, AlCl₃·THF) now that abstraction makes them
   relevant; equilibrium with [Mg₂Cl₄] sink. Wet-lab: anion speciation (²⁷Al NMR if available,
   or Raman ring-breathing 999/1002 region) of cycled vs fresh electrolyte, bare vs poly.

**S3 — "Phenyl-centred first reduction → organic SEI".**
   Intact anions dump the first electron into phenyl π* (0.91–0.94). Expect aryl chemistry
   (biphenyl, benzene, surface Ph–Mg) wherever intact anions meet the electrode — i.e. MORE in
   poly if any reduction happens there at all. Compute: ΔG of [AlPh₂Cl₂]²⁻ → biphenyl routes;
   C 1s shift of aryl-Mg vs carbonate. Wet-lab: GC-MS of cycled electrolyte for biphenyl/benzene;
   C 1s fine structure.

**S4 — "73.98 eV is not (only) Al₂O₃: Al–O–Si aluminosilicate from POSS".**
   Poly's network is silsesquioxane; Al³⁺ + Si–O gives aluminosilicate environments at 74–75 eV.
   Compute: extend `al2p_prediction.txt` with an Al–O–Si model (Al in a POSS-corner/silicate
   cluster — periodic Voronoi/Mulliken trend + an all-electron ΔSCF cluster in ORCA for a real
   BE shift). Wet-lab: Si 2p position (102–103 silsesquioxane vs ~102.5 aluminosilicate),
   O 1s, and whether Al 2p at 73.98 correlates spatially (depth profile) with Si.

**S5 — "The XPS assignment itself" (active — user is re-verifying).**
   70.88 eV is low even for Al⁰ (literature metallic Al 2p₃/₂ ≈ 72.6–72.9; Mg–Al alloying
   lowers it, but 70.9 needs checking against calibration). If the upgraded dataset moves
   either number, re-anchor every story above before writing anything. See §7.

## 7. Questions for the upgraded wet-lab dataset (ask the user; design around answers)

1. **Calibration/referencing:** what was C 1s set to (284.6/284.8/285.0)? Charge neutralizer on?
   Same referencing for bare and poly? A 1–2 eV referencing offset would rewrite the story.
2. **70.88 eV lineshape:** metallic-asymmetric (Doniach-Šunjić) or symmetric? Is there a Mg KLL
   Auger / Mg 2p metallic component consistent with exposed metal? Pure Al⁰ sits ~72.7 eV —
   70.9 implies strong alloying (consistent with our −4.44 eV substitution) or a referencing issue.
3. **Was Ar⁺ sputtering used before/while acquiring Al 2p?** Sputtering reduces Al³⁺ → artificial
   low-BE components. Depth-profile order matters.
4. **73.98 eV companions:** exact O 1s, F 1s, Si 2p positions in the SAME spot. AlF₃ (76.3–76.5)
   vs Al₂O₃ (74.1–74.6) vs aluminosilicate (74.3–74.8) are distinguishable mainly through the
   companions (F 1s 685.0 MgF₂ vs 686.5 AlF₃; Si 2p shift on Al incorporation).
5. **S 2p scan** (was missing in v1): triflate-derived sulfite/sulfide would confirm the OTf
   reduction channel in poly; its absence weakens the MgF₂-from-triflate SEI story.
6. **Bare-electrode F:** still present in the new dataset? We model bare F-free (user-locked);
   if real F persists on bare, that decision must be revisited.
7. **Cl 2p and Mg:Cl:Al stoichiometry** bare vs poly (tests S1/S2 directly — MgCl₂-richer bare SEI).
8. **Anything new entirely** (GC-MS, NMR, more cycles, washed vs unwashed electrodes) — S2/S3
   become testable with speciation/organics data.

## 8. Remaining v2 deliverables (parked, not abandoned)

`REPORT_polyAPC_v2_master.md` still has `[[NODE-FILL]]` scaffolding; publication figures and
the observable-by-observable reconciliation table are unwritten. The user said "let's talk about
the article later" — **do not** write the report until the upgraded wet-lab dataset lands and
one of the stories in §6 survives its tests. When you do: honest framing is mandatory
(transport is NOT the win; retractions in §3 stay in the text; single-trajectory caveats stated).

## 9. Operational pitfalls (each cost us hours — verbatim lessons)

- Finite `--time` on every job, always (backfill).
- Never `rm` the open output file of a running job (writes vanish into an unlinked inode).
- Key monitors/waits to **job IDs**, never to output-file greps (stale-file false positives).
- G16 hard SCF cases (radical anions, near-degenerate pairs): `scf=(xqc,vshift=500,conver=6)
  guess=mix` — and note that *bare-pair* charge-sloshing is itself physics (near-degeneracy of
  the inner-sphere ET pair).
- CP2K kind order = order of first appearance in the coordinates (check "ATOMIC KIND
  INFORMATION") — per-kind arrays like ATOMIC_RADII must follow it.
- Atom indexing: Al is **147** 0-based / 148 1-based; off-by-one here silently breaks every
  analysis. Slab Mg = 0..63 only; 64/65 are the cation's.
