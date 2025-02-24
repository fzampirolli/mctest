# coding=UTF-8



"""
Gera questão paramátrica como no exemplo:
Quais itens têm apenas números ímpares
Itens:
\item I. 2; 3
\item II. 2; 5
\item III. 1; 3
\item IV. 1; 5
\item V. 2; 4

Alternativas:
A. III; IV
B. III; V
C. IV; V
D. I; V
E. II; IV
F. I; II
G. I; III
H. II; III
I. II; V
J. I; IV

# Exemplo de chamada da função
#gerar_QM_itens(setTrue, setFalse, num_itens, num_alternativas, num_itens_corretos, num_afirmacoes_por_item):

itens_format, descricoes = gerar_QM_itens(['1', '3', '5'], ['2', '4'], 5, 10, 2, 2)

"""


def gerar_QM_itens(setTrue=['1', '3', '5'],
                   setFalse=['2', '4'],
                   num_itens=5,  # N. itens na questão (máximo: 10)
                   num_alternativas=10,  # N. alternativas (máximo: 15)
                   num_itens_corretos=3,  # N. itens corretos na questão (máximo: num_itens)
                   num_afirmacoes_por_item=3):  # N. afirmacoes em cada item (menor que quant. de setTrue)

    global itens_format, itens_str

    itens_str = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

    # Parte 2 - Método verifica_parametros

    # Verifica parâmetros para criar variações
    def verifica_parametros(T, F, N, P, C, A):
        from scipy.special import comb
        output, pode_gerar = [], True
        T, F = len(T), len(F)
        if N * C < A or C >= N or P > T:
            output.append(f"ERRO: Não é possível gerar variações com {A} alternativas,"
                          f" {N} itens e {C} item(ns) correto(s)")
            pode_gerar = False
        if comb(T, P) < C:
            output.append(f"ERRO: Não é possível gerar {C} itens distintos com {P} "
                          "afirmações corretas por item.")
            pode_gerar = False
        if comb(T + F, P) < N:
            output.append(f"ERRO: Não é possível gerar {N} itens")
            pode_gerar = False
        if comb(N, P) < A:
            output.append(f"ERRO: Não é possível gerar {A} alternativas")
            pode_gerar = False
        variacoes = (f'Número de variações possíveis: '
                     f'comb({comb(T + F, P):.0f},{N}) = {comb(comb(T + F, P), N):.0f}')
        itens_format = ''
        if not pode_gerar:
            output.extend([f'Itens distintos com {P} afirmações verdadeiras: '
                           f'comb({T},{P}) = {comb(T, P):.0f}',
                           f'Itens distintos com afirmações V+F: '
                           f'comb({T + F},{P}) = {comb(T + F, P):.0f}', variacoes])
            itens_format = "\item " + "\n\item ".join(output)
            itens_format += (f'\n\item setTrue = {T}\n\item setFalse = {F}'
                             f'\n\item num_itens = {N}\n\item num_alternativas = {A}'
                             f'\n\item num_itens_corretos = {C}'
                             f'\n\item num_afirmacoes_por_item = {P}')
            itens_format = itens_format.replace('_', '\_')
        return pode_gerar, itens_format

    pode_gerar, itens_format = verifica_parametros(
        setTrue, setFalse, num_itens, num_afirmacoes_por_item,
        num_itens_corretos, num_alternativas)
    if not pode_gerar:
        print(itens_format)
        descricoes = ['' for _ in range(num_alternativas)]

    # Parte 3 - Definições dos Métodos

    def gerar_itens(setTrue, setFalse, num_itens, num_afirmacoes):
        todas_afirmacoes = setTrue + setFalse  # Junta todas as afirmações
        random.shuffle(todas_afirmacoes)  # Embaralha a lista para aleatoriedade

        # Gerar combinações únicas usando um conjunto para evitar duplicatas
        itens = set()
        while len(itens) < num_itens:
            item = tuple(sorted(random.sample(todas_afirmacoes, num_afirmacoes)))
            itens.add(item)

        return list(itens)  # Converte para lista antes de retornar

    def gerar_itens_corretos(setTrue, setFalse, num_itens, num_afirmacoes, itens):
        # Lista para armazenar os itens que atendem aos critérios
        itens_corretos = []
        for item in itens:
            # Contar a quantidade de afirmações verdadeiras presentes no item
            cont = 0
            for op in item:
                if op in setTrue:
                    cont += 1
            # Se o número de afirmações verdadeiras for igual ao número desejado
            if cont == num_afirmacoes:
                itens_corretos.append(item)
        return itens_corretos

    def gerar_indices_itens_corretos(itens, itens_corretos):
        # Gerar índices dos itens corretos e criar itens_format

        # formatar itens e declarar como variável global
        global itens_format, itens_str
        itens_format = ''

        corretos = []
        for i, item in enumerate(itens):
            s = f"{'; '.join(item)}"
            # itens_format += f"\item {itens_str[i]}. {s}\n"
            itens_format += f"\item {s}\n"

            # Adicionar o índice do item à lista de itens corretos
            for c in itens_corretos:
                if c == item:
                    corretos.append(i)

        return sorted(corretos)  # Ordenar os índices dos itens corretos

    # Parte 4 - Bloco principal

    import random

    while pode_gerar:
        itens = gerar_itens(setTrue, setFalse, num_itens, num_afirmacoes_por_item)

        itens_corretos = gerar_itens_corretos(setTrue, setFalse, num_itens,
                                              num_afirmacoes_por_item, itens)

        # Se o número de itens corretos não for igual ao desejado, gerar uma nova questão
        if len(itens_corretos) != num_itens_corretos:
            continue

        corretos = gerar_indices_itens_corretos(itens, itens_corretos)

        # Alternativa correta
        aux = []
        for corr in range(num_itens_corretos):
            aux.append(itens_str[corretos[corr]])
        itens_comb = [aux]

        # Gerar alternativas erradas
        for i in range(num_alternativas):
            aux = sorted(random.sample(itens_str[:num_itens], num_itens_corretos))
            # Incluir apenas alternativas diferentes
            if not aux in itens_comb:
                itens_comb.append(aux)

        # Montar as descrições das alternativas
        descricoes = []
        for letra in itens_comb:
            descricoes.append(f"{'; '.join(letra)}")

        # Se o número de descrições não for igual ao número de alternativas,
        # gerar uma nova questão
        if len(descricoes) != num_alternativas:
            continue

        # Encerrar o loop, pois a questão foi gerada com sucesso
        break

    if pode_gerar:
        print('Quais itens têm apenas números ímpares')
        print('Itens:')
        print(itens_format)

        print("Alternativas:")
        opcoes = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for idx, alt in enumerate(descricoes):
            print(f"{opcoes[idx]}. {alt}")

    return itens_format, descricoes

#############################################


import numpy as np

def generate_unique_temp_file(extension=''):
    import tempfile
    # Specify the directory where the unique temporary file will be created
    directory = './tmp'

    # Create a unique temporary file with the specified extension in the specified directory
    with tempfile.NamedTemporaryFile(delete=False, dir=directory, suffix=extension) as temp_file:
        temp_file_path = temp_file.name

    # You can now use the path of the temporary file as needed
    return temp_file_path

def read_csv_from_dropbox(url, sep=','):
    """
    Reads a CSV file from Dropbox, saves it to a unique file on the server, and returns the DataFrame.

    Args:
    - url (str): Dropbox URL of the CSV file.
    - sep (str): Separator used in the CSV file (default is ',').

    Returns:
    - pd.DataFrame: DataFrame containing the CSV data.
    """
    import pandas as pd
    import requests
    import os
    import warnings
    from urllib3.exceptions import InsecureRequestWarning

    # Disable InsecureRequestWarning
    warnings.simplefilter('ignore', InsecureRequestWarning)

    # Download the CSV file using requests
    response = requests.get(url, verify=False)  # Disable SSL verification

    # Generate a unique filename
    unique_filename = generate_unique_temp_file('.csv')

    # Save the downloaded content to the unique local file
    local_file_path = os.path.join('./tmp/', unique_filename)
    with open(local_file_path, 'wb') as file:
        file.write(response.content)

    # Read the CSV file using pandas with the specified separator
    df = pd.read_csv(local_file_path, sep=sep)

    # Delete the local file
    os.remove(local_file_path)

    return df


def getCasesMoodle(inp=[], out=[], language=[], skills=[], description=[]):
    cases = {}
    cases['input'] = np.array(inp).tolist()
    cases['output'] = np.array(out).tolist()
    cases['language'] = np.array(language).tolist()
    cases['skills'] = np.array(skills).tolist()
    cases['description'] = np.array(description).tolist()
    return cases


''' PT_BR
desc: change comma to point
input: number
output: string
syntax: str = PT_BR(num)
author: Jorge Tomioka
date: august 2019

ex: 1,000.00 to 1.000,00
'''


def PT_BR(my_value):
    try:
        a = '{:,.2f}'.format(float(my_value))
    except:
        a = 'ERROR in PT_BR function'

    b = a.replace(',', 'v')
    c = b.replace('.', ',')
    return c.replace('v', '.')


def drawMatrix(A, myfile):
    """
    Desenha uma representação visual de uma matriz e salva a imagem em um arquivo.
    Exemplo de uso:
    No enunciado da questão, desenhe a seguinte figura
    (copie o código abaixo para uma nova questão):
    \begin{figure}[h!]
    \centering
    \includegraphics[scale=0.55]{[[code:f"./tmp/imgs180days/{pathGraficoA}"]]}
    \end{figure}

    [[def:
    import numpy as np
    Lin, Col = 4, 5
    A = np.random.randint(10, size=(Lin, Col))
    # Plotagem da função
    import hashlib
    s =str([Lin, Col])
    h = hashlib.md5(s.encode()) # create hash - arquivo único
    h = str(h.hexdigest())
    fig0 = f'fz_figExample01{Lin}_{Col}_{h}.png'
    drawMatrix(A, fig0)
    ]] """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    mat = ax.imshow(A, cmap='Pastel1', interpolation='nearest')

    for x in range(A.shape[0]):
        for y in range(A.shape[1]):
            ax.annotate(str(A[x, y])[0], xy=(y, x), horizontalalignment='center',
                        verticalalignment='center')

    plt.show()
    fig.savefig(f'./tmp/imgs180days/{myfile}.png', dpi=300)
    plt.close()

def printMatrix(A, title='', left='', right='', align='r', dec='3.2f'):
    """
      Draw a matrix
      :param A: matrix = 2D list
      :param title: title, ex.: title = [...]
      :param left: left symbol
      :param right: right symbol
      :param align: aling in r, l, c, C, S
      :param dec: format of decimals
      :return: string of draw matrix
    """
    str1 = """
\\setcounter{MaxMatrixCols}{__size__}
\\begin{displaymath}
\\textbf{__title__}
\\left__tleft__
\\begin{matrix*}[__align__]
"""
    import itertools

    # A = np.array(A)
    B = list(itertools.chain.from_iterable(A))  # 2D to 1D

    if all(isinstance(x, int) for x in B):
        dig = 1 if min(B) < 0 else 0
        digitos = '%' + str(len(str(max(B))) + dig) + 'd '
    elif all(isinstance(x, float) for x in B):
        digitos = '%' + dec
    else:
        digitos = '%s'

    for i in range(len(A)):
        for j in range(len(A[0])):
            str1 += digitos % A[i][j]
            if j < len(A[0]) - 1:
                str1 += "& "
        if i < len(A) - 1:
            str1 += "\\\\"
        str1 += "\n"

    str1 += """\\end{matrix*}
\\right__tright__
\\end{displaymath}"""

    str1 = str1.replace('__tleft__', left).replace('__tright__', right)
    str1 = str1.replace('__title__', title)
    str1 = str1.replace('__align__', align)
    str1 = str1.replace('__size__', str(len(A[0])))
    return str1


"""
from Fernando Teubl - 2022-07-07
License http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
"""


# Print source code
def printCode(codeLines):
    # source = inspect.getsource(code)
    # codeLines = source.splitlines()

    msg = ""
    count = 0
    for line in codeLines.split('\n'):
        count = count + 1
        msg += f"{count:02n}: {line}\n"  # .replace('    ', '__')
    return msg


##
# UTILS

# Main class to read and run an Algorithm
class Algorithm:
    algorithm = None
    last_error = None

    def __init__(self, mod_name, func_name, func_args,
                 forbidden_words=r"import|from|print|input|sort|open|read|write|stdout|stdin"):
        firstline = f"""def {func_name}({", ".join(func_args)}):"""

        # Check code ...
        with open(mod_name + '.py', mode='r') as file:
            self.last_error = None
            code = file.read()
            code_lines = code.splitlines()
            code_inner = "\r\n".join(code_lines[1:])

            if re.search(forbidden_words, code, re.MULTILINE):
                self.last_error = f"""Não é permitido utilizar as seguintes palavras (ou parte de): {", ".join(forbidden_words.split("|")[:-1]) + " e " + forbidden_words.split("|")[:-1][-1]}."""

            elif len(code_lines) == 0 or code_lines[0] != firstline:
                self.last_error = f"""A primeira linha do código deve ser "{firstline}". """

            elif re.search(r"^[^ \t].+$", code_inner, re.MULTILINE):
                self.last_error = """Só é permitido códigos dentro da função Algoritmo()"""

            # Load code ...
            else:
                import importlib
                try:
                    mod = importlib.import_module(mod_name)
                    self.algorithm = eval(f'mod.{func_name}')
                except SyntaxError as e:
                    self.last_error = f"""Erro de sintaxe na linha {e.lineno}."""

    def run(self, *args):
        ret = None
        if callable(self.algorithm):
            try:
                ret = self.algorithm(*args)
            except NameError as e:
                return ret, str(e)
        else:
            None, "Invalid algorithm"
        return ret, None


# Main class to generate the exercise
class TesteDeMesa:
    code = None
    codeLines = None
    table = None
    minRows = 3  # Minimum lines that must be identical. It will be provided to the student automatically if not exact.

    # Constructor
    def __init__(self, function):

        if callable(function):
            self.code = function
            try:
                import inspect
                source = inspect.getsource(self.code)
                self.codeLines = source.splitlines()
            except Exception as e:
                source = getattr(e, 'message', repr(e))
        elif type(function) == str:
            import re
            self.codeLines = function.splitlines()
            func_name = re.findall(r"^def *([a-zA-Z0-9_]+) *\(.*\) *\: *$", self.codeLines[0])
            if len(func_name) != 1:
                raise Exception("Invalid function string.")
            exec(function)
            self.code = eval(func_name[0])
        else:
            raise Exception("Invalid function.")

    # Print source code
    def source(self):
        import re
        msg = ""
        count = 0
        for line in self.codeLines:
            count = count + 1
            line = re.sub(r'^def ', r'Função ', line)
            line = re.sub(r':$ *', r'', line)

            # Repetition
            line = re.sub(r'for *(.+) *in *(.+)', r'Para \1 em \2, faça:', line)
            line = re.sub(r'em *range *\((.+) *, *(.+) *\)', r'de \1 até \2 (não incluso)', line)
            line = re.sub(r'while *(.+)', r'Enquanto \1, faça:', line)

            # Conditional
            line = re.sub(r'elif *(.+)', r'Senão se \1, então:', line)
            line = re.sub(r'if *(.+)', r'Se \1, então:', line)
            line = re.sub(r'else', r'Senão:', line)

            # Functions
            line = re.sub(r'print *\(.*"(.+)".*\)', r'Imprimir "\1"', line)  # print with "
            line = re.sub(r'print *\(.*(.+).*\)', r'Imprimir \1', line)  # print without "
            line = re.sub(r'len *\( *([^ ]+) *\)', r'\1.tamanho', line)  # len

            # Return
            line = re.sub(r'^( +)return', r'\1Retorna', line)

            # Operators
            # line = re.sub(r'([a-z0-9]+) *=[^=] *(.*)', r'\1 ← \2', line)
            # line = re.sub(r'<=', r'≤', line)
            # line = re.sub(r'>=', r'≥', line)
            line = re.sub(r'==', r'=', line)
            # line = re.sub(r'!=', r'≠', line)
            line = re.sub(r'([a-z0-9\[\]]+) *\+= *([a-z0-9\[\]]+)', r'\1 = \1 + \2', line)  # +=
            line = re.sub(r'([a-z0-9\[\]]+) *-= *([a-z0-9\[\]]+)', r'\1 = \1 - \2', line)  # -=
            line = re.sub(r'([a-z0-9\[\]]+) *\*= *([a-z0-9\[\]]+)', r'\1 = \1 * \2', line)  # *=
            line = re.sub(r'([a-z0-9\[\]]+) */= *([a-z0-9\[\]]+)', r'\1 = \1 / \2', line)  # /=
            # line = re.sub(r'([a-z0-9]+) *\* *([a-z0-9]+)', r'\1 × \2', line)  # /
            # line = re.sub(r'([a-z0-9]+) */ *([a-z0-9]+)', r'\1 ÷ \2', line)  # *
            line = re.sub(r'([a-z0-9]+) *% *([a-z0-9]+)', r'\1 mod \2', line)  # mod

            # Logic
            line = re.sub(r' and ', r' E ', line)
            line = re.sub(r' or ', r' OU ', line)

            # Cast
            line = re.sub(r'int *\((.*)\)', r'⎣\1⎦', line)  # change to floor when int
            line = re.sub(r'(float|str) *\((.*)\)', r'\2', line)  # removing other cast

            # Identation
            # line = re.sub('    ', '▐ ', line)  # Always the last!
            msg = msg + f"{count:02n}: {line}\n"

        return msg

        # Print source code

    def sourceFlowChart(self, fileName):
        from pyflowchart import Flowchart
        strCode = '\n'.join([i for i in self.codeLines])
        fc = Flowchart.from_code(strCode)
        flowchart = '''<!DOCTYPE html><html><head><meta charset="UTF-8">
          <title>MCTest - Flowchart.js</title>
          <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/raphael/2.3.0/raphael.min.js"></script>
          <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/flowchart/1.14.1/flowchart.js"></script>
          </head><body><div id="diagram"></div><script>
    var diagram = flowchart.parse(`__code__`);
    diagram.drawSVG('diagram');</script></body></html>'''
        flowchart = flowchart.replace('__code__', fc.flowchart())
        with open(fileName, 'w') as f:
            f.write(flowchart)
        return True

    # Exec code and create the matrix
    def make(self, args, ignoreVars=[]):

        # Init
        lines = []
        self.last_line = None

        # Nested function, used on setrace
        # https://docs.python.org/3/library/inspect.html
        def my_tracer(frame, event, arg=None):
            # Just trace lines!
            if event != 'line':
                return my_tracer

            # Always using the last line because the current line doesn't have the variables updated
            line_no = frame.f_lineno - frame.f_code.co_firstlineno
            if self.last_line == None:
                self.last_line = line_no
                return

            # Create table
            if 'tracing_func' not in frame.f_locals:  # If using pydevd_tracing
                from copy import deepcopy
                lines.append({
                    'line': self.last_line + 1,
                    'vars': deepcopy(frame.f_locals),
                    'command': self.codeLines[self.last_line]
                })
                self.last_line = line_no
                return my_tracer

        # Set sys.settrace
        try:
            import pydevd_tracing
            settrace = pydevd_tracing.SetTrace
        except ModuleNotFoundError as err:
            from sys import settrace
        settrace(my_tracer)

        import sys, io
        stdout_orig = sys.stdout
        string_io = io.StringIO()
        sys.stdout = string_io
        func_ret = self.code(*args)
        sys.stdout = stdout_orig
        func_out = string_io.getvalue()
        settrace(None)

        # Add last line (return)
        lines.append({
            'line': self.last_line + 1,
            'return': str(func_ret) if func_ret != None else '?',
            'command': self.codeLines[self.last_line],
        })

        # Get all variables
        allVars = []
        for vars in lines[:-1]:
            for var in vars['vars']:
                if var not in allVars and var not in ignoreVars:
                    allVars.append(var)

        # First line
        self.table = [['Linha'] + allVars]

        # Fill table
        for line in lines[:-1]:
            v = [str(line['line'])]
            for k in allVars:
                if k in line['vars'].keys():
                    v.append(str(line['vars'][k]))
                else:
                    v.append('?')
            self.table.append(v)
        self.table.append([str(lines[-1]['line']), str(lines[-1]['return'])])

        return func_ret, func_out

        # Print Table

    def show(self, clean=True):
        str = ""
        from copy import deepcopy
        table = deepcopy(self.table)

        if (clean):
            for line in range(len(table) - 1, 1, -1):
                for col in range(1, len(table[line])):
                    if table[line][col] == table[line - 1][col]:
                        table[line][col] = ''

        # Print table
        for line in table:
            str = str + f"{line[0]:^8}"
            for col in range(1, len(line)):
                str = str + f"{line[col]:^8}"
            str = str + '\n'  # f"{line[1]}"
        return str  # .replace(' ', '_')

    @staticmethod
    def str2table(str):
        line = 1
        tbl = []
        for row in str.splitlines():
            cols = []
            v = None
            for col in row.strip().replace(',', ' ').replace('\t', ' ').split(' '):
                c = col.strip()
                if c != '':
                    if c[0] == '[':
                        if v != None:
                            raise Exception(f"Matriz não suportado na linha {line}")
                        elif len(c) > 1:
                            v = [c[1:]]
                        else:
                            v = []
                    elif c[-1] == ']':
                        if v == None:
                            raise Exception(f"Vetor ainda não inicializado na linha {line}")
                        elif len(c) > 1:
                            v.append(c[:-1])
                        print(v)
                        cols.append('[' + ', '.join(v) + ']')
                        v = None
                    elif v != None:
                        v.append(c)
                    else:
                        cols.append(c)
            if len(cols) == 0:
                raise Exception(f"A linha {line} está vazia. Favor, remova!")
            tbl.append(cols)
            line = line + 1
        return tbl

    # Set a custom table template
    def setTable(self, table):
        if isinstance(table, str):
            self.table = TesteDeMesa.str2table(table)
        else:
            self.table = table

    # Correct a question
    def correct(self, answers, maxRows=0):
        if isinstance(answers, str):
            try:
                answers = TesteDeMesa.str2table(answers)
            except Exception as e:
                return 0, getattr(e, 'message', str(e))

        if self.table == None:
            raise Exception("Table is none.")

        feedback = None

        # Check if the first rows is equal ...
        if feedback == None:
            if len(answers) < self.minRows or answers[:self.minRows] != self.table[:self.minRows]:
                feedback = f"As primeiras {self.minRows} linhas devem ser:\n\n"
                for i in range(self.minRows):
                    feedback = feedback + " ".join([f" {self.table[i][c]}" for c in range(len(self.table[i]))]) + "\n"

        corrects = 0;
        if feedback == None:
            for i in range(self.minRows,
                           (maxRows if maxRows > self.minRows and maxRows < len(self.table) else len(self.table))):
                isCorrect = True
                if len(answers) <= i:
                    break
                if len(self.table[i]) != len(answers[i]):
                    if i == len(self.table) - 1:
                        feedback = f"A última linha deve conter apenas o número da linha de retorno e o valor retornado." + \
                                   "\nUtilize '?' se não houver valor retornado."
                    else:
                        feedback = f"Linha {i + 1} tem {len(answers[i])} colunas, mas o esperado é ter {len(self.table[i])} colunas." + \
                                   "\nObs.: Utilize '?' se você quer representar um valor indefinido."
                    isCorrect = False
                elif i != 0:
                    if not answers[i][0].isnumeric():
                        feedback = f"A primeira coluna da linha {i + 1}, que representa o número da linha, precisa ser inteiro."
                    for j in range(1, len(answers[i])):
                        if not answers[i][j].isnumeric() and answers[i][j] != '?' and (
                                answers[i][j][0] != '[' and answers[i][j][-1] != ']'):
                            feedback = f"A coluna {j + 1} da linha {i + 1} precisa ter um valor inteiro, um vetor '[]' ou '?' caso for indefinido."
                            isCorrect = False

                if self.table[i] != answers[i]:
                    isCorrect = False

                if isCorrect:
                    corrects = corrects + 1
                elif feedback == None:
                    feedback = "O teste de mesa contém um ou mais erros..."

        if feedback == None and len(self.table) < len(answers):
            feedback = "O seu Teste de Mesa está maior do que o esperado.\nNão considere a instrução 'return'.\nTente apagar a(s) última(s) linha."
            corrects = int(corrects * 0.8)

        if feedback == None:
            if len(answers) >= (maxRows if maxRows > self.minRows and maxRows < len(self.table) else len(self.table)):
                feedback = "Perfeito."
            else:
                feedback = "O teste de mesa contém um ou mais erros..."

        return corrects / ((maxRows if maxRows > self.minRows and maxRows < len(self.table) else len(
            self.table)) - self.minRows), feedback


#######################

##### Py2Tex from https://github.com/cairomassimo/py2tex

import ast
import contextlib


class CodeGen:
    def __init__(self):
        self._indentation = 0
        self._lines = []

    def line(self, line):
        self._lines.append((line, self._indentation))

    def _indented_lines(self):
        for line, indentation in self._lines:
            yield "  " * indentation + line + "\n"

    def to_string(self):
        return "".join(self._indented_lines())

    @contextlib.contextmanager
    def indent(self):
        self._indentation += 1
        yield
        self._indentation -= 1


class Py2Tex(ast.NodeVisitor, CodeGen):
    def __init__(self):
        super().__init__()
        self._emit_tex = True

    def visit(self, node):
        result = super().visit(node)
        if result is None:
            return ""
        return result

    def visit_all(self, nodes):
        for node in nodes:
            self.visit(node)

    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def body(self, body):
        with self.indent():
            self.visit_all(body)

    def arg(self, a):
        if a.annotation is None:
            return r"\PyArg{" + a.arg + "}"
        else:
            assert isinstance(a.annotation, ast.Str)
            return r"\PyArgAnnotation{" + a.arg + "}{" + a.annotation.s + "}"

    def expr(self, e):
        return r"\PyExpr{" + self.visit(e) + "}"

    def visit_FunctionDef(self, node):
        if not self._emit_tex:
            return
        args = r"\PyArgSep".join(self.arg(a) for a in node.args.args)
        if node.returns:
            self.line(r"\Function{" + node.name + "}{" + args +
                      r"}{ $\rightarrow$ \texttt{" + node.returns.s + "}}")
            self.body(node.body)
            self.line(r"\EndFunction%")
        else:
            self.line(r"\Procedure{" + node.name + "}{" + args + "}")
            self.body(node.body)
            self.line(r"\EndProcedure%")

    def visit_Assign(self, node):
        if not self._emit_tex:
            return
        targets = r" \PyAssignSep ".join(
            self.visit(target) for target in node.targets)
        assign = r"\PyAssign{" + targets + "}{" + self.expr(node.value) + "}"
        self.line(r"\State{" + assign + "}")

    def visit_AnnAssign(self, node):
        if not self._emit_tex:
            return

        target = self.visit(node.target)

        assert isinstance(node.annotation, ast.Str)
        assert node.value == None

        assign = r"\PyAnnotation{" + target + "}{" + node.annotation.s + "}"

        self.line(r"\State{" + assign + "}")

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Str):
            self.handle_magic_string(node.value.s)
            return
        if not self._emit_tex:
            return
        self.line(r"\State{" + self.expr(node.value) + "}")

    def handle_magic_string(self, s: str):
        if s.startswith("!tex\n"):
            for l in s.splitlines()[1:]:
                self.line(l)
        elif s == "!show":
            self._emit_tex = True
        elif s == "!hide":
            self._emit_tex = False
        else:
            self.line(r"\Comment{" + s + "}")

    def visit_Str(self, node):
        return r"\PyStr{" + node.s + "}"

    def visit_Name(self, node):
        return r"\PyName{" + node.id + "}"

    def visit_Num(self, node):
        return r"\PyNum{" + str(node.n) + "}"

    def visit_NameConstant(self, node):
        return r"\Py" + str(node.value)

    def visit_BoolOp(self, node):
        return (r" \Py" + type(node.op).__name__ + " ").join(self.visit(v) for v in node.values)

    def visit_Call(self, node):
        assert isinstance(node.func, ast.Name)
        if node.func.id == "_":
            assert len(node.args) == 1
            [arg] = node.args
            return r"\PyPar{" + self.visit(arg) + "}"
        return r"\PyCall{" + node.func.id + "}" + "{" + r" \PyCallSep ".join(self.visit(a) for a in node.args) + "}"

    def visit_For(self, node):
        if not self._emit_tex:
            return

        assert isinstance(node.iter, ast.Call)
        assert isinstance(node.iter.func, ast.Name)

        nargs = len(node.iter.args)
        args = map(self.visit, node.iter.args)
        assert 1 <= nargs <= 3
        if nargs == 1:
            start = 0
            [stop] = args
            step = 1
        if nargs == 2:
            [start, stop] = args
            step = 1
        if nargs == 3:
            [start, stop, step] = args

        variable = self.visit(node.target)

        self.line(
            r"\PyFor" + "".join("{" + x + "}" for x in [variable, start, stop, step]))
        self.body(node.body)
        self.line(r"\EndPyFor")

    def visit_BinOp(self, node):
        return self.visit(node.left) + r" \Py" + type(node.op).__name__ + " " + self.visit(node.right)

    def visit_UnaryOp(self, node):
        return r"\Py" + type(node.op).__name__ + "{" + self.visit(node.operand) + "}"

    def visit_Subscript(self, node):
        return r"\PySubscript{" + self.visit(node.value) + "}{" + self.visit(node.slice) + "}"

    def visit_Index(self, node):
        return self.visit(node.value)

    def visit_Compare(self, node):
        result = self.visit(node.left)
        for op, right in zip(node.ops, node.comparators):
            result += r" \Py" + type(op).__name__ + " " + self.visit(right)
        return result

    def visit_If(self, node):
        if not self._emit_tex:
            return
        self.line(r"\If{" + self.expr(node.test) + "}")
        self.body(node.body)
        if node.orelse:
            self.line(r"\Else%")
            self.body(node.orelse)
        self.line(r"\EndIf%")

    def visit_While(self, node):
        if not self._emit_tex:
            return
        self.line(r"\While{" + self.expr(node.test) + "}")
        self.body(node.body)
        self.line(r"\EndWhile%")

    def visit_Return(self, node):
        if not self._emit_tex:
            return
        self.line(r"\Return{" + self.expr(node.value) + "}")

    def visit_List(self, node):
        elts = r" \PyListSep ".join(self.visit(el) for el in node.elts)
        return r"\PyList{" + elts + "}"


def ast_to_pseudocode(source_ast, **kwargs):
    return "\n".join(Py2Tex(**kwargs).visit(source_ast)) + "\n"


def source_to_pseudocode(source, **kwargs):
    return ast_to_pseudocode(ast.parse(source), **kwargs)
