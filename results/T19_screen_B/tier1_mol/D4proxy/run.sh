#!/usr/bin/env bash
set +u; source /CH/g16/bsd/g16.profile; set -u
export GAUSS_SCRDIR=/tmp/g16_$$; mkdir -p $GAUSS_SCRDIR
cd /CH/Claude_Calcs_20260603/results/T19_screen_B/tier1_mol/D4proxy
for j in Mg2p Me2O disiloxane THF Mg_Me2O Mg_disiloxane Mg_THF; do
  /CH/g16/g16 < $j.gjf > $j.log 2>&1
done
echo "D4proxy done"; rm -rf $GAUSS_SCRDIR
