#!/usr/bin/env bash
# scf_health.sh [run_dir] — one-shot SCF-convergence health scan of the G16 fan-out.
# Classifies each job: Normal | in-progress(scf-cycles) | SCF-FAILURE(shaking) | ERROR.
set +u
RM="${1:-/CH/poly_v2/run_mol}"
norm=0; inprog=0; scffail=0; othererr=0
echo "==== SCF health @ $(date +%H:%M:%S)  ($RM) ===="
for log in "$RM"/*.log; do
  [ -e "$log" ] || { echo "(no logs yet)"; break; }
  bn=$(basename "$log"); case "$bn" in g16-*) continue;; esac
  name=${bn%.log}
  if grep -q "Normal termination" "$log"; then
    norm=$((norm+1))
  elif grep -qE "Convergence failure|SCF has *not *converged" "$log"; then
    scffail=$((scffail+1)); printf "  %-34s SCF-FAILURE (shaking)%s\n" "$name" "$([ -f "$RM/$name.remediated" ] && echo ' [remedied]')"
  elif grep -q "Error termination" "$log"; then
    othererr=$((othererr+1)); printf "  %-34s ERROR (non-SCF)\n" "$name"
  else
    inprog=$((inprog+1))
    cyc=$(grep -c "Cycle " "$log" 2>/dev/null)
    printf "  %-34s in-progress (scf-cycles so far=%s)\n" "$name" "$cyc"
  fi
done
running=$(squeue -h -u "$USER" -n g16 -o "%i" 2>/dev/null | wc -l)
echo "---- normal=$norm  in-progress=$inprog  SCF-FAIL=$scffail  other-err=$othererr  |  in-queue=$running ----"
