#!/bin/sh

set -e

. venv/bin/activate
cd boiler

export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.
ddtrace-run python3.7 -m run.py
