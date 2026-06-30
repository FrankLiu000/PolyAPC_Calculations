#!/bin/bash
# Persistent poly REUS launcher (reboot-resumable via reus.py checkpoints).
# flock guard => only ONE instance ever runs (prevents the watchdog/manual double-launch race).
exec 200>/tmp/poly_reus.lock
flock -n 200 || { echo "$(date): poly_reus already running (lock held); exit"; exit 0; }
cd /lyz/Claude_workplace/PolyAPC_Calculations/computational_v2/mlff || exit 1
source ./safe_wsl_env.sh
require_mem_gb "${REUS_MIN_MEM_GB:-10}"
export REUS_DT_FS="${REUS_DT_FS:-0.5}"
export REUS_FCAP="${REUS_FCAP:-60}"
export REUS_MAX_ABS_CV="${REUS_MAX_ABS_CV:-25}"
export REUS_MAX_FMAX="${REUS_MAX_FMAX:-200}"
PY=/lyz/Claude_workplace/polyAPC/.mlff_venv/bin/python
Z="4.0 4.2 4.4 4.6 4.8 5.0 5.2 5.4 5.6 5.8 6.0 6.2 6.4 6.6 6.8 7.0 7.2 7.4 7.6 7.8 8.0 8.2 8.4 8.6 8.8 9.0 9.2 9.4"
[ -n "${REUS_Z_WINDOWS:-}" ] && Z="$REUS_Z_WINDOWS"
OUT="${REUS_OUT_DIR:-umb_poly_reus_dt05}"
TAU="${REUS_TAU_FS:-500}"
NCYC="${REUS_NCYC:-50}"
[ -f "${OUT}_DONE" ] && exit 0
echo "=== poly REUS (re)start $(date) ==="
$PY reus.py run_poly_r2_s1/apc_poly_r2_s1.model poly_r3 1.0 "$TAU" "$NCYC" "$OUT" $Z || exit 1
$PY wham.py "$OUT" "$OUT"/window_z*.dat --equil 10000 --boot 100 && touch "${OUT}_DONE"
echo "=== poly REUS DONE $(date) ==="
