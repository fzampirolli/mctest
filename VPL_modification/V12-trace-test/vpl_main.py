import vpl_utils, vpl_mctest, random, sys, json

mc = vpl_mctest.MCTest()
qs = mc.getQuestions(sys.argv[1])
question = {}
if qs != None:
    for q in qs:
        if 'table test' in q['skills']:
            question['func'] = q['description'][0]['func']
            question['text'] = q['description'][0]['text']
            question['args'] = json.loads(q['cases'][0]['input'][0])
            question['ignore'] = ""
            if 'ignore' in q['description'][0]:
                question['ignore'] = q['description'][0]['ignore']
            question['file'] = q['file']
else:
    print("ERRO!")

##
#  CORRECTION

feedback = None
with open(question['file']+'.txt', mode ='r') as file:
    TM = vpl_utils.TesteDeMesa(question['func'])
    func_out = TM.make(question['args'], question['ignore'])
    score, feedback = TM.correct(file.read())

vpl_utils.terminate(score, {
    # 'Pseudo-Código' : TM.source(),
    # 'Saída gerada pela função' : func_out,
    # 'Gabarito' : TM.show(False),
    # 'Variation' : mc.getVariation(),
    # 'Question' : mc.getQuestions(),
    # 'debugUser' : userTable,
    # 'debugTable' : TM.table,
    'Pontuação' : f"Você acertou {int(100 * score)}%\n",
    'Feedback' : feedback,
})
