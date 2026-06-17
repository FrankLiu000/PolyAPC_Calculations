#!/bin/bash
# CHAINED umbrella-sampling driver for the Mg2+ desolvation/approach PMF.
# Windows run high-z -> low-z; each starts from the previous window's equilibrated final config
# (stable descent of the steep approach; avoids the abrupt-pull force singularities).
#   MODEL, START, LABEL, Z0S (window centers, A), K (eV/A2), NSTEPS.
# Writes umb_<LABEL>/window_z<z0>.dat per window, then WHAM -> umb_<LABEL>_pmf.dat.
cd "$(dirname "$0")" || exit 1
VENV=/lyz/Claude_workplace/polyAPC/.mlff_venv
export PATH="$VENV/bin:$PATH" PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# NOTE: no `set -e` — a single window crash (e.g. transient CUDA segfault) must not abort the sweep.

MODEL=${MODEL:-models/apc_bare.model}
START=${START:-md_start.xyz}
LABEL=${LABEL:-bare}
Z0S=${Z0S:-"3.5 4.0 4.5 5.0 5.5 6.0 6.5 7.0 7.5 8.0 8.5 9.0 9.5"}
K=${K:-0.5}
NSTEPS=${NSTEPS:-5000}
WD=umb_${LABEL}; mkdir -p "$WD"

echo "=== chained umbrella: model=$MODEL label=$LABEL k=$K nsteps=$NSTEPS windows=[$Z0S] $(date) ==="
prev_last=""
for z0 in $(echo "$Z0S" | tr ' ' '\n' | sort -rn); do      # high z -> low z
  start="${prev_last:-$START}"
  echo "--- window z0=$z0  (start: $start) ---"
  for attempt in 1 2; do                                    # retry once on transient crash (segfault)
    "$VENV/bin/python" umbrella.py "$MODEL" "$start" "$z0" "$K" "$NSTEPS" "$WD/window_z${z0}" && break
    echo "WARN: window z0=$z0 attempt $attempt failed (rc $?); retrying" >&2
  done
  last="$WD/window_z${z0}_last.xyz"
  [ -f "$last" ] && prev_last="$last" || echo "WARN: no _last for z0=$z0; keeping previous start for next window" >&2
done
echo "=== WHAM ==="
"$VENV/bin/python" wham.py "umb_${LABEL}" "$WD"/window_z*.dat ${WHAM_OPTS:-}
echo "=== UMBRELLA_DONE $LABEL $(date) ==="
