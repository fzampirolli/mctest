sudo rsync -avz -progress -e "sshpass -p $(cat ~/.password-mctest) ssh -p 22" ufabc@mctest.ufabc.edu.br:/backup/ /backup
