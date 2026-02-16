#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Suite de Correção de Exames - MCTest
==========================================

Script aprimorado para processar múltiplos PDFs de exames em lote,
com melhor tratamento de erros, logging e limpeza de arquivos.

Autor: Sistema MCTest
Data: 2024-02-16
"""

import os
import sys
import glob
import time
import shutil
import datetime
from pathlib import Path

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import get_resolver
from django.conf import settings
from django.contrib.auth import get_user_model
from exam.models import Exam

User = get_user_model()


class CorrectionTestSuite:
    """
    Suite de testes para processamento em lote de PDFs de exames.
    
    Features:
    - Processamento recursivo de PDFs em subpastas
    - Geração automática de ZIPs com timestamp
    - Limpeza inteligente de arquivos temporários
    - Logging detalhado de operações
    - Tratamento robusto de erros
    """
    
    def __init__(self):
        """Inicializa o test suite."""
        self.client = None
        self.user = None
        self.exam = None
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        self.start_time = None
        
    def setUp(self, user_email=None, user_password=None, exam_id=1):
        """
        Configura o ambiente de testes.
        
        Args:
            user_email (str): Email do usuário para autenticação
            user_password (str): Senha do usuário
            exam_id (int): ID do exame no banco de dados
            
        Returns:
            bool: True se configuração foi bem-sucedida
        """
        print("=" * 80)
        print("CONFIGURAÇÃO DO TEST SUITE")
        print("=" * 80)
        
        # Inicializa o cliente
        self.client = Client()
        
        # Busca usuário
        if user_email:
            # Tenta autenticar com email e senha fornecidos
            try:
                self.user = User.objects.get(email=user_email)
                print(f"✓ Usuário encontrado: {self.user.email}")
                
                # Tenta fazer login com senha
                if user_password:
                    login_success = self.client.login(
                        username=self.user.username,
                        password=user_password
                    )
                    if login_success:
                        print(f"✓ Login autenticado com senha")
                    else:
                        print(f"⚠ Falha no login com senha, usando force_login")
                        self.client.force_login(self.user)
                else:
                    # Sem senha, usa force_login
                    self.client.force_login(self.user)
                    print(f"✓ Usuário autenticado via force_login")
                    
            except User.DoesNotExist:
                print(f"✗ ERRO: Usuário com email '{user_email}' não encontrado.")
                print(f"  Tentando usar superusuário como fallback...")
                self.user = User.objects.filter(is_superuser=True).first()
                if self.user:
                    self.client.force_login(self.user)
                    print(f"✓ Usando superusuário: {self.user.email}")
                else:
                    print("✗ ERRO: Nenhum superusuário encontrado no banco de dados.")
                    return False
        else:
            # Sem email fornecido, busca superusuário
            self.user = User.objects.filter(is_superuser=True).first()
            if not self.user:
                print("✗ ERRO: Nenhum superusuário encontrado no banco de dados.")
                print("  Crie um superusuário: python manage.py createsuperuser")
                return False
            
            # Faz login forçado (bypass de autenticação)
            self.client.force_login(self.user)
            print(f"✓ Usuário autenticado: {self.user.email}")
        
        # Busca o exame
        try:
            self.exam = Exam.objects.get(pk=exam_id)
            print(f"✓ Exame encontrado: {self.exam.exam_name} (ID: {exam_id})")
            print(f"  - Tipo de impressão: {self.exam.exam_print}")
            print(f"  - Número de alternativas: {self.exam.exam_number_of_anwsers_question}")
            print(f"  - Feedback aos alunos: {self.exam.exam_student_feedback}")
        except Exam.DoesNotExist:
            print(f"✗ ERRO: Exame ID {exam_id} não existe no banco de dados.")
            self.exam = None
            return False
        
        print("=" * 80)
        return True
    
    def find_url_path(self):
        """
        Localiza dinamicamente a URL da função correctStudentsExam.
        
        Returns:
            str: URL completa para a view, ou None se não encontrada
        """
        from exam.views import correctStudentsExam
        
        resolver = get_resolver()
        
        def search_patterns(patterns, prefix=''):
            """Busca recursiva nos padrões de URL."""
            for pattern in patterns:
                # Padrão de URL com include (sub-URLs)
                if hasattr(pattern, 'url_patterns'):
                    current_prefix = prefix + str(pattern.pattern)
                    result = search_patterns(pattern.url_patterns, current_prefix)
                    if result:
                        return result
                # Padrão de URL simples
                else:
                    if hasattr(pattern, 'callback') and pattern.callback == correctStudentsExam:
                        full_path = prefix + str(pattern.pattern)
                        # Substitui placeholders pelo ID do exame
                        full_path = full_path.replace('<int:pk>', str(self.exam.pk))
                        full_path = full_path.replace('<pk>', str(self.exam.pk))
                        # Remove caracteres especiais de regex
                        full_path = full_path.lstrip('^').rstrip('$')
                        return full_path
            return None
        
        return search_patterns(resolver.url_patterns)
    
    def get_pdf_files(self, folder_path):
        """
        Busca todos os PDFs na pasta e subpastas.
        
        Args:
            folder_path (str): Caminho da pasta raiz
            
        Returns:
            list: Lista de caminhos absolutos dos PDFs encontrados
        """
        resolved_path = os.path.expanduser(folder_path)
        
        if not os.path.exists(resolved_path):
            print(f"✗ ERRO: Pasta não encontrada: {resolved_path}")
            return []
        
        # Busca recursiva por PDFs
        search_pattern = os.path.join(resolved_path, '**', '*.pdf')
        all_pdfs = glob.glob(search_pattern, recursive=True)
        
        # Filtra arquivos ocultos do macOS (._*) e outros temporários
        valid_pdfs = [
            f for f in all_pdfs
            if not os.path.basename(f).startswith('._')
            and not os.path.basename(f).startswith('~')
            and not '/.Trash/' in f
        ]
        
        return sorted(valid_pdfs)
    
    def wait_for_background_processes(self, timeout=3):
        """
        Aguarda processos em background (IRT) terminarem.
        
        Args:
            timeout (int): Tempo máximo de espera em segundos
        """
        print(f"\n⏳ Aguardando processos em background (timeout: {timeout}s)...")
        time.sleep(1)  # Aguarda inicial para processos iniciarem
        
        # Verifica se há processos Python rodando _irt_pymc3.py
        max_wait = timeout
        waited = 0
        
        while waited < max_wait:
            try:
                import subprocess
                result = subprocess.run(
                    ['pgrep', '-f', '_irt_pymc3.py'],
                    capture_output=True,
                    timeout=5
                )
                
                if result.returncode != 0:  # Nenhum processo encontrado
                    break
                
                time.sleep(1)
                waited += 2
                
            except Exception:
                break
        
        if waited >= max_wait:
            print(f"⚠ Timeout atingido após {timeout}s")
        else:
            print(f"✓ Processos finalizados (aguardou {waited}s)")
    
    def cleanup_temp_files(self, base_filename):
        """
        Remove arquivos temporários de forma segura.
        
        Args:
            base_filename (str): Nome base do arquivo (sem extensão)
        """
        try:
            base_dir = settings.BASE_DIR
            
            # Padrões de arquivos para remover
            patterns_to_remove = [
                os.path.join(base_dir, 'tmp', f'{base_filename}*.zip'),
                os.path.join(base_dir, 'pdfStudentEmail', f'studentEmail_e{self.exam.id}_r*.pdf'),
                os.path.join(base_dir, 'pdfStudentEmail', f'studentEmail_e{self.exam.id}_*_GAB.png'),
            ]
            
            for pattern in patterns_to_remove:
                for file_path in glob.glob(pattern):
                    try:
                        os.remove(file_path)
                    except FileNotFoundError:
                        pass  # Arquivo já não existe, tudo bem
                    except Exception as e:
                        print(f"  ⚠ Aviso ao remover {file_path}: {e}")
        
        except Exception as e:
            print(f"  ⚠ Erro durante limpeza: {e}")
    
    def move_zip_to_destination(self, pdf_path):
        """
        Move o ZIP gerado para a pasta do PDF original com timestamp.
        
        Args:
            pdf_path (str): Caminho do PDF original
            
        Returns:
            tuple: (success: bool, zip_path: str or None)
        """
        try:
            # Gera timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
            
            # Nome do arquivo sem extensão e sem espaços
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            base_name = base_name.replace(' ', '_')
            
            # Nome final do ZIP
            zip_final_name = f"{base_name}-{timestamp}.zip"
            zip_final_path = os.path.join(os.path.dirname(pdf_path), zip_final_name)
            
            # Caminho do ZIP gerado pelo sistema
            generated_zip = os.path.join(
                settings.BASE_DIR,
                'pdfStudentEmail',
                f'studentEmail_e{self.exam.id}.zip'
            )
            
            # Verifica se o ZIP foi gerado
            if not os.path.exists(generated_zip):
                print(f"  ⚠ ZIP não foi gerado: {generated_zip}")
                return False, None
            
            # Move (renomeia) o arquivo
            shutil.move(generated_zip, zip_final_path)
            
            # Verifica tamanho do arquivo
            zip_size_kb = os.path.getsize(zip_final_path) / 1024
            
            print(f"  ✓ ZIP criado: {os.path.basename(zip_final_path)} ({zip_size_kb:.1f} KB)")
            print(f"  📁 Localização: {zip_final_path}")
            
            return True, zip_final_path
            
        except Exception as e:
            print(f"  ✗ Erro ao mover ZIP: {e}")
            return False, None
    
    def process_single_pdf(self, pdf_path, url):
        """
        Processa um único arquivo PDF.
        
        Args:
            pdf_path (str): Caminho completo do PDF
            url (str): URL da view de correção
            
        Returns:
            bool: True se processamento foi bem-sucedido
        """
        print(f"\n{'─' * 80}")
        print(f"📄 Processando: {os.path.basename(pdf_path)}")
        print(f"   Caminho: {os.path.dirname(pdf_path)}")
        print(f"{'─' * 80}")
        
        self.processed_count += 1
        
        try:
            # Lê o arquivo PDF
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
            
            # Cria o arquivo uploadado
            uploaded_file = SimpleUploadedFile(
                name=os.path.basename(pdf_path),
                content=pdf_content,
                content_type='application/pdf'
            )
            
            # Faz a requisição POST
            print("  ⚙ Enviando requisição para o servidor Django...")
            response = self.client.post(url, {
                'myfilePDF': uploaded_file,
                'choiceReturnQuestions': 'yes'
            }, follow=True)
            
            # Verifica status HTTP
            if response.status_code != 200:
                print(f"  ✗ ERRO HTTP: Status {response.status_code}")
                
                # Tenta extrair mensagens de erro do Django
                if hasattr(response, 'context') and response.context:
                    messages = response.context.get('messages', [])
                    for msg in messages:
                        print(f"     Django: {msg}")
                
                self.error_count += 1
                return False
            
            print("  ✓ Requisição processada com sucesso")
            
            # Aguarda processos em background
            # IMPORTANTE: Espera antes de limpar arquivos
            self.wait_for_background_processes(timeout=3)
            
            # Move o ZIP para destino final
            success, zip_path = self.move_zip_to_destination(pdf_path)
            
            if success:
                self.success_count += 1
                
                # Limpeza de arquivos temporários
                base_filename = f"_e{self.exam.id}_{self.user.email}_{os.path.splitext(os.path.basename(pdf_path))[0].replace(' ', '')}"
                self.cleanup_temp_files(base_filename)
                
                return True
            else:
                print("  ⚠ Processamento concluído mas ZIP não encontrado")
                self.error_count += 1
                return False
        
        except FileNotFoundError:
            print(f"  ✗ ERRO: Arquivo não encontrado: {pdf_path}")
            self.error_count += 1
            return False
        
        except Exception as e:
            print(f"  ✗ ERRO durante processamento: {e}")
            import traceback
            traceback.print_exc()
            self.error_count += 1
            return False
    
    def print_summary(self):
        """Imprime resumo final do processamento."""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        print("\n" + "=" * 80)
        print("RESUMO DO PROCESSAMENTO")
        print("=" * 80)
        print(f"Total de PDFs processados: {self.processed_count}")
        print(f"  ✓ Sucessos: {self.success_count}")
        print(f"  ✗ Erros: {self.error_count}")
        print(f"⏱ Tempo total: {elapsed_time:.1f}s")
        
        if self.success_count > 0:
            avg_time = elapsed_time / self.success_count
            print(f"  ⌀ Tempo médio por PDF: {avg_time:.1f}s")
        
        print("=" * 80)
    
    def run_correction_on_folder(self, folder_path, without_headers=False):
        """
        Executa correção em todos os PDFs de uma pasta.
        
        Args:
            folder_path (str): Caminho da pasta contendo PDFs
            without_headers (bool): Se True, PDFs sem enunciados (gabarito na 1ª página)
            
        Returns:
            bool: True se pelo menos um PDF foi processado com sucesso
        """
        if not self.exam:
            print("✗ ERRO: Exame não configurado. Execute setUp() primeiro.")
            return False
        
        # Inicia contagem de tempo
        self.start_time = time.time()
        
        # Localiza a URL da view
        url = self.find_url_path()
        if not url:
            print("✗ ERRO CRÍTICO: Não foi possível localizar 'correctStudentsExam' no urls.py")
            print("  Verifique se a view está registrada corretamente.")
            return False
        
        # Garante que URL comece com /
        if not url.startswith('/'):
            url = '/' + url
        
        print(f"\n🔗 URL detectada: {url}")
        
        if without_headers:
            print("📋 Modo: SEM enunciados (gabarito na 1ª página)")
        else:
            print("📋 Modo: COM enunciados")
        
        # Busca PDFs
        pdf_files = self.get_pdf_files(folder_path)
        
        if not pdf_files:
            print(f"\n✗ ERRO: Nenhum arquivo PDF encontrado em: {folder_path}")
            return False
        
        print(f"\n📊 Total de PDFs encontrados: {len(pdf_files)}")
        
        # Lista os PDFs
        print("\nArquivos a processar:")
        for i, pdf in enumerate(pdf_files, 1):
            print(f"  {i}. {os.path.basename(pdf)}")
        
        # Processa cada PDF
        for pdf_path in pdf_files:
            self.process_single_pdf(pdf_path, url)
        
        # Imprime resumo
        self.print_summary()
        
        return self.success_count > 0


# Função auxiliar para uso standalone
def run_standalone(folder_path, exam_id, user_email=None, user_password=None, without_headers=False):
    """
    Executa o test suite standalone (fora do shell do Django).
    
    Args:
        folder_path (str): Caminho da pasta com PDFs
        exam_id (int): ID do exame
        user_email (str): Email do usuário para autenticação
        user_password (str): Senha do usuário
        without_headers (bool): Se True, PDFs sem enunciados
    """
    import django
    django.setup()
    
    suite = CorrectionTestSuite()
    
    if not suite.setUp(user_email=user_email, user_password=user_password, exam_id=exam_id):
        print("\n✗ Falha na configuração. Abortando.")
        sys.exit(1)
    
    success = suite.run_correction_on_folder(folder_path, without_headers=without_headers)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    """Permite execução direta do script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test Suite de Correção de Exames - MCTest'
    )
    parser.add_argument('folder', help='Pasta contendo os PDFs')
    parser.add_argument('exam_id', type=int, help='ID do exame no banco de dados')
    parser.add_argument('--email', default=None,
                       help='Email do usuário para autenticação')
    parser.add_argument('--password', default=None,
                       help='Senha do usuário')
    parser.add_argument('--sem-enunciados', action='store_true',
                       help='PDFs sem enunciados (gabarito na 1ª página)')
    
    args = parser.parse_args()
    
    run_standalone(
        folder_path=args.folder,
        exam_id=args.exam_id,
        user_email=args.email,
        user_password=args.password,
        without_headers=args.sem_enunciados
    )
