#!/usr/bin/env python
# coding: utf-8

# http://y-okamoto-psy1949.la.coocan.jp/Python/en1/IRTLClassPyMC3/
"""
Yasuharu Okamoto, 2019.02
"""
# mac
# conda install pymc3
# conda install -c conda-forge arviz
#
# linux
# pip3 install pymc3
# pip3 install arviz
# pip3 install matplotlib==3.1.1
# syntax:
# python3 _irt_pymc3_shell.py epufabc2020_irt100.csv >> epufabc2020_irt100.txt &

import sys

import arviz as az
import numpy as np
import pymc3 as pm

if len(sys.argv) != 2:
    print("Use >> python3 _irt_pymc3_shell.py file.csv")
    exit(0)

print("File: " + str(sys.argv[1]))

X = np.genfromtxt(str(sys.argv[1]), delimiter=',', dtype=int)

N = len(X)
M = len(X[0])
NStg = 5  # Number of stages: A=4, B=3, C=0, D=1, F=0
print('N = ', N)  # Number of students
print('M = ', M)  # Number of questions
print('NStg = ', NStg)

a_Diri = np.ones((M, NStg + 1))
a_coeff = np.zeros((NStg, NStg + 1))
for i in range(NStg):
    for j in range(i + 1):
        a_coeff[i][j] = 1
a_p = np.ones(NStg)

with pm.Model() as stage_model:
    prob_steps = pm.Dirichlet('prob_steps', a=a_Diri, shape=(M, NStg + 1))
    coeff = pm.math.constant(a_coeff, 'coeff')
    prob_response_ = pm.math.matrix_dot(coeff, prob_steps.T)
    prob_response = pm.Deterministic('prob_response', prob_response_)
    p_stages = pm.Categorical('p_stages', p=a_p, shape=N)
    p_at_stage = pm.Deterministic('p_at_stage', prob_response[p_stages])
    y = pm.Bernoulli('y', p=prob_response[p_stages], observed=X)
    trace = pm.sample()

summary = az.summary(trace, var_names=['prob_response'])
ary_prob_response = trace['prob_response']

print('\nP(correct|item,stage)\n')
print('{0: >10s}'.format(' '), end='')
for i in range(NStg):
    print("{0:>10s}".format('Stage-{}'.format(i)), end='')
print(' ')

for j in range(M):
    print('Item-{0: <5d}'.format(j + 1), end='')
    for s in range(NStg):
        print('{0: >10.5f}'.format(ary_prob_response[:, s, j].mean()), end='')
    print(' ')

ary_p_stages = trace['p_stages']
ary_p_stages = ary_p_stages.T
print("\nMean stages and their SD's\n")
print('{0: >11s}{1:>10s}{2:>10s}'.format(' ', 'Mean', 'SD'))
for i in range(len(ary_p_stages)):
    print('person-{0: <4d}{1:>10.3f}{2:>10.3f}'.format(i + 1, ary_p_stages[i].mean(),
                                                       ary_p_stages[i].std()))
v_waic = az.waic(trace)

print('\nWAIC = {0:.3f}  for the number of stages = {1}'.format(v_waic['waic'], NStg))
print('\nWAIC statistics...\n', v_waic)
