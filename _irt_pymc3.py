# coding: utf-8
# http://y-okamoto-psy1949.la.coocan.jp/Python/en1/IRTLClassPyMC3/

import os
# pip3 install pymc3
# pip3 install arviz
import arviz as az
import pymc3 as pm
import numpy as np

import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.http import Http404

os.system('source ../_settings.env')

from mctest.settings import BASE_DIR
from mctest.settings import webMCTest_FROM
from mctest.settings import webMCTest_PASS
from mctest.settings import webMCTest_SERVER

print("Starting IRT...")

print("File: "+str(sys.argv[1]))

file_name = str(sys.argv[1])
s = file_name.split('/')
s = s[len(s)-1].split('_')
destinatario = s[2]

print("Destination: " + destinatario)

msg = "\n"
msg += "Prezado(a), \n\n"
msg += "Seguem algumas estatísticas das correções. \n\n"
msg += "Att, \nFrancisco de Assis Zampirolli\n\n"
msg += "REF.: http://y-okamoto-psy1949.la.coocan.jp/Python/en1/IRTLClassPyMC3/ \n\n"

msg += "==================================================\n\n"

msg += "File: %s\n\n" % "_".join([i for i in s[3:-1]])

X = np.genfromtxt(file_name, delimiter=',', dtype=int)
N = len(X)
M = len(X[0])

NStg = 5  # Number of stages: A=4, B=3, C=0, D=1, F=0

msg += 'N = %s       Number of students  \n' % N
msg += 'M = %s     Number of questions \n' % M
msg += 'NStg = %s  Number of stages, for ex. 0=F, 1=D, 2=C, 3=B, 4=A \n' % NStg

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

msg += '\nP(correct|item,stage)\n'
msg += '{0: >10s}'.format(' ')

for i in range(NStg):
    msg += "{0:>10}".format('Stage-{}'.format(i))
msg += '\n'
for j in range(M):
    msg += 'Item-{0: <7d}'.format(j+1)
    for s in range(NStg):
        msg += '{0: >10.5f}'.format(ary_prob_response[:, s, j].mean())
    msg += '\n'

ary_p_stages = trace['p_stages']
ary_p_stages = ary_p_stages.T
msg += "\nMean stages and their SD's\n"
msg += '{0: >11s}{1:>10s}{2:>10s}\n'.format(' ', '    Mean', 'SD')
for i in range(len(ary_p_stages)):
    msg += 'person-{0: <4d}{1:>10.3f}{2:>10.3f}\n'.format(i+1, ary_p_stages[i].mean(),
                                                       ary_p_stages[i].std())
v_waic = az.waic(trace)

msg += '\nWAIC = {0:.3f}  for the number of stages = {1}'.format(v_waic['waic'], NStg)
msg += '\nWAIC statistics... %s\n' % v_waic

def envia_email(servidor, porta, FROM, PASS, TO, subject, texto, anexo=[]):
    msg = MIMEMultipart()
    msg['From'] = FROM
    msg['To'] = TO
    msg['Subject'] = subject
    msg.attach(MIMEText(texto))

    # Anexa os arquivos
    for f in anexo:
        # print(">>>>$$$$>>>>",f)
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment;filename="%s"' % os.path.basename(f))
        msg.attach(part)

    try:
        gm = smtplib.SMTP(servidor, porta)
        gm.ehlo()
        gm.starttls()
        gm.ehlo()
        gm.login(FROM, PASS)
        gm.sendmail(FROM, TO, msg.as_string())
        gm.close()
        print("Sending email ...")
    except Exception:
        raise Http404(
            "Nao Foi Possivel Enviar o Email.\n Error:" + str([servidor, porta, FROM, TO, subject, texto, anexo]))


print (msg)

myporta = 587
myserver = webMCTest_SERVER
assunto = "Mensagem enviada automaticamente por MCTest com estatíticas das correções"
envia_email(webMCTest_SERVER,
            myporta,
            webMCTest_FROM,
            webMCTest_PASS,
            destinatario,
            assunto,
            msg,
            [file_name])

