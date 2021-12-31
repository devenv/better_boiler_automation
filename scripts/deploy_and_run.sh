#!/bin/sh

echo Deploying...
sh deploy.sh
echo Syncing calendar...
sh calendar_sync.sh
echo Running scheduler
sh run.sh