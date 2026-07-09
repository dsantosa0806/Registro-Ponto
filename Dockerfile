FROM mcr.microsoft.com/playwright/python:v1.54.0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 2 --worker-class gthread --timeout 300 --graceful-timeout 30 --access-logfile - --error-logfile -"]