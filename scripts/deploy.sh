#!/bin/bash

{

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

  rm -rf better_boiler_automation_configs
  git clone git@github.com:devenv/better_boiler_automation_configs.git
  rsync -avP --exclude=.git better_boiler_automation_configs/ boiler_clone/

  cd boiler_clone
  python -c "from metrics import Metrics; Metrics().event('deploy', 'started', alert_type='info')"
  cd ..

  if [ "$new_last_commit" = "$old_last_commit" ]; then
    echo "skipping deployment, same commits: $new_last_commit == $old_last_commit"
    python -c "from metrics import Metrics; Metrics().event('deploy', 'skipped', alert_type='info')"
    exit 0
  fi

  cd boiler_clone

  #pip3.7 install https://www.piwheels.org/simple/grpcio/grpcio-1.38.1-cp37-cp37m-linux_armv6l.whl

  if ! cmp requirements.txt ../boiler/requirements.txt >/dev/null 2>&1; then
    echo "Installing requirements"
    pip3.7 install -r requirements.txt
    if [ $? -eq 0 ]; then
      echo 'requirements installed'
      python -c "from metrics import Metrics; Metrics().event('deploy', 'requirements installed', alert_type='info')"
    else
      echo 'failed installing requirements'
      python -c "from metrics import Metrics; Metrics().event('deploy', 'failed installing requirements', alert_type='error')"
      exit 2
    fi
  else
    python -c "from metrics import Metrics; Metrics().event('deploy', 'requirements skipped', alert_type='info')"
  fi

  echo "Running tests"
  export STATS_ENABLED=False
  python3.7 -m unittest
  if [ $? -eq 0 ]; then
    echo 'tests passed'
    python -c "from metrics import Metrics; Metrics().event('deploy', 'tests passed', alert_type='info')"
  else
    echo 'tests failed'
    export STATS_ENABLED=True
    python -c "from metrics import Metrics; Metrics().event('deploy', 'tests failed', alert_type='error')"
    return 1
  fi

  export STATS_ENABLED=True

  if ! cmp calculator/calculator_config.json ../boiler/calculator/calculator_config.json >/dev/null 2>&1; then
    python -c "from metrics import Metrics; Metrics().event('configuration change', 'calculator', alert_type='info')"
  fi

  cd ..

  rm -rf boiler
  cp -r boiler_clone boiler
  cp boiler/scripts/* ./

  cd boiler
  python -c "from metrics import Metrics; Metrics().event('deploy', 'finished', alert_type='success')"
  cd ..

}