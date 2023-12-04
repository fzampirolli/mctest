'''
=====================================================================
Copyright (C) 2018-2023 Francisco de Assis Zampirolli
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
from django.urls import path

from . import views

app_name = 'exam'
urlpatterns = [
    path('exams/', views.ExamListView.as_view(), name=''),
    path('myexams/', views.LoanedExamByUserListView.as_view(), name='myexams'),
    path('exam/<int:pk>', views.ExamDetailView.as_view(), name='exam-detail'),
    path('exam/create/', views.ExamCreate.as_view(), name='exam-create'),
    path('exam/<int:pk>/createPDF/', views.SerializersExam, name='exam-createPDF'),
    path('exam/<int:pk>/generate/', views.generate_page, name='generate_page'),
    path('exam/<int:pk>/delete/', views.ExamDelete.as_view(), name='exam-delete'),
    path('exam/<int:pk>/update/', views.UpdateExam, name='exam_update'),
    path('exam/<int:pk>/correct/', views.correctStudentsExam, name='exam-correct'),
    path('exam/<int:pk>/variation/', views.variationsExam, name='exam-variation'),
    path('exam/<int:pk>/sendFeedbackStudents/', views.feedbackStudentsExam, name='exam-feedback'),
    path('exam/<int:pk>/sendFeedbackStudentsText/', views.feedbackStudentsExamText, name='exam-feedback'),
]
