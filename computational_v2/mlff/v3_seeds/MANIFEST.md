# v3 MLFF seed structures — config space for the broad {Mg,Al,Cl,O,C,H,Si} potential (T16)
# These are STRUCTURES (geometries). They must be DFT force-labeled on the CPU node
# (PBE-D3/DZVP-MOLOPT-SR-GTH, slab forces masked) before training — that is the T16 active-learning loop.
# Paths are on the EPYC working tree (/CH/poly_v2) unless noted; commit labeled extended-XYZ back to mlff/.

## A. SEI phases (T7) — for SEI growth/stability  [bulk, relaxed]
- MgO      : P0c_periodic/inp/MgO-1.restart       (a=4.27)
- MgCl2    : P0c_periodic/inp/MgCl2-1.restart
- Al2O3    : P0c_periodic/inp/Al2O3-1.restart
- SiO2     : v3/sei/sio2_quartz-1.restart         (alpha-quartz, NEW v3 — the Si phase)
- Mg17Al12 : P0c_periodic/inp/Mg17Al12-1.restart  (alloy; formation flagged artifact but geometry usable)

## B. Mg-Al alloying / co-deposition (T4) — for Al-on-Mg reactivity  [slabs]
- Mg(0001) 3x3x4 clean : common/struct/Mg0001_3x3x4.xyz
- Al adatom fcc/hcp/bridge/ontop : common/struct/Mg0001_Al_{fcc,hcp,bridge,ontop}.xyz
- Al substitution     : common/struct/Mg0001_AlSub.xyz

## C. Electrolyte (v2, ALREADY LABELED) — reuse directly
- dataset_train.xyz (bare 528), dataset_poly_train.xyz (poly 441)  [forces, slab-masked]
- al_queue_*_labeled.xyz (near-surface AL rounds)

## D. Reactive interface (T10) — for the reactive front  [AIMD frames, need forces]
- bare field : /CH/poly_v2/P0d_interface/inp/bias_prod_bare-pos-1.xyz  (441 frames, positions; re-label w/ forces)
- bare CHARGE-2 : bias_edep_bare trajectory (deposition-relevant, near-contact)
- poly field : bias_prod_poly (in progress)

## E. Molecular anions/cation (T1) — gas/cluster references
- common/struct/{AlCl4m,AlPhCl3m,AlPh2Cl2m,AlPh3Clm,AlPh4m,Mg2Cl3_THF6_cation}.xyz
