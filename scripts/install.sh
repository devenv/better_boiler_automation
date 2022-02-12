#!/bin/sh

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: sh install.sh PROMETHEUS_USERNAME PROMETHEUS_PASSWORD LOKI_USERNAME LOKI_PASSWORD"
    exit 1
fi
PROMETHEUS_USERNAME=$1
PROMETHEUS_PASSWORD=$2
LOKI_PASSWORD=$3
LOKI_PASSWORD=$4

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
sh replace_crontab.sh

echo "-- installing grafana --"
sudo cp boiler_clone/configs/grafana-agent.yaml /etc/
sudo sed -i /etc/grafana-agent.yaml "s/PROMETHEUS_USERNAME/$PROMETHEUS_USERNAME/g"
sudo sed -i /etc/grafana-agent.yaml "s/PROMETHEUS_PASSWORD/$PROMETHEUS_PASSWORD/g"
sudo sed -i /etc/grafana-agent.yaml "s/LOKI_USERNAME/$LOKI_USERNAME/g"
sudo sed -i /etc/grafana-agent.yaml "s/LOKI_PASSWORD/$LOKI_PASSWORD/g"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install -y grafana
sudo /bin/systemctl enable grafana-server
sudo /bin/systemctl start grafana-server