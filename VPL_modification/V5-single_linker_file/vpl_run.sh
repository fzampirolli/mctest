. commom_script.sh

function fail_abort {
	rm vpl_execution
	exit 0
}

FILE_EXT=$(echo "$1" | awk -F . '{print $NF}' )

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
			local CLASSNAME=$(echo "$1" |sed 's/\//\./g')
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
		egrep "void[ \t]+main[ \t]*\(" $1 2>&1 >/dev/null
		if [ "$?" -eq "0" ]	; then
			MAINCLASS=$(getClassName "$1")
			break
		fi
		if [ "$MAINCLASS" = "" ] ; then
			echo "Class with \"public static void main(String[] arg)\" method not found"
			fail_abort
		fi
		# cat common_script.sh > vpl_execution
		echo "java -Xmx16M -enableassertions $MAINCLASS" >> vpl_execution
		chmod +x vpl_execution
		;;
	py)
		check_program python
		cat common_script.sh > vpl_execution
		echo "python $1" >>vpl_execution
		;;
	*)
		echo "I'm sorry, but I haven't a default action to run these type of submitted files"
		fail_abort
		;;
esac

chmod +x vpl_execution