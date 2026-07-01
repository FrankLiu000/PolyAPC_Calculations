#!/usr/bin/env bash
# Launch controlled deposited-Mg texture probes only after r8 key-holdout passes.
#
# This is a morphology/texture analogue: added Mg adatoms are explicitly seeded
# and tracked by index.  Al approach/dechlorination/deposition remains dynamic.
set -euo pipefail

repo="$(cd "$(dirname "$0")/../../../.." && pwd)"
mlff="$repo/computational_v2/mlff"
v3="$mlff/v3"
work="$v3/t17"
source "$mlff/safe_wsl_env.sh"
require_mem_gb "${T17_MIN_MEM_GB:-12}"
require_vram_free_gb "${T17_MIN_VRAM_FREE_GB:-6}"

py="${PY:-/lyz/Claude_workplace/polyAPC/.mlff_venv/bin/python}"
driver="$v3/interface_mlff_md.py"
texture="$repo/computational_v2/analysis/mg_texture_from_xyz.py"
model="${MODEL:-$v3/models/t16_broad_r8_keyholdout.model}"
gate="$repo/results/T17_reactive/key_reactive_validation/t16_broad_r8_keyholdout_test_key_gate.json"
metrics="$repo/results/T17_reactive/key_reactive_validation/t16_broad_r8_keyholdout_test_key_metrics.csv"
outdir="$repo/results/T13_nucleation/mgdep_texture_r8"

if pgrep -af '[m]ace_run_train.*t16_broad_r8_keyholdout' >/dev/null; then
  echo "r8 training is still running; not launching Mg-deposit texture probes." >&2
  exit 2
fi
if pgrep -af '[r]eus.py.*umb_poly_reus' >/dev/null && [ "${ALLOW_WITH_REUS:-0}" != "1" ]; then
  echo "REUS is still running on the GPU; not launching Mg-deposit texture probes." >&2
  exit 2
fi
if [ ! -s "$model" ]; then
  echo "missing r8 model: $model" >&2
  exit 2
fi
if [ ! -s "$metrics" ]; then
  echo "missing r8 key-holdout metrics: $metrics" >&2
  exit 2
fi
if [ ! -s "$gate" ]; then
  "$v3/gate_key_holdout.py" "$metrics" "$gate"
fi
if ! grep -q '"passed": true' "$gate"; then
  echo "r8 key-holdout gate did not pass; not launching Mg-deposit texture probes." >&2
  cat "$gate" >&2
  exit 2
fi

cd "$work"
if [ ! -s bare_mgdep_start.xyz ] || [ ! -s poly_mgdep_start.xyz ] || \
   [ ! -s bare_mgdep_indices0.txt ] || [ ! -s poly_mgdep_indices0.txt ] || \
   [ "${BUILD_MGDEP_STARTS:-0}" = "1" ]; then
  build_args=("${MGDEP_N_ADD:-4}" "${MGDEP_Z_OFFSET_A:-2.65}")
  if [ "${BUILD_MGDEP_OVERWRITE:-0}" = "1" ]; then
    build_args+=("--overwrite")
  fi
  "$py" build_mgdep_starts.py "${build_args[@]}"
fi

mkdir -p logs "$outdir"
cp bare_mgdep_indices0.txt poly_mgdep_indices0.txt "$outdir"/
cp bare_mgdep_manifest.json poly_mgdep_manifest.json "$outdir"/

label_tag="${LABEL_TAG:-r8mgdep}"
dt_fs="${DT_FS:-0.5}"
ps="${PS:-500}"
temperature="${T_K:-300}"
fcap="${FCAP:-60}"
export T17_ABORT_ON_CAP="${T17_ABORT_ON_CAP:-1}"
export T17_MAX_T_K="${T17_MAX_T_K:-1500}"
steps="$(python3 - <<PY
print(int(round(float("$ps") * 1000.0 / float("$dt_fs"))))
PY
)"
seeds=(${SEEDS:-2026070201 2026070202})

exec 201>/tmp/t17_mgdep_texture.lock
flock -n 201 || { echo "another T17 Mg-deposit texture launcher is active" >&2; exit 0; }

echo "# T17 Mg-deposit texture probes: ps=$ps dt_fs=$dt_fs steps=$steps T=$temperature fcap=$fcap model=$model"
for seed in "${seeds[@]}"; do
  for system in bare poly; do
    start="${system}_mgdep_start.xyz"
    idx="${system}_mgdep_indices0.txt"
    label="${system}_${label_tag}_seed${seed}_${ps}ps"
    if [ -s "${label}_done.json" ]; then
      echo "skip existing $label"
    else
      if compgen -G "${label}_*" >/dev/null; then
        stamp="$(date +%Y%m%d_%H%M%S)"
        mkdir -p failed
        echo "archive partial/failed $label -> failed/${label}_${stamp}/"
        mkdir -p "failed/${label}_${stamp}"
        mv "${label}_"* "failed/${label}_${stamp}/"
      fi
      echo "launch $label"
      "$py" "$driver" "$model" "$start" "$label" "$steps" "$temperature" "$dt_fs" "$fcap" 0.0 None 0.0 "$seed" \
        > "logs/${label}.log" 2>&1
    fi
    if [ -s "${label}_traj.xyz" ]; then
      "$py" "$texture" "${label}_traj.xyz" "$outdir/${label}_texture" 0.5 "$idx" --nslab 64
    fi
  done
done

echo "# T17 Mg-deposit texture launcher complete"
