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
from django.db import models


# from django.apps import apps

# Create your models here.
class Student(models.Model):
    student_name = models.CharField(max_length=50)
    student_ID = models.CharField(max_length=20)
    student_email = models.EmailField()

    # Classroom = apps.get_model('student', 'Classroom')

    # classrooms = models.ForeignKey(Classroom,
    #                             related_name='classrooms2',  # relacionamento reverso
    #                             on_delete=models.CASCADE
    #                             )
    class Meta:
        ordering = ["student_name"]

    def __str__(self):
        return '; '.join([self.student_ID, self.student_name, self.student_email])
