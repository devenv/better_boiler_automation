#!/bin/sh

. venv/bin/activate

cd boiler_ready

export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.

old_cron=$(crontab -l)
schedule=$(python -m runners.generate_cron)
if [ -z "$schedule" ]; then
    echo "Wrong crontab: $schedule"
    exit 1
fi

if ! echo "$schedule" | crontab -; then
    echo "Couldn't set cron, reverting: $schedule"
    echo "$old_cron" | crontab -
fi 