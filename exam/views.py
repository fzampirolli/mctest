"""
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
"""
# from rest_framework import viewsets#serializers
import csv
import datetime
import glob
import json
import os
import re
import pandas as pd

import PyPDF2
import cv2  # pip install opencv-python
import img2pdf
import numpy as np
import pandas
from django.contrib import messages
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import get_messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.static import serve
from django.urls import reverse_lazy
from pdf2image import convert_from_path
from tablib import Dataset

from exam.CVMCTest import cvMCTest
from exam.UtilsLatex import Utils
from mctest.settings import BASE_DIR
from mctest.settings import webMCTest_FROM
from mctest.settings import webMCTest_PASS
from mctest.settings import webMCTest_SERVER
from .forms import UpdateExamForm, ExamCreateForm
from .models import Exam
from .models import VariationExam
from .models import StudentExam
from topic.models import Question
from topic.models import Answer
from topic.models import Topic


@login_required
def variationsExam(request, pk):
    """
    Summary line.

    Extended description of function.

    Parameters
    ----------
    arg1 : int
        Description of arg1
    arg2 : str
        Description of arg2

    Returns
    -------
    int
        Description of return value

    """
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    data_hora = datetime.datetime.now()
    data_hora = str(data_hora).split('.')[0].replace(' ', ' - ')
    print("variationsExam-00-" + str(datetime.datetime.now()))

    font_size = request.POST.get('font_size')

    exam = get_object_or_404(Exam, pk=pk)

    if exam.exam_print == 'answ':
        messages.error(request,
                       _('variationsExam: there are no variations in the answer-only style!'))
        return render(request, 'exam/exam_errors.html', {})

    for v in exam.variationsExams2.all():
        v.delete()

    st = Utils.validateProf(exam, request.user)
    if st != None:
        return HttpResponse(st)

    print("variationsExam-01-" + str(datetime.datetime.now()))
    for v in range(int(exam.exam_variations)):  # for each variant
        formatVariations = {}
        formatVariations['variations'] = []
        print("variationsExam-02-" + str(datetime.datetime.now()) + ' var: ' + str(v))
        db_questions = Utils.drawQuestionsVariations(request, exam, request.user,
                                                     Utils.getTopics(exam))
        # db_questions_all.append(db_questions)
        # listao.append([qr_answers, str1, QT])

        variant = {}
        variant['variant'] = str(v + 1)  ##### MUDAR para iniciar com a variação 0 !!!!
        variant['questions'] = []
        for q in db_questions[0]:  # for each question QM
            question = dict(zip(['number', 'key', 'topic', 'type', 'weight', 'short', 'text', 'answers'], q))
            question['answers'] = []
            for key, a in enumerate(q[7]):
                answer = {}
                answer['answer'] = key
                answer['sort'] = a[0]
                answer['text'] = a[1]
                answer['feedback'] = a[2]
                question['answers'].append(answer)
            variant['questions'].append(question)
        if len(db_questions) >= 2:  # QM and QT
            for qi in range(1, len(db_questions)):  # for each question QT
                q = db_questions[qi][0]
                if q != None and len(q) == 8:
                    question = dict(zip(['number', 'key', 'topic', 'type', 'weight', 'short', 'text', 'answers'], q))
                    variant['questions'].append(question)
                    st = question['text']

                    # Text question with correct answer
                    a, b = st.find('%%{'), st.find('}%%')
                    if a < b:
                        ans = st[a + len('%%{'):b]
                        answer = {}
                        answer['answer'] = 0
                        answer['sort'] = 0
                        answer['text'] = ans.strip()
                        answer['feedback'] = '\n'
                        question['answers'].append(answer)

                    # Text question with test cases for Moodel+VPL
                    a, b = st.find('begin{comment}'), st.find('end{comment}')
                    if a < b:
                        st = st[a + len('begin{comment}'):b]
                        st = st[st.find("{"):len(st) - 2]
                        st = st.replace('\\\\', '\\')
                        case = json.loads(st)
                        case['input'] = [[c] for c in case['input']]
                        case['output'] = [[c] for c in case['output']]
                        case['key'] = [str(question['key'])]
                        question['testcases'] = case

        formatVariations['variations'].append(variant)
        v = VariationExam.objects.create(variation=formatVariations)
        exam.variationsExams2.add(v)

    choices_list = []
    if request.method == 'POST':
        choices_list.append(request.POST.getlist('choicesJSON'))
        choices_list.append(request.POST.getlist('choicesTemplateCSV'))
        choices_list.append(request.POST.getlist('choicesAiken'))
        choices_list.append(request.POST.getlist('choicesXML'))
        choices_list.append(request.POST.getlist('choicesLatex'))
        choices = [i[0] for i in choices_list if len(i)]

        anexos = []
        path_aux = BASE_DIR + "/pdfExam/report_Exam_" + str(pk)
        message_cases = _('Dear,') + '\n\n'
        message_cases += _(
            'This message contains files created automatically, with all variations of this exam.') + '\n\n'

        if 'JSON' in choices:
            # send by email all case tests of moodle
            print("variationsExam-03-" + str(datetime.datetime.now()))
            path_to_file_LINKER_JSON = path_aux + "_linker.json"
            cases = Utils.get_cases(exam)
            anexos.append([Utils.format_cases(cases, path_to_file_LINKER_JSON)])
            if len(cases['key'] and cases['key'][0]):
                print("generate_page-04-" + str(datetime.datetime.now()))
                message_cases += _(
                    '# JSON: Test cases to be inserted in the Moodle for automatic correction of the codes sent by the students, following these steps:') + '\n'
                message_cases += _(
                    '1. Use the PDF with the exams generated with this date and time (EXACTLY): "') + data_hora + '"\n'
                message_cases += _('2. Save and rename "linker.json" and "students_variations.csv" files') + '\n'
                message_cases += _(
                    '3. After you create a Moodle VPL activity, in the "runtime files", add "linker.json" and "students_variations.csv"') + '\n'
                message_cases += _(
                    '4. Add too other files available at github.com/fzampirolli/mctest/VPL_modification') + '\n'
                message_cases += _(
                    '5. Also enable these files under "Files to keep while running"') + '\n'
                message_cases += _(
                    'Note: "students_variations.csv" will be sent by email when creating PDFs of student exams.') + '\n'
            else:
                message_cases += _(
                    '# JSON: There are no Test Cases!') + '\n'
            message_cases += _('See for details') + ':\n'
            message_cases += '  A. https://doi.org/10.5753/cbie.sbie.2020.1573' + ' - v.01\n'
            message_cases += '  B. "Automated assessment of parametric programming in a large-scale course" (LACLO21)' + ' - v.10\n'
            message_cases += '  C. https://sol.sbc.org.br/index.php/sbie/article/view/18135/17969' + '\n\n'

        if 'TemplateCSV' in choices:
            path_to_file_TEMPLATES = path_aux + "_templates.csv"
            Utils.createFileTemplates(exam, path_to_file_TEMPLATES)
            anexos.append([path_to_file_TEMPLATES])
            message_cases += _('# CSV: Template of questions.') + '\n'
            message_cases += _('See for details') + ':\n'
            message_cases += '  A. https://doi.org/10.5753/cbie.sbie.2020.51. '
            message_cases += _('This CSV file can be used for automatic correction using Google Forms + Sheets.') + '\n'
            message_cases += '  B. "Automated assessment with multiple-choice questions using weighted answers" (CSEDU21)' + '\n\n'

        if 'Aiken' in choices:
            path_to_file_VARIATIONS_DB_aiken = path_aux + "_variations_DB_aiken.txt"
            Utils.createFileDB_aiken(exam, path_to_file_VARIATIONS_DB_aiken)
            anexos.append([path_to_file_VARIATIONS_DB_aiken])
            message_cases += _('# AIKEN: Database of questions for Moodle.') + '\n'
            message_cases += _(
                'See for details: "Facilitating the Generation of Parametric Questions and their export to Moodle" (FIE21)') + '\n\n'

        if 'XML' in choices:
            path_to_file_VARIATIONS_DB_xml = path_aux + "_variations_DB.xml"
            Utils.createFileDB_xml(exam, path_to_file_VARIATIONS_DB_xml)
            anexos.append([path_to_file_VARIATIONS_DB_xml])
            message_cases += _('# XML: Database of questions for Moodle.') + '\n'
            message_cases += _(
                'See for details: "Facilitating the Generation of Parametric Questions and their export to Moodle" (FIE21)') + '\n\n'

        if 'Latex' in choices:
            path_aux = BASE_DIR + "/report_Exam_" + str(pk)
            path_to_file_VARIATIONS_DB_Tex = path_aux + "_variations.tex"
            if not Utils.createFile_Tex(request, exam, path_to_file_VARIATIONS_DB_Tex, data_hora, font_size):
                # message_cases += _("ERROR: Each block must have at least 3 questions/answers") + '\n'
                return render(request, 'exam/exam_msg.html', {})

            path_aux = BASE_DIR + "/pdfExam/report_Exam_" + str(pk)
            path_to_file_VARIATIONS_DB_Tex = path_aux + "_variations.tex"
            anexos.append([path_to_file_VARIATIONS_DB_Tex])
            anexos.append([path_to_file_VARIATIONS_DB_Tex[:-4] + '.pdf'])
            message_cases += _('# TEX+PDF: Database of questions in LaTeX format.') + '\n'
            message_cases += _('Run with command line:') + '\n'
            message_cases += _('pdflatex --shell -scape -interaction nonstopmode "file.tex".') + '\n\n'

        message_cases += '\n'
        if len(anexos):
            # send mail with all anexos
            enviaOK = cvMCTest.envia_email(webMCTest_SERVER,
                                           587,
                                           webMCTest_FROM,
                                           webMCTest_PASS,
                                           str(request.user),
                                           'MCTest: files created automatically; Exam: ' + str(
                                               exam.exam_name) + '; ' + data_hora,
                                           message_cases, anexos)
            # problem with permission ...
            path = os.getcwd()
            getuser = path.split('/')
            getuser = getuser[1]
            getuser = getuser + ':' + getuser
            os.system('chown -R ' + getuser + ' ' + path + ' .')
            os.system('chgrp -R ' + getuser + ' ' + path + ' .')

    messages.error(request,
                   _('Exam variations were stored in the database.'))
    messages.error(request,
                   _('Return and refresh the exam page. Notice the ID change next to the Create-Variations button.'))
    messages.error(request,
                   _('Whenever you click this button, new exam variations will be stored in the database!'))
    messages.error(request,
                   _('If you checked some options, check the attachments sent to your email.'))
    return render(request, 'exam/exam_msg.html', {})

    # return HttpResponseRedirect('/exam/exam/' + str(pk) + '/update/')


@login_required
def feedbackStudentsExamText(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    exam = get_object_or_404(Exam, pk=pk)

    if (exam.exam_student_feedback == 'no'):
        messages.error(request,
                       _('feedbackStudentsExamText: feedback to student is NO, Change to YES and click in Upload-PDF '
                         'again!'))
        return render(request, 'exam/exam_errors.html', {})

    if request.method == 'POST':
        file_name = exam.exam_name
        instrucoes = 'asdfasdf asdf afd '
        try:
            file = request.FILES['myfileZIP']
        except:
            messages.error(request,
                           _(
                               'feedbackStudentsExamText: choose a ZIP file with scanned exams, for example _e31_769.zip!'))
            return render(request, 'exam/exam_errors.html', {})

        filestr = str(file)

        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)

        path_to_file0 = BASE_DIR + "/" + uploaded_file_url
        path2 = BASE_DIR + "/pdfStudentEmail/" + filestr[:-4]

        os.system('rm -rf ' + path2)

        os.system("unzip " + path_to_file0 + " -d " + path2)

        files5 = []
        # r=root, d=directories, f = files  ===>> pega todos os pdfs
        for r, d, f in os.walk(path2):
            for file in f:
                if '.pdf' in file and file[0] != '.':
                    files5.append(os.path.join(r, file))

        myfiles = []
        idQuestion = ""
        for f in np.sort(files5):

            # /Users/fz/PycharmProjects/mctest/pdfStudentEmail/download/e102_c224_q1240_p001_11201811442.pdf
            # ['', 'Users', 'fz', 'PycharmProjects', 'mctest', 'pdfStudentEmail', 'download', '_e102_c224_q1240_p001_11201811442.pdf']
            fp = f.split('/')

            # _e102_c224_q1240_p001_11201811442.pdf
            ss = fp[-1]

            try:
                idExam = ss[ss.find('_e') + 2:ss.find('_c')]
                idClass = ss[ss.find('_c') + 2:ss.find('_q')]
                idQuestion = ss[ss.find('_q') + 2:ss.find('_p')]
                page = ss[ss.find('_p') + 2:ss.find('_p') + 5]
                idStudent = ss[ss.rfind('_') + 1:-4]
                a = int(idExam)
                a = int(idClass)
                a = int(idQuestion)
                a = int(page)
                a = int(idStudent)
            except:
                messages.error(request,
                               _(
                                   "feedbackStudentsExamText: name of the pdf file does not follow a pattern ID_xxx.pdf"))
                return render(request, 'exam/exam_errors.html', {})

            ss0 = ss.split(";")
            nota = erros = ""
            if len(ss0) == 2:
                nota = ss0[0]
                ss1 = ss0[1].split("_")

            elif len(ss0) == 3:
                nota = ss0[0]
                erros = ss0[1]
                ss1 = ss0[2].split("_")

            else:
                ss1 = ss.split("_")

            print('processing ', page, idQuestion, idStudent)
            myfiles.append([idExam, idQuestion, idStudent, nota, erros, page, f])

        try:
            # _e102_c224_q1240
            fileMSG = '_e' + idExam + '_c' + idClass + '_q' + idQuestion + '.txt'
            with open(os.path.join(path2, fileMSG), 'r', encoding="ISO-8859-1") as f:
                msg_str = f.read()
        except:
            msg_str = ""

        path_to_file = BASE_DIR + "/report" + str(pk) + "q" + idQuestion + ".csv"
        # raise Http404(path_to_file)

        try:
            os.remove(path_to_file)
            pass
        except Exception as e:
            pass

        for room in exam.classrooms.all():  # para cada turma
            for s in room.students.all():  # para cada estudante da turma
                # path = os.getcwd() + "/pdfStudentEmail/"
                # file_name = "studentEmail_e" + str(exam.id) + "_r" + str(room.id) + "_s" + s.student_ID

                for f in myfiles:
                    if f[0] == str(exam.id) and f[2] == s.student_ID:
                        email = "fzampirolli@gmail.com"
                        email = s.student_email
                        data_hora = datetime.datetime.now()
                        data_hora = str(data_hora).split('.')[0].replace(' ', ' - ')
                        file_name = f[6]
                        print('send mail to: ', s.student_email)
                        cvMCTest.sendMail(file_name, msg_str, email, str(s.student_name))
                        with open(path_to_file, 'a') as data:  # acrescenta no final do csv a cada envio
                            writer = csv.writer(data)
                            writer.writerow([f[5], s.student_ID, email, s.student_name, f[3], f[4], data_hora])

        try:
            with open(path_to_file, 'r') as f:
                pass
        except:
            messages.error(request,
                           _("feedbackStudentsExamText: no email was sent, are you in the correct Exam and Term?"))
            return render(request, 'exam/exam_errors.html', {})

        return serve(request, os.path.basename(path_to_file),
                     os.path.dirname(path_to_file))

    return HttpResponseRedirect("/")


@login_required
def feedbackStudentsExam(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    exam = get_object_or_404(Exam, pk=pk)

    if (exam.exam_student_feedback == 'no'):
        messages.error(request,
                       _(
                           "feedbackStudentsExam: feedback to student is NO, Change to YES and click in Upload-PDF again!"))
        return render(request, 'exam/exam_errors.html', {})

    if request.method == 'POST':
        file_name = exam.exam_name
        instrucoes = 'asdfasdf asdf afd '

        path_to_file = BASE_DIR + "/" + "report" + str(pk) + ".csv"
        try:
            os.remove(path_to_file)
            pass
        except Exception as e:
            pass

        myfiles = []
        mypath = os.getcwd() + "/pdfStudentEmail/"
        for file in np.sort(glob.glob(mypath + '*.pdf')):
            ss = file.split('_')
            ff = file.split('/')
            idStudent = ss[-1:][0]
            idStudent = idStudent[1:-4]
            idRoom = ss[len(ss) - 2]
            idRoom = idRoom[1:]
            idExam = ss[len(ss) - 3]
            idExam = idExam[1:]
            # return HttpResponse(file,idStudent,idRoom,idExam,ff[len(ff)-1])
            myfiles.append([idExam, idRoom, idStudent, ff[len(ff) - 1]])

        for room in exam.classrooms.all():  # para cada turma
            for s in room.students.all():  # para cada estudante da turma
                path = os.getcwd() + "/pdfStudentEmail/"
                for f in myfiles:
                    if f[0] == str(exam.id) and f[1] == str(room.id) and f[2] == s.student_ID:
                        email = "fzampirolli@gmail.com"
                        # email = s.student_email
                        data_hora = datetime.datetime.now()
                        data_hora = str(data_hora).split('.')[0].replace(' ', ' - ')

                        path = os.getcwd()
                        file_name = "studentEmail_e" + f[0] + "_r" + f[1] + "_s" + f[2]
                        file_name = path + "/pdfStudentEmail/" + file_name + '.pdf'

                        msg_str = ""
                        cvMCTest.sendMail(file_name, msg_str, email, str(s.student_name))

                        with open(path_to_file, 'a') as data:  # acrescenta no final do csv a cada envio
                            writer = csv.writer(data)
                            writer.writerow(['page', s.student_ID, email, s.student_name, data_hora])

        try:
            with open(path_to_file, 'r') as f:
                pass
        except:
            messages.error(request, _("feedbackStudentsExam: no email was sent, are you in the correct Exam and Term?"))
            return render(request, 'exam/exam_errors.html', {})

        return serve(request, os.path.basename(path_to_file),
                     os.path.dirname(path_to_file))

    return HttpResponseRedirect("/")


@login_required
def correctStudentsExam(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    exam = get_object_or_404(Exam, pk=pk)

    strf2 = BASE_DIR + "/pdfStudentEmail/studentEmail_e" + str(exam.id) + "*"
    try:
        for fi in glob.glob(strf2):
            os.remove(fi)
        pass
    except Exception as e:
        pass

    if request.method == 'POST':
        dataset = Dataset()
        try:
            file = request.FILES['myfilePDF']
        except:
            messages.error(request, _('correctStudentsExam: choose a PDF file with scanned exams!'))
            return render(request, 'exam/exam_errors.html', {})

        choiceReturnQuestions = request.POST.get('choiceReturnQuestions')

        fs = FileSystemStorage()
        file0 = str(file.name)
        file0 = file0.replace(' ', '')

        file0 = re.sub('[^A-Za-z0-9._-]+', '', file0)  # remove special characters

        filename = fs.save(file0, file)

        file = file0
        f = file0[:-4] + '.csv'
        if os.path.exists(f):
            os.remove(f)

        MYFILES = BASE_DIR + "/tmp/_e" + str(exam.id) + '_' + str(request.user) + '_' + file0[:-4]

        try:
            input_pdf = PyPDF2.PdfFileReader(open(str(file), "rb"))
        except PyPDF2.utils.PdfReadError:
            messages.error(request, _("correctStudentsExam: Error in read PDF file: ") + str(file))
            return render(request, 'exam/exam_errors.html', {})

        # try reading the pdf file using another way
        pages = convert_from_path(file, 200)  # dpi 100=min 500=max
        numPAGES = 0
        for page in pages:
            myfile0 = MYFILES + '_p' + str(numPAGES) + '.png'
            page.save(myfile0)
            numPAGES += 1
        pages.clear()

        countCorrectExams = 0
        countCorrectQuestions = 0
        qr0 = dict()
        countPage = 0
        while countPage < numPAGES:  # para cada pagina do pdf
            print("#$$$$$$$$$$$$$$$ PAGINA ======", countPage + 1)
            myfile0 = MYFILES + '_p' + str(countPage) + '.png'
            img = cv2.imread(myfile0)
            #img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

            DEBUG = False

            img = img0 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            cvMCTest.centroidsMarked = []
            countCorrectExams += 1

            # img = 255 - imgs[countPage]
            if DEBUG: cv2.imwrite("_test_corrTests" + "_p" + str(countPage + 1).zfill(3) + "_01all.png", img)

            myFlagArea, qr = cvMCTest.getQRCode(img, countPage)
            img = cvMCTest.imgAnswers

            if not qr:
                qr = dict()
                qr['idStudent'] = 'ERROR'
                if myFlagArea:
                    qr['answer'] = exam.exam_number_of_anwsers_question
                else:
                    qr['answer'] = 'ERROR'
                qr['numquest'] = Utils.getNumMCQuestions(exam)
                qr['idExam'] = pk
                qr['idClassroom'] = '0'
                qr['question'] = '0'
                qr['respgrade'] = '0'
                qr['stylesheet'] = '0'  # default horizonal=0

                qr['variations'] = '0'
                qr['variant'] = '0'

            qr['exam_print'] = exam.exam_print

            if int(Utils.getNumMCQuestions(exam) == 0):
                qr['onlyT'] = True
            else:
                qr['onlyT'] = False

            qr['file'] = file
            qr['page'] = countPage
            qr['max_questions_square'] = exam.exam_max_questions_square
            qr['user'] = request.user.email
            qr['exam_print'] = exam.exam_print

            if not countPage and qr[
                'exam_print'] == 'answ':  # para correcoes sem questoes, com apenas quadro de reposta,
                qr0 = qr  # guarda a primeira pagina como gabarito

            if qr['onlyT']:  # questoes dissertativas e uma questao por pagina - frente-verso: salva a página em tmp/
                print(">>>>text>>>>", qr)
                mypath = MYFILES + "_q" + qr['question']

                myfile = mypath + "/_e" + qr['idExam'] + "_c" + qr['idClassroom'] + "_q" + qr['question'] + "_p" + str(
                    countPage + 1).zfill(3) + "_" + qr['idStudent'] + ".pdf"

                myfileMSG = mypath + "/_e" + qr['idExam'] + "_c" + qr['idClassroom'] + "_q" + qr['question'] + '.txt'

                os.system("mkdir " + mypath)

                if not os.path.exists(myfileMSG):
                    with open(myfileMSG, 'w') as fileMSG:
                        fileMSG.write('Write here a message to sent to student, for each question/classroom')
                        fileMSG.close()

                if countPage < numPAGES - 1:  # salva tb verso
                    # countPage += 1
                    # myfile2 = MYFILES + '_p' + str(countPage) + '.png'

                    fileImages = [myfile0]  # , myfile2]

                    flagOK = False  # continua salvando ate achar qrcode ou acabar
                    while not flagOK and countPage < numPAGES - 1:
                        myfile3 = MYFILES + '_p' + str(countPage + 1) + '.png'
                        img2 = cv2.imread(myfile3)
                        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                        flagOK, qr3 = cvMCTest.getQRCode(img2, countPage)

                        if not qr3:
                            fileImages.append(myfile3)
                            countPage += 1
                        else:
                            flagOK = True

                    with open(myfile, "wb") as outputStream:
                        outputStream.write(img2pdf.convert(fileImages))
                else:
                    with open(myfile, "wb") as outputStream:
                        outputStream.write(img2pdf.convert(myfile0))

            elif qr:

                if qr['stylesheet'] == '0' and exam.exam_stylesheet == 'Hor':  # quadro horizontal
                    cvMCTest.findBoxesAnwsersHor(img, countPage, -1)
                    img = cvMCTest.imgAnswersSegment
                    rectSquares = cvMCTest.findSquaresHor(qr, img, countPage)
                else:
                    rectSquares = cvMCTest.findSquares(qr, img, countPage)

                if DEBUG: cv2.imwrite("_test_corrTests" + "_p" + str(countPage + 1).zfill(3) + "_02.png", img)

                if qr['idStudent'] != 'ERROR':
                    strGAB = './pdfStudentEmail/studentEmail_e' + qr['idExam'] + '_r' + qr['idClassroom'] + '_s' + qr[
                        'idStudent'] + '_GAB.png'
                    imgGAB = cv2.medianBlur(cvMCTest.imgAnswers, 3)
                    imgGAB_rgb = cv2.cvtColor(imgGAB, cv2.COLOR_GRAY2RGB)

                testAnswers = []
                qr['squares'] = rectSquares

                if myFlagArea:

                    for countSquare in range(len(rectSquares)):
                        p1, p2 = rectSquares[countSquare]

                        if qr['idStudent'] != 'ERROR':
                            cv2.rectangle(imgGAB_rgb, (p1[1], p1[0]), (p2[1], p2[0]), (255, 255, 0), 1);

                        if qr['stylesheet'] == '0' and exam.exam_stylesheet == 'Hor':  # quadro horizontal
                            imgQi = cvMCTest.imgAnswersSegment[p1[0]:p2[0], p1[1]:p2[1]]
                            [NUM_COLUMNS, img] = cvMCTest.setColumnsHor(imgQi, countPage, countSquare)
                            [NUM_LINES, img] = cvMCTest.setLinesHor(imgQi, countPage, countSquare)
                            NUM_RESPOSTAS = NUM_LINES
                            NUM_QUESTOES = NUM_COLUMNS
                        else:
                            imgQi = cvMCTest.imgAnswers[p1[0]:p2[0], p1[1]:p2[1]]
                            [NUM_COLUMNS, img] = cvMCTest.setColumns(imgQi, countPage, countSquare)
                            [NUM_LINES, img] = cvMCTest.setLines(imgQi, countPage, countSquare)
                            NUM_RESPOSTAS = NUM_COLUMNS
                            NUM_QUESTOES = NUM_LINES

                        if DEBUG: cv2.imwrite(
                            "_test_corrTests" + "_p" + str(countPage + 1).zfill(3) + "_q" + str(countSquare + 1).zfill(
                                2) + "_00.png", imgQi)

                        countCorrectQuestions += NUM_QUESTOES

                        if int(NUM_RESPOSTAS) != int(qr['answer']):
                            qr['correct'] = 'ERROR:' + ' page ' + str(countPage + 1) + ' square ' + str(
                                countSquare + 1) + ': ' + str(NUM_RESPOSTAS) + '-' + str(qr['answer'])

                        imgQiNC = cvMCTest.imgAnswers[p1[0]:p2[0], p1[1]:p2[1]]
                        if qr['stylesheet'] == '0' and exam.exam_stylesheet == 'Hor':  # quadro horizontal
                            testAnswers.append(
                                cvMCTest.segmentAnswersHor([imgQi, imgQiNC], countPage, countSquare, NUM_QUESTOES, qr))
                        else:
                            testAnswers.append(
                                cvMCTest.segmentAnswers([imgQi, imgQiNC], countPage, countSquare, NUM_QUESTOES, qr))

                    qr = cvMCTest.setAnswarsOneLine(testAnswers, qr)  # deixa as respostas de cada quadro em uma linha

                    # alterado em 15/11/2023
                    if len(qr0) == 0:  # se usou questões do BD
                        qr = Utils.getQRanswersbyVariation(qr, exam)

                    qr = cvMCTest.studentGrade(qr, qr0)  # calcula nota final do aluno

                cvMCTest.saveCSVone(qr)  # salva arquivo CSV

                if (exam.exam_student_feedback == 'yes' and not 'ERROR' in qr['correct']):
                    cvMCTest.drawImageGAB(qr, strGAB, imgGAB_rgb)
                    cvMCTest.studentSendEmail(exam, qr, choiceReturnQuestions)  # cria pdf com feedback p/ aluno

            countPage += 1

        myflag = True
        for r in exam.classrooms.all():
            for d in r.discipline.courses.all():
                for i in d.institutes.all():
                    if myflag:
                        i.institute_exams_corrected += countCorrectExams
                        i.institute_questions_corrected += countCorrectQuestions
                        i.save()
                        myflag = False
                        break

        fzip = MYFILES + ".zip"

        try:
            os.system("rm " + fzip)
        except:
            pass

        if qr['onlyT']:  # questoes dissertativas e uma questao por pagina: salva a página em tmp
            os.system("mv " + BASE_DIR + "/tmp/_e" + str(exam.id) + str(request.user) + "*_q0/* " + mypath)
            os.system("zip -j " + fzip + " " + mypath + "/*")
            os.system("rm -rf " + mypath)
            os.system("rm " + mypath[:-5] + "*.png")

        else:
            path_to_file = BASE_DIR + "/" + file[:-4] + ".csv"
            # mypath = BASE_DIR + "/tmp/_e" + str(exam.id) + file[:-4]

            os.system("cp \'" + path_to_file + "\' " + MYFILES + "_RETURN__.csv")

            ### log begin
            f_log = "correct.log"
            if not os.path.exists(f_log):
                with open(f_log, 'w') as csvfile:
                    spamWriter = csv.writer(csvfile, delimiter=' ', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                    spamWriter.writerow("CORRECTIONS of MCTest")
            with open(f_log, 'a') as csvfile:
                spamWriter = csv.writer(csvfile, delimiter=' ', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                spamWriter.writerow(["\n" + str(request.user), ",", str(datetime.datetime.now())])
            os.system("cat >> correct.log " + path_to_file)
            ### log end

            ### IRT begin
            if exam.exam_print in ['both']:  # não é somente quadro de respostas
                try:
                    M = int(Utils.getNumMCQuestions(exam))  # Number of questions
                    X = pandas.read_csv(path_to_file, delimiter=',', usecols=['Q' + str(i) for i in range(1, M + 1)])
                    X.replace('', np.nan, inplace=True)
                    X.replace(' ', np.nan, inplace=True)
                    X.dropna(inplace=True)

                    # more statistis adapted of Profa. Dra. Denise Goya, from UFABC
                    # 31/03/2023
                    ANS = int(exam.exam_number_of_anwsers_question)
                    K = pandas.read_csv(path_to_file, delimiter=',', usecols=['K' + str(i) for i in range(1, M + 1)])
                    K.replace('', np.nan, inplace=True)
                    K.replace(' ', np.nan, inplace=True)
                    K.dropna(inplace=True)
                    K = K.to_numpy() // 10 ** ANS

                    acertos, erros = {}, {}
                    for q in X:  # for each question
                        i = int(q[1:]) - 1
                        for n, s in enumerate(X[q]):  # for each student
                            ki = K[n][i]
                            if len(str(s).split()[0]) == 1:
                                acertos[ki] = acertos.get(ki, 0) + 1
                            else:
                                erros[ki] = erros.get(ki, 0) + 1

                    # incluir chaves se nao existir
                    for k in set(acertos.keys()) | set(erros.keys()):
                        acertos[k] = acertos.get(k, 0)
                        erros[k] = erros.get(k, 0)

                    with open(MYFILES + '_RETURN_statistics.csv', 'w') as f:
                        f.write(f' id,  key, corr, fail, %corr, %fail\n')
                        for i, k in enumerate(sorted(acertos.keys())):
                            a, e = acertos[k], erros[k]
                            f.write(f'{i + 1:3d},{k:5d}, {a:4d}, {e:4d}, {a / (a + e):.3f}, {e / (a + e):.3f}\n')
                        f.close()

                    # irt - questoes ordenadas pelas chaves
                    chaves = sorted(acertos.keys())
                    dados = np.zeros((len(X), len(chaves)), dtype=int)
                    X0 = X.to_numpy()
                    for i, a in enumerate(X0):
                        for j, b in enumerate(a):
                            if len(X0[i, j].split()[0]) == 1:
                                dados[i, chaves.index(K[i, j])] = 1

                    N = len(X['Q1'])  # Number of students
                    with open(MYFILES + '_RETURN_irt.csv', 'w') as csvfile:
                        spamWriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                        for n in range(N):
                            spamWriter.writerow(dados[n])
                        csvfile.close()

                    os.system("python3 _irt_pymc3.py " + MYFILES + "_RETURN_irt.csv &")

                except:
                    messages.error(request, _("correctStudentsExam: Error in IRT or more Statists"))

            else:  # exames sem chaves - primeira página é o gabarito
                try:
                    M = int(Utils.getNumMCQuestions(exam))  # Number of questions
                    X = pandas.read_csv(path_to_file, delimiter=',', usecols=['Q' + str(i) for i in range(1, M + 1)])
                    X.replace('', np.nan, inplace=True)
                    X.replace(' ', np.nan, inplace=True)
                    X.dropna(inplace=True)

                    N = len(X['Q1'])  # Number of students
                    dados = np.zeros((N, M), dtype=int)
                    for q in X:  # for each question
                        for n, s in enumerate(X[q]):  # for each student
                            if len(str(s).split()[0]) == 1:
                                dados[n][int(q[1:]) - 1] = 1
                    N -= 1
                    dados = np.delete(dados, 0, 0)  # remove primeira linha com o gabarito

                    with open(MYFILES + '_RETURN_statistics.csv', 'w') as f:
                        f.write(f' id, corr, fail, aver, std, %corr, %fail\n')
                        media_colunas = np.mean(dados, axis=0)
                        desvio_padrao_colunas = np.std(dados, axis=0)
                        acertos = np.sum(dados, axis=0)
                        erros = N - np.sum(dados, axis=0)
                        for i in range(len(dados[0])):
                            a, e, m, s = acertos[i], erros[i], media_colunas[i], desvio_padrao_colunas[i]
                            f.write(
                                f'{i + 1:3d}, {a:4d}, {e:4d}, {m:.3f}, {s:.3f}, {a / (a + e):.3f}, {e / (a + e):.3f}\n')
                        f.close()

                    with open(MYFILES + '_RETURN_irt.csv', 'w') as csvfile:
                        spamWriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                        for n in range(N):
                            spamWriter.writerow(dados[n])
                        csvfile.close()

                    os.system("python3 _irt_pymc3.py " + MYFILES + "_RETURN_irt.csv &")

                except:
                    messages.error(request, _("correctStudentsExam: Error in IRT"))

            # IRT - end

            #

            myfiles = []
            for f in np.sort(glob.glob(MYFILES + "_RETURN_*.png")):
                myfiles.append(f)

            # incluir também os pdf enviados nos emails dos alunos
            path0 = BASE_DIR + "/pdfStudentEmail/studentEmail_e" + str(exam.id)
            os.system("zip -j " + path0 + ".zip " + path0 + "*.pdf")

            if True:  # len(myfiles):
                try:
                    os.remove(MYFILES + "*.zip")
                except Exception as e:
                    pass
                os.system("zip -j " + MYFILES + ".zip " + MYFILES + "_RETURN_* " + path0 + ".zip")
            # else:
            #     fzip = MYFILES + "_RETURN__.csv"

        try:
            # os.remove("{}.pdf".format(BASE_DIR + "/" + file[:-4]))

            # from datetime import datetime
            # data = datetime.today().strftime('%Y-%m-%d')
            # hora = datetime.now().time().strftime('%H-%M%s')
            data_hora = datetime.datetime.now()
            data_hora = str(data_hora).split('.')[0].replace(' ', '-')
            os.system(f"mv {filename[:-4]}.pdf tmp/{filename[:-4]}-{data_hora}.pdf")
            os.system(f"mv {filename[:-4]}.csv tmp/{filename[:-4]}-{data_hora}.csv")
            # os.remove("{}.csv".format(BASE_DIR + "/" + file[:-4]))
            os.system("rm " + MYFILES + "/*.png")
            if fzip[-3:] == 'zip':
                os.system("rm " + MYFILES + "_RETURN__.csv")
            pass
        except Exception as e:
            pass

    return serve(request, os.path.basename(fzip), os.path.dirname(fzip))


# for line in sys.stdin:
#     nome = unidecode.unidecode(line.split()[0])

#     print(nome,end="\t")
#     print(distro_table(nome),end="\n")

# nome = input()
# nome = unicodedata.normalize('NFKD', nome).encode('ascii','ignore').decode('ascii').split()
# nome = nome[0]+nome[-1]
# print(nome,end="\t")
# print(Utils.distro_table(nome),end="\n")
####################### HASH

@login_required
def generate_page(request, pk):
    print("generate_page-00-" + str(datetime.datetime.now()))
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    exam = get_object_or_404(Exam, pk=pk)
    context = {"students": exam}

    print("generate_page-01-" + str(datetime.datetime.now()))

    try:
        strVarExam = str(exam.variationsExams2.all()[0].id)
    except:
        strVarExam = '0'

    path_aux = BASE_DIR + "/pdfExam/report_Exam_" + str(pk) + "_varID_" + strVarExam
    path_to_file_REPORT = path_aux + "_sendMails.csv"
    path_to_file_STUDENTS = path_aux + "_students.csv"

    path_aux0 = BASE_DIR + "/pdfExam/_e" + str(pk) + "_varID_" + strVarExam
    path_to_file_VARIATIONS_VPL = path_aux0 + "_students_variations.csv"
    path_to_file_VARIATIONS = path_aux0 + "_variations.csv"
    path_to_file_ADAPTIVE_TEST = path_aux0 + '_adaptive_test.csv'
    path_to_file_ADAPTIVE_TEST_variations = path_aux0 + '_adaptive_test_variations_by_bloom.csv'

    if request.POST:
        countStudentsAll = 0
        # start = time.time()
        # tempoTeX = 0
        # tempoPDF = 0

        font_size = request.POST.get('font_size')
        choice_adaptive_test = request.POST.get('adaptative_test')

        st = Utils.validateProf(exam, request.user)
        if st != None:
            return HttpResponse(st)

        if exam.exam_print != 'answ' and len(exam.variationsExams2.all()) != int(exam.exam_variations):
            return HttpResponse(_('Create variations first'))

        print("generate_page-02-" + str(datetime.datetime.now()))

        numVariations = exam.variationsExams2.all().count()
        qr_answers = Utils.getQRanswers(exam.variationsExams2.all())

        if exam.exam_print != 'answ':
            d = exam.variationsExams2.all().first()
            exam0dict = eval(d.variation)
            numQM = len([v['type'] for v in exam0dict['variations'][0]['questions'] if v['type'] == 'QM'])
            numQT = len([v['type'] for v in exam0dict['variations'][0]['questions'] if v['type'] == 'QT'])

            if int(exam.exam_number_of_questions_text) and str(numQT) != str(exam.exam_number_of_questions_text):
                messages.error(request, _('ERROR in generate_page, number_of_questions_text!!!!  ') +
                               str(numQT) + '<>' + str(exam.exam_number_of_questions_text))
                return render(request, 'exam/exam_errors.html', {})
            if int(Utils.getNumMCQuestions(exam)) and str(numQM) != str(Utils.getNumMCQuestions(exam)):
                messages.error(request, _('ERROR in generate_page, number_of_QM!!!! - no questions: ') +
                               str(numQM) + '<>' + str(Utils.getNumMCQuestions(exam)))
                return render(request, 'exam/exam_errors.html', {})

        data_hora = datetime.datetime.now()
        data_hora = str(data_hora).split('.')[0].replace(' ', ' - ')

        storage = get_messages(request)
        for message in storage:
            return render(request, 'exam/exam_errors.html', {})

        strAnswerSheet = Utils.drawAnswerSheet(request, exam)
        strCircles = Utils.drawCircles()
        strInstructions = Utils.drawInstructions(exam)

        strf = BASE_DIR + "/pdfExam/_e" + str(exam.id) + "*"  # remover _eID*
        try:
            for fi in glob.glob(strf):
                os.remove(fi)
            pass
        except Exception as e:
            pass

        listVariations = [['Room', 'ID', 'Name', 'Variation', 'SumLatestGrades']]
        maxStudentsClass = 0  # if maxStudentsClass < exam_variations, save all students in CSV file, for VPL
        for room in exam.classrooms.all():  ############## PARA CADA TURMA
            if maxStudentsClass < len(room.students.all()):
                maxStudentsClass = len(room.students.all())

            if len(room.students.all()) == 0:
                messages.error(request, _('ERROR in generate_page, class with zero students: ') +
                               str(room.classroom_code))
                return render(request, 'exam/exam_errors.html', {})

        ####################################
        ### PARA TESTE ADAPTATIVO 17/11/2023

        if exam.exam_print != 'answ' and int(choice_adaptive_test) and Utils.getNumMCQuestions(exam):
            maxStudentsClassGrade = Utils.createAdaptativeTest(request, exam, choice_adaptive_test,
                                                               path_to_file_ADAPTIVE_TEST)

            variantExam_rankin_bloom_sort = Utils.createCariantExam_rankin_bloom_sort(
                request, exam, path_to_file_ADAPTIVE_TEST_variations)

            df = pd.read_csv(path_to_file_ADAPTIVE_TEST, delimiter=',')

        ### PARA TESTE ADAPTATIVO 17/11/2023 - FIM
        ##########################################

        # create directory with key is room
        distribute_students_by_room_random = {}
        for room in exam.classrooms.all():  ############## PARA CADA TURMA
            distribute_students = []

            for s in room.students.all():
                stname = s.student_name.split(' ')
                stname = stname[0] + ' ' + stname[-1]  # USE FULL NAME
                stname = stname.upper()  # CHANGED: 29/06/22
                if not stname in distribute_students:
                    distribute_students.append(stname)

            distribute_students_random = []
            if int(exam.exam_variations) < maxStudentsClass:
                for s in distribute_students:
                    try:
                        hash_num = Utils.distro_table(s)
                    except:
                        messages.error(request, _('ERROR in Utils.distro_table, student: ') + s)
                        return render(request, 'exam/exam_errors.html', {})
                    distribute_students_random.append([s, hash_num])
            else:
                # distribute students without repetition
                vetRandomRoom = np.arange(int(exam.exam_variations))
                np.random.shuffle(vetRandomRoom)
                vetRandomRoom = vetRandomRoom[:len(distribute_students)]
                for s in distribute_students:

                    hash_num = distribute_students.index(s)
                    hash_num = vetRandomRoom[hash_num]

                    # verify if exist name/surname
                    for key, list_of_values in distribute_students_by_room_random.items():
                        ss = np.array(list_of_values)
                        sss = ss[:, 0]
                        if s in sss:
                            hash_num = np.where(sss == s)
                            hash_num = int(ss[hash_num, 1][0])
                            break

                    distribute_students_random.append([s, hash_num])

            distribute_students_by_room_random[room.id] = distribute_students_random

        for room in exam.classrooms.all():  ############## PARA CADA TURMA
            file_name = "_e" + str(exam.id) + "_varID_" + strVarExam + "_class_" + str(room.id)
            file_name = file_name.replace(" ", "")

            fileExamName = file_name + ".tex"

            # /home/fz/django_webmctest/mctest/pdfExam/_e84_EE teste_PClass_Prova1.pdf
            strALL = ''

            distribute_students_random = np.array(distribute_students_by_room_random[room.id])

            countStudents = 0
            countVariations = 0
            for s in room.students.all():  ############## PARA CADA ESTUDANTE DA TURMA
                # start0 = time.time()
                strSTUDENT = ''
                countStudents += 1
                countVariations += 1

                stname = s.student_name.split(' ')
                stname = stname[0] + ' ' + stname[-1]  # USE FULL NAME
                stname = stname.upper()  # CHANGED: 29/06/22

                indStudent = np.where(distribute_students_random[:, 0] == stname)

                hash_num = int(distribute_students_random[indStudent, 1][0])
                if hash_num == -1:
                    messages.error(request, _('ERROR in distro_table!!!! - student name:' + s.student_name))
                    return render(request, 'exam/exam_errors.html', {})

                var_hash = hash_num % int(exam.exam_variations)

                ################################### 18/11/2023 pega hash adaptativo
                nota_student = 0
                if exam.exam_print != 'answ' and int(choice_adaptive_test) and Utils.getNumMCQuestions(
                        exam) and maxStudentsClassGrade:  # novo var_hash somente se maxStudentsClassGrade>0

                    var_hash, nota_student = Utils.getHashAdaptative(request, exam, df, variantExam_rankin_bloom_sort,
                                                                     s.student_name, maxStudentsClassGrade)

                ################################### 18/11/2023 pega hash adaptativo - FIM

                listVariations.append(
                    [room.classroom_code, s.student_ID, s.student_name, var_hash, nota_student])

                myqr = Utils.defineQRcode(exam, room, s.student_ID, strVarExam, str(var_hash))
                strQuestions = ''
                if Utils.validateNumQuestions(request, exam):  # pegar tb o que foi sorteado

                    if exam.exam_print != 'answ':
                        myqr.append(qr_answers[var_hash])  # inclui as respostas

                    strQuestions += Utils.drawQuestions(request, myqr,
                                                        exam, room, s.student_ID, s.student_name,
                                                        var_hash, data_hora, font_size)


                else:
                    messages.error(request, _('ERROR in validateNumQuestions!!!!'))

                storage = get_messages(request)
                for message in storage:
                    return render(request, 'exam/exam_errors.html', {})

                if exam.exam_print in ['answ', 'both']:
                    if int(Utils.getNumMCQuestions(exam)):
                        strSTUDENT += Utils.drawJumpPage()
                        strSTUDENT += strCircles
                        strSTUDENT += Utils.getHeader(request, exam, room, s.student_ID, s.student_name, myqr,
                                                      data_hora, font_size)
                        strSTUDENT += strAnswerSheet
                        strSTUDENT += strCircles
                        '''
                        hash_student = Utils.distro_table(s.student_name)
                        strSTUDENT += '\n\n \\hspace{3cm} \\tiny{hash:' + str(hash_student) + \
                                      ' model:' + str(hash_student % int(exam.exam_variations)) + '}\n\n'
                        '''
                        strSTUDENT += strInstructions
                        if exam.exam_print_eco == 'no' and exam.exam_print == 'both':
                            strSTUDENT += "\n\n\\newpage\n\n"
                            strSTUDENT += Utils.getHeader(request, exam, room, s.student_ID, s.student_name, myqr,
                                                          data_hora, font_size)
                        if exam.exam_print == 'both':
                            strSTUDENT += strQuestions
                if exam.exam_print in ['ques']:
                    if int(exam.exam_number_of_questions_text):
                        if exam.exam_print_eco == 'yes':
                            strSTUDENT += Utils.getHeader(request, exam, room, s.student_ID, s.student_name, myqr,
                                                          data_hora, font_size)
                            strSTUDENT += strInstructions
                        strSTUDENT += strQuestions

                strALL += strSTUDENT

                if exam.exam_student_feedback == 'yes':  ##################### cria um tex para cada estudante >> email
                    fileExamNameSTUDENT = file_name + '_' + s.student_ID + '.tex'
                    try:
                        with open(fileExamNameSTUDENT, 'w') as fileExamSTUDENT:
                            fileExamSTUDENT = open(fileExamNameSTUDENT, 'w')
                            fileExamSTUDENT.write(Utils.getBegin(font_size))
                            fileExamSTUDENT.write(strSTUDENT)
                            fileExamSTUDENT.write("\\end{document}")
                            fileExamSTUDENT.close()
                    except:
                        messages.error(request,
                                       _('ERROR - watch out for special characters in exam name') + ': ' + file_name)
                        return render(request, 'exam/exam_errors.html', {})

                    myPATH = "pdfExam"
                    if not Utils.genTex(fileExamNameSTUDENT, myPATH):
                        messages.error(request, _('ERROR in genTex') + ': ' + fileExamNameSTUDENT)

                    myFILE = BASE_DIR + "/" + myPATH + "/" + fileExamNameSTUDENT[:-4] + '.pdf'
                    email = s.student_email
                    enviaOK = cvMCTest.sendMail(myFILE, "Exam by MCTest", email, str(s.student_name))
                    with open(path_to_file_REPORT, 'a+') as data:  # acrescenta no final do csv a cada envio
                        writer = csv.writer(data)
                        writer.writerow(
                            [fileExamNameSTUDENT[:-4] + '.pdf', s.student_ID, email + enviaOK, s.student_name,
                             data_hora])
                    # apos enviar, remove do disco
                    try:
                        os.remove(myFILE)
                        os.remove(myFILE[:-3] + 'tex')  # fz add in 2022/8/1
                    except:
                        messages.error(request,
                                       _('ERROR - watch out for special characters in exam name') + ': ' + file_name)
                        return render(request, 'exam/exam_errors.html', {})

                #### Final dos estudantes de uma classe ###

            if not countStudents:
                pass
                # messages.error(request, _('Error: there is no student in classroom(s).'))
                # return render(request, 'exam/exam_errors.html', {})

            countStudentsAll += countStudents
            try:
                with open(fileExamName, 'w') as fileExam:
                    fileExam = open(fileExamName, 'w')
                    fileExam.write(Utils.getBegin(font_size))
                    fileExam.write(strALL)
                    fileExam.write("\\end{document}")
                    fileExam.close()
            except:
                messages.error(request,
                               _('ERROR - watch out for special characters in exam name') + ': ' + fileExamName[:-4])
                return render(request, 'exam/exam_errors.html', {})

            # start1 = time.time()
            if not Utils.genTex(fileExamName, "pdfExam"):
                messages.error(request, _('ERROR in genTex') + ': ' + fileExamName)
                return render(request, 'exam/exam_errors.html', {})

            ### Final das classes selecionadas ###

        if exam.exam_student_feedback == 'yes':  # envia um relatório dos email enviados
            cvMCTest.sendMail(path_to_file_REPORT, "REPORT", str(request.user), "name")

        for d in room.discipline.courses.all():
            for i in d.institutes.all():
                i.institute_exams_generated += countStudentsAll
                i.save()
                break

        # problem with permission ...
        path = os.getcwd()
        getuser = path.split('/')
        getuser = getuser[1]
        getuser = getuser + ':' + getuser
        os.system('chown -R ' + getuser + ' ' + path + ' .')
        os.system('chgrp -R ' + getuser + ' ' + path + ' .')

        anexos = []

        # send file by email with variation of each student
        if int(exam.exam_variations) > 0 and exam.exam_print != 'answ':
            with open(path_to_file_VARIATIONS, 'w', newline='') as file_var:
                writer = csv.writer(file_var, delimiter=',', quoting=csv.QUOTE_NONE, quotechar='',
                                    lineterminator='\n')
                writer.writerows(listVariations)
            anexos.append(path_to_file_VARIATIONS) # util para quando tem várias turmas

            aux = np.array(listVariations)
            with open(path_to_file_VARIATIONS_VPL, 'w', newline='') as file_var:
                writer = csv.writer(file_var, delimiter=',', quoting=csv.QUOTE_NONE, quotechar='',
                                    lineterminator='\n')
                aux = aux[:, 2:4]  # get columns aluno e variacao
                writer.writerows(aux)  # return name; variation
            anexos.append([path_to_file_VARIATIONS_VPL])

        message_cases = 'Following all variations of each student and pdf/tex\n\n'
        if exam.classrooms.all().count() == 1:
            path_to_file = BASE_DIR + "/pdfExam/" + file_name + ".pdf"
            anexos.append(path_to_file)
            anexos.append(path_to_file[:-3] + "tex")
        else:
            fzip = BASE_DIR + "/pdfExam/_e" + str(exam.id) + "_" + str(request.user) + ".zip"
            # zipar todos os exames das turmas
            os.system("zip -j " + fzip + " " + BASE_DIR + "/pdfExam/_e" + str(exam.id) + "*")

            os.system('rm -rf ' + BASE_DIR + "/pdfExam/_e" + str(exam.id) + "*.tex")
            path_to_zip = os.path.dirname(fzip) + "/" + os.path.basename(fzip)
            anexos.append(path_to_zip)

        if exam.exam_print != 'answ' and int(choice_adaptive_test) and Utils.getNumMCQuestions(exam):
            anexos.append(path_to_file_ADAPTIVE_TEST)
            anexos.append(path_to_file_ADAPTIVE_TEST_variations)

        try:
            enviaOK = cvMCTest.envia_email(webMCTest_SERVER,
                                           587,
                                           webMCTest_FROM,
                                           webMCTest_PASS,
                                           str(request.user),
                                           'MCTest: Templates and Variations: ' + str(
                                               exam.exam_name) + ' - ' + data_hora,
                                           message_cases, anexos)
        except:
            pass

        # mostra em uma nova aba o pdf ou faz download do zip
        if exam.classrooms.all().count() == 1:
            try:
                path_to_file = BASE_DIR + "/pdfExam/" + file_name + ".pdf"
                return serve(request, os.path.basename(path_to_file), os.path.dirname(path_to_file))
            except:
                messages.error(request, _('ERROR - watch out for special characters in exam name') + ': ' + file_name)
                return render(request, 'exam/exam_errors.html', {})
        else:
            return serve(request, os.path.basename(fzip), os.path.dirname(fzip))

        # print(">>>>>>>>>>>>>>>>>>>>>>>>> TIME <<<<<<<<<<<<<<<<<<<<<<<<<")
        # print ("s - tex/s", countStudents, (start1-start)/countStudents)
        # print("  tex:", tempoTeX)
        # print("latex:", tempoPDF)
        # print("  ALL:", time.time() - start)


@login_required
def SerializersExam(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    exam_inst = get_object_or_404(Exam, pk=pk)
    questions = exam_inst.questions
    classrooms = exam_inst.classrooms

    return render(request, 'exam/exam_list.html', {})

@login_required
def UpdateExam(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    exam_inst = get_object_or_404(Exam, pk=pk)
    classrooms = exam_inst.classrooms

    # NÃO CONSEGUI INCLUIR EM UM BD JÁ EXISTENTE
    topics = exam_inst.topics

    questions = exam_inst.questions

    try:
        variation_ID = exam_inst.variationsExams2.all()[0].id
    except:
        variation_ID = 0

    st = Utils.validateProf(exam_inst, request.user)
    if st is not None:
        return HttpResponse(st)
        # messages.error(request, _('Error: there is no selected classroom(s).'))
        # return render(request, 'exam/exam_errors.html', {})

    if request.method == 'POST':
        form = UpdateExamForm(request.POST)
        if form.is_valid():
            exam_inst.exam_name = form.cleaned_data['exam_name']
            exam_inst.exam_number_of_questions_var1 = form.cleaned_data['exam_number_of_questions_var1']
            exam_inst.exam_number_of_questions_var2 = form.cleaned_data['exam_number_of_questions_var2']
            exam_inst.exam_number_of_questions_var3 = form.cleaned_data['exam_number_of_questions_var3']
            exam_inst.exam_number_of_questions_var4 = form.cleaned_data['exam_number_of_questions_var4']
            exam_inst.exam_number_of_questions_var5 = form.cleaned_data['exam_number_of_questions_var5']
            exam_inst.exam_number_of_anwsers_question = form.cleaned_data['exam_number_of_anwsers_question']
            exam_inst.exam_number_of_questions_text = form.cleaned_data['exam_number_of_questions_text']
            exam_inst.exam_variations = form.cleaned_data['exam_variations']
            exam_inst.exam_max_questions_square = form.cleaned_data['exam_max_questions_square']
            exam_inst.exam_max_squares_horizontal = form.cleaned_data['exam_max_squares_horizontal']
            exam_inst.exam_stylesheet = form.cleaned_data['exam_stylesheet']
            exam_inst.exam_print = form.cleaned_data['exam_print']
            exam_inst.exam_print_eco = form.cleaned_data['exam_print_eco']
            exam_inst.exam_student_feedback = form.cleaned_data['exam_student_feedback']
            # exam_inst.exam_room = form.cleaned_data['exam_room']
            exam_inst.exam_hour = form.cleaned_data['exam_hour']
            exam_inst.exam_term = form.cleaned_data['exam_term']
            # exam_inst.exam_output = form.cleaned_data['exam_output']
            exam_inst.exam_who_created = form.cleaned_data['exam_who_created']
            # exam_inst.exam_profs_header = form.cleaned_data['exam_profs_header']
            exam_inst.exam_instructions = form.cleaned_data['exam_instructions']

            classrooms = form.cleaned_data['classrooms']
            for q in exam_inst.classrooms.all():
                exam_inst.classrooms.remove(q)
            exam_inst.classrooms.add(*classrooms)

            # NÃO CONSEGUI INCLUIR EM UM BD JÁ EXISTENTE
            topics = form.cleaned_data['topics']
            for q in exam_inst.topics.all():
                exam_inst.topics.remove(q)
            exam_inst.topics.add(*topics)

            questions = form.cleaned_data['questions']
            # raise Http404(len(exam_inst.questions.all()))
            for q in exam_inst.questions.all():
                exam_inst.questions.remove(q)
            exam_inst.questions.add(*questions)

            exam_inst.save()
            return HttpResponseRedirect('/exam/exam/' + str(pk) + '/update/')
        else:
            messages.error(request,str(form.errors))
            return render(request, 'exam/exam_errors.html', {'form': form})

    else:
        # NÃO CONSEGUI INCLUIR EM UM BD JÁ EXISTENTE
        # topics
        tt = topics.filter().values_list('id', flat=True)
        qq = questions.filter(topic__id__in=tt).values_list('id', flat=True)

        form = UpdateExamForm(initial={
            'exam_name': exam_inst.exam_name,
            'classrooms': [c for c in classrooms.filter().values_list('id', flat=True)],
            'topics': tt,
            'questions': qq,
            'exam_number_of_questions_var1': exam_inst.exam_number_of_questions_var1,
            'exam_number_of_questions_var2': exam_inst.exam_number_of_questions_var2,
            'exam_number_of_questions_var3': exam_inst.exam_number_of_questions_var3,
            'exam_number_of_questions_var4': exam_inst.exam_number_of_questions_var4,
            'exam_number_of_questions_var5': exam_inst.exam_number_of_questions_var5,
            'exam_number_of_anwsers_question': exam_inst.exam_number_of_anwsers_question,
            'exam_number_of_questions_text': exam_inst.exam_number_of_questions_text,
            'exam_variations': exam_inst.exam_variations,
            'exam_max_questions_square': exam_inst.exam_max_questions_square,
            'exam_max_squares_horizontal': exam_inst.exam_max_squares_horizontal,
            'exam_stylesheet': exam_inst.exam_stylesheet,
            'exam_print': exam_inst.exam_print,
            'exam_print_eco': exam_inst.exam_print_eco,
            'exam_student_feedback': exam_inst.exam_student_feedback,
            # 'exam_room': exam_inst.exam_room,
            'exam_hour': exam_inst.exam_hour,
            'exam_term': exam_inst.exam_term,
            # 'exam_output': exam_inst.exam_output,
            'exam_who_created': exam_inst.exam_who_created,
            # 'exam_profs_header': exam_inst.exam_profs_header,
            'exam_instructions': exam_inst.exam_instructions,
        })

    return render(request, 'exam/exam_update2.html', {
        'form': form,
        'examinst': exam_inst,
        'variation_ID': variation_ID,
    })


##########################################################
class ExamListView(generic.ListView):
    model = Exam
    fields = '__all__'
    # paginate_by = 100
    success_url = '/exam/exams'
    template_name = 'exam/exam_list.html'

    def get_queryset(self):
        li = Exam.objects.filter(classrooms__discipline__discipline_profs=self.request.user)
        # qs = Exam.objects.none()
        # t = []
        # for e in li:
        #     if not e.pk in t:
        #         t.append(e.pk)
        return li.order_by('exam_name').distinct()

    def form_valid(self, form):
        if not Exam.objects.filter(classrooms__discipline__discipline_profs=self.request.user):
            messages.error(self.request, _('ExamListView: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})


class ExamUpdate(UpdateView):
    model = Exam
    template_name = 'exam/exam_update2.html'
    fields = '__all__'
    success_url = '/exam/myexams'

    def get_queryset(self):
        return Exam.objects.filter(classrooms__discipline__discipline_profs=self.request.user).distinct()

    def form_valid(self, form):
        if not Exam.objects.filter(classrooms__discipline__discipline_profs=self.request.user):
            messages.error(self.request, _('ExamUpdate: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})


class ExamDetailView(generic.DetailView):
    model = Exam
    template_name = 'exam/exam_detail.html'

    def get_queryset(self):
        li = Exam.objects.filter(classrooms__discipline__discipline_profs=self.request.user)
        return li.order_by('exam_name').distinct()

    def form_valid(self, form):
        if not Exam.objects.filter(classrooms__discipline__discipline_profs=self.request.user):
            messages.error(self.request, _('ExamDetailView: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})


class ExamCreate(CreateView):
    form_class = ExamCreateForm

    template_name = 'exam/exam_create.html'
    success_url = '/exam/myexams'

    def get_form_kwargs(self):
        kwargs = super(ExamCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return Exam.objects.filter(classrooms__discipline__discipline_profs=self.request.user)  # .distinct()

    def form_valid(self, form):
        form.instance.exam_who_created = self.request.user
        t = datetime.date.today()
        form.instance.exam_hour = str(t.year) + "-" + str(t.month) + "-" + str(t.day) + " 02:00:00"
        return super(ExamCreate, self).form_valid(form)


class ExamDelete(DeleteView):
    model = Exam
    template_name = 'exam/exam_confirm_delete.html'
    success_url = reverse_lazy('exam:myexams')

    def get_queryset(self):
        return Exam.objects.filter(exam_who_created=self.request.user).distinct()

    def form_valid(self, form):
        if not Exam.objects.filter(classrooms__discipline__discipline_profs=self.request.user):
            messages.error(self.request, _('ClassroomUpdate: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})

        return super().form_valid(form)


class LoanedExamByUserListView(LoginRequiredMixin, generic.ListView):
    model = Exam
    template_name = 'exam/exam_list_who_created_user.html'

    # paginate_by = 100

    def get_queryset(self):
        li = Exam.objects.filter(exam_who_created=self.request.user)
        # qs = Exam.objects.none()
        # t = []
        # for e in li:
        #     if not e.pk in t:
        #         t.append(e.pk)
        return li.order_by('exam_name').distinct()
