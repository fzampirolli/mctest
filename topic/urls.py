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
from django.urls import path
from course import views as vi
from . import views
from django.urls import reverse

app_name = 'topic'

urlpatterns = [
    path('topics/', views.TopicListView.as_view(), name='topic-list'),
    path('topic/<int:pk>', views.TopicDetailView.as_view(), name='topic-detail'),
]
urlpatterns += [
    path('topic/create/', views.TopicCreate.as_view(), name='topic-create'),
    path('topic/<int:pk>/delete/', views.TopicDelete.as_view(), name='topic-delete'),
    path('topic/<int:pk>/update', views.TopicUpdate.as_view(), name='topic-update'),
    path('topic/<int:pk>/createPDFtopic/', views.see_topic_PDF, name='topic-create-PDF'),
    path('course/<int:pk>/', vi.DisciplineDetailView.as_view(), name='discipline-detail'),
]

urlpatterns += [
    path('questions/', views.QuestionListView.as_view(), name='question-list'),
    path('myquestions/', views.LoanedQuestionByUserListView.as_view(), name='myquestions-list'),
    path('myquestions/import/', views.ImportQuestions, name='myquestions-import'),
    path('myquestions/importImage/', views.ImportQuestionsImage, name='myquestions-import-image'),
    path('myquestions/importJson/', views.ImportQuestionsJson, name='myquestions-import-Json'),
    path('question/<int:pk>/createPDF/', views.see_question_PDF, name='question-create-question-PDF'),
    path('question/<int:pk>/saveJson/', views.save_question_Json, name='question-save-Json'),
]
urlpatterns += [
    path('question/create/', views.QuestionCreate.as_view(), name='question-create'),
    path('question/<int:pk>', views.QuestionDetailView.as_view(), name='question-detail'),
    path('question/<int:pk>/update/', views.UpdateQuestion, name='question-update'),
    path('question/<int:pk>/delete/', views.QuestionDelete.as_view(), name='question-delete'),
    path('question/<int:pk>/copy/', views.copy_question, name='copy_question'),
    path('ai-assist/', views.ai_assist, name='ai_assist'),  # Adicione esta linha para a IA Assistência
]

