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
# from rest_framework import viewsets#serializers
import csv
import datetime
import glob
import os
import re

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
from pdf2image import convert_from_path
from tablib import Dataset

from exam.CVMCTest import cvMCTest
from exam.UtilsLatex import Utils
from mctest.settings import BASE_DIR
from mctest.settings import webMCTest_FROM
from mctest.settings import webMCTest_PASS
from mctest.settings import webMCTest_SERVER
from .forms import UpdateExamForm
from .models import Exam


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

    if request.method == 'POST':
        dataset = Dataset()
        try:
            file = request.FILES['myfilePDF']
        except:
            messages.error(request, _('correctStudentsExam: choose a PDF file with scanned exams!'))
            return render(request, 'exam/exam_errors.html', {})

        # if str(file).replace(' ','') != file:
        #    messages.error(request,  _('correctStudentsExam: remove the spaces and symbols in file name.'))
        #    return render(request, 'exam/exam_errors.html', {})

        fs = FileSystemStorage()
        file0 = str(file.name)
        file0 = file0.replace(' ', '')

        file0 = re.sub('[^A-Za-z0-9._-]+', '', file0)  # remove special characters

        filename = fs.save(file0, file)
        # uploaded_file_url = fs.url(filename)

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

        passou = False

        try:
            imgs = cvMCTest.get_images_from_pdf(file)
            passou = True
        except:
            pass
            # messages.error(request, _("correctStudentsExam: Error in read PDF: ") + str(file))
            # return render(request, 'exam/exam_errors.html', {})

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
            img = img0 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            cvMCTest.centroidsMarked = []
            countCorrectExams += 1

            DEBUG = False

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

            qr['exam_print'] = exam.exam_print

            if int(Utils.getNumMCQuestions(exam) == 0):
                qr['onlyT'] = True
            else:
                qr['onlyT'] = False

            qr['file'] = file
            qr['page'] = countPage
            qr['max_questions_square'] = exam.exam_max_questions_square
            qr['user'] = request.user.email
            # qr['correct'] = '0'
            # qr['invalid'] = '0'
            # qr['grade'] = '0'

            if not countPage:  # para correcoes sem questoes, com apenas quadro de reposta,
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

                    qr = cvMCTest.studentGrade(qr, qr0)  # calcula nota final do aluno

                cvMCTest.saveCSVone(qr)  # salva arquivo CSV
                # cvMCTest.writeCSV(qr)  # imprime conteÃºdo do CSV
                # raise Http404(qr)

                if (exam.exam_student_feedback == 'yes'):
                    # raise Http404(qr)
                    cvMCTest.drawImageGAB(qr, strGAB, imgGAB_rgb)
                    cvMCTest.studentSendEmail(qr)  # cria pdf com feedback p/ aluno

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
            try:
                M = int(Utils.getNumMCQuestions(exam))  # Number of questions
                X = pandas.read_csv(path_to_file, delimiter=',', usecols=[str(i) for i in range(1, M + 1)])
                N = len(X['1'])  # Number of students
                dados = np.zeros((N, M), dtype=int)
                for q in X:  # for each question
                    for n, s in enumerate(X[q]):  # for each student
                        if len(str(s).split()[0]) == 1:
                            dados[n][int(q) - 1] = 1

                with open(MYFILES + '_irt.csv', 'w') as csvfile:
                    spamWriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                    for n in range(N):
                        spamWriter.writerow(dados[n])

                os.system("python3 _irt_pymc3.py " + MYFILES + "_irt.csv &")
            except:
                pass
            ### IRT end

            myfiles = []
            for f in np.sort(glob.glob(MYFILES + "_RETURN_*.png")):
                myfiles.append(f)

            if len(myfiles):
                try:
                    os.remove(MYFILES + "*.zip")
                except Exception as e:
                    pass
                os.system("zip -j " + MYFILES + ".zip " + MYFILES + "_RETURN_*")
            else:
                fzip = MYFILES + "_RETURN__.csv"

        try:
            # os.remove("{}.pdf".format(BASE_DIR + "/" + file[:-4]))
            os.remove("{}.csv".format(BASE_DIR + "/" + file[:-4]))
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

    path_aux = BASE_DIR + "/report_Exam_" + str(pk)
    path_to_file_REPORT = path_aux + ".csv"
    path_to_file_VARIATIONS = path_aux + "_variations.csv"
    path_to_file_VARIATIONS_VPL = BASE_DIR + "/students_variations.csv"

    path_to_file_TEMPLATES = path_aux + "_templates.csv"
    path_to_file_STUDENTS = path_aux + "_students.csv"
    # raise Http404("oi00")
    if request.POST:
        countStudentsAll = 0
        # start = time.time()
        # tempoTeX = 0
        # tempoPDF = 0
        # Utils.validateProf(exam, request.user)
        st = Utils.validateProf(exam, request.user)
        if st != None:
            return HttpResponse(st)
        print("generate_page-02-" + str(datetime.datetime.now()))
        listao = []  ############ gera X variacoes de exames
        db_questions_all = []
        for i in range(int(exam.exam_variations)):
            [qr_answers, str1, QT, db_questions] = Utils.drawQuestionsVariations(request, exam, request.user, Utils.getTopics(exam))
            db_questions_all.append(db_questions)
            listao.append([qr_answers, str1, QT])

        data_hora = datetime.datetime.now()
        data_hora = str(data_hora).split('.')[0].replace(' ', ' - ')

        storage = get_messages(request)
        for message in storage:
            return render(request, 'exam/exam_errors.html', {})

        strAnswerSheet = Utils.drawAnswerSheet(exam)

        strCircles = Utils.drawCircles()
        strInstructions = Utils.drawInstructions(exam)

        strf = BASE_DIR + "/pdfExam/_e" + str(exam.id) + "*"  # remover _eID*
        try:
            for fi in glob.glob(strf):
                os.remove(fi)
            pass
        except Exception as e:
            pass

        # messages.debug(request, '%s SQL statements were executed.' % 45)
        # messages.info(request, 'Three credits remain in your account.')
        # messages.success(request, 'Profile details updated.')
        # messages.warning(request, 'Your account expires in three days.')
        # messages.error(request, 'Document deleted.')
        # return render(request, 'exam/exam_errors.html', {})
        # raise Http404(exam.classrooms.all())
        listVariations = [['Room', 'ID', 'Name', 'Variation']]
        maxStudentsClass = 0  # if maxStudentsClass < exam_variations, save all students in CSV file, for VPL
        for room in exam.classrooms.all():  ############## PARA CADA TURMA
            if maxStudentsClass < len(room.students.all()):
                maxStudentsClass = len(room.students.all())

        for room in exam.classrooms.all():  ############## PARA CADA TURMA
            file_name = "_e" + str(
                exam.id) + "_" + room.classroom_code + "_" + room.classroom_type + "_" + exam.exam_name.replace(" ", "")
            file_name = file_name.replace(" ", "")

            fileExamName = file_name + ".tex"

            # /home/fz/django_webmctest/mctest/pdfExam/_e84_EE teste_PClass_Prova1.pdf
            strALL = ''

            countStudents = 0
            countVariations = 0
            for s in room.students.all():  ############## PARA CADA ESTUDANTE DA TURMA
                # start0 = time.time()
                strSTUDENT = ''
                countStudents += 1
                countVariations += 1
                myqr = Utils.defineQRcode(exam, room, s.student_ID, s.student_name)
                strQuestions = ''
                if Utils.validateNumQuestions(request, exam):  # pegar tb o que foi sorteado

                    if int(exam.exam_variations) < maxStudentsClass:
                        hash_num = Utils.distro_table(s.student_name)
                    else:
                        hash_num = countStudents - 1  # para iniciar de zero

                    listVariations.append(
                        [room.classroom_code, s.student_ID, s.student_name, hash_num % int(exam.exam_variations)])

                    if hash_num == -1:
                        messages.error(request, _('ERROR in distro_table!!!! - student name:' + s.student_name))
                        return render(request, 'exam/exam_errors.html', {})

                    strQuestions += Utils.drawQuestions(request,  # countStudents
                                                        listao[hash_num % int(exam.exam_variations)],
                                                        # uma variacao de prova por aluno
                                                        exam, room, s.student_ID, s.student_name, request.user,
                                                        hash_num % int(exam.exam_variations), data_hora)
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
                                                      data_hora)
                        strSTUDENT += strAnswerSheet
                        strSTUDENT += strCircles
                        '''
                        strSTUDENT += '\n\n \\hspace{3cm} \\tiny{hash:' + \
                                      str(Utils.distro_table(s.student_name)) + \
                                      ' model:' + str(Utils.distro_table(s.student_name) % int(exam.exam_variations)) \
                                      + '}\n\n'
                        '''
                        strSTUDENT += strInstructions
                        if exam.exam_print_eco == 'no' and exam.exam_print == 'both':
                            strSTUDENT += "\n\n\\newpage\n\n"
                            strSTUDENT += Utils.getHeader(request, exam, room, s.student_ID, s.student_name, myqr,
                                                          data_hora)
                        if exam.exam_print == 'both':
                            strSTUDENT += strQuestions
                if exam.exam_print in ['ques']:
                    if int(exam.exam_number_of_questions_text):
                        if exam.exam_print_eco == 'yes':
                            strSTUDENT += Utils.getHeader(request, exam, room, s.student_ID, s.student_name, myqr,
                                                          data_hora)
                            strSTUDENT += strInstructions
                        strSTUDENT += strQuestions

                strALL += strSTUDENT

                if exam.exam_student_feedback == 'yes':  ##################### cria um tex para cada estudante >> email
                    fileExamNameSTUDENT = file_name + '_' + s.student_ID + '.tex'
                    with open(fileExamNameSTUDENT, 'w') as fileExamSTUDENT:
                        fileExamSTUDENT = open(fileExamNameSTUDENT, 'w')
                        fileExamSTUDENT.write(Utils.getBegin())
                        fileExamSTUDENT.write(strSTUDENT)
                        fileExamSTUDENT.write("\\end{document}")
                        fileExamSTUDENT.close()
                    myPATH = "pdfExam"
                    Utils.genTex(fileExamNameSTUDENT, myPATH)
                    myFILE = BASE_DIR + "/" + myPATH + "/" + fileExamNameSTUDENT[:-4] + '.pdf'
                    email = s.student_email
                    cvMCTest.sendMail(myFILE, "Exam by MCTest", email, str(s.student_name))
                    with open(path_to_file_REPORT, 'a') as data:  # acrescenta no final do csv a cada envio
                        writer = csv.writer(data)
                        writer.writerow(
                            [fileExamNameSTUDENT[:-4] + '.pdf', s.student_ID, email, s.student_name, data_hora])

                #### Final dos estudantes de uma classe ###

            if exam.exam_student_feedback == 'yes':  # envia um relatório dos email enviados
                cvMCTest.sendMail(path_to_file_REPORT, "REPORT", str(request.user), "name")
                os.remove(path_to_file_REPORT)

            if not countStudents:
                messages.error(request, _('Error: there is no student in classroom(s).'))
                return render(request, 'exam/exam_errors.html', {})

            countStudentsAll += countStudents

            with open(fileExamName, 'w') as fileExam:
                fileExam = open(fileExamName, 'w')
                fileExam.write(Utils.getBegin())
                fileExam.write(strALL)
                fileExam.write("\\end{document}")
                fileExam.close()

            # start1 = time.time()
            Utils.genTex(fileExamName, "pdfExam")

            ### Final das classes selecionadas ###

        for d in room.discipline.courses.all():
            for i in d.institutes.all():
                i.institute_exams_generated += countStudentsAll
                i.save()
                break

        try:
            path_to_file_VARIATIONS_DB_aiken = path_aux + "_variations_DB_aiken.txt"
            Utils.createFileDB_aiken(exam, db_questions_all, path_to_file_VARIATIONS_DB_aiken)

            path_to_file_VARIATIONS_DB_xml = path_aux + "_variations_DB.xml"
            Utils.createFileDB_xml(exam, db_questions_all, path_to_file_VARIATIONS_DB_xml)

            Utils.createFileTemplates(exam, listao, path_to_file_TEMPLATES)
            message_cases = 'Following all templates and variations\n\n'
            anexos = [path_to_file_TEMPLATES, path_to_file_VARIATIONS_DB_aiken, path_to_file_VARIATIONS_DB_xml]

            if int(exam.exam_variations) > 0:  # send file by email with variation of each student
                with open(path_to_file_VARIATIONS, 'w', newline='') as file_var:
                    writer = csv.writer(file_var, delimiter=',', quoting=csv.QUOTE_NONE, quotechar='',
                                        lineterminator='\n')
                    writer.writerows(listVariations)
                anexos.append(path_to_file_VARIATIONS)
                # auxSTR = 'In the attached file are the exam variations per student \n-----'
                # cvMCTest.sendMail(path_to_file_VARIATIONS, auxSTR, str(request.user), str('Professor'))

            cvMCTest.envia_email(webMCTest_SERVER,
                                 587,
                                 webMCTest_FROM,
                                 webMCTest_PASS,
                                 str(request.user),
                                 'MCTest: Templates and Variations: ' + str(exam.exam_name) + ' - ' + data_hora,
                                 message_cases, anexos)
        except:
            pass

        print("generate_page-03-" + str(datetime.datetime.now()))
        # send by email all case tests of moodle
        cases = Utils.get_cases(listao)
        if len(cases['id'] and cases['id'][0]):
            print("generate_page-04-" + str(datetime.datetime.now()))
            message_cases = _('Dear') + '\n\n'
            message_cases += _(
                'This message contains the test cases to be inserted into moodle for automatic correction of student submitted codes.') + '\n\n'
            message_cases += _('Follow these steps:') + '\n\n'
            message_cases += _(
                '1. Use the pdf with the exams generated with this date and time (EXACTLY): ') + data_hora + '\n'
            message_cases += _('2. Save linker.json and students_variations.csv files') + '\n'
            message_cases += _(
                '3. After you create a Moodle VPL activity, in the runtime files, add linker.json and students_variations.csv') + '\n'
            message_cases += _(
                '4. Add too other files available at github.com/fzampirolli/mctest/VPL_modification') + '\n'
            message_cases += '\n\n'

            anexos = [Utils.format_cases(cases, str(request.user) + '-' + str(exam.exam_name) + '-' + data_hora)]
            anexos.append([path_to_file_VARIATIONS])
            aux = np.array(listVariations)
            with open(path_to_file_VARIATIONS_VPL, 'w', newline='') as file_var:
                writer = csv.writer(file_var, delimiter=',', quoting=csv.QUOTE_NONE, quotechar='',
                                    lineterminator='\n')
                aux = aux[:, -2:]  # get last two columns
                writer.writerows(aux)  # return name; variation
            anexos.append([path_to_file_VARIATIONS_VPL])
            cvMCTest.envia_email(webMCTest_SERVER,
                                 587,
                                 webMCTest_FROM,
                                 webMCTest_PASS,
                                 str(request.user),
                                 'MCTest: case test of moodle - Exam: ' + str(exam.exam_name) + ' - ' + data_hora,
                                 message_cases, anexos)

        # problem with permission ...
        path = os.getcwd()
        getuser = path.split('/')
        getuser = getuser[1]
        getuser = getuser + ':' + getuser
        os.system('chown ' + getuser + ' ' + path + ' . -R')

        if exam.classrooms.all().count() == 1:
            path_to_file = BASE_DIR + "/pdfExam/" + file_name + ".pdf"
            return serve(request, os.path.basename(path_to_file),
                         os.path.dirname(path_to_file))
        else:
            fzip = BASE_DIR + "/pdfExam/_e" + str(exam.id) + "_" + str(request.user) + ".zip"
            os.system("zip -j " + fzip + " " + BASE_DIR + "/pdfExam/_e" + str(exam.id) + "*")
            return serve(request, os.path.basename(fzip),
                         os.path.dirname(fzip))

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
    questions = exam_inst.questions
    classrooms = exam_inst.classrooms

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

            questions = form.cleaned_data['questions']
            # raise Http404(len(exam_inst.questions.all()))
            for q in exam_inst.questions.all():
                exam_inst.questions.remove(q)
            exam_inst.questions.add(*questions)

            exam_inst.save()
            return HttpResponseRedirect('/exam/exam/' + str(pk) + '/update/')
        else:
            return HttpResponse(_("Invalid Form! Verify if date follows the format, for example."))


    else:
        form = UpdateExamForm(initial={
            'exam_name': exam_inst.exam_name,
            'classrooms': [c for c in classrooms.filter().values_list('id', flat=True)],
            'questions': [q for q in questions.filter().values_list('id', flat=True)],
            # .course.discipline_profs==request.user],
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
        qs = Exam.objects.none()
        t = []
        for e in li:
            if not e.pk in t:
                t.append(e.pk)
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
        qs = Exam.objects.none()
        t = []
        for e in li:
            if not e.pk in t:
                t.append(e.pk)
        return li.order_by('exam_name').distinct()

    def form_valid(self, form):
        if not Exam.objects.filter(classrooms__discipline__discipline_profs=self.request.user):
            messages.error(self.request, _('ExamDetailView: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})


class ExamCreate(CreateView):
    model = Exam
    # fields = '__all__'
    fields = [
        'exam_name',
        'classrooms',
        #        'questions',
        #        'exam_number_of_questions_var1',
        #        'exam_number_of_questions_var2',
        #        'exam_number_of_questions_var3',
        #        'exam_number_of_questions_var4',
        #        'exam_number_of_questions_var5',
        #        'exam_number_of_anwsers_question',
        #        'exam_number_of_questions_text',
        #        'exam_variations',
        #        'exam_max_questions_square',
        #        'exam_max_squares_horizontal',
        #        'exam_stylesheet',
        #        'exam_print',
        #        'exam_print_eco',
        #        'exam_student_feedback',
        #        #'exam_room',
        #        'exam_term',
        #        'exam_instructions',
    ]
    template_name = 'exam/exam_create.html'
    success_url = '/exam/myexams'

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
    success_url = '/exam/myexams'

    def get_queryset(self):
        return Exam.objects.filter(exam_who_created=self.request.user).distinct()

    def form_valid(self, form):
        if not Exam.objects.filter(classrooms__discipline__discipline_profs=self.request.user):
            messages.error(self.request, _('ClassroomUpdate: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})


class LoanedExamByUserListView(LoginRequiredMixin, generic.ListView):
    model = Exam
    template_name = 'exam/exam_list_who_created_user.html'

    # paginate_by = 100

    def get_queryset(self):
        li = Exam.objects.filter(exam_who_created=self.request.user)
        qs = Exam.objects.none()
        t = []
        for e in li:
            if not e.pk in t:
                t.append(e.pk)
        return li.order_by('exam_name').distinct()
