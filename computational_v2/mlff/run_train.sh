#!/bin/bash
# Fine-tune MACE-MP-0 on the bare-interface DFT-labeled set (LYZ-ROG GPU node).
# Per HANDOFF_GPU_mlff.md. Env-var overridable for smoke-test vs full run.
#   EPOCHS=2 DTYPE=float32 NAME=apc_smoke ./run_train.sh   # quick smoke
#   ./run_train.sh                                          # full run (defaults below)
set -e
cd "$(dirname "$0")"
VENV=/lyz/Claude_workplace/polyAPC/.mlff_venv
export PATH="$VENV/bin:$PATH"

NAME=${NAME:-apc_mlff}
EPOCHS=${EPOCHS:-200}
DTYPE=${DTYPE:-float64}
BATCH=${BATCH:-8}
FWEIGHT=${FWEIGHT:-100}
EWEIGHT=${EWEIGHT:-1}           # set 0 to train FORCE-ONLY (decouples from possibly-inconsistent energies)
LOSS=${LOSS:-huber}             # huber = robust to high-force outlier frames (|F| up to 16 eV/A) that blow up
                                # weighted-MSE (train loss spiked to 2.6e8 -> corrupted Adam -> forces stuck ~1 eV/A)
LR=${LR:-0.01}                  # MACE default; works once E0s absorbs the CP2K<->MACE-MP energy offset
E0S=${E0S:-average}             # 'average' = least-squares atomic E0 from our data -> removes the ~700 eV/atom
                                # CP2K-GTH<->MACE-MP reference offset so energy starts near-correct (no spike).
                                # 'foundation' leaves the offset for the interactions to learn (spikes, slow).
MULTIHEAD=${MULTIHEAD:-False}   # False = specialize on our PES only (single-system production potential)
SWA=${SWA:-yes}                 # 'no' disables SWA stage-two (whose energy_weight=1000 jump is harmful for
                                # force-only training when E/F are not a consistent pair)
TRAIN=${TRAIN:-mlff_train.xyz}
WORK=${WORK:-run_${NAME}}
mkdir -p "$WORK"

echo "=== MACE fine-tune: name=$NAME epochs=$EPOCHS dtype=$DTYPE batch=$BATCH fweight=$FWEIGHT multihead=$MULTIHEAD train=$TRAIN $(date) ==="
"$VENV/bin/mace_run_train" \
  --name="$NAME" \
  --foundation_model=medium \
  --multiheads_finetuning="$MULTIHEAD" \
  --train_file="$TRAIN" \
  --valid_fraction=0.10 \
  --energy_key=energy --forces_key=forces \
  --E0s="$E0S" \
  --loss="$LOSS" --energy_weight="$EWEIGHT" --forces_weight="$FWEIGHT" \
  --lr="$LR" \
  --r_max=5.0 \
  --batch_size="$BATCH" --valid_batch_size="$BATCH" \
  --max_num_epochs="$EPOCHS" \
  $([ "$SWA" = yes ] && echo --swa) \
  --ema --ema_decay=0.99 \
  --seed="${SEED:-20260616}" \
  --device=cuda --default_dtype="$DTYPE" \
  --save_cpu \
  --restart_latest \
  --model_dir="$WORK" --log_dir="$WORK/logs" \
  --checkpoints_dir="$WORK/checkpoints" --results_dir="$WORK/results"
echo "=== TRAIN_DONE $NAME $(date) ==="
ls -la "$WORK"/*.model 2>/dev/null
