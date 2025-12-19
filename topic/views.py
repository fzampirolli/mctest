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
###################################################################
import json
import os, re
import random

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.forms import Textarea
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView
from django.views.static import serve
# ai_assist: comentado uso em question_update.html - incluir na versão MCTest 5.4
from django.views.decorators.csrf import csrf_exempt
from language_tool_python import LanguageTool
import autopep8
from django.contrib import messages
import datetime


###################################################################
from exam.UtilsLatex import Utils
from .forms import UpdateQuestionForm, QuestionCreateForm, TopicCreateForm, TopicUpdateForm
from django.utils.html import format_html

from topic.utils_pdf import PDFGenerator

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, HttpResponseRedirect
# Certifique-se de importar seus models e utils corretamente
from .models import Question, Answer, Topic, Discipline
from topic.UtilsMCTest4 import UtilsMC

User = get_user_model()

from copy import copy

from course.models import Discipline  # Certifique-se de importar Discipline
from django.db.models import Count, Q

@login_required
@csrf_exempt
def see_question_PDF(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if 'exam.change_exam' not in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    question = get_object_or_404(Question, pk=pk)
    context = {"questions": question}

    if request.POST:
        Utils.validateProfByQuestion(question, request.user)

        # --- CONSTRUÇÃO DO CONTEÚDO LATEX ---
        q = question
        latex_content = ""

        # Cabeçalho e Metadados
        latex_content += Utils.getBegin()
        latex_content += "\\noindent\\Huge{MCTest}\\normalsize\\vspace{5mm}\\\\\n"
        latex_content += "\\noindent\\textbf{Topic:} %s\\\\\n" % q.topic.topic_text
        latex_content += "\\noindent\\textbf{Group:} %s\\\\\n" % q.question_group
        latex_content += "\\noindent\\textbf{Short Description:} %s\\\\\n" % q.question_short_description
        latex_content += "\\noindent\\textbf{Type:} %s\\\\\n" % q.question_type
        latex_content += "\\noindent\\textbf{Difficulty:} %s\\\\\n" % q.question_difficulty
        latex_content += "\\noindent\\textbf{Bloom taxonomy:} %s\\\\\n" % q.question_bloom_taxonomy
        latex_content += "\\noindent\\textbf{Last update:} %s\\\\\n" % q.question_last_update
        latex_content += "\\noindent\\textbf{Who created:} %s\\\\\n" % q.question_who_created
        latex_content += "\\noindent\\textbf{Parametric:} %s\\\\\n" % q.question_parametric.upper()

        # Integração VPL
        st = q.question_text
        a, b = st.find('begin{comment}'), st.find('end{comment}')
        if a < b and a != -1:
            latex_content += "\\noindent\\textbf{Integration:} %s\\\\\n" % 'Moodle+VPL'

        # ID da Questão
        ss1 = "\n\\hspace{-15mm}{\\small {\\color{green}\\#%s}} \\hspace{-1mm}"
        ss = ss1 % str(q.id).zfill(4)
        latex_content += "%s %s." % (ss, 1)

        # Lógica Paramétrica
        quest = ""
        ans = []
        feedback_ans = []

        if q.question_parametric == 'no':
            quest = q.question_text + '\n'
            if q.question_type == "QM":
                # Garante lista
                ans = [a.answer_text + '\n' for a in q.answers()]
        else:
            # Paramétrica
            try:
                answers_input = list(q.answers()) if q.question_type == "QM" else []
                [quest, ans, feedback_ans] = UtilsMC.questionParametric(q.question_text, answers_input, [])

                if quest == "":
                    messages.error(request, _('UtilsMC.questionParametric: forbidden words found.'))
                    return render(request, 'exam/exam_errors.html', {})
            except Exception as e:
                messages.error(request, f"Error generating parametric question: {e}")
                return render(request, 'exam/exam_errors.html', {})

        # Adiciona enunciado
        if isinstance(quest, list):
            quest = ''.join(quest)
        latex_content += r' %s' % quest

        # Adiciona Alternativas (Múltipla Escolha)
        latex_content += "\n\n\\vspace{2mm}\\begin{oneparchoices}\\hspace{-3mm}\n"

        if ans:
            import random
            # Copia para não alterar a lista original caso seja reutilizada
            ans_copy = list(ans)
            random.shuffle(ans_copy)

            for idx, a in enumerate(ans_copy):
                # Lógica original assume que ans[0] é a correta antes do shuffle
                # Se ans vier do BD, a correta é a que tem sort=0 ou similar, mas aqui estamos seguindo a lógica
                # de que a lista 'ans' gerada pelo UtilsMC coloca a certa no index 0.
                is_correct = (a == ans[0])

                if is_correct:
                    latex_content += "\\choice \\hspace{-2.0mm}{\\tiny{\\color{blue}\#%s}}%s" % (idx, a)
                else:
                    latex_content += "\\choice \\hspace{-2.0mm}{\\tiny{\\color{red}*%s}}%s" % (idx, a)

                try:
                    # Tenta recuperar feedback
                    original_idx = ans.index(a)
                    if feedback_ans and len(feedback_ans) > original_idx:
                        fb = feedback_ans[original_idx]
                        if fb and fb != '\n':
                            latex_content += '[' + fb + ']'
                except:
                    pass

        latex_content += "\\end{oneparchoices}\\vspace{0mm}\n"
        latex_content += "\\end{document}"

        # --- GERAÇÃO DO PDF (USANDO CLASSE SEGURA) ---
        generator = PDFGenerator()

        final_path = generator.generate(
            latex_content=latex_content,
            filename_base=request.user.username,
            destination_folder_name='pdfQuestion'
        )

        if final_path and os.path.exists(final_path):
            return serve(request, os.path.basename(final_path), os.path.dirname(final_path))
        else:
            messages.error(request, "Error generating PDF file.")
            return render(request, 'exam/exam_errors.html', {})

    return render(request, 'template_da_questao.html', context)



@csrf_exempt
def ai_assist(request):
    if request.method == 'POST':
        question_text = request.POST.get('question_text', '')
        language_choice = request.POST.get('language_choice', 'pt-BR')  # Valor padrão ou qualquer outra lógica que você preferir

        # Identificar e salvar partes do texto entre [[code: e ]]
        blocks = []
        blocks_text = []
        contador = 0
        start = question_text.find('[[code:')
        while start != -1:
            end = question_text.find(']]', start)
            if end != -1:
                block = question_text[start:end + 2]
                blocks.append(block)
                text = "X" + str(contador).zfill(3) + "X"
                blocks_text.append(text)
                question_text = question_text[:start] + text + question_text[end + 2:]
                start = question_text.find('[[code:', end - 7)
                contador += 1
            else:
                break

        # Identificar e salvar partes do texto entre [[def: e ]]
        start = question_text.find('[[def:')
        while start != -1:
            end = question_text.find(']]', start)
            if end != -1:
                code_python = question_text[start:end + 2]

                # Remover a primeira e a última linha do código
                code_lines = code_python.split('\n')
                first_line = code_lines.pop(0)
                last_line = code_lines.pop(-1)

                # Corrigir o código sem a primeira e última linha
                code_python_correct = autopep8.fix_code('\n'.join(code_lines))

                try:
                    # Executar o código corrigido
                    exec(code_python_correct, globals(), locals())
                    code_python_correct = first_line + '\n' + code_python_correct + last_line
                    code_python_correct += (f"\n% ==============\n% Código executado!\n")
                except Exception as e:
                    # Incluir a primeira e última linha novamente
                    code_python_correct = first_line + '\n' + code_python_correct + last_line
                    code_python_correct += (f"\n% ==========================\n% Erro ao executar o código: \n% {e}\n")

                blocks.append(code_python_correct)
                text = "X" + str(contador).zfill(3) + "X"
                blocks_text.append(text)
                question_text = question_text[:start] + text + question_text[end + 2:]
                start = question_text.find('[[def:', end - 6)
                contador += 1
            else:
                break

        # Inicializar a ferramenta de correção ortográfica
        tool = LanguageTool(language_choice)

        # Corrigir os erros de ortografia apenas na parte não ignorada
        matches = tool.check(question_text)
        suggested_text = tool.correct(question_text)

        # Restaurar as partes ignoradas
        for block, text in zip(blocks, blocks_text):
            suggested_text = suggested_text.replace(text, block)  # Mantém [[code: e ]]

        return JsonResponse({'suggested_text': suggested_text})
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

def similar_question_ai(request, pk):
    question_to_copy = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        text = question_to_copy.question_short_description
        if len(text) > 47:
            text = text[:47] + '-cp'
        else:
            text += '-cp'

        # Copiar a questão
        new_question = copy(question_to_copy)
        new_question.pk = None
        new_question.question_short_description = text
        new_question.question_who_created = request.user
        # vai para o prompt da llm: question_to_copy.question_text
        # retorno_llm deve ser validado
        # new_question.question_text = retorno_llm
        new_question.save()

        # Copiar as respostas relacionadas
        lista_respostas = []
        for answer in question_to_copy.answers2.all():
            lista_respostas.append("A: "+ answer.answer_text)

        if lista_respostas:
            # concatenar com retorno_llm + lista_respostas
            pass

        # pede para gerar questao similar com AI para qq caso:
        # QM
        # QM paramétrico (com código python na descrição)
        # QT
        # QT paramétrico

        lista_respostas = []
        for answer in question_to_copy.answers2.all():
            copied_answer = copy(answer)
            copied_answer.pk = None  # Limpar a chave primária
            copied_answer.question = new_question
            # copied_answer.answer = answer_ai
            copied_answer.save()

        messages.error(request, format_html(
            _('The question has been successfully duplicated! You can <a href="../../{}/update/">view and edit the duplicated question here</a>.'),
            new_question.id))

    return render(request, 'exam/exam_msg.html', {})


def copy_question(request, pk):
    question_to_copy = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        text = question_to_copy.question_short_description
        if len(text) > 47:
            text = text[:47] + '-cp'
        else:
            text += '-cp'

        # Copiar a questão
        new_question = copy(question_to_copy)
        new_question.pk = None
        new_question.question_short_description = text
        new_question.question_who_created = request.user
        new_question.save()

        # Copiar as respostas relacionadas
        for answer in question_to_copy.answers2.all():
            copied_answer = copy(answer)
            copied_answer.pk = None  # Limpar a chave primária
            copied_answer.question = new_question
            copied_answer.save()

        messages.error(request, format_html(
            _('The question has been successfully duplicated! You can <a href="../../{}/update/">view and edit the duplicated question here</a>.'),
            new_question.id))

    return render(request, 'exam/exam_msg.html', {})

from django.http import JsonResponse
import json

@login_required
def save_question_Json(request, pk):
    """
    Exporta apenas os dados essenciais das questões do professor logado.
    Formato 'Slim': Sem IDs de banco, sem dados de usuário, apenas conteúdo.
    """
    # 1. Filtra questões criadas pelo usuário
    questions_qs = Question.objects.filter(question_who_created=request.user).select_related('topic')

    export_data = []

    for q in questions_qs:
        # 2. Constrói o objeto da questão (apenas dados conteudistas)
        q_data = {
            "topic_text": q.topic.topic_text, # Usa o TEXTO do tópico, não o ID
            "type": q.question_type,
            "difficulty": q.question_difficulty,
            "group": q.question_group,
            "short_desc": q.question_short_description,
            "text": q.question_text,
            "parametric": q.question_parametric,
            "answers": []
        }

        # 3. Adiciona as respostas
        for ans in q.answers2.all(): # ou Answer.objects.filter(question=q)
            q_data["answers"].append({
                "text": ans.answer_text,
                "feedback": ans.answer_feedback
            })

        export_data.append(q_data)

    # 4. Retorna o arquivo JSON para download
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="{request.user.username}_questions_slim.json"'
    return response

@login_required
@permission_required('exam.change_exam', raise_exception=True)
def ImportQuestionsJson(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['myfile']
            data = json.load(uploaded_file)
        except Exception as e:
            messages.error(request, _('Error reading JSON: ') + str(e))
            return render(request, 'exam/exam_errors.html', {})

        if not data:
            messages.error(request, _('JSON file is empty.'))
            return render(request, 'exam/exam_errors.html', {})

        questions_created = []
        questions_equal = []
        topic_cache = {}

        for item in data:
            topic_text = item.get('topic_text', '').strip()
            question_text = item.get('text', '').strip()

            if not topic_text or not question_text:
                continue

            # Prepara snippet
            txt_snippet = (question_text[:100] + '...') if len(question_text) > 100 else question_text
            txt_snippet = txt_snippet.replace('\n', ' ').replace('\r', '')

            # 1. Validação do Tópico
            if topic_text in topic_cache:
                topic = topic_cache[topic_text]
            else:
                try:
                    topic = Topic.objects.get(topic_text=topic_text)
                    has_permission = False
                    for d in topic.discipline.all():
                        if request.user in d.discipline_profs.all() or request.user in d.discipline_coords.all():
                            has_permission = True
                            break
                    if not has_permission:
                        print(f"Skipped: No permission for topic {topic_text}")
                        continue
                    topic_cache[topic_text] = topic
                except Topic.DoesNotExist:
                    continue

            # 2. Verificação de Duplicatas
            existing_q = Question.objects.filter(
                topic=topic,
                question_text=question_text,
                topic__discipline__discipline_profs=request.user
            ).first()

            if existing_q:
                answers_data = item.get('answers', [])
                if answers_data:
                    first_ans_text = answers_data[0].get('text', '')
                    first_ans_db = existing_q.answers2.first() or Answer.objects.filter(question=existing_q).first()

                    if first_ans_db and first_ans_db.answer_text == first_ans_text:
                        # Salva ID e Texto
                        questions_equal.append({'id': str(existing_q.pk), 'text': txt_snippet})
                        continue

            # 3. Criação da Questão
            try:
                is_parametric = 'yes' if '[[def:' in question_text else 'no'

                new_q = Question.objects.create(
                    topic=topic,
                    question_who_created=request.user,
                    question_text=question_text,
                    question_type=item.get('type', 'QM'),
                    question_difficulty=item.get('difficulty', 1),
                    question_group=item.get('group', ''),
                    question_short_description=item.get('short_desc', '')[:50],
                    question_parametric=is_parametric,
                    question_last_update=datetime.date.today(),
                    question_bloom_taxonomy='remember'
                )

                for ans in item.get('answers', []):
                    Answer.objects.create(
                        question=new_q,
                        answer_text=ans.get('text', ''),
                        answer_feedback=ans.get('feedback', '')
                    )

                questions_created.append({
                    'id': str(new_q.pk),
                    'topic': topic.topic_text,
                    'parametric': is_parametric,
                    'text': txt_snippet
                })

            except Exception as e:
                print(f"Error creating question JSON: {e}")
                continue

        # 4. Relatório Final Melhorado

        # --- NOVAS ---
        if questions_created:
            messages.success(request, '<br>', extra_tags='safe')
            messages.success(request, _('Questions Created Successfully:'))

            for item in questions_created[:20]:
                url = f"/topic/question/{item['id']}/update/"
                link_html = f"<a href='{url}' target='_blank' style='text-decoration: underline; font-weight: bold;'>{item['id']}</a>"

                msg = f"ID: {link_html} - Topic: {item['topic']} - Parametric: {item['parametric']}<br>" \
                      f"<small style='color: #555; font-style: italic; margin-left: 15px;'>\"{item['text']}\"</small>"
                messages.info(request, msg, extra_tags='safe')

            if len(questions_created) > 20:
                messages.info(request, f"... and {len(questions_created) - 20} more.")

        # --- DUPLICADAS ---
        if questions_equal:
            messages.warning(request, '<br>', extra_tags='safe')
            messages.warning(request, _('Skipped similar question(s) already in DB:'))

            for item in questions_equal[:20]:
                qid = item['id']
                url = f"/topic/question/{qid}/update/"
                link_html = f"<a href='{url}' target='_blank' style='text-decoration: underline; color: #856404;'>{qid}</a>"

                msg = f"ID: {link_html} <br>" \
                      f"<small style='margin-left: 15px;'>\"{item['text']}\"</small>"
                messages.warning(request, msg, extra_tags='safe')

            if len(questions_equal) > 20:
                messages.warning(request, f"... and {len(questions_equal) - 20} more.", extra_tags='safe')

        if not questions_created and not questions_equal:
            messages.warning(request, '<br>', extra_tags='safe')
            messages.warning(request, _('No questions were processed or permissions denied.'))

    return render(request, 'exam/exam_msg.html', {})

@login_required
@permission_required('exam.change_exam', raise_exception=True)
def ImportQuestions(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['myfile']
        except KeyError:
            messages.error(request, _('ImportQuestions: choose a TXT file following the model!'))
            return render(request, 'exam/exam_errors.html', {})

        try:
            listao = UtilsMC.questionsReadFiles(request, uploaded_file)
        except Exception as e:
            messages.error(request, _('Error reading file: ') + str(e))
            return render(request, 'exam/exam_errors.html', {})

        if not listao:
            if not messages.get_messages(request):
                messages.error(request, _('No questions found or invalid format.'))
            return render(request, 'exam/exam_errors.html', {})

        questions_created = []
        questions_equal = []
        topic_cache = {}

        for qq in listao:
            topic_text = qq.get('c', '').strip()
            question_text = qq.get('q', '').strip()
            answers_text = qq.get('a', [])

            if not topic_text:
                continue

            # Prepara um snippet (trecho) do texto para exibição (ex: primeiros 100 chars)
            txt_snippet = (question_text[:100] + '...') if len(question_text) > 100 else question_text
            # Remove quebras de linha para não quebrar o layout da mensagem
            txt_snippet = txt_snippet.replace('\n', ' ').replace('\r', '')

            # 2. Verificação de Duplicatas
            is_duplicate = False
            existing_questions = Question.objects.filter(
                topic__topic_text=topic_text,
                question_text=question_text,
                topic__discipline__discipline_profs=request.user
            )

            for q in existing_questions:
                if answers_text:
                    first_answer_db = q.answers2.first() or Answer.objects.filter(question=q).first()
                    if first_answer_db and first_answer_db.answer_text == answers_text[0]:
                        is_duplicate = True
                        # Salva ID e o Texto para mostrar no log
                        questions_equal.append({'id': str(q.pk), 'text': txt_snippet})
                        break

            if is_duplicate:
                continue

            # 3. Validação do Tópico (Cache)
            if topic_text in topic_cache:
                topic = topic_cache[topic_text]
            else:
                try:
                    topic = Topic.objects.get(topic_text=topic_text)
                    has_permission = False
                    for d in topic.discipline.all():
                        if request.user in d.discipline_profs.all() or request.user in d.discipline_coords.all():
                            has_permission = True
                            break
                    if not has_permission:
                        messages.error(request, _("ImportQuestions: Teacher is not associated with any discipline for topic: ") + topic_text)
                        return render(request, 'exam/exam_errors.html', {})
                    topic_cache[topic_text] = topic
                except Topic.DoesNotExist:
                    messages.error(request, "\n" +  _("ImportQuestions: Topic does not exist (Create it first): ") + topic_text)
                    return render(request, 'exam/exam_errors.html', {})

            # 4. Definição de Parametros
            q_type = 'QM'
            difficulty = 1
            type_code = qq.get('t', 'QM')
            if type_code == 'QM': difficulty = 3
            elif type_code == 'QH': difficulty = 5
            elif type_code == 'QT':
                difficulty = 5
                q_type = 'QT'

            # 5. Criação
            try:
                is_parametric = 'yes' if '[[def:' in question_text else 'no'

                new_q = Question.objects.create(
                    topic=topic,
                    question_group=qq.get('st', ''),
                    question_short_description=f"{topic_text}{str(qq.get('n', 0)).zfill(3)}",
                    question_text=question_text,
                    question_type=q_type,
                    question_difficulty=difficulty,
                    question_bloom_taxonomy='remember',
                    question_last_update=datetime.date.today(),
                    question_who_created=request.user,
                    question_parametric=is_parametric,
                )

                # Salva dados completos para o relatório
                questions_created.append({
                    'id': str(new_q.pk),
                    'topic': topic.topic_text,
                    'parametric': is_parametric,
                    'text': txt_snippet
                })

                for ans_text in answers_text:
                    Answer.objects.create(question=new_q, answer_text=ans_text, answer_feedback='')

            except Exception as e:
                messages.error(request, f"Error creating question: {str(e)}")
                return render(request, 'exam/exam_errors.html', {})

        # 6. Relatório Final Melhorado

        # --- QUESTÕES NOVAS ---
        if questions_created:
            messages.success(request, '<br>', extra_tags='safe')
            messages.success(request, _('Questions Created Successfully:'))

            for item in questions_created[:20]:
                qid = item['id']
                url = f"/topic/question/{qid}/update/"
                link_html = f"<a href='{url}' target='_blank' style='text-decoration: underline; font-weight: bold;'>{qid}</a>"

                # Layout: ID (Link) - Topic - Parametric
                #         "Texto da questão..."
                msg = f"ID: {link_html} - Topic: {item['topic']} - Parametric: {item['parametric']}<br>" \
                      f"<small style='color: #555; font-style: italic; margin-left: 15px;'>\"{item['text']}\"</small>"

                messages.info(request, msg, extra_tags='safe')

            if len(questions_created) > 20:
                messages.info(request, f"... and {len(questions_created) - 20} more.")

        # --- QUESTÕES EXISTENTES (PULADAS) ---
        if questions_equal:
            messages.warning(request, '<br>', extra_tags='safe')
            messages.warning(request, _('Skipped similar question(s) already in DB:'))

            # Mostra detalhes das primeiras 20 duplicadas
            for item in questions_equal[:20]:
                qid = item['id']
                url = f"/topic/question/{qid}/update/"
                link_html = f"<a href='{url}' target='_blank' style='text-decoration: underline; color: #856404;'>{qid}</a>"

                msg = f"ID: {link_html} <br>" \
                      f"<small style='margin-left: 15px;'>\"{item['text']}\"</small>"

                messages.warning(request, msg, extra_tags='safe')

            if len(questions_equal) > 20:
                messages.warning(request, f"... and {len(questions_equal) - 20} more.", extra_tags='safe')

        if not questions_created and not questions_equal:
            messages.warning(request, '<br>', extra_tags='safe')
            messages.warning(request, _('No questions were processed.'))

    return render(request, 'exam/exam_msg.html', {})

@login_required
def ImportQuestionsImage(request):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'exam.change_exam' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    if request.method == 'POST':

        try:
            file = request.FILES['myfile']
        except:
            messages.error(request, _('ImportQuestionsImage: choose a PNG following the model!'))
            return render(request, 'exam/exam_errors.html', {})

        fs = FileSystemStorage()
        file0 = str(file.name)
        file0 = file0.replace(' ', '')

        file0 = re.sub('[^A-Za-z0-9._-]+', '', file0)  # remove special characters

        filename = fs.save(file0, file)

        # problem with permission ...
        path = os.getcwd()
        getuser = path.split('/')
        getuser = getuser[2]
        getuser = getuser + ':' + getuser
        os.system('mv ' + filename + ' ' + path + '/tmp/')
        os.system('chown -R ' + getuser + ' ' + path)
        #os.system('chgrp -R ' + getuser + ' ' + path)

        messages.error(request, _('Image imported successfully! ') + filename)

    # return HttpResponseRedirect("../")
    return render(request, 'exam/exam_msg.html', {})


#######################################################################
class TopicListView(LoginRequiredMixin, generic.ListView):
    model = Topic
    fields = '__all__'

    # paginate_by = 10

    def get_queryset(self):
        # if len(Topic.objects.filter(discipline__discipline_coords=self.request.user)):
        #     lista = Topic.objects.filter(discipline__discipline_coords=self.request.user)
        #     return lista.order_by('topic_text').distinct()
        # if len(Topic.objects.filter(discipline__discipline_profs=self.request.user)):
        #     lista = Topic.objects.filter(discipline__discipline_profs=self.request.user)
        #     return lista.order_by('topic_text').distinct()

        t1 = Topic.objects.filter(discipline__discipline_profs=self.request.user)
        t2 = Topic.objects.filter(discipline__discipline_coords=self.request.user)
        return (t1 | t2).order_by('topic_text').distinct()


class TopicUpdate(LoginRequiredMixin, generic.UpdateView):
    # model = Topic
    # fields = '__all__'
    form_class = TopicUpdateForm

    template_name = 'topic/topic_update.html'

    def get_form_kwargs(self):
        kwargs = super(TopicUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Verifica se já existe um tópico com o mesmo topic_text
        topic_text = form.cleaned_data['topic_text']
        discipline_initials = form.cleaned_data['discipline'][0].discipline_code
        topic_count = Topic.objects.filter(topic_text__startswith=f"{discipline_initials}_").count()
        topic_text0 = form.initial['topic_text']

        if Topic.objects.filter(topic_text=topic_text).exists() and topic_text != topic_text0:
            # Sugere um nome com prefixo e contador
            suggested_topic_text = f"{discipline_initials}_{topic_count + 1:02d}_{topic_text}"
            messages.error(
                self.request,
                _("A topic with the same text already exists. Please consider using a unique name. Suggested name: {}").format(
                    suggested_topic_text)
            )
            return render(self.request, 'exam/exam_errors.html', {})

        d = form.cleaned_data['discipline']
        d_obj = get_object_or_404(Discipline, pk=d[0].pk)
        if not self.request.user in d_obj.discipline_coords.all():
            messages.error(self.request, _("TopicCreate: the user isn't the coordinator of the discipline"))
            return render(self.request, 'exam/exam_errors.html', {})

        return super(TopicUpdate, self).form_valid(form)

    def get_queryset(self):
        if len(Topic.objects.filter(discipline__discipline_coords=self.request.user)):
            return Topic.objects.filter(discipline__discipline_coords=self.request.user).distinct()
        if len(Topic.objects.filter(discipline__discipline_profs=self.request.user)):
            return Topic.objects.filter(discipline__discipline_profs=self.request.user).distinct()


class TopicDetailView(LoginRequiredMixin, generic.DetailView):
    model = Topic
    template_name = 'topic/topic_detail.html'

    def get_queryset(self):
        return Topic.objects.all().distinct()


class TopicCreate(LoginRequiredMixin, generic.CreateView):
    form_class = TopicCreateForm
    # model = Topic
    # fields = '__all__'

    template_name = 'topic/topic_create.html'
    success_url = '/topic/topics'

    def get_form_kwargs(self):
        kwargs = super(TopicCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Verifica se já existe um tópico com o mesmo topic_text
        topic_text = form.cleaned_data['topic_text']
        discipline_initials = form.cleaned_data['discipline'][0].discipline_code
        topic_count = Topic.objects.filter(topic_text__startswith=f"{discipline_initials}_").count()

        if Topic.objects.filter(topic_text=topic_text).exists():
            # Sugere um nome com prefixo e contador
            suggested_topic_text = f"{discipline_initials}_{topic_count + 1:02d}_{topic_text}"
            messages.error(
                self.request,
                _("A topic with the same text already exists. Please consider using a unique name. Suggested name: {}").format(
                    suggested_topic_text)
            )
            return render(self.request, 'exam/exam_errors.html', {})

        d = form.cleaned_data['discipline']
        d_obj = get_object_or_404(Discipline, pk=d[0].pk)
        if not self.request.user in d_obj.discipline_coords.all():
            messages.error(self.request, _("TopicCreate: the user isn't the coordinator of the discipline"))
            return render(self.request, 'exam/exam_errors.html', {})

        return super(TopicCreate, self).form_valid(form)

    def get_queryset(self):
        if len(Topic.objects.filter(discipline__discipline_coords=self.request.user)):
            return Topic.objects.filter(discipline__discipline_coords=self.request.user).distinct()
        if len(Topic.objects.filter(discipline__discipline_profs=self.request.user)):
            return Topic.objects.filter(discipline__discipline_profs=self.request.user).distinct()


class TopicDelete(LoginRequiredMixin, generic.DeleteView):
    model = Topic
    template_name = 'topic/topic_confirm_delete.html'
    success_url = '/topic/topics'

    def get_queryset(self):
        if len(Topic.objects.filter(discipline__discipline_coords=self.request.user)):
            return Topic.objects.filter(discipline__discipline_coords=self.request.user).distinct()
        if len(Topic.objects.filter(discipline__discipline_profs=self.request.user)):
            return Topic.objects.filter(discipline__discipline_profs=self.request.user).distinct()


@login_required
def see_topic_PDF_aux(request, new_order, questions_id, allQuestionsStr, countQuestions):
    for qid in new_order:
        q = get_object_or_404(Question, pk=questions_id[qid])
        print('#######################', q.id, q.question_short_description)

        countQuestions += 1
        str1 = "\\noindent\\rule{\\textwidth}{0.8pt}\\\\\n"
        str1 += "\\noindent\\textbf{Count:} %d\\\\\n" % countQuestions
        str1 += "\\noindent\\textbf{Short Description:} %s\\\\\n" % q.question_short_description
        str1 += "\\noindent\\textbf{Group:} %s\\\\\n" % q.question_group
        str1 += "\\noindent\\textbf{Type:} %s\\\\\n" % q.question_type
        str1 += "\\noindent\\textbf{Difficulty:} %s\\\\\n" % q.question_difficulty
        str1 += "\\noindent\\textbf{Bloom taxonomy:} %s\\\\\n" % q.question_bloom_taxonomy
        str1 += "\\noindent\\textbf{Last update:} %s\\\\\n" % q.question_last_update
        str1 += "\\noindent\\textbf{Who created:} %s\\\\\n" % q.question_who_created
        str1 += "\\noindent\\textbf{URL:} \\url{%stopic/question/%s/update/}\\\\\n" % (
            os.getenv('IP_HOST2'), q.id)
        str1 += "\\noindent\\textbf{Parametric:} %s\\\\\n" % q.question_parametric.upper()
        if q.question_type == "QM" and q.question_correction_count:
            Accuracy = (q.question_correct_count / q.question_correction_count) * 100
            str1 +="\\noindent\\textbf{Correct:} %s\\\\\n" % q.question_correct_count
            str1 +="\\noindent\\textbf{Correction:} %s\\\\\n" % q.question_correction_count
            str1 +="\\noindent\\textbf{Accuracy:} %.1f\\\\\n" % Accuracy

        st = q.question_text
        a, b = st.find('begin{comment}'), st.find('end{comment}')
        if a < b:
            str1 += "\\noindent\\textbf{Integration:} %s\\\\\n" % 'Moodle+VPL'

        ss1 = "\n\\hspace{-15mm}{\\small {\\color{green}\\#%s}} \\hspace{-1mm}"
        ss = ss1 % str(q.id).zfill(4)

        str1 += "%s %s." % (ss, 1)

        if q.question_parametric == 'no':
            quest = q.question_text + '\n'
            ans = []
            if q.question_type == "QM":
                for a in q.answers():
                    ans.append(a.answer_text + '\n')
        else:  # QUESTOES PARAMETRICAS
            try:
                if q.question_type == "QM":
                    [quest, ans, feedback_ans] = UtilsMC.questionParametric(q.question_text, q.answers(), [])
                else:  # se for dissertativa, não colocar alternativas
                    [quest, ans, feedback_ans] = UtilsMC.questionParametric(q.question_text, [], [])
                if quest == "":
                    messages.error(request,
                                   _('UtilsMC.questionParametric: do not use some words in the code, '
                                     'for ex. exec, cmd, open, import os, remove, mkdir, sys, gnureadline, '
                                     'subprocess, getopt, shlex, wget, commands, system, exec, eval'))
                    messages.error(request, 'Question: %d' % q.id)
                    return render(request, 'exam/exam_errors.html', {})
            except:
                str1 += "ERRO NA PARTE PARAMÉTRICA!!!\\\\\n"
                messages.error(request, _('ERROR IN THE PARAMETRIC PART!!!'))
                messages.error(request, 'Question: %d' % q.id)
                return render(request, 'exam/exam_errors.html', {})
                # continue

        str1 += r' %s\n\n' % ''.join(quest)
        str1 += "\n\n\\vspace{2mm}\\begin{oneparchoices}\\hspace{-3mm}\n"
        for a in random.sample(ans, len(ans)):
            if ans.index(a) == 0:
                str1 += "\\choice \\hspace{-2.0mm}{\\tiny{\\color{blue}\#%s}}%s" % (str(ans.index(a)), a)
            else:
                str1 += "\\choice \\hspace{-2.0mm}{\\tiny{\\color{red}*%s}}%s" % (str(ans.index(a)), a)

            try:
                if feedback_ans[ans.index(a)] != '\n':
                    str1 += '[' + feedback_ans[ans.index(a)] + ']'  ############# NOVO
            except:  # quando cria alternativas automáticas, não tem feedback
                pass

        str1 += "\\end{oneparchoices}\\vspace{0mm}\\\\\n"

        allQuestionsStr.append(str1)

    return countQuestions, allQuestionsStr


@login_required
@csrf_exempt
@login_required
@csrf_exempt
def see_topic_PDF(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if 'exam.change_exam' not in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    topic = get_object_or_404(Topic, pk=pk)

    # Verifica se o professor tem acesso à disciplina deste tópico
    # Otimizado para .exists()
    if not Topic.objects.filter(pk=pk, discipline__discipline_profs=request.user).exists():
        messages.error(request, _('The professor does not have permission!'))
        return render(request, 'exam/exam_errors.html', {})

    if request.method == 'POST':
        # --- CONSTRUÇÃO DO CONTEÚDO LATEX ---
        latex_content = ""
        latex_content += Utils.getBegin()
        latex_content += "\\noindent\\Huge{MCTest}\\normalsize\\vspace{5mm}\\\\\n"
        latex_content += "\\noindent\\textbf{Topic:} %s\\\\\n" % topic.topic_text

        allQuestionsStr = []
        countQuestions = 0

        # 1. Questões de Múltipla Escolha (QM)
        # Filtra direto no banco para evitar loops desnecessários
        qs_qm = topic.questions2.filter(question_type='QM').order_by('question_text')
        if qs_qm.exists():
            questions_id = [q.id for q in qs_qm]
            questions_text = [q.question_text for q in qs_qm]

            new_order = UtilsMC.sortedBySimilarity2(questions_text)

            # Chama a função auxiliar existente (que retorna strings prontas na lista)
            countQuestions, allQuestionsStr = see_topic_PDF_aux(
                request, new_order, questions_id, allQuestionsStr, countQuestions
            )

        if countQuestions > 0:
            allQuestionsStr.append("\\newpage\\\\\n")

        # 2. Questões de Texto (QT)
        qs_qt = topic.questions2.filter(question_type='QT').order_by('question_text')
        if qs_qt.exists():
            questions_id = [q.id for q in qs_qt]
            questions_text = [q.question_text for q in qs_qt]

            new_order = UtilsMC.sortedBySimilarity2(questions_text)

            countQuestions, allQuestionsStr = see_topic_PDF_aux(
                request, new_order, questions_id, allQuestionsStr, countQuestions
            )

        # Junta todas as partes
        for st in allQuestionsStr:
            latex_content += st

        latex_content += "\\end{document}"

        # --- GERAÇÃO DO PDF ---
        generator = PDFGenerator()

        final_path = generator.generate(
            latex_content=latex_content,
            filename_base=request.user.username,
            destination_folder_name='pdfTopic'
        )

        if final_path and os.path.exists(final_path):
            return serve(request, os.path.basename(final_path), os.path.dirname(final_path))
        else:
            messages.error(request, "Error generating PDF Topic file.")
            return render(request, 'exam/exam_errors.html', {})

    # Se não for POST, provavelmente deveria renderizar algo ou redirecionar
    # Assumindo um retorno padrão caso não seja POST
    return HttpResponseRedirect("/")


###################################################################
# views.py

class QuestionListView(LoginRequiredMixin, generic.ListView):
    model = Question
    template_name = 'question/question_list.html'

    # Sem paginação (paginate_by removido)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Carrega disciplinas onde o usuário é Prof ou Coord para o filtro
        context['filter_disciplines'] = Discipline.objects.filter(
            Q(discipline_profs=self.request.user) |
            Q(discipline_coords=self.request.user)
        ).distinct().order_by('discipline_name')

        # Mantém a seleção
        if self.request.GET.get('discipline'):
            try:
                context['selected_discipline'] = int(self.request.GET.get('discipline'))
            except ValueError:
                pass

        return context

    def get_queryset(self):
        # Base: Questões de disciplinas onde o usuário é prof ou coord
        # (Lógica original: q1 | q2)
        qs = Question.objects.filter(
            Q(topic__discipline__discipline_profs=self.request.user) |
            Q(topic__discipline__discipline_coords=self.request.user)
        )

        disc_id = self.request.GET.get('discipline')

        # LÓGICA DO FILTRO
        if disc_id:
            qs = qs.filter(topic__discipline__id=disc_id)

            # Otimização de Performance
            return qs.select_related('topic') \
                .prefetch_related(
                'topic__discipline',
                'topic__discipline__discipline_coords',
                'topic__discipline__discipline_profs'
            ) \
                .annotate(num_answers=Count('answers2')) \
                .order_by('question_short_description').distinct()
        else:
            # Retorna vazio se não selecionar disciplina (Carga rápida)
            return Question.objects.none()

# class QuestionListView(LoginRequiredMixin, generic.ListView):
#     model = Question
#     template_name = 'question/question_list.html'
#
#     # paginate_by = 100
#
#     def get_queryset(self):
#         q1 = Question.objects.filter(topic__discipline__discipline_profs=self.request.user)
#         q2 = Question.objects.filter(topic__discipline__discipline_coords=self.request.user)
#         return (q1 | q2).order_by('question_short_description').distinct()


class LoanedQuestionByUserListView(LoginRequiredMixin, generic.ListView):
    model = Question
    template_name = 'question/question_list_who_created_user.html'

    # Sem paginação, conforme solicitado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 2. ALTERAÇÃO AQUI:
        # Carrega apenas disciplinas onde o usuário é Professor OU Coordenador
        context['filter_disciplines'] = Discipline.objects.filter(
            Q(discipline_profs=self.request.user) |
            Q(discipline_coords=self.request.user)
        ).distinct().order_by('discipline_name')

        # Se o usuário já selecionou uma disciplina, carrega os Tópicos dela
        selected_discipline = self.request.GET.get('discipline')
        if selected_discipline:
            try:
                disc_id = int(selected_discipline)
                context['selected_discipline'] = disc_id

                # Carrega tópicos apenas da disciplina selecionada
                # E apenas tópicos que tenham questões criadas pelo professor (opcional, mas recomendado para não mostrar tópicos vazios)
                context['filter_topics'] = Topic.objects.filter(
                    discipline__id=disc_id,
                    questions2__question_who_created=self.request.user
                ).distinct().order_by('topic_text')

            except ValueError:
                pass

        if self.request.GET.get('topic'):
            try:
                context['selected_topic'] = int(self.request.GET.get('topic'))
            except ValueError:
                pass

        return context

    def get_queryset(self):
        # Base: Questões criadas pelo professor
        qs = Question.objects.filter(question_who_created=self.request.user)

        disc_id = self.request.GET.get('discipline')
        topic_id = self.request.GET.get('topic')

        # LÓGICA DO FILTRO OBRIGATÓRIO
        if disc_id:
            # Filtra pela disciplina
            qs = qs.filter(topic__discipline__id=disc_id)

            if topic_id:
                qs = qs.filter(topic__id=topic_id)

            # Otimização de Banco de Dados
            return qs.select_related('topic') \
                .prefetch_related(
                'topic__discipline',
                'topic__discipline__discipline_coords',
                'topic__discipline__discipline_profs'
            ) \
                .annotate(num_answers=Count('answers2')) \
                .order_by('question_short_description').distinct()

        else:
            # Se não escolheu disciplina, retorna lista VAZIA (carregamento instantâneo)
            return Question.objects.none()

# class LoanedQuestionByUserListView(LoginRequiredMixin, generic.ListView):
#     model = Question
#     template_name = 'question/question_list_who_created_user.html'
#
#     # paginate_by = 100
#
#     def get_queryset(self):
#         # Otimização: annotate adiciona o campo 'num_answers' em cada objeto
#         lista = Question.objects.filter(question_who_created=self.request.user) \
#             .annotate(num_answers=Count('answers2'))
#         return lista.order_by('question_text').distinct()


class QuestionDetailView(generic.DetailView):
    model = Question
    template_name = 'question/question_detail.html'

    def get_queryset(self):
        q1 = Question.objects.filter(topic__discipline__discipline_profs=self.request.user)
        q2 = Question.objects.filter(topic__discipline__discipline_coords=self.request.user)
        return (q1 | q2).order_by('question_short_description').distinct()


####################################################################
# answers = Answer.objects.filter(question=question_inst)
# answers_data = [{'answer_text': q.answer_text} for q in answers]
from django.core import serializers


@login_required
def UpdateQuestion(request, pk):
    if request.user.get_group_permissions():
        perm = [p for p in request.user.get_group_permissions()]
        if not 'topic.change_question' in perm:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

    question_inst = get_object_or_404(Question, pk=pk)
    AnswerInlineFormSet = inlineformset_factory(
        Question, Answer, fk_name='question', fields=('answer_text', 'answer_feedback',),
        widgets={'answer_text': Textarea(attrs={'cols': 80, 'rows': 1}),
                 'answer_feedback': Textarea(attrs={'cols': 40, 'rows': 1}), },
        extra=1)  # quantidade de alternativas na tela

    Utils.validateProfByQuestion(question_inst, request.user)

    '''
    JSONSerializer = serializers.get_serializer("json")
    json_serializer = JSONSerializer()
    with open("file_json.json","w") as out:
        all_objects = Question.objects.filter(id=pk) 
        #all_objects.append(Answer.objects.filter(question__pk=pk))
        print (all_objects)
        json_serializer.serialize(all_objects, stream=out)
    #print (serializers.serialize("json",Question.objects.filter(id=pk)))
    '''

    if request.method == 'POST':

        form = UpdateQuestionForm(request.POST)
        if form.is_valid():  # Check if the forms are valid:

            profs = []  # pega todos os profs da disciplina
            for d in question_inst.topic.discipline.all():
                for p in d.discipline_coords.all():
                    profs.append(p)
            if not (request.user == question_inst.question_who_created or request.user in profs):
                messages.error(request, _(
                    'ERROR: You did not create this question or you are not the course coordinator. Please get in touch with them.'));
                return render(request, 'exam/exam_errors.html', {})

            '''
            # para aceitar símbolos na descrição, codificiar antes de salvar no BD
            # > echo 'símbolos especiais' | xxd -ps
            user = '_'+str(request.user) + '.txt'
            filetxt = open('.description' + user, 'w')
            filetxt.write(form.cleaned_data["question_text"])
            filetxt.close()
            #os.system('cat .description' + user + ' | xxd -ps >> .description_encode' + user)
            os.system('xxd -ps .description' + user + ' > .description_encode' + user)
            filetxt = open('.description_encode' + user, 'r')
            s = filetxt.read()

            # para decodificar:
            # > echo 'símbolos especiais' | xxd -ps | xxd -ps -r
            user = '_' + str(request.user) + '.txt'
            os.system('cat .description_encode' + user + ' | xxd -ps | xxd -ps -r >> .description_decode' + user)
            filetxt = open('.description_decode' + user, 'r')
            ss = filetxt.read()
            
            não funciona, pois ao visualizar o form mostra o codificado...
            '''

            question_inst.topic = form.cleaned_data['topic']
            question_inst.question_short_description = form.cleaned_data['question_short_description']
            question_inst.question_group = form.cleaned_data['question_group']
            question_inst.question_text = form.cleaned_data['question_text']
            question_inst.question_type = form.cleaned_data['question_type']
            question_inst.question_difficulty = form.cleaned_data['question_difficulty']
            question_inst.question_bloom_taxonomy = form.cleaned_data['question_bloom_taxonomy']
            question_inst.question_parametric = form.cleaned_data['question_parametric']
            question_inst.question_who_created = form.cleaned_data['question_who_created']
            question_inst.question_last_update = form.cleaned_data['question_last_update']

            question_inst.question_correction_count = form.cleaned_data['question_correction_count']
            question_inst.question_correct_count = form.cleaned_data['question_correct_count']
            question_inst.question_IRT_a_discrimination = form.cleaned_data['question_IRT_a_discrimination']
            question_inst.question_IRT_b_ability = form.cleaned_data['question_IRT_b_ability']
            question_inst.question_IRT_c_guessing = form.cleaned_data['question_IRT_c_guessing']

            #  Método criado por Gabriel Tavares Frota de Azevedo para o TCC do BCC/UFABC.
            # validation = UtilsMC.generateCode(request, question_inst.question_text, pk)
            # if validation is not None:
            #    return validation

            question_inst.save()

        formset = AnswerInlineFormSet(request.POST, request.FILES,
                                      instance=question_inst)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect('/topic/question/' + str(pk) + '/update/')

    else:  # If this is a GET (or any other method) create the default form.
        formset = AnswerInlineFormSet(instance=question_inst)

        st = Utils.validateProfByQuestion(question_inst, request.user)
        if st is not None:
            return HttpResponse(st)

        profs = []  # pega todos os profs da disciplina
        for d in question_inst.topic.discipline.all():
            for p in d.discipline_profs.all():
                profs.append(p)
            for p in d.discipline_coords.all():
                profs.append(p)
        if not request.user in profs:
            messages.error(request, _(
                'ERROR: The teacher is not registered in the Discipline (of the topic)'));
            return render(request, 'exam/exam_errors.html', {})

        # raise Http404(profs)

        proposed_update_date = datetime.date.today()  # + datetime.timedelta(weeks=3)
        form = UpdateQuestionForm(initial={
            'topic': question_inst.topic,
            'question_short_description': question_inst.question_short_description,
            'question_group': question_inst.question_group,
            'question_text': question_inst.question_text,
            'question_type': question_inst.question_type,
            'question_difficulty': question_inst.question_difficulty,
            'question_bloom_taxonomy': question_inst.question_bloom_taxonomy,
            'question_parametric': question_inst.question_parametric,
            'question_who_created': question_inst.question_who_created,
            'question_last_update': question_inst.question_last_update,

            'question_correction_count': question_inst.question_correction_count,
            'question_correct_count': question_inst.question_correct_count,
            'question_IRT_a_discrimination': question_inst.question_IRT_a_discrimination,
            'question_IRT_b_ability': question_inst.question_IRT_b_ability,
            'question_IRT_c_guessing': question_inst.question_IRT_c_guessing,
        })

    return render(request, 'question/question_update.html', {
        'form': form,
        'formset': formset,
        'questioninst': question_inst,
    })


#########################################################

class QuestionCreate(LoginRequiredMixin, generic.CreateView):
    form_class = QuestionCreateForm

    template_name = 'question/question_create.html'
    success_url = reverse_lazy('topic:question-create')

    def get_form_kwargs(self):
        kwargs = super(QuestionCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        flag_ok = True
        t = form.cleaned_data['topic']
        t_obj = get_object_or_404(Topic, pk=t.pk)
        for d in t_obj.discipline.all():
            if self.request.user in d.discipline_profs.all() or self.request.user in d.discipline_coords.all():
                flag_ok = False
                break
        if flag_ok:
            messages.error(self.request, _("QuestionCreate: the teacher is not registered in discipline"))
            return render(self.request, 'exam/exam_errors.html', {})

        form.instance.question_who_created = self.request.user
        t = datetime.date.today()
        form.instance.question_last_update = str(t.year) + "-" + str(t.month) + "-" + str(t.day)

        if form.is_valid():
            #  Método criado por Gabriel Tavares Frota de Azevedo para o TCC do BCC/UFABC.
            # code_validation = UtilsMC.generateCode(self.request, form.instance.question_text, form.instance.pk)
            # if code_validation is not None:
            #     return code_validation
            form.save()

        return super(QuestionCreate, self).form_valid(form)

    def get_queryset(self):
        q1 = Question.objects.filter(topic__discipline__discipline_profs=self.request.user)
        q2 = Question.objects.filter(topic__discipline__discipline_coords=self.request.user)
        return (q1 | q2).order_by('question_short_description').distinct()


class QuestionUpdate(UpdateView):
    model = Question
    template_name = 'question/question_update.html'
    fields = '__all__'
    success_url = reverse_lazy('topic:question-detail')

    def get_queryset(self):
        q1 = Question.objects.filter(topic__discipline__discipline_profs=self.request.user)
        q2 = Question.objects.filter(topic__discipline__discipline_coords=self.request.user)
        return (q1 | q2).order_by('question_short_description').distinct()


class QuestionDelete(DeleteView):
    model = Question
    template_name = 'question/question_confirm_delete.html'
    success_url = reverse_lazy('topic:myquestions-list')

    def get_queryset(self):
        q1 = Question.objects.filter(topic__discipline__discipline_profs=self.request.user)
        q2 = Question.objects.filter(topic__discipline__discipline_coords=self.request.user)
        return (q1 | q2).order_by('question_short_description').distinct()