#!/usr/bin/env bash
# run_cp2k.sh <jobname> — run one CP2K job under SLURM (one at a time).
#   sbatch --ntasks=<NP> bin/run_cp2k.sh <jobname>
# Expects <jobname>.inp in the CWD (a P0c/P0d inp/ dir). MPI-only (no OMP) for DFT.
#SBATCH --partition=CPU
#SBATCH --job-name=cp2k
#SBATCH --output=%x-%j.log
set -euo pipefail

NAME="${1:?usage: run_cp2k.sh <jobname (no .inp)>}"
NP="${SLURM_NTASKS:-${NP:-64}}"
export OMP_NUM_THREADS=1

CP2K_BIN="${CP2K_BIN:-/CH/cp2k-2025.1/exe/local/cp2k.psmp}"
echo "[run_cp2k] $NAME on $NP MPI ranks (OMP=1)"
mpirun -np "$NP" "$CP2K_BIN" -i "${NAME}.inp" -o "${NAME}.out"
rc=$?

if grep -qE "PROGRAM ENDED|GEOMETRY OPTIMIZATION COMPLETED|MD| SCF run converged" "${NAME}.out" 2>/dev/null \
   && ! grep -q "ABORT" "${NAME}.out"; then
  echo "[run_cp2k] $NAME: completed"
else
  echo "[run_cp2k] $NAME: check ${NAME}.out (rc=$rc)" >&2
fi
exit $rc
