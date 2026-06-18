#!/bin/bash
# Cron watchdog: relaunch poly REUS if it died and isn't done (survives LYZ-ROG reboots).
# crontab:  */15 * * * * .../watchdog_reus.sh   and   @reboot sleep 90 && .../watchdog_reus.sh
cd /lyz/Claude_workplace/PolyAPC_Calculations/computational_v2/mlff || exit 0
[ -f umb_poly_reus_DONE ] && exit 0                 # finished
pgrep -f '[r]eus.py' >/dev/null && exit 0           # already running
pgrep -f '[m]ace_run_train' >/dev/null && exit 0    # GPU busy with training — defer
setsid bash run_poly_reus.sh >> poly_reus.log 2>&1 < /dev/null &
echo "$(date): watchdog relaunched poly REUS" >> poly_reus_watchdog.log
