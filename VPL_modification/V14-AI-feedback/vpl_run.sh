#!/bin/bash

. common_script.sh

. linker_script.sh

HASH_X=$( get_student_hash $MOODLE_USER_EMAIL )
HASH_T=$( date '+%s%N' )

# env > lixo
# cat lixo
# echo "$MOODLE_USER_EMAIL"
# echo "$HASH_X"

# ext=""
# for file in $VPL_SUBFILES; do
#     current_ext="${file##*.}"
#     if [ -z "$ext" ]; then
#         ext="$current_ext"
#     elif [ "$ext" != "$current_ext" ]; then
#         echo "Erro: Os arquivos devem ter a mesma extensão. Encontrado '$ext' e '$current_ext'."
#         exit 1
#     fi
# done

export VPL_SUBFILE0="$VPL_SUBFILE0"
export FILE_EXT="${filename##*.}"
### ATENCAO

function fail_abort {
	rm vpl_execution
	exit 0
}

FILE_EXT=$(echo "$1" | awk -F . '{print $NF}' )

touch vpl_execution

# echo "$FILE_EXT vs $2" 1>&2

if [[ ! ( $2 =~ "all" || $2 =~ $FILE_EXT) ]] ; then
    # echo "Entrou no if"
    echo "Formato de arquivo inválido."
    fail_abort
fi

{
case $FILE_EXT in
	c)
		check_program gcc
		gcc -fno-diagnostics-color -o vpl_execution -std=c99 $1 -lm -lutil
		;;
	cpp|C)
		check_program g++
		g++ -fno-diagnostics-color -o vpl_execution $1 -lm -lutil
		;;
	java)
		function getClassName {
			#replace / for .
			local CLASSNAME=$(echo "$1" | sed 's/\//\./g')
			#remove file extension .java
			CLASSNAME=$(basename "$CLASSNAME" .java)
			echo $CLASSNAME
		}
		check_program javac
		check_program java
		javac -J-Xmx64m -Xlint:deprecation $1
		if [ "$?" -ne "0" ] ; then
			echo "Not compiled"
			fail_abort
		fi
		MAINCLASS=$(getClassName "$1")
		if [ "$MAINCLASS" = "" ] ; then
			echo "Class with \"public static void main(String[] arg)\" method not found"
			fail_abort
		fi
		# cat common_script.sh > vpl_execution
		# echo $MAINCLASS >&2
		echo "#!/bin/bash" >> vpl_execution
		echo "java -Xmx16M -enableassertions $MAINCLASS" >> vpl_execution
		;;
	py)
		check_program python
 		# cat common_script.sh > vpl_execution
 		
 		# Alguns filtros feitos pelo Paulo Pisani
 		# adaptei em vpl_evaluate.sh
        
		echo "#!/bin/bash" >> vpl_execution
		echo "python3 $1" >> vpl_execution
		;;
	r|R)
		check_program Rscript
		echo "#!/bin/bash" >> vpl_execution
		echo "Rscript $1" >> vpl_execution
		;;
	js)
		check_program js
		echo "#!/bin/bash" >> vpl_execution
		echo "node $1" >> vpl_execution
		;;
	txt) 
	    # ft add
		echo "#!/bin/bash" >> vpl_execution
		echo "python3 vpl_main.py $( student_folder_func )" >> vpl_execution
        #cat << EOS >> vpl_execution
        #cat $vpl_execution
        #echo "passou"
        #exit 0
        # ft end
		;; 
	*)
        echo "Formato de arquivo desconhecido."
# 		echo "I'm sorry, but I haven't a default action to run these type of submitted files" >&2
		fail_abort
		;;
esac
} || {
    echo "Erro de compilação."
    fail_abort
}

chmod +x vpl_execution

