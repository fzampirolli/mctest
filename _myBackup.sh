#!/bin/bash
cd /home/fz/django_webmctest/
#cp __settings.env ../
source _settings.env
source AmbientePython3/bin/activate
cd mctest

#################### SCRIPT PARA BACKUP MYSQL ####################
# mysqldump --no-defaults -u root -p DB_MCTest > mctest.sql


DB_PARAM='--no-defaults  -h $IP_HOST'

echo "  -- Definindo parametros do sistema ..."
DATE=$(date +%Y-%m-%d)
MYSQLDUMP=/usr/bin/mysqldump
BACKUP_DIR=/backup/mysql
BACKUP_NAME=mysql-$DATE.sql
BACKUP_TAR=mysql-$DATE.tar
PATH_MCTest=/home/fz/django_webmctest
PYTHON=/home/fz/django_webmctest/AmbientePython3/bin/python3

echo "  -- in $IP_HOST"
echo "  -- Gerando Backup da base de dados $DB_NAME em $BACKUP_DIR/$BACKUP_NAME ..."
$MYSQLDUMP $DB_PARAM -u $DB_USER -p$DB_PASS $DB_NAME -h $IP_HOST> $BACKUP_DIR/$BACKUP_NAME
# mysqldump --no-defaults -u root -p DB_MCTest -h 177.104.60.18 > mysql-2019-09--2.sql

# Compactando arquivo em tar
echo "  -- Compactando arquivo em tar ..."
tar -cjf $BACKUP_DIR/$BACKUP_TAR -C $BACKUP_DIR $BACKUP_NAME --remove-files

# descompactar um tar
# tar xvjf file.tar

# Excluindo arquivos desnecessarios
echo "  -- Excluindo arquivos desnecessarios ..."
rm -rf $BACKUP_DIR/$BACKUP_NAME

# Excluindo arquivos antigos > 180 dias
find /backup/*/* -type f -ctime +180 -exec rm -rf {} \;
find $PATH_MCTest/mctest/tmp*/* -type f -ctime +180 -exec rm -rf {} \;
find $PATH_MCTest/mctest/pdf*/* -type f -ctime +180 -exec rm -rf {} \;
find $PATH_MCTest/mctest/*.pdf -type f -ctime +180 -exec rm -rf {} \;
find $PATH_MCTest/mctest/*.tex -type f -ctime +180 -exec rm -rf {} \;
find $PATH_MCTest/mctest/*.csv -type f -ctime +180 -exec rm -rf {} \;

# renomeando log grande
find $PATH_MCTest/mctest/ -iname "*.log" -size +1M -exec mv {} "correct-$DATA.log.backup" \;

#################### SCRIPT PARA BACKUP JSON ####################
# python3 manage.py dumpdata --indent 2 > db.json

cd $PATH_MCTest
source AmbientePython3/bin/activate
cd mctest
$PYTHON manage.py shell < _clearsessions.py

BACKUP_DIR=/backup/json
BACKUP_NAME=json-$DATE.json
BACKUP_TAR=json-$DATE.tar

DB_PARAM='manage.py dumpdata --indent 2'

$PYTHON $DB_PARAM >$BACKUP_DIR/$BACKUP_NAME
tar -cjf $BACKUP_DIR/$BACKUP_TAR -C $BACKUP_DIR $BACKUP_NAME --remove-files
rm -rf $BACKUP_DIR/$BACKUP_NAME
