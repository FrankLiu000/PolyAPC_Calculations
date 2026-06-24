#!/usr/bin/env bash
export g16root=/CH GAUSS_EXEDIR=/CH/g16 PATH=/CH/g16:$PATH GAUSS_SCRDIR=/tmp/g16d4_$$
mkdir -p $GAUSS_SCRDIR
cd /CH/Claude_Calcs_20260603/results/T19_screen_B/tier1_mol/D4proxy
for j in THF Me2O disiloxane Mg_THF Mg_Me2O Mg_disiloxane; do
  /CH/g16/g16 < $j.gjf > $j.log 2>&1
done
echo "D4proxy v2 done"; rm -rf $GAUSS_SCRDIR
