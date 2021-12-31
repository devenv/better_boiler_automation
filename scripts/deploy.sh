#!/bin/sh

export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.
export DD_TRACE_ENABLED=False
export STATS_ENABLED=True

. venv/bin/activate

rm -rf boiler_clone
git clone git@github.com:devenv/better_boiler_automation.git boiler_clone

cd boiler_clone
new_last_commit=$(git log --format="%H" -n 1)
cd ../boiler
old_last_commit=$(git log --format="%H" -n 1)
cd ..
if [ "$new_last_commit" = "$old_last_commit" ]; then
  echo "skipping deployment, same commits: $new_last_commit == $old_last_commit"
  exit 0
fi
echo "new commit, deploying: $new_last_commit != $old_last_commit"

python -c "from boiler_clone.metrics import Metrics; Metrics().event('deploy', 'started', alert_type='info')"

rm -rf better_boiler_automation_configs
git clone git@github.com:devenv/better_boiler_automation_configs.git
rsync -avP --exclude=.git better_boiler_automation_configs/ boiler_clone/

cd boiler_clone

#pip3.7 install https://www.piwheels.org/simple/grpcio/grpcio-1.38.1-cp37-cp37m-linux_armv6l.whl

if ! cmp requirements.txt ../boiler/requirements.txt >/dev/null 2>&1; then
  echo "Installing requirements"
  pip3.7 install -r requirements.txt
  if [ $? -eq 0 ]; then
    echo 'requirements installed'
  else
    echo 'failed installing requirements'
    python -c "from boiler_clone.metrics import Metrics; Metrics().event('deploy', 'failed installing requirements', alert_type='error')"
    exit 2
  fi
fi

echo "Running tests"
export STATS_ENABLED=False
python3.7 -m unittest
if [ $? -eq 0 ]; then
  echo 'tests passed'
else
  echo 'tests failed'
  export STATS_ENABLED=True
  python -c "from boiler_clone.metrics import Metrics; Metrics().event('deploy', 'tests failed', alert_type='error')"
  return 1
fi
export STATS_ENABLED=True

cd ..

rm -rf boiler
cp -r boiler_clone boiler
cp boiler/scripts/deploy.sh ./
cp boiler/scripts/run.sh ./
cp boiler/scripts/calendar_sync.sh ./
python -c "from boiler.metrics import Metrics; Metrics().event('deploy', 'finished', alert_type='success')"