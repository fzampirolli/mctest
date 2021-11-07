# coding=UTF-8
import json

import numpy as np


def getCasesMoodle(inp, out):
    cases = {}
    cases['input'] = np.array(inp).tolist()
    cases['output'] = np.array(out).tolist()
    return json.dumps(cases)


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
    :param A: matrix
    :param myfile: name of the file defined in [[def: ... ]]
    :return: file in server
    Author: Francisco Zampirolli
    Date: november 2021

      ex:
        In the description of the question, draw this picture with (copy below for a new question):
        \begin{figure}[h!]
        \centering{
          \includegraphics[scale=0.55]{[[code:fig0]]} 
        }
        \end{figure}
        
        [[def:
        Lin,Col = 4,5
        A = np.random.randint(10, size=(Lin,Col))
        fig0 = 'fzfigExample01(row'+str(Lin)+')(col'+str(Col)+')'
        drawMatrix(A,fig0)
        ]]
    """
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    mat = ax.imshow(A, cmap='Pastel1', interpolation='nearest')
    for x in range(A.shape[0]):
        for y in range(A.shape[1]):
            ax.annotate(str(A[x, y])[0], xy=(y, x), horizontalalignment='center', verticalalignment='center')
    plt.show()
    fig.savefig('./tmp/' + myfile + '.png', dpi=300)
    plt.close()


def printMatrix(A, title='', left='[', right=']', align='r', dec='3.2f'):
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
