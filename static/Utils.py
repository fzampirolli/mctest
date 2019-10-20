# coding=UTF-8

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


''' drawMatrix
desc: create an image from a matrix
input: matrix
output: file in server
syntax: drawMatrix(A,myfile)
author: Francisco Zampirolli
date: august 2019

ex: 
In the description of the question, draw this picture with (copy below for a new question):
\begin{figure}[h!]
\centering{
  \includegraphics[scale=0.55]{[[code:fig0]]} 
}
\end{figure}

[[def:
import numpy as np
Lin=2 
Col=3 
A = np.random.random((Lin, Col))*10
A = A.astype(int)
fig0 = 'myfigExample01'
drawMatrix(A,fig0)
fig0 = 'myfigExample01'
drawMatrix(A,fig0)
]]
'''
def drawMatrix(A,myfile):
  import matplotlib.pyplot as plt
  fig, ax = plt.subplots()
  mat = ax.imshow(A, cmap='Pastel1', interpolation='nearest')
  for x in range(A.shape[0]):
    for y in range(A.shape[1]):
        ax.annotate(str(A[x, y])[0], xy=(y, x), horizontalalignment='center', verticalalignment='center')
  plt.show()
  fig.savefig('./tmp/'+ myfile +'.png', dpi=300)
  plt.close()