#!/bin/bash

# Verificar se o processo Python3 está em execução
if pgrep -x "python3" > /dev/null; then
    echo "O processo Python3 está em execução. Não iniciando um novo processo."
else
    echo "O processo Python3 não está em execução. Iniciando um novo processo."
    . /home/operador/PycharmProjects/crontabDjango.sh
fi

# Verificar se a API Go está rodando na porta 8080
if sudo lsof -i :8080 | grep LISTEN > /dev/null; then
    echo "A API Go já está em execução na porta 8080."
else
    echo "A API Go não está em execução. Iniciando a API Go na porta 8080."

    # Salvar o diretório atual
    CURRENT_DIR=$(pwd)

    # Navegar para o diretório do mctest-validator-api
    cd /home/operador/PycharmProjects/mctest/mctest-validator-api || exit

    # Executar o main.go e redirecionar a saída para logfile.txt
    go run main.go > logfile.txt 2>&1 &

    # Voltar ao diretório original
    cd "$CURRENT_DIR"
fi
