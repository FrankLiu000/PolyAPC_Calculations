#!/usr/bin/env bash
# phase_run.sh <manifest> <label> — submit one molecular wave through throttle.sh
# into the shared RUNDIR (run_mol), wait for it to drain (cancelling any
# never-satisfiable dependencies so the barrier can't hang), then summarise
# Normal-termination counts. Intended to be launched in the background.
set +u
DST=/CH/poly_v2
RM="$DST/run_mol"
export RUNDIR="$RM"
export MAXCORES="${MAXCORES:-96}"
MAN="$1"
LAB="${2:-wave}"
ts(){ date +%H:%M:%S; }

njobs=$(grep -cvE '^\s*#|^\s*$' "$MAN")
echo "[$(ts)] [$LAB] submitting $njobs jobs from $(basename "$MAN")"
bash "$DST/bin/throttle.sh" "$MAN"
echo "[$(ts)] [$LAB] all submitted; waiting for the queue to drain"

while :; do
  q=$(squeue -h -u "$USER" -n g16 -o "%i %t %r")
  [ -z "$q" ] && break
  # cancel jobs whose afterok dependency can never be satisfied (failed parent)
  echo "$q" | awk '$3 ~ /DependencyNeverSatisfied/ {print $1}' | xargs -r scancel
  sleep 30
done

echo "[$(ts)] [$LAB] drained. Per-job summary:"
tot=0; ok=0; bad=""
while read -r name _rest; do
  case "$name" in ''|\#*) continue;; esac
  tot=$((tot+1))
  if [ -f "$RM/$name.log" ] && grep -q "Normal termination" "$RM/$name.log"; then
    ok=$((ok+1))
  else
    bad="$bad $name"
  fi
done < "$MAN"
echo "[$(ts)] [$LAB] Normal termination: $ok / $tot"
[ -n "$bad" ] && echo "[$(ts)] [$LAB] FAILED/incomplete:$bad"
echo "[$(ts)] [$LAB] DONE"
