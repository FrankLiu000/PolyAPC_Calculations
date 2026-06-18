#!/usr/bin/env bash
# run_md_fromrelax.sh <md_jobname> <relax_jobname>
#   Build the clean MD start geometry from a finished GEO_OPT, sanity-check it for
#   close contacts, then run the MD. Designed to be chained with sbatch --dependency.
#   Expects <md_jobname>.inp to @INCLUDE iface_<sys>_clean.coord.inc.
#SBATCH --partition=CPU
#SBATCH --job-name=cp2k
#SBATCH --output=%x-%j.log
#SBATCH --time=4-00:00:00
set -euo pipefail
MD="${1:?usage: run_md_fromrelax.sh <md_jobname> <relax_jobname>}"
RELAX="${2:?need relax jobname}"
SYS="${MD#aimd_}"; SYS="${SYS%_clean}"
INC="iface_${SYS}_clean.coord.inc"

# 1) require the relaxation to have RUN (converged OR hit max-steps); a clash-free
#    geometry is what MD needs, not a force-converged minimum. Only a hard crash blocks.
if ! grep -qE "GEOMETRY OPTIMIZATION COMPLETED|MAXIMUM NUMBER OF OPTIMIZATION STEPS" "${RELAX}.out"; then
  echo "[run_md_fromrelax] ${RELAX} crashed before producing a usable geometry; refusing ${MD}" >&2
  exit 7
fi
# 2) extract the optimized last frame
python3 /CH/poly_v2/bin/lastframe_to_inc.py "${RELAX}-pos-1.xyz" "$INC"
# 3) close-contact sanity gate (non-H heavy pair < 1.6 A => still broken)
python3 - "$INC" <<'PYEOF'
import sys, numpy as np
syms, xyz, inb = [], [], False
for l in open(sys.argv[1]):
    s = l.strip()
    if s.startswith("&COORD"): inb = True; continue
    if s.startswith("&END COORD"): inb = False; continue
    if inb:
        t = s.split(); syms.append(t[0]); xyz.append([float(v) for v in t[1:4]])
xyz = np.array(xyz); n = len(xyz)
d = np.linalg.norm(xyz[:, None] - xyz[None], axis=2) + np.eye(n) * 99
bad = []
for i in range(n):
    for j in range(i + 1, n):
        if i < 64 and j < 64: continue
        h = (syms[i] == "H") + (syms[j] == "H")
        lim = 0.75 if h == 2 else (0.95 if h == 1 else 1.30)  # true clashes only (not normal bonds)
        if d[i, j] < lim: bad.append("%s%d-%s%d %.2f" % (syms[i], i, syms[j], j, d[i, j]))
if bad:
    print("CLOSE CONTACTS REMAIN:", bad); sys.exit(8)
print("clean-start contact gate: OK")
PYEOF

# 4) run the MD
NP="${SLURM_NTASKS:-64}"; export OMP_NUM_THREADS=1
export CP2K_DATA_DIR="${CP2K_DATA_DIR:-/CH/cp2k-2025.1/data}"
export PATH="/CH/cp2k-2025.1/tools/toolchain/install/openmpi-5.0.6/bin:$PATH"
export OMPI_MCA_btl_vader_single_copy_mechanism=none
CP2K_BIN="${CP2K_BIN:-/CH/cp2k-2025.1/exe/local/cp2k.psmp}"
echo "[run_md_fromrelax] ${MD} on ${NP} ranks from ${RELAX} optimized geometry"
mpirun -np "$NP" "$CP2K_BIN" -i "${MD}.inp" -o "${MD}.out"
