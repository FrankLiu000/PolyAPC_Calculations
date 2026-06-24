export g16root=/CH GAUSS_EXEDIR=/CH/g16 PATH=/CH/g16:$PATH
cd /CH/Claude_Calcs_20260603/results/T19_screen_B/tier1_mol/D3proxy
one(){ local j=$1; export GAUSS_SCRDIR=/tmp/g16d3_${j}_$$; mkdir -p $GAUSS_SCRDIR
  /CH/g16/g16 < $j.gjf > $j.log 2>&1
  echo "done $j: norm=$(grep -c 'Normal termination' $j.log)"; rm -rf $GAUSS_SCRDIR; }
for j in disiloxane Me2O BSiOx phosphazene AlOH3 AlCl4; do one $j & done
wait; echo "D3PROXY_FRAGMENTS_DONE"
