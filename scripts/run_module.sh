#!/bin/sh

name=$1

. venv/bin/activate
cd $name

export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.
export STATS_ENABLED=True
export DD_SERVICE=$name
export GLOBAL_STORE=True

python -m runners.run_module $name