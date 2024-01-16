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
# coding=UTF-8

import datetime
import random
import subprocess
import os

import matplotlib

# import matplotlib.pyplot as plt
# import numpy as np

# do not delete - for parametric questions

matplotlib.use('Agg')

from django.contrib import messages
from django.utils.translation import gettext_lazy as _

try:
    from topic.Utils import *
except:
    pass


def createWrongAnswers(a):
    global correctAnswer, a0, a1, a2

    respostas = ""
    # print "======len:", len(a)
    if len(a) == 2:
        a0 = int(a[0])
        a1 = int(a[1])

        rand = random.sample(range(correctAnswer - a1, correctAnswer + int(a1 / 2)), a0)
        for i in rand:
            respostas += "" + str(i) + "\n"

        if correctAnswer in rand:
            respostas = createWrongAnswers(a)

    elif len(a) == 1:
        a0 = int(a[0])
        count = 0
        for i in a2:
            if i != correctAnswer and count < a0:
                count += 1
                respostas += str(i) + "\n"

    return respostas


class UtilsMC(object):

    @staticmethod
    def getQuestion(i, AllLines):
        tam = len(AllLines)
        while i < tam and AllLines[i][:3] not in ['QT:', 'QE:', 'QM:', 'QH:']:  # acha uma questão
            i += 1
        # if i == tam: return(i,' ') # não achou questão

        tp = AllLines[i][:3]
        q = [AllLines[i] + '\n']
        i += 1
        # return HttpResponse(q)
        while i < tam and AllLines[i][:AllLines[i].find(':')] not in ['QT', 'QE', 'QM', 'QH', 'A']:  # ,'[[def']:
            q.append(AllLines[i] + '\n')
            i += 1
        if i <= tam and tp == 'QT:':  # questao do tipo texto
            return (i, ''.join([x for x in q]))
        if i < tam and tp in ['QE:', 'QM:', 'QH:'] and AllLines[i][:2] in ['QT', 'QE:', 'QM:', 'QH:']:
            print('ERRO: questão sem alternativas')

        return (i, ''.join([x for x in q]))

    @staticmethod
    def getAnswer(i, AllLines):
        tam = len(AllLines)
        while i < tam and AllLines[i][:2] not in ['A:']:  # acha uma questão
            i += 1
        # if i == tam: return(i,' ') # não achou questão
        q = [AllLines[i]]
        i += 1
        while i < tam and AllLines[i][:AllLines[i].find(':')] not in ['QT', 'QE', 'QM', 'QH', 'A']:  # ,'[[def']:
            q.append(AllLines[i] + '\n')
            i += 1
        return (i, ''.join([x for x in q]))

    @staticmethod
    def get_Equations(s):
        # s = "um exemplo $*$ x, y = symbols('x,y') :: sin(x+y).expand(trig=True) $*$, outro exemplo $*$ :: b = y - x $*$ fim!"
        # cada equacao tem ter duas partes, uma para definir as variáveis, que vai ser mostrado no enunciado da questao
        # a segunda parte é a equação propriamente dita
        eq_str = '$*$'
        s1 = s.partition(eq_str)
        eq = []
        while len(s1) == 3 and s1[2] != '':
            s2 = s1[2].partition(eq_str)
            if s2[1] != '':
                eq.append(s2[0])
                s1 = s2[2].partition(eq_str)
        return eq

    @staticmethod
    def get_code(s, str):
        # https://automatetheboringstuff.com/chapter7/
        import re
        code = []
        start = '\[\[' + str + ':'
        end = '\]\]'
        # (\S+|\w+|.*)  ->  (\w+|.*)
        reg = re.compile(start + '(\S+|\w+|.*)' + end, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        for groups in reg.findall(s):

            for i in ['cmd', 'mkdir',
                      'gnureadline', 'getopt',
                      'shlex', 'commands']:
                if i in groups:
                    return None  # HttpResponse('ERROR: do not use that word in the code: '+i)

            if str == 'code':
                groups = groups.replace(" ", "")

            code.append(groups)

        return code

    @staticmethod
    def questionParametric(question, answers, exam):
        dt0 = datetime.datetime.now()
        print("questionParametric-00-" + str(dt0))

        ############ question + def #####

        AllLines = question.splitlines()
        for i in range(0, len(AllLines)):
            if AllLines[i].replace(" ", "") == "":
                AllLines[i] = AllLines[i][1:] + '\n'
            else:
                AllLines[i] = AllLines[i] + '\n'
        mystr = ''.join(AllLines).replace("\r", "")

        myDef = UtilsMC.get_code(mystr, 'def')

        if myDef is not None:  # spend more time
            try:
                exec('\n'.join(myDef))  # run the algorithm and variables
            except Exception as e:
                e = str(e).replace('<','$<$').replace('>','$>$')
                e += '\n\n\n\\begin{verbatim}' + '\n'.join(myDef) + '\n\\end{verbatim}'
                return [f"ERROR in [[def: ... ]]: {e}", "", ""]
        else:
            return ["ERROR", "ERROR", "ERROR"]

        arg = UtilsMC.get_code(question, 'code')  # get the args in text

        i = 0
        tam = len(AllLines)
        while i < tam:
            for j in arg:
                try:
                    AllLines[i] = AllLines[i].replace("[[code:" + j + "]]", str(eval(j)))
                except Exception as e:
                    e = str(e).replace('<', '$<$').replace('>', '$>$')
                    e += '\n\n\n\\begin{verbatim}' + '\n'.join(myDef) + '\n\\end{verbatim}'
                    return [f"ERROR in [[code: ... ]]: {e} {j}", "", ""]
            if i >= len(AllLines) or AllLines[i].find("[[def:") > -1:
                tam = i
                break
            i = i + 1

        q_param = ""
        for j in range(0, tam):
            q_param += AllLines[j].replace('\r', '')

        ############ answers #####
        AllLines = []
        for a in answers:
            if not exam:
                AllLines.append(a.answer_text + '\n')
            elif len(AllLines) < int(exam.exam_number_of_anwsers_question):
                AllLines.append(a.answer_text + '\n')
        i = 0
        tam = len(AllLines)

        for a in UtilsMC.get_code(''.join(AllLines), 'code'):  # get the args in answers
            if a not in arg:
                arg.append(a)

        while i < tam:
            for j in arg:
                if AllLines[i].find('[[code:createWrongAnswers(') > -1 and j.find('createWrongAnswers(') > -1:
                    del (AllLines[i])
                    tam -= 1
                    m = 0
                    for k in j.split('\n'):
                        if len(str(k)) > 0:
                            for z in str(eval(k)).split('\n'):
                                if z:
                                    if exam: # limita pelo n. respostas do exame
                                        if len(AllLines) < int(exam.exam_number_of_anwsers_question):
                                            AllLines.insert(i, z.replace('\n\n', '\n'))
                                            i += 1
                                            m += 1
                                    else:
                                        AllLines.insert(i, z.replace('\n\n', '\n'))
                                        i += 1
                                        m += 1

                    i -= 1
                    tam = tam + m
                AllLines[i] = AllLines[i].replace("[[code:" + j + "]]", str(eval(j)))

            if i >= len(AllLines) or AllLines[i].find("[[def:") > -1:
                tam = i
                break

            i = i + 1


        ############ Feedback #####
        AllLinesFeedback = []
        for a in answers:
            if not exam:
                AllLinesFeedback.append(a.answer_feedback + '\n')
            elif len(AllLinesFeedback) < int(exam.exam_number_of_anwsers_question):
                AllLinesFeedback.append(a.answer_feedback + '\n')
        i = 0
        tam = len(AllLinesFeedback)

        for a in UtilsMC.get_code(''.join(AllLinesFeedback), 'code'):  # get the args in answers
            if a not in arg:
                arg.append(a)

        while i < tam:
            for j in arg:
                AllLinesFeedback[i] = AllLinesFeedback[i].replace("[[code:" + j + "]]", str(eval(j)))

            if i >= len(AllLinesFeedback) or AllLinesFeedback[i].find("[[def:") > -1:
                tam = i
                break

            i = i + 1

        return [q_param, AllLines, AllLinesFeedback]

    @staticmethod
    def questionsReadFiles(request, file):
        # estados possiveis: fora de alguma questao
        #                    dentro de uma questao - 'QT','QE','QM','QH' - pergunta
        #                    dentro de uma questao - A - respostas
        # as questões são dos tipos QT (somente texto), QE (fácil), QM (média) ou QH (difícil)
        # podendo ter subtipos, por exemplo, se tiver 5 questões, QE:a:, será escolhido de forma
        # aleatória, somente uma questão do subtipo "a".
        # As questões QT, contendo apenas textos, serão inseridas no final do tex.

        # global correctAnswer

        listao = []
        respostas = []
        d = dict()
        arqnum = 0
        questnum = 0
        questtotal = 0
        questions_file = 0

        latexAccents = [
            [u"à", "\\`a"],  # Grave accent
            [u"è", "\\`e"],
            [u"ì", "\\`\\i"],
            [u"ò", "\\`o"],
            [u"ù", "\\`u"],
            [u"ỳ", "\\`y"],
            [u"À", "\\`A"],
            [u"È", "\\`E"],
            [u"Ì", "\\`\\I"],
            [u"Ò", "\\`O"],
            [u"Ù", "\\`U"],
            [u"Ỳ", "\\`Y"],
            [u"á", "\\'a"],  # Acute accent
            [u"é", "\\'e"],
            [u"í", "\\'\\i"],
            [u"ó", "\\'o"],
            [u"ú", "\\'u"],
            [u"ý", "\\'y"],
            [u"Á", "\\'A"],
            [u"É", "\\'E"],
            [u"Í", "\\'\\I"],
            [u"Ó", "\\'O"],
            [u"Ú", "\\'U"],
            [u"Ý", "\\'Y"],
            [u"â", "\\^a"],  # Circumflex
            [u"ê", "\\^e"],
            [u"î", "\\^\\i"],
            [u"ô", "\\^o"],
            [u"û", "\\^u"],
            [u"ŷ", "\\^y"],
            [u"Â", "\\^A"],
            [u"Ê", "\\^E"],
            [u"Î", "\\^\\I"],
            [u"Ô", "\\^O"],
            [u"Û", "\\^U"],
            [u"Ŷ", "\\^Y"],
            [u"ä", "\\\"a"],  # Umlaut or dieresis
            [u"ë", "\\\"e"],
            [u"ï", "\\\"\\i"],
            [u"ö", "\\\"o"],
            [u"ü", "\\\"u"],
            [u"ÿ", "\\\"y"],
            [u"Ä", "\\\"A"],
            [u"Ë", "\\\"E"],
            [u"Ï", "\\\"\\I"],
            [u"Ö", "\\\"O"],
            [u"Ü", "\\\"U"],
            [u"Ÿ", "\\\"Y"],
            [u"ç", "\\c{c}"],  # Cedilla
            [u"Ç", "\\c{C}"],
            [u"œ", "{\\oe}"],  # Ligatures
            [u"Œ", "{\\OE}"],
            [u"æ", "{\\ae}"],
            [u"Æ", "{\\AE}"],
            [u"å", "{\\aa}"],
            [u"Å", "{\\AA}"],
            [u"–", "--"],  # Dashes
            [u"—", "---"],
            [u"ø", "{\\o}"],  # Misc latin-1 letters
            [u"Ø", "{\\O}"],
            [u"ß", "{\\ss}"],
            [u"¡", "{!`}"],
            [u"¿", "{?`}"],
            [u"\\", "\\\\"],  # Characters that should be quoted
            [u"~", "\\~"],
            [u"&", "\\&"],
            [u"$", "\\$"],
            [u"{", "\\{"],
            [u"}", "\\}"],
            [u"%", "\\%"],
            [u"#", "\\#"],
            [u"_", "\\_"],
            [u"≥", "$\\ge$"],  # Math operators
            [u"≤", "$\\le$"],
            [u"≠", "$\\neq$"],
            [u"©", "\copyright"],  # Misc
            [u"ı", "{\\i}"],
            [u"µ", "$\\mu$"],
            [u"°", "$\\deg$"],
            [u"‘", "`"],  # Quotes
            [u"’", "'"],
            [u"“", "``"],
            [u"”", "''"],
            [u"‚", ","],
            [u"„", ",,"],
        ]

        # raise Http404("oi1")

        # for a in arquivos: # para cada arquivo de questões
        fstr = file.read().decode('utf-8')
        # for i in latexAccents:
        #    fstr = fstr.replace(i[0],i[1])

        # raise Http404("oi1")

        # return HttpResponse(fstr)

        AllLines = fstr.splitlines()
        tam = len(AllLines)
        # return HttpResponse(AllLines)

        i = 0
        while i < tam:
            i, q = UtilsMC.getQuestion(i, AllLines)
            print("#>#>#>#===", i, q)
            d = dict()

            # return HttpResponse(q)

            d["t"] = ''
            vet = q.split('::')
            if len(vet) == 2:  # somente tipo
                d["t"] = vet[0]  # tipo QT, QE, QM ou QH
                # d["q"] = r'\hspace{-12mm}{\color{white}\#'+str(questnum).zfill(3)+r'} \ \ \hspace{2mm} \ ' + vet[1].strip()
                d["q"] = vet[1].strip()
                d["c"] = ''
                d["st"] = ''
            elif len(vet) == 3:  # com conteúdo abordado da questão
                d["t"] = vet[0]
                s = vet[1]  # normalize('NFKD', vet[1].decode('utf-8')).encode('ASCII', 'ignore') # retirar acentos
                d["c"] = s
                # d["q"] = r'\hspace{-12mm}{\color{white}\#'+str(questnum).zfill(3) + r'} \ \ \hspace{2mm} \ ' + vet[2].strip()
                d["q"] = vet[2].strip()
                d["st"] = ''
            elif len(vet) == 4:  # subtipo da questão, um caracter qualquer
                d["t"] = vet[0]  # tipo QT, QE, QM ou QH
                s = vet[1]  # normalize('NFKD', vet[1].decode('utf-8')).encode('ASCII', 'ignore') # retirar acentos
                d["c"] = s
                d["st"] = vet[2]
                # d["q"] =  r'\hspace{-12mm}{\color{white}\#'+str(questnum).zfill(3)+ r'} \ \ \hspace{2mm} \ ' + vet[3].strip()
                d["q"] = vet[3].strip()

            d["n"] = questnum
            d["arq"] = arqnum

            respostas = []
            contRespostas = 0
            if d["t"] != "QT":
                linha_i = AllLines[i]
                while i < tam and AllLines[i][:AllLines[i].find(':')] in ['A']:
                    i, r = UtilsMC.getAnswer(i, AllLines)
                    # print (i,r)
                    # if i == tam: break # não achou questão
                    if (not contRespostas):
                        # respostas.append(r[2:].strip())   # cyan alternativa correta
                        # respostas.append("{\color{cyan} "+r[2:].strip()+"}")   # cyan alternativa correta
                        # respostas.append(r"\hspace{-1.2mm}{\color{white}\#}"+str(r[2:].strip()))
                        respostas.append(str(r[2:].strip()))

                    else:
                        # respostas.append(r[2:].strip())   # gray alternativa errada
                        # respostas.append("{\color{gray} "+r[2:].strip()+"}")
                        respostas.append(str(r[2:].strip()))
                    contRespostas += 1

                if contRespostas == 0:
                    messages.error(request, _('ImportQuestions: ERROR question without answers: ' + str(d['q'])))
                    return ''

            d["a"] = respostas

            listao.append(d)
            questnum += 1

        arqnum += 1
        messages.info(request, _("read question(s): ") + str(len(listao) - questions_file))

        messages.info(request, _("Total of questions without groups:"))
        messages.info(request,
                      _("Easy questions QE: ") + str(len([y for y in listao if y['t'] == 'QE' and y['st'] == ''])))
        messages.info(request,
                      _("Mean questions QM: ") + str(len([y for y in listao if y['t'] == 'QM' and y['st'] == ''])))
        messages.info(request,
                      _("Hard questions QH: ") + str(len([y for y in listao if y['t'] == 'QH' and y['st'] == ''])))
        messages.info(request,
                      _("Text questions QT: ") + str(len([y for y in listao if y['t'] == 'QT' and y['st'] == ''])))

        messages.info(request, _("Total of questions with groups:"))
        messages.info(request,
                      _("Easy questions QE: ") + str(len([y for y in listao if y['t'] == 'QE' and y['st'] != ''])))
        messages.info(request,
                      _("Mean questions QM: ") + str(len([y for y in listao if y['t'] == 'QM' and y['st'] != ''])))
        messages.info(request,
                      _("Hard questions QH: ") + str(len([y for y in listao if y['t'] == 'QH' and y['st'] != ''])))
        messages.info(request,
                      _("Text questions QT: ") + str(len([y for y in listao if y['t'] == 'QT' and y['st'] != ''])))

        return listao

    @staticmethod
    def createListTypes(listao, tipo, numQ):
        global RA

        random.seed(int(RA))  # semente pelo RA

        questTipo = [y for y in listao if y['t'] == tipo and y['st'] == '']  # pega todas as questões SEM subtipo

        st = [(y['st'], y['n']) for y in listao if y['t'] == tipo and y['st'] != '']  # pega COM subtipos
        if st:
            stSet = list(set([i[0] for i in st]))  # retira elementos repetidos
            for i in stSet:  # para cada subtipo, pego apenas UMA questão aleatoriamente
                li = [(y['st'], y['n']) for y in listao if y['t'] == tipo and y['st'] == i]
                escolhoUM = random.sample(li, 1)
                ques = [y for y in listao if y['n'] == escolhoUM[0][1]]
                questTipo.append(ques[0])

        if numQ > len(questTipo):
            print("number of available questions %s: \t %-5d" % (tipo, len(questTipo)))
            print("\nERRO: number of solicitous questions is incompatible with the number of available questions\n")
            # sys.exit(-1)
            return []

        return questTipo

    @staticmethod
    def sortedBySimilarity(questions, limiar=0.7):
        '''
        Esta função (1) cria uma matriz nxn de similaridades de n questões.
        (2) Retira primeiro a questão com maior SOMA das similaridade entre
        as outras questões (max(sum(m)). (3) Retira também essas outras
        questões com similaridade >= limiar. Retorna para o passo (2),
        desconsiderando as questões já retiradas.
        :param questions: list of questions
        :param limiar: limiar
        :return: sort by similarity of text
        '''
        from difflib import SequenceMatcher

        n = len(questions)
        m = np.zeros((n, n))  # matriz de similaridades
        for i in range(n):
            for j in range(n):
                m[i, j] = round(SequenceMatcher(None, questions[i], questions[j]).ratio(), 2)

        np.fill_diagonal(m, 0)  # preenche a diagonal com zero

        questions_new = []
        id_del = []
        while m.max() > 0:
            v = m.sum(axis=1)  # soma cada linha
            vL = np.argsort(v)[::-1][:n]  # índice ordem reversa
            questions_new.append(questions[vL[0]])
            vC = np.argsort(m[vL[0]])[::-1][:n]
            id_aux = [vL[0]]
            for i in vC:
                if i != vL[0] and m[vL[0]][i] >= limiar:
                    questions_new.append(questions[i])
                    id_aux.append(i)

            for i in id_aux:
                m[:, i] = 0  # zera a coluna da questão
                m[i] = 0  # zera a linha da questão
            id_del += id_aux

        questions_aux = questions.copy()
        for i in sorted(id_del, reverse=True):
            del questions[i]

        new_order = id_del
        for v in questions:
            new_order.append(questions_aux.index(v))

        return (new_order)

    @staticmethod
    def sortedBySimilarity2(questions, limiar=0.8):
        '''
        Esta função (1) cria uma matriz nxn de similaridades de n questões.
        (2) Retira primeiro a questão com maior similaridade entre as outras
        questões (max(m)). (3) Retira também essas outras questões com
        similaridade >= limiar. Retorna para o passo (2), desconsiderando
        as questões já retiradas.
        :param questions: list of questions
        :param limiar: limiar
        :return: sort by similarity of text
        '''
        from difflib import SequenceMatcher

        n = len(questions)
        m = np.zeros((n, n))  # matriz de similaridades
        for i in range(n):
            for j in range(n):
                m[i, j] = round(SequenceMatcher(None, questions[i], questions[j]).ratio(), 2)

        np.fill_diagonal(m, 0)  # preenche a diagonal com zero

        questions_new, id_del = [], []
        while len(m) and m.max() > 0:
            idLMax = np.where(m == np.amax(m))[0][0] # linha com maior similaridade

            questions_new.append(questions[idLMax])
            id_aux = [idLMax]

            vC = np.argsort(m[idLMax])[::-1][:n] # maiores similaridades da linha
            for i in vC:
                if i != idLMax and m[idLMax][i] >= limiar:
                    # print(i, m[idLMax][i], questions[idLMax], "~=", questions[i])
                    questions_new.append(questions[i])
                    id_aux.append(i)

            for i in id_aux:
                m[:, i] = 0  # zera a coluna da questão
                m[i] = 0  # zera a linha da questão
            id_del += id_aux

        questions_aux = questions.copy()
        for i in sorted(id_del, reverse=True):
            del questions[i]

        new_order = id_del
        for v in questions:
            new_order.append(questions_aux.index(v))

        return (new_order)
