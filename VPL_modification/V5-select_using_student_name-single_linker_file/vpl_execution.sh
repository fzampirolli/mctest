#!/bin/bash

. common_script.sh

. linker_script.sh

CURRENT_GRADE=0
SCALE=0

echo $ALL_QUESTIONS

for i in $ALL_QUESTIONS ; do

	THIS_QUEST_NUMBER=$(echo $i | cut -f1 -d$"|" )
	THIS_QUEST_KEY=$(echo $i | cut -f2 -d$"|" )
	THIS_QUEST_WEIGHT=$( quest_weight_tag_func $THIS_QUEST_KEY)
	THIS_QUEST_OUTFILE=$( output_file_func $THIS_QUEST_KEY )
	THIS_QUEST_FILE=$( quest_file_tag_func $THIS_QUEST_KEY)
	THIS_QUEST_MODEL=$( quest_model_tag_func $THIS_QUEST_KEY)

	echo "<|--" >> .acumulo.txt
	echo "-Quest $THIS_QUEST_NUMBER:" >> .acumulo.txt
	echo >> .acumulo.txt

	if [ -z "$THIS_QUEST_WEIGHT" ] ; then
		THIS_QUEST_WEIGHT=1
	fi

	THIS_QUEST_EXECUTABLE=$( test_file_func $THIS_QUEST_KEY )

	if [ -f $THIS_QUEST_EXECUTABLE ] ; then

		mv $THIS_QUEST_EXECUTABLE vpl_test
		mv $( cases_file_func $THIS_QUEST_KEY ) evaluate.cases

		./.vpl_tester >> $THIS_QUEST_OUTFILE

		sed -i "s/^Grade :=>>/PartialGrade :=>>/" $THIS_QUEST_OUTFILE
		PARTIAL=$( awk '{ /^PartialGrade :=>> +[[:digit:]]+([.][[:digit:]]+)?$/ } END { print $NF }' $THIS_QUEST_OUTFILE | grep -Eo '[[:digit:]]+([.][[:digit:]]+)?')
	else
		PARTIAL=0
		echo ">Fail: Missing file" >> .acumulo.txt
	fi

	CURRENT_GRADE=$(awk 'BEGIN { printf "%.3f\n", '$CURRENT_GRADE'+('$PARTIAL'*'$THIS_QUEST_WEIGHT') }')
	SCALE=$(awk 'BEGIN { printf "%.3f\n", '$SCALE'+'$THIS_QUEST_WEIGHT' }')
	
	echo $THIS_QUEST_WEIGHT

	THIS_QUEST_GRADE=$(awk 'BEGIN { printf "%.3f\n", ('$THIS_QUEST_WEIGHT'*'$PARTIAL')/('$VPL_GRADEMAX$'-'$VPL_GRADEMIN')+'$VPL_GRADEMIN' }')
	
	THIS_QUEST_AVAIL=$(awk 'BEGIN { printf "%.2f%%", ('$THIS_QUEST_GRADE'/'$THIS_QUEST_WEIGHT')*100 }' )
	echo "THIS_QUEST_AVAIL=$THIS_QUEST_AVAIL"

	# echo ">Key: $THIS_QUEST_KEY" >> .acumulo.txt
	# echo ">Number: $THIS_QUEST_NUMBER" >> .acumulo.txt
	echo ">Arquivo: $THIS_QUEST_FILE" >> .acumulo.txt
	echo ">Escolhido: $( find . -iname $THIS_QUEST_FILE.* 2> /dev/null | sed "s/^\.\///" )" >> .acumulo.txt
	echo ">Modelo: $THIS_QUEST_MODEL" >> .acumulo.txt
	# echo ">Weight: $THIS_QUEST_WEIGHT" >> .acumulo.txt
	# echo ">Partial: $THIS_QUEST_GRADE" >> .acumulo.txt
	# echo ">Scale: $SCALE" >> .acumulo.txt
 	echo ">Avaliação: $THIS_QUEST_GRADE/$THIS_QUEST_WEIGHT" >> .acumulo.txt
	echo ">Avaliação: $THIS_QUEST_AVAIL" >> .acumulo.txt
	echo >> .acumulo.txt
	echo "--|>" >> .acumulo.txt

	cat $THIS_QUEST_OUTFILE >> .acumulo.txt

done

FINAL=$(awk 'BEGIN { printf "%.3f\n", '$CURRENT_GRADE'/'$SCALE' }') 

echo "Grade :=>> $FINAL" >> .acumulo.txt
cat .acumulo.txt
# echo 'Comment :=>>Encerrado'
