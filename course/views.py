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
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from tablib import Dataset

from account.models import User
from student.models import Student
from .models import Institute, Course, Discipline, Classroom
from .resources import StudentResource


@login_required
def ImportClassroomsDiscipline(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


    discipline = get_object_or_404(Discipline, pk=pk)

    if request.method == 'POST':
        dataset = Dataset()
        try:
            new_persons = request.FILES['myfileClassrooms']
            pass
        except:
            messages.error(request, _('ImportClassroomsDiscipline: choose a CSV following the model'))
            return render(request, 'exam/exam_errors.html', {})

        f = new_persons.read().decode('utf-8')

        for c in discipline.classrooms2.all():  # para cada classe da disciplina
            for s in c.students.all():  # remover os alunos existentes da classe
                c.students.remove(s)

        mystr4 = '/course/discipline/' + str(pk) + '/update'
        messages.info(request, _('Return to: ') + '<a href="' + mystr4 + '">link</a>', extra_tags='safe')
        messages.info(request, _('Discipline name') + ' >> ' + discipline.discipline_name, extra_tags='upper')

        contS = 0
        for row in f.split('\n'):
            r = row.split(',')

            if len(r) < 2:
                r = row.split(';')

            if len(r) == 7:
                emailProf = r[6] = r[6].lstrip().rstrip()
                if not User.objects.filter(email=emailProf):  # verificar se professor não existe
                    if [i for u in discipline.courses.all() for i in u.institutes.all() if
                        i.institute_url[4:] == emailProf[emailProf.find('@') + 1:]]:
                        messages.error(request,
                                       _('ImportClassroomsDiscipline: The teacher is not registered in webMCTest'))
                        return render(request, 'exam/exam_errors.html', {})

                for p in User.objects.filter(email=emailProf):  # registrar prof na disciplina, se não estiver
                    if p not in discipline.discipline_profs.all():
                        discipline.discipline_profs.add(p)

                ID = r[0].lstrip().rstrip()
                try:
                    ra_int = int(ID)
                except:
                    messages.error(request, _('ImportClassroomsDiscipline: ID must be digits only: ') + ID)
                    return render(request, 'exam/exam_errors.html', {})

                nome = r[1].lstrip().rstrip()
                if len(nome) > 50:
                    nome = nome[:50]
                emailSt = r[2].lstrip().rstrip()
                codigo = r[3].lstrip().rstrip()
                sala = r[4].lstrip().rstrip()
                modo = r[5].lstrip().rstrip()

                try:  # ATENCAO: NAO FAZ NADA SE ESTUDANTE JÁ EXISTIR, PARA NAO APAGAR DADOS ANTIGOS NO BD
                    s = Student.objects.get(student_ID=ID)
                    #s.delete()
                except:
                    #pass
                    s = Student.objects.create(
                        student_ID=ID,
                        student_name=nome,
                        student_email=emailSt,
                    )

                try:
                    c = Classroom.objects.get(classroom_code=codigo)
                except Classroom.DoesNotExist:
                    c = None
                if not c:
                    c = Classroom.objects.create(
                        discipline=discipline,
                        classroom_code=codigo,
                        classroom_room=sala,
                        classroom_days='',
                        classroom_type=modo,
                    )

                for p in User.objects.filter(email=emailProf):  # add prof in CLASSROOM if there is not
                    if p not in c.classroom_profs.all():
                        c.classroom_profs.add(p)

                c.students.add(s)  # add student in CLASSROOM

        # Show messages
        countClasses = 0
        for c in discipline.classrooms2.all():
            countClasses += 1
            messages.info(request, _('Classroom') + ' >> ' + c.classroom_code, extra_tags='upper')
            for p in c.classroom_profs.all():
                mystr4 = 'PROF: ' + str(countClasses) + '; ' + p.first_name + '; ' + p.last_name + '; ' + p.email
                messages.info(request, mystr4)

            contS = 0
            for s in c.students.all():
                contS += 1
                mystr4 = str(contS) + ';    ' + s.student_ID + '; ' + s.student_name + '; ' + s.student_email
                messages.info(request, mystr4)

        messages.info(request, _('Discipline profs'), extra_tags='upper')
        contS = 0
        for p in discipline.discipline_profs.all():
            contS += 1
            mystr4 = str(contS) + ';    ' + p.first_name + '; ' + p.last_name + '; ' + p.email
            messages.info(request, mystr4)

    return render(request, 'exam/exam_msg.html', {})
    # return HttpResponseRedirect("/course/discipline/" + str(pk) + "/update")


@login_required
def ImportProfsDiscipline(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    discipline = get_object_or_404(Discipline, pk=pk)

    if request.method == 'POST':
        dataset = Dataset()
        try:
            new_persons = request.FILES['myfileProfs']
        except:
            messages.error(request, _('ImportProfsDiscipline: choose a CSV following the model!'))
            return render(request, 'exam/exam_errors.html', {})

        f = new_persons.read().decode('utf-8')

        mystr4 = '/course/discipline/' + str(pk) + '/update'
        messages.info(request, _('Return to: ') + '<a href="' + mystr4 + '">link</a>', extra_tags='safe')
        messages.info(request, _('Discipline profs') + ' >> ' + discipline.discipline_name, extra_tags='upper')

        count = 0
        for row in f.split('\n'):
            r = row.split(',')

            if len(r) < 2:
                r = row.split(';')

            if len(r) == 3:
                count += 1

                emailProf = r[2].lstrip().rstrip()
                if not User.objects.filter(email=emailProf):  # criar professor se não existir
                    username = emailProf[:emailProf.find('@')]
                    if len(username) > 15:
                        username = username[:15]
                    if [i for u in discipline.courses.all() for i in u.institutes.all() if
                        i.institute_url[4:] == emailProf[emailProf.find('@') + 1:]]:
                        p = User.objects.create(
                            first_name=r[0].lstrip().rstrip(),
                            last_name=r[1].lstrip().rstrip(),
                            email=emailProf,
                            username=username,
                        )

                g = Group.objects.get(name='professor')
                for p in User.objects.filter(email=emailProf):
                    if p not in discipline.discipline_profs.all():
                        p.groups.add(g)
                        discipline.discipline_profs.add(p)
        contS = 0
        for p in discipline.discipline_profs.all():
            contS += 1
            mystr4 = str(contS) + ';    ' + p.first_name + '; ' + p.last_name + '; ' + p.email
            messages.info(request, mystr4)

    return render(request, 'exam/exam_msg.html', {})
    # return HttpResponseRedirect("/course/discipline/" + str(pk) + "/update")


@login_required
def ImportStudentsClassroom(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    classroom = get_object_or_404(Classroom, pk=pk)

    if request.method == 'POST':

        person_resource = StudentResource()
        dataset = Dataset()

        try:
            new_persons = request.FILES['myfile']
            f = new_persons.read().decode('utf-8')
            pass
        except:
            messages.error(request, _('ImportStudentsClassroom: choose a CSV following the model'))
            return render(request, 'exam/exam_errors.html', {})

        ''' #################### ''
        # DELETE students with the same RA, but before correct classrooms
        for s1 in Student.objects.all():  # delete student equals
            try:
                i = int(s1.student_ID)
            except:
                s1.delete()
        for s1 in Student.objects.all():  # delete student equals
            studentDELETE = []
            for s2 in Student.objects.filter(student_ID=s1.student_ID).filter(student_name=s1.student_name):  # delete student equals
                if s1 != s2:
                    print('IGUAL: ' + s1.student_name)
                    myflag = True
                    for c in Classroom.objects.all():
                        for s3 in c.students.filter(student_ID=s1.student_ID):
                            print('CLASS: ' + c.classroom_code)
                            if s1 != s3 and s2 == s3:
                                try:
                                    c.students.add(s1)
                                    c.students.remove(s2)
                                    studentDELETE.append(s2)
                                    myflag = False
                                except:
                                    pass
                    if myflag: # se estudante s2 nao está em nenhuma turma, tb abagar
                        studentDELETE.append(s2)
            for s2 in studentDELETE:
                try:
                    print('DEL:   '+s2.student_name)
                    s2.delete()
                except:
                    pass
        '' #################### '''

        for s in classroom.students.all():
            classroom.students.remove(s)

        messages.info(request, _('Classroom students') + ' >> ' + classroom.classroom_code, extra_tags='upper')
        contS = 0
        for row in f.split('\n'):
            r = row.split(',')

            if len(r) < 2:
                r = row.split(';')

            if len(r) == 3 or len(r) == 2:
                ra = r[0].lstrip().rstrip()

                nome = r[1].lstrip().rstrip()
                if len(nome) > 50:
                    nome = nome[:50]
                if len(r) == 3:
                    email = r[2].lstrip().rstrip()
                else:
                    email = ""

                try:
                    ra_int = int(ra)
                except:
                    messages.error(request, _('ImportStudentsClassroom: ID must be digits only: ') + ra + '; ' + nome)
                    return render(request, 'exam/exam_errors.html', {})

                allStudentsEqual = Student.objects.filter(student_ID=ra)

                if len(allStudentsEqual) > 1:
                    for s in allStudentsEqual:  # delete student equals
                        if nome == s.student_name:
                            s.delete()

                if not allStudentsEqual:
                    Student.objects.create(
                        student_ID=ra,
                        student_name=nome,
                        student_email=email,
                    )

                for s in Student.objects.filter(student_ID=ra):
                    classroom.students.add(s)
                    # return message
                    contS += 1
                    mystr4 = str(contS) + ';    ' + s.student_ID + '; ' + s.student_name + '; ' + s.student_email
                    messages.info(request, mystr4)

    mystr4 = '/course/classroom/' + str(pk)
    mystr5 = 'Link'
    messages.info(request, ' ')
    messages.info(request, _(
        'Back to Classroom Detail') + ' <a href="' + mystr4 + '" class="btn btn-outline-primary">' + mystr5 + '</a>',
                  extra_tags='safe')
    return render(request, 'exam/exam_msg.html', {})
    # return HttpResponseRedirect("/course/classroom/" + str(pk) + "/update")


@login_required
def ClassroomStudentDelete(request, pk1, pk2):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    classroom = get_object_or_404(Classroom, pk=pk1)
    student = get_object_or_404(Student, pk=pk2)

    if request.method == 'GET':
        for s in classroom.students.all():
            if s.id == student.id:
                classroom.students.remove(s)

    return render(request, 'classroom/classroom_detail.html', {'classroom': classroom})


# Create a new Student BUG
from student.forms import CreateStudentForm
from django.forms.models import inlineformset_factory
from django.forms import Textarea


@login_required
def ClassroomStudentCreate(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    classroom = get_object_or_404(Classroom, pk=pk)

    # question_inst = get_object_or_404(Question, pk=pk)
    StudentInlineFormSet = inlineformset_factory(
        Classroom, Student, fk_name='classroom', fields=('student_ID', 'student_name', 'student_email',),
        widgets={'student_ID': Textarea(attrs={'cols': 80, 'rows': 1}),
                 'student_name': Textarea(attrs={'cols': 40, 'rows': 1}),
                 'student_email': Textarea(attrs={'cols': 40, 'rows': 1}),
                 },
        extra=1)  # quantidade de estudantes na tela

    if request.method == 'POST':

        form = CreateStudentForm(request.POST)
        if form.is_valid():  # Check if the forms are valid:
            id = form.cleaned_data['student_ID']
            name = form.cleaned_data['student_name']
            email = form.cleaned_data['student_email']

        if Student.objects.filter(student_ID=id):
            messages.error(request, _('StudentCreate: There is ID: ') + id + '; ' + name + '; ' + email)
            return render(request, 'exam/exam_errors.html', {})
        else:
            s = Student.objects.create(
                student_ID=id,
                student_name=name,
                student_email=email,
            )
            classroom.students.add(s)
            messages.info(request, _('StudentCreate: Created Student ') + id + '; ' + name + '; ' + email)

    else:  # If this is a GET (or any other method) create the default form.
        formset = StudentInlineFormSet(instance=classroom)

        form = CreateStudentForm(initial={
            'students': classroom.students,
        })

    return render(request, 'exam/exam_msg.html', {})


class ClassroomUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Classroom
    template_name = 'classroom/classroom_update.html'
    # fields = '__all__'
    fields = [
        'discipline',
        'students',
        'classroom_profs',
        'classroom_code',
        'classroom_room',
        # 'classroom_days',
        'classroom_type',
    ]
    success_url = '/course/classroomsmy'

    def form_valid(self, form):
        if not self.request.user in form.instance.discipline.discipline_profs.all():
            messages.error(self.request, _('ClassroomUpdate: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})
        return super(ClassroomUpdate, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ClassroomUpdate, self).get_form_kwargs()
        return kwargs

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_queryset(self):
        return Classroom.objects.filter(discipline__discipline_profs=self.request.user)


class ClassroomDetailView(LoginRequiredMixin, generic.DetailView):
    model = Classroom
    template_name = 'classroom/classroom_detail.html'


class ClassroomCreate(LoginRequiredMixin, generic.CreateView):
    model = Classroom
    # fields = '__all__'
    fields = [
        'discipline',
        'classroom_code',
        'classroom_room',
        # 'classroom_days',
        'classroom_type',
    ]
    template_name = 'classroom/classroom_create.html'
    success_url = '/course/classroomsmy'

    def form_valid(self, form):
        if not self.request.user in form.instance.discipline.discipline_profs.all():
            messages.error(self.request, _('ClassroomCreate: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})

        return super(ClassroomCreate, self).form_valid(form)

    def get_queryset(self):
        return Classroom.objects.filter(discipline__discipline_profs=self.request.user)


class ClassroomDelete(LoginRequiredMixin, generic.DeleteView):
    model = Classroom
    template_name = 'classroom/classroom_confirm_delete.html'
    success_url = '/course/classroomsmy'

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            raise Http404(value)
            setattr(self, key, value)

    def form_valid(self, form):
        raise Http404("oi")
        if not self.request.user in form.instance.discipline.discipline_profs.all():
            messages.error(self.request, _('ClassroomDelete: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})
        return super(ClassroomDelete, self).form_valid(form)

    def get_queryset(self):
        return Classroom.objects.filter(discipline__discipline_profs=self.request.user)


class LoanedClassroomByUserListView(LoginRequiredMixin, generic.ListView):
    model = Classroom
    template_name = 'classroom/classroom_list_who_created_user.html'

    # paginate_by = 100

    def form_valid(self, form):
        if not self.request.user in form.instance.discipline.discipline_profs.all():
            messages.error(self.request,
                           _('LoanedClassroomByUserListView: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})

        return super(LoanedClassroomByUserListView, self).form_valid(form)

    def get_queryset(self):
        return Classroom.objects.filter(discipline__discipline_profs=self.request.user)


#########################################################################
class InstituteListView(generic.ListView):
    model = Institute
    fields = '__all__'
    # paginate_by = 100
    template_name = 'institute/institute_list.html'
    success_url = '/course/institutes'


class InstituteDetailView(generic.DetailView):
    model = Institute
    # fields = '__all__'
    fields = [
        'institute_name',
        'institute_code',
        'institute_logo',
        'institute_url',
        'institute_exams_generated',
        'institute_exams_corrected',
        'institute_questions_corrected',
    ]
    template_name = 'institute/institute_detail.html'


class InstituteUpdate(UpdateView):
    model = Institute
    template_name = 'institute/institute_update.html'
    # fields = '__all__'
    fields = [
        'institute_name',
        'institute_code',
        'institute_logo',
        'institute_url',
        'institute_exams_generated',
        'institute_exams_corrected',
        'institute_questions_corrected',
        # 'institute_date',
    ]
    success_url = '/course/institutes'


class InstituteCreate(CreateView):
    model = Institute
    # fields = '__all__'
    fields = [
        'institute_name',
        'institute_code',
        'institute_logo',
        'institute_url',
        'institute_exams_generated',
        'institute_exams_corrected',
        'institute_questions_corrected',
        # 'institute_date',
    ]
    template_name = 'institute/institute_create.html'
    success_url = '/course/institutes'


class InstituteDelete(DeleteView):
    model = Institute
    template_name = 'institute/institute_confirm_delete.html'
    success_url = '/course/institutes'


#########################################################################

class CourseListView(generic.ListView):
    model = Course
    fields = '__all__'
    # paginate_by = 100
    template_name = 'course/course_list.html'
    success_url = '/course/courses'


class CourseDetailView(generic.DetailView):
    model = Course
    fields = [
        'institutes',
        'course_name',
        'course_code',
    ]
    template_name = 'course/course_detail.html'


class CourseUpdate(UpdateView):
    model = Course
    fields = [
        'institutes',
        'course_name',
        'course_code',
    ]
    template_name = 'course/course_update.html'
    success_url = '/course/courses'


class CourseCreate(CreateView):
    model = Course
    fields = [
        'institutes',
        'course_name',
        'course_code',
    ]
    # fields = '__all__'
    template_name = 'course/course_create.html'
    success_url = '/course/courses'


class CourseDelete(DeleteView):
    model = Course
    template_name = 'course/course_confirm_delete.html'
    success_url = '/course/courses'


#########################################################################

class DisciplineListView(generic.ListView):
    model = Discipline
    fields = '__all__'
    # paginate_by = 100
    template_name = 'discipline/discipline_list.html'
    success_url = '/course/disciplines'


class DisciplineDetailView(generic.DetailView):
    model = Discipline
    fields = '__all__'
    template_name = 'discipline/discipline_detail.html'


class DisciplineUpdate(UpdateView):
    model = Discipline
    template_name = 'discipline/discipline_update.html'
    fields = '__all__'
    success_url = '/course/disciplines'


class DisciplineCreate(CreateView):
    model = Discipline
    fields = '__all__'
    template_name = 'discipline/discipline_create.html'
    success_url = '/course/disciplines'


class DisciplineDelete(DeleteView):
    model = Discipline
    template_name = 'discipline/discipline_confirm_delete.html'
    success_url = '/course/disciplines'
