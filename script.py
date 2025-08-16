import os
import re
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

SENIOR_USER = os.environ.get("SENIOR_USER")
SENIOR_PASSWORD = os.environ.get("SENIOR_PASSWORD")

SENIOR_URL = (
    "https://platform.senior.com.br/login/"
    "?redirectTo=https%3A%2F%2Fplatform.senior.com.br%2Fsenior-x%2F&tenant=g4f.com.br"
)

def write_summary(md: str):
    """Escreve no Job Summary do GitHub Actions (aba Summary do run)."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(md + "\n")
        except Exception:
            pass

def registrar_ponto():
    log = []
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log.append(f"[{ts}] Início do processo.")

    # sanity check
    faltando = [k for k, v in {"SENIOR_USER": SENIOR_USER, "SENIOR_PASSWORD": SENIOR_PASSWORD}.items() if not v]
    if faltando:
        raise RuntimeError("Variáveis ausentes: " + ", ".join(faltando))

    with sync_playwright() as p:
        # Chromium headless (recomendado no Actions)
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(timezone_id="America/Sao_Paulo", locale="pt-BR")
        context.set_default_timeout(120000)

        # (opcional) bloquear ruído que mantém rede ocupada
        bloquear = ["google-analytics", "gtm", "segment", "hotjar", "doubleclick", "facebook", "sentry"]
        def _route(route):
            url = route.request.url.lower()
            if any(b in url for b in bloquear):
                return route.abort()
            return route.continue_()
        context.route("**/*", _route)

        page = context.new_page()
        page.set_default_timeout(120000)

        try:
            # 1) Login
            page.goto(SENIOR_URL, wait_until="domcontentloaded", timeout=120000)
            log.append("Página de login carregada.")

            # fecha/clica em banners comuns (se existirem)
            try:
                page.get_by_role("button", name=re.compile("aceitar|accept|ok|concordo", re.I)).click(timeout=2000)
                log.append("Banner de cookies/consent fechado.")
            except Exception:
                pass

            # Usuário
            try:
                page.get_by_placeholder(re.compile("Usu[aá]rio|E-mail|Email", re.I)).fill(SENIOR_USER, timeout=5000)
            except PWTimeout:
                page.get_by_label(re.compile("Usu[aá]rio|E-mail|Email", re.I)).fill(SENIOR_USER, timeout=5000)

            # Alguns tenants pedem “Próximo” antes da senha
            for texto in ["Próximo", "Continuar", "Avançar", "Next", "Continue"]:
                try:
                    page.get_by_role("button", name=re.compile(texto, re.I)).click(timeout=1500)
                    page.wait_for_timeout(500)
                    break
                except PWTimeout:
                    pass

            # Senha
            try:
                page.get_by_placeholder(re.compile("Senha|Password", re.I)).fill(SENIOR_PASSWORD, timeout=5000)
            except PWTimeout:
                page.get_by_label(re.compile("Senha|Password", re.I)).fill(SENIOR_PASSWORD, timeout=5000)

            # Entrar
            clicou = False
            for texto in ["Entrar", "Acessar", "Login", "Autenticar", "Continuar", "Entrar na plataforma"]:
                try:
                    page.get_by_role("button", name=re.compile(texto, re.I)).click(timeout=3000)
                    clicou = True
                    break
                except PWTimeout:
                    pass
            if not clicou:
                page.locator("button").first.click(timeout=3000)

            # Pós-login robusto: checa todas as abas e o iframe, sem 'networkidle'
            encontrou = False
            inicio = time.time()
            while time.time() - inicio < 60:
                for pg in context.pages:
                    u = (pg.url or "").lower()
                    if "senior-x" in u:
                        page = pg
                        encontrou = True
                        break
                    try:
                        if pg.locator("#custom_iframe").count():
                            page = pg
                            encontrou = True
                            break
                    except Exception:
                        pass
                if encontrou:
                    break
                page.wait_for_timeout(1000)

            if not encontrou:
                # força a navegação para o Senior-X
                try:
                    page.goto("https://platform.senior.com.br/senior-x/#/", wait_until="domcontentloaded", timeout=60000)
                    encontrou = True
                except Exception:
                    pass

            # Validação final sem networkidle
            ok = False
            for _ in range(30):
                if "senior-x" in (page.url or "").lower():
                    ok = True
                    break
                try:
                    if page.locator("#custom_iframe").count():
                        ok = True
                        break
                except Exception:
                    pass
                page.wait_for_timeout(1000)

            if not ok:
                raise RuntimeError("Login feito, mas o Senior-X não abriu. Verifique credenciais/SSO ou bloqueios pós-login.")

            log.append(f"Login ok. URL atual: {page.url}")

            # 2) Abrir a tela de ponto (sem esperar 'networkidle')
            url_ponto = (
                "https://platform.senior.com.br/senior-x/#/Gest%C3%A3o%20de%20Pessoas%20%7C%20HCM/1/"
                "res:%2F%2Fsenior.com.br%2Fhcm%2Fpontomobile%2FclockingEvent?category=frame&"
                "link=https:%2F%2Fplatform.senior.com.br%2Fhcm-pontomobile%2Fhcm%2Fpontomobile%2F%23%2Fclocking-event&"
                "withCredentials=true&r=0"
            )
            page.goto(url_ponto, wait_until="domcontentloaded", timeout=120000)
            log.append("Tela de registro de ponto requisitada (sem esperar networkidle).")

            # Aguarda o iframe #custom_iframe por polling (até ~90s)
            frame_ok = False
            for _ in range(90):
                try:
                    if page.locator("#custom_iframe").count():
                        frame_ok = True
                        break
                except Exception:
                    pass
                page.wait_for_timeout(1000)

            if not frame_ok:
                # Evidências e falha
                try:
                    with open("ponto.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                except Exception:
                    pass
                try:
                    page.screenshot(path="ponto.png", full_page=True)
                except Exception:
                    pass
                raise RuntimeError("Iframe #custom_iframe não apareceu após abrir a tela de ponto.")

            # 3) Clicar no botão dentro do iframe
            sucesso = False
            candidatos = ["Registrar Ponto", "Registrar ponto"]

            frame = page.frame_locator("#custom_iframe")

            # A) CSS por classe + texto
            try:
                frame.locator('button.resize-clocking-event-button:has-text("Registrar Ponto")').first.click(timeout=10000)
                sucesso = True
                log.append("Clique no botão (.resize-clocking-event-button:has-text('Registrar Ponto')).")
            except Exception:
                pass

            # B) Role + texto
            if not sucesso:
                for label in candidatos:
                    try:
                        frame.get_by_role("button", name=label).click(timeout=8000)
                        sucesso = True
                        log.append(f"Clique por role/name: '{label}'.")
                        break
                    except Exception:
                        continue

            # C) id dinâmico (prefixo)
            if not sucesso:
                try:
                    frame.locator('button[id^="btn-clocking-event-"]').first.click(timeout=8000)
                    sucesso = True
                    log.append("Clique no botão por id^='btn-clocking-event-'.")
                except Exception:
                    pass

            if not sucesso:
                # Evidências extras
                try:
                    with open("ponto.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                except Exception:
                    pass
                try:
                    page.screenshot(path="ponto.png", full_page=True)
                except Exception:
                    pass
                raise RuntimeError("Não encontrei o botão/ação de 'Registrar ponto'. Ajuste os seletores.")

            log.append("Clique para registrar ponto efetuado. Validando sucesso…")

            # 4) Verificação de sucesso (toast/texto dentro do iframe)
            validou = False
            for msg in [
                "Ponto registrado com sucesso",
                "Registro efetuado",
                "Marcação realizada",
                "Seu ponto foi registrado",
                "Operação realizada com sucesso",
                "Marcação realizada com sucesso"
            ]:
                try:
                    frame.get_by_text(re.compile(msg, re.I)).first.wait_for(timeout=8000)
                    validou = True
                    break
                except PWTimeout:
                    continue

            if not validou:
                log.append("Não encontrei mensagem explícita de sucesso. Considerando ok se não houve erro.")

            log.append("Fluxo de registro de ponto concluído.")
            return "\n".join(log)

        finally:
            # Evidências finais
            try:
                page.screenshot(path="ponto.png", full_page=True)
            except Exception:
                pass
            try:
                with open("ponto.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
            except Exception:
                pass

            log.append("Arquivo de evidência gerado com sucesso!")
            context.close()
            browser.close()

if __name__ == "__main__":
    try:
        body = registrar_ponto()
        write_summary(f"### ✅ Ponto registrado\n- Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        write_summary("#### Log\n```\n" + body + "\n```")
        print("OK: Ponto registrado com sucesso.")
    except Exception as e:
        erro = f"❌ Falha ao registrar ponto: {e}"
        print(erro)
        write_summary(f"### ❌ Falha ao registrar o ponto\n- Erro: `{e}`\n")
        write_summary("> Veja também os artifacts `ponto.png` e `ponto.html` para diagnóstico.")
        raise
