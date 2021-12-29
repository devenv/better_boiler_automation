#!/bin/sh

set -e

cd boiler
. venv/bin/activate

export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.
python3.7 -m run.py
