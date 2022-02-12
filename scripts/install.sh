#!/bin/sh

set -e

if [ "$#" -ne 6 ]; then
      echo "Usage: sh install.sh GCLOUD_ID GCLOUD_KEY PROMETHEUS_USERNAME PROMETHEUS_PASSWORD LOKI_USERNAME LOKI_PASSWORD"
      exit 1
fi
GCLOUD_ID=$1
GCLOUD_KEY=$2
PROMETHEUS_USERNAME=$3
PROMETHEUS_PASSWORD=$4
LOKI_USERNAME=$5
LOKI_PASSWORD=$6

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

echo "-- installing grafana --"
sudo ARCH=armv6 GCLOUD_STACK_ID="$GCLOUD_ID" GCLOUD_API_KEY="GCLOUD_KEY" GCLOUD_API_URL="https://integrations-api-eu-west.grafana.net" /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/grafana/agent/release/production/grafanacloud-install.sh)"

echo "-- grafana config --"
sudo cp boiler_clone/configs/grafana-agent.yaml /etc/
sudo sed -i "s/PROMETHEUS_USERNAME/$PROMETHEUS_USERNAME/g" /etc/grafana-agent.yaml
sudo sed -i "s/PROMETHEUS_PASSWORD/$PROMETHEUS_PASSWORD/g" /etc/grafana-agent.yaml
sudo sed -i "s/LOKI_USERNAME/$LOKI_USERNAME/g" /etc/grafana-agent.yaml
sudo sed -i "s/LOKI_PASSWORD/$LOKI_PASSWORD/g" /etc/grafana-agent.yaml

echo "-- grafana restart --"
sudo systemctl restart grafana-agent.service

echo "-- replacing crontab --"
sh replace_crontab.sh