LINKER_FILE="linker.json"
VARIANT_FILE=".variation.json"
HASH_SCRIPT="./espalhador.py"
SELECTOR_SCRIPT="./csv_select.py"

CSV_SELECTOR="students_variations.csv"

BUFFER_FILE_BASE=".acumulo.txt"

QUESTION_TAG_BASE="question"
KEY_TAG_BASE="key"
NUMBER_TAG_BASE="number"
FILE_TAG_BASE="file"
WEIGHT_TAG_BASE="weight"
LANGUAGE_TAG_BASE="language"
SKILLS_TAG_BASE="skills"
DESCRIPTION_TAG_BASE="description"
DESCRIPTION_TEXT_TAG_BASE="text"
DESCRIPTION_FUNC_TAG_BASE="func"
CASES_TAG_BASE="cases"
RUNNABLE_TAG_BASE="runnable"
OUTPUT_BASE_TAG="output"
ERROR_BASE_TAG="error"

GERENIC_KEY='§'

function question_list_func { echo $( python3 ./interpreter.py list_questions $VARIANT_FILE ); }

function student_folder_func { echo "."$HASH_X"_"$THIS_STUDENT_VERSION; }
function question_folder_func { echo "."$1"_"$HASH_T; }
function buffer_file_func { echo "$( student_folder_func )/$BUFFER_FILE_BASE"; }

function question_file_func { echo "."$HASH_T"_"$QUESTION_TAG_BASE"_"$1".json"; } # .question_$1.json
function cases_file_func { echo "."$HASH_T"_"$CASES_TAG_BASE"_"$1".cases"; } # .cases_$1.cases
function test_file_func { echo "."$HASH_T"_"$RUNNABLE_TAG_BASE"_"$1".run"; } # .runnable_$1.run
function output_file_func { echo "."$HASH_T"_"$OUTPUT_BASE_TAG"_"$1".txt"; } # .output_$1.txt
function error_file_func { echo "."$HASH_T"_"$ERROR_BASE_TAG"_"$1".txt" ; } # .error_$1.txt

GERENIC_QUESTION_FILE=$( question_file_func $GERENIC_KEY )
GERENIC_CASES_FILE=$( cases_file_func $GERENIC_KEY )

function question_key_tag_func          { python3 ./interpreter.py get_tag_value "$( student_folder_func )/$( question_folder_func $1 )/$( question_file_func $1 )" $KEY_TAG_BASE      ; }
function question_number_tag_func       { python3 ./interpreter.py get_tag_value "$( student_folder_func )/$( question_folder_func $1 )/$( question_file_func $1 )" $NUMBER_TAG_BASE   ; }
function question_file_tag_func         { python3 ./interpreter.py get_tag_value "$( student_folder_func )/$( question_folder_func $1 )/$( question_file_func $1 )" $FILE_TAG_BASE     ; }
function question_weight_tag_func       { python3 ./interpreter.py get_tag_value "$( student_folder_func )/$( question_folder_func $1 )/$( question_file_func $1 )" $WEIGHT_TAG_BASE   ; }
function question_language_tag_func     { python3 ./interpreter.py get_tag_list  "$( student_folder_func )/$( question_folder_func $1 )/$( question_file_func $1 )" $LANGUAGE_TAG_BASE ; }
# fz add
function question_skills_tag_func       { python3 ./interpreter.py get_tag_list  "$( student_folder_func )/$( question_folder_func $1 )/$( question_file_func $1 )" $SKILLS_TAG_BASE ; }
function question_description_tag_func  { python3 ./interpreter.py get_tag_list "$( student_folder_func )/$( question_folder_func $1 )/$( question_file_func $1 )" $DESCRIPTION_TAG_BASE ; }
function question_description_text_tag_func  { python3 ./interpreter.py get_tag_list2 "$( student_folder_func )/$( question_folder_func $1 )/$( question_file_func $1 )" "$DESCRIPTION_TAG_BASE;$DESCRIPTION_TEXT_TAG_BASE" ; }
function question_description_func_tag_func  { python3 ./interpreter.py get_tag_list2 "$( student_folder_func )/$( question_folder_func $1 )/$( question_file_func $1 )" "$DESCRIPTION_TAG_BASE;$DESCRIPTION_FUNC_TAG_BASE" ; }
# fz end

function variant_counter_func   { python3 ./interpreter.py variants_count $1 ; }
function variant_select_func    { python3 ./interpreter.py variants_select $LINKER_FILE $1 $VARIANT_FILE ; }
function variant_expansion_func { python3 ./interpreter.py variant_expansion $VARIANT_FILE $( $1 $3 ) $( $2 $3 ) $3 ; }

function get_studante_version()   { echo $( python3 ./interpreter.py get_csv_version "$CSV_SELECTOR" "$1" ); }
# fz add
function get_studante_version_email()   { echo $( python3 ./interpreter.py get_csv_version_email "$CSV_SELECTOR" "$1" ); }
# fz end
function get_student_hash()   { echo $( python3 ./interpreter.py get_student_hash "$1" ); }

function question_cases_excpansion_func { python3 ./interpreter.py expand_cases  $( question_file_func $1 ) $CASES_TAG_BASE    ; }
