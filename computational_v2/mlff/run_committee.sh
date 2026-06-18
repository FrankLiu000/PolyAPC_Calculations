#!/bin/bash
# Train committee members (different seeds, identical recipe) for the active-learning σ_F detector.
# Sequential (single GPU). Production models (seed 20260616) are member s1; this adds s2,s3 per system.
set -e
cd "$(dirname "$0")"
EPOCHS=${EPOCHS:-60}
# spec: label:seed:trainfile  (override the default set via SPECS env)
SPECS=${SPECS:-"bare:2:mlff_bare_train.xyz bare:3:mlff_bare_train.xyz poly:2:mlff_poly_train.xyz poly:3:mlff_poly_train.xyz"}
for spec in $SPECS ; do
  IFS=: read lab seed tf <<< "$spec"
  name="apc_${lab}_s${seed}"; work="run_${lab}_s${seed}"
  echo "=== committee member $name (seed $seed, $tf, $EPOCHS ep) $(date) ==="
  rm -rf "$work" "${name}_"*
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  NAME="$name" EPOCHS="$EPOCHS" BATCH=4 DTYPE=float32 LR=0.01 E0S=average LOSS=weighted \
  EWEIGHT=0 FWEIGHT=100 SWA=no MULTIHEAD=False SEED="$seed" TRAIN="$tf" WORK="$work" \
  bash run_train.sh
done
echo "=== COMMITTEE_DONE $(date) ==="
ls -la run_{bare,poly}_s{2,3}/*.model 2>/dev/null
