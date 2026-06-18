#!/usr/bin/env bash
# neb_finish.sh <jid_relax0> <jid_relax6> — complete the MgF2 NEB properly:
# wait for relaxed endpoints -> re-interpolate -> re-run CI-NEB -> extract barrier.
set +u
P2=/CH/poly_v2/phase2; BIN=/CH/poly_v2/bin; LOG=$P2/_neb_finish.log
ts(){ date +%H:%M; }
wj(){ while [ -n "$(squeue -h -j "$1" -o '%i' 2>/dev/null)" ]; do sleep 60; done; }
echo "[$(ts)] waiting endpoint relax $1 $2" >>"$LOG"; wj "$1"; wj "$2"
source ~/miniconda3/etc/profile.d/conda.sh; conda activate build; unset PYTHONPATH
python3 - >>"$LOG" 2>&1 <<'PY'
import numpy as np
try: from ase.mep import NEB
except Exception: from ase.neb import NEB
from ase.io import read
P2='/CH/poly_v2/phase2'
ini=read(f'{P2}/relax_img0-pos-1.xyz',index=-1); fin=read(f'{P2}/relax_img6-pos-1.xyz',index=-1)
for a in (ini,fin): a.set_cell([[9.25,0,0],[0,9.25,0],[0,0,6.104]]); a.set_pbc(True)
imgs=[ini]+[ini.copy() for _ in range(5)]+[fin]; NEB(imgs).interpolate('idpp')
for k,im in enumerate(imgs): im.write(f'{P2}/MgF2_img{k}.xyz')
print("re-interpolated from relaxed endpoints")
PY
rm -f "$P2"/neb_MgF2.out "$P2"/neb_MgF2-1_*.restart "$P2"/neb_MgF2-pos-Replica*
JN=$(sbatch --parsable --ntasks=28 -D "$P2" "$BIN/run_cp2k.sh" neb_MgF2)
echo "[$(ts)] NEB resubmitted jid=$JN" >>"$LOG"; wj "$JN"
python3 - >>"$LOG" 2>&1 <<'PY'
import re,glob,numpy as np
P2='/CH/poly_v2/phase2'; H=27.211386; E=[]
for r in range(1,8):
    f=glob.glob(f'{P2}/neb_MgF2-pos-Replica_nr_{r}-*.xyz')
    es=re.findall(r'E\s*=\s*(-?\d+\.\d+)',open(f[0]).read()) if f else []
    E.append(float(es[-1]) if es else None)
if all(e is not None for e in E):
    b=np.array(E); print("band(Ha):",[round(x,4) for x in E])
    print(f"Mg2+ migration barrier MgF2 = {(b.max()-b[0])*H:.2f} eV (fwd); endpoint dE={(b[-1]-b[0])*H:+.2f} eV")
else: print("band parse incomplete:",E)
PY
echo "[$(ts)] NEB FINISH done" >>"$LOG"
