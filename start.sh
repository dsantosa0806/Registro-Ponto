#!/bin/bash
# Baixa os navegadores necessários antes de iniciar o app
python -m playwright install --with-deps chromium
exec python app.py
