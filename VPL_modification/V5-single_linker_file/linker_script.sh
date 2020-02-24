QUEST_TAG_BASE="quest"

function quest_tag_ini_func { echo "<$QUEST_TAG_BASE=$@>"; }
function quest_file_func { echo ".question_$@.xml"; }
function cases_file_func { echo "vpl_evaluate_$1.cases"; }
function test_file_func { echo "vpl_test_$1.run"; }
function output_file_func { echo ".saida_$1.txt"; }

QUEST_TAG_INI=$( quest_tag_ini_func '[A-Z]+' )
QUEST_TAG_FIN="<\/$QUEST_TAG_BASE>"
QUEST_LINKER_FILE="linker.xml"

NUMBER_TAG_BASE="number"
function number_tag_func { echo "<$NUMBER_TAG_BASE=$@\/>"; }
NUMBER_TAG=$( number_tag_func '[0-9]+' )

FILE_TAG_BASE="file"
function file_tag_func { echo "<$FILE_TAG_BASE=$@\/>"; }
FILE_TAG=$( file_tag_func '[0-9a-zA-Z]+' )

WEIGHT_TAG_BASE="weight"
function weight_tag_func { echo "<$WEIGHT_TAG_BASE=$@\/>"; }
WEIGHT_TAG=$( weight_tag_func '[0-9]+' )

MODEL_TAG_BASE="model"

function model_tag_func { echo "<$MODEL_TAG_BASE=$@>"; }
function model_tag_get_func { echo "<$MODEL_TAG_BASE=$@\/>"; }
function model_tag_set_func { echo "<$MODEL_TAG_BASE=$@/>"; }

MODEL_TAG_INI=$( model_tag_func '[0-9]+' )
MODEL_TAG_FIN="<\/$MODEL_TAG_BASE>"
MODEL_TAG=$( model_tag_get_func '[0-9]+' )

function awk_tagger_file { awk '{ if($i ~ /'$1'/) print $i }' $2 ; }
function awk_tag_counter { awk '{ if ($i ~ /'$1'/) counter++ } BEGIN { counter=0 } END { print counter }' $2 ; }
function sed_tagger_read { sed -r 's:'$($1 '('$2')' )':\1:' ; }

function quest_list_func {       awk_tagger_file $QUEST_TAG_INI $QUEST_LINKER_FILE      | tr -d \\r | sed_tagger_read quest_tag_ini_func '[A-Z]+' ; }
function quest_number_tag_func { awk_tagger_file $NUMBER_TAG    $( quest_file_func $1 ) | tr -d \\r | sed_tagger_read number_tag_func    '[0-9]+' ; }
function quest_file_tag_func {   awk_tagger_file $FILE_TAG      $( quest_file_func $1 ) | tr -d \\r | sed_tagger_read file_tag_func      '[0-9a-zA-Z]+' ; }
function quest_weight_tag_func { awk_tagger_file $WEIGHT_TAG    $( quest_file_func $1 ) | tr -d \\r | sed_tagger_read weight_tag_func    '[0-9]+' ; }
function quest_model_tag_func {  awk_tagger_file $MODEL_TAG     $( quest_file_func $1 ) | tr -d \\r | sed_tagger_read model_tag_get_func '[0-9]+' ; }

# Initial_tag final_tag input_file output_file
function tag_elements_to_file
{
	sed -n "/"$1"/,/"$2"/p" $3 | head -n-1 | tail -n+2 >> $4
	sed -i 's/'$1'//;s/'$2'//;s/^[[:blank:]]//' $4
}
