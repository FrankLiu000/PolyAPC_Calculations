#!/usr/bin/env bash
# harvest_pilots_q2m.sh <last_pilot_jobid> — wait for the charged-slab pilot chain
# (dirichlet -> jellium), then write a verdict block: solver ok? SCF stable? s/step?
set +u
JID=$1
INP=/CH/poly_v2/P0d_interface/inp
OUT=/CH/poly_v2/results/data/bias_pilot_verdict.txt
ts(){ date +%F\ %H:%M:%S; }
for i in $(seq 1 720); do
  [ -z "$(squeue -h -j "$JID" -o '%i' 2>/dev/null)" ] && break
  sleep 60
done
{
  echo "# Charged-slab (CHARGE -2) 50-step AIMD pilots — bias-method validation, $(ts)"
  echo "# Start geometry: final frame of bare 10 ps AIMD; 32 MPI ranks; EPS_SCF 1e-5."
  for P in pilot_q2m_dirichlet pilot_q2m_jellium; do
    O=$INP/$P.out
    echo; echo "== $P =="
    if [ ! -f "$O" ]; then echo "NO OUTPUT (job never started?)"; continue; fi
    grep -q "PROGRAM ENDED" "$O" && echo "completed: yes" || echo "completed: NO (check $O)"
    grep -ci "ABORT" "$O" | xargs echo "aborts:"
    # MD steps reached + timing
    n=$(grep -c "STEP NUMBER" "$O"); echo "MD steps done: $n / 50"
    grep "CP2K       " "$O" | tail -1 | awk '{printf "total walltime %.0f s -> %.1f s/step\n", $7, $7/50}'
    # SCF health: cycles per step (last 10 SCF convergence lines)
    echo "SCF cycles needed (last MD steps):"
    grep -B1 "SCF run converged" "$O" | grep -oE "in +[0-9]+ steps" | tail -10 | sort | uniq -c
    grep -c "SCF run NOT converged" "$O" | xargs echo "SCF failures:"
  done
  echo
  echo "# Decision rule: if dirichlet completed with 0 SCF failures and s/step < ~3x plain"
  echo "# AIMD (~22 s/step at 64 ranks; this pilot is on 32 ranks -> compare to ~44 s/step),"
  echo "# it is the production bias recipe (counter-electrode electrostatics are exact)."
  echo "# Else fall back to jellium (structure/forces ok; energies carry background offset)."
  echo "# PRODUCTION IS PARKED until upgraded wet-lab data lands (user directive)."
} > "$OUT" 2>&1
echo "[harvest_pilots_q2m] wrote $OUT"
