#!/bin/bash

# UBUNTU = 22.04
# Mint >= 21 Mate
# Django 5.0
# python 3

# cv2 3.4.18.65 - precisa alterar código para usar 4.9:
# pip uninstall opencv-python
# pip install opencv-python
# repassar todos as ocorrencias de findContours:
#(_, contours, _) = cv2.findContours(
#(contours, _) = cv2.findContours(

# e vários outros de requirements-titan256GB.txt

# executar esse script como sudo: sudo su

# fazer download do arquivo de configuração
# wget https://raw.githubusercontent.com/fzampirolli/mctest/master/_setup-all.sh

# configurar teclado sem "ç":
# setxkbmap -model abnt -layout us -variant intl
# sudo emacs -nw /etc/environment
# incluir no final: GTK_IM_MODULE=cedilla

# executar:
# source _setup-all.sh

# se pedir uma senha do mysql, incluir "ufabc12345", se não mudou em _settings.env

# ou usando pip:
# python setup.py sdist bdist_wheel
# pip install dist/mctest-5.2.tar.gz # isso está com BUG ainda

# sugestão: baixar o mctest para a pasta abaixo, mudando fz pelo seu login
mkdir /home/fz/PycharmProjects/
cd /home/fz/PycharmProjects/

# se ainda nao fez download:
sudo apt install -y git
git clone https://github.com/fzampirolli/mctest.git

cd mctest

# para clonar o GitHub de uma data específica:
# Para a primeira edição do livro, em 2023-09-07,
# executar dentro da pasta mctest:
# git checkout 8ad0d60055a35fdb5f0e821601a6129ea15ab28a

mkdir tmp
mkdir /var/www/html/tmp/imgs180days
ln -s /var/www/html/tmp/imgs180days
#mkdir tmpGAB
mkdir pdfExam
mkdir pdfQuestion
mkdir pdfTopic
mkdir pdfStudentEmail
mkdir /backup
mkdir /backup/json
mkdir /backup/mysql
#mkdir /backup/tmpGAB

# NÃO MUDAR O USER 'root' DO BD
cp _settings.env ../
source _settings.env

# Instala o python3
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3
sudo apt install -y python3-dev
sudo apt install -y python3-pip
sudo apt install -y idle3
sudo apt install -y default-libmysqlclient-dev
sudo apt install -y build-essential

# Instala e entra em virtualenv
sudo apt install -y virtualenv
virtualenv -p python3 ../AmbientePython3
source ../AmbientePython3/bin/activate

# Instala o MySQL
sudo apt install -y mysql-server
#sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$DB_PASS';"

# Atualiza a lista de pacotes
sudo apt-get update

# Instala o pacote mysql-client-core-8.0
sudo apt install -y mysql-client-core-8.0

# Inicia o serviço do MySQL
sudo systemctl start mysql

# Cria banco de dados e concede privilégios ao root
sudo mysql -u root << EOF
GRANT ALL PRIVILEGES ON *.* TO '$DB_USER'@'localhost' WITH GRANT OPTION;
CREATE DATABASE $DB_NAME;
FLUSH PRIVILEGES;
exit
EOF

SET GLOBAL validate_password_policy=LOW;
SHOW VARIABLES LIKE 'validate_password%';
SET GLOBAL validate_password.policy = 0;

GRANT ALL PRIVILEGES ON *.* TO 'root'@'177.104.62.5' IDENTIFIED BY 'ZAQ!@#$%678***' WITH GRANT OPTION;

# Configura arquivos do mysql
sed -i 's/127\.0\.0\.1/0\.0\.0\.0/g' /etc/mysql/mysql.conf.d/mysqld.cnf
echo '[client]
database = '"$DB_NAME"'
user = '"$DB_USER"'
password = '"$DB_PASS"'
default-character-set = utf8' >>/etc/mysql/my.cnf

# comentar linhas:
sed -i -e '/import pymysql/s/^/# /' -e '/pymysql.version_info = (2, 2, 4, '\''final'\'', 0)/s/^/# /' -e '/pymysql.install_as_MySQLdb()/s/^/# /' mctest/settings.py

# Re-inicia o serviço do MySQL
sudo systemctl daemon-reload
sudo systemctl restart mysql

# Executa o script SQL de um banco de dados exemplo com a senha 'ufabc12345' para:
# fzampirolli@ufabc.edu.br
# fzcoord@ufabc.edu.br
# fzprof@ufabc.edu.br
# fzstudent@ufabc.edu.br
# mysqldump --no-defaults -u root -p DB_MCTest -h localhost > mctest.sql
sudo mysql -u root $DB_NAME < mctest.sql

pip install -r requirements-titan256GB.txt

# se ocorrer algum erro no comando anterior (no ubuntu 23.04):
pip install --upgrade pip setuptools
pip install --upgrade scipy
pip install scikit-image==0.18.1
pip install django
pip install python-dotenv
pip install django-widget-tweaks
pip install django-extensions
pip install django-import-export
pip install mysqlclient
pip install bcrypt
pip install pyqrcode
pip install matplotlib
pip install python-decouple
pip install pypdf2
pip install opencv-python
pip install img2pdf
pip install pandas
pip install pdf2image
pip install pyzbar
pip install arviz
pip install pymc3
pip install Pygments
pip install mysqlclient
pip install requests
pip install autopep8
pip install pymysql==2.2.4
pip install language_tool_python
pip install --upgrade pip setuptools

# para instalar bibliotecas estatísticas do R
# brew install r # para macos
sudo apt install r-base
sudo apt install r-base-dev
pip install rpy2
export R_HOME=/usr/lib/R
export RPY2_CFFI_MODE=ABI
# python -m rpy2.situation


# instala mais alguns pacotes com apt
#sudo snap install emacs --classic
sudo apt install -y textlive-full
sudo apt install -y texlive-extra-utils
sudo apt install -y texlive-pictures
sudo apt install -y texlive-font-utils
sudo apt install -y texlive-latex-extra
sudo apt install -y texlive-lang-portuguese
sudo apt install -y zbar-tools
sudo apt install -y texlive-science
sudo apt install -y libzbar-dev
sudo texhash

cp crontabDjango.sh ../
cp runDjango.sh ../

# source ../runDjango.sh &

# incluir em /etc/crontab
# 2  3    * * *   root     /home/operador/PycharmProjects/mctest/_myBackup.sh
# 5  3    * * *   operador /home/operador/PycharmProjects/_backup-mctest.sh
# *  *    * * *   root     /home/operador/PycharmProjects/crontabDjango0.sh
# sudo service cron start