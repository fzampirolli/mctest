#!/bin/bash
# SCRIPT CRIADO EM 2023-04-18 UTILIZANDO
# UBUNTU 20.04
# Django 4.2
# python 3.8
# cv2 3.4.18.65 (precisa alterar código para usar 4.7)
# e vários outros de requirements-titan256GB.txt
# rodar esse script como sudo: sudo su
# depois rodar: source ./_setup-all.sh
# quando pedir uma senha do mysql, incluir "ufabc12345", se não mudou em _settins.env

# ou usando pip:
# python setup.py sdist bdist_wheel
# pip install dist/mctest-5.2.tar.gz # isso está com BUG ainda

# se ainda nao fez, baixar o mctest da pasta, mudando fz pelo seu login
mkdir /home/fz/PycharmProjects/
cd /home/fz/PycharmProjects/

## assim
#sudo apt install -y git
#git clone https://github.com/fzampirolli/mctest.git

cd mctest

# instala alguns pacotes com apt
#sudo snap install emacs --classic
sudo apt install -y texlive-extra-utils
sudo apt install -y texlive-pictures
sudo apt install -y texlive-font-utils
sudo apt install -y texlive-latex-extra
sudo apt install -y zbar-tools
sudo apt install -y texlive-science
sudo apt install -y libzbar-dev

# NÃO MUDAR O USER DO BD
cp _settings.env ../
source ../_settings.env

# Instala o python3.8
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.8 python3-dev idle3 python3-pip default-libmysqlclient-dev build-essential

# Instala virtualenv
sudo apt install -y virtualenv
virtualenv -p python3.8 ../AmbientePython3
source ../AmbientePython3/bin/activate

# Instala o MySQL
sudo apt install -y mysql-server
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$DB_PASS';"

# Atualiza a lista de pacotes
sudo apt-get update

# Instala o pacote mysql-client-core-8.0
sudo apt install -y mysql-client-core-8.0

# Inicia o serviço do MySQL
sudo systemctl start mysql

cp _settings.env ../
source ../_settings.env

# Cria banco de dados e concede privilégios ao root
sudo mysql -u root << EOF
GRANT ALL PRIVILEGES ON *.* TO '$DB_USER'@'localhost' WITH GRANT OPTION;
CREATE DATABASE $DB_NAME;
FLUSH PRIVILEGES;
exit
EOF

# Configura arquivos do mysql
sed -i 's/127\.0\.0\.1/0\.0\.0\.0/g' /etc/mysql/mysql.conf.d/mysqld.cnf
echo '[client]
database = '"$DB_NAME"'
user = '"$DB_USER"'
password = '"$DB_PASS"'
default-character-set = utf8' >>/etc/mysql/my.cnf

# Re-inicia o serviço do MySQL
sudo systemctl daemon-reload
sudo systemctl restart mysql

# Executa o script SQL no um banco de dados de exemplo
#mysqldump --no-defaults -u root -p DB_MCTest -h localhost > mctest.sql
sudo mysql -u root -p $DB_NAME < mctest.sql

pip install -r requirements-titan256GB.txt

cp crontabDjango.sh ../
cp runDjango.sh ../

source ../runDjango.sh

