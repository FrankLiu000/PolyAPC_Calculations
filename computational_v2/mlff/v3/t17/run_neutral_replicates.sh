#!/usr/bin/env bash
# Launch additional source-verifiable T17 neutral MLFF-MD replicates.
#
# Defaults are publication-oriented: matched bare/poly, 500 ps, 0.5 fs,
# ForceCap60, explicit velocity seeds, and per-run *_meta.json provenance.
# The script refuses to start while the poly REUS PMF job is using the GPU.
set -euo pipefail

repo="$(cd "$(dirname "$0")/../../../.." && pwd)"
mlff="$repo/computational_v2/mlff"
work="$mlff/v3/t17"
source "$mlff/safe_wsl_env.sh"
require_mem_gb "${T17_MIN_MEM_GB:-12}"
require_vram_free_gb "${T17_MIN_VRAM_FREE_GB:-6}"
py="${PY:-/lyz/Claude_workplace/polyAPC/.mlff_venv/bin/python}"
driver="$mlff/v3/interface_mlff_md.py"
model="${MODEL:-$mlff/v3/models/t16_broad_r6.model}"
dt_fs="${DT_FS:-0.5}"
ps="${PS:-500}"
temperature="${T_K:-300}"
fcap="${FCAP:-60}"
steps="$(python3 - <<PY
print(int(round(float("$ps") * 1000.0 / float("$dt_fs"))))
PY
)"
seeds=(${SEEDS:-2026070101 2026070102})

if pgrep -af 'reus.py.*umb_poly_reus' >/dev/null && [ "${ALLOW_WITH_REUS:-0}" != "1" ]; then
  echo "REUS is still running on the GPU; not launching T17 replicates. Set ALLOW_WITH_REUS=1 to override." >&2
  exit 2
fi

exec 200>/tmp/t17_neutral_replicates.lock
flock -n 200 || { echo "another T17 neutral replicate launcher is active" >&2; exit 0; }

cd "$work"
mkdir -p logs
echo "# T17 neutral replicates: ps=$ps dt_fs=$dt_fs steps=$steps T=$temperature fcap=$fcap model=$model"

for seed in "${seeds[@]}"; do
  for system in bare poly; do
    start="${system}_start.xyz"
    label="${system}_neutral_seed${seed}_${ps}ps"
    if [ -s "${label}_cv.csv" ] && [ -s "${label}_meta.json" ]; then
      echo "skip existing $label"
      continue
    fi
    echo "launch $label"
    "$py" "$driver" "$model" "$start" "$label" "$steps" "$temperature" "$dt_fs" "$fcap" 0.0 None 0.0 "$seed" \
      > "logs/${label}.log" 2>&1
  done
done

echo "# T17 neutral replicate launcher complete"
