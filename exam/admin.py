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
from django.contrib import admin

# Register your models here.
from .models import Exam, StudentExam, StudentExamQuestion, ClassroomExam


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_filter = ('exam_who_created', 'classrooms',)
    date_hierarchy = 'exam_hour'
    filter_horizontal = ('questions', 'classrooms',)


@admin.register(StudentExam)
class StudentExamAdmin(admin.ModelAdmin):
    pass


@admin.register(StudentExamQuestion)
class StudentExamAdmin(admin.ModelAdmin):
    pass


@admin.register(ClassroomExam)
class StudentExamAdmin(admin.ModelAdmin):
    pass
