# 📘 Test Suite - Correção de Exames MCTest

Sistema automatizado para processar múltiplos PDFs de exames em lote, gerando ZIPs com resultados, estatísticas e feedback individualizado.

---

## 📋 Índice

- [Instalação](#-instalação)
- [Uso Básico](#-uso-básico)
- [Parâmetros](#-parâmetros)
- [Exemplos](#-exemplos)
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.6+
- Django (projeto MCTest configurado)
- Ambiente virtual em `../AmbientePython3/`
- Banco de dados com exames cadastrados

### Passo 1: Copiar Arquivos

Coloque os arquivos na **raiz do projeto Django** (onde está o `manage.py`):

```bash
cd ~/PycharmProjects/mctest  # Ajuste conforme seu caminho

# Copie os arquivos
cp /caminho/dos/arquivos/tests_correction.py exam/
cp /caminho/dos/arquivos/run_testsuite.sh ./

# Torne o script bash executável
chmod +x run_testsuite.sh
```

### Passo 2: Verificar Estrutura

Sua estrutura deve ficar assim:

```
mctest/                          ← Raiz do projeto
├── manage.py                    ← Deve estar aqui!
├── run_testsuite.sh             ← Script bash
├── mctest/                      ← Configurações Django
│   ├── settings.py
│   └── urls.py
└── exam/
    ├── views.py                 ← Contém correctStudentsExam
    ├── tests_correction.py      ← Test suite Python
    └── models.py
```

### Passo 3: Testar

```bash
# Teste com um PDF
./run_testsuite.sh ~/Downloads/teste_pdf false seu@email.com senha 810

# Se funcionar, está pronto! ✓
```

---

## 💡 Uso Básico

### Sintaxe Completa

```bash
./run_testsuite.sh <pasta_pdfs> <sem_enunciados> <email> <senha> <exam_id>
```

### Exemplo Real

```bash
./run_testsuite.sh \
    ~/Downloads/EP2026/teste \
    true \
    fzampirolli@ufabc.edu.br \
    minhaSenha123 \
    810
```

---

## 📝 Parâmetros

| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| **pasta_pdfs** | String | Pasta contendo PDFs (aceita `~` e caminhos com espaços) | `~/Downloads/Provas` |
| **sem_enunciados** | Boolean | `true` = sem enunciados<br>`false` = com enunciados | `true` |
| **email** | String | Email/login do usuário | `professor@escola.com` |
| **senha** | String | Senha do usuário | `minhasenha123` |
| **exam_id** | Integer | ID do exame no banco | `810` |

### Modos de Operação

#### Modo COM enunciados (`false`)
- Cada página PDF contém: QR Code + Questões + Respostas
- Gabarito está no banco de dados ou na primeira página do PDF (detalhes abaixo)
- Usado para provas completas digitalizadas

#### Modo SEM enunciados (`true`)
- **1ª página**: Gabarito (folha de respostas do professor)
- **Demais páginas**: Respostas dos alunos
- Todas as páginas devem ter QR Code
- Usado para folhas de resposta separadas

---

## 🎯 Exemplos

### Exemplo 1: Processar Turma (Sem Enunciados)

```bash
./run_testsuite.sh \
    ~/Downloads/EP2026/teste \
    true \
    fzampirolli@ufabc.edu.br \
    minhaSenha123 \
    810
```

**Resultado:**
```
✓ Encontrados 2 arquivo(s) PDF
✓ ZIP criado: 002_gabarito-20260216-0801.zip (1.9 KB)
✓ ZIP criado: 004_gabarito-20260216-0801.zip (1.9 KB)
```

---

### Exemplo 2: Processar Turma (Com Enunciados)

```bash
./run_testsuite.sh \
    ~/Downloads/Provas/TurmaA \
    false \
    professor@escola.com \
    senha123 \
    25
```

---

### Exemplo 3: Múltiplas Turmas em Sequência

Crie um script `processar_todas_turmas.sh`:

```bash
#!/bin/bash

EMAIL="fzampirolli@ufabc.edu.br"
SENHA="minhaSenha123"
EXAM_ID=810
BASE_DIR=~/Downloads/EP2026

echo "Processando todas as turmas..."

# Turma 002
./run_testsuite.sh "$BASE_DIR/002" true $EMAIL $SENHA $EXAM_ID

# Turma 004
./run_testsuite.sh "$BASE_DIR/004" true $EMAIL $SENHA $EXAM_ID

# Turma 006
./run_testsuite.sh "$BASE_DIR/006" true $EMAIL $SENHA $EXAM_ID

echo "✓ Todas as turmas processadas!"
```

Execute:
```bash
chmod +x processar_todas_turmas.sh
./processar_todas_turmas.sh
```

---

### Exemplo 4: Caminhos com Espaços

```bash
# Funciona com caminhos contendo espaços
./run_testsuite.sh \
    "/Users/fz/Library/CloudStorage/GoogleDrive-user@gmail.com/Meu Drive/Provas/Turma A" \
    true \
    user@email.com \
    senha \
    810
```

---

## 📦 Estrutura de Arquivos

### Entrada (Antes)

```
~/Downloads/EP2026/teste/
├── 002 avaliação/
│   └── 002 gabarito.pdf       ← Entrada
└── 004 avaliação/
    └── 004 gabarito.pdf       ← Entrada
```

### Saída (Depois)

```
~/Downloads/EP2026/teste/
├── 002 avaliação/
│   ├── 002 gabarito.pdf
│   └── 002_gabarito-20260216-0801.zip   ← Gerado ✓
└── 004 avaliação/
    ├── 004 gabarito.pdf
    └── 004_gabarito-20260216-0801.zip   ← Gerado ✓
```

### Conteúdo do ZIP

Cada ZIP contém:

```
002_gabarito-20260216-0801.zip
├── _RETURN_email_log.csv          ← Relatório detalhado
├── _RETURN__.csv                  ← Respostas e notas
├── _RETURN_statistics.csv         ← Estatísticas por questão
├── _RETURN_irt.csv                ← Dados IRT
└── studentEmail_*.pdf             ← PDFs individuais (se habilitado)
```

#### Descrição dos Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `_RETURN_email_log.csv` | Log completo: página, aluno, nota, status de envio |
| `_RETURN__.csv` | Planilha com todas as respostas e notas calculadas |
| `_RETURN_statistics.csv` | Estatísticas: acertos, erros, % por questão |
| `_RETURN_irt.csv` | Dados para análise IRT (Item Response Theory) |
| `studentEmail_*.pdf` | Feedback visual individual (se `exam_student_feedback='yes'`) |

---

## 🖥️ Saída do Programa

### Saída Completa (Exemplo)

```bash
$ ./run_testsuite.sh ~/Downloads/EP2026/teste true fzampirolli@ufabc.edu.br minhaSenha123 810

================================================================================================
TEST SUITE - CORREÇÃO DE EXAMES EM LOTE
================================================================================================

Configuração:
  📁 Pasta de PDFs: /Users/fz/Downloads/EP2026/teste
  📋 Modo: SEM enunciados (gabarito na 1ª página)
  👤 Email/Login: fzampirolli@ufabc.edu.br
  🔢 Exame ID: 810

✓ Projeto Django encontrado: /Users/fz/PycharmProjects/mctest
✓ Ambiente virtual encontrado
✓ Encontrados 2 arquivo(s) PDF

ℹ Ativando ambiente virtual...
✓ Ambiente virtual ativado

ℹ Detectando configurações do Django...
✓ Settings detectado: mctest.settings

================================================================================================
INICIANDO PROCESSAMENTO
================================================================================================

================================================================================
CONFIGURAÇÃO DO TEST SUITE
================================================================================
✓ Usuário encontrado: fzampirolli@ufabc.edu.br
⚠ Falha no login com senha, usando force_login
✓ Exame encontrado: ESTUDANTES 2026 (ID: 810)
  - Tipo de impressão: answ
  - Número de alternativas: 5
  - Feedback aos alunos: no
================================================================================

🔗 URL detectada: /exam/exam/810/correct/
📋 Modo: SEM enunciados (gabarito na 1ª página)

📊 Total de PDFs encontrados: 2

Arquivos a processar:
  1. 002 gabarito.pdf
  2. 004 gabarito.pdf

────────────────────────────────────────────────────────────────────────────────
📄 Processando: 002 gabarito.pdf
   Caminho: /Users/fz/Downloads/EP2026/teste/002 avaliação
────────────────────────────────────────────────────────────────────────────────
  ⚙ Enviando requisição para o servidor Django...
  ✓ Requisição processada com sucesso

⏳ Aguardando processos em background (timeout: 3s)...
✓ Processos finalizados (aguardou 2s)
  ✓ ZIP criado: 002_gabarito-20260216-0801.zip (1.9 KB)
  📁 Localização: /Users/fz/Downloads/EP2026/teste/002 avaliação/002_gabarito-20260216-0801.zip

────────────────────────────────────────────────────────────────────────────────
📄 Processando: 004 gabarito.pdf
   Caminho: /Users/fz/Downloads/EP2026/teste/004 avaliação
────────────────────────────────────────────────────────────────────────────────
  ⚙ Enviando requisição para o servidor Django...
  ✓ Requisição processada com sucesso

⏳ Aguardando processos em background (timeout: 3s)...
✓ Processos finalizados (aguardou 1s)
  ✓ ZIP criado: 004_gabarito-20260216-0802.zip (1.9 KB)
  📁 Localização: /Users/fz/Downloads/EP2026/teste/004 avaliação/004_gabarito-20260216-0802.zip

================================================================================
RESUMO DO PROCESSAMENTO
================================================================================
Total de PDFs processados: 2
  ✓ Sucessos: 2
  ✗ Erros: 0
⏱ Tempo total: 27.2s
  ⌀ Tempo médio por PDF: 13.6s
================================================================================

================================================================================================
PROCESSAMENTO FINALIZADO
================================================================================================

✓ Test suite concluído com sucesso!

Os ZIPs gerados estão na mesma pasta dos PDFs originais.
Formato: <nome_pdf>-YYYYMMDD-HHMM.zip

Para verificar:
  find "/Users/fz/Downloads/EP2026/teste" -name "*.zip" -mmin -60
```

---

## 🔧 Troubleshooting

### Problema 1: "manage.py não encontrado"

**Erro:**
```
✗ manage.py não encontrado no diretório do script
```

**Solução:**
```bash
# O script DEVE estar na raiz do projeto Django
cd ~/PycharmProjects/mctest  # Onde está o manage.py
ls manage.py                  # Verifica se está lá

# Copie o script para este diretório
cp /caminho/do/run_testsuite.sh ./
./run_testsuite.sh ...
```

---

### Problema 2: "Ambiente virtual não encontrado"

**Erro:**
```
✗ Ambiente virtual não encontrado: ../AmbientePython3/bin/activate
```

**Solução:**
```bash
# Crie o ambiente virtual
cd ~/PycharmProjects
python3 -m venv AmbientePython3

# Instale dependências
source AmbientePython3/bin/activate
pip install django PyPDF2 pdf2image opencv-python pandas numpy
```

---

### Problema 3: "Nenhum arquivo PDF encontrado"

**Erro:**
```
⚠ Nenhum arquivo PDF encontrado em: /caminho/pasta
```

**Solução:**
```bash
# Verifique se a pasta existe
ls -la ~/Downloads/EP2026/teste

# Verifique se há PDFs
find ~/Downloads/EP2026/teste -name "*.pdf"

# Use o caminho absoluto se necessário
./run_testsuite.sh \
    "/Users/fz/Downloads/EP2026/teste" \
    true email senha 810
```

---

### Problema 4: "Usuário não encontrado"

**Erro:**
```
✗ ERRO: Usuário com email 'user@example.com' não encontrado.
```

**Solução:**
```bash
# Verifique se o usuário existe
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(email='fzampirolli@ufabc.edu.br').exists()

# O script usa superusuário como fallback automaticamente
# Mas certifique-se de que o email está correto
```

---

### Problema 5: "Exame não existe"

**Erro:**
```
✗ ERRO: Exame ID 810 não existe no banco de dados.
```

**Solução:**
```bash
# Liste os exames disponíveis
python manage.py shell
>>> from exam.models import Exam
>>> for e in Exam.objects.all():
...     print(f"ID: {e.id}, Nome: {e.exam_name}")

# Use o ID correto
./run_testsuite.sh ... 810  # ← ID válido
```

---

### Problema 6: "Senha com caracteres especiais"

Se sua senha tem caracteres como `$`, `!`, `"`, use aspas simples:

```bash
# ✗ ERRADO
./run_testsuite.sh ... user@email.com Senh@$123! 810

# ✓ CORRETO
./run_testsuite.sh ... user@email.com 'Senh@$123!' 810
```

---

## ❓ FAQ

### P: O script processa subpastas automaticamente?
**R:** Sim! O script busca recursivamente todos os PDFs em subpastas.

### P: Posso interromper o processamento?
**R:** Sim, pressione `Ctrl+C`. Os PDFs já processados terão seus ZIPs gerados.

### P: Como processar apenas 1 PDF de teste?
**R:** Crie uma pasta temporária com apenas esse PDF:
```bash
mkdir ~/teste_individual
cp ~/Downloads/prova.pdf ~/teste_individual/
./run_testsuite.sh ~/teste_individual false email senha 810
```

### P: Onde ficam os ZIPs?
**R:** Na **mesma pasta** do PDF original, com formato: `<nome>-YYYYMMDD-HHMM.zip`

### P: O que fazer se der "Falha no login com senha"?
**R:** Não é um erro! O script usa `force_login` automaticamente. Isso acontece quando:
- Senha está incorreta (mas funciona mesmo assim)
- Configuração de autenticação customizada

### P: Como processar múltiplos exames diferentes?
**R:** Execute o script várias vezes com IDs diferentes:
```bash
./run_testsuite.sh ~/Provas/Turma1 false email senha 100
./run_testsuite.sh ~/Provas/Turma2 false email senha 200
./run_testsuite.sh ~/Provas/Turma3 false email senha 300
```

### P: PDFs precisam ter nomes específicos?
**R:** Não! Qualquer nome de arquivo `.pdf` funciona. Evite apenas:
- Começar com `._` (arquivos ocultos macOS)
- Começar com `~` (temporários)

### P: Quanto tempo demora?
**R:** Aproximadamente **10-15 segundos por PDF**, dependendo de:
- Número de páginas
- Quantidade de questões
- Velocidade do processador

---

## 📊 Recursos Avançados

### Uso Programático (Python)

```python
from exam.tests_correction import CorrectionTestSuite

# Cria instância
suite = CorrectionTestSuite()

# Configura
suite.setUp(
    user_email='professor@escola.com',
    user_password='senha123',
    exam_id=810
)

# Executa
suite.run_correction_on_folder(
    folder_path='~/Downloads/Provas',
    without_headers=True  # False para com enunciados
)
```

### Execução Standalone (sem script bash)

```bash
python exam/tests_correction.py \
    ~/Downloads/Provas \
    810 \
    --email professor@escola.com \
    --password senha123 \
    --sem-enunciados
```

---

## 🎨 Características Técnicas

### Funcionalidades

- ✅ Detecção automática de projeto Django (`mctest` ou `mcstest`)
- ✅ Busca recursiva de PDFs em subpastas
- ✅ Filtragem de arquivos ocultos e temporários (macOS)
- ✅ Autenticação com fallback automático
- ✅ ZIPs com timestamp único
- ✅ Aguarda processos IRT em background
- ✅ Limpeza automática de temporários
- ✅ Logging colorido e detalhado
- ✅ Relatórios de estatísticas
- ✅ Tratamento robusto de erros

### Compatibilidade

- **Sistemas:** macOS, Linux
- **Python:** 3.6+
- **Django:** 2.x, 3.x, 4.x
- **Ambiente:** Ambiente virtual recomendado

---

## 📚 Documentação Adicional

- **PATCH_SUPRIMIR_ERROS.md** - Como eliminar mensagens de `rm` e IRT
- **TROUBLESHOOTING_MODULE_ERROR.md** - Resolver `ModuleNotFoundError`
- **GUIA_USO_COM_LOGIN.md** - Guia detalhado de autenticação

---

## 🆘 Suporte

Em caso de problemas:

1. Verifique se está na raiz do projeto (`ls manage.py`)
2. Verifique se o ambiente virtual existe
3. Teste com apenas 1 PDF primeiro
4. Consulte a seção [Troubleshooting](#-troubleshooting)
5. Execute `python manage.py check` para validar Django

---

## 📝 Changelog

### Versão 2.1 (2024-02-16)
- ✅ Autenticação com email e senha
- ✅ Detecção automática de projeto Django
- ✅ Aguarda processos IRT antes de limpar
- ✅ Timeout reduzido para 3s (mais rápido)
- ✅ Suporte a caminhos com espaços
- ✅ Logging aprimorado

### Versão 2.0 (2026-02-15)
- ✅ Primeira versão do test suite automatizado

---

**Última atualização:** 2026-02-16  
**Versão:** 2.1  
