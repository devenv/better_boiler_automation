#!/bin/bash

{

  export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.
  export DD_TRACE_ENABLED=False

  . venv/bin/activate

  rm -rf boiler_clone
  git clone git@github.com:devenv/better_boiler_automation.git boiler_clone

  cd boiler_clone
  new_last_commit=$(git log --format="%H" -n 1)
  cd ../boiler_ready
  old_last_commit=$(git log --format="%H" -n 1)
  cd ..

  rm -rf better_boiler_automation_configs
  git clone git@github.com:devenv/better_boiler_automation_configs.git
  mkdir boiler_clone/secrets -p
  rsync -avP --exclude=.git better_boiler_automation_configs/secrets/ boiler_clone/secrets/
  mkdir ~/.boiler_ready/secrets -p
  rsync -avP --exclude=.git better_boiler_automation_configs/secrets/ ~/.boiler_ready/secrets/

  if [ "$new_last_commit" = "$old_last_commit" ]; then
    echo "skipping deployment, same commits: $new_last_commit == $old_last_commit"
    exit 0
  fi
  echo 'Deploy started'

  cd boiler_clone

  #pip3.7 install https://www.piwheels.org/simple/grpcio/grpcio-1.38.1-cp37-cp37m-linux_armv6l.whl
 
  if ! cmp requirements.txt ../boiler_ready/requirements.txt >/dev/null 2>&1; then
    echo "Installing requirements"
    pip3.7 install -r requirements.txt
    if [ $? -eq 0 ]; then
      echo 'Requirements installed'
    else
      echo 'Failed installing requirements'
      exit 2
    fi
  else
    echo 'Requirements skipped'
  fi

  echo "Running tests"
  python3.7 -m unittest
  if [ $? -eq 0 ]; then
    echo 'Tests passed'
  else
    echo 'tests failed'
    return 1
  fi

  if ! cmp calculator/calculator_config.json ../boiler_ready/calculator/calculator_config.json >/dev/null 2>&1; then
    echo 'Calculator configuration change'
  fi

  cd ..

  rm -rf boiler_ready
  cp -r boiler_clone boiler_ready
  cp boiler_ready/scripts/* ./

  echo 'Deploy finished'

}