'''
=====================================================================
Copyright (C) 2018-2024 Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of MCTest 5.3.

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
import datetime
###################################################################
import json
import os, re
import random
import subprocess

from django.contrib import messages
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from django.core.files.storage import FileSystemStorage
from django.forms import Textarea
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView
from django.views.static import serve
from tablib import Dataset
# ai_assist: comentado uso em question_update.html - incluir na versão MCTest 5.4
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from language_tool_python import LanguageTool
import autopep8

###################################################################
from account.models import User
from course.models import Discipline
from exam.UtilsLatex import Utils
from mctest.settings import BASE_DIR
from topic.UtilsMCTest4 import UtilsMC
from .forms import UpdateQuestionForm, QuestionCreateForm, TopicCreateForm, TopicUpdateForm
from .models import Topic, Question, Answer
from .resources import QuestionResource
from django.utils.html import format_html

# from sympy import *

from django.shortcuts import redirect

from django.urls import reverse

from copy import copy


@csrf_exempt
def ai_assist(request):
    if request.method == 'POST':
        question_text = request.POST.get('question_text', '')
        language_choice = request.POST.get('language_choice', 'pt-BR')  # Valor padrão ou qualquer outra lógica que você preferir

        # Identificar e salvar partes do texto entre [[code: e ]]
        blocks = []
        blocks_text = []
        contador = 0
        start = question_text.find('[[code:')
        while start != -1:
            end = question_text.find(']]', start)
            if end != -1:
                block = question_text[start:end + 2]
                blocks.append(block)
                text = "X" + str(contador).zfill(3) + "X"
                blocks_text.append(text)
                question_text = question_text[:start] + text + question_text[end + 2:]
                start = question_text.find('[[code:', end - 7)
                contador += 1
            else:
                break

        # Identificar e salvar partes do texto entre [[def: e ]]
        start = question_text.find('[[def:')
        while start != -1:
            end = question_text.find(']]', start)
            if end != -1:
                code_python = question_text[start:end + 2]

                # Remover a primeira e a última linha do código
                code_lines = code_python.split('\n')
                first_line = code_lines.pop(0)
                last_line = code_lines.pop(-1)

                # Corrigir o código sem a primeira e última linha
                code_python_correct = autopep8.fix_code('\n'.join(code_lines))

                try:
                    # Executar o código corrigido
                    exec(code_python_correct, globals(), locals())
                    code_python_correct = first_line + '\n' + code_python_correct + last_line
                    code_python_correct += (f"\n% ==============\n% Código executado!\n")
                except Exception as e:
                    # Incluir a primeira e última linha novamente
                    code_python_correct = first_line + '\n' + code_python_correct + last_line
                    code_python_correct += (f"\n% ==========================\n% Erro ao executar o código: \n% {e}\n")

                blocks.append(code_python_correct)
                text = "X" + str(contador).zfill(3) + "X"
                blocks_text.append(text)
                question_text = question_text[:start] + text + question_text[end + 2:]
                start = question_text.find('[[def:', end - 6)
                contador += 1
            else:
                break

        # Inicializar a ferramenta de correção ortográfica
        tool = LanguageTool(language_choice)

        # Corrigir os erros de ortografia apenas na parte não ignorada
        matches = tool.check(question_text)
        suggested_text = tool.correct(question_text)

        # Restaurar as partes ignoradas
        for block, text in zip(blocks, blocks_text):
            suggested_text = suggested_text.replace(text, block)  # Mantém [[code: e ]]

        return JsonResponse({'suggested_text': suggested_text})
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

def similar_question_ai(request, pk):
    question_to_copy = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        text = question_to_copy.question_short_description
        if len(text) > 47:
            text = text[:47] + '-cp'
        else:
            text += '-cp'

        # Copiar a questão
        new_question = copy(question_to_copy)
        new_question.pk = None
        new_question.question_short_description = text
        new_question.question_who_created = request.user
        # vai para o prompt da llm: question_to_copy.question_text
        # retorno_llm deve ser validado
        # new_question.question_text = retorno_llm
        new_question.save()

        # Copiar as respostas relacionadas
        lista_respostas = []
        for answer in question_to_copy.answers2.all():
            lista_respostas.append("A: "+ answer.answer_text)

        if lista_respostas:
            # concatenar com retorno_llm + lista_respostas
            pass

        # pede para gerar questao similar com AI para qq caso:
        # QM
        # QM paramétrico (com código python na descrição)
        # QT
        # QT paramétrico

        lista_respostas = []
        for answer in question_to_copy.answers2.all():
            copied_answer = copy(answer)
            copied_answer.pk = None  # Limpar a chave primária
            copied_answer.question = new_question
            # copied_answer.answer = answer_ai
            copied_answer.save()

        messages.error(request, format_html(
            _('The question has been successfully duplicated! You can <a href="../../{}/update/">view and edit the duplicated question here</a>.'),
            new_question.id))

    return render(request, 'exam/exam_msg.html', {})


def copy_question(request, pk):
    question_to_copy = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        text = question_to_copy.question_short_description
        if len(text) > 47:
            text = text[:47] + '-cp'
        else:
            text += '-cp'

        # Copiar a questão
        new_question = copy(question_to_copy)
        new_question.pk = None
        new_question.question_short_description = text
        new_question.question_who_created = request.user
        new_question.save()

        # Copiar as respostas relacionadas
        for answer in question_to_copy.answers2.all():
            copied_answer = copy(answer)
            copied_answer.pk = None  # Limpar a chave primária
            copied_answer.question = new_question
            copied_answer.save()

        messages.error(request, format_html(
            _('The question has been successfully duplicated! You can <a href="../../{}/update/">view and edit the duplicated question here</a>.'),
            new_question.id))

    return render(request, 'exam/exam_msg.html', {})


@login_required
def save_question_Json(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'topic.change_question' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    if request.POST:
        question_inst = get_object_or_404(Question, pk=pk)  # questao corrente

        questions = []
        topics = []
        disciplines = []
        answers = []
        for q in Question.objects.filter(question_who_created=request.user):

            # salvo questoes da disciplina corrente, SEM tratar mesmo topico em varias disciplinas
            if (q.topic.discipline.all()[0].id == question_inst.topic.discipline.all()[0].id):
                questions.append(q)
                if not q.topic in topics:
                    topics.append(q.topic)
                    for d in q.topic.discipline.all():
                        if not d in disciplines:
                            disciplines.append(d)

                if Answer.objects.filter(question__pk=q.pk):
                    for a in Answer.objects.filter(question__pk=q.pk):
                        questions.append(a)

        file_name = request.user.username
        fileQuestionName = "./tmp/" + file_name + "_q_ALL" + ".json"

        with open(fileQuestionName, "w") as out:
            questions_str = serialize('json', questions)
            topics_str = serialize('json', topics)
            disciplines_str = serialize('json', disciplines)
            data_q = json.loads(questions_str)
            data_t = json.loads(topics_str)
            data_d = json.loads(disciplines_str)
            data_all = list(data_d) + list(data_t) + list(data_q)

            json.dump(data_all, out, indent=2)

        return serve(request, os.path.basename(fileQuestionName), os.path.dirname(fileQuestionName))


@login_required
def ImportQuestionsJson(request):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'topic.change_question' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    if request.method == 'POST':
        file_questions = ""

        # try:
        if True:
            try:
                file_questions = request.FILES['myfile']
            except:
                messages.error(request, _('ImportQuestionsJson: choose a JSON following the model!'))
                return render(request, 'exam/exam_errors.html', {})

            data = file_questions.read().decode('utf-8')
            objs = serializers.json.Deserializer(data)  # .next().object

            count = 0
            topics = []
            disciplines = []
            questions = []
            answers = []
            for o in objs:
                if type(o.object) == Discipline:
                    d = o.object
                    disciplines.append(d)
                elif type(o.object) == Topic:
                    t = o.object
                    topics.append(t)
                elif type(o.object) == Question:
                    q = o.object
                    questions.append(q)
                elif type(o.object) == Answer:
                    a = o.object
                    answers.append(a)

            for q in questions:  # pega todas as questoes do json
                for t0 in topics:  # pega todos os topicos do json
                    if t0.topic_text == q.topic.topic_text:  # se topico da questao for igual a do json
                        t1 = get_object_or_404(Topic, topic_text=t0.topic_text)
                        for d1 in t1.discipline.all():  # pega todas as disciplinas do BD
                            if Discipline.objects.filter(discipline_code=d1.discipline_code):  # se existe disciplina
                                if request.user in d1.discipline_profs.all() or request.user in d1.discipline_coords.all():  # se prof esta em disc
                                    if Topic.objects.filter(topic_text=t0.topic_text):  # se existe topico
                                        if not Question.objects.filter(
                                                question_text=q.question_text):  # se nao tem questao igual no BD
                                            a1 = []
                                            for a0 in answers:  # pega todas as respostas da questao do json
                                                if a0.question == q:
                                                    a1.append(a0)

                                            raise Http404("Are you sure? Contact your admin")

                                            newQ = Question.objects.create(
                                                topic=t1,
                                                question_group=q.question_group,
                                                question_short_description=q.question_short_description,
                                                question_text=q.question_text,
                                                question_type=q.question_type,
                                                question_difficulty=q.question_difficulty,
                                                question_bloom_taxonomy=q.question_bloom_taxonomy,
                                                question_last_update=q.question_last_update,
                                                question_who_created=q.question_who_created,
                                                # User.objects.get(username=request.user.username),
                                            )
                                            for a in a1:
                                                Answer.objects.create(
                                                    question=newQ,
                                                    answer_text=a.answer_text,
                                                    answer_feedback=a.answer_feedback,
                                                )
        # except:
        #    return HttpResponse("ERROR: in serializers.json.Deserializer ")

    return HttpResponseRedirect("../")


##################################################################

@login_required
@csrf_exempt
def see_question_PDF(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    question = get_object_or_404(Question, pk=pk)
    context = {"questions": question}

    if request.POST:

        Utils.validateProfByQuestion(question, request.user)

        file_name = request.user.username
        fileQuestionName = file_name + ".tex"
        with open(fileQuestionName, 'w') as fileExam:
            q = question
            fileQuestion = open(fileQuestionName, 'w')
            fileQuestion.write(Utils.getBegin())
            fileQuestion.write("\\noindent\\Huge{MCTest}\\normalsize\\vspace{5mm}\\\\\n")
            fileQuestion.write("\\noindent\\textbf{Topic:} %s\\\\\n" % q.topic.topic_text)
            fileQuestion.write("\\noindent\\textbf{Group:} %s\\\\\n" % q.question_group)
            fileQuestion.write("\\noindent\\textbf{Short Description:} %s\\\\\n" % q.question_short_description)
            fileQuestion.write("\\noindent\\textbf{Type:} %s\\\\\n" % q.question_type)
            fileQuestion.write("\\noindent\\textbf{Difficulty:} %s\\\\\n" % q.question_difficulty)
            fileQuestion.write("\\noindent\\textbf{Bloom taxonomy:} %s\\\\\n" % q.question_bloom_taxonomy)
            fileQuestion.write("\\noindent\\textbf{Last update:} %s\\\\\n" % q.question_last_update)
            fileQuestion.write("\\noindent\\textbf{Who created:} %s\\\\\n" % q.question_who_created)
            fileQuestion.write("\\noindent\\textbf{Parametric:} %s\\\\\n" % q.question_parametric.upper())
            # if q.question_type == "QM" and q.question_correction_count:
            #     Accuracy = (q.question_correct_count / q.question_correction_count) * 100
            #     fileQuestion.write( "\\noindent\\textbf{Correct:} %s\\\\\n" % q.question_correct_count)
            #     fileQuestion.write( "\\noindent\\textbf{Correction:} %s\\\\\n" % q.question_correction_count)
            #     fileQuestion.write( "\\noindent\\textbf{Accuracy:} %.1f\\\\\n" % Accuracy)

            st = q.question_text
            a, b = st.find('begin{comment}'), st.find('end{comment}')
            if a < b:
                fileQuestion.write("\\noindent\\textbf{Integration:} %s\\\\\n" % 'Moodle+VPL')

            ss1 = "\n\\hspace{-15mm}{\\small {\\color{green}\\#%s}} \\hspace{-1mm}"
            # Renomear a variável str para evitar conflito
            ss = ss1 % str(q.id).zfill(4)
            str1 = "%s %s." % (ss, 1)

            if q.question_parametric == 'no':
                quest = q.question_text + '\n'
                ans = []
                if q.question_type == "QM":
                    for a in q.answers():
                        ans.append(a.answer_text + '\n')
            else:  # QUESTOES PARAMETRICAS
                if q.question_type == "QM":
                    [quest, ans, feedback_ans] = UtilsMC.questionParametric(q.question_text, q.answers(), [])
                else:  # se for dissertativa, não colocar alternativas
                    [quest, ans, feedback_ans] = UtilsMC.questionParametric(q.question_text, [], [])
                if quest == "":
                    messages.error(request,
                                   _('UtilsMC.questionParametric: do not use some words in the code, '
                                     'for ex. exec, cmd, open, import os, remove, mkdir, sys, gnureadline, '
                                     'subprocess, getopt, shlex, wget, commands, system, exec, eval'))
                    return render(request, 'exam/exam_errors.html', {})

            str1 += r' %s' % ''.join(quest)
            str1 += "\n\n\\vspace{2mm}\\begin{oneparchoices}\\hspace{-3mm}\n"
            for a in random.sample(ans, len(ans)):
                if ans.index(a) == 0:
                    str1 += "\\choice \\hspace{-2.0mm}{\\tiny{\\color{blue}\#%s}}%s" % (str(ans.index(a)), a)
                else:
                    str1 += "\\choice \\hspace{-2.0mm}{\\tiny{\\color{red}*%s}}%s" % (str(ans.index(a)), a)

                try:
                    if feedback_ans[ans.index(a)] != '\n':
                        str1 += '[' + feedback_ans[ans.index(a)] + ']'  ############# NOVO
                except:  # quando cria alternativas automáticas, não tem feedback
                    pass

            str1 += "\\end{oneparchoices}\\vspace{0mm}\n"

            fileQuestion.write(str1)

            fileQuestion.write("\\end{document}")
            fileQuestion.close()

        cmd = ['pdflatex', '--shell-escape', '-interaction', 'nonstopmode',
               fileQuestionName]
        proc = subprocess.Popen(cmd)
        proc.communicate()
        proc = subprocess.Popen(cmd)
        proc.communicate()

        path = os.getcwd()
        os.system("cp " + file_name + ".pdf " + path + "/pdfQuestion/")

        getuser = path.split('/')
        getuser = getuser[2]
        getuser = getuser + ':' + getuser
        os.system('chown -R ' + getuser + ' ' + path)
        #os.system('chgrp -R ' + getuser + ' ' + path)

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

        path_to_file = BASE_DIR + "/pdfQuestion/" + file_name + ".pdf"
        return serve(request, os.path.basename(path_to_file), os.path.dirname(path_to_file))

from decouple import config


@login_required
def ImportQuestions(request):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    # topic = get_object_or_404(Topic, pk=pk)

    if request.method == 'POST':
        teste2 = config('webMCTest_PASS')

        person_resource = QuestionResource()
        dataset = Dataset()
        try:
            new_persons = request.FILES['myfile']
        except:
            messages.error(request, _('ImportQuestions: choose a TXT following the model!'))
            return render(request, 'exam/exam_errors.html', {})

        # mystr4 = '/topic/topic/' + str(pk) + '/update'
        # messages.info(request, _('Return to: ') + '<a href="' + mystr4 + '">link</a>', extra_tags='safe')
        # messages.info(request, _('Topic name') + ' >> ' + topic.topic_text, extra_tags='upper')

        listao = UtilsMC.questionsReadFiles(request, new_persons)
        if listao == '':
            return render(request, 'exam/exam_errors.html', {})

        count = 0
        questions_created = []
        questions_equal = []
        for qq in listao:
            flagIncludeQuestion = False

            myquestions = Question.objects.filter(topic__topic_text=qq['c']).filter(
                topic__discipline__discipline_profs=request.user)

            flagIncludeQuestion = True
            for q in myquestions:
                if qq['q'] == q.question_text:  # if there is the same question on DB
                    if len(qq['a']):
                        a = Answer.objects.filter(question=q)
                        if a[0].answer_text == qq['a'][0]:  # if also the first answers is equal
                            flagIncludeQuestion = False
                            questions_equal.append(str(q.pk))
                            break

            if flagIncludeQuestion:
                tp = 'QM'  # multiple-choice questions
                df = 1  # default QE == Easy
                if qq['t'] == 'QM':
                    df = 3
                elif qq['t'] == 'QH':
                    df = 5
                elif qq['t'] == 'QT':
                    df = 5
                    tp = 'QT'
                if tp:  # se existe topico, cria questao
                    today = datetime.date.today

                    try:
                        topic = Topic.objects.get(topic_text=qq['c'])
                    except:
                        messages.error(request, _("ImportQuestions: topic does not exist - created before in Topic: ")
                                       + qq['c'])
                        return render(request, 'exam/exam_errors.html', {})

                    for d in topic.discipline.all():
                        if not (request.user in d.discipline_profs.all() or request.user in d.discipline_coords.all()):
                            messages.error(request, _(
                                "ImportQuestions: teacher is not associated with any discipline with this topic: ")
                                           + qq['c'])
                            return render(request, 'exam/exam_errors.html', {})

                    newQ = Question.objects.create(
                        topic=topic,
                        question_group=qq['st'],
                        question_short_description=qq['c'] + str(qq['n']).zfill(3),
                        question_text=qq['q'],
                        question_type=tp,
                        question_difficulty=df,
                        question_bloom_taxonomy='remember',
                        question_last_update=datetime.date.today(),
                        question_who_created=User.objects.get(username=request.user.username),
                    )

                    questions_created.append([str(newQ.pk), topic])

                    for a in qq['a']:
                        Answer.objects.create(
                            question=newQ,
                            answer_text=a,
                            answer_feedback='',
                        )

        messages.info(request, _('Questions Created:'))
        for q in questions_created:
            str_d = ''
            for d in Discipline.objects.all():
                for t in d.topics2.all():
                    if t.topic_text == q[1].topic_text:
                        str_d += d.discipline_name + '; '
                        break
            messages.info(request, str(q[0]) + ' - ' + str(q[1].topic_text) + ' - ' + str_d)

        if questions_equal:
            messages.info(request, _('Similar question(s) exist in the DB:'))
            messages.info(request, '; '.join([k for k in questions_equal]))

    # return HttpResponseRedirect("../")
    return render(request, 'exam/exam_msg.html', {})


@login_required
def ImportQuestionsImage(request):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    if request.method == 'POST':

        try:
            file = request.FILES['myfile']
        except:
            messages.error(request, _('ImportQuestionsImage: choose a PNG following the model!'))
            return render(request, 'exam/exam_errors.html', {})

        fs = FileSystemStorage()
        file0 = str(file.name)
        file0 = file0.replace(' ', '')

        file0 = re.sub('[^A-Za-z0-9._-]+', '', file0)  # remove special characters

        filename = fs.save(file0, file)

        # problem with permission ...
        path = os.getcwd()
        getuser = path.split('/')
        getuser = getuser[2]
        getuser = getuser + ':' + getuser
        os.system('mv ' + filename + ' ' + path + '/tmp/')
        os.system('chown -R ' + getuser + ' ' + path)
        #os.system('chgrp -R ' + getuser + ' ' + path)

        messages.error(request, _('Image imported successfully! ') + filename)

    # return HttpResponseRedirect("../")
    return render(request, 'exam/exam_msg.html', {})


#######################################################################
class TopicListView(LoginRequiredMixin, generic.ListView):
    model = Topic
    fields = '__all__'

    # paginate_by = 10

    def get_queryset(self):
        # if len(Topic.objects.filter(discipline__discipline_coords=self.request.user)):
        #     lista = Topic.objects.filter(discipline__discipline_coords=self.request.user)
        #     return lista.order_by('topic_text').distinct()
        # if len(Topic.objects.filter(discipline__discipline_profs=self.request.user)):
        #     lista = Topic.objects.filter(discipline__discipline_profs=self.request.user)
        #     return lista.order_by('topic_text').distinct()

        t1 = Topic.objects.filter(discipline__discipline_profs=self.request.user)
        t2 = Topic.objects.filter(discipline__discipline_coords=self.request.user)
        return (t1 | t2).order_by('topic_text').distinct()


class TopicUpdate(LoginRequiredMixin, generic.UpdateView):
    # model = Topic
    # fields = '__all__'
    form_class = TopicUpdateForm

    template_name = 'topic/topic_update.html'

    def get_form_kwargs(self):
        kwargs = super(TopicUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Verifica se já existe um tópico com o mesmo topic_text
        topic_text = form.cleaned_data['topic_text']
        discipline_initials = form.cleaned_data['discipline'][0].discipline_code
        topic_count = Topic.objects.filter(topic_text__startswith=f"{discipline_initials}_").count()
        topic_text0 = form.initial['topic_text']

        if Topic.objects.filter(topic_text=topic_text).exists() and topic_text != topic_text0:
            # Sugere um nome com prefixo e contador
            suggested_topic_text = f"{discipline_initials}_{topic_count + 1:02d}_{topic_text}"
            messages.error(
                self.request,
                _("A topic with the same text already exists. Please consider using a unique name. Suggested name: {}").format(
                    suggested_topic_text)
            )
            return render(self.request, 'exam/exam_errors.html', {})

        d = form.cleaned_data['discipline']
        d_obj = get_object_or_404(Discipline, pk=d[0].pk)
        if not self.request.user in d_obj.discipline_coords.all():
            messages.error(self.request, _("TopicCreate: the user isn't the coordinator of the discipline"))
            return render(self.request, 'exam/exam_errors.html', {})

        return super(TopicUpdate, self).form_valid(form)

    def get_queryset(self):
        if len(Topic.objects.filter(discipline__discipline_coords=self.request.user)):
            return Topic.objects.filter(discipline__discipline_coords=self.request.user).distinct()
        if len(Topic.objects.filter(discipline__discipline_profs=self.request.user)):
            return Topic.objects.filter(discipline__discipline_profs=self.request.user).distinct()


class TopicDetailView(LoginRequiredMixin, generic.DetailView):
    model = Topic
    template_name = 'topic/topic_detail.html'

    def get_queryset(self):
        return Topic.objects.all().distinct()


class TopicCreate(LoginRequiredMixin, generic.CreateView):
    form_class = TopicCreateForm
    # model = Topic
    # fields = '__all__'

    template_name = 'topic/topic_create.html'
    success_url = '/topic/topics'

    def get_form_kwargs(self):
        kwargs = super(TopicCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Verifica se já existe um tópico com o mesmo topic_text
        topic_text = form.cleaned_data['topic_text']
        discipline_initials = form.cleaned_data['discipline'][0].discipline_code
        topic_count = Topic.objects.filter(topic_text__startswith=f"{discipline_initials}_").count()

        if Topic.objects.filter(topic_text=topic_text).exists():
            # Sugere um nome com prefixo e contador
            suggested_topic_text = f"{discipline_initials}_{topic_count + 1:02d}_{topic_text}"
            messages.error(
                self.request,
                _("A topic with the same text already exists. Please consider using a unique name. Suggested name: {}").format(
                    suggested_topic_text)
            )
            return render(self.request, 'exam/exam_errors.html', {})

        d = form.cleaned_data['discipline']
        d_obj = get_object_or_404(Discipline, pk=d[0].pk)
        if not self.request.user in d_obj.discipline_coords.all():
            messages.error(self.request, _("TopicCreate: the user isn't the coordinator of the discipline"))
            return render(self.request, 'exam/exam_errors.html', {})

        return super(TopicCreate, self).form_valid(form)

    def get_queryset(self):
        if len(Topic.objects.filter(discipline__discipline_coords=self.request.user)):
            return Topic.objects.filter(discipline__discipline_coords=self.request.user).distinct()
        if len(Topic.objects.filter(discipline__discipline_profs=self.request.user)):
            return Topic.objects.filter(discipline__discipline_profs=self.request.user).distinct()


class TopicDelete(LoginRequiredMixin, generic.DeleteView):
    model = Topic
    template_name = 'topic/topic_confirm_delete.html'
    success_url = '/topic/topics'

    def get_queryset(self):
        if len(Topic.objects.filter(discipline__discipline_coords=self.request.user)):
            return Topic.objects.filter(discipline__discipline_coords=self.request.user).distinct()
        if len(Topic.objects.filter(discipline__discipline_profs=self.request.user)):
            return Topic.objects.filter(discipline__discipline_profs=self.request.user).distinct()


@login_required
def see_topic_PDF_aux(request, new_order, questions_id, allQuestionsStr, countQuestions):
    for qid in new_order:
        q = get_object_or_404(Question, pk=questions_id[qid])
        print('#######################', q.id, q.question_short_description)

        countQuestions += 1
        str1 = "\\noindent\\rule{\\textwidth}{0.8pt}\\\\\n"
        str1 += "\\noindent\\textbf{Count:} %d\\\\\n" % countQuestions
        str1 += "\\noindent\\textbf{Short Description:} %s\\\\\n" % q.question_short_description
        str1 += "\\noindent\\textbf{Group:} %s\\\\\n" % q.question_group
        str1 += "\\noindent\\textbf{Type:} %s\\\\\n" % q.question_type
        str1 += "\\noindent\\textbf{Difficulty:} %s\\\\\n" % q.question_difficulty
        str1 += "\\noindent\\textbf{Bloom taxonomy:} %s\\\\\n" % q.question_bloom_taxonomy
        str1 += "\\noindent\\textbf{Last update:} %s\\\\\n" % q.question_last_update
        str1 += "\\noindent\\textbf{Who created:} %s\\\\\n" % q.question_who_created
        str1 += "\\noindent\\textbf{URL:} \\url{%stopic/question/%s/update/}\\\\\n" % (
            os.getenv('IP_HOST2'), q.id)
        str1 += "\\noindent\\textbf{Parametric:} %s\\\\\n" % q.question_parametric.upper()
        if q.question_type == "QM" and q.question_correction_count:
            Accuracy = (q.question_correct_count / q.question_correction_count) * 100
            str1 +="\\noindent\\textbf{Correct:} %s\\\\\n" % q.question_correct_count
            str1 +="\\noindent\\textbf{Correction:} %s\\\\\n" % q.question_correction_count
            str1 +="\\noindent\\textbf{Accuracy:} %.1f\\\\\n" % Accuracy

        st = q.question_text
        a, b = st.find('begin{comment}'), st.find('end{comment}')
        if a < b:
            str1 += "\\noindent\\textbf{Integration:} %s\\\\\n" % 'Moodle+VPL'

        ss1 = "\n\\hspace{-15mm}{\\small {\\color{green}\\#%s}} \\hspace{-1mm}"
        ss = ss1 % str(q.id).zfill(4)

        str1 += "%s %s." % (ss, 1)

        if q.question_parametric == 'no':
            quest = q.question_text + '\n'
            ans = []
            if q.question_type == "QM":
                for a in q.answers():
                    ans.append(a.answer_text + '\n')
        else:  # QUESTOES PARAMETRICAS
            try:
                if q.question_type == "QM":
                    [quest, ans, feedback_ans] = UtilsMC.questionParametric(q.question_text, q.answers(), [])
                else:  # se for dissertativa, não colocar alternativas
                    [quest, ans, feedback_ans] = UtilsMC.questionParametric(q.question_text, [], [])
                if quest == "":
                    messages.error(request,
                                   _('UtilsMC.questionParametric: do not use some words in the code, '
                                     'for ex. exec, cmd, open, import os, remove, mkdir, sys, gnureadline, '
                                     'subprocess, getopt, shlex, wget, commands, system, exec, eval'))
                    messages.error(request, 'Question: %d' % q.id)
                    return render(request, 'exam/exam_errors.html', {})
            except:
                str1 += "ERRO NA PARTE PARAMÉTRICA!!!\\\\\n"
                messages.error(request, _('ERROR IN THE PARAMETRIC PART!!!'))
                messages.error(request, 'Question: %d' % q.id)
                return render(request, 'exam/exam_errors.html', {})
                # continue

        str1 += r' %s\n\n' % ''.join(quest)
        str1 += "\n\n\\vspace{2mm}\\begin{oneparchoices}\\hspace{-3mm}\n"
        for a in random.sample(ans, len(ans)):
            if ans.index(a) == 0:
                str1 += "\\choice \\hspace{-2.0mm}{\\tiny{\\color{blue}\#%s}}%s" % (str(ans.index(a)), a)
            else:
                str1 += "\\choice \\hspace{-2.0mm}{\\tiny{\\color{red}*%s}}%s" % (str(ans.index(a)), a)

            try:
                if feedback_ans[ans.index(a)] != '\n':
                    str1 += '[' + feedback_ans[ans.index(a)] + ']'  ############# NOVO
            except:  # quando cria alternativas automáticas, não tem feedback
                pass

        str1 += "\\end{oneparchoices}\\vspace{0mm}\\\\\n"

        allQuestionsStr.append(str1)

    return countQuestions, allQuestionsStr


@login_required
@csrf_exempt
def see_topic_PDF(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    topic = get_object_or_404(Topic, pk=pk)

    if not len(Topic.objects.filter(discipline__discipline_profs=request.user)):
        messages.error(request,
                       _('The professor does not have permission!'))
        return render(request, 'exam/exam_errors.html', {})

    if request.POST:
        file_name = request.user.username
        fileQuestionName = file_name + ".tex"
        fileQuestion = open(fileQuestionName, 'w')
        fileQuestion.write(Utils.getBegin())

        with open(fileQuestionName, 'w') as fileExam:

            allQuestionsStr = []
            countQuestions = 0

            questions_id, questions_text = [], []
            for q in topic.questions2.all().order_by('question_text'):
                if q.question_type == 'QM':
                    questions_id.append(q.id)
                    questions_text.append(q.question_text)
            new_order = UtilsMC.sortedBySimilarity2(questions_text)
            countQuestions, allQuestionsStr = see_topic_PDF_aux(request, new_order, questions_id, allQuestionsStr,
                                                                countQuestions)

            if countQuestions:
                allQuestionsStr.append("\\newpage\\\\\n")

            questions_id, questions_text = [], []
            for q in topic.questions2.all().order_by('question_text'):
                if q.question_type == 'QT':
                    questions_id.append(q.id)
                    questions_text.append(q.question_text)
            new_order = UtilsMC.sortedBySimilarity2(questions_text)
            countQuestions, allQuestionsStr = see_topic_PDF_aux(request, new_order, questions_id, allQuestionsStr,
                                                                countQuestions)

            fileQuestion.write("\\noindent\\Huge{MCTest}\\normalsize\\vspace{5mm}\\\\\n")
            fileQuestion.write("\\noindent\\textbf{Topic:} %s\\\\\n" % topic.topic_text)
            for st in allQuestionsStr:
                fileQuestion.write(st)

            fileQuestion.write("\\end{document}")
            fileQuestion.close()

        cmd = ['pdflatex', '--shell-escape', '-interaction', 'nonstopmode',
               fileQuestionName]
        proc = subprocess.Popen(cmd)
        proc.communicate()
        proc = subprocess.Popen(cmd)
        proc.communicate()

        path = os.getcwd()
        os.system("cp " + file_name + ".pdf " + path + "/pdfTopic/")

        getuser = path.split('/')
        getuser = getuser[2]
        getuser = getuser + ':' + getuser
        os.system('chown -R ' + getuser + ' ' + path)
        #os.system('chgrp -R ' + getuser + ' ' + path)

        try:
            os.remove("{}.aux".format(file_name))
            os.remove("{}.log".format(file_name))
            # os.remove("{}.tex".format(file_name))
            os.remove("{}.pdf".format(file_name))
            os.remove("{}.out".format(file_name))
            os.remove("temp.txt")
            pass
        except Exception as e:
            pass

        path_to_file = BASE_DIR + "/pdfTopic/" + file_name + ".pdf"
        return serve(request, os.path.basename(path_to_file), os.path.dirname(path_to_file))


###################################################################
class QuestionListView(LoginRequiredMixin, generic.ListView):
    model = Question
    template_name = 'question/question_list.html'

    # paginate_by = 100

    def get_queryset(self):
        q1 = Question.objects.filter(topic__discipline__discipline_profs=self.request.user)
        q2 = Question.objects.filter(topic__discipline__discipline_coords=self.request.user)
        return (q1 | q2).order_by('question_short_description').distinct()


class LoanedQuestionByUserListView(LoginRequiredMixin, generic.ListView):
    model = Question
    template_name = 'question/question_list_who_created_user.html'

    # paginate_by = 100

    def get_queryset(self):
        # return Question.objects.filter(question_who_created=self.request.user)
        lista = Question.objects.filter(question_who_created=self.request.user)
        return lista.order_by('question_text').distinct()


class QuestionDetailView(generic.DetailView):
    model = Question
    template_name = 'question/question_detail.html'

    def get_queryset(self):
        q1 = Question.objects.filter(topic__discipline__discipline_profs=self.request.user)
        q2 = Question.objects.filter(topic__discipline__discipline_coords=self.request.user)
        return (q1 | q2).order_by('question_short_description').distinct()


####################################################################
# answers = Answer.objects.filter(question=question_inst)
# answers_data = [{'answer_text': q.answer_text} for q in answers]
from django.core import serializers


@login_required
def UpdateQuestion(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'topic.change_question' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    question_inst = get_object_or_404(Question, pk=pk)
    AnswerInlineFormSet = inlineformset_factory(
        Question, Answer, fk_name='question', fields=('answer_text', 'answer_feedback',),
        widgets={'answer_text': Textarea(attrs={'cols': 80, 'rows': 1}),
                 'answer_feedback': Textarea(attrs={'cols': 40, 'rows': 1}), },
        extra=1)  # quantidade de alternativas na tela

    Utils.validateProfByQuestion(question_inst, request.user)

    '''
    JSONSerializer = serializers.get_serializer("json")
    json_serializer = JSONSerializer()
    with open("file_json.json","w") as out:
        all_objects = Question.objects.filter(id=pk) 
        #all_objects.append(Answer.objects.filter(question__pk=pk))
        print (all_objects)
        json_serializer.serialize(all_objects, stream=out)
    #print (serializers.serialize("json",Question.objects.filter(id=pk)))
    '''

    if request.method == 'POST':

        form = UpdateQuestionForm(request.POST)
        if form.is_valid():  # Check if the forms are valid:

            profs = []  # pega todos os profs da disciplina
            for d in question_inst.topic.discipline.all():
                for p in d.discipline_coords.all():
                    profs.append(p)
            if not (request.user == question_inst.question_who_created or request.user in profs):
                messages.error(request, _(
                    'ERROR: You did not create this question or you are not the course coordinator. Please get in touch with them.'));
                return render(request, 'exam/exam_errors.html', {})

            '''
            # para aceitar símbolos na descrição, codificiar antes de salvar no BD
            # > echo 'símbolos especiais' | xxd -ps
            user = '_'+str(request.user) + '.txt'
            filetxt = open('.description' + user, 'w')
            filetxt.write(form.cleaned_data["question_text"])
            filetxt.close()
            #os.system('cat .description' + user + ' | xxd -ps >> .description_encode' + user)
            os.system('xxd -ps .description' + user + ' > .description_encode' + user)
            filetxt = open('.description_encode' + user, 'r')
            s = filetxt.read()

            # para decodificar:
            # > echo 'símbolos especiais' | xxd -ps | xxd -ps -r
            user = '_' + str(request.user) + '.txt'
            os.system('cat .description_encode' + user + ' | xxd -ps | xxd -ps -r >> .description_decode' + user)
            filetxt = open('.description_decode' + user, 'r')
            ss = filetxt.read()
            
            não funciona, pois ao visualizar o form mostra o codificado...
            '''

            question_inst.topic = form.cleaned_data['topic']
            question_inst.question_short_description = form.cleaned_data['question_short_description']
            question_inst.question_group = form.cleaned_data['question_group']
            question_inst.question_text = form.cleaned_data['question_text']
            question_inst.question_type = form.cleaned_data['question_type']
            question_inst.question_difficulty = form.cleaned_data['question_difficulty']
            question_inst.question_bloom_taxonomy = form.cleaned_data['question_bloom_taxonomy']
            question_inst.question_parametric = form.cleaned_data['question_parametric']
            question_inst.question_who_created = form.cleaned_data['question_who_created']
            question_inst.question_last_update = form.cleaned_data['question_last_update']

            question_inst.question_correction_count = form.cleaned_data['question_correction_count']
            question_inst.question_correct_count = form.cleaned_data['question_correct_count']
            question_inst.question_IRT_a_discrimination = form.cleaned_data['question_IRT_a_discrimination']
            question_inst.question_IRT_b_ability = form.cleaned_data['question_IRT_b_ability']
            question_inst.question_IRT_c_guessing = form.cleaned_data['question_IRT_c_guessing']

            #  Método criado por Gabriel Tavares Frota de Azevedo para o TCC do BCC/UFABC.
            # validation = UtilsMC.generateCode(request, question_inst.question_text, pk)
            # if validation is not None:
            #    return validation
            
            question_inst.save()

        formset = AnswerInlineFormSet(request.POST, request.FILES,
                                      instance=question_inst)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect('/topic/question/' + str(pk) + '/update/')

    else:  # If this is a GET (or any other method) create the default form.
        formset = AnswerInlineFormSet(instance=question_inst)

        st = Utils.validateProfByQuestion(question_inst, request.user)
        if st is not None:
            return HttpResponse(st)

        profs = []  # pega todos os profs da disciplina
        for d in question_inst.topic.discipline.all():
            for p in d.discipline_profs.all():
                profs.append(p)
            for p in d.discipline_coords.all():
                profs.append(p)
        if not request.user in profs:
            messages.error(request, _(
                'ERROR: The teacher is not registered in the Discipline (of the topic)'));
            return render(request, 'exam/exam_errors.html', {})

        # raise Http404(profs)

        proposed_update_date = datetime.date.today()  # + datetime.timedelta(weeks=3)
        form = UpdateQuestionForm(initial={
            'topic': question_inst.topic,
            'question_short_description': question_inst.question_short_description,
            'question_group': question_inst.question_group,
            'question_text': question_inst.question_text,
            'question_type': question_inst.question_type,
            'question_difficulty': question_inst.question_difficulty,
            'question_bloom_taxonomy': question_inst.question_bloom_taxonomy,
            'question_parametric': question_inst.question_parametric,
            'question_who_created': question_inst.question_who_created,
            'question_last_update': question_inst.question_last_update,

            'question_correction_count': question_inst.question_correction_count,
            'question_correct_count': question_inst.question_correct_count,
            'question_IRT_a_discrimination': question_inst.question_IRT_a_discrimination,
            'question_IRT_b_ability': question_inst.question_IRT_b_ability,
            'question_IRT_c_guessing': question_inst.question_IRT_c_guessing,
        })

    return render(request, 'question/question_update.html', {
        'form': form,
        'formset': formset,
        'questioninst': question_inst,
    })


#########################################################

class QuestionCreate(LoginRequiredMixin, generic.CreateView):
    form_class = QuestionCreateForm

    template_name = 'question/question_create.html'
    success_url = reverse_lazy('topic:question-create')

    def get_form_kwargs(self):
        kwargs = super(QuestionCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        flag_ok = True
        t = form.cleaned_data['topic']
        t_obj = get_object_or_404(Topic, pk=t.pk)
        for d in t_obj.discipline.all():
            if self.request.user in d.discipline_profs.all() or self.request.user in d.discipline_coords.all():
                flag_ok = False
                break
        if flag_ok:
            messages.error(self.request, _("QuestionCreate: the teacher is not registered in discipline"))
            return render(self.request, 'exam/exam_errors.html', {})

        form.instance.question_who_created = self.request.user
        t = datetime.date.today()
        form.instance.question_last_update = str(t.year) + "-" + str(t.month) + "-" + str(t.day)

        if form.is_valid():
            #  Método criado por Gabriel Tavares Frota de Azevedo para o TCC do BCC/UFABC.
            # code_validation = UtilsMC.generateCode(self.request, form.instance.question_text, form.instance.pk)
            # if code_validation is not None:
            #     return code_validation
            form.save()

        return super(QuestionCreate, self).form_valid(form)

    def get_queryset(self):
        q1 = Question.objects.filter(topic__discipline__discipline_profs=self.request.user)
        q2 = Question.objects.filter(topic__discipline__discipline_coords=self.request.user)
        return (q1 | q2).order_by('question_short_description').distinct()


class QuestionUpdate(UpdateView):
    model = Question
    template_name = 'question/question_update.html'
    fields = '__all__'
    success_url = reverse_lazy('topic:question-detail')

    def get_queryset(self):
        q1 = Question.objects.filter(topic__discipline__discipline_profs=self.request.user)
        q2 = Question.objects.filter(topic__discipline__discipline_coords=self.request.user)
        return (q1 | q2).order_by('question_short_description').distinct()


class QuestionDelete(DeleteView):
    model = Question
    template_name = 'question/question_confirm_delete.html'
    success_url = reverse_lazy('topic:myquestions-list')

    def get_queryset(self):
        q1 = Question.objects.filter(topic__discipline__discipline_profs=self.request.user)
        q2 = Question.objects.filter(topic__discipline__discipline_coords=self.request.user)
        return (q1 | q2).order_by('question_short_description').distinct()
