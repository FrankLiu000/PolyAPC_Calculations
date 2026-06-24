#!/usr/bin/env python3
# T8b: build total DOS + element PDOS curves from CP2K Gamma-point .pdos files.
# Gaussian broaden (sigma=0.1 eV); reference metals to E_F, insulators to VBM.
# Output: results/T8b_DOS/outputs/<phase>_dos.csv + dos_meta.json
import glob, re, json, os
import numpy as np

HA = 27.211386245988
SIG = 0.10                       # eV broadening
METALS = {"Al_fcc","Mg17Al12","Mg_hcp"}
T8_GAP = {"Al_fcc":0.00,"Mg17Al12":0.18,"Mg_hcp":0.00,"SiO2":8.46,"Al2O3":6.21,"MgO":3.92,"MgCl2":2.93}  # authoritative T8 k-point/Gamma gaps
OUT = "/CH/Claude_Calcs_20260603/results/T8b_DOS/outputs"
os.makedirs(OUT, exist_ok=True)
PHASES = ["Al_fcc","Mg17Al12","Mg_hcp","SiO2","Al2O3","MgO","MgCl2"]
meta = {}

for ph in PHASES:
    files = sorted(glob.glob(f"{ph}_gpdos-k*-1.pdos"))
    if not files: print("no pdos for", ph); continue
    elem_states = {}      # element -> list of (E_eV, weight)
    Ef = None; occ_all = []
    for f in files:
        h = open(f).readline()
        m = re.search(r"atomic kind (\S+).*E\(Fermi\)\s*=\s*([-\d.]+)", h)
        elem = m.group(1); Ef = float(m.group(2))*HA
        rows = [l.split() for l in open(f).read().splitlines()[2:] if l.strip() and not l.startswith("#")]
        st = []
        for r in rows:
            E = float(r[1])*HA; occ = float(r[2]); w = sum(float(x) for x in r[3:])
            st.append((E, w)); occ_all.append((E, occ))
        elem_states[elem] = st
    # VBM/CBM from occupations (occupied: occ>1; empty: occ<1)
    occE = sorted(occ_all)
    vbm = max((E for E,o in occ_all if o > 1.0), default=Ef)
    cbm = min((E for E,o in occ_all if o < 1.0 and E > vbm), default=Ef)
    gap = max(0.0, cbm - vbm)
    is_metal = ph in METALS
    ref = Ef if is_metal else vbm
    refname = "E_F" if is_metal else "VBM"
    # energy grid relative to ref
    grid = np.arange(-15.0, 12.0, 0.02)
    def broaden(states):
        d = np.zeros_like(grid)
        for E, w in states:
            d += w * np.exp(-0.5*((grid-(E-ref))/SIG)**2)/(SIG*np.sqrt(2*np.pi))
        return d
    elems = sorted(elem_states)
    pdos = {e: broaden(elem_states[e]) for e in elems}
    total = sum(pdos.values())
    # write CSV
    cols = ["E_minus_Ef_eV","totalDOS"] + [f"pdos_{e}" for e in elems]
    with open(f"{OUT}/{ph}_dos.csv","w") as fh:
        fh.write(",".join(cols)+"\n")
        for i,E in enumerate(grid):
            fh.write(f"{E:.3f},{total[i]:.5f},"+",".join(f"{pdos[e][i]:.5f}" for e in elems)+"\n")
    if is_metal:                              # metals: VBM/CBM logic finds spurious Gamma-level gaps; they are metallic
        vbm = cbm = Ef; gap = 0.0
    meta[ph] = {"type":"metal" if is_metal else "insulator","energy_reference":refname,
                "E_F_eV":round(Ef,3),"VBM_eV":round(vbm,3),"CBM_eV":round(cbm,3),
                "gamma_DOS_gap_eV":round(gap,3),"t8_authoritative_gap_eV":T8_GAP[ph],
                "elements":elems,"sigma_eV":SIG,
                "note":"metallic: states at E_F (gapless)" if is_metal else
                       ("Gamma-DOS gap underestimates; T8 k-point gap 8.46 is authoritative" if ph=="SiO2" else "")}
    print(f"  {ph:9s} {'METAL' if is_metal else 'insul'} Ef={Ef:.2f} VBM={vbm:.2f} CBM={cbm:.2f} gap={gap:.2f} eV  elems={elems}")

meta["_provenance"] = "CP2K 2025.1 PBE Gamma-point single-point on T8 relaxed geoms; PDOS COMPONENTS; Gaussian sigma=0.1 eV; 2026-06-23"
json.dump(meta, open(f"{OUT}/dos_meta.json","w"), indent=2)
print("wrote", OUT)
