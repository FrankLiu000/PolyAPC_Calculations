#!/usr/bin/env bash
# aimd_campaign.sh — unattended replicate real-ion interface AIMD (bare vs poly).
# Runs trajectories SEQUENTIALLY at 96 ranks (one AIMD per node). bare_r1 is already
# submitted (jid passed as $1); this waits for it, validates it produced MD steps,
# then runs poly_r1 and replicates r2/r3 (independent velocity SEEDs). Logs progress.
set +u
P0D=/CH/poly_v2/P0d_interface/inp; BIN=/CH/poly_v2/bin; LOG=$P0D/_aimd_campaign.log
ts(){ date +%H:%M:%S; }
wait_jid(){ while [ -n "$(squeue -h -j "$1" -o '%i' 2>/dev/null)" ]; do sleep 120; done; }
steps(){ grep -c 'MD| Step_nr\|Step number' "$P0D/$1.out" 2>/dev/null; }
run(){  # $1 = jobname (input <jobname>.inp must exist)
  local jid=$(sbatch --parsable --ntasks=96 -D "$P0D" "$BIN/run_cp2k.sh" "$1")
  echo "[$(ts)] submitted $1 (jid=$jid)" >>"$LOG"; wait_jid "$jid"
  echo "[$(ts)] $1 done: MD_steps=$(steps "$1") ended=$(grep -c 'PROGRAM ENDED' "$P0D/$1.out" 2>/dev/null)" >>"$LOG"
}
echo "[$(ts)] campaign start; waiting on bare_r1 jid=$1" >>"$LOG"
wait_jid "$1"
nb=$(steps cp2k_aimd_realion_bare)
echo "[$(ts)] bare_r1 finished: MD_steps=$nb" >>"$LOG"
if [ "${nb:-0}" -lt 5 ]; then echo "[$(ts)] bare_r1 did not run (SCF/setup issue) -> ABORTING chain" >>"$LOG"; exit 1; fi
run cp2k_aimd_realion_poly        # poly_r1
for r in 2 3; do
  for sys in bare poly; do
    src="$P0D/cp2k_aimd_realion_${sys}.inp"; dst="$P0D/aimd_${sys}_r${r}.inp"
    sed -e "s/PROJECT aimd_${sys}/PROJECT aimd_${sys}_r${r}/" "$src" > "$dst"
    sed -i "/^&GLOBAL/a\\  SEED ${r}${r}${r}7" "$dst"   # independent initial velocities
    run "aimd_${sys}_r${r}"
  done
done
echo "[$(ts)] AIMD campaign COMPLETE (bare/poly x r1,r2,r3)" >>"$LOG"
