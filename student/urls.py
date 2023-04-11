'''
=====================================================================
Copyright (C) 2018-2023 Francisco de Assis Zampirolli
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
from django.urls import path

from . import views

app_name = 'student'

urlpatterns = [
    # path('student', IndexTemplateView.as_view(), name="index"),
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('classroom/<int:pk>/student/create/', views.StudentCreate.as_view(), name='student-create'),
    path('student/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('student/<int:pk>/delete/', views.StudentDelete.as_view(), name='student-delete'),
    path('student/<int:pk>/update', views.StudentUpdate.as_view(), name='student-update'),
]
