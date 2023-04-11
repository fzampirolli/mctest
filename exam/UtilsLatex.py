'''
=====================================================================
Copyright (C) 2018-2023 Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of MCTest 5.2.

Languages: Python 3.8.5, Django 2.2.4 and many libraries described at
github.com/fzampirolli/mctest

You should cite some references included in vision.ufabc.edu.br
in any publication about it.

MCTest is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License
(gnu.org/licenses/agpl-3.0.txt) as published by the Free Software
Foundation, either version 3 of the License, or (at your option) 
any later version.

MCTest is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

=====================================================================
'''
import binascii
import csv
import datetime
import json
import os
import re
import subprocess
import time
import unicodedata
import zlib

import bcrypt
import numpy as np
import pyqrcode
import random
import string
from django.contrib import messages
from django.http import HttpResponse
# coding=UTF-8
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from topic.UtilsMCTest4 import UtilsMC
from topic.models import Question


class Utils(object):

    @staticmethod
    def getstr_QM(exam, variation_i):
        if int(Utils.getNumMCQuestions(exam)) == 0 or exam.exam_print in ['answ']:
            return ''
        d = exam.variationsExams2.all()[variation_i]
        s = eval(d.variation)
        strQM = '\n\n% QUESTOES DE MULTIPLA ESCOLHA\n\n'
        strQM += "\\\\\\vspace{2mm}\\hspace{-5mm}\\noindent\\textbf{%s:}\\vspace{2mm}\n" % _(
            "Multiple Choice Questions")

        ss1 = "\n\n\hspace{-15mm}{\\tiny {\\color{white}\\@%s}} \\hspace{0mm}"
        for var in s['variations']:
            for q in var['questions']:
                if q['type'] == 'QM':
                    ss = ss1 % str(q['key']).zfill(4)
                    strQM += "%s %s. %s\\vspace{0mm}\n" % (ss, str(q['number']), q['text'])  # q.question_text)
                    if len(q['answers']):
                        strQM += "\n\\begin{oneparchoices}"
                        for a in q['answers']:
                            if exam.exam_student_feedback:  # se enviar pdf ao aluno, retira gabarito
                                strQM += "\n\n\\choice %s" % a['text']
                            else:
                                if a['sort'] == 0:
                                    strQM += "\n\\choice \\hspace{-2.0mm}{\\tiny{\\color{white}\#%s}}%s" % (
                                        str(a['sort']), a['text'])
                                else:
                                    strQM += "\n\\choice \\hspace{-2.0mm}{\\tiny{\\color{white}#%s}}\\hspace{2.0mm}%s" % (
                                        str(a['sort']), a['text'])
                        strQM += "\n\\end{oneparchoices}\\vspace{1mm}\n\n"

        return strQM

    @staticmethod
    def getQRanswers(exam):
        qr_answers_all = []
        for v in exam.variationsExams2.all():
            qr_answers = ''
            s = eval(v.variation)
            for var in s['variations']:
                for q in var['questions']:
                    qr_answers += str(q['key'])
                    for a in q['answers']:
                        qr_answers += str(a['sort'])
                    qr_answers += ';'
            qr_answers_all.append(qr_answers)
        return qr_answers_all

    # sort DB question by topic, used in XML format of Moodle
    @staticmethod
    def sort_db_questions_by_topic_lixo(db_questions):
        count_varia = 0
        mysort = []

        for varia in db_questions:
            count_varia += 1
            for qts in varia:
                for q in qts:
                    if q == None:
                        break
                    q.insert(0, count_varia)
                    mysort.append(q)

        mysort = sorted(mysort, key=lambda x: x[1])  # by question_id
        mysort = sorted(mysort, key=lambda x: x[4])  # by difficulty
        mysort = sorted(mysort, key=lambda x: x[2])  # by topic
        mysort = sorted(mysort, key=lambda x: x[3])  # by type

        return mysort

    # moodle does not accept words like: echo, python, etc.
    # solution: e$$ $$cho, p$$ $$ython, etc.

    @staticmethod
    def convertWordsMoodle(str1):
        str1 = str1.replace('echo', 'e$$ $$cho')
        str1 = str1.replace('val', 'v$$ $$al')
        str1 = str1.replace('exec', 'e$$ $$xec')
        str1 = str1.replace('python', 'p$$ $$ython')
        return str1

    # create file DB with all variations in aiken format
    @staticmethod
    def createFileDB_xml(exam, path_to_file_VARIATIONS_DB):
        db_questions, n = [], 0
        for v in exam.variationsExams2.all():
            s = eval(v.variation)
            n += 1
            for var in s['variations']:
                for q in var['questions']:
                    q_list = [n] + [v for v in q.values()]
                    db_questions.append(q_list)

        db_questions = sorted(db_questions, key=lambda x: x[0])  # by var
        db_questions = sorted(db_questions, key=lambda x: x[2])  # by key
        db_questions = sorted(db_questions, key=lambda x: x[3])  # by topic
        db_questions = sorted(db_questions, key=lambda x: x[4])  # by type

        question_category = '''
        <!-- category: ___category_comments___  -->
        <question type="category">
        <category>
        <text>$course$/top/___question_type___/___question_topic___/diff___question_diff___/___question_short___</text>
        </category>
        <info format="moodle_auto_format">
        <text></text>
        </info>
        <idnumber></idnumber>
        </question>
        '''
        question_model = '''
        <!-- question: ___question_comments___  -->
          <question type="___question_type___">
            <name>
              <text>Topico: ___question_topic___ Dificuldade: ___question_diff___ </text>
            </name>
            <questiontext format="moodle_auto_format">
              <text><![CDATA[<p> ___question_text___ <br></p>]]></text>
            </questiontext>
            <generalfeedback format="moodle_auto_format">
              <text></text>
            </generalfeedback>
            <defaultgrade>1.0000000</defaultgrade>
            <penalty>0.3333333</penalty>
            <hidden>0</hidden>
            <idnumber></idnumber>
            <single>true</single>
            <shuffleanswers>true</shuffleanswers>
            <answernumbering>abc</answernumbering>
            <correctfeedback format="moodle_auto_format">
              <text>Sua resposta está correta.</text>
            </correctfeedback>
            <partiallycorrectfeedback format="moodle_auto_format">
              <text>Sua resposta está parcialmente correta.</text>
            </partiallycorrectfeedback>
            <incorrectfeedback format="moodle_auto_format">
              <text>Sua resposta está incorreta.</text>
            </incorrectfeedback>
            <shownumcorrect/>        
        '''
        answers_model = '''
            <answer fraction="___answer_value___" format="moodle_auto_format">
              <text><![CDATA[<p> ___answer_text___ <br></p>]]></text>
              <feedback format="moodle_auto_format">
                <text></text>
              </feedback>
            </answer>
        '''
        question_ID_before = -1
        varia_gab_all = []
        for q in db_questions:
            q_str = ''
            q_var = q[0]  # variations
            q_count = q[1]  # cont questions by type
            q_id = q[2]
            q_topic = q[3]
            q_type = q[4]
            q_diff = q[5]
            q_short = q[6]
            q_text = Utils.convertWordsMoodle(q[7])
            answers = q[8]

            # remove all occurance singleline comments (%%COMMENT\n ) from string
            q_text = re.sub(re.compile("%%.*?\n"), "", q_text)

            myflag = False  # criar nova categoria ao mudar de questao
            if question_ID_before != int(q_id):
                myflag = True
                question_ID_before = int(q_id)

            q_str += question_model
            q_str = q_str.replace('___question_db_id___', str(q_id))
            q_str = q_str.replace('___question_text___', str(q_text))
            q_str = q_str.replace('___question_diff___', str(q_diff))
            q_str = q_str.replace('___question_id___', str(q_count))
            q_str = q_str.replace('___question_topic___', str(q_topic))

            if len(answers) > 1:  # QM
                q_str = q_str.replace('___question_type___', 'multichoice')
                q_type = 'multichoice'
                for a in answers:
                    a_str = answers_model
                    a_str = a_str.replace('___answer_text___', a['text'])

                    if not int(a['sort']):
                        a_str = a_str.replace('___answer_value___', '100')
                    else:
                        a_str = a_str.replace('___answer_value___', '0')
                    q_str += Utils.convertWordsMoodle(a_str)

            else:  # QT
                if len(answers) == 1:
                    q_str = q_str.replace('___question_type___', 'shortanswer')
                    q_type = 'shortanswer'
                    answerCorrect = answers[0]['text']
                    q_str += '\n<answer fraction="100" format="moodle_auto_format"><text>\n' + answerCorrect + '\n</text></answer>\n'
                else:  # no answers
                    q_str = q_str.replace('___question_type___', 'essay')
                    q_type = 'essay'

            mystr = " #id:" + str(q_id) + " #type:" + q_type + " #topic:" + str(
                q_topic) + " #diff:" + str(
                q_diff) + " #descr:" + str(
                q_short)
            q_str = q_str.replace('___question_comments___', "#c:" + str(q_count) + mystr + " #var:" + str(q_var))
            q_str += '</question>'

            if myflag:
                q_str = question_category + q_str
                q_str = q_str.replace('___category_comments___', mystr)
                q_str = q_str.replace('___question_db_id___', str(q_id))
                q_str = q_str.replace('___question_text___', str(q_text))
                q_str = q_str.replace('___question_diff___', str(q_diff))
                q_str = q_str.replace('___question_id___', str(q_count))
                q_str = q_str.replace('___question_topic___', str(q_topic))
                q_str = q_str.replace('___question_type___', str(q_type))
                q_str = q_str.replace('___question_short___', str(q_short))
                myflag = False

            varia_gab_all.append(q_str)

        if varia_gab_all:
            with open(path_to_file_VARIATIONS_DB, 'w') as f:
                c = 0
                str_begin = '''
<?xml version="1.0" encoding="UTF-8"?>
<quiz>
'''
                f.write(str_begin)
                for q in varia_gab_all:
                    f.write(str(q) + '\n')

                f.write('</quiz>')

    # create file DB with all variations in aiken format
    @staticmethod
    def createFileDB_aiken(exam, path_to_file_VARIATIONS_DB):
        letras_1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        varia_gab_all, count_varia = [], 0
        for v in exam.variationsExams2.all():
            s = eval(v.variation)
            questions_DB = []
            count_varia += 1
            for var in s['variations']:
                for q in var['questions']:
                    correct = 0
                    questions_DB.append("#c:" + str(q['number']) + " #id:" + str(q['key']) + " #topic:" + str(
                        q['topic']) + " #type:" + str(str(q['type'])) + " #diff:" + str(q['weight']) + "\n")
                    questions_DB.append(Utils.convertWordsMoodle(q['text']))
                    if q['type'] == 'QM':  # QM
                        for k, a in enumerate(q['answers']):
                            questions_DB.append(letras_1[int(a['answer'])] + ") " + Utils.convertWordsMoodle(a['text']))
                            if not int(a['sort']):
                                correct = k
                        questions_DB.append('ANSWER: ' + letras_1[correct] + '\n')
                    else:  # QT with
                        if len(q['answers']) == 1:
                            questions_DB.append('ANSWER: ' + q['answers'][0]['text'] + '\n\n')

            if questions_DB:
                varia_gab_all.append(questions_DB)

        if varia_gab_all:
            with open(path_to_file_VARIATIONS_DB, 'w') as f:
                c = 0
                for varia in varia_gab_all:
                    f.write("############# variation ########## " + str(c) + '\n\n')
                    c += 1
                    for q in varia:
                        f.write(str(q) + '\n')

    # create file DB with all variations in aiken format
    @staticmethod
    def createFile_Tex(request, exam, path_to_file_VARIATIONS_DB, data_hora):
        room = exam.classrooms.all()[0]
        varia_gab_all, s_student_ID = [], 0
        for v in exam.variationsExams2.all():
            s = eval(v.variation)
            questions_DB = []
            s_student_ID += 1
            student_name = str(s_student_ID)
            for var in s['variations']:
                myqr = Utils.defineQRcode(exam, room, student_name)
                strQuestions = Utils.drawCircles()
                strQuestions += Utils.getHeader(request, exam, room, student_name, student_name, myqr,
                                                data_hora)
                strQuestions += Utils.drawAnswerSheet(exam)
                strQuestions += Utils.drawCircles()
                strQuestions += Utils.drawInstructions(exam)
                try:
                    hash_num = Utils.distro_table(str(s_student_ID))
                    var_hash = int(var)  # hash_num % int(exam.exam_variations)
                    myqr.append(qr_answers[var_hash])  # inclui as respostas
                except:
                    hash_num = int(s_student_ID)
                    myqr.append('')

                strQuestions += Utils.drawQuestions(request, myqr,
                                                    exam, room, student_name, student_name,
                                                    hash_num % int(exam.exam_variations), data_hora)

                questions_DB.append(strQuestions + '\n\n')

            if questions_DB:
                varia_gab_all.append(questions_DB)

        if varia_gab_all:
            # start1 = time.time()
            with open(path_to_file_VARIATIONS_DB, 'w') as f:
                c = 0
                f.write(Utils.getBegin())
                for varia in varia_gab_all:
                    f.write("%############# variation ########## " + str(c) + '\n\n')
                    c += 1
                    for q in varia:
                        f.write(str(q) + '\n')
                f.write("\\end{document}")
                f.close()
                if not Utils.genTex(path_to_file_VARIATIONS_DB, "pdfExam"):
                    messages.error(request, _('ERROR in genTex') + ': ' + path_to_file_VARIATIONS_DB)

    # create file template of all variations in varia_gab_all
    @staticmethod
    def createFileTemplates(exam, path_to_file_TEMPLATES):
        letras_1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        headerQM, headerQT, contVaria = [], [], 0
        for i in range(int(Utils.getNumMCQuestions(exam))):
            headerQM.append('Q' + str(i + 1))
        for i in range(int(exam.exam_number_of_questions_text)):
            headerQT.append('Q' + str(int(Utils.getNumMCQuestions(exam)) + i + 1))
        varia_gab_all = [['variation'] + headerQM + headerQT + headerQM]

        for v in exam.variationsExams2.all():
            s = eval(v.variation)
            varia_gab, varia_id_questions = [], []
            for var in s['variations']:
                contVaria += 1
                for q in var['questions']:
                    if q['type'] == 'QM':  # QM
                        sort_list = []
                        for k, a in enumerate(q['answers']):
                            if not int(a['sort']):
                                varia_gab.append(letras_1[k])
                            sort_list.append(a['sort'])
                        varia_id_questions.append(str(q['key']) + ''.join([i for i in sort_list]))
                    else:  # QT with
                        if 'answers' in q.keys() and len(q['answers']) == 1:
                            varia_gab.append(q['answers'][0]['text'])
                        else:
                            varia_gab.append('')
            if varia_gab:
                varia_gab_all.append([str(contVaria - 1)] + varia_gab + varia_id_questions)

        if varia_gab_all:
            with open(path_to_file_TEMPLATES, 'w') as data:
                writer = csv.writer(data)
                for varia in varia_gab_all:
                    writer.writerow(varia)

    # cases = {}   #                      quest1          quest2               quest1       quest2
    #              #            [var1:[ [ [c1],[c2]  ],   [[c1]]     ], var2:[ [[c1]]    ,  [[c2]]     ] ]
    # cases['id']    = np.array([     [     [id1]     ,    [id2]     ],      [  [id2]    ,   [id1]     ] ] )
    # cases['input'] = np.array([     [ [ [1], [2,3] ],  [[2, 2]]    ],      [ [[5, 5]   , [[6, 6]]    ] ] )
    # cases['output']= np.array([     [ [ [1,2], [3] ],  [[3, 4, 5]] ],      [ [[4, 5, 6], [[7, 8, 9]] ] ] )
    # return all test cases from q['testcases']
    @staticmethod
    def get_cases(exam):
        print("get_cases-00-" + str(datetime.datetime.now()))
        cases = {}
        cases['key'], cases['input'], cases['output'], cases['skills'], cases['language'], cases[
            'description'] = [], [], [], [], [], []
        for v in exam.variationsExams2.all():
            d = eval(v.variation)
            for var in d['variations']:
                id_list, in_list, ou_list, sk_list, lang_list, description_list = [], [], [], [], [], []
                for q in var['questions']:
                    if q['type'] == 'QT':
                        print("get_cases-01-" + str(datetime.datetime.now()))
                        if 'testcases' in q.keys():
                            case = q['testcases']
                            # case1 = json.loads(case)
                            id_list.append(case['key'])
                            in_list.append(case['input'])
                            ou_list.append(case['output'])
                            try:
                                sk_list.append(case['skills'])
                            except:
                                sk_list.append([])
                            try:
                                lang_list.append(case['language'])
                            except:
                                lang_list.append(['all'])
                            try:
                                description_list.append(case['description'])
                            except:
                                description_list.append([])

                cases['key'].append(id_list)
                cases['input'].append(in_list)
                cases['output'].append(ou_list)
                cases['skills'].append(sk_list)
                cases['language'].append(lang_list)
                cases['description'].append(description_list)
        return cases

    # cases = {}   #                      quest1          quest2               quest1       quest2
    #              #            [var1:[ [ [c1],[c2]  ],   [[c1]]     ], var2:[ [[c1]]    ,  [[c2]]     ] ]
    # cases['id']    = np.array([     [     [id1]     ,    [id2]     ],      [  [id2]    ,   [id1]     ] ] )
    # cases['input'] = np.array([     [ [ [1], [2,3] ],  [[2, 2]]    ],      [ [[5, 5]   , [[6, 6]]    ] ] )
    # cases['output']= np.array([     [ [ [1,2], [3] ],  [[3, 4, 5]] ],      [ [[4, 5, 6], [[7, 8, 9]] ] ] )
    def format_cases(cases, file):  # _version1
        # file = file.replace(' ', '').replace('/', '-').replace(':', '-')
        # files = ['./tmp/' + file + "_linker.json"]
        # files = [BASE_DIR + '/linker.json']

        formatCases = {}
        formatCases['variations'] = []  # variant/models
        numVars = len(cases['key'])
        for v in range(numVars):  # for each variant/model
            # st_f = './tmp/' + file + '-m' + str(v + 1) + ".cases"
            variant = {}
            variant['variant'] = str(v + 1)
            variant['questions'] = []
            numQuestoes = len(cases['key'][v])
            for q in range(numQuestoes):  # for each question
                count_q = q + 1
                question = {}
                question['key'] = str(cases['key'][v][q][0])
                question['number'] = str(count_q)
                question['file'] = 'Q' + str(count_q)
                try:
                    questionObject = get_object_or_404(Question, pk=question['key'])
                    question['weight'] = questionObject.question_difficulty
                except:
                    question['weight'] = '1'
                question['language'] = cases['language'][v][q]
                question['skills'] = cases['skills'][v][q]
                question['description'] = cases['description'][v][q]
                question['cases'] = []
                if isinstance(cases['input'][v][q], list):
                    numCases = len(cases['input'][v][q])
                    for c in range(numCases):  # for each case
                        cases_q = {}
                        cases_q['case'] = "test_" + str(c + 1)
                        if isinstance(cases['input'][v][q][c][0], list):
                            cases_q['input'] = cases['input'][v][q][c][0]
                        else:
                            cases_q['input'] = cases['input'][v][q][c]

                        if isinstance(cases['output'][v][q][c][0], list):
                            cases_q['output'] = cases['output'][v][q][c][0]
                        else:
                            cases_q['output'] = cases['output'][v][q][c]

                        question['cases'].append(cases_q)

                variant['questions'].append(question)

            formatCases['variations'].append(variant)

        with open(file, "w") as out:
            json.dump(formatCases, out, indent=2)

        return file

    @staticmethod
    def format_cases_lixo(cases, file):  # _version1
        # file = file.replace(' ', '').replace('/', '-').replace(':', '-')
        # files = ['./tmp/' + file + "_linker.json"]
        # files = [BASE_DIR + '/linker.json']
        files = [file]
        formatCases = {}
        formatCases['variations'] = []  # variant/models

        for i, v in enumerate(cases['id']):  # for each variant/model
            variant = {}
            variant['variant'] = str(i + 1)
            variant['questions'] = []
            count_q = 0
            qvi = cases['input'][0][i]
            qvo = cases['output'][0][i]
            for q in range(len(qv[v])):  # for each question
                count_q += 1
                question = {}
                question['key'] = str(cases['id'][0][v])
                question['number'] = str(count_q)
                question['file'] = 'Q' + str(count_q)
                try:
                    questionObject = get_object_or_404(Question, pk=question['key'])
                    question['weight'] = questionObject.question_difficulty
                except:
                    question['weight'] = '1'
                question['language'] = ['all']
                question['cases'] = []

                qvi = cases['input'][0][v]
                qvo = cases['output'][0][v]
                for c in range(len(qvi)):
                    cases_q = {}
                    cases_q['case'] = "test_" + str(c + 1)
                    cases_q['input'] = qvi[c]
                    cases_q['output'] = qvo[c]
                    question['cases'].append(cases_q)

                variant['questions'].append(question)

            formatCases['variations'].append(variant)

        with open(files[0], "w") as out:
            json.dump(formatCases, out, indent=2)

        return files

    @staticmethod
    def format_cases_version3(cases, file):  ###### LIXO
        file = file.replace(' ', '').replace('/', '-').replace(':', '-')
        files = ['./tmp/' + file + ".xml"]

        for m in range(len(cases['input'])):  # for each model
            st_f = './tmp/' + file + '-m' + str(m + 1) + ".cases"
            st = '<model=0>\n\n</model>\n\n'
            st += '<model=' + str(m + 1) + '>'

            q_str = []
            for q in range(len(cases['input'][m])):  # for each question
                st += '\n\n<question=' + str(cases['id'][m][q]) + '>'
                if isinstance(cases['input'][m][q], list):
                    for c in range(len(cases['input'][m][q])):  # for each case
                        st += '\n\ncase=test_' + str(c + 1)
                        st += '\ninput='
                        if isinstance(cases['input'][m][q][c], list):
                            st += ' '.join([str(n) for n in cases['input'][m][q][c]]) + ' '
                        else:
                            st += str(cases['input'][m][q][c]) + ' '

                        st += '\noutput='
                        if isinstance(cases['output'][m][q][c], list):
                            st += ' '.join([str(n) for n in cases['output'][m][q][c]]) + ' '
                        else:
                            st += str(cases['output'][m][q][c]) + ' '
                else:
                    st += '\n\ncase=test_' + str(c + 1)
                    st += '\ninput='
                    st += str(cases['input'][m][q]) + ' '

                    if isinstance(cases['output'][m][q], list):
                        for c in range(len(cases['output'][m][q])):  # for each case
                            st += '\noutput='
                            if isinstance(cases['output'][m][q][c], list):
                                st += ' '.join([str(n) for n in cases['output'][m][q][c]]) + ' '
                            else:
                                st += str(cases['output'][m][q][c]) + ' '
                    else:
                        st += '\noutput='
                        st += str(cases['output'][m][q]) + ' '

                st += '\n\n<question>'
            st += '\n\n</model>\n\n'

            f = open(st_f, "w")
            f.write(str(st))
            f.close()
            files.append(st_f)

        st_geral = '<questions>\n'
        for q in range(len(cases['id'][0])):
            st_geral += '<quest=' + str(cases['id'][0][q]) + '/>\n'
            st_geral += '<weight=1/>\n'
            st_geral += '<language>all</language>\n'
            st_geral += '</quest>\n'
        st_geral += '</questions>\n\n'

        st_geral += '<models>\n'
        for en, st in enumerate(files[1:]):
            st_geral += '<model=' + str(en + 1) + '>\n'
            st_geral += '<file=' + st + '/>\n'
            for q in cases['id'][en]:
                st_geral += '<question=' + q + '/>\n'
            st_geral += '</model>\n'
        st_geral += '</models>\n'

        f = open(str(files[0]), "w")
        f.write(str(st_geral))
        f.close()

        return files

    @staticmethod
    def format_cases_version2(cases, file):  ##### LIXO
        file = file.replace(' ', '').replace('/', '-').replace(':', '-')
        st = '<model=0>\n\n</model>\n\n'
        str_q = []

        for q in range(len(cases['id'][0])):  # for each question
            str_q.append(st)

        for q in range(len(cases['id'][0])):  # for each question
            for m in range(len(cases['id'])):  # for each model
                str_q[q] = str_q[q] + '\n\n<model=' + str(m + 1) + '>'
                if isinstance(cases['input'][m][q], list):
                    for c in range(len(cases['input'][m][q])):  # for each case
                        str_q[q] = str_q[q] + '\n\ncase=test_' + str(c + 1)
                        str_q[q] = str_q[q] + '\ninput='
                        if isinstance(cases['input'][m][q][c], list):
                            str_q[q] = str_q[q] + ' '.join([str(n) for n in cases['input'][m][q][c]]) + ' '
                        else:
                            str_q[q] = str_q[q] + str(cases['input'][m][q][c]) + ' '

                        str_q[q] = str_q[q] + '\noutput='
                        if isinstance(cases['output'][m][q][c], list):
                            str_q[q] = str_q[q] + ' '.join([str(n) for n in cases['output'][m][q][c]]) + ' '
                        else:
                            str_q[q] = str_q[q] + str(cases['output'][m][q][c]) + ' '
                else:
                    str_q[q] = str_q[q] + '\n\ncase=test_' + str(c + 1)
                    str_q[q] = str_q[q] + '\ninput='
                    str_q[q] = str_q[q] + str(cases['input'][m][q]) + ' '

                    if isinstance(cases['output'][m][q], list):
                        for c in range(len(cases['output'][m][q])):  # for each case
                            str_q[q] = str_q[q] + '\noutput='
                            if isinstance(cases['output'][m][q][c], list):
                                str_q[q] = str_q[q] + ' '.join([str(n) for n in cases['output'][m][q][c]]) + ' '
                            else:
                                str_q[q] = str_q[q] + str(cases['output'][m][q][c]) + ' '
                    else:
                        str_q[q] = str_q[q] + '\noutput='
                        str_q[q] = str_q[q] + str(cases['output'][m][q]) + ' '

                str_q[q] = str_q[q] + '\n\n</model>\n\n'

        files = ['./tmp/' + file + ".xml"]
        st_geral = ''
        for q in range(len(cases['id'][0])):
            st = './tmp/' + file + '-' + str(cases['id'][0][q]) + ".cases"
            st_geral += '<quest=' + str(q + 1) + '>\n'
            st_geral += '<file=' + st + '/>\n'
            st_geral += '<number=' + str(cases['id'][0][q]) + '/>\n'
            st_geral += '<weight=1/>\n'
            st_geral += '<language>all</language>\n'
            st_geral += '</quest>\n\n'
            files.append(st)
            f = open(st, "w")
            f.write(str(str_q[q]))
            f.close()

        f = open(str(files[0]), "w")
        f.write(str(st_geral))
        f.close()

        return files

    ####################### HASH
    # author: Heitor
    # hash only first and last name
    @staticmethod
    def distro_table(nome):  # version H
        try:
            nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode('ascii').split()
            nome = nome[0] + nome[-1]
            D = {}
            for c in string.ascii_lowercase:
                D[c] = string.ascii_lowercase.find(c) + 1
            for c in string.ascii_uppercase:
                D[c] = string.ascii_uppercase.find(c) + 1

            hash_base_B = 0  # Equivalente ao calculo da versão B
            hash_base_C = 0  # Equivalente ao calculo da versão C

            for c in nome:
                hash_base_B *= 100
                hash_base_B += D[c]
                hash_base_C += int(len(string.ascii_lowercase) ** D[c])

            hash_base_E = hash_base_B  # Equivalente ao calculo da versão D
            hash_base_D = hash_base_C  # Equivalente ao calculo da versão E
            hash_base_C %= int(1e10)

            hash_base_B **= len(string.ascii_lowercase)
            hash_base_E **= len(string.ascii_lowercase)

            for c in nome:
                hash_base_E += int(len(string.ascii_lowercase) ** D[c])

            while hash_base_B > int(1e10):
                a = hash_base_B % int(1e10)
                hash_base_B //= int(1e10)
                hash_base_B += a

            while hash_base_D > int(1e10):
                a = hash_base_D % int(1e10)
                hash_base_D //= int(1e10)
                hash_base_D += a

            while hash_base_E > int(1e10):
                a = hash_base_E % int(1e10)
                hash_base_E //= int(1e10)
                hash_base_E += a
        except:
            return -1

        return (hash_base_B + hash_base_C + hash_base_D + 5 * hash_base_E) // 8

    @staticmethod
    def defineQRcode(exam, room, idStudent):
        str1 = ''
        # if (exam.exam_print in ['ques','answ','both']):
        mill = str(int(round(time.time() * 1000)))
        str1 += str(exam.exam_hour)[2:10].replace("-", "") + '-' + mill + ';'  # 0 - marcador/data
        try:
            room_id = room.id
        except:
            room_id = 0

        str1 += str(room_id) + ';'  # 1 = id turma
        str1 += str(exam.id) + ';'  # 2 = id exame
        str1 += str(idStudent) + ';'  # 3 = id aluno
        i = 0
        for ex in exam.exam_term_choice:
            if ex[0] == exam.exam_term:
                break
            i += 1
        str1 += str(i) + ';'  # 4 = id turno/quadrimestre

        if exam.exam_print in ['answ', 'both']:
            i = 0
            for ex in exam.exam_stylesheet_choice:  # vert/horiz
                if ex[0] == exam.exam_stylesheet:
                    break
                i += 1
            str1 += str(i) + ';'  # 5 = 0-vertical ou 1-horizontal
            str1 += exam.exam_number_of_questions_var1 + ';'  # 6  = numero de questões dificuldade 1
            str1 += exam.exam_number_of_questions_var2 + ';'  # 7  = numero de questões dificuldade 2
            str1 += exam.exam_number_of_questions_var3 + ';'  # 8  = numero de questões dificuldade 3
            str1 += exam.exam_number_of_questions_var4 + ';'  # 9  = numero de questões dificuldade 4
            str1 += exam.exam_number_of_questions_var5 + ';'  # 10 = numero de questões dificuldade 5
            str1 += exam.exam_number_of_questions_text + ';'  # 11 = numero de questões dissertativas
            str1 += exam.exam_number_of_anwsers_question + ';'  # 12 = quantidade de alternativas/respostas

        if exam.exam_print == 'ques':
            str1 += exam.exam_number_of_questions_text + ';'  # 13 = REMOVER ISSO POIS JÁ ESTÁ EM 11 #################

        qrfile = './tmp/QRCode_' + str(room_id) + '_' + str(exam.id) + '_' + str(idStudent) + '.eps'
        # print('$$$$$ QR0=',[qrfile,str1])
        return ([qrfile, str1])

    @staticmethod
    def genTex(fileName, myPath):
        file_name = fileName[:-4]

        cmd = ['pdflatex', '--shell-escape', '-interaction', 'nonstopmode', fileName]
        try:
            proc = subprocess.Popen(cmd)
            proc.communicate()

            path = os.getcwd()
            os.system("cp " + file_name + ".pdf " + path + "/" + myPath + "/")
            os.system("cp " + file_name + ".tex " + path + "/" + myPath + "/")
        except Exception as e:
            return 0

        try:
            os.remove("{}.aux".format(file_name))
            os.remove("{}.log".format(file_name))
            os.remove("{}.tex".format(file_name))
            os.remove("{}.pdf".format(file_name))
            os.remove("{}.out".format(file_name))
            os.remove("temp.txt")
            pass
        except Exception as e:
            pass

        return 1

    @staticmethod
    def getBegin():
        with open('./latex/latex_begin.txt', 'r') as latex_begin:
            str = latex_begin.read()
        return str

    @staticmethod
    def drawCircles():
        str1 = '''
% drawCircles
\\vspace{-5mm}
\\leavevmode\\put(-11,0){\\color{black}\\circle*{15}}\\hspace{-0mm}
\\leavevmode\\put(509,0){\\color{black}\\circle*{15}}
        '''
        return str1

    @staticmethod
    def drawInstructions(exam):
        str1 = '\n\n'
        if (exam.exam_instructions != ""):
            inst = _("Instructions")
            str1 = "\n%drawInstructions\n"
            str1 = str1 + '\\vspace{3mm}\\noindent{\\small\\textbf{%s:}\\vspace{-1mm}' % inst
            str1 = str1 + '''
\\begin{enumerate}[label=(\\alph*)]\n\\itemsep0pt\\parskip0pt\\parsep0pt
_inst1_
\\end{enumerate}}\\normalsize\n
            '''
            str1 = str1.replace("_inst1_", exam.exam_instructions)
        return str1

    @staticmethod
    def drawJumpPage():
        str1 = "\\makeatletter\\renewcommand*\\cleardoublepage{\\ifodd\\c@page \\else\\hbox{}\\newpage\\fi}\n"
        str1 += "\\makeatother\n"
        str1 += "\\cleardoublepage\n"
        str1 += "\\newpage\n"
        return str1

    @staticmethod
    def getHeader(request, exam, room, idStudent, nameStudent, myqr, data_hora):  # define o cabeçalho de cada página
        inst = []
        logo = ''
        for course in room.discipline.courses.all():
            for i in course.institutes.all():
                inst.append(i.institute_name)
                logo = i.institute_logo
                instURL = i.institute_url

        institute = ','.join(inst)
        discipline = room.discipline.discipline_name
        course = "\\textbf{%s}" % ','.join([c.course_name for c in room.discipline.courses.all()])
        classroom = room.classroom_code

        prof = []
        for p in room.classroom_profs.all().order_by('username'):
            prof.append(p.first_name + " " + p.last_name)
        prof = ', '.join(prof)

        disc = "\\textbf{%s:} %s \\hfill" % (_("Discipline"), discipline)
        turma = "\\textbf{%s:} %s\n" % (_("Classroom"), classroom)
        room_str = "\\textbf{%s:} %s\n" % (_("Room"), room.classroom_room)
        # ass = "\\noindent\\textbf{%s:}\\rule{11.15cm}{0.1pt}\\hspace{1cm}\n" % _("Sig.")
        instrucoes = "%s:" % _("Instructions")
        teachers = "%s:" % _("Prof.")
        period = "%s:" % _("Term")
        modality = "%s:" % _("Exam")
        date = "%s:" % _("Date")

        idStudent_str = "\\textbf{\\small{%s:}} %s" % (_("ID/RA"), "_idStudent_")
        nameStudent_str = "\\textbf{\\small{%s:}} %s" % (_("Student"), "_nameStudent_")

        quad = "vazio"
        for i in exam.exam_term_choice:
            if i[0] == exam.exam_term:
                quad = i[1]

        size_qr = 5.65  # 4.5 # 3.9  # 3.3
        if exam.exam_print in ['both'] and Utils.validateNumQuestions(request, exam) > 10:
            size_qr += Utils.validateNumQuestions(request, exam) / 15

        # header da página 1/2
        str1 = "\\vspace{-1mm}\\hspace{5mm}"
        str1 += "\\begin{table}[h]\n"
        str1 += "\\begin{tabular}{|l|p{%scm}|c}\n \\cline{1-2}" % (str(16.5 - size_qr))
        # str1+="\\cline{1-1} \\cline{3-3}\n"
        str1 += "\\multirow{7}{*}{\\vspace{8mm}\\includegraphics[width=2cm]{./figs/%s}} \n" % logo
        str1 += "&\\textbf{%s} \n              " % (institute)
        str1 += "&\\multirow{7}{*}[2.5mm]{\\hspace{-2mm}\\includegraphics[scale=%s]{%s}}\\\\ \n" % (
            size_qr / 3, myqr[0])

        str1 += "&%s                        & \\\\ \n" % (course)
        str1 += "&%s                        & \\\\ \n" % (disc)

        if len(prof):
            str1 += "&\\textbf{%s} %s   & \\\\ \n" % (teachers, prof)  # prof
            str1 += "&%s \\hfill %s  & \\\\ \n" % (turma, room_str)
        else:
            str1 += "&%s \\hfill %s   & \\\\ \n" % (turma, room_str)

            # str1+="&\\textbf{%s} %s\\hfill \\textbf{%s} %s \\hfill " % (period,quad,modality,exam.exam_name)
        str1 += "&\\textbf{%s} %s \\hfill " % (modality, exam.exam_name)
        str1 += "\\textbf{%s} %s           & \\\\ \n \\cline{1-2}" % (date, exam.exam_hour.strftime("%d-%m-%Y"))

        str1 += "\\multicolumn{2}{|l|}{}      & \\\\ \n"
        str1 += "\\multicolumn{2}{|l|}{\\textbf{%s: }\\rule{5cm}{0.1pt}} & \\\\ \n " % _("Sig.")
        str1 += "\\multicolumn{2}{|l|}{%s \\hfill %s}           & \\\\ \n \\cline{1-2}" % (
            nameStudent_str, idStudent_str)
        str1 += "\\end{tabular}\n"
        str1 += "\\end{table}\n"

        str1 += "\\footnote[2]{\\vspace{10mm}\color{lightgray}\\textbf{MCTest:} gerador e corretor de exames disponível para professores - \\textbf{\\url{%s}}}\n\n" % (
            instURL)

        try:
            str1 += '\n\n \\vspace{-7mm}\\hfill {\\tiny {\\color{red}\#E' + str(
                exam.id) + '\#V' + str(exam.variationsExams2.all()[0].id) + ' - ' + data_hora + '\\hspace{55mm}}}\n\n'
        except:
            str1 += '\n\n \\vspace{-7mm}\\hfill {\\tiny {\\color{red}\#E' + str(
                exam.id) + ' - ' + data_hora + '\\hspace{55mm}}}\n\n'

        str1 += '\\vspace{0.4mm}'
        if exam.exam_print == 'both':
            str1 += "\\vspace{%smm}\n\n" % (int(Utils.getNumMCQuestions(exam)) / 2)
        else:
            str1 += "\\vspace{4mm}\n\n"

        return str1.replace("_nameStudent_", nameStudent).replace("_idStudent_", idStudent)

    @staticmethod
    def drawSignatureQR(exam, room, idStudent, nameStudent):
        idStudent_str = "\\textbf{\\small{%s:}} %s\n" % (_("ID/RA"), idStudent)
        nameStudent_str = "\\textbf{\\small{%s:}} %s\n" % (_("Student"), nameStudent)

        str1 = "\\vspace{-4mm}\n"
        str1 += "\\hspace{5mm}%s {%s} " % (nameStudent_str, idStudent_str)
        # str1  = "\\vspace{-4mm}\\begin{table}[h]\n"
        # str1 += "\\begin{tabular}{p{11.7cm}p{2.5cm}r}\n"
        # str1 += "\\hspace{5mm}%s & \\multicolumn{1}{l}{%s} " % (nameStudent_str, idStudent_str)
        # str1 += "  & \\multirow{4}{*}{\\includegraphics[width=2.8cm\\linewidth]{_qrfile_}}} \\\\ \n"
        # str1 += "  &                         &     \\\\ \n"
        # str1 += "  &                         &     \\\\ \n"
        # str1 += "\\vspace{-8mm}\\hspace{5mm}\\textbf{%s: }\\rule{11.15cm}{0.1pt} \\hspace{-5cm} &  & \n" %_("Sig.")
        # str1 += "\\end{tabular}\n"
        # str1 += "\\end{table}\n"

        return str1

    @staticmethod
    def validateNumQuestions(request, exam):
        numQT = numQM = 0
        if exam.exam_print in ['answ']:
            return True

        for q in exam.questions.all():
            if q.question_type == 'QT':
                numQT += 1
            else:
                numQM += 1

        if (numQM < int(Utils.getNumMCQuestions(exam))):
            messages.error(request,
                           _('validateNumQuestions: The number of selected multiple-choice questions is inconsistent') +
                           str(numQM))
            return False
        if (numQT < int(exam.exam_number_of_questions_text)):
            messages.error(request, _('validateNumQuestions: the number of Text questions is inconsistent'))
            return False
        if exam.exam_print == 'both':
            if int(Utils.getNumMCQuestions(exam)) < 3:
                messages.error(request,
                               _('validateNumQuestions: You chose Both. Is it right? Number of QM questions >=3'))
                return False
        if exam.exam_print == 'answ':
            if int(Utils.getNumMCQuestions(exam)) < 3:
                messages.error(request,
                               _('validateNumQuestions: You chose Anwsers. Is it right? Number of QM questions >=3'))
                return False
        if exam.exam_print == 'ques':
            if int(exam.exam_number_of_questions_text) < 1:
                messages.error(request,
                               _('validateNumQuestions: You chose Questions. Is it right? Number of QM questions >=3'))
                return False

                # PROBLEMAS COM QUESTOES PARAMETRICAS
        # if (numQM < int(exam.exam_max_questions_square)):
        #    return HttpResponse("ERROR: number of Multiple Choice questions per block is inconsistent"+
        #           exam.exam_max_questions_square, numQT)

        for i in range(1, 6):
            t = len(exam.questions.filter(question_type='QM').filter(question_difficulty=str(i)))
            if (i == 1 and t < int(exam.exam_number_of_questions_var1)):
                messages.error(request, _('validateNumQuestions: number of QM difficulty questions var1'))
                return False
            if (i == 2 and t < int(exam.exam_number_of_questions_var2)):
                messages.error(request, _('validateNumQuestions: number of QM difficulty questions var2'))
                return False
            if (i == 3 and t < int(exam.exam_number_of_questions_var3)):
                messages.error(request, _('validateNumQuestions: number of QM difficulty questions var3'))
                return False
            if (i == 4 and t < int(exam.exam_number_of_questions_var4)):
                messages.error(request, _('validateNumQuestions: number of QM difficulty questions var4'))
                return False
            if (i == 5 and t < int(exam.exam_number_of_questions_var5)):
                messages.error(request, _('validateNumQuestions: number of QM difficulty questions var5'))
                return False

        return True

    @staticmethod
    def getNumMCQuestions(exam):
        numQuestoes = int(exam.exam_number_of_questions_var1)
        numQuestoes += int(exam.exam_number_of_questions_var2)
        numQuestoes += int(exam.exam_number_of_questions_var3)
        numQuestoes += int(exam.exam_number_of_questions_var4)
        numQuestoes += int(exam.exam_number_of_questions_var5)
        return int(numQuestoes)

    @staticmethod
    def drawAnswerSheet(exam):
        letras_1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        numQT = int(exam.exam_number_of_questions_text)
        numQuestoes = 0
        if exam.exam_print in ['answ', 'both']:
            numQuestoes = Utils.getNumMCQuestions(exam)

        numRespostas = int(exam.exam_number_of_anwsers_question)
        maxQuestQuadro = int(exam.exam_max_questions_square)
        maxQuadrosHoz = int(exam.exam_max_squares_horizontal)
        str1 = ''

        if numQuestoes > 0:
            let = letras_1[0:numRespostas]
            strResps = (',').join([(let[x] + '/' + str(x + 1)) for x in range(len(let))])
            numQuadros = int(numQuestoes / maxQuestQuadro)  # questões por quadro
            numResto = numQuestoes % maxQuestQuadro

            if numResto:
                numQuadros += 1

                if numResto < 3:
                    return HttpResponse("ERROR: Each block must have at least 3 questions/answers")

            if numQuadros == 0:
                numQuadros += 1

            if numQuadros < numQuestoes / maxQuestQuadro:
                maxQuadrosHoz = int(numQuestoes / maxQuestQuadro)
            numQuadrosHoz = numQuadros
            if maxQuadrosHoz < numQuadros:
                numQuadrosHoz = maxQuadrosHoz
            numQuestoesQuadro = maxQuestQuadro
            if numQuestoes < maxQuestQuadro:
                numQuestoesQuadro = numQuestoes
            QL = 1
            if maxQuadrosHoz:
                QL = int(numQuadros / maxQuadrosHoz)
            if QL == 0:
                QL = 1
            QC = numQuadrosHoz
            if QC == 0:
                QC = 1

            if QL * QC * maxQuestQuadro < numQuestoes:
                QL += 1

            fimQuadro_ij = np.zeros([QL, QC])
            contadorQuestoes = 0
            for i in range(QL):
                for j in range(QC):
                    contadorQuestoes += numQuestoesQuadro
                    # fimQuadro_ij[i][j] = contadorQuestoes
                    if contadorQuestoes > numQuestoes:
                        break
                    fimQuadro_ij[i][j] = contadorQuestoes

            if numQuestoes < contadorQuestoes:
                for i in range(QC):
                    if fimQuadro_ij[QL - 1][i] == 0:
                        if numResto:
                            fimQuadro_ij[QL - 1][i] = numQuestoesQuadro * (numQuadros - 1) + numResto
                        else:
                            fimQuadro_ij[QL - 1][i] = numQuestoesQuadro * (numQuadros)

            numQuestEnd = 0
            numQuestStart = 1

            titl = ''
            # titl = _("ANSWER TABLE: Do not use this area as DRAFT!")
            str1 += "\\vspace{-6mm}\\begin{center}\\textbf{%s}\\end{center}\n" % titl

            ######## pagina de resposta - Parte 1 ##############
            if (exam.exam_stylesheet == 'Ver'):  ######################## apresentação VERTICAL dos quadros

                if (exam.exam_print in ['answ', 'both']):
                    str1 += "\\begin{center}\n"
                    for i in range(QL):  # para cada linha de quadros
                        str1 += "\n \\ \\ \n"
                        for j in range(QC):  # para cada coluna de quadros
                            numQuestEnd = int(fimQuadro_ij[i][j])
                            if numQuestStart == numQuestEnd + 1:
                                continue;
                            str1 += "\\begin{tikzpicture}[font=\\tiny]\n"
                            str1 += "  \\foreach \\letter/\\position in {%s} {\n" % strResps
                            str1 += "    \\node[inner sep=3pt] at ({\\position * 0.5},0) {\\letter};\n"
                            str1 += "  }\n"
                            str1 += "  \\foreach \\line in {%s,...,%s} {\n" % (numQuestStart, numQuestEnd)
                            str1 += "     \\begin{scope}[xshift=0cm,yshift=-(\\line-%s+1)*4mm]\n" % (numQuestStart)
                            str1 += "       \\foreach \\letter/\\position in {%s} {\n" % strResps
                            # str1+="           \\node[draw,fill,gray!80!white,inner sep=9pt] at (-0.5,0) {};\n"
                            str1 += "           \\node at (-0.1,0) {\\line};\n"
                            str1 += "           \\node[fill=black!100,draw,circle,inner sep=3pt] at ({\\position * 0.5},0) {};\n"
                            str1 += "           \\node[fill=white,draw,circle,inner sep=2pt] at ({\\position * 0.5},0) {};\n"
                            str1 += "       }\n"
                            str1 += "     \\end{scope}\n"
                            str1 += "  }\n"
                            str1 += "\\end{tikzpicture}\\hspace{%s cm}\n" % 1
                            numQuestStart = numQuestEnd + 1
                        str1 += "\n \\ \\ \n"
                    str1 += "\\end{center}\n"

            else:  ##################### apresentação HORIZONTAL dos quadros

                if (exam.exam_print in ['answ', 'both']):
                    str1 += "\\begin{center} \n"
                    for i in range(QL):  # para cada linha de quadros
                        str1 += "\n \\vspace{-2mm} \\ \n"
                        for j in range(QC):  # para cada coluna de quadros
                            numQuestEnd = int(fimQuadro_ij[i][j])
                            if numQuestStart == numQuestEnd + 1:
                                continue;
                            str1 += "\\begin{tikzpicture}[font=\\tiny,fill=black]\n"
                            # str1+="\\draw[fill=black] (0,0) rectangle (3mm,3mm); \n"
                            str1 += "  \\foreach \\numLab in {%s,...,%s} {\n" % (numQuestStart, numQuestEnd)
                            str1 += "    \\node[inner sep=3pt] at ({(\\numLab-%s+1) * 0.5},-0.1) {\\numLab};\n" % (
                                numQuestStart)
                            str1 += "  }\n"
                            str1 += "  \\foreach \\letter/\\line in {%s} {\n" % strResps
                            str1 += "     \\begin{scope}[xshift=0cm,yshift=-(\\line)*5mm]\n"
                            str1 += "       \\node at (0.1,0) {\\letter};\n"
                            str1 += "       \\foreach \\letter/\\position in {%s,...,%s} {\n" % (
                                1, (numQuestEnd - numQuestStart + 1))
                            str1 += "           \\draw[fill=gray] ({\\position * 0.5 - 0.2},-0.2) rectangle ({\\position * 0.5+0.2},0.2); \n"
                            # str1+="           \\node[fill=gray!100,draw,circle,inner sep=4.2pt] at ({\\position * 0.45},0) {};\n"
                            str1 += "           \\node[fill=white,draw,circle,inner sep=2.3pt] at ({\\position * 0.5},0) {};\n"
                            str1 += "       }\n"
                            str1 += "     \\end{scope}\n"
                            str1 += "  }\n"
                            str1 += "\\end{tikzpicture}\\hspace{%s mm}\n" % 1
                            numQuestStart = numQuestEnd + 1
                        str1 += "\n \\ \\ \n"
                    str1 += "\\end{center}\n"

        return str1

    @staticmethod
    def verifyNumQuestionsByDifficulty(exam, count, diff):
        # aceitar numero maximo de questoes por nivel de dificuldade (1 ate 5)                                                                
        if diff == '1':
            if (count >= int(exam.exam_number_of_questions_var1)):
                return False
            else:
                return True
        elif diff == '2':
            if (count >= int(exam.exam_number_of_questions_var2)):
                return False
            else:
                return True
        elif diff == '3':
            if (count >= int(exam.exam_number_of_questions_var3)):
                return False
            else:
                return True
        elif diff == '4':
            if (count >= int(exam.exam_number_of_questions_var4)):
                return False
            else:
                return True
        else:
            if (count >= int(exam.exam_number_of_questions_var5)):
                return False
            else:
                return True

    @staticmethod
    def drawQuestionsMCDifficulty(request, exam, count, diff, topics):
        db_questions = []

        qr_bytes = ''
        str1 = '\n\n% QUESTOES DE MULTIPLA ESCOLHA\n\n'
        ss1 = "\n\n\hspace{-15mm}{\\tiny {\\color{white}\\@%s}} \\hspace{0mm}"

        count_i = 0

        _group = []  # pegar apenas uma questão por grupo
        for q in exam.questions.filter(question_type='QM').filter(question_difficulty=diff).order_by('?'):
            if (count >= Utils.getNumMCQuestions(exam)):
                break

            if not q.topic in topics:
                messages.error(request,
                               _(
                                   "drawQuestionsMCDifficulty: Topic of the chosen question does not belong to the discipline"))
                return -1

            qg = q.question_group.replace(" ", "")
            flag_group = True
            if qg != "":
                if qg in _group:
                    flag_group = False
                else:
                    _group.append(qg)

            if flag_group:  # incluir apenas uma questao por grupo

                if Utils.verifyNumQuestionsByDifficulty(exam, count_i, diff):
                    count_i += 1
                else:
                    break

                count += 1
                if q.question_parametric == 'no':
                    quest = q.question_text
                    ans = []
                    for a in q.answers2.all():
                        ans.append(a.answer_text)

                    NUM_ans = q.answers2.all().count()

                else:  # QUESTOES PARAMETRICAS
                    try:
                        if q.question_type == "QM":
                            [quest, ans] = UtilsMC.questionParametric(q.question_text, q.answers())
                        else:  # se não for questao de multipla escolha entao nao pegar as alternativas
                            [quest, ans] = UtilsMC.questionParametric(q.question_text, [])
                    except:
                        messages.error(request, _('drawQuestionsMCDifficulty: Error in parametric question'))
                        return -1

                    NUM_ans = len(ans)

                # erro se nao tiver o mesmo numero de alternativas
                if NUM_ans != int(exam.exam_number_of_anwsers_question):
                    messages.error(request,
                                   _('drawQuestionsMCDifficulty: number of answers different: Exam; Question: ') +
                                   exam.exam_number_of_anwsers_question + '; ' + str(NUM_ans) + '; ' + str(q.id).zfill(
                                       3))
                    return -1

                ss = ss1 % str(q.id).zfill(4)
                str1 += "%s %s. %s\\vspace{0mm}\n" % (ss, count, quest)  # q.question_text)
                str1 += "\n\\begin{oneparchoices}"
                stra = ''
                db_answers = []
                for a in random.sample(ans, len(ans)):
                    stra += str(ans.index(a))
                    db_answers.append([str(ans.index(a)), a])
                    if exam.exam_student_feedback:  # se enviar pdf ao aluno, retira gabarito
                        str1 += "\n\n\\choice %s" % a
                    else:
                        if ans.index(a) == 0:
                            str1 += "\n\\choice \\hspace{-2.0mm}{\\tiny{\\color{white}\#%s}}%s" % (str(ans.index(a)), a)
                        else:
                            str1 += "\n\\choice \\hspace{-2.0mm}{\\tiny{\\color{white}#%s}}\\hspace{2.0mm}%s" % (
                                str(ans.index(a)), a)

                str1 += "\n\\end{oneparchoices}\\vspace{1mm}\n\n"

                db_questions.append(
                    [count, q.id, q.topic.topic_text, q.question_type, diff, q.question_short_description, quest,
                     db_answers])

                qr_bytes += str(q.id) + stra + ';'

        return ([str1, qr_bytes, count, db_questions])

    @staticmethod
    def drawQuestionsTDifficulty(request, exam, room, student_ID, student_name, countVariations, data_hora):
        qr_bytes = ''
        titl = _("Text Questions")
        strQT = '\n\n% QUESTOES DISSERTATIVAS\n\n'
        ss1 = "\n\n\hspace{-15mm}{\\tiny {\\color{white}\\@%s}} \\hspace{0mm}"

        # _group = []  # pegar apenas uma questão por grupo
        # for q in exam.questions.filter(question_type = 'QT').filter(question_difficulty=diff).order_by('?'):
        # for q in QT:
        # q = q[0]

        d = exam.variationsExams2.all()[countVariations]
        s = eval(d.variation)

        for var in s['variations']:
            for q in var['questions']:
                if q['type'] == 'QT':
                    ss = ss1 % str(q['key']).zfill(4)
                    if (exam.exam_print_eco == 'no'):

                        # criar um qrcode por questao dissertativa, por pagina, se nao for ecologico
                        myqr = Utils.defineQRcode(exam, room, student_ID)
                        myqr[0] = myqr[0][:-4] + '_q' + str(q['key']) + '.eps'
                        myqr[1] += str(q['key'])

                        # pip install bcrypt
                        # import bcrypt
                        # print (bcrypt.hashpw(b'teste123', bcrypt.gensalt()))
                        # print (bcrypt.hashpw(b'teste123', b'$2b$12$cRYX2M9V6glSp/ip/cmF2Or1nKSvnFZ19pBwSfTH4QKBc5rD7bEW2'))

                        s = str(myqr[1]).encode('utf-8')
                        # print("s>>>>>>>",s)
                        compressed = zlib.compress(s, 6)
                        sbeforeQR = binascii.hexlify(compressed)
                        # print("sbeforeQR",sbeforeQR)

                        # para testar
                        safterScan = binascii.unhexlify(sbeforeQR)
                        decompressed = zlib.decompress(safterScan)
                        if s != decompressed:
                            messages.error(request,
                                           _('drawQuestionsTDifficulty: Error in compression textual questions'))
                            return -1

                        # L, M, Q, or H; each level ==> 7, 15, 25, or 30 percent
                        qr = pyqrcode.create(sbeforeQR, error='M')  # myqr[1])
                        # gerar qr após sorteio das questoes/respostas
                        qr.eps(myqr[0])

                        strQT += Utils.drawCircles()
                        strQT += Utils.getHeader(request, exam, room, student_ID, student_name, myqr, data_hora)
                        strQT += Utils.drawCircles()
                        strQT += "\\vspace{-1mm}\n"
                        strQT += Utils.drawInstructions(exam)
                        strQT += "\\vspace{1mm}\\noindent\\textbf{%s:}\n\\\\" % titl

                    strQT += "%s %s. %s\\\\\n" % (ss, int(q['number']), q['text'])
                    qr_bytes += str(q['key']) + ';'
                    if (exam.exam_print_eco == 'no'):
                        strQT += Utils.drawJumpPage()

        return ([strQT, qr_bytes])

    @staticmethod
    def drawQuestionsTDifficultyVariations(request, exam, count, diff, topics):
        print("drawQuestionsTDifficultyVariations-00-" + str(datetime.datetime.now()))
        bd_qT = []  # pega questoes dissertativas
        _group = []  # pegar apenas uma questão por grupo
        for q in exam.questions.filter(question_type='QT').filter(question_difficulty=diff).order_by('?'):

            if not q.topic in topics:
                messages.error(request,
                               _('drawQuestionsTDifficultyVariations: Topic of the chosen question does not belong to '
                                 'the discipline'))
                return -1

            qg = q.question_group.replace(" ", "")
            flag_group = True
            if qg != "":
                if qg in _group:
                    flag_group = False
                else:
                    _group.append(qg)

            if flag_group:  # incluir apenas uma questao por grupo

                if (count >= int(exam.exam_number_of_questions_text)):  # +int(Utils.getNumMCQuestions(exam))):
                    break

                count += 1
                if q.question_parametric == 'no':
                    quest = q.question_text
                else:  # QUESTOES PARAMETRICAS
                    if q.question_type == "QM":
                        [quest, ans] = UtilsMC.questionParametric(q.question_text, q.answers())
                    else:  # se não for QM entao nao pegar as alternativas
                        [quest, ans] = UtilsMC.questionParametric(q.question_text, [])

                bd_qT.append(
                    [count, q.id, q.topic.topic_text, q.question_type, diff, q.question_short_description, quest])

        return (bd_qT)

    @staticmethod
    def validateProf(exam, user):
        profs = []  # pega todos os profs da disciplina
        if len(exam.classrooms.all()):
            for p in exam.classrooms.all()[0].discipline.discipline_profs.all():
                profs.append(p)
            for p in exam.classrooms.all()[0].discipline.discipline_coords.all():
                profs.append(p)

        if not user in profs:
            return HttpResponse("ERROR: The teacher is not registered in a Discipline (or in a classroom)")

    @staticmethod
    def validateProfByQuestion(question, user):
        profs = []  # pega todos os profs da disciplina
        for d in question.topic.discipline.all():
            for p in d.discipline_profs.all():
                profs.append(p)
            for p in d.discipline_coords.all():
                profs.append(p)
        if not user in profs:
            return HttpResponse("ERROR: The teacher is not registered in the Discipline (of the topic)")

    @staticmethod
    def getTopics(exam):
        topics = []  # pega todos os tópicos da disciplina
        for t in exam.classrooms.all()[0].discipline.topics2.all():
            topics.append(t)

        return topics

    # antes de criar um exame para cada aluno, crio variacoes de exames
    @staticmethod
    def drawQuestionsVariations(request, exam, user, topics):
        print("drawQuestionsVariations-00-" + str(datetime.datetime.now()))
        count = 0
        numMC = int(Utils.getNumMCQuestions(exam))
        db_questions = []
        db_questions.append([])
        if exam.exam_print in ['ques', 'both']:
            for i in range(1, 6):  # para cada nivel de dificultade de questao MC
                s = Utils.drawQuestionsMCDifficulty(request, exam, count, str(i), topics)
                try:
                    if s[3]:
                        count += len(s[3])
                        for qq in s[3]:
                            db_questions[0].append(qq)
                except:
                    pass
        count = 0  # contador diferente para QT
        if int(exam.exam_number_of_questions_text) and exam.exam_print in ['ques', 'both']:
            for i in range(1, 6):  # para cada nivel de dificultade de questao textual/dissertativa
                s = Utils.drawQuestionsTDifficultyVariations(request, exam, count, str(i), topics)
                count += len(s)
                for q in s:
                    q[0] += numMC
                    db_questions.append([q, q.append([])])

                if count >= int(exam.exam_number_of_questions_text):
                    break

        return db_questions

    @staticmethod
    def drawQuestions(request, myqr, exam, room, student_ID, student_name, countVariations, data_hora):
        count = 0

        try:
            str1 = Utils.getstr_QM(exam, countVariations)  # incluir as questões QM
        except:
            return HttpResponse("drawQuestions:" + str(countVariations))

        # incluir as questoes QT
        if int(exam.exam_number_of_questions_text) and exam.exam_print in ['ques', 'both']:
            titl = _("Text Questions")
            if (exam.exam_print_eco == 'yes'):
                str1 += "\\\\\\vspace{2mm}\\noindent\\textbf{%s}  \\hfill {\\color{white} \\#v%s}} \\\n" % (
                    titl, str(countVariations))
            else:
                str1 += "\n\n\\newpage\n\n"

            s = Utils.drawQuestionsTDifficulty(request, exam, room, student_ID, student_name, countVariations,
                                               data_hora)
            str1 += s[0]
            count += 1

        ## chave hash
        if len(student_ID) >= 8:
            stud = student_ID[0:8].encode('utf-8')
        else:
            stud = student_ID.zfill(8).encode('utf-8')

        hashed = bcrypt.hashpw(stud, bcrypt.gensalt(6))
        id_hashed = hashed[7:]
        print("passou11", len(id_hashed), id_hashed, hashed)

        s = str(myqr[1]).encode('utf-8')  # qrcode and file name
        if not exam.exam_print in ['answ']:
            s_ALL = str(myqr[1] + myqr[2]).encode('utf-8')  # also answers into file
        else:
            s_ALL = str(myqr[1]).encode('utf-8')  # also answers into file

        # for compressed and cryptography
        compressed = zlib.compress(s, 6)
        compressed_ALL = zlib.compress(s_ALL, 6)
        sbeforeQR = binascii.hexlify(id_hashed + compressed)
        sbeforeQR_ALL = binascii.hexlify(id_hashed + compressed_ALL)

        # template of each exam is save on service mctest
        if exam.exam_print == 'both':
            fileGAB = 'tmpGAB/' + myqr[1] + '.txt'
            with open(fileGAB, 'w') as myfile:
                myfile = open(fileGAB, 'w')
                myfile.write(sbeforeQR_ALL.decode('utf-8'))
                myfile.close()

            # for test
            with open(fileGAB, 'r') as myfile:
                mysbeforeQR_ALL = myfile.read()
                myfile.close()

            # for test
            safterScanmy = binascii.unhexlify(mysbeforeQR_ALL)
            safterScan = binascii.unhexlify(sbeforeQR_ALL)
            if safterScanmy != safterScan:
                return HttpResponse("ERRO in safterScanmy != safterScan !!!!")
            un_hashed = safterScan[:53]
            safterScan = safterScan[53:]
            decompressed = zlib.decompress(safterScan)

            pre = '$2b$06$' + un_hashed.decode('utf-8')

            if hashed == bcrypt.hashpw(stud, pre.encode('utf-8')):
                print("passou19 = ok", pre)

            if s_ALL != decompressed:
                return HttpResponse("ERROR: in compression")

        # L, M, Q, or H; each level ==> 7, 15, 25, or 30 percent
        qr = pyqrcode.create(sbeforeQR, error='M')
        qr.eps(myqr[0])

        if (exam.exam_print_eco == 'yes'):
            str1 += "\n \ \ \\ \n \\newpage\n"

        return str1
