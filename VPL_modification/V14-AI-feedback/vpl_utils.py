# Setup user
import os, random
USER_ID = int(os.environ['MOODLE_USER_ID'])
USERNAME = os.environ['MOODLE_USER_NAME']
USER_EMAIL = os.environ['MOODLE_USER_EMAIL']

random.seed(USER_ID)

##
# UTILS

def terminate(score=0.0, comments=dict()):
    # GRADEMAX = float(os.environ['VPL_GRADEMAX'])
    # GRADEMIN = float(os.environ['VPL_GRADEMIN'])
    if score < 1.0:
        for title, msg in comments.items():
            print("- " + title)
            print(msg)
        print()
    # print("Grade :=>>{score:.2}".format(score = GRADEMIN + score * (GRADEMAX-GRADEMIN)))
    #print("<|--")

    print(f"GRADE == {round(score*100,2)}")
    #print("--|>")
    
    # print("<|-- ") # início de um comentário
    # print("- Título")
    # print("> pré-formata")
    # print("--|>") # final de um comentário
    

# Main class to generate the exercise
class TesteDeMesa:
    code      = None
    codeLines = None
    table     = None
    minRows   = 3 # Minimum lines that must be identical. It will be provided to the student automatically if not exact.

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
        msg=""
        count = 0
        for line in self.codeLines:
            count = count + 1
            line = re.sub(r'^def ', r'Function ', line)
            line = re.sub(r':$ *', r'', line)

            # Repetition
            line = re.sub(r'for *(.+) *in *(.+)', r'For \1 in \2, do:', line)
            line = re.sub(r'in *range *\((.+) *, *(.+) *\)', r'from \1 until \2 (not included)', line)
            line = re.sub(r'while *(.+)', r'While \1, do:', line)

            # Conditional
            line = re.sub(r'elif *(.+)', r'Else If \1, then:', line)
            line = re.sub(r'if *(.+)', r'If \1, then:', line)
            line = re.sub(r'else', r'Else:', line)

            # Functions
            line = re.sub(r'print *\(.*"(.+)".*\)', r'Print "\1"', line) # print with "
            line = re.sub(r'print *\(.*(.+).*\)', r'Print \1', line) # print without "

            # Return
            line = re.sub(r'^( +)return', r'\1Return', line)

            # Operators
            line = re.sub(r'([a-z0-9]+) *=[^=] *(.*)', r'\1 ← \2', line)
            line = re.sub(r'<=', r'≤', line)
            line = re.sub(r'>=', r'≥', line)
            line = re.sub(r'==', r'=', line)
            line = re.sub(r'!=', r'≠', line)
            line = re.sub(r'([a-z0-9]+) *\* *([a-z0-9]+)', r'\1 × \2', line) # /
            line = re.sub(r'([a-z0-9]+) */ *([a-z0-9]+)', r'\1 ÷ \2', line) # *
            line = re.sub(r'([a-z0-9]+) *% *([a-z0-9]+)', r'\1 mod \2', line) # mod

            # Logic
            line = re.sub(r' and ', r' E ', line)
            line = re.sub(r' or ', r' OU ', line)

            # Cast
            line = re.sub(r'int *\((.*)\)', r'⎣\1⎦', line) # change to floor when int
            line = re.sub(r'(float|str) *\((.*)\)', r'\2', line) # removing other cast

            # Identation
            line = re.sub('    ', '▐ ', line) # Always the last!
            msg = msg + f"{count:02n}: {line}\n"

        return msg


    # Exec code and create the matrix
    def make(self, args):

        # Init
        lines = []
        self.last_line = None
    
        # Nested function, used on setrace
        # https://docs.python.org/3/library/inspect.html
        def my_tracer(frame, event, arg = None):
            # Just trace lines!
            if event != 'line':
                return my_tracer

            # Always using the last line because the current line doesn't have the variables updated
            line_no = frame.f_lineno - frame.f_code.co_firstlineno
            if self.last_line == None:
                self.last_line = line_no
                return

            # Create table
            if 'tracing_func' not in frame.f_locals: # If using pydevd_tracing
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
                if var not in allVars:
                    allVars.append(var)

        # First line
        self.table = [ [ 'Linha' ] + allVars ]

        # Fill table
        for line in lines[:-1]:
            v = [ str(line['line']) ]
            for k in allVars:
                if k in line['vars'].keys():
                    v.append(str(line['vars'][k]))
                else:
                    v.append('?')
            self.table.append(v)
        self.table.append([str(lines[-1]['line']), str(lines[-1]['return'])])

        return func_ret, func_out

    # Print Table
    def show(self, clean = True):
        str = ""
        from copy import deepcopy
        table = deepcopy(self.table)

        if (clean):
            for line in range(len(table)-1, 1, -1):
                for col in range(1, len(table[line])):
                    if table[line][col] == table[line-1][col]:
                       table[line][col] = ''

        # Print table
        for line in table:
            str = str + f"{line[0]:^8}"
            for col in range(1, len(line)):
                str = str + f"{line[col]:^8}"
            str = str + '\n' # f"{line[1]}"
        return str #.replace(' ', '_')

    @staticmethod
    def str2table(str):
        line = 1
        tbl = []
        for row in str.splitlines():
            cols = []
            for col in row.strip().split(' '):
                if col.strip() != '':
                    cols.append(col.strip())
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
    def correct(self, answers):
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
            for i in range (self.minRows, len(self.table)):
                isCorrect = True
                if len(answers) <= i:
                    break
                if len(self.table[i]) != len(answers[i]):
                    if i == len(self.table) - 1:
                        feedback = f"A última linha deve conter apenas o número da linha de retorno e o valor retornado." + \
                            "\nUtilize '?' se não houver valor retornado."
                    else:
                        feedback = f"Linha {i+1} tem {len(answers[i])} colunas, mas o esperado é ter {len(self.table[i])} colunas." + \
                            "\nObs.: Utilize '?' se você quer representar um valor indefinido."
                    isCorrect = False
                elif i != 0:
                    if not answers[i][0].isnumeric():
                        feedback = f"A primeira coluna da linha {i+1}, que representa o número da linha, precisa ser inteiro."
                    for j in range(1, len(answers[i])):
                        if not answers[i][j].isnumeric() and answers[i][j] != '?':
                            feedback = f"A coluna {j+1} da linha {i+1} precisa ter um valor inteiro ou '?' caso for indefinido."
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
            if len(self.table) == len(answers):
                feedback = "Perfeito."
            else:
                feedback = "O teste de mesa contém um ou mais erros..."
        
        return corrects / ( len(self.table) - self.minRows ), feedback
    