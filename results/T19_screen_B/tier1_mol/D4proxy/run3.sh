export g16root=/CH GAUSS_EXEDIR=/CH/g16 PATH=/CH/g16:$PATH
cd /CH/Claude_Calcs_20260603/results/T19_screen_B/tier1_mol/D4proxy
run1(){
  local j=$1
  export GAUSS_SCRDIR=/tmp/g16_${j}_$$
  mkdir -p $GAUSS_SCRDIR
  /CH/g16/g16 < $j.gjf > $j.log 2>&1
  echo "done $j: $(grep -c 'Normal termination' $j.log) normterm"
  rm -rf $GAUSS_SCRDIR
}
# 6 tiny jobs, run all in parallel (8 cores each = 48 cores)
for j in THF Me2O disiloxane Mg_THF Mg_Me2O Mg_disiloxane; do run1 $j & done
wait
echo "D4proxy v3 ALL DONE"
