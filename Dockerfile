# Defina a imagem base
FROM python:3.8-slim-buster

# Defina o diretório de trabalho do contêiner
WORKDIR /app

# Copie o arquivo requirements.txt para o contêiner
COPY requirements-titan256GB.txt .

# Instale as dependências do projeto
RUN pip install --no-cache-dir -r requirements-titan256GB.txt

# Copie o restante do diretório do projeto para o contêiner
COPY . .

# Exponha a porta 8000 para o host
EXPOSE 8001

# Inicialize o servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
