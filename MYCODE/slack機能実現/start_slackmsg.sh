#!/bin/bash
#
# slack mes send起動スクリプト
#

. ./myserver.env
. ./cmd
. ./goenv.sh
. ./nodeenv.sh
. ./pythonenv.sh



pushd $MYSERVER_ROOT/PetWatcher/Automate

echo "#################################"
echo "Start distance_slack.py"
./distance_slack.py &

