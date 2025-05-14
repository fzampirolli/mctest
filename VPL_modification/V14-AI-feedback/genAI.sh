#!/bin/bash
 
# para executar localmente, (des)comente as 2 linhas abaixo
# e criar um arquivo test.py com código python
# FILE_EXT="py"  # adicionado o valor de $FILE_EXT
cp $VPL_SUBFILE_AUX test.py

> genAI.txt  # Apaga o conteúdo de genAI.txt, se ele existir

# ALTERAR ESSE PROMPT CONFORME AS NECESSIDADES DA SUA TURMA
pergunta="Analise o código '$FILE_EXT', feito por um aluno iniciante. A \
análise integra um sistema automático que compara a saída do programa com \
textos esperados. Não explique a finalidade do código. Não sugira validações \
de variáveis. Não recomende trechos de código, testes, blocos try/except, \
comentários, mensagens ou funções prontas (min, max, sort, append, join, map, etc.). \
Se houver erros muito evidentes, destaque-os sem mencionar o número da linha \
e forneça sugestões numeradas de correção, em português (Brasil), concisas \
(máx. 500 caracteres e até 80 caracteres por linha)."



# GROQ
API_KEY="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" ##########  CRIE SUA PRÓPRIA `API_KEY` 
API_URL="https://api.groq.com/openai/v1/chat/completions"
# ver console.groq.com/docs/rate-limits

# Lista de modelos a serem tentados
modelos=(
    ## "llama-3.1-8b-instant" # ruim
    # #"llama-3.3-70b-specdec" #não existe mais
    # #"mixtral-8x7b-32768" #não existe mais
    "gemma2-9b-it"
    "llama3-8b-8192"
    # melhores:
    "llama3-70b-8192"
    "llama-3.3-70b-versatile"
    "meta-llama/llama-4-maverick-17b-128e-instruct"
    "meta-llama/llama-4-scout-17b-16e-instruct"
)

chamar_api_groq() {
    local api_url="$1"
    local api_key="$2"
    local pergunta="$3"
    local code_content="$4"
    local api_model="$5"

    # Enviar requisição para a API da Groq
    response=$(curl -s --fail -X POST "$api_url" \
        -H "Authorization: Bearer $api_key" \
        -H "Content-Type: application/json" \
        -d "$(jq -n \
            --arg user "$code_content" \
            '{
                "messages": [
                    {"role": "system", "content": "'"$pergunta"'"},
                    {"role": "user", "content": $user}
                ],
                "model": "'"$api_model"'",
                "temperature": 0.7
            }')")
    
    echo "$response"
}

limpar_resposta() {
    local content="$1"  # Recebe o conteúdo original como argumento

    # Lista de palavras-chave que indicam onde cortar o texto
    palavras_chave=(
        "[0-9]*. Dica"  # Generaliza qualquer número antes de "Dica"
        "Revisado"
        "Aqui"
        " Aqui"
        "Exemplo"
        "Código"
        "Sugestões"
        "Let me know"
        "Here"
    )

    # Construção dinâmica do comando sed
    sed_pattern=$(printf '/^%s.*/,$d;' "${palavras_chave[@]}")

    # Aplicação das transformações em um único pipeline após a 3a linha
    #echo "$content" | sed -E "$sed_pattern" | sed -E '/^$/d' | sed -E '/```/,/```/d'

    # Assume que 'content' contém o texto original

    # Armazena as duas primeiras linhas
    primeiras_linhas=$(echo "$content" | sed -E '1,2!d')

    # Armazena o restante do conteúdo (após as duas primeiras linhas)
    restante=$(echo "$content" | sed -E '1,2d')

    # Aplica o padrão sed ao restante do conteúdo
    restante=$(echo "$restante" | sed -E "$sed_pattern" | sed -E '/^$/d')

    # Remove trechos de código entre as marcações de bloco de código (```)
    restante=$(echo "$restante" | sed -E '/```/,/```/d')

    # Remove a linha com "seguintes linhas no código:" e todas as linhas após ela
    restante=$(echo "$restante" | sed -E '/seguintes linhas no código:/,$d; /seguintes linhas no código:/d')

    # Combina as duas primeiras linhas com o restante do conteúdo
    content_final="$primeiras_linhas"$'\n'"$restante"

    # Exibe o conteúdo resultante
    echo "$content_final"
}

code_content=$(cat test.py | 
    sed -r 's/\s*#.*$//g' |     # Remove comentários no final de cada linha
    sed -E "/'''/,/'''/d" |     # Remove blocos entre '''...'''
    sed -E '/"""/,/"""/d' |     # Remove blocos entre """..."""
    sed -r '/^\s*$/d')          # Remove linhas em branco

# Conta o número de linhas na string
num_linhas=$(echo "$code_content" | wc -l)
max_linhas=10
content=""
# Verifica se o número de linhas é menor que 10
if (( num_linhas < $max_linhas )); then
    # echo -e "Código: \n$code_content"
    #echo -e "\n=================================\n" >> genAI.txt
    printf "Seu código, sem comentários e linhas em branco, tem %d linhas.\nO limite mínimo de linhas para a consulta na IA é %d linhas. \nAbortou consulta!\n" "$num_linhas" "$max_linhas" >> genAI.txt

else
    #echo -e "Sugestões geradas automaticamente usando ${#modelos[@]} modelos de groq.com. Esse recurso é experimental e pode cometer erros.\n" >> genAI.txt

    #echo -e "Pergunta (no final tem o seu código se >=10 linhas, removendo comentários e linhas em branco): $pergunta" | fold -s -w 132 >> genAI.txt

    # Variável para armazenar a resposta
    response=""

    # Criar uma cópia da lista de modelos
    modelos_disponiveis=("${modelos[@]}")

    # Iterar sobre os modelos sem repetir
    for ((i = 0; i < ${#modelos[@]}; i++)); do
        # Escolher um índice aleatório dentro dos modelos disponíveis
        index=$((RANDOM % ${#modelos_disponiveis[@]}))
        API_MODEL="${modelos_disponiveis[index]}"

        # Remover o modelo escolhido da lista
        unset 'modelos_disponiveis[index]'
        
        # Reorganizar a lista para remover espaços vazios
        modelos_disponiveis=("${modelos_disponiveis[@]}")

        #echo -e "\n#################################"
        #echo -e "\nTentando um modelo aleatório de ${#modelos[@]} possíveis: $API_MODEL" >> genAI.txt

        # Enviar requisição para a API da Groq
        response=$(chamar_api_groq "$API_URL" "$API_KEY" "$pergunta" "$code_content" "$API_MODEL")

        # Verificar se a resposta é válida
        if [[ -n "$response" ]]; then

            content=$(echo "$response" | jq -r '.choices[0].message.content')
            #echo "<<<<<<<<$content>>>>>>>>"

            # Extrair o conteúdo da resposta, removendo trechos de código e todas linhas após "Exemplo:", "Exemplos:", etc
            content=$(limpar_resposta "$content")

            # Contar o número de caracteres na resposta
            num_caracteres=$(echo -n "$content" | wc -m)
            #echo "<<<<$num_caracteres caracteres>>>>"

            # Correção da lógica da condição
            if (( num_caracteres >= 0 && num_caracteres <= 10000 )); then
                # Log de execução
                timestamp=$(date "+%Y-%m-%d %H:%M:%S")

                echo -e "================================= 📌 Modelo: $API_MODEL" >> genAI.txt
                break  # Sai do loop se uma resposta válida for obtida
            #else
                #echo "Resposta do modelo: $API_MODEL não gerou resposta entre 500 e 2000 caracteres. Tentando próximo modelo..." >> genAI.txt
            fi

        #else
            #echo "Resposta nula do modelo: $API_MODEL. Tentando próximo modelo..." >> genAI.txt
        fi

    done

    # Remover caracteres de controle antes de processar com jq
    clean_response=$(echo "$response" | tr -d '\000-\031')
    
    content=$(echo "$clean_response" | jq -r '.choices[0].message.content')
    content=$(echo "$clean_response" | jq -r '.choices[0].message.content' | sed '/Exemplos:/,$d')

    # Extrair o conteúdo da resposta, removendo trechos de código e todas linhas após "Exemplo:", "Exemplos:", etc
    content=$(limpar_resposta "$content")

    # Salvar cada sugestão em uma linha separada no arquivo genAI.txt
    content=$(echo "$content" | sed 's/\*\*//g')
    #echo "$content" >> genAI.txt
    echo "$content" | fold -s -w 100 >> genAI.txt

fi 

if [[ -z "$content" && num_linhas -ge $max_linhas ]]; then
    echo -e "Ultrapassou o limite de perguntas nos modelos de IA. Tente mais tarde.\n" >> genAI.txt
fi

echo -e "================================= 🕒 [$timestamp]\n" >> genAI.txt

cat genAI.txt	    