#!/bin/bash

. common_script.sh

. linker_script.sh

# echo "Frase De Exemplo" | awk '{ if($i ~ /[[:alpha:]]/) print $i }'

HASH_X=$(echo $MOODLE_USER_NAME | python3 ./espalhador.py)

if [ -f $QUEST_LINKER_FILE ] ; then

	# echo "file $QUEST_LINKER_FILE found!"
	QUEST_LIST=$( quest_list_func )

	for THIS_QUEST_KEY in $QUEST_LIST ; do

		touch $( quest_file_func $THIS_QUEST_KEY )
		tag_elements_to_file $( quest_tag_ini_func $THIS_QUEST_KEY ) $QUEST_TAG_FIN $QUEST_LINKER_FILE $( quest_file_func $THIS_QUEST_KEY )

		THIS_QUEST_CASES_FILE=$( cases_file_func $THIS_QUEST_KEY )

		if [ -f $THIS_QUEST_CASES_FILE ] ; then

			# echo $THIS_QUEST_CASES_FILE "Found!"
			VERSIONS=$(awk_tag_counter $MODEL_TAG_FIN $THIS_QUEST_CASES_FILE )
			# echo $VERSIONS

			THIS_QUEST_MODEL=0

			if [ 0 -lt "$VERSIONS"  ] ; then
				if [ 1 -eq $(awk_tag_counter $( model_tag_func 0 ) $THIS_QUEST_CASES_FILE ) ] ; then
					let VERSIONS--
					tag_elements_to_file $( model_tag_func 0 ) $MODEL_TAG_FIN $THIS_QUEST_CASES_FILE vpl_evaluate_temp.cases
				fi

				THIS_QUEST_MODEL=$(expr $HASH_X % $VERSIONS + 1)
				tag_elements_to_file $( model_tag_func $THIS_QUEST_MODEL ) $MODEL_TAG_FIN $THIS_QUEST_CASES_FILE vpl_evaluate_temp.cases

				mv vpl_evaluate_temp.cases $THIS_QUEST_CASES_FILE
			fi

			echo $( model_tag_set_func $THIS_QUEST_MODEL ) >> $( quest_file_func $THIS_QUEST_KEY )

		else
			echo "Missing cases file: $THIS_QUEST_CASES_FILE"
		fi

		THIS_QUEST_NUMBER=$( quest_number_tag_func $THIS_QUEST_KEY)
		THIS_QUEST_FILE=$(   quest_file_tag_func   $THIS_QUEST_KEY)
		# THIS_QUEST_WEIGHT=$( quest_weight_tag_func $THIS_QUEST_KEY)

		THIS_QUEST_FILE=$( find . -iname $THIS_QUEST_FILE.* 2> /dev/null )

		if [ ! -z $THIS_QUEST_FILE ] && [ -f $THIS_QUEST_FILE ] ; then
			# echo "found: '$THIS_QUEST_FILE'"
			./vpl_run.sh $THIS_QUEST_FILE >> vpl_compilation_error.txt 2>&1
			if [ -f vpl_execution ] ; then
					mv vpl_execution $( test_file_func $THIS_QUEST_KEY )
			fi
		# else
		# 	echo "nope"
		fi

		THIS_QUEST="$THIS_QUEST_NUMBER|$THIS_QUEST_KEY"

		ALL_QUESTIONS="$ALL_QUESTIONS $THIS_QUEST"

		# echo $THIS_QUEST
		# echo ">>>"
		# echo "  key:" $THIS_QUEST_KEY
		# echo "  number:" $THIS_QUEST_NUMBER
		# echo "  file:" $THIS_QUEST_FILE
		# echo "  weight:" $THIS_QUEST_WEIGHT
		# echo "  model:" $THIS_QUEST_MODEL
		# echo "<<<"
		# echo


	done

	ALL_QUESTIONS=$( echo $ALL_QUESTIONS | xargs -n1 | sort | xargs )

	echo 'ALL_QUESTIONS="'$ALL_QUESTIONS'"' >> linker_script.sh

else
	echo "echo 'comment :=>> Arquivo $QUEST_LINKER_FILE não achado'" > vpl_execution
fi

# echo "All Questions: $ALL_QUESTIONS"

mv vpl_evaluate.cpp vpl_evaluate.cpp.origin

#Add constants to vpl_evaluate2012.cpp
echo "const float VPL_GRADEMIN=$VPL_GRADEMIN;" >vpl_evaluate.cpp
echo "const float VPL_GRADEMAX=$VPL_GRADEMAX;" >>vpl_evaluate.cpp
let VPL_MAXTIME=VPL_MAXTIME-$SECONDS-1;
echo "const int VPL_MAXTIME=$VPL_MAXTIME;" >>vpl_evaluate.cpp
cat vpl_evaluate.cpp.origin >> vpl_evaluate.cpp

check_program g++
g++ vpl_evaluate.cpp -g -lm -lutil -o .vpl_tester

if [ "$SECONDS" = "" ] ; then
	export SECONDS=20
fi
if [ "$VPL_GRADEMIN" = "" ] ; then
	export VPL_GRADEMIN=0
	export VPL_GRADEMAX=10
fi

mv vpl_execution.sh vpl_execution
chmod +x vpl_execution
