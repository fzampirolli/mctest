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
from django.db import models
# from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from account.models import User
from course.models import Classroom
from student.models import Student
from topic.models import Question
from topic.models import Topic

# Create your models here.
class Exam(models.Model):
    exam_name = models.CharField(
        max_length=20, null=True,
        help_text=_("Exam name, for example, Exam 1"),
        verbose_name=_("Exam name"))
    classrooms = models.ManyToManyField(Classroom,
                                        related_name='exams2',  # relacionamento reverso
                                        #blank=True,
                                        help_text=_("Choose the classrooms"),
                                        verbose_name=_("Classrooms"))
    questions = models.ManyToManyField(Question,
                                       related_name='exams2',  # relacionamento reverso
                                       blank=True,
                                       help_text=_("Choose the questions"),
                                       verbose_name=_("Questions"))

    ''' NOVO: 27/11/2023  NÃO CONSEGUI INCLUIR EM UM BD JÁ EXISTENTE
    primeiro apaga pyc, makemigrations, migrate, detela exames e depois inclui topicos, makemigrations...
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
mysql -u root -p DB_MCTest < "mysql-2023-11-30.sql"
## deixar comentado topics question_* (novos)
python manage.py shell < _delete_exams_classrooms_students.py
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
python manage.py makemigrations
python manage.py migrate
## descomentar topics e question_* (novos)
brew services restart mysql
python manage.py makemigrations
python manage.py migrate
    '''
    topics = models.ManyToManyField(Topic,
                                       related_name='exams2',  # relacionamento reverso
                                       blank=True,
                                       help_text=_("Choose the topics"),
                                       verbose_name=_("Topics"))

    exam_number_of_questions_var1 = models.CharField(
        default=20, max_length=3,
        help_text=_("Number of questions with difficulty level x"),
        verbose_name=_("Difficulty 1"))
    exam_number_of_questions_var2 = models.CharField(
        default=0, max_length=3,
        verbose_name=_("Difficulty 2"))
    exam_number_of_questions_var3 = models.CharField(
        default=0, max_length=3,
        verbose_name=_("Difficulty 3"))
    exam_number_of_questions_var4 = models.CharField(
        default=0, max_length=3,
        verbose_name=_("Difficulty 4"))
    exam_number_of_questions_var5 = models.CharField(
        default=0, max_length=3,
        verbose_name=_("Difficulty 5"))

    exam_number_of_anwsers_question = models.CharField(
        default='5', max_length=2,
        choices=tuple((str(x), str(x)) for x in range(2, 11)),
        help_text=_("Number of answers per question"),
        verbose_name=_("Answers per question"))
    exam_number_of_questions_text = models.CharField(
        default=0, max_length=3,
        help_text=_("Number of textual questions"),
        verbose_name=_("Textual"))
    exam_variations = models.CharField(
        default=2, max_length=3,
        help_text=_("Number of exam variations"),
        verbose_name=_("Variations"))
    exam_max_questions_square = models.CharField(
        default='10', max_length=2,
        choices=tuple((str(x), str(x)) for x in range(3, 51)),
        help_text=_("Number of questions per block"),
        verbose_name=_("Questions by block"))
    exam_max_squares_horizontal = models.CharField(
        default='1', max_length=2,
        choices=tuple((str(x), str(x)) for x in range(1, 6)),
        help_text=_("Maximum number of blocks horizontally"),
        verbose_name=_("Max blocks horiz."))
    exam_stylesheet_choice = (
        ('Hor', 'Horizontal'),
        ('Ver', 'Vertical'),
    )
    exam_stylesheet = models.CharField(
        default='Hor', max_length=3,
        choices=exam_stylesheet_choice,
        help_text=_("Presentations of questions in stylesheet"),
        verbose_name=_("Stylesheet"))
    exam_print_choice = (
        ('answ', _('Answers')),
        ('ques', _('Questions')),
        ('both', _('Both')),
    )
    exam_print = models.CharField(
        default='answ', max_length=4,
        choices=exam_print_choice,
        help_text=_("Generate answersheets; questions; both"),
        verbose_name=_("Answersheets/Questions/Both"))
    exam_print_eco_choice = (
        ('yes', _('Yes')),
        ('no', _('No')),
    )
    exam_print_eco = models.CharField(
        default='yes', max_length=3,
        choices=exam_print_eco_choice,
        help_text=_("Ecological (reduce number of sheets)"),
        verbose_name=_("Ecological"))
    exam_student_feedback_choice = (
        ('yes', _('Yes - feedback: Header and All Questions; *createPDF* >> SEND EMAIL TO STUDENT WITH YOUR EXAM')),
        # ('yes2', _('Yes - Only Header - area between the 4 black disks')),
        # ('yes3', _('Yes - ATTENTION - SEND AN EMAIL to each studente with your EXAM, WHEN PRESS Create-PDF!')),
        ('no', _('No')),
    )
    exam_student_feedback = models.CharField(
        default='no', max_length=3,
        blank=True,
        choices=exam_student_feedback_choice,
        help_text=_("Send feedback to the student"),
        verbose_name=_("Student Feedback"))
    exam_room = models.CharField(
        max_length=20, null=True, blank=True,
        help_text=_("Classroom where the exam will be held"),
        verbose_name=_("Classroom/Lab."))
    exam_hour = models.DateTimeField(
        help_text=_("Date/Hour of exam, format: DD/MM/YYYY HH:MM:SS"),
        verbose_name=_("Date Hour"))
    exam_term_choice = (
        ('t1', _('First term')),
        ('t2', _('Second term')),
        ('t3', _('Third term')),
    )
    exam_term = models.CharField(
        default='t1', max_length=2,
        choices=exam_term_choice,
        help_text=_("Term of exam"),
        verbose_name=_("Term"))
    # exam_output_choice = (
    #     ('pdf', _('PDF output')),
    #     ('moodle1', _('Moodle1 output')),
    #     ('moodle2', _('Moodle1 output')),
    # )
    # exam_output = models.CharField(
    #     default='pdf', max_length=2, null=True, blank=True,
    #     choices=exam_output_choice,
    #     help_text=_("Output of exam"),
    #     verbose_name=_("Output"))
    exam_who_created = models.ForeignKey(User,
                                         on_delete=models.SET_NULL, null=True,
                                         help_text=_("Who created this exam"),
                                         verbose_name=_("Who created"))
    #    exam_profs_header = models.CharField(
    #        default='yes',max_length=3,
    #        blank=True, null=True,
    #        choices=exam_print_eco_choice,
    #        help_text = _("Show teacher(s) in the exam header"),
    #        verbose_name=_("Teachers in header"))
    exam_instructions = models.TextField(
        default=_('\item turning off the phone'), blank=True,
        help_text=_("Exam instructions, for example, '\item turning off the phone'"),
        verbose_name=_("Instructions"))

    class Meta:
        ordering = ["classrooms__discipline__courses__institutes__institute_code",
                    "classrooms__discipline__discipline_code",
                    "classrooms__classroom_code",
                    "exam_name"]

    '''
    def get_form(self, form_class=None):
        form = super(ExamUpdate, self).get_form(form_class)
        form.fields['questions'].queryset = Question.object.filter(topic__discipline__discipline_profs=self.request.user)
        return form
    '''

    def __str__(self): # ok
        return self.exam_name
        # cod = [c.discipline.discipline_code for c in self.classrooms.all()]
        # if cod:
        #     cod = str(cod[0])
        # else:
        #     cod = ''
        # return ' - '.join([
        #     cod,
        #     ','.join([c.classroom_code for c in self.classrooms.all()]),
        #     self.exam_name])

# new 08/12/20: exame tem variacoes
class VariationExam(models.Model):
    exam = models.ForeignKey(Exam,
                             related_name='variationsExams2',  # relacionamento reverso
                             on_delete=models.CASCADE, null=True,
                             verbose_name=_("Exam"),
                             )
    variation = models.TextField(default='', blank=True,
                                 help_text=_(
                                     "Accepts LaTeX description and parameterization using the Python language (see publications)."),
                                 verbose_name=_("Description"),
                                 )

class StudentExam(models.Model):
    exam = models.ForeignKey(Exam,
                             related_name='studentExams2',  # relacionamento reverso
                             on_delete=models.CASCADE, null=True,
                             verbose_name=_("Exam"),
                             )
    student = models.ForeignKey(Student,
                                related_name='studentExams2',  # relacionamento reverso
                                on_delete=models.CASCADE, null=True,
                                verbose_name=_("Student"),
                                )
    grade = models.CharField(max_length=20,
                             verbose_name=_("Exam Grade"),
                             )

class StudentExamQuestion(models.Model):
    studentExam = models.ForeignKey(StudentExam,
                                    related_name='studentExamQuestions2',  # relacionamento reverso
                                    on_delete=models.CASCADE, null=True,
                                    verbose_name=_("Student Exam"),
                                    )
    question = models.ForeignKey(Question,
                                 related_name='studentExamQuestions2',  # relacionamento reverso
                                 on_delete=models.CASCADE, null=True,
                                 verbose_name=_("Exam Question"),
                                 )
    studentAnswer = models.CharField(max_length=2,
                                     verbose_name=_("Student Answer"),
                                     )
    answersOrder = models.CharField(max_length=10,
                                    verbose_name=_("Answers Order"),
                                    )

# new 30/7/19: nota final do aluno na disciplina/turma
class ClassroomExam(models.Model):
    exam = models.ForeignKey(Exam,
                             related_name='classroomExams2',  # relacionamento reverso
                             on_delete=models.CASCADE, null=True,
                             verbose_name=_("Exam"),
                             )
    classroom = models.ForeignKey(Classroom,
                                  related_name='classroomExams2',  # relacionamento reverso
                                  on_delete=models.CASCADE, null=True,
                                  verbose_name=_("Student"),
                                  )
    grade = models.CharField(max_length=20,
                             verbose_name=_("Discipline Grade"),
                             )

