#!/bin/bash

{

  send_event () {
    title=$1
    text=$2
    alert_type=$3
    echo "_e{${#title},${#text}}:$title|$text|#shell|t:$alert_type" | socat -t 0 - UDP:localhost:8125
  }

  export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.
  export DD_TRACE_ENABLED=False
  export STATS_ENABLED=True

  . venv/bin/activate

  rm -rf boiler_clone
  git clone git@github.com:devenv/better_boiler_automation.git boiler_clone
  cp boiler/scheduler/calendar_config.json boiler_clone/scheduler/

  cd boiler_clone
  new_last_commit=$(git log --format="%H" -n 1)
  cd ../boiler
  old_last_commit=$(git log --format="%H" -n 1)
  cd ..

  rm -rf better_boiler_automation_configs
  git clone git@github.com:devenv/better_boiler_automation_configs.git
  rsync -avP --exclude=.git better_boiler_automation_configs/ boiler_clone/


  if [ "$new_last_commit" = "$old_last_commit" ]; then
    echo "skipping deployment, same commits: $new_last_commit == $old_last_commit"
    send_event 'skipped' 'skipped' 'info'
    exit 0
  fi
  send_event 'deploy' 'started' 'info'

  cd boiler_clone

  #pip3.7 install https://www.piwheels.org/simple/grpcio/grpcio-1.38.1-cp37-cp37m-linux_armv6l.whl

  if ! cmp requirements.txt ../boiler/requirements.txt >/dev/null 2>&1; then
    echo "Installing requirements"
    pip3.7 install -r requirements.txt
    if [ $? -eq 0 ]; then
      echo 'requirements installed'
      send_event 'deploy' 'requirements installed' 'info'
    else
      echo 'failed installing requirements'
      send_event 'deploy' 'failed installing requirements' 'error'
      exit 2
    fi
  else
    send_event 'deploy' 'requirements skipped' 'info'
  fi

  echo "Running tests"
  export STATS_ENABLED=False
  python3.7 -m unittest
  if [ $? -eq 0 ]; then
    echo 'tests passed'
    send_event 'deploy' 'tests passed' 'info'
  else
    echo 'tests failed'
    export STATS_ENABLED=True
    send_event 'deploy' 'tests failed' 'error'
    return 1
  fi

  export STATS_ENABLED=True

  if ! cmp calculator/calculator_config.json ../boiler/calculator/calculator_config.json >/dev/null 2>&1; then
    send_event 'configuration change' 'calculator' 'info'
  fi

  cd ..

  rm -rf boiler
  cp -r boiler_clone boiler
  cp boiler/scripts/* ./

  send_event 'deploy' 'finished' 'success'

}