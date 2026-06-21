#!/bin/bash
# r7 = r6 smoothing recipe (ZBL pair_repulsion + Agnesi) RE-ASSEMBLED to finally
# include EPYC's batch-2 frames that r6 missed (reused stale 15:51 train.xyz):
#   near_mg_steered_labeled.xyz (56, the 2.5-3.2 A gap-fill) + neutral_reactive (104).
# These cover EXACTLY the close-approach zone where bare MD blew up at 3.2 A / 11.5 ps.
# Self-contained + reboot-safe: guard-kills GPU, re-assembles, trains, validates, marks.
cd "$(dirname "$0")"
VENV=/lyz/Claude_workplace/polyAPC/.mlff_venv
export PATH="$VENV/bin:$PATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=12
NAME=t16_broad_r7; SEED=20260621; WORK=models/run_${NAME}
MARK=R7_DONE.marker
rm -f "$MARK"
echo "=== r7 START $(date) ==="

# (1) GPU must be free — no MLFF-MD may run during training (2-concurrent hang)
for p in $(ps -eo pid,args --no-headers | grep '[i]nterface_mlff_md' | awk '{print $1}'); do kill -9 $p 2>/dev/null; done
sleep 4
echo "MLFF-MD alive after guard-kill: $(ps -eo args --no-headers|grep -c '[i]nterface_mlff_md')"

# (2) re-assemble from incoming/ (picks up steered + neutral that r6 missed); back up r6 data
[ -d data ] && cp -r data data_r6_backup 2>/dev/null
"$VENV/bin/python" assemble_dataset.py ../incoming data 0.1 0.1 2>&1 | tail -40

# (3) verify the gap-fill frames are now IN the training set
NTRAIN=$(grep -c Lattice data/train.xyz 2>/dev/null)
NSTEER=$(grep -ic 'steer\|near_mg' data/train.xyz 2>/dev/null)
NNEUT=$(grep -ic 'neutral' data/train.xyz 2>/dev/null)
echo "=== assembled: train=$NTRAIN  steer/nearmg-refs=$NSTEER  neutral-refs=$NNEUT ==="
if [ "$NTRAIN" -lt 700 ]; then echo "R7_ABORT: train set too small ($NTRAIN) — assemble failed"; echo "FAIL assemble" > "$MARK"; exit 1; fi

# (4) train r7 — EXACT r6 recipe: foundation medium, ZBL pair_repulsion + Agnesi,
#     float32, r_max6, huber, fw100/ew1, SWA@150, EMA0.99, 200 epochs
mkdir -p "$WORK"
"$VENV/bin/mace_run_train" \
  --name="$NAME" --foundation_model=medium --multiheads_finetuning=False \
  --train_file=data/train.xyz --valid_file=data/val.xyz \
  --energy_key=energy --forces_key=forces --E0s=average \
  --loss=huber --energy_weight=1 --forces_weight=100 \
  --pair_repulsion --distance_transform=Agnesi \
  --r_max=6.0 --batch_size=4 --valid_batch_size=4 --lr=0.01 \
  --max_num_epochs=200 --swa --start_swa=150 --ema --ema_decay=0.99 \
  --seed=$SEED --device=cuda --default_dtype=float32 --save_cpu --restart_latest \
  --model_dir="$WORK" --log_dir="$WORK/logs" --checkpoints_dir="$WORK/checkpoints" --results_dir="$WORK/results" \
  2>&1 | tail -25
cp -f "$WORK/$NAME.model" "models/${NAME}.model" 2>/dev/null
if [ ! -s "models/${NAME}.model" ]; then echo "R7_ABORT: no model produced"; echo "FAIL train" > "$MARK"; exit 1; fi

# (5) validate force MAE vs held-out DFT
MAE=$("$VENV/bin/python" validate_reactive.py "models/${NAME}.model" data/test.xyz 2>&1 | grep -iE 'GLOBAL force MAE|force MAE' | head -1)
echo "=== r7 VALIDATE: $MAE ==="
echo "DONE model=models/${NAME}.model | $MAE | train=$NTRAIN $(date)" > "$MARK"
echo "=== r7 TRAIN_DONE $(date) ==="
