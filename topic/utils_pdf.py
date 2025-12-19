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
import os
import subprocess
import shutil
import uuid
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class PDFGenerator:
    def __init__(self):
        # Define caminhos base
        self.base_path = str(settings.BASE_DIR)
        self.tmp_path = os.path.join(self.base_path, 'tmp')

        # Garante que a pasta tmp existe
        os.makedirs(self.tmp_path, exist_ok=True)

        # Resolve o comando do pdflatex na inicialização
        self.pdflatex_cmd = self._get_pdflatex_path()

    def _get_pdflatex_path(self):
        """
        Tenta localizar o binário do pdflatex de forma portável entre SOs.
        """
        # 1. Verifica se foi definido manualmente no settings.py (Override opcional)
        if hasattr(settings, 'LATEX_COMPILER_PATH') and settings.LATEX_COMPILER_PATH:
            return settings.LATEX_COMPILER_PATH

        # 2. Tenta encontrar no PATH do sistema (Funciona em Win/Mac/Linux)
        path_from_env = shutil.which('pdflatex')
        if path_from_env:
            return path_from_env

        # 3. Fallback: Caminhos comuns que IDEs às vezes escondem do PATH
        common_paths = [
            '/Library/TeX/texbin/pdflatex',   # macOS (MacTeX)
            '/usr/local/bin/pdflatex',        # Linux/macOS
            '/usr/bin/pdflatex',              # Linux (Debian/Ubuntu)
            '/opt/homebrew/bin/pdflatex',     # macOS (Homebrew Silicon)
            # r'C:\texlive\2023\bin\windows\pdflatex.exe' # Exemplo Windows
        ]

        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path

        # 4. Desiste e retorna apenas o comando (vai falhar no subprocess se não estiver no path)
        return 'pdflatex'

    def generate(self, latex_content, filename_base, destination_folder_name):
        """
        Gera um PDF a partir de uma string LaTeX de forma thread-safe.

        :param latex_content: O conteúdo do arquivo .tex (string)
        :param filename_base: O nome FINAL do arquivo sem extensão (ex: 'fzampirolli')
        :param destination_folder_name: Nome da pasta de destino (ex: 'pdfQuestion', 'pdfExam')
        :return: Caminho completo do PDF final ou None em caso de erro.
        """

        # Configurar caminhos de destino
        pdf_dest_path = os.path.join(self.base_path, destination_folder_name)
        os.makedirs(pdf_dest_path, exist_ok=True)

        # --- ISOLAMENTO DE CONCORRÊNCIA ---
        # Gera um ID único para ESTA execução específica.
        unique_id = str(uuid.uuid4())
        compilation_filename = f"compilation_{unique_id}"

        # Caminhos dos arquivos temporários (únicos para este processo)
        full_tex_path = os.path.join(self.tmp_path, f"{compilation_filename}.tex")
        full_pdf_tmp_path = os.path.join(self.tmp_path, f"{compilation_filename}.pdf")

        # Caminho final (onde o arquivo será salvo com o nome desejado)
        final_pdf_path = os.path.join(pdf_dest_path, f"{filename_base}.pdf")

        # 1. Escrever o arquivo .tex temporário
        try:
            with open(full_tex_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
        except IOError as e:
            print(_(f"Error writing temporary .tex file: {e}"))
            return None

        # 2. Compilar usando o comando resolvido
        cmd = [
            self.pdflatex_cmd,
            '--shell-escape',
            '-interaction', 'nonstopmode',
            '-output-directory', self.tmp_path,
            full_tex_path
        ]

        try:
            # Executa duas vezes para garantir referências cruzadas
            subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Verifica se o PDF foi criado
            if not os.path.exists(full_pdf_tmp_path):
                # Decodifica o log de erro para debug
                log_output = proc.stdout.decode('utf-8', errors='ignore')[-800:]
                print(_(f"Error in LaTeX Log (Cmd: {self.pdflatex_cmd}):\n{log_output}"))
                self._cleanup(compilation_filename)
                return None

        except Exception as e:
            print(_(f"Subprocess exception: {e}"))
            self._cleanup(compilation_filename)
            return None

        # 3. Mover para o destino final
        try:
            if os.path.exists(final_pdf_path):
                os.remove(final_pdf_path) # Garante que sobrescreve o antigo

            # Move o arquivo temporário único para o nome final legível
            shutil.move(full_pdf_tmp_path, final_pdf_path)

        except OSError as e:
            print(_(f"Error moving file to final destination: {e}"))
            self._cleanup(compilation_filename)
            return None

        # 4. Limpeza dos arquivos temporários desta compilação
        self._cleanup(compilation_filename)

        return final_pdf_path

    def _cleanup(self, filename_base):
        """Remove arquivos temporários gerados pelo LaTeX para esta compilação específica"""
        extensions = ['.aux', '.log', '.tex', '.out']
        for ext in extensions:
            file_to_remove = os.path.join(self.tmp_path, filename_base + ext)
            if os.path.exists(file_to_remove):
                try:
                    os.remove(file_to_remove)
                except OSError:
                    pass