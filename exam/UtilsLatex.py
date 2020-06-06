'''
=====================================================================
Copyright (C) 2019 Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of webMCTest 1.1 (or MCTest 5.1).

Languages: Python 3.7, Django 2.2.4 and many libraries described at
github.com/fzampirolli/mctest

You should cite some references included in vision.ufabc.edu.br:8000
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
import random
import re
import string
import subprocess
import time
import unicodedata
import zlib

import bcrypt
import numpy as np
import pyqrcode
from django.contrib import messages
from django.http import HttpResponse
# coding=UTF-8
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from mctest.settings import BASE_DIR
from topic.UtilsMCTest4 import UtilsMC
from topic.models import Question


class Utils(object):

    # create file DB with all variations
    @staticmethod
    def createFileDB_aiken(exam, db_questions_all, path_to_file_VARIATIONS_DB):
        letras_1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        varia_gab_all = []
        count_varia = 0
        start = '%%\{'
        end = '\}%%'
        for varia in db_questions_all:
            questions_DB = []
            count_varia += 1
            questions_QM = varia[0]
            q_count_QM = 0
            for q in questions_QM:
                q_count_QM += 1
                q_id = q[0]
                q_bd = get_object_or_404(Question, pk=q_id)
                questions_DB.append("#c:" + str(q_count_QM) + " #id:" + str(q_id) + " #topic:" + str(q_bd.topic.topic_text) + "\n")
                questions_DB.append(q[1])
                answers = q[2]
                c = correct = 0
                for a in answers:
                    questions_DB.append(letras_1[c] + ") " + a[1])
                    if not int(a[0]):
                        correct = c
                    c += 1
                questions_DB.append('ANSWER: ' + letras_1[correct] + '\n')

            questions_QT = varia[1:]
            for q in questions_QT:
                q_count = q_count_QM + int(q[0][0])
                q_id = q[0][1]
                q_text = str(q[0][2])
                q_bd = get_object_or_404(Question, pk=q_id)
                questions_DB.append("#c:" + str(q_count) + " #id:" + str(q_id) + " #topic:" + str(q_bd.topic.topic_text) + "\n")
                questions_DB.append(q_text)
                for answerCorrect in re.findall(start + '(\S+|\w+|.*)' + end, q_text):
                    questions_DB.append('ANSWER: ' + answerCorrect + '\n\n')

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

    # create file template of all variations in varia_gab_all
    @staticmethod
    def createFileTemplates(exam, listao, path_to_file_TEMPLATES):
        contVaria = 0
        letras_1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        varia_gab_header = ['variation']
        for i in range(int(Utils.getNumMCQuestions(exam)) + int(exam.exam_number_of_questions_text)):
            varia_gab_header.append('Q' + str(i + 1))
        varia_gab_all = [varia_gab_header]
        for varia in listao:
            qts = varia[0]
            contVaria += 1
            varia_gab = [str(contVaria - 1)]
            for q in qts.split(';'):
                if len(q):
                    q_str = q[-int(exam.exam_number_of_anwsers_question):]
                    q_ind = q_str.find('0')
                    varia_gab.append(letras_1[q_ind])

            for qt in varia[2]:  # dissertation question: get correct answer for the template
                start = '%%\{'
                end = '\}%%'
                for answerCorrect in re.findall(start + '(\S+|\w+|.*)' + end, qt[2]):
                    varia_gab.append(answerCorrect)

            if varia_gab:
                varia_gab_all.append(varia_gab)

        if varia_gab_all:
            with open(path_to_file_TEMPLATES, 'w') as data:
                writer = csv.writer(data)
                for varia in varia_gab_all:
                    writer.writerow(varia)

    # return test case between begin{comment} and end{comment}
    @staticmethod
    def get_cases(listao):
        print("get_cases-00-" + str(datetime.datetime.now()))
        start_q = '\\color{white}\\\@'
        start = 'begin{comment}'
        end = 'end{comment}'
        cases = {}
        cases['id'] = []
        cases['input'] = []
        cases['output'] = []
        if str(listao).find(start) == -1:  # se nao tem vpl, aborta listao
            return cases
        print("get_cases-01-" + str(datetime.datetime.now()))
        for model in listao:
            for questions in model:
                if not str(questions):
                    continue
                aux_ids = []
                aux_in = []
                aux_ou = []
                for qq in questions:
                    st = str(qq)
                    try:
                        numQuestion = st.split(',')[1].replace(' ', '')
                    except:
                        numQuestion = 'ERRO:' + st
                    for case in re.findall(start + '(.+?)' + end, st):
                        case = str(case)
                        case = case[case.find("{"):len(case) - 4]
                        case = case.replace('\\\\', '\\')
                        case1 = json.loads(case)
                        aux_ids.append(numQuestion)
                        inp0 = []
                        for i in case1['input']:
                            inp0.append([i])
                        out0 = []
                        for i in case1['output']:
                            out0.append([i])
                        aux_in.append(inp0)
                        aux_ou.append(out0)
                cases['id'].append(aux_ids)
                cases['input'].append(aux_in)
                cases['output'].append(aux_ou)

        return cases

    # cases = {}   #                      quest1          quest2               quest1       quest2
    #              #            [mod1:[ [ [c1],[c2]  ],   [[c1]]     ], mod2:[ [[c1]]    ,  [[c2]]     ] ]
    # cases['id']    = np.array([     [     [id1]     ,    [id2]     ],      [  [id2]    ,   [id1]     ] ] )
    # cases['input'] = np.array([     [ [ [1], [2,3] ],  [[2, 2]]    ],      [ [[5, 5]   , [[6, 6]]    ] ] )
    # cases['output']= np.array([     [ [ [1,2], [3] ],  [[3, 4, 5]] ],      [ [[4, 5, 6], [[7, 8, 9]] ] ] )
    @staticmethod
    def format_cases(cases, file):  # _version1
        file = file.replace(' ', '').replace('/', '-').replace(':', '-')
        files = ['./tmp/' + file + ".json"]
        files = [BASE_DIR + '/linker.json']
        formatCases = {}
        formatCases['variations'] = []  # variant/models

        for v in range(len(cases['input'])):  # for each variant/model
            st_f = './tmp/' + file + '-m' + str(v + 1) + ".cases"
            variant = {}
            variant['variant'] = str(v + 1)
            variant['questions'] = []
            count_q = 0
            for q in range(len(cases['input'][v])):  # for each question
                count_q += 1
                question = {}
                question['key'] = str(cases['id'][v][q])
                question['number'] = str(count_q)
                question['file'] = 'Q' + str(count_q)
                try:
                    questionObject = get_object_or_404(Question, pk=question['number'])
                    question['weight'] = questionObject.question_difficulty
                except:
                    question['weight'] = '1'
                question['language'] = ['all']
                question['cases'] = []
                if isinstance(cases['input'][v][q], list):
                    for c in range(len(cases['input'][v][q])):  # for each case
                        cases_q = {}
                        cases_q['case'] = "test_" + str(c + 1)
                        cases_q['input'] = cases['input'][v][q][c]  ##################### AQUI
                        cases_q['output'] = cases['output'][v][q][c]
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
    def defineQRcode(exam, room, idStudent, nameStudent):
        str1 = ''
        # if (exam.exam_print in ['ques','answ','both']):
        mill = str(int(round(time.time() * 1000)))
        str1 += str(exam.exam_hour)[2:10].replace("-", "") + '-' + mill + ';'  # 0 - marcador/data
        str1 += str(room.id) + ';'  # 1 = id turma
        str1 += str(exam.id) + ';'  # 2 = id exame
        str1 += idStudent + ';'  # 3 = id aluno
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

        # qrfile = './tmp/QRCode_'+str(room.id)+'_'+exam.exam_name.replace(' ','')+'_'+str(idStudent)+'.eps'
        qrfile = './tmp/QRCode_' + str(room.id) + '_' + str(exam.id) + '_' + str(idStudent) + '.eps'
        # print('$$$$$ QR0=',[qrfile,str1])
        return ([qrfile, str1])

    @staticmethod
    def genTex(fileName, myPath):
        file_name = fileName[:-4]

        cmd = ['pdflatex', '--shell-escape', '-interaction', 'nonstopmode', fileName]
        proc = subprocess.Popen(cmd)
        proc.communicate()

        path = os.getcwd()
        os.system("cp " + file_name + ".pdf " + path + "/" + myPath + "/")

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

        str1 += "\\vspace{-4.4mm}\\hspace{-5mm}\\footnote[2]{\color{lightgray}\\textbf{MCTest:} gerador e corretor de exames disponível para professores - \\textbf{\\url{%s}}}\n\n" % (
            instURL)

        str1 += '\n\n \\hfill \\tiny{{\\color{red}\#' + str(exam.id) + ' - ' + data_hora + '\\hspace{48mm}}}\n\n'

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
                               _('validateNumQuestions: You chose Questions. Is it right? Number of QM questions >=2'))
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
                    _group += str(qg)

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

                db_questions.append([q.id, quest, db_answers])

                qr_bytes += str(q.id) + stra + ';'

        return ([str1, qr_bytes, count, db_questions])

    @staticmethod
    def drawQuestionsTDifficulty(request, QT, exam, room, student_ID, student_name, count, data_hora):
        qr_bytes = ''
        str1 = ''
        titl = _("Text Questions")
        ss1 = "\n\\hspace{-15mm}{\\tiny {\\color{white}\\@%s}} \\hspace{0mm}"

        _group = []  # pegar apenas uma questão por grupo
        # for q in exam.questions.filter(question_type = 'QT').filter(question_difficulty=diff).order_by('?'):
        for q in QT:

            # q = q[0]

            if len(q) != 3:
                messages.error(request, _('drawQuestionsTDifficulty: Error in QT question'))
                return -1

            count += 1

            ss = ss1 % str(q[1]).zfill(4)
            if (exam.exam_print_eco == 'no'):

                # criar um qrcode por questao dissertativa, por pagina, se nao for ecologico
                myqr = Utils.defineQRcode(exam, room, student_ID, student_name)
                myqr[0] = myqr[0][:-4] + '_q' + str(q[1]) + '.eps'
                myqr[1] += str(q[1])

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
                    messages.error(request, _('drawQuestionsTDifficulty: Error in compression textual questions'))
                    return -1

                # L, M, Q, or H; each level ==> 7, 15, 25, or 30 percent
                qr = pyqrcode.create(sbeforeQR, error='M')  # myqr[1])
                # gerar qr após sorteio das questoes/respostas
                qr.eps(myqr[0])

                str1 += Utils.drawCircles()
                str1 += Utils.getHeader(request, exam, room, student_ID, student_name, myqr, data_hora)
                str1 += Utils.drawCircles()
                str1 += "\\vspace{-1mm}\n"
                str1 += Utils.drawInstructions(exam)
                # str1+=Utils.drawSignatureQR(exam,room,student_ID,student_name).replace('_qrfile_',myqr[0])
                str1 += "\\vspace{1mm}\\textbf{%s:}\n\\\\" % titl

            str1 += "%s %s. %s\\\\\n" % (ss, count + int(Utils.getNumMCQuestions(exam)), q[2])
            qr_bytes += str(q[1]) + ';'
            if (exam.exam_print_eco == 'no'):
                str1 += Utils.drawJumpPage()

        return ([str1, qr_bytes])

    @staticmethod
    def drawQuestionsTDifficultyVariations(request, exam, count, diff, topics):
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
                    _group += str(qg)

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

                bd_qT.append([count, q.id, quest])

        return (bd_qT)

    @staticmethod
    def validateProf(exam, user):
        profs = []  # pega todos os profs da disciplina
        if len(exam.classrooms.all()):
            for p in exam.classrooms.all()[0].discipline.discipline_profs.all():
                profs.append(p)

        if not user in profs:
            return HttpResponse("ERROR: The teacher is not registered in a Discipline (or in a classroom)")

    @staticmethod
    def validateProfByQuestion(question, user):
        profs = []  # pega todos os profs da disciplina
        for d in question.topic.discipline.all():
            for p in d.discipline_profs.all():
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
        str1 = ''
        qr_answers = ''
        count = 0
        numMC = int(Utils.getNumMCQuestions(exam))
        db_questions = []
        if numMC and exam.exam_print in ['ques', 'both']:
            titl = _("Multiple Choice Questions")
            str1 += "\\\\\\vspace{2mm}\\hspace{-5mm}\\noindent\\textbf{%s:}\\vspace{2mm}\n" % titl
            for i in range(1, numMC + 1):  # para cada nivel de dificultade de questao MC
                s = Utils.drawQuestionsMCDifficulty(request, exam, count, str(i), topics)
                try:
                    str1 += s[0]
                    qr_answers += s[1]
                    count = int(s[2])
                    if s[3]:
                        db_questions.append(s[3])
                except:
                    pass

        count = 0  # contador diferente para QT
        QT = []
        if int(exam.exam_number_of_questions_text) and exam.exam_print in ['ques', 'both']:
            for i in range(1, 6):  # para cada nivel de dificultade de questao textual/dissertativa
                s = Utils.drawQuestionsTDifficultyVariations(request, exam, count, str(i), topics)
                count = len(s)
                for q in s:
                    QT.append(q)
                    db_questions.append([q, []])

                if int(exam.exam_number_of_questions_text) <= count:
                    break
        # print(QT)

        return [qr_answers, str1, QT, db_questions]

    @staticmethod
    def drawQuestions(request, exam_i, exam, room, student_ID, student_name, user, countVariations, data_hora):
        # random.seed(int(student_ID))
        str1 = ''
        count = 0

        myqr = Utils.defineQRcode(exam, room, student_ID, student_name)
        numMC = int(Utils.getNumMCQuestions(exam))

        try:
            str1 += exam_i[1]  # incluir as questões QM
        except:
            return HttpResponse("drawQuestions:" + str(exam_i))

        # incluir as questoes QT
        if int(exam.exam_number_of_questions_text) and exam.exam_print in ['ques', 'both']:
            titl = _("Text Questions")
            if (exam.exam_print_eco == 'yes'):
                str1 += "\\\\\\vspace{2mm}\\textbf{%s:}  \\hfill {\\color{white} VERSÃO: \\#v%s}} \\\n" % (
                    titl, str(countVariations))
            else:
                str1 += "\n\n\\newpage\n\n"

            s = Utils.drawQuestionsTDifficulty(request, exam_i[2], exam, room, student_ID, student_name, count,
                                               data_hora)

            str1 += s[0]
            myqr[1] += s[1]
            count += 1

        # pip install bcrypt                                                                                                                   
        # import bcrypt                                                                                 
        # print (bcrypt.hashpw(b'teste123', bcrypt.gensalt()))                                  
        # print (bcrypt.hashpw(b'teste123', b'$2b$12$cRYX2M9V6glSp/ip/cmF2Or1nKSvnFZ19pBwSfTH4QKBc5rD7bEW2'))

        # s = str(myqr[1]).encode('utf-8')
        # print("passou4",exam_i[0])
        # s = str(myqr[1]+exam_i[0]).encode('utf-8')  # incluir as sequencias de respostas no qrcode
        # print("passou5",s)
        # compressed = zlib.compress(s,6)
        # sbeforeQR = binascii.hexlify(compressed)
        # print("passou6",sbeforeQR)

        ## chave hash
        if len(student_ID) >= 8:
            stud = student_ID[0:8].encode('utf-8')
        else:
            stud = student_ID.zfill(8).encode('utf-8')

        hashed = bcrypt.hashpw(stud, bcrypt.gensalt(6))
        id_hashed = hashed[7:]
        print("passou11", len(id_hashed), id_hashed, hashed)

        s = str(myqr[1] + exam_i[0]).encode('utf-8')  # incluir as sequencias de respostas no qrcode
        s0 = str(myqr[1]).encode('utf-8')  # mudar para deixar em um arquivo

        compressed = zlib.compress(s, 6)
        compressed0 = zlib.compress(s0, 6)
        sbeforeQR = binascii.hexlify(id_hashed + compressed)
        sbeforeQR0 = binascii.hexlify(id_hashed + compressed0)

        # gabarito de cada exame vai para um arquivo no servidor
        if exam.exam_print == 'both':

            fileGAB = 'tmpGAB/' + myqr[1] + '.txt'
            with open(fileGAB, 'w') as myfile:
                myfile = open(fileGAB, 'w')
                myfile.write(sbeforeQR.decode('utf-8'))
                myfile.close()

            # para testar
            with open(fileGAB, 'r') as myfile:
                mysbeforeQR = myfile.read()
                myfile.close()

            # para testar
            safterScanmy = binascii.unhexlify(mysbeforeQR)
            safterScan = binascii.unhexlify(sbeforeQR)
            if safterScanmy != safterScan:
                return HttpResponse("ERRO!!!!")
            un_hashed = safterScan[:53]
            safterScan = safterScan[53:]
            decompressed = zlib.decompress(safterScan)

            pre = '$2b$06$' + un_hashed.decode('utf-8')

            if hashed == bcrypt.hashpw(stud, pre.encode('utf-8')):
                print("passou19 = ok", pre)

            if s != decompressed:
                return HttpResponse("ERROR: in compression")

        # L, M, Q, or H; each level ==> 7, 15, 25, or 30 percent
        qr = pyqrcode.create(sbeforeQR0, error='M')  # myqr[1]
        qr.eps(myqr[0])  # gerar qr após sorteio das questoes/respostas

        if (exam.exam_print_eco == 'yes'):
            str1 += "\n \ \ \\ \n \\newpage\n"

        return str1
