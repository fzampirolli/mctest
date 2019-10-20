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
from django.urls import path

from . import views

app_name = 'course'

urlpatterns = [
    # path('institute', IndexTemplateView.as_view(), name="index"),
    path('institutes/', views.InstituteListView.as_view(), name='institute-list'),
    path('institute/create/', views.InstituteCreate.as_view(), name='institute-create'),
    path('institute/<int:pk>/', views.InstituteDetailView.as_view(), name='institute-detail'),
    path('institute/<int:pk>/delete/', views.InstituteDelete.as_view(), name='institute-delete'),
    path('institute/<int:pk>/update', views.InstituteUpdate.as_view(), name='institute-update'),
]

urlpatterns += [
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('course/create/', views.CourseCreate.as_view(), name='course-create'),
    path('course/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('course/<int:pk>/delete/', views.CourseDelete.as_view(), name='course-delete'),
    path('course/<int:pk>/update', views.CourseUpdate.as_view(), name='course-update'),
]

urlpatterns += [
    path('disciplines/', views.DisciplineListView.as_view(), name='discipline-list'),
    path('discipline/create/', views.DisciplineCreate.as_view(), name='disciplines-create'),
    path('discipline/<int:pk>/', views.DisciplineDetailView.as_view(), name='discipline-detail'),
    path('discipline/<int:pk>/delete/', views.DisciplineDelete.as_view(), name='discipline-delete'),
    path('discipline/<int:pk>/update', views.DisciplineUpdate.as_view(), name='discipline-update'),
    path('discipline/<int:pk>/import/', views.ImportProfsDiscipline, name='discipline-profs-import'),
    path('discipline/<int:pk>/import2/', views.ImportClassroomsDiscipline, name='discipline-classrooms-import'),
]

urlpatterns += [
    # path('classrooms/',               views.ClassroomListView.as_view(), name=''),
    path('classroomsmy/', views.LoanedClassroomByUserListView.as_view(), name='classroom-mylist'),
    path('classroom/create/', views.ClassroomCreate.as_view(), name='classroom-create'),
    path('classroom/<int:pk1>/student/<int:pk2>/delete', views.ClassroomStudentDelete, name='classroom-student-delete'),
    # path('classroom/<int:pk>/student/create', views.ClassroomStudentCreate, name='classroom-student-create'),
    path('classroom/<int:pk>', views.ClassroomDetailView.as_view(), name='classroom-detail'),
    path('classroom/<int:pk>/delete/', views.ClassroomDelete.as_view(), name='classroom-delete'),
    path('classroom/<int:pk>/update', views.ClassroomUpdate.as_view(), name='classroom-update'),
    path('classroom/<int:pk>/import/', views.ImportStudentsClassroom, name='classroom-students-import'),
]
