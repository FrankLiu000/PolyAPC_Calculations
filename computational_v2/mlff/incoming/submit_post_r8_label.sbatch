#!/usr/bin/env bash
#SBATCH -J post_r8_label
#SBATCH -p CPU
#SBATCH -N 1
#SBATCH -n 64
#SBATCH -o post_r8_label_%j.out
#SBATCH -e post_r8_label_%j.err

set -euo pipefail

ROOT="${ROOT:-/CH/Claude_Calcs_20260603}"
SRC="${SRC:-$ROOT/computational_v2/mlff/incoming/post_r8_dft_candidates.xyz}"
WORK="${WORK:-$ROOT/computational_v2/mlff/incoming/post_r8_label_batches}"
REPORT="${REPORT:-$ROOT/computational_v2/mlff/incoming/post_r8_LABEL_REPORT.md}"
SPLIT="$ROOT/computational_v2/mlff/incoming/split_post_r8_label_batches.py"
LABEL="$ROOT/computational_v2/bin/label_forces.py"
TEMPLATE="$ROOT/computational_v2/P0d_interface/inp/label_sp_template.inp"

mkdir -p "$WORK"
cp "$TEMPLATE" "$WORK/"
cd "$WORK"

export CP2K_BIN="${CP2K_BIN:-/CH/cp2k-2025.1/exe/local/cp2k.psmp}"
export CP2K_DATA_DIR="${CP2K_DATA_DIR:-/CH/cp2k-2025.1/data}"
export SLURM_NTASKS="${SLURM_NTASKS:-64}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"

{
  echo "# post-r8 DFT/AIMD validation labels"
  echo
  echo "- date_start: $(date '+%F %T %Z')"
  echo "- node: $(hostname)"
  echo "- cp2k: $CP2K_BIN"
  echo "- ntasks: $SLURM_NTASKS"
  echo "- source: $SRC"
  echo "- work: $WORK"
  echo "- slab_force_mask: first 64 atoms"
  echo
} > "$REPORT"

python3 "$SPLIT" "$SRC" "$WORK" 2>&1 | tee split_post_r8.log

if [ ! -s "$WORK/manifest.tsv" ] || [ "$(tail -n +2 "$WORK/manifest.tsv" | wc -l)" -eq 0 ]; then
  {
    echo "## No frames"
    echo
    echo "No post-r8 candidate frames were available. Nothing submitted to CP2K."
  } >> "$REPORT"
  exit 0
fi

{
  echo "## Split"
  echo
  echo '```text'
  cat "$WORK/SPLIT_REPORT.md"
  echo '```'
  echo
} >> "$REPORT"

tail -n +2 "$WORK/manifest.tsv" | while IFS=$'\t' read -r group nat charge lattice nframes nslab scaffold labeled; do
  {
    echo
    echo "## Group $group"
    echo
    echo "- natoms: $nat"
    echo "- charge: $charge"
    echo "- frames: $nframes"
    echo "- scaffold: $scaffold"
    echo "- labeled: $labeled"
    echo
    echo '```text'
  } >> "$REPORT"
  python3 "$LABEL" "$scaffold" "$nat" "$charge" "$lattice" "$labeled" "$nframes" "$nslab" 2>&1 | tee "label_${group}.log"
  tail -n 120 "label_${group}.log" >> "$REPORT"
  echo '```' >> "$REPORT"
done

{
  echo
  echo "## Completion"
  echo
  echo "- date_end: $(date '+%F %T %Z')"
  echo "- labeled files:"
  find "$WORK" -maxdepth 1 -name '*_labeled.xyz' -printf '  - %p (%s bytes)\n' | sort
} >> "$REPORT"
