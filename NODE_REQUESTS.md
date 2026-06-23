# Open node requests (poll this on fetch)

| date | node | request | status |
|---|---|---|---|
| 2026-06-23 | **EPYC** (CP2K) | **DOS/PDOS for 6 SEI phases + Mg\|SiOₓ band alignment** → `results/T8b_DOS/REQUEST_EPYC.md`. Reuse `results/T8_sei_electronic/inputs/*_kp.inp` relaxed geoms; add `&PDOS` print, single-point. Output `results/T8b_DOS/outputs/<phase>_dos.csv` + `dos_meta.json`. Upgrades article Fig 5d (band-gap bars → DOS curves). | **OPEN** |

*(GPU: no action required now. Optional: dump a representative T17 reactive-interface frame — bare Al co-deposited vs poly clean — for a Fig 5 snapshot.)*
