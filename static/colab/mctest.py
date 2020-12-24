def drawCircles():
    str1 = '''
% drawCircles
\\vspace{-5mm}
\\leavevmode\\put(-11,0){\\color{black}\\circle*{15}}\\hspace{-0mm}
\\leavevmode\\put(509,0){\\color{black}\\circle*{15}}
        '''
    return str1

def createWrongAnswers(a):
    global correctAnswer, a0, a1, a2

    respostas = ""
    # print "======len:", len(a)
    if len(a) == 2:
        a0 = int(a[0])
        a1 = int(a[1])

        rand = random.sample(range(correctAnswer - a1, correctAnswer + int(a1 / 2)), a0)
        for i in rand:
            respostas += "" + str(i) + "\n"

        if correctAnswer in rand:
            respostas = createWrongAnswers(a)

    elif len(a) == 1:
        a0 = int(a[0])
        count = 0
        for i in a2:
            if i != correctAnswer and count < a0:
                count += 1
                respostas += str(i) + "\n"

    return respostas