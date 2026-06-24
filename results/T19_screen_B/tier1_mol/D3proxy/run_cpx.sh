export g16root=/CH GAUSS_EXEDIR=/CH/g16 PATH=/CH/g16:$PATH
cd /CH/Claude_Calcs_20260603/results/T19_screen_B/tier1_mol/D3proxy
one(){ local j=$1; export GAUSS_SCRDIR=/tmp/g16cpx_${j}_$$; mkdir -p $GAUSS_SCRDIR
  /CH/g16/g16 < ${j}_cpx.gjf > ${j}_cpx.log 2>&1
  echo "done $j: norm=$(grep -c 'Normal termination' ${j}_cpx.log)"; rm -rf $GAUSS_SCRDIR; }
for j in disiloxane Me2O BSiOx phosphazene AlOH3; do one $j & done
wait; echo "D3PROXY_COMPLEX_OPTS_DONE"
