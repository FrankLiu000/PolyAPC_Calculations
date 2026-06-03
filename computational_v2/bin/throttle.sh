#!/usr/bin/env bash
# throttle.sh [manifest.txt] — submit the G16 molecular fan-out packed onto the
# 96 physical cores of the single CPU node, keeping Sum(cores) <= MAXCORES.
#
# manifest.txt format (one job per line; '#' comments and blanks ignored):
#   <name> <ncores> <mem> [phase_dir] [dependency_jobname]
#   e.g.  AlCl4m_opt   8  14GB  P0a_speciation
#         AlCl4m_tzvp  8  14GB  P0a_speciation  AlCl4m_opt   # chained afterok
#
# Submits each via:  sbatch -c <ncores> --mem <mem> bin/run_g16.sh <name>
# A simple admission loop blocks until enough cores free up (SLURM also packs).
set -euo pipefail

MANIFEST="${1:-manifest.txt}"
MAXCORES="${MAXCORES:-96}"
RUNG16="$(dirname "$0")/run_g16.sh"
declare -A JID         # jobname -> submitted SLURM job id

used_cores() {
  # cores currently requested by our running+pending jobs
  squeue -h -u "$USER" -o "%C" 2>/dev/null | awk '{s+=$1} END{print s+0}'
}

[ -f "$MANIFEST" ] || { echo "throttle: no manifest '$MANIFEST'" >&2; exit 1; }

while read -r name ncores mem phase dep _rest; do
  [ -z "${name:-}" ] && continue
  case "$name" in \#*) continue;; esac
  ncores="${ncores:-8}"; mem="${mem:-14GB}"; phase="${phase:-.}"

  # admission control: wait until this job fits under MAXCORES
  while [ "$(( $(used_cores) + ncores ))" -gt "$MAXCORES" ]; do sleep 20; done

  depflag=()
  if [ -n "${dep:-}" ] && [ -n "${JID[$dep]:-}" ]; then
    depflag=(--dependency=afterok:"${JID[$dep]}")
  fi

  rundir="${RUNDIR:-$phase/gjf}"   # RUNDIR overrides per-phase dirs (shared chk pool)
  # no --mem: this node tracks CPUs only (CR_CPU, RealMemory=1); Gaussian %mem self-limits
  jid=$(sbatch --parsable -c "$ncores" -D "$rundir" "${depflag[@]}" \
        "$RUNG16" "$name")
  JID[$name]="$jid"
  echo "[throttle] submitted $name (${ncores}c ${mem}) jid=$jid ${dep:+dep=$dep}"
done < "$MANIFEST"

echo "[throttle] all jobs submitted."
