#!/bin/bash
# ==============================================================================
# Test Suite Runner - MCTest (Versão Final)
# ==============================================================================
# Script robusto para executar testes de correção de exames em lote.
# Detecta automaticamente o projeto Django e suas configurações.
#
# Uso:
#   ./run_testsuite.sh <pasta_pdfs> <sem_enunciados> <email> <senha> <exam_id>
#
# Parâmetros:
#   pasta_pdfs      : Caminho da pasta contendo PDFs (pode usar ~)
#   sem_enunciados  : true/false (se PDFs não têm enunciados)
#   email           : Email/login do usuário para autenticação
#   senha           : Senha do usuário
#   exam_id         : ID do exame no banco de dados
#
# Exemplo:
#   ./run_testsuite.sh /Users/fz/Library/CloudStorage/GoogleDrive-fzampirolli@gmail.com/Meu\ Drive/___EPUFABC/EP2026/teste true fzampirolli@ufabc.edu.br senha123 810
# ==============================================================================

set -e  # Para em caso de erro (exceto quando esperado)

# ==============================================================================
# CONFIGURAÇÕES E CORES
# ==============================================================================

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color
readonly BOLD='\033[1m'

# Diretórios
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly VENV_PATH="${SCRIPT_DIR}/../AmbientePython3/bin/activate"

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

print_header() {
    echo -e "\n${BLUE}${BOLD}================================================================================================${NC}"
    echo -e "${BLUE}${BOLD}$1${NC}"
    echo -e "${BLUE}${BOLD}================================================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

show_help() {
    cat << EOF
Uso: $0 <pasta_pdfs> <sem_enunciados> <email> <senha> <exam_id>

Parâmetros:
  pasta_pdfs      Caminho da pasta contendo PDFs (aceita ~ e caminhos relativos)
  sem_enunciados  true/false - indica se PDFs não contêm enunciados
  email           Email/login do usuário para autenticação
  senha           Senha do usuário
  exam_id         ID do exame no banco de dados

Exemplos:
  # PDFs com enunciados
  $0 ~/Downloads/provas false user@example.com senha123 810

  # PDFs sem enunciados (gabarito na 1ª página)
  $0 ~/Downloads/provas true fzampirolli@ufabc.edu.br DmgsRsln68 810

Notas:
  - O script ativa automaticamente o ambiente virtual
  - PDFs são processados recursivamente (incluindo subpastas)
  - ZIPs são salvos na mesma pasta do PDF original
  - Formato do ZIP: nome-YYYYMMDD-HHMM.zip
  - O script deve estar na raiz do projeto Django

EOF
    exit 0
}

# ==============================================================================
# VALIDAÇÃO DE PARÂMETROS
# ==============================================================================

# Verifica help
if [ "$1" = "-h" ] || [ "$1" = "--help" ] || [ $# -eq 0 ]; then
    show_help
fi

# Verifica número de argumentos
if [ $# -lt 5 ]; then
    print_error "Número insuficiente de argumentos"
    echo ""
    echo "Uso: $0 <pasta_pdfs> <sem_enunciados> <email> <senha> <exam_id>"
    echo "Execute '$0 --help' para mais informações"
    exit 1
fi

# Captura parâmetros
SUBFOLDER="$1"
WITHOUT_HEADERS_STR="$2"
USER_EMAIL="$3"
DB_PASSWORD="$4"
EXAM_ID="$5"

# Valida pasta
RESOLVED_SUBFOLDER=$(eval echo "$SUBFOLDER")  # Expande ~ e variáveis
if [ ! -d "$RESOLVED_SUBFOLDER" ]; then
    print_error "Pasta não encontrada: $RESOLVED_SUBFOLDER"
    exit 1
fi

# Valida exam_id
if ! [[ "$EXAM_ID" =~ ^[0-9]+$ ]]; then
    print_error "ID do exame deve ser um número: $EXAM_ID"
    exit 1
fi

# Valida email
if [[ ! "$USER_EMAIL" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
    print_warning "Email pode estar em formato inválido: $USER_EMAIL"
    echo "  Continuando mesmo assim..."
fi

# Converte string para booleano Python
WITHOUT_HEADERS_STR=$(echo "$WITHOUT_HEADERS_STR" | tr '[:upper:]' '[:lower:]')
if [[ "$WITHOUT_HEADERS_STR" == "true" || "$WITHOUT_HEADERS_STR" == "1" || "$WITHOUT_HEADERS_STR" == "yes" ]]; then
    WITHOUT_VAL="True"
    MODE_LABEL="SEM enunciados (gabarito na 1ª página)"
else
    WITHOUT_VAL="False"
    MODE_LABEL="COM enunciados"
fi

# ==============================================================================
# VERIFICAÇÕES PRÉ-EXECUÇÃO
# ==============================================================================

print_header "TEST SUITE - CORREÇÃO DE EXAMES EM LOTE"

echo -e "${BOLD}Configuração:${NC}"
echo "  📁 Pasta de PDFs: $RESOLVED_SUBFOLDER"
echo "  📋 Modo: $MODE_LABEL"
echo "  👤 Email/Login: $USER_EMAIL"
echo "  🔢 Exame ID: $EXAM_ID"
echo ""

# Verifica se está na raiz do projeto Django
if [ ! -f "$SCRIPT_DIR/manage.py" ]; then
    print_error "manage.py não encontrado no diretório do script"
    echo ""
    echo "O script deve estar na raiz do projeto Django, onde está o manage.py"
    echo "Diretório do script: $SCRIPT_DIR"
    echo ""
    echo "Mova o script para a raiz do projeto ou execute de lá:"
    echo "  cd /caminho/do/projeto"
    echo "  ./run_testsuite.sh ..."
    exit 1
fi

print_success "Projeto Django encontrado: $SCRIPT_DIR"

# Verifica ambiente virtual
if [ ! -f "$VENV_PATH" ]; then
    print_error "Ambiente virtual não encontrado: $VENV_PATH"
    echo ""
    echo "Crie o ambiente virtual:"
    echo "  python3 -m venv ../AmbientePython3"
    exit 1
fi

print_success "Ambiente virtual encontrado"

# Conta PDFs
PDF_COUNT=$(find "$RESOLVED_SUBFOLDER" -type f -name "*.pdf" ! -name "._*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PDF_COUNT" -eq 0 ]; then
    print_warning "Nenhum arquivo PDF encontrado em: $RESOLVED_SUBFOLDER"
    echo ""
    echo "Verifique se:"
    echo "  - O caminho está correto"
    echo "  - Há arquivos .pdf na pasta ou subpastas"
    exit 1
fi

print_success "Encontrados $PDF_COUNT arquivo(s) PDF"

# ==============================================================================
# ATIVAÇÃO DO AMBIENTE VIRTUAL
# ==============================================================================

echo ""
print_info "Ativando ambiente virtual..."

source "$VENV_PATH"

if [ $? -ne 0 ]; then
    print_error "Falha ao ativar ambiente virtual"
    exit 1
fi

print_success "Ambiente virtual ativado"

# ==============================================================================
# DETECÇÃO AUTOMÁTICA DO MÓDULO SETTINGS
# ==============================================================================

echo ""
print_info "Detectando configurações do Django..."

# Procura pelo diretório de settings
SETTINGS_MODULE=""
for dir in "$SCRIPT_DIR"/*/ ; do
    if [ -f "${dir}settings.py" ] || [ -f "${dir}settings/__init__.py" ]; then
        SETTINGS_MODULE=$(basename "$dir")
        break
    fi
done

if [ -z "$SETTINGS_MODULE" ]; then
    # Fallback: tenta nomes comuns
    for name in mctest mcstest myproject config; do
        if [ -d "$SCRIPT_DIR/$name" ] && ([ -f "$SCRIPT_DIR/$name/settings.py" ] || [ -f "$SCRIPT_DIR/$name/settings/__init__.py" ]); then
            SETTINGS_MODULE="$name"
            break
        fi
    done
fi

if [ -z "$SETTINGS_MODULE" ]; then
    print_error "Não foi possível detectar o módulo de settings do Django"
    echo ""
    echo "Procurados em: $SCRIPT_DIR"
    echo "Estrutura esperada: <projeto>/settings.py ou <projeto>/settings/__init__.py"
    exit 1
fi

print_success "Settings detectado: ${SETTINGS_MODULE}.settings"

# ==============================================================================
# EXECUÇÃO DO TEST SUITE
# ==============================================================================

echo ""
print_header "INICIANDO PROCESSAMENTO"

# Executa Python diretamente (sem script temporário)
python << EOF
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

# Adiciona o diretório do projeto ao path
project_dir = '${SCRIPT_DIR}'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Configura Django com o módulo detectado
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '${SETTINGS_MODULE}.settings')

try:
    django.setup()
except Exception as e:
    print(f"✗ ERRO ao configurar Django: {e}")
    print(f"  Settings module: ${SETTINGS_MODULE}.settings")
    print(f"  Project dir: ${SCRIPT_DIR}")
    sys.exit(1)

# Importa e executa o test suite
try:
    from exam.tests_correction import CorrectionTestSuite
except ImportError as e:
    print(f"✗ ERRO ao importar CorrectionTestSuite: {e}")
    print(f"  Verifique se o módulo exam.tests_correction existe")
    sys.exit(1)

# Cria e configura o suite
suite = CorrectionTestSuite()

# Setup com os parâmetros
if not suite.setUp(
    user_email='${USER_EMAIL}',
    user_password='${DB_PASSWORD}',
    exam_id=${EXAM_ID}
):
    print("\n✗ Falha na configuração do test suite")
    sys.exit(1)

# Executa correção na pasta
success = suite.run_correction_on_folder(
    folder_path='${RESOLVED_SUBFOLDER}',
    without_headers=${WITHOUT_VAL}
)

# Retorna código de saída
sys.exit(0 if success else 1)
EOF

EXIT_CODE=$?

# ==============================================================================
# DESATIVAÇÃO E FINALIZAÇÃO
# ==============================================================================

echo ""
deactivate 2>/dev/null || true

# ==============================================================================
# MENSAGEM FINAL
# ==============================================================================

echo ""
print_header "PROCESSAMENTO FINALIZADO"

if [ $EXIT_CODE -eq 0 ]; then
    print_success "Test suite concluído com sucesso!"
    echo ""
    echo "Os ZIPs gerados estão na mesma pasta dos PDFs originais."
    echo "Formato: <nome_pdf>-YYYYMMDD-HHMM.zip"
    echo ""
    echo "Para verificar:"
    echo "  find \"$RESOLVED_SUBFOLDER\" -name \"*.zip\" -mmin -60"
else
    print_error "Test suite terminou com erros (código: $EXIT_CODE)"
    echo ""
    echo "Verifique:"
    echo "  - Se o exame ID $EXAM_ID existe no banco"
    echo "  - Se os PDFs têm formato válido"
    echo "  - Se o usuário $USER_EMAIL existe"
    echo "  - Logs do Django para mais detalhes"
fi

echo ""

exit $EXIT_CODE