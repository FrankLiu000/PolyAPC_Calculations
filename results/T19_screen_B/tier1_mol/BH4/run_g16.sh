#!/usr/bin/env bash
export g16root=/CH
export GAUSS_EXEDIR=/CH/g16
export PATH=/CH/g16:$PATH
export GAUSS_SCRDIR=/tmp/g16scr_$$
mkdir -p $GAUSS_SCRDIR
cd /CH/Claude_Calcs_20260603/results/T19_screen_B/tier1_mol/BH4
/CH/g16/g16 < BH4m_anion.gjf > BH4m_anion.log 2>&1
/CH/g16/g16 < BH4_red.gjf > BH4_red.log 2>&1
echo "BH4 D1 done"
rm -rf $GAUSS_SCRDIR
