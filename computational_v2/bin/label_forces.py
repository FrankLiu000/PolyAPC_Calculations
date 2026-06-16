#!/usr/bin/env python3
"""label_forces.py — DFT force-labeling driver for the MLFF training set.

Reads frames from an energy-only scaffold (extended-XYZ), runs a CP2K ENERGY_FORCE
single-point per frame (label_sp_template.inp), parses energy + atomic forces, and
APPENDS an extended-XYZ block (positions + energy[eV] + forces[eV/Ang]) to the
training file. Resumable: counts frames already in the output and skips them.

Usage (inside a SLURM alloc, env CP2K_DATA_DIR/CP2K_BIN/SLURM_NTASKS set):
  python3 label_forces.py <scaffold.xyz> <Natoms> <CHARGE> <latticeCSV9> <out_train.xyz> [max_frames]
"""
import sys, os, subprocess, glob

HA = 27.211386245988          # Hartree -> eV
HA_B = 51.42206747            # Hartree/Bohr -> eV/Angstrom
TEMPLATE = "label_sp_template.inp"

scaffold, nat, charge, latcsv, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
maxf = int(sys.argv[6]) if len(sys.argv) > 6 else 10**9
n_slab = int(sys.argv[7]) if len(sys.argv) > 7 else 0  # mask forces on the fixed slab atoms 0..n_slab-1
NP = os.environ.get("SLURM_NTASKS", "64")
CP2K = os.environ.get("CP2K_BIN", "/CH/cp2k-2025.1/exe/local/cp2k.psmp")
lat = latcsv.split(",")
A, B, C = lat[0:3], lat[3:6], lat[6:9]
tmpl = open(TEMPLATE).read()
work = "label_work"; os.makedirs(work, exist_ok=True)

done = 0
if os.path.exists(out):
    done = sum(1 for L in open(out) if L.strip() == str(nat))
print(f"[label] scaffold={scaffold} nat={nat} charge={charge} NP={NP} | already done={done}", flush=True)


def frames(fn):
    fh = open(fn)
    while True:
        h = fh.readline()
        if not h:
            return
        try:
            n = int(h.split()[0])
        except (ValueError, IndexError):
            return
        com = fh.readline()
        at = [fh.readline() for _ in range(n)]
        if any(not x for x in at):
            return
        yield n, com, at


def parse(outf):
    """energy[eV], forces[eV/Ang]. Forces printed as 'FORCES| <idx> fx fy fz |f|' (Ha/Bohr)."""
    E, F = None, []
    for L in open(outf):
        if "ENERGY| Total FORCE_EVAL" in L:
            E = float(L.split()[-1]) * HA
        elif L.lstrip().startswith("FORCES|"):
            p = L.split()
            if len(p) >= 6 and p[1].isdigit():
                F.append([float(p[2]) * HA_B, float(p[3]) * HA_B, float(p[4]) * HA_B])
    return E, F


fo = open(out, "a")
idx = labeled = processed = 0
for n, com, at in frames(scaffold):
    if n != nat:
        continue
    if idx < done:
        idx += 1; continue
    if processed >= maxf:
        break
    processed += 1
    proj = f"lbl{idx}"
    with open(f"{work}/{proj}.coord.inc", "w") as g:
        g.write("    &CELL\n")
        g.write(f"      A {A[0]} {A[1]} {A[2]}\n      B {B[0]} {B[1]} {B[2]}\n      C {C[0]} {C[1]} {C[2]}\n")
        g.write("      PERIODIC XYZ\n    &END CELL\n    &COORD\n")
        for L in at:
            p = L.split()
            g.write(f"      {p[0]} {p[1]} {p[2]} {p[3]}\n")
        g.write("    &END COORD\n")
    inp = tmpl.replace("__PROJ__", proj).replace("__CHARGE__", charge).replace("__COORD__", f"{proj}.coord.inc")
    open(f"{work}/{proj}.inp", "w").write(inp)
    subprocess.run(f"mpirun -np {NP} {CP2K} -i {proj}.inp -o {proj}.out", shell=True, cwd=work)
    E, F = parse(f"{work}/{proj}.out")
    if E is None or len(F) != n:
        sys.stderr.write(f"[label] frame {idx}: PARSE FAIL (E={E}, nF={len(F)}/{n}) - keeping .out\n")
        idx += 1; continue
    # MASK the fixed slab: the bottom slab is held fixed in the source AIMD (& in production
    # MLFF-MD); its UNCONSTRAINED single-point forces are a large +z asymmetric-slab dipole
    # artifact (~92 eV/A net, momentum-violating, unfittable - GPU-node finding 2026-06-16).
    # Zero them (= the fixed-atom convention); electrolyte forces are kept (clean, R~0.89).
    for k in range(min(n_slab, n)):
        F[k] = [0.0, 0.0, 0.0]
    # momentum guard on the FREE (electrolyte) region - catches future labeling regressions
    sf = [sum(F[a][c] for a in range(n_slab, n)) for c in range(3)]
    free_net = (sf[0] ** 2 + sf[1] ** 2 + sf[2] ** 2) ** 0.5
    if free_net > 8.0:
        sys.stderr.write(f"[label] frame {idx}: WARN free-atom ||sumF||={free_net:.2f} eV/A (>8)\n")
    fo.write(f"{n}\n")
    fo.write(f'Lattice="{" ".join(lat)}" Properties=species:S:1:pos:R:3:forces:R:3 '
             f'energy={E:.6f} charge={charge} pbc="T T T"\n')
    for L, f in zip(at, F):
        p = L.split()
        fo.write(f"{p[0]:<2} {p[1]} {p[2]} {p[3]} {f[0]:.6f} {f[1]:.6f} {f[2]:.6f}\n")
    fo.flush()
    fmax = max(max(abs(x) for x in row) for row in F)
    print(f"[label] frame {idx}: E={E:.4f} eV  |F|max={fmax:.3f} eV/A  (labeled {labeled+1})", flush=True)
    for pat in ("*RESTART*", "*.wfn*", "*.cube"):
        for fp in glob.glob(f"{work}/{proj}{pat}"):
            try: os.remove(fp)
            except OSError: pass
    labeled += 1; idx += 1
print(f"[label] DONE: {labeled} new frames labeled (of {processed} processed) -> {out}", flush=True)
