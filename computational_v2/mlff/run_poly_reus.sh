#!/bin/bash
# Persistent poly REUS launcher (reboot-resumable via reus.py checkpoints).
# flock guard => only ONE instance ever runs (prevents the watchdog/manual double-launch race).
exec 200>/tmp/poly_reus.lock
flock -n 200 || { echo "$(date): poly_reus already running (lock held); exit"; exit 0; }
cd /lyz/Claude_workplace/PolyAPC_Calculations/computational_v2/mlff || exit 1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/lyz/Claude_workplace/polyAPC/.mlff_venv/bin/python
Z="4.0 4.2 4.4 4.6 4.8 5.0 5.2 5.4 5.6 5.8 6.0 6.2 6.4 6.6 6.8 7.0 7.2 7.4 7.6 7.8 8.0 8.2 8.4 8.6 8.8 9.0 9.2 9.4"
[ -f umb_poly_reus_DONE ] && exit 0
echo "=== poly REUS (re)start $(date) ==="
$PY reus.py run_poly_r2_s1/apc_poly_r2_s1.model poly_r3 1.0 500 50 umb_poly_reus $Z || exit 1
$PY wham.py umb_poly_reus umb_poly_reus/window_z*.dat --equil 10000 --boot 100 && touch umb_poly_reus_DONE
echo "=== poly REUS DONE $(date) ==="
