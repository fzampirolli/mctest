#!/usr/bin/env python3

import json
import argparse
import sys

def variants_count(in_file, tag="variations"):
    '''
    signature:
        variants_count(in_file, tag="variations")
    returns:
        none
    operation:
        prints list item count in JSON field associated with `tag`, from `in_file` file
    '''
    voorhees = json.load(open(in_file))
    print(len(voorhees[tag]))

def variants_select(in_file, variant, out_file, tag="variations"):
    '''
    signature:
        variants_select(in_file, variant, out_file, tag="variations")
    returns:
        none
    operation:
        selects JSON field associated with `tag`, from file `in_file`, select item with index `variant` from list, print to file `out_file`
    '''
    voorhees = json.load(open(in_file))
    var_data = voorhees[tag][int(variant)]
    json.dump(var_data, open(out_file,'w'), indent=4, sort_keys=False)
    # json.dump(var_data, sys.stdout)

def variant_expansion(in_file, question_out_file, cases_out_file, replacer, tag="questions"):
    '''
    signature:
        def variant_expansion(in_file, question_out_file, cases_out_file, replacer, tag="questions")
    returns:
        none
    operation:
        selects list in JSON field associated with `tag`, from file `in_file`
        for each object `Q` in that list:
            creates a file using `question_out_file`, replacing `replacer` to the value of `Q["key"]`, as name
            insert object data into file as JSON
            creates a file using `cases_out_file`, replacing `replacer` to the value of `Q["key"]`, as name
            expand object in JSON field associated to "cases" tag, into .cases file
    '''
    voorhees = json.load(open(in_file))
    for Q in voorhees[tag]:
        json.dump(Q, open(question_out_file.replace(replacer, Q["key"]) ,'w'), indent=4, sort_keys=False)
        cases_file = open(cases_out_file.replace(replacer, Q["key"]),'w')
        for C in Q["cases"]:
            print("", sep="", file=cases_file)
            print("case=",   C["case"],   sep="", file=cases_file)
            print("input=",  C["input"],  sep="", file=cases_file)
            print("output=", C["output"], sep="", file=cases_file)

def list_questions(in_file, tag="questions"):
    '''
    signature:
        list_questions(in_file, tag="questions")
    returns:
        none
    operation:
        selects list in JSON field associated with `tag`, from file `in_file`
        prints the value of `Q["key"]` for each item `Q` in that list
    '''
    voorhees = json.load(open(in_file))
    L = [ Q["key"] for Q in voorhees[tag] ]
    print(*L)

def get_tag_value(in_file, tag):
    '''
    signature:
        get_tag_value(in_file, tag)
    returns:
        none
    operation:
        prints JSON field associated with `tag`, from file `in_file`
    '''
    voorhees = json.load(open(in_file))
    try:
        print(voorhees[tag])
    except:
        print("")

def get_tag_list(in_file, tag):
    '''
    signature:
        get_tag_value(in_file, tag)
    returns:
        none
    operation:
        prints list in JSON field associated with `tag`, from file `in_file`
    '''
    voorhees = json.load(open(in_file))
    try:
        print(*voorhees[tag])
    except:
        print("")


function_dict = {
    variants_count.__name__    : variants_count,
    variants_select.__name__   : variants_select,
    variant_expansion.__name__ : variant_expansion,
    list_questions.__name__    : list_questions,
    get_tag_value.__name__     : get_tag_value,
    get_tag_list.__name__      : get_tag_list
}

if 1<len(sys.argv):


    parser = argparse.ArgumentParser()

    parser.add_argument( 'function', nargs=1 )
    parser.add_argument( 'arguments', nargs='+' )
    args = parser.parse_args()

    function = function_dict[args.function[0]]
    function( *args.arguments[0:] )

else:
    print("Use a function:", *function_dict.keys(), sep="\n\t")

