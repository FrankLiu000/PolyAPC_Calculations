# poly-APC vs bare-APC — Mg-cluster comparison

## 1. RDF first-peak position and coordination number (to 0.35 nm)

| pair | bare peak (nm) | bare CN | poly peak (nm) | poly CN |
|---|---|---|---|---|
| Mg–Cl(bridge) | 0.250 | 3.00 | 0.250 | 3.00 |
| Mg–O(THF ligand) | 0.212 | 3.00 | 0.212 | 3.00 |
| Mg–O(free THF) | 0.230 | 0.17 | 0.230 | 0.16 |
| Mg–O(all THF) | 0.212 | 3.17 | 0.212 | 3.16 |
| Mg–Cl(anion) | 0.244 | 0.84 | 0.244 | 0.80 |
| Mg–Al(anion) | 0.444 | 0.00 | 0.444 | 0.00 |
| Mg–Mg | 1.124 | 0.00 | 1.126 | 0.00 |
| Mg–O(polymer) | — | — | 1.500 | 0.01 |

## 2. Mg first-shell solvation (mean ± sd)

| species | bare-APC | poly-APC |
|---|---|---|
| Cl (bridge) | 3.00 ± 0.00 | 3.00 ± 0.00 |
| O (THF) | 3.16 ± 0.37 | 3.16 ± 0.36 |
| O (polymer) | — | 0.01 ± 0.08 |
| Cl (anion) | 0.84 ± 0.38 | 0.80 ± 0.41 |
| total(Cl+O) | 6.16 ± 0.37 | 6.16 ± 0.37 |

- Mg with anion-Cl contact (ion pairing): **bare 83.3%**, **poly 79.8%**
- Mg with polymer-O contact (poly): **0.6%**

- dominant motifs (Cl,Othf,Opoly):
  - bare: [('3, 3, 0', 83.8), ('3, 4, 0', 16.2)]
  - poly: [('3, 3, 0', 83.7), ('3, 4, 0', 15.7), ('3, 3, 1', 0.6)]

## 3. Mg-cluster non-bonded interaction energies (short-range, kJ/mol, total over 80 cations)

| interaction | bare-APC | poly-APC |
|---|---|---|
| Coul-SR:MgCluster-Anion | -7793.38 | -7471.69 |
| Coul-SR:MgCluster-Initiator | — | -654.103 |
| Coul-SR:MgCluster-MgCluster | 73942.2 | 73891.6 |
| Coul-SR:MgCluster-Polymer | — | 4.45253 |
| Coul-SR:MgCluster-Solvent | -1233.1 | -1189.08 |
| LJ-SR:MgCluster-Anion | -3510.94 | -3538.49 |
| LJ-SR:MgCluster-Initiator | — | -152.244 |
| LJ-SR:MgCluster-MgCluster | -4942.47 | -4926.51 |
| LJ-SR:MgCluster-Polymer | — | -3436.43 |
| LJ-SR:MgCluster-Solvent | -12109.6 | -8818.5 |

(Short-range Coul-SR + LJ-SR via energy-group decomposition; PME reciprocal part is delocalised and not included.)
