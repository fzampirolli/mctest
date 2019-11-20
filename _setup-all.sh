#!/bin/bash
# ATENÇÃO: esse INSTALADOR não está funcionando CORRETAMENTE ainda !!!!!
# Fazer INSTALAÇÃO MANUAL APÓS INDICAÇÃO !!!!!
#
# rodar em um ambiente virtual com sudo:
# para instalar:

cd ..
sudo su

# Download and Install the Latest Updates for the OS
apt update && apt upgrade -y

apt install python3 python3-dev idle-python3.7
apt install python3-pip

apt install virtualenv
virtualenv -p python3.7 AmbientePython3
source AmbientePython3/bin/activate

git clone git://github.com/sympy/sympy.git
cd sympy
python setupegg.py develop
cd ..

git clone git://github.com/django/django.git
pip install Django==2.2.4

cd mctest

# for debug
# bash -x setup-all.sh
# bash setup-all.sh

cp __settings.env ../
source ../_settings.env

echo "  -- Define MySQL ..."
echo "  -- Check file mctest/settings.py before to continue ..."
echo "  Name of DB:       $DB_NAME"
echo "  Name of user:     $DB_USER"
echo "  Name of password: $DB_PASS"
echo "  Name of IP:       $DB_HOST"

echo "  -- Press <ENTER> to continue or CRTL C to cancel ..."
read #-p "Press [Enter] key to continue ..."
echo "  continue ... "

echo "  -- Define parametry in django ..."
### BEGIN createsuperuser
#python manage.py createsuperuser spawn

echo "  -- Check values before to continue ..."
echo "  Name of USER:       $DEFAULT_USER"
echo "  Name of EMAIL:      $DEFAULT_EMAIL"
echo "  Name of PASS:       $DEFAULT_PASS"
echo "  -- Press <ENTER> to continue or CRTL C to cancel ..."
read #-p "Press [Enter] key to continue ..."
echo "  continue ... "

# Set the Server Timezone to CST
echo "America/Sao_Paulo" >/etc/timezone
dpkg-reconfigure -f noninteractive tzdata

###### latex - INSTALL LINE BY LINE
apt install linuxbrew-wrapper
apt install texlive-extra-utils
apt install texlive-pictures
apt install texlive-font-utils
apt install texlive-latex-extra
apt install zbar-tools

apt install python3.7-dev
# deploy
# pip freeze > requirements.txt
pip install -r requirements.txt

apt -y install mysql-server mysql-client
#mysql_secure_installation

# Install MySQL Server in a Non-Interactive mode. Default root password will be "root"
echo "  -- mysql-server mysql-server/root_password password root" | sudo debconf-set-selections
echo "  -- mysql-server mysql-server/root_password_again password root" | sudo debconf-set-selections

# apt -y install mysql-server mysql-client

##### BEGIN - Run the MySQL Secure Installation wizard

MYSQL_ROOT_PASSWORD=$DB_PASS
MYSQL=$(grep 'temporary password' /var/log/mysqld.log | awk '{print $11}')

SECURE_MYSQL=$(expect -c "

  set timeout 10
  spawn mysql_secure_installation

  expect \"Would you like to setup VALIDATE PASSWORD plugin?\ ((Press y|Y for Yes, any other key for No:) :\"
  send \"y\r\"
  expect \"There are three levels of password validation policy:\ ((Please enter 0 = LOW, 1 = MEDIUM and 2 = STRONG:) :\"
  send \"0\r\"
  expect \"New password:\"
  send \"$MYSQL_ROOT_PASSWORD\r\"
  expect \"Re-enter new password:\"
  send \"$MYSQL_ROOT_PASSWORD\r\"
  expect \"Do you wish to continue with the password provided?(Press y|Y for Yes, any other key for No) :\"
  send \"y\r\"
  expect \"Remove anonymous users? (Press y|Y for Yes, any other key for No) :\"
  send \"y\r\"
  expect \"Disallow root login remotely? (Press y|Y for Yes, any other key for No) : \"
  send \"y\r\"
  expect \"Remove test database and access to it? (Press y|Y for Yes, any other key for No) :\"
  send \"y\r\"
  expect \"Reload privilege tables now? (Press y|Y for Yes, any other key for No) :\"
  send \"y\r\"
  expect eof
  ")

echo $SECURE_MYSQL

##### END - Run the MySQL Secure Installation wizard

MYSQL_ROOT_PASSWORD=$DB_PASS

mkdir tmp
mkdir tmpGAB
mkdir pdfExam
mkdir pdfQuestion
mkdir pdfStudentEmail
mkdir /backup
mkdir /backup/json
mkdir /backup/mysql

mysql -u root -p -e -h $DB_HOST 'create database '"$DB_NAME"'; create user '"$DB_USER"'@'"$DB_HOST"' identified by '"$DB_PASS"'; GRANT ALL ON *.* TO '"$DB_USER"'@'"$DB_HOST"' IDENTIFIED BY '"$DB_PASS"'; grant all privileges on '"$DB_NAME"'.* to '"$DB_USER"'@'"$DB_HOST"'; FLUSH PRIVILEGES;'

sed -i 's/127\.0\.0\.1/0\.0\.0\.0/g' /etc/mysql/mysql.conf.d/mysqld.cnf
echo '[client]
database = '"$DB_NAME"'
user = '"$DB_USER"'
password = '"$DB_PASS"'
default-character-set = utf8' >>/etc/mysql/my.cnf

apt install python-mysqldb
apt install libmysqlclient-dev
pip install mysqlclient
pip install django-import-export
pip install django-widget-tweaks
pip install django-extensions
pip install python-decouple

#service mysql restart
systemctl daemon-reload
systemctl restart mysql

python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations

#python manage.py createsuperuser
#Endereço de email: fzampirolli@ufabc.edu.br
#Nome do usuário: fzampirolli
#Primeiro nome: Francisco
#Último nome: Zampirolli
#Password:

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('"$DEFAULT_USER"', '"$DEFAULT_EMAIL"', '"$DEFAULT_PASS"')" | python manage.py shell

### END createsuperuser

#python manage.py runserver
python3 manage.py runserver $DB_HOST:8000 --noreload

# exportar sql
#mysqldump --no-defaults -u root -p $DB_NAME -h $DB_HOST > mctest.sql

echo "  -- Popular mysql ??? ..."
echo "mysql -u root -p '"$DB_NAME"' < 'mctest.sql'"
# mysqldump --no-defaults -u root -p DB_MCTest -h 177.104.60.18 > mysql-2019-09--2.sql
# mysql -u root -p DB_MCTest --binary-mode -o < mysql-2019-09--2.sql

# OUTROS

cp crontabDjango.sh ../
cp runDjango.sh ../

echo '
*/10 *  * * *   root   /home/fz/django_webmctest/crontabDjango.sh
00 00   * * *   root   /home/fz/django_webmctest/mctest/_myBackup.sh
' >> /etc/crontab
service cron restart


: '
brew services restart mysql
mysql -h localhost -P 3306 -u root -p DB_MCTest

mysql -u root
grant all privileges on DB_MCTest.* to 'fz'@'localhost';
grant usage on *.* to 'fz'@'localhost';

grant all privileges on DB_MCTest.* to 'root'@'localhost';
grant usage on *.* to 'root'@'localhost';
FLUSH PRIVILEGES;

sudo find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
sudo find . -path "*/migrations/*.pyc"  -delete
python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py squashmigrations account 0001


sudo apt-get purge mysql-server mysql-client mysql-common mysql-server-core-* mysql-client-core-*
sudo rm -rf /etc/mysql /var/lib/mysql
sudo apt-get autoremove
sudo apt-get autoclean

### editar locale/*
django-admin.py makemessages -l pt
django-admin.py compilemessages


#### crontab
sudo apt install cron
sudo emacs /etc/crontab

*/10 *  * * *   root   /home/fz/django_webmctest/crontabDjango.sh
00 00   * * *   root   /home/fz/django_webmctest/mctest/_myBackup.sh


>> cat crontabDjango.sh
#!/bin/bash
cd /home/fz/django_webmctest/
source AmbientePython3/bin/activate
cd mctest
source ../runDjango.sh &

>> cat runDjango.sh
python3 manage.py runserver 177.104.60.16:8000 --noreload

sudo service cron restart

### editar locale/*
django-admin.py makemessages -l pt
django-admin.py compilemessages

pip install django-extensions
python manage.py graph_models -a -o myapp_models.png

pip install pydotplus
python manage.py graph_models -a -o myapp_models2.png
manage.py graph_models -a -g -o my_project_visualized.png

alterar senha mysql
sudo systemctl stop mysql
sudo mysqld_safe --skip-grant-tables &
use mysql;
update user set authentication_string=PASSWORD("Zaq1234567***") where User='root';
flush privileges;


pip3 install django-widget-tweaks
pip3 install django-extensions
pip3 install python-decouple

sudo find . -name "*~"  -exec rm {} \;
sudo find . -name "*#"  -exec rm {} \;
sudo find . -name ".DS_Store"  -exec rm {} \;
sudo find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
sudo find . -path "*/migrations/*.pyc"  -delete
sudo find . -path "*/__pycache__/*.pyc"  -delete
sudo find . -path "*/tmp/*"  -exec rm {} \;
sudo find . -path "*/pdf*/*"  -exec rm {} \;
sudo find . -path "*/tmp/*"  -exec rm {} \;
sudo rm *.tex
sudo rm *.pdf
sudo rm *.csv

'
