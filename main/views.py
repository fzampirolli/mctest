import os
from datetime import datetime
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.cache import cache # Importante para o status Online
from django.conf import settings

# Imports dos seus modelos
from account.forms import UserCreateForm
from account.models import User
from course.models import Institute, Course, Classroom, Discipline
from topic.models import Topic, Question, Answer
from exam.models import Exam
from student.models import Student

# --- LÓGICA DE LOG EM ARQUIVO (HISTÓRICO SEM BANCO DE DADOS) ---
# Define o arquivo na raiz do projeto
LOG_FILE = os.path.join(settings.BASE_DIR, 'login_history.log')

@receiver(user_logged_in)
def log_user_login_to_file(sender, request, user, **kwargs):
    """Grava o login no arquivo de texto quando o usuário entra."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, 'a') as f:
            f.write(f"{user.id}|{timestamp}\n")
    except Exception as e:
        print(f"Erro ao gravar log: {e}")

# --- VIEWS EXISTENTES ---

def custom_logout(request):
    logout(request)
    return redirect('/')

class SignUp(generic.CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def According(request):
    return render(request, 'According.html', {})

def contributors(request):
    return render(request, 'contributors.html', {})

def users(request):
    return render(request, 'users.html', {})

def readme(request):
    return render(request, 'readme.html', {})

def compare(request):
    return render(request, 'compareTexts.html', {})

def license(request):
    return render(request, 'license.html', {})


# --- VIEW PRINCIPAL CORRIGIDA ---

def index(request):
    # 1. Recupera todos os usuários para iterar (ou apenas os recentes para otimizar)
    # Aqui pegamos todos para garantir que encontraremos quem está online, 
    # mas ordenamos para a lista de "Recentes"
    all_users = User.objects.all().order_by('-last_login')

    # ---------------------------------------------------------
    # PARTE A: Ler o Histórico do Arquivo de Texto
    # ---------------------------------------------------------
    history_map = {}
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                # Lê de trás para frente para pegar os mais novos
                for line in reversed(lines):
                    if not line.strip(): continue
                    try:
                        uid_str, dt_str = line.strip().split('|')
                        uid = int(uid_str)

                        if uid not in history_map:
                            history_map[uid] = []

                        # Guarda apenas os 2 últimos registros
                        if len(history_map[uid]) < 2:
                            dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            history_map[uid].append({'timestamp': dt_obj})
                    except:
                        continue
        except Exception as e:
            print(f"Erro leitura log: {e}")

    # ---------------------------------------------------------
    # PARTE B: Detectar quem está realmente ONLINE (Via Cache)
    # ---------------------------------------------------------
    users_now = []

    # Itera sobre os usuários para verificar o cache
    for u in all_users:
        # Verifica se existe a chave criada pelo Middleware
        last_seen = cache.get(f'last_seen_{u.id}')

        # Injeta o histórico em TODOS os objetos de usuário (para a tabela)
        u.history = history_map.get(u.id, [])

        if last_seen:
            users_now.append(u)

    # Lista para a tabela "Offline" (top 10 recentes)
    users_recent = all_users[:10]

    # ---------------------------------------------------------
    # PARTE C: Contadores do Dashboard
    # ---------------------------------------------------------
    num_institutes = Institute.objects.all().count()
    num_courses = Course.objects.all().count()
    num_disciplines = Discipline.objects.all().count()
    num_classrooms = Classroom.objects.all().count()
    num_exams = Exam.objects.all().count()
    num_users = User.objects.all().count()
    num_students = Student.objects.all().count()

    num_questions = Question.objects.all().count()
    num_topics = Topic.objects.all().count()
    num_QM = Question.objects.filter(question_type='QM').count()
    num_QT = Question.objects.filter(question_type='QT').count()
    num_Parametric = Question.objects.filter(question_parametric='yes').count()

    public_institutes = Institute.objects.all().order_by('institute_name')
    public_courses = Course.objects.all().order_by('course_name')
    public_disciplines = Discipline.objects.all().order_by('discipline_name')

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
                           'num_students': num_students,
                           'users_now': users_now,   # Lista corrigida via Cache
                           'users': users_recent,    # Lista geral com histórico injetado
                           'num_visits': num_visits,
                           # Passamos as listas para o template sempre
                           'public_institutes': public_institutes,
                           'public_courses': public_courses,
                           'public_disciplines': public_disciplines})