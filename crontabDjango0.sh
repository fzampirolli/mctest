#!/bin/bash

# Verificar se o processo Python3 está em execução
if pgrep -x "python3" > /dev/null; then
    echo "O processo Python3 está em execução. Não iniciando um novo processo."
else
    echo "O processo Python3 não está em execução. Iniciando um novo processo."

    . /home/operador/PycharmProjects/crontabDjango.sh
fi
