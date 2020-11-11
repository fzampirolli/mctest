'''
=====================================================================
Copyright (C) 2019 Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of webMCTest 1.1 (or MCTest 5.1).

Languages: Python 3.7, Django 2.2.4 and many libraries described at
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
from django.utils.translation import gettext_lazy as _

from .models import Question, Topic, User


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

    def __init__(self, *args, **kwargs):
        super(UpdateQuestionForm, self).__init__(*args, **kwargs)
        try:
            #user = kwargs['initial']['question_who_created']
            #self.fields['topic'].queryset = Topic.objects.filter(discipline__discipline_profs=user)
            c = Discipline.objects.filter()
            self.fields['question_who_created'].queryset = c.objects.filter(discipline__discipline_profs=user)
        except:
            pass
