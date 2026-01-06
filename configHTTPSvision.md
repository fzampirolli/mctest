Este é um cenário excelente e muito comum. A estratégia muda um pouco porque **você não pode gerar o certificado SSL (Let's Encrypt) enquanto estiver na sua casa**.

Por que? O Let's Encrypt valida o domínio `vision.ufabc.edu.br`. Ele vai tentar conectar nesse endereço. Se você rodar isso em casa, ele vai bater no IP da universidade (ou falhar) e não no seu computador de casa.

**A Estratégia:**

1. **Em Casa:** Deixamos o "terreno preparado" (Django configurado, Apache instalado, arquivos de configuração escritos, permissões de pasta ajustadas).
2. **Na UFABC (Dia D):** Você rodará apenas 3 comandos para gerar o certificado e "virar a chave".

Siga este roteiro rigorosamente.

---

### PARTE 1: O que fazer EM CASA (Preparação)

#### 1. Preparar o Django (`settings.py`)

Vamos deixar o Django pronto para aceitar tanto o seu teste local quanto o domínio final.

Edite o arquivo `settings.py` (ajuste o caminho se necessário):

```bash
sudo emacs /usr/local/lib/PycharmProjects/mctest/mctest/settings.py

```

Altere/Adicione estas configurações:

```python
import os

# 1. Hosts: Adicionamos localhost (pra casa) e vision (pra ufabc)
ALLOWED_HOSTS = ['vision.ufabc.edu.br', '127.0.0.1', 'localhost']

# 2. Caminhos Estáticos (Confirme se está assim)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 3. Segurança HTTPS (Configuração híbrida)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = ['https://vision.ufabc.edu.br']

# NOTA: Não ative SECURE_SSL_REDIRECT = True ainda, senão você não consegue testar em casa via HTTP.

```

**Importante:** Como mudou de pasta, rode o collectstatic para garantir:

```bash
python3 manage.py collectstatic

```

#### 2. Ajustar Permissões de Pasta (Crítico)

Como você mudou para `/usr/local/lib/...`, essa é uma pasta de sistema. O Apache (usuário `www-data`) precisa conseguir ler os arquivos aí.

Rode estes comandos para garantir que o Apache tenha acesso:

```bash
# Dá propriedade ao seu usuário (supondo que seja 'operador', se não for, mude) e ao grupo do Apache
sudo chown -R $USER:www-data /usr/local/lib/PycharmProjects/mctest

# Garante que as pastas sejam legíveis e executáveis (para entrar nelas)
sudo find /usr/local/lib/PycharmProjects/mctest -type d -exec chmod 755 {} \;

# Garante que os arquivos sejam legíveis
sudo find /usr/local/lib/PycharmProjects/mctest -type f -exec chmod 644 {} \;

```

#### 3. Criar a Configuração do Apache (Mas não ativar!)

Vamos deixar o arquivo pronto, apontando para os certificados que *ainda não existem*.

1. Crie o arquivo:

```bash
sudo emacs /etc/apache2/sites-available/vision.conf

```

2. Cole o conteúdo abaixo. **Atenção:** Já atualizei os caminhos para `/usr/local/lib/...`:

```apache
# --- PORTA 80: Redireciona tudo para HTTPS ---
<VirtualHost *:80>
    ServerName vision.ufabc.edu.br
    ServerAdmin webmaster@ufabc.edu.br

    # Redirecionamento permanente (Só vai funcionar quando tiver o cert)
    Redirect permanent / https://vision.ufabc.edu.br/

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

# --- PORTA 443: Site Seguro ---
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName vision.ufabc.edu.br
    ServerAdmin webmaster@ufabc.edu.br

    # Certificados SSL (Caminhos que SERÃO criados na UFABC)
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/vision.ufabc.edu.br/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/vision.ufabc.edu.br/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf

    # Configurações do Proxy
    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"

    # Arquivos Estáticos (Caminho NOVO)
    Alias /static /usr/local/lib/PycharmProjects/mctest/static
    <Directory /usr/local/lib/PycharmProjects/mctest/static>
        Require all granted
    </Directory>

    # Regras de Proxy:
    ProxyPass /static !
    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/

    ErrorLog ${APACHE_LOG_DIR}/vision_ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/vision_ssl_access.log combined
</VirtualHost>
</IfModule>

```

3. **NÃO ATIVE O SITE AINDA!** (`a2ensite`). Se ativar agora, o Apache vai falhar ao reiniciar porque os arquivos `/etc/letsencrypt/...` não existem.

#### 4. Instalar o Certbot (Se não tiver)

```bash
sudo apt update
sudo apt install certbot python3-certbot-apache

```

---

### PARTE 2: "Dia D" - Ao chegar na UFABC

Leve o computador, conecte o cabo de rede e certifique-se de que a internet funciona e que o DNS `vision.ufabc.edu.br` já está apontando para o IP dessa máquina.

Siga estes passos na ordem:

#### Passo 1: Parar serviços conflitantes

```bash
sudo service cron stop
sudo systemctl stop apache2

```

#### Passo 2: Gerar o Certificado (O passo Mágico)

Agora que está na rede da UFABC, o Let's Encrypt vai conseguir validar.

```bash
sudo certbot certonly --standalone -d vision.ufabc.edu.br

```

*(Se der sucesso, prossiga. Se der erro, verifique se o firewall libera a porta 80).*

#### Passo 3: Ativar a configuração do Apache

Agora que o certificado existe (passo anterior), podemos ligar o arquivo de configuração que criamos em casa.

```bash
# Habilita módulos necessários
sudo a2enmod ssl proxy proxy_http headers rewrite

# Habilita o nosso site vision
sudo a2ensite vision.conf

# Desabilita o padrão (se quiser limpar)
sudo a2dissite 000-default.conf

```

#### Passo 4: Reiniciar Apache e Cron

```bash
sudo systemctl start apache2
sudo service cron start

```

### Resumo da Configuração de Renovação Automática (Faça na UFABC)

Depois que tudo funcionar, edite o arquivo de renovação para garantir que ele pare o apache automaticamente (igual fizemos antes):

1. `sudo emacs /etc/letsencrypt/renewal/vision.ufabc.edu.br.conf`
2. Adicione na seção `[renewalparams]`:

```ini
pre_hook = systemctl stop apache2
post_hook = systemctl start apache2

```

### Checklist Rápido para levar no bolso:

1. **Em Casa:** `settings.py` atualizado, permissões da pasta `/usr/local` corrigidas, arquivo `vision.conf` criado (mas inativo).
2. **Na UFABC:**
* `stop apache2`
* `certbot ... --standalone -d vision...`
* `a2ensite vision.conf`
* `start apache2`
