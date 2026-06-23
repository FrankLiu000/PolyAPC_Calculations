export g16root=/CH GAUSS_EXEDIR=/CH/g16 PATH=/CH/g16:$PATH
cd /CH/Claude_Calcs_20260603/results/T19_screen_B/tier1_mol/D3proxy
one(){ local j=$1; export GAUSS_SCRDIR=/tmp/g16tz_${j}_$$; mkdir -p $GAUSS_SCRDIR
  /CH/g16/g16 < ${j}.gjf > ${j}.log 2>&1
  echo "done $j: norm=$(grep -c 'Normal termination' ${j}.log)"; rm -rf $GAUSS_SCRDIR; }
for j in disiloxane_tz Me2O_tz BSiOx_tz phosphazene_tz AlOH3_tz AlCl4_tz \
         disiloxane_cpxtz Me2O_cpxtz BSiOx_cpxtz phosphazene_cpxtz AlOH3_cpxtz \
         disiloxane_bsse Me2O_bsse BSiOx_bsse phosphazene_bsse AlOH3_bsse; do
  one $j &
  while [ $(jobs -r | wc -l) -ge 6 ]; do wait -n; done
done
wait; echo "D3PROXY_TZ_DONE"
