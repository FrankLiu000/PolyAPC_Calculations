#!/usr/bin/env bash
# harvest_clean_md.sh <md_jobid> <sys>   (sys = bare | poly)
# Wait for a clean-start interface MD, then re-evaluate the chloride-abstraction
# question on the UNcorrupted trajectory. Writes results/data/aimd_clean_<sys>.txt
# and a one-line VERDICT (did the abstraction survive the clean start?).
set +u
JID=$1; SYS=$2
INP=/CH/poly_v2/P0d_interface/inp
OUT=/CH/poly_v2/results/data/aimd_clean_${SYS}.txt
LOG=$INP/_harvest_clean_${SYS}.log
ts(){ date +%F\ %H:%M:%S; }
echo "[$(ts)] waiting on $SYS MD job $JID" >> "$LOG"
for i in $(seq 1 7200); do            # up to 120 h
  [ -z "$(squeue -h -j "$JID" -o '%i' 2>/dev/null)" ] && break
  sleep 60
done
echo "[$(ts)] job $JID gone; analyzing clean $SYS" >> "$LOG"
cd "$INP" || exit 9
TRAJ=aimd_${SYS}_clean-pos-1.xyz
{
  echo "# CLEAN-START interface AIMD — $SYS (repaired geometry, slab-fixed GEO_OPT then MD)"
  echo "# Re-evaluation of the chloride-abstraction finding after fixing the corrupted"
  echo "# cation-Cl start (Cl66/67/68 were stacked; old run exploded T>1000K). $(ts)"
  echo
  python3 /CH/poly_v2/bin/analyze_interface_access.py "$TRAJ" "${SYS}_clean" /CH/poly_v2/results/data/${SYS}_clean
  echo
  python3 - "$TRAJ" "$SYS" <<'PYEOF'
import numpy as np, sys
sys.path.insert(0, '/CH/poly_v2/bin')
from analyze_interface_access import frames
traj, lab = sys.argv[1], sys.argv[2]
d148, d149, tmax = [], [], 0.0
for syms, x in frames(traj):
    al = x[147]
    d148.append(np.linalg.norm(x[148]-al)); d149.append(np.linalg.norm(x[149]-al))
d148, d149 = np.array(d148), np.array(d149)
ab = False
for nm, d in [("Cl148", d148), ("Cl149", d149)]:
    far = np.where(d > 3.0)[0]
    fr = len(far)/len(d)
    if fr > 0.5: ab = True
    print("%s  Al-%s mean %.2f final %.2f max %.2f | frac(>3A) %.2f%s"
          % (lab, nm, d.mean(), d[-1], d.max(), fr,
             ("  first-departure t=%.2f ps" % (far[0]/1000.)) if len(far) else ""))
print()
print("VERDICT (%s): chloride abstraction %s on the clean start" % (lab, "RECURS" if ab else "DOES NOT RECUR"))
print("# If DOES NOT RECUR on a clean start -> the original 'gateway' was an artifact of the")
print("#   exploding corrupted geometry; the v3 flagship story must be retracted/rewritten.")
print("# If RECURS cleanly -> the finding is real and was merely confounded, not caused, by the bug.")
PYEOF
} > "$OUT" 2>> "$LOG"
echo "[$(ts)] wrote $OUT" >> "$LOG"
