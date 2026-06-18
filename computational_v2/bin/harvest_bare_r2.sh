#!/usr/bin/env bash
# harvest_bare_r2.sh <bare_r2_aimd_jobid>
# Wait for the bare_r2 replicate interface AIMD, then answer THE load-bearing question
# for story S1: does the chloride abstraction RECUR with an independent velocity seed?
# Appends a replicate block to results/data/aimd_interface_stats.txt
set +u
JID=$1
INP=/CH/poly_v2/P0d_interface/inp
OUT=/CH/poly_v2/results/data/aimd_interface_stats.txt
LOG=$INP/_harvest_bare_r2.log
ts(){ date +%F\ %H:%M:%S; }
echo "[$(ts)] waiting on job $JID" >> "$LOG"
# wait up to 96 h, keyed to the job id (not output-file grep)
for i in $(seq 1 5760); do
  [ -z "$(squeue -h -j "$JID" -o '%i' 2>/dev/null)" ] && break
  sleep 60
done
echo "[$(ts)] job $JID gone; analyzing" >> "$LOG"
cd "$INP" || exit 9
{
  echo
  echo "# ===== REPLICATE bare_r2 (independent velocity seed, same start geometry) ====="
  echo "# Key question: does the cation->Cl abstraction recur? Generated $(ts) by harvest_bare_r2.sh"
  echo
  python3 /CH/poly_v2/bin/analyze_interface_access.py aimd_bare_r2-pos-1.xyz bare_r2 /CH/poly_v2/results/data/bare_r2
  echo
  python3 - <<'EOF'
import numpy as np, sys
sys.path.insert(0, '/CH/poly_v2/bin')
from analyze_interface_access import frames
d148, d149 = [], []
last = None
for syms, x in frames("aimd_bare_r2-pos-1.xyz"):
    al = x[147]
    d148.append(np.linalg.norm(x[148]-al)); d149.append(np.linalg.norm(x[149]-al))
    last = (syms, x)
d148, d149 = np.array(d148), np.array(d149)
for lab, d in [("Cl148", d148), ("Cl149", d149)]:
    far = np.where(d > 3.0)[0]
    print("bare_r2  Al-%s mean %.2f final %.2f max %.2f | frac(>3A) %.2f%s"
          % (lab, d.mean(), d[-1], d.max(), len(far)/len(d),
             ("  first-departure t=%.2f ps" % (far[0]/1000.)) if len(far) else ""))
syms, x = last
for idx in (148, 149):
    cl = x[idx]; dd = np.linalg.norm(x - cl, axis=1); dd[idx] = 99
    near = np.argsort(dd)[:3]
    print("bare_r2  Cl%d final neighbors: %s" % (idx, ", ".join("%s%d %.2f" % (syms[i], i, dd[i]) for i in near)))
ab = (len(np.where(d148 > 3.0)[0]) > 0.5*len(d148)) or (len(np.where(d149 > 3.0)[0]) > 0.5*len(d149))
print()
print("VERDICT: abstraction %s in replicate r2 (criterion: either Cl >3 A from Al for >50%% of frames)"
      % ("RECURS" if ab else "DOES NOT RECUR"))
print("# If RECURS: S1 gateway is seed-robust (start-geometry sensitivity still untested).")
print("# If NOT: abstraction is stochastic/rare on 10 ps -> S1 needs the molecular abstraction-dG test")
print("#         (with/without network fragment) before any assertion. See HANDOFF v3 sec.5/6.")
EOF
} >> "$OUT" 2>> "$LOG"
echo "[$(ts)] appended replicate block to $OUT" >> "$LOG"
