class MCTest:
    USER_ID = None
    USERNAME = None

    VARIATION = None
    LINKER = None
    QUESTIONS = None
    
    def __init__(self):
        import os
        self.USER_ID = int(os.environ['MOODLE_USER_ID'])
        self.USERNAME = os.environ['MOODLE_USER_NAME']

    def getVariation(self):
        if self.VARIATION == None:
            import csv
            with open('students_variations.csv') as csvfile:
                import unicodedata
                students = csv.reader(csvfile)
                name = unicodedata.normalize('NFKD', self.USERNAME).encode('ascii', 'ignore').decode('ascii').upper()
                for student in students:
                    s = unicodedata.normalize('NFKD', student[0]).encode('ascii', 'ignore').decode('ascii').upper()
                    if len(student) > 0 and s == name:
                        self.VARIATION = str(int(student[1]) + 1)
                        break
        return self.VARIATION

    def getQuestions(self, pathID):
        import os
        for d in os.listdir('./'):
            if os.path.isdir(d): #BUG: verificar o ID correto da pasta
                if pathID in str(d):
                    path = d
                
        if self.LINKER == None:
            import json
            self.LINKER = json.load(open(path+'/.variation.json'))
            self.QUESTIONS = self.LINKER['questions']
        '''
        if self.LINKER != None and self.QUESTIONS == None:
            for q in self.LINKER['variations']:
                if q['variant'] == self.getVariation():
                    self.QUESTIONS = q['questions']
                    break
        '''
        return self.QUESTIONS
