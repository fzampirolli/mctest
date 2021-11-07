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


def printMatrix(A, title='', left='[', right=']'):
    """
      Draw a matrix
      :param A: matrix numpy
      :param title: title, ex.: title = [...]
      :param left: left symbol
      :param right: right symbol
      :return: string of draw matrix
    """
    A = np.array(A)
    str1 = """
\\setcounter{MaxMatrixCols}{__size__}
\\begin{displaymath}
\\textbf{__title__}
\\left__tleft__
\\begin{matrix}
"""

    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            str1 += str(A[i, j])
            if j < A.shape[1] - 1:
                str1 += "&"
        if i < A.shape[0] - 1:
            str1 += "\\\\"
        str1 += "\n"

    str1 += """\\end{matrix}
\\right__tright__
\\end{displaymath}
    """
    str1 = str1.replace('__tleft__', left).replace('__tright__', right)
    str1 = str1.replace('__title__', title)
    str1 = str1.replace('__size__', str(len(A[0])))
    return str1
