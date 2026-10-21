#!/bin/bash
#
# _killDjango.sh
# Roda via cron (como root) a cada hora. Mata processos python3 que estejam
# consumindo memória demais, mas SOMENTE se não houver usuários logados
# no Django no momento da checagem.
#
# CORREÇÕES nesta versão:
#   1. cd explícito para o diretório do projeto (cron não garante CWD).
#   2. Usa o python3 da virtualenv diretamente, sem depender de PATH/source.
#   3. Loga tudo (data, usuário, cwd, saída do check) para diagnóstico.
#   4. Tenta SIGTERM (kill -15) antes de SIGKILL (kill -9), dando chance
#      ao processo de terminar sem corromper PDFs em geração.
#   5. Se USERS_NOW não vier um número válido, aborta em vez de assumir 0.

set -u

PROJECT_DIR="/home/operador/PycharmProjects/mctest"
VENV_PY="/home/operador/PycharmProjects/AmbientePython3/bin/python3"
LOG_FILE="$PROJECT_DIR/_killDjango.txt"
LIMITE_MEMORIA=50

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

cd "$PROJECT_DIR" || { log "ERRO: não foi possível entrar em $PROJECT_DIR"; exit 1; }

log "---- início da checagem (whoami=$(whoami) cwd=$(pwd)) ----"

# Roda a checagem de usuários logados com a venv correta.
# stderr vai para o log, para não poluir/quebrar a captura de USERS_NOW.
USERS_NOW=$("$VENV_PY" manage.py shell < _check_users.py 2>>"$LOG_FILE")

log "USERS_NOW='$USERS_NOW'"

# Valida que USERS_NOW é um número. Se não for, algo deu errado
# (ambiente/venv/django quebrado) e é mais seguro NÃO matar nada.
if ! [[ "$USERS_NOW" =~ ^[0-9]+$ ]]; then
    log "ERRO: USERS_NOW não é um número válido. Abortando sem matar processos (fail-safe)."
    exit 1
fi

if [ "$USERS_NOW" -gt 0 ]; then
    log "Há $USERS_NOW usuário(s) logado(s) no Django. Não matando processos python3."
    exit 0
fi

log "Nenhum usuário logado no Django. Verificando processos python3..."

for pid in $(pgrep -x python3); do
    MEMORIA=$(ps -o %mem= -p "$pid" 2>/dev/null | tr -d ' ')
    [ -z "$MEMORIA" ] && continue

    if (( $(echo "$MEMORIA > $LIMITE_MEMORIA" | bc -l) )); then
        CMD=$(ps -o cmd= -p "$pid" 2>/dev/null)
        log "PID $pid usando ${MEMORIA}% de memória (cmd: $CMD). Enviando SIGTERM..."
        kill -15 "$pid" 2>/dev/null

        # Dá alguns segundos para o processo terminar graciosamente
        # (ex: finalizar escrita do PDF em andamento).
        for i in 1 2 3 4 5; do
            sleep 1
            kill -0 "$pid" 2>/dev/null || break
        done

        if kill -0 "$pid" 2>/dev/null; then
            log "PID $pid não terminou após SIGTERM. Forçando com SIGKILL..."
            kill -9 "$pid" 2>/dev/null
        else
            log "PID $pid terminou graciosamente após SIGTERM."
        fi
    fi
done

log "---- fim da checagem ----"