# 🤖 Registro Automático de Ponto (Senior X)

Este projeto automatiza o **registro de ponto** no sistema **Senior X** usando **Playwright** e **GitHub Actions**.  
Assim, você não precisa marcar manualmente — o script faz login, acessa a tela correta e registra o ponto automaticamente.

---

## 🚀 Funcionalidades
- Login automático na plataforma **Senior X**.  
- Acesso à tela de registro de ponto e clique no botão **Registrar Ponto**.  
- Captura de evidências (`ponto.png` e `ponto.html`) em caso de falha.  
- Log detalhado enviado para o **Job Summary** do GitHub Actions.  
- Execução automática em horários agendados pelo **GitHub Actions (cron)**.  

---

## 📂 Estrutura do projeto
```
.
├── script.py      # Script principal em Python
├── ponto.yml      # Workflow do GitHub Actions
└── README.md      # Documentação do projeto
```

---

## 🛠️ Pré-requisitos
1. Ter uma conta no [GitHub](https://github.com/).  
2. Ter um repositório chamado **Registro de ponto** para armazenar este projeto.  
3. Usuário e senha válidos do **Senior X**.  

---

## ⚙️ Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/Registro-de-ponto.git
cd Registro-de-ponto
```

### 2. Configurar variáveis secretas no GitHub
No repositório, vá em:  
`Settings` → `Secrets and variables` → `Actions` → **New repository secret**  

Adicione:  
- `SENIOR_USER` → Seu usuário do Senior  
- `SENIOR_PASSWORD` → Sua senha do Senior  

### 3. Workflow (`ponto.yml`)
O workflow já está configurado para rodar automaticamente.  
No `ponto.yml`, você encontra algo assim:

```yaml
on:
  schedule:
    - cron: "0 11 * * *"   # Executa às 08h (Brasília)
    - cron: "0 15 * * *"   # Executa às 12h (Brasília)
    - cron: "0 16 * * *"   # Executa às 13h (Brasília)
    - cron: "0 21 * * *"   # Executa às 18h (Brasília)
```

📌 Lembre-se: os horários no `cron` são sempre em **UTC**.  
Acima já está convertido para 08h, 12h, 13h e 18h de Brasília.  

---

## ▶️ Execução manual
Você também pode rodar manualmente pelo GitHub Actions:  
1. Vá em **Actions**.  
2. Escolha o workflow **Ponto**.  
3. Clique em **Run workflow**.  

---

## 📊 Logs e Evidências
- Após cada execução, o resumo aparece no **Actions → Job Summary**.  
- Caso ocorra erro, os arquivos `ponto.png` e `ponto.html` ficam disponíveis como **artifacts** para diagnóstico.  

---

## 🧹 Limpeza de artifacts
Por padrão, os artifacts ficam salvos por **90 dias**.  
Se quiser reduzir, adicione no `ponto.yml`:

```yaml
with:
  retention-days: 7
```

Assim, os artifacts expiram após 7 dias.

---

## ✅ Conclusão
Com este projeto, você automatiza o **registro de ponto** de forma segura, agendada e auditável via GitHub Actions.  
Isso garante praticidade, consistência e evidências de cada marcação.  

---

✍️ **Autor:** [Daniel Almeida](https://github.com/dsantosa0806)  
📌 Projeto para uso pessoal/educacional.
