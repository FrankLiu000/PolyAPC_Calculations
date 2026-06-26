#!/bin/bash
export LD_LIBRARY_PATH=/opt/intel/oneapi/2025.2/lib:/opt/intel/oneapi/2025.2/opt/compiler/lib:/opt/intel/oneapi/2025.2/opt/mpi/libfabric/lib:${LD_LIBRARY_PATH:-}
source /lyz/gmx2025.1/bin/GMXRC 2>/dev/null
D=$1; DEF=$2; PIN=$3; cd "$D" || exit 1
while [ ! -f STOP_${DEF} ]; do
  NJOB=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null|grep -c .)
  if [ "${NJOB:-9}" -le 1 ]; then NT=24; PO=""; else NT=12; PO="-pinoffset $PIN"; fi
  CPI=""; [ -f ${DEF}.cpt ] && CPI="-cpi ${DEF}.cpt"
  gmx mdrun -s ${DEF}.tpr -deffnm ${DEF} $CPI -noappend -ntmpi 1 -ntomp $NT -nb gpu -pme gpu -bonded gpu -pin on $PO -maxh 1 -cpt 10 >>${DEF}_run.log 2>&1
  sleep 8
done
