#!/bin/bash

# make
# base64 -d zip.tar.gz.b64 > zip.tar.gz && tar -zxf zip.tar.gz

. common_script.sh

# cat common_script.sh

. linker_script.sh

HASH_X=$( get_student_hash $MOODLE_USER_EMAIL )

HASH_T=$( date '+%s%N' )

HASH_E=$MOODLE_USER_EMAIL


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
        # echo "<<<"
        # echo


    else
        echo "Arquivo $( question_file_func $THIS_QUESTION_KEY ) não achado"
    fi

done


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



mv vpl_evaluate1.cpp vpl_evaluate.cpp.origin

#Add constants to vpl_evaluate.cpp
echo "const float VPL_GRADEMIN=$VPL_GRADEMIN;" >vpl_evaluate.cpp
echo "const float VPL_GRADEMAX=$VPL_GRADEMAX;" >>vpl_evaluate.cpp
let VPL_MAXTIME=VPL_MAXTIME-$SECONDS-1;
echo "const int VPL_MAXTIME=$VPL_MAXTIME;" >>vpl_evaluate.cpp
cat vpl_evaluate.cpp.origin >> vpl_evaluate.cpp

check_program g++
g++ vpl_evaluate.cpp -g -lm -lutil -o .vpl_tester

mv vpl_execution.sh vpl_execution

chmod +x vpl_execution

#ls -a1R

#echo '#### vpl_evaluate.sh - passou'

