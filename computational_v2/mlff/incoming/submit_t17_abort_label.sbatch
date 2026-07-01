#!/usr/bin/env bash
#SBATCH -J t17_abort_label
#SBATCH -p CPU
#SBATCH -N 1
#SBATCH -n 64
#SBATCH -o t17_abort_label_%j.out
#SBATCH -e t17_abort_label_%j.err

set -euo pipefail

ROOT="${ROOT:-/CH/Claude_Calcs_20260603}"
WORK="$ROOT/computational_v2/mlff/incoming/t17_abort_label_20260701"
SRC="$ROOT/computational_v2/mlff/incoming/t17_bare_seed2026070101_abort_unlabeled.xyz"
OUT="$ROOT/computational_v2/mlff/incoming/t17_bare_seed2026070101_abort_labeled.xyz"
REPORT="$ROOT/computational_v2/mlff/incoming/t17_bare_seed2026070101_abort_LABEL_REPORT.md"
LAT="12.836,0.0,0.0,6.418,11.116,0.0,0.0,0.0,55.0"

mkdir -p "$WORK"
cp "$ROOT/computational_v2/P0d_interface/inp/label_sp_template.inp" "$WORK/"
cd "$WORK"

export CP2K_BIN="${CP2K_BIN:-/CH/cp2k-2025.1/exe/local/cp2k.psmp}"
export CP2K_DATA_DIR="${CP2K_DATA_DIR:-/CH/cp2k-2025.1/data}"
export SLURM_NTASKS="${SLURM_NTASKS:-64}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"

{
  echo "# T17 guarded-abort DFT force labels"
  echo
  echo "- date_start: $(date '+%F %T %Z')"
  echo "- node: $(hostname)"
  echo "- cp2k: $CP2K_BIN"
  echo "- ntasks: $SLURM_NTASKS"
  echo "- source: $SRC"
  echo "- output: $OUT"
  echo "- charge: 0"
  echo "- slab_force_mask: first 64 atoms"
  echo
} > "$REPORT"

python3 "$ROOT/computational_v2/bin/label_forces.py" "$SRC" 172 0 "$LAT" "$OUT" 9 64 2>&1 | tee label_forces.log

{
  echo
  echo "## Completion"
  echo
  echo "- date_end: $(date '+%F %T %Z')"
  echo "- output_frames: $(grep -c '^172$' "$OUT" 2>/dev/null || echo 0)"
  echo
  echo '```text'
  tail -n 80 label_forces.log
  echo '```'
} >> "$REPORT"
