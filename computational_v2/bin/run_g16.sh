#!/usr/bin/env bash
# run_g16.sh <jobname> — run one Gaussian 16 job under SLURM.
#   sbatch -c <ncores> bin/run_g16.sh <jobname>
# Expects <jobname>.gjf in the CWD (a phase gjf/ dir) and the .gjf to declare
# its own %nprocshared/%mem and route line. Per-job private scratch.
#SBATCH --partition=CPU
#SBATCH --job-name=g16
#SBATCH --output=%x-%j.log
set -euo pipefail

NAME="${1:?usage: run_g16.sh <jobname (no .gjf)>}"
NCORES="${SLURM_CPUS_PER_TASK:-8}"

# shellcheck disable=SC1091
source /CH/g16/bsd/g16.profile
export GAUSS_SCRDIR="/mnt/scratch_disk/g16_scratch/${NAME}"
mkdir -p "$GAUSS_SCRDIR"

echo "[run_g16] $NAME on $NCORES cores, scratch=$GAUSS_SCRDIR"
g16 < "${NAME}.gjf" > "${NAME}.log" 2>&1
rc=$?

if [ -f "${NAME}.chk" ]; then
  formchk "${NAME}.chk" "${NAME}.fchk" || echo "[run_g16] formchk failed (non-fatal)"
fi

if grep -q "Normal termination" "${NAME}.log"; then
  echo "[run_g16] $NAME: Normal termination"
else
  echo "[run_g16] $NAME: NON-normal termination (rc=$rc) — inspect ${NAME}.log" >&2
fi
# leave non-zero rc to fail dependency chains on error
grep -q "Normal termination" "${NAME}.log"
