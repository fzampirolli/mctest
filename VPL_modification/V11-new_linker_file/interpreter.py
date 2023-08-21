#!/usr/bin/env python3

import json
import argparse
import sys
import csv
import unicodedata
import string

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
            if type(C["input"]) is not list:
                print("input=",  C["input"],  sep="", file=cases_file)
            else:
                for i in C["input"]:
                    print("input=",  i,  sep="", file=cases_file)
            if type(C["output"]) is not list:
                print("output=", C["output"], sep="", file=cases_file)
            else:
                for i in C["output"]:
                    print("output=", i, sep="", file=cases_file)

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

def get_student_hash(name, max_v = int(1e10), min_v = int(1e9), factor=[113, 397, 409]):
    '''
    signature:
        get_student_hash(name, max_v = int(1e10), min_v = int(1e9), factor=[113, 397, 409])
    returns:
        none
    operation:
        prints list hash calculated from 'name' using 'factor' as coheficient
    '''

    primeLst = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,239,241,251,257,263,269,271,277,281,283,293,307,311,313,317,331,337,347,349,353,359,367,373,379,383,389,397,401,409,419,421,431,433,439,443,449,457,461,463,467,479,487,491,499,503,509,521,523,541,547,557,563,569,571,577,587,593,599,601,607,613,617,619,631,641,643,647,653,659,661,673,677,683,691,701,709,719,727,733,739,743,751,757,761,769,773,787,797,809,811,821,823,827,829,839,853,857,859,863,877,881,883,887,907,911,919,929,937,941,947,953,967,971,977,983,997]

    D = {}
    for c in string.ascii_lowercase:
        D[c] = string.ascii_lowercase.find(c)+1

    for c in string.ascii_uppercase:
        D[c] = string.ascii_uppercase.find(c)+1

    D['-'] = 0;
    D["'"] = 0;

    name = unicodedata.normalize('NFKD', name).encode('ascii','ignore').decode('ascii').split()
    name = name[0]+name[-1]

    hash_b = 0

    for j in range(len(factor)):
        current_hash = 0
        for i in range(len(name)):
            current_hash = current_hash*factor[j] + primeLst[-D[name[-i-1]]] # + primeLst[-D[name[-i-1]]]

        hash_b += current_hash

    while hash_b > max_v or hash_b < min_v:
        if hash_b > max_v:
            hash_b = hash_b%max_v + hash_b//min_v
        else:
            hash_b **= primeLst[1]
    print(int(hash_b))

def get_csv_version(in_file, name):
    '''
    signature:
        get_csv_version(in_file, name)
    returns:
        none
    operation:
        prints the number of second columng in CSV from file `in_file` when the first column is 'name'
    '''
    name = unicodedata.normalize('NFKD', name).encode('ascii','ignore').decode('ascii').lower().split()
    name = name[0]+name[-1]
    try:
        selector = {}
        for i in csv.reader(open(in_file)):
            aux = i[0]
            aux = unicodedata.normalize('NFKD', aux).encode('ascii','ignore').decode('ascii').lower().split()
            aux = aux[0]+aux[-1]
            selector[aux] = i[1]
        if name in selector:
            print(selector[name])
        else:
            print("")
    except:
        print("")

function_dict = {
    variants_count.__name__    : variants_count,
    variants_select.__name__   : variants_select,
    variant_expansion.__name__ : variant_expansion,
    list_questions.__name__    : list_questions,
    get_tag_value.__name__     : get_tag_value,
    get_tag_list.__name__      : get_tag_list,
    get_csv_version.__name__   : get_csv_version,
    get_student_hash.__name__  : get_student_hash
}

if 1<len(sys.argv):


    parser = argparse.ArgumentParser()

    parser.add_argument( 'function', nargs=1 )
    parser.add_argument( 'arguments', nargs='+' )
    args = parser.parse_args()

    # print(args.arguments, flush=True)

    function = function_dict[args.function[0]]
    function( *args.arguments[0:] )

else:
    print("Use a function:", *function_dict.keys(), sep="\n\t")

