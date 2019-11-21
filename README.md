# mctest v. 5.1 (or webMCTest 1.1)

Welcome to webMCTest, a website devoted to assist in preparing and correcting exams.

WebMCtest is a free open-source software (see [License](License.txt)), and its best 
advantage is the handling to parametric questions through 
![equation](http://latex.codecogs.com/gif.latex?\LaTeX) and Python, 
**allowing for infinite variations of each same question**.

Please access [vision.ufabc.edu.br:8000](http://vision.ufabc.edu.br:8000)
for some [examples](http://vision.ufabc.edu.br/MCTest/MCTest5-Experiments/).

#### Help us spread webMCtest. If more people use it, the faster the improvements.

WebMCtest must be installed on an Ubuntu 18.04 server through ports 3306 and 8000.

Define specific data in the file [_settings.env](_settings.env).

### After downloading in [github.com/fzampirolli/mctest](https://github.com/fzampirolli/mctest), 
install webMCTest with:
```
sudo su
source _setup_all.sh 
```

### Future Improvements
1) Error messages and graphical interfaces;
 
2) Install [_setup-all.sh](_setup-all.sh) (including other operating systems);

3) The time to generate PDF from an exam with many students.

4) Site and DB in different languages. For example, 
   edit the [locale/pt/LC_MESSAGES/django.po](locale/pt/LC_MESSAGES/django.po) 
   for Portuguese and use the commands:
   ```
   django-admin.py makemessages -l pt
   django-admin.py compilemessages
   ```

   Afterwards make the following changes in [_settings.env](_settings.env):
   ```
   LANGUAGE_CODE = 'pt-br'
   TIME_ZONE = 'America/Sao_Paulo'
   ```

   Please see [locale](locale) for other languages;

5) AI Exams Module: individual exams based on the students and the class history;

6) AI Students Module: evaluation of how the weigh questions in order to show the 
   skills and abilities of each student;

7) Use of blockchain to validate exams, history and other features;

8) Inclusion of facial recognition in the QR Code of the exams;

9) Improve of Item Response Theory;  

10) Use Markdown to describe questions and send exams or activities to students.
---
### Versions 

##### webMCTest 1.0 (ou MCTest 5.0)
* August 2018
* Multiple choice test model in QR Code itself

##### webMCTest 1.1
* August 2019
* New graphical interfaces
* The multiple-choice test template is now stored on the server

##### webMCTest 1.2
* grant #2018/23561-1, São Paulo Research Foundation (FAPESP)
* 01/09/2019 - 31/08/2021
* Title: A universal system for generation and correction automatic of parametrized questions
