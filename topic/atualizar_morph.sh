#!/bin/bash

# Configurações de diretório e URL
URL="https://raw.githubusercontent.com/fzampirolli/pdi-vc/master/morph/morph.py"
DESTINO="/home/operador/PycharmProjects/mctest/topic/morph.py"
STRIP_SCRIPT="/home/operador/PycharmProjects/mctest/topic/strip_show_methods.py"
LOG="$HOME/morph_update.log"

# Garante que a pasta de destino exista
mkdir -p "$(dirname "$DESTINO")"

# Baixa o arquivo sobrescrevendo a versão antiga (-o)
curl -sSL "$URL" -o "$DESTINO"

if [ $? -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERRO ao baixar morph.py." >> "$LOG"
    exit 1
fi

# Remove os métodos show*/ desnecessários no mctest (e evitam SyntaxError
# em Python < 3.11 por causa de sintaxe tipo axes[*divmod(...)])
python3 "$STRIP_SCRIPT" "$DESTINO" >> "$LOG" 2>&1

# Valida que o arquivo resultante compila na versão local do Python
python3 -c "import ast; ast.parse(open('$DESTINO').read())" 2>> "$LOG"
if [ $? -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ATENÇÃO: morph.py ainda não compila após limpeza! Verifique manualmente." >> "$LOG"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] morph.py atualizado e validado com sucesso." >> "$LOG"