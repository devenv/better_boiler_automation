#!/bin/sh

. venv/bin/activate

cd boiler_ready

export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.
export STATS_ENABLED=True
export DD_SERVICE=$name

python runners/generate_cron.py