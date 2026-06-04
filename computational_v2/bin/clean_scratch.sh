#!/usr/bin/env bash
# clean_scratch.sh — routinely remove Gaussian scratch dirs of TERMINATED jobs.
# Safe by construction: a scratch dir is deleted ONLY when
#   (a) it belongs to one of our jobs   (a matching run_mol/<name>.gjf exists),
#   (b) run_mol/<name>.log shows a terminal line (Normal/Error termination => the
#       g16 process has finished), AND
#   (c) the dir has not been modified in the last GRACE seconds (guards a freshly
#       resubmitted job that is reusing the same scratch path).
# Running/pending jobs (no terminal line yet) are never touched, nor are other
# users' scratch dirs. New jobs also self-clean via the EXIT trap in run_g16.sh;
# this sweep handles the backlog and any crash that pre-dated the trap.
set +u
SCR=/mnt/scratch_disk/g16_scratch
RM=/CH/poly_v2/run_mol
GRACE=${GRACE:-300}
now=$(date +%s); freed_kb=0; n=0
for d in "$SCR"/*/; do
  [ -d "$d" ] || continue
  name=$(basename "$d")
  [ -f "$RM/$name.gjf" ] || continue
  log="$RM/$name.log"; [ -f "$log" ] || continue
  grep -qE "Normal termination|Error termination" "$log" || continue
  mtime=$(stat -c %Y "$d" 2>/dev/null || echo "$now")
  [ $(( now - mtime )) -lt "$GRACE" ] && continue
  sz=$(du -sk "$d" 2>/dev/null | awk '{print $1+0}')
  if rm -rf "$d"; then freed_kb=$(( freed_kb + sz )); n=$((n+1)); fi
done
echo "[clean_scratch $(date +%H:%M:%S)] removed $n terminated-job scratch dirs, freed ~$(( freed_kb/1024 )) MB"
