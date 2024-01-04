'''
=====================================================================
Copyright (C) 2018-2023 Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of MCTest 5.2.

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
# from django.contrib.auth.models import User
import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from account.models import User
from course.models import Course, Discipline, Classroom
from django.shortcuts import get_object_or_404

# Create your models here.
class Topic(models.Model):
    discipline = models.ManyToManyField(Discipline,
                                        related_name='topics2',  # relacionamento reverso
                                        help_text=_("Choose a discipline for this topic."),
                                        verbose_name=_("Disciplines"),
                                        )
    topic_text = models.CharField(max_length=50,
                                  help_text=_("Tip: Include a prefix in the topic, such as discipline code."),
                                  verbose_name=_("Topic"),
                                  )
    topic_description = models.TextField(default='', blank=True, max_length=200,
                                         verbose_name=_("Description"),
                                         )

    def questions(self):
        mylist = [a for a in Question.objects.all() if a.topic.topic_text == self.topic_text]
        mylist = list(dict.fromkeys(mylist)) # remove duplicates
        return mylist

    questions.short_description = 'Questions'

    def display_Questions(self):
        return ', '.join(
            [a.question_short_description for a in Question.objects.all() if a.topic.topic_text == self.topic_text])

    display_Questions.short_description = 'Questions'

    def get_absolute_url(self):
        return "/topic/topics/"
        # return "../topic/%i" % self.id

    class Meta:
        ordering = ["discipline__discipline_code", "topic_text"]

    def __str__(self): # ok
        d = ','.join([d.discipline_code for d in self.discipline.all()])
        t = self.topic_text
        return '[{0}]<{1}>'.format(d, t)


class Question(models.Model):
    topic = models.ForeignKey(Topic,
                              related_name='questions2',  # relacionamento reverso
                              on_delete=models.CASCADE, null=True,
                              verbose_name=_("Topic"),
                              )
    question_group = models.CharField(default='', blank=True, max_length=50,
                                      help_text=_("Only one question per group will be sorted for each exam (student)"),
                                      verbose_name=_("Question Group"),
                                      )
    question_short_description = models.CharField(max_length=50,
                                                  help_text=_("Enter a short description"),
                                                  verbose_name=_("Short Description"),
                                                  )
    question_text = models.TextField(default='', blank=True,
                                     help_text=_(
                                         "Accepts LaTeX description and parameterization using the Python language (see publications)."),
                                     verbose_name=_("Description"),
                                     )

    question_type_choice = (
        ('QM', _('Multiple-Choice Question')),
        ('QT', _('Text Question')),
    )
    question_type = models.CharField(default='', max_length=2,
                                     choices=question_type_choice,
                                     verbose_name=_("Type"),
                                     )
    question_difficulty_choice = (
        ('1', _('Very easy level question')),
        ('2', _('Easy level question')),
        ('3', _('Mid-level question')),
        ('4', _('Difficult level question')),
        ('5', _('Very Difficult level question')),
    )
    question_difficulty = models.CharField(default='', max_length=2,
                                           choices=question_difficulty_choice,
                                           verbose_name=_("Difficulty"),
                                           )
    question_bloom_choice = (
        ('remember', _('remember: recognizing, recalling')),
        ('understand', _('understand: interpreting, exemplifying, classifying, comparing')),
        ('apply', _('apply: executing, implementing')),
        ('analyze', _('analyze: differentiating, organizing, attibuting')),
        ('evaluate', _('evaluate: checking, critiquing')),
        ('create', _('create: generating, planning, producing')),
    )
    question_bloom_taxonomy = models.CharField(default='', max_length=10,
                                               choices=question_bloom_choice,
                                               verbose_name=_("Bloom Taxonomy"),
                                               )


    question_parametric_choice = (
        ('yes', _('Yes')),
        ('no', _('No')),
    )
    question_parametric = models.CharField(
        default='no', max_length=3,
        choices=question_parametric_choice,
        help_text=_("Question with some randomly chosen values"),
        verbose_name=_("Parametric question"))

    question_last_update = models.DateField(default=datetime.date.today, null=True, blank=True,
                                            verbose_name=_("Last Update"),
                                            )
    question_who_created = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                             verbose_name=_("Who Created"),
                                             )

    ''' Novos campos 04/12/2023
primeiro apaga pyc, makemigrations, migrate, detela exames e depois inclui topicos, makemigrations...
find . -path "*/migrations/*.pyc"  -delete
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations 
python manage.py makemigrations 
python manage.py migrate
brew services restart mysql

mysql -u root -p DB_MCTest
use DB_MCTest;
show tables;
describe topic_question;

ALTER TABLE topic_question
ADD COLUMN question_correction_count INT DEFAULT 0,
ADD COLUMN question_correct_count INT DEFAULT 0,
ADD COLUMN question_IRT_a_discrimination DOUBLE DEFAULT 0.0,
ADD COLUMN question_IRT_b_ability DOUBLE DEFAULT 0.0,
ADD COLUMN question_IRT_c_guessing DOUBLE DEFAULT 0.0;


UPDATE topic_question SET
question_correction_count = IFNULL(question_correction_count, 0),
question_correct_count = IFNULL(question_correct_count, 0),
question_IRT_a_discrimination = IFNULL(question_IRT_a_discrimination, 0.0),
question_IRT_b_ability = IFNULL(question_IRT_b_ability, 0.0),
question_IRT_c_guessing = IFNULL(question_IRT_c_guessing, 0.0);

    '''
    question_correction_count = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name=_("Correction Count"))
    question_correct_count = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name=_("Correct Count"))
    question_IRT_a_discrimination = models.FloatField(default=0.0, null=True, blank=True, verbose_name=_("Discrimination"))
    question_IRT_b_ability = models.FloatField(default=0.0, null=True, blank=True, verbose_name=_("Ability"))
    question_IRT_c_guessing = models.FloatField(default=0.0, null=True, blank=True, verbose_name=_("Guessing"))

    def display_Topic(self):
        return self.topic.topic_text

    display_Topic.short_description = 'Topic'

    def answers(self):
        question_inst = get_object_or_404(Question, pk=self.id)
        return [a for a in question_inst.answers2.all()]
        #return [a for a in Answer.objects.all() if a.question.id == self.id]

    answers.short_description = 'Answers'

    def display_Answers(self):
        question_inst = get_object_or_404(Question, pk=self.id)
        return ', '.join([a.answer_text for a in question_inst.answers2.all()])
        #return ', '.join([a.answer_text for a in Answer.objects.all() if a.question.id == self.id])

    display_Answers.short_description = 'Answers'

    class Meta:
        ordering = ["topic__discipline__discipline_code", "topic__topic_text", "question_type", "question_difficulty",
                    "question_group", "question_short_description"]
        permissions = (("can_mark_update", "Set question as validated"),)

    def get_absolute_url(self):
        return "../question/%i" % self.id

    def __str__(self): # ok
        # u  = ';'.join([d. for d in Discipline.objects.all() if (self.user
        # d = ';'.join([d.discipline_code for d in Discipline.objects.all() if (d in self.topic.discipline.all())])
        # t = ';'.join([t.topic_text for t in Topic.objects.all() if (t == self.topic)])
        d = 'oi_d_lento'
        t = self.topic.topic_text
        df = "dif " + self.question_difficulty
        g = "gro " + self.question_group
        p = "par " + self.question_parametric
        tp = "typ " + self.question_type
        id = "#" + str(self.id).zfill(4)
        des = "des " + self.question_short_description
        ans = "ans " + str(self.answers2.all().count())
        return '{0}; top {1}; {2}; {3}; {4}; {5}; {6}; {7}; {8}'.format(d, t, tp, df, g, p, id, ans, des)


class Answer(models.Model):
    question = models.ForeignKey(Question,
                                 related_name='answers2',  # relacionamento reverso
                                 on_delete=models.CASCADE
                                 )
    answer_text = models.TextField(default='', max_length=200,
                                   verbose_name=_("Answer Text"),
                                   )

    answer_feedback = models.TextField(default='', max_length=200, blank=True,
                                       verbose_name=_("Answer Feedback"),
                                       )

    def display_Question(self):
        return self.question.question_text

    display_Question.short_description = 'Question'

    class Meta:
        ordering = ["id"]

    # def __str__(self):
    #     return '[{0}]  {1}'.format(self.question.question_short_description, self.answer_text)
