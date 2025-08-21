# Criação de Pacotes com FPM

<!-- Autor:Joao Martini Data:20/08/2025 -->

## Este repositório contém os scripts e as configurações para empacotar o aplicativo **MCTest** em um pacote Debian (`.deb`), usando a ferramenta FPM (Effing Package Management). O objetivo é transformar um processo de instalação que era manual e complexo em uma experiência simples, integrada ao sistema e automatizada.

## Visão Geral

O MCTest é um aplicativo web baseado no framework Django, com muitas dependências, tanto de sistema (MySQL, TeX Live, R) quanto do ambiente Python. A criação do pacote com FPM resolve os seguintes problemas:

  - **Simplificação:** Reduz a instalação a um único comando.
  - **Consistência:** Garante que todas as dependências e configurações sejam aplicadas da mesma forma em qualquer ambiente.
  - **Automação:** Usa scripts para automatizar tarefas após a instalação, como a configuração do banco de dados.
  - **Integração com o Sistema:** Integra o aplicativo ao sistema operacional, adicionando um atalho na área de trabalho, como qualquer outro programa.

Download: https://drive.google.com/file/d/1LqyMbcAvLv7KNAUzw18vKajKEAKlL8HR/view?usp=sharing

-----

## ⚙️ Pré-requisitos

Para instalar o pacote `.deb` gerado, o sistema do usuário deve ser uma distribuição baseada em Debian (como Ubuntu 20.04 - 22.04, Pop\!\_OS 20.04 - 22.04).

O pacote foi criado para instalar suas dependências automaticamente. No entanto, o script `preinst` verifica se os seguintes pacotes essenciais estão presentes. Caso contrário, ele informa ao usuário como instalá-los:

  - `mysql-server` e `mysql-client`
  - `python3`, `python3-pip`, `python3-dev`, `virtualenv`
  - `texlive-full` (e outros pacotes TeX)
  - `r-base` (e outros pacotes R)
  - `build-essential`, `libzbar-dev`, `default-libmysqlclient-dev`

-----

## 🚀 Instalação e Uso

### Instalação

1.  Baixe o arquivo `mctest_5.3_amd64.deb`.

2.  Abra um terminal na pasta onde o arquivo foi salvo e execute o seguinte comando:

    ```bash
    sudo apt install ./mctest_5.3_amd64.deb
    ```

    O `apt` vai ler as informações do pacote, instalar todas as dependências de sistema listadas e, em seguida, executar os scripts de configuração.

### Como usar

Após a instalação, um atalho chamado **"Mctest"** será criado no menu de aplicativos do seu sistema. Basta clicar no ícone para iniciar o servidor e abrir o programa no seu navegador padrão.

O script `start_mctest.sh` gerencia a inicialização do servidor em segundo plano.

-----

## 🛠️ Como o Pacote Funciona

O processo de instalação usa uma série de scripts para garantir a configuração correta do ambiente:

1.  **`preinst` (Antes da instalação):**

      - Verifica se todas as dependências de sistema (MySQL, Python, TeX Live, etc.) estão instaladas.
      - Se alguma dependência estiver faltando, o script para a instalação e informa ao usuário exatamente qual comando executar para corrigir o problema.

2.  **`postinst` (Depois da instalação):**

      - Este é o principal script de configuração. Ele é responsável por:
          - Criar as pastas necessárias (`/tmp`, `/backup`, etc.).
          - Configurar o banco de dados MySQL: cria o banco de dados `MCTest`, o usuário e aplica as permissões.
          - Importar a estrutura inicial do banco de dados a partir do arquivo `mctest.sql`.
          - Ativar o ambiente virtual (virtualenv) do Python que já vem incluído no pacote.
          - Criar o atalho na área de trabalho (`Mctest.desktop`) para facilitar o acesso ao programa.

3.  **`prerm` e `postrm` (Remoção):**

      - Gerenciam a desinstalação completa do programa.
      - O script `prerm` remove o atalho da área de trabalho.
      - O script `postrm` verifica se o servidor está rodando, pede confirmação para finalizá-lo e, então, remove a pasta do programa.

-----

## 🏗️ Como Construir o Pacote (Para Desenvolvedores)

Se você quer recriar o pacote `.deb` a partir do código-fonte, siga estes passos:

### 1\. Preparação do Ambiente

Garanta que a ferramenta FPM esteja instalada:

```bash
# Instalar Ruby e ferramentas de desenvolvimento
sudo apt install ruby ruby-dev build-essential

# Instalar o FPM
sudo gem install fpm
```

### 2\. Estrutura de Pastas

O comando FPM espera uma estrutura de pastas específica. Crie uma pasta de trabalho (conhecida como "staging", por exemplo: `/home/user/PycharmProjects`) que contenha:

  * A pasta do projeto `mctest`.
  * A pasta com o ambiente virtual (`virtualenv`) já criado e com as dependências instaladas.
  * Uma pasta `debian/` contendo os scripts (`preinst`, `postinst`, `prerm`, `postrm`, `CreateShortcut.sh`, `start_mctest.sh`).

### 3\. Comando FPM

Execute o comando a seguir para gerar o pacote. Adapte os caminhos (`--prefix` e `-C`) de acordo com a sua estrutura de pastas.

```bash
fpm -s dir -t deb -n mctest -v 5.3 \
    --prefix /usr/local/lib/PycharmProjects \
    -C /home/jplock/PycharmProjects \
    --before-install debian/preinst \
    --after-install debian/postinst \
    --before-remove debian/prerm \
    --after-remove debian/postrm \
    --verbose \
    --url "http://mctest.ufabc.edu.br" \
    --description "MCTest é um sofware livre e de código aberto (veja Licença) e sua melhor vantagem é o tratamento de questões paramétricas através do LaTeX e Python, permitindo variações infinitas de cada questão.

Documentação: https://github.com/fzampirolli/mctest
Página de Ajuda: http://mctest.ufabc.edu.br/readme
Mais exemplos: http://vision.ufabc.edu.br" \
    --depends "python3" \
    --depends "python3-dev" \
    --depends "python3-pip" \
    --depends "idle3" \
    --depends "default-libmysqlclient-dev" \
    --depends "build-essential" \
    --depends "virtualenv" \
    --depends "mysql-server" \
    --depends "mysql-client-core-8.0" \
    --depends "r-base" \
    --depends "r-base-dev" \
    --depends "r-base-core" \
    --depends "texlive-full" \
    --depends "texlive-extra-utils" \
    --depends "texlive-pictures" \
    --depends "texlive-font-utils" \
    --depends "texlive-latex-extra" \
    --depends "texlive-lang-portuguese" \
    --depends "texlive-science" \
    --depends "zbar-tools" \
    --depends "libzbar-dev"
```
