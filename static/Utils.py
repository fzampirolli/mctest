# coding=UTF-8

import numpy as np


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


##################################################

"""
Copyright 2024 by Francisco de Assis Zampirolli from UFABC
License MIT
https://github.com/fzampirolli/morph
25 January 2024
"""
import matplotlib.pyplot as plt, numpy as np, cv2, requests, sys, subprocess
from PIL import Image
from skimage import io


class mm(object):
    """ A helper class for image processing tasks. """

    IN_COLAB = 'google.colab' in sys.modules  #### INICIALIZATION ####
    count_Images = 0

    def __init__(self):
        pass

    @staticmethod
    def install(packages=['matplotlib', 'numpy', 'opencv-python']):
        """This function will install the packages
        input: <packages> list of packages.
        Examples: mm.install(['matplotlib', 'scikit-image']) """
        for package in packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    #### IMAGE UTILITIES: CREATE, DRAW, CHECK ####

    @staticmethod
    def read(file):
        """ Reads an image from a local file path or URL.
        input: <str> File path or URL (full or 'id=keyGoogleDrive').
        output: the read image.
        Examples:
        img_local  = mm.read('image.png')
        img_url    = mm.read('https://example.com/image.jpg')
        img_gdrive = mm.read('id=keyGoogleDrive')"""
        if file.startswith(('http', 'id=')):
            url, pre = '', 'https://drive.google.com/file/d/'
            if pre in file:
                url = 'https://drive.google.com/uc?export=view&id='
                url += file[len(pre):].split('/')[0]
            elif file.startswith('id='):
                url = 'https://drive.google.com/uc?export=view&id=' + file[3:]
            else:
                url = file
            return io.imread(url)
        else:
            return cv2.imread(file)

    @staticmethod
    def color(img):
        """ Converts an image to RGB color space.
        input: <numpy.ndarray> Image in BGR, grayscale, or RGBA format.
        output: RGB image in <numpy.ndarray> format.
        Example:
        img     = mm.read('image.png')
        img_rgb = mm.color(img) """
        if len(img.shape) == 2:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif len(img.shape) == 3 and img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        elif len(img.shape) == 3 and img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            raise ValueError("Unsupported image format.")

    @staticmethod
    def gray(img):
        """ Converts a color image to grayscale.
        input: <numpy.ndarray> Input color image.
        output: grayscale image.
        Examples:
        img = mm.read('image.png')
        img_gray = mm.gray(img) """
        if len(img.shape) == 3 and img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        else:
            return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    @staticmethod
    def threshold(img, limiar=0):
        """ Thresholds an input image by a threshold value or using Otsu's method.
        input: <numpy.ndarray> Input image to be thresholded.
        output: <numpy.ndarray> Thresholded image.
        Examples:
        img = mm.read('image.png')
        th = mm.threshold(img) """
        if limiar == 0:
            value, th = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            value, th = cv2.threshold(img, limiar, 255, cv2.THRESH_BINARY)
        return th

    @staticmethod
    def show(*args):
        """ This function will draw images f
        input: <*args> set of images f_i, where i>0 is binary image
        output: image drawing
        Example:
        f1, f2 = np.zeros((100, 100,3)),  np.zeros((100, 100))
        f2[50:60, 50:60] = 1
        mm.show(f1, f2)"""
        colors = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 0, 255], [0, 255, 255],
                  [255, 255, 0], [255, 50, 50], [50, 255, 50]]  # red, green, blue, cyan, ...
        f = args[0].copy()
        for i in range(1, len(args)):
            if i >= len(colors):
                break
            f[args[i] > 0] = colors[i - 1]
        _ = plt.imshow(f, "gray")
        if not mm.IN_COLAB:
            plt.savefig('fig_' + str(mm.count_Images).zfill(4) + '.png')
            mm.count_Images += 1

    @staticmethod
    def readImg(h, w):
        """ This function reads an image from input and returns it as a NumPy array.
        input: size of image: height and width
        output: image
        Example:
          mm.readImg(3, 4)
          0 1 0 0
          1 1 1 1
          0 1 0 0
          The function will return the following NumPy array:
          array([[0, 1, 0, 0],
                 [1, 1, 1, 1],
                 [0, 1, 0, 0]]) """
        m = np.zeros((h, w), dtype='uint8')
        # Loop over each row of the image and read it from standard input.
        for l in range(h):
            # Split the row into individual pixel values and convert them to integers.
            m[l] = [int(i) for i in input().split() if i]
        return m

    @staticmethod
    def readImg2():
        """ This function reads an image of varying size from standard input.
        Example:
          mm.readImg2()
          255   0  255
          128  64  192
          0   192  128 """
        b = []
        read_row = input()
        while read_row:  # Read each line of the input until there is no more input.
            # Split the line into individual pixel values and convert them to integers.
            row = [int(i) for i in read_row.split() if i]
            b.append(row)  # Add the row to the list of rows.
            read_row = input()
        return np.array(b).astype('uint8')

    @staticmethod
    def randomImage(h, w, maxValue=9):
        """ Creates a random image of size h x w with integer values in [0,maxValue].
        input: size of image: height, width and max value
        output: image
        Example:
          mm.randomImage(3, 3, maxValue=5)
          The function will return a random NumPy array, such as:
          array([[2, 1, 3],
                 [0, 4, 2],
                 [5, 1, 5]], dtype=uint8)"""
        return np.random.randint(maxValue + 1, size=(h, w)).astype('uint8')

    @staticmethod
    def drawImage(f):
        """ Converts the input image f into a string representation suitable for printing.
        Args: f (ndarray): The input image.
        Returns: A string representing the input image.
        Example:
            string_representation = mm.drawImage(f)
            print(string_representation) """
        l, c = f.shape
        if np.min(f) < 0:
            digits = '%' + str(1 + len(str(np.max(f)))) + 'd '
        else:
            digits = '%' + str(len(str(np.max(f)))) + 'd '
        # print('"'+digits+'"')
        string_representation = ''
        for i in range(l):
            for j in range(c):
                string_representation += digits % f[i][j]
            string_representation += '\n'
        return string_representation

    @staticmethod
    def drawImagePlt(f):
        """ Displays the input image f using Matplotlib.
        Args: f (ndarray): The input image.
        Example: drawImagePlt(f) """
        h, w = f.shape
        m = min(h, w)
        # Set up the plot.
        plt.figure(figsize=(m, m))
        plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = False
        plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True
        # Display the image.
        _ = plt.imshow(f, 'gray')
        # Set the tick marks and labels.
        plt.yticks(range(h))
        plt.xticks(range(w))
        plt.ylabel('y')
        plt.xlabel('x')
        # Add grid lines.
        [plt.axvline(i + .5, 0, h, color='r') for i in range(w - 1)]
        [plt.axhline(j + .5, 0, w, color='r') for j in range(h - 1)]

    @staticmethod
    def drawImageKernel(f, B, x, y):
        """This function will draw image f, considering a kernel
        input:
         - f: input image
         - B: kernel
         - x,y: center pixel of kernel
        output:
         - string: image drawing
        """
        h, w = f.shape
        Bh, Bw = B.shape
        Bcx, Bcy = Bw // 2, Bh // 2
        m = min(h, w)
        plt.figure(figsize=(m, m))
        plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = False
        plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True
        plt.imshow(f, 'gray')
        plt.yticks(range(h))
        plt.xticks(range(w))
        plt.ylabel('y')
        plt.xlabel('x')
        plt.title('Processando pixel (x,y)=(%d,%d)' % (x, y))
        [plt.axvline(i + .5, 0, h, color='r') for i in range(w - 1)]
        [plt.axhline(j + .5, 0, w, color='r') for j in range(h - 1)]
        [plt.plot([i + x - Bcx - .5, i + x - Bcx - .5], [y - Bcy - .5, Bh + y - Bcy - .5], color='y', linewidth=5) for i
         in range(Bw + 1)]
        [plt.plot([x - Bcx - .5, x - Bcx + Bw - .5], [j + y - Bcy - .5, j + y - Bcy - .5], color='y', linewidth=5) for j
         in range(Bh + 1)]

    @staticmethod
    def lblshow(f, border=3):
        """This function will draw image f with each component has a color
        input:
         - f: input image
         - border: border optional [defaul=2]
        output:
         - y: color image
        """
        from skimage import measure  # <<<<<<<<<<<<<<<<<<
        r = f
        # Find contours at a constant value of 0.8
        contours = measure.find_contours(r, 0.0)

        fig, ax = plt.subplots()
        ax.imshow(r, interpolation='nearest', cmap=plt.cm.gray)

        for n, contour in enumerate(contours):
            ax.plot(contour[:, 1], contour[:, 0], linewidth=border)

        ax.axis('image')
        ax.set_xticks([])
        ax.set_yticks([])
        _ = plt.imshow(f, "gray")
        if not mm.IN_COLAB:
            plt.savefig('fig_' + str(mm.count_Images).zfill(4) + '.png')
            mm.count_Images += 1

    @staticmethod
    def binary(f):
        """This function checks whether the image is binary
        input:
         - f: input image
        output:
         - y: True if binary image
        """
        hist, bins = np.histogram(f.ravel(), 256, [0, 256])
        if np.count_nonzero(hist > 0) == 2:  # binary
            return True
        elif np.count_nonzero(hist > 0) > 2:
            return False
        else:
            return None

    ##### OPERATIONS ON IMAGES (DO NOT USE NEIGHBORHOOD) #####

    @staticmethod
    def subm(f, g):
        """This fuction will be subtract f by g
        input:
          - f: input image
          - g: input image
        output:
          - y: result of subtraction
        """
        # return cv2.subtract(f,g)
        return np.maximum(f - g, 0)

    @staticmethod
    def addm(f, g):
        """This fuction will be add f by g
        input:
          - f: input image
          - g: input image
        output:
          - y: result of add
        """
        return cv2.add(f, g)

    @staticmethod
    def union(f, g):
        """This fuction will be union f by g
        input:
          - f: input image
          - g: input image
        output:
          - y: result of add
        """
        return np.maximum(f, g)

    @staticmethod
    def hist(img):
        """Função para retornar o histograma
          Sintaxe:
            hist = hist(img)
            input: image
            output hist
        """
        H = np.zeros(np.max(img) + 1, dtype=int)
        for i in range(len(img.flatten())):
            cor = img.flatten()[i]
            H[cor] += 1
        return np.asarray(H)

    @staticmethod
    def histPlus(img):
        """Função para retornar o histograma e todos os pixels de cada cor
          Sintaxe:
            hist, dict = histPlus(img)
            input: image
            output hist e dict
        """
        H = np.zeros(np.max(img) + 1, dtype=int)
        vet = {}  # cria um dicionário para os pixels de cada cor
        for i in range(len(img.flatten())):
            cor = img.flatten()[i]
            H[cor] += 1
            if str(cor) in vet.keys():
                vet[str(cor)].append(i)
            else:
                vet[str(cor)] = [i]
        return H, vet

    @staticmethod
    def equalizacao(image):
        """Função para retornar a imagem equalizada pelo valor máximo
          Sintaxe:
            imgEqu = equalizacao(image)
            input: image
            output imgEqu
        """

        @staticmethod
        def somaAcumulada(prob):
            soma = np.zeros(len(prob))
            soma[0] = prob[0]
            for i in range(1, len(prob)):
                soma[i] = soma[i - 1] + prob[i]
            return np.asarray(soma)

        hist = mm.hist(image)  # histograma
        prob = hist / sum(hist)  # probabilidades
        soma = somaAcumulada(prob)  # função de distribuição acumulada
        soma = soma * (np.max(image))  # multiplicando pelo valor máximo da img

        soma = np.round(soma)  # arredondando para obter os níveis de cinza correspondetes

        l, c = image.shape
        imgEqua = np.zeros([l, c])
        for i in range(l):
            for j in range(c):
                imgEqua[i, j] = soma[image[i, j]]
        return imgEqua.astype('int')

    #### MINKOWSKI SUM ####

    @staticmethod
    def sesum(b, n=0):
        """This function will be create a structure function nB by Minkowski sum B
        input:
          - b: structure fuction
          - n: number of sum
        output:
          - y: result of Minkowski sum
        """

        def _sesum(nb, b):
            h, w = b.shape
            nbh, nbw = nb.shape
            H = nbh + h - 1 if h % 2 else nbh + h
            W = nbw + w - 1 if w % 2 else nbw + w
            Hc, Wc = H // 2, W // 2
            r = np.zeros((H, W)).astype('uint8')
            r[h // 2:-(h // 2), w // 2:-(w // 2)] = nb
            return cv2.dilate(r, b).astype('uint8')

        B = b.copy()
        for i in range(n):
            B = _sesum(B, b)
        return B

    @staticmethod
    def sebox(n=0):
        """This function will be create a box structure function nB by Minkowski sum B
        input:
          - n: number of sum
        output:
          - y: result of Minkowski sum
        """
        B = mm.sebox()
        return mm.sesum(B, n)

    @staticmethod
    def secross(n=0):
        """This function will be create a cross structure function nB by Minkowski sum B
        input:
          - n: number of sum
        output:
          - y: result of Minkowski sum
        """
        B = mm.sebox()
        B[0, 0] = B[0, 2] = B[2, 0] = B[2, 2] = 0
        return mm.sesum(B, n)

    @staticmethod
    def sedisk(n=3):
        """This function will be create a disk structure function
        input:
          - n: number of sum
        output:
          - y: result of disk
        """
        return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n))

    #### BASIC MORPHOLOGICAL OPERATORS ####

    @staticmethod
    def ero(f, Bc=np.zeros((3, 3), dtype='uint8')):
        """This function will create an erosion of f by Bc
        input:
         - f: input image
         - Bc: structuring element
        output:
         - y: result of filter
        """
        try:
            return cv2.erode(f, Bc)
        except:  # with weight in Bc
            return mm.ero1(f, Bc)

    @staticmethod
    def dil(f, Bc=np.zeros((3, 3), dtype='uint8')):
        """This function will create an dilate of f by Bc
        input:
         - f: input image
         - Bc: structuring element
        output:
         - y: result of filter
        """
        try:
            return cv2.dilate(f, Bc)
        except:  # with weight in Bc
            return mm.dil1(f, Bc)

    @staticmethod
    def ero0(f, Bc=np.zeros((3, 3), dtype='uint8')):
        """This function will create an erosion of f by Bc
        input:
         - f: input image
         - Bc: structuring element
        output:
         - y: result of filter
        """
        H, W = f.shape
        Bh, Bw = Bc.shape
        g = f.copy()  # nas listas, as vezes eu uso assim

        # para varrer imagem na ordem raster
        for y in range(H):  # para cada linha y
            for x in range(W):  # para cada coluna x

                # para cada vizinho de (x,y)
                for by in range(Bh):
                    for bx in range(Bw):
                        viz_y = int(y + by - Bh / 2 + 0.5)
                        viz_x = int(x + bx - Bw / 2 + 0.5)

                        # verificar o domínion da image
                        if Bc[by, bx] and 0 <= viz_y < H and 0 <= viz_x < W:

                            # para calcular o mínino dos vizinhos
                            if g[y, x] > f[viz_y, viz_x]:
                                g[y, x] = f[viz_y, viz_x]
        return g

    @staticmethod
    def dil0(f, Bc=np.zeros((3, 3), dtype='uint8')):
        """This function will create a dilate of f by Bc
        input:
         - f: input image
         - Bc: structuring element
        output:
         - y: result of filter
        """
        H, W = f.shape
        Bh, Bw = Bc.shape
        Bcy, Bcx = Bh / 2, Bw / 2
        g = f.copy()  # nas listas, as vezes eu uso assim

        # para varrer imagem na ordem raster
        for y in range(H):  # para cada linha y
            for x in range(W):  # para cada coluna x

                # para cada vizinho de (x,y)
                for by in range(Bh):
                    for bx in range(Bw):
                        viz_x = int(x + bx - Bcx + 0.5)
                        viz_y = int(y + by - Bcy + 0.5)

                        # verificar o domínion da image
                        if Bc[by, bx] and 0 <= viz_x < W and 0 <= viz_y < H:

                            # para calcular o máximo dos vizinhos
                            if g[y, x] < f[viz_y, viz_x]:
                                g[y, x] = f[viz_y, viz_x]
        return g

    @staticmethod
    def ero1(f, b=np.zeros((3, 3), dtype='uint8')):
        """This function will create an erosion of f by b
        input:
         - f: input image
         - b: structuring element
        output:
         - y: result of filter
        """
        H, W = f.shape
        Bh, Bw = b.shape
        g = f.copy()  # nas listas, as vezes eu uso assim

        # para varrer imagem na ordem raster
        for y in range(H):  # para cada linha y
            for x in range(W):  # para cada coluna x

                # para cada vizinho de (x,y)
                for by in range(Bh):
                    for bx in range(Bw):
                        viz_y = int(y + by - Bh / 2 + 0.5)
                        viz_x = int(x + bx - Bw / 2 + 0.5)

                        # verificar o domínion da image
                        if 0 <= viz_y < H and 0 <= viz_x < W:

                            # para calcular o mínino dos vizinhos
                            if g[y, x] > f[viz_y, viz_x] - b[by, bx]:
                                g[y, x] = f[viz_y, viz_x] - b[by, bx]
        return g

    @staticmethod
    def dil1(f, b=np.zeros((3, 3), dtype='uint8')):
        """This function will create a dilate of f by b
        input:
         - f: input image
         - b: structuring element
        output:
         - y: result of filter
        """
        H, W = f.shape
        Bh, Bw = b.shape
        g = f.copy()  # nas listas, as vezes eu uso assim

        # para varrer imagem na ordem raster
        for y in range(H):  # para cada linha y
            for x in range(W):  # para cada coluna x

                # para cada vizinho de (x,y)
                for by in range(Bh):
                    for bx in range(Bw):
                        viz_y = int(y + by - Bh / 2 + 0.5)
                        viz_x = int(x + bx - Bw / 2 + 0.5)

                        # verificar o domínion da image
                        if 0 <= viz_y < H and 0 <= viz_x < W:

                            # para calcular o mínino dos vizinhos
                            if g[y, x] < f[viz_y, viz_x] + b[by, bx]:
                                g[y, x] = f[viz_y, viz_x] + b[by, bx]
        return g

    @staticmethod
    def correlacao0(F, kernel, bias):
        """This function will create an correlation of f by b
        input:
        - f: input image
        - b: kernel
        output:
        - y: result of filter
        """
        Bh, Bw = kernel.shape
        if (Bh == Bw):  # apenas para kernel quadrado
            H, W = f.shape
            H = H - Bh + 1  # REMOVO A BORDA!!!
            W = W - Bw + 1  # REMOVO A BORDA!!!
            new_f = np.zeros((H, W))
            for i in range(H):  # para cada linha i
                for j in range(W):  # para cada coluna j
                    new_f[i][j] = np.sum(f[i:i + Bh, j:j + Bw] * kernel) + bias

        return new_f.astype(np.uint8)

    ##### MORPHOLOGICAL OPERATORS USING DILATATION OR EROSION #####

    @staticmethod
    def gradm(f, b=np.zeros((3, 3), dtype='uint8')):
        """This fuction will be dilate f by b minus erodel f by b
        input:
          - f: input image
          - b: neighbors
        output:
          - y: result of condictional dilations
        """
        return mm.subm(mm.dil(f, b), mm.ero(f, b))

    @staticmethod
    def cero(f, g, b=np.zeros((3, 3), dtype='uint8'), n=1):
        """This fuction will be erode g with maximum f, n times
        input:
          - f: input image
          - g: mark image
          - b: neighbors
          - n: number of iterations
        output:
          - y: result of condictional erodes
        """
        y = np.maximum(f, g)
        for i in range(n):
            d = cv2.erode(y, b)
            y = np.maximum(d, g)
        return y

    @staticmethod
    def cdil(f, g, b=np.zeros((3, 3), dtype='uint8'), n=1):
        """This fuction will be dilate g with minimum f, n times
        input:
          - f: input image
          - g: mark image
          - b: neighbors
          - n: number of iterations
        output:
          - y: result of condictional dilations
        """
        y = np.minimum(f, g)
        for i in range(n):
            d = cv2.dilate(y, b)
            y = np.minimum(d, g)
        return y

    @staticmethod
    def infrec(f, g, b=np.zeros((3, 3), dtype='uint8')):
        """This function will be dilate g with minimum f, until converge
        input:
          - f: input image
          - g: mark image
          - b: neighbors
        output:
          - y: result of inf-reconstruction
        """
        y = np.minimum(f, g)
        y1 = np.zeros_like(f)
        while not np.array_equal(y, y1):
            y1 = y
            d = cv2.dilate(y, b)
            y = np.minimum(d, g)
        return y

    @staticmethod
    def suprec(f, g, b=np.zeros((3, 3), dtype='uint8')):
        """This function will be erode g with maximum f, until converge
        input:
          - f: input image
          - g: mark image
          - b: neighbors
        output:
          - y: result of sup-reconstruction
        """
        y = np.maximum(f, g)
        y1 = np.ones_like(f) * 255
        while not np.array_equal(y, y1):
            y1 = y
            d = cv2.erode(y, b)
            y = np.maximum(d, g)
        return y

    @staticmethod
    def closerec(f, b=np.zeros((3, 3), dtype='uint8'), bc=np.zeros((3, 3), dtype='uint8')):
        """This function will be erode g with maximum f, until converge
        input:
          - f: input image
          - b: mark image
          - bc: neighbors
        output:
          - y: result of sup-reconstruction
        """

        return mm.suprec(f, mm.dil(f, b), bc)

    @staticmethod
    def areaopen(f, a):
        """This function will be dilate g with minimum f, until converge
        input:
          - f: input image
          - a: area
          #- Bc: neighbors
        output:
          - y: result of areaopen
        """

        def _areaopen(f, a):
            y = np.zeros(f.shape).astype(int)
            if mm.binary(f):  # binary
                num_labels, labels_im = cv2.connectedComponents(f)
                for i in range(1, num_labels):
                    area = np.sum(labels_im[labels_im == i] > 0)
                    if area > a:  # filtra por área aproximada
                        # print('area:',area)
                        y[labels_im == i] = area
            else:  # gray scale
                hist, bins = np.histogram(f.ravel(), 256, [0, 256])
                for cor, h in enumerate(hist):
                    if h and cor:
                        # print('>>cor:',cor)
                        ret, fcor = cv2.threshold(f, cor, 255, cv2.THRESH_BINARY)
                        fo = _areaopen(fcor, a)
                        if np.amax(fo) == 0:
                            break
                        y += fo
            return y

        return _areaopen(f, a)

    @staticmethod
    def asf(f, filter='OC', b=np.zeros((3, 3), dtype='uint8'), n=1):
        """This function will create an alternating sequential filter
        input:
          - f: input image
          - b: structuring fuctions
          - n: number of iterations
          - filter: 'OC', 'CO', 'OCO', 'COC' [Default: 'OC']
        output:
          - y: result of filter
        ATENÇÃO:
        """
        filter = filter.upper()
        y = f.copy()
        if filter == 'OC':
            for i in range(n):
                bi = mm.sesum(b, i)
                y = cv2.morphologyEx(y, cv2.MORPH_OPEN, bi)
                y = cv2.morphologyEx(y, cv2.MORPH_CLOSE, bi)
        elif filter == 'CO':
            for i in range(n):
                bi = mm.sesum(b, i)
                y = cv2.morphologyEx(y, cv2.MORPH_CLOSE, bi)
                y = cv2.morphologyEx(y, cv2.MORPH_OPEN, bi)
        elif filter == 'OCO':
            for i in range(n):
                bi = mm.sesum(b, i)
                y = cv2.morphologyEx(y, cv2.MORPH_OPEN, bi)
                y = cv2.morphologyEx(y, cv2.MORPH_CLOSE, bi)
                y = cv2.morphologyEx(y, cv2.MORPH_OPEN, bi)
        elif filter == 'COC':
            for i in range(n):
                bi = mm.sesum(b, i)
                y = cv2.morphologyEx(y, cv2.MORPH_CLOSE, bi)
                y = cv2.morphologyEx(y, cv2.MORPH_OPEN, bi)
                y = cv2.morphologyEx(y, cv2.MORPH_CLOSE, bi)

        return y

    @staticmethod
    def openth(f, b=np.zeros((3, 3), dtype='uint8')):
        return mm.subm(f, cv2.morphologyEx(f, cv2.MORPH_OPEN, b))

    @staticmethod
    def openth1(f, b=np.zeros((3, 3), dtype='uint8')):
        return mm.subm(f, mm.dil1(mm.ero1(f, b), b))

    @staticmethod
    def closeth(f, b=np.zeros((3, 3), dtype='uint8')):
        return mm.subm(cv2.morphologyEx(f, cv2.MORPH_CLOSE, b), f)

    @staticmethod
    def closerecth(f, b=np.zeros((3, 3), dtype='uint8')):
        return mm.subm(cv2.morphologyEx(f, cv2.MORPH_CLOSE, b), f)

    @staticmethod
    def open(f, b=np.zeros((3, 3), dtype='uint8')):
        return cv2.morphologyEx(f, cv2.MORPH_OPEN, b)

    @staticmethod
    def close(f, b=np.zeros((3, 3), dtype='uint8')):
        return cv2.morphologyEx(f, cv2.MORPH_CLOSE, b)

    @staticmethod
    def water0(f, b=np.zeros((3, 3), dtype='uint8'), op='region'):
        """This function will create the watershed
          input:
            - f: input binary image
            - op: regions of watershed

          output:
            - y: watershed
        """
        f = mm.label0(f, b)
        h, w = f.shape
        bh, bw = b.shape
        g = f.copy()
        while np.amin(g) == 0:
            for x in range(h):
                for y in range(w):
                    for bx in range(bh):
                        for by in range(bw):
                            viz_x = int(x + bx - bh / 2 + 0.5)
                            viz_y = int(y + by - bw / 2 + 0.5)
                            if 0 <= viz_x < h and 0 <= viz_y < w:
                                if g[x, y] == 0 and g[x, y] < f[viz_x, viz_y]:
                                    g[x, y] = f[viz_x, viz_y]
            f = g.copy()

        if op == 'region':
            return g
        elif op == 'line':
            return mm.gradm(g, mm.secross())

    @staticmethod
    def waterB(f, m, b=np.zeros((3, 3), dtype='uint8'), op='region'):
        """This function will create the watershed, process only border pixel of each object
          input:
            - f: input binary image
            - op: regions of watershed

          output:
            - y: watershed
        """
        m = mm.label0(m, b)
        h, w = m.shape
        bh, bw = b.shape
        queue = []
        for x in range(h):
            for y in range(w):
                if m[x, y]:
                    for bx in range(bh):
                        for by in range(bw):
                            viz_x = int(x + bx - bh / 2 + 0.5)
                            viz_y = int(y + by - bw / 2 + 0.5)
                            if 0 <= viz_x < h and 0 <= viz_y < w:
                                if not m[viz_x, viz_y]:
                                    queue.append([abs(f[x, y] - f[viz_x, viz_y]), x, y])

        while len(queue):
            # queue = sorted(queue, key=lambda a:a[0])
            cor_diff, x, y = queue.pop(0)
            cor = m[x, y]
            for bx in range(bh):
                for by in range(bw):
                    viz_x = int(x + bx - bh / 2 + 0.5)
                    viz_y = int(y + by - bw / 2 + 0.5)
                    if 0 <= viz_x < h and 0 <= viz_y < w:
                        if not m[viz_x, viz_y]:
                            m[viz_x, viz_y] = cor
                            queue.append([abs(f[x, y] - f[viz_x, viz_y]), viz_x, viz_y])

        if op == 'region':
            return m
        elif op == 'line':
            return mm.gradm(m, mm.secross())

    @staticmethod
    def watershed(f, mark, op='region'):
        """This function will create the watershed
          input:
            - f: input image
              - f==[] # binary watershed by skimage
              - else  # condictional watershed by cv2
            - mark: markers image
            - op: region or line [default: region]

          output:
            - y: watershed
        """

        mark = mark * 255 if np.amax(mark) == 1 else mark

        if len(f):  # condictional watershed by cv2

            ret, markers = cv2.connectedComponents(mark)
            w = cv2.watershed(f, markers)
            if op == 'line':
                f[markers == -1] = [255, 0, 0]
                return f
            else:
                return w

        else:  # binary watershed by skimage

            from scipy import ndimage as ndi
            from skimage.segmentation import watershed
            fones = np.ones_like(mark) * 255
            markers = ndi.label(mark)[0]
            w = watershed(fones, markers, mask=fones)

            if op == 'line':
                return np.array((w - cv2.erode(w.astype('uint16'), mm.sebox())) > 0).astype('uint16')
            else:
                return w

    @staticmethod
    def regmax(f, b=np.ones((3, 3), dtype='uint8')):
        """This function will be calculate region maximum
        input:
          - f: input image
          - b: neighbors
        output:
          - y: result of regmax
        """
        if np.amax(f) <= 255:
            k = 255
        else:
            k = 65535
        fminus = mm.subm(f, 1)
        g = mm.subm(f, mm.infrec(fminus, f, b))
        return mm.union(mm.threshold(g, 0), mm.threshold(f, k))

    @staticmethod
    def regmin(f, b=np.ones((3, 3), dtype='uint8')):
        """This function will be calculate region minimum
        input:
          - f: input image
          - b: neighbors
        output:
          - y: result of regmax
        """
        fplus = mm.addm(f, 1);
        g = mm.subm(mm.suprec(fplus, f, b), f);
        return mm.union(mm.threshold(g, 1), mm.threshold(f, 0))

    def blob(f, op='area', border=1, precision=0.01, show='True'):
        """This function will be calculate topology of each connect component
        input:
          - f: input image
          - op: 'area', 'perimeter', etc [default='area']
          - border: border of lines [default=1]
          - precision: precision of polygonon [default=0.01]
          - show=True, return image, else, return measure
        output:
          - y: image with op or measure
        """
        if mm.binary(f):  # binary
            measures = []
            cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
            if op == 'area':
                color_img = np.zeros_like(f).astype('uint32')
                num_labels, labels_im = cv2.connectedComponents(f)
                for i in range(1, num_labels):
                    area = np.sum(labels_im[labels_im == i] > 0)
                    measures.append(area)
                    color_img[labels_im == i] = area

            elif op == 'textLabel':
                for k, c in enumerate(cont):
                    x, y, w, h = cv2.boundingRect(c)
                    measures.append(k + 1)
                    cv2.putText(color_img, str(k + 1), (x + w // 3, y + h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.2,
                                (255, 0, 0), border, cv2.LINE_AA)

            elif op == 'textPer':
                cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
                for k, c in enumerate(cont):
                    perimeter = int(cv2.arcLength(c, True))
                    measures.append(perimeter)
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.putText(color_img, str(perimeter), (x + w // 3, y + h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.2,
                                (255, 0, 0), border, cv2.LINE_AA)

            elif op == 'textArea':
                cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
                for k, c in enumerate(cont):
                    area = int(cv2.contourArea(c))
                    measures.append(area)
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.putText(color_img, str(area), (x + w // 3, y + h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.2,
                                (255, 0, 0), border, cv2.LINE_AA)

            elif op == 'box':
                color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
                cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                for c in cont:
                    rect = cv2.minAreaRect(c)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    measures.append(box)
                    cv2.drawContours(color_img, [box], 0, (255, 0, 0), border)

            elif op == 'rect':
                color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
                cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                for c in cont:
                    x, y, w, h = cv2.boundingRect(c)
                    measures.append([x, y, w, h])
                    cv2.rectangle(color_img, (x, y), (x + w, y + h), (0, 255, 0), border)

            elif op == 'circle':
                color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
                cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                for c in cont:
                    (x, y), radius = cv2.minEnclosingCircle(c)
                    center = (int(x), int(y))
                    radius = int(radius)
                    measures.append([center, radius])
                    cv2.circle(color_img, center, radius, (0, 255, 0), border)

            elif op == 'ellipse':
                color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
                cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                for c in cont:
                    ellipse = cv2.fitEllipse(c)
                    measures.append(ellipse)
                    cv2.ellipse(color_img, ellipse, (0, 255, 0), border)

            elif op == 'convex':
                color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
                cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                for c in cont:
                    hull = cv2.convexHull(c)
                    measures.append(hull)
                    cv2.drawContours(color_img, [hull], 0, (255, 0, 0), border)

            elif op == 'poly':
                color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
                cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                for c in cont:
                    epsilon = precision * cv2.arcLength(c, True)
                    approx = cv2.approxPolyDP(c, epsilon, True)
                    measures.append(approx)
                    cv2.drawContours(color_img, [approx], 0, (255, 0, 0), border)

            elif op == 'line':
                color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
                cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                for c in cont:
                    ellipse = cv2.fitEllipse(c)
                    cv2.ellipse(color_img, ellipse, (255, 0, 0), border)

                    rows, cols = f.shape[:2]
                    [vx, vy, x, y] = cv2.fitLine(c, cv2.DIST_L2, 0, 0.01, 0.01)
                    measures.append([vx, vy, x, y])
                    lefty = int((-x * vy / vx) + y)
                    righty = int(((cols - x) * vy / vx) + y)
                    cv2.line(color_img, (cols - 1, righty), (0, lefty), (0, 255, 0), border)

            if show:
                mm.show(color_img)
                return color_img
            else:
                return measures

    def blobAll(f, border=1, precision=0.01, show='False'):
        """This function will be calculate topology of each connect component
        input:
          - f: input image
          - border: border of lines [default=1]
          - precision: precision of polygonon [default=0.01]
          - show=False, return measure
        output:
          - y: measures
        """
        num_labels, labels = cv2.connectedComponents(f)
        measures_all = ['textLabel', 'textArea', 'textPer', 'box', 'rect',
                        'circle', 'ellipse', 'convex', 'poly', 'line']
        measures_vect = {k: [] for k in measures_all}
        for i in range(np.amax(labels)):
            for m in measures_all:
                aux = np.zeros_like(labels).astype('uint8')
                aux[labels == i] = 255
                measures_vect[m].append(mm.blob(aux, m, 1, 0.01, False)[0])
        return measures_vect

    def intersec(f1, f2):
        return np.minimum(f1, f2)

    @staticmethod
    def toggle(f, f1, f2, op='gray'):
        """This function will be calculate label of each connect component
        input:
          - f: input image
          - f1: input image
          - f2: input image
          - op: input image
        output:
          - y: image with op
        """
        f11 = mm.subm(f, f1)
        f22 = mm.subm(f2, f)
        g = np.logical_and((f11 <= f), (f <= f22))
        if op == 'gray':
            t = np.array(g, dtype='uint8') * 255
            g = mm.union(mm.intersec(mm.neg(t), f1), mm.intersec(t, f2))
        return g

    @staticmethod
    def label(f):
        """This function will be calculate label of each connect component
        input:
          - f: input image
        output:
          - y: image with op
        """
        num_labels, labels_im = cv2.connectedComponents(f)
        return labels_im

    @staticmethod
    def label0(f, b=np.ones((3, 3), dtype='uint8')):
        """This function will be calculate label of each connect component
        input:
          - f: input image
          - b: structure element
        output:
          - y: image with op
        """
        h, w = f.shape
        bh, bw = b.shape

        g = np.zeros(f.shape).astype(int)
        cor = 1
        pilha = []
        for x in range(h):
            for y in range(w):

                if (f[x, y]) and not g[x, y]:  # buscar pixel de objeto não pintado

                    pilha.append([x, y])  # colocar na pilha pixel p=[x,y]

                    while pilha:  # laço para pintar todos os pixel de cada objeto com cor
                        i, j = pilha.pop()  # retirar da pilha pixel q=[i,j]
                        g[i, j] = cor

                        # para cada vizinho de (i,j)
                        for bx in range(bh):
                            for by in range(bw):
                                if b[bx, by]:
                                    viz_x = int(i + bx - bh / 2 + 0.5)
                                    viz_y = int(j + by - bw / 2 + 0.5)
                                    # verificar o domínion da image
                                    if 0 <= viz_x < h and 0 <= viz_y < w:
                                        if f[viz_x, viz_y] and not g[viz_x, viz_y]:  # colocar na pilha
                                            pilha.append([viz_x, viz_y])  # somente pixels não visitados e =1

                    cor += 1  # incremento para pintar o próximo objeto
        return g

    @staticmethod
    def dist(f):
        """This function will be calculate euclidean distance of each connect component
        input:
          - f: input image
        output:
          - y: image with op
        """
        y = cv2.distanceTransform(f, cv2.DIST_L2, 5)
        if np.amax(y) <= 255:
            y = y.astype('uint8')
        else:
            y = y.astype('uint16')
        return y

    @staticmethod
    def dist1(f, b):
        """This function will be calculate distance by erosions
        input:
          - f: input image
        output:
          - y: image with op
        """
        g = f.copy()
        while True:
            f = g.copy()
            g = mm.ero1(g, b)
            if np.array_equal(f, g): break
        return g

    @staticmethod
    def gdist(f, g, b=np.ones((3, 3), dtype='uint8')):
        """This function will be calculate geodesic distance with erode neg of g intersect f
        input:
          - f: input binary image with 0 and 1
          - g: marker - input binary image with 0 and 1
          - b: kernel
        output:
          - y: image with op
        """
        h, w = f.shape
        max = h * w
        fneg = (max - f * max).astype('uint16')
        gneg = (1 - g).astype('uint16')
        c = 0
        y = gneg
        while True and c < 1000000:
            c += 1
            y0 = y
            log = np.logical_xor(gneg, fneg)
            y = log * (y + mm.cero(gneg, fneg, b, c))
            if np.array_equal(y0, y):
                break
        return y

    @staticmethod
    def thin(f):
        """This function will be calculate the skeleton of image
        input:
          - f: input image
        output:
          - y: image with skeleton
        """
        from skimage.morphology import skeletonize

        return np.array(skeletonize(f)).astype('uint8')

    @staticmethod
    def frame(f, border=5):
        """This function will be return a frame of image
        input:
          - f: input image
          - border: default=5
        output:
          - y: image
        """
        g = np.ones_like(f) * 255
        g[border:-border, border:-border] = 0
        return g

    def edgeoff(f, b=np.ones((3, 3), dtype='uint8')):
        """This function will be remove border componentes
        input:
          - f: input image
          - b: structiring function
        output:
          - y: image
        """
        return mm.subm(f, mm.infrec(mm.frame(f), f, b))

    @staticmethod
    def clohole(f, b=np.ones((3, 3), dtype='uint8')):
        """This function will be close hole of image
        input:
          - f: input image
        output:
          - y: image
        """
        frame = mm.frame(f)
        return mm.neg(mm.infrec(frame, mm.neg(f), b))

    @staticmethod
    def neg(f):
        """This function will be return the inverting image
        input:
          - f: input image
        output:
          - y: image
        """
        return cv2.bitwise_not(f)

    def hmin(f, h, b=np.ones((3, 3), dtype='uint8')):
        """sup-reconstructs the gray-scale image f
           from the marker created by the addition of the positive integer value h to f
        input:
          - f: input image
          - b: structiring function
        output:
          - y: image
        """
        g = mm.addm(f, h)
        return mm.suprec(f, g, b)

    def skelm(f, b=np.zeros((3, 3), dtype='uint8')):
        """versão corrigida em 2/3/2023
        essa implementação NÃO roda na lista3 até 2023.1
        """
        global sesum, ero1, dil1
        img = f.copy()
        skel = np.zeros((f.shape))
        ero = np.ones((f.shape))
        n = 0
        while np.max(ero):
            nb = mm.sesum(b, n)
            ero = mm.ero1(img, nb)
            Sn = ero - mm.dil1(mm.ero1(ero, b), b)  # mm.subm dá underflow pois usa uint8
            skel = np.maximum(skel, Sn)
            # print(f'n={n} nb=\n{mm.drawImage(nb)}\nero=\n{mm.drawImage(ero)}\nSn=\n{mm.drawImage(Sn)}\n')
            n += 1
        return skel

    def skel(f):  # implementação do cv2
        """implementação do cv2
        https://docs.opencv.org/4.x/df/d2d/group__ximgproc.html#ga37002c6ca80c978edb6ead5d6b39740c
        técnica de Zhang-Suen: http://rstudio-pubs-static.s3.amazonaws.com/302782_e337cfbc5ad24922bae96ca5977f4da8.html
        """
        return cv2.ximgproc.thinning(f)

    # essa implementação é a do enunciado e
    # RODA na lista3 de 2022.1
    # porém, não calcula corretamento o esqueleto
    def esqueleto(f, b):
        global dilatacao, erosao, sesum
        img = f.copy()
        skel = np.zeros((f.shape))
        n = 0
        while np.max(img):
            nb = mm.sesum(b, n)
            abertura = mm.dil1(mm.ero1(img, b), b)
            skel = np.logical_or(skel, np.logical_and(img, np.logical_not(abertura))).astype(int)
            img = mm.ero1(img, nb)
            n += 1
        return skel

    def verifyBoundBox(object, center, matrix, width, height):
        """ Função interessante para verificar se conseguiu segmentar corretamente imagens comparando com gabaritos (matriz lide de TXT).
            Ver exemplos de datasets: https://storage.googleapis.com/openimages/web/visualizer/index.html
            Utilizar OIDv4 para baixar exemplos: https://github.com/theAIGuysCode/OIDv4_ToolKit

            A matriz contem um boundbox normalizado por linha do arquivo TXT para cada objeto. Para ler essa matriz:

                import pandas as pd
                df = pd.read_csv("00001.txt", sep='\t', header=None)
                matrix = df.to_numpy()

                As colunas têm objetos, p1=[x1,y1] e p2=[x2,y2] (valores nomalizados entre 0 e 1 - são os dois pontos extremos para definir o retângulo)
            input:
              - object: é um dos índices dos objetos segmentados - valores entre 0 e 8 (n=9 objetos segmentados)
              - center: centro=[x,y] de massa do objeto segmentado
              - matrix: matriz objetos e bounding boxes, em cada linha tem: [i x1 y1 x2 y2]
              - width: largura da imagem
              - height: altura da imagem
            output:
              - correct: conseguiu segmentar corretamente se retorno correct = 1
        """
        import numpy as np
        correct = 0
        for v in matrix[matrix[:, 0] == object]:
            p1 = v[1:][:2] * [width, height] // 1
            p2 = v[1:][2:] * [width, height] // 1
            if (p1 < np.array(center)).all() and (np.array(center) < p2).all():
                correct += 1
        return correct


'''
O problema na questão do esqueleto da lista3:

Implementei duas versões no final do arquivo morph.py

O problema surgiu pois considerei implementações da sugestão que está na lista.

O ideal é considerar pesos nos vizinhos! Não temos controle sobre esses pesos e na origem do kernel nas implementações do OpenCV.

Neste arquivo morph.py estão quase todas as implementações necessárias para fazer as listas, basta saber utiliza corretamente os métodos de entrada e de processamento.

Padronizei esse arquivo com: 
 * mm.operacao0, para tratar erosão e dilatação sem pesos nos vizinhos, porém somente valores > 0
 * mm.operacao1, tem pesos nos vizinhos. Exemplos
 * mm.operacao, implementação do opencv - pois são mais rápidas para serem aplicadas na segunda parte do curso: Visão Computacional.

mm.ero0
mm.ero1
mm.ero
'''




