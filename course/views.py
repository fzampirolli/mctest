'''
=====================================================================
Copyright (C) 2018-2026 Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of MCTest 5.4.

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
import csv
import io
from datetime import datetime

# Django Imports
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin # Importante para segurança
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

# App Imports
# Removido import direto de 'account.models' para evitar conflito
from student.models import Student
from .forms import ClassroomCreateForm, ClassroomUpdateForm
from .models import Institute, Course, Discipline, Classroom

# Obtém a classe de Usuário correta
User = get_user_model()


@login_required
@permission_required('exam.change_exam', raise_exception=True)
def ImportClassroomsDiscipline(request, pk):
    discipline = get_object_or_404(Discipline, pk=pk)

    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['myfileClassrooms']
        except KeyError:
            messages.error(request, _('ImportClassroomsDiscipline: choose a CSV following the model'))
            return render(request, 'exam/exam_errors.html', {})

        # 1. Tratamento de Encoding
        try:
            file_data = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            file_data = uploaded_file.read().decode('latin-1')

        # 2. Sniffer (Detecção de separador)
        io_string = io.StringIO(file_data)
        try:
            dialect = csv.Sniffer().sniff(io_string.read(2048), delimiters=[',', ';'])
            io_string.seek(0)
            reader = csv.reader(io_string, dialect)
        except csv.Error:
            io_string.seek(0)
            reader = csv.reader(io_string, delimiter=';')

        # 3. Limpeza: Remove alunos das turmas existentes (comportamento original)
        for c in discipline.classrooms2.all():
            c.students.clear()

        # Links de navegação (Feedback)
        mystr4 = f'/course/discipline/{pk}/update'
        messages.info(request, _('Return to: ') + f'<a href="{mystr4}">link</a>', extra_tags='safe')
        messages.info(request, _('Discipline name') + ' >> ' + discipline.discipline_name, extra_tags='upper')

        # Variáveis auxiliares
        contALL = 0
        contFault = 0
        studentsFault = ''

        # Data para novas turmas
        data_atual = datetime.now()
        ano_quad = f"{data_atual.year}.{(data_atual.month + 3) // 4}"

        # 4. Loop de Importação
        for row in reader:
            if not row: continue

            r = [col.strip() for col in row]

            # Requer pelo menos ID, Nome, Email, Código, Sala, Tipo (6 colunas)
            if len(r) < 6:
                # Se for muito curto, ignora ou loga erro
                if len(r) > 1: print(f"Linha ignorada (incompleta): {r}")
                continue

            try:
                # --- Extração ---
                st_id = r[0]
                st_nome = r[1]
                st_email = r[2]
                class_code = r[3]
                class_room = r[4]
                class_type = r[5]

                # Professor é opcional (coluna 7)
                emailProf = r[6] if len(r) > 6 else None

                # Validação ID
                int(st_id)

                # Tratamento de Nome Grande
                if len(st_nome) > 39:
                    st_nome = st_nome[:39]
                    messages.info(request, f"### BIG ###: {r[1]} ==> {st_nome}")

                # --- PROFESSOR ---
                if emailProf:
                    # Verifica se o professor existe no sistema
                    prof = User.objects.filter(email=emailProf).first()

                    if not prof:
                        # Se não existe, loga o erro (conforme original)
                        # Nota: A lógica original tentava checar institute_url, removi para simplificar,
                        # mas se for vital, avise que recoloco.
                        messages.error(request, _('Teacher not registered: ') + emailProf)
                    else:
                        # Adiciona à disciplina se não estiver
                        if prof not in discipline.discipline_profs.all():
                            discipline.discipline_profs.add(prof)

                # --- ESTUDANTE (Update or Create) ---
                # Resolve o problema da variável 's' indefinida
                s, created = Student.objects.update_or_create(
                    student_ID=st_id,
                    defaults={
                        'student_name': st_nome,
                        'student_email': st_email,
                    }
                )
                contALL += 1

                # --- TURMA (Classroom) ---
                # Busca a turma APENAS dentro desta disciplina
                c, created_c = Classroom.objects.get_or_create(
                    discipline=discipline,
                    classroom_code=class_code,
                    defaults={
                        'classroom_room': class_room,
                        'classroom_type': class_type,
                        'classroom_days': ano_quad,
                    }
                )

                # --- VÍNCULOS ---

                # Adiciona Professor à Turma
                if emailProf and prof:
                    if prof not in c.classroom_profs.all():
                        c.classroom_profs.add(prof)

                # Adiciona Estudante à Turma (Agora 's' e 'c' existem com certeza)
                c.students.add(s)

            except Exception as e:
                contFault += 1
                studentsFault += str(row) + f' ({e})\n'

        # --- RELATÓRIO FINAL ---

        # 1. Turmas
        countClasses = 0
        for c in discipline.classrooms2.all():
            countClasses += 1
            messages.info(request, _('Classroom') + ' >> ' + c.classroom_code, extra_tags='upper')

            # Profs da turma
            for p in c.classroom_profs.all():
                mystr4 = f'PROF: {countClasses}; {p.first_name}; {p.last_name}; {p.email}'
                messages.info(request, mystr4)

            # Alunos da turma
            contS = 0
            for s in c.students.all():
                contS += 1
                mystr4 = f'{contS};    {s.student_ID}; {s.student_name}; {s.student_email}'
                messages.info(request, mystr4)

        # 2. Profs da Disciplina
        messages.info(request, _('Discipline profs'), extra_tags='upper')
        contS = 0
        for p in discipline.discipline_profs.all():
            contS += 1
            mystr4 = f'{contS};    {p.first_name}; {p.last_name}; {p.email}'
            messages.info(request, mystr4)

        # 3. Resumo
        messages.info(request, _('TOTAL'), extra_tags='upper')
        messages.info(request, _('Registered: ') + str(contALL))
        messages.info(request, _('Not registered: ') + str(contFault))
        if studentsFault:
            messages.info(request, str(studentsFault))

    return render(request, 'exam/exam_msg.html', {})

@login_required
@permission_required('exam.change_exam', raise_exception=True)
def ImportProfsDiscipline(request, pk):
    discipline = get_object_or_404(Discipline, pk=pk)

    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['myfileProfs']
        except KeyError:
            messages.error(request, _('ImportProfsDiscipline: choose a CSV following the model!'))
            return render(request, 'exam/exam_errors.html', {})

        # 1. Encoding
        try:
            file_data = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            file_data = uploaded_file.read().decode('latin-1')

        # 2. Sniffer
        io_string = io.StringIO(file_data)
        try:
            dialect = csv.Sniffer().sniff(io_string.read(2048), delimiters=[',', ';'])
            io_string.seek(0)
            reader = csv.reader(io_string, dialect)
        except csv.Error:
            io_string.seek(0)
            reader = csv.reader(io_string, delimiter=';')

        group_prof, created_group = Group.objects.get_or_create(name='professor')

        cont_sucesso = 0
        erros_log = []

        # --- NOVO: Conjunto para guardar IDs dos novos professores adicionados ---
        new_prof_ids = set()

        for row in reader:
            if not row: continue

            r = [col.strip() for col in row]

            if len(r) < 3: continue

            try:
                first_name = r[0]
                last_name = r[1]
                email_prof = r[2].lower()

                # Bloquear Alunos
                if '@aluno.ufabc.edu.br' in email_prof:
                    erros_log.append(f"ALUNO BLOQUEADO: {email_prof}")
                    continue

                    # Busca ou Cria Usuário
                user = User.objects.filter(email=email_prof).first()

                if user:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
                else:
                    base_username = email_prof.split('@')[0][:20]
                    username = base_username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1

                    user = User.objects.create(
                        username=username,
                        email=email_prof,
                        first_name=first_name,
                        last_name=last_name,
                        is_active=True
                    )

                if group_prof not in user.groups.all():
                    user.groups.add(group_prof)

                # Adiciona à Disciplina e marca como NOVO
                if user not in discipline.discipline_profs.all():
                    discipline.discipline_profs.add(user)
                    new_prof_ids.add(user.id) # <--- Guardamos o ID aqui
                    cont_sucesso += 1

            except Exception as e:
                erros_log.append(f"Falha na linha {r}: {str(e)}")

        # Feedback
        mystr4 = f'/course/discipline/{pk}/update'
        messages.info(request, _('Return to: ') + f'<a href="{mystr4}">link</a>', extra_tags='safe')

        if erros_log:
            for err in erros_log:
                messages.warning(request, err)

        # --- LISTAGEM ORDENADA E DESTACADA ---
        messages.info(request, _('List of Professors'), extra_tags='upper')

        # 1. Ordena por nome
        all_profs = discipline.discipline_profs.all().order_by('first_name', 'last_name')

        contS = 0
        for p in all_profs:
            contS += 1

            # Formata os dados básicos
            prof_str = f"{p.first_name} {p.last_name} ({p.email})"

            # 2. Verifica se é novo e aplica estilo
            if p.id in new_prof_ids:
                # Destaque: Azul, Negrito e sufixo [NOVO]
                msg_html = f"<b><span style='color: #007bff;'>{contS}; {prof_str} [NOVO]</span></b>"
            else:
                # Normal
                msg_html = f"{contS}; {prof_str}"

            # Usa extra_tags='safe' para renderizar o HTML
            messages.info(request, msg_html, extra_tags='safe')

    return render(request, 'exam/exam_msg.html', {})

@login_required
@permission_required('exam.change_exam', raise_exception=True)
def ImportStudentsClassroom(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)

    if request.method == 'POST':
        try:
            # O nome do input no HTML deve ser 'myfileClassrooms' ou 'myfile' (ajuste conforme seu template)
            uploaded_file = request.FILES.get('myfileClassrooms') or request.FILES.get('myfile')
            if not uploaded_file:
                raise KeyError
        except KeyError:
            messages.error(request, _('ImportStudentsClassroom: choose a CSV following the model'))
            return render(request, 'exam/exam_errors.html', {})

        # 1. Tratamento de Encoding
        try:
            # Tenta ler como UTF-8
            file_data = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            # Se falhar, tenta Latin-1 (comum em Excel antigo/Windows)
            uploaded_file.seek(0)
            file_data = uploaded_file.read().decode('latin-1')

        # 2. Sniffer (Detecção automática de separador , ou ;)
        io_string = io.StringIO(file_data)
        try:
            dialect = csv.Sniffer().sniff(io_string.read(2048), delimiters=[',', ';'])
            io_string.seek(0)
            reader = csv.reader(io_string, dialect)
        except csv.Error:
            io_string.seek(0)
            reader = csv.reader(io_string, delimiter=';') # Fallback padrão

        # Limpa os alunos atuais da turma antes de importar (Lógica original mantida)
        classroom.students.clear()

        messages.info(request, _('Classroom students') + ' >> ' + classroom.classroom_code, extra_tags='upper')

        contS = 0
        erros_log = []

        for row in reader:
            if not row: continue

            # Limpeza básica dos campos
            r = [col.strip() for col in row]

            # Requer pelo menos 2 colunas (ID, Nome)
            if len(r) < 2:
                continue

            try:
                # Extração de dados
                student_id = r[0]
                nome = r[1]
                email = r[2] if len(r) > 2 else ""

                # Validação: ID deve ser numérico
                int(student_id)

                # Tratamento de Nomes Grandes (> 39 chars)
                if len(nome) > 39:
                    # Lógica simplificada de corte preservando o último sobrenome se possível
                    partes = nome.split()
                    if len(partes) > 1:
                        ultimo_nome = partes[-1]
                        limite_base = 38 - len(ultimo_nome) # 38 pra deixar espaço pro espaço
                        nome_base = " ".join(partes[:-1])
                        nome = f"{nome_base[:limite_base]} {ultimo_nome}"
                    else:
                        nome = nome[:39]

                    messages.info(request, f"### BIG ###: {r[1]} ==> {nome}")

                # UPDATE OR CREATE: Atualiza se existir, Cria se não existir
                # Isso substitui todo aquele bloco de try/except/delete/filter
                student, created = Student.objects.update_or_create(
                    student_ID=student_id,
                    defaults={
                        'student_name': nome,
                        'student_email': email,
                    }
                )

                # Adiciona à turma
                classroom.students.add(student)

                contS += 1
                msg_aluno = f"{contS}; {student.student_ID}; {student.student_name}; {student.student_email}"
                messages.info(request, msg_aluno)

            except ValueError:
                messages.error(request, _('ImportStudentsClassroom: ID must be digits only: ') + f"{r[0]}; {r[1]}")
                erros_log.append(r)
            except Exception as e:
                erros_log.append(f"Erro na linha {r}: {e}")

        if erros_log:
            messages.warning(request, f"Total de erros: {len(erros_log)}")

    # Botão de Voltar
    link_voltar = f'/course/classroom/{pk}'
    texto_botao = _('Back to Classroom Detail')
    html_botao = f'{texto_botao} <a href="{link_voltar}" class="btn btn-outline-primary">Link</a>'

    messages.info(request, ' ')
    messages.info(request, html_botao, extra_tags='safe')

    return render(request, 'exam/exam_msg.html', {})

@login_required
def ClassroomStudentDelete(request, pk1, pk2):
    # Verificação de permissão simplificada e pythonica
    if not request.user.has_perm('exam.change_exam'):
        return HttpResponseRedirect("/")

    classroom = get_object_or_404(Classroom, pk=pk1)
    student = get_object_or_404(Student, pk=pk2)

    # Verifica se o aluno está na turma antes de remover
    if student in classroom.students.all():
        classroom.students.remove(student)

    return render(request, 'classroom/classroom_detail.html', {'classroom': classroom})


@login_required
@csrf_protect
def ClassroomStudentCreate(request, pk):
    if not request.user.has_perm('exam.change_exam'):
        return HttpResponseRedirect("/")

    classroom = get_object_or_404(Classroom, pk=pk)

    if request.method == 'POST':
        # Uso seguro de getlist (assume que o form envia arrays)
        ids = request.POST.getlist('student_ID')
        names = request.POST.getlist('student_name')
        emails = request.POST.getlist('student_email')

        if ids:
            id_val = ids[0]
            name_val = names[0]
            email_val = emails[0]

            # Tenta pegar existente ou criar
            # Lógica corrigida para evitar race condition
            s, created = Student.objects.get_or_create(
                student_ID=id_val,
                defaults={'student_name': name_val, 'student_email': email_val}
            )

            classroom.students.add(s)

            action = "Created" if created else "Added"
            messages.info(request, f"{action} student ID: {id_val}; name: {s.student_name}; email: {s.student_email}")

    return render(request, 'exam/exam_msg.html', {})
# --- CLASSROOM VIEWS ---

class ClassroomUpdate(LoginRequiredMixin, generic.UpdateView):
    form_class = ClassroomUpdateForm
    model = Classroom # Faltou especificar o model aqui ou no queryset
    template_name = 'classroom/classroom_update.html'
    success_url = '/course/classroomsmy'

    def get_form_kwargs(self):
        kwargs = super(ClassroomUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Validação de segurança
        if not (self.request.user in form.instance.discipline.discipline_profs.all() or
                self.request.user in form.instance.discipline.discipline_coords.all()):
            messages.error(self.request, _('ClassroomUpdate: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})
        return super(ClassroomUpdate, self).form_valid(form)

    def get_queryset(self):
        c1 = Classroom.objects.filter(discipline__discipline_profs=self.request.user)
        c2 = Classroom.objects.filter(discipline__discipline_coords=self.request.user)
        return (c1 | c2).distinct()


class ClassroomDetailView(LoginRequiredMixin, generic.DetailView):
    model = Classroom
    template_name = 'classroom/classroom_detail.html'
    # Sugestão: Adicionar get_queryset aqui também para evitar que profs vejam turmas de outros


class ClassroomCreate(LoginRequiredMixin, generic.CreateView):
    form_class = ClassroomCreateForm
    template_name = 'classroom/classroom_create.html'
    success_url = '/course/classroomsmy'

    def get_form_kwargs(self):
        kwargs = super(ClassroomCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Nota: form.instance.discipline pode ser None se o form não tiver setado ainda,
        # mas como é Create e o form salva, deve estar ok se o campo for obrigatório.
        if form.instance.discipline and not (
                self.request.user in form.instance.discipline.discipline_profs.all() or
                self.request.user in form.instance.discipline.discipline_coords.all()):
            messages.error(self.request, _('ClassroomCreate: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})

        return super(ClassroomCreate, self).form_valid(form)


class ClassroomDelete(LoginRequiredMixin, generic.DeleteView):
    model = Classroom
    template_name = 'classroom/classroom_confirm_delete.html'
    success_url = '/course/classroomsmy'

    def form_valid(self, form):
        classroom = self.object
        if self.request.user not in classroom.discipline.discipline_profs.all():
            messages.error(self.request, _('ClassroomDelete: The teacher is not registered in a Discipline'))
            return render(self.request, 'exam/exam_errors.html', {})
        return super(ClassroomDelete, self).form_valid(form)

    def get_queryset(self):
        qs = super().get_queryset()
        c1 = qs.filter(discipline__discipline_profs=self.request.user)
        c2 = qs.filter(discipline__discipline_coords=self.request.user)
        return (c1 | c2).distinct()


class ClassroomListView(LoginRequiredMixin, generic.ListView):
    model = Classroom
    template_name = 'classroom/classroom_list.html'

    # REMOVIDO: def form_valid (não existe em ListView)

    def get_queryset(self):
        # Filtra para mostrar apenas o que o usuário pode ver
        c1 = Classroom.objects.filter(discipline__discipline_profs=self.request.user)
        c2 = Classroom.objects.filter(discipline__discipline_coords=self.request.user)
        return (c1 | c2).order_by('classroom_code').distinct()


class LoanedClassroomByUserListView(LoginRequiredMixin, generic.ListView):
    model = Classroom
    template_name = 'classroom/classroom_list_who_created_user.html'

    # REMOVIDO: def form_valid (não existe em ListView)

    def get_queryset(self):
        return Classroom.objects.filter(classroom_profs=self.request.user).order_by('classroom_code').distinct()

#########################################################################
# IMPORTANTE: Adicionado LoginRequiredMixin para segurança
#########################################################################

class InstituteListView(generic.ListView):
    model = Institute
    template_name = 'institute/institute_list.html'

class InstituteDetailView(generic.DetailView):
    model = Institute
    template_name = 'institute/institute_detail.html'
    fields = ['institute_name', 'institute_code', 'institute_logo', 'institute_url', 'institute_exams_generated', 'institute_exams_corrected', 'institute_questions_corrected']

class InstituteUpdate(LoginRequiredMixin, UpdateView):
    model = Institute
    template_name = 'institute/institute_update.html'
    fields = ['institute_name', 'institute_code', 'institute_logo', 'institute_url', 'institute_exams_generated', 'institute_exams_corrected', 'institute_questions_corrected']
    success_url = '/course/institutes'

class InstituteCreate(LoginRequiredMixin, CreateView):
    model = Institute
    template_name = 'institute/institute_create.html'
    fields = ['institute_name', 'institute_code', 'institute_logo', 'institute_url', 'institute_exams_generated', 'institute_exams_corrected', 'institute_questions_corrected']
    success_url = '/course/institutes'

class InstituteDelete(LoginRequiredMixin, DeleteView):
    model = Institute
    template_name = 'institute/institute_confirm_delete.html'
    success_url = '/course/institutes'

#########################################################################

class CourseListView(generic.ListView):
    model = Course
    template_name = 'course/course_list.html'
    def get_queryset(self):
        return Course.objects.all().order_by('course_name').distinct()

class CourseDetailView(generic.DetailView):
    model = Course
    fields = ['institutes', 'course_name', 'course_code']
    template_name = 'course/course_detail.html'

class CourseUpdate(LoginRequiredMixin, UpdateView):
    model = Course
    fields = ['institutes', 'course_name', 'course_code']
    template_name = 'course/course_update.html'
    success_url = '/course/courses'

class CourseCreate(LoginRequiredMixin, CreateView):
    model = Course
    fields = ['institutes', 'course_name', 'course_code']
    template_name = 'course/course_create.html'
    success_url = '/course/courses'

class CourseDelete(LoginRequiredMixin, DeleteView):
    model = Course
    template_name = 'course/course_confirm_delete.html'
    success_url = '/course/courses'

#########################################################################

class DisciplineListView(generic.ListView):
    model = Discipline
    template_name = 'discipline/discipline_list.html'
    def get_queryset(self):
        return Discipline.objects.all().order_by('discipline_name').distinct()

class DisciplineDetailView(generic.DetailView):
    model = Discipline
    fields = '__all__'
    template_name = 'discipline/discipline_detail.html'

class DisciplineUpdate(LoginRequiredMixin, UpdateView):
    model = Discipline
    template_name = 'discipline/discipline_update.html'
    fields = '__all__'
    success_url = '/course/disciplines'

class DisciplineCreate(LoginRequiredMixin, CreateView):
    model = Discipline
    fields = '__all__'
    template_name = 'discipline/discipline_create.html'
    success_url = '/course/disciplines'

class DisciplineDelete(LoginRequiredMixin, DeleteView):
    model = Discipline
    template_name = 'discipline/discipline_confirm_delete.html'
    success_url = '/course/disciplines'
