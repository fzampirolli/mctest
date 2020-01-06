#!/bin/bash
cd /home/ufabc/django_webmctest/

rsync -avzhe -progress -e "sshpass -p $(cat /home/ufabc/.password-vision) ssh -p 22" /backup/ fz@vision.ufabc.edu.br:/backup-mctest/ >> log3h5m.log 2>&1
