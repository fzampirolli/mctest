#!/bin/bash

# make
# base64 -d zip.tar.gz.b64 > zip.tar.gz && tar -zxf zip.tar.gz

. common_script.sh

# cat common_script.sh

. linker_script.sh

HASH_X=$( get_student_hash $MOODLE_USER_EMAIL )

HASH_T=$( date '+%s%N' )

HASH_E=$MOODLE_USER_EMAIL

# env > lixo
# cat lixo
# echo "$MOODLE_USER_EMAIL"
# echo "$HASH_X"
# exit 0

if [ -f $LINKER_FILE ] ; then

    #THIS_STUDENT_VERSION=$( get_studante_version "$MOODLE_USER_NAME" )
    # fz add
    THIS_STUDENT_VERSION=$( get_studante_version_email "$MOODLE_USER_EMAIL" )
    # fz end
    

    if [ -z "$THIS_STUDENT_VERSION" ] ; then
        VARIANTS=$( variant_counter_func $LINKER_FILE )
        THIS_STUDENT_VERSION=$(expr $HASH_X % $VARIANTS)
    fi

    if [ ! -z "$THIS_STUDENT_VERSION" ] ; then
        variant_select_func $THIS_STUDENT_VERSION
    fi
    
    rm $LINKER_FILE
else
	echo "echo 'comment :=>> Arquivo $LINKER_FILE não achado'" > vpl_execution
fi

mkdir $( student_folder_func )

if [ -f $VARIANT_FILE ] ; then

    variant_expansion_func question_file_func cases_file_func $GERENIC_KEY
    QUESTION_LIST=$( question_list_func )
    mv $VARIANT_FILE "$( student_folder_func )/$VARIANT_FILE"
    #echo $QUESTION_LIST
    #exit 0
fi

for THIS_QUESTION_KEY in $QUESTION_LIST ; do

    if [ -f $( question_file_func $THIS_QUESTION_KEY ) ] ; then

        mkdir "$(student_folder_func)/$( question_folder_func $THIS_QUESTION_KEY)"
        mv "./$( question_file_func $THIS_QUESTION_KEY )" "$(student_folder_func)/$( question_folder_func $THIS_QUESTION_KEY )/$( question_file_func $THIS_QUESTION_KEY )"
        mv "./$( cases_file_func $THIS_QUESTION_KEY )" "$(student_folder_func)/$( question_folder_func $THIS_QUESTION_KEY )/$( cases_file_func $THIS_QUESTION_KEY )"

        THIS_QUESTION_NUMBER=$( question_number_tag_func   $THIS_QUESTION_KEY )
        THIS_QUESTION_FILE=$(   question_file_tag_func     $THIS_QUESTION_KEY )
        THIS_QUESTION_WEIGHT=$( question_weight_tag_func   $THIS_QUESTION_KEY )
        THIS_QUESTION_LANG=$(   question_language_tag_func $THIS_QUESTION_KEY )
        THIS_QUESTION_EXECUTABLE="$( student_folder_func )/$( question_folder_func $THIS_QUESTION_KEY)/$( test_file_func $THIS_QUESTION_KEY )"
        THIS_QUESTION_ERROR="$( student_folder_func )/$( question_folder_func $THIS_QUESTION_KEY)/$( error_file_func $THIS_QUESTION_KEY )"

        THIS_QUESTION_CHOSEN_FILE=$( find $THIS_QUESTION_FILE.* 2> /dev/null )

        if [ ! -z $THIS_QUESTION_CHOSEN_FILE ] && [ -f $THIS_QUESTION_CHOSEN_FILE ] ; then
            # echo "found: '$THIS_QUESTION_CHOSEN_FILE'"
            ./vpl_run.sh $THIS_QUESTION_CHOSEN_FILE "$THIS_QUESTION_LANG" >> $THIS_QUESTION_ERROR 2>&2
            if [ -f vpl_execution ] ; then
                # echo "Creating:"$( test_file_func $THIS_QUESTION_KEY )
                mv vpl_execution $THIS_QUESTION_EXECUTABLE
            else
                echo
                echo "NOTIFICAÇÃO DE ERRO"
                echo "Questão: $THIS_QUESTION_NUMBER"
                cat $THIS_QUESTION_ERROR
                echo
            fi
        else
            echo "Arquivo para questão não encontrado." >> $THIS_QUESTION_ERROR
         	#echo "nope:$THIS_QUESTION_KEY"
        fi

        THIS_QUESTION="$THIS_QUESTION_NUMBER|$THIS_QUESTION_KEY"

        ALL_QUESTIONS="$ALL_QUESTIONS $THIS_QUESTION"

        #### Alguns filtros feitos pelo Paulo Pisani

        # Nome do arquivo atual (supondo que seja Q1.py, Q2.py, etc.)
        VPL_SUBFILE_VAR="VPL_SUBFILE$((THIS_QUESTION_NUMBER - 1))"
        
        # Obter o nome do arquivo correspondente
        filename=$(basename "${!VPL_SUBFILE_VAR}")
        
        # Extrair a extensão do arquivo
        FILE_EXT="${filename##*.}"
        
        # Construir o nome do arquivo auxiliar com a extensão correta
        VPL_SUBFILE_AUX=$(basename "$THIS_QUESTION_FILE.$FILE_EXT")
        export VPL_SUBFILE_AUX="$VPL_SUBFILE_AUX"

        # echo $THIS_QUESTION
        # echo ">>>"
        # echo "  key:"    $THIS_QUESTION_KEY
        # echo "  number:" $THIS_QUESTION_NUMBER
        # echo "  path: "  $(student_folder_func)/$( question_folder_func $THIS_QUESTION_KEY)
        # echo "  file:"   $THIS_QUESTION_FILE
        # echo "  exec:"   $THIS_QUESTION_EXECUTABLE
        # echo "  erro:"   $THIS_QUESTION_ERROR
        # echo "  weight:" $THIS_QUESTION_WEIGHT
        # echo "  lang:"   $THIS_QUESTION_LANG
        # echo "  ext:"    $FILE_EXT
        # echo "  aux:"    $VPL_SUBFILE_AUX
        # echo "<<<"
        # echo
        
        if [ "$FILE_EXT" = "py" ]; then

            if python3 verificar_arquivo.py "$VPL_SUBFILE_AUX" ; then
                echo "Erro ao verificar arquivo." >> vpl_compilation_error.txt
                echo "Erro ao verificar arquivo: $VPL_SUBFILE_AUX"
                exit 0
            fi
        fi
        
        ########## 
        # PARA UTILIZAR UMA LLMs NO AUXÍLIO AOS ALUNOS, USE  USE_LLM="true" na LINHA ABAIXO.
        # EM genIA.sh CRIE SUA PRÓPRIA `API_KEY` EM console.groq.com/keys, 
        # POIS A CHAVE ATUAL POSSUI LIMITE DE ACESSOS E CONSULTAS. 
        # CASO ALGUM PROFESSOR TENHA UMA MÁQUINA COM VÁRIAS GPUS DE ÚLTIMA GERAÇÃO DISPONÍVEL,
        # PODEMOS INSTALAR ESSA LLM LOCALMENTE PARA EVITAR LIMITAÇÕES DE ACESSO
                
        USE_LLM="false"
        
        # Verifica se o uso da LLM está ativado
        if [ "${USE_LLM}" = "true" ]; then
        
            echo "🚨 ATENÇÃO: Sugestões geradas por IA via arquivo ▶ \"$VPL_SUBFILE_AUX\". Revise com cuidado!"
            
            # Chama o script encapsulado
            bash genAI.sh
        
        fi

    else
        echo "Arquivo $( question_file_func $THIS_QUESTION_KEY ) não achado"
    fi

done

if [ "${USE_LLM}" = "true" ]; then
    echo "⚠️ Para visualizar detalhes dos casos de teste, acesse as abas 'Comentários' e 'Execução'." 
    echo -e ""
fi

ALL_QUESTIONS=$( echo $ALL_QUESTIONS | xargs -n1 | sort | xargs )

echo 'ALL_QUESTIONS="'$ALL_QUESTIONS'"' >> linker_script.sh
echo 'THIS_STUDENT_VERSION="'$THIS_STUDENT_VERSION'"' >> linker_script.sh
echo 'HASH_X="'$HASH_X'"' >> linker_script.sh
echo 'HASH_T="'$HASH_T'"' >> linker_script.sh


if [ "$SECONDS" = "" ] ; then
	export SECONDS=20
fi
if [ "$VPL_GRADEMIN" = "" ] ; then
	export VPL_GRADEMIN=0
	export VPL_GRADEMAX=10
fi

mv vpl_evaluate2019.cpp vpl_evaluate.cpp
#cat vpl_evaluate.cpp
#exit 0

mv vpl_evaluate.cpp vpl_evaluate.cpp.origin

#Add constants to vpl_evaluate2012.cpp
echo "const float VPL_GRADEMIN=$VPL_GRADEMIN;" >vpl_evaluate.cpp
echo "const float VPL_GRADEMAX=$VPL_GRADEMAX;" >>vpl_evaluate.cpp
let VPL_MAXTIME=VPL_MAXTIME-$SECONDS-1;
echo "const int VPL_MAXTIME=$VPL_MAXTIME;" >>vpl_evaluate.cpp
cat vpl_evaluate.cpp.origin >> vpl_evaluate.cpp

check_program g++
g++ vpl_evaluate.cpp -g -lm -lutil -o .vpl_tester

# mv vpl_execution.sh vpl_execution

# o problema está nessa linha
# echo "./.vpl_tester | tee vpl_tester_out" >> vpl_execution
echo "./vpl_execution.sh | tee vpl_tester_out" >> vpl_execution

#"$(cat "$user_filename")"

chmod +x vpl_execution

# exit 0 ## Descomente esta linha para ignorar o Feedback por IA !
cat >> vpl_execution <<'EOF'

    GROQ_KEY="xxx"  # Obtain your key from https://console.groq.com/keys
    AI_REMOVE_COMMENTS=0
    AI_MIN_CHARS=5
    AI_MAX_CHARS=2000
    AI_DEBUG=0

    ai_models=(
        "gemma2-9b-it"
        "llama-3.3-70b-versatile"
        "llama-3.1-8b-instant"
        "llama3-8b-8192"
        "llama3-70b-8192"
        "meta-llama/llama-4-maverick-17b-128e-instruct"
        "meta-llama/llama-4-scout-17b-16e-instruct"
    )


    _ai_log=""
    ai_log() {
        _ai_log+="${1}\n"
    }

    ai_query() {

        local question="$1 ${AI_RULES}"
        #local code_content="$2"
        local code_content="Analise cada arquivo separadamente e de forma independente. Inclua o nome do arquivo no início, por exemplo: Q1.py"$'\n'"$2"

        call_api_groq() {
            local api_url="$1"
            local api_key="$2"
            local question="$3"
            local code_content="$4"
            local api_model="$5"

            response=$(curl -s --fail -X POST "$api_url" \
                -H "Authorization: Bearer $api_key" \
                -H "Content-Type: application/json" \
                -d "$(jq -n \
                    --arg user "$code_content" \
                    '{
                        "messages": [
                            {"role": "system", "content": "'"$question"'"},
                            {"role": "user", "content": $user}
                        ],
                        "model": "'"$api_model"'",
                        "temperature": 0.7
                    }')")
            
            echo "$response"
        }
        
        available_models=("${ai_models[@]}")
        for ((i = 0; i < ${#ai_models[@]}; i++)); do
            index=$((RANDOM % ${#available_models[@]})) # Pick a random AI model
            API_MODEL="${available_models[index]}"
            unset 'available_models[index]' # Remove from list (no call it again)
            available_models=("${available_models[@]}") # Reorganize list without current model

            GROQ_URL="https://api.groq.com/openai/v1/chat/completions"
            response=$(call_api_groq "$GROQ_URL" "$GROQ_KEY" "$question" "$code_content" "$API_MODEL")

            if [[ -n "$response" ]]; then
            
                response=$(echo "$response" | tr -d '\000-\031') # Remove control characteres and extract content
                response=$(echo "$response" | jq -r '.choices[0].message.content')
                response=$(echo "$response" | sed 's/^\(\s*\)-/\1*/g') # Items starting with '-' has special formatting in VPL output.
                # response=$(echo "$response" | sed 's/^/>/') # Insert '>' as prefix...

                num_char=$(echo -n "$response" | wc -m)

                if (( num_char >= $AI_MIN_CHARS && num_char <= $AI_MAX_CHARS )); then
                    content=$(printf "=== INÍCIO [🤖 modelo: $API_MODEL] ===\n\n ")

                    content+="$response"
                    
                    # Remove trechos de código entre as marcações de bloco de código (```)
                    content=$(echo "$content" | sed -E '/```/,/```/d')
    
                    content+=$(printf "\n\n=== FIM [⏰  $(date "+%Y-%m-%d %H:%M:%S")] ===")
    
                    echo "$content"
                    break
                else
                    ai_log "Resposta do modelo: $API_MODEL gerou $num_char caracteresmas deve ser entre $AI_MIN_CHARS e $AI_MAX_CHARS caracteres. Tentando próximo modelo..."
                fi
            else
                ai_log "Resposta nula do modelo: $API_MODEL. Tentando próximo modelo..."
            fi
        done
    }

    code_contents=""
    code_contents+=$(printf "# === Arquivos submetidos concatenados automaticamente pelo VPL.\n ")
    code_contents+=$(printf "# === Blocos entre '# === INÍCIO ...' e '# === FIM ...' representam arquivos separados.\n ")
    code_contents+=$(printf "# === Desconsiderar das análises todos os comentários.\n ")
    for user_filename in $VPL_SUBFILES; do

    AI_RULES="Analise o(s) código(s) escrito(s) por um aluno iniciante. \
Esta análise é usada em um sistema automático de verificação de saídas. \
Não explique, nem interprete a lógica ou o objetivo do código. Não há enunciado disponível. \
Não sugira trechos de código, estruturas, funções (como min, max, sum, sort, append, join, map etc.), \
testes ou melhorias. Ignore blocos try/except, bibliotecas, dicionários e comentários. \
Se houver erros evidentes, aponte-os com número da linha e motivo. \
Use apenas texto puro (não em Markdown, html, etc), em português do Brasil, com no máximo 500 caracteres no total \
e 80 caracteres por linha."

        code_contents+=$(printf "\n# === INÍCIO '${user_filename}' ===\n ")

        if [ $AI_REMOVE_COMMENTS -eq 0 ]; then
            # code_contents+=$(cat $user_filename)  # remove a identação?
            #code_contents+="$(cat "$user_filename")"
            #code_contents+=$(awk '{print}' "$user_filename")
            code_contents+=$(<"$user_filename")
            
        else
            code_contents+=$(cat $user_filename | 
                sed -r 's/\s*#.*$//g' |     # Remove comentários no final de cada linha
                sed -E "/'''/,/'''/d" |     # Remove blocos entre '''...'''
                sed -E '/"""/,/"""/d' |     # Remove blocos entre """..."""
                sed -r '/^\s*$/d')          # Remove linhas em branco
        fi
        code_contents+=$(printf "\n# === FIM '${user_filename}' ===\n ")
    done
    
    echo "<|--"

    if [ ! -f "vpl_tester_out" ]; then
        echo "-!!! ERRO em 'vpl_evaluate.sh' !!!"
        echo "O arquivo 'vpl_tester_out' nao foi gerado."
        echo "Localize e altere a seguinte linha em 'vpl_evaluate.sh':"
        echo ""
        echo "echo \"./.vpl_tester | tee vpl_tester_out\" >> vpl_execution"
        exit 1
    fi


    echo -e "\n-🚀 Feedback automático gerado por IA ⚠️ Revise com cuidado, pode conter erros!\n"

    GRADE=$(grep -oP "^Grade :=>>\s*\K\d+(\.\d+)?(?=\s|$)" vpl_tester_out)
    if [ -z "$GRADE" ]; then
        GRADE='0'
    fi

    if grep -qE "Traceback|SyntaxError|IndentationError" vpl_tester_out; then
        echo -e "🚫 Erro detectado: problema de compilação (sintaxe) ou execução (lógica)!\n"
        echo -e "🔍 Abaixo, uma sugestão de correção com base na análise do erro:\n"
        ERR=$(sed -n '/--- Program output ---/,/--- Expected output/p' vpl_tester_out | sed '/--- Expected output/q')
        ai_query "Interprete o erro e sugira como corrigi-lo." "$ERR"
    
    elif awk "BEGIN {exit !($GRADE <= $VPL_GRADEMIN)}"; then
        echo -e "💪 Vamos lá, você consegue!\n"
        echo -e "🛠️ Algumas sugestões para te ajudar a melhorar:\n"
        ai_query "Verifique se o código faz sentido. Tente identificar trechos estranhos e oriente como corrigi-los." "$code_contents"
    
    elif awk "BEGIN {exit !($GRADE >= $VPL_GRADEMAX)}"; then
        echo -e "🎉 Parabéns, você gabaritou!\n"
        echo -e "📊 Aqui vai uma análise do(s) seu(s) código(s):\n"
        ai_query "Avalie o código e sugira melhorias. Você pode apresentar pequenas versões refatoradas (mesmo que isso contrarie as regras abaixo)." "$code_contents"
    
    else
        echo -e "✨ Vocé está quase lá!\n"
        echo -e "🧭 Confira as dicas a seguir para ajustar seu(s) código(s):\n"
        ai_query "Tente identificar trechos confusos ou sem sentido. Dê orientações de como corrigi-los." "$code_contents"
    fi




    # Debug...
    if [ $AI_DEBUG -ne 0 ]; then
        echo "-Var"
        for var in $(compgen -v); do
            if [[ $var == AI_* ]]; then
                echo "\$$var=${!var//$'\n'/\\n}"
            fi
        done
        echo "\$GRADE = $GRADE"

        echo "- Log"
        if [ -n "$_ai_log" ]; then
            printf "$_ai_log"
        else
            echo "<Sem log>"
        fi

        echo "-Export"
        export
        
        echo "-User code"
        echo "$code_contents"

        echo "-arquivo vpl_execution"
        cat -n vpl_execution

        echo "-arquivo vpl_tester (original)"
        cat -n vpl_tester_out
    fi

    echo "--|>"
EOF
