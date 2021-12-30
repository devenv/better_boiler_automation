#!/bin/sh

set -e

. venv/bin/activate
cd boiler

export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.
export DD_TRACE_ENABLED=True
export STATS_ENABLED=True
export DD_SERVICE=scheduler

#ddtrace-run python3.7 run.py
python3.7 run.py