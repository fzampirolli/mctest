'''
=====================================================================
Copyright (C) 2021 Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of MCTest 5.2.

Languages: Python 3.8.5, Django 3.1.4 and many libraries described at
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
import os
import random
import subprocess

from django.contrib import messages
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Textarea
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView
from django.views.static import serve
from tablib import Dataset

###################################################################
from account.forms import UserCreateForm
from account.models import User
from course.models import Institute, Course, Classroom, Discipline
from exam.UtilsLatex import Utils
from exam.models import Exam
from mctest.settings import BASE_DIR
from topic.UtilsMCTest4 import UtilsMC
from .forms import UpdateQuestionForm
# from django.contrib.auth.models import User
from .models import Topic, Question, Answer
from .resources import QuestionResource


# from sympy import *



###################################################################
import json
from django.core.serializers import serialize
from django.http import HttpResponse, HttpResponseRedirect, Http404


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

            ss1 = "\n\\hspace{-15mm}{\\small {\\color{green}\\#%s}} \\hspace{-1mm}"
            ss = ss1 % str(q.id).zfill(3)
            str1 = "%s %s." % (ss, 1)

            if q.question_parametric == 'no':
                quest = q.question_text + '\n'
                ans = []
                if q.question_type == "QM":
                    for a in q.answers():
                        ans.append(a.answer_text + '\n')
            else:  # QUESTOES PARAMETRICAS
                if q.question_type == "QM":
                    [quest, ans] = UtilsMC.questionParametric(q.question_text, q.answers())
                else:  # se for dissertativa, não colocar alternativas
                    [quest, ans] = UtilsMC.questionParametric(q.question_text, [])
                if quest == "":
                    messages.error(request,
                                   _('UtilsMC.questionParametric: do not use some words in the code, '
                                     'for ex. exec, cmd, open, import os, remove, mkdir, sys, gnureadline, '
                                     'subprocess, getopt, shlex, wget, commands, system, exec, eval'))
                    return render(request, 'exam/exam_errors.html', {})

            str1 += r' %s\n\n' % ''.join(quest)
            str1 += "\n\n\\vspace{2mm}\\begin{oneparchoices}\n"
            for a in random.sample(ans, len(ans)):
                if ans.index(a) == 0:
                    str1 += "\\choice \\hspace{-2.0mm}{\\tiny{\\color{blue}\#%s}}%s" % (str(ans.index(a)), a)
                else:
                    str1 += "\\choice \\hspace{-2.0mm}{\\tiny{\\color{red}*%s}}%s" % (str(ans.index(a)), a)
            str1 += "\\end{oneparchoices}\\vspace{0mm}\n"

            fileQuestion.write(str1)

            fileQuestion.write("\\end{document}")
            fileQuestion.close()

        cmd = ['pdflatex', '--shell-escape', '-interaction', 'nonstopmode', fileQuestionName]
        proc = subprocess.Popen(cmd)
        proc.communicate()
        proc = subprocess.Popen(cmd)
        proc.communicate()

        path = os.getcwd()
        os.system("cp " + file_name + ".pdf " + path + "/pdfQuestion/")

        getuser = path.split('/')
        getuser = getuser[1]
        getuser = getuser + ':' + getuser
        os.system('chown -R ' + getuser + ' ' + path + ' .')
        os.system('chgrp -R ' + getuser + ' ' + path + ' .')

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

    if request.method == 'POST':
        teste2 = config('webMCTest_PASS')

        person_resource = QuestionResource()
        dataset = Dataset()
        try:
            new_persons = request.FILES['myfile']
        except:
            messages.error(request, _('ImportQuestions: choose a TXT following the model!'))
            return render(request, 'exam/exam_errors.html', {})

        listao = UtilsMC.questionsReadFiles(new_persons)
        count = 0
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

                    newQ = Question.objects.create(
                        topic=topic,
                        question_group=qq['st'],
                        question_short_description=qq['c'] + str(qq['n']),
                        question_text=qq['q'],
                        question_type=tp,
                        question_difficulty=df,
                        question_bloom_taxonomy='remember',
                        question_last_update=datetime.date.today(),
                        question_who_created=User.objects.get(username=request.user.username),
                    )
                    for a in qq['a']:
                        Answer.objects.create(
                            question=newQ,
                            answer_text=a,
                            answer_feedback='',
                        )

    return HttpResponseRedirect("../")



#######################################################################
class TopicListView(LoginRequiredMixin, generic.ListView):
    model = Topic
    fields = '__all__'

    # paginate_by = 100

    def get_queryset(self):
        if len(Topic.objects.filter(discipline__discipline_coords=self.request.user)):
            return Topic.objects.filter(discipline__discipline_coords=self.request.user)
        if len(Topic.objects.filter(discipline__discipline_profs=self.request.user)):
            return Topic.objects.filter(discipline__discipline_profs=self.request.user)


class TopicUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Topic
    template_name = 'topic/topic_update.html'
    fields = '__all__'

    def get_queryset(self):
        return Topic.objects.all().distinct()


class TopicDetailView(LoginRequiredMixin, generic.DetailView):
    model = Topic
    template_name = 'topic/topic_detail.html'

    def get_queryset(self):
        return Topic.objects.all().distinct()


class TopicCreate(LoginRequiredMixin, generic.CreateView):
    model = Topic
    fields = '__all__'
    template_name = 'topic/topic_create.html'
    success_url = '/topic/topics'

    def form_valid(self, form):
        d = form.cleaned_data['discipline']
        d_obj = get_object_or_404(Discipline, pk=d[0].pk)
        if not self.request.user in d_obj.discipline_coords.all():
            messages.error(self.request, _("TopicCreate: the user isn't the coordinator of the discipline"))
            return render(self.request, 'exam/exam_errors.html', {})

        return super(TopicCreate, self).form_valid(form)

    def get_queryset(self):
        if len(Topic.objects.filter(discipline__discipline_coords=self.request.user)):
            return Topic.objects.filter(discipline__discipline_coords=self.request.user)
        if len(Topic.objects.filter(discipline__discipline_profs=self.request.user)):
            return Topic.objects.filter(discipline__discipline_profs=self.request.user)


class TopicDelete(LoginRequiredMixin, generic.DeleteView):
    model = Topic
    template_name = 'topic/topic_confirm_delete.html'
    success_url = '/topic/topics'

    def get_queryset(self):
        if len(Topic.objects.filter(discipline__discipline_coords=self.request.user)):
            return Topic.objects.filter(discipline__discipline_coords=self.request.user).distinct()
        if len(Topic.objects.filter(discipline__discipline_profs=self.request.user)):
            return Topic.objects.filter(discipline__discipline_profs=self.request.user).distinct()


###################################################################
class QuestionListView(LoginRequiredMixin, generic.ListView):
    model = Question
    template_name = 'question/question_list.html'

    # paginate_by = 100

    def get_queryset(self):
        return Question.objects.filter(topic__discipline__discipline_profs=self.request.user)


class LoanedQuestionByUserListView(LoginRequiredMixin, generic.ListView):
    model = Question
    template_name = 'question/question_list_who_created_user.html'

    # paginate_by = 100

    def get_queryset(self):
        return Question.objects.filter(question_who_created=self.request.user)


class QuestionDetailView(generic.DetailView):
    model = Question
    template_name = 'question/question_detail.html'

    # paginate_by = 100

    def get_queryset(self):
        return Question.objects.filter(topic__discipline__discipline_profs=self.request.user)


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
            question_inst.save()

        formset = AnswerInlineFormSet(request.POST, request.FILES,
                                      instance=question_inst)
        if formset.is_valid():  # Check if the forms are valid:
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
        if not request.user in profs:
            return HttpResponse("ERROR: The teacher is not registered in the Discipline (of the topic)")

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
        })

    return render(request, 'question/question_update.html', {
        'form': form,
        'formset': formset,
        'questioninst': question_inst,
    })


#########################################################

class QuestionCreate(LoginRequiredMixin, generic.CreateView):
    model = Question
    # fields = '__all__'
    fields = [
        'topic',
        'question_short_description',
        'question_group',
        'question_text',
        'question_type',
        'question_difficulty',
        'question_bloom_taxonomy',
        'question_parametric',
    ]
    template_name = 'question/question_create.html'
    success_url = reverse_lazy('topic:question-create')

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
        return super(QuestionCreate, self).form_valid(form)

    def get_queryset(self):
        return Question.objects.filter(topic__discipline__discipline_profs=self.request.user)


class QuestionUpdate(UpdateView):
    model = Question
    template_name = 'question/question_update.html'
    fields = '__all__'
    success_url = reverse_lazy('topic:question-detail')

    def get_queryset(self):
        return Question.objects.filter(topic__discipline__discipline_profs=self.request.user).distinct()


class QuestionDelete(DeleteView):
    model = Question
    template_name = 'question/question_confirm_delete.html'
    success_url = reverse_lazy('topic:myquestions-list')

    def get_queryset(self):
        return Question.objects.filter(topic__discipline__discipline_profs=self.request.user).distinct()
