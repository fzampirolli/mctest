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
from django import forms
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from course.models import Classroom, Discipline
from topic.models import Question, User, Topic
from .models import Exam


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


class ExamCreateForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            'exam_name',
            'classrooms',
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ExamCreateForm, self).__init__(*args, **kwargs)

        classes = []
        for d in Discipline.objects.filter(discipline_coords=user):
            for p in d.classrooms2.all():
                classes.append(p.pk)

        for d in Discipline.objects.filter(discipline_profs=user):
            for c in d.classrooms2.all():
                if user in c.classroom_profs.all():
                    classes.append(c.pk)

        # se é coord, mostra todas as turmas das disciplinas que coordena
        if classes:
            self.fields['classrooms'].queryset = Classroom.objects.filter(pk__in=classes).order_by()
        else:
            self.fields['classrooms'].queryset = Classroom.objects.filter(classroom_profs=user)

class UpdateExamForm(forms.Form):
    exam_name = forms.CharField(
        max_length=20,
        help_text=_("Exam name, for example, Exam 1"),
        label=_("Exam name"))
    classrooms = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Classroom.objects.all(),
        help_text=_("Choose the classrooms"),
        label=_("Classrooms"))

    #  NÃO CONSEGUI INCLUIR EM UM BD JÁ EXISTENTE
    # topics = forms.ModelMultipleChoiceField(
    #     widget=forms.CheckboxSelectMultiple,
    #     queryset=Topic.objects.all(),
    #     help_text=_("Choose the topics"),
    #     label=_("Topics"))

    questions = forms.ModelMultipleChoiceField(required=False,
                                               widget=forms.CheckboxSelectMultiple,
                                               queryset=Question.objects.filter(),
                                               # queryset=Question.objects.filter(topic__discipline__discipline_profs=user),
                                               help_text=_("Choose the questions"),
                                               label=_("Questions"))
    exam_number_of_questions_var1 = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'size': '5', 'class': 'inputText'}),
        help_text=_("Number of questions with difficulty level x"),
        label=_("Difficulty 1"))
    exam_number_of_questions_var2 = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'size': '5', 'class': 'inputText'}),
        label=_("Difficulty 2"))
    exam_number_of_questions_var3 = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'size': '5', 'class': 'inputText'}),
        label=_("Difficulty 3"))
    exam_number_of_questions_var4 = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'size': '5', 'class': 'inputText'}),
        label=_("Difficulty 4"))
    exam_number_of_questions_var5 = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'size': '5', 'class': 'inputText'}),
        help_text=_("The system first draws the questions with difficulty 1, then 2, ..."),
        label=_("Difficulty 5"))
    exam_number_of_anwsers_question = forms.ChoiceField(
        choices=tuple((str(x), str(x)) for x in range(2, 11)),
        help_text=_("Number of answers per question"),
        label=_("Answers per question"))
    exam_number_of_questions_text = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'size': '5', 'class': 'inputText'}),
        help_text=_("Number of textual questions"),
        label=_("Textual"))
    exam_variations = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'size': '5', 'class': 'inputText'}),
        help_text=_("Number of exam variations"),
        label=_("Variations"))
    exam_max_questions_square = forms.ChoiceField(
        choices=tuple((str(x), str(x)) for x in range(3, 51)),
        help_text=_("Number of questions per block"),
        label=_("Questions by block"))
    exam_max_squares_horizontal = forms.ChoiceField(
        choices=tuple((str(x), str(x)) for x in range(1, 6)),
        help_text=_("Maximum number of blocks horizontally"),
        label=_("Max blocks horiz."))
    exam_stylesheet = forms.ChoiceField(
        choices=Exam.exam_stylesheet_choice,
        help_text=_("Presentations of questions in stylesheet"),
        label=_("Stylesheet"))
    exam_print = forms.ChoiceField(
        choices=Exam.exam_print_choice,
        help_text=_("Generate answersheets; questions; both"),
        label=_("Answersheets/Questions/Both"))
    exam_print_eco = forms.ChoiceField(
        choices=Exam.exam_print_eco_choice,
        help_text=_("Ecological (reduce number of sheets)"),
        label=_("Ecological"))
    exam_student_feedback = forms.ChoiceField(
        choices=Exam.exam_student_feedback_choice,
        help_text=_("Send feedback to the student - Very attention! If you choose YES, an exam will be emailed to "
                    "each student after clicking createPDF."),
        label=_("Student Feedback"))
    #    exam_room = forms.CharField(
    #        max_length=20,
    #        widget=forms.TextInput(attrs={'size':'5', 'class':'inputText'}),
    #        help_text = _("Classroom where the exam will be held"),
    #        label=_("Classroom/Lab."))
    exam_hour = forms.DateField(
        help_text=_("Date of exam, format: DD/MM/YYYY"),
        label=_("Date Hour"))
    exam_term = forms.ChoiceField(
        choices=Exam.exam_term_choice,
        help_text=_("Term of exam"),
        label=_("Term"))
    # exam_output = forms.ChoiceField(
    #     choices=Exam.exam_output_choice,
    #     help_text=_("Output of exam"),
    #     label=_("Output"))
    exam_who_created = forms.ModelChoiceField(
        queryset=User.objects.order_by('email'),
        help_text=_("Who created this exam"),
        label=_("Who created"))
    #    exam_profs_header = forms.ChoiceField(
    #        choices = Exam.exam_print_eco_choice,
    #        help_text = _("Show teacher(s) in the exam header"),
    #        label=_("Teachers in header"))
    exam_instructions = forms.CharField(required=False,
                                        widget=forms.Textarea(attrs={'cols': 80, 'rows': 4}),
                                        help_text=_("Exam instructions, for example, '\item turning off the phone'"),
                                        label=_("Instructions"))

    def __init__(self, *args, **kwargs):
        super(UpdateExamForm, self).__init__(*args, **kwargs)
        try:  # ao criar um exame, é necessário definir uma classe!!! então....

            # pego a classe do exame
            classroomID = kwargs['initial']['classrooms']
            classroom = get_object_or_404(Classroom, pk=classroomID[0])

            # pego todas as questoes da disciplina a qual a classe pertence
            questions = Question.objects.filter(topic__discipline__pk=classroom.discipline.pk)

            # pego todas as classes da disciplina a qual o exame pertence, se coordenador
            discipline = get_object_or_404(Discipline, pk=classroom.discipline.pk)
            # classrooms = Classroom.objects.filter(discipline__pk=discipline.pk)
            usuario = kwargs['initial']['exam_who_created']  # usuário do exame
            qs = []
            for p in discipline.discipline_coords.all():
                if usuario == p:
                    qs = discipline.classrooms2.all()
                    break

            # pego todas as classes da disciplina que o professor possui
            if not qs:
                for c in discipline.classrooms2.all():  # Classroom.objects.filter(discipline__discipline_profs__email=p.email):
                    for p in c.classroom_profs.all():
                        if p == usuario:
                            qs.append(c.pk)
                qs = Classroom.objects.filter(pk__in=qs)

            #  NÃO CONSEGUI INCLUIR EM UM BD JÁ EXISTENTE
            #topics = Topic.objects.filter(discipline__discipline_pk=discipline.pk)
            #self.fields['topics'].queryset = discipline.topics2.all()

            self.fields[
                'questions'].queryset = questions  # Question.objects.filter(topic__discipline__discipline_profs=user)

            self.fields[
                'classrooms'].queryset = qs  # Classroom.objects.filter(discipline__discipline_profs=user)

        except:
            pass
