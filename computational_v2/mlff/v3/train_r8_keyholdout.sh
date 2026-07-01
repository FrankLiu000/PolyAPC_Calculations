#!/usr/bin/env bash
# r8 = publication-gated reactive/co-deposition MACE.
# It trains on data_r8_keyholdout/train.xyz and validates on the explicit
# key-reactive holdout set (Al near-surface, Al-on-Mg deposition, Cl-strip).
set -euo pipefail
cd "$(dirname "$0")"

repo="$(cd ../../.. && pwd)"
source "$repo/computational_v2/mlff/safe_wsl_env.sh"
require_mem_gb "${R8_MIN_MEM_GB:-14}"
require_vram_free_gb "${R8_MIN_VRAM_FREE_GB:-8}"

if pgrep -af '[r]eus.py.*umb_poly_reus' >/dev/null && [ "${ALLOW_WITH_REUS:-0}" != "1" ]; then
  echo "REUS is still running on the GPU; not launching r8 training. Set ALLOW_WITH_REUS=1 to override." >&2
  exit 2
fi

VENV=${VENV:-/lyz/Claude_workplace/polyAPC/.mlff_venv}
export PATH="$VENV/bin:$PATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-12}"

NAME=${R8_NAME:-t16_broad_r8_keyholdout}
EPOCHS=${EPOCHS:-220}
DTYPE=${DTYPE:-float32}
BATCH=${BATCH:-4}
WORK=models/run_${NAME}
DATA=data_r8_keyholdout
MARK=R8_KEYHOLDOUT_DONE.marker
mkdir -p "$WORK"

[ -s "$DATA/train.xyz" ] || "$VENV/bin/python" assemble_key_reactive_holdout.py ../incoming "$DATA"

echo "=== r8 START $(date) name=$NAME epochs=$EPOCHS dtype=$DTYPE ==="
"$VENV/bin/mace_run_train" \
  --name="$NAME" --foundation_model=medium --multiheads_finetuning=False \
  --train_file="$DATA/train.xyz" --valid_file="$DATA/val.xyz" \
  --energy_key=energy --forces_key=forces --E0s=average \
  --loss=huber --energy_weight=1 --forces_weight=120 \
  --pair_repulsion --distance_transform=Agnesi \
  --r_max=6.0 --batch_size="$BATCH" --valid_batch_size="$BATCH" --lr=0.006 \
  --max_num_epochs="$EPOCHS" --swa --start_swa=160 --ema --ema_decay=0.99 \
  --seed="${SEED:-20260701}" --device=cuda --default_dtype="$DTYPE" --save_cpu \
  --model_dir="$WORK" --log_dir="$WORK/logs" --checkpoints_dir="$WORK/checkpoints" --results_dir="$WORK/results"

cp -f "$WORK/$NAME.model" "models/${NAME}.model"
"$VENV/bin/python" validate_reactive.py "models/${NAME}.model" "$DATA/test_key.xyz" \
  "../../../results/T17_reactive/key_reactive_validation/${NAME}_test_key" --device cpu | tee "${NAME}_test_key_validation.log"

echo "DONE model=models/${NAME}.model $(date)" > "$MARK"
echo "=== r8 DONE $(date) ==="
