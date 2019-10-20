# 177.104.60.16 fz default; bios senha mctest
#https://docs.djangoproject.com/pt-br/1.11/intro/tuturial02/
#http://www.codigofluente.com.br/01-instalacao-do-django-no-linux-ubuntu/

sudo apt update && sudo apt -y upgrade
sudo apt install python3 python3-dev idle-python3.6
sudo apt install python3-pip

sudo su
emacs /etc/bash.bashrc &
PYTHON_HOME=/usr/
export PYTHON_HOME
PATH=$PATH:$PYTHON_HOME/bin/

crld D

sudo apt install virtualenv
mkdir webmctest
cd webmctest
virtualenv -p python3.6 AmbientePython3
source AmbientePython3/bin/activate

sudo apt-get update
sudo apt-get install git
git clone git://github.com/django/django.git
pip install -e django
git pull # para atualizar dentro do django
python -m django --version
django-admin startproject mctest
cd mctest
python manage.py runserver

# criar app
python manage.py startapp account
python manage.py startapp topic
python manage.py startapp course
python manage.py startapp exam
python manage.py startapp student

#pip install django-custom-user
pip install django-import-export
pip install pyqrcode
pip install numpy
pip install PyPDF2
pip install opencv-python
pip install scikit-image
pip install more-itertools
pip install pyzbar
pip install validate_email
pip install tablib
pip install celery


#---
emacs mctest/settings.py

from django.utils.translation import gettext_lazy as _

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'account',
    'import_export',
    'topic.apps.TopicConfig',
    'course.apps.CourseConfig',
    'exam.apps.ExamConfig',
    'student.apps.StudentConfig',
]

AUTH_USER_MODEL = 'custom_user.EmailUser'

TEMPLATES = [ ...
        'DIRS': ['./templates', os.path.join(BASE_DIR, 'templates')],

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DB_MCTest',
        'USER': 'fz',
        #'USER': 'root',  # l104 -fz & vision
        'PASSWORD': '2008ufabc2018',
        #'HOST': '177.104.60.16',       # l104 - fz
        #'HOST': '177.104.60.15',       # l104 - guiou
        #'HOST': '177.104.60.18',       # vision
        'HOST': 'localhost',  
        'PORT': '3306',
        'TEST': {
            'NAME': 'test_DB_MCTest',
        },
    }
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

LANGUAGES = (
    ('en', _('English')),
    ('pt', _('Portugues')),
)
MULTILINGUAL_LANGUAGES = (
    "en-us",
    "pt-br",
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

IMPORT_EXPERT_USE_TRANSACTIONS=True

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#---fim

######################################################################

# mysql
sudo apt update
sudo apt -y install mysql-server mysql-client
sudo mysql_secure_installation
sudo mysql -u root -p

############ MUITA ATENÇÃO AQUI !!!!!!!

## virtual
create database DB_MCTest;
create user 'fz'@'localhost' identified by '2008ufabc2018';
GRANT ALL ON DB_MCTest.* TO 'fz'@'localhost' IDENTIFIED BY '2008ufabc2018';
grant all privileges on DB_MCTest.* to 'fz'@'localhost';
grant usage on *.* to 'fz'@'localhost';
FLUSH PRIVILEGES;
show databases;
show global variables like 'port%';
GRANT ALL PRIVILEGES ON test_DB_MCTest.* TO 'fz'@'localhost';
quit

### VISION.UFABC.EDU.BR

create database DB_MCTest;

create user 'root'@'177.104.60.18' identified by '2008ufabc2018';
GRANT ALL ON DB_MCTest.* TO 'root'@'177.104.60.18' IDENTIFIED BY '2008ufabc2018';
GRANT ALL ON *.* TO 'root'@'177.104.60.18' IDENTIFIED BY '2008ufabc2018';
grant all privileges on DB_MCTest.* to 'root'@'177.104.60.18';
grant usage on *.* to 'root'@'177.104.60.18';
GRANT ALL PRIVILEGES ON test_DB_MCTest.* TO 'root'@'177.104.60.18';

create user 'fz'@'177.104.60.18' identified by '2008ufabc2018';
GRANT ALL ON DB_MCTest.* TO 'fz'@'177.104.60.18' IDENTIFIED BY '2008ufabc2018';
GRANT ALL ON *.* TO 'fz'@'177.104.60.18' IDENTIFIED BY '2008ufabc2018';
grant all privileges on DB_MCTest.* to 'fz'@'177.104.60.18';
grant usage on *.* to 'fz'@'177.104.60.18';
GRANT ALL PRIVILEGES ON test_DB_MCTest.* TO 'fz'@'177.104.60.18';

FLUSH PRIVILEGES;
show databases;
show global variables like 'port%';
quit

### l104 - fz
create database DB_MCTest;
create user 'root'@'177.104.60.16' identified by 'ufabc2018';
GRANT ALL ON DB_MCTest.* TO 'root'@'177.104.60.16' IDENTIFIED BY 'ufabc2018';
grant all privileges on DB_MCTest.* to 'root'@'177.104.60.16';
grant usage on *.* to 'root'@'177.104.60.16';
GRANT ALL PRIVILEGES ON test_DB_MCTest.* TO 'root'@'177.104.60.16';
create user 'fz'@'177.104.60.16' identified by 'ufabc2018';
GRANT ALL ON DB_MCTest.* TO 'fz'@'177.104.60.16' IDENTIFIED BY 'ufabc2018';
grant all privileges on DB_MCTest.* to 'fz'@'177.104.60.16';
grant usage on *.* to 'fz'@'177.104.60.16';
FLUSH PRIVILEGES;
show databases;
show global variables like 'port%';
quit


#---
sudo emacs -nw /etc/mysql/my.cnf 
[client]
database = DB_MCTest
user = fz  # root vision
password = 2008ufabc2018
default-character-set = utf8
#---fim

sudo emacs -nw /etc/mysql/mysql.conf.d/mysqld.cnf
#bind-address            = 127.0.0.1
bind-address            = 0.0.0.0


sudo apt-get install python-mysqldb
sudo apt-get install libmysqlclient-dev
pip install mysqlclient

systemctl daemon-reload
systemctl restart mysql

python manage.py migrate
python manage.py makemigrations

python manage.py createsuperuser  

python manage.py runserver # ou . ../django.sh

#####check----- TABELAS do django
sudo mysql -u root -p
use DB_MCTest;
show tables;
drop table topic_topic;

desc custom_user_emailuser;
select * from custom_user_emailuser;

#####
python manage.py check
python manage.py shell
python manage.py dbshell
drop table if exists topic_*;  #apagar

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
python manage.py migrate --fake topic zero
python manage.py migrate --fake course zero
python manage.py migrate --fake exam zero
python manage.py migrate --fake student zero

#python manage.py migrate --fake users zero

python manage.py migrate
python manage.py makemigrations 
python manage.py migrate

# para remover mysql
sudo apt-get purge mysql-server mysql-client mysql-common mysql-server-core-* mysql-client-core-*
sudo rm -rf /etc/mysql /var/lib/mysql
sudo apt-get autoremove
sudo apt-get autoclean


sudo mysqldump -u root -p DB_MCTest > mctest.sql  #ERRO


####### json

python manage.py dumpdata --indent 2 > db.json

python manage.py dumpdata admin --indent 2 > admin.json
python manage.py dumpdata auth.user > user.json
python manage.py dumpdata --exclude auth.permission > db2.json
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > db2.json

## para carregar um bd
python manage.py loaddata db.json


###### 
pip install djangorestframework
pip install markdown       # Markdown support for the browsable API.
pip install django-filter  # Filtering support


###### latex
sudo apt install linuxbrew-wrapper
sudo apt install texlive-extra-utils
sudo apt install texlive-font-utils
apt-get install zbar-tools 
epstopdf QRCode.eps 


### editar locale/*
django-admin.py makemessages -l pt
emacs locale/pt/LC_MESSAGES/django.po &
django-admin.py compilemessages
