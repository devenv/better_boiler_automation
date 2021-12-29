#!/bin/sh

set -e

rm -rf boiler_clone
git clone git@github.com:devenv/better_boiler_automation.git boiler_clone

rm -rf better_boiler_automation_configs
git clone git@github.com:devenv/better_boiler_automation_configs.git
rsync -avP better_boiler_automation_configs/ boiler_clone/

. venv/bin/activate
cd boiler_clone

#pip3.7 install https://www.piwheels.org/simple/grpcio/grpcio-1.38.1-cp37-cp37m-linux_armv6l.whl

echo Installing requirements
pip3.7 install -r requirements.txt
if [ $? -eq 0 ]; then
  echo 'requirements installed'
else
  echo 'failed installing requirements'
  exit 2
fi

export PYTHONPATH=/home/pi/venv/lib/python3.7/site-packages:.

echo Running tests
python3.7 -m unittest
if [ $? -eq 0 ]; then
  echo 'tests passed'
else
  echo 'tests failed'
  return 1
fi

cd ..

rm -rf boiler
cp -r boiler_clone boiler