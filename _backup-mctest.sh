#!/bin/bash
cd /home/operador/PycharmProjects/

rsync -avzhe -progress -e "sshpass -p $(cat /home/operador/.password-vision) ssh -p 22" /backup/ fz@vision.ufabc.edu.br:/backup-mctest/ >> log3h5m.log 2>&1
