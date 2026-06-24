export g16root=/CH GAUSS_EXEDIR=/CH/g16 PATH=/CH/g16:$PATH
cd /CH/Claude_Calcs_20260603/results/T19_screen_B/tier1_mol/D3proxy
one(){ local j=$1; export GAUSS_SCRDIR=/tmp/g16cp_${j}_$$; mkdir -p $GAUSS_SCRDIR
  /CH/g16/g16 < ${j}_cp.gjf > ${j}_cp.log 2>&1
  echo "done $j: norm=$(grep -c 'Normal termination' ${j}_cp.log)"; rm -rf $GAUSS_SCRDIR; }
for j in AlOH3 phosphazene; do one $j & done
wait; echo "CP_SP_BATCH1_DONE"
