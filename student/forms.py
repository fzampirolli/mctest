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

webMCTest is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License
(gnu.org/licenses/agpl-3.0.txt) as published by the Free Software
Foundation, either version 3 of the License, or (at your option) 
any later version.

webMCTest is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

=====================================================================
'''
from django import forms
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from course.models import Classroom


class CreateStudentForm(forms.Form):
    # classroom = forms.ModelChoiceField(queryset=Classroom.objects.all(),
    #                               label=_("Classroom"))
    student_ID = forms.CharField(
        help_text=_("id"),
        label=_("Student ID"))

    student_name = forms.CharField(
        help_text=_("name"),
        label=_("Student Name"))

    student_email = forms.CharField(
        help_text=_("email"),
        label=_("Student Email"))

    def __init__(self, *args, **kwargs):
        # super(CreateStudentForm, self).__init__(*args, **kwargs)
        try:  # ao criar um exame, é necessário definir uma classe, então....

            # pego a classe do estudante
            classroomID = kwargs['initial']['classrooms']
            classroom = get_object_or_404(Classroom, pk=classroomID[0])

            self.fields[
                'classrooms'].queryset = classroom  # Classroom.objects.filter(discipline__discipline_profs=user)
        except:
            pass
