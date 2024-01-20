#!/bin/bash

. common_script.sh

. linker_script.sh

HASH_X=$(echo $MOODLE_USER_NAME | python3 ./espalhador.py)
# echo $HASH_X

if [ -f $LINKER_FILE ] ; then

    VARIANTS=$( variant_counter_func $LINKER_FILE )
    THIS_STUDENT_VERSION=$(expr $HASH_X % $VARIANTS)

    if [ ! -z "$THIS_STUDENT_VERSION" ] ; then
        variant_select_func $THIS_STUDENT_VERSION
    fi

    # echo "Variants:"$VARIANTS
    # echo "file $LINKER_FILE found!"
    # echo $THIS_STUDENT_VERSION
    # cat $VARIANT_FILE | python3 -m json.tool

else
	echo "echo 'comment :=>> Arquivo $LINKER_FILE não achado'" > vpl_execution
fi

if [ -f $VARIANT_FILE ] ; then

    variant_expansion_func question_file_func cases_file_func $GERENIC_KEY
    QUESTION_LIST=$( question_list_func )
    # echo $QUESTION_LIST

fi

for THIS_QUESTION_KEY in $QUESTION_LIST ; do

    if [ -f $( question_file_func $THIS_QUESTION_KEY ) ] ; then

        THIS_QUESTION_NUMBER=$( question_number_tag_func   $THIS_QUESTION_KEY )
        THIS_QUESTION_FILE=$(   question_file_tag_func     $THIS_QUESTION_KEY )
        THIS_QUESTION_WEIGHT=$( question_weight_tag_func   $THIS_QUESTION_KEY )
        THIS_QUESTION_LANG=$(   question_language_tag_func $THIS_QUESTION_KEY )

        THIS_QUESTION_CHOSEN_FILE=$( find $THIS_QUESTION_FILE.* 2> /dev/null )

        if [ ! -z $THIS_QUESTION_CHOSEN_FILE ] && [ -f $THIS_QUESTION_CHOSEN_FILE ] ; then
            # echo "found: '$THIS_QUESTION_CHOSEN_FILE'"
            ./vpl_run.sh $THIS_QUESTION_CHOSEN_FILE >> vpl_compilation_error.txt 2>&2 1>&2
            if [ -f vpl_execution ] ; then
                # echo "Creating:"$( test_file_func $THIS_QUESTION_KEY )
                mv vpl_execution $( test_file_func $THIS_QUESTION_KEY )
            else
                echo "Erro de compilação"
            fi
        # else
        # 	echo "nope:$THIS_QUESTION_KEY"
        fi

        THIS_QUESTION="$THIS_QUESTION_NUMBER|$THIS_QUESTION_KEY"

        ALL_QUESTIONS="$ALL_QUESTIONS $THIS_QUESTION"

        # echo $THIS_QUESTION
        # echo ">>>"
        # echo "  key:" $THIS_QUESTION_KEY
        # echo "  number:" $THIS_QUESTION_NUMBER
        # echo "  file:" $THIS_QUESTION_FILE
        # echo "  weight:" $THIS_QUESTION_WEIGHT
        # echo "  lang:" $THIS_QUESTION_LANG
        # echo "<<<"
        # echo


    else
        echo "Arquivo $( question_file_func $THIS_QUESTION_KEY ) não achado"
    fi

done


ALL_QUESTIONS=$( echo $ALL_QUESTIONS | xargs -n1 | sort | xargs )

echo 'ALL_QUESTIONS="'$ALL_QUESTIONS'"' >> linker_script.sh
echo 'THIS_STUDENT_VERSION="'$THIS_STUDENT_VERSION'"' >> linker_script.sh


if [ "$SECONDS" = "" ] ; then
	export SECONDS=20
fi
if [ "$VPL_GRADEMIN" = "" ] ; then
	export VPL_GRADEMIN=0
	export VPL_GRADEMAX=10
fi


mv vpl_evaluate.cpp vpl_evaluate.cpp.origin

#Add constants to vpl_evaluate2012.cpp
echo "const float VPL_GRADEMIN=$VPL_GRADEMIN;" >vpl_evaluate.cpp
echo "const float VPL_GRADEMAX=$VPL_GRADEMAX;" >>vpl_evaluate.cpp
let VPL_MAXTIME=VPL_MAXTIME-$SECONDS-1;
echo "const int VPL_MAXTIME=$VPL_MAXTIME;" >>vpl_evaluate.cpp
cat vpl_evaluate.cpp.origin >> vpl_evaluate.cpp

check_program g++
g++ vpl_evaluate.cpp -g -lm -lutil -o .vpl_tester

mv vpl_execution.sh vpl_execution
chmod +x vpl_execution
