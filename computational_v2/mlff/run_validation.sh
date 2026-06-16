#!/bin/bash
# Post-training validation driver (run after run_train.sh finishes).
#   1. held-out force/energy RMSE (eval_test.py)
#   2. MLFF-MD demonstration (run_md.py) from the AIMD-equilibrated final frame
#   3. AIMD-matched interface analysis on the MLFF trajectory (analyze_interface_access.py)
#   4. figure (fig_mlff.py)
set -e
cd "$(dirname "$0")"
VENV=/lyz/Claude_workplace/polyAPC/.mlff_venv
PY="$VENV/bin/python"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

MODEL=${MODEL:-run_apc_mlff/apc_mlff.model}
[ -f "$MODEL" ] || MODEL=run_apc_mlff/apc_mlff_stagetwo.model
START=${START:-md_start.xyz}   # clean intact-anion equilibrium frame (select_md_start.py; Al-Cl 2.22/2.25 A, Al-slab 8.99 A)
NSTEPS=${NSTEPS:-30000}    # 30 ps @ 1 fs (vs AIMD's 10 ps that cost days; demonstrates the speed payoff)
echo "=== MODEL=$MODEL  START=$START  NSTEPS=$NSTEPS  $(date) ==="

echo "### [1/4] held-out test accuracy"
$PY eval_test.py "$MODEL" mlff_test.xyz

echo "### [2/4] MLFF-MD demonstration ($NSTEPS steps)"
$PY run_md.py "$MODEL" "$START" "$NSTEPS" md_bare

echo "### [3/4] AIMD-matched interface analysis on the MLFF trajectory"
$PY ../bin/analyze_interface_access.py md_bare_traj.xyz MLFF-MD md_bare_iface

echo "### [4/4] figure"
$PY fig_mlff.py ../results/figures/fig_mlff_train.png
echo "=== VALIDATION_DONE $(date) ==="
