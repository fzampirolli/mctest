#!/bin/bash
cd /home/operador/PycharmProjects/
sudo apt update && sudo apt -y upgrade
source _settings.env
source AmbientePython3/bin/activate
cd mctest
source ../runDjango.sh &
