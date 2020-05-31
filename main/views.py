from django.shortcuts import render
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView
from account.forms import UserCreateForm
from django.urls import reverse_lazy
from account.models import User
from course.models import Institute, Course, Classroom, Discipline
from topic.models import Topic, Question, Answer
from exam.models import Exam

# Create your views here.


class SignUp(generic.CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

######################################
from django.contrib.sessions.models import Session
from django.utils import timezone


def contributors(request):
    return render(request, 'contributors.html', {})

def users(request):
    return render(request, 'users.html', {})


def readme(request):
    return render(request, 'readme.html', {})


def license(request):
    return render(request, 'license.html', {})


def index(request):
    users = User.objects.order_by('-last_login')[:10]  # all list 10 last users-login

    # all users logged now
    # Session.objects.all().delete()
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))
    users_now = User.objects.filter(id__in=uid_list)

    num_institutes = Institute.objects.all().count()
    num_courses = Course.objects.all().count()
    num_disciplines = Discipline.objects.all().count()
    num_classrooms = Classroom.objects.all().count()

    num_exams = Exam.objects.all().count()

    num_users = User.objects.all().count()

    num_questions = Question.objects.all().count()
    num_topics = Topic.objects.all().count()
    num_QM = Question.objects.filter(question_type='QM').count()
    num_QT = Question.objects.filter(question_type='QT').count()
    num_Parametric = Question.objects.filter(question_parametric='yes').count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(request, 'index.html',
                  context={'num_institutes': num_institutes,
                           'num_courses': num_courses,
                           'num_disciplines': num_disciplines,
                           'num_classrooms': num_classrooms,
                           'num_questions': num_questions,
                           'num_topics': num_topics,
                           'num_QM': num_QM,
                           'num_QT': num_QT,
                           'num_Parametric': num_Parametric,
                           'num_exams': num_exams,
                           'num_users': num_users,
                           'users_now': users_now,
                           'users': users,
                           'num_visits': num_visits})

