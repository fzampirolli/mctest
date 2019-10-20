# Create your views here.
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from course.models import Classroom
from student.models import Student


# from .models import Institute, Course, Discipline, Classroom
# from .resources import StudentResource

class StudentListView(generic.ListView):
    model = Student
    fields = '__all__'
    # paginate_by = 100
    template_name = 'student/student_list.html'
    success_url = '/student/students'


class StudentDetailView(generic.DetailView):
    model = Student
    fields = '__all__'
    template_name = 'student/student_detail.html'


class StudentUpdate(UpdateView):
    model = Student
    template_name = 'student/student_update.html'
    fields = '__all__'
    success_url = '/student/{student_id}'

    def get_success_url(self):
        return reverse('student:student-detail', kwargs={
            'pk': self.object.pk,
        })

    def form_valid(self, form):
        id = form.cleaned_data['student_ID']
        name = form.cleaned_data['student_name']
        email = form.cleaned_data['student_email']
        pk = self.object.pk
        studentsEqual = []
        count = 0
        for s in Student.objects.filter(student_ID=id):
            if pk != s.pk:
                if name != s.student_name or email != s.student_email:
                    studentsEqual.append(s)
                    count += 1

        if count:
            messages.error(self.request,
                           _("StudentUpdate: There is already student(s) with ID ") + id + ":" + str(studentsEqual))
            return render(self.request, 'exam/exam_errors.html', {})

        return super(StudentUpdate, self).form_valid(form)


class StudentCreate(CreateView):
    model = Student
    template_name = 'student/student_create.html'
    fields = '__all__'

    # form_class = CreateStudentForm
    # success_url = '/classroom/{classroom_id}'

    def form_valid(self, form):
        id = form.cleaned_data['student_ID']
        name = form.cleaned_data['student_name']
        email = form.cleaned_data['student_email']
        pk = self.object.pk
        classroom = get_object_or_404(Classroom, pk=pk)
        studentsEqual = []
        count = 0
        for s in Student.objects.filter(student_ID=id):
            if id != s.pk:
                if name != s.student_name or email != s.student_email:
                    studentsEqual.append(s)
                    count += 1
                    if not Student.objects.filter(student_ID=id):
                        s_add = Student.objects.create(
                            student_ID=id,
                            student_name=name,
                            student_email=email,
                        )

        if count:
            messages.error(self.request,
                           _("StudentCreate: There is already student(s) with ID ") + id + ":" + str(studentsEqual))
            return render(self.request, 'exam/exam_errors.html', {})

        return super(StudentCreate, self).form_valid(form)

    def __init__(self, *args, **kwargs):
        pk = self.kwargs['pk']
        classroom = get_object_or_404(Classroom, pk=pk)


class StudentDelete(DeleteView):
    model = Student
    template_name = 'student/student_confirm_delete.html'
    success_url = '/student/students'

    def get_queryset(self):
        pk = self.kwargs['pk']
        classrooms = Classroom.objects.filter(students=pk)
        studentClassrooms = []
        for c in classrooms:
            studentClassrooms.append(c)

        return Student.objects.filter(pk=pk)
