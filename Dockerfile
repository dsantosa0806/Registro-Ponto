# Usa a imagem oficial Playwright já com navegadores instalados
FROM mcr.microsoft.com/playwright/python:v1.54.0


# Define diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Expõe a porta que o Railway vai mapear
EXPOSE 8080

# Comando padrão para iniciar o app Flask
CMD ["python", "app.py"]
