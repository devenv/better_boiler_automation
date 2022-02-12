#!/bin/sh

name=$1

sh deploy_module.sh $name

. venv/bin/activate
cd $name

export PYTHONPATH=/home/pi/venv/lib/python3.9/site-packages:.
export STATS_ENABLED=True
export LOGGER_ENABLED=True
export GLOBAL_STORE=True

python -m runners.run_module $name