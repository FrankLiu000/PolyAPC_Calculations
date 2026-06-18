#!/usr/bin/env bash
# scf_monitor.sh — routine SCF-convergence watchdog for the molecular fan-out.
# Every INTERVAL s it scans run_mol logs and, on detecting a "shaking" job
# (SCF convergence failure), acts ONCE:
#   * leaf job (redox/SEI/raman-gas) -> auto-remedy (scf_remedy.sh: hardened SCF + guess)
#   * parent job (*_opt/*_ramanopt)  -> FLAG for manual handling (dependents affected)
# It logs health each tick to _scf_monitor.log, and EXITS (to notify the operator)
# whenever it performs an action or the queue empties — so interventions are surfaced.
set +u
RM=/CH/poly_v2/run_mol; BIN=/CH/poly_v2/bin
INT=${INTERVAL:-180}; HL=$RM/_scf_monitor.log
ts(){ date +%H:%M:%S; }
is_leaf(){ case "$1" in *_opt|*_ramanopt) return 1;; *) return 0;; esac; }
echo "[$(ts)] scf_monitor start (interval ${INT}s)" >> "$HL"
tot_acted=0

for i in $(seq 1 480); do
  acted=0
  for log in "$RM"/*.log; do
    [ -e "$log" ] || break
    bn=$(basename "$log"); case "$bn" in g16-*) continue;; esac
    name=${bn%.log}
    grep -q "Normal termination" "$log" && continue
    [ -f "$RM/$name.remediated" ] && continue
    if grep -qE "Convergence failure|SCF has *not *converged" "$log"; then
      if is_leaf "$name"; then
        echo "[$(ts)] SCF-shaking LEAF $name -> auto-remedy" >> "$HL"
        bash "$BIN/scf_remedy.sh" "$name" >> "$HL" 2>&1
      else
        echo "[$(ts)] SCF-shaking PARENT $name -> FLAG (manual; dependents impacted)" >> "$HL"
      fi
      touch "$RM/$name.remediated"; acted=$((acted+1))
    fi
  done
  running=$(squeue -h -u "$USER" -n g16 -o "%i" 2>/dev/null | wc -l)
  tot_acted=$((tot_acted + acted))
  echo "[$(ts)] tick $i: in-queue=$running acted_now=$acted total_remedied=$tot_acted" >> "$HL"
  bash "$BIN/clean_scratch.sh" >> "$HL" 2>&1   # routine scratch cleanup of terminated jobs
  # keep monitoring (auto-remedies logged above); exit only when the molecular queue drains
  [ "$running" -eq 0 ] && { echo "[$(ts)] queue empty -> exiting (total remedied=$tot_acted)" >> "$HL"; exit 0; }
  sleep "$INT"
done
echo "[$(ts)] max iterations reached -> exiting" >> "$HL"
