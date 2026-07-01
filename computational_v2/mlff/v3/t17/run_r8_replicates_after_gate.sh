#!/usr/bin/env bash
# Launch matched bare/poly T17 MLFF-MD only after r8 key-holdout validation passes.
set -euo pipefail

repo="$(cd "$(dirname "$0")/../../../.." && pwd)"
mlff="$repo/computational_v2/mlff"
v3="$mlff/v3"
source "$mlff/safe_wsl_env.sh"
require_mem_gb "${T17_MIN_MEM_GB:-12}"
require_vram_free_gb "${T17_MIN_VRAM_FREE_GB:-6}"

model="$v3/models/t16_broad_r8_keyholdout.model"
gate="$repo/results/T17_reactive/key_reactive_validation/t16_broad_r8_keyholdout_test_key_gate.json"
metrics="$repo/results/T17_reactive/key_reactive_validation/t16_broad_r8_keyholdout_test_key_metrics.csv"

if pgrep -af '[m]ace_run_train.*t16_broad_r8_keyholdout' >/dev/null; then
  echo "r8 training is still running; not launching T17." >&2
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
  echo "r8 key-holdout gate did not pass; not launching T17." >&2
  cat "$gate" >&2
  exit 2
fi

cd "$v3/t17"
MODEL="$model" LABEL_TAG="${LABEL_TAG:-r8neutral}" PS="${PS:-500}" SEEDS="${SEEDS:-2026070201 2026070202}" \
  ./run_neutral_replicates.sh
"${PY:-/lyz/Claude_workplace/polyAPC/.mlff_venv/bin/python}" ./summarize_r8_codeposition_texture.py
"${PY:-/lyz/Claude_workplace/polyAPC/.mlff_venv/bin/python}" ./select_post_r8_dft_frames.py
