# Guia de Configuração SSL e Apache: vision.ufabc.edu.br

Este guia detalha o processo de sucesso para configurar o servidor, utilizando IPv6 para contornar bloqueios de firewall e o modo Standalone para garantir a emissão do certificado.

## PARTE 1: Preparação (Pode ser feito via SSH ou Local)

### 1. Configurar o IPv6 (O "Pulo do Gato")

Para escapar do erro de *Connection Reset* no IPv4 da UFABC, configuramos o IPv6 fixo que o DNS já reconhece.

Edite o arquivo do Netplan:

```bash
sudo emacs /etc/netplan/01-netcfg.yaml

```

Deixe a configuração conforme o sucesso obtido:

```yaml
network:
  version: 2
  ethernets:
    enp5s0:
      dhcp4: true
      addresses:
        - 2801:a4:fabc:1035::18/128
      gateway6: 2801:a4:fabc:1035::1

```

Aplique e verifique:

```bash
sudo netplan try
ip -6 addr show enp5s0  # Deve mostrar o final ::18

```

### 2. Preparar Permissões e Favicon

O Apache precisa de acesso aos arquivos e ao ícone da aba.

```bash
# Definir dono como www-data
sudo chown -R www-data:www-data /var/www/html/static
sudo chown -R $USER:www-data /usr/local/lib/PycharmProjects/mctest

# Permissões de leitura
sudo find /var/www/html/static -type f -exec chmod 644 {} +

```

### 3. Criar a Configuração do Apache (vision.conf)

Crie o arquivo: `sudo emacs /etc/apache2/sites-available/vision.conf`

```apache
<VirtualHost *:80>
    ServerName vision.ufabc.edu.br
    Redirect permanent / https://vision.ufabc.edu.br/
</VirtualHost>

<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName vision.ufabc.edu.br
    ServerAdmin fzampirolli@ufabc.edu.br

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/vision.ufabc.edu.br/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/vision.ufabc.edu.br/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf

    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"

    # Favicon
    Alias /favicon.ico /var/www/html/static/icon.png
    ProxyPass /favicon.ico !

    # Arquivos Estáticos
    Alias /static /usr/local/lib/PycharmProjects/mctest/static
    <Directory /usr/local/lib/PycharmProjects/mctest/static>
        Require all granted
    </Directory>

    # --- REGRAS DE PROXY (Ordem Crítica) ---
    
    # 1. Serviço ENEM e outros (Porta 8000)
    ProxyPass /ENEM/ http://127.0.0.1:8000/ENEM/
    ProxyPassReverse /ENEM/ http://127.0.0.1:8000/ENEM/

    # 2. Django Principal (Porta 8001)
    ProxyPass /static !
    ProxyPass / http://127.0.0.1:8001/
    ProxyPassReverse / http://127.0.0.1:8001/

    ErrorLog ${APACHE_LOG_DIR}/vision_ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/vision_ssl_access.log combined
</VirtualHost>
</IfModule>

```

---

## PARTE 2: Instalação do Certificado (O "Dia D")

Siga esta sequência rigorosa para evitar conflitos na porta 80:

1. **Parar tudo:**
```bash
sudo systemctl stop cron
sudo systemctl stop apache2
sudo pkill -f python3

```


2. **Gerar o Certificado via IPv6 (Modo Standalone):**
   Como o DNS já aponta para o IP `::18` e sua máquina está configurada, o Let's Encrypt validará via IPv6.
```bash
sudo certbot certonly --standalone -d vision.ufabc.edu.br

```


3. **Ativar Apache:**
```bash
sudo a2enmod ssl proxy proxy_http headers rewrite
sudo a2ensite vision.conf
sudo systemctl start apache2
sudo systemctl start cron

```



---

## PARTE 3: Renovação Automática (Hooks)

Como o modo `--standalone` exige a porta 80 livre, configuramos "ganchos" para o Certbot gerir o Apache sozinho.

### Passo 1: Editar o arquivo de renovação

```bash
sudo emacs /etc/letsencrypt/renewal/vision.ufabc.edu.br.conf

```

Adicione ao final, na seção `[renewalparams]`:

```ini
pre_hook = systemctl stop apache2
post_hook = systemctl start apache2

```

### Passo 2: Testar a automação

Este comando simula a renovação, para o apache, testa o desafio e reinicia o apache:

```bash
sudo certbot renew --dry-run

```

### Passo 3: Garantir o Timer do Sistema

```bash
# Ativar o despertador do Certbot
sudo systemctl enable --now certbot.timer

# Verificar se está na lista
systemctl list-timers | grep certbot

```

**Resultado esperado:** Todos os dias o sistema verificará a validade. Se faltarem menos de 30 dias, ele desligará o site por ~10 segundos, renovará o certificado e religará tudo automaticamente.