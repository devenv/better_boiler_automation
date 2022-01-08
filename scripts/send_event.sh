#!/bin/bash

title=$1
text=$2
alert_type=$3

echo "_e{${#title},${#text}}:$title|$text|#shell|t:$alert_type" | socat -t 0 - UDP:localhost:8125