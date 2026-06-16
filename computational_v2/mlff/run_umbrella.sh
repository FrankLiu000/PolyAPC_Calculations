#!/bin/bash
# Umbrella-sampling driver for the Mg2+ desolvation/approach free energy.
#   MODEL, START, LABEL, plus Z0S (window centers, A), K (eV/A2), NSTEPS.
# Writes umb_<LABEL>/window_z<z0>.dat per window, then WHAM -> umb_<LABEL>_pmf.dat.
#
# NOTE: the current MLFFs are trained only on the ~8.5-9.5 A equilibrium basin. Windows below
# ~8 A are EXTRAPOLATION (unreliable) until the active-learning loop labels near-surface configs.
# Default Z0S is the in-distribution pilot range.
set -e
cd "$(dirname "$0")"
VENV=/lyz/Claude_workplace/polyAPC/.mlff_venv
export PATH="$VENV/bin:$PATH" PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

MODEL=${MODEL:-models/apc_bare.model}
START=${START:-md_start.xyz}
LABEL=${LABEL:-bare}
Z0S=${Z0S:-"8.0 8.5 9.0 9.5 10.0"}
K=${K:-1.0}
NSTEPS=${NSTEPS:-6000}
WD=umb_${LABEL}; mkdir -p "$WD"

echo "=== umbrella: model=$MODEL start=$START label=$LABEL k=$K nsteps=$NSTEPS windows=[$Z0S] $(date) ==="
for z0 in $Z0S; do
  echo "--- window z0=$z0 ---"
  "$VENV/bin/python" umbrella.py "$MODEL" "$START" "$z0" "$K" "$NSTEPS" "$WD/window_z${z0}"
done
echo "=== WHAM ==="
"$VENV/bin/python" wham.py "umb_${LABEL}" "$WD"/window_z*.dat
echo "=== UMBRELLA_DONE $LABEL $(date) ==="
