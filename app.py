import os
import threading
from flask import Flask, jsonify, request
import script

app = Flask(__name__)

execucao_lock = threading.Lock()


def autorizado():
    """
    Segurança opcional:
    Se você definir RUN_TOKEN no Railway, será necessário chamar:
    /run?token=SEU_TOKEN
    ou enviar header X-RUN-TOKEN.
    """
    token_configurado = os.environ.get("RUN_TOKEN")

    if not token_configurado:
        return True

    token_recebido = request.headers.get("X-RUN-TOKEN") or request.args.get("token")
    return token_recebido == token_configurado


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "API do registro de ponto funcionando",
        "busy": execucao_lock.locked()
    }), 200


@app.route("/run", methods=["GET", "POST"])
def run():
    if not autorizado():
        return jsonify({
            "status": "unauthorized",
            "message": "Token inválido ou ausente."
        }), 401

    if not execucao_lock.acquire(blocking=False):
        return jsonify({
            "status": "busy",
            "message": "Já existe uma execução em andamento. Aguarde finalizar antes de chamar novamente."
        }), 409

    try:
        log = script.registrar_ponto()
        return jsonify({
            "status": "success",
            "log": log
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

    finally:
        execucao_lock.release()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))

    app.run(
        host="0.0.0.0",
        port=port,
        threaded=False
    )