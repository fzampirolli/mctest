#!/bin/bash

# Defina o limite de uso de memória (em porcentagem)
LIMITE_MEMORIA=50
LOG_FILE="./_killDjango.txt"

# Verifique se há usuários logados no Django
USERS_NOW=$(python3 manage.py shell < _check_users.py)

echo $USERS_NOW
echo "--"
if [ "$USERS_NOW" -gt 0 ]
then
    echo "Há $USERS_NOW usuários logados no Django. Não matando processos Python3."
else
    echo "Nenhum usuário logado no Django. Verificando processos python3..."

    # Percorra todos os processos Python3
    for pid in $(pgrep python3)
    do
        # Obtenha o uso de memória do processo
        MEMORIA=$(ps -o %mem -p $pid | tail -n 1 | tr -d ' ')

        # Verifique se o uso de memória excede o limite
        if (( $(echo "$MEMORIA > $LIMITE_MEMORIA" | bc -l) ))
        then
            echo "Matando processo python3 com PID $pid que está usando $MEMORIA% de memória..."
            echo "$(date): Matando processo python3 com PID $pid que está usando $MEMORIA% de memória..." >> $LOG_FILE
            kill -9 $pid
        fi
    done
fi