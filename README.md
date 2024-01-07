# MCTest v. 5.3

Welcome to MCTest, a website dedicated to assisting in exam preparation and grading.

MCTest is free and open-source software (see [License](License.txt)),
with its most notable feature being the ability to handle parametric questions 
using LaTeX and Python. This allows for numerous variations of the same question.

[Books](book) and
[Play List](https://youtube.com/playlist?list=PL5rrrH7S583Ad6iQ_neu0F7JwpPqyxNEh&si=PYf6PLBuPfTdZg41).

Please access [vision.ufabc.edu.br](http://vision.ufabc.edu.br)
for some [examples](http://vision.ufabc.edu.br/MCTest/MCTest5-Experiments/).

#### Help us spread MCTest. The more people use it, the faster we can make improvements.

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

10) Use Markdown to describe questions and send exams or activities to students;

11) Adapt the Android application to this version of MCTest [[ref15](http://www.lbd.dcc.ufmg.br/colecoes/wvc/2015/018.pdf), [ref16b](https://itp.ifsp.edu.br/ojs/index.php/IC/article/viewFile/221/394)];

12) Study the integration of MCTest with other systems, for example, SIGAA and Moodle, sharing different databases;

13) Run the parametric question codes on other servers, similar to those used in the Moodle VPL plug-in;

14) Integrate with [MakeTests](https://github.com/fernandoteubl/MakeTests);

15) Write a complete tutorial to install and use MCTest.

---
### I would like to collaborate with experts to write articles or technical reports
A maximum of 5 authors per article; Authors' order proportional to the number of pages written; I already have data/implementations for some topics:

1) Security in exams using QRcode;

2) Exams with multiple-choice questions and different weights in the answers;

3) Answer sheet design comparisons;

4) A case study using Item Response Theory;

5) Individualized online activities with multiple-choice parametric questions;

6) MCTest: Software Requirements Specification;

7) MCTest: graphic interface;

8) MCTest: data base;

9) MCTest: software architecture;

10) MCTest: software deployment.

---
### Versions 

##### MCTest 5.0
* August 2018
* Multiple choice test model in QR Code itself

##### MCTest 5.1
* August 2019
* New graphical interfaces
* The multiple-choice test template is now stored on the server

##### MCTest 5.2
* grant #2018/23561-1, São Paulo Research Foundation (FAPESP)
* 01/09/2019 - 31/08/2021
* Title: A universal system for generation and correction automatic of parametrized questions


##### MCTest 5.3 - Currently in progress
* Questions with skills in linker.json
* Table test skill by Teubl 
* Hash with email 
* Exam with topics and adapted test
* VPL 13 for Moodle 4.1

---
## Install MCTest

To install [MCTest](https://github.com/fzampirolli/mctest), follow the steps below:

1. **Install [VirtualBox](https://www.virtualbox.org/)**

2. **Install Ubuntu 22.04 on VirtualBox**

3. **In Ubuntu, run the following commands in the terminal**:

   ```bash
   sudo su
   wget https://raw.githubusercontent.com/fzampirolli/mctest/master/_setup-all.sh
   sed -i 's/\/home\/fz\//\/home\/yourUsername\//g' _setup-all.sh
   source _setup-all.sh
   pip install mysqlclient
   ```

Change `yourUsername` above before running the script.

This will download the installation script and perform the necessary configurations.

Please wait for completion: After a few minutes, the process will be finished, and MCTest will be set up.

In the same terminal, run MCTest with the following command, changing `yourUsername`:

~~~bash
source /home/yourUsername/PycharmProjects/runDjango.sh
~~~

Access MCTest: After completion, open a web browser with the URL http://127.0.0.1:8000.

For new terminals, run MCTest with the following commands, changing `yourUsername`:

```bash
sudo su
source /home/yourUsername/PycharmProjects/AmbientePython3/bin/activate
source /home/yourUsername/PycharmProjects/_settings.env
source /home/yourUsername/PycharmProjects/runDjango.sh
```

For more details and configuration options, refer to the [_setup-all.sh](https://raw.githubusercontent.com/fzampirolli/mctest/master/_setup-all.sh) file.
