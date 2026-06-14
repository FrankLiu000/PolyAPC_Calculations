#!/usr/bin/env bash
# harvest_bias_prod.sh <jobid> <bare|poly> — field-driven (+-1V) interface AIMD analysis
set +u
JID=$1; SYS=$2
INP=/CH/poly_v2/P0d_interface/inp
OUT=/CH/poly_v2/results/data/bias_prod_${SYS}.txt
ts(){ date +%F\ %H:%M:%S; }
for i in $(seq 1 28800); do [ -z "$(squeue -h -j "$JID" -o '%i' 2>/dev/null)" ] && break; sleep 60; done
sleep 60
cd "$INP" || exit 9
TRAJ=bias_prod_${SYS}-pos-1.xyz
{
  echo "# Production +-1 V biased interface AIMD — $SYS  (constant-V Dirichlet, idealized counter-electrode)"
  echo "# Field ~0.043 V/A (4e8 V/m). Tests whether the field drives anion desolvation/approach/reduction. $(ts)"
  echo
  python3 /CH/poly_v2/bin/analyze_interface_access.py "$TRAJ" "biasprod_${SYS}" /CH/poly_v2/results/data/biasprod_${SYS}
  echo
  python3 - "$TRAJ" "$SYS" <<'PYEOF'
import numpy as np, sys
sys.path.insert(0,'/CH/poly_v2/bin'); from analyze_interface_access import frames
traj,lab=sys.argv[1],sys.argv[2]
d148,d149,hmin=[],[],[]
for syms,x in frames(traj):
    al=x[147]; d148.append(np.linalg.norm(x[148]-al)); d149.append(np.linalg.norm(x[149]-al))
d148,d149=np.array(d148),np.array(d149)
for nm,dd in [("Cl148",d148),("Cl149",d149)]:
    far=np.where(dd>3.0)[0]
    print("%s field  Al-%s mean %.2f final %.2f max %.2f frac>3A %.2f%s"%(lab,nm,dd.mean(),dd[-1],dd.max(),len(far)/len(dd),
          "  Cl-loss t=%.2fps"%(far[0]/1000.) if len(far) else "  (intact)"))
print("# Compare to the zero-field clean run (anion intact, ~10 A from front). Field-driven change = the test.")
PYEOF
} > "$OUT" 2>&1
echo "[harvest_bias_prod] wrote $OUT"
