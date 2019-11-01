#!/bin/bash
# Default evaluate script for VPL
# @Copyright 2014 Juan Carlos Rodríguez-del-Pino
# @License http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
# @Author Juan Carlos Rodríguez-del-Pino <jcrodriguez@dis.ulpgc.es>

#load VPL environment vars
. common_script.sh
if [ "$SECONDS" = "" ] ; then
	export SECONDS=20
fi
if [ "$VPL_GRADEMIN" = "" ] ; then
	export VPL_GRADEMIN=0
	export VPL_GRADEMAX=10
fi

#exist run script?
if [ ! -s vpl_run.sh ] ; then
	echo "I'm sorry, but I haven't a default action to evaluate the type of submitted files"
else
	#avoid conflict with C++ compilation
	mv vpl_evaluate.cpp vpl_evaluate.cpp.save
	#Prepare run
	./vpl_run.sh >>vpl_compilation_error.txt 2>&1
	cat vpl_compilation_error.txt
	if [ -f vpl_execution ] ; then
		mv vpl_execution vpl_test
		
		echo "#!/bin/bash" > vpl_execution
		
############################# AVALIADOR MULTI CASO #############################

        #error_model_not_found

		seletor=modelo.txt
		
        if [ -s $seletor ]; then
            
		    tr_seletor=$(tr "[:lower:]" "[:upper:]" < $seletor)
        	
        	if [ ! $(echo $tr_seletor | awk '{o=0; for(i=1;i<=NF;i++) if($i ~ /MODELO:?[:space:]*/) { o=1; break } print (o)}') != 1 ]; then
        	
        	    eval_alternative=$(echo $tr_seletor | awk '{for(i=1;i<=NF;i++) if($i ~ /MODELO:?[:space:]*/) print ($(i+1))}')
        		
        		eval_select=vpl_evaluate_$eval_alternative.cases
        		if [ -f $eval_select ] ; then
				    mv $eval_select vpl_evaluate.cases
				    #echo $eval_alternative
                else
                    echo "echo 'Comment :=>>Seleção inválida no arquivo $seletor, a opção $eval_alternative não existe'" >> vpl_execution
                    echo "echo 'Grade :=>>$VPL_GRADEMIN'" >> vpl_execution
                    chmod +x vpl_execution
                    exit 1
                fi
        	else
        	    echo 'echo "Comment :=>>Erro no arquivo $seletor, o formato correto é '"'Modelo: X'"'"' >> vpl_execution
			    echo "echo 'Grade :=>>$VPL_GRADEMIN'" >> vpl_execution
			    chmod +x vpl_execution
			    exit 1
        	fi
		else
			echo "echo 'Comment :=>>Erro: o arquivo '$seletor' é necessário para completar a avaliação'" >> vpl_execution
			echo "echo 'Comment :=>>Deve conter: 'Modelo: X' onde X é o modelo indicado'" >> vpl_execution
			echo "echo 'Grade :=>>$VPL_GRADEMIN'" >> vpl_execution
			chmod +x vpl_execution
			exit 1
        fi
        
################################################################################
        
		
		if [ -f vpl_evaluate.cases ] ; then
			mv vpl_evaluate.cases evaluate.cases
		else
			echo "Error need file 'vpl_evaluate.cases' to make an evaluation"
			exit 1
		fi
		#Add constants to vpl_evaluate.cpp
		echo "const float VPL_GRADEMIN=$VPL_GRADEMIN;" >vpl_evaluate.cpp
		echo "const float VPL_GRADEMAX=$VPL_GRADEMAX;" >>vpl_evaluate.cpp
		let VPL_MAXTIME=VPL_MAXTIME-$SECONDS-1;
		echo "const int VPL_MAXTIME=$VPL_MAXTIME;" >>vpl_evaluate.cpp
		cat vpl_evaluate.cpp.save >> vpl_evaluate.cpp
		check_program g++
		g++ vpl_evaluate.cpp -g -lm -lutil -o .vpl_tester
		if [ ! -f .vpl_tester ] ; then
			echo "Error compiling evaluation program"
		else
			#echo "#!/bin/bash" >> vpl_execution
			echo "./.vpl_tester" >> vpl_execution
		fi
	else
		echo "#!/bin/bash" >> vpl_execution
		echo "echo" >> vpl_execution
		echo "echo '<|--'" >> vpl_execution
		echo "echo '-$VPL_COMPILATIONFAILED'" >> vpl_execution
		if [ -f vpl_wexecution ] ; then
			echo "echo '======================'" >> vpl_execution
			echo "echo 'It seems you are trying to test a program with a graphic user interface'" >> vpl_execution
		fi
		echo "echo '--|>'" >> vpl_execution		
		echo "echo" >> vpl_execution		
		echo "echo 'Grade :=>>$VPL_GRADEMIN'" >> vpl_execution
	fi
	chmod +x vpl_execution
fi

printf "\n\n"

#ls | cat