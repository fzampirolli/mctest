#!/bin/bash

. common_script.sh

. linker_script.sh

rm linker_script.sh

CURRENT_GRADE=0
SCALE=0

BUFFER_FILE=$( buffer_file_func )

touch $BUFFER_FILE

echo "<|--" >> $BUFFER_FILE
# echo "-Modelo: $THIS_STUDENT_VERSION" >> $BUFFER_FILE
echo >> $BUFFER_FILE
echo "--|>" >> $BUFFER_FILE
echo >> $BUFFER_FILE
echo >> $BUFFER_FILE

for i in $ALL_QUESTIONS ; do

	THIS_QUESTION_NUMBER=$(echo $i | cut -f1 -d$"|" )
	THIS_QUESTION_KEY=$(echo $i | cut -f2 -d$"|" )
	THIS_QUESTION_WEIGHT=$( question_weight_tag_func $THIS_QUESTION_KEY)
	THIS_QUESTION_FILE=$( question_file_tag_func $THIS_QUESTION_KEY)
	THIS_QUESTION_LANG=$( question_language_tag_func $THIS_QUESTION_KEY )
	# fz add
	THIS_QUESTION_SKILLS=$( question_skills_tag_func $THIS_QUESTION_KEY )
	THIS_QUESTION_DESCRIPTION=$( question_description_tag_func $THIS_QUESTION_KEY )
	THIS_QUESTION_DESCRIPTION_TEXT=$( question_description_text_tag_func $THIS_QUESTION_KEY )
	THIS_QUESTION_DESCRIPTION_FUNC=$( question_description_func_tag_func $THIS_QUESTION_KEY )
	# fz end
	THIS_QUESTION_OUTFILE="$( student_folder_func )/$( question_folder_func $THIS_QUESTION_KEY)/$( output_file_func $THIS_QUESTION_KEY )"
	THIS_QUESTION_EXECUTABLE="$( student_folder_func )/$( question_folder_func $THIS_QUESTION_KEY)/$( test_file_func $THIS_QUESTION_KEY )"
	THIS_QUESTION_CASES_FILE="$( student_folder_func )/$( question_folder_func $THIS_QUESTION_KEY)/$( cases_file_func $THIS_QUESTION_KEY )"
	THIS_QUESTION_CHOSEN_FILE=$( find $THIS_QUESTION_FILE.* 2> /dev/null )
	THIS_QUESTION_ERROR="$( student_folder_func )/$( question_folder_func $THIS_QUESTION_KEY)/$( error_file_func $THIS_QUESTION_KEY )"

    
    # echo $THIS_QUESTION
    # echo ">>>"
    # echo "  key:" $THIS_QUESTION_KEY
    # echo "  number:" $THIS_QUESTION_NUMBER
    # echo "  file:" $THIS_QUESTION_FILE
    # echo "  chosen file:" $THIS_QUESTION_CHOSEN_FILE
    # echo "  weight:" $THIS_QUESTION_WEIGHT
    # echo "  lang:" $THIS_QUESTION_LANG
    # echo "  skills:" $THIS_QUESTION_SKILLS
    # echo "  description:" $THIS_QUESTION_DESCRIPTION
    # echo "  description:" $THIS_QUESTION_DESCRIPTION_TEXT
    # echo "  description:" $THIS_QUESTION_DESCRIPTION_FUNC
    # echo "  executable:" $THIS_QUESTION_EXECUTABLE
    # echo "  executable:" $THIS_QUESTION_OUTFILE
    # echo ">>>>" $( student_folder_func )
    # echo "<<<"
    # echo
    # exit 0

	echo "<|--" >> $BUFFER_FILE
	echo "-Question $THIS_QUESTION_NUMBER:" >> $BUFFER_FILE
	echo >> $BUFFER_FILE

	if [ -z "$THIS_QUESTION_WEIGHT" ] ; then
		THIS_QUESTION_WEIGHT=1
	fi

	if [ -f $THIS_QUESTION_EXECUTABLE ] ; then

    	cp $THIS_QUESTION_EXECUTABLE vpl_test
		cp $THIS_QUESTION_CASES_FILE evaluate.cases

		./.vpl_tester >> $THIS_QUESTION_OUTFILE
    	sed -i "s/^Grade :=>>/PartialGrade :=>>/" $THIS_QUESTION_OUTFILE
    	
        if [ "${THIS_QUESTION_CHOSEN_FILE##*.}" = "txt" ]; then    ############### table test

            #echo "Grade :=>> 50" >> $THIS_QUESTION_OUTFILE  ############### NÃO ESTÁ PEGANDO A NOTA!!!!!!
            #cat $THIS_QUESTION_OUTFILE

            PARTIAL=$(cat $THIS_QUESTION_OUTFILE | grep -Eo 'Grade = +[[:digit:]]+([.][[:digit:]]+)?')
            #echo "-Nota: $PARTIAL" >> $BUFFER_FILE
            PARTIAL="${PARTIAL:8}"
        else
        	PARTIAL=$( awk '{ /^PartialGrade :=>> +[[:digit:]]+([.][[:digit:]]+)?$/ } END { print $NF }' $THIS_QUESTION_OUTFILE | grep -Eo '[[:digit:]]+([.][[:digit:]]+)?')
		fi

        #echo "-Nota: [$PARTIAL]" >> $BUFFER_FILE
        #cat $BUFFER_FILE
        #exit 0
        
	else
		PARTIAL=0
		echo ">Erro: Arquivo esperado não encontrado" >> $BUFFER_FILE
		sed -e 's/^/>/' $THIS_QUESTION_ERROR >> $BUFFER_FILE 2> /dev/null
	fi
    
	CURRENT_GRADE=$(awk 'BEGIN { printf "%.3f\n", '$CURRENT_GRADE'+('$PARTIAL'*'$THIS_QUESTION_WEIGHT') }')
	SCALE=$(awk 'BEGIN { printf "%.3f\n", '$SCALE'+'$THIS_QUESTION_WEIGHT' }')

	THIS_QUESTION_GRADE=$(awk 'BEGIN { printf "%.3f\n", ('$THIS_QUESTION_WEIGHT'*'$PARTIAL')/('$VPL_GRADEMAX$'-'$VPL_GRADEMIN')+'$VPL_GRADEMIN' }')
	THIS_QUESTION_AVAIL=$(awk 'BEGIN { printf "%.2f%%", ('$THIS_QUESTION_GRADE'/'$THIS_QUESTION_WEIGHT')*100 }' )

 	echo "Avaliação: $THIS_QUESTION_GRADE/$THIS_QUESTION_WEIGHT ($THIS_QUESTION_AVAIL)" >> $BUFFER_FILE
	echo >> $BUFFER_FILE
	# echo ">Key: $THIS_QUESTION_KEY" >> $BUFFER_FILE
	# echo ">Number: $THIS_QUESTION_NUMBER" >> $BUFFER_FILE
	echo ">Arquivo: $THIS_QUESTION_FILE" >> $BUFFER_FILE
	echo ">Escolhido: $THIS_QUESTION_CHOSEN_FILE" >> $BUFFER_FILE
	
	# fz add
	echo ">Habilidades: $THIS_QUESTION_SKILLS" >> $BUFFER_FILE
	if [ ! $(expr length "$THIS_QUESTION_DESCRIPTION") = 0 ] ; then
    	if [ ! $(expr length "$THIS_QUESTION_DESCRIPTION_TEXT") = 0 ] ; then
	        echo "-Descrição resumida da questão:" >> $BUFFER_FILE
	        echo "$THIS_QUESTION_DESCRIPTION_TEXT" >> $BUFFER_FILE
	    fi
    	if [ ! $(expr length "$THIS_QUESTION_DESCRIPTION_FUNC") = 0 ] ; then
	        echo "" >> $BUFFER_FILE
	        echo "-Método:" >> $BUFFER_FILE
	        echo "$THIS_QUESTION_DESCRIPTION_FUNC" >> $BUFFER_FILE
	    fi
	fi
	# fz end
	
	echo "" >> $BUFFER_FILE
	# echo ">Weight: $THIS_QUESTION_WEIGHT" >> $BUFFER_FILE
	# echo ">Partial: $THIS_QUESTION_GRADE" >> $BUFFER_FILE
	# echo ">Peso: $SCALE" >> $BUFFER_FILE
	echo "Avaliação: $THIS_QUESTION_AVAIL" >> $BUFFER_FILE
	echo "--|>" >> $BUFFER_FILE
	echo >> $BUFFER_FILE

    if [ -s $THIS_QUESTION_OUTFILE ] ; then
	    cat $THIS_QUESTION_OUTFILE >> $BUFFER_FILE 
	fi

	echo >> $BUFFER_FILE
	echo >> $BUFFER_FILE

done

FINAL=$(awk 'BEGIN { printf "%.3f\n", '$CURRENT_GRADE'/'$SCALE' }')
FINAL_SHONW=$(awk 'BEGIN { printf "%.2f\n", '$CURRENT_GRADE'/'$SCALE' }')

echo "<|--" >> $BUFFER_FILE
echo "-Nota: $FINAL_SHONW" >> $BUFFER_FILE
echo "--|>" >> $BUFFER_FILE

echo "Grade :=>> $FINAL" >> $BUFFER_FILE
cat $BUFFER_FILE
#echo 'Comment :=>>Encerrado'


# echo "<|--"
# echo
# echo
# ls -a1R | sed -e 's/^/>/'
# echo "--|>"
