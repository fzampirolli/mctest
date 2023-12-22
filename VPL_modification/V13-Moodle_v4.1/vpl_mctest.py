class MCTest:
    USER_ID = None
    USERNAME = None
    USER_EMAIL = None

    VARIATION = None
    LINKER = None
    QUESTIONS = None
    
    def __init__(self):
        import os
        self.USER_ID = int(os.environ['MOODLE_USER_ID'])
        self.USERNAME = os.environ['MOODLE_USER_NAME']
        self.USER_EMAIL = os.environ['MOODLE_USER_EMAIL']

    def getVariation(self):
        if self.VARIATION == None:
            import csv
            with open('students_variations.csv') as csvfile:
                import unicodedata
                students = csv.reader(csvfile)
                name = unicodedata.normalize('NFKD', self.USERNAME).encode('ascii', 'ignore').decode('ascii').upper()
                
                email = unicodedata.normalize('NFKD', self.USER_EMAIL).encode('ascii', 'ignore').decode('ascii').upper() # fz add
                email = email.replace('@','').replace('.','').replace('-','').replace('_','') # fz add
                
                for student in students:
                    
                    #s = unicodedata.normalize('NFKD', student[0]).encode('ascii', 'ignore').decode('ascii').upper()
                    s = unicodedata.normalize('NFKD', student[1]).encode('ascii', 'ignore').decode('ascii').upper() # fz add
                    s = s.replace('@','').replace('.','').replace('-','').replace('_','') # fz add

                    #if len(student) > 0 and s == name:
                    if len(student) > 0 and s == email:
                        #self.VARIATION = str(int(student[1]) + 1)
                        self.VARIATION = str(int(student[2]) + 1) # fz add 
                        break
        return self.VARIATION

    def getQuestions(self, pathID):
        import os
        
        # print("========================================")
        # print(pathID)
        # print(os.listdir('./'))
        # print("========================================")

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
