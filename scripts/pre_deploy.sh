#!/bin/bash

{

  export PYTHONPATH=/home/pi/venv/lib/python3.9/site-packages:.
  export DD_TRACE_ENABLED=False

  . venv/bin/activate

  rm -rf boiler_clone
  git clone git@github.com:devenv/better_boiler_automation.git boiler_clone >/dev/null 2>&1

  cd boiler_clone
  new_last_commit=$(git log --format="%H" -n 1)
  old_last_commit=""
  if [ -d "../boiler_ready" ]; then
    cd ../boiler_ready
    old_last_commit=$(git log --format="%H" -n 1)
  fi
  cd ..

  rm -rf better_boiler_automation_configs
  git clone git@github.com:devenv/better_boiler_automation_configs.git >/dev/null 2>&1

  if ! cmp ~/.boiler/secrets/calculator_config.json better_boiler_automation_configs/secrets/calculator_config.json >/dev/null 2>&1; then
    echo 'Calculator configuration change'
  fi

  mkdir boiler_clone/secrets -p
  rsync -avP --exclude=.git better_boiler_automation_configs/secrets/ boiler_clone/secrets/ >/dev/null 2>&1
  mkdir ~/.boiler/secrets -p
  mkdir ~/.boiler/data -p
  rsync -avP --exclude=.git better_boiler_automation_configs/secrets/ ~/.boiler/secrets/ >/dev/null 2>&1

  if [ "$new_last_commit" = "$old_last_commit" ]; then
    echo "Skipping deployment, same commits"
    exit 0
  fi
  echo 'Deploy started'

  cd boiler_clone

  #pip install https://www.piwheels.org/simple/grpcio/grpcio-1.38.1-cp37-cp37m-linux_armv6l.whl
 
  if ! cmp requirements.txt ../boiler_ready/requirements.txt >/dev/null 2>&1; then
    echo "Installing requirements"
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
      echo 'Requirements installed'
    else
      echo 'Failed installing requirements'
      exit 2
    fi
  else
    echo 'Skipping installing requirements'
  fi

  echo "Running tests"
  python -m unittest
  if [ $? -eq 0 ]; then
    echo 'Tests passed'
  else
    echo 'Tests failed'
    return 1
  fi

  cd ..

  rm -rf boiler_ready
  cp -r boiler_clone boiler_ready
  cp boiler_ready/scripts/* ./

  echo 'Deploy finished'

  exit

}