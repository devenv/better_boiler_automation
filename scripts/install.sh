#!/bin/sh

set -e

cd

echo "-- creating venv --"
rm -rf venv
python3 -m venv venv

echo "-- cloning repo --"
rm -rf boiler_clone
git clone git@github.com:devenv/better_boiler_automation.git boiler_clone

echo "-- copying scripts --"
cp boiler_clone/scripts/* ./

echo "-- running deploy --"
sh pre_deploy.sh

echo "-- replacing crontab --"
sh replacep_crontab.sh

echo "-- installing grafana --"
sudo boiler_clone/config/grafana-agent.yaml /etc/
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install -y grafana
sudo /bin/systemctl enable grafana-server
sudo /bin/systemctl start grafana-server