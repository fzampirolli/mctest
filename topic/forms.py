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
from django import forms
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from .models import Question, Topic, User, Discipline


class TopicCreateForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(TopicCreateForm, self).__init__(*args, **kwargs)
        try:
            d1 = Discipline.objects.filter(discipline_profs=user)
            d2 = Discipline.objects.filter(discipline_coords=user)
            self.fields['discipline'].queryset = (d1 | d2).distinct()
        except:
            pass

class TopicUpdateForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(TopicUpdateForm, self).__init__(*args, **kwargs)
        try:
            d1 = Discipline.objects.filter(discipline_profs=user)
            d2 = Discipline.objects.filter(discipline_coords=user)
            self.fields['discipline'].queryset = (d1 | d2).distinct()
        except:
            pass

class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
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

        # template_name = 'question/question_create.html'
        # success_url = reverse_lazy('topic:question-create')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(QuestionCreateForm, self).__init__(*args, **kwargs)
        try:
            t1 = Topic.objects.filter(discipline__discipline_profs=user)
            t2 = Topic.objects.filter(discipline__discipline_coords=user)
            self.fields['topic'].queryset = (t1 | t2).distinct()
        except:
            pass


class UpdateQuestionForm(forms.Form):
    topic = forms.ModelChoiceField(queryset=Topic.objects.all(),
                                   label=_("Topic"))

    question_short_description = forms.CharField(
        label=_("Short Description"))
    question_group = forms.CharField(required=False,
                                     help_text=_("Only one question per group will be sorted for each exam"),
                                     label=_("Group"))
    question_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 4}),
                                    help_text=_("Description (you can include latex format)"),
                                    label=_("Description"))
    question_type = forms.ChoiceField(choices=Question.question_type_choice,
                                      label=_("Type"))
    question_difficulty = forms.ChoiceField(choices=Question.question_difficulty_choice,
                                            label=_("Difficulty"))
    question_bloom_taxonomy = forms.ChoiceField(choices=Question.question_bloom_choice,
                                                label=_("Bloom Taxonomy"))
    question_parametric = forms.ChoiceField(choices=Question.question_parametric_choice,
                                            help_text=_("Question with some randomly chosen values"),
                                            label=_("Parametric question"))
    question_who_created = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label=_("Who Created"))
    question_last_update = forms.DateField(
        label=_("Last Update"))


    # Novos campos 04/12/2023
    question_correction_count = forms.IntegerField(label=_("Correction Count"))
    question_correct_count = forms.IntegerField(label=_("Correct Count"))
    question_IRT_a_discrimination = forms.FloatField(label=_("Discrimination"))
    question_IRT_b_ability = forms.FloatField(label=_("Ability"))
    question_IRT_c_guessing = forms.FloatField(label=_("Guessing"))

    def __init__(self,  *args, **kwargs):
        super(UpdateQuestionForm, self).__init__(*args, **kwargs)
        try:
            user = kwargs.pop('user')#kwargs['initial']['question_who_created']
            t1 = Topic.objects.filter(discipline__discipline_profs=user)
            t2 = Topic.objects.filter(discipline__discipline_coords=user)
            self.fields['topic'].queryset = (t1 | t2).distinct()

            c = Discipline.objects.filter()
            self.fields['question_who_created'].queryset = c.objects.filter(discipline__discipline_profs=user)
        except:
            pass
