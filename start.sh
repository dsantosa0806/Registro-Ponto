#!/bin/bash
# Baixa os navegadores necessários antes de iniciar o app
python -m playwright install chromium
exec python app.py
