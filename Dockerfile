# Playwright com Chromium já instalado
FROM mcr.microsoft.com/playwright/python:v1.54.0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# NÃO expõe porta
# NÃO sobe servidor web

CMD ["python", "script.py"]
