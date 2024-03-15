'''
=====================================================================
Copyright (C) 2018-2024 Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of MCTest 5.3.

Languages: Python, Django and many libraries described at
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
import requests
import math

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
from django.shortcuts import get_object_or_404, render

from topic.UtilsMCTest4 import UtilsMC
from topic.models import Question
from exam.models import VariationExam
from exam.models import Exam
from exam.models import StudentExam
from exam.models import StudentExamQuestion


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
    def getQRanswers(variations):
        qr_answers_all = []
        for v in variations:
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

    @staticmethod
    def getQRanswersbyVariation(qr, exam):
        # pega a variação que está no QRcode e o gabarito do bd em VariantExam
        if 'correct' in qr and not 'ERROR' in qr['correct']:  # se conseguiu ler o QRCode, pega a variação
            id_variante = int(qr['variations']) + int(qr['variant'])
            if id_variante > int(qr['variations']) + int(exam.exam_variations):  # não existe variant
                return qr
            try:
                variationsExam = get_object_or_404(VariationExam, pk=str(id_variante))
            except:
                qr['correct'] = 'ERROR'
                return qr

            qr_answers = []
            dbtext = []
            s = eval(variationsExam.variation)
            for var in s['variations']:
                for q in var['questions']:
                    if q['type'] == 'QM':
                        qr_ans = str(q['key'])
                        for a in q['answers']:
                            qr_ans += str(a['sort'])
                        qr_answers.append(qr_ans)
                    else:
                        dbtext.append(str(q['key']))

            qr['correct'] = qr_answers
            qr['dbtext'] = dbtext

        return qr

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
        # str1 = str1.replace('echo', 'e$$ $$cho')
        # str1 = str1.replace('val', 'v$$ $$al')
        # str1 = str1.replace('exec', 'e$$ $$xec')
        # str1 = str1.replace('python', 'p$$ $$ython')
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

    @staticmethod
    def createRequest_BD_Moodle(exam, path_to_file_VARIATIONS_DB):

        # Constantes
        MOODLE_URL = "http://localhost/moodle/webservice/rest/server.php"
        TOKEN = "1d6040a8333e399a7740442024e7eb2d"

        def fazer_solicitacao(payload, url):
            '''
            Função genérica para fazer uma solicitação POST para a URL fornecida com o payload fornecido.
            Retorna o conteúdo da resposta.
            '''
            payload['wstoken'] = TOKEN
            payload['moodlewsrestformat'] = 'json'

            response = requests.post(url, data=payload)
            return response.content

        def construir_payload(**kwargs):
            '''
            Função para construir um payload com base nos parâmetros fornecidos.
            Retorna o payload como um dicionário.
            '''
            payload = {}
            for key, value in kwargs.items():
                payload[key] = value
            return payload

        letras_1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        varia_gab_all, count_varia = [], 0
        for v in exam.variationsExams2.all():
            s = eval(v.variation)
            questions_DB = []
            count_varia += 1
            jsonDict = {}
            for var in s['variations']:
                for q in var['questions']:
                    jsonDict["nomeDoCurso"] = exam.clasrooms.all()[0].disciple.discipline_code
                    jsonDict["categoria"] = 'MCTest'
                    jsonDict["feedbackCorreto"] = "Sua resposta está correta."
                    jsonDict["feedbackParcialmenteCorreto"] = "Sua resposta está parcialmente correta."
                    jsonDict["feedbackIncorreto"] = "Sua resposta está incorreta."
                    jsonDict["nomeDaQuestao"] = str(q['topic']) + str(q['key'])
                    jsonDict["textoDaQuestao"] = Utils.convertWordsMoodle(q['text'])
                    questions_DB.append("#c:" + str(q['number']) + " #id:" + str(q['key']) + " #topic:" + str(
                        q['topic']) + " #type:" + str(str(q['type'])) + " #diff:" + str(q['weight']) + "\n")
                    questions_DB.append(Utils.convertWordsMoodle(q['text']))
                    if q['type'] == 'QM':  # QM
                        for k, a in enumerate(q['answers']):
                            jsonDict["alternativa" + letras_1[k]] = a['answer']
                            questions_DB.append(letras_1[int(a['answer'])] + ") " + Utils.convertWordsMoodle(a['text']))
                            if not int(a['sort']):
                                jsonDict["fracaoA" + letras_1[k]] = "1.0"
                            else:
                                jsonDict["fracaoA" + letras_1[k]] = "0.0"
                    # else:  # QT with
                    #    if len(q['answers']) == 1:
                    #        questions_DB.append('ANSWER: ' + q['answers'][0]['text'] + '\n\n')

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
    def createFile_Tex(request, exam, path_to_file_VARIATIONS_DB, data_hora, font_size=11):
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
                                                data_hora, font_size)
                if not Utils.drawAnswerSheet(request, exam):
                    return False
                else:
                    strQuestions += Utils.drawAnswerSheet(request, exam)
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
                                                    hash_num % int(exam.exam_variations), data_hora, font_size)

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
        return True

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
    def defineQRcode(exam, room, idStudent, strVarExam="", hash_num=""):
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

            # alteração em 15/11/2023
            str1 += strVarExam + ';'  # 13 = variations
            str1 += hash_num + ';'  # 14 = variation in variations

        if exam.exam_print == 'ques':
            str1 += exam.exam_number_of_questions_text + ';'  # 15

        qrfile = './tmp/QRCode_' + str(room_id) + '_' + str(exam.id) + '_' + str(idStudent) + '.eps'
        # print('$$$$$ QR0=',[qrfile,str1])
        return ([qrfile, str1])

    @staticmethod
    def genTex(fileName, myPath):
        file_name = fileName[:-4]

        cmd = ['pdflatex', '--shell-escape', '-interaction', 'nonstopmode', '--mem=5m', fileName]
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
    def getBegin(font_size="10"):
        with open('./latex/latex_begin.txt', 'r') as latex_begin:
            str = latex_begin.read()
        str = str.replace("10pt,brazil,a4paper", f'{font_size}pt,brazil,a4paper')
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
    def getHeader(request, exam, room, idStudent, nameStudent, myqr, data_hora,
                  font_size=11):  # define o cabeçalho de cada página
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

        # institute = Utils.format_size_text(institute, font_size)
        # discipline = Utils.format_size_text(discipline, font_size)
        # course = Utils.format_size_text(course, font_size)
        # classroom = Utils.format_size_text(classroom, font_size)
        # prof = Utils.format_size_text(prof, font_size)
        nameStudent = Utils.format_size_text(nameStudent, font_size)

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
    def format_size_text(text, font_size):
        if len(text) > 45:
            text = text[:45]
        if int(font_size) == 10:
            if len(text) > 35:
                text = '{\\small ' + text + '}'
        elif int(font_size) == 11:
            if len(text) > 35:
                text = '{\\small ' + text + '}'
            elif len(text) > 28:
                text = '{\\scriptsize ' + text + '}'
        elif int(font_size) == 12:
            if len(text) > 35:
                text = '{\\scriptsize ' + text + '}'
            elif len(text) > 28:
                text = '{\\tiny ' + text + '}'

        return text

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
    def drawAnswerSheet(request, exam):
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
                    # return HttpResponse("ERROR: The teacher is not registered in a Discipline (or in a classroom)")
                    messages.error(request, _("ERROR: Each block must have at least 3 questions/answers"))
                    return ''  # render(request, 'exam/exam_errors.html', {})
                    # return -1

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
                        str1 += "\n \\vspace{-5mm} \\ \\hspace{-7mm} \n"
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

                        if len(ans) < int(exam.exam_number_of_anwsers_question):
                            ans.append(a.answer_text)

                    NUM_ans = len(ans)  # q.answers2.all().count()

                else:  # QUESTOES PARAMETRICAS
                    try:
                        if q.question_type == "QM":
                            [quest, ans, feedback_ans] = UtilsMC.questionParametric(q.question_text, q.answers(), exam)
                        else:  # se não for questao de multipla escolha entao nao pegar as alternativas
                            [quest, ans, feedback_ans] = UtilsMC.questionParametric(q.question_text, [], exam)
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
                    try:
                        feed = feedback_ans[ans.index(a)]
                    except:  # quando cria alternativas automáticas, não tem feedback
                        feed = '\n'
                    if exam.exam_student_feedback:  # se enviar pdf ao aluno, retira gabarito
                        str1 += "\n\n\\choice %s" % a
                    else:
                        if ans.index(a) == 0:
                            str1 += "\n\\choice \\hspace{-2.0mm}{\\tiny{\\color{white}\#%s}}%s" % (str(ans.index(a)), a)
                        else:
                            str1 += "\n\\choice \\hspace{-2.0mm}{\\tiny{\\color{white}#%s}}\\hspace{2.0mm}%s" % (
                                str(ans.index(a)), a)

                        if feed != '\n':
                            str1 += '[' + feed + ']'  ############# NOVO

                    db_answers.append([str(ans.index(a)), a, feed])

                str1 += "\n\\end{oneparchoices}\\vspace{1mm}\n\n"

                db_questions.append(
                    [count, q.id, q.topic.topic_text, q.question_type, diff, q.question_short_description, quest,
                     db_answers])

                qr_bytes += str(q.id) + stra + ';'

        return ([str1, qr_bytes, count, db_questions])

    @staticmethod
    def drawQuestionsTDifficulty(request, exam, room, student_ID, student_name, countVariations, data_hora,
                                 strVarExam="", hash_num="", font_size=11):
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
                        myqr = Utils.defineQRcode(exam, room, student_ID, strVarExam, hash_num)
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
                        strQT += Utils.getHeader(request, exam, room, student_ID, student_name, myqr, data_hora,
                                                 font_size)
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
                        [quest, ans, feedback_ans] = UtilsMC.questionParametric(q.question_text, q.answers(), exam)
                    else:  # se não for QM entao nao pegar as alternativas
                        [quest, ans, feedback_ans] = UtilsMC.questionParametric(q.question_text, [], exam)

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
    def drawQuestions(request, myqr, exam, room, student_ID, student_name, countVariations, data_hora, font_size=11):
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
                                               data_hora, font_size)
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
        # sbeforeQR_ALL = binascii.hexlify(id_hashed + compressed_ALL)

        # L, M, Q, or H; each level ==> 7, 15, 25, or 30 percent
        qr = pyqrcode.create(sbeforeQR, error='M')
        qr.eps(myqr[0])

        if (exam.exam_print_eco == 'yes'):
            str1 += "\n \ \ \\ \n \\newpage\n"

        return str1

    @staticmethod
    def pl1_rasch_model(skill, difficulty):
        """Código desenvolvido por Lucas Montagnani Calil Elias para criar testes adaptativos com CAT,
        como Trabalho de Conclusão de Curso do Bacharelado em Ciência da Computação,
        da Universidade Federal do ABC, em 2023-2024"""
        # d = 1.702
        d = 1
        p = 1 / (1 + np.exp(-d * (skill - difficulty)))
        return p

    @staticmethod
    def ability_estimation(th, b, r):
        """Código desenvolvido por Lucas Montagnani Calil Elias para criar testes adaptativos com CAT,
        como Trabalho de Conclusão de Curso do Bacharelado em Ciência da Computação,
        da Universidade Federal do ABC, em 2023-2024"""
        if np.mean(r) == 1:
            # return max(b), 0, 0
            return np.log(2 * len(b)), 0, 0
        if np.sum(r) == 0:
            # return min(b), 0, 0
            return -np.log(2 * len(b)), 0, 0
        # Calcula a habilidade atualizada do aluno
        numerador = np.sum(r - Utils.pl1_rasch_model(th, b))
        denominador = np.sum(Utils.pl1_rasch_model(th, b) * (1 - Utils.pl1_rasch_model(th, b)))

        result = th + (numerador / denominador)
        adjustment = numerador / denominador
        # Calulcala o Standard Error
        se = 1 / np.sqrt(denominador)

        return result, se, adjustment

    @staticmethod
    def ability_estimation_aux(th, b, r):
        """Código desenvolvido por Lucas Montagnani Calil Elias para criar testes adaptativos com CAT,
        como Trabalho de Conclusão de Curso do Bacharelado em Ciência da Computação,
        da Universidade Federal do ABC, em 2023-2024"""
        adj = 1
        while (adj >= 0.05 or adj <= -0.05):
            th, se, adj = Utils.ability_estimation(th, b, r)
        # devolver a habilidade do aluno (theta) e o erro padrão do calculo
        return th  # , se

    @staticmethod
    def fisher_information(student_skill, question_difficulty):
        """Código desenvolvido por Lucas Montagnani Calil Elias para criar testes adaptativos com CAT,
        como Trabalho de Conclusão de Curso do Bacharelado em Ciência da Computação,
        da Universidade Federal do ABC, em 2023-2024"""
        d = 1.702
        p = Utils.pl1_rasch_model(student_skill, question_difficulty)
        q = 1 - p
        I = d ** 2 * p * q
        return I

    @staticmethod
    def item_selection(student_ability, question_topic, num_questions):
        """Código desenvolvido por Lucas Montagnani Calil Elias para criar testes adaptativos com CAT,
        como Trabalho de Conclusão de Curso do Bacharelado em Ciência da Computação,
        da Universidade Federal do ABC, em 2023-2024"""
        bloom_array = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']
        # Recupera todas as questões do topico escolhido na tela de Criar-PDF
        questions = Question.objects.filter(topic=question_topic)
        # Cria uma matriz para armazenar o ganho de informação de cada item
        fi_matrix = []
        # Itera sobre todas as questões
        for q in questions.all():
            # Valida se a questão já foi calibrada (se o parametro B do TRI é diferente de null)
            if (q.question_IRT_b_ability == -5.0):
                # Caso B sejá nulo realiza uma conversão da taxinomia de Bloom para a escala TRi (-2, 2)
                b_parameter = bloom_array.index(q.question_bloom_taxonomy) - 3.0
            else:
                b_parameter = q.question_IRT_b_ability
            # Calcula o ganho de informação com base no theta calculado anteriormente e na dificuldade de cada questão
            fi = Utils.fisher_information(student_ability, b_parameter)
            # Adiciona uma tupla (vetor binario) contendo respectivamente o id e o ganho de informação da questão na matriz
            fi_matrix.append([q.id, fi])
        # Ordena a matrix de forma decrescente com base no ganho de informação, ou seja, as questões com maior ganho ficam no topo
        ord_desc_mtx = sorted(fi_matrix, key=lambda x: x[1], reverse=True)
        # Seleciona as n (num_questions) questões com mais ganho de informação, sendo n a quantidade de questões requisitadas para o exame
        q_selected_ids = [row[0] for row in ord_desc_mtx[:num_questions]]
        return q_selected_ids

    @staticmethod
    def createAdaptativeTest(request, exam, choice_adaptive_test_number, path_to_file_ADAPTIVE_TEST, adaptive_test):
        bloom_array = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']

        # Inicializa um dicionário para armazenar as notas dos alunos para cada prova
        student_grades_by_exam = {}

        student_u_b_all_exams = {}

        # Inicializa um conjunto para armazenar todos os IDs de exames
        all_exam_ids = set()

        for room in exam.classrooms.all():  ############## PARA CADA TURMA

            # Encontre todos os exames já aplicadados na turma
            exams_with_same_room = Exam.objects.filter(classrooms__id=room.id)
            # exams_with_same_room = Exam.objects.filter(
            #     classrooms__id=room.id,
            #     exam_hour__date__lte=exam.exam_hour.date(),
            # )

            exams_aux = list(exams_with_same_room)  # Convert queryset to list

            exams_aux.remove(exam)  # remove o exame correte

            # Sort exams_aux by the 'exam_data' attribute
            exams_aux_sorted = sorted(exams_aux, key=lambda ex: ex.exam_hour)

            for exam0 in exams_aux_sorted:  ############ PARA CADA exam0

                if exam.exam_hour < exam0.exam_hour:  # descarta exames que ainda não foram aplicados
                    continue

                for s in room.students.all():  ### Laço para pegar a nota de cada aluno em exam0

                    # Encontre a nota do aluno s em exam0
                    student_exam0 = StudentExam.objects.filter(exam=exam0, student=s).first()

                    ################################################
                    # Adaptado de Lucas Montagnani Calil Elias - 2/2/2024

                    studExQt = StudentExamQuestion.objects.filter(studentExam=student_exam0)
                    # Cria vetores vazios para armazenar a dificuldade das questões respondidas (vetor b) e se o aluno acertou ou errou elas (vertor u)
                    b_vector, u_vector = [], []
                    # itera sobre todas as questões dos exames realizados anteriormente pelo aluno s (verifcar se não está pegando exames de disciplinas ou turmas anteriores)
                    for seq in studExQt.all():
                        # Recupera os dados da questão
                        question = Question.objects.filter(id=seq.question.id, question_type='QM').first()

                        # verifica se o aluno acertou a questão
                        ss = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                        correto = seq.answersOrder.index('0')
                        marcou = ss.index(seq.studentAnswer) if seq.studentAnswer in ss else -1
                        acertou = 1 if marcou == correto else 0

                        # Calcula o parâmetro b
                        b_parameter = 0

                        if adaptive_test == 'WPC':  # Weighted Percentage Correct
                            # O parâmetro b é calculado como a diferença entre 1 e a porcentagem ponderada de respostas corretas
                            if question.question_correction_count:
                                b_parameter = float(
                                    10 * (1 - question.question_correct_count / question.question_correction_count))
                            else:
                                b_parameter = float(bloom_array.index(question.question_bloom_taxonomy) + 1)
                        elif adaptive_test == 'CAT':  # Computerized Adaptive Testing
                            # O parâmetro b é a habilidade IRT da questão
                            # Valida se a questão já foi calibrada (se o parametro B do TRI é diferente de -5)
                            if (question.question_IRT_b_ability == -5.0):
                                b_parameter = bloom_array.index(question.question_bloom_taxonomy) - 2.0
                            else:
                                b_parameter = float(question.question_IRT_b_ability)
                        elif adaptive_test == 'SATB':  # Semi-Adaptive Testing by Bloom
                            # O parâmetro b é o índice da taxonomia de Bloom da questão entre 1 e 6
                            b_parameter = float(bloom_array.index(question.question_bloom_taxonomy) - 2.0)
                        # elif adaptive_test == "SATD": # Semi-Adaptive Testing by Difficulty
                        #    b_parameter = float(question.question_difficulty) # BUG: todas as variações são iguais

                        # Insere a dificuldade e se o estudante acertou ou erro nos respecitvos vetores em ordem
                        b_vector.append(b_parameter)
                        u_vector.append(acertou)

                    b_vector = np.array(b_vector)
                    u_vector = np.array(u_vector)
                    # Calcula a habilidade do estudante
                    if adaptive_test == 'CAT':
                        if np.any(u_vector) and np.any(b_vector):
                            grade = Utils.ability_estimation_aux(0, b_vector, u_vector)
                        else:
                            grade = -5.0

                        # Selected_questions = Utils.item_selection(student_ability, question_topic, num_questions)
                    else:
                        # Calcula a média da habilidade do estudante multiplicando elemento a elemento os vetores b_vector e u_vector
                        grade = np.dot(b_vector, u_vector) / len(b_vector)

                    # Inicialize um dicionário para o aluno atual, caso não exista
                    if s.id not in student_grades_by_exam:
                        student_grades_by_exam[s.id] = {
                            'room_id': room.id,
                            'room_code': room.classroom_code,
                            'name': s.student_name,
                            'email': s.student_email,
                            'grades': [],
                        }
                        student_u_b_all_exams[s.id] = {
                            'b_vector': [],
                            'u_vector': [],
                        }

                    # Adicione a nota à lista de notas para o aluno e a prova atuais
                    student_grades_by_exam[s.id]['grades'].append({
                        'exam_hour': exam0.exam_hour,
                        'exam_id': exam0.id,
                        'exam_name': exam0.exam_name,
                        'grade': grade,
                    })

                    student_u_b_all_exams[s.id]['b_vector'].extend(b_vector)
                    student_u_b_all_exams[s.id]['u_vector'].extend(u_vector)

                # Adicione o ID do exame ao conjunto
                all_exam_ids.add(exam0.id)

        # Calcule o número máximo de exames
        max_num_exams = len(all_exam_ids)

        # Create a CSV: 'RoomID', 'RoomCode', 'NameStudent', 'EmailStudent',
        # 'ExamID{i}', 'ExamDate{i}', 'ExamAbilities{i}', ...
        with open(path_to_file_ADAPTIVE_TEST, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')

            # Write header
            header_row = ['RoomID', 'RoomCode', 'NameStudent', 'EmailStudent']
            # Add exam information to the header
            for i, (exam_name, exam_data) in enumerate(student_grades_by_exam.items()):
                # header_row.append(f'ExamID{i}')  # Uncomment if needed
                # header_row.append(f'ExamDate{i}')  # Uncomment if needed
                for ex in exam_data['grades']:
                    header_row.append(f"{str(ex['exam_hour'])[:10]}:{ex['exam_id']}:{ex['exam_name']} ")
            # header_row.append('MeanPreviousAbilities')
            csv_writer.writerow(header_row)

            # exam_grade['exam_id'], str(exam_grade['exam_hour'])[:10],

            # Write data
            for student_id, student_data in student_grades_by_exam.items():
                row_data = [student_data['room_id'], student_data['room_code'], student_data['name'],
                            student_data['email']]

                # Lista para armazenar a soma das últimas X notas
                total_grades = []

                # Populate exam information for each exam
                for exam_grade in student_data['grades']:
                    # Make sure 'exam_id' is included in the dictionary, or use get method with a default value

                    if np.isinf(float(exam_grade['grade'])):  # não fez o exame
                        exam_grade['grade'] = -5

                    row_data.extend([exam_grade['grade']])

                    nota = float(exam_grade.get('grade'))
                    if math.isnan(nota):
                        nota = 0.0

                    total_grades.append(nota)

                # if len(total_grades) > int(choice_adaptive_test_number):
                #     mediaUltimos = np.mean(total_grades[-int(choice_adaptive_test_number):])
                # else:
                #     mediaUltimos = np.mean(total_grades)
                #
                # if maxStudentsClassesGrade < mediaUltimos:
                #     maxStudentsClassesGrade = mediaUltimos
                #
                # row_data.extend([float(mediaUltimos)])

                csv_writer.writerow(row_data)

        # limpeza do df
        import pandas as pd
        df = pd.read_csv(path_to_file_ADAPTIVE_TEST, delimiter=',')

        # Iterar pelas colunas do final para o começom removendo as vazias
        columns_to_remove = [col for col in reversed(df.columns) if df[col].isna().all()]
        for col in columns_to_remove:
            del df[col]

        # criar última coluna com a média das últimas X colunas ou ate a coluna StudentEmail
        X = int(choice_adaptive_test_number)
        num_cols = min(X, len(df.columns)) - 4
        if num_cols > 0:
            cols = df.columns[-num_cols:]
            cols1 = df.columns[:-num_cols]
            df['MeanPreviousAbilities'] = df[cols].replace(np.nan, 0).mean(axis=1)
        else:
            df = df.assign(MeanPreviousAbilities=0)

        # Ordenar última coluna
        df = df.sort_values(by='MeanPreviousAbilities')
        # Pega o valor máximo
        maxStudentsClassesGrade = df['MeanPreviousAbilities'].max()
        # Pega o valor mínimo
        minStudentsClassesGrade = df['MeanPreviousAbilities'].min()

        df.to_csv(path_to_file_ADAPTIVE_TEST, index=False, float_format='%.3f')

        return minStudentsClassesGrade, maxStudentsClassesGrade, student_u_b_all_exams

    @staticmethod
    def createCariantExam_rankin_sort(request, exam, path_to_file_ADAPTIVE_TEST_variations, adaptive_test):

        bloom_array = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']

        #####################################################
        ### definir peso das variações pelo método adaptativo
        variantExam_rankin = []
        for variationsExam in exam.variationsExams2.all():
            vars = eval(variationsExam.variation)
            sum_b = []
            for var in vars['variations']:
                for q in var['questions']:  # para cada questão

                    # pego a questão no BD para saber a porcentagem de acertos
                    qBD = get_object_or_404(Question, pk=str(q['key']))
                    aBD = []
                    for a in qBD.answers2.all():
                        aBD.append(a.id)

                    if q['type'] == 'QM':  #### ESCADA DE HABILIDADE FICA ENTRE -2 ATÉ 2, EM GERAL
                        if adaptive_test == "WPC":  # Weighted Percentage Correct
                            if qBD.question_correction_count:
                                sum_b.append(float(10 * (qBD.question_correct_count / qBD.question_correction_count)))
                            else:
                                sum_b.append(float(bloom_array.index(qBD.question_bloom_taxonomy)))
                        elif adaptive_test == 'CAT':  # Computerized Adaptive Testing
                            # Valida se a questão já foi calibrada (se o parametro B do TRI é diferente de -5)
                            if (qBD.question_IRT_b_ability == -5.0):
                                sum_b.append(float(bloom_array.index(qBD.question_bloom_taxonomy) - 2.0))
                            else:
                                sum_b.append(float(qBD.question_IRT_b_ability))

                        elif adaptive_test == "SATB":  # Semi-Adaptive Testing by Bloom
                            sum_b.append(float(bloom_array.index(qBD.question_bloom_taxonomy) - 2.0))

            # 0+0+0+0+5=5
            # 1+1+1+1+1=5
            # if not adaptive_test == "WPC":
            #     if max(sum_b) - min(sum_b) > 3:
            #         print(">>>>>>>***** ", *sum_b)
            #         continue
            # else:
            #     if max(sum_b) - min(sum_b) > 50:
            #         print(">>>>>>>***** ", *sum_b)
            #         continue

            valor = np.mean(sum_b)  # + len(sum_b) * np.std(sum_b) # penalidade com std alto

            # variantExam_rankin.append([vars['variations'][0]['variant'], variationsExam.id, valor, *sum_b, *aBD])
            variantExam_rankin.append([
                vars['variations'][0]['variant'],
                variationsExam.id,
                float(valor),
                float(np.std(sum_b)),
                *[float(element) for element in sum_b],  # Convert each element of sum_b to float
                *aBD
            ])

        # Convert the last columns to float
        # data = [[item[0], item[1], float(item[2])] for item in variantExam_rankin]

        # criando uma nova lista
        # data = variantExam_rankin

        # Sort the data by the converted last column
        variantExam_rankin_sort = np.array(sorted(variantExam_rankin, key=lambda x: x[2]))

        # Create a CSV writer
        with open(path_to_file_ADAPTIVE_TEST_variations, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')

            # Write header
            header_row = ['Variation', 'VariationID', 'MeanAbilities', 'STD']
            # Adicionar 'b1', 'b2', ... no início da lista
            header_row += [f'b{i}' for i in range(1, len(sum_b) + 1)]
            # Adicionar 'k1', 'k2', ... no início da lista
            header_row += [f'k{i}' for i in range(1, len(aBD) + 1)]
            csv_writer.writerow(header_row)

            for v in variantExam_rankin_sort:
                row = [
                    (format(float(val), '.3f') if '.' in val else val) if (
                            val and val.replace('.', '').replace('-', '').isdigit()) else val
                    for val in v
                ]
                csv_writer.writerow(row)

        return variantExam_rankin_sort

    @staticmethod
    def getHashVariationByCat(request, student_u_b_all_exams, variantExam_rankin_bloom_sort, id_student):
        """Código desenvolvido por Lucas Montagnani Calil Elias para criar testes adaptativos com CAT,
        como Trabalho de Conclusão de Curso do Bacharelado em Ciência da Computação,
        da Universidade Federal do ABC, em 2023-2024"""
        # Recupera os vetores de respostas e de paramêtros das questões respondidas pelo estudante
        # u, b, a, c = Utils.student_prev_questios_answers(exam, id_student)
        u = student_u_b_all_exams[id_student]['u_vector']
        b = student_u_b_all_exams[id_student]['b_vector']
        # Calcula a nota do estudante com a TRI do CAT
        nota_student = Utils.ability_estimation_aux(0, np.array(b), np.array(u))
        # Inicia variaveis auxiliares para seleção da melhor variação
        best_fi = -1.0
        best_variation = 0
        # Itera sobre cadas variação de variantExam_rankin_sort
        for variation in variantExam_rankin_bloom_sort:
            # Calcula FI daquela variação, passando como parâmetros a nota do estudante a difuculdade ("SumAbilities") da variação
            fi = Utils.fisher_information(float(nota_student), float(variation[2]))
            # Verifica se a FI desta variação é maior que a melhor até o momento
            if (fi > best_fi):
                # Caso seja maior, atuzaliza ela como a melhor e salva o identificador daquela variação
                best_fi = fi
                best_variation = variation[0]
        # Retorna o identificador da variação escolhida para aquele aluno, junto da nota do aluno
        return int(best_variation), nota_student

    @staticmethod
    def getHashAdaptative(request, exam, df, variantExam_rankin_bloom_sort, student_name, minStudentsClassesGrade,
                          maxStudentsClassesGrade):
        import pandas as pd

        # Filtre as linhas com 'NomeAluno' igual ao nome do aluno
        df_student = df[df['NameStudent'] == student_name]

        if df_student.shape[0] > 1:
            messages.error(request, _('ERROR - students with same name') + student_name)
            return render(request, 'exam/exam_errors.html', {})

        try:
            # Encontre o último elemento que não seja NaN
            vet_aux = df_student.values[0]
            # Encontrar índices onde o valor é diferente de NaN
            indices_nao_nan = np.where(pd.notna(vet_aux))[0]
        except:
            nota_student = 0
            indices_nao_nan = np.array([])

        # Verificar se há índices não nulos
        if indices_nao_nan.size > 0:
            # Obter o último índice diferente de NaN
            ultimo_indice = indices_nao_nan[-1]
            # Obter o último valor diferente de NaN
            nota_student = vet_aux[ultimo_indice]
        else:
            # Tratar caso não haja valores não nulos
            nota_student = 0

        # pegar max e min da coluna com SumPrevieusAbilities
        rmax = np.max(variantExam_rankin_bloom_sort[:, 2].astype(float))
        rmin = np.min(variantExam_rankin_bloom_sort[:, 2].astype(float))

        '''
        Se nota_student = minStudentsClassesGrade => nota_student_proportion = rmin
        Se nota_student = maxStudentsClassesGrade => nota_student_proportion = rmax
        Se minStudentsClassesGrade < nota_student < maxStudentsClassesGrade =>
        achar nota_student_proportion proporcional entre rmin e rmax
        '''
        nota_student_proportion = rmin
        if maxStudentsClassesGrade != minStudentsClassesGrade:
            # Calcular a proporção relativa
            nota_student_proportion = rmin + ((nota_student - minStudentsClassesGrade) / (
                        maxStudentsClassesGrade - minStudentsClassesGrade)) * (rmax - rmin)

        # Filtrar as linhas com valor igual a nota_student_porcent na coluna 2
        linhas_hash_num = []
        nota_aux = nota_student_proportion
        while not linhas_hash_num:
            linhas_hash_num = [linha for linha in variantExam_rankin_bloom_sort if
                               float(linha[2]) - 0.1 < nota_aux < float(linha[2]) + 0.1]
            nota_aux += 0.01
            if nota_aux > 10:  # pega uma variante aleatória
                linhas_hash_num = variantExam_rankin_bloom_sort
                break
        # Selecionar uma linha aleatória
        var_hash = int(random.choice(linhas_hash_num)[0]) % int(exam.exam_variations)

        return var_hash, nota_student
