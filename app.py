from flask import Flask, jsonify
import script  # importa seu script.py (mas não executa o __main__)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "message": "API do registro de ponto funcionando"}), 200

@app.route("/run", methods=["GET"])
def run():
    try:
        log = script.registrar_ponto()
        return jsonify({"status": "success", "log": log}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
