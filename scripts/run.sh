#!/bin/sh

set -e

. venv/bin/activate
cd boiler

export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.
export DD_TRACE_ENABLED=True
export STATS_ENABLED=True
ddtrace-run python3.7 -m run.py
