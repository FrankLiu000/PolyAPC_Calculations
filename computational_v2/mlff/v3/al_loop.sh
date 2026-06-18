#!/bin/bash
# T16 active learning: run a committee over a T17 trajectory, flag high-σ_F frames,
# write an AL queue for EPYC to DFT-label. Wraps the v2 committee_uncertainty.py.
# usage: ./al_loop.sh <traj.xyz> <out_queue.xyz> [threshold_meV]
set -e
cd "$(dirname "$0")"
V2=/lyz/Claude_workplace/PolyAPC_Calculations/computational_v2/mlff
PY=/lyz/Claude_workplace/polyAPC/.mlff_venv/bin/python
TRAJ=${1:?traj}; OUT=${2:-al_queue_t17.xyz}; THR=${3:-}
MODELS=$(ls models/run_*/*_s*.model 2>/dev/null | tr '\n' ' ')
[ -n "$MODELS" ] || { echo "need a committee (train >=3 seeds: SEED=.. NAME=t16_s1 ./train_reactive.sh)"; exit 1; }
echo "committee: $MODELS"
$PY "$V2/committee_uncertainty.py" --models $MODELS --traj "$TRAJ" --out "$OUT" ${THR:+--threshold $THR} ${THR:+} ${THR:+}
echo "AL queue -> $OUT ; push to EPYC (computational_v2/mlff/incoming/) for DFT labels, then re-assemble+retrain"
