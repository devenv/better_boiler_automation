#!/bin/sh

. venv/bin/activate
cd boiler

export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.
export DD_TRACE_ENABLED=False
export STATS_ENABLED=True
export DD_SERVICE=scheduler

python3.7 run.py