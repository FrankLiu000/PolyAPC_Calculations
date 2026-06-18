#!/usr/bin/env bash
# harvest_bias_v2.sh <jobid> — wait for softened bias pilot, append verdict
set +u
JID=$1
INP=/CH/poly_v2/P0d_interface/inp
OUT=/CH/poly_v2/results/data/bias_pilot_verdict.txt
ts(){ date +%F\ %H:%M:%S; }
for i in $(seq 1 8640); do
  [ -z "$(squeue -h -j "$JID" -o '%i' 2>/dev/null)" ] && break
  sleep 60
done
cd "$INP" || exit 9
{
  echo
  echo "# ===== SOFTENED RETRY (bias_pilot_v2, +-1 V, ALPHA0.15/NBROYDEN12, ADDED_MOS400, MAX_SCF250) $(ts) ====="
  conv=$(grep -c "SCF run converged" bias_pilot_v2.out 2>/dev/null)
  fail=$(grep -c "SCF run NOT converged" bias_pilot_v2.out 2>/dev/null)
  ended=$(grep -c "PROGRAM ENDED" bias_pilot_v2.out 2>/dev/null)
  echo "PROGRAM ENDED: $ended | SCF converged steps: $conv | SCF NOT-converged: $fail"
  echo "per-step cycles:"
  awk '/Broy.\/Diag./{c++} /SCF run converged/{print "  converged in "c" cycles"; c=0} /SCF run NOT converged/{print "  FAILED at "c" cycles"; c=0}' bias_pilot_v2.out 2>/dev/null | tail -12
  echo "ener (step / s-step in last col):"
  tail -6 bias_pilot_v2-1.ener 2>/dev/null
  if [ "$ended" -ge 1 ] && [ "$fail" -eq 0 ]; then
    echo "VERDICT: softened +-1V bias AIMD CONVERGES RELIABLY -> production-viable (note s/step cost above)."
  elif [ "$fail" -ge 1 ]; then
    echo "VERDICT: still hits SCF failures at +-1V -> needs further hardening (Pulay mixing / looser EPS_SCF / lower field)."
  else
    echo "VERDICT: incomplete (walltime/other) -- check bias_pilot_v2.out."
  fi
} >> "$OUT" 2>&1
