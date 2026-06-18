#!/usr/bin/env bash
# throttle.sh [manifest.txt] — submit the G16 molecular fan-out with dependency-aware
# ordering, pacing so RUNNING jobs' cores stay <= MAXCORES (SLURM also enforces the
# node's hard 96-core cap; RAM is safe because any 96-core mix is <=~192 GB < free).
# RUNDIR overrides the per-phase dirs so all jobs share one .chk pool.
#   manifest line:  <name> <ncores> <mem> [phase_dir] [dependency_jobname]
set -euo pipefail

MANIFEST="${1:-manifest.txt}"
MAXCORES="${MAXCORES:-96}"
RUNG16="$(dirname "$0")/run_g16.sh"
declare -A JID         # jobname -> submitted SLURM job id (for afterok chaining)

used_cores() {
  # cores of our RUNNING jobs only (pending-dependency jobs must not stall admission)
  squeue -h -u "$USER" -t R -o "%C" 2>/dev/null | awk '{s+=$1} END{print s+0}'
}

[ -f "$MANIFEST" ] || { echo "throttle: no manifest '$MANIFEST'" >&2; exit 1; }

while read -r name ncores mem phase dep _rest; do
  [ -z "${name:-}" ] && continue
  case "$name" in \#*) continue;; esac
  ncores="${ncores:-8}"; phase="${phase:-.}"

  # admission: wait until this job's cores fit under MAXCORES of currently-running work
  while [ "$(( $(used_cores) + ncores ))" -gt "$MAXCORES" ]; do sleep 20; done

  depflag=()
  if [ -n "${dep:-}" ] && [ -n "${JID[$dep]:-}" ]; then
    depflag=(--dependency=afterok:"${JID[$dep]}")
  fi

  rundir="${RUNDIR:-$phase/gjf}"   # shared chk pool when RUNDIR set
  jid=$(sbatch --parsable -c "$ncores" -D "$rundir" "${depflag[@]}" "$RUNG16" "$name")
  JID[$name]="$jid"
  echo "[throttle] submitted $name (${ncores}c ${mem:-}) jid=$jid ${dep:+dep=$dep}"
done < "$MANIFEST"

echo "[throttle] all jobs submitted."
