Vamos fazer uma **limpeza total** e reconfigurar do zero. Como o seu script roda a cada minuto via Crontab, a primeira coisa a fazer é pausar esse agendamento para que ele não fique "ressuscitando" processos antigos enquanto trabalhamos.

Siga este roteiro passo a passo rigorosamente.

### Passo 1: Parar tudo (Cron, Apache e Python)

Vamos parar o "barulho" para trabalhar no silêncio.

1. **Pare o serviço de agendamento (Cron)** para impedir que o script rode sozinho:
```bash
sudo service cron stop

```


2. **Pare o Apache:**
```bash
sudo systemctl stop apache2

```


3. **Mate os processos Python (Django) antigos:**
```bash
sudo pkill -f python3
sudo pkill -f runserver

```


4. **Apague as configurações "lixo" do Apache:**
```bash
# Remove configurações antigas ativas e disponíveis
sudo rm /etc/apache2/sites-enabled/*
sudo rm /etc/apache2/sites-available/*

# (Opcional) Se quiser manter o 000-default.conf original, pule a linha acima, 
# mas para garantir limpeza total, apagar é mais seguro.

```



### Passo 2: Gerar o Certificado (Modo Standalone)

Com a porta 80 livre (Apache parado), vamos gerar o certificado limpo.

Execute:

```bash
sudo certbot certonly --standalone -d mctest.ufabc.edu.br --force-renewal

```

Resposta:
```bash
sudo certbot certonly --standalone -d mctest.ufabc.edu.br --force-renewal
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Requesting a certificate for mctest.ufabc.edu.br

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/mctest.ufabc.edu.br/fullchain.pem
Key is saved at:    /etc/letsencrypt/live/mctest.ufabc.edu.br/privkey.pem
This certificate expires on 2026-04-06.
These files will be updated when the certificate renews.
Certbot has set up a scheduled task to automatically renew this certificate in the background.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
* Donating to ISRG / Let's Encrypt: https://letsencrypt.org/donate
* Donating to EFF:          https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
root@mctest22:/home/operador/PycharmProjects#
```

*(Se der "Congratulations", prossiga. Se der erro, me avise antes de continuar).*

### Passo 3: Configurar o Django (`settings.py`)

O Django precisa ser configurado para aceitar que o Apache faça a segurança (HTTPS) e repasse para ele.

1. Edite o arquivo:
```bash
emacs /home/operador/PycharmProjects/mctest/mctest/settings.py

```


2. Verifique ou adicione estas configurações no final do arquivo:
```python
import os

# 1. Hosts permitidos
ALLOWED_HOSTS = ['mctest.ufabc.edu.br', '127.0.0.1', 'localhost', '177.104.62.5']

# 2. Configuração CRUCIAL para Proxy Reverso SSL
# Isso diz ao Django: "Se o cabeçalho X-Forwarded-Proto for https, considere seguro"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 3. Permite POST/Login via HTTPS
CSRF_TRUSTED_ORIGINS = ['https://mctest.ufabc.edu.br']

# 4. (Opcional) Força HTTPS dentro do Django (como precaução extra)
# SECURE_SSL_REDIRECT = True 
# Recomendo deixar FALSE por enquanto e deixar o Apache gerenciar o redirecionamento

```


3. Salve (`Ctrl+x`, `Ctrl+s`) e saia (`Ctrl+x`, `Ctrl+c`).

### Passo 4: Criar a Configuração Limpa do Apache

Vamos criar um único arquivo que gerencia tudo.

1. Crie o arquivo `mctest.conf`:
```bash
sudo emacs /etc/apache2/sites-available/mctest.conf

```


2. Cole este conteúdo exato:
```apache
# --- PORTA 80: Redireciona tudo para HTTPS ---
<VirtualHost *:80>
    ServerName mctest.ufabc.edu.br
    ServerAdmin webmaster@ufabc.edu.br

    # Redirecionamento permanente
    Redirect permanent / https://mctest.ufabc.edu.br/

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

# --- PORTA 443: Site Seguro (Proxy para Django 8080) ---
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName mctest.ufabc.edu.br
    ServerAdmin webmaster@ufabc.edu.br

    # Certificados SSL (Caminho padrão do Certbot)
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/mctest.ufabc.edu.br/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/mctest.ufabc.edu.br/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf

    # Configurações do Proxy
    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"

    # Arquivos Estáticos (Opcional - Melhora performance)
    Alias /static /home/operador/PycharmProjects/mctest/static
    <Directory /home/operador/PycharmProjects/mctest/static>
        Require all granted
    </Directory>

    # Regras de Proxy:
    # Não fazer proxy da pasta static
    ProxyPass /static !
    # Mandar todo o resto para o Django na 8080
    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/

    ErrorLog ${APACHE_LOG_DIR}/ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/ssl_access.log combined
</VirtualHost>
</IfModule>

```


3. Salve e saia.

### Passo 5: Ativar e Reiniciar

1. Habilite os módulos e o site:
```bash
sudo a2enmod ssl proxy proxy_http headers rewrite
sudo a2ensite mctest.conf

```


2. Inicie o Apache:
```bash
sudo systemctl start apache2

```


3. **Ligue o Cron novamente** (para que seu script suba o Django automaticamente):
```bash
sudo service cron start

```



### O que esperar agora?

1. Aguarde 1 minuto (para o Cron rodar o script `crontabDjango0.sh` e subir o Python na porta 8080).
2. **Teste 1 (HTTPS):** Acesse `http://mctest.ufabc.edu.br`. Ele deve ir para `https` e mostrar o Django.
3. **Teste 2 (ENEM):** Acesse `http://mctest.ufabc.edu.br:8000/ENEM/`. Ele deve continuar funcionando via HTTP, pois o Apache na porta 443/80 não interfere na porta 8000.


##  Renovação automáica do certificado

O Certbot cria automaticamente uma tarefa agendada (`systemd timer` ou `cron`) para verificar a validade duas vezes por dia. No entanto, existe um **problema técnico** específico na sua configuração:

Como usámos o modo `--standalone` (porque foi o único que funcionou com o firewall), a renovação automática **vai falhar** se o Apache estiver a correr, pois o Apache ocupa a porta 80.

Para garantir que a renovação funciona automaticamente sem intervenção manual, precisamos configurar o Certbot para **parar o Apache** momentaneamente antes de renovar e **iniciá-lo** logo a seguir.

Aqui está o processo para automatizar isto:

### Passo 1: Editar a configuração de renovação

O Certbot guarda as preferências de cada domínio num ficheiro de configuração. Vamos dizer-lhe para usar "ganchos" (hooks).

1. Abra o ficheiro de configuração do seu domínio:
```bash
sudo emacs /etc/letsencrypt/renewal/mctest.ufabc.edu.br.conf

```


2. Vá até ao final do ficheiro, na secção `[renewalparams]`. Adicione (ou modifique) as linhas para incluir o `pre_hook` e `post_hook`. Deve ficar assim:
```ini
[renewalparams]
account = ... (o seu id da conta) ...
authenticator = standalone
server = https://acme-v02.api.letsencrypt.org/directory
key_type = ecdsa

# --- ADICIONE ESTAS DUAS LINHAS ---
pre_hook = systemctl stop apache2
post_hook = systemctl start apache2

```


* **pre_hook:** Pára o Apache antes de tentar renovar (liberta a porta 80).
* **post_hook:** Reinicia o Apache assim que terminar (volta a colocar o site no ar).


3. Salve (`Ctrl+x`, `Ctrl+s`) e saia (`Ctrl+x`, `Ctrl+c`).

---

### Passo 2: Simular a Renovação (Obrigatório)

Vamos testar se o Certbot consegue realmente parar e iniciar o Apache sozinho. Este comando não altera o certificado atual, apenas simula o processo.

Execute:

```bash
sudo certbot renew --dry-run

```

**O que deve observar na saída:**

1. Ele deve mostrar algo como "Simulating renewal of...".
2. Deve ver logs a indicar que o Apache parou.
3. Se correr bem: **"Congratulations, all simulated renewals succeeded"**.
4. O Apache deve estar a correr novamente no final.

---

### Passo 3: Verificar se o Timer está ativo

O Ubuntu já traz um "despertador" configurado para o Certbot. Apenas confirme se está ativo:

```bash
systemctl list-timers | grep certbot

```

Se aparecer uma linha com `certbot.timer`, está tudo pronto.

### Resumo do que vai acontecer daqui para a frente:

1. Todos os dias, o sistema verifica a validade.
2. Enquanto faltarem mais de 30 dias, ele não faz nada.
3. Quando faltarem menos de 30 dias (perto de **06 de março de 2026**), ele vai:
* Parar o Apache (Site fica offline por ~10 segundos).
* Renovar o certificado na porta 80.
* Iniciar o Apache.
* O novo certificado será válido até junho/2026.

```bash
sudo systemctl enable --now certbot.timer
```

```bash
systemctl list-timers | grep certbot
```

## Renovação manual

Se a renovação automática falhar (por exemplo, se o firewall bloquear, o timer do sistema travar ou houver mudanças na rede), você pode fazer a renovação manualmente a qualquer momento.

Como configuramos o modo **Standalone**, o segredo é sempre **liberar a porta 80** antes de pedir o certificado.

Guarde este roteiro de emergência:


### O Método Manual "Bruto" (Garantido)

Se a Opção 1 falhar, faça o processo passo a passo, controlando você mesmo o servidor. Este é o método mais seguro para resolver problemas.

**1. Pare o Apache (Para liberar a porta 80):**
O site ficará fora do ar por alguns segundos.

```bash
sudo systemctl stop apache2

```

**2. Rode o Certbot no modo Standalone:**
Este comando sobe um servidor temporário na porta 80 e conversa com a Let's Encrypt.

```bash
sudo certbot certonly --standalone -d mctest.ufabc.edu.br

```

* Ele pode perguntar: *"You have an existing certificate... What would you like to do?"*
* Responda: **2** (Renew & replace).

**3. Inicie o Apache de volta:**

```bash
sudo systemctl start apache2

```

---

### Como verificar se renovou?

Depois de renovar, você não precisa esperar para saber se deu certo. Pode consultar a validade do arquivo do certificado direto no terminal:

```bash
openssl x509 -noout -dates -in /etc/letsencrypt/live/mctest.ufabc.edu.br/fullchain.pem

```

Vai aparecer algo como:
`notAfter=Apr  6 13:50:22 2026 GMT` (Esta é a data de expiração).

### Resumo

Se o "bicho pegar": **Para Apache** -> **Certbot Standalone** -> **Inicia Apache**.