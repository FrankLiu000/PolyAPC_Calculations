#!/bin/bash
# T16 — fine-tune MACE-MP-0 into a REACTIVE Mg/electrolyte/SEI FF (energy+forces).
# Differs from v2 run_train.sh: EWEIGHT=1 (energy ON — reactive PES needs energies),
# r_max 6.0 (Al-anion + SEI longer-range), float64 (reactive energetics), broader data.
# Smoke:  EPOCHS=2 NAME=t16_smoke ./train_reactive.sh
# Full :  ./train_reactive.sh
set -e
cd "$(dirname "$0")"
VENV=/lyz/Claude_workplace/polyAPC/.mlff_venv
export PATH="$VENV/bin:$PATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True   # POSS graph pins GPU otherwise (v2 gotcha)
NAME=${NAME:-t16_reactive}; EPOCHS=${EPOCHS:-300}; DTYPE=${DTYPE:-float64}
BATCH=${BATCH:-4}; FWEIGHT=${FWEIGHT:-100}; EWEIGHT=${EWEIGHT:-1}   # energy ON for reactive
LOSS=${LOSS:-huber}; LR=${LR:-0.01}; E0S=${E0S:-average}; RMAX=${RMAX:-6.0}
TRAIN=${TRAIN:-data/train.xyz}; VALID=${VALID:-data/val.xyz}; WORK=${WORK:-models/run_${NAME}}
mkdir -p "$WORK" models
[ -s "$TRAIN" ] || { echo "FATAL: $TRAIN missing — run assemble_dataset.py on EPYC's incoming/ first"; exit 1; }
echo "=== T16 MACE reactive fine-tune: $NAME ep=$EPOCHS dtype=$DTYPE EWEIGHT=$EWEIGHT r_max=$RMAX $(date) ==="
"$VENV/bin/mace_run_train" \
  --name="$NAME" --foundation_model=medium --multiheads_finetuning=False \
  --train_file="$TRAIN" $([ -s "$VALID" ] && echo --valid_file="$VALID" || echo --valid_fraction=0.10) \
  --energy_key=energy --forces_key=forces --E0s="$E0S" \
  --loss="$LOSS" --energy_weight="$EWEIGHT" --forces_weight="$FWEIGHT" \
  --lr="$LR" --r_max="$RMAX" --batch_size="$BATCH" --valid_batch_size="$BATCH" \
  --max_num_epochs="$EPOCHS" --swa --ema --ema_decay=0.99 \
  --seed="${SEED:-20260618}" --device=cuda --default_dtype="$DTYPE" --save_cpu --restart_latest \
  --model_dir="$WORK" --log_dir="$WORK/logs" --checkpoints_dir="$WORK/checkpoints" --results_dir="$WORK/results"
cp -f "$WORK/$NAME.model" "models/${NAME}.model" 2>/dev/null || true
echo "=== T16 TRAIN_DONE $NAME $(date) -> models/${NAME}.model ==="
