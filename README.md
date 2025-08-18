# 🤖 Registro Automático de Ponto (Senior X)

Este projeto automatiza o **registro de ponto** no sistema **Senior X** usando **Playwright**.  
Agora ele pode ser executado de duas formas:
- **Localmente** (`python script.py`)  
- **Remotamente** via **Railway com Docker**, disparado em horários exatos pelo [cron-job.org](https://cron-job.org)  

---

## 🚀 Funcionalidades
- Login automático na plataforma **Senior X**  
- Registro de ponto com captura de evidências (`ponto.png` e `ponto.html`) em caso de falha  
- Logs detalhados da execução  
- Disponível como **endpoint web** (`/run`) para ser chamado via cron-job.org  

---

## 📂 Estrutura do projeto
```
.
├── app.py          # API Flask que expõe o script
├── script.py       # Script principal em Python
├── requirements.txt
├── Dockerfile      # Configuração de container Playwright + Python
├── .dockerignore   # Ignora arquivos desnecessários no build
└── README.md
```

---

## 🛠️ Pré-requisitos
- Python 3.9+ instalado (para execução local)  
- Conta no [Railway.app](https://railway.app) (para deploy na nuvem com Docker)  
- Conta no [cron-job.org](https://cron-job.org) (para disparar nos horários certos)  
- Usuário e senha válidos do **Senior X**  

---

## ⚙️ Configuração

### 1. Executar localmente
Clone o repositório:
```bash
git clone https://github.com/seu-usuario/Registro-de-ponto.git
cd Registro-de-ponto
```

Instale as dependências:
```bash
pip install -r requirements.txt
```

Configure as variáveis de ambiente:
```bash
export SENIOR_USER="seu_usuario"
export SENIOR_PASSWORD="sua_senha"
```

Execute:
```bash
python script.py
```

Isso vai abrir o navegador headless via **Playwright**, logar e registrar o ponto.

---

### 2. Hospedar no Railway (via Docker)
1. O repositório já possui um **Dockerfile** baseado na imagem oficial do Playwright (`mcr.microsoft.com/playwright/python:v1.54.0`).  
   👉 Essa imagem já vem com Chromium, Firefox e WebKit instalados.  
2. No Railway:
   - Crie um novo projeto.  
   - Escolha **Deploy from GitHub Repo**.  
   - O Railway detecta o `Dockerfile` automaticamente.  
3. Configure as variáveis de ambiente no painel do Railway:
   - `SENIOR_USER`
   - `SENIOR_PASSWORD`  
4. Quando o deploy finalizar, você terá uma URL pública do tipo:
   ```
   https://seuprojeto.up.railway.app
   ```

Endpoints disponíveis:
- `GET /` → retorna status da API  
- `GET /run` → executa o registro de ponto  

Exemplo:
```bash
curl https://seuprojeto.up.railway.app/run
```

---

### 3. Configurar o cron-job.org
1. Crie uma conta em [cron-job.org](https://cron-job.org).  
2. Clique em **Create Cronjob**.  
3. Configure:
   - **URL**: `https://seuprojeto.up.railway.app/run`  
   - **Schedule**: horários exatos que deseja executar (em ponto).  
   - **Notifications**: opcional (receber e-mail em caso de falha).  
4. Salve.  

Agora o cron-job.org vai disparar o registro de ponto exatamente nos horários que você definiu ✅  

---

## 📊 Logs e Evidências
- Ao rodar localmente → logs aparecem no terminal.  
- Ao rodar no Railway → logs ficam disponíveis no painel de Deployments.  
- Em caso de falha, são gerados `ponto.png` e `ponto.html`.  

---

## ✅ Conclusão
Com este projeto, você automatiza o **registro de ponto** de forma:
- **Local** → útil para testes  
- **Remota** → hospedado no Railway via Docker, disparado automaticamente pelo cron-job.org  

Isso garante **praticidade, consistência e execução em ponto**.  

---

✍️ **Autor:** [Daniel Almeida](https://github.com/dsantosa0806)  
📌 Projeto para uso pessoal/educacional.
