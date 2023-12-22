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
            question['file'] = q['file']
            
    #question = json.loads(qs[0]['cases'][0]['input'][0].replace('\n', '__NEW_LINE__'))
    #question['func'] = question['func'].replace('__NEW_LINE__', '\n')
else:
    print("ERRO!")

##
#  CORRECTION

feedback = None
with open(question['file']+'.txt', mode ='r') as file:
    TM = vpl_utils.TesteDeMesa(question['func'])
    func_out = TM.make(question['args'])
    score, feedback = TM.correct(file.read())
    #print(question['file']+'.txt')
    #print(file.read())


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
