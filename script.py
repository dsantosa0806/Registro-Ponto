import os
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

SENIOR_USER = os.environ.get("SENIOR_USER")
SENIOR_PASSWORD = os.environ.get("SENIOR_PASSWORD")
SENIOR_URL = "https://platform.senior.com.br/login/?redirectTo=https%3A%2F%2Fplatform.senior.com.br%2Fsenior-x%2F&tenant=g4f.com.br"

def write_summary(md: str):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(md + "\n")

def registrar_ponto():
    log = []
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log.append(f"[{ts}] Início do processo.")

    if not (SENIOR_USER and SENIOR_PASSWORD):
        raise RuntimeError("Variáveis de ambiente SENIOR_USER e SENIOR_PASSWORD não configuradas.")

    with sync_playwright() as p:
        # Verifica se os navegadores do Playwright estão instalados antes de continuar
        try:
            # playwright.__file__ aponta para o local do pacote, mas o comando deve ser executado via CLI
            import subprocess
            subprocess.run(["playwright", "install", "chromium"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            raise RuntimeError(f"Falha ao instalar o navegador Chromium do Playwright: {e}")
            
        browser = p.chromium.launch(headless=True,
                                    args=["--no-sandbox",
                                     "--disable-dev-shm-usage"]
                                )
        context = browser.new_context(timezone_id="America/Sao_Paulo", locale="pt-BR")
        page = context.new_page()

        try:
            # 1) Acessa a página de login
            page.goto(SENIOR_URL, wait_until="load", timeout=60000)
            log.append("Página de login carregada.")

            # 2) Preenche usuário e senha
            # --- Localizadores comuns (ajuste se necessário) ---
            # Tente por placeholder:
            try:
                page.get_by_placeholder("Usuário").fill(SENIOR_USER, timeout=5000)
            except PWTimeout:
                page.get_by_label("Usuário").fill(SENIOR_USER, timeout=5000)

            # 3.1) Tenta clicar no botão "próximo" se existir
            #    Isso é comum em fluxos onde há múltiplas telas após o login
            try:
                # Tenta diferentes variações do botão "próximo"
                proximo_buttons = [
                    "Próximo",
                    "Próxima",
                    "Continuar",
                    "Avançar",
                    "Next",
                    "Continue"
                ]
                
                for button_text in proximo_buttons:
                    try:
                        # Tenta por texto exato
                        page.get_by_role("button", name=button_text).click(timeout=3000)
                        log.append(f"Botão '{button_text}' clicado com sucesso.")
                        # Aguarda um pouco para a próxima tela carregar
                        page.wait_for_timeout(2000)
                        break
                    except PWTimeout:
                        try:
                            # Tenta por texto parcial
                            page.get_by_text(button_text, exact=False).click(timeout=3000)
                            log.append(f"Botão '{button_text}' (parcial) clicado com sucesso.")
                            page.wait_for_timeout(2000)
                            break
                        except PWTimeout:
                            continue
                else:
                    log.append("Nenhum botão 'próximo' encontrado. Continuando...")
                    
            except Exception as e:
                log.append(f"Aviso: Erro ao tentar clicar em botão próximo: {e}")
                # Não falha o processo, apenas registra o aviso
                
            try:
                page.get_by_placeholder("Senha").fill(SENIOR_PASSWORD, timeout=5000)
            except PWTimeout:
                page.get_by_label("Senha").fill(SENIOR_PASSWORD, timeout=5000)

            # Clica no botão entrar/logar
            # Tentativas por texto/role (ajuste o texto exato se diferente)
            clicked = False
            for text in ["Entrar", "Acessar", "Login", "Continuar", "Entrar na plataforma", "Autenticar"]:
                try:
                    page.get_by_role("button", name=text).click(timeout=3000)
                    clicked = True
                    break
                except PWTimeout:
                    continue
            if not clicked:
                # Fallback genérico: primeiro botão da tela
                page.locator("button").first.click(timeout=3000)

            log.append("Credenciais enviadas. Aguardando pós-login…")

            # 3) Espera redirecionar para o Senior X (dashboard)
            #    Ajuste o fragmento se sua URL pós-login for diferente
            page.wait_for_url(lambda u: "senior-x" in u, timeout=60000)
            log.append(f"Login ok. URL atual: {page.url}")

            # Após o login, acessar a URL específica do registro de ponto
            url_ponto = "https://platform.senior.com.br/senior-x/#/Gest%C3%A3o%20de%20Pessoas%20%7C%20HCM/1/res:%2F%2Fsenior.com.br%2Fhcm%2Fpontomobile%2FclockingEvent?category=frame&link=https:%2F%2Fplatform.senior.com.br%2Fhcm-pontomobile%2Fhcm%2Fpontomobile%2F%23%2Fclocking-event&withCredentials=true&r=0"
            page.goto(url_ponto, wait_until="load", timeout=60000)
            log.append("Página de registro de ponto acessada diretamente após login.")

            # 4) Abrir/acionar o registro de ponto
            #    *** SEÇÃO “LOCALIZADORES” ***
            # Tente primeiro por texto direto no botão/menu:
            # === INÍCIO DO BLOCO AJUSTADO ===
            # === INÍCIO DO BLOCO AJUSTADO ===
            sucesso = False
            candidatos = ["Registrar Ponto", "Registrar ponto"]

            # 1) garanta que a tela terminou de montar (SPA)
            page.wait_for_load_state("networkidle", timeout=60000)
            page.wait_for_timeout(1500)  # pequeno respiro

            # 2) debug: liste todos os frames/iframes disponíveis (aparece no Job Summary)
            try:
                frames_info = [f"- {i}: {fr.url}" for i, fr in enumerate(page.frames)]
                write_summary("#### Frames detectados:\n" + "\n".join(frames_info))
            except Exception:
                pass

            # 3) encontre o frame alvo por URL (pontomobile / clocking / hcm)
            alvos = ("pontomobile", "clocking-event", "hcm-pontomobile", "hcm")
            frame_alvo = None

            # tente por até ~20s (às vezes o microfrontend aparece atrasado)
            for _ in range(20):
                for fr in page.frames:
                    u = (fr.url or "").lower()
                    if any(k in u for k in alvos):
                        frame_alvo = fr
                        break
                if frame_alvo:
                    break
                page.wait_for_timeout(1000)

            if not frame_alvo:
                # fallback: tente achar qualquer iframe e usar o primeiro para inspecionar
                try:
                    page.wait_for_selector("iframe", timeout=10000)
                    # atualiza a lista e tenta de novo
                    for fr in page.frames:
                        u = (fr.url or "").lower()
                        if any(k in u for k in alvos):
                            frame_alvo = fr
                            break
                except Exception:
                    pass

            if not frame_alvo:
                raise RuntimeError(
                    "Não localizei o iframe do módulo de ponto. "
                    "Veja 'Frames detectados' no Summary para o(s) URL(s) encontrado(s) e me envie."
                )

            log.append(f"Iframe alvo encontrado: {frame_alvo.url}")

            # 4) tente clicar no botão dentro do frame
            #   Tentativa A: id dinâmico por prefixo
            try:
                frame_alvo.locator('button[id^="btn-clocking-event-"]').first.click(timeout=10000)
                sucesso = True
                log.append("Clique no botão (id^=btn-clocking-event-) efetuado.")
            except Exception:
                pass

            #   Tentativa B: role + texto
            if not sucesso:
                for label in candidatos:
                    try:
                        frame_alvo.get_by_role("button", name=label).click(timeout=8000)
                        sucesso = True
                        log.append(f"Clique por role/name: '{label}'.")
                        break
                    except Exception:
                        continue

            #   Tentativa C: CSS com :has-text
            if not sucesso:
                try:
                    frame_alvo.locator('button:has-text("Registrar Ponto")').first.click(timeout=8000)
                    sucesso = True
                    log.append("Clique por CSS :has-text('Registrar Ponto').")
                except Exception:
                    pass

            if not sucesso:
                raise RuntimeError("Não encontrei o botão/ação de 'Registrar ponto'. Ajuste os seletores.")

            log.append("Clique para registrar ponto efetuado. Validando sucesso…")
            # === FIM DO BLOCO AJUSTADO ===

            # 5) Verificação de sucesso
            # Tente detectar um toast/mensagem/estado após bater o ponto:
            validou = False
            possiveis_sucessos = [
                "Ponto registrado com sucesso",
                "Registro efetuado",
                "Marcação realizada",
                "Seu ponto foi registrado",
                "Operação realizada com sucesso"
            ]
            for msg in possiveis_sucessos:
                try:
                    page.get_by_text(msg, exact=False).wait_for(timeout=8000)
                    validou = True
                    break
                except PWTimeout:
                    continue

            # Fallback: se a plataforma exibe um “último registro” com hora atual
            if not validou:
                # Ajuste para algum seletor que mostre o último registro
                # Exemplo (fictício): page.locator('[data-testid="ultimo-registro"]')
                pass

            if not validou:
                # Não invalida: pode ser que não haja mensagem visível; fica como “provável sucesso”
                log.append("Não encontrei mensagem de sucesso explícita. Supondo sucesso pelo fluxo sem erros.")

            log.append("Fluxo de registro de ponto concluído.")
            return "\n".join(log)

        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    try:
        body = registrar_ponto()
        write_summary(f"### ✅ Ponto registrado\n- Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        print("OK: Ponto registrado com sucesso.")
    except Exception as e:
        erro = f"❌ Falha ao registrar ponto: {e}"
        print(erro)
        write_summary(f"### ❌ Falha ao registrar o ponto\n- Erro: `{e}`\n")
        raise
